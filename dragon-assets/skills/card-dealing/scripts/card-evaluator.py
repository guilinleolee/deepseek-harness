#!/usr/bin/env python3
"""
Card Evaluator - 卡片质量评估器
Card Dealing Protocol - 发牌协议脚本

评估卡片质量和适配度，判断是否应该发送。

Usage:
    python card-evaluator.py --card-type action --context context.json
    python card-evaluator.py --evaluate-batch cards.json
    python card-evaluator.py --interactive
"""

import json
import argparse
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional, List
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


class CardType(Enum):
    """卡片类型枚举"""
    INFORMATION = "information"
    CONFIRMATION = "confirmation"
    RECOMMENDATION = "recommendation"
    ACTION = "action"
    WARNING = "warning"


@dataclass
class EvaluationContext:
    """评估上下文"""
    user_state: str = "idle"
    flow_state: str = "normal"
    interruption_cost: float = 0.0
    user_explicit_request: bool = False  # 用户主动请求
    recent_card_count: int = 0         # 最近发牌数量
    recent_time_window: int = 300       # 时间窗口(秒)


@dataclass
class EvaluationResult:
    """评估结果"""
    card_type: str
    quality_score: float              # 0.0-1.0 总体质量得分
    decision_correctness: float       # 决策正确性
    card_type_appropriateness: float   # 类型恰当性
    timing_appropriateness: float     # 时机恰当性
    user_value_delivered: float       # 用户价值交付
    recommendation: str              # send/delay/skip
    confidence: float                 # 评估置信度
    reasons: List[str]                # 评估理由
    warnings: List[str]               # 警告信息
    quality_gates_passed: List[str]   # 通过的质量门控
    quality_gates_failed: List[str]  # 未通过的质量门控


