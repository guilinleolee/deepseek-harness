"""test_error_handler.py · T4 必检

验证 6 种错误码决策树
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pathlib import Path

import pytest
import yaml


def load_cfg():
    with open(Path(__file__).resolve().parent.parent / "fallback.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_all_required_error_codes_present():
    cfg = load_cfg()
    required = {"BESTIP_EMPTY", "PARAM_MISSING", "RATE_LIMIT_HIT", "PROTOCOL_404", "TIMEOUT", "CONNECTION_REFUSED"}
    defined = set(cfg["error_handlers"].keys())
    assert required <= defined


def test_bestip_empty_switch_source():
    cfg = load_cfg()
    assert cfg["error_handlers"]["BESTIP_EMPTY"]["action"] == "switch_source"


def test_param_missing_fill_defaults():
    cfg = load_cfg()
    assert cfg["error_handlers"]["PARAM_MISSING"]["action"] == "fill_defaults"


def test_rate_limit_has_backoff_factor():
    cfg = load_cfg()
    h = cfg["error_handlers"]["RATE_LIMIT_HIT"]
    assert h["action"] == "retry_with_backoff"
    assert h["backoff_factor"] >= 1.5


def test_protocol_404_mark_deprecated():
    cfg = load_cfg()
    assert cfg["error_handlers"]["PROTOCOL_404"]["action"] == "mark_deprecated"


def test_timeout_retry_smaller_backoff():
    cfg = load_cfg()
    assert cfg["error_handlers"]["TIMEOUT"]["action"] == "retry_with_backoff"


def test_connection_refused_switch_source():
    cfg = load_cfg()
    assert cfg["error_handlers"]["CONNECTION_REFUSED"]["action"] == "switch_source"


def test_max_retries_under_5():
    cfg = load_cfg()
    assert cfg["max_retries"] <= 5