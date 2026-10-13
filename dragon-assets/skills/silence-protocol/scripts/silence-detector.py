#!/usr/bin/env python3
"""
沉默检测器
Silence Detector
根据上下文评估是否应沉默
"""

import json
import sys
from dataclasses import dataclass, asdict
from typing import Optional
from enum import Enum


class SilenceDecision(Enum):
    MANDATORY_SILENCE = "mandatory_silence"
    DEFAULT_SILENCE = "default_silence"
    CONDITIONAL_SILENCE = "conditional_silence"
    NO_SILENCE = "no_silence"


class SilenceDuration(Enum):
    IMMEDIATE = 0
    SHORT = 5
    MEDIUM = 15
    LONG = 30
    SESSION = -1
    PERMANENT = -2


@dataclass
class UserContext:
    """用户上下文"""
    flow_state: bool = False
    task_complexity: float = 5.0  # 1-10
    cognitive_load: float = 5.0  # 1-10
    user_state: str = "normal"  # deep_work/creative/normal/idle/rest
    work_start_time: Optional[str] = None
    session_duration: int = 0  # minutes
    recent_interactions: int = 0
    is_undisturbed: bool = True
    time_of_day: str = "work_hours"  # work_hours/meeting/rest/night
    user_preference_override: Optional[str] = None


@dataclass
class CardContext:
    """卡片上下文"""
    card_type: str = "notification"  # notification/task/reminder/update/urgent
    priority: str = "normal"  # critical/high/normal/low
    uncertainty_reduction: float = 0.5  # 0-1
    action_clarity: float = 0.5  # 0-1
    sender: str = "system"
    deadline: Optional[str] = None
    requires_response: bool = False


@dataclass
class SilenceEvaluation:
    """沉默评估结果"""
    decision: SilenceDecision
    duration: SilenceDuration
    confidence: float  # 0-1
    reasons: list
    cost: float
    benefit: float
    net_value: float
    alternative: str


@dataclass
class SilenceCondition:
    """沉默条件"""
    condition_type: str  # mandatory/default/conditional
    condition_expr: str
    reason: str
    silence_duration: SilenceDuration
    alternative: str
    priority: int = 1


