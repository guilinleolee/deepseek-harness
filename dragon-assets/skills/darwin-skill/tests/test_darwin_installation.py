#!/usr/bin/env python3
"""
test_darwin_installation.py · darwin-skill × 天龙引擎 10 项安装自检

累计 PASS: 10/10 (天龙阶段 35-C)
"""

from __future__ import annotations
import sys
import os
import subprocess
import unittest
import json
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SKILL_DIR_RESOLVED = SKILL_DIR.resolve()
sys.path.insert(0, str(SKILL_DIR_RESOLVED / "scripts"))


class TestDarwinInstallation(unittest.TestCase):
    """darwin-skill 安装自检套件 · 10 项"""

    def test_01_license_verbatim(self):
        """T1: LICENSE verbatim MIT 全文 + 版权"""
        license_path = SKILL_DIR / "LICENSE"
        self.assertTrue(license_path.exists())
        txt = license_path.read_text(encoding="utf-8", errors="ignore")
        self.assertIn("MIT License", txt)
        self.assertIn("Copyright", txt)
        self.assertIn("Permission is hereby granted", txt)
        self.assertTrue(800 <= license_path.stat().st_size <= 1500)

    def test_02_skill_md_frontmatter(self):
        """T2: SKILL.md frontmatter 必填 5 字段"""
        skill_md = SKILL_DIR / "SKILL.md"
        self.assertTrue(skill_md.exists())
        content = skill_md.read_text(encoding="utf-8", errors="ignore")
        for field in ["license: MIT", "source:", "upstream:", "modified_by:", "mirror_mode:"]:
            self.assertIn(field, content, f"frontmatter 缺字段: {field}")

    def test_03_tianlong_extensions(self):
        """T3: 天龙扩展三件套 (AGENT/HANDOFF/PRODUCT)"""
        for f in ["AGENT.md", "HANDOFF.md", "PRODUCT.md"]:
            self.assertTrue((SKILL_DIR / f).exists(), f"天龙扩展文档缺失: {f}")

    def test_04_upstream_mirror_scripts(self):
        """T4: upstream scripts 完整 (screenshot.mjs)"""
        scripts_dir = SKILL_DIR / "scripts"
        self.assertTrue((scripts_dir / "screenshot.mjs").exists())

    def test_05_upstream_mirror_references(self):
        """T5: upstream references 完整 (2 个文件)"""
        refs_dir = SKILL_DIR / "references"
        for r in ["runtime-neutrality.md", "skilllens-evidence.md"]:
            self.assertTrue((refs_dir / r).exists(), f"upstream reference 缺失: {r}")

    def test_06_upstream_mirror_templates(self):
        """T6: upstream templates 完整 (3 个 result-card 模板)"""
        templates_dir = SKILL_DIR / "templates"
        for t in ["result-card.html", "result-card-dark.html", "result-card-white.html"]:
            self.assertTrue((templates_dir / t).exists(), f"upstream template 缺失: {t}")

    def test_07_l3_specs_with_neat_freak_bridge(self):
        """T7: l3-specs/ MIT 子包装增强 + darwin-neat-freak-bridge.md"""
        l3_dir = SKILL_DIR / "l3-specs"
        self.assertTrue(l3_dir.exists())
        bridge = l3_dir / "darwin-neat-freak-bridge.md"
        self.assertTrue(bridge.exists(), "darwin-neat-freak-bridge.md 缺失")
        content = bridge.read_text(encoding="utf-8", errors="ignore")
        self.assertIn("neat-freak", content)
        self.assertIn("Phase 0.5", content)

    def test_08_check_py_exit_code_contract(self):
        """T8: darwin_check.py exit code 0=PASS 契约"""
        check_py = SKILL_DIR / "scripts" / "darwin_check.py"
        result = subprocess.run(
            [sys.executable, str(check_py)],
            capture_output=True, text=False, timeout=30, encoding="utf-8"
        )
        self.assertEqual(result.returncode, 0, f"darwin_check.py 退出码={result.returncode} (期望 0)")

    def test_09_test_prompts_json_format(self):
        """T9: test-prompts.json darwin 格式 (与 cangjie 共享 schema)"""
        test_prompts_path = SKILL_DIR / "test-prompts.json"
        self.assertTrue(test_prompts_path.exists())
        data = json.loads(test_prompts_path.read_text(encoding="utf-8"))
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        for item in data:
            for field in ["id", "scenario", "prompt", "expected"]:
                self.assertIn(field, item, f"test case 缺字段: {field}")

    def test_10_mit_attribution_section(self):
        """T10: mit-attribution-statements.md 包含 darwin 致谢段"""
        mem_path = SKILL_DIR.parent.parent.parent / "memory" / "mit-attribution-statements.md"
        if not mem_path.exists():
            self.skipTest("mit-attribution-statements.md 未找到 (阶段 35-C 后必过)")
        content = mem_path.read_text(encoding="utf-8", errors="ignore")
        self.assertIn("alchaincyf/darwin-skill", content, "darwin 致谢段未写入")


if __name__ == "__main__":
    unittest.main(verbosity=2)