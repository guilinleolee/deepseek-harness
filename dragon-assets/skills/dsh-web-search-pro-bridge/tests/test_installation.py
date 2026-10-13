"""
dsh-web-search-pro-bridge 安装测试套件 V1.0（阶段 40）

5 PASS：
  test_01_skill_md_exists            — SKILL.md 存在
  test_02_license_verbatim           — LICENSE 与上游 SHA256 一致
  test_03_notice_modified            — NOTICE 含 "Modified by dragon-engine"
  test_04_eleven_tools_documented    — SKILL.md 11 工具全部提及
  test_05_check_script_runs          — check 脚本退出码契约 0/1/2/3

退出码契约与 check.py 一致。
"""
from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SKILL_MD = ROOT / "SKILL.md"
LICENSE = ROOT / "LICENSE"
NOTICE = ROOT / "NOTICE"
CHECK_SCRIPT = ROOT / "scripts" / "dsh_web_search_pro_check.py"


def test_01_skill_md_exists() -> None:
    """SKILL.md exists and is non-empty."""
    assert SKILL_MD.is_file(), f"SKILL.md not found at {SKILL_MD}"
    text = SKILL_MD.read_text(encoding="utf-8")
    assert len(text) > 1000, f"SKILL.md too short ({len(text)} bytes)"
    assert "dsh-web-search-pro" in text
    assert "name: dsh-web-search-pro-bridge" in text


def test_02_license_verbatim() -> None:
    """LICENSE matches upstream anweat/dsh-web-search-pro master branch verbatim.

    Expected: 1088 B, MIT, sha256=88538D9C1577EC39BE72824B460B17473BFC3CF5B72FBC0DB52610761A649AC5.
    """
    assert LICENSE.is_file(), f"LICENSE not found at {LICENSE}"
    content = LICENSE.read_bytes()
    assert len(content) == 1088, f"LICENSE size mismatch: {len(content)} B (expected 1088)"
    digest = hashlib.sha256(content).hexdigest()
    assert (
        digest == "88538d9c1577ec39be72824b460b17473bfc3cf5b72fbc0db52610761a649ac5"
    ), f"LICENSE sha256 mismatch: {digest}"
    # MIT keyword check
    text = content.decode("utf-8")
    assert "MIT License" in text
    assert "Copyright (c) 2026 dsh-web-search-pro contributors" in text


def test_03_notice_modified() -> None:
    """NOTICE contains attribution + 'Modified by dragon-engine' line."""
    assert NOTICE.is_file(), f"NOTICE not found at {NOTICE}"
    text = NOTICE.read_text(encoding="utf-8")
    assert "anweat" in text.lower(), "NOTICE must credit anweat upstream"
    assert "Modified by dragon-engine" in text, "NOTICE missing modified-by line"
    assert "MIT" in text, "NOTICE must mention MIT license"


def test_04_eleven_tools_documented() -> None:
    """SKILL.md references all 11 dsh-web-search-pro tools."""
    text = SKILL_MD.read_text(encoding="utf-8")
    required_tools = [
        "web_search_pro",
        "web_fetch_pro",
        "web_platform_search",
        "web_snapshot",
        "web_history",
        "web_cache_clear",
        "web_search_stats",
        "web_rule",
        "web_exa_contents",
        "web_backend_status",
        "web_deps",
    ]
    missing = [t for t in required_tools if t not in text]
    assert not missing, f"SKILL.md missing tools: {missing}"
    # Must mention all 19 platforms collectively (at least 12 sampled)
    platforms_sample = [
        "GitHub", "B站", "YouTube", "V2EX", "小红书", "Twitter", "Reddit",
        "Instagram", "Facebook", "RSS", "知乎", "微博", "豆瓣", "贴吧",
        "抖音", "快手",
    ]
    missing_platforms = [p for p in platforms_sample if p not in text]
    assert len(missing_platforms) <= 2, f"Too many missing platforms: {missing_platforms}"


def test_05_check_script_runs() -> None:
    """check.py exits with one of the contracted exit codes {0,1,2,3}."""
    assert CHECK_SCRIPT.is_file(), f"check script not found at {CHECK_SCRIPT}"
    proc = subprocess.run(
        [sys.executable, str(CHECK_SCRIPT), "--json"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    # exit code must be 0/1/2/3
    assert proc.returncode in (0, 1, 2, 3), (
        f"unexpected exit code {proc.returncode}; "
        f"stderr={proc.stderr[:200]!r}"
    )
    # JSON output must be parseable
    import json

    payload = json.loads(proc.stdout)
    assert "status" in payload
    assert payload["status"] == proc.returncode, (
        f"JSON status {payload['status']} != exit code {proc.returncode}"
    )
    # Must include diagnostic keys
    assert "dsh_home" in payload
    assert "installed" in payload
    assert "bundles" in payload


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
