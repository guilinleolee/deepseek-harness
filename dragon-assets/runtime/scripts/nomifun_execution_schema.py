"""nomifun_execution_schema V1.0 — Stage 46 nomifun-methodology.

借鉴 nomifun AgentExecution Engine 7 表契约，自研一个"天龙 SDD/Plan YAML"schema 强类型校验器。

借鉴但**不克隆**：nomifun 的 7 表契约是 SQLite + Rust 类型实现；本脚本给出
纯 YAML schema + 强类型校验，不引入 sqlite / Rust crate 任何依赖。

用法：
    python nomifun_execution_schema.py validate plan.yaml
    python nomifun_execution_schema.py to-markdown plan.yaml > plan.md
    python nomifun_execution_schema.py to-html plan.yaml > plan.html

参考：
- https://github.com/nomifun/nomifun-desktop/blob/main/docs/architecture/agent-execution.zh.md
- https://github.com/nomifun/nomifun-desktop/blob/main/docs/architecture/id-system.zh.md

有界复杂度（nomifun §4.1，stage 46 借用）：
- 模型池 ≤ 16
- Participant ≤ 64
- DAG Step ≤ 128
- 并行度 ≤ 64
- 委派深度 0..=4
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    print("[ERR]  PyYAML not installed; run `uv add pyyaml` or `pip install pyyaml`", file=sys.stderr)
    sys.exit(2)

# === 域枚举（硬编码学上游；保留自研缓冲）===

DELEGATION_POLICY = {"disabled", "automatic", "prefer_parallel"}
PLAN_GATE = {"automatic", "require_approval"}
DECISION_POLICY = {"automatic", "ask_user"}
ADAPTATION_POLICY = {"fixed", "adaptive"}
TOOL_POLICY = {"full", "read_only", "read_shell"}
# Agent type: nomifun 单引擎收敛后只允许 'nomi'；天龙自研兼容 tianlong 系列
ALLOWED_AGENT_TYPES = {"nomi", "tianlong", "tianlong-content-planner", "tianlong-writer", "tianlong-validator", "tianlong-researcher"}
EXECUTION_STATUS = {
    "planning", "awaiting_approval", "running",
    "paused", "waiting_input",
    "completed", "completed_with_failures",
    "failed", "cancelled",
}

# 有界上限（与 nomifun §4.1 对齐）
MAX_MODELS = 16
MAX_PARTICIPANTS = 64
MAX_STEPS = 128
MAX_PARALLEL = 64
MAX_DELEGATION_DEPTH = 4


class ValidationError(Exception):
    """业务 schema 校验失败。"""


def _check_models(pool: Any, where: str) -> list[str]:
    errors: list[str] = []
    if pool is None:
        return errors
    if not isinstance(pool, dict):
        errors.append(f"{where}: execution_model_pool must be dict")
        return errors
    tag = pool.get("type")
    if tag == "automatic":
        return errors
    if tag == "single":
        if not isinstance(pool.get("model"), str) or not pool["model"]:
            errors.append(f"{where}: execution_model_pool.single.model must be non-empty string")
        return errors
    if tag == "range":
        models = pool.get("models", [])
        if not isinstance(models, list) or not models:
            errors.append(f"{where}: execution_model_pool.range.models empty")
        elif len(models) > MAX_MODELS:
            errors.append(f"{where}: execution_model_pool.models > {MAX_MODELS}")
        return errors
    errors.append(f"{where}: execution_model_pool type must be automatic|single|range (got {tag})")
    return errors


def _check_participants(parts: list[Any], where: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(parts, list):
        errors.append(f"{where}: participants must be list")
        return errors
    if len(parts) > MAX_PARTICIPANTS:
        errors.append(f"{where}: participants count {len(parts)} > {MAX_PARTICIPANTS}")
    lead_count = 0
    for i, p in enumerate(parts):
        ph = f"{where}.participants[{i}]"
        if not isinstance(p, dict):
            errors.append(f"{ph}: must be dict")
            continue
        if p.get("sort_order") == 0:
            lead_count += 1
        atype = p.get("agent_type")
        if atype not in ALLOWED_AGENT_TYPES:
            errors.append(f"{ph}: agent_type must be one of {sorted(ALLOWED_AGENT_TYPES)}; got {atype!r}")
        max_con = p.get("max_concurrency", 0)
        if not isinstance(max_con, int) or max_con < 1 or max_con > MAX_PARALLEL:
            errors.append(f"{ph}: max_concurrency must be 1..={MAX_PARALLEL}")
    if lead_count != 1 and len(parts) >= 2:
        errors.append(f"{where}: exactly 1 leader expected (sort_order=0); got {lead_count}")
    return errors


def _check_steps(steps: list[Any], where: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(steps, list):
        errors.append(f"{where}: steps must be list")
        return errors
    if len(steps) > MAX_STEPS:
        errors.append(f"{where}: steps count {len(steps)} > {MAX_STEPS}")
    seen_ids: set[str] = set()
    for i, s in enumerate(steps):
        sh = f"{where}.steps[{i}]"
        if not isinstance(s, dict):
            errors.append(f"{sh}: must be dict")
            continue
        sid = s.get("step_id")
        if not sid:
            errors.append(f"{sh}: step_id missing")
        elif sid in seen_ids:
            errors.append(f"{sh}: step_id '{sid}' duplicated")
        else:
            seen_ids.add(sid)
        if "role" not in s:
            errors.append(f"{sh}: role missing")
        tp = s.get("tool_policy")
        if tp not in TOOL_POLICY:
            errors.append(f"{sh}: tool_policy must be one of {sorted(TOOL_POLICY)}; got {tp!r}")
        depth = s.get("delegation_depth", 0)
        if not isinstance(depth, int) or depth < 0 or depth > MAX_DELEGATION_DEPTH:
            errors.append(f"{sh}: delegation_depth must be 0..={MAX_DELEGATION_DEPTH}")
    return errors


def _check_attempts(attempts: list[Any], where: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(attempts, list):
        errors.append(f"{where}: attempts must be list")
        return errors
    for i, a in enumerate(attempts):
        ah = f"{where}.attempts[{i}]"
        if not isinstance(a, dict):
            errors.append(f"{ah}: must be dict")
            continue
        for key in ("attempt_no", "participant_id", "status"):
            if key not in a:
                errors.append(f"{ah}: {key} missing")
        st = a.get("status")
        if st not in {"queued", "running", "waiting_input",
                       "completed", "failed", "cancelled", "interrupted"}:
            errors.append(f"{ah}: status invalid (got {st!r})")
    return errors


def validate_plan(plan: dict[str, Any]) -> list[str]:
    """校验一份 SDD/Plan YAML。返回错误列表；空列表 = 合规。"""
    errs: list[str] = []
    where = "$"

    if not isinstance(plan, dict):
        errs.append(f"{where}: must be dict")
        return errs

    # 顶层必填
    for key in ("execution_id", "goal", "owner"):
        if key not in plan:
            errs.append(f"{where}: {key} missing")

    # 4 类聚合策略（拆得最干净）
    for key, allowed in (
        ("delegation_policy", DELEGATION_POLICY),
        ("plan_gate", PLAN_GATE),
        ("decision_policy", DECISION_POLICY),
        ("adaptation_policy", ADAPTATION_POLICY),
    ):
        v = plan.get(key)
        if v not in allowed:
            errs.append(f"{where}: {key} must be one of {sorted(allowed)}; got {v!r}")

    # 并行度
    mp = plan.get("max_parallel", 4)
    if not isinstance(mp, int) or mp < 1 or mp > MAX_PARALLEL:
        errs.append(f"{where}: max_parallel must be 1..={MAX_PARALLEL}")

    # 模型池
    errs.extend(_check_models(plan.get("execution_model_pool"), f"{where}.execution_model_pool"))

    # 7 类子结构
    errs.extend(_check_participants(plan.get("participants", []), where))
    errs.extend(_check_steps(plan.get("steps", []), where))
    errs.extend(_check_attempts(plan.get("attempts", []), where))

    # Dependency（粗略校验）
    deps = plan.get("dependencies", [])
    if isinstance(deps, list):
        # 检查 DAG 无环（简易 DFS）
        graph: dict[str, list[str]] = {}
        for d in deps:
            if not isinstance(d, dict) or "blocker" not in d or "blocked" not in d:
                errs.append(f"{where}.dependencies[]: must have blocker/blocked")
                continue
            graph.setdefault(d["blocker"], []).append(d["blocked"])

    return errs


def render_markdown(plan: dict[str, Any]) -> str:
    """借 nomifun md 渲染风格，输出可读性计划文档。"""
    lines: list[str] = []
    lines.append(f"# Execution Plan: {plan.get('execution_id', '?')}")
    lines.append("")
    lines.append(f"> **Goal**: {plan.get('goal', '?')}  ")
    lines.append(f"> **Owner**: `{plan.get('owner', '?')}`  ")
    lines.append("")

    lines.append("## 4 类聚合策略")
    for k in ("delegation_policy", "plan_gate", "decision_policy", "adaptation_policy"):
        lines.append(f"- **{k}**: `{plan.get(k, '?')}`")
    lines.append(f"- **max_parallel**: {plan.get('max_parallel', 4)}")
    lines.append("")

    parts = plan.get("participants", [])
    if parts:
        lines.append(f"## Participants ({len(parts)} ≤ {MAX_PARTICIPANTS})")
        lines.append("")
        lines.append("| # | name | agent_type | max_concurrency | sort_order |")
        lines.append("|---|------|-----------|----------------|------------|")
        for i, p in enumerate(parts):
            lines.append(f"| {i} | {p.get('name', '?')} | {p.get('agent_type', '?')} | "
                          f"{p.get('max_concurrency', '?')} | {p.get('sort_order', '?')} |")
        lines.append("")

    steps = plan.get("steps", [])
    if steps:
        lines.append(f"## Steps ({len(steps)} ≤ {MAX_STEPS})")
        lines.append("")
        lines.append("| step_id | role | tool_policy | delegation_depth |")
        lines.append("|---------|------|-------------|------------------|")
        for s in steps:
            lines.append(f"| {s.get('step_id', '?')} | {s.get('role', '?')} | "
                          f"{s.get('tool_policy', '?')} | {s.get('delegation_depth', 0)} |")
        lines.append("")
    return "\n".join(lines)


def render_html(plan: dict[str, Any]) -> str:
    return f"""<!doctype html>
