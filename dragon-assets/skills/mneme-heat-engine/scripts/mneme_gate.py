"""mneme-heat-engine · mneme-gate v1.0 (W2 · 09-06 skills-administrator 协同)

借鉴自 dsh-mneme v0.7.0 自进化记忆设计（MIT ✅）。
天龙自实现 Python 版：给主仓 skill catalog 加 heat 治理。
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

from heat_engine import INIT_HEAT, MAX_HEAT, MIN_HEAT, tick_heat, boost_heat


def skill_register(skill_id: str, today: str | None = None) -> dict:
    """skill 入 catalog 时初始化 heat."""
    if today is None:
        today = datetime.now(timezone.utc).date().isoformat()
    return {
        "skill_id": skill_id,
        "heat": INIT_HEAT,
        "last_used_date": today,
        "trigger_count": 0,
        "status": "active",
    }


def skill_tick_daily(skills: list[dict], today: str | None = None) -> list[dict]:
    """每日 cron tick 所有 skill heat（未触发则衰减）."""
    if today is None:
        today = datetime.now(timezone.utc).date().isoformat()
    results = []
    for s in skills:
        last_used = s.get("last_used_date", today)
        days = (date.fromisoformat(today) - date.fromisoformat(last_used)).days
        new_heat = tick_heat(s["heat"], days)
        new_status = "active" if new_heat >= 0.1 else "cold"
        if days > 60:
            new_status = "candidate_retire"
        elif days > 30:
            new_status = "cold"
        results.append({
            "skill_id": s["skill_id"],
            "input_heat": s["heat"],
            "days_since_used": days,
            "new_heat": round(new_heat, 4),
            "status": new_status,
        })
    return results


def skill_used(skill: dict, today: str | None = None) -> dict:
    """skill 被触发使用 -> boost_heat + 更新 last_used_date."""
    if today is None:
        today = datetime.now(timezone.utc).date().isoformat()
    skill["heat"] = boost_heat(skill["heat"])
    skill["last_used_date"] = today
    skill["trigger_count"] = skill.get("trigger_count", 0) + 1
    skill["status"] = "active"
    return skill


def cmd_demo(args: argparse.Namespace) -> int:
    today = "2026-08-24"
    # Step 1: 3 个 skill 入库（初始化 heat）
    catalog = [
        skill_register("mneme-heat-engine"),
        skill_register("darwin-skill"),
        skill_register("obsolete-skill"),
    ]
    print(f"[STEP 1] registered {len(catalog)} skills")

    # Step 2: 模拟 30 天未使用 obsolete-skill
    catalog[2]["last_used_date"] = "2026-06-01"

    # Step 3: 每日 tick
    ticks = skill_tick_daily(catalog, today)
    print(f"[STEP 3] daily tick -> {len(ticks)} results")

    # Step 4: 模拟 darwin-skill 被使用 1 次（boost）
    catalog[1] = skill_used(catalog[1], today)
    print(f"[STEP 4] darwin-skill boosted -> heat={round(catalog[1]['heat'], 4)}")

    print(json.dumps({
        "step1_registered": [s["skill_id"] for s in catalog],
        "step3_daily_tick": ticks,
        "step4_darwin_after_boost": {
            "heat": round(catalog[1]["heat"], 4),
            "trigger_count": catalog[1]["trigger_count"],
        },
    }, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="mneme-heat-engine · mneme-gate v1.0 (skills catalog heat)",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_demo = sub.add_parser("demo", help="演示 mneme-gate 端到端")
    p_demo.set_defaults(func=cmd_demo)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())