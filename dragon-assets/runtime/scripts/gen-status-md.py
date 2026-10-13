#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen-status-md.py · 天龙引擎 STATUS.md dashboard generator
==========================================================

Aggregates:
  - INDEX_MASTER.json (5-asset totals)
  - skill-admin.py --json (5-class data quality)
  - check-cjk-filenames.py --emit-runbook (filename mojibake count)

Writes STATUS.md to repo root. ASCII-only — safe for any harness.

Usage:
    python scripts/gen-status-md.py
    python scripts/gen-status-md.py --output STATUS.md
    python scripts/gen-status-md.py --json-only
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INDEX_DIR = REPO / "index"
MASTER = INDEX_DIR / "INDEX_MASTER.json"


def load_master() -> dict:
    if not MASTER.exists():
        return {}
    return json.loads(MASTER.read_text(encoding="utf-8"))


def run_skill_admin() -> dict:
    """Invoke scripts/skill-admin.py --json and parse output."""
    try:
        out = subprocess.run(
            [sys.executable, str(REPO / "scripts" / "skill-admin.py"), "--json"],
            capture_output=True, text=True, timeout=60, cwd=str(REPO),
            encoding="utf-8", errors="replace",
        )
        if out.returncode not in (0, 1):  # 0=clean, 1=issues found
            return {}
        return json.loads(out.stdout)
    except Exception:
        return {}


def count_cjk() -> int:
    try:
        out = subprocess.run(
            [sys.executable, str(REPO / "scripts" / "check-cjk-filenames.py")],
            capture_output=True, text=True, timeout=60, cwd=str(REPO),
            encoding="utf-8", errors="replace",
        )
        m = re.search(r"\[(?:WARN|OK)\]\D+(\d+)", out.stdout)
        if m:
            return int(m.group(1))
        return 0
    except Exception:
        return -1


def render_markdown(master: dict, admin: dict, cjk_count: int) -> str:
    lines: list[str] = []
    lines.append("# STATUS")
    lines.append("")
    lines.append(f"_generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_")
    lines.append(f"_repo: `{REPO}`_")
    lines.append("")
    lines.append("---")
    lines.append("")

    # === Block 1: 5-asset index ===
    lines.append("## 1. Five-asset index")
    lines.append("")
    counts = master.get("counts", {})
    total = master.get("total", "?")
    schema = master.get("schema", "?")
    lines.append(f"- **schema**: `{schema}`")
    lines.append(f"- **total**: {total}")
    if counts:
        lines.append("")
        lines.append("| kind | count | jsonl |")
        lines.append("|------|-------|-------|")
        for kind in ("skill", "agent", "hook", "command", "plugin"):
            n = counts.get(kind, 0)
            j = master.get("files", {}).get(kind, "?")
            lines.append(f"| {kind} | {n} | `{j}` |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # === Block 2: Data quality ===
    lines.append("## 2. Data quality (skill-admin)")
    lines.append("")
    if admin:
        c = admin.get("counts", {})
        total = sum(c.values())
        lines.append("| class | count | threshold |")
        lines.append("|-------|-------|-----------|")
        lines.append(f"| A: license unknown | {c.get('A_license_unknown', '?')} | < 800 |")
        lines.append(f"| B: triggers missing | {c.get('B_triggers_missing', '?')} | < 600 |")
        lines.append(f"| C: AGPL no NOTICE | {c.get('C_AGPL_missing_NOTICE', '?')} | == 0 |")
        lines.append(f"| D: size / pycache | {c.get('D_size_or_pycache', '?')} | == 0 |")
        lines.append(f"| E: stale (pre-2026) | {c.get('E_stale_pre_2026', '?')} | < 100 |")
        lines.append(f"| **TOTAL ISSUES** | **{total}** | |")
        # color hint based on threshold violations
        bad = []
        if c.get("A_license_unknown", 0) > 800: bad.append("A")
        if c.get("B_triggers_missing", 0) > 600: bad.append("B")
        if c.get("C_AGPL_missing_NOTICE", 0) > 0: bad.append("C")
        if c.get("D_size_or_pycache", 0) > 0: bad.append("D")
        if c.get("E_stale_pre_2026", 0) > 100: bad.append("E")
        if bad:
            lines.append("")
            lines.append(f"Over threshold: {', '.join(bad)}")
    else:
        lines.append("_skill-admin.py not run or failed_")
    lines.append("")
    lines.append("---")
    lines.append("")

    # === Block 3: CJK filename mojibake ===
    lines.append("## 3. Filename mojibake (CJK GBK-misread)")
    lines.append("")
    if cjk_count == 0:
        lines.append("**[OK]** 0 corrupted filenames.")
    elif cjk_count < 0:
        lines.append("_check-cjk-filenames.py failed to run_")
    else:
        lines.append(f"**[WARN]** {cjk_count} corrupted filenames.")
        lines.append("")
        lines.append("See `docs/cjk-rename-runbook.md` for manual `git mv` checklist.")
        lines.append("Open Windows cmd (not bash) and apply renames one by one.")
        lines.append("After rename: rerun this generator; expect cjk_count == 0.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # === Block 4: Health checklist ===
    lines.append("## 4. Health checklist (run these weekly)")
    lines.append("")
    lines.append("```bash")
    lines.append("python scripts/build-index.py --include-library")
    lines.append("python tests/test_index.py")
    lines.append("python scripts/skill-admin.py")
    lines.append("python scripts/check-cjk-filenames.py --emit-runbook docs/cjk-rename-runbook.md")
    lines.append("python scripts/gen-status-md.py")
    lines.append("```")
    lines.append("")
    lines.append("CI equivalent: `.github/workflows/index-sync.yml` runs steps 1-5")
    lines.append("on every push to master/main and weekly on Sunday 03:00 UTC.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    ap = argparse.ArgumentParser(description="Generate STATUS.md dashboard")
    ap.add_argument("--output", default=str(REPO / "STATUS.md"))
    ap.add_argument("--json-only", action="store_true",
                    help="Print status as JSON instead of markdown")
    args = ap.parse_args()

    master = load_master()
    admin = run_skill_admin()
    cjk = count_cjk()

    if args.json_only:
        print(json.dumps({
            "master": master,
            "admin": admin,
            "cjk_corrupted": cjk,
        }, indent=2, ensure_ascii=False))
        return 0

    md = render_markdown(master, admin, cjk)
    Path(args.output).write_text(md, encoding="utf-8")
    print(f"[OK] STATUS.md written: {args.output}")
    print(f"     assets={master.get('total', '?')} · issues={admin.get('total_issues', '?')} · cjk={cjk}")
    return 0


if __name__ == "__main__":
    sys.exit(main())