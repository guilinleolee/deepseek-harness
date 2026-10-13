#!/usr/bin/env python3
"""
OpenSpace Anti-loop Guard
自演化防循环机制 - 防止在同一问题上无限演化
"""

import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

LOOP_HISTORY_FILE = Path("~/.claude/memory/openspace-loop-history.json").expanduser()
LOOP_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)


class LoopStatus(Enum):
    SAFE = "safe"
    WARNING = "warning"
    BLOCKED = "blocked"
    COOLDOWN = "cooldown"


@dataclass
class LoopAttempt:
    evolution_id: str
    target: str
    pattern_hash: str
    attempt_count: int
    last_attempt_at: float
    similarity_to_previous: float


@dataclass
class LoopGuardResult:
    allowed: bool
    status: LoopStatus
    reason: str
    attempts: int
    cooldown_until: Optional[float] = None


class AntiLoopGuard:
    def __init__(
        self,
        max_attempts: int = 5,
        similarity_threshold: float = 0.85,
        cooldown_hours: int = 24,
    ):
        self.max_attempts = max_attempts
        self.similarity_threshold = similarity_threshold
        self.cooldown_hours = cooldown_hours
        self.attempt_history: list[LoopAttempt] = []
        self._load_history()

    def _load_history(self):
        """加载历史记录"""
        if LOOP_HISTORY_FILE.exists():
            try:
                import json
                with open(LOOP_HISTORY_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.attempt_history = [self._dict_to_attempt(a) for a in data]
            except (json.JSONDecodeError, KeyError):
                self.attempt_history = []
        else:
            self.attempt_history = []

    def _save_history(self):
        """保存历史记录"""
        import json
        data = [self._attempt_to_dict(a) for a in self.attempt_history]
        with open(LOOP_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _attempt_to_dict(self, attempt: LoopAttempt) -> dict:
        return {
            "evolution_id": attempt.evolution_id,
            "target": attempt.target,
            "pattern_hash": attempt.pattern_hash,
            "attempt_count": attempt.attempt_count,
            "last_attempt_at": attempt.last_attempt_at,
            "similarity_to_previous": attempt.similarity_to_previous,
        }

    def _dict_to_attempt(self, d: dict) -> LoopAttempt:
        return LoopAttempt(
            evolution_id=d["evolution_id"],
            target=d["target"],
            pattern_hash=d["pattern_hash"],
            attempt_count=d["attempt_count"],
            last_attempt_at=d["last_attempt_at"],
            similarity_to_previous=d.get("similarity_to_previous", 0.0),
        )

    def _compute_pattern_hash(self, target: str, context: dict) -> str:
        """计算模式哈希"""
        pattern_str = f"{target}:{json.dumps(context, sort_keys=True)}"
        return hashlib.sha256(pattern_str.encode()).hexdigest()[:16]

    def _calculate_similarity(self, hash1: str, hash2: str) -> float:
        """计算两个哈希的相似度"""
        if hash1 == hash2:
            return 1.0
        matches = sum(c1 == c2 for c1, c2 in zip(hash1, hash2))
        return matches / len(hash1)

    def _is_in_cooldown(self, target: str) -> tuple[bool, Optional[float]]:
        """检查是否在冷却期"""
        now = time.time()
        for attempt in reversed(self.attempt_history):
            if attempt.target == target and attempt.attempt_count >= self.max_attempts:
                cooldown_end = attempt.last_attempt_at + (self.cooldown_hours * 3600)
                if now < cooldown_end:
                    return True, cooldown_end
        return False, None

    def check_and_record(
        self,
        evolution_id: str,
        target: str,
        context: dict = None,
    ) -> LoopGuardResult:
        """
        检查是否允许演化并记录尝试
        """
        context = context or {}
        pattern_hash = self._compute_pattern_hash(target, context)
        now = time.time()

        in_cooldown, cooldown_until = self._is_in_cooldown(target)
        if in_cooldown:
            remaining_hours = (cooldown_until - now) / 3600
            return LoopGuardResult(
                allowed=False,
                status=LoopStatus.COOLDOWN,
                reason=f"目标已进入冷却期，剩余 {remaining_hours:.1f} 小时",
                attempts=self.max_attempts,
                cooldown_until=cooldown_until,
            )

        similar_attempts = [
            a for a in self.attempt_history
            if a.target == target and self._calculate_similarity(a.pattern_hash, pattern_hash) >= self.similarity_threshold
        ]

        if similar_attempts:
            latest_attempt = max(similar_attempts, key=lambda a: a.attempt_count)
            similarity = self._calculate_similarity(latest_attempt.pattern_hash, pattern_hash)

            if latest_attempt.attempt_count >= self.max_attempts:
                new_attempt = LoopAttempt(
                    evolution_id=evolution_id,
                    target=target,
                    pattern_hash=pattern_hash,
                    attempt_count=latest_attempt.attempt_count + 1,
                    last_attempt_at=now,
                    similarity_to_previous=similarity,
                )
                self.attempt_history.append(new_attempt)
                self._save_history()

                return LoopGuardResult(
                    allowed=False,
                    status=LoopStatus.BLOCKED,
                    reason=f"检测到循环演化，已尝试 {latest_attempt.attempt_count} 次相同或相似的演化",
                    attempts=latest_attempt.attempt_count + 1,
                )

            if latest_attempt.attempt_count >= self.max_attempts - 2:
                new_attempt = LoopAttempt(
                    evolution_id=evolution_id,
                    target=target,
                    pattern_hash=pattern_hash,
                    attempt_count=latest_attempt.attempt_count + 1,
                    last_attempt_at=now,
                    similarity_to_previous=similarity,
                )
                self.attempt_history.append(new_attempt)
                self._save_history()

                return LoopGuardResult(
                    allowed=True,
                    status=LoopStatus.WARNING,
                    reason=f"接近演化次数上限（{latest_attempt.attempt_count + 1}/{self.max_attempts}），请注意",
                    attempts=latest_attempt.attempt_count + 1,
                )

        existing = [a for a in self.attempt_history if a.target == target]
        attempt_count = max((a.attempt_count for a in existing), default=0) + 1

        new_attempt = LoopAttempt(
            evolution_id=evolution_id,
            target=target,
            pattern_hash=pattern_hash,
            attempt_count=attempt_count,
            last_attempt_at=now,
            similarity_to_previous=0.0,
        )
        self.attempt_history.append(new_attempt)
        self._save_history()

        return LoopGuardResult(
            allowed=True,
            status=LoopStatus.SAFE,
            reason="演化检查通过",
            attempts=attempt_count,
        )

    def get_status(self, target: str = None) -> dict:
        """获取防循环状态"""
        if target:
            attempts = [a for a in self.attempt_history if a.target == target]
            if not attempts:
                return {"target": target, "status": "no_history", "attempts": 0}

            latest = max(attempts, key=lambda a: a.attempt_count)
            return {
                "target": target,
                "status": latest.status.value if hasattr(latest, 'status') else "unknown",
                "attempts": latest.attempt_count,
                "last_attempt_at": latest.last_attempt_at,
                "max_attempts": self.max_attempts,
            }

        return {
            "total_attempts": len(self.attempt_history),
            "unique_targets": len(set(a.target for a in self.attempt_history)),
            "blocked_count": sum(1 for a in self.attempt_history if a.attempt_count >= self.max_attempts),
        }

    def reset_target(self, target: str) -> bool:
        """重置目标的历史记录"""
        original_len = len(self.attempt_history)
        self.attempt_history = [a for a in self.attempt_history if a.target != target]
        self._save_history()
        return len(self.attempt_history) < original_len


def main():
    """命令行接口"""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="OpenSpace Anti-loop Guard")
    parser.add_argument("--check", help="检查目标")
    parser.add_argument("--status", help="查看目标状态")
    parser.add_argument("--reset", help="重置目标")
    parser.add_argument("--history", action="store_true", help="查看历史")
    parser.add_argument("--evolution-id", help="演化ID")

    args = parser.parse_args()
    guard = AntiLoopGuard()

    if args.check:
        result = guard.check_and_record(
            evolution_id=args.evolution_id or f"manual-{int(time.time())}",
            target=args.check,
        )
        print(json.dumps({
            "allowed": result.allowed,
            "status": result.status.value,
            "reason": result.reason,
            "attempts": result.attempts,
            "cooldown_until": result.cooldown_until,
        }, ensure_ascii=False, indent=2))
    elif args.status:
        print(json.dumps(guard.get_status(args.status), ensure_ascii=False, indent=2))
    elif args.reset:
        result = guard.reset_target(args.reset)
        print(json.dumps({"success": result}, ensure_ascii=False, indent=2))
    elif args.history:
        print(json.dumps([guard._attempt_to_dict(a) for a in guard.attempt_history[-20:]], ensure_ascii=False, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    import json
    main()
