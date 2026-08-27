#!/usr/bin/env python3
"""
暂停控制器 (Pause Controller)

基于暂停协议提示词，对任务执行决策进行暂停评估和执行控制。
支持5种暂停类型：resource_contention/backpressure/circuit_breaker/dependency_pause/human_review

用法:
    python pause-controller.py --mode detect --task-id TASK_001
    python pause-controller.py --mode execute --task-id TASK_001 --pause-type resource_contention
    python pause-controller.py --mode monitor --pause-id PAUSE_001
    python pause-controller.py --input-json '{"task_id":"TASK_001","pause_type":"resource_contention"}'
"""

import argparse
import json
import sys
import time
from dataclasses import dataclass, field, asdict
from typing import Optional
from pathlib import Path
from datetime import datetime
from enum import Enum


class PauseState(Enum):
    """暂停状态枚举"""
    WAITING = "waiting"
    ACTIVE = "active"
    MONITORING = "monitoring"
    RECOVERING = "recovering"
    RESOLVED = "resolved"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class PauseCondition:
    """暂停条件"""
    condition_id: str
    description: str
    met: bool
    confidence: float = 0.0
    value: str = ""
    threshold: str = ""


@dataclass
class WakeCondition:
    """唤醒条件"""
    condition_id: str
    description: str
    satisfied: bool = False
    current_value: str = ""
    target_value: str = ""


@dataclass
class DegradedStrategy:
    """降级执行策略"""
    strategy_name: str
    conditions_met: bool
    outcome: str
    steps: list[str] = field(default_factory=list)


@dataclass
class PauseCost:
    """暂停成本"""
    waiting_time_ms: int = 0
    resource_waste_ms: int = 0
    context_loss_ms: int = 0
    total_cost_ms: int = 0
    impact_level: str = "low"  # low/medium/high/critical


@dataclass
class PauseDecision:
    """暂停决策"""
    task_id: str
    pause_type: str  # resource_contention/backpressure/circuit_breaker/dependency_pause/human_review
    should_pause: bool
    confidence: float
    reason: str
    action: str  # pause_and_wait/pause_and_degrade/pause_and_escalate/cancel_pause
    conditions: list[PauseCondition] = field(default_factory=list)
    wake_conditions: list[WakeCondition] = field(default_factory=list)
    pause_cost: Optional[PauseCost] = None
    degraded_strategy: Optional[DegradedStrategy] = None
    max_pause_duration_ms: int = 0
    escalation_required: bool = False
    notifications_required: list[str] = field(default_factory=list)
    timestamp: str = ""


@dataclass
class PauseRecord:
    """暂停记录"""
    pause_id: str
    pause_type: str
    task_id: str
    start_time: str
    end_time: str = ""
    duration_ms: int = 0
    resolution: str = ""  # auto_recovered/manual_intervention/timeout/escalated/degraded
    wake_condition_met: bool = False
    degraded_executed: bool = False
    data_loss: str = "none"  # none/partial/total
    resumed_from: str = ""
    impact_analysis: dict = field(default_factory=dict)


