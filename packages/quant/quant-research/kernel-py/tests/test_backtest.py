"""Unit tests for the SMA-cross simulator: trade model, metrics, validation."""

import math

import pytest

from pcpt.backtest import _sma, run_backtest


def make_bars(closes: list, start: str = "2024-01-01") -> list:
    """Bars whose open equals the previous close (clean signal→execution seams)."""
    bars = []
    price = closes[0]
    for index, close in enumerate(closes):
        bars.append({
            "date": f"{start[:8]}{index:02d}",
            "open": price,
            "high": max(price, close) * 1.001,
            "low": min(price, close) * 0.999,
            "close": close,
            "volume": 1000.0,
        })
        price = close
    return bars


def test_sma_warmup_and_values() -> None:
    lines = _sma([1.0, 2.0, 3.0, 4.0], 2)
    assert lines[0] is None
    assert lines[1] == 1.5
    assert lines[2] == 2.5
    assert lines[3] == 3.5


def test_downtrend_then_uptrend_makes_one_round_trip() -> None:
    # Falling, rising, falling: the golden cross fires mid-run and the death
    # cross closes the position before the series ends.
    closes = (
        [100.0 - index for index in range(30)]
        + [70.0 + 2 * index for index in range(30)]
        + [128.0 - 3 * index for index in range(15)]
    )
    report = run_backtest(
        bars=make_bars(closes), fast=3, slow=10,
        initial_cash=1_000_000.0, fee_rate=0.0, symbol="TEST",
    )
    sides = [trade["side"] for trade in report["trades"]]
    assert sides == ["buy", "sell"]
    assert report["metrics"]["trade_count"] == 1
    assert report["metrics"]["win_rate"] == 1.0
    assert report["final_equity"] > report["initial_cash"]


def test_fee_reduces_final_equity() -> None:
    closes = (
        [100.0 - index for index in range(30)]
        + [70.0 + 2 * index for index in range(30)]
        + [128.0 - 3 * index for index in range(15)]
    )
    without_fee = run_backtest(
        bars=make_bars(closes), fast=3, slow=10, initial_cash=1_000_000.0, fee_rate=0.0, symbol="TEST",
    )
    with_fee = run_backtest(
        bars=make_bars(closes), fast=3, slow=10, initial_cash=1_000_000.0, fee_rate=0.001, symbol="TEST",
    )
    assert with_fee["final_equity"] < without_fee["final_equity"]


def test_execution_lags_the_signal_by_one_bar() -> None:
    # The buy must fill at the bar AFTER the first golden cross's close.
    closes = [100.0 - index for index in range(30)] + [70.0 + 2 * index for index in range(30)]
    bars = make_bars(closes)
    report = run_backtest(bars=bars, fast=3, slow=10, initial_cash=1_000_000.0, fee_rate=0.0, symbol="TEST")
    closes_list = closes
    fast = _sma(closes_list, 3)
    slow = _sma(closes_list, 10)
    cross_index = next(
        index for index in range(len(closes_list))
        if fast[index] is not None and slow[index] is not None and fast[index] > slow[index]
    )
    buy = report["trades"][0]
    assert buy["date"] == bars[cross_index + 1]["date"]
    assert buy["price"] == bars[cross_index + 1]["open"]


def test_flat_series_never_trades() -> None:
    closes = [100.0] * 40
    report = run_backtest(
        bars=make_bars(closes), fast=3, slow=10, initial_cash=1_000_000.0, fee_rate=0.0, symbol="TEST",
    )
    assert report["trades"] == []
    assert report["metrics"]["trade_count"] == 0
    assert report["metrics"]["win_rate"] == 0.0
    assert report["final_equity"] == 1_000_000.0


def test_metrics_shape() -> None:
    closes = [100.0 - index for index in range(30)] + [70.0 + 2 * index for index in range(30)]
    report = run_backtest(
        bars=make_bars(closes), fast=3, slow=10, initial_cash=1_000_000.0, fee_rate=0.0, symbol="TEST",
    )
    metrics = report["metrics"]
    assert set(metrics) == {"total_return", "annual_return", "max_drawdown", "sharpe", "win_rate", "trade_count"}
    assert metrics["max_drawdown"] >= 0
    assert metrics["sharpe"] == metrics["sharpe"]  # not NaN
    expected_annual = (1 + metrics["total_return"]) ** (1 / (len(report["equity"]) / 252)) - 1
    assert math.isclose(metrics["annual_return"], expected_annual, rel_tol=1e-6)


def test_validation_rejects_impossible_parameters() -> None:
    bars = make_bars([100.0] * 40)
    with pytest.raises(ValueError, match="至少覆盖慢线窗口"):
        run_backtest(bars=bars[:5], fast=3, slow=10, initial_cash=1_000_000.0, fee_rate=0.0)
    with pytest.raises(ValueError, match="快线窗口"):
        run_backtest(bars=bars, fast=1, slow=10, initial_cash=1_000_000.0, fee_rate=0.0)
    with pytest.raises(ValueError, match="必须小于"):
        run_backtest(bars=bars, fast=10, slow=5, initial_cash=1_000_000.0, fee_rate=0.0)
    with pytest.raises(ValueError, match="初始资金"):
        run_backtest(bars=bars, fast=3, slow=10, initial_cash=-1, fee_rate=0.0)
    with pytest.raises(ValueError, match="手续费率"):
        run_backtest(bars=bars, fast=3, slow=10, initial_cash=1_000_000.0, fee_rate=0.9)
    with pytest.raises(ValueError, match="date/open/close"):
        run_backtest(
            bars=[{"open": 1.0, "close": 1.0}] * 40, fast=3, slow=10,
            initial_cash=1_000_000.0, fee_rate=0.0,
        )
