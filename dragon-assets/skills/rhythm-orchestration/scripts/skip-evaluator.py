#!/usr/bin/env python3
"""
跳过决策评估器 (Skip Evaluator)

基于跳过协议提示词，对任务执行决策进行跳过评估。
支持5种跳过类型：trivial/redundancy/context/risk/expertise

用法:
    python skip-evaluator.py --task-id TASK_001 --estimated-time 30 --complexity simple
    python skip-evaluator.py --input-json '{"task_id":"TASK_001","estimated_time":30}'
"""

import argparse
import json
import sys
from dataclasses import dataclass, field, asdict
from typing import Optional
from pathlib import Path
from datetime import datetime


@dataclass
class SkipCondition:
    """跳过条件"""
    condition_id: str
    description: str
    met: bool
    confidence: float = 0.0
    details: str = ""


@dataclass
class SkipDecision:
    """跳过决策"""
    task_id: str
    skip_type: str  # trivial_skip/redundancy_skip/context_skip/risk_skip/expertise_skip
    should_skip: bool
    confidence: float
    reason: str
    action: str
    conditions: list[SkipCondition] = field(default_factory=list)
    quality_impact: str = "neutral"  # positive/neutral/negative
    override: bool = False
    estimated_time_saved_ms: int = 0


class SkipEvaluator:
    """跳过决策评估器核心类"""

    # 跳过类型配置
    SKIP_TYPES = {
        'trivial_skip': {
            'name': '微任务跳过',
            'conditions': [
                {'id': 'time_threshold', 'description': '预估时间 < 30秒', 'threshold': 30000},
                {'id': 'complexity_simple', 'description': '复杂度为 simple', 'expected': 'simple'},
                {'id': 'no_dependencies', 'description': '无外部依赖', 'expected': True},
                {'id': 'high_confidence', 'description': '置信度 >= 0.95', 'threshold': 0.95}
            ],
            'max_pause_duration': '0s',
            'override': False
        },
        'redundancy_skip': {
            'name': '冗余跳过',
            'conditions': [
                {'id': 'cache_hit', 'description': '缓存命中', 'expected': True},
                {'id': 'freshness', 'description': '结果新鲜度 < 2小时', 'threshold': 7200},
                {'id': 'source_task_exists', 'description': '源任务存在', 'expected': True},
                {'id': 'result_complete', 'description': '结果完整可复用', 'expected': True}
            ],
            'max_pause_duration': '0s',
            'override': False
        },
        'context_skip': {
            'name': '上下文跳过',
            'conditions': [
                {'id': 'version_match', 'description': '上下文版本一致', 'expected': True},
                {'id': 'deps_completed', 'description': '前置任务全部成功', 'expected': True},
                {'id': 'within_window', 'description': '在有效时间窗口内', 'expected': True},
                {'id': 'intent_unchanged', 'description': '用户需求未变更', 'expected': True}
            ],
            'max_pause_duration': '0s',
            'override': False
        },
        'risk_skip': {
            'name': '风险跳过',
            'conditions': [
                {'id': 'low_risk', 'description': '风险评分 < 0.7', 'threshold': 0.7},
                {'id': 'security_approved', 'description': '安全评估已通过', 'expected': True},
                {'id': 'resource_available', 'description': '资源充足', 'expected': True},
                {'id': 'no_regression', 'description': '无回归风险', 'expected': True}
            ],
            'max_pause_duration': '0s',
            'override': False
        },
        'expertise_skip': {
            'name': '能力跳过',
            'conditions': [
                {'id': 'has_capability', 'description': '当前Agent有能力执行', 'expected': True},
                {'id': 'no_external_tools', 'description': '无需外部工具', 'expected': True},
                {'id': 'has_permissions', 'description': '权限充足', 'expected': True}
            ],
            'max_pause_duration': '0s',
            'override': False
        }
    }

    def __init__(self):
        self.decision: Optional[SkipDecision] = None

    def evaluate(self, task_data: dict) -> SkipDecision:
        """评估跳过决策"""
        task_id = task_data.get('task_id', 'UNKNOWN')

        # 第一步：识别跳过类型
        skip_type = self._identify_skip_type(task_data)

        if not skip_type:
            # 不应该跳过
            return SkipDecision(
                task_id=task_id,
                skip_type='none',
                should_skip=False,
                confidence=1.0,
                reason='不满足任何跳过条件',
                action='normal_execution'
            )

        # 第二步：评估跳过条件
        conditions = self._evaluate_conditions(skip_type, task_data)

        # 第三步：计算跳过置信度
        confidence = self._calculate_confidence(skip_type, conditions)

        # 第四步：确定动作
        should_skip = confidence >= 0.85 and self._all_critical_conditions_met(conditions)

        action = self._determine_action(skip_type, should_skip, task_data)

        # 构建决策
        self.decision = SkipDecision(
            task_id=task_id,
            skip_type=skip_type,
            should_skip=should_skip,
            confidence=confidence,
            reason=self._build_reason(skip_type, conditions),
            action=action,
            conditions=conditions,
            quality_impact=self._assess_quality_impact(skip_type, should_skip),
            override=self.SKIP_TYPES.get(skip_type, {}).get('override', False),
            estimated_time_saved_ms=self._estimate_time_saved(task_data)
        )

        return self.decision

    def _identify_skip_type(self, task_data: dict) -> Optional[str]:
        """识别跳过类型"""
        estimated_time = task_data.get('estimated_time_ms', 0)
        complexity = task_data.get('complexity', 'medium')
        cache_hit = task_data.get('cache_hit', False)
        cache_freshness = task_data.get('cache_freshness_s', 99999)
        context_version = task_data.get('context_version', 1)
        current_version = task_data.get('current_version', 1)
        risk_score = task_data.get('risk_score', 0.0)
        security_approved = task_data.get('security_approved', True)
        has_capability = task_data.get('agent_has_capability', True)
        has_dependencies = task_data.get('has_external_dependencies', False)

        # 微任务跳过检查
        if (estimated_time < 30000 and
            complexity == 'simple' and
            not has_dependencies):
            return 'trivial_skip'

        # 冗余跳过检查
        if cache_hit and cache_freshness < 7200:
            return 'redundancy_skip'

        # 上下文跳过检查
        if (context_version < current_version or
            not task_data.get('deps_completed', True)):
            return 'context_skip'

        # 风险跳过检查
        if risk_score >= 0.7 or not security_approved:
            return 'risk_skip'

        # 能力跳过检查
        if not has_capability:
            return 'expertise_skip'

        return None

    def _evaluate_conditions(self, skip_type: str, task_data: dict) -> list[SkipCondition]:
        """评估跳过条件"""
        config = self.SKIP_TYPES.get(skip_type, {})
        conditions_config = config.get('conditions', [])
        conditions = []

        for cfg in conditions_config:
            cond_id = cfg['id']
            condition = SkipCondition(
                condition_id=cond_id,
                description=cfg['description'],
                met=False,
                confidence=0.0
            )

            # 根据条件类型评估
            if cond_id == 'time_threshold':
                threshold = cfg.get('threshold', 30000)
                actual = task_data.get('estimated_time_ms', 0)
                condition.met = actual < threshold
                condition.confidence = min(1.0, actual / threshold) if condition.met else 0.5
                condition.details = f'{actual}ms < {threshold}ms'

            elif cond_id == 'complexity_simple':
                actual = task_data.get('complexity', 'medium')
                condition.met = actual == cfg.get('expected', 'simple')
                condition.confidence = 1.0 if condition.met else 0.8
                condition.details = f'complexity={actual}'

            elif cond_id == 'no_dependencies':
                actual = task_data.get('has_external_dependencies', False)
                condition.met = not actual
                condition.confidence = 1.0
                condition.details = f'has_dependencies={actual}'

            elif cond_id == 'high_confidence':
                condition.met = task_data.get('confidence', 0.0) >= cfg.get('threshold', 0.95)
                condition.confidence = task_data.get('confidence', 0.0)
                condition.details = f'confidence={condition.confidence}'

            elif cond_id == 'cache_hit':
                actual = task_data.get('cache_hit', False)
                condition.met = actual == cfg.get('expected', True)
                condition.confidence = 1.0
                condition.details = f'cache_hit={actual}'

            elif cond_id == 'freshness':
                actual = task_data.get('cache_freshness_s', 99999)
                threshold = cfg.get('threshold', 7200)
                condition.met = actual < threshold
                condition.confidence = min(1.0, actual / threshold) if condition.met else 0.3
                condition.details = f'freshness={actual}s < {threshold}s'

            elif cond_id == 'source_task_exists':
                condition.met = bool(task_data.get('source_task_id'))
                condition.confidence = 1.0 if condition.met else 0.5
                condition.details = f'source_task={task_data.get("source_task_id")}'

            elif cond_id == 'result_complete':
                condition.met = task_data.get('result_complete', False)
                condition.confidence = 1.0 if condition.met else 0.6
                condition.details = f'result_complete={condition.met}'

            elif cond_id == 'version_match':
                cv = task_data.get('context_version', 1)
                expected = cfg.get('expected', True)
                condition.met = (cv == current_version()) if expected else cv < current_version()
                condition.confidence = 1.0
                condition.details = f'context_version={cv}'

            elif cond_id == 'deps_completed':
                condition.met = task_data.get('deps_completed', True)
                condition.confidence = 1.0 if condition.met else 0.4
                condition.details = f'deps_completed={condition.met}'

            elif cond_id == 'within_window':
                condition.met = task_data.get('within_time_window', True)
                condition.confidence = 0.9 if condition.met else 0.5
                condition.details = f'within_window={condition.met}'

            elif cond_id == 'intent_unchanged':
                condition.met = task_data.get('user_intent_unchanged', True)
                condition.confidence = 0.8 if condition.met else 0.3
                condition.details = f'intent_unchanged={condition.met}'

            elif cond_id == 'low_risk':
                actual = task_data.get('risk_score', 0.0)
                threshold = cfg.get('threshold', 0.7)
                condition.met = actual < threshold
                condition.confidence = 1.0 - actual if condition.met else actual
                condition.details = f'risk_score={actual} < {threshold}'

            elif cond_id == 'security_approved':
                actual = task_data.get('security_approved', True)
                condition.met = actual == cfg.get('expected', True)
                condition.confidence = 1.0
                condition.details = f'security_approved={actual}'

            elif cond_id == 'resource_available':
                condition.met = task_data.get('resource_available', True)
                condition.confidence = 0.9 if condition.met else 0.4
                condition.details = f'resource_available={condition.met}'

            elif cond_id == 'no_regression':
                condition.met = task_data.get('no_regression_risk', True)
                condition.confidence = 0.8 if condition.met else 0.5
                condition.details = f'no_regression_risk={condition.met}'

            elif cond_id == 'has_capability':
                actual = task_data.get('agent_has_capability', True)
                condition.met = actual == cfg.get('expected', True)
                condition.confidence = 1.0
                condition.details = f'agent_has_capability={actual}'

            elif cond_id == 'no_external_tools':
                condition.met = not task_data.get('needs_external_tools', False)
                condition.confidence = 0.9
                condition.details = f'needs_external_tools={task_data.get("needs_external_tools", False)}'

            elif cond_id == 'has_permissions':
                condition.met = task_data.get('has_required_permissions', True)
                condition.confidence = 1.0 if condition.met else 0.3
                condition.details = f'has_permissions={condition.met}'

            conditions.append(condition)

        return conditions

    def _calculate_confidence(self, skip_type: str, conditions: list[SkipCondition]) -> float:
        """计算跳过置信度"""
        if not conditions:
            return 0.0

        weights = {
            'trivial_skip': [0.3, 0.25, 0.2, 0.25],
            'redundancy_skip': [0.3, 0.3, 0.2, 0.2],
            'context_skip': [0.3, 0.3, 0.2, 0.2],
            'risk_skip': [0.3, 0.25, 0.2, 0.25],
            'expertise_skip': [0.4, 0.3, 0.3]
        }

        w = weights.get(skip_type, [0.25] * len(conditions))
        total_weight = sum(w)
        weighted_sum = sum(c.confidence * c.met * w[i] for i, c in enumerate(conditions))
        normalized_confidence = weighted_sum / total_weight if total_weight > 0 else 0.0

        return min(1.0, normalized_confidence)

    def _all_critical_conditions_met(self, conditions: list[SkipCondition]) -> bool:
        """检查所有关键条件是否满足"""
        return all(c.met for c in conditions)

    def _determine_action(self, skip_type: str, should_skip: bool, task_data: dict) -> str:
        """确定执行动作"""
        if not should_skip:
            return 'normal_execution'

        action_map = {
            'trivial_skip': 'return_minimal_result',
            'redundancy_skip': 'reuse_cached_result',
            'context_skip': 'reassess_context',
            'risk_skip': 'escalate_for_review',
            'expertise_skip': 'delegate_to_specialist'
        }

        base_action = action_map.get(skip_type, 'skip_task')

        # 如果是缓存跳过，记录来源
        if skip_type == 'redundancy_skip' and should_skip:
            source_task = task_data.get('source_task_id', 'unknown')
            return f'reuse_result_from:{source_task}'

        return base_action

    def _build_reason(self, skip_type: str, conditions: list[SkipCondition]) -> str:
        """构建跳过原因"""
        met_conditions = [c.description for c in conditions if c.met]
        not_met_conditions = [c.description for c in conditions if not c.met]

        reason = f"{self.SKIP_TYPES[skip_type]['name']}: "
        reason += ", ".join(met_conditions[:2])

        if not_met_conditions:
            reason += f" (未满足: {not_met_conditions[0]})"

        return reason

    def _assess_quality_impact(self, skip_type: str, should_skip: bool) -> str:
        """评估质量影响"""
        positive_types = ['trivial_skip', 'redundancy_skip']
        neutral_types = ['context_skip']
        risk_types = ['risk_skip', 'expertise_skip']

        if not should_skip:
            return 'neutral'

        if skip_type in positive_types:
            return 'positive'
        elif skip_type in neutral_types:
            return 'neutral'
        else:
            return 'negative'

    def _estimate_time_saved(self, task_data: dict) -> int:
        """估算节省时间"""
        estimated_time = task_data.get('estimated_time_ms', 0)

        type_savings = {
            'trivial_skip': 0.95,
            'redundancy_skip': 1.0,
            'context_skip': 0.0,
            'risk_skip': 0.0,
            'expertise_skip': 0.5
        }

        skip_type = self.decision.skip_type if self.decision else None
        savings_ratio = type_savings.get(skip_type, 0.0)

        return int(estimated_time * savings_ratio)

    def generate_report(self) -> str:
        """生成跳过决策报告"""
        if not self.decision:
            return "No decision made yet. Run evaluate() first."

        d = self.decision
        lines = [
            "=" * 60,
            "跳过决策评估报告",
            "=" * 60,
            f"任务ID: {d.task_id}",
            f"跳过类型: {d.skip_type}",
            f"跳过决策: {'是' if d.should_skip else '否'}",
            f"置信度: {d.confidence:.2%}",
            f"预估节省: {d.estimated_time_saved_ms}ms",
            "",
            "触发条件:",
        ]

        for cond in d.conditions:
            status = "[✓]" if cond.met else "[✗]"
            lines.append(f"  {status} {cond.description}")
            if cond.details:
                lines.append(f"      {cond.details}")

        lines.extend([
            "",
            f"决策理由: {d.reason}",
            f"执行动作: {d.action}",
            f"质量影响: {d.quality_impact}",
            f"覆盖标志: {d.override}",
            "=" * 60,
        ])

        return "\n".join(lines)

    def generate_yaml(self) -> str:
        """生成YAML格式输出"""
        if not self.decision:
            return "No decision made yet."

        d = self.decision
        lines = [
            "skip_decision:",
            f"  task_id: \"{d.task_id}\"",
            f"  skip_type: \"{d.skip_type}\"",
            f"  should_skip: {str(d.should_skip).lower()}",
            f"  confidence: {d.confidence:.2f}",
            f"  reason: \"{d.reason}\"",
            f"  action: \"{d.action}\"",
            f"  quality_impact: \"{d.quality_impact}\"",
            f"  override: {str(d.override).lower()}",
            f"  time_saved_ms: {d.estimated_time_saved_ms}",
            "  conditions:",
        ]

        for cond in d.conditions:
            lines.append(f"    - id: \"{cond.condition_id}\"")
            lines.append(f"      description: \"{cond.description}\"")
            lines.append(f"      met: {str(cond.met).lower()}")
            lines.append(f"      confidence: {cond.confidence:.2f}")
            if cond.details:
                lines.append(f"      details: \"{cond.details}\"")

        return "\n".join(lines)


