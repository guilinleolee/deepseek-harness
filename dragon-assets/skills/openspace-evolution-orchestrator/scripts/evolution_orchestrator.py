#!/usr/bin/env python3
"""
OpenSpace Evolution Orchestrator
天龙引擎自演化编排核心 - 协调 165 个自演化 Skills 的 FIX/DERIVED/CAPTURED 模式
"""

import json
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

HISTORY_FILE = Path("~/.claude/memory/openspace-evolution-history.json").expanduser()
HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)


class EvolutionMode(Enum):
    FIX = "fix"           # 修复缺陷模式
    DERIVED = "derived"    # 派生新技能模式
    CAPTURED = "captured"  # 捕获工作流模式


class EvolutionStatus(Enum):
    PENDING = "pending"
    CONFIRMING = "confirming"
    EXECUTING = "executing"
    COMPLETED = "completed"
    ABORTED = "aborted"
    FAILED = "failed"


@dataclass
class EvolutionSignal:
    mode: EvolutionMode
    target: str
    trigger_reason: str
    confidence: float
    attempts: int = 0


@dataclass
class EvolutionRecord:
    id: str
    mode: EvolutionMode
    target: str
    status: EvolutionStatus
    trigger_reason: str
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    result: Optional[dict] = None
    anti_loop_passed: bool = False
    confirmation_approved: bool = False


class EvolutionOrchestrator:
    def __init__(self):
        self.evolution_queue: list[EvolutionSignal] = []
        self.current_evolution: Optional[EvolutionRecord] = None
        self.history: list[EvolutionRecord] = []
        self._load_history()

    def _load_history(self):
        """加载演化历史"""
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.history = [self._dict_to_record(r) for r in data]
            except (json.JSONDecodeError, KeyError):
                self.history = []

    def _save_history(self):
        """保存演化历史"""
        data = [self._record_to_dict(r) for r in self.history]
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _record_to_dict(self, record: EvolutionRecord) -> dict:
        return {
            "id": record.id,
            "mode": record.mode.value,
            "target": record.target,
            "status": record.status.value,
            "trigger_reason": record.trigger_reason,
            "created_at": record.created_at,
            "completed_at": record.completed_at,
            "result": record.result,
            "anti_loop_passed": record.anti_loop_passed,
            "confirmation_approved": record.confirmation_approved,
        }

    def _dict_to_record(self, d: dict) -> EvolutionRecord:
        return EvolutionRecord(
            id=d["id"],
            mode=EvolutionMode(d["mode"]),
            target=d["target"],
            status=EvolutionStatus(d["status"]),
            trigger_reason=d["trigger_reason"],
            created_at=d.get("created_at", time.time()),
            completed_at=d.get("completed_at"),
            result=d.get("result"),
            anti_loop_passed=d.get("anti_loop_passed", False),
            confirmation_approved=d.get("confirmation_approved", False),
        )

    def detect_signal(self, mode: EvolutionMode, target: str, reason: str, confidence: float) -> EvolutionSignal:
        """检测演化信号"""
        signal = EvolutionSignal(
            mode=mode,
            target=target,
            trigger_reason=reason,
            confidence=confidence
        )
        self.evolution_queue.append(signal)
        return signal

    def process_queue(self) -> Optional[EvolutionRecord]:
        """处理演化队列"""
        if not self.evolution_queue:
            return None

        signal = self.evolution_queue.pop(0)
        record = EvolutionRecord(
            id=f"evo-{int(time.time())}-{signal.target[:8]}",
            mode=signal.mode,
            target=signal.target,
            status=EvolutionStatus.PENDING,
            trigger_reason=signal.trigger_reason,
        )
        self.current_evolution = record
        return record

    def get_status(self) -> dict:
        """获取当前状态"""
        return {
            "queue_length": len(self.evolution_queue),
            "current": self._record_to_dict(self.current_evolution) if self.current_evolution else None,
            "history_count": len(self.history),
            "recent_evolutions": [self._record_to_dict(r) for r in self.history[-5:]],
        }

    def get_history(self, limit: int = 50) -> list[dict]:
        """获取演化历史"""
        records = self.history[-limit:]
        return [self._record_to_dict(r) for r in records]


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="OpenSpace Evolution Orchestrator")
    parser.add_argument("--status", action="store_true", help="查看当前状态")
    parser.add_argument("--history", action="store_true", help="查看演化历史")
    parser.add_argument("--mode", choices=["fix", "derived", "captured"], help="指定演化模式")
    parser.add_argument("--target", help="目标技能或模式")
    parser.add_argument("--reason", default="Manual trigger", help="触发原因")

    args = parser.parse_args()
    orchestrator = EvolutionOrchestrator()

    if args.status:
        status = orchestrator.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
    elif args.history:
        history = orchestrator.get_history()
        print(json.dumps(history, ensure_ascii=False, indent=2))
    elif args.mode and args.target:
        mode = EvolutionMode(args.mode)
        signal = orchestrator.detect_signal(mode, args.target, args.reason, 0.9)
        record = orchestrator.process_queue()
        if record:
            print(json.dumps(orchestrator._record_to_dict(record), ensure_ascii=False, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
