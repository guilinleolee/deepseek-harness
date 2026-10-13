"""test_47_2_03_endpoints · 5 个 a-stock-data 端点都覆盖"""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from finance_workbook import (
    build_finance_workbook,
    mock_pe_pb,
    mock_financial_3statements,
    mock_quarterly,
    mock_north_bound,
    mock_consensus,
)


def test_47_2_03_endpoints():
    """5 个端点对应 5 个 sheet，数据语义对齐 a-stock-data-bridge schema"""
    # 每个端点的 schema 字段验证
    pe = mock_pe_pb().data
    assert {"pe_ttm", "pe_static", "pb", "market_cap"} <= set(pe.keys())

    fin = mock_financial_3statements().data
    assert {"balance_sheet", "income_statement", "cash_flow_statement"} <= set(fin.keys())
    assert {"revenue", "net_profit", "eps"} <= set(fin["income_statement"].keys())

    q = mock_quarterly().data
    assert {"revenue_yoy", "net_profit_yoy", "roe", "roa"} <= set(q.keys())

    nb = mock_north_bound().data
    assert {"net_buy_amount_5d", "holdings_ratio", "rank_in_north"} <= set(nb.keys())

    cons = mock_consensus().data
    assert {"consensus_eps_2025E", "buy_count", "target_price_median"} <= set(cons.keys())

    # 5 sheet 全部覆盖这 5 个端点
    out = Path(__file__).resolve().parent.parent / "output" / f"test-{date.today().isoformat()}.xlsx"
    out.parent.mkdir(parents=True, exist_ok=True)
    result = build_finance_workbook("600519.SH", out)

    expected_endpoints = {
        "pe_pb_market_cap",       # Sheet 1
        "financial_3statements",  # Sheet 2
        "quarterly_report_37fields",  # Sheet 3
        "north_top10",            # Sheet 4
        "consensus_eps",          # Sheet 1 + Sheet 5
    }
    assert set(result["endpoints"]) == expected_endpoints, \
        f"[FAIL] endpoints mismatch: {set(result['endpoints'])} vs {expected_endpoints}"

    print(f"[PASS] 47.2.03 endpoints: 5/5 端点覆盖 a-stock-data-bridge schema")


if __name__ == "__main__":
    test_47_2_03_endpoints()
