#!/usr/bin/env python3
"""
OpenSpace Metric Collector
指标收集器 - 追踪 Skills 的执行指标
"""

import json
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

METRICS_FILE = Path("~/.claude/memory/openspace-metrics.json").expanduser()
METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)


class MetricType(Enum):
    EXECUTION_COUNT = "execution_count"
    SUCCESS_RATE = "success_rate"
    AVG_DURATION = "avg_duration"
    CONFIDENCE_SCORE = "confidence_score"


@dataclass
class SkillMetric:
    skill_name: str
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    total_duration: float = 0.0
    last_execution_at: Optional[float] = None
    last_success_at: Optional[float] = None
    last_failure_at: Optional[float] = None
    confidence_score: float = 1.0
    baseline_duration: float = 0.0

    @property
    def success_rate(self) -> float:
        if self.execution_count == 0:
            return 0.0
        return self.success_count / self.execution_count

    @property
    def avg_duration(self) -> float:
        if self.execution_count == 0:
            return 0.0
        return self.total_duration / self.execution_count

    @property
    def is_baseline_set(self) -> bool:
        return self.baseline_duration > 0


@dataclass
class MetricSnapshot:
    skill_name: str
    timestamp: float
    execution_count: int
    success_rate: float
    avg_duration: float
    confidence_score: float


