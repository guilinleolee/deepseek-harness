"""
dsh-eval-bridge V1.0 · 5 unittest
"""
import os
import sys
import unittest
from unittest.mock import MagicMock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

import dsh_eval_bridge as eb  # noqa: E402


class TestBenchmarkParse(unittest.TestCase):
    """#1 benchmark YAML schema 借鉴校验"""

    def test_basic_parse(self):
        yaml_text = """
name: skill-regression
model: deepseek-v4
profile: headless
trials: 3
cases:
  - id: fix-tests-001
    prompt: Fix the failing tests in this workspace.
    workspace: ./fixtures/fix-tests
    expected:
      tool: bash
      check: ./check.sh
  - id: write-doc-002
    prompt: Write a README.
"""
        bm = eb.parse_benchmark_yaml(yaml_text)
        self.assertEqual(bm.name, "skill-regression")
        self.assertEqual(bm.model, "deepseek-v4")
        self.assertEqual(bm.trials, 3)
        self.assertEqual(len(bm.cases), 2)
        self.assertEqual(bm.cases[0].expected_tool, "bash")
        self.assertEqual(bm.cases[0].expected_check, "./check.sh")

    def test_missing_top_key_fails(self):
        with self.assertRaises(ValueError):
            eb.parse_benchmark_yaml("""
model: deepseek-v4
profile: headless
cases: []
""")

    def test_missing_case_key_fails(self):
        with self.assertRaises(ValueError):
            eb.parse_benchmark_yaml("""
name: x
model: deepseek-v4
profile: headless
cases:
  - prompt: missing id
""")


class TestMetricCompute(unittest.TestCase):
    """#2 11 类评测指标计算"""

    def _make_trials(self, n_pass: int, n: int):
        return [
            eb.TrialResult(
                case_id="x", trial_idx=i,
                task_success=(i < n_pass), tool_success=True,
                tool_selection_correct=(i < n_pass),
                actual_tool="deepseek-v4",
                steps=3 + i,
                input_tokens=10_000, output_tokens=5_000,
                latency_ms=1500 + i * 10, ttft_ms=200,
                final_answer="ok", judge_score=0.8,
            ) for i in range(n)
        ]

    def test_task_success_rate(self):
        t = self._make_trials(n_pass=3, n=5)
        m = eb.compute_case_metrics(t)
        self.assertEqual(m["task_success_rate"], 0.6)  # 3/5

    def test_p95_latency(self):
        t = self._make_trials(n_pass=5, n=5)
        m = eb.compute_case_metrics(t)
        # lat = 1500,1510,1520,1530,1540 → p95 = index=3 → 1530
        self.assertEqual(m["latency_p95_ms"], 1530)

    def test_cost_with_pricing(self):
        # 1 trial: input=10k × 0.27/1M = 0.0027, output=5k × 1.10/1M = 0.0055
        t = self._make_trials(n_pass=1, n=1)
        for tr in t:
            tr.cost_usd = eb.compute_cost_usd(tr, {
                "deepseek-v4": {
                    "inputUsdPerMTokens": 0.27,
                    "outputUsdPerMTokens": 1.10,
                    "cacheReadUsdPerMTokens": 0.07,
                    "cacheWriteUsdPerMTokens": 0.27,
                }
            })
        m = eb.compute_case_metrics(t)
        self.assertAlmostEqual(m["total_cost_usd"], 0.0082, places=4)


class TestJudgeParse(unittest.TestCase):
    """#3 LLM judge strict JSON schema 解析"""

    def test_valid_verdict(self):
        v = eb.parse_judge_verdict('{"score": 0.85, "hallucinated": false, "comment": "good"}')
        self.assertEqual(v["score"], 0.85)
        self.assertFalse(v["hallucinated"])
        self.assertEqual(v["comment"], "good")

    def test_markdown_wrapped(self):
        # judge 输出常包在 ```json ... ```
        v = eb.parse_judge_verdict('```json\n{"score":0.5,"hallucinated":true,"comment":"missed key point"}\n```')
        self.assertEqual(v["score"], 0.5)
        self.assertTrue(v["hallucinated"])

    def test_invalid_json_fallback(self):
        v = eb.parse_judge_verdict("not json at all")
        self.assertEqual(v["score"], 0.0)  # 容错默认
        self.assertTrue(v["hallucinated"])
        self.assertIn("failed", v["comment"])

    def test_score_out_of_range_clamped(self):
        v = eb.parse_judge_verdict('{"score": 1.5, "hallucinated": false, "comment": "too high"}')
        self.assertEqual(v["score"], 1.0)  # clamped


class TestPairedAB(unittest.TestCase):
    """#4 paired A/B 计算"""

    def test_b_wins(self):
        run_a = {"cases": [
            {"case_id": "c1", "task_success_rate": 0.5},
            {"case_id": "c2", "task_success_rate": 0.7},
        ]}
        run_b = {"cases": [
            {"case_id": "c1", "task_success_rate": 0.7},  # B 高 0.2 → B WIN
            {"case_id": "c2", "task_success_rate": 0.5},  # B 低 0.2 → A WIN
        ]}
        result = eb.paired_ab_compare(run_a, run_b)
        self.assertEqual(result["summary"]["B_win"], 1)
        self.assertEqual(result["summary"]["A_win"], 1)
        self.assertEqual(result["summary"]["tie"], 0)
        self.assertEqual(result["summary"]["total"], 2)

    def test_signed_delta(self):
        run_a = {"cases": [{"case_id": "c1", "task_success_rate": 0.5}]}
        run_b = {"cases": [{"case_id": "c1", "task_success_rate": 0.8}]}
        result = eb.paired_ab_compare(run_a, run_b)
        self.assertEqual(result["common_cases"][0]["delta"], 0.3)  # B-A = +0.3

    def test_no_common_cases(self):
        run_a = {"cases": [{"case_id": "x", "task_success_rate": 0.5}]}
        run_b = {"cases": [{"case_id": "y", "task_success_rate": 0.5}]}
        result = eb.paired_ab_compare(run_a, run_b)
        self.assertEqual(result["common_cases"], [])


class TestJudgePromptBuild(unittest.TestCase):
    """#5 judge prompt 生成（schema 借鉴）"""

    def test_prompt_has_required_fields(self):
        prompt = eb.build_judge_prompt(
            case_prompt="Fix the tests",
            expected={"tool": "bash", "check": "./check.sh"},
            actual_answer="Done!",
        )
        self.assertIn("Fix the tests", prompt)
        self.assertIn('"tool"', prompt)
        self.assertIn('"bash"', prompt)
        self.assertIn("Done!", prompt)
        self.assertIn("score", prompt)
        self.assertIn("hallucinated", prompt)


if __name__ == "__main__":
    unittest.main(verbosity=2)
