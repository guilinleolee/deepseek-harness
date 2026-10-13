#!/usr/bin/env python3
"""
Wiki-MemPalace 桥接仪表盘
实时可视化 Wiki ↔ MemPalace 同步状态

Usage:
    python3 dashboard.py
    python3 dashboard.py --compact
    python3 dashboard.py --watch
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import yaml
import re

WIKI_DIR = Path.home() / ".claude" / "wiki"
MEMPALACE_DIR = Path.home() / ".claude" / "mempalace"
BRIDGE_STATE_FILE = Path.home() / ".claude" / "bridge_state.json"
CONTRADICTION_DB = Path.home() / ".claude" / "mempalace" / "contradictions.json"


def load_bridge_state() -> dict:
    """加载桥接状态"""
    if BRIDGE_STATE_FILE.exists():
        return json.loads(BRIDGE_STATE_FILE.read_text(encoding="utf-8"))
    return {
        "wiki_to_mp": {},
        "mp_to_wiki": {},
        "last_sync": None,
        "sync_count": 0,
        "contradictions": []
    }


def load_contradictions() -> dict:
    """加载矛盾记录"""
    if CONTRADICTION_DB.exists():
        try:
            return json.loads(CONTRADICTION_DB.read_text(encoding="utf-8"))
        except:
            pass
    return {"contradictions": [], "last_scan": None}


def count_wiki_notes() -> int:
    """统计Wiki笔记数"""
    if not WIKI_DIR.exists():
        return 0
    return len(list(WIKI_DIR.glob("*.md")))


def count_mempalace_entities() -> int:
    """统计MemPalace实体数"""
    if not MEMPALACE_DIR.exists():
        return 0
    return len(list(MEMPALACE_DIR.glob("*.json")))


def get_sync_rate(wiki_count: int, mp_count: int) -> float:
    """计算同步率"""
    if wiki_count == 0 and mp_count == 0:
        return 0.0
    if wiki_count == 0:
        return 0.0
    if mp_count == 0:
        return 0.0
    synced = min(wiki_count, mp_count)
    total = max(wiki_count, mp_count)
    return (synced / total) * 100


def get_memory_resonance() -> float:
    """获取平均记忆共鸣度"""
    if not MEMPALACE_DIR.exists():
        return 0.0
    entities = list(MEMPALACE_DIR.glob("*.json"))
    if not entities:
        return 0.0
    total = 0.0
    count = 0
    for f in entities:
        try:
            entity = json.loads(f.read_text(encoding="utf-8"))
            resonance = entity.get("memory_resonance", 1.0)
            if resonance:
                total += resonance
                count += 1
        except:
            pass
    return total / count if count > 0 else 0.0


def get_compound_stats() -> dict:
    """获取复利统计"""
    if not MEMPALACE_DIR.exists():
        return {"total_value": 0, "avg_value": 0, "max_value": 0, "level_distribution": {}}
    entities = list(MEMPALACE_DIR.glob("*.json"))
    if not entities:
        return {"total_value": 0, "avg_value": 0, "max_value": 0, "level_distribution": {}}
    total_value = 0.0
    max_value = 0.0
    levels = {"seed": 0, "seedling": 0, "growth": 0, "mature": 0, "wisdom": 0}
    for f in entities:
        try:
            entity = json.loads(f.read_text(encoding="utf-8"))
            value = entity.get("compound_value", 0)
            total_value += value
            if value > max_value:
                max_value = value
            level = entity.get("level", "seed")
            levels[level] = levels.get(level, 0) + 1
        except:
            pass
    return {
        "total_value": total_value,
        "avg_value": total_value / len(entities),
        "max_value": max_value,
        "level_distribution": levels
    }


def time_ago(dt_str: Optional[str]) -> str:
    """计算时间差"""
    if not dt_str:
        return "从未同步"
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        now = datetime.now()
        diff = (now - dt).total_seconds()
        if diff < 60:
            return f"{int(diff)}秒前"
        elif diff < 3600:
            return f"{int(diff / 60)}分钟前"
        elif diff < 86400:
            return f"{int(diff / 3600)}小时前"
        else:
            return f"{int(diff / 86400)}天前"
    except:
        return dt_str[:19] if dt_str else "未知"


def render_box(content: str, width: int = 64) -> str:
    """渲染边框"""
    lines = content.strip().split("\n")
    result = f"╔{'═' * (width - 2)}╗\n"
    for line in lines:
        padding = width - len(line) - 3
        if padding < 0:
            padding = 0
        result += f"║ {line}{' ' * padding}║\n"
    result += f"╚{'═' * (width - 2)}╝"
    return result


def format_dashboard(state: dict, contradictions: dict) -> str:
    """格式化仪表盘"""
    wiki_count = count_wiki_notes()
    mp_count = count_mempalace_entities()
    synced = len(state.get("wiki_to_mp", {}))
    sync_rate = get_sync_rate(wiki_count, mp_count)
    resonance = get_memory_resonance()
    compound = get_compound_stats()
    last_sync = state.get("last_sync")
    contradiction_list = contradictions.get("contradictions", [])
    pending = sum(1 for c in contradiction_list if c.get("status") == "pending")
    resolved = sum(1 for c in contradiction_list if c.get("status") == "resolved")

    width = 64

    # 标题
    lines = [
        " Wiki ↔ MemPalace 桥接仪表盘 ",
    ]

    # 同步状态
    lines.append("")
    lines.append("【同步状态】")
    lines.append(f"  Wiki笔记:    {wiki_count:>6} 个")
    lines.append(f"  MemPalace实体: {mp_count:>5} 个")
    lines.append(f"  同步率:     {sync_rate:>6.1f}%")
    lines.append(f"  总同步次数:  {state.get('sync_count', 0):>6} 次")
    lines.append(f"  最后同步:    {time_ago(last_sync):>12}")

    # 复利状态
    lines.append("")
    lines.append("【复利状态】")
    lines.append(f"  总复利值:   {compound['total_value']:>10.0f}")
    lines.append(f"  平均复利值:  {compound['avg_value']:>10.1f}")
    lines.append(f"  最大复利值:  {compound['max_value']:>10.0f}")
    lines.append(f"  记忆共鸣度:  {resonance:>10.2f}")

    # 等级分布
    levels = compound.get("level_distribution", {})
    if levels:
        lines.append("")
        lines.append("【等级分布】")
        level_icons = {"seed": "🌱", "seedling": "🌿", "growth": "🌳", "mature": "⭐", "wisdom": "💎"}
        level_names = {"seed": "种子", "seedling": "幼苗", "growth": "成长", "mature": "成熟", "wisdom": "智慧"}
        for level, count in levels.items():
            icon = level_icons.get(level, "○")
            name = level_names.get(level, level)
            bar = "█" * min(count, 20)
            lines.append(f"  {icon} {name:<4}: {count:>4} {bar}")

    # 矛盾状态
    lines.append("")
    lines.append("【矛盾状态】")
    lines.append(f"  待解决:     {pending:>6} 个")
    lines.append(f"  已解决:     {resolved:>6} 个")
    if pending > 0:
        lines.append(f"  ⚠️  存在未解决矛盾")
    else:
        lines.append(f"  ✓  无未解决矛盾")

    # 最近矛盾
    if contradiction_list:
        lines.append("")
        lines.append("【最近矛盾】")
        for c in contradiction_list[:3]:
            ctype = c.get("type", "unknown")
            status = "⏳" if c.get("status") == "pending" else "✓"
            reason = c.get("reason", "")[:30]
            lines.append(f"  {status} [{ctype:<15}] {reason}")

    return render_box("\n".join(lines), width)


def format_compact(state: dict, contradictions: dict) -> str:
    """紧凑格式"""
    wiki_count = count_wiki_notes()
    mp_count = count_mempalace_entities()
    sync_rate = get_sync_rate(wiki_count, mp_count)
    resonance = get_memory_resonance()
    compound = get_compound_stats()
    contradiction_list = contradictions.get("contradictions", [])
    pending = sum(1 for c in contradiction_list if c.get("status") == "pending")

    return (
        f"Wiki: {wiki_count} | MemPalace: {mp_count} | "
        f"同步: {sync_rate:.1f}% | 复利: {compound['total_value']:.0f} | "
        f"共鸣: {resonance:.2f} | 矛盾: {pending}"
    )


def format_json(state: dict, contradictions: dict) -> str:
    """JSON格式"""
    wiki_count = count_wiki_notes()
    mp_count = count_mempalace_entities()
    compound = get_compound_stats()

    return json.dumps({
        "wiki_notes": wiki_count,
        "mempalace_entities": mp_count,
        "sync_rate": get_sync_rate(wiki_count, mp_count),
        "total_syncs": state.get("sync_count", 0),
        "last_sync": state.get("last_sync"),
        "compound": compound,
        "memory_resonance": get_memory_resonance(),
        "contradictions": {
            "pending": sum(1 for c in contradictions.get("contradictions", []) if c.get("status") == "pending"),
            "resolved": sum(1 for c in contradictions.get("contradictions", []) if c.get("status") == "resolved"),
            "total": len(contradictions.get("contradictions", []))
        }
    }, ensure_ascii=False, indent=2)


def watch_mode():
    """监听模式"""
    import time
    print("开始监听 Wiki ↔ MemPalace 桥接状态 (Ctrl+C 退出)...")
    last_state = None
    while True:
        try:
            state = load_bridge_state()
            contradictions = load_contradictions()
            current = format_compact(state, contradictions)
            if current != last_state:
                print(f"\r{datetime.now().strftime('%H:%M:%S')} | {current}", end="")
                last_state = current
            time.sleep(3)
        except KeyboardInterrupt:
            print("\n退出监听模式")
            break


def main():
    parser = argparse.ArgumentParser(description="Wiki-MemPalace 桥接仪表盘")
    parser.add_argument("--compact", action="store_true", help="紧凑输出")
    parser.add_argument("--watch", action="store_true", help="监听模式")
    parser.add_argument("--json", action="store_true", help="JSON格式输出")
    args = parser.parse_args()

    if args.watch:
        watch_mode()
        return

    state = load_bridge_state()
    contradictions = load_contradictions()

    if args.json:
        print(format_json(state, contradictions))
    elif args.compact:
        print(format_compact(state, contradictions))
    else:
        print(format_dashboard(state, contradictions))


if __name__ == "__main__":
    main()
