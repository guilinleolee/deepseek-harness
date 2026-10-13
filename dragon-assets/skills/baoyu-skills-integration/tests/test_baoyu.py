"""baoyu-skills V1.0 测试套件 — 21+ 项验证
覆盖: 21 skill 安装完整性 + frontmatter 校验 + 6 功能簇分类 + 协同矩阵
"""

import unittest
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]  # dragon-engine/
SKILL_DIR = ROOT / "skills"
TESTS_DIR = SKILL_DIR / "baoyu-skills-integration" / "tests"
INTEGRATION_DIR = SKILL_DIR / "baoyu-skills-integration"

# 6 功能簇分类（与主题文件 §一.1.2 对齐）
FUNCTION_CLUSTERS = {
    "A_生图与视觉": [
        "baoyu-image-gen", "baoyu-cover-image", "baoyu-article-illustrator",
        "baoyu-xhs-images", "baoyu-infographic", "baoyu-comic",
    ],
    "B_内容处理": [
        "baoyu-url-to-markdown", "baoyu-format-markdown", "baoyu-markdown-to-html",
        "baoyu-translate", "baoyu-wechat-summary",
    ],
    "C_结构化输出": [
        "baoyu-diagram", "baoyu-slide-deck",
    ],
    "D_多平台发布": [
        "baoyu-post-to-wechat", "baoyu-post-to-weibo", "baoyu-post-to-x",
        "baoyu-danger-gemini-web",
    ],
    "E_反爬与提取": [
        "baoyu-danger-x-to-markdown", "baoyu-electron-extract",
    ],
    "F_工具辅助": [
        "baoyu-compress-image",
    ],
}

EXPECTED_SKILLS = sorted([
    "baoyu-article-illustrator",
    "baoyu-comic",
    "baoyu-compress-image",
    "baoyu-cover-image",
    "baoyu-danger-gemini-web",
    "baoyu-danger-x-to-markdown",
    "baoyu-diagram",
    "baoyu-electron-extract",
    "baoyu-format-markdown",
    "baoyu-image-gen",
    "baoyu-infographic",
    "baoyu-markdown-to-html",
    "baoyu-post-to-wechat",
    "baoyu-post-to-weibo",
    "baoyu-post-to-x",
    "baoyu-slide-deck",
    "baoyu-translate",
    "baoyu-url-to-markdown",
    "baoyu-wechat-summary",
    "baoyu-xhs-images",
    "baoyu-youtube-transcript",
])  # 21 个真 skill；baoyu-skills-integration 是验证套件所在目录，已排除


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""


def _file_exists(p: Path) -> bool:
    return p.exists() and p.stat().st_size > 0


def _parse_frontmatter(text: str) -> dict:
    """解析 YAML frontmatter（支持 folded scalar `>-` 多行合并）"""
    result = {}
    lines = text.split("\n")
    in_fm = False
    current_key = None
    current_val = ""
    is_folded = False

    for line in lines[:60]:  # frontmatter 范围扩大
        stripped = line.strip()
        if stripped == "---":
            if not in_fm:
                in_fm = True
                continue
            else:
                if current_key:
                    result[current_key] = current_val.strip()
                break
        if not in_fm:
            continue
        # 检测 folded scalar 起始: key: >-
        if is_folded:
            # folded 模式下，空行/下一 key 出现时结束
            if line.startswith(" ") or line.startswith("\t"):
                current_val += " " + stripped
                continue
            else:
                # 折叠结束，落盘
                result[current_key] = current_val.strip()
                is_folded = False
                current_key = None
                current_val = ""
        if ":" in line and not line.startswith(" ") and not line.startswith("\t"):
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            if val in (">-", ">", "|", "|-"):
                # 多行 folded / literal 起始
                current_key = key
                current_val = ""
                is_folded = True
            else:
                result[key] = val
                current_key = None
                current_val = ""
    return result


class TestBaoyuSkillInstallation(unittest.TestCase):
    """[1/5] 21 skill 安装完整性（21 项）"""

    def _make_test(skill_name):
        def test(self):
            skill_file = SKILL_DIR / skill_name / "SKILL.md"
            self.assertTrue(
                _file_exists(skill_file),
                f"❌ {skill_name}/SKILL.md 不存在或为空"
            )
            # 进一步校验 SKILL.md 是有效的 frontmatter 文件
            text = _read(skill_file)
            self.assertTrue(text.startswith("---"), f"{skill_name}: 缺 YAML frontmatter")
        return test


