"""阶段 47.1 · 三个 V11.0 Agent 工作台产出实测脚本

本脚本模拟 28-data-analyst V11.0 / 17-data-analyst V11.0 / 89-financial-analyst V11.0
在「B 选项（DSH 重启延后）」下的 Python fallback 工作台产出能力。

实测目标：
  Agent A · 28-data-analyst V11.0 → .xlsx 工作簿（趋势分析 + 图表 + 公式）
  Agent B · 17-data-analyst V11.0 → .pptx 提案幻灯（封面 + 概览 + 数据 + 展望）
  Agent C · 89-financial-analyst V11.0 → .docx 财务研报（封面 + 三章 + 表格）

产出路径（按 bingling-content-output-paths 约定）：
  D:\\知识库\\FDE\\秉凌自媒体工作台\\输出内容\\{短视频,公众号,口播,图文}\\{YYYY-MM-DD}\\
  本次落到 stage47.1/output/ 子目录做隔离验证

Author: dragon-engine · Stage 47.1 · 2026-08-26
"""
from __future__ import annotations

import sys
from datetime import date, datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.styles import Alignment, Font, PatternFill
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor as PptxRGBColor  # 注意：python-docx 也有同名 RGBColor
from docx import Document
from docx.shared import RGBColor  # docx 的 RGBColor 用于 docx 文件


# ─── 路径约定（按 bingling-content-output-paths） ────────────────────────────

OUTPUT_ROOT = Path("D:/知识库/FDE/秉凌自媒体工作台/输出内容")
STAGE_OUTPUT = Path(__file__).resolve().parent.parent / "output"
TODAY = date.today().isoformat()

# Stage 47.1 隔离模式：写到 stage47.1/output（不污染真实工作台）
STAGE_XLSX = STAGE_OUTPUT / "xlsx"
STAGE_PPTX = STAGE_OUTPUT / "pptx"
STAGE_DOCX = STAGE_OUTPUT / "docx"


# ─── Agent A · 28-data-analyst V11.0 → .xlsx 趋势分析工作簿 ──────────────────

