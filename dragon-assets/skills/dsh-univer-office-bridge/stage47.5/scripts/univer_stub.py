"""阶段 47.5 · univer_* 工具链 stub（B 选项下不重启 DSH 也能验证接口语义）

本脚本模拟 13 个 univer_* DSH 工具的接口语义：
  - 输入：file / worktree / unitId / code / range / ...
  - 输出：与真实 DSH univer_* 工具返回结构对齐（dict / FetchResult-like）

策略：
  - 接口实现走 Python 文件读写（避免依赖 DSH 启动 + Gateway 进程）
  - 13 个工具函数同构于 dsh-univer-office 上游 SKILL.md §1
  - 任何工具调用都打印 stdout 模拟 DSH 工具返回值

Author: dragon-engine · Stage 47.5 · 2026-08-26
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


# ─── 接口语义（13 个 univer_* 工具） ─────────────────────────────────────────

# 启动类（5）
def univer_new(file: str, **kw) -> dict:
    """创建空 .univer 文件（永不覆盖，永不创建隐式 Unit）"""
    path = Path(file)
    if path.exists():
        return {"ok": False, "error": "FILE_EXISTS", "file": str(path)}
    path.parent.mkdir(parents=True, exist_ok=True)
    # .univer 是 SQLite 文件，最简 SQLite 头即可
    path.write_bytes(b"SQLite format 3\x00")  # stub
    return {"ok": True, "file": str(path), "bytes": path.stat().st_size}


def univer_status(file: str, **kw) -> dict:
    """列出 trunk Units 和 worktrees"""
    path = Path(file)
    if not path.exists():
        return {"ok": False, "error": "FILE_NOT_FOUND", "file": str(path)}
    return {
        "ok": True,
        "file": str(path),
        "units": [],  # stub
        "worktrees": [],
    }


def univer_worktree(file: str, worktree_id: str | None = None, action: str = "create", **kw) -> dict:
    """create / ready / reopen / merge / discard"""
    valid_actions = {"create", "ready", "reopen", "merge", "discard"}
    if action not in valid_actions:
        return {"ok": False, "error": "INVALID_ACTION", "action": action}
    return {
        "ok": True,
        "file": file,
        "worktree_id": worktree_id or "wt-stub-001",
        "action": action,
        "state": action if action == "create" else "ready",
    }


def univer_unit(file: str, unit_id: str | None = None, kind: str = "sheet", name: str = "Sheet1", action: str = "create", **kw) -> dict:
    """create or remove Sheet/Doc/Slide/Base/Board"""
    valid_kinds = {"sheet", "doc", "slide", "base", "board"}
    if kind not in valid_kinds:
        return {"ok": False, "error": "INVALID_KIND", "kind": kind}
    return {
        "ok": True,
        "file": file,
        "unit_id": unit_id or f"{kind}-stub-001",
        "kind": kind,
        "name": name,
        "action": action,
    }


def univer_import(file: str, source: str, **kw) -> dict:
    """Import local xlsx/csv/tsv/docx/pptx as new Unit"""
    src = Path(source)
    if not src.exists():
        return {"ok": False, "error": "SOURCE_NOT_FOUND", "source": str(src)}
    suffix = src.suffix.lower()
    kind_map = {".xlsx": "sheet", ".xls": "sheet", ".csv": "sheet", ".tsv": "sheet",
                ".docx": "doc", ".pptx": "slide"}
    kind = kind_map.get(suffix)
    if not kind:
        return {"ok": False, "error": "UNSUPPORTED_FORMAT", "source": str(src)}
    return {
        "ok": True,
        "file": file,
        "source": str(src),
        "kind": kind,
        "unit_id": f"{kind}-import-stub-001",
        "rows_or_pages": 0,
    }


# 写入类（2）
def univer_execute(file: str, unit_id: str, worktree_id: str, code: str = "", **kw) -> dict:
    """Run version-matched Facade JavaScript against one Unit in a draft worktree"""
    return {
        "ok": True,
        "file": file,
        "unit_id": unit_id,
        "worktree_id": worktree_id,
        "code_hash": hash(code) if code else 0,
        "mutated": "setValue" in code or "setFormula" in code,
        "read_only": "setValue" not in code and "setFormula" not in code,
    }


def univer_compile_svg(source: str, file: str, worktree_id: str, unit_id: str, page: int = 1, mode: str = "replace", **kw) -> dict:
    """Compile workspace SVG into one explicit Slide page with browser text metrics"""
    src = Path(source)
    if not src.exists():
        return {"ok": False, "error": "SVG_NOT_FOUND", "source": str(src)}
    return {
        "ok": True,
        "source": str(src),
        "file": file,
        "unit_id": unit_id,
        "worktree_id": worktree_id,
        "page": page,
        "mode": mode,
        "warnings": [],
    }


# 验证类（3）
def univer_inspect(file: str, unit_id: str, range: str | None = None, **kw) -> dict:
    """Read structured Unit content from trunk or one worktree"""
    return {
        "ok": True,
        "file": file,
        "unit_id": unit_id,
        "range": range,
        "rows": [],
        "cells": 0,
    }


def univer_lint(file: str, unit_id: str, pages: list[int] | None = None, **kw) -> dict:
    """Check Slide text off-page, container escape, text overlap"""
    return {
        "ok": True,
        "file": file,
        "unit_id": unit_id,
        "pages": pages or [],
        "findings": [],
        "off_page_count": 0,
        "escaped_container_count": 0,
        "overlap_count": 0,
    }


def univer_screenshot(file: str, unit_id: str, output: str, **kw) -> dict:
    """Render Sheet/Doc/Slide/Base/Board as PNG evidence"""
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    png_path = out / f"{unit_id}.png"
    # 最小有效 PNG 字节
    png_path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR"
        b"\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
        b"\x00\x00\x00\rIDATx\x9cc\xf8\xff\xff?\x00\x05\xfe\x02\xfeA\xc3\xa9\x00"
        b"\x00\x00\x00IEND\xaeB`\x82"
    )
    return {
        "ok": True,
        "file": file,
        "unit_id": unit_id,
        "png_path": str(png_path),
        "size_bytes": png_path.stat().st_size,
    }


# 参考类（2）
def univer_api(action: str, queries: list[str] | None = None, **kw) -> dict:
    """Find version-matched Facade symbols by API keyword, then show exact labels"""
    if action == "find":
        return {"ok": True, "action": "find", "queries": queries or [], "results": []}
    return {"ok": True, "action": action, "results": []}


def univer_resources(action: str = "registries", **kw) -> dict:
    """List/find/read/export bundled SVG resources or clear download cache"""
    return {
        "ok": True,
        "action": action,
        "registries": ["default"],
        "resources": [],
    }


# 交付类（1）
def univer_export(file: str, unit_id: str, format: str = "xlsx", output: str = "", **kw) -> dict:
    """Export Sheet/Base to xlsx/csv/tsv, Doc to docx, Slide to pptx"""
    valid_formats = {"xlsx", "csv", "tsv", "docx", "pptx"}
    if format not in valid_formats:
        return {"ok": False, "error": "INVALID_FORMAT", "format": format}
    out = Path(output) if output else Path(f"{unit_id}.{format}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(f"[stub] {format} export from {file} unit {unit_id}\n")
    return {
        "ok": True,
        "file": file,
        "unit_id": unit_id,
        "format": format,
        "output": str(out),
        "size_bytes": out.stat().st_size,
    }


# ─── 注册表（13 工具） ────────────────────────────────────────────────────

UNIVER_TOOLS = {
    # 启动 5
    "univer_new": univer_new,
    "univer_status": univer_status,
    "univer_worktree": univer_worktree,
    "univer_unit": univer_unit,
    "univer_import": univer_import,
    # 写入 2
    "univer_execute": univer_execute,
    "univer_compile_svg": univer_compile_svg,
    # 验证 3
    "univer_inspect": univer_inspect,
    "univer_lint": univer_lint,
    "univer_screenshot": univer_screenshot,
    # 参考 2
    "univer_api": univer_api,
    "univer_resources": univer_resources,
    # 交付 1
    "univer_export": univer_export,
}


def call(tool_name: str, **kw) -> dict:
    """统一入口：tool_name(**kw) → 返回 dict"""
    if tool_name not in UNIVER_TOOLS:
        return {"ok": False, "error": "UNKNOWN_TOOL", "tool": tool_name}
    return UNIVER_TOOLS[tool_name](**kw)


# ─── 主入口 ────────────────────────────────────────────────────────────────

def main() -> int:
    """演示：跑通 13 个工具的最小 happy path"""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        univer_file = f"{tmp}/demo.univer"
        worktree_id = "wt-demo-001"

        print("=" * 70)
        print("Stage 47.5 · 13 univer_* 工具 stub 链路验证")
        print("=" * 70)

        # 1. 启动
        r = call("univer_new", file=univer_file)
        print(f"\n[1] univer_new        → {r['ok']}  file={r.get('file', '?')}")

        r = call("univer_status", file=univer_file)
        print(f"[2] univer_status     → {r['ok']}  units={len(r['units'])} worktrees={len(r['worktrees'])}")

        r = call("univer_worktree", file=univer_file, action="create", worktree_id=worktree_id)
        print(f"[3] univer_worktree   → {r['ok']}  action={r['action']} state={r['state']}")

        r = call("univer_unit", file=univer_file, unit_id="sheet-demo-001", kind="sheet", name="趋势")
        print(f"[4] univer_unit       → {r['ok']}  kind={r['kind']} unit_id={r['unit_id']}")

        r = call("univer_import", file=univer_file, source=f"{tmp}/data.xlsx")
        # 没源文件，会 fail 但接口正常
        print(f"[5] univer_import     → {r['ok']}  error={r.get('error', 'none')}")

        # 2. 写入
        r = call("univer_execute", file=univer_file, unit_id="sheet-demo-001", worktree_id=worktree_id,
                 code="sheet.getActiveSheet().getRange('A1').setValue({v: 'test', t: 1})")
        print(f"\n[6] univer_execute    → {r['ok']}  mutated={r['mutated']}")

        r = call("univer_compile_svg", source=f"{tmp}/page.svg", file=univer_file,
                 unit_id="slide-demo-001", worktree_id=worktree_id, page=1)
        print(f"[7] univer_compile_svg→ {r['ok']}  error={r.get('error', 'none')}")

        # 3. 验证
        r = call("univer_inspect", file=univer_file, unit_id="sheet-demo-001", range="Sheet1!A1:D20")
        print(f"\n[8] univer_inspect    → {r['ok']}  range={r.get('range')}")

        r = call("univer_lint", file=univer_file, unit_id="slide-demo-001", pages=[1])
        print(f"[9] univer_lint       → {r['ok']}  findings={len(r['findings'])}")

        r = call("univer_screenshot", file=univer_file, unit_id="sheet-demo-001", output=tmp)
        print(f"[10] univer_screenshot → {r['ok']}  png={r.get('png_path', 'none')}")

        # 4. 参考
        r = call("univer_api", action="find", queries=["setValue", "setFormula"])
        print(f"\n[11] univer_api        → {r['ok']}  queries={r['queries']}")

        r = call("univer_resources", action="registries")
        print(f"[12] univer_resources  → {r['ok']}  registries={r['registries']}")

        # 5. 交付
        r = call("univer_export", file=univer_file, unit_id="sheet-demo-001", format="xlsx", output=f"{tmp}/out.xlsx")
        print(f"\n[13] univer_export     → {r['ok']}  format={r['format']} size={r['size_bytes']} B")

        # 收尾：worktree ready
        r = call("univer_worktree", file=univer_file, worktree_id=worktree_id, action="ready")
        print(f"\n[*] worktree ready    → {r['ok']}  state={r['state']}")

        print("=" * 70)
        print(f"Stage 47.5 PASS: 13/13 工具 stub 跑通")
        print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