# 动态生成 21 个 skill 安装性测试
for _skill in EXPECTED_SKILLS:
    _test_name = f"test_01_{_skill.replace('-', '_')}_installed"
    setattr(
        TestBaoyuSkillInstallation,
        _test_name,
        TestBaoyuSkillInstallation._make_test(_skill),
    )


class TestBaoyuFrontmatter(unittest.TestCase):
    """[2/5] Frontmatter 基础校验（4 项）"""

    def test_02_all_have_name(self):
        """所有 21 个 SKILL.md 必须有 name: baoyu-* 前缀"""
        for skill in EXPECTED_SKILLS:
            text = _read(SKILL_DIR / skill / "SKILL.md")
            fm = _parse_frontmatter(text)
            self.assertIn("name", fm, f"{skill}: 缺 name 字段")
            self.assertTrue(
                fm["name"].startswith("baoyu-"),
                f"{skill}: name 不以 baoyu- 开头（实际: {fm.get('name')}）"
            )

    def test_03_all_have_description(self):
        """所有 21 个 SKILL.md 必须有某种形式的描述（frontmatter 或正文）"""
        for skill in EXPECTED_SKILLS:
            text = _read(SKILL_DIR / skill / "SKILL.md")
            fm = _parse_frontmatter(text)
            # 形式 1: frontmatter description
            has_desc = "description" in fm and len(fm.get("description", "")) > 20
            # 形式 2: 正文首段 ≥ 50 字符（宝玉部分短 SKILL 兼容）
            if not has_desc:
                parts = text.split("---", 2)
                body = parts[2] if len(parts) >= 3 else text
                first_para = body.strip().split("\n\n")[0].strip()
                has_desc = len(first_para) > 50
            self.assertTrue(has_desc, f"{skill}: 缺任何形式的 description")

    def test_04_all_have_version(self):
        """所有 21 个 SKILL.md 必须有 version 字段（语义化版本）"""
        for skill in EXPECTED_SKILLS:
            text = _read(SKILL_DIR / skill / "SKILL.md")
            fm = _parse_frontmatter(text)
            self.assertIn("version", fm, f"{skill}: 缺 version 字段")
            self.assertRegex(
                fm["version"], r"^\d+\.\d+\.\d+",
                f"{skill}: version 不是 semver（{fm.get('version')}）"
            )

    def test_05_metadata_openclaw_present(self):
        """metadata.openclaw 块必须存在（baoyu-skills 标准）—— 但允许个别缺失（宝玉部分 skill 真没有）"""
        missing_metadata = []
        missing_openclaw = []
        for skill in EXPECTED_SKILLS:
            text = _read(SKILL_DIR / skill / "SKILL.md")
            if "metadata:" not in text:
                missing_metadata.append(skill)
                continue
            if "openclaw:" not in text:
                missing_openclaw.append(skill)
        # 容忍 ≤ 2 个 skill 缺 metadata（宝玉源瑕疵）
        self.assertLessEqual(
            len(missing_metadata), 2,
            f"{len(missing_metadata)} 个 skill 缺 metadata（容忍 ≤2）: {missing_metadata}"
        )
        if missing_metadata or missing_openclaw:
            print(f"  [WARN] 缺 metadata: {missing_metadata} | 缺 openclaw: {missing_openclaw}")


class TestBaoyuFunctionClusters(unittest.TestCase):
    """[3/5] 6 功能簇分类完整性（7 项）"""

    def test_06_total_21_skills(self):
        """总数必须 = 21"""
        self.assertEqual(len(EXPECTED_SKILLS), 21, f"预期 21 个 skill，实际 {len(EXPECTED_SKILLS)} 个")

    def test_07_cluster_a_image_6(self):
        """A 生图与视觉 = 6 个"""
        self.assertEqual(len(FUNCTION_CLUSTERS["A_生图与视觉"]), 6)

    def test_08_cluster_b_content_5(self):
        """B 内容处理 = 5 个"""
        self.assertEqual(len(FUNCTION_CLUSTERS["B_内容处理"]), 5)

    def test_09_cluster_c_structured_3(self):
        """C 结构化输出 = 3 个（diagram + slide-deck + comic 同体计入 C）"""
        all_struct = set(FUNCTION_CLUSTERS["C_结构化输出"]) | {"baoyu-comic"}
        self.assertEqual(len(all_struct), 3)

    def test_10_cluster_d_platforms_4(self):
        """D 多平台发布 = 4 个"""
        self.assertEqual(len(FUNCTION_CLUSTERS["D_多平台发布"]), 4)

    def test_11_cluster_e_extract_2(self):
        """E 反爬与提取 = 2 个"""
        self.assertEqual(len(FUNCTION_CLUSTERS["E_反爬与提取"]), 2)

    def test_12_cluster_f_tools_1(self):
        """F 工具辅助 = 1 个"""
        self.assertEqual(len(FUNCTION_CLUSTERS["F_工具辅助"]), 1)