class SilenceDetector:
    """沉默检测器"""

    def __init__(self, config_path: Optional[str] = None):
        self.conditions: list[SilenceCondition] = []
        self.cost_thresholds = {
            "high": 15,
            "medium": 8,
            "low": 3
        }
        if config_path:
            self.load_config(config_path)
        else:
            self._init_default_conditions()

    def _init_default_conditions(self):
        """初始化默认沉默条件"""
        self.conditions = [
            # 必须沉默条件
            SilenceCondition(
                condition_type="mandatory",
                condition_expr="flow_state == True",
                reason="心流状态，打断代价极高",
                silence_duration=SilenceDuration.SESSION,
                alternative="延迟到心流结束",
                priority=1
            ),
            SilenceCondition(
                condition_type="mandatory",
                condition_expr="task_complexity >= 8 AND cognitive_load >= 7",
                reason="复杂认知任务，上下文切换成本高",
                silence_duration=SilenceDuration.LONG,
                alternative="任务完成后发送",
                priority=2
            ),
            SilenceCondition(
                condition_type="mandatory",
                condition_expr="user_state == 'deep_work'",
                reason="深度工作状态保护",
                silence_duration=SilenceDuration.SESSION,
                alternative="深度工作结束后发送",
                priority=1
            ),
            SilenceCondition(
                condition_type="mandatory",
                condition_expr="time_of_day == 'rest'",
                reason="休息时段不打扰",
                silence_duration=SilenceDuration.LONG,
                alternative="用户清醒后发送",
                priority=2
            ),
            SilenceCondition(
                condition_type="mandatory",
                condition_expr="is_undisturbed == False",
                reason="用户设置勿扰模式",
                silence_duration=SilenceDuration.PERMANENT,
                alternative="用户取消勿扰后发送",
                priority=1
            ),

            # 默认沉默条件
            SilenceCondition(
                condition_type="default",
                condition_expr="task_complexity >= 6",
                reason="中等复杂度任务",
                silence_duration=SilenceDuration.MEDIUM,
                alternative="用户空闲时发送",
                priority=3
            ),
            SilenceCondition(
                condition_type="default",
                condition_expr="recent_interactions < 2",
                reason="用户交互频率低",
                silence_duration=SilenceDuration.SHORT,
                alternative="下次交互后发送",
                priority=4
            ),

            # 条件沉默
            SilenceCondition(
                condition_type="conditional",
                condition_expr="card_type == 'notification' AND priority == 'low'",
                reason="低优先级通知",
                silence_duration=SilenceDuration.MEDIUM,
                alternative="累积后发送摘要",
                priority=5
            ),
            SilenceCondition(
                condition_type="conditional",
                condition_expr="card_type == 'update' AND uncertainty_reduction < 0.3",
                reason="不确定性减少低的信息更新",
                silence_duration=SilenceDuration.SHORT,
                alternative="用户主动请求",
                priority=5
            ),
        ]

    def load_config(self, config_path: str):
        """从YAML加载配置"""
        import yaml
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            self._load_conditions_from_config(config)
        except Exception as e:
            print(f"配置加载失败: {e}, 使用默认条件")
            self._init_default_conditions()

    def _load_conditions_from_config(self, config: dict):
        """从配置加载沉默条件"""
        self.conditions = []
        if 'silence_conditions' not in config:
            self._init_default_conditions()
            return

        for cond_type in ['mandatory_silence', 'default_silence', 'conditional_silence']:
            if cond_type in config['silence_conditions']:
                for item in config['silence_conditions'][cond_type]:
                    stype = "mandatory" if "mandatory" in cond_type else \
                            "default" if "default" in cond_type else "conditional"
                    self.conditions.append(SilenceCondition(
                        condition_type=stype,
                        condition_expr=item.get('condition', ''),
                        reason=item.get('reason', ''),
                        silence_duration=self._parse_duration(item.get('silence_duration', 'medium')),
                        alternative=item.get('alternative', 'later'),
                        priority=item.get('priority', 5)
                    ))

    def _parse_duration(self, duration_str: str) -> SilenceDuration:
        """解析沉默时长"""
        duration_map = {
            'immediate': SilenceDuration.IMMEDIATE,
            'short': SilenceDuration.SHORT,
            'medium': SilenceDuration.MEDIUM,
            'long': SilenceDuration.LONG,
            'session': SilenceDuration.SESSION,
            'permanent': SilenceDuration.PERMANENT,
        }
        return duration_map.get(duration_str.lower(), SilenceDuration.MEDIUM)

    def evaluate(self, user_ctx: UserContext, card_ctx: CardContext) -> SilenceEvaluation:
        """评估是否应沉默"""

        # 1. 检查用户显式偏好
        if user_ctx.user_preference_override:
            if user_ctx.user_preference_override == "always_silence":
                return SilenceEvaluation(
                    decision=SilenceDecision.MANDATORY_SILENCE,
                    duration=SilenceDuration.PERMANENT,
                    confidence=1.0,
                    reasons=["用户显式设置永远沉默"],
                    cost=0, benefit=0, net_value=0,
                    alternative="never_send"
                )
            elif user_ctx.user_preference_override == "never_silence":
                return SilenceEvaluation(
                    decision=SilenceDecision.NO_SILENCE,
                    duration=SilenceDuration.IMMEDIATE,
                    confidence=1.0,
                    reasons=["用户显式设置永不沉默"],
                    cost=0, benefit=0, net_value=0,
                    alternative="send_immediately"
                )

        # 2. 检查critical卡片绕过
        if card_ctx.priority == "critical":
            return SilenceEvaluation(
                decision=SilenceDecision.NO_SILENCE,
                duration=SilenceDuration.IMMEDIATE,
                confidence=1.0,
                reasons=["critical优先级卡片绕过沉默"],
                cost=0, benefit=10, net_value=10,
                alternative="immediate_delivery"
            )

        # 3. 按优先级评估沉默条件
        matched_conditions = []
        for cond in sorted(self.conditions, key=lambda c: c.priority):
            if self._matches_condition(cond, user_ctx, card_ctx):
                matched_conditions.append(cond)

        if not matched_conditions:
            return SilenceEvaluation(
                decision=SilenceDecision.NO_SILENCE,
                duration=SilenceDuration.IMMEDIATE,
                confidence=0.9,
                reasons=["无沉默条件匹配"],
                cost=0, benefit=self._estimate_benefit(card_ctx),
                net_value=self._estimate_benefit(card_ctx),
                alternative="immediate_delivery"
            )

        # 4. 选择最高优先级匹配条件
        best_match = matched_conditions[0]
        decision_map = {
            "mandatory": SilenceDecision.MANDATORY_SILENCE,
            "default": SilenceDecision.DEFAULT_SILENCE,
            "conditional": SilenceDecision.CONDITIONAL_SILENCE
        }

        cost = self._calculate_cost(user_ctx, card_ctx)
        benefit = self._estimate_benefit(card_ctx)

        return SilenceEvaluation(
            decision=decision_map.get(best_match.condition_type, SilenceDecision.DEFAULT_SILENCE),
            duration=best_match.silence_duration,
            confidence=0.85 if best_match.condition_type == "mandatory" else 0.7,
            reasons=[best_match.reason],
            cost=cost,
            benefit=benefit,
            net_value=benefit - cost,
            alternative=best_match.alternative
        )

    def _matches_condition(self, cond: SilenceCondition, user_ctx: UserContext, card_ctx: CardContext) -> bool:
        """检查条件是否匹配"""
        expr = cond.condition_expr

        try:
            # 简单表达式解析（避免eval安全风险）
            result = self._eval_simple_condition(expr, user_ctx, card_ctx)
            return result
        except Exception:
            return False

    def _eval_simple_condition(self, expr: str, user_ctx: UserContext, card_ctx: CardContext) -> bool:
        """评估简单条件表达式"""
        # 获取用户上下文属性
        user_attrs = asdict(user_ctx)
        card_attrs = asdict(card_ctx)

        # 简单AND/OR解析
        if ' AND ' in expr:
            parts = expr.split(' AND ')
            return all(self._eval_simple_condition(p.strip(), user_ctx, card_ctx) for p in parts)
        if ' OR ' in expr:
            parts = expr.split(' OR ')
            return any(self._eval_simple_condition(p.strip(), user_ctx, card_ctx) for p in parts)

        # 简单比较解析
        if ' == ' in expr:
            left, right = expr.split(' == ')
            left = left.strip()
            right = right.strip().strip('"\'')
            return str(user_attrs.get(left, card_attrs.get(left, '')) == right
        if ' >= ' in expr:
            left, right = expr.split(' >= ')
            try:
                val = float(user_attrs.get(left.strip(), 0))
                return val >= float(right.strip())
            except (ValueError, TypeError):
                return False
        if ' <= ' in expr:
            left, right = expr.split(' <= ')
            try:
                val = float(user_attrs.get(left.strip(), 0))
                return val <= float(right.strip())
            except (ValueError, TypeError):
                return False
        if ' > ' in expr:
            left, right = expr.split(' > ')
            try:
                val = float(user_attrs.get(left.strip(), 0))
                return val > float(right.strip())
            except (ValueError, TypeError):
                return False
        if ' < ' in expr:
            left, right = expr.split(' < ')
            try:
                val = float(user_attrs.get(left.strip(), 0))
                return val < float(right.strip())
            except (ValueError, TypeError):
                return False

        # 简单属性检查
        return user_attrs.get(expr.strip(), False) or card_attrs.get(expr.strip(), False)

    def _calculate_cost(self, user_ctx: UserContext, card_ctx: CardContext) -> float:
        """计算打断成本"""
        # 认知成本
        cognitive = 0
        if user_ctx.flow_state:
            cognitive += 15  # 心流打断惩罚
        cognitive += user_ctx.task_complexity * 1.5
        cognitive += user_ctx.cognitive_load * 1.0

        # 情感成本
        emotional = 3
        if user_ctx.flow_state:
            emotional += 7  # 心流打断挫败感

        # 效率成本
        efficiency = 5
        if user_ctx.task_complexity >= 7:
            efficiency += 10

        return cognitive + emotional + efficiency

    def _estimate_benefit(self, card_ctx: CardContext) -> float:
        """估算发牌收益"""
        benefit = 0
        benefit += card_ctx.uncertainty_reduction * 5
        benefit += card_ctx.action_clarity * 5
        if card_ctx.priority == "critical":
            benefit += 10
        elif card_ctx.priority == "high":
            benefit += 5
        return benefit

    def should_silence(self, user_ctx: UserContext, card_ctx: CardContext) -> tuple[bool, SilenceEvaluation]:
        """判断是否应沉默"""
        evaluation = self.evaluate(user_ctx, card_ctx)

        # 必须沉默直接返回
        if evaluation.decision == SilenceDecision.MANDATORY_SILENCE:
            return True, evaluation

        # 打断成本 > 发牌收益时沉默
        if evaluation.cost > evaluation.benefit:
            return True, evaluation

        # 低优先级卡片默认沉默
        if card_ctx.priority in ["low", "normal"] and evaluation.decision in [
            SilenceDecision.DEFAULT_SILENCE,
            SilenceDecision.CONDITIONAL_SILENCE
        ]:
            return True, evaluation

        return False, evaluation

    def export_result(self, evaluation: SilenceEvaluation) -> dict:
        """导出评估结果"""
        return {
            "decision": evaluation.decision.value,
            "duration": evaluation.duration.name,
            "confidence": evaluation.confidence,
            "reasons": evaluation.reasons,
            "cost": round(evaluation.cost, 2),
            "benefit": round(evaluation.benefit, 2),
            "net_value": round(evaluation.net_value, 2),
            "alternative": evaluation.alternative
        }


def main():
    """命令行入口"""
    if len(sys.argv) < 3:
        print("用法: python silence-detector.py <user_context.json> <card_context.json>")
        sys.exit(1)

    try:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            user_data = json.load(f)
        with open(sys.argv[2], 'r', encoding='utf-8') as f:
            card_data = json.load(f)

        user_ctx = UserContext(**user_data)
        card_ctx = CardContext(**card_data)

        detector = SilenceDetector()
        should_silence, evaluation = detector.should_silence(user_ctx, card_ctx)

        result = detector.export_result(evaluation)
        result["should_silence"] = should_silence

        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
