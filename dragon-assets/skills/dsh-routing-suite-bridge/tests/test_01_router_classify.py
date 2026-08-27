"""test_01_router_classify · 4-mode 决策 + 模型适配"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from router import (
    classify, adapt, RouteResult, is_valid_mode,
    MODE_SPEC, MODE_REACT, MODE_MIXED, MODE_WEAK,
    VALID_MODES,
)


def test_01_router_classify():
    # spec 触发
    r = classify("帮我规划下周内容矩阵")
    assert r.mode == MODE_SPEC, f"[FAIL] expected spec, got {r.mode}"
    assert r.confidence > 0.7
    assert "review" in r.persona_hints, f"[FAIL] persona_hints missing 3 锚: {r.persona_hints}"
    print(f"[PASS] classify '规划' → spec (confidence={r.confidence}, hints={r.persona_hints})")

    # react 触发
    r = classify("写一个 Python 函数")
    assert r.mode == MODE_REACT
    print(f"[PASS] classify '写一个 Python 函数' → react")

    # weak 触发
    r = classify("随便看看")
    assert r.mode == MODE_WEAK
    print(f"[PASS] classify '随便看看' → weak")

    # 默认（无关键词）→ react
    r = classify("你好")
    assert r.mode == MODE_REACT
    assert r.confidence == 0.5
    print(f"[PASS] classify '你好' (no keyword) → react default")

    # 空字符串 → weak
    r = classify("")
    assert r.mode == MODE_WEAK
    assert r.confidence == 1.0
    print(f"[PASS] classify '' (empty) → weak")

    # Pro 模型 → 强制 spec
    r = adapt("pro", "随便看看")
    assert r.mode == MODE_SPEC, f"[FAIL] Pro 应强制 spec, got {r.mode}"
    assert r.model_hint == "pro"
    assert "spec_sentence" in r.persona_hints
    print(f"[PASS] adapt('pro', '随便看看') → spec (forced by Pro)")

    # Flash 模型 → neutral
    r = adapt("flash", "帮我规划下季度")
    assert r.mode in (MODE_WEAK, MODE_REACT), f"[FAIL] Flash 应弱化, got {r.mode}"
    assert r.model_hint == "flash"
    assert "neutral" in r.persona_hints
    print(f"[PASS] adapt('flash', '帮我规划下季度') → {r.mode} (Flash neutral)")

    # Sonnet 模型
    r = adapt("sonnet", "分析 2026 AI 趋势")
    assert r.mode == MODE_SPEC
    assert r.model_hint == "pro"
    print(f"[PASS] adapt('sonnet', '分析...') → spec")

    # 4 模式都合法
    assert VALID_MODES == {MODE_SPEC, MODE_REACT, MODE_MIXED, MODE_WEAK}
    for m in VALID_MODES:
        assert is_valid_mode(m)
    assert not is_valid_mode("unknown_mode")
    print(f"[PASS] 4 modes 合法验证: {VALID_MODES}")


if __name__ == "__main__":
    test_01_router_classify()
