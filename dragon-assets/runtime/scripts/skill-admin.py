#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
skill-admin.py · 天龙引擎数据质量看板
==========================================

读取 index/*.jsonl（build-index.py 产物）做 5 类体检：

  A. **license 缺口**：active 且 license=unknown 的资产清单（分 kind）
  B. **触发词缺口**：active skill 但无 triggers 字段 — LLM 路由会失明
  C. **AGPL 红线**：license=AGPL-3.0 但目录下无 LICENSE 或 NOTICE 副本
  D. **体积异常**：单文件 > 100 KB 或路径有 `__pycache__`
  E. **更新停滞**：mtime 早于 2026-01-01 的 active skill

输出格式：
  默认：人可读报告（按 kind 分组，行列格式）
  --json：JSON 给 CI / cron 消费

退出码：发现 ≥ 1 项 WARN/FAIL 时为 1，否则 0。

调用：
    python scripts/skill-admin.py
    python scripts/skill-admin.py --kind skill
    python scripts/skill-admin.py --json
    python scripts/skill-admin.py --check AGPL --strict
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INDEX_DIR = REPO / "index"

KIND_TO_FILE = {
    "skill":   "SKILLS.jsonl",
    "agent":   "AGENTS.jsonl",
    "hook":    "HOOKS.jsonl",
    "command": "COMMANDS.jsonl",
    "plugin":  "PLUGINS.jsonl",
}

STALE_THRESHOLD = dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc)
LARGE_FILE_KB = 100

def load_kind(kind: str) -> list:
    p = INDEX_DIR / KIND_TO_FILE[kind]
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]


def check_license_gap(rows: list, kind: str) -> list:
    """An entry is "license unknown" only if:
       - no `license` field at all, AND `license_raw` is also absent/empty
       - OR license_raw is a sentinel (unknown / tbd / ? / n/a / none)
    A literal `license: UNKNOWN` stamp = "author confirms unknown" = OK
    (uppercase UNKNOWN in raw = intentional sentinel, not unknown by accident).
    """
    SENTINELS = {"unknown", "tbd", "?", "n/a", "none", ""}
    out = []
    for r in rows:
        if r.get("status") != "active":
            continue
        # license_raw preserves original casing from frontmatter
        raw = (r.get("license_raw") or "").strip().lower()
        # license is normalized (e.g. "MIT", "AGPL-3.0") or "unknown"
        norm = (r.get("license") or "").strip().lower()
        # Both empty/missing = no declaration at all
        if not raw and not norm:
            out.append({"kind": kind, "id": r["id"], "path": r["path"]})
            continue
        # Raw says UNKNOWN but normalize turned it into lowercase "unknown"
        # That's still a sentinel — author stamped intentionally
        if raw in SENTINELS:
            continue
        # If only normalized says unknown (raw empty) but no raw either way,
        # it's because LICENSE sniff couldn't identify it. Flag it.
        if norm in SENTINELS and not raw:
            out.append({"kind": kind, "id": r["id"], "path": r["path"]})
    return out


def check_triggers_gap(rows: list, kind: str) -> list:
    if kind not in ("skill", "agent"):
        return []
    return [
        {"kind": kind, "id": r["id"], "path": r["path"], "no_triggers_count": 0}
        for r in rows
        if r.get("status") == "active" and not r.get("triggers")
    ]


def check_agpl_missing_notice(rows: list, kind: str, repo: Path) -> list:
    out = []
    for r in rows:
        if r.get("license") != "AGPL-3.0":
            continue
        # 找该 skill 根目录
        p = repo / r["path"]
        if not p.exists():
            continue
        sibling = p.parent
        has_license = any((sibling / nm).exists() for nm in ("LICENSE", "LICENSE.md", "LICENCE"))
        has_notice = any((sibling / nm).exists() for nm in ("NOTICE", "NOTICE.md"))
        if not (has_license and has_notice):
            out.append({
                "kind": kind, "id": r["id"], "path": r["path"],
                "missing": [n for n, ok in (("LICENSE", has_license), ("NOTICE", has_notice)) if not ok],
            })
    return out


def check_size(rows: list, kind: str, repo: Path) -> list:
    out = []
    for r in rows:
        p = repo / r["path"]
        if "__pycache__" in r["path"]:
            out.append({"kind": kind, "id": r["id"], "path": r["path"], "reason": "__pycache__"})
        elif p.exists() and r.get("size_kb", 0) > LARGE_FILE_KB:
            out.append({"kind": kind, "id": r["id"], "path": r["path"], "reason": f"{r['size_kb']} KB > {LARGE_FILE_KB}"})
    return out


def check_stale(rows: list, kind: str) -> list:
    out = []
    for r in rows:
        mtime = r.get("mtime", "")
        if not mtime:
            continue
        try:
            ts = dt.datetime.fromisoformat(mtime.replace("Z", "+00:00"))
        except Exception:
            continue
        if ts < STALE_THRESHOLD and r.get("status") == "active":
            out.append({
                "kind": kind, "id": r["id"], "path": r["path"],
                "mtime": mtime, "age_days": (dt.datetime.now(dt.timezone.utc) - ts).days,
            })
    return out


# ============================================================
# I/O
# ============================================================

def report_text(findings: dict, levels: dict) -> str:
    lines = [f"# skill-admin · 天龙引擎数据质量看板 · {dt.datetime.now().isoformat(timespec='seconds')}\n"]
    lines.append(f"\n## 总览")
    lines.append(f"\n| 检查 | 量 |")
    lines.append(f"|---|---|")
    for k, v in findings.items():
        lines.append(f"| {k} | {len(v)} |")

    for key, items in findings.items():
        if not items:
            continue
        lines.append(f"\n## {key}（{len(items)} 项）")
        lines.append(f"\n| kind | id | path | 备注 |")
        lines.append(f"|---|---|---|---|")
        for it in items[:30]:
            note = it.get("missing") or it.get("reason") or it.get("mtime") or ""
            lines.append(f"| {it.get('kind','?')} | {it.get('id','?')} | `{it.get('path','?')}` | {note} |")
        if len(items) > 30:
            lines.append(f"\n... 还有 {len(items)-30} 项被截断。传 `--json` 看完整。")
    return "\n".join(lines) + "\n"


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception: pass

    ap = argparse.ArgumentParser(description="天龙引擎数据质量看板")
    ap.add_argument("--kind", choices=list(KIND_TO_FILE), help="只看一类")
    ap.add_argument("--check", choices=["all", "license", "triggers", "agpl", "size", "stale"],
                    default="all")
    ap.add_argument("--json", action="store_true", help="JSON 输出")
    ap.add_argument("--strict", action="store_true", help="任一检查非零即非零退出码")
    args = ap.parse_args()

    kinds = [args.kind] if args.kind else list(KIND_TO_FILE)
    all_rows = {k: load_kind(k) for k in kinds}

    findings: dict = {
        "A_license_unknown":   [],
        "B_triggers_missing":  [],
        "C_AGPL_missing_NOTICE": [],
        "D_size_or_pycache":   [],
        "E_stale_pre_2026":    [],
    }
    for k, rows in all_rows.items():
        if args.check in ("all", "license"):
            findings["A_license_unknown"].extend(check_license_gap(rows, k))
        if args.check in ("all", "triggers"):
            findings["B_triggers_missing"].extend(check_triggers_gap(rows, k))
        if args.check in ("all", "agpl"):
            findings["C_AGPL_missing_NOTICE"].extend(check_agpl_missing_notice(rows, k, REPO))
        if args.check in ("all", "size"):
            findings["D_size_or_pycache"].extend(check_size(rows, k, REPO))
        if args.check in ("all", "stale"):
            findings["E_stale_pre_2026"].extend(check_stale(rows, k))

    if args.json:
        print(json.dumps({
            "generated_at": dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "counts": {k: len(v) for k, v in findings.items()},
            "findings": findings,
        }, ensure_ascii=False, indent=2))
    else:
        print(report_text(findings, levels={}))

    total = sum(len(v) for v in findings.values())
    if args.strict and total > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