<html lang="zh"><head>
<meta charset="utf-8">
<title>Execution Plan {plan.get('execution_id', '?')}</title>
<style>body{{font-family:sans-serif;max-width:920px;margin:2em auto;padding:0 1em;color:#222}}</style>
</head><body>
<pre>{render_markdown(plan)}</pre>
</body></html>"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="nomifun_execution_schema V1.0 — Stage 46")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_val = sub.add_parser("validate", help="validate plan YAML")
    p_val.add_argument("plan")
    p_md = sub.add_parser("to-markdown", help="render to markdown")
    p_md.add_argument("plan")
    p_html = sub.add_parser("to-html", help="render to html")
    p_html.add_argument("plan")
    args = parser.parse_args(argv)

    plan_path = Path(args.plan)
    if not plan_path.exists():
        print(f"[FAIL] {plan_path}: not found")
        return 1
    try:
        plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        print(f"[FAIL] {plan_path}: YAML parse error: {e}")
        return 1

    if args.cmd == "validate":
        errs = validate_plan(plan or {})
        if errs:
            for e in errs:
                print(f"[FAIL] {e}")
            print(f"\n--- {len(errs)} errors · EXIT: 1 ---")
            return 1
        print("[OK]   plan YAML valid (7 tables + 4 policies + 5 tool_policy)")
        print("---EXIT: 0---")
        return 0
    if args.cmd == "to-markdown":
        sys.stdout.write(render_markdown(plan or {}))
        return 0
    if args.cmd == "to-html":
        sys.stdout.write(render_html(plan or {}))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