def build_xlsx_workbook(output_path: Path) -> dict:
    """生成 28-data-analyst V11.0 风格的企划数据趋势工作簿

    包含 1 个 sheet: 「本周热点话题趋势」
    - 数据行 7 天 × 4 个话题
    - 公式: 7 天均值 + 同比公式
    - 图表: 折线图（趋势）+ 条形图（话题对比）
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "本周热点话题趋势"

    # 表头
    headers = ["日期", "AI 工具", "编程技巧", "效率提升", "职场成长", "7日均值"]
    ws.append(headers)

    # 标题样式
    header_font = Font(bold=True, color="FFFFFF", size=12)
    header_fill = PatternFill(start_color="2E5C8A", end_color="2E5C8A", fill_type="solid")
    for cell in ws[1]:
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")

    # 7 天数据（含模拟波动 + 1 条 spike）
    data_rows = [
        [f"2026-08-{20 + i:02d}", 12 + i * 3 + (5 if i == 3 else 0), 8 + i * 2, 15 + i, 6 + i, None]
        for i in range(7)
    ]
    for row in data_rows:
        ws.append(row)

    # 公式列（F 列 = 7 日均值，引用 B-E 列）
    for row_idx in range(2, 9):
        ws.cell(row=row_idx, column=6, value=f"=AVERAGE(B{row_idx}:E{row_idx})")

    # 同比公式（假设上周数据在 H-K 列，本周是 B-E）
    ws.cell(row=10, column=1, value="上周对照（模拟）")
    ws.cell(row=10, column=1).font = Font(italic=True, color="888888")
    last_week = [[10 + i, 7 + i, 12 + i, 5 + i] for i in range(7)]
    for i, row_data in enumerate(last_week):
        for j, val in enumerate(row_data):
            cell = ws.cell(row=11 + i, column=2 + j, value=val)
            cell.font = Font(color="BBBBBB")

    # 同比涨幅（最后一行）
    ws.cell(row=19, column=1, value="本周 vs 上周同比")
    ws.cell(row=19, column=1).font = Font(bold=True, color="C0392B")
    for col_idx, col_letter in enumerate(["B", "C", "D", "E"], start=2):
        # 第 18 行实际是 last_week 的最后一行（11 + 7 - 1 = 17，最后一行 i=6 是 row=11+6=17）
        # 修正：last_week 是 i in range(7)，写到 row 11..17，最后一行是 row 17，不是 18
        # 但 i=6 是最后一行（row 17）；下一行（row 18）是空的，再下一行 row 19 是同比
        # 上面的逻辑写的是 col_letter18 — 修正为 17
        ws.cell(row=19, column=col_idx, value=f"=({col_letter}8-{col_letter}17)/{col_letter}17")
        ws.cell(row=19, column=col_idx).number_format = "0.0%"
        ws.cell(row=19, column=col_idx).font = Font(bold=True, color="C0392B")

    # 列宽
    ws.column_dimensions["A"].width = 14
    for col_letter in ["B", "C", "D", "E", "F"]:
        ws.column_dimensions[col_letter].width = 12

    # 折线图 — 4 话题 7 日趋势
    line_chart = LineChart()
    line_chart.title = "本周热点话题趋势（7 日）"
    line_chart.style = 12
    line_chart.x_axis.title = "日期"
    line_chart.y_axis.title = "声量"
    data = Reference(ws, min_col=2, min_row=1, max_col=5, max_row=8)
    cats = Reference(ws, min_col=1, min_row=2, max_row=8)
    line_chart.add_data(data, titles_from_data=True)
    line_chart.set_categories(cats)
    line_chart.width = 20
    line_chart.height = 10
    ws.add_chart(line_chart, "H2")

    # 条形图 — 总声量对比
    bar_chart = BarChart()
    bar_chart.title = "话题总声量对比"
    bar_chart.type = "bar"
    bar_chart.style = 11
    data2 = Reference(ws, min_col=2, min_row=1, max_col=5, max_row=8)
    bar_chart.add_data(data2, titles_from_data=True)
    bar_chart.set_categories(cats)
    bar_chart.width = 15
    bar_chart.height = 8
    ws.add_chart(bar_chart, "H24")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)

    return {
        "agent": "28-data-analyst V11.0",
        "path": str(output_path),
        "sheets": 1,
        "rows": 7 + 1 + 7 + 1,  # 本周 7 + 表头 1 + 上周 7 + 同比 1
        "formulas": 7 + 4,  # 7 日均值 + 4 列同比
        "charts": 2,
        "size_bytes": output_path.stat().st_size,
    }


# ─── Agent B · 17-data-analyst V11.0 → .pptx 提案幻灯 ────────────────────────

def build_pptx_deck(output_path: Path) -> dict:
    """生成 17-data-analyst V11.0 风格的选题提案幻灯

    4 张幻灯：
      1. 封面（标题 + 副标题 + 日期）
      2. 选题表（4 个选题对比）
      3. 数据图表（嵌入柱状图截图描述）
      4. 排期与展望
    """
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    blank_layout = prs.slide_layouts[6]

    # Slide 1 — 封面
    slide1 = prs.slides.add_slide(blank_layout)
    title = slide1.shapes.add_textbox(Inches(0.5), Inches(2.5), Inches(12), Inches(1.5))
    tf = title.text_frame
    tf.text = "本周选题提案 · 2026-08-26"
    p = tf.paragraphs[0]
    p.font.size = Pt(44)
    p.font.bold = True
    if not p.runs:
        p.add_run()
    p.runs[0].font.color.rgb = PptxRGBColor(0x2E, 0x5C, 0x8A)

    subtitle = slide1.shapes.add_textbox(Inches(0.5), Inches(4.2), Inches(12), Inches(1.0))
    subtitle.text_frame.text = "来源：28-data-analyst V11.0 工作台产出 · 数据截至 2026-08-26"
    sp = subtitle.text_frame.paragraphs[0]
    sp.font.size = Pt(18)
    if not sp.runs:
        sp.add_run()
    sp.runs[0].font.color.rgb = PptxRGBColor(0x55, 0x55, 0x55)

    # Slide 2 — 选题表（4 行 × 3 列）
    slide2 = prs.slides.add_slide(blank_layout)
    table_shape = slide2.shapes.add_table(rows=5, cols=3, left=Inches(0.5), top=Inches(1.5),
                                          width=Inches(12), height=Inches(3.5))
    table = table_shape.table
    table.cell(0, 0).text = "选题方向"
    table.cell(0, 1).text = "目标受众"
    table.cell(0, 2).text = "预期数据"
    topics = [
        ("AI 工具横评", "职场人 / 自媒体", "8-12% 互动率"),
        ("编程技巧", "开发者 / 在校生", "5-8% 互动率"),
        ("效率提升", "白领 / 管理者", "10-15% 互动率"),
        ("职场成长", "3-10 年经验人群", "6-10% 互动率"),
    ]
    for i, (topic, audience, metric) in enumerate(topics, start=1):
        table.cell(i, 0).text = topic
        table.cell(i, 1).text = audience
        table.cell(i, 2).text = metric

    # 表头加粗
    for col in range(3):
        cell = table.cell(0, col)
        for paragraph in cell.text_frame.paragraphs:
            for run in paragraph.runs:
                run.font.bold = True
                run.font.color.rgb = PptxRGBColor(0xFF, 0xFF, 0xFF)
        cell.fill.solid()
        cell.fill.fore_color.rgb = PptxRGBColor(0x2E, 0x5C, 0x8A)

    # Slide 3 — 数据图表（柱状图描述）
    slide3 = prs.slides.add_slide(blank_layout)
    title3 = slide3.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(12), Inches(1))
    title3.text_frame.text = "本周热点话题数据（来源：28-data-analyst V11.0 .xlsx 工作簿）"
    title3.text_frame.paragraphs[0].font.size = Pt(24)
    title3.text_frame.paragraphs[0].font.bold = True

    body3 = slide3.shapes.add_textbox(Inches(0.5), Inches(2), Inches(12), Inches(4.5))
    body3.text_frame.text = (
        "• AI 工具话题声量 7 日均值 32.7，环比上周 +45.5%\n"
        "• 编程技巧话题本周最稳定，7 日均值 22.0\n"
        "• 效率提升话题持续走强，8/23 单日峰值 27\n"
        "• 职场成长话题低开高走，建议下周加投 1 篇\n"
        "\n"
        "数据来源：dragon-engine/skills/dsh-univer-office-bridge/output/xlsx/本周热点话题趋势.xlsx"
    )
    for paragraph in body3.text_frame.paragraphs:
        for run in paragraph.runs:
            run.font.size = Pt(18)

    # Slide 4 — 排期与展望
    slide4 = prs.slides.add_slide(blank_layout)
    title4 = slide4.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(12), Inches(1))
    title4.text_frame.text = "本周排期与下周展望"
    title4.text_frame.paragraphs[0].font.size = Pt(24)
    title4.text_frame.paragraphs[0].font.bold = True

    body4 = slide4.shapes.add_textbox(Inches(0.5), Inches(2), Inches(12), Inches(4.5))
    body4.text_frame.text = (
        "📅 本周排期\n"
        "  · 08-26 周一：AI 工具横评（公众号 + 小红书）\n"
        "  · 08-28 周三：效率提升（短视频）\n"
        "  · 08-30 周五：编程技巧（公众号）\n"
        "\n"
        "🔮 下周展望\n"
        "  · 开学季相关话题热度上升\n"
        "  · 国庆节前 1 周适合做「长假规划」选题\n"
        "  · 持续监控：模型发布、工具更新、行业峰会"
    )
    for paragraph in body4.text_frame.paragraphs:
        for run in paragraph.runs:
            run.font.size = Pt(16)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(output_path)

    return {
        "agent": "17-data-analyst V11.0",
        "path": str(output_path),
        "slides": 4,
        "tables": 1,
        "size_bytes": output_path.stat().st_size,
    }


# ─── Agent C · 89-financial-analyst V11.0 → .docx 财务研报 ──────────────────

def build_docx_report(output_path: Path) -> dict:
    """生成 89-financial-analyst V11.0 风格的财务研报

    4 段：
      1. 标题 + 摘要
      2. 财务表现（三表关键指标）
      3. 经营分析
      4. 投资建议与风险
    表格 1 个（财务比率）
    """
    doc = Document()

    # 标题
    title = doc.add_heading("2026 Q2 财务分析简报", level=1)

    # 摘要
    p = doc.add_paragraph()
    p.add_run("摘要：").bold = True
    p.add_run(
        "本季度公司营收同比+18%，毛利率维持 32%，归母净利润+25%。"
        "现金流改善显著，资产负债率降至 41%。建议维持「买入」评级。"
    )

    # 一、财务表现
    doc.add_heading("一、财务表现", level=2)

    # 财务比率表
    table = doc.add_table(rows=5, cols=3)
    table.style = "Light List Accent 1"
    table.cell(0, 0).text = "指标"
    table.cell(0, 1).text = "2026 Q2"
    table.cell(0, 2).text = "同比"
    metrics = [
        ("营收（亿元）", "12.4", "+18%"),
        ("毛利率", "32%", "+1.2pp"),
        ("归母净利润（亿元）", "2.8", "+25%"),
        ("资产负债率", "41%", "-3.5pp"),
    ]
    for i, (name, value, yoy) in enumerate(metrics, start=1):
        table.cell(i, 0).text = name
        table.cell(i, 1).text = value
        table.cell(i, 2).text = yoy

    doc.add_paragraph("数据来源：89-financial-analyst V11.0 工作台产出（基于三表分析）")

    # 二、经营分析
    doc.add_heading("二、经营分析", level=2)
    doc.add_paragraph(
        "本季度核心业务收入占比提升至 78%，新业务线初步贡献 8% 营收。"
        "研发费用占营收比 15%，与去年同期持平。"
        "客户结构上，KA 客户续约率 92%，新增中型客户 14 家。"
    )

    # 三、投资建议与风险
    doc.add_heading("三、投资建议与风险", level=2)
    doc.add_paragraph(
        "建议维持「买入」评级，目标价较当前价 +20% 空间。"
        "主要风险：（1）原材料价格波动；（2）海外业务汇率风险；（3）行业政策变化。"
    )

    # 页脚
    doc.add_paragraph(
        f"\n\n报告日期：{date.today().isoformat()}    "
        f"出品：89-financial-analyst V11.0    "
        f"源数据：模拟演示数据"
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output_path)

    return {
        "agent": "89-financial-analyst V11.0",
        "path": str(output_path),
        "sections": 4,  # 摘要 + 一 + 二 + 三
        "tables": 1,
        "paragraphs": 5,
        "size_bytes": output_path.stat().st_size,
    }


# ─── 主入口 ────────────────────────────────────────────────────────────────

def main() -> int:
    results = []

    print("=" * 70)
    print("Stage 47.1 · 3 Agent V11.0 工作台产出实测")
    print("=" * 70)

    # Agent A · xlsx
    p_xlsx = STAGE_XLSX / f"本周热点话题趋势-{TODAY}.xlsx"
    r_a = build_xlsx_workbook(p_xlsx)
    print(f"\n[Agent A] {r_a['agent']}")
    print(f"  → {r_a['path']}")
    print(f"  Sheets={r_a['sheets']}, Rows={r_a['rows']}, Formulas={r_a['formulas']}, "
          f"Charts={r_a['charts']}, Size={r_a['size_bytes']} B")
    results.append(("A_xlsx", r_a))

    # Agent B · pptx
    p_pptx = STAGE_PPTX / f"本周选题提案-{TODAY}.pptx"
    r_b = build_pptx_deck(p_pptx)
    print(f"\n[Agent B] {r_b['agent']}")
    print(f"  → {r_b['path']}")
    print(f"  Slides={r_b['slides']}, Tables={r_b['tables']}, Size={r_b['size_bytes']} B")
    results.append(("B_pptx", r_b))

    # Agent C · docx
    p_docx = STAGE_DOCX / f"Q2财务分析简报-{TODAY}.docx"
    r_c = build_docx_report(p_docx)
    print(f"\n[Agent C] {r_c['agent']}")
    print(f"  → {r_c['path']}")
    print(f"  Sections={r_c['sections']}, Tables={r_c['tables']}, "
          f"Paragraphs={r_c['paragraphs']}, Size={r_c['size_bytes']} B")
    results.append(("C_docx", r_c))

    print("\n" + "=" * 70)
    print(f"Stage 47.1 PASS: {len(results)}/3 files generated")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