class PauseController:
    """暂停控制器核心类"""

    # 暂停类型配置
    PAUSE_TYPES = {
        'resource_contention': {
            'trigger_threshold': 1,
            'default_level': 'hold',
            'confidence_weight': 1.0,
            'max_duration_ms': 300000,  # 5分钟
            'label': '资源争用暂停',
            'description': '所需资源不可用，API配额耗尽，数据库连接超时',
            'conditions': [
                {'id': 'resource_available', 'description': '资源是否可用', 'weight': 0.3},
                {'id': 'wait_time', 'description': '等待时间是否>30秒', 'weight': 0.25},
                {'id': 'alternative_resource', 'description': '是否有替代资源', 'weight': 0.25},
                {'id': 'retry_exhausted', 'description': '重试是否已耗尽', 'weight': 0.2},
            ],
            'wake_conditions': [
                {'id': 'resource_available', 'description': 'resource_available == true', 'target': 'true'},
                {'id': 'wait_time_acceptable', 'description': 'wait_time < max_wait', 'target': 'acceptable'},
                {'id': 'alternative_available', 'description': 'alternative_available == true', 'target': 'true'},
            ],
            'escalation_threshold_ms': 300000,
            'escalation_action': '请求资源管理员介入',
        },
        'backpressure': {
            'trigger_threshold': 1,
            'default_level': 'hold',
            'confidence_weight': 0.9,
            'max_duration_ms': 600000,  # 10分钟
            'label': '背压暂停',
            'description': '队列深度过大，处理速率过低，内存使用过高',
            'conditions': [
                {'id': 'queue_depth', 'description': '队列深度是否>20', 'weight': 0.3},
                {'id': 'processing_rate', 'description': '处理速率是否<50%', 'weight': 0.25},
                {'id': 'memory_usage', 'description': '内存使用是否>80%', 'weight': 0.25},
                {'id': 'downstream_capacity', 'description': '下游能力是否不足', 'weight': 0.2},
            ],
            'wake_conditions': [
                {'id': 'queue_depth_reduced', 'description': 'queue_depth < 15', 'target': '<15'},
                {'id': 'processing_rate_normal', 'description': 'processing_rate > 60%', 'target': '>60%'},
                {'id': 'memory_usage_normal', 'description': 'memory_usage < 75%', 'target': '<75%'},
            ],
            'escalation_threshold_ms': 600000,
            'escalation_action': '启用背压控制并通知系统管理员',
        },
        'circuit_breaker': {
            'trigger_threshold': 1,
            'default_level': 'critical',
            'confidence_weight': 1.0,
            'max_duration_ms': 900000,  # 15分钟
            'label': '熔断器暂停',
            'description': '错误率过高，超时次数过多，健康检查失败',
            'conditions': [
                {'id': 'error_rate', 'description': '错误率是否>50%', 'weight': 0.35},
                {'id': 'timeout_count', 'description': '超时次数是否>10', 'weight': 0.3},
                {'id': 'health_check_failed', 'description': '健康检查是否失败', 'weight': 0.2},
                {'id': 'circuit_state', 'description': '熔断器状态是否为open', 'weight': 0.15},
            ],
            'wake_conditions': [
                {'id': 'health_check_passed', 'description': 'health_check_passed == true', 'target': 'true'},
                {'id': 'error_rate_reduced', 'description': 'error_rate < 30%', 'target': '<30%'},
                {'id': 'circuit_state', 'description': 'circuit_state == "half_open"', 'target': 'half_open'},
            ],
            'escalation_threshold_ms': 900000,
            'escalation_action': '立即通知运维团队并触发熔断',
        },
        'dependency_pause': {
            'trigger_threshold': 1,
            'default_level': 'warm',
            'confidence_weight': 0.85,
            'max_duration_ms': 1800000,  # 30分钟
            'label': '依赖暂停',
            'description': '前置任务未完成，外部依赖不可用，预估等待过长',
            'conditions': [
                {'id': 'dependency_status', 'description': '依赖状态是否pending/failed', 'weight': 0.3},
                {'id': 'estimated_wait', 'description': '预估等待是否>5分钟', 'weight': 0.3},
                {'id': 'alternative_path', 'description': '是否有替代路径', 'weight': 0.25},
                {'id': 'can_parallel', 'description': '是否可以并行', 'weight': 0.15},
            ],
            'wake_conditions': [
                {'id': 'dependency_completed', 'description': 'dependency_status == "completed"', 'target': 'completed'},
                {'id': 'alternative_path_available', 'description': 'alternative_path_available == true', 'target': 'true'},
                {'id': 'parallel_enabled', 'description': 'can_parallel == true', 'target': 'true'},
            ],
            'escalation_threshold_ms': 1800000,
            'escalation_action': '通知上游依赖方或寻找替代方案',
        },
        'human_review': {
            'trigger_threshold': 1,
            'default_level': 'warm',
            'confidence_weight': 0.95,
            'max_duration_ms': 3600000,  # 60分钟
            'label': '人工审核暂停',
            'description': '需要人工决策，风险等级中高，无明确执行路径',
            'conditions': [
                {'id': 'decision_required', 'description': '是否需要人工决策', 'weight': 0.35},
                {'id': 'risk_level', 'description': '风险等级是否中高', 'weight': 0.3},
                {'id': 'no_clear_path', 'description': '是否有明确执行路径', 'weight': 0.2},
                {'id': 'user_requested', 'description': '是否用户请求人工审核', 'weight': 0.15},
            ],
            'wake_conditions': [
                {'id': 'decision_received', 'description': 'decision_received == true', 'target': 'true'},
                {'id': 'timeout_reached', 'description': 'timeout_reached == true', 'target': 'true'},
            ],
            'escalation_threshold_ms': 3600000,
            'escalation_action': '超时升级至主管或自动降级处理',
        },
    }

    # 暂停级别配置
    PAUSE_LEVELS = {
        'soft': {
            'overhead_ms': 100,
            'description': '软暂停，保留所有状态，可快速恢复',
            'state_saving_required': False,
            'recovery_time_ms': 500,
        },
        'warm': {
            'overhead_ms': 500,
            'description': '温暂停，保存部分状态',
            'state_saving_required': True,
            'recovery_time_ms': 2000,
        },
        'hold': {
            'overhead_ms': 1000,
            'description': '保持暂停，保存完整状态',
            'state_saving_required': True,
            'recovery_time_ms': 5000,
        },
        'critical': {
            'overhead_ms': 5000,
            'description': '关键暂停，完整状态保存+通知',
            'state_saving_required': True,
            'recovery_time_ms': 15000,
        },
    }

    # 降级执行策略配置
    DEGRADED_STRATEGIES = {
        'use_cache': {
            'name': '使用缓存',
            'conditions': ['cache_available == true', 'cache_freshness < threshold'],
            'outcome': '返回缓存结果',
            'steps': [
                '检查缓存是否可用',
                '验证缓存新鲜度',
                '加载缓存数据',
                '返回缓存结果',
                '标记结果为缓存来源',
            ],
        },
        'partial_result': {
            'name': '返回部分结果',
            'conditions': ['partial_result_possible == true', 'user_acceptance == true'],
            'outcome': '返回部分完成内容',
            'steps': [
                '评估部分结果可行性',
                '收集已完成的部分',
                '标记未完成部分',
                '征求用户同意',
                '返回部分结果',
            ],
        },
        'fallback_response': {
            'name': '返回降级响应',
            'conditions': ['fallback_available == true', 'user_notified == true'],
            'outcome': '返回预设降级结果',
            'steps': [
                '检查降级响应是否可用',
                '通知用户降级状态',
                '加载预设降级响应',
                '记录降级事件',
                '返回降级结果',
            ],
        },
        'retry_with_backoff': {
            'name': '指数退避重试',
            'conditions': ['retry_count < max_retries', 'error_recoverable == true'],
            'outcome': '使用指数退避策略重试',
            'steps': [
                '检查重试次数',
                '计算退避延迟',
                '执行等待',
                '重新尝试操作',
                '评估重试结果',
            ],
        },
        'skip_and_continue': {
            'name': '跳过并继续',
            'conditions': ['task_non_blocking == true', 'downstream_aware == true'],
            'outcome': '跳过当前任务继续执行后续任务',
            'steps': [
                '确认任务非阻塞',
                '通知下游依赖方',
                '保存跳过标记',
                '继续执行后续任务',
                '记录跳过事件',
            ],
        },
    }

    def __init__(self):
        self.pause_records: dict[str, PauseRecord] = {}
        self.active_pauses: dict[str, PauseRecord] = {}
        self.pause_history: list[PauseRecord] = []

    def evaluate(
        self,
        task_id: str,
        pause_type: Optional[str] = None,
        resource_available: bool = True,
        wait_time_ms: int = 0,
        queue_depth: int = 0,
        processing_rate: float = 100.0,
        memory_usage: float = 50.0,
        error_rate: float = 0.0,
        timeout_count: int = 0,
        health_check_passed: bool = True,
        circuit_state: str = "closed",
        dependency_status: str = "completed",
        estimated_wait_ms: int = 0,
        alternative_path: bool = False,
        can_parallel: bool = False,
        decision_required: bool = False,
        risk_level: str = "low",
        user_requested: bool = False,
        cache_available: bool = False,
        partial_result_possible: bool = False,
        fallback_available: bool = False,
        task_non_blocking: bool = False,
        retry_count: int = 0,
        max_retries: int = 3,
        error_recoverable: bool = False,
        downstream_aware: bool = False,
    ) -> PauseDecision:
        """评估暂停决策"""
        timestamp = datetime.now().isoformat()

        # 如果未指定暂停类型，自动识别
        if not pause_type:
            pause_type = self._identify_pause_type(
                resource_available=resource_available,
                wait_time_ms=wait_time_ms,
                queue_depth=queue_depth,
                processing_rate=processing_rate,
                memory_usage=memory_usage,
                error_rate=error_rate,
                timeout_count=timeout_count,
                health_check_passed=health_check_passed,
                circuit_state=circuit_state,
                dependency_status=dependency_status,
                estimated_wait_ms=estimated_wait_ms,
                decision_required=decision_required,
                risk_level=risk_level,
                user_requested=user_requested,
            )

        # 获取暂停类型配置
        type_config = self.PAUSE_TYPES.get(pause_type, self.PAUSE_TYPES['resource_contention'])

        # 评估条件
        conditions = self._evaluate_conditions(
            pause_type=pause_type,
            resource_available=resource_available,
            wait_time_ms=wait_time_ms,
            queue_depth=queue_depth,
            processing_rate=processing_rate,
            memory_usage=memory_usage,
            error_rate=error_rate,
            timeout_count=timeout_count,
            health_check_passed=health_check_passed,
            circuit_state=circuit_state,
            dependency_status=dependency_status,
            estimated_wait_ms=estimated_wait_ms,
            alternative_path=alternative_path,
            can_parallel=can_parallel,
            decision_required=decision_required,
            risk_level=risk_level,
            user_requested=user_requested,
        )

        # 计算置信度
        confidence = self._calculate_confidence(conditions, type_config)

        # 确定暂停级别
        pause_level = type_config['default_level']

        # 评估唤醒条件
        wake_conditions = self._evaluate_wake_conditions(
            pause_type=pause_type,
            resource_available=resource_available,
            wait_time_ms=wait_time_ms,
            queue_depth=queue_depth,
            processing_rate=processing_rate,
            memory_usage=memory_usage,
            error_rate=error_rate,
            health_check_passed=health_check_passed,
            circuit_state=circuit_state,
            dependency_status=dependency_status,
            decision_required=decision_required,
        )

        # 确定是否应该暂停
        should_pause = self._should_pause(conditions, confidence, pause_type)

        # 计算暂停成本
        pause_cost = self._calculate_pause_cost(
            pause_type=pause_type,
            wait_time_ms=wait_time_ms,
            queue_depth=queue_depth,
            conditions=conditions,
        )

        # 评估降级执行策略
        degraded_strategy = self._evaluate_degraded_strategy(
            cache_available=cache_available,
            partial_result_possible=partial_result_possible,
            fallback_available=fallback_available,
            task_non_blocking=task_non_blocking,
            retry_count=retry_count,
            max_retries=max_retries,
            error_recoverable=error_recoverable,
            downstream_aware=downstream_aware,
            should_pause=should_pause,
        )

        # 确定动作
        action = self._determine_action(
            should_pause=should_pause,
            conditions=conditions,
            degraded_strategy=degraded_strategy,
            pause_level=pause_level,
            confidence=confidence,
        )

        # 确定是否需要升级
        escalation_required = (
            confidence >= 0.9 and
            (len([c for c in conditions if c.met]) >= type_config['trigger_threshold'])
        )

        # 生成原因
        reason = self._generate_reason(pause_type, conditions, confidence)

        # 确定需要的通知
        notifications_required = self._get_notifications(pause_type, escalation_required, pause_level)

        return PauseDecision(
            task_id=task_id,
            pause_type=pause_type,
            should_pause=should_pause,
            confidence=confidence,
            reason=reason,
            action=action,
            conditions=conditions,
            wake_conditions=wake_conditions,
            pause_cost=pause_cost,
            degraded_strategy=degraded_strategy,
            max_pause_duration_ms=type_config['max_duration_ms'],
            escalation_required=escalation_required,
            notifications_required=notifications_required,
            timestamp=timestamp,
        )

    def _identify_pause_type(
        self,
        resource_available: bool,
        wait_time_ms: int,
        queue_depth: int,
        processing_rate: float,
        memory_usage: float,
        error_rate: float,
        timeout_count: int,
        health_check_passed: bool,
        circuit_state: str,
        dependency_status: str,
        estimated_wait_ms: int,
        decision_required: bool,
        risk_level: str,
        user_requested: bool,
    ) -> str:
        """识别暂停类型"""
        # 熔断器优先级最高
        if not health_check_passed or circuit_state == "open" or error_rate > 0.5 or timeout_count > 10:
            return 'circuit_breaker'

        # 人工审核
        if decision_required or user_requested or risk_level in ['medium', 'high']:
            return 'human_review'

        # 背压
        if queue_depth > 20 or processing_rate < 50 or memory_usage > 80:
            return 'backpressure'

        # 依赖暂停
        if dependency_status in ['pending', 'failed'] or estimated_wait_ms > 300000:
            return 'dependency_pause'

        # 资源争用
        if not resource_available or wait_time_ms > 30000:
            return 'resource_contention'

        # 默认
        return 'resource_contention'

    def _evaluate_conditions(
        self,
        pause_type: str,
        resource_available: bool,
        wait_time_ms: int,
        queue_depth: int,
        processing_rate: float,
        memory_usage: float,
        error_rate: float,
        timeout_count: int,
        health_check_passed: bool,
        circuit_state: str,
        dependency_status: str,
        estimated_wait_ms: int,
        alternative_path: bool,
        can_parallel: bool,
        decision_required: bool,
        risk_level: str,
        user_requested: bool,
    ) -> list[PauseCondition]:
        """评估暂停条件"""
        conditions = []

        if pause_type == 'resource_contention':
            conditions.extend([
                PauseCondition(
                    condition_id='resource_available',
                    description='资源是否可用',
                    met=not resource_available,
                    confidence=0.9,
                    value=str(resource_available),
                    threshold='false',
                ),
                PauseCondition(
                    condition_id='wait_time',
                    description='等待时间是否>30秒',
                    met=wait_time_ms > 30000,
                    confidence=0.85,
                    value=f'{wait_time_ms}ms',
                    threshold='>30000ms',
                ),
                PauseCondition(
                    condition_id='alternative_resource',
                    description='是否有替代资源',
                    met=not alternative_path,
                    confidence=0.8,
                    value=str(alternative_path),
                    threshold='false',
                ),
                PauseCondition(
                    condition_id='retry_exhausted',
                    description='重试是否已耗尽',
                    met=wait_time_ms > 60000,
                    confidence=0.75,
                    value=f'{wait_time_ms}ms',
                    threshold='>60000ms',
                ),
            ])

        elif pause_type == 'backpressure':
            conditions.extend([
                PauseCondition(
                    condition_id='queue_depth',
                    description='队列深度是否>20',
                    met=queue_depth > 20,
                    confidence=0.9,
                    value=str(queue_depth),
                    threshold='>20',
                ),
                PauseCondition(
                    condition_id='processing_rate',
                    description='处理速率是否<50%',
                    met=processing_rate < 50,
                    confidence=0.85,
                    value=f'{processing_rate}%',
                    threshold='<50%',
                ),
                PauseCondition(
                    condition_id='memory_usage',
                    description='内存使用是否>80%',
                    met=memory_usage > 80,
                    confidence=0.8,
                    value=f'{memory_usage}%',
                    threshold='>80%',
                ),
                PauseCondition(
                    condition_id='downstream_capacity',
                    description='下游能力是否不足',
                    met=processing_rate < 30,
                    confidence=0.75,
                    value=f'{processing_rate}%',
                    threshold='insufficient',
                ),
            ])

        elif pause_type == 'circuit_breaker':
            conditions.extend([
                PauseCondition(
                    condition_id='error_rate',
                    description='错误率是否>50%',
                    met=error_rate > 0.5,
                    confidence=0.95,
                    value=f'{error_rate*100:.1f}%',
                    threshold='>50%',
                ),
                PauseCondition(
                    condition_id='timeout_count',
                    description='超时次数是否>10',
                    met=timeout_count > 10,
                    confidence=0.9,
                    value=str(timeout_count),
                    threshold='>10',
                ),
                PauseCondition(
                    condition_id='health_check_failed',
                    description='健康检查是否失败',
                    met=not health_check_passed,
                    confidence=0.95,
                    value=str(health_check_passed),
                    threshold='false',
                ),
                PauseCondition(
                    condition_id='circuit_state',
                    description='熔断器状态是否为open',
                    met=circuit_state == 'open',
                    confidence=0.85,
                    value=circuit_state,
                    threshold='open',
                ),
            ])

        elif pause_type == 'dependency_pause':
            conditions.extend([
                PauseCondition(
                    condition_id='dependency_status',
                    description='依赖状态是否pending/failed',
                    met=dependency_status in ['pending', 'failed'],
                    confidence=0.9,
                    value=dependency_status,
                    threshold='pending/failed',
                ),
                PauseCondition(
                    condition_id='estimated_wait',
                    description='预估等待是否>5分钟',
                    met=estimated_wait_ms > 300000,
                    confidence=0.85,
                    value=f'{estimated_wait_ms}ms',
                    threshold='>300000ms',
                ),
                PauseCondition(
                    condition_id='alternative_path',
                    description='是否有替代路径',
                    met=not alternative_path,
                    confidence=0.8,
                    value=str(alternative_path),
                    threshold='false',
                ),
                PauseCondition(
                    condition_id='can_parallel',
                    description='是否可以并行',
                    met=not can_parallel,
                    confidence=0.7,
                    value=str(can_parallel),
                    threshold='false',
                ),
            ])

        elif pause_type == 'human_review':
            conditions.extend([
                PauseCondition(
                    condition_id='decision_required',
                    description='是否需要人工决策',
                    met=decision_required,
                    confidence=0.9,
                    value=str(decision_required),
                    threshold='true',
                ),
                PauseCondition(
                    condition_id='risk_level',
                    description='风险等级是否中高',
                    met=risk_level in ['medium', 'high'],
                    confidence=0.85,
                    value=risk_level,
                    threshold='medium/high',
                ),
                PauseCondition(
                    condition_id='no_clear_path',
                    description='是否有明确执行路径',
                    met=decision_required,
                    confidence=0.8,
                    value=str(decision_required),
                    threshold='true',
                ),
                PauseCondition(
                    condition_id='user_requested',
                    description='是否用户请求人工审核',
                    met=user_requested,
                    confidence=0.95,
                    value=str(user_requested),
                    threshold='true',
                ),
            ])

        return conditions

    def _calculate_confidence(self, conditions: list[PauseCondition], type_config: dict) -> float:
        """计算暂停置信度"""
        if not conditions:
            return 0.0

        met_conditions = [c for c in conditions if c.met]
        if not met_conditions:
            return 0.0

        # 权重加权置信度
        weighted_sum = sum(c.confidence for c in met_conditions)
        base_confidence = weighted_sum / len(conditions)

        # 应用类型权重
        confidence = base_confidence * type_config['confidence_weight']

        return min(confidence, 1.0)

    def _evaluate_wake_conditions(
        self,
        pause_type: str,
        resource_available: bool,
        wait_time_ms: int,
        queue_depth: int,
        processing_rate: float,
        memory_usage: float,
        error_rate: float,
        health_check_passed: bool,
        circuit_state: str,
        dependency_status: str,
        decision_required: bool,
    ) -> list[WakeCondition]:
        """评估唤醒条件"""
        wake_conditions = []

        if pause_type == 'resource_contention':
            wake_conditions.extend([
                WakeCondition(
                    condition_id='resource_available',
                    description='resource_available == true',
                    satisfied=resource_available,
                    current_value=str(resource_available),
                    target_value='true',
                ),
                WakeCondition(
                    condition_id='wait_time_acceptable',
                    description='wait_time < max_wait',
                    satisfied=wait_time_ms < 30000,
                    current_value=f'{wait_time_ms}ms',
                    target_value='<30000ms',
                ),
            ])

        elif pause_type == 'backpressure':
            wake_conditions.extend([
                WakeCondition(
                    condition_id='queue_depth_reduced',
                    description='queue_depth < 15',
                    satisfied=queue_depth < 15,
                    current_value=str(queue_depth),
                    target_value='<15',
                ),
                WakeCondition(
                    condition_id='processing_rate_normal',
                    description='processing_rate > 60%',
                    satisfied=processing_rate > 60,
                    current_value=f'{processing_rate}%',
                    target_value='>60%',
                ),
                WakeCondition(
                    condition_id='memory_usage_normal',
                    description='memory_usage < 75%',
                    satisfied=memory_usage < 75,
                    current_value=f'{memory_usage}%',
                    target_value='<75%',
                ),
            ])

        elif pause_type == 'circuit_breaker':
            wake_conditions.extend([
                WakeCondition(
                    condition_id='health_check_passed',
                    description='health_check_passed == true',
                    satisfied=health_check_passed,
                    current_value=str(health_check_passed),
                    target_value='true',
                ),
                WakeCondition(
                    condition_id='error_rate_reduced',
                    description='error_rate < 30%',
                    satisfied=error_rate < 0.3,
                    current_value=f'{error_rate*100:.1f}%',
                    target_value='<30%',
                ),
                WakeCondition(
                    condition_id='circuit_state',
                    description='circuit_state == "half_open"',
                    satisfied=circuit_state == 'half_open',
                    current_value=circuit_state,
                    target_value='half_open',
                ),
            ])

        elif pause_type == 'dependency_pause':
            wake_conditions.extend([
                WakeCondition(
                    condition_id='dependency_completed',
                    description='dependency_status == "completed"',
                    satisfied=dependency_status == 'completed',
                    current_value=dependency_status,
                    target_value='completed',
                ),
            ])

        elif pause_type == 'human_review':
            wake_conditions.extend([
                WakeCondition(
                    condition_id='decision_received',
                    description='decision_received == true',
                    satisfied=False,  # 需要外部输入
                    current_value='pending',
                    target_value='true',
                ),
                WakeCondition(
                    condition_id='timeout_reached',
                    description='timeout_reached == true',
                    satisfied=False,  # 需要等待超时
                    current_value='not_reached',
                    target_value='true',
                ),
            ])

        return wake_conditions

    def _should_pause(self, conditions: list[PauseCondition], confidence: float, pause_type: str) -> bool:
        """确定是否应该暂停"""
        type_config = self.PAUSE_TYPES.get(pause_type, {})
        threshold = type_config.get('trigger_threshold', 1)

        met_count = len([c for c in conditions if c.met])

        # 满足阈值条件且置信度足够
        return met_count >= threshold and confidence >= 0.6

    def _calculate_pause_cost(
        self,
        pause_type: str,
        wait_time_ms: int,
        queue_depth: int,
        conditions: list[PauseCondition],
    ) -> PauseCost:
        """计算暂停成本"""
        base_wait_time = wait_time_ms if wait_time_ms > 0 else 60000  # 默认1分钟

        # 资源浪费：队列深度越大，浪费越多
        resource_waste = queue_depth * 5000 if queue_depth > 0 else 0

        # 上下文丢失：时间越长，上下文丢失风险越大
        context_loss = int(base_wait_time * 0.1)

        total_cost = base_wait_time + resource_waste + context_loss

        # 影响级别
        if total_cost < 60000:
            impact_level = 'low'
        elif total_cost < 300000:
            impact_level = 'medium'
        elif total_cost < 900000:
            impact_level = 'high'
        else:
            impact_level = 'critical'

        return PauseCost(
            waiting_time_ms=base_wait_time,
            resource_waste_ms=resource_waste,
            context_loss_ms=context_loss,
            total_cost_ms=total_cost,
            impact_level=impact_level,
        )

    def _evaluate_degraded_strategy(
        self,
        cache_available: bool,
        partial_result_possible: bool,
        fallback_available: bool,
        task_non_blocking: bool,
        retry_count: int,
        max_retries: int,
        error_recoverable: bool,
        downstream_aware: bool,
        should_pause: bool,
    ) -> Optional[DegradedStrategy]:
        """评估降级执行策略"""
        if not should_pause:
            return None

        # 优先级：缓存 > 部分结果 > 降级响应 > 退避重试 > 跳过继续
        if cache_available:
            return DegradedStrategy(
                strategy_name='use_cache',
                conditions_met=True,
                outcome='返回缓存结果',
                steps=self.DEGRADED_STRATEGIES['use_cache']['steps'],
            )

        if partial_result_possible:
            return DegradedStrategy(
                strategy_name='partial_result',
                conditions_met=True,
                outcome='返回部分完成内容',
                steps=self.DEGRADED_STRATEGIES['partial_result']['steps'],
            )

        if fallback_available:
            return DegradedStrategy(
                strategy_name='fallback_response',
                conditions_met=True,
                outcome='返回预设降级结果',
                steps=self.DEGRADED_STRATEGIES['fallback_response']['steps'],
            )

        if error_recoverable and retry_count < max_retries:
            return DegradedStrategy(
                strategy_name='retry_with_backoff',
                conditions_met=True,
                outcome='使用指数退避策略重试',
                steps=self.DEGRADED_STRATEGIES['retry_with_backoff']['steps'],
            )

        if task_non_blocking and downstream_aware:
            return DegradedStrategy(
                strategy_name='skip_and_continue',
                conditions_met=True,
                outcome='跳过当前任务继续执行后续任务',
                steps=self.DEGRADED_STRATEGIES['skip_and_continue']['steps'],
            )

        return None

    def _determine_action(
        self,
        should_pause: bool,
        conditions: list[PauseCondition],
        degraded_strategy: Optional[DegradedStrategy],
        pause_level: str,
        confidence: float,
    ) -> str:
        """确定暂停动作"""
        if not should_pause:
            return 'no_action'

        # 如果有降级策略且可以执行
        if degraded_strategy:
            return 'pause_and_degrade'

        # 高置信度 + 关键级别
        if confidence >= 0.9 and pause_level == 'critical':
            return 'pause_and_escalate'

        # 标准暂停等待
        return 'pause_and_wait'

    def _generate_reason(self, pause_type: str, conditions: list[PauseCondition], confidence: float) -> str:
        """生成暂停原因"""
        met_conditions = [c for c in conditions if c.met]
        type_config = self.PAUSE_TYPES.get(pause_type, {})

        if not met_conditions:
            return '未满足暂停条件'

        condition_names = [c.description for c in met_conditions[:3]]
        reason = f"{type_config.get('label', pause_type)}: {', '.join(condition_names)}"
        reason += f" (置信度: {confidence:.0%})"

        return reason

    def _get_notifications(self, pause_type: str, escalation_required: bool, pause_level: str) -> list[str]:
        """获取需要的通知"""
        notifications = []

        if pause_level == 'critical':
            notifications.append('orchestrator')
            notifications.append('system_admin')

        if escalation_required:
            notifications.append('escalation_manager')
            notifications.append('task_owner')

        if pause_type == 'human_review':
            notifications.append('human_reviewer')

        if pause_type == 'circuit_breaker':
            notifications.append('on_call_engineer')

        return notifications

    def execute_pause(self, decision: PauseDecision) -> PauseRecord:
        """执行暂停"""
        pause_id = f"PAUSE-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        start_time = datetime.now().isoformat()

        record = PauseRecord(
            pause_id=pause_id,
            pause_type=decision.pause_type,
            task_id=decision.task_id,
            start_time=start_time,
            resolution='pending',
        )

        self.pause_records[pause_id] = record
        self.active_pauses[pause_id] = record

        return record

    def monitor_pause(self, pause_id: str, current_metrics: dict) -> bool:
        """监控暂停状态，返回是否满足唤醒条件"""
        if pause_id not in self.active_pauses:
            return False

        record = self.active_pauses[pause_id]
        type_config = self.PAUSE_TYPES.get(record.pause_type, {})

        # 检查是否超时
        start = datetime.fromisoformat(record.start_time)
        elapsed_ms = int((datetime.now() - start).total_seconds() * 1000)
        max_duration = type_config.get('max_duration_ms', 600000)

        if elapsed_ms > max_duration:
            record.end_time = datetime.now().isoformat()
            record.duration_ms = elapsed_ms
            record.resolution = 'timeout'
            self.active_pauses.pop(pause_id, None)
            return True

        # 检查唤醒条件
        wake_satisfied = self._check_wake_conditions(record.pause_type, current_metrics)

        if wake_satisfied:
            record.end_time = datetime.now().isoformat()
            record.duration_ms = elapsed_ms
            record.resolution = 'auto_recovered'
            record.wake_condition_met = True
            self.active_pauses.pop(pause_id, None)

        return wake_satisfied

    def _check_wake_conditions(self, pause_type: str, metrics: dict) -> bool:
        """检查唤醒条件是否满足"""
        if pause_type == 'resource_contention':
            return metrics.get('resource_available', False)

        elif pause_type == 'backpressure':
            return (
                metrics.get('queue_depth', 100) < 15 and
                metrics.get('processing_rate', 0) > 60
            )

        elif pause_type == 'circuit_breaker':
            return (
                metrics.get('health_check_passed', False) and
                metrics.get('error_rate', 1.0) < 0.3
            )

        elif pause_type == 'dependency_pause':
            return metrics.get('dependency_status') == 'completed'

        elif pause_type == 'human_review':
            return metrics.get('decision_received', False)

        return False

    def resolve_pause(self, pause_id: str, resolution: str = 'manual_intervention') -> Optional[PauseRecord]:
        """解决暂停"""
        if pause_id not in self.active_pauses:
            return None

        record = self.active_pauses.pop(pause_id)
        record.end_time = datetime.now().isoformat()
        start = datetime.fromisoformat(record.start_time)
        record.duration_ms = int((datetime.now() - start).total_seconds() * 1000)
        record.resolution = resolution

        self.pause_history.append(record)

        return record

    def generate_report(self, decision: PauseDecision) -> str:
        """生成文本格式报告"""
        type_config = self.PAUSE_TYPES.get(decision.pause_type, {})

        lines = []
        lines.append("=" * 60)
        lines.append("暂停决策报告")
        lines.append("=" * 60)
        lines.append("")
        lines.append(f"任务ID: {decision.task_id}")
        lines.append(f"暂停类型: {type_config.get('label', decision.pause_type)}")
        lines.append(f"暂停类型ID: {decision.pause_type}")
        lines.append(f"是否暂停: {'是' if decision.should_pause else '否'}")
        lines.append(f"置信度: {decision.confidence:.0%}")
        lines.append(f"执行动作: {decision.action}")
        lines.append(f"暂停原因: {decision.reason}")
        lines.append("")

        if decision.conditions:
            lines.append("触发条件:")
            for cond in decision.conditions:
                status = '[X]' if cond.met else '[ ]'
                lines.append(f"  {status} {cond.description} (值: {cond.value}, 阈值: {cond.threshold})")
            lines.append("")

        if decision.wake_conditions:
            lines.append("唤醒条件:")
            for wake in decision.wake_conditions:
                status = '[X]' if wake.satisfied else '[ ]'
                lines.append(f"  {status} {wake.description}")
            lines.append("")

        if decision.pause_cost:
            lines.append("暂停成本:")
            lines.append(f"  等待时间: {decision.pause_cost.waiting_time_ms}ms")
            lines.append(f"  资源浪费: {decision.pause_cost.resource_waste_ms}ms")
            lines.append(f"  上下文丢失: {decision.pause_cost.context_loss_ms}ms")
            lines.append(f"  总成本: {decision.pause_cost.total_cost_ms}ms")
            lines.append(f"  影响级别: {decision.pause_cost.impact_level}")
            lines.append("")

        if decision.degraded_strategy:
            lines.append("降级策略:")
            lines.append(f"  策略名称: {decision.degraded_strategy.strategy_name}")
            lines.append(f"  预期结果: {decision.degraded_strategy.outcome}")
            lines.append("  执行步骤:")
            for step in decision.degraded_strategy.steps:
                lines.append(f"    - {step}")
            lines.append("")

        if decision.notifications_required:
            lines.append(f"需要的通知: {', '.join(decision.notifications_required)}")

        if decision.escalation_required:
            lines.append("⚠️  需要升级处理")

        lines.append("")
        lines.append(f"最大暂停时长: {decision.max_pause_duration_ms}ms")
        lines.append(f"评估时间: {decision.timestamp}")
        lines.append("=" * 60)

        return '\n'.join(lines)

    def generate_yaml(self, decision: PauseDecision) -> str:
        """生成YAML格式报告"""
        import yaml

        data = asdict(decision)
        # 转换枚举和dataclass
        if decision.pause_cost:
            data['pause_cost'] = asdict(decision.pause_cost)
        if decision.degraded_strategy:
            data['degraded_strategy'] = asdict(decision.degraded_strategy)

        data['pause_type_label'] = self.PAUSE_TYPES.get(decision.pause_type, {}).get('label', '')

        return yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)


