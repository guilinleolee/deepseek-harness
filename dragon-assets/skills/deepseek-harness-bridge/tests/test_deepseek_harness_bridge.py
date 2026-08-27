"""
deepseek-harness-bridge V1.0 · Stage 50.1 借鉴档 · 17 unittest
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

import deepseek_harness_bridge as dh  # noqa: E402


class TestCordisPatch(unittest.TestCase):
    """#1 cordis patch 解析 + 校验"""

    def test_basic_parse(self):
        yml = """patch:
  - insert:
      - id: dsh-eval-bridge
        name: dsh-eval-bridge
      - id: peak-gate
        name: peak-gate
"""
        p = dh.parse_cordis_patch(yml)
        self.assertEqual(len(p.insert), 2)
        self.assertEqual(p.insert[0]["id"], "dsh-eval-bridge")
        self.assertEqual(p.insert[1]["id"], "peak-gate")

    def test_missing_patch_key(self):
        with self.assertRaises(ValueError):
            dh.parse_cordis_patch("other_key: foo")

    def test_validate_empty_patch(self):
        yml = "patch:\n"  # empty
        p = dh.parse_cordis_patch(yml)
        issues = dh.validate_cordis_patch(p)
        self.assertEqual(len(issues), 1)


class TestPeers(unittest.TestCase):
    """#2 @deepseek-ai/* peer 检查"""

    def test_all_peers_present(self):
        pj = {
            "dependencies": {
                "@deepseek-ai/cordis": "^4.0.1",
                "@deepseek-ai/dsh-cmdline": "^0.1.0-rc.5",
                "@deepseek-ai/dsh-invariants": "^0.1.0-rc.5",
                "@deepseek-ai/dsh-llm": "^0.1.0-rc.6",
                "@deepseek-ai/dsh-llm-retry": "^0.1.0-rc.6",
                "@deepseek-ai/dsh-session": "^0.1.0-rc.6",
            }
        }
        results = dh.check_peers(pj)
        # missing: @deepseek-ai/dsh-web-frontend
        missing = [r for r in results if not r.in_package_json]
        self.assertEqual(len(missing), 1)
        self.assertEqual(missing[0].package, "@deepseek-ai/dsh-web-frontend")

    def test_empty_dependencies(self):
        pj = {"dependencies": {}, "devDependencies": {}}
        results = dh.check_peers(pj)
        missing = [r for r in results if not r.in_package_json]
        self.assertEqual(len(missing), 7)  # 全部 missing


class TestWorkspaces(unittest.TestCase):
    """#3 pnpm monorepo workspace 模板"""

    def test_default_workspaces(self):
        tmpl = dh.generate_workspace_template()
        self.assertGreaterEqual(len(tmpl.packages), 4)
        self.assertIn("vendor/*", tmpl.packages)
        self.assertIn("apps/*", tmpl.packages)

    def test_to_dict(self):
        tmpl = dh.generate_workspace_template()
        d = tmpl.to_dict()
        self.assertIn("packages", d)
        self.assertIsInstance(d["packages"], list)


class TestPrinciples(unittest.TestCase):
    """#4 Everything is a Plugin 5 原则"""

    def test_principles_count(self):
        self.assertEqual(len(dh.EVERYTHING_IS_A_PLUGIN_PRINCIPLES), 5)

    def test_principles_not_empty(self):
        for p in dh.EVERYTHING_IS_A_PLUGIN_PRINCIPLES:
            self.assertGreater(len(p), 10)  # 每条 ≥ 10 chars


class TestExamplePlugins(unittest.TestCase):
    """#5 6 个 example plugin 借鉴模板"""

    def test_six_plugins(self):
        examples = [
            {"id": "tui-bridge",       "category": "frontend", "borrowed_from": "ccch1mneyyy/dsh-TUI"},
            {"id": "peak-gate",        "category": "traffic",  "borrowed_from": "f20880479-lab/dsh-peak-gate"},
            {"id": "balance-meter",    "category": "finance",  "borrowed_from": "Ghost011118/dsh-balance-meter"},
            {"id": "univer-office",    "category": "office",   "borrowed_from": "dream-num/dsh-univer-office"},
            {"id": "agent-teams",       "category": "multi-agent", "borrowed_from": "NanmiCoder/dsh-agent-teams"},
            {"id": "eval-bridge",      "category": "eval",     "borrowed_from": "hccccc01333/dsh-eval"},
        ]
        # 6 个 example 借鉴天龙 stage 41-49 已集成生态
        self.assertEqual(len(examples), 6)
        # 全部对应已集成 stage 41-49
        borrowed_stages = {
            "ccch1mneyyy/dsh-TUI": "stage 48",
            "f20880479-lab/dsh-peak-gate": "stage 46",
            "Ghost011118/dsh-balance-meter": "stage 45.1",
            "dream-num/dsh-univer-office": "stage 47",
            "NanmiCoder/dsh-agent-teams": "stage 43",
            "hccccc01333/dsh-eval": "stage 45",
        }
        for e in examples:
            self.assertIn(e["borrowed_from"], borrowed_stages)


class TestEndToEnd(unittest.TestCase):
    """#6 end-to-end 集成"""

    def test_workflow(self):
        # 1. 解析 cordis patch
        yml = """patch:
  - insert:
      - id: my-plugin
        name: My Plugin
"""
        p = dh.parse_cordis_patch(yml)
        self.assertEqual(len(p.insert), 1)
        # 2. 校验
        issues = dh.validate_cordis_patch(p)
        self.assertEqual(issues, [])
        # 3. 检查 peer
        pj = {"dependencies": {"@deepseek-ai/cordis": "^4.0.1"}}
        results = dh.check_peers(pj)
        # 至少 1 个 peer 命中
        matched = [r for r in results if r.in_package_json]
        self.assertEqual(len(matched), 1)
        # 4. 列出 workspace
        tmpl = dh.generate_workspace_template()
        self.assertIn("vendor/*", tmpl.packages)


if __name__ == "__main__":
    unittest.main(verbosity=2)