def current_version() -> int:
    """获取当前上下文版本"""
    return 1


def main():
    parser = argparse.ArgumentParser(
        description='跳过决策评估器 - 基于跳过协议评估任务是否应跳过',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python skip-evaluator.py --task-id TASK_001 --estimated-time 25 --complexity simple
  python skip-evaluator.py --input-json '{"task_id":"TASK_001","cache_hit":true}'
  python skip-evaluator.py --task-id TASK_002 --risk-score 0.8 --security-approved false

跳过类型:
  trivial_skip      - 微任务跳过 (time<30s, simple, no deps)
  redundancy_skip   - 冗余跳过 (cache_hit, fresh<2h)
  context_skip      - 上下文跳过 (version_mismatch, deps_failed)
  risk_skip         - 风险跳过 (risk>0.7, !security_approved)
  expertise_skip    - 能力跳过 (!has_capability)
'''
    )

    parser.add_argument('--task-id', help='任务ID')
    parser.add_argument('--estimated-time', type=int, dest='estimated_time',
                        help='预估执行时间(毫秒)')
    parser.add_argument('--complexity', choices=['simple', 'medium', 'complex'],
                        default='medium', help='任务复杂度')
    parser.add_argument('--cache-hit', type=lambda x: x.lower() == 'true',
                        dest='cache_hit', help='缓存命中')
    parser.add_argument('--cache-freshness', type=int, dest='cache_freshness',
                        help='缓存新鲜度(秒)')
    parser.add_argument('--risk-score', type=float, dest='risk_score',
                        help='风险评分(0.0-1.0)')
    parser.add_argument('--security-approved', type=lambda x: x.lower() == 'true',
                        dest='security_approved', default='true',
                        help='安全评估是否通过')
    parser.add_argument('--input-json', dest='input_json', help='JSON格式输入')
    parser.add_argument('--output', '-o', choices=['text', 'yaml', 'json'],
                        default='text', help='输出格式')
    parser.add_argument('--verbose', '-v', action='store_true')

    args = parser.parse_args()

    try:
        # 构建任务数据
        if args.input_json:
            task_data = json.loads(args.input_json)
        else:
            task_data = {
                'task_id': args.task_id or 'UNKNOWN',
                'estimated_time_ms': args.estimated_time or 0,
                'complexity': args.complexity,
                'cache_hit': args.cache_hit if args.cache_hit is not None else False,
                'cache_freshness_s': args.cache_freshness or 99999,
                'risk_score': args.risk_score or 0.0,
                'security_approved': args.security_approved,
            }

        # 评估跳过决策
        evaluator = SkipEvaluator()
        decision = evaluator.evaluate(task_data)

        # 输出结果
        if args.output == 'yaml':
            print(evaluator.generate_yaml())
        elif args.output == 'json':
            print(json.dumps(asdict(decision), indent=2, ensure_ascii=False))
        else:
            print(evaluator.generate_report())

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
