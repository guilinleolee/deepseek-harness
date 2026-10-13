#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_page_agent_bridge.py · ROI-5 累计验证 3 PASS
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import page_agent_check  # noqa: E402


class TestPageAgentBridge(unittest.TestCase):
    """3 PASS 累计验证."""

    def test_01_skill_md_exists(self):
        skill = ROOT / "SKILL.md"
        self.assertTrue(skill.exists(), "SKILL.md missing")
        self.assertGreater(skill.stat().st_size, 1000, "SKILL.md too small")

    def test_02_license_verbatim(self):
        lic = ROOT / "LICENSE"
        self.assertTrue(lic.exists(), "LICENSE missing")
        text = lic.read_text(encoding="utf-8")
        self.assertIn("MIT License", text)
        self.assertIn("Copyright (c) 2025 Alibaba", text)
        self.assertIn("Modified by dragon-engine", text)
        self.assertIn("browser-use", text, "missing upstream browser-use attribution")

    def test_03_cdn_runtime_paths(self):
        conf = ROOT / "runtime.conf"
        self.assertTrue(conf.exists(), "runtime.conf missing")
        text = conf.read_text(encoding="utf-8")
        self.assertIn("cdn.jsdelivr.net", text)
        self.assertIn("page-agent@1.12.2", text)
        self.assertIn("qwen3.5-plus", text)
        self.assertIn("dragon-engine/skills/page-agent-bridge", text)

    def test_04_no_demo_cdn_bundled(self):
        """Mirror must NOT bundle demo CDN (per ROI-5 user decision 2026-08-26)."""
        conf = ROOT / "runtime.conf"
        text = conf.read_text(encoding="utf-8")
        self.assertIn("does NOT bundle demo", text, "demo CDN policy declaration missing")


if __name__ == "__main__":
    print("\n--- page-agent-bridge · ROI-5 · 3 PASS ---")
    unittest.main(verbosity=2)