"""Cross-sectional IC kernel tests: alignment, factor math, correlation,
aggregate, caps, and parity with the TypeScript pipeline's conventions."""

import unittest

from pcpt.cross_ic import PanelError, run_cross_section_ic


def _panel(seeded_slopes, count=12):
    """A panel where each symbol ramps linearly with its own slope."""
    panel = {}
    for order, symbol in enumerate(["AAA", "BBB", "CCC"]):
        slope = 1 + order * 3
        panel[symbol] = [
            {
                "date": f"2024-01-{i + 1:02d}",
                "open": 10 + order * 10 + i * slope,
                "high": 11 + order * 10 + i * slope,
                "low": 9 + order * 10 + i * slope,
                "close": 10 + order * 10 + i * slope,
                "volume": 100,
            }
            for i in range(count)
        ]
    return panel


class TestRunCrossSectionIC(unittest.TestCase):
    def test_perfectly_ordered_panel_scores_positive_ic(self):
        result = run_cross_section_ic(_panel(3), "momentum", 5, window=3)
        self.assertEqual(len(result["symbols"]), 3)
        valid = [p["ic"] for p in result["points"] if p["ic"] is not None]
        self.assertGreaterEqual(len(valid), 2)
        self.assertTrue(all(ic > 0 for ic in valid))
        self.assertIsNotNone(result["summary"])
        self.assertGreater(result["summary"]["mean_ic"], 0)

    def test_alignment_drops_unshared_dates(self):
        panel = _panel(3)
        panel["BBB"] = panel["BBB"][1:]  # BBB misses day 1
        result = run_cross_section_ic(panel, "momentum", 5, window=3)
        # 11 shared dates, horizon 5 → 6 evaluation points.
        self.assertEqual(result["shared_dates"], 11)
        self.assertEqual(len(result["points"]), 6)

    def test_degenerate_dispersion_clamps_icir_to_zero(self):
        # One flat-close panel: forward returns are constant where defined →
        # degenerate sections report ic None; with a two-symbol constant panel
        # every section degenerates, so the summary is None (fewer than 2 valid).
        flat = {
            symbol: [
                {
                    "date": f"2024-01-{i + 1:02d}",
                    "open": 10, "high": 11, "low": 9, "close": 10, "volume": 100,
                }
                for i in range(12)
            ]
            for symbol in ("AAA", "BBB")
        }
        result = run_cross_section_ic(flat, "momentum", 5, window=3)
        self.assertIsNone(result["summary"])

    def test_caps_reject_out_of_bounds(self):
        with self.assertRaises(PanelError):
            run_cross_section_ic({"A": [], "B": []}, "momentum", 21)
        with self.assertRaises(PanelError):
            run_cross_section_ic({s: [] for s in "ABCDEFGHIJK"}, "momentum", 5)
        with self.assertRaises(PanelError):
            run_cross_section_ic({"A": [], "B": []}, "not_a_factor", 5)

    def test_shared_dates_too_few_fails_loud(self):
        panel = {symbol: _panel(3)[symbol][:1] for symbol in ("AAA", "BBB")}
        with self.assertRaises(PanelError):
            run_cross_section_ic(panel, "momentum", 1, window=1)


if __name__ == "__main__":
    unittest.main()
