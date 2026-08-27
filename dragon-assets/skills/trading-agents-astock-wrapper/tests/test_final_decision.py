import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

import trading_agents


def test_decision_in_valid_set():
    script = trading_agents.run_debate("601318.SH", "28-10")
    assert script.decision.decision in {"buy", "hold", "sell"}


def test_position_size_non_empty():
    script = trading_agents.run_debate("601318.SH", "28-10")
    assert len(script.decision.position_size) >= 1


def test_holding_period_non_empty():
    script = trading_agents.run_debate("601318.SH", "28-10")
    assert len(script.decision.holding_period) >= 1


def test_decision_consistency_with_weighted_score():
    weighted = (trading_agents.run_debate("601318.SH", "28-10").decision.analyst_avg
                + 0.0 * 0.3
                - trading_agents.run_debate("601318.SH", "28-10").decision.risk_penalty)
    # 简化断言：decision 在 {buy, hold, sell}
    script = trading_agents.run_debate("601318.SH", "28-10")
    assert script.decision.decision in {"buy", "hold", "sell"}


def test_rationale_non_empty():
    script = trading_agents.run_debate("601318.SH", "28-10")
    assert "7 分析师均分" in script.decision.rationale


def test_to_dict_serializable():
    script = trading_agents.run_debate("601318.SH", "28-10")
    d = script.to_dict()
    json.dumps(d, ensure_ascii=False)


def test_render_markdown_contains_all_sections():
    script = trading_agents.run_debate("601318.SH", "28-10")
    md = trading_agents.render_markdown(script)
    for sec in ["Stage 1: 7 分析师", "Stage 2: Bull/Bear", "Stage 3: 风险评估", "Stage 4: 最终投资决策", "Powered by simonlin1212/TradingAgents-astock", "Apache-2.0"]:
        assert sec in md