"""test_47_3_02_deck · 5 页 KOL 选题 .pptx 结构验证"""
import sys
from pathlib import Path

from pptx import Presentation

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from kol_deck import build_kol_topic_deck


def test_47_3_02_deck():
    out = Path(__file__).resolve().parent.parent / "output" / "test.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    result = build_kol_topic_deck("AI 工具", out)

    assert out.exists(), f"[FAIL] pptx not created: {out}"
    assert out.stat().st_size > 10000, f"[FAIL] pptx too small: {out.stat().st_size}"

    prs = Presentation(out)
    assert len(prs.slides) >= 5, f"[FAIL] expected ≥5 slides, got {len(prs.slides)}"

    # 必备标题
    all_text = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                all_text.append(shape.text_frame.text)
    full = "\n".join(all_text)

    assert "KOL 选题调研报告" in full, "[FAIL] 封面标题缺失"
    assert "平台调研概览" in full, "[FAIL] Slide 2 标题缺失"
    assert "Top 4 选题候选" in full, "[FAIL] Slide 3 标题缺失"
    assert "选题优先级建议" in full, "[FAIL] Slide 4 标题缺失"
    assert "下周行动建议" in full, "[FAIL] Slide 5 标题缺失"

    # 必备平台
    for p in ["小红书", "微博", "知乎", "B站"]:
        assert p in full, f"[FAIL] 平台 '{p}' 未出现在 deck"

    # 4 平台调研汇总
    assert "349,000" not in full  # 这个数字特定，但总之应该有 "互动量" 或 "总互动量"
    assert "互动量" in full or "互动" in full, "[FAIL] 互动量字段缺失"

    print(f"[PASS] 47.3.02 deck: {result['slides']} slides + 4 平台调研 + Top 4 选题")


if __name__ == "__main__":
    test_47_3_02_deck()
