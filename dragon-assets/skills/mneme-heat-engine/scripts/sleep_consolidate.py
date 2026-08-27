"""mneme-heat-engine · sleep_consolidate 4 阶段 v1.0

借鉴自 dsh-mneme v0.4.0 Sleep Mode 设计（MIT ✅）。
天龙自实现 Python 版（仅演示骨架，生产需对接 MEMORY.md 解析器）。
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone

PHASES = ["DEDUPE", "MERGE", "ARCHIVE", "REBIRTH"]


def phase1_dedupe(nodes: list[dict]) -> list[dict]:
    """Phase 1 去重：wikilink 相同的节点合并.

    演示逻辑：按 wikilink 分组，compilations 取 max，heat 取 max。
    """
    by_link: dict[str, dict] = {}
    for n in nodes:
        link = n.get("wikilink", n.get("id", ""))
        if link in by_link:
            cur = by_link[link]
            cur["compilations"] = max(cur.get("compilations", 1),
                                      n.get("compilations", 1))
            cur["heat"] = max(cur.get("heat", 0), n.get("heat", 0))
        else:
            by_link[link] = dict(n)
    return list(by_link.values())


def phase2_merge(nodes: list[dict]) -> list[dict]:
    """Phase 2 合并：相邻碎片合并.

    演示逻辑：返回原 list（生产实现需按主题 + 时间窗聚类）。
    """
    return list(nodes)


def phase3_archive(nodes: list[dict], today: str) -> tuple[list[dict], list[dict]]:
    """Phase 3 归档：heat < 0.1 且 last_ref > 30 天 → archive."""
    from datetime import date
    active, archive = [], []
    for n in nodes:
        heat = n.get("heat", 0)
        last_ref = n.get("last_ref_date", today)
        last = date.fromisoformat(last_ref)
        now = date.fromisoformat(today)
        days = (now - last).days
        if heat < 0.1 and days > 30:
            archive.append(n)
        else:
            active.append(n)
    return active, archive


def phase4_rebirth(archive: list[dict], referenced_ids: list[str]) -> list[dict]:
    """Phase 4 重生：archive 节点被重新引用 → 召回主表."""
    rebirth = []
    for n in archive:
        if n.get("id") in referenced_ids:
            n["heat"] = 0.7
            n["last_ref_date"] = datetime.now(timezone.utc).date().isoformat()
            rebirth.append(n)
    return rebirth


def cmd_demo(args: argparse.Namespace) -> int:
    today = args.today
    nodes = [
        {"id": "A", "wikilink": "老李", "heat": 0.7,
         "last_ref_date": "2026-08-20", "compilations": 3},
        {"id": "A2", "wikilink": "老李", "heat": 0.5,
         "last_ref_date": "2026-07-15", "compilations": 2},
        {"id": "B", "wikilink": "old", "heat": 0.08,
         "last_ref_date": "2026-06-01", "compilations": 5},
        {"id": "C", "wikilink": "khazix-writer", "heat": 0.85,
         "last_ref_date": "2026-08-23", "compilations": 10},
    ]
    referenced = ["B"]

    log = {}
    log["phase1_dedupe_input"] = len(nodes)
    nodes = phase1_dedupe(nodes)
    log["phase1_dedupe_output"] = len(nodes)

    log["phase2_merge_input"] = len(nodes)
    nodes = phase2_merge(nodes)
    log["phase2_merge_output"] = len(nodes)

    active, archive = phase3_archive(nodes, today)
    log["phase3_archive_active"] = len(active)
    log["phase3_archive_archived"] = len(archive)

    rebirth = phase4_rebirth(archive, referenced)
    log["phase4_rebirth_count"] = len(rebirth)
    final_active = active + rebirth
    log["final_active_count"] = len(final_active)

    print(json.dumps({
        "today": today,
        "log": log,
        "active_ids": [n["id"] for n in final_active],
        "archived_ids": [n["id"] for n in archive
                         if n["id"] not in referenced],
    }, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="mneme-heat-engine · sleep_consolidate 4 阶段 v1.0",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_demo = sub.add_parser("demo", help="演示 4 阶段端到端")
    p_demo.add_argument("--today", default="2026-08-24")
    p_demo.set_defaults(func=cmd_demo)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())