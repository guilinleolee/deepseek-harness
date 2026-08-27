#!/usr/bin/env python3
"""
trigger-matrix-generator.py
触发矩阵生成器 - 基于 trigger-design-prompt.md 生成升级触发矩阵配置
天龙引擎 V9.02 | escalation-matrix 套件
"""

import argparse
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

try:
    from yaml import dump, Dumper
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


# ============================================================================
# 数据模型层
# ============================================================================

class Priority(Enum):
    P0 = "P0"  # 立即处理
    P1 = "P1"  # 5分钟内响应
    P2 = "P2"  # 10分钟内响应
    P3 = "P3"  # 30分钟内响应
    P4 = "P4"  # 记录观察


class Level(Enum):
    L1 = "L1"  # 执行层
    L2 = "L2"  # 编排层
    L3 = "L3"  # 治理层
    L4 = "L4"  # 决策层


class ConditionType(Enum):
    COUNT_EXCEED = "count_exceed"
    TIME_EXCEED = "time_exceed"
    STATUS_CHECK = "status_check"
    PATTERN_MATCH = "pattern_match"
    COMPOSITE = "composite"


@dataclass
class TriggerCondition:
    """触发条件定义"""
    id: str
    name: str
    description: str
    condition: dict
    priority: Priority
    target_level: Level
    sla: str
    actions: list[str] = field(default_factory=list)
    suppress_until: str = ""
    escalation_path: str = ""


@dataclass
class ErrorTrigger(TriggerCondition):
    """错误类型触发器"""
    patterns: list[str] = field(default_factory=list)
    severity: str = "medium"
    urgent_bypass: bool = False


@dataclass
class TimeoutTrigger(TriggerCondition):
    """超时触发器"""
    sla_value: str = ""
    hard_timeout: str = ""
    multiplier: float = 1.5


@dataclass
class ResourceTrigger(TriggerCondition):
    """资源触发器"""
    resource: str = ""
    threshold: float = 0.0
    single_action: str = ""
    two_action: str = ""
    all_action: str = ""


@dataclass
class ImpactTrigger(TriggerCondition):
    """影响范围触发器"""
    scope: str = ""
    users_affected: str = ""
    escalation_target: Level = Level.L2


@dataclass
class SuppressionRule:
    """触发抑制规则"""
    name: str
    description: str
    enabled: bool = True
    cooldown_window: str = "5分钟"
    same_error_only: bool = True
    same_context: bool = False
    parent_handling: bool = True
    batch_trigger_once: bool = True
    aggregate_window: str = "1分钟"
    critical_triggers: list[str] = field(default_factory=list)


@dataclass
class UrgentPath:
    """紧急升级路径"""
    trigger: str
    bypass_levels: list[str] = field(default_factory=list)
    target_level: Level
    reason: str
    parallel_notification: bool = True
    immediate_escalation: bool = True


@dataclass
class TriggerStatistics:
    """触发统计配置"""
    enabled: bool = True
    metrics: list[str] = field(default_factory=list)


# ============================================================================
# 触发器生成器
# ============================================================================

class TriggerGenerator:
    """触发器生成器基类"""

    def generate(self) -> list[TriggerCondition]:
        raise NotImplementedError


