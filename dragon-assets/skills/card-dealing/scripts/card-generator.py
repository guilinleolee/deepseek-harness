#!/usr/bin/env python3
"""
Card Generator - 发牌生成器
Card Dealing Protocol - 发牌协议脚本

基于上下文生成卡片，根据决策矩阵选择最优卡片类型。

Usage:
    python card-generator.py --context "用户正在编写代码"
    python card-generator.py --context-file context.json --output cards.json
    python card-generator.py --interactive

Outputs:
    Generated cards with type, content, priority, timing recommendation
"""

import json
import argparse
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class CardType(Enum):
    """卡片类型枚举"""
    INFORMATION = "information"      # 信息卡
    CONFIRMATION = "confirmation"     # 确认卡
    RECOMMENDATION = "recommendation" # 推荐卡
    ACTION = "action"                 # 行动卡
    WARNING = "warning"                # 警告卡


@dataclass
class CardContext:
    """卡片生成上下文"""
    user_state: str = "idle"           # idle/working/meeting/typing
    uncertainty_reduction: float = 0.0   # 0.0-1.0 不确定性降低量
    action_clarity: float = 0.0        # 0.0-1.0 行动清晰度
    time_sensitivity: float = 0.0       # 0.0-1.0 时效性
    relevance: float = 0.0              # 0.0-1.0 相关性
    current_task: str = ""
    flow_state: str = "normal"         # normal/deep_flow/breaking
    interruption_cost: float = 0.0     # 打断成本
    user_query: str = ""               # 用户主动查询


@dataclass
class GeneratedCard:
    """生成的卡片"""
    card_type: str
    title: str
    content: str
    priority: float                    # 0.0-1.0 优先级
    timing: str                        # immediate/delayed/queued
    delay_reason: str = ""
    quality_score: float = 0.0         # 0.0-1.0 质量得分
    uncertainty_reduction: float = 0.0
    action_clarity_boost: float = 0.0


