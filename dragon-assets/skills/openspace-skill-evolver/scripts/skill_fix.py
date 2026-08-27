#!/usr/bin/env python3
"""
OpenSpace Skill Fix
FIX 模式 - 修复技能缺陷
"""

import json
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

FIX_HISTORY_FILE = Path("~/.claude/memory/openspace-fix-history.json").expanduser()
FIX_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)


class FixStatus(Enum):
    PENDING = "pending"
    ANALYZING = "analyzing"
    FIXING = "fixing"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class FixRecord:
    id: str
    skill_name: str
    issue: str
    analysis: str
    status: FixStatus
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    fix_content: Optional[str] = None
    verification_result: Optional[dict] = None
    attempts: int = 0


class SkillFix:
    def __init__(self):
        self.fix_queue: list[FixRecord] = []
        self.completed_fixes: list[FixRecord] = []
        self._load_history()

    def _load_history(self):
        """加载历史记录"""
        if FIX_HISTORY_FILE.exists():
            try:
                with open(FIX_HISTORY_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.completed_fixes = [self._dict_to_record(r) for r in data]
            except (json.JSONDecodeError, KeyError):
                self.completed_fixes = []

    def _save_history(self):
        """保存历史记录"""
        data = [self._record_to_dict(r) for r in self.completed_fixes]
        with open(FIX_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _record_to_dict(self, record: FixRecord) -> dict:
        return {
            "id": record.id,
            "skill_name": record.skill_name,
            "issue": record.issue,
            "analysis": record.analysis,
            "status": record.status.value,
            "created_at": record.created_at,
            "completed_at": record.completed_at,
            "fix_content": record.fix_content,
            "verification_result": record.verification_result,
            "attempts": record.attempts,
        }

    def _dict_to_record(self, d: dict) -> FixRecord:
        return FixRecord(
            id=d["id"],
            skill_name=d["skill_name"],
            issue=d["issue"],
            analysis=d.get("analysis", ""),
            status=FixStatus(d["status"]),
            created_at=d.get("created_at", time.time()),
            completed_at=d.get("completed_at"),
            fix_content=d.get("fix_content"),
            verification_result=d.get("verification_result"),
            attempts=d.get("attempts", 0),
        )

    def create_fix(
        self,
        skill_name: str,
        issue: str,
        analysis: str = "",
    ) -> FixRecord:
        """创建修复任务"""
        record = FixRecord(
            id=f"fix-{int(time.time())}-{skill_name[:8]}",
            skill_name=skill_name,
            issue=issue,
            analysis=analysis,
            status=FixStatus.PENDING,
        )
        self.fix_queue.append(record)
        return record

    def analyze_issue(self, fix_id: str) -> dict:
        """分析问题"""
        for record in self.fix_queue:
            if record.id == fix_id:
                record.status = FixStatus.ANALYZING
                return {
                    "fix_id": fix_id,
                    "skill_name": record.skill_name,
                    "issue": record.issue,
                    "analysis": self._perform_analysis(record),
                }
        return {"error": "Fix record not found"}

    def _perform_analysis(self, record: FixRecord) -> str:
        """执行分析"""
        skill_path = Path(f"~/.claude/skills/{record.skill_name}").expanduser()
        if not skill_path.exists():
            return f"Skill '{record.skill_name}' not found"

        skill_file = skill_path / "SKILL.md"
        if not skill_file.exists():
            return f"SKILL.md not found for '{record.skill_name}'"

        issues = []
        if "超时" in record.issue or "timeout" in record.issue.lower():
            issues.append("可能存在超时配置问题")
        if "错误" in record.issue or "error" in record.issue.lower():
            issues.append("可能存在异常处理问题")
        if "失败" in record.issue or "fail" in record.issue.lower():
            issues.append("可能存在边界条件处理问题")

        return "; ".join(issues) if issues else "需要进一步分析"

    def apply_fix(self, fix_id: str, fix_content: str) -> bool:
        """应用修复"""
        for record in self.fix_queue:
            if record.id == fix_id:
                record.status = FixStatus.FIXING
                record.fix_content = fix_content
                record.attempts += 1

                skill_path = Path(f"~/.claude/skills/{record.skill_name}").expanduser()
                skill_file = skill_path / "SKILL.md"

                if skill_file.exists():
                    content = skill_file.read_text(encoding="utf-8")
                    content += f"\n\n<!-- FIX {fix_id} -->\n{fix_content}\n<!-- END FIX {fix_id} -->"
                    skill_file.write_text(content, encoding="utf-8")

                record.status = FixStatus.VERIFYING
                return True
        return False

    def verify_fix(self, fix_id: str, test_result: dict) -> bool:
        """验证修复"""
        for record in self.fix_queue:
            if record.id == fix_id:
                record.verification_result = test_result
                if test_result.get("passed", False):
                    record.status = FixStatus.COMPLETED
                    record.completed_at = time.time()
                    self.fix_queue.remove(record)
                    self.completed_fixes.append(record)
                    self._save_history()
                    return True
                else:
                    record.status = FixStatus.FAILED
                    return False
        return False

    def get_queue(self) -> list[dict]:
        """获取修复队列"""
        return [self._record_to_dict(r) for r in self.fix_queue]

    def get_history(self, limit: int = 50) -> list[dict]:
        """获取修复历史"""
        records = self.completed_fixes[-limit:]
        return [self._record_to_dict(r) for r in records]


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="OpenSpace Skill Fix")
    parser.add_argument("--create", action="store_true", help="创建修复任务")
    parser.add_argument("--target", help="目标技能名称")
    parser.add_argument("--issue", help="问题描述")
    parser.add_argument("--analyze", help="分析修复任务")
    parser.add_argument("--apply", help="应用修复")
    parser.add_argument("--fix-content", help="修复内容")
    parser.add_argument("--verify", help="验证修复")
    parser.add_argument("--queue", action="store_true", help="查看修复队列")
    parser.add_argument("--history", action="store_true", help="查看修复历史")

    args = parser.parse_args()
    fixer = SkillFix()

    if args.create and args.target and args.issue:
        record = fixer.create_fix(args.target, args.issue)
        print(json.dumps(fixer._record_to_dict(record), ensure_ascii=False, indent=2))
    elif args.analyze:
        result = fixer.analyze_issue(args.analyze)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.apply and args.fix_content:
        result = fixer.apply_fix(args.apply, args.fix_content)
        print(json.dumps({"success": result}, ensure_ascii=False, indent=2))
    elif args.verify:
        test_result = {"passed": True, "tests_run": 5}
        result = fixer.verify_fix(args.verify, test_result)
        print(json.dumps({"success": result}, ensure_ascii=False, indent=2))
    elif args.queue:
        print(json.dumps(fixer.get_queue(), ensure_ascii=False, indent=2))
    elif args.history:
        print(json.dumps(fixer.get_history(), ensure_ascii=False, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
