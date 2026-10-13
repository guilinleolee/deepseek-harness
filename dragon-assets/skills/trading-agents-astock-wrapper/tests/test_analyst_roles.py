import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

import trading_agents


def test_7_analyst_roles_registered():
    assert len(trading_agents.ANALYST_ROLES) == 7


def test_required_7_roles_present():
    required = {"fundamental_analyst", "technical_analyst", "sentiment_analyst",
                "valuation_analyst", "risk_analyst", "macro_analyst", "regulatory_analyst"}
    assert set(trading_agents.ANALYST_ROLES.keys()) == required


def test_every_analyst_has_chinese_name():
    for role, cfg in trading_agents.ANALYST_ROLES.items():
        assert "chinese" in cfg
        assert len(cfg["chinese"]) >= 2


def test_every_analyst_has_endpoints():
    for role, cfg in trading_agents.ANALYST_ROLES.items():
        assert len(cfg["endpoints"]) >= 1


def test_every_analyst_has_rating_dimensions():
    for role, cfg in trading_agents.ANALYST_ROLES.items():
        assert len(cfg["rating_dimensions"]) >= 3


def test_analyst_run_function():
    op = trading_agents.run_analyst_round("fundamental_analyst", "600519.SH", 1, "28-10")
    assert op.role == "fundamental_analyst"
    assert 1 <= op.rating <= 10
    assert op.conclusion in {"buy", "hold", "sell"}


def test_run_debate_returns_full_script():
    script = trading_agents.run_debate("601318.SH", "28-10", rounds=5)
    assert script.symbol == "601318.SH"
    assert len(script.analysts) == 7
    assert script.decision.decision in {"buy", "hold", "sell"}