class CardGenerator:
    """发牌生成器"""

    # 质量门控阈值
    UNCERTAINTY_THRESHOLD = 0.30
    ACTION_THRESHOLD = 0.60
    QUALITY_GATE_MIN = 0.50

    # 打断成本阈值
    HIGH_INTERRUPTION_COST = 0.70

    # 优先级权重
    WEIGHTS = {
        'uncertainty_reduction': 0.25,
        'action_clarity': 0.25,
        'time_sensitivity': 0.15,
        'relevance': 0.20,
        'quality': 0.15
    }

    def __init__(self, config: Optional[dict] = None):
        """初始化生成器"""
        self.config = config or {}
        self._load_thresholds()

    def _load_thresholds(self):
        """从配置加载阈值"""
        self.UNCERTAINTY_THRESHOLD = self.config.get(
            'uncertainty_threshold', 0.30)
        self.ACTION_THRESHOLD = self.config.get(
            'action_threshold', 0.60)
        self.QUALITY_GATE_MIN = self.config.get(
            'quality_gate_min', 0.50)

    def analyze_context(self, context: CardContext) -> dict:
        """分析上下文，返回各维度评分"""
        return {
            'uncertainty_reduction': context.uncertainty_reduction,
            'action_clarity': context.action_clarity,
            'time_sensitivity': context.time_sensitivity,
            'relevance': context.relevance,
            'interruption_cost': context.interruption_cost,
            'flow_state': context.flow_state,
            'user_state': context.user_state
        }

    def select_card_type(self, context: CardContext) -> CardType:
        """根据上下文选择最优卡片类型"""
        scores = self.analyze_context(context)

        # 警告卡：严重风险 always highest priority
        if self._is_critical_risk(context):
            return CardType.WARNING

        # 行动卡：下一步行动明确且可执行
        if (scores['action_clarity'] >= self.ACTION_THRESHOLD and
                self._is_action_feasible(context)):
            return CardType.ACTION

        # 推荐卡：不确定但有多个选项
        if (scores['uncertainty_reduction'] >= self.UNCERTAINTY_THRESHOLD and
                self._has_multiple_options(context)):
            return CardType.RECOMMENDATION

        # 确认卡：需要确认理解
        if self._needs_confirmation(context):
            return CardType.CONFIRMATION

        # 信息卡：一般信息价值
        if (scores['uncertainty_reduction'] >= self.UNCERTAINTY_THRESHOLD * 0.8 and
                scores['relevance'] >= 0.5):
            return CardType.INFORMATION

        return None  # 不发牌

    def _is_critical_risk(self, context: CardContext) -> bool:
        """判断是否为严重风险"""
        return context.time_sensitivity >= 0.9

    def _is_action_feasible(self, context: CardContext) -> bool:
        """判断行动是否可执行"""
        return context.action_clarity >= self.ACTION_THRESHOLD

    def _has_multiple_options(self, context: CardContext) -> bool:
        """判断是否有多个选项"""
        return context.action_clarity < self.ACTION_THRESHOLD

    def _needs_confirmation(self, context: CardContext) -> bool:
        """判断是否需要确认"""
        return context.uncertainty_reduction < self.UNCERTAINTY_THRESHOLD * 0.5

    def calculate_priority(self, context: CardContext, card_type: CardType) -> float:
        """计算卡片优先级"""
        scores = self.analyze_context(context)

        # 时效性加成
        if card_type == CardType.WARNING:
            return min(1.0, scores['time_sensitivity'] * 1.5)

        # 一般优先级计算
        priority = (
            scores['uncertainty_reduction'] * self.WEIGHTS['uncertainty_reduction'] +
            scores['action_clarity'] * self.WEIGHTS['action_clarity'] +
            scores['time_sensitivity'] * self.WEIGHTS['time_sensitivity'] +
            scores['relevance'] * self.WEIGHTS['relevance']
        )

        return min(1.0, priority)

    def determine_timing(self, context: CardContext, card_type: CardType) -> tuple:
        """确定发牌时机"""
        scores = self.analyze_context(context)

        # 警告卡立即发送
        if card_type == CardType.WARNING:
            return "immediate", ""

        # 心流状态：延迟发送
        if scores['flow_state'] == 'deep_flow':
            return "delayed", "deep_flow_state"

        # 高打断成本：延迟
        if scores['interruption_cost'] >= self.HIGH_INTERRUPTION_COST:
            return "delayed", f"high_interruption_cost_{scores['interruption_cost']:.2f}"

        # 用户忙：延迟
        if scores['user_state'] == 'typing':
            return "delayed", "user_typing"

        # 会议中：延迟
        if scores['user_state'] == 'meeting':
            return "queued", "in_meeting"

        return "immediate", ""

    def quality_gate(self, context: CardContext, card_type: CardType,
                     priority: float) -> bool:
        """质量门控检查"""
        scores = self.analyze_context(context)

        # 检查基础质量阈值
        quality_score = (
            scores['uncertainty_reduction'] * 0.4 +
            scores['action_clarity'] * 0.35 +
            scores['relevance'] * 0.25
        )

        if quality_score < self.QUALITY_GATE_MIN:
            return False

        # 打断成本检查
        if (scores['interruption_cost'] >= self.HIGH_INTERRUPTION_COST and
                priority < 0.6):
            return False

        # 心流保护检查
        if scores['flow_state'] == 'deep_flow' and card_type != CardType.WARNING:
            if priority < 0.8:
                return False

        return True

    def generate_card_content(self, context: CardContext,
                               card_type: CardType) -> GeneratedCard:
        """生成卡片内容"""
        priority = self.calculate_priority(context, card_type)
        timing, delay_reason = self.determine_timing(context, card_type)
        scores = self.analyze_context(context)

        # 根据卡片类型生成内容
        if card_type == CardType.INFORMATION:
            title, content = self._generate_info_content(context, scores)
        elif card_type == CardType.CONFIRMATION:
            title, content = self._generate_confirm_content(context, scores)
        elif card_type == CardType.RECOMMENDATION:
            title, content = self._generate_recommend_content(context, scores)
        elif card_type == CardType.ACTION:
            title, content = self._generate_action_content(context, scores)
        elif card_type == CardType.WARNING:
            title, content = self._generate_warning_content(context, scores)
        else:
            title, content = "", ""

        return GeneratedCard(
            card_type=card_type.value,
            title=title,
            content=content,
            priority=priority,
            timing=timing,
            delay_reason=delay_reason,
            quality_score=scores.get('uncertainty_reduction', 0) * 0.5,
            uncertainty_reduction=scores['uncertainty_reduction'],
            action_clarity_boost=scores['action_clarity']
        )

    def _generate_info_content(self, context: CardContext, scores: dict) -> tuple:
        """生成信息卡内容"""
        title = f"信息: {context.current_task or '相关知识'}"
        content = f"这条信息可以将不确定性降低 {scores['uncertainty_reduction']*100:.0f}%，"
        content += f"与您当前任务的相关度为 {scores['relevance']*100:.0f}%。"
        return title, content

    def _generate_confirm_content(self, context: CardContext, scores: dict) -> tuple:
        """生成确认卡内容"""
        title = "确认理解"
        content = f"我想确认一下关于「{context.current_task}」的理解是否正确。"
        content += " 请确认或纠正。"
        return title, content

    def _generate_recommend_content(self, context: CardContext, scores: dict) -> tuple:
        """生成推荐卡内容"""
        title = "建议选项"
        content = f"针对「{context.current_task}」，我建议以下几个选项:"
        content += f"\n1. 选项A (推荐度: {scores['action_clarity']*100:.0f}%)"
        content += f"\n2. 选项B"
        content += f"\n3. 选项C"
        return title, content

    def _generate_action_content(self, context: CardContext, scores: dict) -> tuple:
        """生成行动卡内容"""
        title = f"行动建议: {context.current_task}"
        content = f"下一步建议: {context.current_task}"
        content += f"\n行动清晰度: {scores['action_clarity']*100:.0f}%"
        content += f"\n建议立即执行或添加到计划中。"
        return title, content

    def _generate_warning_content(self, context: CardContext, scores: dict) -> tuple:
        """生成警告卡内容"""
        title = "⚠️ 严重警告"
        content = f"检测到紧急情况: {context.current_task or '风险'}"
        content += "\n请立即处理或确认了解此风险。"
        return title, content

    def generate(self, context: CardContext) -> Optional[GeneratedCard]:
        """主生成方法"""
        # 选择卡片类型
        card_type = self.select_card_type(context)
        if card_type is None:
            return None

        # 计算优先级
        priority = self.calculate_priority(context, card_type)

        # 质量门控检查
        if not self.quality_gate(context, card_type, priority):
            return None

        # 生成卡片内容
        return self.generate_card_content(context, card_type)

    def generate_batch(self, contexts: list) -> list:
        """批量生成卡片"""
        cards = []
        for ctx in contexts:
            card = self.generate(ctx)
            if card:
                cards.append(card)
        return cards


