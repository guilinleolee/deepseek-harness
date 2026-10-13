#!/usr/bin/env python3
"""
OpenSpace Confirmation Gate
自演化确认门控 - 确保每次演化都有明确目标和验证标准
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

CONFIRMATION_FILE = Path("~/.claude/memory/openspace-confirmations.json").expanduser()
CONFIRMATION_FILE.parent.mkdir(parents=True, exist_ok=True)


class GateStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass
class ConfirmationCriteria:
    goal: str                          # 演化目标
    expected_result: str                # 预期结果
    exit_conditions: list[str]         # 退出条件
    verification_metrics: list[str]    # 验证指标
    risk_assessment: str = "medium"    # 风险评估
    estimated_complexity: str = "medium"  # 预估复杂度


@dataclass
class ConfirmationRecord:
    id: str
    evolution_id: str
    criteria: ConfirmationCriteria
    status: GateStatus
    created_at: float = field(default_factory=time.time)
    decided_at: Optional[float] = None
    approver: str = "system"
    notes: str = ""


class ConfirmationGate:
    def __init__(self):
        self.pending_confirmations: list[ConfirmationRecord] = []
        self.completed_confirmations: list[ConfirmationRecord] = []
        self._load_confirmations()

    def _load_confirmations(self):
        """加载确认记录"""
        if CONFIRMATION_FILE.exists():
            try:
                import json
                with open(CONFIRMATION_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.completed_confirmations = [self._dict_to_record(r) for r in data]
            except (json.JSONDecodeError, KeyError):
                self.completed_confirmations = []
        else:
            self.completed_confirmations = []

    def _save_confirmations(self):
        """保存确认记录"""
        import json
        data = [self._record_to_dict(r) for r in self.completed_confirmations]
        with open(CONFIRMATION_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _record_to_dict(self, record: ConfirmationRecord) -> dict:
        return {
            "id": record.id,
            "evolution_id": record.evolution_id,
            "criteria": {
                "goal": record.criteria.goal,
                "expected_result": record.criteria.expected_result,
                "exit_conditions": record.criteria.exit_conditions,
                "verification_metrics": record.criteria.verification_metrics,
                "risk_assessment": record.criteria.risk_assessment,
                "estimated_complexity": record.criteria.estimated_complexity,
            },
            "status": record.status.value,
            "created_at": record.created_at,
            "decided_at": record.decided_at,
            "approver": record.approver,
            "notes": record.notes,
        }

    def _dict_to_record(self, d: dict) -> ConfirmationRecord:
        criteria_data = d["criteria"]
        criteria = ConfirmationCriteria(
            goal=criteria_data["goal"],
            expected_result=criteria_data["expected_result"],
            exit_conditions=criteria_data["exit_conditions"],
            verification_metrics=criteria_data["verification_metrics"],
            risk_assessment=criteria_data.get("risk_assessment", "medium"),
            estimated_complexity=criteria_data.get("estimated_complexity", "medium"),
        )
        return ConfirmationRecord(
            id=d["id"],
            evolution_id=d["evolution_id"],
            criteria=criteria,
            status=GateStatus(d["status"]),
            created_at=d.get("created_at", time.time()),
            decided_at=d.get("decided_at"),
            approver=d.get("approver", "system"),
            notes=d.get("notes", ""),
        )

    def create_confirmation(
        self,
        evolution_id: str,
        goal: str,
        expected_result: str,
        exit_conditions: list[str],
        verification_metrics: list[str],
        risk_assessment: str = "medium",
        estimated_complexity: str = "medium",
    ) -> ConfirmationRecord:
        """创建确认请求"""
        criteria = ConfirmationCriteria(
            goal=goal,
            expected_result=expected_result,
            exit_conditions=exit_conditions,
            verification_metrics=verification_metrics,
            risk_assessment=risk_assessment,
            estimated_complexity=estimated_complexity,
        )
        record = ConfirmationRecord(
            id=f"gate-{int(time.time())}-{evolution_id[:8]}",
            evolution_id=evolution_id,
            criteria=criteria,
            status=GateStatus.PENDING,
        )
        self.pending_confirmations.append(record)
        return record

    def approve(self, gate_id: str, approver: str = "user", notes: str = "") -> bool:
        """批准确认"""
        for record in self.pending_confirmations:
            if record.id == gate_id:
                record.status = GateStatus.APPROVED
                record.decided_at = time.time()
                record.approver = approver
                record.notes = notes
                self.pending_confirmations.remove(record)
                self.completed_confirmations.append(record)
                self._save_confirmations()
                return True
        return False

    def reject(self, gate_id: str, reason: str = "") -> bool:
        """拒绝确认"""
        for record in self.pending_confirmations:
            if record.id == gate_id:
                record.status = GateStatus.REJECTED
                record.decided_at = time.time()
                record.notes = reason
                self.pending_confirmations.remove(record)
                self.completed_confirmations.append(record)
                self._save_confirmations()
                return True
        return False

    def check_auto_approve(self, criteria: ConfirmationCriteria) -> bool:
        """检查是否自动批准（低风险简单任务）"""
        auto_approve_conditions = [
            criteria.risk_assessment == "low",
            criteria.estimated_complexity in ["low", "medium"],
            len(criteria.exit_conditions) > 0,
            len(criteria.verification_metrics) > 0,
        ]
        return all(auto_approve_conditions)

    def get_pending(self) -> list[dict]:
        """获取待确认列表"""
        return [self._record_to_dict(r) for r in self.pending_confirmations]

    def verify_exit_conditions(self, gate_id: str, actual_results: dict) -> bool:
        """验证退出条件"""
        for record in self.completed_confirmations:
            if record.id == gate_id:
                for condition in record.criteria.exit_conditions:
                    if not self._check_condition(condition, actual_results):
                        return False
                return True
        return False

    def _check_condition(self, condition: str, results: dict) -> bool:
        """检查单个条件"""
        if "成功" in condition:
            return results.get("success", False)
        if "指标" in condition:
            key = condition.split("指标")[0].strip()
            return results.get(key, 0) > 0
        return True


def main():
    """命令行接口"""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="OpenSpace Confirmation Gate")
    parser.add_argument("--create", action="store_true", help="创建确认请求")
    parser.add_argument("--pending", action="store_true", help="查看待确认列表")
    parser.add_argument("--approve", help="批准确认")
    parser.add_argument("--reject", help="拒绝确认")
    parser.add_argument("--evolution-id", help="演化ID")
    parser.add_argument("--goal", help="演化目标")
    parser.add_argument("--expected", help="预期结果")
    parser.add_argument("--exit-conditions", nargs="+", help="退出条件")
    parser.add_argument("--metrics", nargs="+", help="验证指标")
    parser.add_argument("--risk", default="medium", choices=["low", "medium", "high"], help="风险评估")

    args = parser.parse_args()
    gate = ConfirmationGate()

    if args.create and args.evolution_id and args.goal and args.expected:
        record = gate.create_confirmation(
            evolution_id=args.evolution_id,
            goal=args.goal,
            expected_result=args.expected,
            exit_conditions=args.exit_conditions or ["演化完成"],
            verification_metrics=args.metrics or ["成功率"],
            risk_assessment=args.risk,
        )
        print(json.dumps(gate._record_to_dict(record), ensure_ascii=False, indent=2))
    elif args.pending:
        print(json.dumps(gate.get_pending(), ensure_ascii=False, indent=2))
    elif args.approve:
        result = gate.approve(args.approve)
        print(json.dumps({"success": result}, ensure_ascii=False, indent=2))
    elif args.reject:
        result = gate.reject(args.reject)
        print(json.dumps({"success": result}, ensure_ascii=False, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
