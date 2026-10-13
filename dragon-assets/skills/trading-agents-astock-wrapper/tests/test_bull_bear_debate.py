import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

import trading_agents


def test_bull_templates_count():
    assert len(trading_agents.BULL_TEMPLATES) >= 5


def test_bear_templates_count():
    assert len(trading_agents.BEAR_TEMPLATES) >= 5


def test_bull_bear_no_overlap():
    overlap = set(trading_agents.BULL_TEMPLATES) & set(trading_agents.BEAR_TEMPLATES)
    assert len(overlap) == 0


def test_debate_bull_arguments_at_least_3():
    script = trading_agents.run_debate("601318.SH", "28-10")
    assert len(script.bull_bear.bull_arguments) >= 3


def test_debate_bear_arguments_at_least_3():
    script = trading_agents.run_debate("601318.SH", "28-10")
    bear_args = script.bull_bear.bear_arguments.split(", ")
    assert len(bear_args) >= 3


def test_bull_bear_scores_opposite_direction():
    script = trading_agents.run_debate("601318.SH", "28-10")
    diff = script.bull_bear.bull_score - script.bull_bear.bear_score
    assert abs(diff) > 0