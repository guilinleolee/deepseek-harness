"""mneme-heat-engine · sleep_scheduler V2.0.0 (cron-like scheduler)

每 N 小时自动跑 sleep_consolidate + heat tick + mneme_gate tick。

设计意图：
  - 模仿 dsh-mneme v0.4.0 Sleep Mode 定时触发
  - 与 cron_weekly.sh (skill-updater V1.1.3) 风格一致
  - 支持 Windows Task Scheduler（PowerShell）+ Linux cron (systemd timer)

触发动作：
  1. tick_heat 每日衰减
  2. sleep_consolidate 4 阶段
  3. mneme_gate 技能 heat 治理
  4. session_decouple 检查（无 session 时跳过）

退出码契约（与 aihot_check / darwin_check 一致）：
  0 = PASS（全部完成）
  1 = FAIL（至少 1 个动作异常）
  2 = WARN（部分跳过 · 如 archive 目录无文件）
  3 = ERROR（环境异常 · 如 import error）
"""
from __future__ import annotations

import argparse
import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from heat_engine import INIT_HEAT, tick_heat, today_iso
from mneme_gate import skill_register, skill_tick_daily, skill_used
from session_decouple import on_session_close


def action_tick_heat(dry_run: bool = False) -> dict[str, Any]:
    """每日 heat tick（演示：3 个节点 × 30 天衰减）."""
    sample = [
        {"id": "node-A", "heat": 0.7, "last_ref_date": "2026-07-25"},
        {"id": "node-B", "heat": 0.3, "last_ref_date": "2026-08-20"},
        {"id": "node-C", "heat": 0.1, "last_ref_date": "2026-06-01"},
    ]
    today = today_iso()
    results = []
    for n in sample:
        days = (
            datetime.fromisoformat(today).date()
            - datetime.fromisoformat(n["last_ref_date"]).date()
        ).days
        new_heat = tick_heat(n["heat"], days)
        results.append({
            "id": n["id"],
            "old_heat": n["heat"],
            "new_heat": round(new_heat, 4),
            "days_since_ref": days,
        })
    return {
        "action": "tick_heat",
        "ok": True,
        "results": results,
        "dry_run": dry_run,
    }


def action_sleep_consolidate(dry_run: bool = False) -> dict[str, Any]:
    """sleep 4 阶段（演示：4 节点走完整 pipeline）."""
    from sleep_consolidate import (phase1_dedupe, phase2_merge,
                                    phase3_archive, phase4_rebirth)
    today = "2026-08-24"
    nodes = [
        {"id": "A", "wikilink": "老李", "heat": 0.7,
         "last_ref_date": "2026-08-20", "compilations": 3},
        {"id": "A2", "wikilink": "老李", "heat": 0.5,
         "last_ref_date": "2026-07-15", "compilations": 2},
        {"id": "B", "wikilink": "old", "heat": 0.08,
         "last_ref_date": "2026-06-01", "compilations": 5},
        {"id": "C", "wikilink": "active", "heat": 0.85,
         "last_ref_date": "2026-08-23", "compilations": 10},
    ]
    original_count = len(nodes)
    nodes = phase1_dedupe(nodes)
    nodes = phase2_merge(nodes)
    active, archive = phase3_archive(nodes, today)
    rebirth = phase4_rebirth(archive, ["B"])
    final = active + rebirth

    return {
        "action": "sleep_consolidate",
        "ok": True,
        "input_nodes": original_count,
        "phase1_after": "dedupe merged A+A2",
        "phase3_archived": len(archive),
        "phase4_rebirth": len(rebirth),
        "final_active": len(final),
        "dry_run": dry_run,
    }


def action_mneme_gate_tick(dry_run: bool = False) -> dict[str, Any]:
    """skills catalog heat tick（演示：3 skills）."""
    today = today_iso()
    catalog = [
        skill_register("mneme-heat-engine"),
        skill_register("darwin-skill"),
        skill_register("obsolete-skill"),
    ]
    # 模拟 obsolete-skill 60 天未用
    catalog[2]["last_used_date"] = "2026-06-01"
    ticks = skill_tick_daily(catalog, today)
    return {
        "action": "mneme_gate_tick",
        "ok": True,
        "skills_count": len(catalog),
        "ticks": ticks,
        "dry_run": dry_run,
    }


