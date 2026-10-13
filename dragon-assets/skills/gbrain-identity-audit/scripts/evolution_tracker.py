#!/usr/bin/env python3
"""
演进追踪器 - Evolution Tracker
追踪天龙引擎Agent的身份配置变更历史、能力成长轨迹和风险预警
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent))


def load_history(agent_id: str) -> list[dict[str, Any]]:
    """加载Agent演进历史"""
    history_dir = Path(__file__).parent.parent / "evolution-history"
    history_file = history_dir / f"{agent_id}.json"

    if not history_file.exists():
        return []

    try:
        with open(history_file, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_history(agent_id: str, history: list[dict[str, Any]]):
    """保存演进历史"""
    history_dir = Path(__file__).parent.parent / "evolution-history"
    history_dir.mkdir(parents=True, exist_ok=True)
    history_file = history_dir / f"{agent_id}.json"

    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def load_current_identity(agent_id: str) -> dict[str, Any] | None:
    """加载当前身份配置"""
    config_dir = Path(__file__).parent.parent / "identity-configs"
    config_file = config_dir / f"{agent_id}.yaml"

    if not config_file.exists():
        return None

    try:
        import yaml
        with open(config_file, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception:
        return None


def generate_snapshot(agent_id: str, notes: str = "") -> dict[str, Any]:
    """生成当前身份配置的快照"""
    config = load_current_identity(agent_id)

    snapshot = {
        "timestamp": datetime.now().isoformat(),
        "agent_id": agent_id,
        "version": config.get("identity", {}).get("version", "unknown") if config else "unknown",
        "notes": notes,
        "changes": {},
    }

    if config:
        identity = config.get("identity", {})
        snapshot["changes"] = {
            "primary_role": identity.get("role", {}).get("primary", ""),
            "secondary_count": len(identity.get("role", {}).get("secondary", [])),
            "keywords_count": len(identity.get("role", {}).get("keywords", [])),
            "can_do_count": len(identity.get("capabilities", {}).get("can_do", [])),
            "cannot_do_count": len(identity.get("capabilities", {}).get("cannot_do", [])),
            "upstream_count": len(identity.get("collaboration", {}).get("upstream", [])),
            "downstream_count": len(identity.get("collaboration", {}).get("downstream", [])),
        }

    return snapshot


def compare_snapshots(snap_a: dict[str, Any], snap_b: dict[str, Any]) -> dict[str, Any]:
    """比较两个快照，识别变更"""
    changes = {}
    fields = ["primary_role", "secondary_count", "keywords_count",
               "can_do_count", "cannot_do_count", "upstream_count", "downstream_count"]

    for field in fields:
        val_a = snap_a.get("changes", {}).get(field, 0)
        val_b = snap_b.get("changes", {}).get(field, 0)

        if val_a != val_b:
            changes[field] = {
                "before": val_a,
                "after": val_b,
                "delta": val_b - val_a,
            }

    return changes


def analyze_growth_trajectory(history: list[dict[str, Any]]) -> dict[str, Any]:
    """分析能力成长轨迹"""
    if len(history) < 2:
        return {
            "trajectory": "insufficient_data",
            "message": "历史数据不足，需要至少2个快照才能分析成长轨迹",
        }

    # 按时间排序
    sorted_history = sorted(history, key=lambda x: x["timestamp"])

    # 计算各维度变化
    capability_trend = []
    for snap in sorted_history:
        cap_count = snap.get("changes", {}).get("can_do_count", 0)
        capability_trend.append(cap_count)

    # 判断趋势
    if len(capability_trend) >= 3:
        first_half = sum(capability_trend[:len(capability_trend)//2]) / (len(capability_trend)//2)
        second_half = sum(capability_trend[len(capability_trend)//2:]) / (len(capability_trend) - len(capability_trend)//2)

        if second_half > first_half * 1.1:
            trend = "growing"
        elif second_half < first_half * 0.9:
            trend = "shrinking"
        else:
            trend = "stable"
    else:
        trend = "insufficient_data"

    return {
        "trajectory": trend,
        "capability_trend": capability_trend,
        "latest_count": capability_trend[-1] if capability_trend else 0,
        "first_count": capability_trend[0] if capability_trend else 0,
        "growth_rate": f"{((capability_trend[-1] - capability_trend[0]) / max(capability_trend[0], 1) * 100):.1f}%"
        if capability_trend and capability_trend[0] > 0 else "0%",
    }


def detect_risk_warnings(history: list[dict[str, Any]], current: dict[str, Any]) -> list[dict[str, Any]]:
    """检测风险预警"""
    warnings = []

    if not current:
        warnings.append({
            "type": "missing_config",
            "severity": "high",
            "message": "Agent缺少身份配置",
            "recommendation": "立即为此Agent生成身份配置",
        })
        return warnings

    identity = current.get("identity", {})
    capabilities = identity.get("capabilities", {})

    # 检查能力边界是否完整
    can_do = capabilities.get("can_do", [])
    cannot_do = capabilities.get("cannot_do", [])

    if not can_do:
        warnings.append({
            "type": "missing_boundaries",
            "severity": "high",
            "message": "Agent缺少 can_do 定义",
            "recommendation": "明确此Agent能够执行的能力范围",
        })

    if not cannot_do:
        warnings.append({
            "type": "missing_boundaries",
            "severity": "medium",
            "message": "Agent缺少 cannot_do 定义",
            "recommendation": "定义此Agent不能执行的能力边界",
        })

    # 检查协作接口
    collaboration = identity.get("collaboration", {})
    upstream = collaboration.get("upstream", [])
    downstream = collaboration.get("downstream", [])

    if not upstream and not downstream:
        warnings.append({
            "type": "missing_interfaces",
            "severity": "medium",
            "message": "Agent缺少协作接口定义",
            "recommendation": "定义上下游协作关系",
        })

    # 检查历史变更
    if history:
        sorted_history = sorted(history, key=lambda x: x["timestamp"])
        latest = sorted_history[-1]

        # 检查版本是否更新
        current_version = identity.get("version", "unknown")
        history_version = latest.get("version", "unknown")

        if current_version != history_version:
            days_since_update = (
                datetime.now() - datetime.fromisoformat(latest["timestamp"])
            ).days

            if days_since_update > 30:
                warnings.append({
                    "type": "stale_identity",
                    "severity": "low",
                    "message": f"身份配置已 {days_since_update} 天未更新",
                    "recommendation": "进行例行身份审计，更新配置",
                })

    return warnings


def track_evolution(
    agent_id: str,
    notes: str = "",
    format: str = "markdown",
) -> str:
    """追踪Agent的演进"""
    # 加载历史
    history = load_history(agent_id)

    # 生成新快照
    new_snapshot = generate_snapshot(agent_id, notes)

    # 保存历史
    if history:
        last_snapshot = history[-1]
        changes = compare_snapshots(last_snapshot, new_snapshot)

        if changes:
            new_snapshot["diff"] = changes
            print(f"📊 检测到变更: {list(changes.keys())}")

    history.append(new_snapshot)
    save_history(agent_id, history)

    # 分析成长轨迹
    trajectory = analyze_growth_trajectory(history)

    # 检测风险预警
    current = load_current_identity(agent_id)
    warnings = detect_risk_warnings(history, current)

    if format == "json":
        return json.dumps({
            "agent_id": agent_id,
            "snapshot": new_snapshot,
            "trajectory": trajectory,
            "warnings": warnings,
            "history_count": len(history),
        }, ensure_ascii=False, indent=2)

    # 生成文本报告
    lines = []
    lines.append(f"# {agent_id} 演进追踪报告\n")
    lines.append(f"**快照时间**: {new_snapshot['timestamp']}\n")
    lines.append(f"**版本**: {new_snapshot['version']}\n")

    if notes:
        lines.append(f"**备注**: {notes}\n")

    lines.append("\n## 当前状态\n")
    for key, value in new_snapshot.get("changes", {}).items():
        lines.append(f"- **{key}**: {value}")
    lines.append("")

    lines.append("\n## 成长轨迹\n")
    if trajectory["trajectory"] == "growing":
        lines.append("📈 **能力正在增长**\n")
    elif trajectory["trajectory"] == "shrinking":
        lines.append("📉 **能力正在缩减**\n")
    else:
        lines.append("➡️ **能力保持稳定**\n")
    lines.append(f"- 首次记录能力数: {trajectory.get('first_count', 0)}")
    lines.append(f"- 当前能力数: {trajectory.get('latest_count', 0)}")
    lines.append(f"- 增长率: {trajectory.get('growth_rate', '0%')}")
    lines.append("")

    if warnings:
        lines.append("\n## ⚠️ 风险预警\n")
        for w in warnings:
            severity_icon = "🔴" if w["severity"] == "high" else "🟡"
            lines.append(f"{severity_icon} **[{w['type']}]** {w['message']}")
            lines.append(f"   建议: {w['recommendation']}\n")
    else:
        lines.append("\n## ✅ 风险状态\n")
        lines.append("未检测到显著风险\n")

    lines.append("\n## 历史记录\n")
    lines.append(f"共 {len(history)} 条记录\n")
    for i, snap in enumerate(history[-5:], 1):
        lines.append(f"{i}. {snap['timestamp'][:10]} - v{snap['version']}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="天龙引擎演进追踪器")
    parser.add_argument("--agent", "-a", required=True, help="指定Agent ID")
    parser.add_argument("--notes", "-n", default="", help="变更备注")
    parser.add_argument("--format", "-f", choices=["markdown", "json"], default="markdown", help="输出格式")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--show-history", action="store_true", help="显示历史记录")

    args = parser.parse_args()

    if args.show_history:
        history = load_history(args.agent)
        print(f"📜 {args.agent} 演进历史 ({len(history)} 条记录)\n")
        for i, snap in enumerate(history, 1):
            print(f"{i}. {snap['timestamp'][:19]} - v{snap['version']}")
            if snap.get("notes"):
                print(f"   备注: {snap['notes']}")
        return 0

    print(f"🔄 追踪 {args.agent} 的演进...")
    report = track_evolution(args.agent, args.notes, args.format)

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"✅ 演进追踪报告已保存到 {args.output}")
    else:
        print(report)

    return 0


if __name__ == "__main__":
    sys.exit(main())
