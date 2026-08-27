#!/usr/bin/env python3
"""
Card Manager - 卡片生命周期管理器
Card Dealing Protocol - 发牌协议脚本

管理卡片的完整生命周期：生成 → 评估 → 排队 → 发送 → 追踪。

Usage:
    python card-manager.py --context "用户正在编写代码"
    python card-manager.py --status
    python card-manager.py --flush
    python card-manager.py --interactive
"""

import json
import time
import argparse
from dataclasses import dataclass, asdict, field
from enum import Enum
from typing import Optional, List, Dict
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from card_generator import CardGenerator, CardContext, CardType
from card_evaluator import CardEvaluator, EvaluationContext


class CardStatus(Enum):
    """卡片状态枚举"""
    PENDING = "pending"           # 待处理
    QUEUED = "queued"            # 队列中
    SENT = "sent"                 # 已发送
    CONFIRMED = "confirmed"      # 已确认
    IGNORED = "ignored"          # 已忽略
    EXPIRED = "expired"          # 已过期
    FAILED = "failed"            # 发送失败


@dataclass
class Card:
    """卡片对象"""
    card_id: str
    card_type: str
    title: str
    content: str
    priority: float
    timing: str                    # immediate/delayed/queued
    delay_reason: str
    status: str = CardStatus.PENDING.value
    created_at: str = ""
    sent_at: str = ""
    confirmed_at: str = ""
    evaluation_score: float = 0.0
    context_summary: str = ""


@dataclass
class CardQueue:
    """卡片队列"""
    cards: List[Card] = field(default_factory=list)
    max_size: int = 10
    max_age_seconds: int = 3600    # 1小时过期

    def add(self, card: Card):
        """添加卡片到队列"""
        if len(self.cards) >= self.max_size:
            # 移除最低优先级卡片
            self.cards.sort(key=lambda c: c.priority)
            self.cards.pop(0)
        self.cards.append(card)

    def pop_highest_priority(self) -> Optional[Card]:
        """弹出最高优先级卡片"""
        if not self.cards:
            return None
        self.cards.sort(key=lambda c: c.priority, reverse=True)
        return self.cards.pop(0)

    def remove_expired(self) -> int:
        """移除过期卡片"""
        now = time.time()
        original_len = len(self.cards)
        self.cards = [
            c for c in self.cards
            if (now - datetime.fromisoformat(c.created_at).timestamp())
            < self.max_age_seconds
        ]
        return original_len - len(self.cards)

    def get_by_status(self, status: str) -> List[Card]:
        """按状态获取卡片"""
        return [c for c in self.cards if c.status == status]


@dataclass
class CardStats:
    """卡片统计"""
    total_generated: int = 0
    total_sent: int = 0
    total_confirmed: int = 0
    total_ignored: int = 0
    avg_evaluation_score: float = 0.0
    by_type: Dict[str, int] = field(default_factory=dict)


