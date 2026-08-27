"""
QualityRatchet - 棘轮机制
确保质量只升不降，自动选择最优版本
来源: https://github.com/mmlong818/Cat-Research
集成时间: 2026-03-23
"""
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict


@dataclass
class VersionRecord:
    """版本记录"""
    version: str
    score: float
    accepted: bool
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


class QualityRatchet:
    """
    棘轮机制 - 质量只升不降

    核心原理：
    - 像棘轮一样，只允许向前转动，不允许后退
    - 每次提交新版本时，只有分数更高才会被接受
    - 自动追踪历史，保留最优版本

    使用示例:
        ratchet = QualityRatchet(target_score=80)
        ratchet.submit("v1", 60)  # True - 接受
        ratchet.submit("v2", 55)  # False - 拒绝（质量下降）
        ratchet.submit("v3", 75)  # True - 接受
        print(ratchet.best_version)  # "v3"
        print(ratchet.best_score)    # 75
    """

    def __init__(
        self,
        target_score: float = 80.0,
        min_score: float = 60.0,
        max_attempts: int = 5,
        tolerance: float = 0.02
    ):
        """
        初始化棘轮

        Args:
            target_score: 目标分数
            min_score: 最低可接受分数
            max_attempts: 最大尝试次数
            tolerance: 降分容忍度（百分比）
        """
        self.target_score = target_score
        self.min_score = min_score
        self.max_attempts = max_attempts
        self.tolerance = tolerance

        self._best_version: Optional[str] = None
        self._best_score: float = 0.0
        self._history: List[VersionRecord] = []
        self._attempts: int = 0

    def submit(self, version: str, score: float, metadata: Dict = None) -> bool:
        """
        提交新版本

        Args:
            version: 版本标识
            score: 质量分数
            metadata: 额外元数据

        Returns:
            bool: 是否接受新版本
        """
        self._attempts += 1

        # 检查最低分数门槛
        if score < self.min_score:
            self._history.append(VersionRecord(
                version=version,
                score=score,
                accepted=False,
                metadata=metadata or {}
            ))
            return False

        # 棘轮机制：只有分数更高才接受（允许容忍度）
        effective_best = self._best_score * (1 - self.tolerance)

        if score > effective_best:
            self._best_version = version
            self._best_score = score
            self._history.append(VersionRecord(
                version=version,
                score=score,
                accepted=True,
                metadata=metadata or {}
            ))
            return True
        else:
            self._history.append(VersionRecord(
                version=version,
                score=score,
                accepted=False,
                metadata=metadata or {}
            ))
            return False

    @property
    def best_version(self) -> Optional[str]:
        """获取最优版本"""
        return self._best_version

    @property
    def best_score(self) -> float:
        """获取最优分数"""
        return self._best_score

    @property
    def attempts(self) -> int:
        """获取尝试次数"""
        return self._attempts

    def is_target_reached(self) -> bool:
        """检查是否达到目标分数"""
        return self._best_score >= self.target_score

    def can_continue(self) -> bool:
        """检查是否可以继续尝试"""
        return self._attempts < self.max_attempts and not self.is_target_reached()

    def get_history(self) -> List[Dict]:
        """获取完整历史"""
        return [asdict(record) for record in self._history]

    def get_best_version(self) -> Optional[Dict]:
        """获取最优版本详情"""
        if not self._best_version:
            return None
        for record in self._history:
            if record.version == self._best_version and record.accepted:
                return asdict(record)
        return None

    def get_stats(self) -> Dict:
        """获取统计信息"""
        accepted = [r for r in self._history if r.accepted]
        rejected = [r for r in self._history if not r.accepted]

        return {
            "total_attempts": self._attempts,
            "accepted_count": len(accepted),
            "rejected_count": len(rejected),
            "best_version": self._best_version,
            "best_score": self._best_score,
            "target_score": self.target_score,
            "target_reached": self.is_target_reached(),
            "can_continue": self.can_continue()
        }

    def save(self, filepath: str):
        """保存状态到文件"""
        data = {
            "config": {
                "target_score": self.target_score,
                "min_score": self.min_score,
                "max_attempts": self.max_attempts,
                "tolerance": self.tolerance
            },
            "state": {
                "best_version": self._best_version,
                "best_score": self._best_score,
                "attempts": self._attempts
            },
            "history": self.get_history()
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, filepath: str) -> 'QualityRatchet':
        """从文件加载状态"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        ratchet = cls(
            target_score=data["config"]["target_score"],
            min_score=data["config"]["min_score"],
            max_attempts=data["config"]["max_attempts"],
            tolerance=data["config"]["tolerance"]
        )
        ratchet._best_version = data["state"]["best_version"]
        ratchet._best_score = data["state"]["best_score"]
        ratchet._attempts = data["state"]["attempts"]
        ratchet._history = [VersionRecord(**r) for r in data["history"]]

        return ratchet

    def reset(self):
        """重置棘轮状态"""
        self._best_version = None
        self._best_score = 0.0
        self._history = []
        self._attempts = 0


# ── CLI 入口 ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    # Windows GBK 兼容
    if hasattr(sys.stdout, 'buffer'):
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "demo":
            # 演示棘轮机制
            ratchet = QualityRatchet(target_score=80)
            print("[Ratchet] Quality Ratchet Demo")
            print(f"Target score: {ratchet.target_score}")
            print()

            versions = [
                ("v1", 60),
                ("v2", 55),  # 下降，应被拒绝
                ("v3", 75),
                ("v4", 72),  # 下降，应被拒绝
                ("v5", 82),
            ]

            for version, score in versions:
                accepted = ratchet.submit(version, score)
                status = "[OK] Accepted" if accepted else "[X] Rejected"
                print(f"Submit {version} (score={score}): {status} | best={ratchet.best_score}")

            print()
            print(f"[Stats] Final result:")
            print(f"   Best version: {ratchet.best_version}")
            print(f"   Best score: {ratchet.best_score}")
            print(f"   Target reached: {'Yes' if ratchet.is_target_reached() else 'No'}")

        elif command == "stats":
            print(json.dumps({
                "total_attempts": 0,
                "accepted_count": 0,
                "rejected_count": 0,
                "best_version": None,
                "best_score": 0,
                "target_score": 80,
                "target_reached": False,
                "can_continue": True
            }, ensure_ascii=False, indent=2))

        else:
            print("Usage: python ratchet.py [demo|stats]")
    else:
        print("QualityRatchet - 棘轮机制")
        print("Usage: python ratchet.py [demo|stats]")