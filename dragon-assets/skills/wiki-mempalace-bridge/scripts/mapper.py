#!/usr/bin/env python3
"""
Wiki-MemPalace 映射器
将Wiki笔记映射到MemPalace房间结构
"""

import json
import re
from pathlib import Path
from typing import Optional


WING_TEMPLATES = {
    "knowledge_hall": {
        "name": "知识大厅",
        "rooms": ["architecture", "development", "research", "operations", "data"]
    },
    "business_hall": {
        "name": "商业大厅",
        "rooms": ["strategy", "marketing", "sales", "finance", "hr"]
    },
    "life_hall": {
        "name": "生活大厅",
        "rooms": ["health", "travel", "food", "entertainment", "family"]
    },
    "creative_hall": {
        "name": "创意大厅",
        "rooms": ["design", "writing", "art", "music", "video"]
    }
}

TAG_TO_ROOM = {
    # 技术
    "architecture": "architecture",
    "架构": "architecture",
    "system": "architecture",
    "系统": "architecture",
    "development": "development",
    "开发": "development",
    "coding": "development",
    "编程": "development",
    "research": "research",
    "调研": "research",
    "study": "research",
    "学习": "research",
    "operations": "operations",
    "运维": "operations",
    "devops": "operations",
    "data": "data",
    "数据": "data",
    "database": "data",
    "数据库": "data",
    # 商业
    "strategy": "strategy",
    "战略": "strategy",
    "marketing": "marketing",
    "营销": "marketing",
    "sales": "sales",
    "销售": "sales",
    "finance": "finance",
    "财务": "finance",
    "hr": "hr",
    "人力资源": "hr",
    # 生活
    "health": "health",
    "健康": "health",
    "travel": "travel",
    "旅游": "travel",
    "food": "food",
    "美食": "food",
    "entertainment": "entertainment",
    "娱乐": "entertainment",
    "family": "family",
    "家庭": "family",
    # 创意
    "design": "design",
    "设计": "design",
    "writing": "writing",
    "写作": "writing",
    "art": "art",
    "艺术": "art",
    "music": "music",
    "音乐": "music",
    "video": "video",
    "视频": "video",
}


