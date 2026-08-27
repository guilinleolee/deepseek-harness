"""
dsh-tui-bridge V1.0 · 借鉴 dsh-TUI 4 类核心设计 · 自研 Python CLI

================================================================================
  Stage 47 · 2026-08-24

设计：
  - 借鉴档模式（stage 41 mneme / stage 45 dsh-eval / stage 46 dsh-peak-gate 同）
  - 5 重 blocker：巨型 15 MB / 子模块 vendor / DSH 主仓 / TUI runtime / 30+ verify
  - 4 CLI：state-snapshot / parse-channel / render-cordis-patch / auto-save-sim
  - pytest 14+ unittest PASS
  - 退出码契约：0=OK / 1=PARSE_ERR / 2=PATCH_ERR / 3=STATE_ERR
================================================================================
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import yaml
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

EXIT_OK = 0
EXIT_PARSE = 1
EXIT_PATCH = 2
EXIT_STATE = 3


# ==============================================================================
# 1. TUI 状态机 dataclass（6 字段）
# ==============================================================================

@dataclass
class TUIStateSnapshot:
    """dsh-TUI 状态快照"""
    state_id: str
    current_scene: str           # main/settings/tree/resume
    input_buffer: str = ""
    thinking_buffer: str = ""
    working_status: str = "idle"  # idle/thinking/tool-calling/awaiting-approval
    context_progress: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def parse_state_snapshot(raw: str) -> TUIStateSnapshot:
    """解析 DSH TUI 状态 JSON 为 dataclass"""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"invalid JSON: {e}") from e

    for field in ["state_id", "current_scene"]:
        if field not in data:
            raise ValueError(f"missing required field: {field}")

    return TUIStateSnapshot(
        state_id=data["state_id"],
        current_scene=data["current_scene"],
        input_buffer=data.get("input_buffer", ""),
        thinking_buffer=data.get("thinking_buffer", ""),
        working_status=data.get("working_status", "idle"),
        context_progress=float(data.get("context_progress", 0.0)),
    )


# ==============================================================================
# 2. DSH TUI Channel Protocol（6 类消息 parser）
# ==============================================================================

CHANNEL_TYPES = {
    "user_input",          # { content, seq }
    "assistant_thought",   # { delta, done }
    "tool_call",           # { tool, args }
    "tool_result",         # { tool, status, output }
    "working_activity",    # { type, msg }
    "approval_request",    # { tool, args, deadline }
}


@dataclass
class ChannelMessage:
    type: str
    payload: Dict[str, Any]
    seq: Optional[int] = None
    timestamp: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


def parse_channel_message(raw: str) -> ChannelMessage:
    """解析 dsh-ecosystem-spec tui-channel 消息"""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"invalid JSON: {e}") from e

    if "type" not in data:
        raise ValueError("missing 'type' field")

    msg_type = data["type"]
    if msg_type not in CHANNEL_TYPES:
        raise ValueError(f"unknown channel type: {msg_type} (allowed: {CHANNEL_TYPES})")

    payload = {k: v for k, v in data.items() if k != "type"}

    # 字段类型校验
    if msg_type == "user_input" and "content" not in payload:
        raise ValueError("user_input requires 'content'")
    if msg_type == "assistant_thought" and "delta" not in payload:
        raise ValueError("assistant_thought requires 'delta'")
    if msg_type == "tool_call" and "tool" not in payload:
        raise ValueError("tool_call requires 'tool'")

    return ChannelMessage(
        type=msg_type,
        payload=payload,
        seq=data.get("seq"),
        timestamp=data.get("timestamp", ""),
    )


# ==============================================================================
# 3. cordis patch 生成（template）
# ==============================================================================

def generate_cordis_patch(
    *,
    plugin_id: str = "dsh-tui-bridge",
    plugin_name: str = "dsh-tui-bridge",
    upstream: str = "@deepseek-harness-tui/dsh-tui",
    bridge: str = "dsh_tui_bridge.py",
    version: str = "0.9.2 → bridge V1.0",
) -> Dict[str, Any]:
    """生成 cordis patch yaml dict"""
    return {
        "patch": [
            {
                "insert": [
                    {
                        "id": plugin_id,
                        "name": plugin_name,
                        "config": {
                            "upstream": upstream,
                            "bridge": bridge,
                            "version": version,
                            "borrowed": True,
                            "integration_stage": 47,
                        },
                    }
                ]
            }
        ]
    }


# ==============================================================================
# 4. Settings auto-save simulator（借鉴 commit #575 设计）
# ==============================================================================

def settings_autosave_simulator(
    initial_state: Dict[str, Any],
    modifications: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """串行写入 + 末次胜出（借鉴 dsh-TUI commit #575）

    Args:
        initial_state: 起始 dict
        modifications: 修改列表（按序应用，后写的覆盖先写的）
    Returns:
        最终 state dict
    """
    state = dict(initial_state)
    for change in modifications:
        if isinstance(change, dict):
            state.update(change)
    return state


# ==============================================================================
# CLI
# ==============================================================================

def cmd_state_snapshot(args: argparse.Namespace) -> int:
    """解析 TUI 状态 JSON"""
    try:
        snap = parse_state_snapshot(args.input)
    except ValueError as e:
        print(f"[parse error] {e}", file=sys.stderr)
        return EXIT_STATE
    print(json.dumps(snap.to_dict(), indent=2, ensure_ascii=False))
    return EXIT_OK


def cmd_parse_channel(args: argparse.Namespace) -> int:
    """解析 channel 消息"""
    try:
        msg = parse_channel_message(args.input)
    except ValueError as e:
        print(f"[parse error] {e}", file=sys.stderr)
        return EXIT_PARSE
    print(json.dumps(msg.to_dict(), indent=2, ensure_ascii=False))
    return EXIT_OK


def cmd_render_cordis_patch(args: argparse.Namespace) -> int:
    """生成 cordis patch yaml"""
    patch = generate_cordis_patch(
        plugin_id=args.plugin_id,
        plugin_name=args.plugin_name,
        upstream=args.upstream,
        bridge=args.bridge,
        version=args.version,
    )
    yml = yaml.dump(patch, allow_unicode=True, sort_keys=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(yml)
        print(f"[ok] patch written to {args.output}", file=sys.stderr)
    else:
        print(yml, end="")
    return EXIT_OK


def cmd_auto_save_sim(args: argparse.Namespace) -> int:
    """settings auto-save simulator"""
    if args.modifications:
        modifications = json.loads(args.modifications)
    else:
        modifications = []
    initial = json.loads(args.initial) if args.initial else {}
    final = settings_autosave_simulator(initial, modifications)
    print(json.dumps(final, indent=2, ensure_ascii=False))
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="dsh_tui_bridge",
        description="Stage 47 dsh-tui-bridge V1.0 · 借鉴档 4 类核心设计 · 自研",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("state-snapshot", help="解析 TUI 状态 JSON")
    sp.add_argument("--input", required=True, help="TUI state JSON")
    sp.set_defaults(func=cmd_state_snapshot)

    sp = sub.add_parser("parse-channel", help="解析 channel 消息")
    sp.add_argument("--input", required=True, help="channel message JSON")
    sp.set_defaults(func=cmd_parse_channel)

    sp = sub.add_parser("render-cordis-patch", help="生成 cordis patch yaml")
    sp.add_argument("--plugin-id", default="dsh-tui-bridge")
    sp.add_argument("--plugin-name", default="dsh-tui-bridge")
    sp.add_argument("--upstream", default="@deepseek-harness-tui/dsh-tui")
    sp.add_argument("--bridge", default="dsh_tui_bridge.py")
    sp.add_argument("--version", default="0.9.2 → bridge V1.0")
    sp.add_argument("--output", help="输出文件")
    sp.set_defaults(func=cmd_render_cordis_patch)

    sp = sub.add_parser("auto-save-sim", help="settings auto-save simulator")
    sp.add_argument("--initial", help="初始 state JSON")
    sp.add_argument("--modifications", help="修改列表 JSON")
    sp.set_defaults(func=cmd_auto_save_sim)

    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
