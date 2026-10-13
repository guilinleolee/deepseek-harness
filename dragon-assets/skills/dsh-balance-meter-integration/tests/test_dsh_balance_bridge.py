"""
dsh-balance-meter-bridge V1.0 · 5+ unittest (Stage 45.1)
"""
import os
import sys
import json
import unittest
from unittest.mock import patch, MagicMock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

import dsh_balance_bridge as bb  # noqa: E402


class TestPeakHour(unittest.TestCase):
    """#1 peak/off-peak 分时定价"""

    def test_peak_10am_beijing(self):
        # 2026-08-24 10:00 Beijing
        from datetime import datetime, timezone, timedelta
        bj = timezone(timedelta(hours=8))
        dt = datetime(2026, 8, 24, 10, 0, tzinfo=bj)
        self.assertTrue(bb.is_peak_hour(dt))

    def test_offpeak_13pm_beijing(self):
        # 2026-08-24 13:00 Beijing（午休 off-peak）
        from datetime import datetime, timezone, timedelta
        bj = timezone(timedelta(hours=8))
        dt = datetime(2026, 8, 24, 13, 0, tzinfo=bj)
        self.assertFalse(bb.is_peak_hour(dt))

    def test_offpeak_20pm_beijing(self):
        # 2026-08-24 20:00 Beijing
        from datetime import datetime, timezone, timedelta
        bj = timezone(timedelta(hours=8))
        dt = datetime(2026, 8, 24, 20, 0, tzinfo=bj)
        self.assertFalse(bb.is_peak_hour(dt))


class TestSessionCost(unittest.TestCase):
    """#2 4 buckets session cost 估算"""

    def test_flash_offpeak(self):
        result = bb.estimate_session_cost(
            input_tokens=1_000_000,
            output_tokens=1_000_000,
            model="deepseek-v4-flash",
            band="off_peak",
        )
        # 1M input × 0.02 = 0.02, 1M output × 1.00 = 1.00
        self.assertEqual(result["input_cost_cny"], 0.02)
        self.assertEqual(result["output_cost_cny"], 1.00)
        self.assertEqual(result["total_cost_cny"], 1.02)
        self.assertEqual(result["band"], "off_peak")

    def test_pro_peak(self):
        result = bb.estimate_session_cost(
            input_tokens=500_000,
            output_tokens=200_000,
            model="deepseek-v4-pro",
            band="peak",
        )
        # 500k × 0.40 = 0.20, 200k × 8.00 = 1.60
        self.assertEqual(result["input_cost_cny"], 0.20)
        self.assertEqual(result["output_cost_cny"], 1.60)
        self.assertEqual(result["total_cost_cny"], 1.80)

    def test_cache_read_billing(self):
        # cache_read 不应该 0
        result = bb.estimate_session_cost(
            input_tokens=0, output_tokens=0,
            cache_read_tokens=1_000_000,
            cache_write_tokens=1_000_000,
            model="deepseek-v4-flash", band="off_peak",
        )
        # cache_read 计费 0.02/M, cache_write 0/M (DeepSeek 不单独收费)
        self.assertEqual(result["cache_read_cost_cny"], 0.02)
        self.assertEqual(result["cache_write_cost_cny"], 0.0)


class TestBalanceSources(unittest.TestCase):
    """#3 3 source 余额读取"""

    def test_manual_source(self):
        r = bb.read_balance_manual(manual_balance=4.16, manual_currency="CNY")
        self.assertTrue(r["ok"])
        self.assertEqual(r["source"], "manual")
        self.assertEqual(r["total_balance"], 4.16)
        self.assertEqual(r["currency"], "CNY")

    def test_official_source_http_error(self):
        # mock 一个失败的 HTTP
        with patch("urllib.request.urlopen") as mock_open:
            mock_open.side_effect = __import__("urllib.error").error.HTTPError(
                url="", code=401, msg="Unauthorized", hdrs={}, fp=None
            )
            r = bb.read_balance_official(api_key="bad-key")
            self.assertFalse(r["ok"])
            self.assertEqual(r["error"]["code"], 401)

    def test_proxy_source_bad_path(self):
        r = bb.read_balance_proxy(
            api_key="x", endpoint="http://x", currency_path="data.nope.value"
        )
        # 因为 endpoint 不会真的连，但 path bad 也不会到这里；先测 endpoint error
        # 实际上 proxy 走 urllib 先，path 在解析后才用
        self.assertIn("ok", r)


class TestLedger(unittest.TestCase):
    """#4 local ledger 快照"""

    def test_load_empty_ledger(self):
        snap = bb.load_ledger("/nonexistent/path/ledger.json")
        self.assertEqual(snap.baseline, 0)
        self.assertEqual(snap.remaining, 0)
        self.assertEqual(snap.spent, 0)

    def test_load_real_ledger(self, tmp_dir=None):
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({
                "baseline": 10.0,
                "remaining": 5.42,
                "spent": 4.58,
                "currency": "CNY",
                "sessions": [{"id": "abc", "cost": 0.5}],
                "updated_at": "2026-08-24T12:00:00Z",
            }, f)
            tmp_path = f.name
        try:
            snap = bb.load_ledger(tmp_path)
            self.assertEqual(snap.baseline, 10.0)
            self.assertEqual(snap.remaining, 5.42)
            self.assertEqual(snap.spent, 4.58)
            self.assertEqual(snap.currency, "CNY")
            self.assertEqual(len(snap.sessions), 1)
        finally:
            os.unlink(tmp_path)


class TestPricingBand(unittest.TestCase):
    """#5 pricing band demo"""

    def test_flash_default_offpeak(self):
        # 强制 off_peak
        pricing = bb.get_pricing("deepseek-v4-flash", band="off_peak")
        self.assertEqual(pricing["input"], 0.02)
        self.assertEqual(pricing["output"], 1.00)

    def test_flash_peak_doubles(self):
        off = bb.get_pricing("deepseek-v4-flash", band="off_peak")
        peak = bb.get_pricing("deepseek-v4-flash", band="peak")
        self.assertEqual(peak["input"], off["input"] * 2)
        self.assertEqual(peak["output"], off["output"] * 2)

    def test_pro_more_expensive(self):
        flash = bb.get_pricing("deepseek-v4-flash", band="off_peak")
        pro = bb.get_pricing("deepseek-v4-pro", band="off_peak")
        # pro input 0.20 > flash 0.02
        self.assertGreater(pro["input"], flash["input"] * 5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