class L1TriggerGenerator(TriggerGenerator):
    """L1执行层触发器生成器"""

    def generate(self) -> list[TriggerCondition]:
        return [
            ErrorTrigger(
                id="retry_exceeded",
                name="重试超限",
                description="重试次数超过预设值",
                condition={"field": "retry_count", "operator": ">", "value": 3},
                priority=Priority.P3,
                target_level=Level.L2,
                sla="30秒",
                actions=["增加重试次数或切换方案"],
                escalation_path="L1重试3次 → L2",
                patterns=["ConnectionError", "TimeoutError", "HTTP 5xx"],
                severity="high",
            ),
            ErrorTrigger(
                id="time_exceeded",
                name="时间超限",
                description="执行时间超过SLA",
                condition={"field": "execution_time", "operator": ">", "value": "SLA"},
                priority=Priority.P3,
                target_level=Level.L2,
                sla="30秒",
                actions=["延长SLA或优化流程"],
                escalation_path="L1超时 → L2",
                patterns=["TimeoutError"],
                severity="medium",
                urgent_bypass=False,
            ),
            ErrorTrigger(
                id="error_blacklist",
                name="黑名单错误",
                description="遇到预设黑名单中的错误类型",
                condition={"field": "error_type", "operator": "in", "value": "${error_blacklist}"},
                priority=Priority.P2,
                target_level=Level.L2,
                sla="即时",
                actions=["执行预设修复方案"],
                escalation_path="L1 → L2",
                patterns=["SyntaxError", "ImportError", "ModuleNotFoundError"],
                severity="high",
                urgent_bypass=True,
            ),
            ErrorTrigger(
                id="unknown_error",
                name="未知错误",
                description="无法识别或归类的错误类型",
                condition={"field": "recognizable", "operator": "==", "value": False},
                priority=Priority.P4,
                target_level=Level.L2,
                sla="10分钟",
                actions=["记录日志并监控", "增加已知错误模式"],
                escalation_path="L1 → L2",
                patterns=["UnknownError"],
                severity="low",
                urgent_bypass=False,
            ),
            ResourceTrigger(
                id="resource_exhausted",
                name="资源耗尽",
                description="CPU/内存/磁盘等资源耗尽",
                condition={"field": "resource_usage", "operator": ">", "value": "100%"},
                priority=Priority.P2,
                target_level=Level.L2,
                sla="1分钟",
                actions=["扩容或清理资源"],
                escalation_path="L1 → L2",
                resource="cpu",
                threshold=0.9,
                single_action="scale_up",
                two_action="scale_up + optimize",
                all_action="degrade_non_critical",
            ),
            ImpactTrigger(
                id="impact_propagating",
                name="影响扩散",
                description="错误影响范围超出预期",
                condition={"field": "impact_level", "operator": ">", "value": "threshold"},
                priority=Priority.P1,
                target_level=Level.L3,
                sla="5分钟",
                actions=["通知相关方", "隔离影响范围"],
                escalation_path="L1 → L3",
                scope="team",
                users_affected="2-10",
            ),
        ]


class L2TriggerGenerator(TriggerGenerator):
    """L2编排层触发器生成器"""

    def generate(self) -> list[TriggerCondition]:
        return [
            TriggerCondition(
                id="coordination_failed",
                name="协调失败",
                description="多Agent协调无法达成一致",
                condition={"field": "attempts", "operator": ">", "value": 3},
                priority=Priority.P2,
                target_level=Level.L3,
                sla="10分钟",
                actions=["重新分配资源", "调整协调策略"],
                escalation_path="L2协调3次无效 → L3",
            ),
            TriggerCondition(
                id="dependency_unavailable",
                name="依赖不可用",
                description="外部依赖服务不可用",
                condition={"field": "status", "operator": "==", "value": "unavailable"},
                priority=Priority.P2,
                target_level=Level.L3,
                sla="10分钟",
                actions=["切换备用依赖", "降级处理"],
                escalation_path="L2 → L3",
            ),
            TriggerCondition(
                id="cross_system_impact",
                name="跨系统影响",
                description="故障影响超出单一系统范围",
                condition={"field": "systems_count", "operator": ">", "value": 1},
                priority=Priority.P1,
                target_level=Level.L3,
                sla="5分钟",
                actions=["并行通知多个团队", "协调跨系统修复"],
                escalation_path="L2 → L3",
            ),
            ResourceTrigger(
                id="resource_bottleneck",
                name="资源瓶颈",
                description="所有可用资源都达到上限",
                condition={"field": "all_resources_busy", "operator": "==", "value": True},
                priority=Priority.P2,
                target_level=Level.L3,
                sla="10分钟",
                actions=["扩容资源", "优化资源分配"],
                escalation_path="L2 → L3",
                resource="all",
                threshold=0.95,
            ),
            TriggerCondition(
                id="escalation_loop",
                name="升级循环",
                description="检测到L1↔L2循环升级",
                condition={"field": "loop_count", "operator": ">", "value": 3},
                priority=Priority.P0,
                target_level=Level.L3,
                sla="即时",
                actions=["强制指定处理者", "终止升级循环"],
                escalation_path="L2 → L3",
            ),
        ]


