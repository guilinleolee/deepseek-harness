#!/usr/bin/env python3
"""
OpenSpace Tool Degradation Detector
工具降级检测器 - 检测工具性能退化并触发自适应调整
"""

import json
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

DEGRADATION_FILE = Path("~/.claude/memory/openspace-degradation.json").expanduser()
DEGRADATION_FILE.parent.mkdir(parents=True, exist_ok=True)


class DegradationStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    RECOVERING = "recovering"


class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class DegradationThreshold:
    response_time_warning: float = 1.5   # 基准的 1.5 倍
    response_time_critical: float = 2.0   # 基准的 2.0 倍
    error_rate_warning: float = 0.05      # 5% 错误率
    error_rate_critical: float = 0.10     # 10% 错误率
    success_rate_warning: float = 0.90    # 90% 成功率
    success_rate_critical: float = 0.80  # 80% 成功率
    window_size: int = 20                  # 评估窗口大小


@dataclass
class ToolHealth:
    tool_name: str
    status: DegradationStatus
    baseline_response_time: float = 0.0
    baseline_success_rate: float = 1.0
    current_response_time: float = 0.0
    current_error_rate: float = 0.0
    current_success_rate: float = 1.0
    recent_executions: list = field(default_factory=list)
    last_check_at: float = field(default_factory=time.time)
    degradation_score: float = 0.0
    consecutive_failures: int = 0
    cooldown_until: Optional[float] = None


@dataclass
class DegradationAlert:
    id: str
    tool_name: str
    level: AlertLevel
    message: str
    created_at: float = field(default_factory=time.time)
    acknowledged: bool = False
    acknowledged_at: Optional[float] = None


@dataclass
class ExecutionRecord:
    timestamp: float
    success: bool
    duration: float
    error_type: Optional[str] = None


