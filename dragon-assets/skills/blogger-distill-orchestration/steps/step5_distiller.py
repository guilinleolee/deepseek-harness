# -*- coding: utf-8 -*-
"""
Step5Distiller — 风格蒸馏提取管道
来源: blogger-distill-orchestration SKILL.md (lines 172-206)

蒸馏管道：Step5Distiller + distill_style + generate_skill_files
输出: distill_guide.md (Mode A) / self_analysis.md (Mode B) + skill_files/6节/
"""

import json
import os
import re
from typing import Any, Optional


# ── 三维度常量 ──────────────────────────────────────────────────────────────

MODE_A_DIMENSIONS = [
    "像 TA 一样思考",
    "像 TA 一样决策",
    "像 TA 一样写",
]

MODE_B_DIMENSIONS = [
    "你的思考模式",
    "你的决策风格",
    "你的写作方式",
]


# ── 风格元素提取 ─────────────────────────────────────────────────────────

def _extract_thinking_pattern(report: dict, stats: dict) -> dict:
    """提取思考模式"""
    dimensions = report.get("dimensions", [])
    summary = report.get("summary", {})

    # 从 D1(标题策略) 和 D9(内容多样性) 推导思考模式
    d1 = next((d for d in dimensions if d.get("name") == "D1_标题策略"), {})
    d9 = next((d for d in dimensions if d.get("name") == "D9_内容多样性"), {})

    return {
        "core_trait": summary.get("writing_style", "信息分享型"),
        "title_strategy": d1.get("description", ""),
        "content_structure": summary.get("content_framework", "干货优先"),
        "diversity_score": d9.get("score", 0),
        "emotional_tone": summary.get("emotional_tone", "理性中立"),
    }


def _extract_decision_pattern(report: dict, stats: dict) -> dict:
    """提取决策风格"""
    dimensions = report.get("dimensions", [])
    posting_freq = stats.get("posting_frequency", {})

    # 从 D7(时间分布) 和 D5(商业化潜力) 推导决策风格
    d7 = next((d for d in dimensions if d.get("name") == "D7_时间分布"), {})
    d5 = next((d for d in dimensions if d.get("name") == "D5_商业化潜力"), {})

    return {
        "posting_rhythm": posting_freq.get("pattern", "不固定"),
        "frequency_per_week": posting_freq.get("avg_posts_per_week", 0),
        "timing_preference": d7.get("description", "晚间发布"),
        "commercial_orientation": d5.get("score", 0),
        "commercial_style": summary_from_score(d5.get("score", 0)),
    }


def _extract_writing_pattern(report: dict, stats: dict) -> dict:
    """提取写作风格"""
    dimensions = report.get("dimensions", [])
    summary = report.get("summary", {})

    # 从 D2(内容框架) 和 D3(视觉风格) 推导写作模式
    d2 = next((d for d in dimensions if d.get("name") == "D2_内容框架"), {})
    d3 = next((d for d in dimensions if d.get("name") == "D3_视觉风格"), {})
    avg_content = stats.get("avg_content_length", 0)

    return {
        "framework": d2.get("description", ""),
        "avg_length": avg_content,
        "visual_style": d3.get("description", ""),
        "image_count_avg": stats.get("avg_image_count", 0),
        "tag_usage": summary.get("tag_usage", "精准标签"),
        "content_tone": summary.get("writing_style", "信息分享型"),
    }


def summary_from_score(score: float) -> str:
    """分数 → 文字描述"""
    if score >= 8:
        return "高度商业化"
    elif score >= 6:
        return "适度商业化"
    elif score >= 4:
        return "低商业化"
    else:
        return "纯内容创作"


# ── 创作指南生成 (Mode A) ───────────────────────────────────────────────