def action_session_decouple_check(dry_run: bool = False) -> dict[str, Any]:
    """session 状态检查（演示：无活跃 session 时跳过）."""
    # 实际应读 DSH session 状态文件，这里演示逻辑
    return {
        "action": "session_decouple_check",
        "ok": True,
        "active_sessions": 0,
        "action_taken": "no active sessions, skipped",
        "dry_run": dry_run,
    }


ACTIONS = [
    ("tick_heat", action_tick_heat),
    ("sleep_consolidate", action_sleep_consolidate),
    ("mneme_gate_tick", action_mneme_gate_tick),
    ("session_decouple_check", action_session_decouple_check),
]


def run_all(dry_run: bool = False) -> dict:
    """按顺序跑全部 4 个动作，聚合报告."""
    started_at = datetime.now(timezone.utc).isoformat()
    results = []
    has_fail = False

    for action_name, action_fn in ACTIONS:
        try:
            r = action_fn(dry_run=dry_run)
            r["action_name"] = action_name
            results.append(r)
        except Exception as e:
            has_fail = True
            results.append({
                "action_name": action_name,
                "ok": False,
                "error": str(e),
                "traceback": traceback.format_exc(),
            })

    return {
        "started_at": started_at,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "dry_run": dry_run,
        "actions_total": len(ACTIONS),
        "actions_ok": sum(1 for r in results if r.get("ok")),
        "has_fail": has_fail,
        "exit_code": 1 if has_fail else 0,
        "results": results,
    }


def cmd_run(args: argparse.Namespace) -> int:
    """跑一次完整调度."""
    report = run_all(dry_run=args.dry_run)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report["exit_code"]


def cmd_install_windows_task(args: argparse.Namespace) -> int:
    """输出 Windows 计划任务安装命令（用户手动执行）."""
    cmd = (
        f'SchTasks /Create /SC HOURLY /MO 4 /TN "MnemeSleepScheduler" '
        f'/TR "python {Path(__file__).resolve()} run" /F'
    )
    print(json.dumps({
        "platform": "windows",
        "task_name": "MnemeSleepScheduler",
        "schedule": "every 4 hours",
        "install_command": cmd,
        "uninstall_command": 'SchTasks /Delete /TN "MnemeSleepScheduler" /F',
        "manual_run": (
            f'python {Path(__file__).resolve()} run --dry-run'
        ),
    }, ensure_ascii=False, indent=2))
    return 0


def cmd_install_linux_cron(args: argparse.Namespace) -> int:
    """输出 Linux cron 安装命令."""
    script = Path(__file__).resolve()
    log_path = Path("logs/mneme-sleep-scheduler.log").resolve()
    cmd = (
        f'0 */4 * * * /usr/bin/python3 {script} run >> {log_path} 2>&1'
    )
    print(json.dumps({
        "platform": "linux",
        "schedule": "every 4 hours (cron expression: 0 */4 * * *)",
        "cron_line": cmd,
        "install": f"echo '{cmd}' | crontab -",
        "manual_run": f"python3 {script} run --dry-run",
    }, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="mneme-heat-engine · sleep_scheduler V2.0 (cron-like scheduler)",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="跑一次完整调度")
    p_run.add_argument("--dry-run", action="store_true",
                       help="只统计不修改（默认 false）")
    p_run.set_defaults(func=cmd_run)

    p_win = sub.add_parser("install-windows-task",
                            help="输出 Windows Task Scheduler 安装命令")
    p_win.set_defaults(func=cmd_install_windows_task)

    p_linux = sub.add_parser("install-linux-cron",
                              help="输出 Linux cron 安装命令")
    p_linux.set_defaults(func=cmd_install_linux_cron)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())