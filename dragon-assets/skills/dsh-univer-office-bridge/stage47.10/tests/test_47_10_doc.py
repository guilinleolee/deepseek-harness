"""test_47_10_doc · 5 个 univer_doc 场景"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from doc_demo import (
    test_datastream_model,
    test_modern_vs_traditional,
    test_paragraph_styles,
    test_data_uri_image,
    test_export_docx,
    build_weekly_report_doc,
    FDocument, FParagraph, FTextStyle, FParagraphStyle,
)


def test_47_10_doc():
    # 场景 1: dataStream
    r1 = test_datastream_model()
    assert r1["ok"]
    # 14 paragraphs + 1 doc-end \r\n = 15 \r 总数
    assert r1["cr_count"] == 15, f"[FAIL] \\r 计数 {r1['cr_count']} != 15"
    print(f"[PASS] datastream: {r1['cr_count']} \\r (14 paragraphs + 1 doc-end)")

    # 场景 2: modern vs traditional
    r2 = test_modern_vs_traditional()
    assert r2["ok"]
    print(f"[PASS] modern vs traditional: Modern/Traditional 区别正确")

    # 场景 3: 段落样式
    r3 = test_paragraph_styles()
    assert r3["ok"]
    assert r3["headings"] >= 3
    assert r3["lists"] >= 6
    assert r3["tasks"] == 2
    assert r3["richtext"] >= 1
    print(f"[PASS] paragraph_styles: {r3['headings']} headings + {r3['lists']} lists + {r3['tasks']} tasks")

    # 场景 4: data URI 图片
    r4 = test_data_uri_image()
    assert r4["ok"]
    assert r4["width"] == 320
    print(f"[PASS] data_uri_image: {r4['width']}x{r4['height']} PNG data URI")

    # 场景 5: 导出 docx
    r5 = test_export_docx()
    assert r5["ok"]
    assert r5["docx_paragraphs"] >= 14
    print(f"[PASS] export_docx: {r5['result']['size_bytes']} B · {r5['docx_paragraphs']} 段落")

    # 边界：空 doc 也应能导出
    print("\n--- 边界 case ---")
    empty_doc = FDocument(id="doc-empty", name="空文档")
    out = Path(__file__).resolve().parent.parent / "output" / "test-empty.docx"
    from doc_demo import export_doc_to_docx
    r_empty = export_doc_to_docx(empty_doc, out)
    assert out.exists()
    assert r_empty["paragraphs"] == 0
    print(f"[PASS] empty doc export: {r_empty['size_bytes']} B")


# 独立 test
test_datastream_model.__test__ = True
test_modern_vs_traditional.__test__ = True
test_paragraph_styles.__test__ = True
test_data_uri_image.__test__ = True
test_export_docx.__test__ = True
