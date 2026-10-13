import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pathlib import Path
import pytest
import yaml


def test_license_file_exists():
    lic = Path(__file__).resolve().parent.parent / "LICENSE"
    assert lic.exists()


def test_license_is_apache_2_0():
    lic_text = (Path(__file__).resolve().parent.parent / "LICENSE").read_text(encoding="utf-8")
    assert "Apache License" in lic_text
    assert "Version 2.0" in lic_text


def test_notice_has_apocdata():
    notice = (Path(__file__).resolve().parent.parent / "NOTICE").read_text(encoding="utf-8")
    assert "ApocData" in notice or "天启至数" in notice


def test_skill_md_has_attribution_section():
    skill = (Path(__file__).resolve().parent.parent / "SKILL.md").read_text(encoding="utf-8")
    assert "## Attribution" in skill or "Apache" in skill


def test_skill_md_has_base_url():
    skill = (Path(__file__).resolve().parent.parent / "SKILL.md").read_text(encoding="utf-8")
    assert "data.tianqis.com" in skill or "apocdata" in skill.lower()


def test_fallback_yaml_silent_failure_false():
    with open(Path(__file__).resolve().parent.parent / "fallback.yaml", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    assert cfg.get("silent_failure") is False


def test_fallback_yaml_official_count():
    with open(Path(__file__).resolve().parent.parent / "fallback.yaml", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    assert cfg.get("official_fallbacks") == 2


def test_fallback_yaml_profile_full_has_fallbacks():
    with open(Path(__file__).resolve().parent.parent / "fallback.yaml", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    assert len(cfg["endpoints"]["profile_full"]) >= 4


def test_skill_md_has_chinese():
    skill = (Path(__file__).resolve().parent.parent / "SKILL.md").read_text(encoding="utf-8")
    assert any('一' <= c <= '鿿' for c in skill)