class CardEvaluator:
    """卡片质量评估器"""

    # 评估阈值
    QUALITY_THRESHOLD = 0.50          # 最低质量阈值
    HIGH_QUALITY_THRESHOLD = 0.70     # 高质量阈值
    MAX_RECENT_CARDS = 3             # 时间窗口内最大发牌数
    HIGH_INTERRUPTION_COST = 0.70    # 高打断成本阈值

    # 质量维度权重
    DIMENSION_WEIGHTS = {
        'decision_correctness': 0.35,
        'card_type_appropriateness': 0.30,
        'timing_appropriateness': 0.25,
        'user_value_delivered': 0.10
    }

    def __init__(self, config: Optional[dict] = None):
        """初始化评估器"""
        self.config = config or {}
        self._load_thresholds()

    def _load_thresholds(self):
        """从配置加载阈值"""
        self.QUALITY_THRESHOLD = self.config.get('quality_threshold', 0.50)
        self.HIGH_QUALITY_THRESHOLD = self.config.get(
            'high_quality_threshold', 0.70)
        self.MAX_RECENT_CARDS = self.config.get('max_recent_cards', 3)

    def evaluate_timing(self, context: EvaluationContext) -> tuple:
        """评估时机恰当性"""
        score = 1.0
        reasons = []
        warnings = []

        # 心流保护检查
        if context.flow_state == 'deep_flow':
            score *= 0.5
            reasons.append("心流状态: 降低时机得分")
            warnings.append("心流保护: 高打断成本场景")

        # 用户打字中检查
        if context.user_state == 'typing':
            score *= 0.6
            reasons.append("用户打字中: 降低时机得分")

        # 打断成本评估
        if context.interruption_cost >= self.HIGH_INTERRUPTION_COST:
            score *= (1.0 - context.interruption_cost * 0.3)
            reasons.append(f"高打断成本({context.interruption_cost:.2f})")

        # 用户主动请求：提高得分
        if context.user_explicit_request:
            score = min(1.0, score * 1.2)
            reasons.append("用户主动请求: 提高时机得分")

        return max(0.0, score), reasons, warnings

    def evaluate_decision_correctness(self, card_type: CardType,
                                     context: EvaluationContext) -> tuple:
        """评估决策正确性"""
        score = 0.7
        reasons = []

        # 基于用户状态的决策评估
        if context.user_explicit_request:
            score = 0.9
            reasons.append("用户主动请求: 高置信度决策")
        elif context.flow_state == 'deep_flow' and card_type != CardType.WARNING:
            score = 0.4
            reasons.append("心流中非警告卡: 决策存在风险")
        elif context.interruption_cost >= self.HIGH_INTERRUPTION_COST:
            score = 0.5
            reasons.append(f"高打断成本场景: 决策需谨慎")

        return score, reasons

    def evaluate_card_type_appropriateness(self, card_type: CardType,
                                          context: EvaluationContext) -> tuple:
        """评估卡片类型恰当性"""
        score = 0.8
        reasons = []

        # 警告卡特殊情况
        if card_type == CardType.WARNING:
            if context.user_explicit_request:
                score = 1.0
                reasons.append("警告卡 + 用户请求: 最优匹配")
            else:
                score = 0.6
                reasons.append("警告卡: 需要明确风险依据")
            return score, reasons

        # 基于用户状态匹配
        if context.user_state == 'idle':
            if card_type in [CardType.INFORMATION, CardType.RECOMMENDATION]:
                score = 0.9
                reasons.append("用户空闲: 信息/推荐卡最优")
        elif context.user_state == 'working':
            if card_type == CardType.ACTION:
                score = 0.9
                reasons.append("用户工作中: 行动卡最优")
            elif card_type == CardType.INFORMATION:
                score = 0.5
                reasons.append("用户工作中: 信息卡可能打断")
        elif context.user_state == 'typing':
            score *= 0.4
            reasons.append("用户打字中: 大多数卡片不恰当")

        return max(0.0, score), reasons

    def evaluate_user_value(self, card_type: CardType,
                            context: EvaluationContext) -> tuple:
        """评估用户价值交付"""
        score = 0.6
        reasons = []

        # 用户主动请求
        if context.user_explicit_request:
            score = 0.9
            reasons.append("用户主动请求: 高预期价值")
        else:
            reasons.append("系统主动推送: 价值不确定")

        # 警告卡价值
        if card_type == CardType.WARNING:
            score = max(score, 0.85)
            reasons.append("警告卡: 风险规避价值高")

        # 确认卡价值
        if card_type == CardType.CONFIRMATION:
            score = max(score, 0.7)
            reasons.append("确认卡: 减少误解价值")

        return min(1.0, score), reasons

    def check_quality_gates(self, card_type: CardType,
                           context: EvaluationContext) -> tuple:
        """检查质量门控"""
        passed = []
        failed = []

        # 频率门控
        if context.recent_card_count >= self.MAX_RECENT_CARDS:
            failed.append(
                f"频率门控: 最近{self.MAX_RECENT_CARDS}张卡，时间窗口内")
        else:
            passed.append(
                f"频率门控: {context.recent_card_count}/{self.MAX_RECENT_CARDS}张")

        # 打断成本门控
        if (context.interruption_cost >= self.HIGH_INTERRUPTION_COST and
                card_type not in [CardType.WARNING, CardType.ACTION]):
            failed.append("打断成本门控: 高打断成本 + 非紧急卡片")
        else:
            passed.append("打断成本门控: 通过")

        # 心流门控
        if context.flow_state == 'deep_flow' and card_type == CardType.WARNING:
            passed.append("心流门控: 警告卡 override 心流保护")
        elif context.flow_state == 'deep_flow':
            failed.append("心流门控: 深心流状态不允许非警告卡")
        else:
            passed.append("心流门控: 正常状态")

        # 用户状态门控
        if context.user_state == 'typing' and card_type != CardType.WARNING:
            failed.append("用户状态门控: 用户打字中")
        else:
            passed.append("用户状态门控: 允许发牌")

        return passed, failed

    def determine_recommendation(self, quality_score: float,
                                passed_gates: list,
                                failed_gates: list) -> tuple:
        """确定发送建议"""
        # 有失败的门控
        if failed_gates:
            # 警告卡特殊处理
            if any('override' in g for g in passed_gates):
                return "send", "override_by_warning"
            return "skip", "quality_gate_failed"

        # 质量阈值检查
        if quality_score < self.QUALITY_THRESHOLD:
            return "delay", f"quality_below_threshold_{quality_score:.2f}"

        # 高质量直接发送
        if quality_score >= self.HIGH_QUALITY_THRESHOLD:
            return "send", "high_quality"

        return "send", "quality_acceptable"

    def calculate_confidence(self, context: EvaluationContext,
                              reasons: list, warnings: list) -> float:
        """计算评估置信度"""
        confidence = 0.7

        # 用户主动请求提高置信度
        if context.user_explicit_request:
            confidence += 0.15

        # 警告卡提高置信度
        # (card_type passed as string, check from context if needed)
        # 警告卡需要结合card_type，这里简化处理
        if context.interruption_cost >= self.HIGH_INTERRUPTION_COST:
            confidence -= 0.10

        # 有警告信息降低置信度
        confidence -= len(warnings) * 0.05

        return max(0.0, min(1.0, confidence))

    def evaluate(self, card_type: str, context: EvaluationContext) -> EvaluationResult:
        """主评估方法"""
        card_type_enum = CardType(card_type)

        # 各维度评估
        timing_score, timing_reasons, timing_warnings = self.evaluate_timing(context)
        decision_score, decision_reasons = self.evaluate_decision_correctness(
            card_type_enum, context)
        type_score, type_reasons = self.evaluate_card_type_appropriateness(
            card_type_enum, context)
        value_score, value_reasons = self.evaluate_user_value(
            card_type_enum, context)

        # 综合质量得分
        quality_score = (
            decision_score * self.DIMENSION_WEIGHTS['decision_correctness'] +
            type_score * self.DIMENSION_WEIGHTS['card_type_appropriateness'] +
            timing_score * self.DIMENSION_WEIGHTS['timing_appropriateness'] +
            value_score * self.DIMENSION_WEIGHTS['user_value_delivered']
        )

        # 收集理由和警告
        reasons = (timing_reasons + decision_reasons +
                   type_reasons + value_reasons)
        warnings = timing_warnings

        # 质量门控检查
        passed_gates, failed_gates = self.check_quality_gates(
            card_type_enum, context)

        if failed_gates:
            warnings.extend(failed_gates)

        # 确定建议
        recommendation, reason = self.determine_recommendation(
            quality_score, passed_gates, failed_gates)

        # 计算置信度
        confidence = self.calculate_confidence(context, reasons, warnings)

        return EvaluationResult(
            card_type=card_type,
            quality_score=quality_score,
            decision_correctness=decision_score,
            card_type_appropriateness=type_score,
            timing_appropriateness=timing_score,
            user_value_delivered=value_score,
            recommendation=recommendation,
            confidence=confidence,
            reasons=reasons,
            warnings=warnings,
            quality_gates_passed=passed_gates,
            quality_gates_failed=failed_gates
        )

    def evaluate_batch(self, cards: list,
                        contexts: list) -> List[EvaluationResult]:
        """批量评估"""
        results = []
        for card, ctx in zip(cards, contexts):
            result = self.evaluate(card.get('card_type', 'information'), ctx)
            results.append(result)
        return results


