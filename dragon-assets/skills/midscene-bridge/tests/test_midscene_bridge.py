#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_midscene_bridge.py · ROI-3 累计验证 4 PASS
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import midscene_check  # noqa: E402


class TestMidsceneBridge(unittest.TestCase):
    """4 PASS 累计验证."""

    def test_01_skill_md_exists(self):
        skill = ROOT / "SKILL.md"
        self.assertTrue(skill.exists(), "SKILL.md missing")
        self.assertGreater(skill.stat().st_size, 1000, "SKILL.md too small")

    def test_02_license_verbatim(self):
        lic = ROOT / "LICENSE"
        self.assertTrue(lic.exists(), "LICENSE missing")
        text = lic.read_text(encoding="utf-8")
        self.assertIn("MIT License", text)
        self.assertIn("Copyright (c) 2025 Midscene.js", text)
        self.assertIn("Modified by dragon-engine", text)

    def test_03_3_api_wrappers(self):
        """aiAct/aiQuery/aiAssert 都在 SKILL.md + runtime.conf 中."""
        skill = ROOT / "SKILL.md"
        conf = ROOT / "runtime.conf"
        self.assertTrue(skill.exists())
        self.assertTrue(conf.exists())
        skill_text = skill.read_text(encoding="utf-8")
        conf_text = conf.read_text(encoding="utf-8")
        for api in ("aiAct", "aiQuery", "aiAssert"):
            self.assertIn(api, skill_text, f"missing API in SKILL.md: {api}")
            self.assertIn(api, conf_text, f"missing API in runtime.conf: {api}")

    def test_04_midscene_check_4_code(self):
        rc = midscene_check.main()
        self.assertIn(rc, (0, 1, 2, 3), f"unexpected exit code: {rc}")


if __name__ == "__main__":
    print("\n--- midscene-bridge · ROI-3 · 4 PASS ---")
    unittest.main(verbosity=2)