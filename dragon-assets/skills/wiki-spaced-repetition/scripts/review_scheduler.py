#!/usr/bin/env python3
"""
Wiki 间隔重复复习调度器
基于 spaced_repetition.py 提供高级复习调度功能

Usage:
    python3 review_scheduler.py --today
    python3 review_scheduler.py --queue
    python3 review_scheduler.py --schedule
"""

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from spaced_repetition import SpacedRepetition


def format_priority_score(note) -> str:
    today = date.today()
    try:
        days_until = (date.fromisoformat(note.next_review) - today).days if note.next_review else 0
    except (ValueError, TypeError):
        days_until = 0

    if days_until < 0:
        return f"🔴 逾期 {abs(days_until)} 天"
    elif days_until == 0:
        return "🟡 今天到期"
    elif days_until == 1:
        return "🟢 明天到期"
    else:
        return f"⏳ {days_until} 天后"


def cmd_today(sr: SpacedRepetition):
    """显示今日复习任务"""
    due = sr.get_due_reviews()
    stats = sr.get_stats()

    print("=" * 60)
    print(" 📅 今日复习调度")
    print("=" * 60)
    print(f"\n📊 概览:")
    print(f"   待复习笔记: {len(due)} 条")
    print(f"   总笔记数:  {stats['total_notes']}")
    print(f"   连续天数:  {stats['avg_streak']:.1f} 天")
    print(f"   平均质量:  {stats['avg_quality']:.2f}")

    if not due:
        print("\n🎉 太棒了！今日没有待复习笔记。")
        return

    print(f"\n📚 待复习笔记 ({len(due)} 条):")
    for note in due[:20]:
        priority = format_priority_score(note)
        print(f"\n  {priority}")
        print(f"  [{note.note_id}] {note.title}")
        print(f"    间隔: {note.interval}天 | EF: {note.ef:.2f} | 复习次数: {note.total_reviews}")
        if note.reviews:
            last = note.reviews[-1]
            print(f"    上次复习: {last.date} (q={last.quality})")
        if note.reference_count > 0 or note.archive_count > 0:
            cf = sr._calculate_compound_factor(note)
            print(f"    复利因子: {cf:.2f}")


def cmd_queue(sr: SpacedRepetition):
    """显示完整复习队列"""
    queue = sr.get_queue()
    stats = sr.get_stats()

    print("=" * 60)
    print(" 📋 复习队列")
    print("=" * 60)
    print(f"\n📊 统计:")
    print(f"   总笔记数:    {stats['total_notes']}")
    print(f"   到期复习:    {stats['due_reviews']}")
    print(f"   总复习次数:  {stats['total_reviews']}")
    print(f"   平均质量:    {stats['avg_quality']:.2f}")
    print(f"   平均连续:    {stats['avg_streak']:.1f} 天")

    overdue = [n for n in queue if date.fromisoformat(n.next_review) < date.today()]
    today_due = [n for n in queue if n.next_review == date.today().isoformat()]
    upcoming = [n for n in queue if date.fromisoformat(n.next_review) > date.today()]

    if overdue:
        print(f"\n🔴 逾期复习 ({len(overdue)} 条):")
        for n in overdue[:10]:
            print(f"   [{n.note_id}] {n.title} (EF={n.ef:.2f})")

    if today_due:
        print(f"\n🟡 今日到期 ({len(today_due)} 条):")
        for n in today_due[:10]:
            print(f"   [{n.note_id}] {n.title}")

    if upcoming:
        print(f"\n⏳ 未来复习 ({len(upcoming)} 条，前10):")
        for n in upcoming[:10]:
            print(f"   [{n.note_id}] {n.title} -> {n.next_review}")

    if not queue:
        print("\n📭 复习队列为空，请先添加笔记。")


