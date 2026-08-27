#!/usr/bin/env python3
"""
沉默管理器
Silence Manager
管理沉默协议的完整生命周期
"""

import json
import time
import sys
from dataclasses import dataclass, field
from typing import Optional, Callable
from enum import Enum
from datetime import datetime, timedelta


class SilenceState(Enum):
    ACTIVE = "active"
    PENDING = "pending"
    WAKE = "wake"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CardDelivery(Enum):
    IMMEDIATE = "immediate"
    SILENCED = "silenced"
    DELAYED = "delayed"
    CANCELLED = "cancelled"


@dataclass
class SilenceCard:
    """沉默卡片"""
    card_id: str
    content: str
    priority: str
    timestamp: str
    silence_until: Optional[datetime] = None
    state: SilenceState = SilenceState.PENDING
    silence_reason: str = ""
    delivery_attempts: int = 0
    wake_condition: Optional[str] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class SilenceEvent:
    """沉默事件"""
    event_id: str
    card_id: str
    decision: str
    duration: int
    reason: str
    outcome: str  # delivered/wake_bypass/timeout/cancelled
    was_correct: bool = False
    timestamp: str = ""


class SilenceManager:
    """沉默管理器"""

    def __init__(self, detector=None, config_path: Optional[str] = None):
        self.detector = detector
        if self.detector is None:
            from silence_detector import SilenceDetector
            self.detector = SilenceDetector(config_path)

        self.active_silences: dict[str, SilenceCard] = {}
        self.silence_history: list[SilenceEvent] = []
        self.statistics = {
            "total_cards_processed": 0,
            "total_silenced": 0,
            "total_delivered": 0,
            "total_cancelled": 0,
            "timeout_triggers": 0,
            "wake_bypasses": 0,
            "silence_rate": 0.0,
            "timeout_rate": 0.0
        }

        self.callbacks = {
            "on_silence": [],
            "on_deliver": [],
            "on_wake": [],
            "on_timeout": [],
            "on_cancel": []
        }

    def register_callback(self, event: str, callback: Callable):
        """注册回调函数"""
        if event in self.callbacks:
            self.callbacks[event].append(callback)

    def _trigger_callbacks(self, event: str, *args, **kwargs):
        """触发回调"""
        for callback in self.callbacks.get(event, []):
            try:
                callback(*args, **kwargs)
            except Exception as e:
                print(f"回调执行失败: {e}")

    def process_card(self, card_id: str, content: str, priority: str,
                     user_ctx: dict, card_ctx: dict) -> tuple[CardDelivery, SilenceEvent]:
        """处理卡片，决定沉默或发送"""
        self.statistics["total_cards_processed"] += 1

        # 构建卡片对象
        card = SilenceCard(
            card_id=card_id,
            content=content,
            priority=priority,
            timestamp=datetime.now().isoformat()
        )

        # 评估沉默
        from silence_detector import UserContext, CardContext
        user_context = UserContext(**user_ctx)
        card_context = CardContext(
            priority=priority,
            card_type=card_ctx.get("card_type", "notification")
        )

        should_silence, evaluation = self.detector.should_silence(user_context, card_context)

        # 记录评估结果
        card.silence_reason = ", ".join(evaluation.reasons)
        card.wake_condition = evaluation.alternative

        # 创建沉默事件
        event = SilenceEvent(
            event_id=f"se_{int(time.time()*1000)}",
            card_id=card_id,
            decision=evaluation.decision.value,
            duration=evaluation.duration.value,
            reason=", ".join(evaluation.reasons),
            outcome="pending",
            timestamp=datetime.now().isoformat()
        )

        if should_silence:
            # 执行沉默
            card.state = SilenceState.ACTIVE
            if evaluation.duration.value >= 0:
                card.silence_until = datetime.now() + timedelta(minutes=evaluation.duration.value)
            else:
                card.silence_until = None  # 永久或会话沉默

            self.active_silences[card_id] = card
            self.statistics["total_silenced"] += 1

            self._trigger_callbacks("on_silence", card, evaluation)

            # 如果有超时，设置定时器检查
            if evaluation.duration.value > 0:
                event.outcome = "silenced"
            else:
                event.outcome = "session_silenced"

            return CardDelivery.SILENCED, event

        else:
            # 直接发送
            card.state = SilenceState.COMPLETED
            card.delivery_attempts += 1
            self.statistics["total_delivered"] += 1

            event.outcome = "delivered"
            event.was_correct = True

            self._trigger_callbacks("on_deliver", card, evaluation)

            return CardDelivery.IMMEDIATE, event

    def check_wake_conditions(self) -> list[tuple[SilenceCard, SilenceEvent]]:
        """检查唤醒条件，返回需要发送的卡片"""
        to_deliver = []
        now = datetime.now()

        for card_id, card in list(self.active_silences.items()):
            if card.state != SilenceState.ACTIVE:
                continue

            should_deliver = False
            reason = ""

            # 1. 检查超时
            if card.silence_until and now >= card.silence_until:
                should_deliver = True
                reason = "timeout"
                self.statistics["timeout_triggers"] += 1

            # 2. 检查唤醒条件
            elif self._check_wake_condition(card):
                should_deliver = True
                reason = "wake_bypass"
                self.statistics["wake_bypasses"] += 1

            if should_deliver:
                self._deliver_card(card, reason)
                to_deliver.append((card, reason))

        return to_deliver

    def _check_wake_condition(self, card: SilenceCard) -> bool:
        """检查唤醒条件（需要根据实际场景扩展）"""
        # 基础实现：检查是否达到沉默时长
        if card.silence_until and datetime.now() >= card.silence_until:
            return True

        # 后续可扩展：检查用户状态变化、紧急程度等
        return False

    def _deliver_card(self, card: SilenceCard, reason: str):
        """发送卡片"""
        # 查找对应的沉默事件
        event = None
        for e in self.silence_history:
            if e.card_id == card.card_id:
                event = e
                break

        if event:
            event.outcome = reason
            event.was_correct = (reason != "timeout")

        # 更新卡片状态
        card.state = SilenceState.COMPLETED
        card.delivery_attempts += 1

        # 移除活跃沉默
        if card.card_id in self.active_silences:
            del self.active_silences[card.card_id]

        self._trigger_callbacks("on_deliver" if reason != "timeout" else "on_timeout", card)

    def cancel_silence(self, card_id: str, reason: str = "user_request") -> bool:
        """取消沉默"""
        if card_id not in self.active_silences:
            return False

        card = self.active_silences[card_id]
        card.state = SilenceState.CANCELLED

        # 立即发送
        self._deliver_card(card, f"cancelled: {reason}")

        self.statistics["total_cancelled"] += 1
        self._trigger_callbacks("on_cancel", card, reason)

        return True

    def update_user_context(self, user_ctx: dict) -> list[tuple[SilenceCard, SilenceEvent]]:
        """更新用户上下文，触发智能唤醒检查"""
        # 检查是否需要基于新上下文唤醒某些卡片
        to_deliver = []
        for card_id, card in list(self.active_silences.items()):
            # 检查是否满足唤醒条件
            if self._should_wake_for_new_context(card, user_ctx):
                self._deliver_card(card, "context_change")
                to_deliver.append((card, "context_change"))

        return to_deliver

    def _should_wake_for_new_context(self, card: SilenceCard, user_ctx: dict) -> bool:
        """根据新上下文判断是否应唤醒（需要根据实际场景扩展）"""
        # 基础实现：用户退出深度工作/心流状态时唤醒
        flow_state = user_ctx.get("flow_state", False)
        user_state = user_ctx.get("user_state", "normal")

        # 如果用户之前在深度工作，现在不在，可以唤醒
        if card.metadata.get("silenced_during_flow") and not flow_state:
            return True

        return False

    def record_event(self, event: SilenceEvent):
        """记录沉默事件"""
        self.silence_history.append(event)
        # 保持历史记录限制
        if len(self.silence_history) > 10000:
            self.silence_history = self.silence_history[-5000:]

    def update_statistics(self):
        """更新统计数据"""
        total = self.statistics["total_cards_processed"]
        silenced = self.statistics["total_silenced"]

        if total > 0:
            self.statistics["silence_rate"] = silenced / total

        if silenced > 0:
            self.statistics["timeout_rate"] = self.statistics["timeout_triggers"] / silenced

    def get_statistics(self) -> dict:
        """获取统计数据"""
        self.update_statistics()
        return self.statistics.copy()

    def get_active_silences(self) -> list[dict]:
        """获取当前活跃沉默列表"""
        return [
            {
                "card_id": c.card_id,
                "content": c.content,
                "priority": c.priority,
                "state": c.state.value,
                "silence_reason": c.silence_reason,
                "silence_until": c.silence_until.isoformat() if c.silence_until else None,
                "wake_condition": c.wake_condition,
                "delivery_attempts": c.delivery_attempts
            }
            for c in self.active_silences.values()
        ]

    def export_history(self, limit: int = 100) -> list[dict]:
        """导出沉默历史"""
        events = self.silence_history[-limit:]
        return [
            {
                "event_id": e.event_id,
                "card_id": e.card_id,
                "decision": e.decision,
                "duration": e.duration,
                "reason": e.reason,
                "outcome": e.outcome,
                "was_correct": e.was_correct,
                "timestamp": e.timestamp
            }
            for e in events
        ]