class L3TriggerGenerator(TriggerGenerator):
    """L3治理层触发器生成器"""

    def generate(self) -> list[TriggerCondition]:
        return [
            TriggerCondition(
                id="governance_ineffective",
                name="治理无效",
                description="治理措施执行后问题未解决",
                condition={"field": "attempts", "operator": ">", "value": 3},
                priority=Priority.P2,
                target_level=Level.L4,
                sla="10分钟",
                actions=["调整治理策略", "重新评估问题"],
                escalation_path="L3治理无效 → L4",
            ),
            TriggerCondition(
                id="core_function_impact",
                name="核心功能影响",
                description="影响业务核心功能正常运行",
                condition={"field": "core_affected", "operator": "==", "value": True},
                priority=Priority.P0,
                target_level=Level.L4,
                sla="即时",
                actions=["启动核心功能保护", "通知所有相关方"],
                escalation_path="L2 → L4",
            ),
            TriggerCondition(
                id="business_decision_req",
                name="需要业务决策",
                description="问题超出技术范畴需要业务判断",
                condition={"field": "decision_type", "operator": "==", "value": "business"},
                priority=Priority.P2,
                target_level=Level.L4,
                sla="30分钟",
                actions=["准备业务背景材料", "通知业务决策者"],
                escalation_path="L3 → L4",
            ),
            TriggerCondition(
                id="security_incident",
                name="安全事件",
                description="涉及安全漏洞或数据泄露",
                condition={"field": "security_level", "operator": ">=", "value": "high"},
                priority=Priority.P0,
                target_level=Level.L4,
                sla="即时",
                actions=["启动安全响应流程", "隔离受影响系统"],
                escalation_path="L1 → L4",
            ),
            TriggerCondition(
                id="multi_system_failure",
                name="多系统故障",
                description="多个关联系统同时故障",
                condition={"field": "failure_count", "operator": ">", "value": 2},
                priority=Priority.P0,
                target_level=Level.L4,
                sla="即时",
                actions=["启动灾难恢复", "通知管理层"],
                escalation_path="L1 → L4",
            ),
        ]


class L4TriggerGenerator(TriggerGenerator):
    """L4决策层触发器生成器"""

    def generate(self) -> list[TriggerCondition]:
        return [
            TriggerCondition(
                id="max_level_reached",
                name="最高层级",
                description="所有自动层级都已尝试仍无法解决",
                condition={"field": "level", "operator": "==", "value": "max"},
                priority=Priority.P0,
                target_level=Level.L4,
                sla="即时",
                actions=["立即升级到人工"],
                escalation_path="L4 → 人工",
            ),
            TriggerCondition(
                id="circular_escalation",
                name="循环升级",
                description="问题在各层级间循环无法解决",
                condition={"field": "cycle_count", "operator": ">", "value": 3},
                priority=Priority.P0,
                target_level=Level.L4,
                sla="即时",
                actions=["强制终止升级链", "强制指定处理者"],
                escalation_path="L4 → 人工",
            ),
            TriggerCondition(
                id="unrecoverable_state",
                name="不可恢复状态",
                description="系统进入无法自动恢复的状态",
                condition={"field": "state", "operator": "==", "value": "unrecoverable"},
                priority=Priority.P0,
                target_level=Level.L4,
                sla="即时",
                actions=["启动应急响应", "通知人工介入"],
                escalation_path="L4 → 人工",
            ),
        ]


# ============================================================================
# 错误类型触发器生成器
# ============================================================================

