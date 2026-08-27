"""em_global_get.py · global-stock-data-bridge V1.0 统一节流入口

天龙自研模块 · 与 a-stock-data-bridge V1.0 em_get.py 同范式
- 节流 ≥1s + 抖动
- 主源失败切备胎
- 非静默（错误也记录）
- 含技术指标层（L3）计算入口
"""
from __future__ import annotations

import random
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from typing import Any, Callable

TZ_CN = timezone(timedelta(hours=8))

DEFAULT_MIN_INTERVAL = 1.0
DEFAULT_JITTER_MIN = 0.1
DEFAULT_JITTER_MAX = 0.5
DEFAULT_MAX_RETRIES = 3

FALLBACK_ON = {"429", "500", "502", "503", "504", "API_KEY_INVALID", "RATE_LIMIT"}


@dataclass
class GlobalFetchResult:
    source: str
    endpoint: str
    data: Any
    fetched_at: str
    fallback_used: bool
    fallback_from: str | None = None
    market: str = ""  # "US" | "HK" | "CN" | "GLOBAL"
    error: str | None = None

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}


class Throttle:
    def __init__(self, min_interval=DEFAULT_MIN_INTERVAL, jitter_min=DEFAULT_JITTER_MIN, jitter_max=DEFAULT_JITTER_MAX):
        self.min_interval = min_interval
        self.jitter_min = jitter_min
        self.jitter_max = jitter_max
        self.last_call = 0.0

    def wait(self) -> float:
        now = time.monotonic()
        elapsed = now - self.last_call
        jitter = random.uniform(self.jitter_min, self.jitter_max)
        wait_time = max(0.0, self.min_interval + jitter - elapsed)
        if wait_time > 0:
            time.sleep(wait_time)
        self.last_call = time.monotonic()
        return wait_time


class GlobalSourceSession:
    """美港股会话复用 + 5 层防封"""

    def __init__(self):
        self.throttle = Throttle()
        self.total_calls = 0
        self.fallbacks_used = 0
        self.errors_seen: list[str] = []

    def em_global_get(
        self,
        endpoint_name: str,
        market: str,
        primary_source: Callable[[], Any],
        fallback_sources: list[Callable[[], Any]] | None = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> GlobalFetchResult:
        fallback_sources = fallback_sources or []
        now_iso = datetime.now(TZ_CN).isoformat(timespec="seconds")
        self.throttle.wait()
        self.total_calls += 1

        last_err = None
        for attempt in range(max_retries):
            try:
                data = primary_source()
                return GlobalFetchResult(
                    source=endpoint_name, endpoint=endpoint_name, data=data,
                    fetched_at=now_iso, fallback_used=False, market=market,
                )
            except Exception as e:
                last_err = repr(e)
                self.errors_seen.append(repr(e)[:80])
                if attempt < max_retries - 1:
                    backoff = (2 ** attempt) + random.uniform(0, 0.5)
                    time.sleep(backoff)

        for i, fb in enumerate(fallback_sources):
            self.throttle.wait()
            self.fallbacks_used += 1
            try:
                data = fb()
                return GlobalFetchResult(
                    source=f"{endpoint_name}.fallback.{i}", endpoint=endpoint_name,
                    data=data, fetched_at=now_iso, fallback_used=True,
                    fallback_from=endpoint_name, market=market,
                )
            except Exception as e:
                last_err = repr(e)
                self.errors_seen.append(repr(e)[:80])

        return GlobalFetchResult(
            source=endpoint_name, endpoint=endpoint_name, data=None,
            fetched_at=now_iso, fallback_used=True, market=market,
            error=last_err or "all sources failed",
        )

    def stats(self) -> dict:
        return {
            "total_calls": self.total_calls,
            "fallbacks_used": self.fallbacks_used,
            "errors_seen": len(self.errors_seen),
            "throttle_min_interval": self.throttle.min_interval,
        }


_default_session = GlobalSourceSession()


def get_session() -> GlobalSourceSession:
    return _default_session


# ─────────────────────────────────────────────
# 技术指标层（L3）纯计算函数（基于 L1 历史数据）
# ─────────────────────────────────────────────

def calc_ma(prices: list[float], period: int = 20) -> list[float | None]:
    """简单移动平均线（SMA）
    prices: 收盘价序列（最早 → 最新）
    return: 与 prices 等长，前 period-1 个为 None
    """
    out: list[float | None] = [None] * len(prices)
    if len(prices) < period:
        return out
    for i in range(period - 1, len(prices)):
        window = prices[i - period + 1:i + 1]
        out[i] = sum(window) / period
    return out


def calc_macd(prices: list[float], fast: int = 12, slow: int = 26, signal: int = 9) -> dict:
    """MACD 指标（12, 26, 9）
    return: { dif: [...], dea: [...], macd: [...] } （柱状 = (dif-dea)*2）
    """
    if len(prices) < slow + signal:
        return {"dif": [None] * len(prices), "dea": [None] * len(prices), "macd": [None] * len(prices)}

    def ema(data: list[float], n: int) -> list[float | None]:
        k = 2 / (n + 1)
        out: list[float | None] = [None] * len(data)
        # 第一个有效 EMA 用前 n 期的 SMA
        if len(data) < n:
            return out
        out[n - 1] = sum(data[:n]) / n
        for i in range(n, len(data)):
            out[i] = data[i] * k + out[i - 1] * (1 - k)
        return out

    ema_fast = ema(prices, fast)
    ema_slow = ema(prices, slow)
    dif = [None if (f is None or s is None) else f - s for f, s in zip(ema_fast, ema_slow)]
    # DEA = DIF 的 EMA(signal)
    dif_valid = [d for d in dif if d is not None]
    if len(dif_valid) < signal:
        dea = [None] * len(prices)
    else:
        dea_raw = ema(dif_valid, signal)
        dea = [None] * (len(prices) - len(dif_valid)) + dea_raw
    macd_hist = [None if (d is None or e is None) else (d - e) * 2 for d, e in zip(dif, dea)]
    return {"dif": dif, "dea": dea, "macd": macd_hist}


def calc_rsi(prices: list[float], period: int = 14) -> list[float | None]:
    """RSI 指标（14）"""
    out: list[float | None] = [None] * len(prices)
    if len(prices) <= period:
        return out
    gains, losses = [], []
    for i in range(1, len(prices)):
        diff = prices[i] - prices[i - 1]
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))
    # 第一个 RSI 用 SMA
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    if avg_loss == 0:
        out[period] = 100.0
    else:
        rs = avg_gain / avg_loss
        out[period] = 100 - (100 / (1 + rs))
    # 后续用 Wilder 平滑
    for i in range(period + 1, len(prices)):
        avg_gain = (avg_gain * (period - 1) + gains[i - 1]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i - 1]) / period
        if avg_loss == 0:
            out[i] = 100.0
        else:
            rs = avg_gain / avg_loss
            out[i] = 100 - (100 / (1 + rs))
    return out


