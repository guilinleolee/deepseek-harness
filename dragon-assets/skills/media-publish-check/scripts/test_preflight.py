import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location("preflight", ROOT / "scripts" / "preflight.py")
PREFLIGHT = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(PREFLIGHT)
RULES = PREFLIGHT.load_rules(ROOT / "references" / "term-patterns.json")


class PreflightTests(unittest.TestCase):
    def scan(self, text, platform):
        return PREFLIGHT.scan(text, RULES, platform, 20)

    def test_target_platform_name_is_not_external_name(self):
        cases = {
            "douyin": "这条抖音视频讲三个步骤。",
            "xiaohongshu": "这篇小红书笔记讲三个步骤。",
            "weixin-video-accounts": "这条微信视频号内容讲三个步骤。",
            "kuaishou": "这条快手视频讲三个步骤。",
        }
        for platform, text in cases.items():
            with self.subTest(platform=platform):
                self.assertFalse(any(hit["category"] == "其他平台名称" for hit in self.scan(text, platform)))

    def test_external_name_is_high_priority_in_strict_mode(self):
        hits = self.scan("这件东西是我在淘宝买的。", "douyin")
        self.assertTrue(any(hit["rule_id"] == "external-names-douyin" and hit["priority"] == "high" for hit in hits))

    def test_alias_with_cta_deduplicates_weaker_alias_hit(self):
        hits = self.scan("请去某音搜索阿明。", "xiaohongshu")
        self.assertTrue(any(hit["rule_id"] == "alias-with-diversion" for hit in hits))
        self.assertFalse(any(hit["rule_id"] == "platform-alias-hint" for hit in hits))

    def test_all_scope_does_not_guess_target_platform(self):
        hits = self.scan("抖音、小红书、视频号和快手。", "all")
        self.assertFalse(any(hit["category"] == "其他平台名称" for hit in hits))

    def test_ai_is_candidate_not_final_risk(self):
        hits = self.scan("画面使用AI生成的数字人。", "douyin")
        self.assertTrue(any(hit["rule_id"] == "ai-content-hints" for hit in hits))
        self.assertTrue(all("severity" not in hit for hit in hits))

    def test_medical_and_absolute_claims_are_found(self):
        hits = self.scan("全网第一款100%治失眠产品。", "kuaishou")
        ids = {hit["rule_id"] for hit in hits}
        self.assertIn("absolute-commercial", ids)
        self.assertIn("medical-claims", ids)

    def test_plain_text_has_no_candidate(self):
        self.assertEqual([], self.scan("今天分享三个整理桌面的方法。", "xiaohongshu"))


if __name__ == "__main__":
    unittest.main()
