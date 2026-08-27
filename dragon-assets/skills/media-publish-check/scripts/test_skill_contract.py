import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
ALL_MD = "\n".join(path.read_text(encoding="utf-8") for path in ROOT.rglob("*.md"))


class SkillContractTests(unittest.TestCase):
    def test_four_platforms_present(self):
        for name in ("抖音", "小红书", "视频号", "快手"):
            self.assertIn(name, SKILL)

    def test_exact_two_quick_conclusions_present(self):
        self.assertIn("审核没问题，可以直接发。", SKILL)
        self.assertIn("不建议直接发。", SKILL)

    def test_six_way_short_video_labels_present(self):
        for label in (
            "含有虚构演绎内容",
            "含有AI生成内容",
            "含有营销信息",
            "内容为转载",
            "内容为个人观点",
            "无需标注",
        ):
            self.assertIn(label, ALL_MD)

    def test_no_stale_three_platform_mode(self):
        for phrase in ("三平台适配", "目标平台：[抖音/小红书/微信视频号/三平台]", "只列三平台"):
            self.assertNotIn(phrase, ALL_MD)

    def test_no_alias_pass_guarantee(self):
        for phrase in ("别名即可过审", "某音可以过审", "橙色软件可以过审", "只说一次就能过审"):
            self.assertNotIn(phrase, ALL_MD)

    def test_xingtu_specialist_is_optional_and_scoped(self):
        module = ROOT / "references" / "douyin-xingtu-diversion.md"
        text = module.read_text(encoding="utf-8")
        self.assertTrue(module.exists())
        self.assertIn("可选", text)
        self.assertIn("不取代", text)
        for code in ("DYX-01", "DYX-02", "DYX-03", "DYX-04", "DYX-05", "DYX-06", "DYX-07"):
            self.assertIn(code, text)

    def test_personal_memory_is_opt_in_and_local_only(self):
        module = ROOT / "references" / "personal-account-memory.md"
        text = module.read_text(encoding="utf-8")
        self.assertTrue(module.exists())
        self.assertIn("只在用户明确开启后使用", text)
        self.assertIn("不包含网络请求", text)
        self.assertIn("候选提醒", text)
        self.assertIn("不自动生效", text)

    def test_local_markdown_links_resolve(self):
        for path in (ROOT / "SKILL.md", *ROOT.joinpath("references").glob("*.md")):
            text = path.read_text(encoding="utf-8")
            for target in re.findall(r"\[[^\]]+\]\(([^)]+\.md)\)", text):
                with self.subTest(source=path.name, target=target):
                    self.assertTrue((path.parent / target).resolve().exists())


if __name__ == "__main__":
    unittest.main()