def _build_distill_guide(
    blogger_name: str,
    thinking: dict,
    decision: dict,
    writing: dict,
    stats: dict,
    dimensions: list[dict],
) -> str:
    """生成 Mode A 创作指南"""
    lines = [
        f"# {blogger_name} 风格创作指南",
        "",
        "> 本指南由 blogger-distill-orchestration 自动生成",
        f"> 来源: {len(stats.get('notes', []))} 条笔记分析",
        "",
        "## 一句话定位",
        "",
        f"**{thinking['core_trait']} · {writing['framework']} · {decision['commercial_style']}**",
        "",
        "---",
        "",
    ]

    # ── 维度1: 像 TA 一样思考
    lines += [
        "## 像 TA 一样思考",
        "",
        "### 核心理念",
        "",
        f"TA 的内容底层逻辑是「**{thinking['core_trait']}**」，",
        f"体现在标题策略上表现为: {thinking['title_strategy']}。",
        "",
        "### 选题倾向",
        "",
    ]

    # 从各个维度中提取选题关键词
    for dim in dimensions:
        desc = dim.get("description", "")
        if desc and len(desc) > 5:
            lines.append(f"- {desc}")

    lines += [
        "",
        "### 内容深度",
        "",
        f"平均正文长度 **{writing['avg_length']}** 字，",
        f"属于「{'深度长文' if writing['avg_length'] > 800 else '中等篇幅' if writing['avg_length'] > 400 else '简短精炼'}」类型。",
        "",
        f"内容多样性评分 **{thinking['diversity_score']}/10**，",
        f"情感基调 **{thinking['emotional_tone']}**。",
        "",
        "---",
        "",
    ]

    # ── 维度2: 像 TA 一样决策
    lines += [
        "## 像 TA 一样决策",
        "",
        "### 发布节奏",
        "",
        f"TA 采用「**{decision['posting_rhythm']}」发布策略，",
        f"平均每周 **{decision['frequency_per_week']:.1f}** 篇，",
        f"最佳发布时段: {decision['timing_preference']}。",
        "",
        "### 商业化决策",
        "",
        f"商业化程度: **{decision['commercial_orientation']}/10** — {decision['commercial_style']}。",
        "",
        "### 标签决策",
        "",
        f"标签策略: {writing['tag_usage']}，平均每篇 **{stats.get('avg_tag_count', 0):.0f}** 个标签。",
        "",
        "---",
        "",
    ]

    # ── 维度3: 像 TA 一样写
    lines += [
        "## 像 TA 一样写",
        "",
        "### 内容框架",
        "",
        f"TA 偏好的框架是「**{writing['framework']}」。",
        "",
        "### 视觉风格",
        "",
        f"视觉呈现: {writing['visual_style']}，",
        f"平均每篇 **{writing['image_count_avg']:.0f}** 张图片。",
        "",
        "### 文案调性",
        "",
        f"整体调性: **{writing['content_tone']}**，情感色彩 **{thinking['emotional_tone']}**。",
        "",
        "---",
        "",
        "## 关键指标速查",
        "",
        "| 指标 | 数值 |",
        "|------|------|",
        f"| 平均点赞 | {stats.get('avg_liked', 0):.0f} |",
        f"| 平均收藏 | {stats.get('avg_collected', 0):.0f} |",
        f"| 平均评论 | {stats.get('avg_comment', 0):.0f} |",
        f"| 平均转发 | {stats.get('avg_share', 0):.0f} |",
        f"| 平均互动率 | {stats.get('avg_engagement_rate', 0):.1f}% |",
        f"| 平均图文量 | {writing['avg_length']:.0f}字 |",
        f"| 平均图片数 | {writing['image_count_avg']:.0f}张 |",
        f"| 原创率 | {stats.get('originality_rate', 0):.0%} |",
        "",
    ]

    return "\n".join(lines)


# ── 自我分析报告生成 (Mode B) ───────────────────────────────────────

