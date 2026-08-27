"""test_fallback.py · T3 必检

验证 3 官方备胎降级
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pathlib import Path

import pytest
import yaml

from em_get import SourceSession  # noqa: E402


def test_primary_success_no_fallback():
    session = SourceSession()
    result = session.em_get("kline_with_ma", primary_source=lambda: {"price": 100.0})
    assert result.fallback_used is False


def test_primary_fails_fallback_used():
    session = SourceSession()
    result = session.em_get(
        "pe_pb_market_cap",
        primary_source=lambda: (_ for _ in ()).throw(RuntimeError("down")),
        fallback_sources=[lambda: {"price": 99.5}],
    )
    assert result.fallback_used is True
    assert result.data == {"price": 99.5}


def test_all_failures_no_silent():
    session = SourceSession()
    def fail():
        raise RuntimeError("down")
    result = session.em_get("research_report_list", primary_source=fail, fallback_sources=[fail, fail])
    assert result.data is None
    assert result.error is not None


def test_session_stats_increments():
    session = SourceSession()
    session.em_get("e1", lambda: 1)
    session.em_get("e2", lambda: 2)
    assert session.stats()["total_calls"] == 2


def test_silent_failure_disabled_in_yaml():
    with open(Path(__file__).resolve().parent.parent / "fallback.yaml", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    assert cfg.get("silent_failure") is False


def test_official_fallbacks_count():
    with open(Path(__file__).resolve().parent.parent / "fallback.yaml", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    assert cfg.get("official_fallbacks") == 3