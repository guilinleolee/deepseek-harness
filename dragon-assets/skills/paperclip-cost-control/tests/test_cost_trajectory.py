"""
paperclip-cost-control V2.0 · cost-trajectory.py 5 unittest
"""
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

import cost_trajectory as ct  # noqa: E402


class TestEstimateMath(unittest.TestCase):
    """#1 cost 数学"""

    def test_basic_deepseek(self):
        # DeepSeek 输入 1M tokens = 0.14 USD
        i, o, total, cpt = ct.estimate_cost(
            input_tokens=1_000_000, output_tokens=0,
            price={"input": 0.14, "output": 0.28},
        )
        self.assertAlmostEqual(i, 0.14)
        self.assertAlmostEqual(o, 0.0)
        self.assertAlmostEqual(total, 0.14)
        self.assertAlmostEqual(cpt, 1.4e-7)

    def test_zero_tokens_handling(self):
        i, o, total, cpt = ct.estimate_cost(
            input_tokens=0, output_tokens=0,
            price={"input": 0.14, "output": 0.28},
        )
        self.assertEqual(total, 0.0)
        self.assertEqual(i, 0.0)
        self.assertEqual(o, 0.0)
        # token=0 时，cpt 不应 inf 或 nan
        self.assertTrue(cpt == 0.0)

    def test_50_50_split(self):
        i, o, total, _ = ct.estimate_cost(
            input_tokens=50_000, output_tokens=20_000,
            price={"input": 0.14, "output": 0.28},
        )
        # 50k input = 0.007, 20k output = 0.0056
        self.assertAlmostEqual(i, 0.007, places=4)
        self.assertAlmostEqual(o, 0.0056, places=4)


class TestMockFallback(unittest.TestCase):
    """#2 trajectory-debug 不可用时 fallback mock"""

    def test_mock_returns_sensible(self):
        pt = ct.PriceTable()
        # 不传 rpc，调用会失败，应当走 mock
        cb = ct.estimate_session_cost(session_id="x", price_table=pt)
        self.assertEqual(cb.provider, "deepseek")
        self.assertGreater(cb.total_cost_usd, 0)
        self.assertEqual(cb.session_id, "x")


class TestRPCSuccess(unittest.TestCase):
    """#3 trajectory-debug RPC 成功调用"""

    def test_real_rpc_returns_perf_data(self):
        # mock DshTrajectoryRPC
        mock_rpc = MagicMock()
        mock_rpc.call.return_value = {
            "ok": True,
            "value": {
                "tokens_by_provider": {"openai": {"input": 100_000, "output": 40_000}},
                "ttl_latency_ms": 5000,
                "by_step": [{"seq": 1, "cost": 0.001}, {"seq": 2, "cost": 0.002}],
            },
        }
        pt = ct.PriceTable()
        cb = ct.estimate_session_cost(
            session_id="y", price_table=pt, rpc=mock_rpc,
        )
        self.assertEqual(cb.provider, "openai")
        # 100k input × $2.50/M = 0.25, 40k output × $10.00/M = 0.4 → total 0.65
        self.assertAlmostEqual(cb.total_cost_usd, 0.65, places=3)
        self.assertEqual(len(cb.by_step_top_5), 2)


class TestMonthlyCompare(unittest.TestCase):
    """#4 月环比"""

    def test_compare_with_mocked_rpc(self):
        with patch.object(ct, "DshTrajectoryRPC") as mock_cls:
            mock_rpc = mock_cls.return_value
            # 注意：mock 返回 key 是 primary_provider 且 tokens 是 dict
            mock_rpc.call.side_effect = [
                {"ok": True, "value": {
                    "tokens": {"input": 1_000_000, "output": 500_000},
                    "primary_provider": "deepseek",
                }},
                {"ok": True, "value": {
                    "tokens": {"input": 2_000_000, "output": 1_000_000},
                    "primary_provider": "deepseek",
                }},
            ]
            result = ct.monthly_cost_compare(days=30)
            self.assertIn("current_cost_usd", result)
            self.assertIn("delta_pct", result)
            # current = 1M × 0.14 + 500k × 0.28 = 0.14 + 0.14 = 0.28
            # prev    = 2M × 0.14 + 1M × 0.28 = 0.28 + 0.28 = 0.56
            # delta   = (0.28 - 0.56) / max(0.56, 0.01) × 100 ≈ -50%
            self.assertAlmostEqual(result["delta_pct"], -50.0, places=0)


class TestQuote(unittest.TestCase):
    """#5 报价生成"""

    def test_quote_markdown_contains_session(self):
        pt = ct.PriceTable()
        md = ct.generate_quote(
            session_id="abc12345xyz", retail_markup_pct=30, currency="CNY",
            price_table=pt,
        )
        self.assertIn("abc12345", md)
        self.assertIn("CNY", md)
        self.assertIn("加价", md)


if __name__ == "__main__":
    unittest.main(verbosity=2)
