#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rename-cjk.py · 天龙引擎 CJK 误码文件名批量重命名
====================================================

策略：读 `docs/cjk-rename-runbook.md` 表格（`# | source | target | type`），
解析出 34 条 `src -> dst` 映射，scan 磁盘确认每条 src 真实存在，然后
按需 dry-run 或 --apply。

源 runbook 由 `scripts/check-cjk-filenames.py --emit-runbook` 生成，
目标列含中文（受 harness 影响：runbook 里 target 字段由用户手动审过）。

⚠️ 默认 dry-run。加 `--apply` 才真改 + .bak 备份到 .cjk-rename-bak/。
   加 `--emit-powershell` 输出可在 PowerShell 直接执行的脚本块。

调用：
    python scripts/rename-cjk.py                # dry-run
    python scripts/rename-cjk.py --apply        # 实际 rename
    python scripts/rename-cjk.py --emit-powershell   # 打印 PowerShell
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RUNBOOK = REPO / "docs" / "cjk-rename-runbook.md"
BAK_ROOT = REPO / ".cjk-rename-bak"
TABLE_ROW = re.compile(r"^\|\s*(\d+)\s*\|\s*`([^`]+)`\s*\|\s*`([^`]+)`\s*\|\s*(\w+)\s*\|$")


def parse_runbook() -> list[tuple[str, str, str]]:
    """Return [(src_rel, dst_rel, kind), ...] from the runbook table."""
    if not RUNBOOK.exists():
        return []
    rows: list[tuple[str, str, str]] = []
    for line in RUNBOOK.read_text(encoding="utf-8", errors="replace").splitlines():
        m = TABLE_ROW.match(line.strip())
        if m:
            _, src, dst, kind = m.groups()
            rows.append((src, dst, kind))
    return rows


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    ap = argparse.ArgumentParser(description="天龙引擎 CJK 误码文件名批量重命名")
    ap.add_argument("--runbook", default=str(RUNBOOK),
                    help=f"runbook 路径 (default: {RUNBOOK})")
    ap.add_argument("--apply", action="store_true",
                    help="实际重命名（默认 dry-run）")
    ap.add_argument("--emit-powershell", action="store_true",
                    help="输出 PowerShell 一键脚本到 stdout")
    args = ap.parse_args()

    rows = parse_runbook()
    if not rows:
        print(f"[ERR] runbook 表为空或不存在: {args.runbook}", file=sys.stderr)
        return 1

    # Resolve to absolute paths.
    # The runbook "target" column is just the basename (e.g. "00调研师.md").
    # The correct dst = src.parent / dst_basename, NOT REPO / dst_basename
    # (else the file lands at repo root and loses its parent dir).
    plan: list[tuple[Path, Path, str]] = []
    missing: list[str] = []
    for src_rel, dst_rel, kind in rows:
        src = REPO / src_rel
        dst = src.parent / Path(dst_rel).name
        if not src.exists():
            missing.append(src_rel)
            continue
        plan.append((src, dst, kind))

    print(f"[INFO] runbook: {len(rows)} entries · resolved: {len(plan)}")
    if missing:
        print(f"[WARN] {len(missing)} src not on disk (already renamed?):", file=sys.stderr)
        for m in missing:
            print(f"        {m}", file=sys.stderr)

    if args.emit_powershell:
        print("# PowerShell · CJK 误码文件名一键重命名")
        print("# 在仓库根目录运行：powershell -File rename-cjk.ps1")
        print("# 或直接复制粘贴以下行")
        print()
        print("Set-Location", str(REPO).replace("/", "\\"))
        print()
        for src, dst, _kind in plan:
            s = str(src.relative_to(REPO)).replace("/", "\\")
            d = str(dst.relative_to(REPO)).replace("/", "\\")
            print(f'git mv "{s}" "{d}"')
        return 0

    # Show plan
    print()
    for src, dst, kind in plan:
        s = src.relative_to(REPO)
        d = dst.relative_to(REPO)
        print(f"  [{kind:4}] {s}")
        print(f"        -> {d}")

    if not args.apply:
        print()
        print("(dry-run) 加 --apply 才真改。")
        print("也可加 --emit-powershell 打印可在 PowerShell 直接运行的脚本。")
        return 0

    # Real rename
    BAK_ROOT.mkdir(exist_ok=True)
    print(f"\n[APPLY] renaming {len(plan)} · backup -> {BAK_ROOT}")
    n_ok = n_skip = n_err = 0
    for src, dst, _kind in plan:
        if dst.exists():
            print(f"  [SKIP] dst exists: {dst.relative_to(REPO)}")
            n_skip += 1
            continue
        # backup with subdir mirroring + parent mkdir
        bak_rel = src.relative_to(REPO)
        bak = BAK_ROOT / bak_rel
        bak.parent.mkdir(parents=True, exist_ok=True)
        if bak.exists():
            bak.unlink()
        try:
            if src.is_dir():
                shutil.copytree(src, bak)
            else:
                shutil.copy2(src, bak)
        except Exception as e:
            print(f"  [ERR]  backup {bak_rel}: {e}")
            n_err += 1
            continue
        try:
            src.rename(dst)
            n_ok += 1
        except Exception as e:
            print(f"  [ERR]  rename {src.name}: {e}")
            # restore from backup
            try:
                if dst.is_dir():
                    shutil.rmtree(dst, ignore_errors=True)
                    shutil.copytree(bak, src)
                else:
                    shutil.copy2(bak, src)
            except Exception:
                pass
            n_err += 1

    print(f"\n[DONE] renamed={n_ok}  skip={n_skip}  err={n_err}")
    print(f"\nNext:")
    print(f"  python scripts/build-index.py --include-library")
    print(f"  python scripts/check-cjk-filenames.py    # expect 0")
    return 0 if n_err == 0 else 1


if __name__ == "__main__":
    sys.exit(main())