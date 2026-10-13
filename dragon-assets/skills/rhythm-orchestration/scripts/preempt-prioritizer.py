#!/usr/bin/env python3
"""
插队优先级器 (Preempt Prioritizer)

基于插队协议提示词，为高优先级任务计算最佳插队时机和中断级别。
支持5种插队类型：安全关键/数据完整性/性能/用户交互/截止时间。

用法:
    python preempt-prioritizer.py <task.json> [--mode evaluate|schedule|abort]
    python preempt-prioritizer.py --input-json <json>
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path
from datetime import datetime


@dataclass
class PreemptCondition:
    """插队条件评估"""
    condition_id: str
    description: str
    met: bool
    value: str = ""
    threshold: str = ""
    severity: str = ""  # critical/high/medium/low


@dataclass
class InterruptionCost:
    """中断成本计算"""
    state_saving_overhead_ms: int
    context_recovery_overhead_ms: int
    total_overhead_ms: int
    priority_task_time_ms: int
    opportunity_cost_ms: int


@dataclass
class PreemptDecision:
    """插队决策结果"""
    preempt_task_id: str
    preempt_type: str
    interrupt_level: str  # full/partial/minimal/none
    should_preempt: bool
    confidence: float
    reason: str
    action: str
    conditions: list[PreemptCondition] = field(default_factory=list)
    interruption_cost: Optional[InterruptionCost] = None
    net_benefit: int = 0  # 正数=值得, 负数=不值
    notifications_required: list[str] = field(default_factory=list)


class PreemptPrioritizer:
    """插队优先级器核心类"""

    # 插队类型配置
    PREEMPT_TYPES = {
        'security_preempt': {
            'trigger_threshold': 1,  # 任一触发
            'default_level': 'full',
            'confidence_weight': 1.0,
            'max_delay_ms': 0,
            'label': '安全关键插队 (CRITICAL)',
            'conditions': ['security_keyword_detected', 'auth_tampering', 'risk_level_high', 'confidence_1']
        },
        'data_integrity_preempt': {
            'trigger_threshold': 4,  # 全部触发
            'default_level': 'full',
            'confidence_weight': 0.9,
            'max_delay_ms': 5000,
            'label': '数据完整性插队 (HIGH)',
            'conditions': ['modifies_critical_data', 'bulk_operation', 'no_transaction', 'no_backup']
        },
        'performance_preempt': {
            'trigger_threshold': 4,  # 全部触发
            'default_level': 'partial',
            'confidence_weight': 0.7,
            'max_delay_ms': 10000,
            'label': '性能插队 (MEDIUM)',
            'conditions': ['cpu_high', 'memory_high', 'response_slow', 'error_rate_high']
        },
        'user_interaction_preempt': {
            'trigger_threshold': 1,  # 任一触发
            'default_level': 'partial',
            'confidence_weight': 0.85,
            'max_delay_ms': 5000,
            'label': '用户交互插队 (HIGH)',
            'conditions': ['user_waiting', 'session_timeout', 'explicit_user_request', 'task_blocking']
        },
        'deadline_preempt': {
            'trigger_threshold': 4,  # 全部触发
            'default_level': 'minimal',
            'confidence_weight': 0.6,
            'max_delay_ms': 600000,
            'label': '截止时间插队 (MEDIUM)',
            'conditions': ['time_critical', 'high_impact', 'many_dependencies', 'critical_path']
        }
    }

    # 中断级别配置
    INTERRUPT_LEVELS = {
        'full': {
            'description': '完全中断当前任务',
            'impact': '高',
            'use_case': '安全/数据关键',
            'overhead_ms': 5000,
            'state_saving': True,
            'recovery_time_ms': 30000
        },
        'partial': {
            'description': '部分中断，保留状态',
            'impact': '中',
            'use_case': '性能/用户交互',
            'overhead_ms': 2000,
            'state_saving': True,
            'recovery_time_ms': 10000
        },
        'minimal': {
            'description': '最小中断',
            'impact': '低',
            'use_case': '截止时间紧迫',
            'overhead_ms': 500,
            'state_saving': False,
            'recovery_time_ms': 2000
        },
        'none': {
            'description': '不中断',
            'impact': '无',
            'use_case': '可并行时',
            'overhead_ms': 0,
            'state_saving': False,
            'recovery_time_ms': 0
        }
    }

    def __init__(self):
        self.decisions: list[PreemptDecision] = []

    def evaluate(self, preempt_task_data: dict, interrupted_task_data: Optional[dict] = None) -> PreemptDecision:
        """
        评估插队决策

        Args:
            preempt_task_data: 高优先级任务数据
            interrupted_task_data: 被中断任务数据(可选)

        Returns:
            PreemptDecision: 插队决策结果
        """
        # 识别插队类型
        preempt_type = self._identify_preempt_type(preempt_task_data)
        if not preempt_type:
            return PreemptDecision(
                preempt_task_id=preempt_task_data.get('id', 'unknown'),
                preempt_type='none',
                interrupt_level='none',
                should_preempt=False,
                confidence=0.0,
                reason='未满足任何插队类型条件',
                action='正常执行，不插队'
            )

        # 评估触发条件
        conditions = self._evaluate_conditions(preempt_type, preempt_task_data)

        # 计算置信度
        confidence = self._calculate_confidence(preempt_type, conditions)

        # 确定中断级别
        interrupt_level = self._determine_interrupt_level(preempt_type, preempt_task_data, conditions)

        # 计算中断成本
        interruption_cost = self._calculate_interruption_cost(interrupt_level, preempt_task_data, interrupted_task_data)

        # 计算净收益
        net_benefit = self._calculate_net_benefit(preempt_type, preempt_task_data, interruption_cost)

        # 确定通知要求
        notifications = self._get_required_notifications(preempt_type, interrupt_level)

        # 最终决策
        should_preempt = net_benefit > 0 and confidence >= 0.6

        reason = self._build_reason(preempt_type, conditions, confidence, net_benefit)
        action = self._build_action(preempt_type, interrupt_level, should_preempt)

        decision = PreemptDecision(
            preempt_task_id=preempt_task_data.get('id', 'unknown'),
            preempt_type=preempt_type,
            interrupt_level=interrupt_level,
            should_preempt=should_preempt,
            confidence=confidence,
            reason=reason,
            action=action,
            conditions=conditions,
            interruption_cost=interruption_cost,
            net_benefit=net_benefit,
            notifications_required=notifications
        )

        self.decisions.append(decision)
        return decision

    def _identify_preempt_type(self, task_data: dict) -> Optional[str]:
        """识别插队类型"""
        for preempt_type, config in self.PREEMPT_TYPES.items():
            trigger_count = 0
            for condition in config['conditions']:
                if task_data.get(condition, False):
                    trigger_count += 1

            if trigger_count >= 1 if config['trigger_threshold'] == 1 else trigger_count >= config['trigger_threshold']:
                return preempt_type

        return None

    def _evaluate_conditions(self, preempt_type: str, task_data: dict) -> list[PreemptCondition]:
        """评估插队条件"""
        conditions = []
        config = self.PREEMPT_TYPES[preempt_type]

        condition_configs = {
            'security_preempt': [
                ('security_keyword_detected', '涉及安全相关关键词', 'security_keywords'),
                ('auth_tampering', '操作认证或权限系统', 'auth_tampering'),
                ('risk_level_high', 'risk_level >= high', 'risk_level'),
                ('confidence_1', '插队置信度 >= 1.0', 'confidence')
            ],
            'data_integrity_preempt': [
                ('modifies_critical_data', '修改关键数据', 'data_type'),
                ('bulk_operation', '批量操作无事务', 'is_bulk'),
                ('no_transaction', '无事务保护', 'has_transaction'),
                ('no_backup', '没有备份', 'has_backup')
            ],
            'performance_preempt': [
                ('cpu_high', 'CPU使用率 > 80%', 'cpu_usage'),
                ('memory_high', '内存使用 > 85%', 'memory_usage'),
                ('response_slow', '响应时间 > 10秒', 'response_time'),
                ('error_rate_high', '错误率 > 5%', 'error_rate')
            ],
            'user_interaction_preempt': [
                ('user_waiting', '用户正在等待', 'user_waiting'),
                ('session_timeout', '会话即将超时', 'session_timeout_min'),
                ('explicit_user_request', '显式用户请求', 'user_request'),
                ('task_blocking', '任务阻塞用户', 'is_blocking')
            ],
            'deadline_preempt': [
                ('time_critical', '距离截止 < 10分钟', 'time_to_deadline_min'),
                ('high_impact', '任务影响度高', 'impact_level'),
                ('many_dependencies', '下游依赖 > 3个', 'downstream_count'),
                ('critical_path', '关键路径任务', 'is_critical_path')
            ]
        }

        for condition_id, description, data_key in condition_configs.get(preempt_type, []):
            value = task_data.get(data_key, task_data.get(condition_id, False))
            threshold = self._get_threshold(preempt_type, condition_id)

            met = False
            severity = 'low'

            if isinstance(value, bool):
                met = value
            elif isinstance(value, (int, float)):
                if '>' in threshold:
                    threshold_val = float(threshold.split('>')[1].strip())
                    met = value > threshold_val
                elif '<' in threshold:
                    threshold_val = float(threshold.split('<')[1].strip())
                    met = value < threshold_val
                elif '>=' in threshold:
                    threshold_val = float(threshold.split('>=')[1].strip())
                    met = value >= threshold_val

            if met:
                if preempt_type == 'security_preempt' and condition_id == 'security_keyword_detected':
                    severity = 'critical'
                elif preempt_type == 'data_integrity_preempt':
                    severity = 'high'
                else:
                    severity = 'medium'

            conditions.append(PreemptCondition(
                condition_id=condition_id,
                description=description,
                met=met,
                value=str(value),
                threshold=threshold,
                severity=severity
            ))

        return conditions

    def _get_threshold(self, preempt_type: str, condition_id: str) -> str:
        """获取条件阈值"""
        thresholds = {
            'security_preempt': {
                'security_keyword_detected': 'true',
                'auth_tampering': 'true',
                'risk_level_high': '>= high',
                'confidence_1': '>= 1.0'
            },
            'data_integrity_preempt': {
                'modifies_critical_data': 'true',
                'bulk_operation': 'true',
                'no_transaction': 'false',
                'no_backup': 'true'
            },
            'performance_preempt': {
                'cpu_high': '> 80%',
                'memory_high': '> 85%',
                'response_slow': '> 10s',
                'error_rate_high': '> 5%'
            },
            'user_interaction_preempt': {
                'user_waiting': 'true',
                'session_timeout': '< 5min',
                'explicit_user_request': 'true',
                'task_blocking': 'true'
            },
            'deadline_preempt': {
                'time_critical': '< 10min',
                'high_impact': '>= high',
                'many_dependencies': '> 3',
                'critical_path': 'true'
            }
        }
        return thresholds.get(preempt_type, {}).get(condition_id, 'true')

    def _calculate_confidence(self, preempt_type: str, conditions: list[PreemptCondition]) -> float:
        """计算插队置信度"""
        config = self.PREEMPT_TYPES[preempt_type]
        met_count = sum(1 for c in conditions if c.met)
        total_count = len(conditions)

        # 基础置信度
        base_confidence = met_count / total_count if total_count > 0 else 0

        # 权重调整
        weighted = base_confidence * config['confidence_weight']

        return min(1.0, weighted)

    def _determine_interrupt_level(self, preempt_type: str, task_data: dict,
                                   conditions: list[PreemptCondition]) -> str:
        """确定中断级别"""
        config = self.PREEMPT_TYPES[preempt_type]

        # 严重条件触发更高中断级别
        critical_met = any(c.severity == 'critical' and c.met for c in conditions)
        high_met = any(c.severity == 'high' and c.met for c in conditions)

        if critical_met:
            return 'full'
        elif high_met:
            return 'partial'

        return config['default_level']

    def _calculate_interruption_cost(self, interrupt_level: str,
                                     preempt_data: dict,
                                     interrupted_data: Optional[dict]) -> InterruptionCost:
        """计算中断成本"""
        level_config = self.INTERRUPT_LEVELS[interrupt_level]

        state_saving = level_config['overhead_ms'] if level_config['state_saving'] else 0

        # 从被中断任务计算恢复开销
        recovery_time = level_config['recovery_time_ms']
        if interrupted_data:
            progress_loss = interrupted_data.get('progress_loss_percent', 0) / 100
            estimated_remaining = interrupted_data.get('estimated_remaining_ms', 0)
            recovery_time = int(estimated_remaining * progress_loss * 0.5)

        total_overhead = state_saving + recovery_time

        # 优先级任务时间
        priority_time = preempt_data.get('estimated_duration_ms', 10000)

        # 机会成本
        opportunity_cost = total_overhead + priority_time

        return InterruptionCost(
            state_saving_overhead_ms=state_saving,
            context_recovery_overhead_ms=recovery_time,
            total_overhead_ms=total_overhead,
            priority_task_time_ms=priority_time,
            opportunity_cost_ms=opportunity_cost
        )

    def _calculate_net_benefit(self, preempt_type: str, preempt_data: dict,
                              interruption_cost: InterruptionCost) -> int:
        """计算净收益"""
        # 收益计算
        response_improvement = preempt_data.get('response_improvement_ms', 0)
        satisfaction_improvement = preempt_data.get('satisfaction_improvement_percent', 0) * 100
        risk_avoided = preempt_data.get('risk_avoided_value', 0)

        benefit = response_improvement + satisfaction_improvement + risk_avoided

        # 成本
        cost = interruption_cost.total_overhead_ms + interruption_cost.opportunity_cost_ms

        return int(benefit - cost)

    def _get_required_notifications(self, preempt_type: str, interrupt_level: str) -> list[str]:
        """获取需要的通知"""
        notifications = ['编排协调师']

        if interrupt_level == 'full':
            notifications.extend(['被中断Agent', '用户(如有需要)'])
        elif interrupt_level == 'partial':
            notifications.extend(['被中断Agent'])

        if preempt_type == 'security_preempt':
            notifications.append('安全师')

        return notifications

    def _build_reason(self, preempt_type: str, conditions: list[PreemptCondition],
                     confidence: float, net_benefit: int) -> str:
        """构建决策理由"""
        met_conditions = [c.description for c in conditions if c.met]
        met_str = '、'.join(met_conditions) if met_conditions else '无'

        reason = f"插队类型: {self.PREEMPT_TYPES[preempt_type]['label']}\n"
        reason += f"触发条件: {met_str}\n"
        reason += f"置信度: {confidence:.2f}\n"
        reason += f"净收益: {'+' if net_benefit >= 0 else ''}{net_benefit}ms"

        return reason

    def _build_action(self, preempt_type: str, interrupt_level: str, should_preempt: bool) -> str:
        """构建行动建议"""
        if not should_preempt:
            return "不插队，等待当前任务完成"

        level_desc = self.INTERRUPT_LEVELS[interrupt_level]['description']
        type_config = self.PREEMPT_TYPES[preempt_type]

        if preempt_type == 'security_preempt':
            return f"立即插队 ({level_desc})"
        elif preempt_type == 'data_integrity_preempt':
            return f"带备份插队 ({level_desc})"
        elif preempt_type == 'user_interaction_preempt':
            return f"立即处理 ({level_desc})"
        else:
            return f"插队执行 {type_config['label']} ({level_desc})"

    def schedule_preempt(self, preempt_tasks: list[dict]) -> list[PreemptDecision]:
        """调度多个插队任务"""
        decisions = []

        for task in preempt_tasks:
            decision = self.evaluate(task)
            decisions.append(decision)

        # 按优先级排序
        decisions.sort(key=lambda d: (
            self.PREEMPT_TYPES.get(d.preempt_type, {}).get('confidence_weight', 0) * d.confidence,
            -d.net_benefit
        ), reverse=True)

        return decisions

    def generate_report(self) -> str:
        """生成决策报告"""
        if not self.decisions:
            return "无插队决策记录"

        lines = []
        lines.append("=" * 60)
        lines.append("插队决策报告")
        lines.append("=" * 60)

        for i, decision in enumerate(self.decisions, 1):
            lines.append(f"\n[决策 {i}]")
            lines.append(f"  任务ID: {decision.preempt_task_id}")
            lines.append(f"  插队类型: {decision.preempt_type}")
            lines.append(f"  中断级别: {decision.interrupt_level}")
            lines.append(f"  决策: {'✓ 插队' if decision.should_preempt else '✗ 不插队'}")
            lines.append(f"  置信度: {decision.confidence:.2f}")
            lines.append(f"  净收益: {'+' if decision.net_benefit >= 0 else ''}{decision.net_benefit}ms")

            if decision.conditions:
                lines.append("  触发条件:")
                for c in decision.conditions:
                    status = '✓' if c.met else '✗'
                    lines.append(f"    {status} {c.description}: {c.value} (阈值: {c.threshold})")

            lines.append(f"  行动: {decision.action}")

            if decision.notifications_required:
                lines.append(f"  通知: {', '.join(decision.notifications_required)}")

        lines.append("\n" + "=" * 60)
        return '\n'.join(lines)

    def generate_yaml(self) -> str:
        """生成YAML格式输出"""
        if not self.decisions:
            return "decisions: []"

        lines = ["preempt_decisions:"]

        for decision in self.decisions:
            lines.append(f"  - task_id: \"{decision.preempt_task_id}\"")
            lines.append(f"    preempt_type: \"{decision.preempt_type}\"")
            lines.append(f"    interrupt_level: \"{decision.interrupt_level}\"")
            lines.append(f"    should_preempt: {str(decision.should_preempt).lower()}")
            lines.append(f"    confidence: {decision.confidence:.2f}")
            lines.append(f"    net_benefit: {decision.net_benefit}")
            lines.append(f"    action: \"{decision.action}\"")
            lines.append(f"    reason: |")
            for line in decision.reason.split('\n'):
                lines.append(f"      {line}")

            if decision.conditions:
                lines.append(f"    conditions:")
                for c in decision.conditions:
                    lines.append(f"      - id: \"{c.condition_id}\"")
                    lines.append(f"        met: {str(c.met).lower()}")
                    lines.append(f"        value: \"{c.value}\"")
                    lines.append(f"        threshold: \"{c.threshold}\"")
                    lines.append(f"        severity: \"{c.severity}\"")

            if decision.notifications_required:
                lines.append(f"    notifications:")
                for n in decision.notifications_required:
                    lines.append(f"      - \"{n}\"")

        return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='插队优先级器 - 基于插队协议计算最佳插队时机和中断级别',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python preempt-prioritizer.py task.json --mode evaluate
  python preempt-prioritizer.py --input-json '{"security_keyword_detected": true, "id": "sec-001"}'
  python preempt-prioritizer.py tasks.json --mode schedule --output preempt.yaml
'''
    )

    parser.add_argument('task', nargs='?', help='任务JSON文件路径')
    parser.add_argument('--input-json', '--json', dest='input_json',
                        help='从JSON字符串加载任务数据')
    parser.add_argument('--mode', choices=['evaluate', 'schedule', 'abort'],
                        default='evaluate', help='执行模式')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--format', '-f', choices=['text', 'yaml', 'json'],
                        default='text', help='输出格式')
    parser.add_argument('--interrupted', help='被中断任务JSON文件')

    args = parser.parse_args()

    try:
        prioritizer = PreemptPrioritizer()

        # 加载数据
        preempt_data = None
        interrupted_data = None

        if args.input_json:
            preempt_data = json.loads(args.input_json)
        elif args.task:
            with open(args.task, 'r', encoding='utf-8') as f:
                preempt_data = json.load(f)

        if args.interrupted:
            with open(args.interrupted, 'r', encoding='utf-8') as f:
                interrupted_data = json.load(f)

        if not preempt_data:
            parser.print_help()
            sys.exit(1)

        # 执行决策
        if args.mode == 'schedule' and isinstance(preempt_data, list):
            decisions = prioritizer.schedule_preempt(preempt_data)
        else:
            task = preempt_data if isinstance(preempt_data, dict) else preempt_data[0]
            decision = prioritizer.evaluate(task, interrupted_data)
            decisions = [decision]

        # 生成输出
        if args.format == 'yaml':
            output = prioritizer.generate_yaml()
        elif args.format == 'json':
            output = json.dumps([{
                'task_id': d.preempt_task_id,
                'preempt_type': d.preempt_type,
                'interrupt_level': d.interrupt_level,
                'should_preempt': d.should_preempt,
                'confidence': d.confidence,
                'net_benefit': d.net_benefit,
                'action': d.action,
                'reason': d.reason,
                'conditions': [{'id': c.condition_id, 'met': c.met} for c in d.conditions],
                'notifications': d.notifications_required
            } for d in decisions], indent=2, ensure_ascii=False)
        else:
            output = prioritizer.generate_report()

        # 输出
        if args.output:
            Path(args.output).write_text(output, encoding='utf-8')
            print(f'决策报告已保存到: {args.output}', file=sys.stderr)
        else:
            print(output)

    except FileNotFoundError as e:
        print(f'错误: {e}', file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f'JSON解析错误: {e}', file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f'错误: {e}', file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
