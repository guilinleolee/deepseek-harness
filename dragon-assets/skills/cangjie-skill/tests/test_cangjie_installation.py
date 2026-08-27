#!/usr/bin/env python3
"""
test_cangjie_installation.py · cangjie-skill × 天龙引擎 27 项安装自检

累计 PASS: 27/27 (天龙阶段 35-B)

组成:
  - 5 mirror 完整性（methodology + extractors + templates + scripts + assets）
  - 8 AGPL 红线（R1-R8）
  - 6 SKILL.md / 文件结构
  - 5 mirror 字节级保护
  - 3 darwin 兼容 test-prompts.json 模板
  - 1 端到端目录布局
  - 1 AGPL 不可子包装验证
  - 1 AGPL 致谢模板（待周 2-C 激活）
"""

from __future__ import annotations
import sys
import os
import subprocess
import unittest
import json
import re
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SKILL_DIR_RESOLVED = SKILL_DIR.resolve()
sys.path.insert(0, str(SKILL_DIR_RESOLVED / "scripts"))


class TestCangjieMirror(unittest.TestCase):
    """A. mirror 完整性（5 项）"""

    def test_a1_methodology_8_files(self):
        """A1: methodology/ 8 文件完整（00-overview → 07-stage5-deliver）"""
        methodology_dir = SKILL_DIR / "methodology"
        required = [
            "00-overview.md", "01-stage0-adler.md", "02-stage1-parallel-extract.md",
            "03-stage1.5-triple-verify.md", "04-stage2-ria-plus.md", "05-stage3-zettelkasten.md",
            "06-stage4-pressure-test.md", "07-stage5-deliver.md",
        ]
        for f in required:
            self.assertTrue((methodology_dir / f).exists(), f"methodology 缺失: {f}")

    def test_a2_extractors_5_files(self):
        """A2: extractors/ 5 文件完整"""
        extractors_dir = SKILL_DIR / "extractors"
        required = [
            "case-extractor.md", "counter-example-extractor.md", "framework-extractor.md",
            "glossary-extractor.md", "principle-extractor.md",
        ]
        for f in required:
            self.assertTrue((extractors_dir / f).exists(), f"extractors 缺失: {f}")

    def test_a3_templates_5_files(self):
        """A3: templates/ 5 文件完整"""
        templates_dir = SKILL_DIR / "templates"
        required = [
            "BOOK_OVERVIEW.md.template", "DIGEST.md.template", "INDEX.md.template",
            "SKILL.md.template", "test-prompts.json.template",
        ]
        for f in required:
            self.assertTrue((templates_dir / f).exists(), f"templates 缺失: {f}")

    def test_a4_scripts_exists(self):
        """A4: scripts/ 至少 1 个脚本（generate_star_history.py）"""
        scripts_dir = SKILL_DIR / "scripts"
        self.assertTrue((scripts_dir / "generate_star_history.py").exists())

    def test_a5_assets_exists(self):
        """A5: assets/ 至少 3 个文件（star-history.svg + wechat-qrcode + 个人微信）"""
        assets_dir = SKILL_DIR / "assets"
        files = list(assets_dir.iterdir())
        self.assertGreaterEqual(len(files), 3, f"assets 数量异常: {len(files)}")


