#!/usr/bin/env python3
"""
打断成本计算器
Interruption Cost Calculator
根据打断成本矩阵计算打断代价
"""

import json
import sys
from dataclasses import dataclass, asdict
from typing import Optional
from enum import Enum


class TaskFocus(Enum):
    DEEP = "深度"
    MEDIUM = "中度"
    LOW = "低度"


class FlowState(Enum):
    IN_FLOW = "in_flow"
    NOT_IN_FLOW = "not_in_flow"


@dataclass
class InterruptionContext:
    """打断上下文"""
    task_name: str = ""
    task_focus: str = "中度"
    flow_state: bool = False
    cognitive_load: str = "低"
    session_duration: int = 0

    # 认知成本
    context_switch_time: float = 3.0
    mental_state_recovery: float = 2.0
    deep_work_loss: float = 5.0

    # 情感成本
    frustration_level: float = 3.0
    trust_impact: float = 1.0
    anxiety_increase: float = 2.0

    # 效率成本
    task_completion_delay: float = 5.0
    flow_state_break: bool = False
    productivity_loss: float = 0.2


@dataclass
class CardBenefit:
    """发牌收益"""
    uncertainty_reduction: str = "medium"
    action_clarity: str = "medium"
    efficiency_improvement: float = 0.0


@dataclass
class CostBreakdown:
    """成本分解"""
    cognitive_cost: float
    emotional_cost: float
    efficiency_cost: float
    flow_penalty: float
    focus_penalty: float
    total_cost: float


@dataclass
class BenefitBreakdown:
    """收益分解"""
    uncertainty_value: float
    clarity_value: float
    efficiency_gain: float
    total_benefit: float


@dataclass
class EvaluationResult:
    """评估结果"""
    decision: str
    cost_breakdown: CostBreakdown
    benefit_breakdown: BenefitBreakdown
    net_value: float
    risk_adjusted_threshold: float
    recommendation: str


