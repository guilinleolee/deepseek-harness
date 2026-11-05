"""
anysearch V3.1 — DSH bridge probe tests (stage 40.1)

2 PASS:
  test_dsh_bridge_probe_exits_cleanly — bridge check.py exits {0,1,2,3}
  test_routing_rules_present_in_skill_md — SKILL.md mentions DSH bridge routing table
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

SKILL_MD = Path(__file__).resolve().parents[1] / "SKILL.md"
BRIDGE_CHECK = (
    Path(__file__).resolve().parents[2]
    / "dsh-web-search-pro-bridge"
    / "scripts"
    / "dsh_web_search_pro_check.py"
)


def test_dsh_bridge_probe_exits_cleanly() -> None:
    """Bridge probe check.py exits with one of {0,1,2,3} contracted codes."""
    if not BRIDGE_CHECK.is_file():
        pytest.skip(f"Bridge check not found at {BRIDGE_CHECK}")
    proc = subprocess.run(
        [sys.executable, str(BRIDGE_CHECK)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode in (0, 1, 2, 3), (
        f"unexpected exit {proc.returncode}; "
        f"stdout={proc.stdout[:200]!r}, stderr={proc.stderr[:200]!r}"
    )
    # Sanity: stdout should mention DSH_HOME or status
    out = proc.stdout.lower()
    assert ("status=" in out) or ("dsh_home" in out), (
        f"unrecognized output: {proc.stdout[:200]!r}"
    )


def test_routing_rules_present_in_skill_md() -> None:
    """SKILL.md must declare the V3.1 DSH bridge routing table."""
    assert SKILL_MD.is_file()
    text = SKILL_MD.read_text(encoding="utf-8")
    # Must reference the new V3.1 frontmatter bump
    assert "version: 3.1.0" in text
    # Must have the new "DSH bridge probe" section
    assert "DSH bridge probe" in text
    # Must enumerate the routing states
    required_states = [
        "DSH + bridge probe exit=0",
        "Not DSH",
        "Use DSH bridge",
    ]
    for state in required_states:
        assert state in text, f"missing routing state: {state!r}"
    # Must reference the probe command path
    assert "dsh_web_search_pro_check.py" in text
    # Must include the bridge limitations table
    assert "Bridge limitations" in text
    assert "Vertical sub-domains" in text


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
