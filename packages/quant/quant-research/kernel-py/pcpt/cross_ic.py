"""Kernel-side cross-sectional factor IC: align a multi-symbol panel on
shared dates, compute one factor per symbol (no lookahead), and correlate
each date's factor cross-section against its horizon-day forward-return
cross-section with a rank (Spearman) correlation. Mirrors the audited
TypeScript pipeline in ``paat/cross-ic.ts`` — the numbers must agree."""

from __future__ import annotations

# Hard caps mirroring the TypeScript compliance layer.
HORIZON_LIMITS = {"min": 1, "max": 20}
PANEL_SIZE_LIMITS = {"min": 2, "max": 10}
FACTOR_NAMES = ("momentum", "volatility", "volume_ratio", "price_position")
DEFAULT_FACTOR_WINDOWS = {
    "momentum": 20,
    "volatility": 20,
    "volume_ratio": 20,
    "price_position": 20,
}


def _factor_momentum(bars: list, window: int) -> list:
    """`close[t] / close[t - window] - 1`, null before the window fills."""
    out = [None] * len(bars)
    for i in range(window, len(bars)):
        base = bars[i - window]["close"]
        if base:
            out[i] = bars[i]["close"] / base - 1
    return out


def _factor_volatility(bars: list, window: int) -> list:
    """Annualized close-return std over the trailing window."""
    out = [None] * len(bars)
    for i in range(window, len(bars)):
        closes = [bar["close"] for bar in bars[i - window : i + 1]]
        returns = [closes[k] / closes[k - 1] - 1 for k in range(1, len(closes)) if closes[k - 1]]
        if len(returns) >= 2:
            mean = sum(returns) / len(returns)
            var = sum((r - mean) ** 2 for r in returns) / (len(returns) - 1)
            out[i] = (var * 252) ** 0.5
    return out


def _factor_volume_ratio(bars: list, window: int) -> list:
    """Latest volume over its trailing-window mean."""
    out = [None] * len(bars)
    for i in range(window, len(bars)):
        volumes = [bar["volume"] for bar in bars[i - window : i + 1]]
        mean = sum(volumes) / len(volumes)
        if mean:
            out[i] = bars[i]["volume"] / mean
    return out


def _factor_price_position(bars: list, window: int) -> list:
    """Close position within the trailing window's low-high range, 0-1."""
    out = [None] * len(bars)
    for i in range(window, len(bars)):
        low = min(bar["low"] for bar in bars[i - window : i + 1])
        high = max(bar["high"] for bar in bars[i - window : i + 1])
        if high != low:
            out[i] = (bars[i]["close"] - low) / (high - low)
    return out


_FACTORS = {
    "momentum": _factor_momentum,
    "volatility": _factor_volatility,
    "volume_ratio": _factor_volume_ratio,
    "price_position": _factor_price_position,
}


def _compute_factor(name: str, bars: list, window=None) -> list:
    """Date-aligned factor values for one symbol (the four audited factors)."""
    if name not in _FACTORS:
        raise PanelError(f"未知因子：{name}")
    return _FACTORS[name](bars, window if window is not None else DEFAULT_FACTOR_WINDOWS[name])


class PanelError(ValueError):
    """A panel-level validation failure (shape, alignment, or caps)."""


def _rank(values: list) -> list:
    """Average ranks with tie handling, mirroring ``ic.spearman``."""
    indexed = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    start = 0
    while start < len(indexed):
        end = start
        while end + 1 < len(indexed) and values[indexed[end + 1]] == values[indexed[start]]:
            end += 1
        average = (start + end) / 2 + 1
        for j in range(start, end + 1):
            ranks[indexed[j]] = average
        start = end + 1
    return ranks


def _spearman(xs: list, ys: list):
    """Rank correlation; ``None`` when fewer than two pairs or zero variance."""
    if len(xs) != len(ys) or len(xs) < 2:
        return None
    rx, ry = _rank(xs), _rank(ys)
    n = len(xs)
    mean_x = sum(rx) / n
    mean_y = sum(ry) / n
    cov = var_x = var_y = 0.0
    for i in range(n):
        dx = rx[i] - mean_x
        dy = ry[i] - mean_y
        cov += dx * dy
        var_x += dx * dx
        var_y += dy * dy
    if var_x == 0 or var_y == 0:
        return None
    return cov / ((var_x * var_y) ** 0.5)


def _factor_series(name: str, bars: list, window):
    """One symbol's factor values keyed by date."""
    factor = _compute_factor(name, bars, window)
    return {bar["date"]: factor[i] for i, bar in enumerate(bars)}


def run_cross_section_ic(
    panel: dict,
    factor: str,
    horizon: int,
    window=None,
) -> dict:
    """Correlate the factor cross-section with forward returns per shared date.

    ``panel`` maps symbol -> its full bar list (oldest first). The dates every
    symbol shares are the evaluation calendar; a symbol's factor at date t
    reads only closes up to t (no lookahead).
    """
    symbols = sorted(panel)
    if not PANEL_SIZE_LIMITS["min"] <= len(symbols) <= PANEL_SIZE_LIMITS["max"]:
        raise PanelError(
            f"symbols 面板必须是 {PANEL_SIZE_LIMITS['min']}-{PANEL_SIZE_LIMITS['max']} 只标的"
        )
    if not isinstance(horizon, int) or not HORIZON_LIMITS["min"] <= horizon <= HORIZON_LIMITS["max"]:
        raise PanelError(f"horizon 必须是 {HORIZON_LIMITS['min']}-{HORIZON_LIMITS['max']} 的整数")

    factor_by_symbol = {symbol: _factor_series(factor, panel[symbol], window) for symbol in symbols}
    close_by_symbol = {
        symbol: {bar["date"]: bar["close"] for bar in panel[symbol]} for symbol in symbols
    }
    shared = set.intersection(*(set(close_by_symbol[symbol]) for symbol in symbols)) if symbols else set()
    dates = sorted(shared)
    if len(dates) < 2:
        raise PanelError("各标的共享交易日不足 2 天，无法构建横截面")

    points = []
    for index in range(len(dates) - horizon):
        date = dates[index]
        future = dates[index + horizon]
        factor_values, forward_returns = [], []
        for symbol in symbols:
            factor_value = factor_by_symbol[symbol].get(date)
            close_today = close_by_symbol[symbol].get(date)
            close_future = close_by_symbol[symbol].get(future)
            if factor_value is None or close_today is None or close_future is None:
                continue
            factor_values.append(factor_value)
            forward_returns.append(close_future / close_today - 1)
        points.append({"date": date, "ic": _spearman(factor_values, forward_returns)})

    valid = [point["ic"] for point in points if point["ic"] is not None]
    summary = None
    if len(valid) >= 2:
        mean = sum(valid) / len(valid)
        variance = sum((ic - mean) ** 2 for ic in valid) / (len(valid) - 1)
        std = variance ** 0.5
        safe_std = 0.0 if std < 1e-4 else std
        summary = {
            "observations": len(valid),
            "mean_ic": mean,
            "std_ic": std,
            "icir": 0.0 if safe_std == 0 else mean / safe_std,
            "positive_share": sum(1 for ic in valid if ic > 0) / len(valid),
            "t_stat": 0.0 if safe_std == 0 else (mean / safe_std) * (len(valid) ** 0.5),
        }
    return {
        "factor": factor,
        "horizon": horizon,
        "symbols": symbols,
        "shared_dates": len(dates),
        "points": points,
        "summary": summary,
    }
