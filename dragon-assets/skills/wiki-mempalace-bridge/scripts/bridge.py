#!/usr/bin/env python3
"""
Wiki-MemPalace 桥接核心脚本
双向同步 Wiki笔记 和 MemPalace房间

Usage:
    python3 bridge.py --sync wiki-to-mp --note-id "microservice-ddd"
    python3 bridge.py --sync bidirectional --all
    python3 bridge.py --sync contradiction --note-id "microservice-ddd" --status "resolved"
    python3 bridge.py --status
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import yaml

WIKI_DIR = Path.home() / ".claude" / "wiki"
MEMPALACE_DIR = Path.home() / ".claude" / "mempalace"
BRIDGE_STATE_FILE = Path.home() / ".claude" / "bridge_state.json"


def load_bridge_state() -> dict:
    """加载桥接状态"""
    if BRIDGE_STATE_FILE.exists():
        return json.loads(BRIDGE_STATE_FILE.read_text(encoding="utf-8"))
    return {
        "wiki_to_mp": {},      # wiki_note_id -> mempalace_entity_id
        "mp_to_wiki": {},      # mempalace_entity_id -> wiki_note_id
        "last_sync": None,
        "sync_count": 0,
        "contradictions": []
    }


def save_bridge_state(state: dict):
    """保存桥接状态"""
    BRIDGE_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    BRIDGE_STATE_FILE.write_text(
        json.dumps(state, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def read_wiki_note(note_id: str) -> Optional[dict]:
    """读取Wiki笔记"""
    note_path = WIKI_DIR / f"{note_id}.md"
    if not note_path.exists():
        for p in WIKI_DIR.glob(f"*{note_id}*.md"):
            note_path = p
            break
        else:
            return None

    content = note_path.read_text(encoding="utf-8")

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                fm = yaml.safe_load(parts[1])
                return {"frontmatter": fm, "content": parts[2], "path": note_path}
            except:
                pass

    return {"frontmatter": {}, "content": content, "path": note_path}


def read_mempalace_entity(entity_id: str) -> Optional[dict]:
    """读取MemPalace实体"""
    entity_file = MEMPALACE_DIR / f"{entity_id}.json"
    if not entity_file.exists():
        return None

    try:
        return json.loads(entity_file.read_text(encoding="utf-8"))
    except:
        return None


def create_mempalace_entity(note: dict) -> str:
    """在MemPalace中创建实体"""
    fm = note["frontmatter"]
    title = fm.get("title", "Untitled")
    tags = fm.get("tags", [])
    compound = fm.get("compound", {})

    # 生成实体ID
    entity_id = f"entity_{note['path'].stem}"

    # 创建实体
    entity = {
        "entity_id": entity_id,
        "name": title,
        "claims": [],
        "wiki_notes": [note["path"].stem],
        "wiki_compound_value": compound.get("current_value", 0),
        "bridge_status": "synced",
        "last_sync": datetime.now().isoformat(),
        "room": _tags_to_room(tags),
        "wing": _tags_to_wing(tags),
        "compound_value": compound.get("current_value", 5),
        "link_count": compound.get("link_count", 0),
        "level": compound.get("level", "seed")
    }

    # 保存实体
    MEMPALACE_DIR.mkdir(parents=True, exist_ok=True)
    entity_file = MEMPALACE_DIR / f"{entity_id}.json"
    entity_file.write_text(json.dumps(entity, ensure_ascii=False, indent=2), encoding="utf-8")

    return entity_id


def update_wiki_mempalace_field(note_path: Path, entity_id: str, room: str, wing: str, importance: float):
    """更新Wiki笔记的MemPalace映射字段"""
    content = note_path.read_text(encoding="utf-8")

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                fm = yaml.safe_load(parts[1])
                content = parts[2]
            except:
                fm = {}
    else:
        fm = {}

    # 更新mempalace字段
    fm["mempalace"] = {
        "entity_id": entity_id,
        "room": room,
        "wing": wing,
        "importance": importance,
        "synced_at": datetime.now().isoformat(),
        "last_contradiction": fm.get("mempalace", {}).get("last_contradiction"),
        "contradiction_count": fm.get("mempalace", {}).get("contradiction_count", 0)
    }

    # 写回文件
    fm_text = yaml.dump(fm, allow_unicode=True, default_flow_style=False)
    full_content = f"---\n{fm_text}---{content}"
    note_path.write_text(full_content, encoding="utf-8")


def _tags_to_room(tags: list) -> str:
    """标签转房间"""
    if not tags:
        return "general/uncategorized"
    return " / ".join(str(t).replace("#", "") for t in tags[:3])


def _tags_to_wing(tags: list) -> str:
    """标签转Wing"""
    for tag in tags:
        tag_str = str(tag).lower()
        if "tech" in tag_str or "技术" in tag_str:
            return "knowledge_hall"
        if "biz" in tag_str or "商业" in tag_str or "business" in tag_str:
            return "business_hall"
        if "life" in tag_str or "生活" in tag_str:
            return "life_hall"
        if "creative" in tag_str or "创意" in tag_str:
            return "creative_hall"
    return "knowledge_hall"


def sync_wiki_to_mempalace(note_id: str) -> dict:
    """同步Wiki笔记到MemPalace"""
    state = load_bridge_state()

    note = read_wiki_note(note_id)
    if not note:
        return {"error": f"Wiki笔记未找到: {note_id}"}

    fm = note["frontmatter"]
    title = fm.get("title", "Untitled")

    # 检查是否已同步
    existing_entity_id = state["wiki_to_mp"].get(note_id)
    if existing_entity_id:
        # 更新实体
        entity = read_mempalace_entity(existing_entity_id)
        if entity:
            compound = fm.get("compound", {})
            entity["wiki_compound_value"] = compound.get("current_value", 0)
            entity["link_count"] = compound.get("link_count", 0)
            entity["level"] = compound.get("level", "seed")
            entity["last_sync"] = datetime.now().isoformat()

            entity_file = MEMPALACE_DIR / f"{existing_entity_id}.json"
            entity_file.write_text(json.dumps(entity, ensure_ascii=False, indent=2), encoding="utf-8")

            return {
                "note_id": note_id,
                "entity_id": existing_entity_id,
                "action": "updated",
                "title": title
            }

    # 创建新实体
    entity_id = create_mempalace_entity(note)

    # 更新映射
    state["wiki_to_mp"][note_id] = entity_id
    state["mp_to_wiki"][entity_id] = note_id
    state["sync_count"] += 1
    state["last_sync"] = datetime.now().isoformat()
    save_bridge_state(state)

    # 更新Wiki笔记
    tags = fm.get("tags", [])
    compound = fm.get("compound", {})
    update_wiki_mempalace_field(
        note["path"],
        entity_id,
        _tags_to_room(tags),
        _tags_to_wing(tags),
        compound.get("current_value", 5) / 1000  # 归一化到0-1
    )

    return {
        "note_id": note_id,
        "entity_id": entity_id,
        "action": "created",
        "title": title,
        "room": _tags_to_room(tags),
        "wing": _tags_to_wing(tags)
    }


def sync_mempalace_to_wiki(entity_id: str) -> dict:
    """同步MemPalace实体到Wiki"""
    state = load_bridge_state()

    entity = read_mempalace_entity(entity_id)
    if not entity:
        return {"error": f"MemPalace实体未找到: {entity_id}"}

    note_id = state["mp_to_wiki"].get(entity_id)
    if not note_id:
        return {"error": f"未找到对应Wiki笔记: {entity_id}"}

    note = read_wiki_note(note_id)
    if not note:
        return {"error": f"Wiki笔记未找到: {note_id}"}

    # 检查是否有矛盾需要标记
    if entity.get("contradictions"):
        _mark_note_contradiction(note["path"], entity["contradictions"])

    return {
        "entity_id": entity_id,
        "note_id": note_id,
        "action": "synced"
    }


def sync_bidirectional(all_notes: bool = False, note_id: Optional[str] = None) -> dict:
    """双向同步"""
    results = {"wiki_to_mp": [], "mp_to_wiki": [], "errors": []}

    if all_notes:
        # 同步所有Wiki笔记
        if WIKI_DIR.exists():
            for md_file in WIKI_DIR.glob("*.md"):
                nid = md_file.stem
                result = sync_wiki_to_mempalace(nid)
                if "error" in result:
                    results["errors"].append(result)
                else:
                    results["wiki_to_mp"].append(result)

    elif note_id:
        # 同步指定笔记
        result = sync_wiki_to_mempalace(note_id)
        if "error" in result:
            results["errors"].append(result)
        else:
            results["wiki_to_mp"].append(result)

        # 反向同步
        if "entity_id" in result:
            reverse_result = sync_mempalace_to_wiki(result["entity_id"])
            if "error" not in reverse_result:
                results["mp_to_wiki"].append(reverse_result)

    return results


def _mark_note_contradiction(note_path: Path, contradictions: list):
    """标记笔记矛盾"""
    content = note_path.read_text(encoding="utf-8")

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                fm = yaml.safe_load(parts[1])
                content = parts[2]
            except:
                fm = {}
    else:
        fm = {}

    compound = fm.get("compound", {})

    # 添加矛盾标记
    compound["disputed"] = True
    compound["disputed_with"] = [c.get("entity_id") for c in contradictions]
    compound["dispute_reason"] = "; ".join(c.get("reason", "") for c in contradictions)
    compound["resolution_status"] = "pending"

    fm["compound"] = compound

    fm_text = yaml.dump(fm, allow_unicode=True, default_flow_style=False)
    full_content = f"---\n{fm_text}---{content}"
    note_path.write_text(full_content, encoding="utf-8")


def get_bridge_status() -> dict:
    """获取桥接状态"""
    state = load_bridge_state()

    wiki_count = len(state["wiki_to_mp"])
    mp_count = len(state["mp_to_wiki"])
    sync_rate = min(wiki_count, mp_count) / max(wiki_count, mp_count) * 100 if wiki_count or mp_count else 0

    contradiction_count = len(state.get("contradictions", []))

    return {
        "wiki_notes": wiki_count,
        "mempalace_entities": mp_count,
        "sync_rate": round(sync_rate, 1),
        "total_syncs": state["sync_count"],
        "last_sync": state["last_sync"],
        "pending_contradictions": contradiction_count
    }


def format_status_table(status: dict) -> str:
    """格式化状态表格"""
    lines = [
        "╔══════════════════════════════════════════════════════════════════╗",
        "║       Wiki ↔ MemPalace 桥接状态                          ║",
        "╠══════════════════════════════════════════════════════════════════╣"
    ]

    wiki_count = status["wiki_notes"]
    mp_count = status["mempalace_entities"]
    sync_rate = status["sync_rate"]
    total_syncs = status["total_syncs"]
    last_sync = status["last_sync"] or "从未同步"
    contradictions = status["pending_contradictions"]

    lines.append(f"║  Wiki笔记: {wiki_count:<6}  MemPalace实体: {mp_count:<6}              ║")
    lines.append(f"║  同步率: {sync_rate:<5}%  总同步次数: {total_syncs:<6}                  ║")
    lines.append(f"║  最后同步: {last_sync:<32}              ║")
    lines.append(f"║  待解决矛盾: {contradictions:<4}                                     ║")
    lines.append("╚══════════════════════════════════════════════════════════════════╝")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Wiki-MemPalace 桥接器")
    parser.add_argument("--sync", choices=["wiki-to-mp", "mp-to-wiki", "bidirectional", "contradiction"],
                        help="同步方向")
    parser.add_argument("--note-id", help="笔记ID")
    parser.add_argument("--entity-id", help="MemPalace实体ID")
    parser.add_argument("--all", action="store_true", help="同步所有笔记")
    parser.add_argument("--status", action="store_true", help="显示桥接状态")
    parser.add_argument("--format", choices=["json", "table"], default="table", help="输出格式")

    args = parser.parse_args()

    if args.status:
        status = get_bridge_status()
        if args.format == "json":
            print(json.dumps(status, ensure_ascii=False, indent=2))
        else:
            print(format_status_table(status))

    elif args.sync == "wiki-to-mp":
        if not args.note_id:
            print("Error: --note-id required for wiki-to-mp sync")
            sys.exit(1)
        result = sync_wiki_to_mempalace(args.note_id)
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"✓ 同步成功: {result['title']}")
            print(f"  Entity ID: {result['entity_id']}")
            print(f"  Action: {result['action']}")

    elif args.sync == "mp-to-wiki":
        if not args.entity_id:
            print("Error: --entity-id required for mp-to-wiki sync")
            sys.exit(1)
        result = sync_mempalace_to_wiki(args.entity_id)
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"✓ 同步成功")

    elif args.sync == "bidirectional":
        results = sync_bidirectional(all_notes=args.all, note_id=args.note_id)
        if args.format == "json":
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            print(f"\n✓ 双向同步完成")
            print(f"  Wiki → MemPalace: {len(results['wiki_to_mp'])} 条")
            print(f"  MemPalace → Wiki: {len(results['mp_to_wiki'])} 条")
            if results["errors"]:
                print(f"  错误: {len(results['errors'])} 条")

    elif args.sync == "contradiction":
        if not args.note_id:
            print("Error: --note-id required for contradiction sync")
            sys.exit(1)
        print(f"矛盾同步: {args.note_id}")
        print(f"状态: {args.status or 'pending'}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
