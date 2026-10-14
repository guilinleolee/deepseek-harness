"""Unit tests for the synthetic source, validation, and the akshare cache layer."""

import pytest

from pdat.datasource import fetch_kline, synthetic_kline


def test_synthetic_is_deterministic() -> None:
    first = synthetic_kline("000001", 50)
    second = synthetic_kline("000001", 50)
    assert first == second


def test_synthetic_varies_by_symbol() -> None:
    assert synthetic_kline("000001", 20) != synthetic_kline("AAPL", 20)


def test_synthetic_bar_count_exact() -> None:
    assert len(synthetic_kline("600000", 120)) == 120


def test_synthetic_dates_are_weekdays_only() -> None:
    from datetime import date

    series = synthetic_kline("300750", 40)
    for bar in series:
        assert date.fromisoformat(bar["date"]).weekday() < 5


def test_synthetic_prices_stay_positive() -> None:
    for bar in synthetic_kline("BTC/USDT", 300):
        assert bar["low"] > 0
        assert bar["close"] > 0


def test_bars_must_be_in_range() -> None:
    with pytest.raises(ValueError, match="1-1500"):
        fetch_kline(source="synthetic", symbol="000001", period="daily", bars=0)
    with pytest.raises(ValueError, match="1-1500"):
        fetch_kline(source="synthetic", symbol="000001", period="daily", bars=1501)


def test_unknown_source_fails_loud() -> None:
    with pytest.raises(ValueError, match="未知数据源"):
        fetch_kline(source="wind", symbol="000001", period="daily", bars=10)


def test_akshare_rejects_non_daily_period() -> None:
    with pytest.raises(ValueError, match="daily"):
        fetch_kline(source="akshare", symbol="000001", period="minute", bars=10)


def test_cache_round_trip(tmp_path) -> None:
    written = []

    class FakeFrame:
        @staticmethod
        def to_dict(_records):
            return written

    written = [
        {"日期": "2024-01-02", "开盘": 1.0, "最高": 2.0, "最低": 0.5, "收盘": 1.5, "成交量": 10.0},
    ]

    import pdat.datasource as datasource

    original = datasource._akshare_daily
    datasource._akshare_daily = lambda symbol, bars: FakeFrame.to_dict("records")
    try:
        first = fetch_kline(
            source="akshare", symbol="000001", period="daily", bars=10,
            max_retries=0, cache_dir=str(tmp_path),
        )
        assert len(first) == 1
        assert (tmp_path / "000001.daily.json").is_file()
        # Second read hits the cache: the fake source is left in place, so a
        # cache miss would raise (the fake returns rows only because it is
        # still patched); flip the patch to prove the cache serves it.
        datasource._akshare_daily = lambda symbol, bars: (_ for _ in ()).throw(AssertionError("cache miss"))
        second = fetch_kline(
            source="akshare", symbol="000001", period="daily", bars=10,
            max_retries=0, cache_dir=str(tmp_path),
        )
        assert second == first
    finally:
        datasource._akshare_daily = original


def test_empty_fetch_is_an_error(tmp_path) -> None:
    import pdat.datasource as datasource

    original = datasource._akshare_daily
    datasource._akshare_daily = lambda symbol, bars: []
    try:
        with pytest.raises(ConnectionError, match="数据源获取失败"):
            fetch_kline(
                source="akshare", symbol="000001", period="daily", bars=10,
                max_retries=0, cache_dir=str(tmp_path),
            )
    finally:
        datasource._akshare_daily = original


def test_retry_backoff_then_success(tmp_path, monkeypatch) -> None:
    import pdat.datasource as datasource

    calls = {"count": 0}
    sleeps = []

    def flaky(symbol, bars):
        calls["count"] += 1
        if calls["count"] == 1:
            raise ConnectionError("网络抖动")
        return [
            {"日期": "2024-01-02", "开盘": 1.0, "最高": 2.0, "最低": 0.5, "收盘": 1.5, "成交量": 10.0},
        ]

    monkeypatch.setattr(datasource, "_akshare_daily", flaky)
    monkeypatch.setattr(datasource.time, "sleep", lambda seconds: sleeps.append(seconds))
    rows = fetch_kline(
        source="akshare", symbol="000001", period="daily", bars=10,
        max_retries=1, cache_dir=str(tmp_path),
    )
    assert calls["count"] == 2
    assert sleeps == [1]
    assert len(rows) == 1
