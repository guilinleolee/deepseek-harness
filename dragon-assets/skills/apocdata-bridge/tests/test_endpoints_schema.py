import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

import em_apocdata


def test_total_endpoints_is_8():
    assert len(em_apocdata.ENDPOINTS) == 8


def test_required_8_endpoints_present():
    required = {"quote","stock","profile_full","financials","news","announcements","capital_flow","technical"}
    assert set(em_apocdata.ENDPOINTS.keys()) == required


def test_profile_full_is_core():
    assert em_apocdata.ENDPOINTS["profile_full"].get("core") is True


def test_every_endpoint_has_layer():
    for name, meta in em_apocdata.ENDPOINTS.items():
        assert "layer" in meta
        assert meta["layer"].startswith("L")


def test_base_templates_use_defined_endpoints():
    for ttype, eps in em_apocdata.BASE_TEMPLATES.items():
        for ep in eps:
            assert ep in em_apocdata.ENDPOINTS


def test_4_prompt_templates_defined():
    required = {"qwen", "deepseek", "kimi", "openai"}
    assert set(em_apocdata.PROMPT_TEMPLATES.keys()) == required


def test_each_prompt_contains_chinese():
    for tmpl in em_apocdata.PROMPT_TEMPLATES.values():
        assert any('一' <= c <= '鿿' for c in tmpl)