def cmd_schedule(sr: SpacedRepetition):
    """生成复习计划"""
    queue = sr.get_queue()
    due = sr.get_due_reviews()

    print("=" * 60)
    print(" 📆 复习计划")
    print("=" * 60)

    if not due:
        print("\n✅ 今日无复习任务。")
        # 给出未来7天的计划
        print("\n未来7天复习计划:")
        for i in range(1, 8):
            future_date = date.today() + timedelta(days=i)
            future_notes = [
                n for n in queue
                if n.next_review == future_date.isoformat()
            ]
            marker = "📅" if i <= 3 else "  "
            print(f"  {marker} {future_date.strftime('%Y-%m-%d')}: {len(future_notes)} 条")
        return

    # 生成今日计划
    print(f"\n📋 今日复习计划 ({len(due)} 条):")

    # 按优先级分组
    high_priority = [n for n in due if n.ef < 1.8 or n.total_reviews == 0]
    mid_priority = [n for n in due if n.ef < 2.3]
    low_priority = [n for n in due if n not in high_priority and n not in mid_priority]

    if high_priority:
        print(f"\n🔴 高优先级 ({len(high_priority)} 条，EF<1.8 或新笔记):")
        for n in high_priority:
            print(f"   [{n.note_id}] {n.title} (EF={n.ef:.2f})")

    if mid_priority:
        print(f"\n🟡 中优先级 ({len(mid_priority)} 条，EF<2.3):")
        for n in mid_priority:
            print(f"   [{n.note_id}] {n.title} (EF={n.ef:.2f})")

    if low_priority:
        print(f"\n🟢 基础优先级 ({len(low_priority)} 条):")
        for n in low_priority:
            print(f"   [{n.note_id}] {n.title} (EF={n.ef:.2f})")

    # 估计时间
    avg_questions = 4
    time_per_note = 5  # 分钟
    total_minutes = len(due) * time_per_note
    print(f"\n⏱️ 预计总时间: {total_minutes} 分钟 ({len(due)} 条 × {time_per_note} 分钟)")


def cmd_note(sr: SpacedRepetition, note_id: str):
    """查看指定笔记复习信息"""
    note = sr.get_note(note_id)
    if not note:
        print(f"笔记 {note_id} 不在复习队列中")
        return

    print("=" * 60)
    print(f" 📄 笔记复习详情: {note.title}")
    print("=" * 60)
    print(f"\n  笔记ID:     {note.note_id}")
    print(f"  添加日期:   {note.added_at}")
    print(f"  总复习次数: {note.total_reviews}")
    print(f"  连续天数:   {note.streak}")
    print(f"  当前间隔:   {note.interval} 天")
    print(f"  EF:        {note.ef:.2f}")
    print(f"  下次复习:   {note.next_review}")
    print(f"  归档次数:   {note.archive_count}")
    print(f"  引用次数:   {note.reference_count}")

    # 复利因子
    cf = sr._calculate_compound_factor(note)
    print(f"  复利因子:   {cf:.2f}")

    if note.reviews:
        print(f"\n  最近复习记录:")
        for r in note.reviews[-5:]:
            q_emoji = "🔴" if r.quality <= 2 else "🟡" if r.quality == 3 else "🟢"
            print(f"    {q_emoji} {r.date}: q={r.quality}, 间隔={r.interval}天, EF={r.ef:.2f}")

    # 遗忘曲线
    curve = sr.get_forgetting_curve_data(note_id)
    if curve.get("retention"):
        print(f"\n  遗忘曲线 (理论):")
        for d, r in zip(curve["intervals"], curve["retention"]):
            bar = "█" * int(r / 10) + "░" * (10 - int(r / 10))
            print(f"    {d:>3}天: {bar} {r}%")


def main():
    parser = argparse.ArgumentParser(description="Wiki 复习调度器")
    parser.add_argument("--today", action="store_true", help="显示今日复习任务")
    parser.add_argument("--queue", action="store_true", help="显示完整复习队列")
    parser.add_argument("--schedule", action="store_true", help="生成复习计划")
    parser.add_argument("--note", help="查看指定笔记复习详情")
    args = parser.parse_args()

    sr = SpacedRepetition()

    if args.today:
        cmd_today(sr)
    elif args.queue:
        cmd_queue(sr)
    elif args.schedule:
        cmd_schedule(sr)
    elif args.note:
        cmd_note(sr, args.note)
    else:
        # 默认显示今日
        cmd_today(sr)


if __name__ == "__main__":
    main()