def load_context_from_file(filepath: str) -> CardContext:
    """从文件加载上下文"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return CardContext(**data)


def save_cards_to_file(cards: list, filepath: str):
    """保存卡片到文件"""
    output = [asdict(card) for card in cards]
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)


def interactive_mode():
    """交互模式"""
    print("=== Card Generator 交互模式 ===")
    print("输入上下文信息生成卡片，输入 'quit' 退出\n")

    generator = CardGenerator()

    while True:
        print("\n请输入用户当前任务描述:")
        task = input("> ").strip()
        if task.lower() in ['quit', 'exit', 'q']:
            break

        print("\n请输入用户状态 (idle/working/typing/meeting):")
        state = input("> ").strip() or "idle"

        print("\n不确定性降低量 (0.0-1.0, 回车默认0.3):")
        uncertainty = float(input("> ").strip() or "0.3")

        print("\n行动清晰度 (0.0-1.0, 回车默认0.5):")
        action = float(input("> ").strip() or "0.5")

        print("\n时效性 (0.0-1.0, 回车默认0.3):")
        sensitivity = float(input("> ").strip() or "0.3")

        print("\n相关性 (0.0-1.0, 回车默认0.6):")
        relevance = float(input("> ").strip() or "0.6")

        print("\n心流状态 (normal/deep_flow, 回车默认normal):")
        flow = input("> ").strip() or "normal"

        context = CardContext(
            user_state=state,
            uncertainty_reduction=uncertainty,
            action_clarity=action,
            time_sensitivity=sensitivity,
            relevance=relevance,
            current_task=task,
            flow_state=flow
        )

        card = generator.generate(context)

        if card:
            print(f"\n✓ 生成卡片:")
            print(f"  类型: {card.card_type}")
            print(f"  标题: {card.title}")
            print(f"  内容: {card.content}")
            print(f"  优先级: {card.priority:.2f}")
            print(f"  时机: {card.timing} {card.delay_reason}")
            print(f"  质量得分: {card.quality_score:.2f}")
        else:
            print("\n✗ 未生成卡片 (未通过质量门控)")


def main():
    parser = argparse.ArgumentParser(description="Card Generator - 发牌生成器")
    parser.add_argument('--context', type=str, help='上下文描述')
    parser.add_argument('--context-file', type=str, help='从文件加载上下文')
    parser.add_argument('--output', type=str, help='输出文件路径')
    parser.add_argument('--config', type=str, help='配置文件路径')
    parser.add_argument('--interactive', action='store_true', help='交互模式')
    parser.add_argument('--uncertainty', type=float, default=0.3,
                        help='不确定性降低量 (默认0.3)')
    parser.add_argument('--action', type=float, default=0.5,
                        help='行动清晰度 (默认0.5)')
    parser.add_argument('--sensitivity', type=float, default=0.3,
                        help='时效性 (默认0.3)')
    parser.add_argument('--relevance', type=float, default=0.6,
                        help='相关性 (默认0.6)')
    parser.add_argument('--state', type=str, default='idle',
                        choices=['idle', 'working', 'typing', 'meeting'],
                        help='用户状态 (默认idle)')
    parser.add_argument('--flow', type=str, default='normal',
                        choices=['normal', 'deep_flow'],
                        help='心流状态 (默认normal)')

    args = parser.parse_args()

    # 加载配置
    config = {}
    if args.config:
        with open(args.config, 'r', encoding='utf-8') as f:
            config = json.load(f)

    generator = CardGenerator(config)

    # 交互模式
    if args.interactive:
        interactive_mode()
        return

    # 从文件加载上下文
    if args.context_file:
        context = load_context_from_file(args.context_file)
    else:
        # 从命令行参数构建上下文
        context = CardContext(
            user_state=args.state,
            uncertainty_reduction=args.uncertainty,
            action_clarity=args.action,
            time_sensitivity=args.sensitivity,
            relevance=args.relevance,
            current_task=args.context or "",
            flow_state=args.flow
        )

    # 生成卡片
    card = generator.generate(context)

    if card:
        print(json.dumps(asdict(card), ensure_ascii=False, indent=2))

        if args.output:
            save_cards_to_file([card], args.output)
            print(f"\n卡片已保存到: {args.output}")
    else:
        print("未生成卡片 (未通过质量门控)")


if __name__ == '__main__':
    main()
