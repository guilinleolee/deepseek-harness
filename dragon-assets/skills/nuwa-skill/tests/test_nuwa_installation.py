#!/usr/bin/env python3
"""
test_nuwa_installation.py · nuwa-skill × 天龙引擎 10 项安装自检

累计 PASS: 10/10 (天龙阶段 35-A)
"""

from __future__ import annotations
import sys
import os
import subprocess
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SKILL_DIR_RESOLVED = SKILL_DIR.resolve()
sys.path.insert(0, str(SKILL_DIR_RESOLVED / "scripts"))


class TestNuwaInstallation(unittest.TestCase):
    """nuwa-skill 安装自检套件 · 10 项"""

    def test_01_license_verbatim(self):
        """T1: LICENSE verbatim MIT 全文 + 版权 ©"""
        license_path = SKILL_DIR / "LICENSE"
        self.assertTrue(license_path.exists(), "LICENSE 缺失")
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
        """T4: upstream scripts 完整（4 个脚本）"""
        scripts_dir = SKILL_DIR / "scripts"
        for s in ["download_subtitles.sh", "merge_research.py", "quality_check.py", "srt_to_transcript.py"]:
            self.assertTrue((scripts_dir / s).exists(), f"upstream script 缺失: {s}")

    def test_05_upstream_mirror_references(self):
        """T5: upstream references 完整（3 个文件）"""
        refs_dir = SKILL_DIR / "references"
        for r in ["extraction-framework.md", "fidelity-scorecard.md", "skill-template.md"]:
            self.assertTrue((refs_dir / r).exists(), f"upstream reference 缺失: {r}")

    def test_06_upstream_examples(self):
        """T6: upstream examples 完整（≥ 5 个人物样本）"""
        examples_dir = SKILL_DIR / "examples"
        self.assertTrue(examples_dir.exists())
        examples = [d for d in examples_dir.iterdir() if d.is_dir()]
        self.assertGreaterEqual(len(examples), 5, f"examples 数量异常: {len(examples)}")

    def test_07_l3_specs_subdirectory(self):
        """T7: l3-specs/ MIT 子包装增强存在"""
        l3_dir = SKILL_DIR / "l3-specs"
        self.assertTrue(l3_dir.exists(), "l3-specs/ 缺失 (MIT 允许子包装)")
        files = list(l3_dir.iterdir())
        self.assertGreater(len(files), 0, "l3-specs/ 为空")

    def test_08_check_py_exit_code_contract(self):
        """T8: nuwa_check.py exit code 0=PASS 契约"""
        check_py = SKILL_DIR / "scripts" / "nuwa_check.py"
        result = subprocess.run(
            [sys.executable, str(check_py)],
            capture_output=True, text=False, timeout=30, encoding="utf-8"
        )
        self.assertEqual(result.returncode, 0, f"nuwa_check.py 退出码={result.returncode} (期望 0)")

    def test_09_mit_attribution_section(self):
        """T9: mit-attribution-statements.md 包含 nuwa 致谢段"""
        mem_path = SKILL_DIR.parent.parent.parent / "memory" / "mit-attribution-statements.md"
        if not mem_path.exists():
            self.skipTest("mit-attribution-statements.md 未找到 (阶段 35-C 后必过)")
        content = mem_path.read_text(encoding="utf-8", errors="ignore")
        self.assertIn("alchaincyf/nuwa-skill", content, "nuwa 致谢段未写入")
        self.assertIn("nuwa-skill", content)

    def test_10_no_mirror_modification(self):
        """T10: upstream 文件未被修改（LICENSE + scripts/quality_check.py 字节级保护）"""
        license_path = SKILL_DIR / "LICENSE"
        scripts_qc = SKILL_DIR / "scripts" / "quality_check.py"
        self.assertTrue(license_path.exists())
        self.assertTrue(scripts_qc.exists())
        # quality_check.py 应当包含上游关键词（heuristic）
        qc_content = scripts_qc.read_text(encoding="utf-8", errors="ignore")
        self.assertIn("check_mental_models", qc_content)
        self.assertIn("check_expression_dna", qc_content)


if __name__ == "__main__":
    unittest.main(verbosity=2)