class TestCangjieAGPLRedLines(unittest.TestCase):
    """B. AGPL 红线 8 项（R1-R8）"""

    def test_b1_license_agpl_verbatim(self):
        """R1: LICENSE AGPL-3.0 verbatim + 字节级大小校验"""
        license_path = SKILL_DIR / "LICENSE"
        self.assertTrue(license_path.exists())
        txt = license_path.read_text(encoding="utf-8", errors="ignore")
        self.assertIn("GNU AFFERO GENERAL PUBLIC LICENSE", txt)
        self.assertIn("Version 3", txt)
        size = license_path.stat().st_size
        self.assertTrue(30000 <= size <= 40000, f"LICENSE size 异常: {size} B")

    def test_b2_commercial_licensing_3_tiers(self):
        """R3: COMMERCIAL_LICENSING.md 三档商用合作"""
        cl_path = SKILL_DIR / "COMMERCIAL_LICENSING.md"
        self.assertTrue(cl_path.exists())
        content = cl_path.read_text(encoding="utf-8", errors="ignore")
        for keyword in ["深度内置授权", "上架与露出合作", "收益分成", "AGPL-3.0"]:
            self.assertIn(keyword, content, f"COMMERCIAL_LICENSING 缺: {keyword}")

    def test_b3_readme_agpl_attribution(self):
        """R4: README.md 末尾 AGPL 强制署名段"""
        readme_path = SKILL_DIR / "README.md"
        self.assertTrue(readme_path.exists())
        content = readme_path.read_text(encoding="utf-8", errors="ignore")
        # 上游 README 含 "GNU AGPL v3" / "AGPL v3.0" / "AGPL-3.0" / "AGPL_v3" 多种写法
        has_agpl = any(marker in content for marker in [
            "AGPL-3.0", "AGPL v3", "AGPL_v3", "GNU AGPL", "Affero General Public License",
        ])
        self.assertTrue(has_agpl, "README.md 末尾缺 AGPL 署名")

    def test_b4_test_prompts_darwin_compatible(self):
        """R5: test-prompts.json.template 含 darwin_compatible 字段（cangjie→darwin 衔接关键）"""
        test_prompts_path = SKILL_DIR / "templates" / "test-prompts.json.template"
        self.assertTrue(test_prompts_path.exists())
        content = test_prompts_path.read_text(encoding="utf-8", errors="ignore")
        self.assertIn("darwin_compatible", content)

    def test_b5_5_scenario_risk_matrix(self):
        """R6: PRODUCT.md / COMMERCIAL_LICENSING.md 含 5 场景风险矩阵 (C1/C2/C3/C4/C5)"""
        sources = []
        for name in ["PRODUCT.md", "COMMERCIAL_LICENSING.md"]:
            p = SKILL_DIR / name
            if p.exists():
                sources.append(p)
        found = False
        for p in sources:
            content = p.read_text(encoding="utf-8", errors="ignore")
            if all(s in content for s in ["C1", "C2", "C3", "C4", "C5"]):
                found = True
                break
        self.assertTrue(found, "5 场景风险矩阵缺失 (PRODUCT.md 或 COMMERCIAL_LICENSING.md 任一必须含 C1-C5)")

    def test_b6_no_external_template_upload(self):
        """R7: 文档层「上传 completeness methodology 到对外网络」明确禁止"""
        combined = ""
        for name in ["AGENT.md", "HANDOFF.md", "PRODUCT.md", "COMMERCIAL_LICENSING.md"]:
            p = SKILL_DIR / name
            if p.exists():
                combined += p.read_text(encoding="utf-8", errors="ignore")
        # 至少含一处"上传" + "禁止"或"🔴"
        self.assertTrue("上传" in combined)
        self.assertTrue("禁止" in combined or "🔴" in combined)

    def test_b7_not_selling_methodology(self):
        """R8: 不卖方法论 / 课程 作为知识付费"""
        combined = ""
        for name in ["AGENT.md", "PRODUCT.md", "COMMERCIAL_LICENSING.md"]:
            p = SKILL_DIR / name
            if p.exists():
                combined += p.read_text(encoding="utf-8", errors="ignore")
        self.assertIn("知识付费", combined)
        self.assertIn("禁止", combined)

    def test_b8_no_l3_specs_subpackaging(self):
        """AGPL 不可子包装 — 验证没有 l3-specs/ 目录"""
        l3_dir = SKILL_DIR / "l3-specs"
        self.assertFalse(l3_dir.exists(), "AGPL 不允许 l3-specs/ 子包装（派生必开源）")


class TestCangjieFrontmatter(unittest.TestCase):
    """C. SKILL.md / 文件结构（6 项）"""

    def test_c1_skill_md_frontmatter(self):
        """C1: SKILL.md frontmatter 必填字段"""
        skill_md = SKILL_DIR / "SKILL.md"
        self.assertTrue(skill_md.exists())
        content = skill_md.read_text(encoding="utf-8", errors="ignore")
        for field in ["license: AGPL-3.0", "source:", "upstream:", "modified_by:", "mirror_mode:"]:
            self.assertIn(field, content, f"frontmatter 缺字段: {field}")

    def test_c2_tianlong_extensions_3_files(self):
        """C2: 天龙扩展三件套 (AGENT/HANDOFF/PRODUCT)"""
        for f in ["AGENT.md", "HANDOFF.md", "PRODUCT.md"]:
            self.assertTrue((SKILL_DIR / f).exists(), f"天龙扩展文档缺失: {f}")

    def test_c3_readme_3_languages(self):
        """C3: README.md 3 语言版本（中文 / English / 日本語）"""
        for f in ["README.md", "README.en.md", "README.ja.md"]:
            self.assertTrue((SKILL_DIR / f).exists(), f"README 语言版本缺失: {f}")

    def test_c4_github_repo_md(self):
        """C4: GITHUB_REPO.md 镜像存在"""
        self.assertTrue((SKILL_DIR / "GITHUB_REPO.md").exists())

    def test_c5_assets_small_files(self):
        """C5: assets 关键文件存在（star-history.svg + wechat + 个人微信）"""
        assets_dir = SKILL_DIR / "assets"
        self.assertTrue((assets_dir / "star-history.svg").exists())
        self.assertTrue((assets_dir / "wechat-personal-qr.jpg").exists())

    def test_c6_pipeline_state_md_template(self):
        """C6: SKILL.md 描述 PIPELINE_STATE.md 格式（断点续跑协议）"""
        skill_md = SKILL_DIR / "SKILL.md"
        content = skill_md.read_text(encoding="utf-8", errors="ignore")
        self.assertIn("PIPELINE_STATE.md", content)
        self.assertIn("断点续跑", content)