def main():
    parser = argparse.ArgumentParser(
        description='暂停控制器 - 基于暂停协议的任务执行暂停决策',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 检测模式：评估是否应该暂停
  python pause-controller.py --mode detect --task-id TASK_001 --pause-type resource_contention \\
    --resource-available false --wait-time 45000

  # 执行模式：执行暂停决策
  python pause-controller.py --mode execute --task-id TASK_001 --pause-type backpressure \\
    --queue-depth 25 --processing-rate 40 --memory-usage 85

  # 监控模式：监控活跃暂停
  python pause-controller.py --mode monitor --pause-id PAUSE_001

  # JSON输入模式
  python pause-controller.py --input-json '{"task_id":"TASK_001","error_rate":0.6}'

暂停类型:
  resource_contention - 资源争用暂停
  backpressure       - 背压暂停
  circuit_breaker    - 熔断器暂停
  dependency_pause   - 依赖暂停
  human_review       - 人工审核暂停
        '''
    )

    parser.add_argument('--mode', '-m', choices=['detect', 'execute', 'monitor'],
                        default='detect', help='运行模式')
    parser.add_argument('--task-id', help='任务ID')
    parser.add_argument('--pause-id', help='暂停记录ID')
    parser.add_argument('--pause-type', '-t',
                        choices=['resource_contention', 'backpressure', 'circuit_breaker',
                                 'dependency_pause', 'human_review'],
                        help='暂停类型')

    # 资源争用参数
    parser.add_argument('--resource-available', type=lambda x: x.lower() == 'true',
                        default=True, help='资源是否可用')
    parser.add_argument('--wait-time', type=int, default=0,
                        help='等待时间(ms)')

    # 背压参数
    parser.add_argument('--queue-depth', type=int, default=0,
                        help='队列深度')
    parser.add_argument('--processing-rate', type=float, default=100.0,
                        help='处理速率(%%)')
    parser.add_argument('--memory-usage', type=float, default=50.0,
                        help='内存使用(%%)')

    # 熔断器参数
    parser.add_argument('--error-rate', type=float, default=0.0,
                        help='错误率(0-1)')
    parser.add_argument('--timeout-count', type=int, default=0,
                        help='超时次数')
    parser.add_argument('--health-check-passed', type=lambda x: x.lower() == 'true',
                        default=True, help='健康检查是否通过')
    parser.add_argument('--circuit-state', default='closed',
                        help='熔断器状态')

    # 依赖参数
    parser.add_argument('--dependency-status', default='completed',
                        help='依赖状态')
    parser.add_argument('--estimated-wait', type=int, default=0,
                        help='预估等待时间(ms)')
    parser.add_argument('--alternative-path', type=lambda x: x.lower() == 'true',
                        default=False, help='是否有替代路径')
    parser.add_argument('--can-parallel', type=lambda x: x.lower() == 'true',
                        default=False, help='是否可以并行')

    # 人工审核参数
    parser.add_argument('--decision-required', type=lambda x: x.lower() == 'true',
                        default=False, help='是否需要人工决策')
    parser.add_argument('--risk-level', default='low',
                        help='风险等级')
    parser.add_argument('--user-requested', type=lambda x: x.lower() == 'true',
                        default=False, help='是否用户请求人工审核')

    # 降级策略参数
    parser.add_argument('--cache-available', type=lambda x: x.lower() == 'true',
                        default=False, help='缓存是否可用')
    parser.add_argument('--partial-result-possible', type=lambda x: x.lower() == 'true',
                        default=False, help='是否可以返回部分结果')
    parser.add_argument('--fallback-available', type=lambda x: x.lower() == 'true',
                        default=False, help='降级响应是否可用')
    parser.add_argument('--task-non-blocking', type=lambda x: x.lower() == 'true',
                        default=False, help='任务是否非阻塞')
    parser.add_argument('--retry-count', type=int, default=0,
                        help='当前重试次数')
    parser.add_argument('--max-retries', type=int, default=3,
                        help='最大重试次数')
    parser.add_argument('--error-recoverable', type=lambda x: x.lower() == 'true',
                        default=False, help='错误是否可恢复')
    parser.add_argument('--downstream-aware', type=lambda x: x.lower() == 'true',
                        default=False, help='下游是否已知')

    parser.add_argument('--input-json', help='从JSON字符串加载参数')
    parser.add_argument('--output', '-o', choices=['text', 'yaml', 'json'],
                        default='text', help='输出格式')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')

    args = parser.parse_args()

    try:
        controller = PauseController()

        # 从JSON加载
        if args.input_json:
            params = json.loads(args.input_json)
        else:
            params = vars(args)

        task_id = params.get('task_id', 'UNKNOWN')
        pause_id = params.get('pause_id', '')

        # 检测模式
        if args.mode == 'detect':
            decision = controller.evaluate(
                task_id=task_id,
                pause_type=params.get('pause_type'),
                resource_available=params.get('resource_available', True),
                wait_time_ms=params.get('wait_time', 0),
                queue_depth=params.get('queue_depth', 0),
                processing_rate=params.get('processing_rate', 100.0),
                memory_usage=params.get('memory_usage', 50.0),
                error_rate=params.get('error_rate', 0.0),
                timeout_count=params.get('timeout_count', 0),
                health_check_passed=params.get('health_check_passed', True),
                circuit_state=params.get('circuit_state', 'closed'),
                dependency_status=params.get('dependency_status', 'completed'),
                estimated_wait_ms=params.get('estimated_wait', 0),
                alternative_path=params.get('alternative_path', False),
                can_parallel=params.get('can_parallel', False),
                decision_required=params.get('decision_required', False),
                risk_level=params.get('risk_level', 'low'),
                user_requested=params.get('user_requested', False),
                cache_available=params.get('cache_available', False),
                partial_result_possible=params.get('partial_result_possible', False),
                fallback_available=params.get('fallback_available', False),
                task_non_blocking=params.get('task_non_blocking', False),
                retry_count=params.get('retry_count', 0),
                max_retries=params.get('max_retries', 3),
                error_recoverable=params.get('error_recoverable', False),
                downstream_aware=params.get('downstream_aware', False),
            )

            if args.output == 'yaml':
                print(controller.generate_yaml(decision))
            elif args.output == 'json':
                output = asdict(decision)
                if decision.pause_cost:
                    output['pause_cost'] = asdict(decision.pause_cost)
                if decision.degraded_strategy:
                    output['degraded_strategy'] = asdict(decision.degraded_strategy)
                print(json.dumps(output, ensure_ascii=False, indent=2))
            else:
                print(controller.generate_report(decision))

        # 执行模式
        elif args.mode == 'execute':
            decision = controller.evaluate(
                task_id=task_id,
                pause_type=params.get('pause_type'),
                resource_available=params.get('resource_available', True),
                wait_time_ms=params.get('wait_time', 0),
                queue_depth=params.get('queue_depth', 0),
                processing_rate=params.get('processing_rate', 100.0),
                memory_usage=params.get('memory_usage', 50.0),
                error_rate=params.get('error_rate', 0.0),
                timeout_count=params.get('timeout_count', 0),
                health_check_passed=params.get('health_check_passed', True),
                circuit_state=params.get('circuit_state', 'closed'),
                dependency_status=params.get('dependency_status', 'completed'),
                estimated_wait_ms=params.get('estimated_wait', 0),
                alternative_path=params.get('alternative_path', False),
                can_parallel=params.get('can_parallel', False),
                decision_required=params.get('decision_required', False),
                risk_level=params.get('risk_level', 'low'),
                user_requested=params.get('user_requested', False),
                cache_available=params.get('cache_available', False),
                partial_result_possible=params.get('partial_result_possible', False),
                fallback_available=params.get('fallback_available', False),
                task_non_blocking=params.get('task_non_blocking', False),
                retry_count=params.get('retry_count', 0),
                max_retries=params.get('max_retries', 3),
                error_recoverable=params.get('error_recoverable', False),
                downstream_aware=params.get('downstream_aware', False),
            )

            if decision.should_pause:
                record = controller.execute_pause(decision)
                print(f"暂停已执行: {record.pause_id}")
                print(f"暂停类型: {record.pause_type}")
                print(f"开始时间: {record.start_time}")
            else:
                print("不需要暂停，继续执行")

        # 监控模式
        elif args.mode == 'monitor':
            if not pause_id:
                print("错误: 监控模式需要 --pause-id 参数", file=sys.stderr)
                sys.exit(1)

            # 模拟监控指标
            metrics = {
                'resource_available': True,
                'queue_depth': 10,
                'processing_rate': 75.0,
                'memory_usage': 60.0,
                'error_rate': 0.1,
                'health_check_passed': True,
                'dependency_status': 'completed',
                'decision_received': False,
            }

            if controller.monitor_pause(pause_id, metrics):
                print(f"暂停 {pause_id} 已满足唤醒条件")
            else:
                print(f"暂停 {pause_id} 仍在进行中")

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
