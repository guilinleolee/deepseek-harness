"""
dsh-peak-gate-bridge V1.0 · 借鉴 dsh-peak-gate 5 类核心设计 · 自研 Python CLI

================================================================================
  Stage 46 · 2026-08-24

设计：
  - 借鉴档模式（与 stage 45 dsh-eval-bridge 同）
  - 不镜像真源（DSH Desktop 路径依赖 blocker）
  - 4 CLI 子命令：is-peak / generate-config / hold / parse-cmd
  - 借鉴 5 类：peak window 数学 / 队列数据结构 / 拦截逻辑 / localStorage schema / 指令表
  - pytest 5+ unittest PASS
  - 退出码契约：0=OK / 1=PEAK_MATH_FAIL / 2=CONFIG_ERR / 3=PARSE_ERR
================================================================================
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

EXIT_OK = 0
EXIT_PEAK_MATH = 1
EXIT_CONFIG = 2
EXIT_PARSE = 3


# ==============================================================================
# 1. peak window 数学（与 stage 45.1 dsh_balance_bridge 完全一致）
# ==============================================================================

def is_peak_hour(beijing_dt: Optional[datetime] = None) -> bool:
    """Beijing 09:00-12:00 / 14:00-18:00 为 peak"""
    dt = beijing_dt or datetime.now(timezone(timedelta(hours=8)))
    h = dt.hour
    return (9 <= h < 12) or (14 <= h < 18)


def is_off_peak_weekend(beijing_dt: Optional[datetime] = None) -> bool:
    """周六周日全天 off-peak（2026-08-23 起官方政策）"""
    dt = beijing_dt or datetime.now(timezone(timedelta(hours=8)))
    return dt.weekday() in (5, 6)  # Saturday=5, Sunday=6


def get_current_band(beijing_dt: Optional[datetime] = None) -> str:
    """当前 Beijing 时间段：peak / off-peak"""
    dt = beijing_dt or datetime.now(timezone(timedelta(hours=8)))
    if is_off_peak_weekend(dt):
        return "off-peak"
    return "peak" if is_peak_hour(dt) else "off-peak"


def next_off_peak_dt(beijing_dt: Optional[datetime] = None) -> datetime:
    """下次 off-peak 开始时间"""
    dt = beijing_dt or datetime.now(timezone(timedelta(hours=8)))
    if is_off_peak_weekend(dt):
        # 周六/周日：现在是 off-peak，next off-peak = 现在
        return dt

    # 工作日
    h = dt.hour
    if h < 9:
        # 早于 9:00，今天 9:00 前是 off-peak → 现在就是 off-peak
        return dt
    elif 12 <= h < 14:
        # 12-14 午休 → 现在 off-peak
        return dt
    elif h >= 18:
        # 18:00 后到次日 9:00 → 下次 off-peak = 现在
        return dt
    elif 9 <= h < 12:
        # 上午 peak → next off-peak = 今天 12:00
        return dt.replace(hour=12, minute=0, second=0, microsecond=0)
    elif 14 <= h < 18:
        # 下午 peak → next off-peak = 今天 18:00
        return dt.replace(hour=18, minute=0, second=0, microsecond=0)
    return dt


# ==============================================================================
# 2. 队列数据结构（FIFO with priority + status）
# ==============================================================================

@dataclass
class PeakGateHold:
    """队列单条 hold"""
    id: str
    source_session: str
    content: str
    held_at: str
    auto_send_at: str
    status: str = "queued"   # 'queued' | 'sent' | 'muted' | 'cancelled'
    tag: str = "peak-card"   # 'peak-card' | '/peakgate-hold'
    priority: int = 0


@dataclass
class PeakGateQueue:
    """整个队列"""
    holds: List[PeakGateHold] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {"holds": [asdict(h) for h in self.holds]}

    def add(self, h: PeakGateHold) -> None:
        self.holds.append(h)

    def remove(self, seq: int) -> Optional[PeakGateHold]:
        if 0 <= seq < len(self.holds):
            return self.holds.pop(seq)
        return None


# ==============================================================================
# 3. localStorage schema 生成
# ==============================================================================

def generate_localstorage_schema(
    *,
    enabled: bool = True,
    timezone: str = "Asia/Shanghai",
    off_peak_weekends: bool = True,
    peak_windows: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    """3 keys: settings / muted / holds"""
    if peak_windows is None:
        peak_windows = [
            {"start": "09:00", "end": "12:00"},
            {"start": "14:00", "end": "18:00"},
        ]
    return {
        "dsh.peakGate.settings.v1": {
            "enabled": enabled,
            "timezone": timezone,
            "peakWindows": peak_windows,
            "offPeakWeekends": off_peak_weekends,
        },
        "dsh.peakGate.muted.v1": {},
        "dsh.peakGate.holds.v1": [],
    }


# ==============================================================================
# 4. /peakgate 指令表 parser（5 子命令）
# ==============================================================================

PEAKGATE_CMDS = ["hold", "list", "remove", "cancel", ""]   # 空字符串 = 帮助


@dataclass
class PeakGateCommand:
    """解析后的 /peakgate 指令"""
    cmd: str                    # hold/list/remove/cancel
    args: List[str] = field(default_factory=list)
    text: str = ""              # hold 的消息内容

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def parse_peakgate_command(raw: str) -> PeakGateCommand:
    """解析 /peakgate <cmd> [args]
    容错：空字符串、空白、未知 cmd → cmd='help'
    """
    raw = raw.strip()
    # 去掉前缀 /peakgate
    m = re.match(r"^/?peakgate\s*(.*)$", raw)
    if not m:
        return PeakGateCommand(cmd="help")

    rest = m.group(1).strip()
    if not rest:
        return PeakGateCommand(cmd="help")

    parts = rest.split(maxsplit=1)
    head = parts[0]
    if head not in {"hold", "list", "remove", "cancel"}:
        return PeakGateCommand(cmd="help", args=[rest])

    cmd = head
    tail = parts[1] if len(parts) > 1 else ""

    if cmd == "hold":
        return PeakGateCommand(cmd="hold", text=tail)
    elif cmd == "remove":
        seq_str = tail.strip()
        if not seq_str.isdigit():
            return PeakGateCommand(cmd="help", args=[f"remove requires integer, got '{seq_str}'"])
        return PeakGateCommand(cmd="remove", args=[int(seq_str)])
    elif cmd == "list":
        return PeakGateCommand(cmd="list")
    elif cmd == "cancel":
        return PeakGateCommand(cmd="cancel")
    return PeakGateCommand(cmd="help")


# ==============================================================================
# CLI
# ==============================================================================

def cmd_is_peak(args: argparse.Namespace) -> int:
    """当前 Beijing 时间 peak/off-peak"""
    band = get_current_band()
    next_off = next_off_peak_dt()
    result = {
        "beijing_now": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "band": band,
        "is_peak_now": is_peak_hour(),
        "next_off_peak_at": next_off.isoformat(),
        "is_off_peak_weekend": is_off_peak_weekend(),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return EXIT_OK


def cmd_generate_config(args: argparse.Namespace) -> int:
    """生成 3-key localStorage schema"""
    schema = generate_localstorage_schema(
        enabled=args.enabled,
        timezone=args.timezone,
        off_peak_weekends=args.off_peak_weekends,
    )
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)
        print(f"[ok] schema written to {args.output}", file=sys.stderr)
    else:
        print(json.dumps(schema, indent=2, ensure_ascii=False))
    return EXIT_OK


def cmd_hold(args: argparse.Namespace) -> int:
    """入队单条 hold"""
    next_off = next_off_peak_dt()
    auto_send = args.auto_send_at or next_off.isoformat()
    h = PeakGateHold(
        id=f"hold-{datetime.now().timestamp():.0f}",
        source_session=args.session,
        content=args.content,
        held_at=datetime.now(timezone(timedelta(hours=8))).isoformat(),
        auto_send_at=auto_send,
        status="queued",
        tag="/peakgate-hold",
    )
    print(json.dumps(asdict(h), indent=2, ensure_ascii=False))
    return EXIT_OK


def cmd_parse_cmd(args: argparse.Namespace) -> int:
    """解析 /peakgate 指令"""
    try:
        result = parse_peakgate_command(args.cmd_raw)
    except ValueError as e:
        print(f"[parse error] {e}", file=sys.stderr)
        return EXIT_PARSE
    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="dsh_peak_gate_bridge",
        description="Stage 46 dsh-peak-gate-bridge V1.0 · 借鉴档 5 类核心设计 · 自研",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("is-peak", help="当前 Beijing 时间 peak/off-peak")
    sp.set_defaults(func=cmd_is_peak)

    sp = sub.add_parser("generate-config", help="生成 3-key localStorage schema")
    sp.add_argument("--enabled", type=lambda x: x.lower() in ('true', '1', 'yes'), default=True)
    sp.add_argument("--timezone", default="Asia/Shanghai")
    sp.add_argument("--off-peak-weekends", type=lambda x: x.lower() in ('true', '1', 'yes'), default=True)
    sp.add_argument("--output", help="输出文件路径（默认 stdout）")
    sp.set_defaults(func=cmd_generate_config)

    sp = sub.add_parser("hold", help="入队单条 hold")
    sp.add_argument("--session", required=True, help="源会话 ID")
    sp.add_argument("--content", required=True, help="消息内容")
    sp.add_argument("--auto-send-at", help="auto-send 时间（默认 = next off-peak）")
    sp.set_defaults(func=cmd_hold)

    sp = sub.add_parser("parse-cmd", help="解析 /peakgate 指令")
    sp.add_argument("cmd_raw", help="原始指令文本（含或不含 /peakgate 前缀）")
    sp.set_defaults(func=cmd_parse_cmd)

    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