def interactive_evaluation():
    """交互式评估"""
    print("=== Card Evaluator 交互模式 ===")
    print("评估卡片发送决策，输入 'quit' 退出\n")

    evaluator = CardEvaluator()

    while True:
        print("\n请输入卡片类型 (information/confirmation/recommendation/action/warning):")
        card_type = input("> ").strip()
        if card_type.lower() in ['quit', 'exit', 'q']:
            break

        print("\n请输入用户状态 (idle/working/typing/meeting, 回车默认idle):")
        state = input("> ").strip() or "idle"

        print("\n心流状态 (normal/deep_flow, 回车默认normal):")
        flow = input("> ").strip() or "normal"

        print("\n打断成本 (0.0-1.0, 回车默认0.3):")
        cost = float(input("> ").strip() or "0.3")

        print("\n用户主动请求? (y/N):")
        request = input("> ").strip().lower() == 'y'

        print(f"\n最近发牌数量 (回车默认0):")
        recent = int(input("> ").strip() or "0")

        context = EvaluationContext(
            user_state=state,
            flow_state=flow,
            interruption_cost=cost,
            user_explicit_request=request,
            recent_card_count=recent
        )

        try:
            result = evaluator.evaluate(card_type, context)
            print(f"\n{'='*50}")
            print(f"评估结果:")
            print(f"  总体质量得分: {result.quality_score:.2f}")
            print(f"  决策正确性: {result.decision_correctness:.2f}")
            print(f"  类型恰当性: {result.card_type_appropriateness:.2f}")
            print(f"  时机恰当性: {result.timing_appropriateness:.2f}")
            print(f"  用户价值: {result.user_value_delivered:.2f}")
            print(f"  置信度: {result.confidence:.2f}")
            print(f"\n  建议: {result.recommendation.upper()}")
            print(f"  原因: {result.reasons}")
            print(f"\n  通过门控: {result.quality_gates_passed}")
            print(f"  失败门控: {result.quality_gates_failed}")
            print(f"  警告: {result.warnings}")
        except Exception as e:
            print(f"\n✗ 评估错误: {e}")


