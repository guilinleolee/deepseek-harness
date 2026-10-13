"""mneme-heat-engine · interest-drift V2.0.0 (阶段 42 候选)

借鉴 dsh-mneme v0.8.0 设计意图（MIT ✅ · 计划 9 月末发版 · 我们按设计文档先实现）。
天龙自实现 Python 版（零依赖）。

兴趣漂移定义：
  - 在 N 个时间窗内，对每个实体（entities 表）计算 heat 加权分布
  - 比较相邻时间窗的 KL 散度（分布差异）
  - 散度 > 阈值 → 标记为"兴趣漂移"
  - 配合 32-01 market-researcher V10.1 决策下游（自动识别关注点转移）

时间窗默认 7 天（每周一快照）。
漂移阈值默认 0.3（KL 散度 0-1+ 范围）。
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from heat_engine import INIT_HEAT, tick_heat


def snapshot_entities(
    entities: list[dict],
    today: str | None = None,
) -> dict[str, float]:
    """生成当前 entities heat 快照（按 type 维度）."""
    if today is None:
        today = datetime.now(timezone.utc).date().isoformat()

    # 按 type 分组聚合 heat
    type_heat: dict[str, float] = defaultdict(float)
    for e in entities:
        e_type = e.get("type", "unknown")
        type_heat[e_type] += e.get("heat", INIT_HEAT)
    return dict(type_heat)


def kl_divergence(p: dict[str, float], q: dict[str, float]) -> float:
    """KL 散度 D(P||Q) · 衡量两个分布的差异.

    公式：D(P||Q) = Σ P(x) * log(P(x) / Q(x))

    返回 0 表示分布一致，越大差异越大。
    """
    eps = 1e-10  # 避免 log(0)
    all_keys = set(p) | set(q)
    p_total = sum(p.values()) + eps * len(p)
    q_total = sum(q.values()) + eps * len(q)
    d = 0.0
    for k in all_keys:
        p_val = (p.get(k, 0) + eps) / p_total
        q_val = (q.get(k, 0) + eps) / q_total
        d += p_val * math.log(p_val / q_val)
    return d


def detect_drift(
    snapshots: list[dict[str, float]],
    threshold: float = 0.3,
) -> list[dict]:
    """从一系列时间快照中检测漂移点."""
    if len(snapshots) < 2:
        return []

    drifts = []
    for i in range(1, len(snapshots)):
        prev = snapshots[i - 1]
        curr = snapshots[i]
        d = kl_divergence(curr, prev)
        drifted = d >= threshold
        # 找出最大增量 / 最大减量 type
        all_keys = set(prev) | set(curr)
        delta = {k: curr.get(k, 0) - prev.get(k, 0) for k in all_keys}
        max_gain = max(delta.items(), key=lambda x: x[1], default=(None, 0))
        max_loss = min(delta.items(), key=lambda x: x[1], default=(None, 0))

        drifts.append({
            "index": i,
            "kl_divergence": round(d, 4),
            "threshold": threshold,
            "drifted": drifted,
            "max_gain_type": max_gain[0],
            "max_gain_value": round(max_gain[1], 4),
            "max_loss_type": max_loss[0],
            "max_loss_value": round(max_loss[1], 4),
        })
    return drifts


def project_future_heat(
    entities: list[dict],
    days: int,
) -> list[dict]:
    """投影 N 天后所有 entity 的 heat（按 tick_heat 衰减）."""
    projected = []
    for e in entities:
        new_heat = tick_heat(e.get("heat", INIT_HEAT), days)
        projected.append({
            "id": e["id"],
            "type": e.get("type", "unknown"),
            "current_heat": e.get("heat", INIT_HEAT),
            "projected_heat": round(new_heat, 4),
            "heat_change": round(new_heat - e.get("heat", INIT_HEAT), 4),
        })
    return projected


def generate_drift_report(
    entities: list[dict],
    snapshots: list[dict[str, float]],
    days_projection: int = 30,
    threshold: float = 0.3,
) -> dict:
    """生成完整兴趣漂移报告（含快照 + 漂移点 + 投影）."""
    drifts = detect_drift(snapshots, threshold=threshold)
    projection = project_future_heat(entities, days=days_projection)
    current_snapshot = snapshot_entities(entities)

    # 排序：未来 heat 最高的 entity（即将"热门"）
    hot_future = sorted(projection, key=lambda x: x["projected_heat"], reverse=True)[:5]
    # 排序：当前 heat 最高（现在"热门"）
    hot_now = sorted(entities, key=lambda x: x.get("heat", 0), reverse=True)[:5]

    return {
        "report_date": datetime.now(timezone.utc).date().isoformat(),
        "current_snapshot": current_snapshot,
        "drift_analysis": drifts,
        "drift_detected": any(d["drifted"] for d in drifts),
        "days_projection": days_projection,
        "hot_now": [{"id": e["id"], "heat": e.get("heat", 0)} for e in hot_now],
        "hot_future": hot_future,
        "summary": _summarize(current_snapshot, drifts, hot_now, hot_future),
    }


def _summarize(
    current: dict[str, float],
    drifts: list[dict],
    hot_now: list[dict],
    hot_future: list[dict],
) -> str:
    """生成人类可读摘要."""
    top_type = max(current.items(), key=lambda x: x[1], default=("unknown", 0))
    drifted = sum(1 for d in drifts if d["drifted"])
    lines = [
        f"当前最热 type: {top_type[0]} (聚合 heat={round(top_type[1], 2)})",
        f"漂移点: {drifted}/{len(drifts)} 个时间窗检测到漂移",
        f"现在热门: {', '.join(e['id'] for e in hot_now[:3])}",
        f"未来热门: {', '.join(e['id'] for e in hot_future[:3])}",
    ]
    return " | ".join(lines)


def cmd_demo(args: argparse.Namespace) -> int:
    """V2.0 兴趣漂移端到端演示."""
    today = "2026-08-24"

    # 构造一个"兴趣迁移"的场景：老李从 AI 关注转向财经
    entities_initial = [
        {"id": "ai-openai", "type": "ai-product", "heat": 0.9},
        {"id": "ai-claude", "type": "ai-product", "heat": 0.85},
        {"id": "ai-gpt5", "type": "ai-product", "heat": 0.7},
        {"id": "stock-moutai", "type": "stock-cn", "heat": 0.3},
        {"id": "stock-pingan", "type": "stock-cn", "heat": 0.25},
    ]
    snapshot_w1 = snapshot_entities(entities_initial, today)

    # 7 天后：AI 关注度衰减，财经升温
    entities_w2 = [
        {"id": "ai-openai", "type": "ai-product", "heat": tick_heat(0.9, 7)},
        {"id": "ai-claude", "type": "ai-product", "heat": tick_heat(0.85, 7)},
        {"id": "ai-gpt5", "type": "ai-product", "heat": tick_heat(0.7, 7)},
        {"id": "stock-moutai", "type": "stock-cn", "heat": 0.8},  # 升温
        {"id": "stock-pingan", "type": "stock-cn", "heat": 0.75},
        {"id": "new-stock-tx", "type": "stock-cn", "heat": 0.65},  # 新增
    ]
    snapshot_w2 = snapshot_entities(entities_w2, today)

    # 生成报告
    report = generate_drift_report(
        entities=entities_w2,
        snapshots=[snapshot_w1, snapshot_w2],
        days_projection=30,
        threshold=0.3,
    )

    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"\nSUMMARY: {report['summary']}")
    print(f"DRIFT DETECTED: {report['drift_detected']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="mneme-heat-engine · interest-drift V2.0 (借鉴 dsh-mneme v0.8.0)",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_demo = sub.add_parser("demo", help="演示兴趣漂移检测端到端")
    p_demo.set_defaults(func=cmd_demo)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())