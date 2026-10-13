"""test_47_1_pptx · 17-data-analyst V11.0 .pptx 提案幻灯产出验证

验证：
  1. 文件存在 + 大小 > 5000
  2. 4 张幻灯
  3. 至少 1 个表格（选题表）
  4. 包含 "本周选题提案" 标题文本
"""
import sys
from datetime import date
from pathlib import Path

from pptx import Presentation

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from office_producers import build_pptx_deck


def test_47_1_pptx():
    out = Path(__file__).resolve().parent.parent / "output" / "pptx" / f"test-{date.today().isoformat()}.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    result = build_pptx_deck(out)

    assert out.exists(), f"[FAIL] pptx not created: {out}"
    assert out.stat().st_size > 5000, f"[FAIL] pptx too small: {out.stat().st_size}"

    prs = Presentation(out)
    assert len(prs.slides) >= 4, f"[FAIL] expected ≥4 slides, got {len(prs.slides)}"

    # 找包含"本周选题提案"的幻灯
    found_title = False
    has_table = False
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                text = shape.text_frame.text
                if "本周选题提案" in text:
                    found_title = True
            if shape.has_table:
                has_table = True

    assert found_title, "[FAIL] 标题 '本周选题提案' not found"
    assert has_table, "[FAIL] no table in slides"

    print(f"[PASS] pptx: {result}")


if __name__ == "__main__":
    test_47_1_pptx()
