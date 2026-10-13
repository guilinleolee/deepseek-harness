#!/usr/bin/env python3
"""
OpenSpace Skill Capture
CAPTURED 模式 - 捕获工作流为 Skill
"""

import json
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

CAPTURE_HISTORY_FILE = Path("~/.claude/memory/openspace-capture-history.json").expanduser()
CAPTURE_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)


class CaptureStatus(Enum):
    PENDING = "pending"
    COLLECTING = "collecting"
    NORMALIZING = "normalizing"
    TEMPLATING = "templating"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class WorkflowExample:
    workflow_name: str
    steps: list[dict]
    execution_time: float
    success: bool
    captured_at: float = field(default_factory=time.time)


@dataclass
class CaptureRecord:
    id: str
    workflow_name: str
    description: str
    examples: list[WorkflowExample]
    status: CaptureStatus
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    skill_name: Optional[str] = None
    skill_content: Optional[str] = None
    validation_result: Optional[dict] = None


class SkillCapture:
    def __init__(self):
        self.capture_queue: list[CaptureRecord] = []
        self.completed_captures: list[CaptureRecord] = []
        self._load_history()

    def _load_history(self):
        """加载历史记录"""
        if CAPTURE_HISTORY_FILE.exists():
            try:
                with open(CAPTURE_HISTORY_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.completed_captures = [self._dict_to_record(r) for r in data]
            except (json.JSONDecodeError, KeyError):
                self.completed_captures = []
        else:
            self.completed_captures = []

    def _save_history(self):
        """保存历史记录"""
        data = [self._record_to_dict(r) for r in self.completed_captures]
        with open(CAPTURE_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _record_to_dict(self, record: CaptureRecord) -> dict:
        return {
            "id": record.id,
            "workflow_name": record.workflow_name,
            "description": record.description,
            "examples": [
                {
                    "workflow_name": e.workflow_name,
                    "steps": e.steps,
                    "execution_time": e.execution_time,
                    "success": e.success,
                    "captured_at": e.captured_at,
                }
                for e in record.examples
            ],
            "status": record.status.value,
            "created_at": record.created_at,
            "completed_at": record.completed_at,
            "skill_name": record.skill_name,
            "skill_content": record.skill_content,
            "validation_result": record.validation_result,
        }

    def _dict_to_record(self, d: dict) -> CaptureRecord:
        examples = [
            WorkflowExample(
                workflow_name=e["workflow_name"],
                steps=e["steps"],
                execution_time=e["execution_time"],
                success=e["success"],
                captured_at=e.get("captured_at", time.time()),
            )
            for e in d.get("examples", [])
        ]
        return CaptureRecord(
            id=d["id"],
            workflow_name=d["workflow_name"],
            description=d.get("description", ""),
            examples=examples,
            status=CaptureStatus(d["status"]),
            created_at=d.get("created_at", time.time()),
            completed_at=d.get("completed_at"),
            skill_name=d.get("skill_name"),
            skill_content=d.get("skill_content"),
            validation_result=d.get("validation_result"),
        )

    def create_capture(
        self,
        workflow_name: str,
        description: str = "",
    ) -> CaptureRecord:
        """创建捕获任务"""
        record = CaptureRecord(
            id=f"capture-{int(time.time())}-{workflow_name[:8]}",
            workflow_name=workflow_name,
            description=description,
            examples=[],
            status=CaptureStatus.PENDING,
        )
        self.capture_queue.append(record)
        return record

    def add_example(
        self,
        capture_id: str,
        steps: list[dict],
        execution_time: float,
        success: bool = True,
    ) -> bool:
        """添加工 workflow 示例"""
        for record in self.capture_queue:
            if record.id == capture_id:
                example = WorkflowExample(
                    workflow_name=record.workflow_name,
                    steps=steps,
                    execution_time=execution_time,
                    success=success,
                )
                record.examples.append(example)
                record.status = CaptureStatus.COLLECTING
                return True
        return False

    def normalize_workflow(self, capture_id: str) -> dict:
        """规范化工作流"""
        for record in self.capture_queue:
            if record.id == capture_id:
                record.status = CaptureStatus.NORMALIZING

                successful_examples = [e for e in record.examples if e.success]
                if not successful_examples:
                    return {"error": "No successful examples to normalize"}

                common_steps = self._extract_common_steps(successful_examples)
                return {
                    "capture_id": capture_id,
                    "workflow_name": record.workflow_name,
                    "normalized_steps": common_steps,
                    "example_count": len(successful_examples),
                }
        return {"error": "Capture record not found"}

    def _extract_common_steps(self, examples: list[WorkflowExample]) -> list[dict]:
        """提取共同步骤"""
        if not examples:
            return []

        all_steps = []
        for example in examples:
            all_steps.extend(example.steps)

        step_counts = {}
        for step in all_steps:
            step_key = json.dumps(step, sort_keys=True)
            step_counts[step_key] = step_counts.get(step_key, 0) + 1

        min_count = len(examples) // 2
        common_steps = [
            json.loads(step_key)
            for step_key, count in step_counts.items()
            if count >= min_count
        ]

        return common_steps

    def generate_template(
        self,
        capture_id: str,
        skill_name: str,
    ) -> str:
        """生成 Skill 模板"""
        for record in self.capture_queue:
            if record.id == capture_id:
                record.status = CaptureStatus.TEMPLATING

                template = f"""# {skill_name}

## 功能描述
{record.description or 'Auto-captured workflow skill'}

## 使用方式
```bash
/{skill_name}
```

## 工作流程

"""
                for i, step in enumerate(record.examples[0].steps if record.examples else [], 1):
                    step_name = step.get("name", f"Step {i}")
                    step_desc = step.get("description", "")
                    template += f"### {i}. {step_name}\n"
                    if step_desc:
                        template += f"{step_desc}\n"

                template += f"""
## 验证标准
- 至少执行 {len(record.examples)} 次成功
- 平均执行时间: {sum(e.execution_time for e in record.examples) / len(record.examples):.2f}s

## 来源
自动捕获自 {record.workflow_name}
创建时间: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
                record.skill_name = skill_name
                record.skill_content = template
                return template
        return ""

    def save_skill(self, capture_id: str) -> bool:
        """保存 Skill"""
        for record in self.capture_queue:
            if record.id == capture_id:
                if not record.skill_content:
                    return False

                skill_path = Path(f"~/.claude/skills/{record.skill_name}").expanduser()
                skill_path.mkdir(parents=True, exist_ok=True)

                skill_file = skill_path / "SKILL.md"
                skill_file.write_text(record.skill_content, encoding="utf-8")

                scripts_path = skill_path / "scripts"
                scripts_path.mkdir(exist_ok=True)

                record.status = CaptureStatus.COMPLETED
                record.completed_at = time.time()
                self.capture_queue.remove(record)
                self.completed_captures.append(record)
                self._save_history()
                return True
        return False

    def validate_skill(self, capture_id: str, test_result: dict) -> bool:
        """验证 Skill"""
        for record in self.capture_queue:
            if record.id == capture_id:
                record.validation_result = test_result
                return test_result.get("passed", False)
        return False

    def get_queue(self) -> list[dict]:
        """获取捕获队列"""
        return [self._record_to_dict(r) for r in self.capture_queue]

    def get_history(self, limit: int = 50) -> list[dict]:
        """获取捕获历史"""
        records = self.completed_captures[-limit:]
        return [self._record_to_dict(r) for r in records]


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="OpenSpace Skill Capture")
    parser.add_argument("--create", action="store_true", help="创建捕获任务")
    parser.add_argument("--workflow", help="工作流名称")
    parser.add_argument("--description", help="描述")
    parser.add_argument("--add-example", help="添加示例")
    parser.add_argument("--normalize", help="规范化工作流")
    parser.add_argument("--template", help="生成模板")
    parser.add_argument("--skill-name", help="技能名称")
    parser.add_argument("--save", help="保存技能")
    parser.add_argument("--queue", action="store_true", help="查看捕获队列")
    parser.add_argument("--history", action="store_true", help="查看捕获历史")

    args = parser.parse_args()
    capturer = SkillCapture()

    if args.create and args.workflow:
        record = capturer.create_capture(args.workflow, args.description or "")
        print(json.dumps(capturer._record_to_dict(record), ensure_ascii=False, indent=2))
    elif args.normalize:
        result = capturer.normalize_workflow(args.normalize)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.template and args.skill_name:
        template = capturer.generate_template(args.template, args.skill_name)
        print(template)
    elif args.save:
        result = capturer.save_skill(args.save)
        print(json.dumps({"success": result}, ensure_ascii=False, indent=2))
    elif args.queue:
        print(json.dumps(capturer.get_queue(), ensure_ascii=False, indent=2))
    elif args.history:
        print(json.dumps(capturer.get_history(), ensure_ascii=False, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
