#!/usr/bin/env python3
"""
Wiki AI味检测仪表盘
实时可视化 Wiki 知识质量状态

Usage:
    python3 dashboard.py
    python3 dashboard.py --compact
    python3 dashboard.py --watch
    python3 dashboard.py --history
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
from dataclasses import dataclass

WIKI_DIR = Path.home() / ".claude" / "wiki"
HISTORY_FILE = Path.home() / ".claude" / "wiki_quality_history.json"


@dataclass
class QualityStats:
    total_notes: int
    grade_distribution: dict
    avg_score: float
    avg_ai_probability: float
    health_score: float
    trend: str
    top_flags: list
    top_suggestions: list


def load_history() -> list:
    """加载历史记录"""
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except:
            pass
    return []


def save_history(history: list):
    """保存历史记录"""
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(
        json.dumps(history, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def load_latest_scan() -> Optional[list]:
    """加载最新的扫描结果"""
    from .detector import AITasteDetector

    detector = AITasteDetector()
    return detector.scan_all()


def calculate_stats(results: list) -> QualityStats:
    """计算统计数据"""
    if not results:
        return QualityStats(
            total_notes=0,
            grade_distribution={"A": 0, "B": 0, "C": 0, "D": 0},
            avg_score=0,
            avg_ai_probability=0,
            health_score=100,
            trend="stable",
            top_flags=[],
            top_suggestions=[]
        )

    grades = {"A": 0, "B": 0, "C": 0, "D": 0}
    total_score = 0
    total_ai_prob = 0
    all_flags = []
    all_suggestions = []

    for r in results:
        grades[r.grade] = grades.get(r.grade, 0) + 1
        total_score += r.score
        total_ai_prob += r.ai_probability
        all_flags.extend(r.flags)
        all_suggestions.extend(r.suggestions)

    # 统计高频标记和建议
    flag_counts = {}
    for f in all_flags:
        flag_counts[f] = flag_counts.get(f, 0) + 1
    top_flags = sorted(flag_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    suggestion_counts = {}
    for s in all_suggestions:
        suggestion_counts[s] = suggestion_counts.get(s, 0) + 1
    top_suggestions = sorted(suggestion_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    # 计算健康度
    health_score = 100
    if grades["D"] > len(results) * 0.5:
        health_score -= 30
    elif grades["C"] > len(results) * 0.5:
        health_score -= 15
    if grades["D"] > 0:
        health_score -= grades["D"] * 5

    # 计算趋势
    history = load_history()
    trend = "stable"
    if len(history) >= 2:
        prev_avg = history[-2].get("avg_score", 0)
        curr_avg = total_score / len(results)
        if curr_avg > prev_avg + 0.5:
            trend = "improving"
        elif curr_avg < prev_avg - 0.5:
            trend = "declining"

    return QualityStats(
        total_notes=len(results),
        grade_distribution=grades,
        avg_score=total_score / len(results),
        avg_ai_probability=total_ai_prob / len(results),
        health_score=health_score,
        trend=trend,
        top_flags=top_flags,
        top_suggestions=top_suggestions
    )


def save_snapshot(stats: QualityStats):
    """保存统计快照"""
    history = load_history()
    snapshot = {
        "timestamp": datetime.now().isoformat(),
        "total_notes": stats.total_notes,
        "grade_distribution": stats.grade_distribution,
        "avg_score": stats.avg_score,
        "avg_ai_probability": stats.avg_ai_probability,
        "health_score": stats.health_score
    }
    history.append(snapshot)
    # 保留最近100条记录
    history = history[-100:]
    save_history(history)


def get_trend_emoji(trend: str) -> str:
    """获取趋势图标"""
    return {"improving": "📈", "declining": "📉", "stable": "➡️"}.get(trend, "➡️")


def get_health_color(score: float) -> str:
    """获取健康度颜色"""
    if score >= 80:
        return "🟢"
    elif score >= 60:
        return "🟡"
    elif score >= 40:
        return "🟠"
    else:
        return "🔴"


def render_dashboard(stats: QualityStats) -> str:
    """渲染仪表盘"""
    trend_emoji = get_trend_emoji(stats.trend)
    health_emoji = get_health_color(stats.health_score)
    grades = stats.grade_distribution

    width = 60

    lines = [
        f" ╔{'═' * (width - 2)}╗",
        f" ║{' Wiki AI味检测仪表盘 '.center(width - 2)}║",
        f" ╠{'═' * (width - 2)}╣",
        f" ║{'【整体健康度】'.center(width - 2)}║",
        f" ║  {health_emoji} 健康度: {stats.health_score:>5.1f}%  {trend_emoji} 趋势: {stats.trend:<10}  ║",
        f" ╠{'═' * (width - 2)}╣",
        f" ║{'【质量统计】'.center(width - 2)}║",
        f" ║  笔记总数: {stats.total_notes:>6}  平均评分: {stats.avg_score:>5.1f}/14  ║",
        f" ║  平均AI概率: {stats.avg_ai_probability:>5.1f}%  ║",
        f" ╠{'═' * (width - 2)}╣",
        f" ║{'【等级分布】'.center(width - 2)}║",
    ]

    # 等级分布条形图
    max_count = max(grades.values()) if grades.values() else 1
    grade_icons = {"A": "🟢", "B": "🟡", "C": "🟠", "D": "🔴"}
    grade_names = {"A": "A级(人类)", "B": "B级(少量)", "C": "C级(较重)", "D": "D级(AI)"}

    for grade in ["A", "B", "C", "D"]:
        count = grades.get(grade, 0)
        bar_len = int((count / max_count) * 20) if max_count > 0 else 0
        bar = "█" * bar_len
        icon = grade_icons.get(grade, "⚪")
        lines.append(f" ║  {icon} {grade_names[grade]:<12} {count:>4} {bar:<20}  ║")

    lines.append(f" ╠{'═' * (width - 2)}╣")

    # 高频问题
    if stats.top_flags:
        lines.append(f" ║{'【高频问题】'.center(width - 2)}║")
        for flag, count in stats.top_flags[:3]:
            lines.append(f" ║  ⚠️  {flag[:width - 10]}{' ' * max(0, width - 12 - len(flag))}  ║")

    lines.append(f" ╚{'═' * (width - 2)}╝")

    return "\n".join(lines)


def render_compact(stats: QualityStats) -> str:
    """紧凑格式"""
    grades = stats.grade_distribution
    health = stats.health_score
    trend = get_trend_emoji(stats.trend)
    return (
        f"健康:{health:.0f}% {trend} | "
        f"笔记:{stats.total_notes} | "
        f"评分:{stats.avg_score:.1f}/14 | "
        f"AI概率:{stats.avg_ai_probability:.0f}% | "
        f"A:{grades['A']} B:{grades['B']} C:{grades['C']} D:{grades['D']}"
    )


def render_json(stats: QualityStats) -> str:
    """JSON格式"""
    return json.dumps({
        "total_notes": stats.total_notes,
        "grade_distribution": stats.grade_distribution,
        "avg_score": stats.avg_score,
        "avg_ai_probability": stats.avg_ai_probability,
        "health_score": stats.health_score,
        "trend": stats.trend,
        "top_flags": [{"flag": f, "count": c} for f, c in stats.top_flags],
        "top_suggestions": [{"suggestion": s, "count": c} for s, c in stats.top_suggestions]
    }, ensure_ascii=False, indent=2)


def render_history() -> str:
    """渲染历史趋势"""
    history = load_history()

    if not history:
        return "暂无历史记录"

    lines = [
        " ╔═══════════════════════════════════════════════════════╗",
        " ║           Wiki 知识质量历史趋势                  ║",
        " ╠═══════════════════════════════════════════════════════╣",
    ]

    # 最近10条记录
    recent = history[-10:]
    for entry in recent:
        ts = entry.get("timestamp", "")[:16]
        score = entry.get("avg_score", 0)
        health = entry.get("health_score", 0)
        notes = entry.get("total_notes", 0)
        grades = entry.get("grade_distribution", {})
        d_count = grades.get("D", 0)
        lines.append(
            f" ║ {ts} | 评分:{score:.1f} | 健康:{health:.0f}% | "
            f"D级:{d_count} | 笔记:{notes} ║"
        )

    lines.append(" ╚═══════════════════════════════════════════════════════╝")
    return "\n".join(lines)


def watch_mode():
    """监听模式"""
    import time
    print("开始监听 Wiki 知识质量状态 (Ctrl+C 退出)...")

    last_output = None
    while True:
        try:
            results = load_latest_scan()
            stats = calculate_stats(results)
            output = render_compact(stats)

            if output != last_output:
                print(f"\r{datetime.now().strftime('%H:%M:%S')} | {output}", end="")
                last_output = output
                save_snapshot(stats)

            time.sleep(10)
        except KeyboardInterrupt:
            print("\n退出监听模式")
            break
        except Exception as e:
            print(f"\n错误: {e}")
            time.sleep(10)


def main():
    parser = argparse.ArgumentParser(description="Wiki AI味检测仪表盘")
    parser.add_argument("--compact", action="store_true", help="紧凑输出")
    parser.add_argument("--watch", action="store_true", help="监听模式")
    parser.add_argument("--json", action="store_true", help="JSON格式输出")
    parser.add_argument("--history", action="store_true", help="显示历史趋势")
    parser.add_argument("--save", action="store_true", help="保存当前快照")
    args = parser.parse_args()

    if args.watch:
        watch_mode()
        return

    results = load_latest_scan()
    stats = calculate_stats(results)

    if args.history:
        print(render_history())
        return

    if args.json:
        print(render_json(stats))
    elif args.compact:
        print(render_compact(stats))
    else:
        print(render_dashboard(stats))

    if args.save or (not args.history and not args.json and not args.compact):
        save_snapshot(stats)


if __name__ == "__main__":
    main()
