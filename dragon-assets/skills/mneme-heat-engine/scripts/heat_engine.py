"""mneme-heat-engine · heat 衰减引擎 v1.0

借鉴自 dsh-mneme v0.7.0 heat 幂律衰减设计（MIT ✅）。
天龙自实现 Python 版，不引入上游依赖。
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timezone

# 算法常量
INIT_HEAT = 0.7
MAX_HEAT = 1.0
MIN_HEAT = 0.05
DECAY_PER_DAY = 0.99        # 幂律衰减系数
BOOST_ON_REF = 1.05         # 被引用加成
ARCHIVE_THRESHOLD = 0.1     # 归档阈值
ARCHIVE_DAYS_THRESHOLD = 30 # 30 天未引用则归档


def tick_heat(heat: float, days_since_ref: int) -> float:
    """每日 tick：未被引用则幂律衰减.

    >>> tick_heat(0.7, 0)
    0.7
    >>> round(tick_heat(0.7, 30), 3)
    0.518
    >>> tick_heat(0.01, 100)
    0.05
    """
    new_heat = heat * (DECAY_PER_DAY ** days_since_ref)
    return max(MIN_HEAT, new_heat)


def boost_heat(heat: float) -> float:
    """被引用时加成.

    >>> boost_heat(0.5)
    0.525
    >>> boost_heat(0.99)
    1.0
    """
    return min(MAX_HEAT, heat * BOOST_ON_REF)


def should_archive(heat: float, last_ref_date: str, today: str) -> bool:
    """判断节点是否应归档.

    >>> should_archive(0.05, "2026-07-01", "2026-08-24")
    True
    >>> should_archive(0.7, "2026-08-20", "2026-08-24")
    False
    """
    last = date.fromisoformat(last_ref_date)
    now = date.fromisoformat(today)
    days = (now - last).days
    return heat < ARCHIVE_THRESHOLD and days > ARCHIVE_DAYS_THRESHOLD


def today_iso() -> str:
    """当前日期 ISO 格式."""
    return datetime.now(timezone.utc).date().isoformat()


def cmd_tick(args: argparse.Namespace) -> int:
    heat = tick_heat(args.heat, args.days_since_ref)
    print(json.dumps({"heat": round(heat, 4), "input_heat": args.heat,
                      "days_since_ref": args.days_since_ref}, ensure_ascii=False))
    return 0


def cmd_boost(args: argparse.Namespace) -> int:
    heat = boost_heat(args.heat)
    print(json.dumps({"heat": round(heat, 4), "input_heat": args.heat},
                     ensure_ascii=False))
    return 0


def cmd_should_archive(args: argparse.Namespace) -> int:
    archive = should_archive(args.heat, args.last_ref_date, args.today)
    print(json.dumps({"should_archive": archive,
                      "heat": args.heat,
                      "last_ref_date": args.last_ref_date,
                      "today": args.today}, ensure_ascii=False))
    return 0 if not archive else 1


def cmd_daily_tick(args: argparse.Namespace) -> int:
    today = today_iso()
    sample = [
        {"id": "node-A", "heat": 0.7, "last_ref_date": "2026-07-25"},
        {"id": "node-B", "heat": 0.3, "last_ref_date": "2026-08-20"},
        {"id": "node-C", "heat": 0.1, "last_ref_date": "2026-06-01"},
    ]
    results = []
    for n in sample:
        last = date.fromisoformat(n["last_ref_date"])
        days = (date.fromisoformat(today) - last).days
        new_heat = tick_heat(n["heat"], days)
        archive = should_archive(new_heat, n["last_ref_date"], today)
        results.append({
            "id": n["id"],
            "input_heat": n["heat"],
            "days_since_ref": days,
            "new_heat": round(new_heat, 4),
            "should_archive": archive,
        })
    print(json.dumps({"today": today, "results": results},
                     ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="mneme-heat-engine v1.0 · MEMORY 节点热衰减引擎",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_tick = sub.add_parser("tick", help="单节点 heat tick")
    p_tick.add_argument("--heat", type=float, required=True)
    p_tick.add_argument("--days-since-ref", type=int, required=True)
    p_tick.set_defaults(func=cmd_tick)

    p_boost = sub.add_parser("boost", help="单节点 boost")
    p_boost.add_argument("--heat", type=float, required=True)
    p_boost.set_defaults(func=cmd_boost)

    p_arch = sub.add_parser("should-archive", help="判断是否归档")
    p_arch.add_argument("--heat", type=float, required=True)
    p_arch.add_argument("--last-ref-date", required=True)
    p_arch.add_argument("--today", required=True)
    p_arch.set_defaults(func=cmd_should_archive)

    p_dt = sub.add_parser("daily-tick", help="全量 daily tick 演示")
    p_dt.add_argument("--workspace", default=".")
    p_dt.set_defaults(func=cmd_daily_tick)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())