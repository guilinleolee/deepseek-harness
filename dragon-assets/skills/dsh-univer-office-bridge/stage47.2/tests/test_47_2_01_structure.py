"""test_47_2_01_structure · 5 sheets + FetchResult 接口语义"""
import sys
from datetime import date
from pathlib import Path

import openpyxl

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from finance_workbook import build_finance_workbook, FetchResult, mock_pe_pb


def test_47_2_01_structure():
    out = Path(__file__).resolve().parent.parent / "output" / f"test-{date.today().isoformat()}.xlsx"
    out.parent.mkdir(parents=True, exist_ok=True)
    result = build_finance_workbook("600519.SH", out)

    assert out.exists(), f"[FAIL] xlsx not created: {out}"
    assert result["sheets"] == 5, f"[FAIL] expected 5 sheets, got {result['sheets']}"

    wb = openpyxl.load_workbook(out)
    expected = ["1_估值快照", "2_财报三表", "3_季报关键指标", "4_资金流与持仓", "5_投资分析"]
    for name in expected:
        assert name in wb.sheetnames, f"[FAIL] sheet '{name}' missing"

    # FetchResult 接口语义（与 a-stock-data-bridge em_get.FetchResult 同构）
    r = mock_pe_pb()
    assert hasattr(r, "source")
    assert hasattr(r, "endpoint")
    assert hasattr(r, "data")
    assert hasattr(r, "fetched_at")
    assert hasattr(r, "fallback_used")
    assert hasattr(r, "rows")
    assert r.endpoint == "pe_pb_market_cap"
    assert r.source == "eastmoney"

    print(f"[PASS] 47.2.01 structure: {result['sheets']} sheets, FetchResult 接口同构")


if __name__ == "__main__":
    test_47_2_01_structure()
