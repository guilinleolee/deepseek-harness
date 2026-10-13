"""test_47_2_02_cross_sheet · 跨 sheet 公式联动（核心验证）"""
import sys
from datetime import date
from pathlib import Path

import openpyxl

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from finance_workbook import build_finance_workbook


def test_47_2_02_cross_sheet():
    """验证财务健康度评分（sheet 4）跨 sheet 引用 sheet 3 的 ROE/资产负债率/毛利率"""
    out = Path(__file__).resolve().parent.parent / "output" / f"test-{date.today().isoformat()}.xlsx"
    out.parent.mkdir(parents=True, exist_ok=True)
    build_finance_workbook("600519.SH", out)

    wb = openpyxl.load_workbook(out)
    ws4 = wb["4_资金流与持仓"]

    # 验证跨 sheet 公式存在
    cross_sheet_formulas = []
    for row in ws4.iter_rows():
        for cell in row:
            if isinstance(cell.value, str) and cell.value.startswith("=") and "'" in cell.value:
                cross_sheet_formulas.append((cell.coordinate, cell.value))

    assert len(cross_sheet_formulas) >= 4, \
        f"[FAIL] expected ≥4 cross-sheet formulas in Sheet 4, got {len(cross_sheet_formulas)}: {cross_sheet_formulas}"

    # 验证 B12（财务健康度总分）是 SUM 公式
    b12 = ws4["B12"].value
    assert isinstance(b12, str) and b12.startswith("=SUM"), \
        f"[FAIL] B12 should be SUM formula, got {b12}"

    # 验证 Sheet 5（投资分析）的 IF 综合评级公式
    ws5 = wb["5_投资分析"]
    b8 = ws5["B8"].value
    assert isinstance(b8, str) and "IF" in b8, \
        f"[FAIL] B8 should be IF formula, got {b8}"

    print(f"[PASS] 47.2.02 cross-sheet: {len(cross_sheet_formulas)} 跨 sheet 公式 + SUM/IF 联动")


if __name__ == "__main__":
    test_47_2_02_cross_sheet()
