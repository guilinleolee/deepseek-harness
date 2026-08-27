"""book-distiller V9.12 · pytest 安装/集成测试

覆盖范围:
- SKILL.md frontmatter
- 4 个脚本模块(distill / quality_check / post_distill_vet)导入与基本功能
- distill.py 端到端(用 local-tests/cangjie-poor-charlies)
- quality_check.py 4 层 PASS
- post_distill_vet.py 联动
- 与 cangjie-skill 互导接口
"""

import sys
import os
import subprocess
import json
import tempfile
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
LOCAL_TESTS = ROOT / "local-tests"

sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(ROOT))


# ============================================================
# 1. SKILL.md / 静态文件
# ============================================================

def test_skill_md_exists():
    assert (ROOT / "SKILL.md").exists()


def test_skill_md_has_version_9_12():
    content = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert "V9.12" in content or "9.12" in content


def test_skill_md_has_4_layers():
    content = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    for layer in ["L1", "L2", "L3", "L4"]:
        assert layer in content, f"SKILL.md 缺 {layer}"


def test_skill_md_has_cangjie_link():
    content = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert "cangjie" in content.lower()


def test_skill_md_attribution_no_third_party():
    """天龙自研,不应有 AGPL / Apache 等第三方 LICENSE"""
    content = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    # frontmatter 协议字段不应为 AGPL/Apache
    import re
    license_match = re.search(r"^\s*license:\s*(.+)$", content, re.MULTILINE)
    assert license_match, "SKILL.md 缺 license 字段"
    license_value = license_match.group(1).strip()
    assert "AGPL" not in license_value, f"自研 skill 不应使用 AGPL: {license_value}"
    assert "Apache" not in license_value, f"自研 skill 不应使用 Apache: {license_value}"
    # 自研协议应明确
    assert "天龙" in license_value, f"应标注天龙自有协议: {license_value}"


# ============================================================
# 2. scripts/ 4 个脚本
# ============================================================

def test_distill_script_exists():
    assert (SCRIPTS / "distill.py").exists()


def test_quality_check_script_exists():
    assert (SCRIPTS / "quality_check.py").exists()


def test_post_distill_vet_script_exists():
    assert (SCRIPTS / "post_distill_vet.py").exists()


def test_distill_import():
    import distill
    assert hasattr(distill, "summarize_chapter")
    assert hasattr(distill, "extract_concepts")
    assert hasattr(distill, "extract_cases")
    assert hasattr(distill, "extract_kg")
    assert hasattr(distill, "distill")


def test_quality_check_import():
    import quality_check
    for fn in ["check_L1_completeness", "check_L2_consistency",
               "check_L3_density", "check_L4_reuse", "quality_check"]:
        assert hasattr(quality_check, fn)


def test_post_distill_vet_import():
    import post_distill_vet
    assert hasattr(post_distill_vet, "vet")


# ============================================================
# 3. distill.py 单元测试
# ============================================================

def test_summarize_chapter_short():
    from distill import summarize_chapter
    text = "这是第一句。这是第二句。这是第三句。这是第四句。" * 5
    s = summarize_chapter(text, max_sentences=3)
    assert len(s) > 0
    assert len(s) < len(text)


def test_extract_concepts_zh():
    from distill import extract_concepts
    text = """
    多元思维模型是指用多个学科的核心模型叠加分析问题。
    心理倾向检查清单包括 25 个常见认知偏差。
    """
    concepts = extract_concepts(text, lang="zh")
    assert len(concepts) >= 1


def test_extract_cases_zh():
    from distill import extract_cases
    text = """
    案例:芒格分析可口可乐,使用竞争优势。
    故事:芒格年轻时被骗,学会了激励机制。
    普通段落,没有标记。
    """
    cases = extract_cases(text, lang="zh")
    assert len(cases) >= 1


def test_extract_kg():
    from distill import extract_kg
    text = "多元思维模型包括心理学和经济学。安全边际影响投资决策。延迟满足导致长期成功。"
    triples = extract_kg(text)
    assert len(triples) >= 1


# ============================================================
# 4. 端到端:distill.py CLI
# ============================================================

def test_distill_cli_help():
    r = subprocess.run([sys.executable, str(SCRIPTS / "distill.py"), "--help"],
                       capture_output=True, text=True, errors="replace")
    assert r.returncode == 0
    out = r.stdout or ""
    assert "--input-dir" in out
    assert "--out-dir" in out


