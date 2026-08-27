#!/usr/bin/env python3
"""
OpenSpace Skill Derive
DERIVED 模式 - 从现有技能派生新技能
"""

import hashlib
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

DERIVE_HISTORY_FILE = Path("~/.claude/memory/openspace-derive-history.json").expanduser()
DERIVE_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)


class DeriveStatus(Enum):
    PENDING = "pending"
    ANALYZING = "analyzing"
    DESIGNING = "designing"
    IMPLEMENTING = "implementing"
    TESTING = "testing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class DerivePattern:
    source_skill: str
    pattern_name: str
    occurrences: int
    first_seen: float
    last_seen: float
    similarity_score: float


@dataclass
class DeriveRecord:
    id: str
    source_skill: str
    new_skill_name: str
    pattern: str
    status: DeriveStatus
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    skill_content: Optional[str] = None
    test_result: Optional[dict] = None


class SkillDerive:
    def __init__(self):
        self.derive_queue: list[DeriveRecord] = []
        self.completed_derives: list[DeriveRecord] = []
        self.detected_patterns: list[DerivePattern] = []
        self._load_history()

    def _load_history(self):
        """加载历史记录"""
        if DERIVE_HISTORY_FILE.exists():
            try:
                with open(DERIVE_HISTORY_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.completed_derives = [self._dict_to_record(r) for r in data.get("completed", [])]
                    self.detected_patterns = [self._dict_to_pattern(r) for r in data.get("patterns", [])]
            except (json.JSONDecodeError, KeyError):
                self.completed_derives = []
                self.detected_patterns = []
        else:
            self.completed_derives = []
            self.detected_patterns = []

    def _save_history(self):
        """保存历史记录"""
        data = {
            "completed": [self._record_to_dict(r) for r in self.completed_derives],
            "patterns": [self._pattern_to_dict(p) for p in self.detected_patterns],
        }
        with open(DERIVE_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _record_to_dict(self, record: DeriveRecord) -> dict:
        return {
            "id": record.id,
            "source_skill": record.source_skill,
            "new_skill_name": record.new_skill_name,
            "pattern": record.pattern,
            "status": record.status.value,
            "created_at": record.created_at,
            "completed_at": record.completed_at,
            "skill_content": record.skill_content,
            "test_result": record.test_result,
        }

    def _dict_to_record(self, d: dict) -> DeriveRecord:
        return DeriveRecord(
            id=d["id"],
            source_skill=d["source_skill"],
            new_skill_name=d["new_skill_name"],
            pattern=d["pattern"],
            status=DeriveStatus(d["status"]),
            created_at=d.get("created_at", time.time()),
            completed_at=d.get("completed_at"),
            skill_content=d.get("skill_content"),
            test_result=d.get("test_result"),
        )

    def _pattern_to_dict(self, pattern: DerivePattern) -> dict:
        return {
            "source_skill": pattern.source_skill,
            "pattern_name": pattern.pattern_name,
            "occurrences": pattern.occurrences,
            "first_seen": pattern.first_seen,
            "last_seen": pattern.last_seen,
            "similarity_score": pattern.similarity_score,
        }

    def _dict_to_pattern(self, d: dict) -> DerivePattern:
        return DerivePattern(
            source_skill=d["source_skill"],
            pattern_name=d["pattern_name"],
            occurrences=d["occurrences"],
            first_seen=d["first_seen"],
            last_seen=d["last_seen"],
            similarity_score=d["similarity_score"],
        )

    def detect_pattern(
        self,
        source_skill: str,
        pattern_name: str,
        similarity_score: float = 0.8,
    ) -> DerivePattern:
        """检测派生模式"""
        existing = [p for p in self.detected_patterns if p.source_skill == source_skill and p.pattern_name == pattern_name]
        if existing:
            existing[0].occurrences += 1
            existing[0].last_seen = time.time()
            self._save_history()
            return existing[0]

        pattern = DerivePattern(
            source_skill=source_skill,
            pattern_name=pattern_name,
            occurrences=1,
            first_seen=time.time(),
            last_seen=time.time(),
            similarity_score=similarity_score,
        )
        self.detected_patterns.append(pattern)
        self._save_history()
        return pattern

    def create_derive(
        self,
        source_skill: str,
        new_skill_name: str,
        pattern: str,
    ) -> DeriveRecord:
        """创建派生任务"""
        record = DeriveRecord(
            id=f"derive-{int(time.time())}-{source_skill[:8]}",
            source_skill=source_skill,
            new_skill_name=new_skill_name,
            pattern=pattern,
            status=DeriveStatus.PENDING,
        )
        self.derive_queue.append(record)
        return record

    def analyze_source(self, derive_id: str) -> dict:
        """分析源技能"""
        for record in self.derive_queue:
            if record.id == derive_id:
                record.status = DeriveStatus.ANALYZING
                source_path = Path(f"~/.claude/skills/{record.source_skill}").expanduser()

                if not source_path.exists():
                    return {"error": f"Source skill '{record.source_skill}' not found"}

                skill_file = source_path / "SKILL.md"
                if skill_file.exists():
                    content = skill_file.read_text(encoding="utf-8")
                    return {
                        "derive_id": derive_id,
                        "source_skill": record.source_skill,
                        "content_preview": content[:500],
                        "analysis": self._analyze_pattern(record),
                    }
                return {"error": "SKILL.md not found"}
        return {"error": "Derive record not found"}

    def _analyze_pattern(self, record: DeriveRecord) -> str:
        """分析派生模式"""
        return f"从 {record.source_skill} 派生出 {record.new_skill_name}，基于模式: {record.pattern}"

    def design_new_skill(self, derive_id: str, design_content: str) -> bool:
        """设计新技能"""
        for record in self.derive_queue:
            if record.id == derive_id:
                record.status = DeriveStatus.DESIGNING
                record.skill_content = design_content
                return True
        return False

    def implement_skill(self, derive_id: str) -> bool:
        """实现新技能"""
        for record in self.derive_queue:
            if record.id == derive_id:
                record.status = DeriveStatus.IMPLEMENTING

                new_skill_path = Path(f"~/.claude/skills/{record.new_skill_name}").expanduser()
                new_skill_path.mkdir(parents=True, exist_ok=True)

                if record.skill_content:
                    skill_file = new_skill_path / "SKILL.md"
                    skill_file.write_text(record.skill_content, encoding="utf-8")

                scripts_path = new_skill_path / "scripts"
                scripts_path.mkdir(exist_ok=True)

                return True
        return False

    def test_skill(self, derive_id: str, test_result: dict) -> bool:
        """测试新技能"""
        for record in self.derive_queue:
            if record.id == derive_id:
                record.status = DeriveStatus.TESTING
                record.test_result = test_result

                if test_result.get("passed", False):
                    record.status = DeriveStatus.COMPLETED
                    record.completed_at = time.time()
                    self.derive_queue.remove(record)
                    self.completed_derives.append(record)
                    self._save_history()
                    return True
                else:
                    record.status = DeriveStatus.FAILED
                    return False
        return False

    def get_patterns(self, min_occurrences: int = 3) -> list[dict]:
        """获取检测到的模式"""
        patterns = [p for p in self.detected_patterns if p.occurrences >= min_occurrences]
        return [self._pattern_to_dict(p) for p in patterns]

    def get_queue(self) -> list[dict]:
        """获取派生队列"""
        return [self._record_to_dict(r) for r in self.derive_queue]


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="OpenSpace Skill Derive")
    parser.add_argument("--create", action="store_true", help="创建派生任务")
    parser.add_argument("--source", help="源技能名称")
    parser.add_argument("--new-name", help="新技能名称")
    parser.add_argument("--pattern", help="派生模式")
    parser.add_argument("--analyze", help="分析派生任务")
    parser.add_argument("--patterns", action="store_true", help="查看检测到的模式")
    parser.add_argument("--queue", action="store_true", help="查看派生队列")
    parser.add_argument("--min-occ", type=int, default=3, help="最小出现次数")

    args = parser.parse_args()
    deriver = SkillDerive()

    if args.create and args.source and args.new_name and args.pattern:
        record = deriver.create_derive(args.source, args.new_name, args.pattern)
        print(json.dumps(deriver._record_to_dict(record), ensure_ascii=False, indent=2))
    elif args.analyze:
        result = deriver.analyze_source(args.analyze)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.patterns:
        print(json.dumps(deriver.get_patterns(args.min_occ), ensure_ascii=False, indent=2))
    elif args.queue:
        print(json.dumps(deriver.get_queue(), ensure_ascii=False, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
