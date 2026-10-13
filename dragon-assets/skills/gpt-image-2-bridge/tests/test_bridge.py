"""gpt-image-2-bridge V1.0 集成测试

8 个测试场景:
  1. adapter_cover_mondo 输出 schema
  2. adapter_cover_baoyu 输出 schema
  3. adapter_illustration 输出 schema
  4. adapter_storyboard 输出 schema
  5. ROUTING_MATRIX 12 类目覆盖
  6. fetch_cases 调 query.py（mock）
  7. bridge 干跑 (--dry-run) 无 API 调用
  8. prompt 中英双语 (zh / en)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# 路径注入
BRIDGE_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = BRIDGE_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import bridge as br  # noqa: E402

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_CASE = {
    "id": "case-17",
    "category": "UI & Interfaces",
    "title": "Notion-like dashboard with AI sidebar",
    "prompt": "Modern SaaS dashboard, dark mode, AI sidebar, neumorphic cards, "
              "3-column layout, vibrant gradient accent (cyan-purple), glassmorphism. "
              "Mockup screenshot, 1440x900.",
    "image_url": "/images/case-17.jpg",
}

SAMPLE_CASES_POSTER = {
    "id": "case-156",
    "category": "Posters & Typography",
    "title": "Vintage cinema poster typography",
    "prompt": "Art deco movie poster, hand-lettered title 'MIDNIGHT', "
              "limited color palette (gold/black/red), strong vertical composition, "
              "texture overlay, classic 1920s aesthetic.",
}

SAMPLE_CASES_SCENE = {
    "id": "case-310",
    "category": "Scenes & Storytelling",
    "title": "Cyberpunk city rooftop chase",
    "prompt": "Wide establishing shot, neon-lit Tokyo, rain, protagonist on rooftop edge, "
              "hover vehicles in background, cinematic 2.39:1 aspect.",
}


# ---------------------------------------------------------------------------
# Test 1: adapter_cover_mondo schema
# ---------------------------------------------------------------------------

def test_adapter_cover_mondo():
    p = br.adapter_cover_mondo(SAMPLE_CASES_POSTER, lang="en", style="modern")
    assert p["adapter"] == "cover_mondo"
    assert p["downstream_skill"] == "qiaomu-mondo-poster-design"
    assert p["output_format"] == "PNG 1024x1024"
    assert p["source_case_id"] == "case-156"
    assert "case-156" in p["prompt"]
    assert "modern" in p["prompt"]
    assert p["filename"].endswith(".png")
    print(f"   ✅ Test 1 PASS: cover_mondo schema (filename={p['filename']})")


# ---------------------------------------------------------------------------
# Test 2: adapter_cover_baoyu schema
# ---------------------------------------------------------------------------

def test_adapter_cover_baoyu():
    p = br.adapter_cover_baoyu(SAMPLE_CASE, lang="zh")
    assert p["adapter"] == "cover_baoyu"
    assert p["downstream_skill"] == "baoyu-cover-image"
    assert p["output_format"] == "PNG 900x383 (16:9)"
    assert "公众号" in p["prompt"] or "封面" in p["prompt"]
    assert p["source_case_id"] == "case-17"
    print(f"   ✅ Test 2 PASS: cover_baoyu schema (中文 prompt)")


# ---------------------------------------------------------------------------
# Test 3: adapter_illustration schema
# ---------------------------------------------------------------------------

def test_adapter_illustration():
    p = br.adapter_illustration(SAMPLE_CASES_POSTER, lang="en",
                                  style_prefix="Style: clean editorial.")
    assert p["adapter"] == "illustrations_smart"
    assert p["downstream_skill"] == "smart-illustrator"
    assert p["output_format"] == "PNG 16:9 (1920x1080)"
    assert "case-156" in p["prompt"]
    assert p["filename"].startswith("illustrations/")
    print(f"   ✅ Test 3 PASS: illustration schema (filename={p['filename']})")


# ---------------------------------------------------------------------------
# Test 4: adapter_storyboard schema
# ---------------------------------------------------------------------------

def test_adapter_storyboard():
    cases = [SAMPLE_CASES_SCENE, SAMPLE_CASES_POSTER, SAMPLE_CASE]
    p = br.adapter_storyboard(cases, duration=30, lang="en", title="Test compilation")
    assert p["adapter"] == "storyboard_seedance"
    assert p["downstream_skill"] == "seedance2-skill"
    assert p["duration_sec"] == 30
    assert len(p["shots"]) >= 3
    assert p["shots"][0]["shot_id"] == 1
    assert p["shots"][0]["duration_sec"] >= 5
    assert all("prompt_zh" in s and "prompt_en" in s for s in p["shots"])
    print(f"   ✅ Test 4 PASS: storyboard ({len(p['shots'])} shots, {p['duration_sec']}s)")


# ---------------------------------------------------------------------------
# Test 5: ROUTING_MATRIX 12 类目覆盖
# ---------------------------------------------------------------------------

def test_routing_matrix_coverage():
    for cat in br.CATEGORIES:
        assert cat in br.ROUTING_MATRIX, f"Missing routing for {cat}"
        for adp in ("cover_mondo", "cover_baoyu", "illustrations", "storyboard"):
            assert adp in br.ROUTING_MATRIX[cat], f"{cat} missing {adp}"
            assert 0 <= br.ROUTING_MATRIX[cat][adp] <= 3
    # 验证 Posters 在 cover_mondo 拿最高分
    assert br.ROUTING_MATRIX["Posters & Typography"]["cover_mondo"] == 3
    assert br.ROUTING_MATRIX["Scenes & Storytelling"]["storyboard"] == 3
    print(f"   ✅ Test 5 PASS: ROUTING_MATRIX 覆盖 12 类目 × 4 adapter")


# ---------------------------------------------------------------------------
# Test 6: parse_template_definitions
# ---------------------------------------------------------------------------

def test_parse_template_definitions():
    defs = br.parse_template_definitions()
    if not defs:
        print("   ⚠️  Test 6 SKIP: templates.md 未找到")
        return
    # 至少应该有 ≥10 个模板
    assert len(defs) >= 10, f"仅 {len(defs)} 模板"
    # 验证 schema
    for slug, d in list(defs.items())[:3]:
        assert "title" in d and "template" in d
    print(f"   ✅ Test 6 PASS: templates.md 解析 {len(defs)} 模板")


# ---------------------------------------------------------------------------
# Test 7: bridge dry-run 主流程
# ---------------------------------------------------------------------------

def test_bridge_dry_run(tmp_dir: Path):
    """mock fetch_cases 让 bridge 走完 4 adapter 干跑。"""
    original_fetch = br.fetch_cases
    original_stats = br.fetch_category_stats

    def mock_fetch(*args, **kwargs):
        return [SAMPLE_CASE, SAMPLE_CASES_POSTER, SAMPLE_CASES_SCENE]

    def mock_stats():
        return {"UI & Interfaces": 73, "Posters & Typography": 80,
                "Scenes & Storytelling": 20}

    br.fetch_cases = mock_fetch
    br.fetch_category_stats = mock_stats
    try:
        result = br.bridge(
            category="UI & Interfaces",
            only=None,
            count=3,
            dry_run=True,
            output_dir=tmp_dir,
            lang="zh",
        )
    finally:
        br.fetch_cases = original_fetch
        br.fetch_category_stats = original_stats

    assert result["ok"] is True
    assert "cover_mondo" in result["adapters_run"]
    assert "cover_baoyu" in result["adapters_run"]
    assert any("illustrations_smart" in a for a in result["adapters_run"])
    assert "storyboard_seedance" in result["adapters_run"]
    # 验证产物文件
    assert (tmp_dir / "prompts_used.json").exists()
    assert (tmp_dir / "manifest.json").exists()
    prompts = json.loads((tmp_dir / "prompts_used.json").read_text(encoding="utf-8"))
    assert len(prompts) == 6  # 1+1+3+1
    print(f"   ✅ Test 7 PASS: bridge 干跑 ({len(prompts)} prompts, 4 adapter 全跑)")


# ---------------------------------------------------------------------------
# Test 8: 跨语言 prompt
# ---------------------------------------------------------------------------

def test_bilingual_prompts():
    p_zh = br.adapter_cover_mondo(SAMPLE_CASES_POSTER, lang="zh", style="minimal")
    p_en = br.adapter_cover_mondo(SAMPLE_CASES_POSTER, lang="en", style="minimal")
    assert "一张" in p_zh["prompt"]
    assert "A" in p_en["prompt"] and "poster" in p_en["prompt"]
    # 两个 prompt 不应该完全相同
    assert p_zh["prompt"] != p_en["prompt"]
    print(f"   ✅ Test 8 PASS: 中英 prompt 区分 (zh_len={len(p_zh['prompt'])}, en_len={len(p_en['prompt'])})")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def main():
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        tests = [
            test_adapter_cover_mondo,
            test_adapter_cover_baoyu,
            test_adapter_illustration,
            test_adapter_storyboard,
            test_routing_matrix_coverage,
            test_parse_template_definitions,
            lambda: test_bridge_dry_run(tmp_dir),
            test_bilingual_prompts,
        ]
        passed = 0
        failed = 0
        for t in tests:
            try:
                t()
                passed += 1
            except Exception as e:
                failed += 1
                print(f"   ❌ {t.__name__} FAIL: {e}")
        print(f"\n📊 Result: {passed} PASS / {failed} FAIL / {len(tests)} total")
        return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())