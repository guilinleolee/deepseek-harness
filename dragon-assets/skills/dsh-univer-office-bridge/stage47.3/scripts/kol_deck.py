"""阶段 47.3 · Slide + agent-reach 联动（KOL 选题 .pptx 自动生成）

本脚本：
  1. 调用 agent-reach 多平台调研（模拟 4 平台：xhs/weibo/zhihu/bilibili）的 FetchResult 接口语义
  2. 交叉汇总 → 自动产出 KOL 选题 .pptx（5 页）

Author: dragon-engine · Stage 47.3 · 2026-08-26
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from datetime import date as _date, datetime, timezone, timedelta
from pathlib import Path
from typing import Any

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor as PptxRGBColor
from pptx.enum.shapes import MSO_SHAPE


TZ_CN = timezone(timedelta(hours=8))
PRIMARY = PptxRGBColor(0x2E, 0x5C, 0x8A)
SECONDARY = PptxRGBColor(0x55, 0x55, 0x55)
ACCENT = PptxRGBColor(0xC0, 0x39, 0x2B)


# ─── 模拟 FetchResult（与 agent-reach V1.5.0 / a-stock-data-bridge 同构） ─────

@dataclass
class ReachResult:
    """agent-reach 多平台调研单条结果 · 接口语义"""
    platform: str           # xhs / weibo / zhihu / bilibili / etc.
    query: str
    posts: list[dict]       # [{"author": ..., "title": ..., "summary": ..., "engagement": int, "url": ...}]
    fetched_at: str = field(default_factory=lambda: datetime.now(TZ_CN).isoformat())
    backend: str = "opencli"  # opencli / exa / mcporter / etc.
    error: str | None = None

    @property
    def total_engagement(self) -> int:
        return sum(p.get("engagement", 0) for p in self.posts)

    def to_dict(self):
        return {
            "platform": self.platform,
            "query": self.query,
            "fetched_at": self.fetched_at,
            "backend": self.backend,
            "count": len(self.posts),
            "total_engagement": self.total_engagement,
            "error": self.error,
        }


def mock_xhs_search(query: str) -> ReachResult:
    """agent-reach xiaohongshu 平台调研结果"""
    posts = [
        {"author": "@AI产品经理李", "title": "AI 工具横评：我用了 30 款，这 5 款最值得推荐",
         "summary": "实测对比 ChatGPT/Claude/Gemini/文心/通义，附场景适配表",
         "engagement": 12400, "url": "https://xiaohongshu.com/explore/abc"},
        {"author": "@效率提升指南", "title": "3 个让工作效率翻倍的 Notion 模板",
         "summary": "项目管理 + 周报模板 + 知识库，附下载",
         "engagement": 8900, "url": "https://xiaohongshu.com/explore/def"},
        {"author": "@职场小白成长", "title": "工作 3 年才明白的 5 个道理",
         "summary": "沟通、复利、长期主义、自我迭代",
         "engagement": 6700, "url": "https://xiaohongshu.com/explore/ghi"},
        {"author": "@编程小哥", "title": "VS Code 9 个神仙插件",
         "summary": "GitLens + Prettier + 通义灵码 + Continue",
         "engagement": 5400, "url": "https://xiaohongshu.com/explore/jkl"},
    ]
    return ReachResult(platform="xiaohongshu", query=query, posts=posts)


def mock_weibo_search(query: str) -> ReachResult:
    """agent-reach weibo 平台调研结果"""
    posts = [
        {"author": "@互联网那点事", "title": "#AI产品经理# 2026 年 AI 产品趋势观察",
         "summary": "从 GPT-5 到 Claude 4，2026 年 AI 产品的 5 大变化",
         "engagement": 32100, "url": "https://weibo.com/123"},
        {"author": "@科技每日推送", "title": "#编程技巧# 10 个 Git 命令让效率翻倍",
         "summary": "stash/cherry-pick/rebase 实战案例",
         "engagement": 21500, "url": "https://weibo.com/456"},
    ]
    return ReachResult(platform="weibo", query=query, posts=posts)


def mock_zhihu_search(query: str) -> ReachResult:
    """agent-reach zhihu 平台调研结果"""
    posts = [
        {"author": "机器之心", "title": "2026 年 AI 编程工具深度横评",
         "summary": "Cursor / Windsurf / Continue / Cody / Copilot 全方位对比，含实测代码质量数据",
         "engagement": 8900, "url": "https://zhuanlan.zhihu.com/p/123"},
        {"author": "效率火箭", "title": "职场人士必装的 10 款效率工具",
         "summary": "Obsidian + Notion + Things 3 + Alfred + Raycast",
         "engagement": 6700, "url": "https://zhuanlan.zhihu.com/p/456"},
        {"author": "前端早茶", "title": "React 19 实战：Server Components 入门到精通",
         "summary": "从原理到代码，含 3 个真实项目案例",
         "engagement": 5400, "url": "https://zhuanlan.zhihu.com/p/789"},
    ]
    return ReachResult(platform="zhihu", query=query, posts=posts)


def mock_bilibili_search(query: str) -> ReachResult:
    """agent-reach bilibili 平台调研结果"""
    posts = [
        {"author": "影视飓风", "title": "我用 GPT-4o 拍了一部短片",
         "summary": "AI 视频工具全流程实战",
         "engagement": 152000, "url": "https://bilibili.com/video/BV1"},
        {"author": "罗翔说刑法", "title": "聊聊职场法律那些事",
         "summary": "劳动合同 + 竞业限制 + 离职注意事项",
         "engagement": 89000, "url": "https://bilibili.com/video/BV2"},
    ]
    return ReachResult(platform="bilibili", query=query, posts=posts)


# ─── 主函数：4 平台调研 → 自动产出 .pptx ─────────────────────────────────

def build_kol_topic_deck(query: str, output_path: Path) -> dict:
    """调用 4 平台调研（agent-reach）→ 汇总 → 5 页 KOL 选题 .pptx"""
    # 1. 4 平台调研
    results = [
        mock_xhs_search(query),
        mock_weibo_search(query),
        mock_zhihu_search(query),
        mock_bilibili_search(query),
    ]

    # 2. 交叉汇总
    all_posts = []
    for r in results:
        for p in r.posts:
            p["platform"] = r.platform
            all_posts.append(p)

    # 按互动量排序
    all_posts.sort(key=lambda x: x.get("engagement", 0), reverse=True)
    top_posts = all_posts[:8]

    # 平台维度统计
    platform_stats = {
        r.platform: {
            "count": len(r.posts),
            "engagement": r.total_engagement,
            "backend": r.backend,
        }
        for r in results
    }

    # 选题候选（按互动量 Top 4）
    top_topics = []
    for p in top_posts[:4]:
        top_topics.append({
            "title": p["title"],
            "platform": p["platform"],
            "engagement": p["engagement"],
            "summary": p.get("summary", ""),
        })

    # 3. 写 .pptx
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Slide 1 — 封面
    slide1 = prs.slides.add_slide(blank_layout)
    title_box = slide1.shapes.add_textbox(Inches(0.5), Inches(2.5), Inches(12), Inches(1.5))
    tf = title_box.text_frame
    tf.text = f"KOL 选题调研报告"
    p = tf.paragraphs[0]
    p.font.size = Pt(44)
    p.font.bold = True
    if not p.runs:
        p.add_run()
    p.runs[0].font.color.rgb = PRIMARY

    sub_box = slide1.shapes.add_textbox(Inches(0.5), Inches(4.0), Inches(12), Inches(1))
    sub_box.text_frame.text = f"关键词：{query}    数据日期：{_date.today().isoformat()}"
    sp = sub_box.text_frame.paragraphs[0]
    sp.font.size = Pt(20)
    if not sp.runs:
        sp.add_run()
    sp.runs[0].font.color.rgb = SECONDARY

    source_box = slide1.shapes.add_textbox(Inches(0.5), Inches(5.0), Inches(12), Inches(1))
    source_box.text_frame.text = (
        "数据来源：agent-reach V1.5.0（4 平台调研）· 小红书 + 微博 + 知乎 + B站\n"
        "产出：dsh-univer-office-bridge · 阶段 47.3 联动"
    )
    ssp = source_box.text_frame.paragraphs[0]
    ssp.font.size = Pt(14)
    if not ssp.runs:
        ssp.add_run()
    ssp.runs[0].font.color.rgb = SECONDARY

    # Slide 2 — 平台调研概览（4 平台表格）
    slide2 = prs.slides.add_slide(blank_layout)
    title2 = slide2.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12), Inches(1))
    title2.text_frame.text = "平台调研概览"
    p2 = title2.text_frame.paragraphs[0]
    p2.font.size = Pt(28)
    p2.font.bold = True
    if not p2.runs:
        p2.add_run()
    p2.runs[0].font.color.rgb = PRIMARY

    # 表格
    table_shape = slide2.shapes.add_table(
        rows=5, cols=4, left=Inches(0.5), top=Inches(1.5),
        width=Inches(12), height=Inches(3),
    )
    table = table_shape.table
    headers = ["平台", "帖子数", "总互动量", "后端"]
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        cell.text = h
        for para in cell.text_frame.paragraphs:
            for run in para.runs:
                run.font.bold = True
                run.font.color.rgb = PptxRGBColor(0xFF, 0xFF, 0xFF)
        cell.fill.solid()
        cell.fill.fore_color.rgb = PRIMARY

    platform_name_zh = {"xiaohongshu": "小红书", "weibo": "微博", "zhihu": "知乎", "bilibili": "B站"}
    for i, r in enumerate(results, start=1):
        stats = platform_stats[r.platform]
        table.cell(i, 0).text = platform_name_zh[r.platform]
        table.cell(i, 1).text = str(stats["count"])
        table.cell(i, 2).text = f"{stats['engagement']:,}"
        table.cell(i, 3).text = stats["backend"]

    # Slide 3 — Top 4 选题候选
    slide3 = prs.slides.add_slide(blank_layout)
    title3 = slide3.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12), Inches(1))
    title3.text_frame.text = "Top 4 选题候选（按互动量排序）"
    p3 = title3.text_frame.paragraphs[0]
    p3.font.size = Pt(28)
    p3.font.bold = True
    if not p3.runs:
        p3.add_run()
    p3.runs[0].font.color.rgb = PRIMARY

    shape_list = []
    y_pos = 1.5
    for i, t in enumerate(top_topics):
        # 卡片
        card = slide3.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(0.5), Inches(y_pos), Inches(12.3), Inches(1.1),
        )
        card.fill.solid()
        card.fill.fore_color.rgb = PptxRGBColor(0xF5, 0xF5, 0xF5)
        card.line.color.rgb = PRIMARY
        # 编号
        num_box = card.text_frame.add_paragraph() if i == 0 else card.text_frame.paragraphs[0]
        # 用 textbox 内嵌更稳
        shape_list.append(card)
        y_pos += 1.3

    # 直接用 4 个 textbox 更清晰
    y_pos = 1.5
    # 删除上面的 shape_list 试验
    # 简单方式：4 个独立 textbox
    # 把卡片删了重做
    for s in shape_list:
        sp = s._element
        sp.getparent().remove(sp)

    for i, t in enumerate(top_topics):
        # 编号
        num_box = slide3.shapes.add_textbox(Inches(0.5), Inches(y_pos), Inches(0.6), Inches(1.1))
        ntf = num_box.text_frame
        ntf.text = f"#{i+1}"
        np_para = ntf.paragraphs[0]
        np_para.font.size = Pt(36)
        np_para.font.bold = True
        if not np_para.runs:
            np_para.add_run()
        np_para.runs[0].font.color.rgb = ACCENT

        # 标题 + 摘要
        content_box = slide3.shapes.add_textbox(Inches(1.2), Inches(y_pos), Inches(11.6), Inches(1.1))
        ctf = content_box.text_frame
        ctf.word_wrap = True
        title_p = ctf.paragraphs[0]
        title_p.text = t["title"]
        title_p.font.size = Pt(18)
        title_p.font.bold = True
        if not title_p.runs:
            title_p.add_run()
        title_p.runs[0].font.color.rgb = PRIMARY

        summary_p = ctf.add_paragraph()
        summary_p.text = f"[{platform_name_zh[t['platform']]} · 互动量 {t['engagement']:,}] {t['summary']}"
        summary_p.font.size = Pt(14)
        if not summary_p.runs:
            summary_p.add_run()
        summary_p.runs[0].font.color.rgb = SECONDARY

        y_pos += 1.3

    # Slide 4 — 选题优先级矩阵（4 个候选）
    slide4 = prs.slides.add_slide(blank_layout)
    title4 = slide4.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12), Inches(1))
    title4.text_frame.text = "选题优先级建议"
    p4 = title4.text_frame.paragraphs[0]
    p4.font.size = Pt(28)
    p4.font.bold = True
    if not p4.runs:
        p4.add_run()
    p4.runs[0].font.color.rgb = PRIMARY

    body4 = slide4.shapes.add_textbox(Inches(0.5), Inches(1.7), Inches(12), Inches(5))
    btf = body4.text_frame
    btf.word_wrap = True
    lines = [
        ("🔥 必做（互动量 > 50k）", "01 + 04", PRIMARY, 20),
        ("📌 高优（互动量 5k-50k）", "02 + 03", PptxRGBColor(0xF5, 0x8C, 0x00), 16),
        ("⚪ 备选（互动量 < 5k）", "（本期不做）", SECONDARY, 14),
        ("", "", PRIMARY, 8),
        ("🎯 推荐排期：", "本周先做 01（周一）+ 03（周三）+ 04（周五）", PRIMARY, 16),
        ("📊 数据回看：", "7 日后用 a-stock-data-bridge 拉指数表现，回看互动 → 实际转化率", PRIMARY, 14),
        ("🛡 风险提示：", "微博/小红书话题热度衰减快，建议选题确认 24h 内发布", ACCENT, 14),
    ]
    for label, value, color, size in lines:
        para = btf.add_paragraph() if btf.paragraphs[0].text else btf.paragraphs[0]
        para.text = f"{label}    {value}"
        para.font.size = Pt(size)
        if not para.runs:
            para.add_run()
        para.runs[0].font.color.rgb = color

    # Slide 5 — 下周行动建议
    slide5 = prs.slides.add_slide(blank_layout)
    title5 = slide5.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12), Inches(1))
    title5.text_frame.text = "下周行动建议"
    p5 = title5.text_frame.paragraphs[0]
    p5.font.size = Pt(28)
    p5.font.bold = True
    if not p5.runs:
        p5.add_run()
    p5.runs[0].font.color.rgb = PRIMARY

    body5 = slide5.shapes.add_textbox(Inches(0.5), Inches(1.7), Inches(12), Inches(5))
    btf5 = body5.text_frame
    btf5.word_wrap = True
    actions = [
        "1. 立即行动：本周末前确认 Top 4 选题的 3 个排期（周一/三/五）",
        "2. 内容生产：每个选题分配 28-04 内容策划师 + 28-01 文案 + 35-05 视频导演",
        "3. 数据回流：发布 7 日后用 a-stock-data-bridge 拉热榜，对比本期 vs 历史",
        "4. 多平台分发：agent-reach 联动 content-publisher，自动适配 4 平台格式",
        "5. 月度复盘：月底用 hv-analysis + 28-10 财经底座 出本月 KOL 转化报告",
    ]
    for i, action in enumerate(actions):
        para = btf5.paragraphs[0] if i == 0 else btf5.add_paragraph()
        para.text = action
        para.font.size = Pt(16)
        if not para.runs:
            para.add_run()
        para.runs[0].font.color.rgb = SECONDARY if i > 0 else PRIMARY

    output_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(output_path)

    return {
        "query": query,
        "path": str(output_path),
        "platforms": [r.platform for r in results],
        "posts_total": sum(len(r.posts) for r in results),
        "engagement_total": sum(r.total_engagement for r in results),
        "top_topics": len(top_topics),
        "slides": len(prs.slides),
        "size_bytes": output_path.stat().st_size,
    }


def date():
    """Compatibility alias for _date"""
    return _date


if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "output" / f"KOL选题调研-2026-08-26.pptx"
    r = build_kol_topic_deck("AI 工具 编程技巧 效率提升", out)

    print("=" * 70)
    print("Stage 47.3 · Slide + agent-reach 联动（KOL 选题 .pptx 自动生成）")
    print("=" * 70)
    print(f"  Query:      {r['query']}")
    print(f"  Path:       {r['path']}")
    print(f"  Platforms:  {r['platforms']}")
    print(f"  Posts:      {r['posts_total']}")
    print(f"  Engagement: {r['engagement_total']:,}")
    print(f"  Top topics: {r['top_topics']}")
    print(f"  Slides:     {r['slides']}")
    print(f"  Size:       {r['size_bytes']} B")
    print("=" * 70)