def calc_kdj(highs: list[float], lows: list[float], closes: list[float],
             n: int = 9, k_period: int = 3, d_period: int = 3) -> dict:
    """KDJ 指标（9, 3, 3）
    K/D 取 50 起步，后续用 SMA 平滑
    """
    length = len(closes)
    k: list[float | None] = [None] * length
    d: list[float | None] = [None] * length
    j: list[float | None] = [None] * length
    if length < n:
        return {"k": k, "d": d, "j": j}
    prev_k, prev_d = 50.0, 50.0
    for i in range(n - 1, length):
        hn = max(highs[i - n + 1:i + 1])
        ln = min(lows[i - n + 1:i + 1])
        rsv = ((closes[i] - ln) / (hn - ln) * 100) if hn != ln else 50.0
        cur_k = (prev_k * (k_period - 1) + rsv) / k_period
        cur_d = (prev_d * (d_period - 1) + cur_k) / d_period
        cur_j = 3 * cur_k - 2 * cur_d
        k[i] = cur_k
        d[i] = cur_d
        j[i] = cur_j
        prev_k, prev_d = cur_k, cur_d
    return {"k": k, "d": d, "j": j}


def calc_bollinger(prices: list[float], period: int = 20, std_dev: float = 2.0) -> dict:
    """布林带（20, 2）"""
    length = len(prices)
    upper: list[float | None] = [None] * length
    middle: list[float | None] = [None] * length
    lower: list[float | None] = [None] * length
    if length < period:
        return {"upper": upper, "middle": middle, "lower": lower}
    for i in range(period - 1, length):
        window = prices[i - period + 1:i + 1]
        mean = sum(window) / period
        var = sum((x - mean) ** 2 for x in window) / period
        std = var ** 0.5
        middle[i] = mean
        upper[i] = mean + std_dev * std
        lower[i] = mean - std_dev * std
    return {"upper": upper, "middle": middle, "lower": lower}