class ErrorTypeTriggerGenerator:
    """错误类型触发器生成器"""

    def __init__(self):
        self.error_definitions = {
            "syntax_error": ErrorTrigger(
                id="syntax_error",
                name="语法错误",
                description="代码语法错误",
                condition={"field": "error_type", "operator": "==", "value": "SyntaxError"},
                priority=Priority.P2,
                target_level=Level.L2,
                sla="即时",
                actions=["修复语法错误"],
                escalation_path="L1 → L2",
                patterns=["SyntaxError", "ParseError", "IndentationError"],
                severity="high",
            ),
            "import_error": ErrorTrigger(
                id="import_error",
                name="导入错误",
                description="模块导入失败",
                condition={"field": "error_type", "operator": "==", "value": "ImportError"},
                priority=Priority.P2,
                target_level=Level.L2,
                sla="即时",
                actions=["安装依赖或修复路径"],
                escalation_path="L1 → L2",
                patterns=["ImportError", "ModuleNotFoundError", "NoModuleNamed"],
                severity="medium",
            ),
            "type_error": ErrorTrigger(
                id="type_error",
                name="类型错误",
                description="数据类型不匹配",
                condition={"field": "error_type", "operator": "==", "value": "TypeError"},
                priority=Priority.P3,
                target_level=Level.L2,
                sla="5分钟",
                actions=["修复类型转换"],
                escalation_path="L1重试3次 → L2",
                patterns=["TypeError", "AttributeError"],
                severity="medium",
            ),
            "connection_error": ErrorTrigger(
                id="connection_error",
                name="连接错误",
                description="网络连接失败",
                condition={"field": "error_type", "operator": "==", "value": "ConnectionError"},
                priority=Priority.P2,
                target_level=Level.L2,
                sla="即时",
                actions=["重试连接或切换端点"],
                escalation_path="L1 → L2",
                patterns=["ConnectionError", "ConnectionRefused", "ConnectionTimeout", "HTTP 503"],
                severity="high",
                urgent_bypass=True,
            ),
        }

    def generate(self) -> list[ErrorTrigger]:
        return list(self.error_definitions.values())

    def get_by_type(self, error_type: str) -> ErrorTrigger | None:
        return self.error_definitions.get(error_type)


# ============================================================================
# 超时触发器生成器
# ============================================================================

class TimeoutTriggerGenerator:
    """超时触发器生成器"""

    def __init__(self, sla_multiplier: float = 1.5):
        self.sla_multiplier = sla_multiplier

    def generate(self) -> list[TimeoutTrigger]:
        return [
            TimeoutTrigger(
                id="simple_task_timeout",
                name="简单任务超时",
                description="简单任务执行时间超限",
                condition={"field": "execution_time", "operator": ">", "value": "15秒"},
                priority=Priority.P3,
                target_level=Level.L2,
                sla="30秒",
                actions=["优化执行流程"],
                escalation_path="L1 → L2",
                sla_value="10秒",
                hard_timeout="15秒",
                multiplier=1.5,
            ),
            TimeoutTrigger(
                id="medium_task_timeout",
                name="中等任务超时",
                description="中等复杂度任务执行超时",
                condition={"field": "execution_time", "operator": ">", "value": "7.5分钟"},
                priority=Priority.P3,
                target_level=Level.L2,
                sla="5分钟",
                actions=["分段执行或优化算法"],
                escalation_path="L1 → L2",
                sla_value="5分钟",
                hard_timeout="7.5分钟",
                multiplier=1.5,
            ),
            TimeoutTrigger(
                id="complex_task_timeout",
                name="复杂任务超时",
                description="复杂任务执行超时",
                condition={"field": "execution_time", "operator": ">", "value": "45分钟"},
                priority=Priority.P2,
                target_level=Level.L2,
                sla="10分钟",
                actions=["拆解任务或增加资源"],
                escalation_path="L1 → L2",
                sla_value="30分钟",
                hard_timeout="45分钟",
                multiplier=1.5,
            ),
            TimeoutTrigger(
                id="critical_task_timeout",
                name="关键任务超时",
                description="关键任务执行超时，需要紧急处理",
                condition={"field": "execution_time", "operator": ">", "value": "6分钟"},
                priority=Priority.P0,
                target_level=Level.L4,
                sla="即时",
                actions=["立即升级到最高决策层"],
                escalation_path="L1 → L4",
                sla_value="5分钟",
                hard_timeout="6分钟",
                multiplier=1.2,
            ),
        ]


# ============================================================================
# 资源触发器生成器
# ============================================================================

