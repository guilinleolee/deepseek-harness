"""test_apache_notice.py · T3 必检

验证 Apache-2.0 NOTICE + LICENSE 三件套（美港股版）：
1. LICENSE 文件存在且大小约 10,760 B
2. LICENSE 含 Apache-2.0 标准头部
3. NOTICE 含上游归属 + Modified 段
4. NOTICE 含商标声明
5. NOTICE 含第三方数据源声明（5 个：Yahoo / Alpha Vantage / SEC / HKEXnews / FRED）
6. SKILL.md 含 ## Attribution 段
7. SKILL.md 含 7 层架构完整描述
8. 5 数据源必须覆盖美港股主战场（Yahoo 必选 + SEC/HKEXnews 至少一个）
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pathlib import Path

import pytest
import yaml

BASE = Path(__file__).resolve().parent.parent


def test_license_file_exists_and_size():
    lic = BASE / "LICENSE"
    assert lic.exists(), "LICENSE 文件缺失"
    size = lic.stat().st_size
    assert 10000 <= size <= 12000, f"LICENSE 大小异常 {size} B（应 ~10760）"


def test_license_is_apache_2_0():
    lic = (BASE / "LICENSE").read_text(encoding="utf-8")
    assert "Apache License" in lic
    assert "Version 2.0" in lic
    assert "TERMS AND CONDITIONS" in lic


def test_notice_has_upstream_attribution():
    notice = (BASE / "NOTICE").read_text(encoding="utf-8")
    assert "simonlin1212" in notice
    assert "global-stock-data" in notice
    assert "Apache-2.0" in notice or "Apache 2.0" in notice


def test_notice_has_modified_segment():
    notice = (BASE / "NOTICE").read_text(encoding="utf-8")
    assert "Modified" in notice
    assert "dragon-engine" in notice or "天龙引擎" in notice or "天蟒引擎" in notice


def test_notice_has_trademark_clause():
    notice = (BASE / "NOTICE").read_text(encoding="utf-8")
    assert "商标" in notice or "Trademark" in notice or "trademark" in notice.lower()


def test_notice_has_third_party_api_clause():
    notice = (BASE / "NOTICE").read_text(encoding="utf-8")
    refs = ["Yahoo Finance", "Alpha Vantage", "SEC EDGAR", "HKEXnews", "FRED"]
    hits = sum(1 for r in refs if r in notice)
    assert hits >= 5, f"第三方源声明不全，命中 {hits}/5（应 >= 5）"


def test_skill_md_has_attribution_section():
    skill = (BASE / "SKILL.md").read_text(encoding="utf-8")
    assert "## Attribution" in skill
    assert "simonlin1212" in skill
    assert "Apache-2.0" in skill or "Apache License" in skill


def test_skill_md_7_layers_documented():
    skill = (BASE / "SKILL.md").read_text(encoding="utf-8")
    for i in range(1, 8):
        assert f"L{i}" in skill, f"SKILL.md 缺 L{i} 层描述"


def test_source_priority_5_sources():
    import json
    with open(BASE / "source_priority.json", encoding="utf-8") as f:
        cfg = json.load(f)
    sources = cfg["sources"]
    required = ["yahoo_finance", "alpha_vantage", "sec_edgar", "hkexnews", "fred"]
    for r in required:
        assert r in sources, f"source_priority.json 缺数据源 {r}"


def test_yahoo_alphavantage_sec_or_hkexnews_present():
    import json
    with open(BASE / "source_priority.json", encoding="utf-8") as f:
        cfg = json.load(f)
    sources = cfg["sources"]
    assert "yahoo_finance" in sources
    has_us_official = "sec_edgar" in sources
    has_hk_official = "hkexnews" in sources
    assert has_us_official or has_hk_official, "美股/港股官方源至少缺一"