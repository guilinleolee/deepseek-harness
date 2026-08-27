"""test_47_1_xlsx · 28-data-analyst V11.0 .xlsx 工作簿产出验证

验证：
  1. 文件存在 + 大小 > 0
  2. 1 个 sheet，名称 "本周热点话题趋势"
  3. 表头 6 列（日期 + 4 话题 + 7日均值）
  4. 至少 7 行数据
  5. 至少 7 个公式（F 列 7 日均值）
  6. 至少 1 个图表
"""
import sys
from datetime import date
from pathlib import Path

import openpyxl

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from office_producers import build_xlsx_workbook


def test_47_1_xlsx():
    out = Path(__file__).resolve().parent.parent / "output" / "xlsx" / f"test-{date.today().isoformat()}.xlsx"
    out.parent.mkdir(parents=True, exist_ok=True)
    result = build_xlsx_workbook(out)

    assert out.exists(), f"[FAIL] xlsx not created: {out}"
    assert out.stat().st_size > 1000, f"[FAIL] xlsx too small: {out.stat().st_size}"

    wb = openpyxl.load_workbook(out)
    assert len(wb.sheetnames) == 1, f"[FAIL] expected 1 sheet, got {len(wb.sheetnames)}"
    ws = wb["本周热点话题趋势"]
    assert ws is not None, "[FAIL] sheet '本周热点话题趋势' missing"

    # 表头
    headers = [c.value for c in ws[1]]
    assert headers == ["日期", "AI 工具", "编程技巧", "效率提升", "职场成长", "7日均值"], \
        f"[FAIL] headers mismatch: {headers}"

    # 数据行（至少 7 天）
    data_rows = sum(1 for row in ws.iter_rows(min_row=2, max_row=8, values_only=True) if row[0])
    assert data_rows >= 7, f"[FAIL] data rows {data_rows} < 7"

    # F 列（7日均值）应该是公式
    formula_cells = 0
    for row_idx in range(2, 9):
        cell = ws.cell(row=row_idx, column=6)
        if isinstance(cell.value, str) and cell.value.startswith("="):
            formula_cells += 1
    assert formula_cells >= 7, f"[FAIL] formula cells {formula_cells} < 7"

    # 图表
    assert len(ws._charts) >= 1, f"[FAIL] expected ≥1 chart, got {len(ws._charts)}"

    print(f"[PASS] xlsx: {result}")


if __name__ == "__main__":
    test_47_1_xlsx()