class InterruptionCostCalculator:
    """打断成本计算器"""

    def __init__(self, config_path: Optional[str] = None):
        self.cost_weights = {
            "cognitive": {"deep_work": 2.0, "mental_state": 1.5, "default": 1.0},
            "emotional": {"frustration": 1.0, "trust": 0.5, "anxiety": 0.5},
            "efficiency": {"delay": 1.0, "loss": 60},
            "flow_penalty": 15,
            "focus_penalty": {"深度": 10, "中度": 5, "低度": 0}
        }
        self.benefit_values = {
            "high": 5, "medium": 3, "low": 1
        }
        if config_path:
            self.load_config(config_path)

    def load_config(self, config_path: str):
        """加载配置文件"""
        import yaml
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            if 'interruption_cost' in config:
                ic = config['interruption_cost']
                self.cost_weights = {
                    "cognitive": ic.get('cognitive', self.cost_weights["cognitive"]),
                    "emotional": ic.get('emotional', self.cost_weights["emotional"]),
                    "efficiency": ic.get('efficiency', self.cost_weights["efficiency"]),
                    "flow_penalty": ic.get('flow_penalty', self.cost_weights["flow_penalty"]),
                    "focus_penalty": ic.get('focus_penalty', self.cost_weights["focus_penalty"])
                }
        except Exception:
            pass

    def calculate_cost(self, context: InterruptionContext) -> CostBreakdown:
        """计算总打断成本"""

        # 1. 认知成本
        cognitive_multiplier = self.cost_weights["cognitive"]["deep_work"] if context.task_focus == "深度" \
            else self.cost_weights["cognitive"]["mental_state"] if context.flow_state \
            else self.cost_weights["cognitive"]["default"]

        cognitive_cost = (
            context.context_switch_time +
            context.mental_state_recovery +
            context.deep_work_loss * cognitive_multiplier
        )

        # 2. 情感成本（转换为时间当量）
        emotional_cost = (
            context.frustration_level * self.cost_weights["emotional"]["frustration"] +
            context.trust_impact * self.cost_weights["emotional"]["trust"] +
            context.anxiety_increase * self.cost_weights["emotional"]["anxiety"]
        )

        # 3. 效率成本
        efficiency_cost = (
            context.task_completion_delay +
            context.productivity_loss * self.cost_weights["efficiency"]["loss"]
        )

        # 4. 心流破坏惩罚
        flow_penalty = self.cost_weights["flow_penalty"] if context.flow_state_break else 0

        # 5. 专注度惩罚
        focus_penalty = self.cost_weights["focus_penalty"].get(context.task_focus, 0)

        # 总成本
        total_cost = cognitive_cost + emotional_cost + efficiency_cost + flow_penalty + focus_penalty

        return CostBreakdown(
            cognitive_cost=round(cognitive_cost, 2),
            emotional_cost=round(emotional_cost, 2),
            efficiency_cost=round(efficiency_cost, 2),
            flow_penalty=round(flow_penalty, 2),
            focus_penalty=round(focus_penalty, 2),
            total_cost=round(total_cost, 2)
        )

    def calculate_benefit(self, card: CardBenefit) -> BenefitBreakdown:
        """计算发牌收益"""

        uncertainty_value = self.benefit_values.get(card.uncertainty_reduction, 2)
        clarity_value = self.benefit_values.get(card.action_clarity, 2)
        efficiency_gain = card.efficiency_improvement * 30  # 转换为分钟

        total_benefit = uncertainty_value + clarity_value + efficiency_gain

        return BenefitBreakdown(
            uncertainty_value=uncertainty_value,
            clarity_value=clarity_value,
            efficiency_gain=round(efficiency_gain, 2),
            total_benefit=round(total_benefit, 2)
        )

    def evaluate(self, context: InterruptionContext, card: CardBenefit) -> EvaluationResult:
        """评估打断是否值得"""

        cost = self.calculate_cost(context)
        benefit = self.calculate_benefit(card)

        # 计算净价值
        net_value = benefit.total_benefit - cost.total_cost

        # 风险调整
        risk_factor = 1.2 if context.flow_state_break or context.flow_state else 1.0
        risk_adjusted_threshold = 0 * risk_factor

        # 决策
        if net_value > risk_adjusted_threshold + 5:
            decision = "发牌"
            recommendation = f"建议发牌。发牌收益({benefit.total_benefit:.0f}分钟) > 打断成本({cost.total_cost:.0f}分钟)"
        elif net_value > risk_adjusted_threshold - 5:
            decision = "延后"
            delay = max(5, min(int(cost.total_cost - benefit.total_benefit), 60)
            recommendation = f"建议延后{delay}分钟后发送"
        else:
            decision = "沉默"
            recommendation = f"建议沉默。打断成本({cost.total_cost:.0f}分钟) > 发牌收益({benefit.total_benefit:.0f}分钟)"

        return EvaluationResult(
            decision=decision,
            cost_breakdown=cost,
            benefit_breakdown=benefit,
            net_value=round(net_value, 2),
            risk_adjusted_threshold=risk_adjusted_threshold,
            recommendation=recommendation
        )

    def export_result(self, result: EvaluationResult) -> dict:
        """导出评估结果"""
        return {
            "decision": result.decision,
            "cost_breakdown": asdict(result.cost_breakdown),
            "benefit_breakdown": asdict(result.benefit_breakdown),
            "net_value": result.net_value,
            "risk_adjusted_threshold": result.risk_adjusted_threshold,
            "recommendation": result.recommendation
        }


def calculate_scenario_costs():
    """计算各场景标准成本"""
    scenarios = {
        "深度工作": InterruptionContext(
            task_name="深度工作",
            task_focus="深度",
            flow_state=True,
            cognitive_load="高",
            context_switch_time=5,
            mental_state_recovery=5,
            deep_work_loss=10,
            frustration_level=7,
            trust_impact=3,
            anxiety_increase=4,
            task_completion_delay=15,
            flow_state_break=True,
            productivity_loss=0.4
        ),
        "创意工作": InterruptionContext(
            task_name="创意工作",
            task_focus="深度",
            flow_state=True,
            cognitive_load="高",
            context_switch_time=3,
            mental_state_recovery=4,
            deep_work_loss=8,
            frustration_level=6,
            trust_impact=2,
            anxiety_increase=3,
            task_completion_delay=10,
            flow_state_break=True,
            productivity_loss=0.35
        ),
        "普通工作": InterruptionContext(
            task_name="普通工作",
            task_focus="中度",
            flow_state=False,
            cognitive_load="低",
            context_switch_time=2,
            mental_state_recovery=2,
            deep_work_loss=3,
            frustration_level=3,
            trust_impact=1,
            anxiety_increase=2,
            task_completion_delay=5,
            flow_state_break=False,
            productivity_loss=0.15
        ),
        "空闲/休息": InterruptionContext(
            task_name="空闲/休息",
            task_focus="低度",
            flow_state=False,
            cognitive_load="低",
            context_switch_time=1,
            mental_state_recovery=1,
            deep_work_loss=0,
            frustration_level=2,
            trust_impact=1,
            anxiety_increase=1,
            task_completion_delay=2,
            flow_state_break=False,
            productivity_loss=0.05
        )
    }

    calculator = InterruptionCostCalculator()
    results = {}

    for name, ctx in scenarios.items():
        cost = calculator.calculate_cost(ctx)
        results[name] = {
            "total_cost_minutes": cost.total_cost,
            "breakdown": asdict(cost)
        }

    return results


def main():
    """命令行入口"""
    if len(sys.argv) >= 3:
        try:
            with open(sys.argv[1], 'r', encoding='utf-8') as f:
                ctx_data = json.load(f)
            with open(sys.argv[2], 'r', encoding='utf-8') as f:
                card_data = json.load(f)

            context = InterruptionContext(**ctx_data)
            card = CardBenefit(**card_data)

            calculator = InterruptionCostCalculator()
            result = calculator.evaluate(context, card)
            print(json.dumps(calculator.export_result(result), ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"计算失败: {e}")
            sys.exit(1)
    else:
        # 输出场景标准成本
        results = calculate_scenario_costs()
        print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
