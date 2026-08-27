"""test_47_2_04_chart · Sheet 2 含原生图表"""
import sys
from datetime import date
from pathlib import Path

import openpyxl

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from finance_workbook import build_finance_workbook


def test_47_2_04_chart():
    out = Path(__file__).resolve().parent.parent / "output" / f"test-{date.today().isoformat()}.xlsx"
    out.parent.mkdir(parents=True, exist_ok=True)
    build_finance_workbook("600519.SH", out)

    wb = openpyxl.load_workbook(out)
    ws2 = wb["2_财报三表"]

    assert len(ws2._charts) >= 1, f"[FAIL] expected ≥1 chart in Sheet 2, got {len(ws2._charts)}"
    chart = ws2._charts[0]
    assert chart.title is not None, "[FAIL] chart has no title"

    print(f"[PASS] 47.2.04 chart: 1 个条形图 '{chart.title.tx.rich.p[0].r[0].t if chart.title else 'untitled'}'")


if __name__ == "__main__":
    test_47_2_04_chart()
