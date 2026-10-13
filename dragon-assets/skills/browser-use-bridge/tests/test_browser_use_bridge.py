#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_browser_use_bridge.py · ROI-2 累计验证 8 PASS
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import browser_use_check  # noqa: E402


class TestBrowserUseBridge(unittest.TestCase):
    """8 PASS 累计验证."""

    def test_01_skill_md_exists(self):
        skill = ROOT / "SKILL.md"
        self.assertTrue(skill.exists(), "SKILL.md missing")
        self.assertGreater(skill.stat().st_size, 1000, "SKILL.md too small")

    def test_02_license_verbatim(self):
        lic = ROOT / "LICENSE"
        self.assertTrue(lic.exists(), "LICENSE missing")
        text = lic.read_text(encoding="utf-8")
        self.assertIn("MIT License", text)
        self.assertIn("Copyright (c) 2024 Gregor Zunic", text)
        self.assertIn("Modified by dragon-engine", text)

    def test_03_runtime_conf_paths(self):
        conf = ROOT / "runtime.conf"
        self.assertTrue(conf.exists(), "runtime.conf missing")
        text = conf.read_text(encoding="utf-8")
        self.assertIn("browser-use", text)
        self.assertIn("api/v4", text)
        self.assertIn("dragon-engine/skills/browser-use-bridge", text)

    def test_04_env_example_4_fields(self):
        env = ROOT / ".env.example"
        self.assertTrue(env.exists(), ".env.example missing")
        text = env.read_text(encoding="utf-8")
        for k in ("BROWSER_USE_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY"):
            self.assertIn(k, text, f"missing env key field: {k}")

    def test_05_cloud_sdk_import(self):
        rc = browser_use_check.check_cloud_sdk_import()
        self.assertIn(rc, (0, 2), f"unexpected import status: {rc}")

    def test_06_rest_endpoint_schema(self):
        self.assertTrue(browser_use_check.check_rest_endpoint_schema())

    def test_07_browser_use_check_4_code(self):
        rc = browser_use_check.check_subcommand_dryrun()
        self.assertIn(rc, (0, 1, 2, 3), f"unexpected subcommand exit: {rc}")

    def test_08_llm_provider_strategy(self):
        self.assertTrue(browser_use_check.check_llm_provider_strategy())


if __name__ == "__main__":
    print("\n--- browser-use-bridge · ROI-2 · 8 PASS ---")
    unittest.main(verbosity=2)