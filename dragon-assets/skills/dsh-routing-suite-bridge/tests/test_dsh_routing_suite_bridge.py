"""
dsh-routing-suite-bridge V1.0 · Stage 51.1 借鉴档 · 14 unittest
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

import dsh_routing_suite_bridge as rs  # noqa: E402


class TestReasoningModes(unittest.TestCase):
    """#1 4 类 reasoning-mode router preset"""

    def test_default_modes_count(self):
        self.assertEqual(len(rs.DEFAULT_MODES), 4)

    def test_modes_have_names(self):
        names = [m.name for m in rs.DEFAULT_MODES]
        self.assertEqual(names, ["spec", "react", "mixed", "weak"])

    def test_spec_mode(self):
        spec = rs.DEFAULT_MODES[0]
        self.assertEqual(spec.name, "spec")
        self.assertIn("Pro", spec.suitable_models)
        self.assertEqual(spec.expected_gain_pct, 5.0)

    def test_react_mode(self):
        react = rs.DEFAULT_MODES[1]
        self.assertEqual(react.name, "react")
        self.assertIn("Flash", react.suitable_models)
        self.assertEqual(react.expected_gain_pct, 5.7)

    def test_mixed_mode_is_trap(self):
        mixed = rs.DEFAULT_MODES[2]
        self.assertEqual(mixed.expected_gain_pct, 0.0)
        self.assertEqual(len(mixed.suitable_models), 0)


class TestValidateBehavior(unittest.TestCase):
    """#2 4 类路由行为带校验"""

    def test_valid_behaviors(self):
        for b in ["spec", "react", "mixed", "weak"]:
            self.assertTrue(rs.validate_behavior(b))

    def test_invalid_behaviors(self):
        for b in ["unknown", "Spec", "REACT", ""]:
            self.assertFalse(rs.validate_behavior(b))


class TestEvalP1P23(unittest.TestCase):
    """#3 P1-P23 评测框架"""

    def test_parse_p_id(self):
        self.assertEqual(rs.parse_p_id("P1"), 1)
        self.assertEqual(rs.parse_p_id("P15"), 15)
        self.assertEqual(rs.parse_p_id("P23"), 23)

    def test_parse_invalid_p_id(self):
        self.assertEqual(rs.parse_p_id("invalid"), 0)

    def test_filter_eval_by_model(self):
        results = [
            rs.EvalResult(p_id="P1", task="t1", mode="pro", success=True, gain_pct=5.0, notes="Pro model"),
            rs.EvalResult(p_id="P2", task="t2", mode="flash", success=True, gain_pct=6.0, notes="Flash model"),
            rs.EvalResult(p_id="P3", task="t3", mode="pro", success=False, gain_pct=4.0, notes="Pro model"),
        ]
        pro_only = rs.filter_eval_by_model(results, "pro")
        self.assertEqual(len(pro_only), 2)
        self.assertTrue(all("Pro" in r.notes for r in pro_only))


class TestInstallSteps(unittest.TestCase):
    """#4 install.ps1 三步"""

    def test_three_steps(self):
        self.assertEqual(len(rs.INSTALL_STEPS), 3)
        for step in rs.INSTALL_STEPS:
            self.assertTrue(step.startswith(tuple("123")))


class TestRuntimeInjectorConfig(unittest.TestCase):
    """#5 Runtime injector 配置"""

    def test_default_config(self):
        cfg = rs.RuntimeInjectorConfig()
        self.assertEqual(cfg.version, "0.3.3")
        self.assertGreaterEqual(len(cfg.dev_tools), 5)
        self.assertIn("dev_inject", cfg.dev_tools)

    def test_reload_strategy(self):
        cfg = rs.RuntimeInjectorConfig()
        self.assertIn(cfg.reload_strategy, ["hot", "soft", "restart"])


class TestEndToEnd(unittest.TestCase):
    """#6 end-to-end 集成"""

    def test_workflow(self):
        # 1. 列出 4 类 router mode
        self.assertEqual(len(rs.DEFAULT_MODES), 4)
        # 2. 校验行为带
        self.assertTrue(rs.validate_behavior("spec"))
        self.assertFalse(rs.validate_behavior("unknown"))
        # 3. 解析 P1-P23
        for i in range(1, 24):
            self.assertEqual(rs.parse_p_id(f"P{i}"), i)
        # 4. install 3 步
        self.assertEqual(len(rs.INSTALL_STEPS), 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
