"""阶段 47.14 · univer_* 13 工具 一次性 e2e

把 47.5 13 工具 stub + 47.6 4 E2E + 47.7 embed + 47.8 base + 47.9 board + 47.10 doc
+ 47.11 cross_unit + 47.12 resources + 47.13 api 整合为一条端到端工作流。

Author: dragon-engine · Stage 47.14 · 2026-08-26
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# 把 stage47.5 stub 加入路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "stage47.5" / "scripts"))

from univer_stub import (
    call,
    univer_new, univer_status, univer_worktree, univer_unit, univer_import,
    univer_execute, univer_compile_svg, univer_inspect, univer_lint, univer_screenshot,
    univer_api, univer_resources, univer_export,
)

TZ_CN = timezone(timedelta(hours=8))


def full_13_tool_e2e() -> dict:
    """一次性跑通 13 个 univer_* 工具，按官方工作流顺序"""
    import tempfile
    workdir = Path(tempfile.mkdtemp(prefix="univer_e2e_"))

    print("=" * 70)
    print("Stage 47.14 · univer_* 13 工具一次性 e2e")
    print("=" * 70)

    trace = []  # 记录每步结果

    # === Phase 1: 启动（5 工具）===
    print("\n--- Phase 1: 启动（5 工具）---")

    # 1. univer_new
    univer_file = str(workdir / "demo-47.14.univer")
    r1 = univer_new(file=univer_file)
    assert r1["ok"], f"[FAIL] univer_new: {r1}"
    trace.append(("univer_new", r1))
    print(f"[1/13] univer_new     → file={Path(r1['file']).name} ({r1['bytes']} B)")

    # 2. univer_worktree (create)
    wt_id = "wt-47-14-001"
    r2 = univer_worktree(file=univer_file, worktree_id=wt_id, action="create")
    assert r2["ok"]
    trace.append(("univer_worktree.create", r2))
    print(f"[2/13] univer_worktree → action=create state={r2['state']}")

    # 3. univer_unit (Sheet)
    sheet_id = "sheet-main"
    r3 = univer_unit(file=univer_file, unit_id=sheet_id, kind="sheet", name="本周热点")
    assert r3["ok"]
    trace.append(("univer_unit", r3))
    print(f"[3/13] univer_unit    → kind=sheet unit_id={r3['unit_id']}")

    # 4. univer_unit (Slide)
    slide_id = "slide-chart"
    r4 = univer_unit(file=univer_file, unit_id=slide_id, kind="slide", name="热点图表")
    assert r4["ok"]
    trace.append(("univer_unit.slide", r4))
    print(f"[4/13] univer_unit    → kind=slide unit_id={r4['unit_id']}")

    # 5. univer_status
    r5 = univer_status(file=univer_file)
    assert r5["ok"]
    trace.append(("univer_status", r5))
    print(f"[5/13] univer_status  → units={len(r5['units'])} worktrees={len(r5['worktrees'])}")

    # === Phase 2: 写入（2 工具）===
    print("\n--- Phase 2: 写入（2 工具）---")

    # 6. univer_execute
    r6 = univer_execute(
        file=univer_file, unit_id=sheet_id, worktree_id=wt_id,
        code="sheet.getActiveSheet().getRange('A1').setValue({v: 'hello-47.14', t: 1})",
    )
    assert r6["ok"] and r6["mutated"]
    trace.append(("univer_execute", r6))
    print(f"[6/13] univer_execute  → mutated={r6['mutated']}")

    # 7. univer_compile_svg
    svg_src = str(workdir / "page.svg")
    Path(svg_src).write_text('<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>')
    r7 = univer_compile_svg(source=svg_src, file=univer_file, worktree_id=wt_id, unit_id=slide_id, page=1)
    assert r7["ok"]
    trace.append(("univer_compile_svg", r7))
    print(f"[7/13] univer_compile_svg → page=1 mode={r7['mode']}")

    # === Phase 3: 验证（3 工具）===
    print("\n--- Phase 3: 验证（3 工具）---")

    # 8. univer_inspect
    r8 = univer_inspect(file=univer_file, unit_id=sheet_id, range="Sheet1!A1:D20")
    assert r8["ok"]
    trace.append(("univer_inspect", r8))
    print(f"[8/13] univer_inspect  → range={r8['range']}")

    # 9. univer_lint
    r9 = univer_lint(file=univer_file, unit_id=slide_id, pages=[1])
    assert r9["ok"]
    trace.append(("univer_lint", r9))
    print(f"[9/13] univer_lint    → {len(r9['findings'])} findings")

    # 10. univer_screenshot
    r10 = univer_screenshot(file=univer_file, unit_id=sheet_id, output=str(workdir))
    assert r10["ok"]
    trace.append(("univer_screenshot", r10))
    print(f"[10/13] univer_screenshot → png={Path(r10['png_path']).name} ({r10['size_bytes']} B)")

    # === Phase 4: 参考（2 工具）===
    print("\n--- Phase 4: 参考（2 工具）---")

    # 11. univer_api
    r11 = univer_api(action="find", queries=["setValue", "setFormula"])
    assert r11["ok"]
    trace.append(("univer_api", r11))
    print(f"[11/13] univer_api     → queries={r11['queries']}")

    # 12. univer_resources
    r12 = univer_resources(action="registries")
    assert r12["ok"]
    trace.append(("univer_resources", r12))
    print(f"[12/13] univer_resources → registries={r12['registries']}")

    # === Phase 5: 交付（1 工具）===
    print("\n--- Phase 5: 交付（1 工具）---")

    # 13. univer_export
    out_path = str(workdir / "final.xlsx")
    r13 = univer_export(file=univer_file, unit_id=sheet_id, format="xlsx", output=out_path)
    assert r13["ok"]
    trace.append(("univer_export", r13))
    print(f"[13/13] univer_export  → format={r13['format']} ({r13['size_bytes']} B)")

    # === 收尾 ===
    print("\n--- 收尾（worktree ready）---")
    r14 = univer_worktree(file=univer_file, worktree_id=wt_id, action="ready")
    assert r14["ok"]
    trace.append(("univer_worktree.ready", r14))
    print(f"[*] worktree ready → state={r14['state']}")

    # 总结
    print("\n" + "=" * 70)
    print(f"Stage 47.14 端到端 PASS: {len(trace)} 步全部成功")
    print(f"univer_file: {univer_file}")
    print(f"13 个 univer_* 工具全部跑通 + worktree 收尾")
    print("=" * 70)

    return {
        "ok": all(r["ok"] if isinstance(r, dict) else True for _, r in trace),
        "trace_count": len(trace),
        "trace": [(name, r.get("ok") if isinstance(r, dict) else None) for name, r in trace],
        "univer_file": univer_file,
        "worktree_id": wt_id,
        "sheet_id": sheet_id,
        "slide_id": slide_id,
        "final_export": r13["output"],
    }


# 独立 test function
full_13_tool_e2e.__test__ = True


def test_47_14_all_13_tools():
    """聚合测试：13 工具 + worktree 收尾"""
    r = full_13_tool_e2e()
    assert r["ok"]
    assert r["trace_count"] >= 14  # 13 tools + worktree.ready

    # 验证 trace 全 OK
    failed = [(name, ok) for name, ok in r["trace"] if not ok]
    assert not failed, f"[FAIL] trace 失败: {failed}"
    print(f"\n[PASS] 47.14 all_13_tools: {r['trace_count']} 步全成功")


def test_47_14_artifact_persistence():
    """验证产物持久化（univer_file + final_export 都在磁盘上）"""
    r = full_13_tool_e2e()
    assert Path(r["univer_file"]).exists(), f"[FAIL] univer_file 不存在: {r['univer_file']}"
    assert Path(r["final_export"]).exists(), f"[FAIL] final_export 不存在: {r['final_export']}"
    print(f"[PASS] artifact_persistence: univer_file={Path(r['univer_file']).stat().st_size} B, export={Path(r['final_export']).stat().st_size} B")


def test_47_14_worktree_lifecycle():
    """验证 worktree 完整生命周期（create → execute → ready）"""
    import tempfile
    workdir = Path(tempfile.mkdtemp(prefix="wt_lifecycle_"))
    univer_file = str(workdir / "lifecycle.univer")

    # create
    r1 = univer_worktree(file=univer_file, worktree_id="wt-lc", action="create")
    assert r1["state"] == "create"

    # execute
    r2 = univer_execute(file=univer_file, unit_id="u1", worktree_id="wt-lc",
                       code="setValue", )
    assert r2["mutated"] is True

    # ready
    r3 = univer_worktree(file=univer_file, worktree_id="wt-lc", action="ready")
    assert r3["state"] == "ready"

    # 错误模式
    r4 = univer_worktree(file=univer_file, worktree_id="wt-lc", action="invalid_action")
    assert not r4["ok"]

    print(f"[PASS] worktree_lifecycle: create → execute → ready + 错误模式拒绝")


if __name__ == "__main__":
    test_47_14_all_13_tools()
    test_47_14_artifact_persistence()
    test_47_14_worktree_lifecycle()