class ToolDegradationDetector:
    def __init__(self, threshold: Optional[DegradationThreshold] = None):
        self.threshold = threshold or DegradationThreshold()
        self.tool_health: dict[str, ToolHealth] = {}
        self.alerts: list[DegradationAlert] = []
        self._load_data()

    def _load_data(self):
        """加载数据"""
        if DEGRADATION_FILE.exists():
            try:
                with open(DEGRADATION_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.tool_health = {
                        name: self._dict_to_health(h) for name, h in data.get("health", {}).items()
                    }
                    self.alerts = [self._dict_to_alert(a) for a in data.get("alerts", [])]
            except (json.JSONDecodeError, KeyError):
                self.tool_health = {}
                self.alerts = []
        else:
            self.tool_health = {}
            self.alerts = []

    def _save_data(self):
        """保存数据"""
        data = {
            "health": {name: self._health_to_dict(h) for name, h in self.tool_health.items()},
            "alerts": [self._alert_to_dict(a) for a in self.alerts[-50:]],
        }
        with open(DEGRADATION_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _health_to_dict(self, health: ToolHealth) -> dict:
        return {
            "tool_name": health.tool_name,
            "status": health.status.value,
            "baseline_response_time": health.baseline_response_time,
            "baseline_success_rate": health.baseline_success_rate,
            "current_response_time": health.current_response_time,
            "current_error_rate": health.current_error_rate,
            "current_success_rate": health.current_success_rate,
            "recent_executions": [
                {"timestamp": e.timestamp, "success": e.success, "duration": e.duration}
                for e in health.recent_executions
            ],
            "last_check_at": health.last_check_at,
            "degradation_score": health.degradation_score,
            "consecutive_failures": health.consecutive_failures,
            "cooldown_until": health.cooldown_until,
        }

    def _dict_to_health(self, d: dict) -> ToolHealth:
        executions = [
            ExecutionRecord(
                timestamp=e["timestamp"],
                success=e["success"],
                duration=e["duration"],
            )
            for e in d.get("recent_executions", [])
        ]
        return ToolHealth(
            tool_name=d["tool_name"],
            status=DegradationStatus(d["status"]),
            baseline_response_time=d.get("baseline_response_time", 0.0),
            baseline_success_rate=d.get("baseline_success_rate", 1.0),
            current_response_time=d.get("current_response_time", 0.0),
            current_error_rate=d.get("current_error_rate", 0.0),
            current_success_rate=d.get("current_success_rate", 1.0),
            recent_executions=executions,
            last_check_at=d.get("last_check_at", time.time()),
            degradation_score=d.get("degradation_score", 0.0),
            consecutive_failures=d.get("consecutive_failures", 0),
            cooldown_until=d.get("cooldown_until"),
        )

    def _alert_to_dict(self, alert: DegradationAlert) -> dict:
        return {
            "id": alert.id,
            "tool_name": alert.tool_name,
            "level": alert.level.value,
            "message": alert.message,
            "created_at": alert.created_at,
            "acknowledged": alert.acknowledged,
            "acknowledged_at": alert.acknowledged_at,
        }

    def _dict_to_alert(self, d: dict) -> DegradationAlert:
        return DegradationAlert(
            id=d["id"],
            tool_name=d["tool_name"],
            level=AlertLevel(d["level"]),
            message=d["message"],
            created_at=d.get("created_at", time.time()),
            acknowledged=d.get("acknowledged", False),
            acknowledged_at=d.get("acknowledged_at"),
        )

    def register_tool(
        self,
        tool_name: str,
        baseline_response_time: float = 0.0,
        baseline_success_rate: float = 1.0,
    ):
        """注册工具"""
        if tool_name not in self.tool_health:
            self.tool_health[tool_name] = ToolHealth(
                tool_name=tool_name,
                status=DegradationStatus.HEALTHY,
                baseline_response_time=baseline_response_time,
                baseline_success_rate=baseline_success_rate,
            )
            self._save_data()

    def record_execution(
        self,
        tool_name: str,
        success: bool,
        duration: float,
        error_type: Optional[str] = None,
    ):
        """记录工具执行"""
        if tool_name not in self.tool_health:
            self.register_tool(tool_name)

        health = self.tool_health[tool_name]
        record = ExecutionRecord(
            timestamp=time.time(),
            success=success,
            duration=duration,
            error_type=error_type,
        )
        health.recent_executions.append(record)

        window_size = self.threshold.window_size
        if len(health.recent_executions) > window_size:
            health.recent_executions = health.recent_executions[-window_size:]

        self._update_health_metrics(tool_name)
        self._check_degradation(tool_name)
        self._save_data()

    def _update_health_metrics(self, tool_name: str):
        """更新健康指标"""
        health = self.tool_health[tool_name]
        executions = health.recent_executions

        if not executions:
            return

        total_duration = sum(e.duration for e in executions)
        success_count = sum(1 for e in executions if e.success)
        error_count = len(executions) - success_count

        health.current_response_time = total_duration / len(executions)
        health.current_error_rate = error_count / len(executions)
        health.current_success_rate = success_count / len(executions)
        health.last_check_at = time.time()

        consecutive = 0
        for e in reversed(executions):
            if not e.success:
                consecutive += 1
            else:
                break
        health.consecutive_failures = consecutive

    def _check_degradation(self, tool_name: str):
        """检查降级状态"""
        health = self.tool_health[tool_name]

        if health.cooldown_until and time.time() < health.cooldown_until:
            return

        response_time_ratio = (
            health.current_response_time / health.baseline_response_time
            if health.baseline_response_time > 0
            else 1.0
        )

        degradation_score = 0.0
        new_status = DegradationStatus.HEALTHY

        if health.current_error_rate >= self.threshold.error_rate_critical:
            degradation_score = 1.0
            new_status = DegradationStatus.CRITICAL
        elif health.current_error_rate >= self.threshold.error_rate_warning:
            degradation_score = 0.7
            new_status = DegradationStatus.DEGRADED
        elif response_time_ratio >= self.threshold.response_time_critical:
            degradation_score = 0.8
            new_status = DegradationStatus.CRITICAL
        elif response_time_ratio >= self.threshold.response_time_warning:
            degradation_score = 0.5
            new_status = DegradationStatus.WARNING
        elif health.current_success_rate < self.threshold.success_rate_critical:
            degradation_score = 0.9
            new_status = DegradationStatus.CRITICAL
        elif health.current_success_rate < self.threshold.success_rate_warning:
            degradation_score = 0.4
            new_status = DegradationStatus.WARNING

        if health.consecutive_failures >= 3:
            degradation_score = max(degradation_score, 0.8)
            if new_status == DegradationStatus.HEALTHY:
                new_status = DegradationStatus.WARNING

        if degradation_score > health.degradation_score:
            health.degradation_score = degradation_score
            health.status = new_status
            if degradation_score >= 0.7:
                self._create_alert(
                    tool_name,
                    AlertLevel.CRITICAL if degradation_score >= 0.9 else AlertLevel.WARNING,
                    f"工具 {tool_name} 检测到性能降级 (score: {degradation_score:.2f})",
                )
        elif degradation_score < health.degradation_score - 0.1:
            if health.status != DegradationStatus.HEALTHY:
                health.status = DegradationStatus.RECOVERING
                self._create_alert(
                    tool_name,
                    AlertLevel.INFO,
                    f"工具 {tool_name} 正在恢复 (score: {degradation_score:.2f})",
                )

    def _create_alert(self, tool_name: str, level: AlertLevel, message: str):
        """创建告警"""
        alert = DegradationAlert(
            id=f"alert-{int(time.time())}-{tool_name[:8]}",
            tool_name=tool_name,
            level=level,
            message=message,
        )
        self.alerts.append(alert)

    def acknowledge_alert(self, alert_id: str) -> bool:
        """确认告警"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                alert.acknowledged_at = time.time()
                self._save_data()
                return True
        return False

    def get_tool_health(self, tool_name: str) -> Optional[dict]:
        """获取工具健康状态"""
        if tool_name not in self.tool_health:
            return None
        health = self.tool_health[tool_name]
        return {
            "tool_name": health.tool_name,
            "status": health.status.value,
            "baseline_response_time": health.baseline_response_time,
            "current_response_time": health.current_response_time,
            "baseline_success_rate": health.baseline_success_rate,
            "current_success_rate": health.current_success_rate,
            "current_error_rate": health.current_error_rate,
            "degradation_score": health.degradation_score,
            "consecutive_failures": health.consecutive_failures,
            "recent_execution_count": len(health.recent_executions),
            "last_check_at": health.last_check_at,
        }

    def get_degraded_tools(self) -> list[dict]:
        """获取降级工具列表"""
        degraded = [
            self.get_tool_health(name)
            for name, health in self.tool_health.items()
            if health.status != DegradationStatus.HEALTHY
        ]
        return degraded

    def get_alerts(self, unacknowledged_only: bool = False) -> list[dict]:
        """获取告警列表"""
        alerts = self.alerts
        if unacknowledged_only:
            alerts = [a for a in alerts if not a.acknowledged]
        return [self._alert_to_dict(a) for a in alerts[-20:]]

    def set_cooldown(self, tool_name: str, minutes: int = 5):
        """设置冷却期"""
        if tool_name in self.tool_health:
            self.tool_health[tool_name].cooldown_until = time.time() + (minutes * 60)
            self._save_data()


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="OpenSpace Tool Degradation Detector")
    parser.add_argument("--register", help="注册工具")
    parser.add_argument("--baseline-time", type=float, help="基准响应时间")
    parser.add_argument("--baseline-success", type=float, help="基准成功率")
    parser.add_argument("--record", action="store_true", help="记录执行")
    parser.add_argument("--tool", help="工具名称")
    parser.add_argument("--success", type=lambda x: x.lower() == "true", default=True, help="是否成功")
    parser.add_argument("--duration", type=float, help="执行耗时")
    parser.add_argument("--error-type", help="错误类型")
    parser.add_argument("--status", help="查看工具状态")
    parser.add_argument("--degraded", action="store_true", help="查看降级工具")
    parser.add_argument("--alerts", action="store_true", help="查看告警")
    parser.add_argument("--acknowledge", help="确认告警")

    args = parser.parse_args()
    detector = ToolDegradationDetector()

    if args.register:
        detector.register_tool(
            args.register,
            args.baseline_time or 1.0,
            args.baseline_success or 1.0,
        )
        print(json.dumps({"success": True}, ensure_ascii=False, indent=2))
    elif args.record and args.tool:
        detector.record_execution(
            args.tool,
            args.success,
            args.duration or 0.0,
            args.error_type,
        )
        print(json.dumps({"success": True, "tool": args.tool}, ensure_ascii=False, indent=2))
    elif args.status:
        status = detector.get_tool_health(args.status)
        if status:
            print(json.dumps(status, ensure_ascii=False, indent=2))
        else:
            print(json.dumps({"error": "Tool not found"}, ensure_ascii=False, indent=2))
    elif args.degraded:
        print(json.dumps(detector.get_degraded_tools(), ensure_ascii=False, indent=2))
    elif args.alerts:
        print(json.dumps(detector.get_alerts(), ensure_ascii=False, indent=2))
    elif args.acknowledge:
        result = detector.acknowledge_alert(args.acknowledge)
        print(json.dumps({"success": result}, ensure_ascii=False, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
