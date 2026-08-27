"""
dsh-peak-gate-bridge V1.0 · 5 unittest
"""
import os
import sys
import json
import unittest
from datetime import datetime, timezone, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

import dsh_peak_gate_bridge as pg  # noqa: E402


class TestPeakWindow(unittest.TestCase):
    """#1 peak window 数学"""

    bj = timezone(timedelta(hours=8))

    def test_peak_10am_beijing(self):
        dt = datetime(2026, 8, 24, 10, 0, tzinfo=self.bj)
        self.assertTrue(pg.is_peak_hour(dt))

    def test_peak_15pm_beijing(self):
        dt = datetime(2026, 8, 24, 15, 0, tzinfo=self.bj)
        self.assertTrue(pg.is_peak_hour(dt))

    def test_offpeak_13pm_beijing(self):
        dt = datetime(2026, 8, 24, 13, 0, tzinfo=self.bj)
        self.assertFalse(pg.is_peak_hour(dt))

    def test_offpeak_20pm_beijing(self):
        dt = datetime(2026, 8, 24, 20, 0, tzinfo=self.bj)
        self.assertFalse(pg.is_peak_hour(dt))

    def test_weekend_offpeak(self):
        # 2026-08-29 是周六
        dt = datetime(2026, 8, 29, 10, 0, tzinfo=self.bj)  # 周六 10 AM，应该 off-peak
        self.assertTrue(pg.is_off_peak_weekend(dt))
        self.assertEqual(pg.get_current_band(dt), "off-peak")


class TestNextOffPeak(unittest.TestCase):
    """#2 next off-peak 计算"""

    bj = timezone(timedelta(hours=8))

    def test_10am_to_12pm(self):
        # 上午 10 点，下次 off-peak = 今天 12:00
        dt = datetime(2026, 8, 24, 10, 0, tzinfo=self.bj)
        nxt = pg.next_off_peak_dt(dt)
        self.assertEqual(nxt.hour, 12)
        self.assertEqual(nxt.minute, 0)

    def test_15pm_to_18pm(self):
        # 下午 15 点，下次 off-peak = 今天 18:00
        dt = datetime(2026, 8, 24, 15, 0, tzinfo=self.bj)
        nxt = pg.next_off_peak_dt(dt)
        self.assertEqual(nxt.hour, 18)

    def test_20pm_already_offpeak(self):
        # 晚上 20 点，已经 off-peak → 返回现在
        dt = datetime(2026, 8, 24, 20, 0, tzinfo=self.bj)
        nxt = pg.next_off_peak_dt(dt)
        self.assertEqual(nxt, dt)


class TestLocalStorageSchema(unittest.TestCase):
    """#3 localStorage 3-key schema 生成"""

    def test_default_schema(self):
        schema = pg.generate_localstorage_schema()
        self.assertIn("dsh.peakGate.settings.v1", schema)
        self.assertIn("dsh.peakGate.muted.v1", schema)
        self.assertIn("dsh.peakGate.holds.v1", schema)
        settings = schema["dsh.peakGate.settings.v1"]
        self.assertEqual(settings["timezone"], "Asia/Shanghai")
        self.assertEqual(len(settings["peakWindows"]), 2)
        self.assertTrue(settings["enabled"])
        self.assertTrue(settings["offPeakWeekends"])

    def test_custom_timezone(self):
        schema = pg.generate_localstorage_schema(timezone="America/New_York")
        self.assertEqual(schema["dsh.peakGate.settings.v1"]["timezone"], "America/New_York")


class TestParseCmd(unittest.TestCase):
    """#4 /peakgate 5 子命令 parser"""

    def test_hold(self):
        r = pg.parse_peakgate_command("/peakgate hold task: process docs")
        self.assertEqual(r.cmd, "hold")
        self.assertEqual(r.text, "task: process docs")

    def test_hold_no_prefix(self):
        r = pg.parse_peakgate_command("peakgate hold some text")
        self.assertEqual(r.cmd, "hold")
        self.assertEqual(r.text, "some text")

    def test_list(self):
        r = pg.parse_peakgate_command("/peakgate list")
        self.assertEqual(r.cmd, "list")
        self.assertEqual(r.args, [])

    def test_remove(self):
        r = pg.parse_peakgate_command("/peakgate remove 5")
        self.assertEqual(r.cmd, "remove")
        self.assertEqual(r.args, [5])

    def test_remove_invalid_seq(self):
        r = pg.parse_peakgate_command("/peakgate remove abc")
        self.assertEqual(r.cmd, "help")  # 容错

    def test_cancel(self):
        r = pg.parse_peakgate_command("/peakgate cancel")
        self.assertEqual(r.cmd, "cancel")

    def test_help(self):
        r = pg.parse_peakgate_command("/peakgate")
        self.assertEqual(r.cmd, "help")

    def test_unknown_cmd(self):
        r = pg.parse_peakgate_command("/peakgate unknown arg")
        self.assertEqual(r.cmd, "help")


class TestQueueDataStruct(unittest.TestCase):
    """#5 PeakGateQueue 数据结构"""

    def test_add_and_remove(self):
        q = pg.PeakGateQueue()
        h1 = pg.PeakGateHold(
            id="h1", source_session="s1", content="c1",
            held_at="2026-08-24T10:00", auto_send_at="2026-08-24T12:00",
        )
        q.add(h1)
        self.assertEqual(len(q.holds), 1)

        removed = q.remove(0)
        self.assertEqual(removed.id, "h1")
        self.assertEqual(len(q.holds), 0)

    def test_remove_oob(self):
        q = pg.PeakGateQueue()
        self.assertIsNone(q.remove(0))
        self.assertIsNone(q.remove(-1))

    def test_to_dict(self):
        q = pg.PeakGateQueue()
        h = pg.PeakGateHold(
            id="h1", source_session="s1", content="c1",
            held_at="2026-08-24T10:00", auto_send_at="2026-08-24T12:00",
            status="queued", tag="peak-card",
        )
        q.add(h)
        d = q.to_dict()
        self.assertIn("holds", d)
        self.assertEqual(len(d["holds"]), 1)
        self.assertEqual(d["holds"][0]["id"], "h1")
        self.assertEqual(d["holds"][0]["tag"], "peak-card")


if __name__ == "__main__":
    unittest.main(verbosity=2)
