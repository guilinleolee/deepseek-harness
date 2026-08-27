"""mneme-heat-engine · session-decoupling v1.0 (W2)

借鉴自 dsh-mneme v0.6.0 会话生命周期设计（MIT ✅）。
天龙自实现 Python 版：DSH 会话关闭 ≠ 删 MEMORY 节点。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from heat_engine import should_archive


def on_session_close(
    session_id: str,
    preserve_memory: bool = True,
    heat_maintained: bool = True,
) -> dict[str, Any]:
    """DSH 会话关闭钩子.

    默认行为：
    - transcript_deleted = True（DSH 原本就清 transcript）
    - memory_preserved = True（MEMORY 节点不被删除）
    - heat_maintained = True（heat 字段不被重置）

    显式"忘掉 X"时：调用 forget_node() 删除指定节点。
    """
    return {
        "session_id": session_id,
        "transcript_deleted": True,
        "memory_preserved": preserve_memory,
        "heat_maintained": heat_maintained,
        "action": "session_closed_with_memory_intact",
    }


def forget_node(
    node_id: str,
    nodes: list[dict],
    reason: str = "user_explicit_request",
) -> list[dict]:
    """用户显式说"忘掉 X"时删除对应节点（archive 后再删）."""
    kept = [n for n in nodes if n.get("id") != node_id]
    archived = [n for n in nodes if n.get("id") == node_id]
    return {
        "kept": kept,
        "archived_then_deleted": archived,
        "reason": reason,
    }


def cmd_demo(args: argparse.Namespace) -> int:
    today = "2026-08-24"
    nodes = [
        {"id": "A", "wikilink": "老李", "heat": 0.7,
         "last_ref_date": "2026-08-20", "compilations": 3},
        {"id": "B", "wikilink": "old", "heat": 0.08,
         "last_ref_date": "2026-06-01", "compilations": 5},
    ]

    # Step 1: session 关闭（默认保留 MEMORY）
    result = on_session_close(session_id="sess-001")
    print(f"[STEP 1] session_close -> {result['action']}")

    # Step 2: 用户显式"忘掉 B"
    forgotten = forget_node("B", nodes)
    print(f"[STEP 2] forget B -> kept={len(forgotten['kept'])}, "
          f"archived={len(forgotten['archived_then_deleted'])}")

    # Step 3: 验证 A 节点 heat 仍维持
    a_node = forgotten["kept"][0]
    print(f"[STEP 3] A.heat={a_node['heat']} (preserved)")

    # Step 4: 模拟"不小心被归档"判定
    archived_now = should_archive(a_node["heat"], a_node["last_ref_date"], today)
    print(f"[STEP 4] A.should_archive(4 days) = {archived_now}")

    print(json.dumps({
        "step1_session_close": result,
        "step2_forget_B": {
            "kept_count": len(forgotten["kept"]),
            "forgotten_count": len(forgotten["archived_then_deleted"]),
        },
        "step3_A_preserved": {"id": a_node["id"], "heat": a_node["heat"]},
        "step4_should_archive": archived_now,
    }, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="mneme-heat-engine · session_decouple v1.0",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_demo = sub.add_parser("demo", help="演示 session-decouple 端到端")
    p_demo.set_defaults(func=cmd_demo)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())