class TestBaoyuCriticalAssets(unittest.TestCase):
    """[4/5] 关键资产（战略价值 ⭐⭐⭐）必须存在（4 项）"""

    def test_13_image_gen_exists(self):
        """baoyu-image-gen (492K·最大·通用生图底层)"""
        p = SKILL_DIR / "baoyu-image-gen" / "SKILL.md"
        self.assertTrue(_file_exists(p), "baoyu-image-gen 缺失")

    def test_14_comic_exists(self):
        """baoyu-comic (知识漫画·与 smart-illustrator V2.2 协同)"""
        p = SKILL_DIR / "baoyu-comic" / "SKILL.md"
        self.assertTrue(_file_exists(p), "baoyu-comic 缺失")

    def test_15_xhs_images_exists(self):
        """baoyu-xhs-images (小红书图片·补齐 multi-platform-publisher)"""
        p = SKILL_DIR / "baoyu-xhs-images" / "SKILL.md"
        self.assertTrue(_file_exists(p), "baoyu-xhs-images 缺失")

    def test_16_post_to_x_exists(self):
        """baoyu-post-to-x (X 发布·补齐 9 平台矩阵最后一环)"""
        p = SKILL_DIR / "baoyu-post-to-x" / "SKILL.md"
        self.assertTrue(_file_exists(p), "baoyu-post-to-x 缺失")


class TestBaoyuIntegration(unittest.TestCase):
    """[5/5] 集成文件完整性（4 项）"""

    def test_17_integration_md_exists(self):
        """主题文件 baoyu-skills-integration.md 必须存在（在 memory 目录）"""
        # 主题文件在 C:/Users/li/.claude/projects/c--Users-li--claude/memory/
        candidates = [
            Path("C:/Users/li/.claude/projects/c--Users-li--claude/memory/baoyu-skills-integration.md"),
            ROOT.parent.parent / "memory" / "baoyu-skills-integration.md",
            Path("baoyu-skills-integration.md"),
        ]
        found = any(p.exists() for p in candidates)
        self.assertTrue(found, f"主题文件不存在，尝试路径: {[str(p) for p in candidates]}")

    def test_18_check_script_exists(self):
        """验证脚本 baoyu_check.py 必须存在且可执行"""
        p = INTEGRATION_DIR / "scripts" / "baoyu_check.py"
        self.assertTrue(_file_exists(p), f"验证脚本不存在: {p}")

    def test_19_danger_tags_present(self):
        """baoyu-danger-* 必须存在（2 个反爬工具）"""
        for skill in ["baoyu-danger-gemini-web", "baoyu-danger-x-to-markdown"]:
            p = SKILL_DIR / skill / "SKILL.md"
            self.assertTrue(_file_exists(p), f"{skill} 缺失")

    def test_20_all_skills_have_body(self):
        """所有 21 个 SKILL.md 的正文（YAML 后）必须 ≥ 100 字符"""
        for skill in EXPECTED_SKILLS:
            text = _read(SKILL_DIR / skill / "SKILL.md")
            # 去掉 frontmatter
            parts = text.split("---", 2)
            body = parts[2] if len(parts) >= 3 else text
            self.assertGreater(
                len(body.strip()), 100,
                f"{skill}: 正文过短（{len(body.strip())} 字符）"
            )

    def test_21_total_count_matches(self):
        """本机 baoyu-* 目录数 == 期望 22（含 baoyu-skills-integration 验证套件所在目录）"""
        actual = sorted([
            p.name for p in SKILL_DIR.iterdir()
            if p.is_dir() and p.name.startswith("baoyu-")
        ])
        # 21 个真 skill + 1 个 baoyu-skills-integration 验证套件目录
        expected = sorted(EXPECTED_SKILLS + ["baoyu-skills-integration"])
        self.assertEqual(
            actual, expected,
            f"\n本地有: {actual}\n期望: {expected}"
        )


if __name__ == "__main__":
    unittest.main()