class ResourceTriggerGenerator:
    """资源触发器生成器"""

    def __init__(self):
        self.cpu_threshold = 0.9
        self.memory_threshold = 0.85
        self.disk_threshold = 0.95
        self.network_threshold = 0.8

    def generate(self) -> list[ResourceTrigger]:
        return [
            ResourceTrigger(
                id="cpu_exhausted",
                name="CPU耗尽",
                description="CPU使用率超过阈值",
                condition={"field": "cpu_usage", "operator": ">", "value": self.cpu_threshold},
                priority=Priority.P2,
                target_level=Level.L2,
                sla="1分钟",
                actions=["扩容CPU", "优化计算"],
                escalation_path="L1自处理",
                resource="cpu",
                threshold=self.cpu_threshold,
                single_action="scale_up",
            ),
            ResourceTrigger(
                id="memory_exhausted",
                name="内存耗尽",
                description="内存使用率超过阈值",
                condition={"field": "memory_usage", "operator": ">", "value": self.memory_threshold},
                priority=Priority.P2,
                target_level=Level.L2,
                sla="1分钟",
                actions=["释放内存", "扩容内存"],
                escalation_path="L1自处理",
                resource="memory",
                threshold=self.memory_threshold,
                single_action="scale_up",
            ),
            ResourceTrigger(
                id="disk_exhausted",
                name="磁盘耗尽",
                description="磁盘使用率超过阈值",
                condition={"field": "disk_usage", "operator": ">", "value": self.disk_threshold},
                priority=Priority.P2,
                target_level=Level.L2,
                sla="5分钟",
                actions=["清理磁盘", "扩容存储"],
                escalation_path="L1 → L2",
                resource="disk",
                threshold=self.disk_threshold,
                single_action="cleanup",
            ),
            ResourceTrigger(
                id="network_exhausted",
                name="网络带宽耗尽",
                description="网络带宽使用率超过阈值",
                condition={"field": "network_usage", "operator": ">", "value": self.network_threshold},
                priority=Priority.P2,
                target_level=Level.L2,
                sla="1分钟",
                actions=["限流", "扩容带宽"],
                escalation_path="L1 → L2",
                resource="network",
                threshold=self.network_threshold,
                single_action="rate_limit",
            ),
        ]


# ============================================================================
# 影响范围触发器生成器
# ============================================================================

class ImpactTriggerGenerator:
    """影响范围触发器生成器"""

    def generate(self) -> list[ImpactTrigger]:
        return [
            ImpactTrigger(
                id="local_impact",
                name="局部影响",
                description="仅影响当前任务",
                condition={"field": "users_affected", "operator": "==", "value": 1},
                priority=Priority.P4,
                target_level=Level.L1,
                sla="无",
                actions=["记录日志"],
                escalation_path="L1自处理",
                scope="local",
                users_affected="1",
            ),
            ImpactTrigger(
                id="team_impact",
                name="团队影响",
                description="影响单个团队",
                condition={"field": "users_affected", "operator": "between", "value": [2, 10]},
                priority=Priority.P2,
                target_level=Level.L2,
                sla="10分钟",
                actions=["通知团队负责人", "协调修复"],
                escalation_path="L1 → L2",
                scope="team",
                users_affected="2-10",
                escalation_target=Level.L2,
            ),
            ImpactTrigger(
                id="department_impact",
                name="部门影响",
                description="影响多个团队",
                condition={"field": "users_affected", "operator": "between", "value": [11, 100]},
                priority=Priority.P1,
                target_level=Level.L3,
                sla="5分钟",
                actions=["通知部门负责人", "启动部门级响应"],
                escalation_path="L2 → L3",
                scope="department",
                users_affected="11-100",
                escalation_target=Level.L3,
            ),
            ImpactTrigger(
                id="organization_impact",
                name="组织影响",
                description="影响整个组织",
                condition={"field": "users_affected", "operator": ">", "value": 100},
                priority=Priority.P0,
                target_level=Level.L4,
                sla="即时",
                actions=["通知管理层", "启动组织级响应"],
                escalation_path="L3 → L4",
                scope="organization",
                users_affected=">100",
                escalation_target=Level.L4,
            ),
            ImpactTrigger(
                id="external_impact",
                name="外部影响",
                description="影响外部用户",
                condition={"field": "users_affected", "operator": ">", "value": 0, "scope": "external"},
                priority=Priority.P0,
                target_level=Level.L4,
                sla="即时",
                actions=["通知外部用户", "启动公关响应"],
                escalation_path="L3 → L4 + 人工",
                scope="external",
                users_affected="any external",
                escalation_target=Level.L4,
            ),
        ]


# ============================================================================
# 抑制规则生成器
# ============================================================================