class MetricCollector:
    def __init__(self):
        self.metrics: dict[str, SkillMetric] = {}
        self.snapshots: list[MetricSnapshot] = []
        self._load_metrics()

    def _load_metrics(self):
        """加载指标数据"""
        if METRICS_FILE.exists():
            try:
                with open(METRICS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.metrics = {
                        name: self._dict_to_metric(m) for name, m in data.get("metrics", {}).items()
                    }
                    self.snapshots = [
                        self._dict_to_snapshot(s) for s in data.get("snapshots", [])
                    ]
            except (json.JSONDecodeError, KeyError):
                self.metrics = {}
                self.snapshots = []
        else:
            self.metrics = {}
            self.snapshots = []

    def _save_metrics(self):
        """保存指标数据"""
        data = {
            "metrics": {name: self._metric_to_dict(m) for name, m in self.metrics.items()},
            "snapshots": [self._snapshot_to_dict(s) for s in self.snapshots[-100:]],
        }
        with open(METRICS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _metric_to_dict(self, metric: SkillMetric) -> dict:
        return {
            "skill_name": metric.skill_name,
            "execution_count": metric.execution_count,
            "success_count": metric.success_count,
            "failure_count": metric.failure_count,
            "total_duration": metric.total_duration,
            "last_execution_at": metric.last_execution_at,
            "last_success_at": metric.last_success_at,
            "last_failure_at": metric.last_failure_at,
            "confidence_score": metric.confidence_score,
            "baseline_duration": metric.baseline_duration,
        }

    def _dict_to_metric(self, d: dict) -> SkillMetric:
        return SkillMetric(
            skill_name=d["skill_name"],
            execution_count=d.get("execution_count", 0),
            success_count=d.get("success_count", 0),
            failure_count=d.get("failure_count", 0),
            total_duration=d.get("total_duration", 0.0),
            last_execution_at=d.get("last_execution_at"),
            last_success_at=d.get("last_success_at"),
            last_failure_at=d.get("last_failure_at"),
            confidence_score=d.get("confidence_score", 1.0),
            baseline_duration=d.get("baseline_duration", 0.0),
        )

    def _snapshot_to_dict(self, snapshot: MetricSnapshot) -> dict:
        return {
            "skill_name": snapshot.skill_name,
            "timestamp": snapshot.timestamp,
            "execution_count": snapshot.execution_count,
            "success_rate": snapshot.success_rate,
            "avg_duration": snapshot.avg_duration,
            "confidence_score": snapshot.confidence_score,
        }

    def _dict_to_snapshot(self, d: dict) -> MetricSnapshot:
        return MetricSnapshot(
            skill_name=d["skill_name"],
            timestamp=d["timestamp"],
            execution_count=d["execution_count"],
            success_rate=d["success_rate"],
            avg_duration=d["avg_duration"],
            confidence_score=d["confidence_score"],
        )

    def record_execution(
        self,
        skill_name: str,
        success: bool,
        duration: float,
    ):
        """记录执行"""
        if skill_name not in self.metrics:
            self.metrics[skill_name] = SkillMetric(skill_name=skill_name)

        metric = self.metrics[skill_name]
        metric.execution_count += 1
        metric.total_duration += duration
        metric.last_execution_at = time.time()

        if success:
            metric.success_count += 1
            metric.last_success_at = time.time()
        else:
            metric.failure_count += 1
            metric.last_failure_at = time.time()

        self._update_confidence(metric)
        self._save_metrics()

    def _update_confidence(self, metric: SkillMetric):
        """更新置信度"""
        if metric.execution_count < 5:
            metric.confidence_score = 0.3
        elif metric.execution_count < 20:
            metric.confidence_score = 0.6
        elif metric.execution_count < 50:
            metric.confidence_score = 0.8
        else:
            base_confidence = min(0.95, 0.7 + (metric.success_rate * 0.25))
            metric.confidence_score = base_confidence

    def set_baseline(self, skill_name: str, baseline_duration: float):
        """设置性能基准"""
        if skill_name not in self.metrics:
            self.metrics[skill_name] = SkillMetric(skill_name=skill_name)
        self.metrics[skill_name].baseline_duration = baseline_duration
        self._save_metrics()

    def get_metric(self, skill_name: str) -> Optional[dict]:
        """获取单个技能指标"""
        if skill_name not in self.metrics:
            return None
        metric = self.metrics[skill_name]
        return {
            "skill_name": metric.skill_name,
            "execution_count": metric.execution_count,
            "success_count": metric.success_count,
            "failure_count": metric.failure_count,
            "success_rate": metric.success_rate,
            "avg_duration": metric.avg_duration,
            "total_duration": metric.total_duration,
            "confidence_score": metric.confidence_score,
            "baseline_duration": metric.baseline_duration,
            "last_execution_at": metric.last_execution_at,
            "last_success_at": metric.last_success_at,
            "last_failure_at": metric.last_failure_at,
            "is_baseline_set": metric.is_baseline_set,
        }

    def get_all_metrics(self) -> list[dict]:
        """获取所有指标"""
        return [self.get_metric(name) for name in self.metrics.keys()]

    def get_snapshot_history(
        self,
        skill_name: str,
        limit: int = 50,
    ) -> list[dict]:
        """获取指标历史快照"""
        snapshots = [
            s for s in self.snapshots
            if s.skill_name == skill_name
        ][-limit:]
        return [self._snapshot_to_dict(s) for s in snapshots]

    def create_snapshot(self, skill_name: str) -> Optional[MetricSnapshot]:
        """创建指标快照"""
        if skill_name not in self.metrics:
            return None
        metric = self.metrics[skill_name]
        snapshot = MetricSnapshot(
            skill_name=skill_name,
            timestamp=time.time(),
            execution_count=metric.execution_count,
            success_rate=metric.success_rate,
            avg_duration=metric.avg_duration,
            confidence_score=metric.confidence_score,
        )
        self.snapshots.append(snapshot)
        self._save_metrics()
        return snapshot

    def reset_metric(self, skill_name: str) -> bool:
        """重置指标"""
        if skill_name in self.metrics:
            del self.metrics[skill_name]
            self._save_metrics()
            return True
        return False


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="OpenSpace Metric Collector")
    parser.add_argument("--record", action="store_true", help="记录执行")
    parser.add_argument("--skill", help="技能名称")
    parser.add_argument("--success", type=lambda x: x.lower() == "true", default=True, help="是否成功")
    parser.add_argument("--duration", type=float, default=0.0, help="执行耗时(秒)")
    parser.add_argument("--get", help="获取技能指标")
    parser.add_argument("--all", action="store_true", help="获取所有指标")
    parser.add_argument("--set-baseline", help="设置性能基准")
    parser.add_argument("--baseline-duration", type=float, help="基准耗时")
    parser.add_argument("--reset", help="重置指标")

    args = parser.parse_args()
    collector = MetricCollector()

    if args.record and args.skill:
        collector.record_execution(args.skill, args.success, args.duration)
        print(json.dumps({"success": True, "skill": args.skill}, ensure_ascii=False, indent=2))
    elif args.get:
        metric = collector.get_metric(args.get)
        if metric:
            print(json.dumps(metric, ensure_ascii=False, indent=2))
        else:
            print(json.dumps({"error": f"No metric found for '{args.get}'"}, ensure_ascii=False, indent=2))
    elif args.all:
        print(json.dumps(collector.get_all_metrics(), ensure_ascii=False, indent=2))
    elif args.set_baseline and args.baseline_duration is not None:
        collector.set_baseline(args.set_baseline, args.baseline_duration)
        print(json.dumps({"success": True}, ensure_ascii=False, indent=2))
    elif args.reset:
        result = collector.reset_metric(args.reset)
        print(json.dumps({"success": result}, ensure_ascii=False, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