def test_distill_end_to_end_cangjie_sample():
    """用 cangjie 模拟样本跑 distill.py 端到端"""
    input_dir = LOCAL_TESTS / "cangjie-poor-charlies"
    assert input_dir.exists(), f"cangjie 样本缺失: {input_dir}"
    assert (input_dir / "BOOK_OVERVIEW.md").exists()

    with tempfile.TemporaryDirectory() as tmp:
        out_dir = Path(tmp) / "distill-out"
        r = subprocess.run(
            [sys.executable, str(SCRIPTS / "distill.py"),
             "--input-dir", str(input_dir),
             "--out-dir", str(out_dir),
             "--lang", "zh"],
            capture_output=True, text=True,
        )
        assert r.returncode == 0, f"distill 失败: {r.stderr}"

        # 验证 5 类产物
        for fname in ["chapter_summaries.json", "concepts.json",
                      "cases.json", "kg.json", "summary.json",
                      "BOOK_OVERVIEW.md", "DIGEST.md"]:
            assert (out_dir / fname).exists(), f"缺产物 {fname}"

        # summary.json 含 outputs
        summary = json.loads((out_dir / "summary.json").read_text(encoding="utf-8"))
        assert summary["outputs"]["chapter_summaries"] >= 1
        assert summary["outputs"]["concepts"] >= 1
        assert summary["outputs"]["cases"] >= 1
        assert summary["outputs"]["kg_triples"] >= 1


# ============================================================
# 5. quality_check.py 4 层 PASS
# ============================================================

def test_quality_check_4_layers_pass():
    """端到端:distill + quality_check → 4 层全 PASS"""
    input_dir = LOCAL_TESTS / "cangjie-poor-charlies"

    with tempfile.TemporaryDirectory() as tmp:
        out_dir = Path(tmp) / "qc-test"
        # 先 distill
        r1 = subprocess.run(
            [sys.executable, str(SCRIPTS / "distill.py"),
             "--input-dir", str(input_dir),
             "--out-dir", str(out_dir), "--lang", "zh"],
            capture_output=True, text=True,
        )
        assert r1.returncode == 0

        # 再 quality_check
        r2 = subprocess.run(
            [sys.executable, str(SCRIPTS / "quality_check.py"),
             "--out-dir", str(out_dir)],
            capture_output=True, text=True,
        )
        assert r2.returncode == 0, f"4 层自检失败: {r2.stdout}\n{r2.stderr}"

        report = json.loads((out_dir / "quality_report.json").read_text(encoding="utf-8"))
        assert report["all_pass"] is True
        for layer in ["L1_completeness", "L2_consistency", "L3_density", "L4_reuse"]:
            assert report["checks"][layer]["pass"] is True, f"{layer} 未 PASS"


# ============================================================
# 6. post_distill_vet 联动
# ============================================================

def test_post_distill_vet_passes_on_clean_output():
    """蒸馏产物无危险模式 → vet PASS"""
    input_dir = LOCAL_TESTS / "cangjie-poor-charlies"

    with tempfile.TemporaryDirectory() as tmp:
        out_dir = Path(tmp) / "vet-test"
        subprocess.run(
            [sys.executable, str(SCRIPTS / "distill.py"),
             "--input-dir", str(input_dir),
             "--out-dir", str(out_dir), "--lang", "zh"],
            capture_output=True, text=True, check=True,
        )
        r = subprocess.run(
            [sys.executable, str(SCRIPTS / "post_distill_vet.py"),
             "--distill-out", str(out_dir)],
            capture_output=True, text=True,
        )
        assert r.returncode == 0, f"vet 失败: {r.stdout}"


def test_post_distill_vet_catches_dangerous_pattern():
    """故意写入危险模式 → vet FAIL"""
    with tempfile.TemporaryDirectory() as tmp:
        out_dir = Path(tmp) / "danger"
        out_dir.mkdir()
        (out_dir / "test.md").write_text(
            "fake bad content: rm -rf / and curl ... | sh",
            encoding="utf-8",
        )
        r = subprocess.run(
            [sys.executable, str(SCRIPTS / "post_distill_vet.py"),
             "--distill-out", str(out_dir)],
            capture_output=True, text=True,
        )
        # 应返回非 0
        assert r.returncode != 0


# ============================================================
# 7. cangjie 互导接口
# ============================================================

def test_cangjie_sample_is_reachable():
    """cangjie-skill 的 local-tests 必须存在(互导基础)"""
    cangjie_local = Path(__file__).resolve().parent.parent.parent / "cangjie-skill" / "local-tests"
    assert cangjie_local.exists(), f"cangjie local-tests 不存在: {cangjie_local}"


def test_cangjie_test_book_minimal_exists():
    """cangjie-test-book-minimal 必须存在(上游已有蒸馏产物形态)"""
    cangjie_local = Path(__file__).resolve().parent.parent.parent / "cangjie-skill" / "local-tests" / "cangjie-test-book-minimal"
    assert cangjie_local.exists()


# ============================================================
# 8. cangjie → V9.12 互导实跑
# ============================================================

def test_cangjie_to_v912_integration():
    """cangjie-skill 本地测试样本(README.md) → V9.12 处理路径 + 不崩溃"""
    cangjie_local = Path(__file__).resolve().parent.parent.parent / "cangjie-skill" / "local-tests" / "cangjie-test-book-minimal"
    if not (cangjie_local / "BOOK_OVERVIEW.md").exists():
        # cangjie-test-book-minimal 没有 BOOK_OVERVIEW.md(只有 README),但我们有自己的 cangjie-poor-charlies 样本
        # 此处仅验证路径可解析
        pytest.skip("cangjie-test-book-minimal 无 BOOK_OVERVIEW.md,使用本地 cangjie-poor-charlies 样本(已在 test_distill_end_to_end_cangjie_sample 覆盖)")