def main():
    """命令行入口"""
    manager = SilenceManager()

    if len(sys.argv) < 2:
        print("用法:")
        print("  python silence-manager.py process <card.json> <user_ctx.json>")
        print("  python silence-manager.py check-wake")
        print("  python silence-manager.py cancel <card_id>")
        print("  python silence-manager.py statistics")
        print("  python silence-manager.py active")
        print("  python silence-manager.py history")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "process" and len(sys.argv) >= 4:
        try:
            with open(sys.argv[2], 'r', encoding='utf-8') as f:
                card_data = json.load(f)
            with open(sys.argv[3], 'r', encoding='utf-8') as f:
                user_ctx = json.load(f)

            delivery, event = manager.process_card(
                card_id=card_data.get("card_id", f"card_{int(time.time()*1000)}"),
                content=card_data.get("content", ""),
                priority=card_data.get("priority", "normal"),
                user_ctx=user_ctx,
                card_ctx=card_data
            )

            manager.record_event(event)

            result = {
                "delivery": delivery.value,
                "event": {
                    "event_id": event.event_id,
                    "decision": event.decision,
                    "outcome": event.outcome,
                    "was_correct": event.was_correct
                }
            }
            print(json.dumps(result, ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"处理失败: {e}")
            sys.exit(1)

    elif cmd == "check-wake":
        to_deliver = manager.check_wake_conditions()
        print(json.dumps({
            "delivered_count": len(to_deliver),
            "cards": [{"card_id": c[0].card_id, "reason": c[1]} for c in to_deliver]
        }, ensure_ascii=False, indent=2))

    elif cmd == "cancel" and len(sys.argv) >= 3:
        card_id = sys.argv[2]
        success = manager.cancel_silence(card_id)
        print(json.dumps({"success": success}))

    elif cmd == "statistics":
        stats = manager.get_statistics()
        print(json.dumps(stats, ensure_ascii=False, indent=2))

    elif cmd == "active":
        active = manager.get_active_silences()
        print(json.dumps({"active_silences": active}, ensure_ascii=False, indent=2))

    elif cmd == "history":
        history = manager.export_history()
        print(json.dumps({"history": history}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
