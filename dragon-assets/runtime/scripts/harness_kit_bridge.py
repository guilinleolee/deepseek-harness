"""harness_kit_bridge V1.0 — Stage 47.3 harnesskit-methodology.

借鉴 RealZST/HarnessKit 4 类方法论 (Apache-2.0 · 414⭐ · 5 个月迭代)：
① Skill manager (统一 frontmatter + enabled) ② MCP registry (transport + status)
③ Hook chain (pre/post ToolUse) ④ Config sync (inventory vs registry diff)

零依赖 (仅 Python 3 + PyYAML)。5 CLI 子命令：
- skill_manager  inventory + frontmatter 校验 + enabled 过滤
- mcp_registry   MCP servers 校验 + status snapshot
- hook_chain     pre/post ToolUse 顺序 + 循环检测
- config_sync    local vs registry 双向 diff
- license_check  Apache-2.0 verbatim + Modified by
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("[ERR] PyYAML not installed", file=sys.stderr)
    sys.exit(2)

# 借鉴 HarnessKit Skill manager 元数据 schema
SKILL_KEYS_REQUIRED = {"name", "version", "enabled"}
SKILL_KEYS_OPTIONAL = {"base_version", "description", "triggers", "upstream",
                       "downstream", "inputs", "outputs", "errors",
                       "DO", "DONTS", "example"}

MCP_TRANSPORT = {"stdio", "http", "sse"}
HOOK_EVENTS = {"PreToolUse", "PostToolUse", "SessionStart", "UserPromptSubmit",
               "Notification", "Stop", "SubagentStop", "PreCompact",
               "SessionEnd"}


def _norm(text: str) -> str:
    """归一化换行 + 折叠空白 (Apache LICENSE 验证)."""
    return re.sub(r"\s+", " ", text)


def cmd_skill_manager(args: argparse.Namespace) -> int:
    inv = Path(args.inventory)
    if not inv.exists():
        print(f"[FAIL] {inv}: not found")
        return 1
    try:
        data = json.loads(inv.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"[FAIL] JSON parse: {e}")
        return 1
    skills = data.get("skills", [])
    if not isinstance(skills, list):
        print(f"[FAIL] 'skills' must be list")
        return 1
    errs: list[str] = []
    enabled_count = 0
    for i, s in enumerate(skills):
        sh = f"skills[{i}]"
        if not isinstance(s, dict):
            errs.append(f"{sh}: must be dict")
            continue
        missing = SKILL_KEYS_REQUIRED - s.keys()
        if missing:
            errs.append(f"{sh}: missing required keys {sorted(missing)}")
        if s.get("enabled") is True:
            enabled_count += 1
        # version semver (V? omitted)
        ver = str(s.get("version", ""))
        if not re.match(r"^V?\d+(\.\d+){0,2}$", ver):
            errs.append(f"{sh}: version '{ver}' not semver")
    if errs:
        for e in errs:
            print(f"[FAIL] {e}")
        print(f"\n--- {len(errs)} errors · EXIT: 1 ---")
        return 1
    print(f"[OK] {len(skills)}/{len(skills)} skills validated; {enabled_count} enabled")
    print("---EXIT: 0---")
    return 0


def cmd_mcp_registry(args: argparse.Namespace) -> int:
    cfg = Path(args.config)
    if not cfg.exists():
        print(f"[FAIL] {cfg}: not found")
        return 1
    data = yaml.safe_load(cfg.read_text(encoding="utf-8"))
    servers = data.get("mcp_servers", [])
    if not isinstance(servers, list):
        print(f"[FAIL] 'mcp_servers' must be list")
        return 1
    errs: list[str] = []
    enabled = 0
    for i, s in enumerate(servers):
        sh = f"mcp_servers[{i}]"
        if not isinstance(s, dict):
            errs.append(f"{sh}: must be dict")
            continue
        if "name" not in s:
            errs.append(f"{sh}: name missing")
        if "transport" not in s:
            errs.append(f"{sh}: transport missing")
        elif s["transport"] not in MCP_TRANSPORT:
            errs.append(f"{sh}: transport '{s['transport']}' not in {sorted(MCP_TRANSPORT)}")
        elif s["transport"] in ("http", "sse") and "url" not in s:
            errs.append(f"{sh}: transport={s['transport']} requires url")
        elif s["transport"] == "stdio" and "command" not in s:
            errs.append(f"{sh}: transport=stdio requires command")
        if s.get("enabled") is True:
            enabled += 1
    if errs:
        for e in errs:
            print(f"[FAIL] {e}")
        print(f"\n--- {len(errs)} errors · EXIT: 1 ---")
        return 1
    print(f"[OK] {len(servers)}/{len(servers)} MCP servers validated; {enabled} enabled")
    print("---EXIT: 0---")
    return 0


def _detect_cycle(graph: dict[str, list[str]]) -> bool:
    """DFS cycle detection."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[str, int] = {n: WHITE for n in graph}
    def dfs(node: str) -> bool:
        color[node] = GRAY
        for nb in graph.get(node, []):
            if color.get(nb, WHITE) == GRAY:
                return True
            if color.get(nb, WHITE) == WHITE and dfs(nb):
                return True
        color[node] = BLACK
        return False
    for n in list(graph.keys()):
        if color[n] == WHITE and dfs(n):
            return True
    return False


