#!/usr/bin/env python3
"""
Wiki知识复利计算器
Knowledge Compound Interest Calculator

公式: value(N) = initial × (1 + links × 0.1)^N × memory_resonance
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional
import yaml

WIKI_DIR = Path.home() / ".claude" / "wiki"


def calculate_compound_value(
    initial_value: float,
    link_count: int,
    compilation_count: int,
    memory_resonance: float = 1.0
) -> float:
    """计算复利值"""
    base_multiplier = (1 + link_count * 0.1) ** compilation_count
    return initial_value * base_multiplier * memory_resonance


def get_level(value: float) -> tuple[str, str]:
    """根据复利值获取等级"""
    if value > 1000:
        return "wisdom", "🟣智慧"
    elif value > 200:
        return "mature", "🔵成熟"
    elif value > 50:
        return "growth", "🟢成长"
    elif value > 10:
        return "seedling", "🟡幼苗"
    else:
        return "seed", "🔴种子"


def read_note(note_id: str) -> Optional[dict]:
    """读取笔记并解析Frontmatter"""
    note_path = WIKI_DIR / f"{note_id}.md"
    if not note_path.exists():
        # 尝试模糊匹配
        for p in WIKI_DIR.glob(f"*{note_id}*.md"):
            note_path = p
            break
        else:
            return None

    content = note_path.read_text(encoding="utf-8")

    # 解析Frontmatter
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                fm = yaml.safe_load(parts[1])
                return {"frontmatter": fm, "content": parts[2], "path": note_path}
            except:
                pass

    return {"frontmatter": {}, "content": content, "path": note_path}


def update_compound_value(
    note_id: str,
    trigger: str,
    source: Optional[str] = None
) -> dict:
    """更新笔记复利值"""
    note = read_note(note_id)
    if not note:
        return {"error": f"Note not found: {note_id}"}

    fm = note["frontmatter"]
    compound = fm.get("compound", {})

    # 获取当前值
    initial_value = compound.get("initial_value", 5)
    link_count = compound.get("link_count", 0)
    compilation_count = compound.get("compilation_count", 0)
    memory_resonance = compound.get("memory_resonance", 1.0)

    # 根据触发器更新
    if trigger == "link":
        link_count += 1
        # 权威来源加成
        if source:
            compound_history = compound.get("compound_history", [])
            compound_history.append({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "value": link_count,
                "event": f"link_added_from_{source}"
            })
            compound["compound_history"] = compound_history

    elif trigger == "compilation":
        compilation_count += 1

    elif trigger == "memory_resonance":
        memory_resonance += 0.2
        memory_resonance = min(memory_resonance, 2.0)  # 上限

    # 计算新复利值
    new_value = calculate_compound_value(
        initial_value, link_count, compilation_count, memory_resonance
    )

    level, level_emoji = get_level(new_value)

    # 更新Frontmatter
    compound.update({
        "current_value": round(new_value, 2),
        "link_count": link_count,
        "compilation_count": compilation_count,
        "memory_resonance": round(memory_resonance, 2),
        "level": level,
        "last_updated": datetime.now().strftime("%Y-%m-%d")
    })

    fm["compound"] = compound

    # 写回文件
    write_note(note["path"], fm, note["content"])

    return {
        "note_id": note_id,
        "previous_value": compound.get("current_value", initial_value),
        "new_value": round(new_value, 2),
        "link_count": link_count,
        "compilation_count": compilation_count,
        "memory_resonance": round(memory_resonance, 2),
        "level": level_emoji
    }


def write_note(path: Path, frontmatter: dict, content: str):
    """写回笔记"""
    fm_text = yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False)
    full_content = f"---\n{fm_text}---{content}"
    path.write_text(full_content, encoding="utf-8")


def get_note_value(note_id: str) -> dict:
    """获取单条笔记复利值"""
    note = read_note(note_id)
    if not note:
        return {"error": f"Note not found: {note_id}"}

    compound = note["frontmatter"].get("compound", {})

    initial_value = compound.get("initial_value", 5)
    link_count = compound.get("link_count", 0)
    compilation_count = compound.get("compilation_count", 0)
    memory_resonance = compound.get("memory_resonance", 1.0)
    current_value = compound.get("current_value", initial_value)
    level, level_emoji = get_level(current_value)

    return {
        "note_id": note_id,
        "title": note["frontmatter"].get("title", note_id),
        "initial_value": initial_value,
        "current_value": current_value,
        "link_count": link_count,
        "compilation_count": compilation_count,
        "memory_resonance": memory_resonance,
        "level": level_emoji,
        "compound_growth": f"{((current_value/initial_value)-1)*100:.1f}%" if initial_value > 0 else "N/A"
    }


def get_top_notes(top: int = 20) -> list[dict]:
    """获取复利值最高的笔记"""
    notes = []

    if not WIKI_DIR.exists():
        return []

    for md_file in WIKI_DIR.glob("*.md"):
        note_id = md_file.stem
        try:
            value_info = get_note_value(note_id)
            if "error" not in value_info and value_info.get("current_value", 0) > 0:
                notes.append(value_info)
        except:
            continue

    # 排序
    notes.sort(key=lambda x: x["current_value"], reverse=True)
    return notes[:top]


def format_json(data: dict) -> str:
    """格式化JSON输出"""
    return json.dumps(data, ensure_ascii=False, indent=2)


def format_table(notes: list[dict]) -> str:
    """格式化表格输出"""
    if not notes:
        return "No notes found."

    lines = [
        "╔═══════════════════════════════════════════════════════════════════════╗",
        "║                     Wiki 知识复利排行榜                               ║",
        "╠═══════════════════════════════════════════════════════════════════════╣"
    ]

    for i, note in enumerate(notes, 1):
        title = note["title"][:30] if len(note.get("title", "")) > 30 else note.get("title", note["note_id"])
        value = f"{note['current_value']:.0f}"
        level = note["level"]
        growth = note.get("compound_growth", "N/A")
        links = note.get("link_count", 0)

        lines.append(f"║ {i:2}. {title:<35} {value:>8} {level}  ×{links}  +{growth:<8} ║")

    lines.append("╚═══════════════════════════════════════════════════════════════════════╝")

    return "\n".join(lines)


def dashboard():
    """复利仪表盘"""
    all_notes = get_top_notes(100)

    if not all_notes:
        print("╔══════════════════════════════════════════════════════════╗")
        print("║          Wiki 知识复利仪表盘                              ║")
        print("╠══════════════════════════════════════════════════════════╣")
        print("║  知识总数: 0    平均复利值: N/A                         ║")
        print("║  提示: 暂无笔记，开始归档你的第一个知识吧！               ║")
        print("╚══════════════════════════════════════════════════════════╝")
        return

    total_notes = len(all_notes)
    avg_value = sum(n["current_value"] for n in all_notes) / total_notes
    total_value = sum(n["current_value"] for n in all_notes)
    wisdom_count = len([n for n in all_notes if n["current_value"] > 1000])
    top_note = all_notes[0]

    level_counts = {
        "🟣智慧": len([n for n in all_notes if n["current_value"] > 1000]),
        "🔵成熟": len([n for n in all_notes if 200 < n["current_value"] <= 1000]),
        "🟢成长": len([n for n in all_notes if 50 < n["current_value"] <= 200]),
        "🟡幼苗": len([n for n in all_notes if 10 < n["current_value"] <= 50]),
        "🔴种子": len([n for n in all_notes if n["current_value"] <= 10]),
    }

    print("╔═══════════════════════════════════════════════════════════════════════════╗")
    print("║                        Wiki 知识复利仪表盘                                  ║")
    print("╠═══════════════════════════════════════════════════════════════════════════════╣")
    print(f"║  知识总数: {total_notes:<6}  平均复利值: {avg_value:<8.1f}  总复利值: {total_value:<10.0f}     ║")
    print(f"║  复利飞轮: {level_counts['🟣智慧']:<3}个智慧级  最高复利: {top_note['title'][:20]:<20} ║")
    print("╠═══════════════════════════════════════════════════════════════════════════════╣")
    print("║  等级分布:                                                              ║")
    print(f"║    🟣智慧(>1000): {level_counts['🟣智慧']:<4}  🔵成熟(200-1000): {level_counts['🔵成熟']:<4}  🟢成长(50-200): {level_counts['🟢成长']:<4}  ║")
    print(f"║    🟡幼苗(10-50):  {level_counts['🟡幼苗']:<4}  🔴种子(<10):     {level_counts['🔴种子']:<4}                                     ║")
    print("╠═══════════════════════════════════════════════════════════════════════════════╣")
    print("║  Top 5 知识复利:                                                       ║")

    for i, note in enumerate(all_notes[:5], 1):
        title = note["title"][:35] if len(note.get("title", "")) > 35 else note.get("title", note["note_id"])
        value = f"{note['current_value']:.0f}"
        print(f"║  {i}. {title:<40} {value:>8} {note['level']}                   ║")

    print("╚═══════════════════════════════════════════════════════════════════════════════╝")


def main():
    parser = argparse.ArgumentParser(description="Wiki知识复利计算器")
    parser.add_argument("--note-id", help="笔记ID")
    parser.add_argument("--update", help="更新笔记复利值")
    parser.add_argument("--trigger", choices=["link", "compilation", "memory_resonance"],
                        help="触发类型")
    parser.add_argument("--source", help="来源笔记ID(链接时)")
    parser.add_argument("--top", type=int, default=20, help="显示Top N")
    parser.add_argument("--format", choices=["json", "table"], default="table",
                        help="输出格式")
    parser.add_argument("--dashboard", action="store_true", help="显示仪表盘")

    args = parser.parse_args()

    if args.dashboard:
        dashboard()
    elif args.note_id:
        if args.format == "json":
            print(format_json(get_note_value(args.note_id)))
        else:
            note = get_note_value(args.note_id)
            if "error" in note:
                print(f"Error: {note['error']}")
            else:
                print(f"\n📊 笔记: {note['title']}")
                print(f"   当前复利值: {note['current_value']:.2f}")
                print(f"   等级: {note['level']}")
                print(f"   链接数: {note['link_count']}")
                print(f"   复习次数: {note['compilation_count']}")
                print(f"   记忆共鸣: {note['memory_resonance']:.2f}")
                print(f"   复利增长: {note['compound_growth']}")
    elif args.update:
        result = update_compound_value(args.update, args.trigger or "link", args.source)
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"\n✅ 更新成功!")
            print(f"   笔记: {result['note_id']}")
            print(f"   {result['previous_value']:.2f} → {result['new_value']:.2f}")
            print(f"   等级: {result['level']}")
    else:
        # 默认显示Top列表
        notes = get_top_notes(args.top)
        if args.format == "json":
            print(format_json(notes))
        else:
            print(format_table(notes))


if __name__ == "__main__":
    main()
