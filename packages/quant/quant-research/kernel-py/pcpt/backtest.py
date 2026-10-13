"""Daily SMA-cross simulator: a pure function of its inputs.

Signal discipline (documented contract): the fast/slow comparison runs on
bar `t`'s closes, and the order executes at bar `t+1`'s open — no same-bar
lookahead. Sizing is all-in/all-out; each fill pays `fee_rate` once.
"""

import math

MAX_FEE_RATE = 0.05
TRADING_DAYS_PER_YEAR = 252


def _sma(closes: list, window: int) -> list:
    """Rolling SMA; positions inside the warm-up window are None."""
    out = []
    window_sum = 0.0
    for index, value in enumerate(closes):
        window_sum += value
        if index >= window:
            window_sum -= closes[index - window]
        out.append(window_sum / window if index >= window - 1 else None)
    return out


def _validate(bars: list, fast: int, slow: int, initial_cash: float, fee_rate: float) -> None:
    """Fail loud on any impossible parameter combination."""
    if not isinstance(bars, list) or len(bars) < slow + 1:
        raise ValueError(f"K线根数必须至少覆盖慢线窗口（≥ {slow + 1}），收到 {len(bars) if isinstance(bars, list) else bars}")
    if not isinstance(fast, int) or fast < 2 or fast > 120:
        raise ValueError(f"快线窗口必须是 2-120 的整数，收到 {fast}")
    if not isinstance(slow, int) or slow < 3 or slow > 250:
        raise ValueError(f"慢线窗口必须是 3-250 的整数，收到 {slow}")
    if fast >= slow:
        raise ValueError(f"快线窗口（{fast}）必须小于慢线窗口（{slow}）")
    if not isinstance(initial_cash, (int, float)) or initial_cash <= 0 or initial_cash > 1e12:
        raise ValueError(f"初始资金必须是 0-1e12 的数值，收到 {initial_cash}")
    if not isinstance(fee_rate, (int, float)) or fee_rate < 0 or fee_rate > MAX_FEE_RATE:
        raise ValueError(f"手续费率必须是 0-{MAX_FEE_RATE} 之间的数值，收到 {fee_rate}")
    for index, bar in enumerate(bars):
        if not isinstance(bar, dict) or "date" not in bar or "open" not in bar or "close" not in bar:
            raise ValueError(f"第 {index} 根K线缺少 date/open/close 字段")


def _metrics(equity: list, initial_cash: float, buy_prices: list, sell_prices: list) -> dict:
    """Headline metrics from the equity curve and the completed round trips."""
    final = equity[-1]["value"]
    total_return = round(final / initial_cash - 1, 6)
    years = len(equity) / TRADING_DAYS_PER_YEAR
    annual_return = round((1 + total_return) ** (1 / years) - 1, 6) if years > 0 else 0.0
    peak = equity[0]["value"]
    max_drawdown = 0.0
    returns = []
    previous = equity[0]["value"]
    for point in equity:
        peak = max(peak, point["value"])
        if peak > 0:
            max_drawdown = max(max_drawdown, (peak - point["value"]) / peak)
        if previous > 0:
            returns.append(point["value"] / previous - 1)
        previous = point["value"]
    mean = sum(returns) / len(returns) if returns else 0.0
    variance = (sum((r - mean) ** 2 for r in returns) / len(returns)) if returns else 0.0
    std = math.sqrt(variance)
    sharpe = (mean / std) * math.sqrt(TRADING_DAYS_PER_YEAR) if std > 0 else 0.0
    rounds = min(len(buy_prices), len(sell_prices))
    wins = sum(1 for index in range(rounds) if sell_prices[index] > buy_prices[index])
    win_rate = wins / rounds if rounds else 0.0
    return {
        "total_return": total_return,
        "annual_return": annual_return,
        "max_drawdown": round(max_drawdown, 6),
        "sharpe": round(sharpe, 4),
        "win_rate": round(win_rate, 4),
        "trade_count": rounds,
    }


def run_backtest(bars: list, fast: int, slow: int, initial_cash: float, fee_rate: float, symbol: str = "") -> dict:
    """Run the simulator and return the equity curve, fills, and metrics."""
    _validate(bars, fast, slow, initial_cash, fee_rate)
    closes = [float(bar["close"]) for bar in bars]
    fast_line = _sma(closes, fast)
    slow_line = _sma(closes, slow)
    cash = float(initial_cash)
    shares = 0.0
    position = False
    pending_action = None
    trades = []
    buy_prices = []
    sell_prices = []
    equity = []
    for index, bar in enumerate(bars):
        if pending_action is not None:
            open_price = float(bar["open"])
            if pending_action == "buy" and not position:
                shares = (cash * (1 - fee_rate)) / open_price
                cash = 0.0
                position = True
                buy_prices.append(open_price)
                trades.append({"date": bar["date"], "side": "buy", "price": open_price, "shares": round(shares, 6)})
            elif pending_action == "sell" and position:
                proceeds = shares * open_price * (1 - fee_rate)
                cash = proceeds
                sell_prices.append(open_price)
                trades.append({"date": bar["date"], "side": "sell", "price": open_price, "shares": round(shares, 6)})
                shares = 0.0
                position = False
            pending_action = None
        equity.append({"date": bar["date"], "value": round(cash + shares * float(bar["close"]), 4)})
        if fast_line[index] is not None and slow_line[index] is not None:
            if fast_line[index] > slow_line[index] and not position:
                pending_action = "buy"
            elif fast_line[index] < slow_line[index] and position:
                pending_action = "sell"
    final_equity = equity[-1]["value"]
    return {
        "symbol": symbol,
        "fast": fast,
        "slow": slow,
        "initial_cash": initial_cash,
        "final_equity": final_equity,
        "equity": equity,
        "trades": trades,
        "metrics": _metrics(equity, initial_cash, buy_prices, sell_prices),
    }
