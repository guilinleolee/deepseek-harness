"""test_47_6_e2e · 4 个端到端场景全部 PASS"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "stage47.5" / "scripts"))

from end_to_end import (
    e2e_1_xlsx_round_trip,
    e2e_2_multi_sheet,
    e2e_3_pptx_lint,
    e2e_4_multi_unit,
)


def test_47_6_e2e():
    stage47_root = Path(__file__).resolve().parent.parent.parent
    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)

        # E2E-1
        r1 = e2e_1_xlsx_round_trip(stage47_root / "stage47.1" / "output", workdir)
        assert r1["ok"], f"[FAIL] E2E-1 失败: {r1}"
        assert r1["export_size"] > 0, f"[FAIL] E2E-1 导出为空"
        print(f"[PASS] E2E-1: 47.1 xlsx round-trip ({r1['export_size']} B export)")

        # E2E-2: 47.2 xlsx 5 sheet
        r2 = e2e_2_multi_sheet(stage47_root / "stage47.2" / "output", workdir)
        if not r2.get("source") or not Path(r2["source"]).exists():
            print(f"[SKIP] E2E-2: 47.2 output 不存在，跳过")
        else:
            assert r2["ok"], f"[FAIL] E2E-2 失败: {r2}"
            assert r2["all_5_sheets_inspected"], f"[FAIL] E2E-2 5 sheet 没全部 inspect"
            print(f"[PASS] E2E-2: 47.2 5 sheet 跨公式 round-trip ({len(r2['sheet_inspections'])} sheets)")

        # E2E-3: 47.3 pptx
        r3 = e2e_3_pptx_lint(stage47_root / "stage47.3" / "output", workdir)
        if not r3.get("source") or not Path(r3["source"]).exists():
            print(f"[SKIP] E2E-3: 47.3 output 不存在，跳过")
        else:
            assert r3["ok"], f"[FAIL] E2E-3 失败: {r3}"
            assert r3["lint_passed"], f"[FAIL] E2E-3 lint 有 finding: {r3['lint_findings']}"
            assert r3["screenshot_size"] > 0
            print(f"[PASS] E2E-3: 47.3 pptx 5 slide round-trip (lint=0, screenshot={r3['screenshot_size']} B)")

        # E2E-4: 多 Unit
        r4 = e2e_4_multi_unit(stage47_root, workdir)
        if not r4["ok"] and r4.get("error") == "MISSING_SOURCE":
            print(f"[SKIP] E2E-4: source 缺失 {r4}")
        else:
            assert r4["ok"], f"[FAIL] E2E-4 失败: {r4}"
            assert len(r4["units"]) == 3, f"[FAIL] E2E-4 units 不全: {r4['units']}"
            assert {u["kind"] for u in r4["units"]} == {"sheet", "doc", "slide"}
            print(f"[PASS] E2E-4: 多 Unit (Sheet + Doc + Slide) 同一 .univer 容器")


if __name__ == "__main__":
    test_47_6_e2e()
