"""nomifun_delegate_cli V1.0 — Stage 46 nomifun-methodology.

借鉴 nomifun 三件模型工具协议（nomi_delegate / nomi_execution_get / nomi_execution_update），
输出天龙自研最小骨架 CLI（**离线模式**· 不调用 nomifun runtime）。

参考：https://github.com/nomifun/nomifun-desktop/blob/main/docs/architecture/agent-execution.zh.md §6

3 个子命令：
- plan <goal>          输出一份 initial YAML plan
- get <execution_id>   从本地 YAML cache 读取 / 摘要（mock）
- update <id> <cmd>    走 nomi_execution_update 协议（mock）

DON'T:
- 不要连真 nomifun runtime
- 不要 import nomi-* 任何 crate
- 不要把 plan 输出写到 /etc/passwd 之类
"""
from __future__ import annotations

import argparse
import datetime as _dt
import sys
import uuid
from pathlib import Path


def _now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def cmd_plan(goal: str, max_parallel: int = 4) -> int:
    ex_id = f"exec-{uuid.uuid4().hex[:12]}"
    plan_lines = [
        f"execution_id: {ex_id}",
        f"goal: |",
        f"  {goal}",
        f"owner: tianlong",
        f"created_at: {_now_iso()}",
        f"delegation_policy: disabled",
        f"plan_gate: require_approval",
        f"decision_policy: ask_user",
        f"adaptation_policy: fixed",
        f"max_parallel: {max_parallel}",
        f"execution_model_pool:",
        f"  type: single",
        f"  model: tianlong-default",
        f"participants:",
        f"  - name: tianlong-agent",
        f"    agent_type: tianlong",
        f"    sort_order: 0",
        f"    max_concurrency: {max_parallel}",
        f"steps:",
        f"  - step_id: step-1",
        f"    role: planner",
        f"    tool_policy: full",
        f"    delegation_depth: 0",
        f"  - step_id: step-2",
        f"    role: implementer",
        f"    tool_policy: read_only",
        f"    delegation_depth: 0",
        f"attempts: []",
        f"dependencies: []",
        f"events:",
        f"  - type: created",
        f"    actor: tianlong",
        f"    at: {_now_iso()}",
    ]
    print("\n".join(plan_lines))
    return 0


def cmd_get(execution_id: str) -> int:
    print(f"[mock] reading {execution_id}")
    print("status: planning")
    print(f"checked_at: {_now_iso()}")
    print("---EXIT: 0---")
    return 0


_ALLOWED_UPDATES = {
    "approve", "replan", "adjust", "add", "rename", "update_step",
    "reassign", "configure", "steer", "retry", "pause", "resume",
    "cancel", "request_user_decision",
}


def cmd_update(execution_id: str, action: str) -> int:
    if action not in _ALLOWED_UPDATES:
        print(f"[FAIL] action '{action}' not in allowed set: {sorted(_ALLOWED_UPDATES)}")
        return 1
    print(f"[mock] {execution_id} ← {action} @ {_now_iso()}")
    print("status updated")
    print("---EXIT: 0---")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="nomifun_delegate_cli V1.0 — Stage 46 borrow-only scaffold")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_plan = sub.add_parser("plan", help="create initial execution plan (offline)")
    p_plan.add_argument("goal")
    p_plan.add_argument("--max-parallel", type=int, default=4)

    p_get = sub.add_parser("get", help="read execution summary (mock)")
    p_get.add_argument("execution_id")

    p_up = sub.add_parser("update", help="send execution_update action (mock)")
    p_up.add_argument("execution_id")
    p_up.add_argument("action", choices=sorted(_ALLOWED_UPDATES))

    args = parser.parse_args(argv)

    if args.cmd == "plan":
        return cmd_plan(args.goal, args.max_parallel)
    if args.cmd == "get":
        return cmd_get(args.execution_id)
    if args.cmd == "update":
        return cmd_update(args.execution_id, args.action)
    return 2


if __name__ == "__main__":
    sys.exit(main())