class CardManager:
    """卡片生命周期管理器"""

    def __init__(self, config: Optional[dict] = None):
        """初始化管理器"""
        self.config = config or {}
        self.queue = CardQueue(
            max_size=self.config.get('queue_max_size', 10),
            max_age_seconds=self.config.get('queue_max_age', 3600)
        )
        self.generator = CardGenerator(self.config)
        self.evaluator = CardEvaluator(self.config)
        self.stats = CardStats()
        self.sent_history: List[Card] = []

    def generate_card(self, context: CardContext) -> Optional[Card]:
        """生成卡片"""
        card_data = self.generator.generate(context)
        if not card_data:
            return None

        # 评估卡片
        eval_context = EvaluationContext(
            user_state=context.user_state,
            flow_state=context.flow_state,
            interruption_cost=context.interruption_cost,
            user_explicit_request=bool(context.user_query),
            recent_card_count=self.stats.total_sent
        )
        eval_result = self.evaluator.evaluate(card_data.card_type, eval_context)

        # 创建卡片对象
        card = Card(
            card_id=f"card_{int(time.time() * 1000)}",
            card_type=card_data.card_type,
            title=card_data.title,
            content=card_data.content,
            priority=card_data.priority,
            timing=card_data.timing,
            delay_reason=card_data.delay_reason,
            status=CardStatus.PENDING.value,
            created_at=datetime.now().isoformat(),
            evaluation_score=eval_result.quality_score
        )

        self.stats.total_generated += 1
        type_count = self.stats.by_type.get(card.card_type, 0)
        self.stats.by_type[card.card_type] = type_count + 1

        return card

    def should_send(self, card: Card, context: EvaluationContext) -> bool:
        """判断是否应该发送"""
        # 评估决策
        eval_result = self.evaluator.evaluate(card.card_type, context)

        if eval_result.recommendation == 'skip':
            return False

        # 频率检查
        recent_count = len([
            c for c in self.sent_history
            if (datetime.now() - datetime.fromisoformat(c.sent_at)).seconds < 300
        ])
        if recent_count >= self.config.get('max_cards_per_5min', 3):
            return False

        return True

    def send_card(self, card: Card, context: EvaluationContext) -> bool:
        """发送卡片"""
        if not self.should_send(card, context):
            return False

        card.status = CardStatus.SENT.value
        card.sent_at = datetime.now().isoformat()
        self.stats.total_sent += 1
        self.sent_history.append(card)
        return True

    def queue_card(self, card: Card):
        """将卡片加入队列"""
        card.status = CardStatus.QUEUED.value
        self.queue.add(card)

    def process_queue(self, context: EvaluationContext) -> Optional[Card]:
        """处理队列，返回可发送的卡片"""
        # 清理过期卡片
        self.queue.remove_expired()

        # 尝试发送最高优先级卡片
        while True:
            card = self.queue.pop_highest_priority()
            if not card:
                break

            # 更新上下文检查
            eval_context = EvaluationContext(
                user_state=context.user_state,
                flow_state=context.flow_state,
                interruption_cost=0.0,  # 队列中已等待，成本降低
                user_explicit_request=False,
                recent_card_count=self.stats.total_sent
            )

            if self.should_send(card, eval_context):
                card.status = CardStatus.SENT.value
                card.sent_at = datetime.now().isoformat()
                self.stats.total_sent += 1
                self.sent_history.append(card)
                return card
            else:
                # 重新放回队列末尾
                card.priority *= 0.9  # 降低优先级
                self.queue.add(card)

        return None

    def confirm_card(self, card_id: str):
        """确认卡片"""
        for card in self.sent_history:
            if card.card_id == card_id:
                card.status = CardStatus.CONFIRMED.value
                card.confirmed_at = datetime.now().isoformat()
                self.stats.total_confirmed += 1
                return True
        return False

    def ignore_card(self, card_id: str):
        """忽略卡片"""
        for card in self.sent_history:
            if card.card_id == card_id:
                card.status = CardStatus.IGNORED.value
                self.stats.total_ignored += 1
                return True
        return False

    def get_status(self) -> dict:
        """获取管理器状态"""
        return {
            'queue_size': len(self.queue.cards),
            'queue_max': self.queue.max_size,
            'history_size': len(self.sent_history),
            'stats': asdict(self.stats)
        }

    def get_queue_preview(self, limit: int = 5) -> List[dict]:
        """获取队列预览"""
        sorted_cards = sorted(
            self.queue.cards,
            key=lambda c: c.priority,
            reverse=True
        )[:limit]
        return [
            {
                'card_id': c.card_id,
                'type': c.card_type,
                'title': c.title,
                'priority': c.priority,
                'age_seconds': (
                    datetime.now() -
                    datetime.fromisoformat(c.created_at)
                ).seconds
            }
            for c in sorted_cards
        ]


