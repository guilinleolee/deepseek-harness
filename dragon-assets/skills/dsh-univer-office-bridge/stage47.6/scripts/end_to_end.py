"""阶段 47.6 · 47.1/47.2/47.3 产物经 univer stub 端到端消化

策略：
  - 把 47.1/47.2/47.3 生成的真实 .xlsx/.pptx/.docx 文件作为 univer_import 的 source
  - 在同一个 .univer 文件中创建多 Unit 容器（Sheet + Doc + Slide）
  - 用 univer_execute / univer_compile_svg 模拟 Facade 写入
  - 用 univer_export 导出到新路径
  - 验证产物完整

4 个端到端场景：
  E2E-1: 47.1 xlsx → univer_import(Sheet) → univer_export(.xlsx)
  E2E-2: 47.2 xlsx（5 sheet） → univer_import(Sheet) → univer_inspect 跨 sheet 公式
  E2E-3: 47.3 pptx → univer_import(Slide) → univer_lint(无 finding)
  E2E-4: 47.1 docx + xlsx + pptx → 同一 .univer 多 Unit 容器

Author: dragon-engine · Stage 47.6 · 2026-08-26
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "stage47.5" / "scripts"))

from univer_stub import call


def e2e_1_xlsx_round_trip(stage47_1_output: Path, workdir: Path) -> dict:
    """47.1 xlsx → univer_import(Sheet) → univer_export(.xlsx)"""
    source = stage47_1_output / "xlsx"
    # 选真实产物（非 test-*），按名字长度倒序选最大的（最像真实产物）
    src_files = sorted(
        [f for f in source.glob("*.xlsx") if not f.name.startswith("test-")],
        key=lambda f: f.stat().st_size,
        reverse=True,
    )
    if not src_files:
        return {"ok": False, "error": "NO_SOURCE", "stage": "47.1"}
    src = src_files[0]
    univer_file = str(workdir / "e2e1.univer")
    wt = "wt-e2e1"

    # 启动
    r1 = call("univer_new", file=univer_file)
    r2 = call("univer_worktree", file=univer_file, worktree_id=wt, action="create")
    r3 = call("univer_import", file=univer_file, source=str(src))

    # 写入（Facade mock）
    r4 = call("univer_execute", file=univer_file, unit_id=r3["unit_id"], worktree_id=wt,
              code="sheet.getActiveSheet().getRange('F1').setValue({v:'再加工', t:1})")

    # 验证
    r5 = call("univer_inspect", file=univer_file, unit_id=r3["unit_id"], range="Sheet1!A1:F10")

    # 导出
    out_path = str(workdir / "e2e1_export.xlsx")
    r6 = call("univer_export", file=univer_file, unit_id=r3["unit_id"], format="xlsx", output=out_path)

    # 收尾
    r7 = call("univer_worktree", file=univer_file, worktree_id=wt, action="ready")

    return {
        "stage": "47.1 xlsx round-trip",
        "ok": all(r["ok"] for r in [r1, r2, r3, r4, r5, r6, r7]),
        "source": str(src),
        "source_size": src.stat().st_size,
        "univer_file": univer_file,
        "export": out_path,
        "export_size": Path(out_path).stat().st_size if Path(out_path).exists() else 0,
        "unit_id": r3["unit_id"],
        "results": {"new": r1, "worktree": r2, "import": r3, "execute": r4, "inspect": r5, "export": r6, "ready": r7},
    }


def e2e_2_multi_sheet(stage47_2_output: Path, workdir: Path) -> dict:
    """47.2 xlsx（5 sheet 含跨 sheet 公式）→ univer_import → 跨 sheet 引用"""
    source = stage47_2_output
    src_files = sorted(
        [f for f in source.glob("*.xlsx") if not f.name.startswith("test-")],
        key=lambda f: f.stat().st_size,
        reverse=True,
    )
    if not src_files:
        return {"ok": False, "error": "NO_SOURCE", "stage": "47.2"}
    src = src_files[0]
    univer_file = str(workdir / "e2e2.univer")
    wt = "wt-e2e2"

    r1 = call("univer_new", file=univer_file)
    r2 = call("univer_worktree", file=univer_file, worktree_id=wt, action="create")
    r3 = call("univer_import", file=univer_file, source=str(src))

    # 跨 sheet 公式验证（执行读所有 5 个 sheet）
    ranges = ["1_估值快照!A1:B10", "2_财报三表!A1:D30", "3_季报关键指标!A1:G15",
              "4_资金流与持仓!A1:B12", "5_投资分析!A1:D8"]
    inspections = []
    for rng in ranges:
        # univer_inspect 只支持单 unit；模拟跨 sheet 通过多次调用
        sheet_name = rng.split("!")[0]
        r = call("univer_inspect", file=univer_file, unit_id=r3["unit_id"], range=rng)
        inspections.append((sheet_name, r["ok"]))

    r6 = call("univer_export", file=univer_file, unit_id=r3["unit_id"], format="xlsx",
              output=str(workdir / "e2e2_export.xlsx"))
    r7 = call("univer_worktree", file=univer_file, worktree_id=wt, action="ready")

    return {
        "stage": "47.2 5 sheet 跨公式 round-trip",
        "ok": all(r["ok"] for r in [r1, r2, r3, r6, r7]) and all(ok for _, ok in inspections),
        "source": str(src),
        "univer_file": univer_file,
        "export": str(workdir / "e2e2_export.xlsx"),
        "sheet_inspections": inspections,
        "all_5_sheets_inspected": len(inspections) == 5,
        "unit_id": r3["unit_id"],
    }


def e2e_3_pptx_lint(stage47_3_output: Path, workdir: Path) -> dict:
    """47.3 pptx → univer_import(Slide) → univer_lint 无 finding"""
    source = stage47_3_output
    src_files = sorted(
        [f for f in source.glob("*.pptx") if not f.name.startswith("test-")],
        key=lambda f: f.stat().st_size,
        reverse=True,
    )
    if not src_files:
        return {"ok": False, "error": "NO_SOURCE", "stage": "47.3"}
    src = src_files[0]
    univer_file = str(workdir / "e2e3.univer")
    wt = "wt-e2e3"

    r1 = call("univer_new", file=univer_file)
    r2 = call("univer_worktree", file=univer_file, worktree_id=wt, action="create")
    r3 = call("univer_import", file=univer_file, source=str(src))

    # 5 slide lint
    r4 = call("univer_lint", file=univer_file, unit_id=r3["unit_id"], pages=[1, 2, 3, 4, 5])

    # screenshot 第 1 页
    r5 = call("univer_screenshot", file=univer_file, unit_id=r3["unit_id"],
              output=str(workdir / "screenshots"))

    # export pptx
    r6 = call("univer_export", file=univer_file, unit_id=r3["unit_id"],
              format="pptx", output=str(workdir / "e2e3_export.pptx"))

    r7 = call("univer_worktree", file=univer_file, worktree_id=wt, action="ready")

    return {
        "stage": "47.3 pptx 5 slide round-trip",
        "ok": all(r["ok"] for r in [r1, r2, r3, r4, r5, r6, r7]),
        "source": str(src),
        "univer_file": univer_file,
        "export": str(workdir / "e2e3_export.pptx"),
        "lint_findings": r4["findings"],
        "lint_passed": len(r4["findings"]) == 0,
        "screenshot_size": r5["size_bytes"],
        "unit_id": r3["unit_id"],
    }


def e2e_4_multi_unit(stage47_root: Path, workdir: Path) -> dict:
    """47.1 xlsx + docx + 47.3 pptx → 同一 .univer 多 Unit 容器"""
    xlsx_dir = stage47_root / "stage47.1" / "output" / "xlsx"
    docx_dir = stage47_root / "stage47.1" / "output" / "docx"
    pptx_dir = stage47_root / "stage47.3" / "output"

    def pick_largest(d):
        cands = [f for f in d.glob("*") if not f.name.startswith("test-")]
        return max(cands, key=lambda f: f.stat().st_size) if cands else None

    xlsx_src = pick_largest(xlsx_dir)
    docx_src = pick_largest(docx_dir)
    pptx_src = pick_largest(pptx_dir)

    if not all([xlsx_src, docx_src, pptx_src]):
        return {"ok": False, "error": "MISSING_SOURCE",
                "xlsx": str(xlsx_src) if xlsx_src else None,
                "docx": str(docx_src) if docx_src else None,
                "pptx": str(pptx_src) if pptx_src else None}

    univer_file = str(workdir / "e2e4_multi.univer")
    wt = "wt-e2e4"

    r1 = call("univer_new", file=univer_file)
    r2 = call("univer_worktree", file=univer_file, worktree_id=wt, action="create")

    # 多 Unit 导入
    r3_xlsx = call("univer_import", file=univer_file, source=str(xlsx_src))
    r3_docx = call("univer_import", file=univer_file, source=str(docx_src))
    r3_pptx = call("univer_import", file=univer_file, source=str(pptx_src))

    # 状态
    r_status = call("univer_status", file=univer_file)

    # 各 Unit lint + screenshot
    r_xlsx_inspect = call("univer_inspect", file=univer_file, unit_id=r3_xlsx["unit_id"])
    r_docx_inspect = call("univer_inspect", file=univer_file, unit_id=r3_docx["unit_id"])
    r_pptx_lint = call("univer_lint", file=univer_file, unit_id=r3_pptx["unit_id"], pages=[1])

    # 多格式 export
    r_xlsx_export = call("univer_export", file=univer_file, unit_id=r3_xlsx["unit_id"],
                         format="xlsx", output=str(workdir / "multi_xlsx.xlsx"))
    r_docx_export = call("univer_export", file=univer_file, unit_id=r3_docx["unit_id"],
                         format="docx", output=str(workdir / "multi_docx.docx"))
    r_pptx_export = call("univer_export", file=univer_file, unit_id=r3_pptx["unit_id"],
                         format="pptx", output=str(workdir / "multi_pptx.pptx"))

    r_ready = call("univer_worktree", file=univer_file, worktree_id=wt, action="ready")

    return {
        "stage": "47.4 multi-unit (Sheet + Doc + Slide 同一 .univer)",
        "ok": all(r["ok"] for r in [r1, r2, r3_xlsx, r3_docx, r3_pptx,
                                    r_xlsx_inspect, r_docx_inspect, r_pptx_lint,
                                    r_xlsx_export, r_docx_export, r_pptx_export, r_ready]),
        "univer_file": univer_file,
        "units": [
            {"kind": "sheet", "id": r3_xlsx["unit_id"], "export": r_xlsx_export["output"]},
            {"kind": "doc", "id": r3_docx["unit_id"], "export": r_docx_export["output"]},
            {"kind": "slide", "id": r3_pptx["unit_id"], "export": r_pptx_export["output"]},
        ],
        "lint_passed": len(r_pptx_lint["findings"]) == 0,
    }


# ─── 主入口 ────────────────────────────────────────────────────────────────

def main() -> int:
    stage47_root = Path(__file__).resolve().parent.parent.parent
    print("=" * 70)
    print("Stage 47.6 · 47.1/47.2/47.3 产物经 univer stub 端到端消化")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        results = []

        # E2E-1: 47.1 xlsx
        r1 = e2e_1_xlsx_round_trip(stage47_root / "stage47.1" / "output", workdir)
        results.append(r1)
        print(f"\n[E2E-1] {r1['stage']}")
        print(f"  ok={r1['ok']}  source={Path(r1.get('source', '?')).name}  export={r1.get('export_size', 0)} B")

        # E2E-2: 47.2 xlsx 5 sheet
        r2 = e2e_2_multi_sheet(stage47_root / "stage47.2" / "output", workdir)
        results.append(r2)
        print(f"\n[E2E-2] {r2['stage']}")
        print(f"  ok={r2['ok']}  5 sheets inspected={r2.get('all_5_sheets_inspected', False)}")

        # E2E-3: 47.3 pptx
        r3 = e2e_3_pptx_lint(stage47_root / "stage47.3" / "output", workdir)
        results.append(r3)
        print(f"\n[E2E-3] {r3['stage']}")
        print(f"  ok={r3['ok']}  lint_passed={r3.get('lint_passed', False)}")

        # E2E-4: 多 Unit
        r4 = e2e_4_multi_unit(stage47_root, workdir)
        results.append(r4)
        print(f"\n[E2E-4] {r4['stage']}")
        print(f"  ok={r4['ok']}  units={len(r4.get('units', []))}")
        for u in r4.get("units", []):
            print(f"    - {u['kind']}: {Path(u['export']).name}")

        all_ok = all(r["ok"] for r in results)
        print("\n" + "=" * 70)
        print(f"Stage 47.6 PASS: {sum(1 for r in results if r['ok'])}/{len(results)} 端到端场景")
        print("=" * 70)

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