def _build_self_analysis(
    blogger_name: str,
    thinking: dict,
    decision: dict,
    writing: dict,
    stats: dict,
) -> str:
    """生成 Mode B 自我分析报告"""
    lines = [
        f"# {blogger_name} 自我分析报告",
        "",
        "> 本报告由 blogger-distill-orchestration 自动生成",
        f"> 分析范围: {len(stats.get('notes', []))} 条笔记",
        "",
        "---",
        "",
    ]

    # ── 维度1: 你的思考模式
    lines += [
        "## 你的思考模式",
        "",
        f"**核心创作理念**: {thinking['core_trait']}",
        "",
        f"- 标题策略: {thinking['title_strategy']}",
        f"- 内容结构: {thinking['content_structure']}",
        f"- 情感基调: {thinking['emotional_tone']}",
        f"- 多样性得分: {thinking['diversity_score']}/10",
        "",
        "### 创作思维诊断",
        "",
    ]

    # 思维模式分类
    if thinking['diversity_score'] >= 7:
        lines.append("- 你是**探索型**创作者，风格多元，敢于尝试新形式")
    elif thinking['diversity_score'] >= 4:
        lines.append("- 你是**专注型**创作者，有稳定的内容方向")
    else:
        lines.append("- 你是**深耕型**创作者，专注于特定领域的持续输出")

    if thinking['emotional_tone'] in ["情感丰富", "高度情感化"]:
        lines.append("- 情感表达强烈，与受众建立深层情感连接")
    else:
        lines.append("- 理性叙事为主，信息传递效率优先")

    lines += [
        "",
        "---",
        "",
    ]

    # ── 维度2: 你的决策风格
    lines += [
        "## 你的决策风格",
        "",
        f"**发布节奏**: {decision['posting_rhythm']} — 平均每周 {decision['frequency_per_week']:.1f} 篇",
        f"- 发布时间偏好: {decision['timing_preference']}",
        f"- 商业化程度: {decision['commercial_orientation']}/10 — {decision['commercial_style']}",
        "",
        "### 决策风格诊断",
        "",
    ]

    if decision['frequency_per_week'] >= 5:
        lines.append("- 高频输出型: 内容产量高，需要规模化生产流程")
    elif decision['frequency_per_week'] >= 2:
        lines.append("- 稳定更新型: 兼顾质量与产量的平衡状态")
    else:
        lines.append("- 精品路线型: 追求单篇质量而非数量")

    if decision['commercial_orientation'] >= 7:
        lines.append("- 商业意识强: 变现能力突出，需注意内容与商业的平衡")
    elif decision['commercial_orientation'] <= 3:
        lines.append("- 纯创作者: 坚持内容初心，商业化潜力待挖掘")
    else:
        lines.append("- 平衡型: 内容与商业兼顾，适合长期发展")

    lines += [
        "",
        "---",
        "",
    ]

    # ── 维度3: 你的写作方式
    lines += [
        "## 你的写作方式",
        "",
        f"**框架偏好**: {writing['framework']}",
        f"**视觉风格**: {writing['visual_style']}",
        f"- 平均篇幅: {writing['avg_length']:.0f} 字",
        f"- 平均图片: {writing['image_count_avg']:.0f} 张",
        f"- 标签策略: {writing['tag_usage']}",
        "",
        "### 写作方式诊断",
        "",
    ]

    if writing['avg_length'] > 800:
        lines.append("- **深度内容型**: 擅长长文输出，信息密度高")
    elif writing['avg_length'] > 400:
        lines.append("- **均衡型**: 篇幅适中，阅读体验好")
    else:
        lines.append("- **精炼型**: 短小精悍，适合碎片化阅读场景")

    if writing['image_count_avg'] >= 6:
        lines.append("- **视觉丰富型**: 重度依赖图片表达，图文结合紧密")
    elif writing['image_count_avg'] >= 3:
        lines.append("- **图文平衡型**: 图片辅助文字，相得益彰")
    else:
        lines.append("- **文字主导型**: 以文字为核心，图片点缀")

    lines += [
        "",
        "---",
        "",
        "## 综合诊断",
        "",
        "| 维度 | 评分 | 描述 |",
        "|------|------|------|",
        f"| 内容多样性 | {thinking['diversity_score']:.0f}/10 | {'多元探索' if thinking['diversity_score'] >= 7 else '稳定深耕'} |",
        f"| 发布频率 | {min(10, decision['frequency_per_week'] * 2):.0f}/10 | {'高频' if decision['frequency_per_week'] >= 5 else '稳定' if decision['frequency_per_week'] >= 2 else '低频精品'} |",
        f"| 商业化程度 | {decision['commercial_orientation']:.0f}/10 | {decision['commercial_style']} |",
        f"| 篇幅深度 | {min(10, writing['avg_length'] / 100):.0f}/10 | {'深度' if writing['avg_length'] > 800 else '中等' if writing['avg_length'] > 400 else '精炼'} |",
        "",
    ]

    return "\n".join(lines)


# ── 6节 Skill 文件生成 ────────────────────────────────────────────────

SKILL_FILE_TEMPLATES = {
    "01_标题策略": """# 01_标题策略

## 适用场景
学习 TA 的标题写法时调用本节

## 核心规律
{thinking_title}

## 模板示例
- 「{example_title_1}」
- 「{example_title_2}」
- 「{example_title_3}」

## 禁忌事项
- 避免{avoid_1}
- 避免{avoid_2}

## 快速调用
当用户说"帮我写标题"或"生成爆款标题"时，使用本模板。
""",
    "02_内容框架": """# 02_内容框架

## 适用场景
构建内容结构时调用本节

## 框架模式
{frame_pattern}

## 开篇写法
{opening_style}

## 结尾写法
{ending_style}

## 快速调用
当用户说"帮我规划内容结构"或"怎么写内容"时，使用本模板。
""",
    "03_视觉风格": """# 03_视觉风格

## 适用场景
设计图片排版时调用本节

## 视觉基调
{visual_base}

## 构图偏好
{composition}

## 色调倾向
{color_tone}

## 快速调用
当用户说"帮我设计图片"或"配图风格"时，使用本模板。
""",
    "04_互动策略": """# 04_互动策略

## 适用场景
引导用户互动时调用本节

## 评论区运营
{comment_strategy}

## 收藏引导
{favorite_guide}

## 转发引导
{share_guide}

## 快速调用
当用户说"怎么引导互动"或"增加收藏"时，使用本模板。
""",
    "05_商业化路径": """# 05_商业化路径

## 适用场景
制定变现策略时调用本节

## 商业化程度
{commercial_level}

## 可用变现方式
{monetization_ways}

## 植入技巧
{placement_tips}

## 快速调用
当用户说"怎么变现"或"商业合作"时，使用本模板。
""",
    "06_长期规划": """# 06_长期规划

## 适用场景
制定长期内容计划时调用本节

## 定位方向
{positioning}

## 成长路径
{growth_path}

## 阶段目标
{stage_goals}

## 快速调用
当用户说"长期发展"或"账号规划"时，使用本模板。
""",
}