class SuppressionRuleGenerator:
    """触发抑制规则生成器"""

    def generate(self) -> list[SuppressionRule]:
        return [
            SuppressionRule(
                name="cooldown_suppression",
                description="相同错误在冷却时间内不重复触发",
                cooldown_window="5分钟",
                same_error_only=True,
                same_context=False,
            ),
            SuppressionRule(
                name="dependency_suppression",
                description="依赖问题已在处理中时抑制下级触发",
                parent_handling=True,
                critical_triggers=["dependency_unavailable"],
            ),
            SuppressionRule(
                name="batch_operation_suppression",
                description="批量任务只触发一次",
                batch_trigger_once=True,
                aggregate_window="1分钟",
            ),
            SuppressionRule(
                name="degradation_mode_suppression",
                description="系统处于降级模式时抑制非紧急触发",
                critical_triggers=["security_incident", "data_loss", "core_function_impact"],
            ),
        ]


# ============================================================================
# 紧急路径生成器
# ============================================================================

class UrgentPathGenerator:
    """紧急升级路径生成器"""

    def generate(self) -> list[UrgentPath]:
        return [
            UrgentPath(
                trigger="security_incident",
                bypass_levels=["L2", "L3"],
                target_level=Level.L4,
                reason="安全事件需要最高决策层快速响应",
                parallel_notification=True,
                immediate_escalation=True,
            ),
            UrgentPath(
                trigger="data_loss_risk",
                bypass_levels=["L2", "L3"],
                target_level=Level.L4,
                reason="数据丢失风险不可逆",
                parallel_notification=True,
                immediate_escalation=True,
            ),
            UrgentPath(
                trigger="core_function_failure",
                bypass_levels=["L3"],
                target_level=Level.L4,
                reason="核心功能影响业务连续性",
                parallel_notification=True,
                immediate_escalation=True,
            ),
            UrgentPath(
                trigger="business_decision_required",
                bypass_levels=[],
                target_level=Level.L4,
                reason="业务决策必须由决策层做出",
                parallel_notification=True,
                immediate_escalation=False,
            ),
            UrgentPath(
                trigger="escalation_loop",
                bypass_levels=["L2", "L3"],
                target_level=Level.L3,
                reason="循环升级必须立即终止",
                parallel_notification=True,
                immediate_escalation=True,
            ),
        ]


# ============================================================================
# 触发矩阵生成器（总控）
# ============================================================================