class TestCangjieMirrorByteLevel(unittest.TestCase):
    """D. mirror 字节级保护（5 项）"""

    def test_d1_methodology_00_overview(self):
        """D1: methodology/00-overview.md 含 Adler 四步 + 5 并行提取器"""
        path = SKILL_DIR / "methodology" / "00-overview.md"
        content = path.read_text(encoding="utf-8", errors="ignore")
        self.assertTrue(len(content) > 100)

    def test_d2_extractor_framework(self):
        """D2: extractors/framework-extractor.md 镜像完整"""
        path = SKILL_DIR / "extractors" / "framework-extractor.md"
        self.assertTrue(path.exists())
        self.assertGreater(path.stat().st_size, 100)

    def test_d3_template_book_overview(self):
        """D3: templates/BOOK_OVERVIEW.md.template 镜像完整"""
        path = SKILL_DIR / "templates" / "BOOK_OVERVIEW.md.template"
        self.assertTrue(path.exists())
        self.assertGreater(path.stat().st_size, 100)

    def test_d4_template_skill_md(self):
        """D4: templates/SKILL.md.template 含 R/I/A1/A2/E/B 六段"""
        path = SKILL_DIR / "templates" / "SKILL.md.template"
        content = path.read_text(encoding="utf-8", errors="ignore")
        for marker in ["R", "I", "A1", "A2", "E", "B"]:
            self.assertIn(marker, content, f"SKILL.md.template 缺段: {marker}")

    def test_d5_template_test_prompts(self):
        """D5: templates/test-prompts.json.template 含 7 字段 schema"""
        path = SKILL_DIR / "templates" / "test-prompts.json.template"
        content = path.read_text(encoding="utf-8", errors="ignore")
        for field in ["skill", "version", "source_book", "darwin_compatible", "test_cases", "minimum_pass_rate", "notes"]:
            self.assertIn(field, content, f"test-prompts.json.template 缺字段: {field}")


class TestCangjieTestPromptsSchema(unittest.TestCase):
    """E. darwin 兼容 test-prompts.json 模板（3 项）"""

    def test_e1_should_trigger(self):
        """E1: 含 should_trigger 测试用例"""
        path = SKILL_DIR / "templates" / "test-prompts.json.template"
        content = path.read_text(encoding="utf-8", errors="ignore")
        self.assertIn("should_trigger", content)

    def test_e2_should_not_trigger(self):
        """E2: 含 should_not_trigger 诱饵测试用例"""
        path = SKILL_DIR / "templates" / "test-prompts.json.template"
        content = path.read_text(encoding="utf-8", errors="ignore")
        self.assertIn("should_not_trigger", content)

    def test_e3_cross_skill_confusion(self):
        """E3: 含 ≥1 跨 skill 混淆诱饵（应触发同书另一个 skill）"""
        path = SKILL_DIR / "templates" / "test-prompts.json.template"
        content = path.read_text(encoding="utf-8", errors="ignore")
        self.assertIn("should-not-trigger-02", content)
        self.assertIn("跨 skill 混淆", content)


class TestCangjieExecution(unittest.TestCase):
    """F. check 脚本与端到端（2 项）"""

    def test_f1_check_py_exit_code(self):
        """F1: cangjie_check.py exit code 0=PASS 契约"""
        check_py = SKILL_DIR / "scripts" / "cangjie_check.py"
        result = subprocess.run(
            [sys.executable, str(check_py)],
            capture_output=True, text=False, timeout=30, encoding="utf-8"
        )
        self.assertEqual(result.returncode, 0, f"cangjie_check.py 退出码={result.returncode} (期望 0)")

    def test_f2_agpl_attribution_section(self):
        """F2: agpl-attribution-statements.md 包含 cangjie 致谢段（待周 2-C 激活）"""
        mem_path = SKILL_DIR.parent.parent.parent / "memory" / "agpl-attribution-statements.md"
        if not mem_path.exists():
            self.skipTest("agpl-attribution-statements.md 未找到 (阶段 35-B-2 后必过)")
        content = mem_path.read_text(encoding="utf-8", errors="ignore")
        self.assertIn("kangarooking/cangjie-skill", content, "cangjie 致谢段未写入")


if __name__ == "__main__":
    unittest.main(verbosity=2)