import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

import trading_agents


def test_risk_5_categories_present():
    script = trading_agents.run_debate("601318.SH", "28-10")
    risk = script.risk
    for attr in ["market_risk", "policy_risk", "liquidity_risk", "compliance_risk", "operational_risk"]:
        assert hasattr(risk, attr)


def test_risk_scores_in_range_1_10():
    script = trading_agents.run_debate("601318.SH", "28-10")
    risk = script.risk
    for attr in ["market_risk", "policy_risk", "liquidity_risk", "compliance_risk", "operational_risk"]:
        score = getattr(risk, attr)
        assert 1 <= score <= 10


def test_overall_risk_score_in_range():
    script = trading_agents.run_debate("601318.SH", "28-10")
    assert 0 <= script.risk.overall_risk_score <= 10


def test_risk_events_is_list():
    script = trading_agents.run_debate("601318.SH", "28-10")
    assert isinstance(script.risk.risk_events, list)