class TriggerMatrixGenerator:
    """触发矩阵生成器总控"""

    def __init__(self, scenario: str = "generic", sla_multiplier: float = 1.5):
        self.scenario = scenario
        self.sla_multiplier = sla_multiplier
        self.l1_gen = L1TriggerGenerator()
        self.l2_gen = L2TriggerGenerator()
        self.l3_gen = L3TriggerGenerator()
        self.l4_gen = L4TriggerGenerator()
        self.error_gen = ErrorTypeTriggerGenerator()
        self.timeout_gen = TimeoutTriggerGenerator(sla_multiplier)
        self.resource_gen = ResourceTriggerGenerator()
        self.impact_gen = ImpactTriggerGenerator()
        self.suppression_gen = SuppressionRuleGenerator()
        self.urgent_gen = UrgentPathGenerator()

    def generate_level_triggers(self) -> dict[str, Any]:
        """生成各层触发配置"""
        return {
            "level_1": self._format_triggers(self.l1_gen.generate()),
            "level_2": self._format_triggers(self.l2_gen.generate()),
            "level_3": self._format_triggers(self.l3_gen.generate()),
            "level_4": self._format_triggers(self.l4_gen.generate()),
        }

    def generate_error_triggers(self) -> dict[str, Any]:
        """生成错误类型触发配置"""
        return {
            "syntax_error": self._format_trigger(self.error_gen.get_by_type("syntax_error")),
            "import_error": self._format_trigger(self.error_gen.get_by_type("import_error")),
            "type_error": self._format_trigger(self.error_gen.get_by_type("type_error")),
            "connection_error": self._format_trigger(self.error_gen.get_by_type("connection_error")),
        }

    def generate_timeout_triggers(self) -> dict[str, Any]:
        """生成超时触发配置"""
        return {
            "simple_task": self._format_trigger(self.timeout_gen.generate()[0]),
            "medium_task": self._format_trigger(self.timeout_gen.generate()[1]),
            "complex_task": self._format_trigger(self.timeout_gen.generate()[2]),
            "critical_task": self._format_trigger(self.timeout_gen.generate()[3]),
        }

    def generate_resource_triggers(self) -> dict[str, Any]:
        """生成资源触发配置"""
        return {
            "cpu_threshold": self.resource_gen.cpu_threshold,
            "memory_threshold": self.resource_gen.memory_threshold,
            "disk_threshold": self.resource_gen.disk_threshold,
            "network_threshold": self.resource_gen.network_threshold,
        }

    def generate_impact_triggers(self) -> dict[str, Any]:
        """生成影响范围触发配置"""
        return {
            "local": self._format_trigger(self.impact_gen.generate()[0]),
            "team": self._format_trigger(self.impact_gen.generate()[1]),
            "department": self._format_trigger(self.impact_gen.generate()[2]),
            "organization": self._format_trigger(self.impact_gen.generate()[3]),
            "external": self._format_trigger(self.impact_gen.generate()[4]),
        }

    def generate_suppression_rules(self) -> dict[str, Any]:
        """生成抑制规则配置"""
        rules = {}
        for rule in self.suppression_gen.generate():
            rules[rule.name] = {
                "enabled": rule.enabled,
                "cooldown_window": rule.cooldown_window,
                "same_error_only": rule.same_error_only,
                "same_context": rule.same_context,
                "parent_handling": rule.parent_handling,
                "batch_trigger_once": rule.batch_trigger_once,
                "aggregate_window": rule.aggregate_window,
                "critical_triggers": rule.critical_triggers,
            }
        return rules

    def generate_urgent_paths(self) -> list[dict[str, Any]]:
        """生成紧急路径配置"""
        return [
            {
                "trigger": up.trigger,
                "bypass": up.bypass_levels,
                "target": f"level_{up.target_level.value.lower()}",
                "reason": up.reason,
                "parallel_notification": up.parallel_notification,
                "immediate_escalation": up.immediate_escalation,
            }
            for up in self.urgent_gen.generate()
        ]

    def generate_statistics_config(self) -> dict[str, Any]:
        """生成统计配置"""
        return {
            "enabled": True,
            "metrics": [
                "trigger_count",
                "escalation_rate",
                "false_positive_rate",
                "repeat_trigger_count",
            ],
        }

    def generate_complete_matrix(self) -> dict[str, Any]:
        """生成完整触发矩阵"""
        return {
            "metadata": {
                "name": f"{self.scenario}触发矩阵",
                "version": "1.0.0",
                "created_date": datetime.now().strftime("%Y-%m-%d"),
                "author": "天龙引擎",
                "description": f"{self.scenario}场景的触发矩阵配置",
            },
            "level_triggers": self.generate_level_triggers(),
            "error_triggers": self.generate_error_triggers(),
            "timeout_triggers": self.generate_timeout_triggers(),
            "resource_triggers": self.generate_resource_triggers(),
            "impact_triggers": self.generate_impact_triggers(),
            "urgent_paths": self.generate_urgent_paths(),
            "suppression": self.generate_suppression_rules(),
            "statistics": self.generate_statistics_config(),
        }

    def _format_trigger(self, trigger: TriggerCondition) -> dict[str, Any]:
        """格式化单个触发器"""
        if trigger is None:
            return {}
        return {
            "id": trigger.id,
            "name": trigger.name,
            "description": trigger.description,
            "condition": trigger.condition,
            "priority": trigger.priority.value,
            "target_level": f"level_{trigger.target_level.value.lower()}",
            "sla": trigger.sla,
            "actions": trigger.actions,
            "escalation_path": trigger.escalation_path,
        }

    def _format_triggers(self, triggers: list[TriggerCondition]) -> dict[str, Any]:
        """格式化触发器列表"""
        return [self._format_trigger(t) for t in triggers]

    def to_yaml(self) -> str:
        """输出YAML格式"""
        if not YAML_AVAILABLE:
            return self._to_text()
        matrix = self.generate_complete_matrix()
        return dump(matrix, Dumper=Dumper, default_flow_style=False, allow_unicode=True)

    def _to_text(self) -> str:
        """输出文本格式（无YAML库时）"""
        import json
        matrix = self.generate_complete_matrix()
        return json.dumps(matrix, indent=2, ensure_ascii=False)

    def to_dict(self) -> dict[str, Any]:
        """输出字典格式"""
        return self.generate_complete_matrix()