class WikiMapper:
    """Wiki笔记映射器"""

    def __init__(self, wiki_note: dict):
        self.note = wiki_note
        self.fm = wiki_note.get("frontmatter", {})
        self.content = wiki_note.get("content", "")

    def get_title(self) -> str:
        """获取标题"""
        return self.fm.get("title", "Untitled")

    def get_tags(self) -> list:
        """获取标签"""
        tags = self.fm.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",")]
        return [str(t).replace("#", "").strip() for t in tags]

    def get_compound_value(self) -> float:
        """获取复利值"""
        compound = self.fm.get("compound", {})
        return compound.get("current_value", compound.get("initial_value", 5))

    def get_level(self) -> str:
        """获取等级"""
        compound = self.fm.get("compound", {})
        return compound.get("level", "seed")

    def map_to_wing(self) -> str:
        """映射到Wing"""
        tags = self.get_tags()

        for tag in tags:
            tag_lower = tag.lower()
            if any(k in tag_lower for k in ["tech", "技术", "dev", "code", "架构", "data", "算法"]):
                return "knowledge_hall"
            if any(k in tag_lower for k in ["biz", "商业", "market", "营销", "sales", "财务", "hr"]):
                return "business_hall"
            if any(k in tag_lower for k in ["life", "生活", "health", "travel", "food"]):
                return "life_hall"
            if any(k in tag_lower for k in ["design", "设计", "creative", "创意", "art", "art"]):
                return "creative_hall"

        return "knowledge_hall"  # 默认

    def map_to_room(self) -> str:
        """映射到Room"""
        tags = self.get_tags()

        for tag in tags:
            tag_clean = tag.lower().replace("-", "_").replace(" ", "_")
            for key, room in TAG_TO_ROOM.items():
                if key in tag_clean:
                    return room

        # 从内容推断
        content_keywords = self.content.lower()
        if any(k in content_keywords for k in ["api", "rest", "grpc", "endpoint"]):
            return "architecture"
        if any(k in content_keywords for k in ["database", "sql", "nosql", "存储"]):
            return "data"
        if any(k in content_keywords for k in ["test", "测试", "qa", "验证"]):
            return "operations"

        return "development"  # 默认

    def map_to_hall(self) -> str:
        """获取完整的Hall路径"""
        wing = self.map_to_wing()
        room = self.map_to_room()
        return f"{wing}/{room}"

    def get_importance(self) -> float:
        """获取重要性评分 (0-1)"""
        value = self.get_compound_value()

        if value > 1000:
            return 1.0
        elif value > 200:
            return 0.8
        elif value > 50:
            return 0.6
        elif value > 10:
            return 0.4
        else:
            return 0.2

    def get_memory_resonance(self) -> float:
        """获取记忆共鸣度"""
        compound = self.fm.get("compound", {})
        return compound.get("memory_resonance", 1.0)

    def extract_entities(self) -> list:
        """提取实体"""
        entities = []

        # 从frontmatter提取
        if "sources" in self.fm:
            for source in self.fm["sources"]:
                entities.append({
                    "type": "source",
                    "name": str(source),
                    "source": "frontmatter"
                })

        # 从双链语法提取 [[链接]]
        wiki_links = re.findall(r'\[\[([^\]]+)\]\]', self.content)
        for link in wiki_links:
            entities.append({
                "type": "link",
                "name": link,
                "source": "wiki_link"
            })

        return entities

    def build_mempalace_entity(self) -> dict:
        """构建MemPalace实体"""
        return {
            "entity_id": f"entity_{Path(self.note.get('path', 'unknown')).stem}",
            "name": self.get_title(),
            "type": "wiki_note",
            "wing": self.map_to_wing(),
            "room": self.map_to_room(),
            "hall": self.map_to_hall(),
            "importance": self.get_importance(),
            "compound_value": self.get_compound_value(),
            "memory_resonance": self.get_memory_resonance(),
            "level": self.get_level(),
            "tags": self.get_tags(),
            "entities": self.extract_entities(),
            "source": "wiki-mempalace-bridge"
        }

    def get_mapping_report(self) -> dict:
        """获取映射报告"""
        return {
            "title": self.get_title(),
            "tags": self.get_tags(),
            "wing": self.map_to_wing(),
            "room": self.map_to_room(),
            "hall": self.map_to_hall(),
            "importance": self.get_importance(),
            "compound_value": self.get_compound_value(),
            "level": self.get_level(),
            "entities_found": len(self.extract_entities())
        }


def map_wiki_note(wiki_note: dict) -> dict:
    """便捷函数：映射Wiki笔记"""
    mapper = WikiMapper(wiki_note)
    return mapper.build_mempalace_entity()


def get_mapping_report(wiki_note: dict) -> dict:
    """便捷函数：获取映射报告"""
    mapper = WikiMapper(wiki_note)
    return mapper.get_mapping_report()


def preview_mapping(tags: list, content: str = "") -> dict:
    """预览映射结果（不依赖完整笔记）"""
    preview_note = {
        "frontmatter": {"title": "Preview", "tags": tags},
        "content": content
    }
    return get_mapping_report(preview_note)


if __name__ == "__main__":
    import sys
    import yaml

    if len(sys.argv) < 2:
        print("Usage: python3 mapper.py <note_id>")
        sys.exit(1)

    note_id = sys.argv[1]
    wiki_dir = Path.home() / ".claude" / "wiki"
    note_path = wiki_dir / f"{note_id}.md"

    if not note_path.exists():
        print(f"Note not found: {note_id}")
        sys.exit(1)

    content = note_path.read_text(encoding="utf-8")

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm = yaml.safe_load(parts[1])
            content = parts[2]
        else:
            fm = {}
    else:
        fm = {}

    wiki_note = {"frontmatter": fm, "content": content, "path": note_path}
    report = get_mapping_report(wiki_note)

    print(json.dumps(report, ensure_ascii=False, indent=2))