def _generate_skill_files(
    blogger_name: str,
    thinking: dict,
    decision: dict,
    writing: dict,
    stats: dict,
    output_dir: str,
) -> list[str]:
    """生成 6 节 skill 文件"""
    skill_dir = os.path.join(output_dir, f"{blogger_name}_skill_files")
    os.makedirs(skill_dir, exist_ok=True)

    files = []

    # ── 01 标题策略
    notes = stats.get("notes", [])
    sample_titles = [n.get("title", "") for n in notes[:5] if n.get("title")]

    s1_path = os.path.join(skill_dir, "01_标题策略.md")
    with open(s1_path, "w", encoding="utf-8") as f:
        f.write(SKILL_FILE_TEMPLATES["01_标题策略"].format(
            thinking_title=thinking.get("title_strategy", "信息价值型"),
            example_title_1=sample_titles[0] if len(sample_titles) > 0 else "待补充",
            example_title_2=sample_titles[1] if len(sample_titles) > 1 else "待补充",
            example_title_3=sample_titles[2] if len(sample_titles) > 2 else "待补充",
            avoid_1="过度标题党",
            avoid_2="信息空洞",
        ))
    files.append(s1_path)

    # ── 02 内容框架
    s2_path = os.path.join(skill_dir, "02_内容框架.md")
    with open(s2_path, "w", encoding="utf-8") as f:
        f.write(SKILL_FILE_TEMPLATES["02_内容框架"].format(
            frame_pattern=writing.get("framework", "问题-分析-解决"),
            opening_style="开门见山或悬念切入，根据内容类型选择",
            ending_style="总结升华或互动引导",
        ))
    files.append(s2_path)

    # ── 03 视觉风格
    s3_path = os.path.join(skill_dir, "03_视觉风格.md")
    with open(s3_path, "w", encoding="utf-8") as f:
        f.write(SKILL_FILE_TEMPLATES["03_视觉风格"].format(
            visual_base=writing.get("visual_style", "简洁干净"),
            composition=f"平均{writing.get('image_count_avg', 0):.0f}张图片，图文比例适中",
            color_tone="根据内容调性选择，整体协调统一",
        ))
    files.append(s3_path)

    # ── 04 互动策略
    s4_path = os.path.join(skill_dir, "04_互动策略.md")
    with open(s4_path, "w", encoding="utf-8") as f:
        f.write(SKILL_FILE_TEMPLATES["04_互动策略"].format(
            comment_strategy="主动提问，引导评论区讨论",
            favorite_guide="结尾提供实用价值，激发收藏动机",
            share_guide="共鸣点或实用信息促进转发",
        ))
    files.append(s4_path)

    # ── 05 商业化路径
    commercial_score = decision.get("commercial_orientation", 0)
    s5_path = os.path.join(skill_dir, "05_商业化路径.md")
    with open(s5_path, "w", encoding="utf-8") as f:
        f.write(SKILL_FILE_TEMPLATES["05_商业化路径"].format(
            commercial_level=f"{commercial_score}/10 — {decision.get('commercial_style', '低商业化')}",
            monetization_ways="种草带货/品牌合作/知识付费/引流私域（根据商业化程度选择）",
            placement_tips="软植入优先，避免硬广破坏内容体验",
        ))
    files.append(s5_path)

    # ── 06 长期规划
    s6_path = os.path.join(skill_dir, "06_长期规划.md")
    with open(s6_path, "w", encoding="utf-8") as f:
        f.write(SKILL_FILE_TEMPLATES["06_长期规划"].format(
            positioning=thinking.get("core_trait", "待定位"),
            growth_path=f"第1-3月稳定更新 · 第4-6月拓展内容边界 · 第7-12月形成独特风格",
            stage_goals=f"月度目标: 涨粉{'快' if decision.get('frequency_per_week', 0) >= 3 else '稳'} · 季度目标: 建立辨识度",
        ))
    files.append(s6_path)

    return files


