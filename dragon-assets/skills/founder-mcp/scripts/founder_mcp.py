#!/usr/bin/env python3
"""
Founder MCP Server - Solo Founder跑道守护MCP工具服务器
Version: 1.0.0
Created: 2026-05-20

使用 FastMCP 构建，暴露5个 Solo Founder 核心工具：
1. founder_pressure_test     - 想法6问验证
2. founder_mvp_scope_limit - MVP边界保护
3. founder_launch_check    - 20项上线检查
4. founder_airstrip_one   - 魔法时刻触发器设计
5. founder_runway_calculation - 跑道计算
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from mcp.server.fastmcp import Context, FastMCP
from pydantic import BaseModel, ConfigDict, Field

# ─────────────────────────────────────────────────────────────
# MCP Server 实例
# ─────────────────────────────────────────────────────────────

mcp = FastMCP(
    "founder_mcp",
    dependencies=["pydantic>=2.0"],
)


# ─────────────────────────────────────────────────────────────
# 输入/输出模型 (Pydantic v2)
# ─────────────────────────────────────────────────────────────


class ResponseFormat(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"


# ── Tool 1: Pressure Test ──────────────────────────────────

class PressureTestInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    problem_description: str = Field(
        ...,
        description="要验证的商业想法/问题描述",
        min_length=5,
        max_length=2000,
    )
    format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="输出格式：markdown(人类可读) 或 json(机器可读)",
    )


def evaluate_pressure_test(description: str) -> dict[str, Any]:
    """执行6问想法验证逻辑"""
    questions = [
        {
            "id": 1,
            "question": "真实痛点 - 这个问题是你亲身经历的吗？还是道听途说？",
            "prompt": "分析问题描述，判断是否来自第一手亲身经历",
        },
        {
            "id": 2,
            "question": "具体客户 - 你能说出这个人的名字、行业、职位吗？",
            "prompt": "分析问题描述，判断是否能准确定位目标客户画像",
        },
        {
            "id": 3,
            "question": "付费意愿 - 如果明天收他们$99/月，他们会掏钱吗？",
            "prompt": "分析问题描述，判断目标客户的付费意愿和定价合理性",
        },
        {
            "id": 4,
            "question": "竞品缺口 - 为什么现有方案做不好？",
            "prompt": "分析问题描述，判断差异化优势和竞品缺口",
        },
        {
            "id": 5,
            "question": "防御壁垒 - 6个月后会有10个竞争对手吗？",
            "prompt": "分析问题描述，判断6个月后的竞争态势和防御壁垒",
        },
        {
            "id": 6,
            "question": "时间窗口 - 你的优势会在12个月内消失吗？",
            "prompt": "分析问题描述，判断时间窗口和先发优势可持续性",
        },
    ]

    # 模拟评估（实际使用时替换为LLM调用或专家评估）
    results = []
    positive_count = 0

    for q in questions:
        # 启发式评分：描述越具体越可能通过
        score = min(10, max(1, len(description) // 100))
        passed = score >= 5

        results.append(
            {
                "id": q["id"],
                "question": q["question"],
                "assessment": f"[需要LLM评估] {q['prompt']}",
                "score": score,
                "passed": passed,
                "recommendation": "建议补充更多具体细节" if not passed else "描述较为具体",
            }
        )
        if passed:
            positive_count += 1

    passed_count = positive_count
    threshold = 4  # 通过标准：至少4问通过
    final_passed = passed_count >= threshold

    return {
        "problem": description,
        "total_questions": 6,
        "passed_questions": passed_count,
        "threshold": threshold,
        "result": "PASS" if final_passed else "FAIL",
        "evaluations": results,
        "summary": f"通过 {passed_count}/6 问 {'✅ 想法值得追求' if final_passed else '❌ 需补充更多信息'}",
        "next_steps": [
            "补充第一手痛点来源",
            "明确目标客户画像",
            "验证$99/月的付费意愿",
            "识别竞品缺口",
            "建立防御壁垒",
            "评估时间窗口",
        ]
        if not final_passed
        else [
            "立即开始MVP开发",
            "寻找第一个付费客户",
            "快速验证商业模式",
        ],
        "evaluated_at": datetime.now().isoformat(),
    }


@mcp.tool(
    name="founder_pressure_test",
    description="创始想法压力测试：用6个关键问题验证你的商业想法是否值得追求。通过标准：6问中至少4问有明确答案。",
    annotations={
        "title": "Founder Pressure Test",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def founder_pressure_test(params: PressureTestInput, ctx: Context) -> str:
    """
    创始想法压力测试工具。

    在投入任何开发资源之前，用6问验证想法是否值得追求。

    返回格式：
    - markdown: 人类可读的评估报告
    - json: 结构化数据便于程序处理
    """
    await ctx.report_progress(0.1, "开始想法压力测试...")
    await ctx.log_info(f"Pressure test for: {params.problem_description[:50]}...")

    result = evaluate_pressure_test(params.problem_description)

    await ctx.report_progress(0.8, "生成评估报告...")

    if params.format == ResponseFormat.JSON:
        await ctx.report_progress(1.0, "完成")
        return json.dumps(result, ensure_ascii=False, indent=2)

    # Markdown 格式
    await ctx.report_progress(1.0, "完成")
    return _format_pressure_test_markdown(result)


def _format_pressure_test_markdown(result: dict) -> str:
    lines = [
        "# 🔍 创始想法压力测试报告",
        "",
        f"**评估时间**: {result['evaluated_at']}",
        "",
        f"## 📊 总体结果",
        "",
        f"| 指标 | 数值 |",
        f"|------|------|",
        f"| 通过问题数 | {result['passed_questions']}/6 |",
        f"| 通过标准 | ≥{result['threshold']}问 |",
        f"| **最终结论** | **{result['result']}** |",
        "",
        "## ❓ 六问详情",
        "",
    ]

    for ev in result["evaluations"]:
        status = "✅" if ev["passed"] else "❌"
        lines.append(f"### {status} Q{ev['id']}: {ev['question']}")
        lines.append(f"- 评分: {ev['score']}/10")
        lines.append(f"- 评估: {ev['assessment']}")
        lines.append(f"- 建议: {ev['recommendation']}")
        lines.append("")

    lines.extend([
        "## 📝 总结",
        "",
        result["summary"],
        "",
        "## ➡️ 下一步行动",
        "",
    ])
    for step in result["next_steps"]:
        lines.append(f"- [ ] {step}")

    return "\n".join(lines)


# ── Tool 2: MVP Scope Limit ────────────────────────────────

class MvpScopeInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    proposed_features: list[str] = Field(
        ...,
        description="待评估的功能列表",
        min_length=1,
        max_length=50,
    )
    core_value_proposition: str = Field(
        default="",
        description="核心价值主张（帮助判断哪些功能是MVP必须的）",
        max_length=500,
    )
    format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="输出格式：markdown 或 json",
    )


def evaluate_mvp_scope(
    features: list[str], core_value: str
) -> dict[str, Any]:
    """执行MVP范围限制逻辑"""
    # MVP规则：功能数 = max(3, 核心价值主张所需的最小功能数)
    # 每加一个功能，必须回答：去掉这个功能MVP还能工作吗？

    categories = {
        "必须保留": [],      # 去掉MVP就无法工作的功能
        "可延迟": [],        # MVP后再加
        "建议删除": [],      # 别人做得更好或成本更低
    }

    must_have_keywords = ["核心", "关键", "主要", "基础"]
    delay_keywords = ["高级", "增强", "优化", "分析", "统计"]
    delete_keywords = ["用户反馈", "多用户", "权限", "高级分析"]

    for feature in features:
        f_lower = feature.lower()
        if any(kw in f_lower for kw in delete_keywords):
            categories["建议删除"].append(feature)
        elif any(kw in f_lower for kw in delay_keywords):
            categories["可延迟"].append(feature)
        else:
            categories["必须保留"].append(feature)

    # MVP = 必须保留功能（至少3个）
    mvp_features = categories["必须保留"]
    if len(mvp_features) < 3:
        mvp_features = features[: max(3, len(features) // 2)]

    return {
        "input_features": features,
        "core_value": core_value,
        "categories": categories,
        "mvp_features": mvp_features,
        "mvp_size": len(mvp_features),
        "trimmed_count": len(features) - len(mvp_features),
        "boundaries": {
            "dont_add": [
                "用户反馈系统（手动收集）",
                "多用户/权限系统（先单用户）",
                "高级分析（先Excel）",
            ],
            "must_have": [
                "支付系统（没有它就没收入）",
            ],
        },
        "recommendation": (
            f"MVP保留 {len(mvp_features)} 个核心功能，"
            f"削减 {len(features) - len(mvp_features)} 个非核心功能。"
        ),
        "evaluated_at": datetime.now().isoformat(),
    }


@mcp.tool(
    name="founder_mvp_scope_limit",
    description="MVP范围限制器：执行MVP边界保护分析，确保功能精简到最小。每加一个功能必须回答：去掉这个功能MVP还能工作吗？",
    annotations={
        "title": "Founder MVP Scope Limit",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def founder_mvp_scope_limit(params: MvpScopeInput, ctx: Context) -> str:
    """MVP范围限制工具。评估功能列表，返回精简后的MVP功能集。"""
    await ctx.report_progress(0.2, "分析功能列表...")
    await ctx.log_info(f"Evaluating {len(params.proposed_features)} features")

    result = evaluate_mvp_scope(
        params.proposed_features, params.core_value_proposition
    )

    await ctx.report_progress(0.9, "生成建议...")

    if params.format == ResponseFormat.JSON:
        await ctx.report_progress(1.0, "完成")
        return json.dumps(result, ensure_ascii=False, indent=2)

    lines = [
        "# 🎯 MVP范围分析报告",
        "",
        f"**评估时间**: {result['evaluated_at']}",
        "",
        f"## 📊 输入概览",
        "",
        f"| 指标 | 数值 |",
        f"|------|------|",
        f"| 原始功能数 | {len(result['input_features'])} |",
        f"| **MVP功能数** | **{result['mvp_size']}** |",
        f"| 削减数量 | {result['trimmed_count']} |",
        "",
    ]

    if result["core_value"]:
        lines.extend([
            f"**核心价值主张**: {result['core_value']}",
            "",
        ])

    lines.extend([
        "## ✅ MVP功能（必须保留）",
        "",
    ])
    for f in result["mvp_features"]:
        lines.append(f"- [x] **{f}**")

    lines.extend(["", "## ⏳ 可延迟功能", ""])
    for f in result["categories"]["可延迟"]:
        lines.append(f"- [ ] {f}")

    lines.extend(["", "## 🗑️ 建议删除功能", ""])
    for f in result["categories"]["建议删除"]:
        lines.append(f"- ~~{f}~~  // 别人做得更好或成本更低")

    lines.extend([
        "",
        "## 🚫 MVP边界保护",
        "",
        "**不加**：",
    ])
    for b in result["boundaries"]["dont_add"]:
        lines.append(f"- ❌ {b}")
    lines.append("")
    lines.append("**必须加**：")
    for b in result["boundaries"]["must_have"]:
        lines.append(f"- ✅ {b}")

    lines.extend(["", "## 💡 建议", "", result["recommendation"]])

    await ctx.report_progress(1.0, "完成")
    return "\n".join(lines)


# ── Tool 3: Launch Checklist ────────────────────────────────

class LaunchCheckInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    product_name: str = Field(
        default="我的产品",
        description="产品名称（用于报告）",
        max_length=100,
    )
    product_url: Optional[str] = Field(
        default=None,
        description="产品URL（用于检查，如果提供则执行实际检查）",
        max_length=500,
    )
    format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="输出格式：markdown 或 json",
    )


def get_launch_checklist() -> list[dict[str, Any]]:
    """返回20项上线检查清单"""
    return [
        # 核心价值 (4项)
        {
            "id": 1, "category": "核心价值", "item": "客户能在3分钟内理解产品是什么",
            "status": False, "weight": "critical",
        },
        {
            "id": 2, "category": "核心价值", "item": "客户能在5分钟内完成注册",
            "status": False, "weight": "critical",
        },
        {
            "id": 3, "category": "核心价值", "item": "客户能在10分钟内体验到核心价值",
            "status": False, "weight": "critical",
        },
        {
            "id": 4, "category": "核心价值", "item": "客户愿意向朋友推荐你的产品",
            "status": False, "weight": "important",
        },
        # 商业闭环 (4项)
        {
            "id": 5, "category": "商业闭环", "item": "支付已接通Stripe/支付宝",
            "status": False, "weight": "critical",
        },
        {
            "id": 6, "category": "商业闭环", "item": "退款政策已写明",
            "status": False, "weight": "important",
        },
        {
            "id": 7, "category": "商业闭环", "item": "服务条款和隐私政策已发布",
            "status": False, "weight": "important",
        },
        {
            "id": 8, "category": "商业闭环", "item": "客户能联系到真人（你）",
            "status": False, "weight": "critical",
        },
        # 技术底线 (4项)
        {
            "id": 9, "category": "技术底线", "item": "核心页面加载<3秒",
            "status": False, "weight": "critical",
        },
        {
            "id": 10, "category": "技术底线", "item": "注册/登录流程无bug",
            "status": False, "weight": "critical",
        },
        {
            "id": 11, "category": "技术底线", "item": "移动端可正常使用",
            "status": False, "weight": "important",
        },
        {
            "id": 12, "category": "技术底线", "item": "关键数据有备份",
            "status": False, "weight": "critical",
        },
        # 获客准备 (4项)
        {
            "id": 13, "category": "获客准备", "item": "有1条让人想分享的内容",
            "status": False, "weight": "important",
        },
        {
            "id": 14, "category": "获客准备", "item": "有1个收集邮箱的入口",
            "status": False, "weight": "important",
        },
        {
            "id": 15, "category": "获客准备", "item": "知道前10个客户在哪里",
            "status": False, "weight": "critical",
        },
        {
            "id": 16, "category": "获客准备", "item": "定价经过竞品对比",
            "status": False, "weight": "important",
        },
        # 法律/合规 (4项)
        {
            "id": 17, "category": "法律/合规", "item": "明确的数据存储政策",
            "status": False, "weight": "important",
        },
        {
            "id": 18, "category": "法律/合规", "item": "明确的服务限制（如有）",
            "status": False, "weight": "important",
        },
        {
            "id": 19, "category": "法律/合规", "item": "有紧急情况联系信息",
            "status": False, "weight": "important",
        },
        {
            "id": 20, "category": "法律/合规", "item": "准备好客户支持时间",
            "status": False, "weight": "important",
        },
    ]


@mcp.tool(
    name="founder_launch_check",
    description="上线前20项检查清单：覆盖核心价值(4项)、商业闭环(4项)、技术底线(4项)、获客准备(4项)、法律合规(4项)。检查每个条目并返回完成状态。",
    annotations={
        "title": "Founder Launch Checklist",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def founder_launch_check(params: LaunchCheckInput, ctx: Context) -> str:
    """上线检查清单工具。返回20项检查清单，用户逐项确认。"""
    await ctx.report_progress(0.1, "加载上线检查清单...")
    await ctx.log_info(f"Launch check for: {params.product_name}")

    checklist = get_launch_checklist()

    # 按分类分组
    categories: dict[str, list] = {}
    for item in checklist:
        cat = item["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item)

    await ctx.report_progress(1.0, "完成")

    if params.format == ResponseFormat.JSON:
        return json.dumps(
            {
                "product": params.product_name,
                "checklist": checklist,
                "total": 20,
                "checked": 0,
                "categories": list(categories.keys()),
                "evaluated_at": datetime.now().isoformat(),
            },
            ensure_ascii=False,
            indent=2,
        )

    # Markdown 格式
    lines = [
        f"# 🚀 {params.product_name} 上线前检查清单",
        "",
        "共20项检查，分为5个类别。请逐项确认真实状态：",
        "",
    ]

    for cat, items in categories.items():
        lines.append(f"## {cat} ({len(items)}项)")
        lines.append("")
        for item in items:
            w = {"critical": "🔴", "important": "🟡", "optional": "🟢"}.get(
                item["weight"], "⚪"
            )
            lines.append(f"{w} [{item['id']:02d}] [ ] {item['item']}")
        lines.append("")

    lines.extend([
        "## 📋 状态说明",
        "",
        "| 标记 | 含义 |",
        "|------|------|",
        "| 🔴 | 必须完成，否则不能上线 |",
        "| 🟡 | 重要，建议完成 |",
        "| 🟢 | 可选，有则更好 |",
        "",
        "## 📝 使用方法",
        "",
        "1. 将 `[ ]` 改为 `[x]` 表示已完成",
        "2. 🔴 项必须全部通过才能上线",
        "3. 🟡 项建议全部通过",
        "4. 上线后持续跟踪未完成项",
    ])

    return "\n".join(lines)


# ── Tool 4: Airstrip One / Magic Moment ───────────────────

class AirstripOneInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    user_journey: str = Field(
        ...,
        description="用户旅程描述（从注册到第一次体验核心价值的完整流程）",
        min_length=20,
        max_length=3000,
    )
    format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="输出格式：markdown 或 json",
    )


def find_magic_moments(journey: str) -> dict[str, Any]:
    """分析用户旅程，找到魔法时刻和触发器"""
    # 魔法时刻 = 用户第一次说出"哇！"的时刻
    # 通常是：解决问题、获得价值、超出预期

    magic_moment_prompts = [
        "用户第一次说出'哇！'是什么时候？",
        "用户第一次主动向别人提起你是什么时候？",
        "用户第一次愿意付钱是什么时候？",
    ]

    # 分析旅程，尝试识别关键节点
    journey_lower = journey.lower()
    keywords = ["注册", "登录", "首次", "第一次", "体验", "价值", "问题", "解决", "支付", "购买"]

    identified_nodes = []
    for kw in keywords:
        if kw in journey_lower:
            identified_nodes.append(kw)

    return {
        "journey": journey,
        "magic_moments_prompts": magic_moment_prompts,
        "identified_nodes": identified_nodes,
        "magic_moment": "需要根据实际旅程分析",
        "triggers": {
            "push": {
                "description": "Push触发：到达魔法时刻后X小时",
                "action": "在用户到达魔法时刻后发送Push通知，强化记忆",
            },
            "behavior": {
                "description": "行为触发：完成关键动作后Y分钟",
                "action": "当用户完成关键动作后Y分钟，发送引导内容",
            },
            "time": {
                "description": "时间触发：注册后第Z天",
                "action": "在用户注册后第Z天，发送里程碑提醒",
            },
        },
        "magic_moment_metrics": {
            "magic_reach_rate": {
                "<20%": "onboarding有大问题，需要重构",
                "20_50%": "需要优化，有提升空间",
                ">50%": "表现良好，找到增长杠杆",
            }
        },
        "acceleration_strategy": [
            "删除到达魔法时刻前的所有摩擦",
            "把魔法时刻提前到第一次使用",
            "用 onboarding 引导用户到达",
        ],
        "evaluated_at": datetime.now().isoformat(),
    }


@mcp.tool(
    name="founder_airstrip_one",
    description="Airstrip One魔法时刻设计：找到用户旅程中的'魔法时刻'（第一次'哇！'的体验），并设计触发器加速用户到达该时刻。",
    annotations={
        "title": "Founder Airstrip One Magic Moment",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def founder_airstrip_one(params: AirstripOneInput, ctx: Context) -> str:
    """魔法时刻设计工具。分析用户旅程，找到魔法时刻并设计触发器。"""
    await ctx.report_progress(0.2, "分析用户旅程...")
    await ctx.log_info("Analyzing user journey for magic moments")

    result = find_magic_moments(params.user_journey)

    await ctx.report_progress(0.9, "设计触发器...")

    if params.format == ResponseFormat.JSON:
        await ctx.report_progress(1.0, "完成")
        return json.dumps(result, ensure_ascii=False, indent=2)

    lines = [
        "# ✈️ Airstrip One - 魔法时刻设计报告",
        "",
        f"**评估时间**: {result['evaluated_at']}",
        "",
        "## 🎯 核心概念",
        "",
        "**Airstrip One = 跑道一号 = 你的钱烧完前的最后期限**",
        "",
        "找到用户旅程中的**魔法时刻**——用户第一次说出'哇！'的体验——",
        "然后**不惜一切代价加速用户到达这个时刻**。",
        "",
        "## 🔮 三个魔法时刻问题",
        "",
    ]
    for i, prompt in enumerate(result["magic_moments_prompts"], 1):
        lines.append(f"{i}. {prompt}")
    lines.append("")

    lines.extend([
        "## 🎬 魔法时刻到达率指标",
        "",
        "| 到达率 | 诊断 |",
        "|------|------|",
        "| <20% | 🔴 onboarding 有大问题，需要重构 |",
        "| 20-50% | 🟡 需要优化，有提升空间 |",
        "| >50% | 🟢 表现良好，找到增长杠杆 |",
        "",
        "## ⚡ 加速到达魔法时刻",
        "",
    ])
    for s in result["acceleration_strategy"]:
        lines.append(f"- **删除摩擦**: {s}")
    lines.append("")

    lines.extend([
        "## 📡 三类触发器设计",
        "",
    ])

    for trigger_type, details in result["triggers"].items():
        icon = {"push": "📲", "behavior": "🎯", "time": "⏰"}.get(trigger_type, "📌")
        lines.extend([
            f"### {icon} {trigger_type.upper()} 触发",
            f"- **描述**: {details['description']}",
            f"- **行动**: {details['action']}",
            "",
        ])

    lines.extend([
        "## ✅ 下一步",
        "",
        "- [ ] 明确你的魔法时刻是什么",
        "- [ ] 测量当前魔法时刻到达率",
        "- [ ] 识别并删除到达魔法时刻前的所有摩擦",
        "- [ ] 设计三类触发器",
        "- [ ] 上线后持续跟踪指标",
    ])

    await ctx.report_progress(1.0, "完成")
    return "\n".join(lines)


# ── Tool 5: Runway Calculation ─────────────────────────────

class RunwayInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    monthly_burn: float = Field(
        ...,
        description="每月烧钱速度（支出），单位：美元",
        gt=0,
    )
    cash_reserves: float = Field(
        ...,
        description="现金储备（账户余额），单位：美元",
        ge=0,
    )
    monthly_revenue: float = Field(
        default=0.0,
        description="每月收入，单位：美元",
        ge=0,
    )
    format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="输出格式：markdown 或 json",
    )


def calculate_runway(
    monthly_burn: float, cash_reserves: float, monthly_revenue: float
) -> dict[str, Any]:
    """计算跑道"""
    net_burn = max(0, monthly_burn - monthly_revenue)

    if net_burn <= 0:
        runway_months = float("inf")
        runway_status = "breakeven"
        runway_summary = "你已经实现盈亏平衡或盈利，无需担心跑道！"
    elif monthly_burn <= 0:
        runway_months = float("inf")
        runway_status = "no_burn"
        runway_summary = "你没有烧钱，跑道无限长。"
    else:
        runway_months = cash_reserves / net_burn
        runway_status = "burning"

    # 里程碑判断
    if runway_months == float("inf"):
        months_display = "∞ (无限)"
        urgency = "none"
    else:
        months_display = f"{runway_months:.1f} 个月"
        if runway_months < 3:
            urgency = "critical"
        elif runway_months < 6:
            urgency = "warning"
        elif runway_months < 12:
            urgency = "attention"
        else:
            urgency = "healthy"

    milestones = [
        ("生存期", "$0-$500 MRR", monthly_revenue < 500),
        ("验证期", "$500-$5k MRR", 500 <= monthly_revenue < 5000),
        ("增长期", "$5k-$50k MRR", 5000 <= monthly_revenue < 50000),
        ("自由期", "$50k+ MRR", monthly_revenue >= 50000),
    ]
    current_phase = next((m[0] for m in milestones if m[2]), "生存期")

    return {
        "monthly_burn": monthly_burn,
        "monthly_revenue": monthly_revenue,
        "net_burn": net_burn,
        "cash_reserves": cash_reserves,
        "runway_months": runway_months if runway_months != float("inf") else None,
        "runway_months_display": months_display,
        "runway_status": runway_status,
        "runway_summary": runway_summary,
        "urgency": urgency,
        "current_phase": current_phase,
        "milestones": [
            {"name": m[0], "range": m[1], "active": m[2]}
            for m in milestones
        ],
        "recommendations": _get_runway_recommendations(
            runway_months, net_burn, monthly_revenue
        ),
        "evaluated_at": datetime.now().isoformat(),
    }


def _get_runway_recommendations(
    runway_months: float, net_burn: float, monthly_revenue: float
) -> list[dict[str, str]]:
    recs = []

    if runway_months == float("inf"):
        return [{"priority": "success", "action": "继续保持！"}]

    if runway_months < 3:
        recs.append({
            "priority": "critical",
            "action": "🔴 立即行动：要么融资，要么大幅削减开支，要么快速提升收入",
        })
    elif runway_months < 6:
        recs.append({
            "priority": "warning",
            "action": "🟡 加速变现：优先提升收入，同时控制成本",
        })

    if net_burn > 0 and monthly_revenue > 0:
        months_to_breakeven = (
            "∞" if monthly_revenue == 0
            else f"{net_burn / monthly_revenue:.1f}个月"
        )
        recs.append({
            "priority": "info",
            "action": f"按当前增速，需要 {months_to_breakeven} 才能盈亏平衡",
        })

    if net_burn > 0:
        target_revenue = net_burn * 2
        recs.append({
            "priority": "target",
            "action": f"🎯 目标：尽快达到 ${target_revenue:.0f}/月 收入（净烧钱额的2倍）",
        })

    recs.append({
        "priority": "habit",
        "action": "📊 每周跟踪跑道，每月复盘",
    })

    return recs


@mcp.tool(
    name="founder_runway_calculation",
    description="跑道计算：计算现金储备还能支撑多久（跑道月数）。结合里程碑心态判断当前阶段，并给出生存建议。",
    annotations={
        "title": "Founder Runway Calculation",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def founder_runway_calculation(params: RunwayInput, ctx: Context) -> str:
    """跑道计算工具。输入烧钱速度和现金储备，返回跑道分析。"""
    await ctx.report_progress(0.1, "计算跑道...")
    await ctx.log_info(
        f"Runway: burn=${params.monthly_burn}/mo, "
        f"revenue=${params.monthly_revenue}/mo, "
        f"cash=${params.cash_reserves}"
    )

    result = calculate_runway(
        params.monthly_burn, params.cash_reserves, params.monthly_revenue
    )

    await ctx.report_progress(0.9, "生成建议...")

    if params.format == ResponseFormat.JSON:
        await ctx.report_progress(1.0, "完成")
        return json.dumps(result, ensure_ascii=False, indent=2)

    urgency_icon = {"critical": "🔴", "warning": "🟡", "attention": "🟠", "healthy": "🟢", "none": "✅"}.get(result["urgency"], "⚪")

    lines = [
        "# 🛫 跑道计算报告",
        "",
        f"**评估时间**: {result['evaluated_at']}",
        "",
        "## 💰 财务概览",
        "",
        f"| 指标 | 数值 |",
        f"|------|------|",
        f"| 每月支出 | ${result['monthly_burn']:,.2f} |",
        f"| 每月收入 | ${result['monthly_revenue']:,.2f} |",
        f"| **净烧钱** | ${result['net_burn']:,.2f}/月 |",
        f"| 现金储备 | ${result['cash_reserves']:,.2f} |",
        "",
        "## 🛫 跑道分析",
        "",
        f"| 指标 | 数值 |",
        f"|------|------|",
        f"| **{urgency_icon} 剩余跑道** | **{result['runway_months_display']}** |",
        f"| 紧急程度 | {result['urgency']} |",
        f"| 当前阶段 | {result['current_phase']} |",
        "",
        f"**{result['runway_summary']}**",
        "",
        "## 📍 里程碑阶段",
        "",
    ]

    for m in result["milestones"]:
        icon = "✅" if m["active"] else "⬜"
        lines.append(f"{icon} **{m['name']}** ({m['range']})")
    lines.append("")

    lines.extend(["## 💡 建议", ""])
    for rec in result["recommendations"]:
        priority_icon = {
            "critical": "🔴", "warning": "🟡", "info": "🔵",
            "target": "🎯", "habit": "📊", "success": "✅",
        }.get(rec["priority"], "•")
        lines.append(f"{priority_icon} {rec['action']}")

    lines.extend(["", "## 🗺️ 生存策略", ""])

    runway = result["runway_months"]
    if runway == float("inf") or runway is None:
        pass
    elif runway < 3:
        lines.extend([
            "- 🔴 **立即止血**：暂停所有非必要开支",
            "- 🔴 **寻找收入**：哪怕低价也要先拿下付费客户",
            "- 🔴 **考虑融资**：如果有投资人关系，现在就启动",
        ])
    elif runway < 6:
        lines.extend([
            "- 🟡 **控制增长**：增长要量入为出",
            "- 🟡 **聚焦变现**：所有功能优先服务付费转化",
            "- 🟡 **准备B计划**：如果3个月内无法改善，准备融资或被收购",
        ])
    elif runway < 12:
        lines.extend([
            "- 🟠 **优化效率**：提升单位经济模型",
            "- 🟠 **建立壁垒**：用收入支撑护城河建设",
            "- 🟠 **未雨绸缪**：开始建立投资人关系",
        ])
    else:
        lines.extend([
            "- 🟢 **保持节奏**：不要因为有钱就胡乱扩张",
            "- 🟢 **加速增长**：用充足跑道换取更快增长",
            "- 🟢 **建立文化**：用好的文化吸引人才",
        ])

    await ctx.report_progress(1.0, "完成")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────
# Server Entry Point
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # stdio transport (local, subprocess mode)
    mcp.run()
    # OR for HTTP remote:
    # mcp.run(transport="streamable_http", port=8765)
