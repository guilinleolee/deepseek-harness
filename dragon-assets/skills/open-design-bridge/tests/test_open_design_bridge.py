"""
open-design-bridge V1.0 · Stage 49.4 Apache 重量档 · 15+ unittest
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

import open_design_bridge as od  # noqa: E402


class TestLocalFirstConfig(unittest.TestCase):
    """#1 local-first config"""

    def test_default_valid(self):
        cfg = od.LocalFirstConfig()
        self.assertEqual(cfg.validate(), [])

    def test_offline_first_false_flagged(self):
        cfg = od.LocalFirstConfig(offline_first=False)
        issues = cfg.validate()
        self.assertEqual(len(issues), 1)
        self.assertIn("offline_first", issues[0])

    def test_byok_only_false_flagged(self):
        cfg = od.LocalFirstConfig(byok_only=False)
        issues = cfg.validate()
        self.assertEqual(len(issues), 1)
        self.assertIn("byok", issues[0])


class TestCLIDetect(unittest.TestCase):
    """#2 20+ CLIs BYOK"""

    def test_supported_count(self):
        self.assertGreaterEqual(len(od.SUPPORTED_CLIS), 20)

    def test_dsh_present(self):
        dsh = [c for c in od.SUPPORTED_CLIS if c["name"] == "deepseek"]
        self.assertEqual(len(dsh), 1)
        self.assertEqual(dsh[0]["api_key_env"], "DEEPSEEK_API_KEY")

    def test_detect_clis_returns_list(self):
        clis = od.detect_installed_clis()
        self.assertEqual(len(clis), len(od.SUPPORTED_CLIS))
        for c in clis:
            self.assertIsInstance(c.installed, bool)
            self.assertIsInstance(c.api_key_present, bool)


class TestSandboxValidation(unittest.TestCase):
    """#3 sandboxed preview path"""

    def test_tmp_allowed(self):
        self.assertTrue(od.validate_preview_sandbox("/tmp/foo.html"))

    def test_workspace_allowed(self):
        self.assertTrue(od.validate_preview_sandbox("/workspace/x/y"))

    def test_preview_dir_allowed(self):
        self.assertTrue(od.validate_preview_sandbox("./.preview/index.html"))

    def test_root_blocked(self):
        self.assertFalse(od.validate_preview_sandbox("/etc/passwd"))

    def test_home_blocked(self):
        self.assertFalse(od.validate_preview_sandbox("/home/user/file"))


class TestSkillTemplate(unittest.TestCase):
    """#4 design skill template"""

    def test_default_borrows_from_nexu_io(self):
        # 函数签名默认 borrowed_from='nexu-io/open-design'
        sk = od.generate_design_skill_template("hero-section")
        self.assertEqual(sk.name, "hero-section")
        self.assertEqual(sk.borrows_from, "nexu-io/open-design")
        self.assertIn(".html", sk.stream_artifacts)

    def test_custom_borrowed(self):
        sk = od.generate_design_skill_template("dashboard", borrowed_from="custom-source")
        self.assertEqual(sk.borrows_from, "custom-source")


class TestApacheNotice(unittest.TestCase):
    """#5 Apache-2.0 NOTICE template"""

    def test_notice_contains_basics(self):
        notice = od.APACHE_NOTICE_TEMPLATE
        self.assertIn("Apache", notice)
        self.assertIn("nexu-io", notice)

    def test_notice_marker_for_modified(self):
        # 检查 'Modifications by dragon-engine'（注意大小写 + 复数 'Modifications'）
        notice = od.APACHE_NOTICE_TEMPLATE
        self.assertIn("Modifications by dragon-engine", notice)


class TestEndToEnd(unittest.TestCase):
    """#6 end-to-end integration"""

    def test_workflow(self):
        cfg = od.LocalFirstConfig()
        self.assertEqual(cfg.validate(), [])
        clis = od.detect_installed_clis()
        self.assertGreater(len(clis), 0)
        self.assertTrue(od.validate_preview_sandbox("/tmp/design.html"))
        sk = od.generate_design_skill_template("test")
        self.assertIsNotNone(sk)


if __name__ == "__main__":
    unittest.main(verbosity=2)
