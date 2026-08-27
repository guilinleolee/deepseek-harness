#!/usr/bin/env python3
"""
ViMax RAG Tracker - 角色追踪与RAG存储管理器
支持Scene/Event/Novel三层角色一致性追踪
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class CharacterProfile:
    """角色档案"""
    id: str
    name: str
    description: str
    traits: List[str]
    static_features: Dict[str, str] = field(default_factory=dict)  # 静态特征
    dynamic_features: Dict[str, Any] = field(default_factory=dict)  # 动态特征
    appearances: List[Dict] = field(default_factory=list)  # 出现记录
    relationships: Dict[str, str] = field(default_factory=dict)  # 关系网络


@dataclass
class SceneAppearance:
    """场景出现记录"""
    scene_id: str
    event_id: str
    description: str
    actions: List[str]
    emotions: List[str]
    dialogue: Optional[str] = None


class ViMaxRAGTracker:
    """ViMax RAG角色追踪器"""

    def __init__(self, db_path: str = "./vimax_rag"):
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)

        self.characters_file = self.db_path / "characters.json"
        self.relationships_file = self.db_path / "relationships.json"
        self.scenes_file = self.db_path / "scenes.json"
        self.events_file = self.db_path / "events.json"

        self.characters: Dict[str, CharacterProfile] = {}
        self._load_characters()

    def _load_characters(self):
        """加载角色数据"""
        if self.characters_file.exists():
            with open(self.characters_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for char_id, char_data in data.items():
                    self.characters[char_id] = CharacterProfile(**char_data)

    def _save_characters(self):
        """保存角色数据"""
        data = {
            char_id: {
                "id": char.id,
                "name": char.name,
                "description": char.description,
                "traits": char.traits,
                "static_features": char.static_features,
                "dynamic_features": char.dynamic_features,
                "appearances": char.appearances,
                "relationships": char.relationships
            }
            for char_id, char in self.characters.items()
        }
        with open(self.characters_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_character(self, char_id: str, name: str, description: str,
                     traits: List[str], static_features: Dict[str, str]) -> CharacterProfile:
        """添加角色"""
        character = CharacterProfile(
            id=char_id,
            name=name,
            description=description,
            traits=traits,
            static_features=static_features
        )
        self.characters[char_id] = character
        self._save_characters()
        print(f"[RAG] 添加角色: {name} ({char_id})")
        return character

    def update_character(self, char_id: str, updates: Dict[str, Any]):
        """更新角色信息"""
        if char_id not in self.characters:
            print(f"[RAG] 角色不存在: {char_id}")
            return None

        character = self.characters[char_id]
        for key, value in updates.items():
            if hasattr(character, key):
                setattr(character, key, value)

        self._save_characters()
        print(f"[RAG] 更新角色: {char_id}")
        return character

    def record_appearance(self, char_id: str, scene_id: str, event_id: str,
                        description: str, actions: List[str], emotions: List[str],
                        dialogue: Optional[str] = None):
        """记录角色出现"""
        if char_id not in self.characters:
            print(f"[RAG] 角色不存在: {char_id}")
            return

        appearance = SceneAppearance(
            scene_id=scene_id,
            event_id=event_id,
            description=description,
            actions=actions,
            emotions=emotions,
            dialogue=dialogue
        )

        self.characters[char_id].appearances.append({
            "scene_id": scene_id,
            "event_id": event_id,
            "description": description,
            "actions": actions,
            "emotions": emotions,
            "dialogue": dialogue,
            "timestamp": datetime.now().isoformat()
        })

        self._save_characters()
        print(f"[RAG] 记录出现: {char_id} in scene {scene_id}")

    def get_character(self, char_id: str) -> Optional[CharacterProfile]:
        """获取角色信息"""
        return self.characters.get(char_id)

    def query_character(self, query: str) -> List[CharacterProfile]:
        """查询角色"""
        results = []
        query_lower = query.lower()

        for character in self.characters.values():
            # 匹配名称
            if query_lower in character.name.lower():
                results.append(character)
                continue

            # 匹配描述
            if query_lower in character.description.lower():
                results.append(character)
                continue

            # 匹配特征
            for feature_value in character.static_features.values():
                if query_lower in feature_value.lower():
                    results.append(character)
                    break

        return results

    def get_character_arc(self, char_id: str) -> Dict[str, Any]:
        """获取角色成长弧"""
        if char_id not in self.characters:
            return {"error": "角色不存在"}

        character = self.characters[char_id]
        appearances = character.appearances

        if not appearances:
            return {"error": "无出现记录"}

        # 提取情感变化
        emotions_over_time = [a.get("emotions", []) for a in appearances]

        # 提取动作变化
        actions_over_time = [a.get("actions", []) for a in appearances]

        return {
            "character_id": char_id,
            "character_name": character.name,
            "total_appearances": len(appearances),
            "emotions_over_time": emotions_over_time,
            "actions_over_time": actions_over_time,
            "growth_summary": self._summarize_growth(character)
        }

    def _summarize_growth(self, character: CharacterProfile) -> str:
        """总结角色成长"""
        if len(character.appearances) < 2:
            return "角色出场次数不足，无法分析成长轨迹"

        # 简单分析：提取情感关键词变化
        emotions = []
        for app in character.appearances:
            emotions.extend(app.get("emotions", []))

        if not emotions:
            return "无情感记录"

        # 统计最常见的情感
        from collections import Counter
        emotion_counts = Counter(emotions)
        return f"主要情感: {emotion_counts.most_common(3)}"

    def export_all(self) -> Dict[str, Any]:
        """导出所有RAG数据"""
        return {
            "characters": {
                char_id: {
                    "id": char.id,
                    "name": char.name,
                    "description": char.description,
                    "traits": char.traits,
                    "static_features": char.static_features,
                    "appearance_count": len(char.appearances),
                    "relationships": char.relationships
                }
                for char_id, char in self.characters.items()
            },
            "total_characters": len(self.characters),
            "export_time": datetime.now().isoformat()
        }

    def consistency_check(self) -> Dict[str, Any]:
        """角色一致性检查"""
        issues = []

        for char_id, character in self.characters.items():
            # 检查静态特征一致性
            appearances = character.appearances
            if len(appearances) < 2:
                continue

            # 简单检查：描述一致性
            descriptions = [app.get("description", "") for app in appearances]
            if len(set(descriptions)) > len(descriptions) * 0.8:
                issues.append({
                    "character_id": char_id,
                    "type": "description_inconsistency",
                    "severity": "warning",
                    "message": f"角色{character.name}描述变化较多"
                })

        return {
            "check_time": datetime.now().isoformat(),
            "total_characters": len(self.characters),
            "issues_found": len(issues),
            "issues": issues
        }


def main():
    parser = argparse.ArgumentParser(description="ViMax RAG Tracker")
    parser.add_argument("--add", nargs=4, metavar=("ID", "NAME", "DESC", "TRAITS"),
                        help="添加角色 (ID NAME DESCRIPTION TRAITS)")
    parser.add_argument("--query", metavar="TEXT", help="查询角色")
    parser.add_argument("--arc", metavar="CHAR_ID", help="获取角色成长弧")
    parser.add_argument("--record", nargs=5, metavar=("CHAR_ID", "SCENE_ID", "EVENT_ID", "DESC", "ACTIONS"),
                        help="记录出现")
    parser.add_argument("--check", action="store_true", help="一致性检查")
    parser.add_argument("--export", action="store_true", help="导出数据")
    parser.add_argument("--db", default="./vimax_rag", help="数据库目录")

    args = parser.parse_args()
    tracker = ViMaxRAGTracker(args.db)

    if args.add:
        char_id, name, desc, traits = args.add
        traits_list = traits.split(",")
        tracker.add_character(char_id, name, desc, traits_list, {})

    elif args.query:
        results = tracker.query_character(args.query)
        print(f"[RAG] 查询结果 ({len(results)}个):")
        for char in results:
            print(f"  - {char.name}: {char.description[:50]}...")

    elif args.arc:
        arc = tracker.get_character_arc(args.arc)
        print(json.dumps(arc, ensure_ascii=False, indent=2))

    elif args.record:
        char_id, scene_id, event_id, desc, actions = args.record
        tracker.record_appearance(
            char_id, scene_id, event_id, desc,
            actions.split(","), []
        )

    elif args.check:
        result = tracker.consistency_check()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.export:
        data = tracker.export_all()
        print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
