"""
dsh-desktop-bridge V1.0 · Stage 49.1 借鉴档 · anywhere-labs/dsh-desktop MIT 借鉴

================================================================================
  Stage 49.1 · 2026-08-26

设计：
  - 借鉴档模式（与 stage 45 dsh-eval / 46 dsh-peak-gate / 48 dsh-TUI 同）
  - 3 重 blocker：双 submodule (.agents / .yarn) + Yarn Berry 工具链 + 中文社区无 CI 测试
  - 不实跑上游 yarn install（避免与 DSH Desktop 真实冲突）
  - 自研 5 类借鉴：DSH 桌面架构 / 插件契约 / 命令面板 / 多 workspace / agent 协同
  - pytest 5+ unittest PASS
  - 退出码契约：0=OK / 1=PARSE_ERR / 2=CONFIG_ERR / 3=CMD_ERR
================================================================================
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

EXIT_OK = 0
EXIT_PARSE = 1
EXIT_CONFIG = 2
EXIT_CMD = 3


# ==============================================================================
# 1. DSH 桌面架构（5 层 · 借鉴上游 AGENTS.md + .agents/.yarn 目录）
# ==============================================================================

@dataclass
class DSHDesktopState:
    """DSH 桌面状态"""
    active_workspace: str = "default"
    active_plugin: str = ""
    panel_layout: str = "single-column"  # single-column / dual-pane / fullscreen
    theme: str = "auto"                  # auto / light / dark
    language: str = "zh-CN"
    recent_workspaces: List[str] = field(default_factory=list)


# ==============================================================================
# 2. DSH 插件契约（6 字段 · 借鉴上游 .agents/ 目录结构）
# ==============================================================================

REQUIRED_PLUGIN_KEYS = ["id", "name", "version", "entry", "manifest"]

@dataclass
class DSHPluginManifest:
    """DSH 插件 manifest 借鉴档（不实跑，仅设计参考）"""
    id: str
    name: str
    version: str
    entry: str
    manifest: str = "dsh.plugin/v1"
    borrowed: bool = True
    borrowed_from: Optional[str] = None


def parse_manifest(yaml_text: str) -> DSHPluginManifest:
    """极简 YAML manifest 解析（仅 6 字段）"""
    # 提取 5 个字段
    result = {}
    for key in REQUIRED_PLUGIN_KEYS:
        m = re.search(rf'^\s*{key}:\s*(.+?)\s*$', yaml_text, re.MULTILINE)
        if not m:
            raise ValueError(f"missing required key: {key}")
        result[key] = m.group(1).strip().strip('"\'')

    return DSHPluginManifest(**result)


# ==============================================================================
# 3. 命令面板（5 指令 · 借鉴 DSH Composer Dock）
# ==============================================================================

COMPOSER_COMMANDS = {
    "/workspace": "list or switch workspace",
    "/plugin":    "manage plugins (list/install/disable)",
    "/memory":    "memory operations (capture/recall/forget)",
    "/debug":     "trajectory debug integration",
    "/peakgate":  "stage 46 peak/off-peak gate",
}


def list_composer_commands() -> List[Dict[str, str]]:
    return [{"cmd": k, "desc": v} for k, v in COMPOSER_COMMANDS.items()]


def parse_composer_command(raw: str) -> Dict[str, Any]:
    """解析 /command [args]"""
    raw = raw.strip()
    if not raw.startswith("/"):
        return {"ok": False, "error": "must start with /"}
    parts = raw.split(maxsplit=1)
    cmd = parts[0]
    args = parts[1] if len(parts) > 1 else ""
    if cmd not in COMPOSER_COMMANDS:
        return {"ok": False, "error": f"unknown command: {cmd}"}
    return {"ok": True, "cmd": cmd, "args": args}


# ==============================================================================
# 4. 多 workspace 路由（借鉴 stage 48 dsh-TUI settings.autosave）
# ==============================================================================

@dataclass
class Workspace:
    id: str
    name: str
    path: str
    is_default: bool = False


def route_workspace(target: str, workspaces: List[Workspace]) -> Workspace:
    """用户指定 workspace → 路由到 Workspace"""
    for ws in workspaces:
        if ws.id == target or ws.name == target:
            return ws
    raise KeyError(f"workspace not found: {target}")


# ==============================================================================
# 5. agent 协同（agent_teams 协议借鉴）
# ==============================================================================

@dataclass
class AgentTask:
    """轻量级 agent task（借鉴 dsh-agent-teams V0.1.13）"""
    id: str
    description: str
    status: str = "queued"     # queued / running / done / failed
    assignee: str = "captain"  # captain 或 member id
    created_at: str = ""


def dispatch_task(task: AgentTask, team_members: List[str]) -> Dict[str, Any]:
    """把 task 派给指定 assignee；如 assignee = 'captain' 则 round-robin 给第一个 member"""
    if task.assignee == "captain" and team_members:
        task.assignee = team_members[0]
    return {"task_id": task.id, "assignee": task.assignee, "status": "dispatched"}


# ==============================================================================
# CLI
# ==============================================================================

def cmd_parse_manifest(args: argparse.Namespace) -> int:
    """解析 DSH 插件 manifest YAML"""
    try:
        manifest = parse_manifest(args.yaml)
    except ValueError as e:
        print(f"[parse error] {e}", file=sys.stderr)
        return EXIT_PARSE
    print(json.dumps(asdict(manifest), indent=2, ensure_ascii=False))
    return EXIT_OK


def cmd_list_commands(args: argparse.Namespace) -> int:
    """列出所有 composer dock 命令"""
    for item in list_composer_commands():
        print(f"  {item['cmd']:<14} {item['desc']}")
    return EXIT_OK


def cmd_parse_command(args: argparse.Namespace) -> int:
    """解析 composer dock 命令"""
    result = parse_composer_command(args.cmd_raw)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return EXIT_OK if result.get("ok") else EXIT_CMD


def cmd_dispatch(args: argparse.Namespace) -> int:
    """派发 agent task（demo）"""
    members = args.members.split(",") if args.members else []
    task = AgentTask(
        id=args.task_id, description=args.description, assignee=args.assignee,
    )
    result = dispatch_task(task, members)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="dsh_desktop_bridge",
        description="Stage 49.1 dsh-desktop-bridge V1.0 · anywhere-labs/dsh-desktop MIT 借鉴档",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("parse-manifest", help="解析 DSH 插件 manifest YAML")
    sp.add_argument("--yaml", required=True, help="plugin manifest yaml")
    sp.set_defaults(func=cmd_parse_manifest)

    sp = sub.add_parser("list-commands", help="列出 composer dock 命令")
    sp.set_defaults(func=cmd_list_commands)

    sp = sub.add_parser("parse-command", help="解析 composer dock 命令")
    sp.add_argument("cmd_raw", help="原命令（如 /workspace default）")
    sp.set_defaults(func=cmd_parse_command)

    sp = sub.add_parser("dispatch", help="派发 agent task")
    sp.add_argument("--task-id", required=True)
    sp.add_argument("--description", required=True)
    sp.add_argument("--assignee", default="captain")
    sp.add_argument("--members", default="", help="comma-separated team members")
    sp.set_defaults(func=cmd_dispatch)

    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