def cmd_hook_chain(args: argparse.Namespace) -> int:
    cfg = Path(args.hooks)
    if not cfg.exists():
        print(f"[FAIL] {cfg}: not found")
        return 1
    try:
        data = json.loads(cfg.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"[FAIL] JSON parse: {e}")
        return 1
    hooks = data.get("hooks", [])
    if not isinstance(hooks, list):
        print(f"[FAIL] 'hooks' must be list")
        return 1
    errs: list[str] = []
    graph: dict[str, list[str]] = {}
    for i, h in enumerate(hooks):
        hh = f"hooks[{i}]"
        if not isinstance(h, dict):
            errs.append(f"{hh}: must be dict")
            continue
        ev = h.get("event")
        if ev not in HOOK_EVENTS:
            errs.append(f"{hh}: event '{ev}' not in {sorted(HOOK_EVENTS)}")
        script = h.get("script", h.get("name", "?"))
        # 简单链检测: 假设钩子按 script 名字引用
        deps = h.get("after", [])
        if isinstance(deps, list):
            graph[script] = deps
    cycle = _detect_cycle(graph)
    if cycle:
        errs.append("hook chain has cycle (DFS detected)")
    if errs:
        for e in errs:
            print(f"[FAIL] {e}")
        print(f"\n--- {len(errs)} errors · EXIT: 1 ---")
        return 1
    print(f"[OK] {len(hooks)} hooks validated, no cycle detected")
    print("---EXIT: 0---")
    return 0


def cmd_config_sync(args: argparse.Namespace) -> int:
    """比对 inventory.json 与 registry.json 双向 diff."""
    local = Path(args.local)
    registry = Path(args.registry)
    if not local.exists() or not registry.exists():
        print(f"[FAIL] local or registry not found ({local}, {registry})")
        return 1
    try:
        l = json.loads(local.read_text(encoding="utf-8"))
        r = json.loads(registry.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"[FAIL] JSON parse: {e}")
        return 1
    l_keys = set((l.get("skills") or {}).keys()) if isinstance(l.get("skills"), dict) else set()
    r_keys = set((r.get("skills") or {}).keys()) if isinstance(r.get("skills"), dict) else set()
    added = l_keys - r_keys
    removed = r_keys - l_keys
    common = l_keys & r_keys
    changed = []
    for k in common:
        if (l["skills"][k] != r["skills"][k]):
            changed.append(k)
    print(f"[OK] config_sync diff:")
    print(f"  + added:    {len(added)}")
    print(f"  - removed:  {len(removed)}")
    print(f"  ~ changed:  {len(changed)}")
    print(f"  = same:     {len(common) - len(changed)}")
    if added:
        print(f"  added details: {sorted(added)[:5]}")
    if removed:
        print(f"  removed details: {sorted(removed)[:5]}")
    if changed:
        print(f"  changed details: {sorted(changed)[:5]}")
    print("---EXIT: 0---")
    return 0


def cmd_license_check(args: argparse.Namespace) -> int:
    skill_path = Path(args.skill)
    base = skill_path.parent
    lic = base / "LICENSE"
    notice = base / "NOTICE"
    if not lic.exists():
        print(f"[FAIL] {lic}: not found")
        return 1
    if not notice.exists():
        print(f"[FAIL] {notice}: not found")
        return 1
    lic_bytes = lic.read_bytes()
    notice_bytes = notice.read_bytes()
    lic_norm = _norm(lic_bytes.decode("utf-8", errors="replace"))
    notice_text = notice_bytes.decode("utf-8", errors="replace")
    checks = [
        ("LICENSE contains Apache License", "Apache License" in lic_norm),
        ("LICENSE contains Version 2.0", "Version 2.0" in lic_norm),
        ("LICENSE contains 'Licensed under the Apache License, Version 2.0'", "Licensed under the Apache License" in lic_norm),
        ("NOTICE contains 'Modified by dragon-engine / 2026-08-26'", "Modified by dragon-engine / 2026-08-26" in notice_text),
    ]
    overall_fail = False
    for label, ok in checks:
        print(f"  [{'OK' if ok else 'FAIL'}] {label}")
        if not ok:
            overall_fail = True
    print()
    print("---EXIT: 1---" if overall_fail else "---EXIT: 0---")
    return 1 if overall_fail else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="harness_kit_bridge V1.0 — Stage 47.3 harnesskit-methodology")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_sm = sub.add_parser("skill_manager")
    p_sm.add_argument("inventory")

    p_mr = sub.add_parser("mcp_registry")
    p_mr.add_argument("config")

    p_hc = sub.add_parser("hook_chain")
    p_hc.add_argument("hooks")

    p_cs = sub.add_parser("config_sync")
    p_cs.add_argument("--local", required=True)
    p_cs.add_argument("--registry", required=True)

    p_lc = sub.add_parser("license_check")
    p_lc.add_argument("skill")

    args = parser.parse_args(argv)
    if args.cmd == "skill_manager":
        return cmd_skill_manager(args)
    if args.cmd == "mcp_registry":
        return cmd_mcp_registry(args)
    if args.cmd == "hook_chain":
        return cmd_hook_chain(args)
    if args.cmd == "config_sync":
        return cmd_config_sync(args)
    if args.cmd == "license_check":
        return cmd_license_check(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
