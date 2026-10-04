"""Deterministic synthetic walk and the akshare-backed source with an
on-disk cache. Only the standard library is required to serve `synthetic`;
`akshare` imports lazily so an absent install fails with a friendly
CONFIG_ERROR instead of breaking the kernel.
"""

import hashlib
import json
import math
import time
from pathlib import Path

from utils.python_logger import log_debug

SYNTHETIC_START_DATE = "2024-01-02"
SYNTHETIC_BASE_PRICE = 100.0
SYNTHETIC_DRIFT = 0.0004
SYNTHETIC_VOLATILITY = 0.015
CACHE_REFRESH_HINT_DAYS = 7


def _seed_from(symbol: str) -> int:
    """Derive a stable 31-bit seed from the symbol (md5, stable across runs)."""
    digest = hashlib.md5(symbol.encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


class _Lcg:
    """A fixed-coefficient linear congruential generator (deterministic everywhere)."""

    _A = 1103515245
    _C = 12345
    _M = 2 ** 31

    def __init__(self, seed: int) -> None:
        self._state = seed % self._M

    def next_float(self) -> float:
        """Next uniform float in [0, 1)."""
        self._state = (self._A * self._state + self._C) % self._M
        return self._state / self._M

    def next_normal(self) -> float:
        """Approximate standard normal via the sum of twelve uniforms."""
        return sum(self.next_float() for _ in range(12)) - 6.0


def _dates(count: int) -> list:
    """`count` weekday dates starting at SYNTHETIC_START_DATE (no clock reads)."""
    from datetime import date, timedelta

    start = date.fromisoformat(SYNTHETIC_START_DATE)
    out = []
    cursor = start
    while len(out) < count:
        if cursor.weekday() < 5:
            out.append(cursor.isoformat())
        cursor += timedelta(days=1)
    return out


def synthetic_kline(symbol: str, bars: int) -> list:
    """Deterministic geometric random walk seeded by the symbol.

    Same symbol + same bar count → byte-identical series on every machine,
    which is what keyless snapshot replay requires.
    """
    rng = _Lcg(_seed_from(symbol))
    dates = _dates(bars)
    price = SYNTHETIC_BASE_PRICE
    out = []
    for index in range(bars):
        ret = SYNTHETIC_DRIFT + SYNTHETIC_VOLATILITY * rng.next_normal()
        open_price = price
        close = max(1.0, open_price * math.exp(ret))
        high = max(open_price, close) * (1 + 0.005 * rng.next_float())
        low = min(open_price, close) * (1 - 0.005 * rng.next_float())
        volume = 1_000_000 + 500_000 * rng.next_float()
        out.append({
            "date": dates[index],
            "open": round(open_price, 4),
            "high": round(high, 4),
            "low": round(low, 4),
            "close": round(close, 4),
            "volume": round(volume, 2),
        })
        price = close
    return out


class ConfigError(Exception):
    """Deployment-plane kernel failure (e.g. an uninstalled optional source)."""


def _cache_path(cache_dir: str, symbol: str, period: str) -> Path:
    """One cache file per (symbol, period) pair."""
    safe = symbol.replace("/", "_")
    return Path(cache_dir) / f"{safe}.{period}.json"


def _read_cache(cache_dir: str, symbol: str, period: str) -> list:
    """Read the cached series; a missing or corrupt file is a cache miss."""
    path = _cache_path(cache_dir, symbol, period)
    if not path.is_file():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        bars = payload.get("bars", [])
        if isinstance(bars, list) and bars:
            log_debug(f"缓存命中：{symbol} {period}（{len(bars)} 根）")
            return bars
    except (json.JSONDecodeError, OSError):
        log_debug(f"缓存文件不可读，忽略：{path}")
    return []


def _write_cache(cache_dir: str, symbol: str, period: str, bars: list) -> None:
    """Persist the fetched series; cache failures never fail the request."""
    try:
        path = _cache_path(cache_dir, symbol, period)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"fetched_at": int(time.time()), "bars": bars}, ensure_ascii=False),
            encoding="utf-8",
        )
    except OSError:
        log_debug(f"缓存写入失败，忽略：{symbol} {period}")


def _akshare_daily(symbol: str, bars: int) -> list:
    """Fetch A-share daily bars through akshare and normalize the frame.

    The caller must have installed the requirements (`pip install -r
    requirements.txt`); an absent install raises the friendly CONFIG_ERROR.
    """
    try:
        import akshare as ak  # noqa: PLC0415 — deliberately lazy: optional dependency
    except ImportError as exc:
        raise ConfigError(
            "数据源 akshare 未安装：请先执行 pip install -r requirements.txt，或改用 synthetic 数据源"
        ) from exc
    code = symbol
    frame = ak.stock_zh_a_hist(symbol=code, period="daily", adjust="qfq")
    rows = frame.tail(bars)
    return [
        {
            "date": str(row["日期"]),
            "open": float(row["开盘"]),
            "high": float(row["最高"]),
            "low": float(row["最低"]),
            "close": float(row["收盘"]),
            "volume": float(row["成交量"]),
        }
        for row in rows.to_dict("records")
    ]


def fetch_kline(source: str, symbol: str, period: str, bars: int, max_retries: int = 0, cache_dir: str | None = None) -> list:
    """Serve one daily kline series.

    `synthetic` is pure and never cached; `akshare` reads through the on-disk
    cache (hit = the file exists) and retries transient failures with a short
    backoff up to `max_retries` times.
    """
    if not isinstance(bars, int) or bars < 1 or bars > 1500:
        raise ValueError(f"K线根数必须是 1-1500 的整数，收到 {bars}")
    if source == "synthetic":
        return synthetic_kline(symbol, bars)
    if source != "akshare":
        raise ValueError(f"未知数据源：{source}（仅支持 synthetic / akshare）")
    if period != "daily":
        raise ValueError(f"数据源 {source} 当前仅支持 daily 周期，收到 {period}")
    if cache_dir:
        cached = _read_cache(cache_dir, symbol, period)
        if cached:
            return cached[-bars:]
    last_error: Exception = RuntimeError("未执行任何获取")
    for attempt in range(max_retries + 1):
        try:
            bars_fetched = _akshare_daily(symbol, bars)
            if not bars_fetched:
                raise ValueError(f"数据源未返回 {symbol} 的数据")
            if cache_dir:
                _write_cache(cache_dir, symbol, period, bars_fetched)
            return bars_fetched
        except (ConnectionError, RuntimeError, ValueError, OSError) as exc:
            last_error = exc
            if attempt < max_retries:
                time.sleep(min(2 ** attempt, 8))
    message = f"数据源获取失败：{last_error}"
    raise ConnectionError(message)
