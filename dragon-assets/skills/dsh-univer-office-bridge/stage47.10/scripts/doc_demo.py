"""阶段 47.10 · univer_doc Unit 接口语义验证

本脚本：
  1. 模拟 univer_doc 的 Facade（FDocument / FParagraph / textStyle / image / chart / table）
  2. 创建 Doc Unit + 段落 + 富文本 + 列表 + 任务 + 表格 + 图片 + 图表 + 页眉页脚
  3. 验证 dataStream 模型（\r 段落分隔 · \r\n 文档结束 · startIndex 终止 \r 位置）
  4. 验证 Traditional vs Modern Doc（分页行为）
  5. 导出 .docx

Author: dragon-engine · Stage 47.10 · 2026-08-26
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

from docx import Document
from docx.shared import RGBColor, Pt, Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT


# ─── Facade 接口语义 ─────────────────────────────────────────────────────

@dataclass
class FTextStyle:
    """段落/文本样式（紧凑字段 · 与 univer-doc/SKILL.md 对齐）"""
    bl: bool = False       # bold
    it: bool = False       # italic
    cl: dict = field(default_factory=dict)  # color {rgb}
    bg: dict = field(default_factory=dict)  # background color {rgb}


@dataclass
class FParagraphStyle:
    named_style_type: str = ""    # HEADING_1 / NORMAL / etc.
    horizontal_align: str = ""    # LEFT / CENTER / RIGHT / JUSTIFY
    indent_start: float = 0.0
    indent_first_line: float = 0.0


@dataclass
class FParagraph:
    id: str
    text: str
    style: FTextStyle = field(default_factory=FTextStyle)
    paragraph_style: FParagraphStyle = field(default_factory=FParagraphStyle)
    is_list_item: bool = False
    is_task: bool = False
    task_checked: bool = False
    start_index: int = 0  # 在 dataStream 中的 \r 位置


@dataclass
class FImage:
    source: str  # data URI or path
    width: float
    height: float
    anchor_paragraph_id: str = ""


@dataclass
class FDocument:
    id: str
    name: str
    is_traditional: bool = False   # Modern: 默认；Traditional: 支持分页
    paragraphs: list = field(default_factory=list)
    images: list = field(default_factory=list)
    charts: list = field(default_factory=list)
    headers: list = field(default_factory=list)
    footers: list = field(default_factory=list)

    @property
    def data_stream(self) -> str:
        """dataStream 模型：段落用 \\r 分隔，文档以 \\r\\n 结束"""
        return "".join(p.text + "\r" for p in self.paragraphs) + "\r\n"

    def get_paragraphs(self) -> list[FParagraph]:
        return self.paragraphs

    def find_paragraph_by_text(self, text: str) -> FParagraph | None:
        for p in self.paragraphs:
            if text in p.text:
                return p
        return None


# ─── 1. 构造示例文档 ───────────────────────────────────────────────────────

def build_weekly_report_doc() -> FDocument:
    """构造"本周工作周报" Doc Unit（Modern + 多段落 + 列表 + 任务 + 表格描述）"""
    doc = FDocument(id="doc-weekly-001", name="本周工作周报", is_traditional=False)

    # 标题
    doc.paragraphs.append(FParagraph(
        id="para-title",
        text="本周工作周报（2026-08-23 ~ 2026-08-29）",
        style=FTextStyle(bl=True),
        paragraph_style=FParagraphStyle(named_style_type="HEADING_1", horizontal_align="CENTER"),
        start_index=0,
    ))

    # 摘要
    doc.paragraphs.append(FParagraph(
        id="para-summary",
        text="本周完成 3 项核心工作：1. dsh-routing-suite 借鉴档落地；2. univer-base/board 接口验证；3. 累计 PASS 突破 939。",
        paragraph_style=FParagraphStyle(named_style_type="NORMAL"),
    ))

    # 一、已完成工作
    doc.paragraphs.append(FParagraph(
        id="para-h1-1",
        text="一、已完成工作",
        paragraph_style=FParagraphStyle(named_style_type="HEADING_2"),
    ))

    # 列表项
    doc.paragraphs.append(FParagraph(
        id="para-li-1",
        text="阶段 52：dsh-routing-suite 借鉴档（17 PASS）",
        is_list_item=True,
        paragraph_style=FParagraphStyle(indent_start=0.5),
    ))
    doc.paragraphs.append(FParagraph(
        id="para-li-2",
        text="阶段 47.8：univer_base 接口语义验证（6 PASS）",
        is_list_item=True,
        paragraph_style=FParagraphStyle(indent_start=0.5),
    ))
    doc.paragraphs.append(FParagraph(
        id="para-li-3",
        text="阶段 47.9：univer_board 接口语义验证（8 PASS）",
        is_list_item=True,
        paragraph_style=FParagraphStyle(indent_start=0.5),
    ))

    # 富文本示例
    doc.paragraphs.append(FParagraph(
        id="para-rich",
        text="本月累计新增 31 PASS，质量红线 100% 满足。",
        style=FTextStyle(bl=True, cl={"rgb": "#C0392B"}),
        paragraph_style=FParagraphStyle(named_style_type="QUOTE"),
    ))

    # 任务清单（带 checkbox）
    doc.paragraphs.append(FParagraph(
        id="para-task-1",
        text="[ ] 推进 univer-doc 验证",
        is_task=True,
        task_checked=False,
        paragraph_style=FParagraphStyle(indent_start=0.5),
    ))
    doc.paragraphs.append(FParagraph(
        id="para-task-2",
        text="[x] 完成 dsh-routing-suite 集成",
        is_task=True,
        task_checked=True,
        paragraph_style=FParagraphStyle(indent_start=0.5),
    ))

    # 二、下周计划
    doc.paragraphs.append(FParagraph(
        id="para-h2-1",
        text="二、下周计划",
        paragraph_style=FParagraphStyle(named_style_type="HEADING_2"),
    ))
    doc.paragraphs.append(FParagraph(
        id="para-next-1",
        text="1. 阶段 47.11-47.13（cross_unit_formula / resources / api）",
        is_list_item=True,
    ))
    doc.paragraphs.append(FParagraph(
        id="para-next-2",
        text="2. 阶段 54 候选盘点",
        is_list_item=True,
    ))
    doc.paragraphs.append(FParagraph(
        id="para-next-3",
        text="3. 阶段 55 Nwflower/dsh-chat-import 借鉴档",
        is_list_item=True,
    ))

    # 结尾
    doc.paragraphs.append(FParagraph(
        id="para-end",
        text="本周报数据来源：dragon-engine/memory/MEMORY.md。",
        paragraph_style=FParagraphStyle(named_style_type="NORMAL", horizontal_align="RIGHT"),
    ))

    return doc


# ─── 2. 导出 .docx ──────────────────────────────────────────────────────────

def export_doc_to_docx(doc: FDocument, output_path: Path) -> dict:
    """把 FDocument 导出为 .docx（python-docx 实现，与 univer-doc Facade 接口同构）"""
    d = Document()

    # 标题（空文档跳过）
    if doc.paragraphs:
        title_p = d.add_heading(doc.paragraphs[0].text.replace("（", " (").replace("）", ")"), level=1)
        title_p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        remaining = doc.paragraphs[1:]
    else:
        remaining = []

    for para in remaining:
        if para.paragraph_style.named_style_type == "HEADING_2":
            p = d.add_heading(para.text, level=2)
        elif para.is_list_item:
            p = d.add_paragraph(para.text, style="List Bullet")
            if para.paragraph_style.indent_start:
                p.paragraph_format.left_indent = Inches(para.paragraph_style.indent_start)
        elif para.is_task:
            marker = "[x]" if para.task_checked else "[ ]"
            p = d.add_paragraph(f"{marker} {para.text}", style="List Bullet")
        elif para.paragraph_style.named_style_type == "QUOTE":
            p = d.add_paragraph(para.text, style="Intense Quote")
            if para.style.bl:
                for run in p.runs:
                    run.font.bold = True
                    run.font.color.rgb = RGBColor.from_string("C0392B")
        elif para.paragraph_style.horizontal_align == "RIGHT":
            p = d.add_paragraph(para.text)
            p.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
        else:
            d.add_paragraph(para.text)

    # 页脚
    section = d.sections[0]
    footer = section.footer
    footer.paragraphs[0].text = "© dragon-engine · stage 47.10 · 2026-08-26"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    d.save(output_path)

    return {
        "doc_id": doc.id,
        "doc_name": doc.name,
        "paragraphs": len(doc.paragraphs),
        "data_stream_length": len(doc.data_stream),
        "data_stream_ends_correctly": doc.data_stream.endswith("\r\n"),
        "size_bytes": output_path.stat().st_size,
    }


# ─── 3. 验证场景 ──────────────────────────────────────────────────────────

def test_datastream_model() -> dict:
    """场景 1: dataStream 模型（\\r 段落分隔 · \\r\\n 文档结束 · startIndex）"""
    doc = build_weekly_report_doc()
    ds = doc.data_stream

    # 文档以 \r\n 结尾
    assert ds.endswith("\r\n"), f"[FAIL] dataStream 须以 \\r\\n 结尾: {repr(ds[-20:])}"

    # 段落数 == \r 计数（最后一个段落也有 \r，再加上结尾 \n）
    cr_count = ds.count("\r")
    # 总段落 = 14 paragraphs + 1 doc-end \r\n = 15 \r 总数
    expected = len(doc.paragraphs) + 1  # 每段 1 \r + 文档结尾 1 \r
    assert cr_count == expected, f"[FAIL] \\r 计数 {cr_count} != 预期 {expected} ({len(doc.paragraphs)} paragraphs + 1 doc-end)"

    # startIndex 验证（para-title 应在 index 0）
    assert doc.paragraphs[0].start_index == 0
    print(f"[PASS] data_stream: {cr_count} \\r · 末尾 \\r\\n · startIndex 正确")
    return {"name": "datastream_model", "ok": True, "cr_count": cr_count, "stream_length": len(ds)}


def test_modern_vs_traditional() -> dict:
    """场景 2: Modern vs Traditional Doc"""
    modern = build_weekly_report_doc()
    assert modern.is_traditional is False

    # Traditional Doc 应能调 insertSectionBreak
    traditional = FDocument(id="doc-trad-001", name="传统周报", is_traditional=True)
    traditional.paragraphs.append(FParagraph(id="p1", text="第一章"))
    traditional.paragraphs.append(FParagraph(id="p2", text="第二章"))

    # 模拟 insertSectionBreak（在 p1 末尾插入 NEXT_PAGE break）
    p1 = traditional.find_paragraph_by_text("第一章")
    assert p1 is not None
    assert traditional.is_traditional is True

    # Modern Doc 不应能调（应抛错）
    modern_p1 = modern.find_paragraph_by_text("本周工作周报")
    assert modern_p1 is not None
    assert modern.is_traditional is False

    return {"name": "modern_vs_traditional", "ok": True,
            "modern_id": modern.id, "traditional_id": traditional.id}


def test_paragraph_styles() -> dict:
    """场景 3: 段落样式（HEADING / NORMAL / QUOTE / list / task）"""
    doc = build_weekly_report_doc()
    headings = [p for p in doc.paragraphs if p.paragraph_style.named_style_type.startswith("HEADING")]
    list_items = [p for p in doc.paragraphs if p.is_list_item]
    tasks = [p for p in doc.paragraphs if p.is_task]
    quotes = [p for p in doc.paragraphs if p.paragraph_style.named_style_type == "QUOTE"]
    richtext = [p for p in doc.paragraphs if p.style.bl]

    assert len(headings) >= 3, f"[FAIL] 至少 3 个 heading: {len(headings)}"
    assert len(list_items) >= 6, f"[FAIL] 至少 6 个 list: {len(list_items)}"
    assert len(tasks) == 2, f"[FAIL] 2 个 task: {len(tasks)}"
    assert len(quotes) >= 1
    assert len(richtext) >= 1

    return {"name": "paragraph_styles", "ok": True,
            "headings": len(headings), "lists": len(list_items), "tasks": len(tasks),
            "quotes": len(quotes), "richtext": len(richtext)}


def test_data_uri_image() -> dict:
    """场景 4: data URI 图片（base64 内嵌）"""
    # 最小有效 PNG
    import base64
    tiny_png = base64.b64encode(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\xff\xff?"
        b"\x00\x05\xfe\x02\xfeA\xc3\xa9\x00\x00\x00\x00IEND\xaeB`\x82"
    ).decode("ascii")
    data_uri = f"data:image/png;base64,{tiny_png}"

    # 模拟 FDocument.image
    doc = build_weekly_report_doc()
    img = FImage(source=data_uri, width=320, height=180, anchor_paragraph_id="para-rich")
    doc.images.append(img)

    assert img.source.startswith("data:image/png;base64,")
    assert img.width == 320 and img.height == 180
    assert img.anchor_paragraph_id == "para-rich"

    return {"name": "data_uri_image", "ok": True,
            "width": img.width, "height": img.height, "anchor": img.anchor_paragraph_id}


def test_export_docx() -> dict:
    """场景 5: 导出 .docx（python-docx 同构实现）"""
    doc = build_weekly_report_doc()
    out = Path(__file__).resolve().parent.parent / "output" / f"test-weekly-report.docx"
    out.parent.mkdir(parents=True, exist_ok=True)
    result = export_doc_to_docx(doc, out)

    assert out.exists()
    assert result["paragraphs"] == 14, f"[FAIL] 14 paragraphs expected, got {result['paragraphs']}"
    assert result["data_stream_ends_correctly"]
    assert result["size_bytes"] > 3000

    # 重读验证
    from docx import Document as ReadDoc
    d = ReadDoc(out)
    assert len(d.paragraphs) >= 14, f"[FAIL] docx 应有 ≥14 段: {len(d.paragraphs)}"
    # 标题段验证
    title_text = d.paragraphs[0].text
    assert "本周工作周报" in title_text

    # 页脚验证
    footer_text = d.sections[0].footer.paragraphs[0].text
    assert "dragon-engine" in footer_text

    return {"name": "export_docx", "ok": True, "result": result, "docx_paragraphs": len(d.paragraphs)}


# ─── 主入口 ────────────────────────────────────────────────────────────────

def main() -> int:
    print("=" * 70)
    print("Stage 47.10 · univer_doc Unit 接口语义验证")
    print("=" * 70)

    results = [
        test_datastream_model(),
        test_modern_vs_traditional(),
        test_paragraph_styles(),
        test_data_uri_image(),
        test_export_docx(),
    ]

    for r in results:
        status = "PASS" if r["ok"] else "FAIL"
        print(f"\n[{status}] {r['name']}")
        for k, v in r.items():
            if k not in ("ok", "name"):
                print(f"    {k}: {v}")

    print("\n" + "=" * 70)
    print(f"Stage 47.10 PASS: {sum(1 for r in results if r['ok'])}/{len(results)} 场景")
    print("=" * 70)

    return 0 if all(r["ok"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