def main():
    parser = argparse.ArgumentParser(description="Card Evaluator - 卡片质量评估器")
    parser.add_argument('--card-type', type=str, required=True,
                        choices=['information', 'confirmation', 'recommendation',
                                 'action', 'warning'],
                        help='卡片类型')
    parser.add_argument('--context', type=str, help='上下文JSON字符串')
    parser.add_argument('--context-file', type=str, help='从文件加载上下文')
    parser.add_argument('--interactive', action='store_true', help='交互模式')
    parser.add_argument('--evaluate-batch', type=str,
                        help='批量评估文件')
    parser.add_argument('--output', type=str, help='输出文件路径')
    parser.add_argument('--state', type=str, default='idle',
                        choices=['idle', 'working', 'typing', 'meeting'],
                        help='用户状态')
    parser.add_argument('--flow', type=str, default='normal',
                        choices=['normal', 'deep_flow'],
                        help='心流状态')
    parser.add_argument('--cost', type=float, default=0.3,
                        help='打断成本 (0.0-1.0)')
    parser.add_argument('--request', action='store_true',
                        help='用户主动请求')
    parser.add_argument('--recent', type=int, default=0,
                        help='最近发牌数量')

    args = parser.parse_args()

    # 交互模式
    if args.interactive:
        interactive_evaluation()
        return

    # 加载上下文
    if args.context_file:
        with open(args.context_file, 'r', encoding='utf-8') as f:
            ctx_data = json.load(f)
        context = EvaluationContext(**ctx_data)
    elif args.context:
        context = EvaluationContext(
            user_state=args.state,
            flow_state=args.flow,
            interruption_cost=args.cost,
            user_explicit_request=args.request,
            recent_card_count=args.recent
        )
    else:
        context = EvaluationContext(
            user_state=args.state,
            flow_state=args.flow,
            interruption_cost=args.cost,
            user_explicit_request=args.request,
            recent_card_count=args.recent
        )

    evaluator = CardEvaluator()

    # 批量评估
    if args.evaluate_batch:
        with open(args.evaluate_batch, 'r', encoding='utf-8') as f:
            data = json.load(f)
        cards = data.get('cards', [])
        contexts = [
            EvaluationContext(**c) for c in data.get('contexts', [])
        ]
        results = evaluator.evaluate_batch(cards, contexts)
        output = [asdict(r) for r in results]
    else:
        # 单个评估
        result = evaluator.evaluate(args.card_type, context)
        output = asdict(result)

    print(json.dumps(output, ensure_ascii=False, indent=2))

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"\n结果已保存到: {args.output}")


if __name__ == '__main__':
    main()