# ============================================================================
# CLI接口
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="触发矩阵生成器 - 生成升级触发矩阵配置",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python trigger-matrix-generator.py                           # 生成通用触发矩阵
  python trigger-matrix-generator.py --scenario dev            # 生成开发场景触发矩阵
  python trigger-matrix-generator.py --scenario ops             # 生成运维场景触发矩阵
  python trigger-matrix-generator.py --output matrix.yaml      # 输出到文件
  python trigger-matrix-generator.py --format text              # 文本格式输出
        """
    )
    parser.add_argument(
        "--scenario",
        default="generic",
        choices=["generic", "dev", "ops", "客服", "data"],
        help="场景类型 (default: generic)"
    )
    parser.add_argument(
        "--sla-multiplier",
        type=float,
        default=1.5,
        help="SLA超时倍数 (default: 1.5)"
    )
    parser.add_argument(
        "--output", "-o",
        help="输出文件路径"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["yaml", "json", "text"],
        default="yaml",
        help="输出格式 (default: yaml)"
    )
    parser.add_argument(
        "--level", "-l",
        choices=["l1", "l2", "l3", "l4", "error", "timeout", "resource", "impact", "urgent"],
        help="仅生成指定层级的触发器"
    )

    args = parser.parse_args()

    generator = TriggerMatrixGenerator(
        scenario=args.scenario,
        sla_multiplier=args.sla_multiplier
    )

    if args.level:
        matrix = _generate_partial_matrix(generator, args.level)
    else:
        matrix = generator.generate_complete_matrix()

    if args.format == "yaml":
        output = dump(matrix, Dumper=Dumper, default_flow_style=False, allow_unicode=True) if YAML_AVAILABLE else _json_dumps(matrix)
    elif args.format == "json":
        import json
        output = json.dumps(matrix, indent=2, ensure_ascii=False)
    else:
        import json
        output = _format_text(matrix)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"✅ 触发矩阵已保存到: {args.output}")
    else:
        print(output)


def _generate_partial_matrix(generator: TriggerMatrixGenerator, level: str) -> dict[str, Any]:
    """生成部分触发矩阵"""
    partial_map = {
        "l1": {"level_1": generator.generate_level_triggers()["level_1"]},
        "l2": {"level_2": generator.generate_level_triggers()["level_2"]},
        "l3": {"level_3": generator.generate_level_triggers()["level_3"]},
        "l4": {"level_4": generator.generate_level_triggers()["level_4"]},
        "error": {"error_triggers": generator.generate_error_triggers()},
        "timeout": {"timeout_triggers": generator.generate_timeout_triggers()},
        "resource": {"resource_triggers": generator.generate_resource_triggers()},
        "impact": {"impact_triggers": generator.generate_impact_triggers()},
        "urgent": {"urgent_paths": generator.generate_urgent_paths()},
    }
    return partial_map.get(level, {})


def _json_dumps(data: dict) -> str:
    import json
    return json.dumps(data, indent=2, ensure_ascii=False)


def _format_text(matrix: dict[str, Any]) -> str:
    """格式化文本输出"""
    lines = []
    lines.append("=" * 60)
    lines.append(f"触发矩阵: {matrix.get('metadata', {}).get('name', 'Unknown')}")
    lines.append(f"版本: {matrix.get('metadata', {}).get('version', 'Unknown')}")
    lines.append(f"日期: {matrix.get('metadata', {}).get('created_date', 'Unknown')}")
    lines.append("=" * 60)

    if "level_triggers" in matrix:
        lines.append("\n## 层级触发配置")
        for level, triggers in matrix["level_triggers"].items():
            lines.append(f"\n### {level.upper()}")
            for t in triggers:
                lines.append(f"  - [{t.get('priority', 'N/A')}] {t.get('name', 'Unknown')}")
                lines.append(f"    ID: {t.get('id', 'N/A')}")
                lines.append(f"    SLA: {t.get('sla', 'N/A')}")
                lines.append(f"    升级路径: {t.get('escalation_path', 'N/A')}")

    if "urgent_paths" in matrix:
        lines.append("\n## 紧急升级路径")
        for up in matrix["urgent_paths"]:
            bypass_str = " → ".join([f"L{p}" for p in up.get("bypass", [])])
            lines.append(f"  - {up.get('trigger', 'N/A')}: {bypass_str} → {up.get('target', 'N/A')}")
            lines.append(f"    原因: {up.get('reason', 'N/A')}")

    return "\n".join(lines)


if __name__ == "__main__":
    main()