# ── Step5 主类 ──────────────────────────────────────────────────────────────

class Step5Distiller:
    """
    Step 5 风格蒸馏提取管道

    依赖:
      - xiaohongshu-content-analyzer (P0-2)
      - _extract_thinking_pattern()
      - _extract_decision_pattern()
      - _extract_writing_pattern()
      - _build_distill_guide()
      - _build_self_analysis()
      - _generate_skill_files()

    输入:
      - {blogger_name}_analysis.json (Step4 产出)
      - {blogger_name}_stats.json (Step4 产出)

    处理:
      1. _extract_thinking/decision/writing_pattern() → 提取三维度特征
      2. Mode A: _build_distill_guide() → 创作指南 + _generate_skill_files()
      3. Mode B: _build_self_analysis() → 自我分析报告

    输出:
      - {blogger_name}_distill_guide.md (Mode A)
      - {blogger_name}_self_analysis.md (Mode B)
      - {blogger_name}_skill_files/ (Mode A)
      - distill_summary.json

    关键参数:
      - mode: "learn" (学习他人) | "self" (自我分析)
    """

    def __init__(
        self,
        mode: str = "learn",
        output_dir: str = "./output",
    ):
        self.mode = mode
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def run(self, report: dict, stats: dict) -> dict:
        """
        执行蒸馏流程

        Args:
            report: 从 {blogger_name}_analysis.json 加载的分析报告
            stats: 从 {blogger_name}_stats.json 加载的统计数据

        Returns:
            dict: 蒸馏结果摘要
        """
        blogger_name = report.get("blogger_name", stats.get("blogger_name", "unknown"))
        print(f"[Step5Distiller] 开始蒸馏 blogger={blogger_name}, mode={self.mode}")

        # ── 提取三维度特征
        thinking = _extract_thinking_pattern(report, stats)
        decision = _extract_decision_pattern(report, stats)
        writing = _extract_writing_pattern(report, stats)

        print(f"[Step5Distiller] 三维度提取完成: 思考={thinking['core_trait']}, "
              f"决策={decision['commercial_style']}, 写作={writing['framework']}")

        output_files = []

        if self.mode == "learn":
            # ── Mode A: 学习他人风格
            guide = _build_distill_guide(blogger_name, thinking, decision, writing, stats, report.get("dimensions", []))
            guide_path = os.path.join(self.output_dir, f"{blogger_name}_distill_guide.md")
            with open(guide_path, "w", encoding="utf-8") as f:
                f.write(guide)
            output_files.append(guide_path)
            print(f"[Step5Distiller] 创作指南已写入: {guide_path}")

            # 生成 6 节 skill 文件
            skill_files = _generate_skill_files(blogger_name, thinking, decision, writing, stats, self.output_dir)
            output_files.extend(skill_files)
            print(f"[Step5Distiller] skill_files 已生成: {len(skill_files)} 个")

        else:
            # ── Mode B: 自我分析
            self_analysis = _build_self_analysis(blogger_name, thinking, decision, writing, stats)
            analysis_path = os.path.join(self.output_dir, f"{blogger_name}_self_analysis.md")
            with open(analysis_path, "w", encoding="utf-8") as f:
                f.write(self_analysis)
            output_files.append(analysis_path)
            print(f"[Step5Distiller] 自我分析报告已写入: {analysis_path}")

        # ── 写入蒸馏摘要
        summary = {
            "blogger_name": blogger_name,
            "mode": self.mode,
            "dimensions": {
                "thinking": thinking,
                "decision": decision,
                "writing": writing,
            },
            "output_files": [os.path.basename(f) for f in output_files],
            "stats_snapshot": {
                "total_notes": stats.get("total_notes", 0),
                "avg_liked": stats.get("avg_liked", 0),
                "avg_collected": stats.get("avg_collected", 0),
                "avg_engagement_rate": stats.get("avg_engagement_rate", 0),
            },
        }

        summary_path = os.path.join(self.output_dir, f"{blogger_name}_distill_summary.json")
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        print(f"[Step5Distiller] 完成: mode={self.mode}, 产出{len(output_files)}个文件")
        print(f"[Step5Distiller] 摘要: {summary_path}")

        return {
            "blogger_name": blogger_name,
            "mode": self.mode,
            "thinking_trait": thinking["core_trait"],
            "decision_style": decision["commercial_style"],
            "writing_framework": writing["framework"],
            "output_files": output_files,
            "distill_summary_path": summary_path,
        }
