"""test_apache_notice.py · T5 必检

验证 Apache-2.0 NOTICE + LICENSE 三件套
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pathlib import Path

import pytest


def test_license_file_exists_and_size():
    lic = Path(__file__).resolve().parent.parent / "LICENSE"
    assert lic.exists()
    size = lic.stat().st_size
    assert 10000 <= size <= 12000


def test_license_is_apache_2_0():
    lic = (Path(__file__).resolve().parent.parent / "LICENSE").read_text(encoding="utf-8")
    assert "Apache License" in lic
    assert "Version 2.0" in lic


def test_notice_has_upstream_attribution():
    notice = (Path(__file__).resolve().parent.parent / "NOTICE").read_text(encoding="utf-8")
    assert "simonlin1212" in notice


def test_notice_has_modified_segment():
    notice = (Path(__file__).resolve().parent.parent / "NOTICE").read_text(encoding="utf-8")
    assert "Modified" in notice


def test_notice_has_trademark_clause():
    notice = (Path(__file__).resolve().parent.parent / "NOTICE").read_text(encoding="utf-8")
    assert "商标" in notice or "Trademark" in notice


def test_notice_has_third_party_api_clause():
    notice = (Path(__file__).resolve().parent.parent / "NOTICE").read_text(encoding="utf-8")
    assert "第三方" in notice


def test_skill_md_has_attribution_section():
    skill = (Path(__file__).resolve().parent.parent / "SKILL.md").read_text(encoding="utf-8")
    assert "## Attribution" in skill


def test_no_trademark_in_skill_name():
    skill = (Path(__file__).resolve().parent.parent / "SKILL.md").read_text(encoding="utf-8")
    bad = ["a-stock-data-official", "a-stock-data-官方"]
    for b in bad:
        assert b not in skill