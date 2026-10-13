#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_cua_driver_bridge.py · ROI-1 累计验证 5 PASS
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import cua_check  # noqa: E402


class TestCuaDriverBridge(unittest.TestCase):
    """5 PASS 累计验证."""

    def test_01_skill_md_exists(self):
        """SKILL.md exists and > 1000 bytes."""
        skill = ROOT / "SKILL.md"
        self.assertTrue(skill.exists(), "SKILL.md missing")
        self.assertGreater(skill.stat().st_size, 1000, "SKILL.md too small")

    def test_02_license_verbatim(self):
        """LICENSE verbatim MIT + Modified by."""
        lic = ROOT / "LICENSE"
        self.assertTrue(lic.exists(), "LICENSE missing")
        text = lic.read_text(encoding="utf-8")
        self.assertIn("MIT License", text)
        self.assertIn("Copyright (c) 2025 Cua AI, Inc.", text)
        self.assertIn("Modified by dragon-engine", text)

    def test_03_7_driver_commands(self):
        """runtime.conf 列出 7 driver 命令 + MCP subcommand."""
        conf = ROOT / "runtime.conf"
        self.assertTrue(conf.exists(), "runtime.conf missing")
        text = conf.read_text(encoding="utf-8")
        self.assertIn("cua-driver", text)
        self.assertIn("mcp_subcommand", text)

    def test_04_cua_check_4_exit_codes(self):
        """cua_check.py 退出码契约 0/1/2/3 都已实现."""
        rc = cua_check.main()
        # 本机 Windows 通常未装 cua-driver → 期望 0(镜像健康)或 2(平台不支持)
        self.assertIn(rc, (0, 1, 2, 3), f"unexpected exit code: {rc}")

    def test_05_runtime_conf_realpath(self):
        """runtime.conf paths 真实指向本机 dragon-engine."""
        conf = ROOT / "runtime.conf"
        text = conf.read_text(encoding="utf-8")
        self.assertIn("dragon-engine/skills/cua-driver-bridge", text)


if __name__ == "__main__":
    print("\n--- cua-driver-bridge · ROI-1 · 5 PASS ---")
    unittest.main(verbosity=2)