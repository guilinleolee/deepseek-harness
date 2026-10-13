"""router.py · dsh-routing-suite-bridge 路由核心 · V1.0

天龙自研模块 · MIT
借鉴 yjh051108/dsh-routing-suite v0.3.0 (6,842⭐ MIT) 的 4-mode 决策树 + 模型适配范式

接口语义（与上游 dsh-router-standard v0.3.0 对齐）：
  - spec / react / mixed / weak 四模式
  - Pro=spec / Flash=neutral 模型适配
  - 单任务三锚（persona 静态）：回顾 + 收敛 + 反跑题
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict
from typing import Any


# ─── 模式常量 ────────────────────────────────────────────────────────────────

MODE_SPEC = "spec"
MODE_REACT = "react"
MODE_MIXED = "mixed"
MODE_WEAK = "weak"

VALID_MODES = {MODE_SPEC, MODE_REACT, MODE_MIXED, MODE_WEAK}

# 模型能力分级
MODEL_PRO = {"pro", "sonnet", "gpt-4", "gpt-4o", "opus", "deepseek-chat"}
MODEL_FLASH = {"flash", "haiku", "gpt-3.5", "gpt-3.5-turbo", "deepseek-flash", "mini"}


# ─── 任务分类器 ────────────────────────────────────────────────────────────

# 复杂任务触发词（spec 模式）
SPEC_KEYWORDS = [
    "规划", "计划", "调研", "分析", "研报", "研究", "对比", "横评", "深度",
    "策略", "方案", "设计", "架构", "制定", "决策",
    "plan", "research", "analyze", "strategy", "design", "architect",
]

# 执行性任务触发词（react 模式）
REACT_KEYWORDS = [
    "执行", "实现", "写", "生成", "创建", "做出", "产出", "实现", "完成",
    "execute", "implement", "write", "generate", "create", "build", "make",
]

# 模糊任务触发词（weak / mixed）
WEAK_KEYWORDS = [
    "随便", "看看", "什么", "怎么样", "好不好",
    "any", "whatever", "anything",
]


@dataclass
class RouteResult:
    """路由决策结果"""
    mode: str
    confidence: float
    reason: str
    matched_keywords: list[str] = field(default_factory=list)
    model_hint: str | None = None
    persona_hints: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v not in (None, [], "")}


def classify(task: str) -> RouteResult:
    """任务复杂度判定 → 4 mode 决策

    接口语义对齐 dsh-router-standard v0.3.0：
      - spec: 复杂（多步/规划/研究）
      - react: 中等（明确目标/执行）
      - mixed: 模糊（避免，回退 weak）
      - weak: 简单（单步/查询）或 fallback
    """
    if not task or not task.strip():
        return RouteResult(
            mode=MODE_WEAK,
            confidence=1.0,
            reason="empty task → weak",
            matched_keywords=[],
        )

    text_lower = task.lower()
    spec_matches = [k for k in SPEC_KEYWORDS if k.lower() in text_lower or k in task]
    react_matches = [k for k in REACT_KEYWORDS if k.lower() in text_lower or k in task]
    weak_matches = [k for k in WEAK_KEYWORDS if k.lower() in text_lower or k in task]

    # 决策逻辑：spec 优先 → react → weak
    if spec_matches and not weak_matches:
        return RouteResult(
            mode=MODE_SPEC,
            confidence=0.9,
            reason=f"complex task detected (matched {len(spec_matches)} spec keywords)",
            matched_keywords=spec_matches,
            persona_hints=["review", "converge", "anti_drift"],  # 三锚
        )

    if react_matches and not spec_matches and not weak_matches:
        return RouteResult(
            mode=MODE_REACT,
            confidence=0.85,
            reason=f"execution task detected (matched {len(react_matches)} react keywords)",
            matched_keywords=react_matches,
        )

    if spec_matches and react_matches:
        # 两者都有 → 默认 spec（复杂优先）
        return RouteResult(
            mode=MODE_SPEC,
            confidence=0.7,
            reason="spec + react keywords conflict → spec wins (complex first)",
            matched_keywords=spec_matches + react_matches,
            persona_hints=["review", "converge", "anti_drift"],
        )

    if weak_matches:
        return RouteResult(
            mode=MODE_WEAK,
            confidence=0.6,
            reason=f"weak/ambiguous task → avoid mixed",
            matched_keywords=weak_matches,
        )

    # 无明确匹配 → 默认 react（最常用）
    return RouteResult(
        mode=MODE_REACT,
        confidence=0.5,
        reason="no keyword matched → default react",
        matched_keywords=[],
    )


def adapt(model: str, task: str) -> RouteResult:
    """模型适配：Pro=spec / Flash=neutral

    接口语义对齐 dsh-router-standard model adaptation：
      - Pro 模型 → spec 句 + few-shot（区分度 +5.0）
      - Flash 模型 → neutral + classify（+5.7）
    """
    model_lower = model.lower()
    base = classify(task)

    if any(m in model_lower for m in MODEL_PRO):
        # Pro 强制 spec（避免 weak / mixed）
        return RouteResult(
            mode=MODE_SPEC if base.mode in (MODE_SPEC, MODE_REACT) else MODE_SPEC,
            confidence=max(base.confidence, 0.8),
            reason=f"Pro model '{model}' → forced spec (gain +5.0)",
            matched_keywords=base.matched_keywords,
            model_hint="pro",
            persona_hints=["spec_sentence", "few_shot", "review", "converge", "anti_drift"],
        )

    if any(m in model_lower for m in MODEL_FLASH):
        # Flash → weak/neutral + classify（避免复杂 spec）
        return RouteResult(
            mode=MODE_WEAK if base.mode != MODE_SPEC else MODE_REACT,
            confidence=max(base.confidence, 0.7),
            reason=f"Flash model '{model}' → neutral + classify (gain +5.7)",
            matched_keywords=base.matched_keywords,
            model_hint="flash",
            persona_hints=["neutral", "classify"],
        )

    # 未知模型 → 沿用基础决策
    return RouteResult(
        **asdict(base),
        model_hint="unknown",
    )


def is_valid_mode(mode: str) -> bool:
    return mode in VALID_MODES


# ─── 主入口 ────────────────────────────────────────────────────────────────

def main() -> int:
    """演示：5 个测试任务路由"""
    test_tasks = [
        ("帮我规划下周内容矩阵", "pro"),
        ("搜索 AI 行业最新动态", "flash"),
        ("随便看看有什么可做的", "pro"),
        ("实现一个 Python 函数做 5 选 3 组合", "sonnet"),
        ("深度调研中国新能源汽车产业链，写一份研报", "pro"),
    ]

    print("=" * 70)
    print("Stage 52 · dsh-routing-suite-bridge · 4-mode 路由演示")
    print("=" * 70)

    for task, model in test_tasks:
        r = adapt(model, task)
        print(f"\n[{r.model_hint or 'unknown':6s}] {task}")
        print(f"  → mode={r.mode}  confidence={r.confidence}")
        print(f"  → reason: {r.reason}")
        if r.persona_hints:
            print(f"  → persona: {r.persona_hints}")

    print("\n" + "=" * 70)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
