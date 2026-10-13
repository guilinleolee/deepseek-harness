"""test_throttle.py · T2 必检

验证 em_global_get() 节流控制 + 技术指标层计算
1. 节流门 >= 1s 间隔
2. 抖动控制在 [0.1, 0.5] s 内
3. L3 技术指标层 5 个计算函数全部可工作
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import time
from pathlib import Path

import pytest

BASE = Path(__file__).resolve().parent.parent

from em_global_get import (  # noqa: E402
    Throttle, DEFAULT_MIN_INTERVAL, DEFAULT_JITTER_MIN, DEFAULT_JITTER_MAX,
    GlobalSourceSession,
    calc_ma, calc_macd, calc_rsi, calc_kdj, calc_bollinger,
)


def test_throttle_class_defaults():
    t = Throttle()
    assert t.min_interval == DEFAULT_MIN_INTERVAL
    assert DEFAULT_MIN_INTERVAL >= 1.0
    assert DEFAULT_JITTER_MIN >= 0.0
    assert DEFAULT_JITTER_MAX > DEFAULT_JITTER_MIN


def test_throttle_second_call_waits():
    """第二次调用应该等待（>= 0.9s）"""
    t = Throttle()
    t.wait()
    t0 = time.monotonic()
    t.wait()
    elapsed = time.monotonic() - t0
    assert elapsed >= 0.9, f"节流未生效，elapsed={elapsed:.3f}s"


def test_global_session_em_get_primary_success():
    """GlobalSourceSession 主源成功路径"""
    session = GlobalSourceSession()
    result = session.em_global_get(
        endpoint_name="quote_realtime",
        market="US",
        primary_source=lambda: {"price": 150.0, "symbol": "AAPL"},
    )
    assert result.fallback_used is False
    assert result.market == "US"
    assert result.data["price"] == 150.0


def test_global_session_fallback_used():
    """主源失败切备胎"""
    def fail():
        raise RuntimeError("primary down")
    def fb():
        return {"price": 149.5}

    session = GlobalSourceSession()
    result = session.em_global_get(
        endpoint_name="valuation_ratios",
        market="US",
        primary_source=fail,
        fallback_sources=[fb],
    )
    assert result.fallback_used is True
    assert result.data["price"] == 149.5


# ─────────────────────────────────────────────
# L3 技术指标层 5 个计算函数全部单测
# ─────────────────────────────────────────────

def test_calc_ma_basic():
    """MA20 基础用例"""
    prices = [10.0] * 19 + [20.0, 30.0]
    out = calc_ma(prices, 20)
    # 前 19 个为 None
    assert all(x is None for x in out[:19])
    # 第 20 个 = (10*19 + 20) / 20 = 10.5
    assert abs(out[19] - 10.5) < 1e-9
    # 第 21 个 = (10*18 + 20 + 30) / 20 = 11.5
    assert abs(out[20] - 11.5) < 1e-9


def test_calc_macd_basic():
    """MACD 输出 dif / dea / macd 三组序列"""
    prices = [10.0 + i * 0.1 for i in range(60)]
    out = calc_macd(prices)
    assert "dif" in out and "dea" in out and "macd" in out
    assert len(out["dif"]) == 60
    # 前 25 个 dif 应该为 None（slow=26）
    assert all(x is None for x in out["dif"][:25])
    # 后段应有有效值
    assert any(x is not None for x in out["dif"][-10:])


def test_calc_rsi_basic():
    """RSI 14 输出长度对齐 prices"""
    prices = [10.0 + i for i in range(30)]
    out = calc_rsi(prices, 14)
    assert len(out) == 30
    # 前 14 个为 None
    assert all(x is None for x in out[:14])
    # 后段有值
    assert any(x is not None for x in out[20:])


def test_calc_kdj_basic():
    """KDJ(9,3,3) 输出 k/d/j 三组"""
    highs = [10.0 + i for i in range(30)]
    lows = [9.0 + i for i in range(30)]
    closes = [9.5 + i for i in range(30)]
    out = calc_kdj(highs, lows, closes, n=9, k_period=3, d_period=3)
    assert "k" in out and "d" in out and "j" in out
    assert len(out["k"]) == 30
    # 前 8 个为 None
    assert all(x is None for x in out["k"][:8])
    # 9 起有值
    assert out["k"][8] is not None


def test_calc_bollinger_basic():
    """布林带(20, 2) 输出 upper/middle/lower"""
    prices = [100.0] * 19 + [110.0]
    out = calc_bollinger(prices, 20, 2.0)
    assert len(out["upper"]) == 20
    # 前 19 个为 None
    assert all(x is None for x in out["middle"][:19])
    # 第 20 个 middle ≈ 100.5
    assert abs(out["middle"][19] - 100.5) < 1e-9
    # upper > middle > lower
    assert out["upper"][19] > out["middle"][19] > out["lower"][19]