def interactive_mode():
    """交互模式"""
    print("=== Card Manager 交互模式 ===")
    print("输入上下文信息生成和管理卡片，输入 'quit' 退出\n")

    manager = CardManager()

    while True:
        print("\n命令: generate / status / queue / flush / confirm / ignore / quit")
        cmd = input("> ").strip().lower()

        if cmd in ['quit', 'exit', 'q']:
            break

        if cmd == 'generate':
            print("\n请描述用户当前任务:")
            task = input("> ").strip() or "一般信息"

            print("\n用户状态 (idle/working/typing/meeting):")
            state = input("> ").strip() or "idle"

            print("\n心流状态 (normal/deep_flow):")
            flow = input("> ").strip() or "normal"

            print("\n不确定性降低 (0.0-1.0):")
            uncertainty = float(input("> ").strip() or "0.3")

            print("\n行动清晰度 (0.0-1.0):")
            action = float(input("> ").strip() or "0.5")

            context = CardContext(
                user_state=state,
                current_task=task,
                flow_state=flow,
                uncertainty_reduction=uncertainty,
                action_clarity=action,
                relevance=0.6
            )

            card = manager.generate_card(context)
            if card:
                print(f"\n✓ 生成卡片:")
                print(f"  ID: {card.card_id}")
                print(f"  类型: {card.card_type}")
                print(f"  标题: {card.title}")
                print(f"  优先级: {card.priority:.2f}")
                print(f"  时机: {card.timing}")
                print(f"  质量: {card.evaluation_score:.2f}")

                # 询问是否发送
                eval_ctx = EvaluationContext(
                    user_state=state,
                    flow_state=flow
                )
                if manager.should_send(card, eval_ctx):
                    print("\n→ 建议发送 (按 Enter 发送，或输入 'queue' 加入队列)")
                    action = input("> ").strip()
                    if not action:
                        manager.send_card(card, eval_ctx)
                        print(f"  ✓ 已发送")
                    elif action == 'queue':
                        manager.queue_card(card)
                        print(f"  → 已加入队列")
                else:
                    print("\n→ 不建议发送 (已加入队列)")
                    manager.queue_card(card)
            else:
                print("\n✗ 未生成卡片")

        elif cmd == 'status':
            status = manager.get_status()
            print(f"\n管理器状态:")
            print(f"  队列大小: {status['queue_size']}/{status['queue_max']}")
            print(f"  历史记录: {status['history_size']}")
            print(f"  统计: {json.dumps(status['stats'], indent=2, ensure_ascii=False)}")

        elif cmd == 'queue':
            preview = manager.get_queue_preview()
            if preview:
                print(f"\n队列预览 (前{len(preview)}张):")
                for i, card in enumerate(preview, 1):
                    print(f"  {i}. [{card['type']}] {card['title']}")
                    print(f"     优先级: {card['priority']:.2f} | "
                          f"等待: {card['age_seconds']}秒")
            else:
                print("\n队列为空")

        elif cmd == 'flush':
            print("\n处理队列...")
            ctx = EvaluationContext(user_state='idle', flow_state='normal')
            while True:
                card = manager.process_queue(ctx)
                if not card:
                    break
                print(f"  发送: [{card.card_type}] {card.title}")

        elif cmd == 'confirm':
            print("\n确认的卡片ID:")
            card_id = input("> ").strip()
            if manager.confirm_card(card_id):
                print("  ✓ 已确认")
            else:
                print("  ✗ 未找到卡片")

        elif cmd == 'ignore':
            print("\n忽略的卡片ID:")
            card_id = input("> ").strip()
            if manager.ignore_card(card_id):
                print("  ✓ 已标记忽略")
            else:
                print("  ✗ 未找到卡片")


def main():
    parser = argparse.ArgumentParser(description="Card Manager - 卡片生命周期管理器")
    parser.add_argument('--context', type=str, help='上下文描述')
    parser.add_argument('--interactive', action='store_true', help='交互模式')
    parser.add_argument('--status', action='store_true', help='显示状态')
    parser.add_argument('--flush', action='store_true', help='处理队列')
    parser.add_argument('--output', type=str, help='输出文件')
    parser.add_argument('--config', type=str, help='配置文件')

    args = parser.parse_args()

    # 加载配置
    config = {}
    if args.config:
        with open(args.config, 'r', encoding='utf-8') as f:
            config = json.load(f)

    manager = CardManager(config)

    if args.interactive:
        interactive_mode()
        return

    if args.status:
        print(json.dumps(manager.get_status(), ensure_ascii=False, indent=2))
        return

    if args.flush:
        ctx = EvaluationContext(user_state='idle', flow_state='normal')
        while True:
            card = manager.process_queue(ctx)
            if not card:
                break
            print(f"发送: [{card.card_type}] {card.title}")
        return

    if args.context:
        context = CardContext(
            user_state='idle',
            current_task=args.context,
            uncertainty_reduction=0.3,
            action_clarity=0.5,
            relevance=0.6
        )
        card = manager.generate_card(context)
        if card:
            print(json.dumps(asdict(card), ensure_ascii=False, indent=2))
        else:
            print("未生成卡片")
        return

    # 默认显示状态
    print(json.dumps(manager.get_status(), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
