"""
voxcpm-tts-integration 单元测试 · V1.0
12 个测试用例
"""

import sys
import os
import json
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import voxcpm
from voxcpm import (
    LANGUAGES, DIALECTS, MODES, BACKENDS,
    VOICE_DESIGN_DIMENSIONS, VOICE_DESIGN_TEMPLATES,
    get_language_name, get_dialect_name,
    validate_mode, check_ethics, parse_voice_design, build_input,
)
import query as voxcpm_query


def test_1_language_count():
    """测试 1: 30 种全球语言"""
    assert len(LANGUAGES) == 30, f"应有 30 语言，实际 {len(LANGUAGES)}"
    assert "zh" in LANGUAGES
    assert "en" in LANGUAGES
    assert "ja" in LANGUAGES
    print(f"✅ Test 1 PASS: 30 种全球语言")


def test_2_dialect_count():
    """测试 2: 9 种中文方言"""
    assert len(DIALECTS) == 9, f"应有 9 方言，实际 {len(DIALECTS)}"
    assert "sichuan" in DIALECTS
    assert "yue" in DIALECTS
    assert "dongbei" in DIALECTS
    print(f"✅ Test 2 PASS: 9 种中文方言")


def test_3_modes():
    """测试 3: 4 种调用模式"""
    assert len(MODES) == 4
    assert set(MODES) == {"tts", "voice_design", "controllable_clone", "hifi_clone"}
    assert validate_mode("tts") is True
    assert validate_mode("invalid") is False
    print(f"✅ Test 3 PASS: 4 种调用模式")


def test_4_backends():
    """测试 4: 3 种部署栈"""
    assert len(BACKENDS) == 3
    assert "pytorch" in BACKENDS
    assert "nano_vllm" in BACKENDS
    assert "vllm_omni" in BACKENDS
    print(f"✅ Test 4 PASS: 3 种部署栈（核心）")


def test_5_voice_design_dimensions():
    """测试 5: 5 维音色设计"""
    assert len(VOICE_DESIGN_DIMENSIONS) == 5
    assert "gender" in VOICE_DESIGN_DIMENSIONS
    assert "age" in VOICE_DESIGN_DIMENSIONS
    assert "timbre" in VOICE_DESIGN_DIMENSIONS
    assert "emotion" in VOICE_DESIGN_DIMENSIONS
    assert "speed" in VOICE_DESIGN_DIMENSIONS
    print(f"✅ Test 5 PASS: 5 维音色设计")


def test_6_ethics_consent_required():
    """测试 6: 伦理护栏 - 克隆需同意书"""
    ethics = check_ethics("测试", "controllable_clone", consent_file=None)
    assert ethics["passed"] is False
    assert any(i["type"] == "missing_consent" for i in ethics["issues"])

    # 有同意书则通过
    fake_consent = Path("/tmp/fake_consent.txt")
    fake_consent.write_text("I consent", encoding="utf-8")
    ethics2 = check_ethics("测试", "controllable_clone", consent_file=str(fake_consent))
    assert ethics2["passed"] is True
    fake_consent.unlink()
    print(f"✅ Test 6 PASS: 伦理护栏 - 同意书强制")


def test_7_ethics_blocked_keywords():
    """测试 7: 伦理护栏 - 拦截敏感关键词"""
    ethics = check_ethics("这是一个诈骗语音", "tts", consent_file=None)
    assert ethics["passed"] is False
    assert any(i["type"] == "blocked_keyword" for i in ethics["issues"])
    print(f"✅ Test 7 PASS: 伦理护栏 - 拦截敏感关键词")


def test_8_parse_voice_design():
    """测试 8: 解析音色设计括号语法"""
    parsed = parse_voice_design("(年轻女性,温柔甜美)你好世界")
    assert parsed["is_design"] is True
    assert parsed["voice_desc"] == "年轻女性,温柔甜美"
    assert parsed["text"] == "你好世界"

    # 普通文本
    parsed2 = parse_voice_design("普通文本")
    assert parsed2["is_design"] is False
    assert parsed2["text"] == "普通文本"
    print(f"✅ Test 8 PASS: 音色设计括号语法解析")


def test_9_build_input_schema():
    """测试 9: 输入 schema 构建"""
    inp = build_input(
        text="你好",
        mode="tts",
        voice_desc=None,
        reference_audio=None,
        prompt_audio=None,
        prompt_text=None,
        language="zh",
        dialect="auto",
        cfg_value=2.0,
        inference_steps=10,
        output="out.wav",
    )
    assert inp["text"] == "你好"
    assert inp["mode"] == "tts"
    assert inp["language"] == "zh"
    assert inp["cfg_value"] == 2.0
    assert inp["output_path"] == "out.wav"
    print(f"✅ Test 9 PASS: 输入 schema 构建")


def test_10_query_capabilities():
    """测试 10: 能力查询"""
    caps = voxcpm_query.query_capabilities("languages")
    assert caps["category"] == "languages"
    assert caps["count"] == 30

    caps_all = voxcpm_query.query_capabilities("all")
    assert "languages" in caps_all
    assert "dialects" in caps_all
    assert "modes" in caps_all
    assert "backends" in caps_all
    print(f"✅ Test 10 PASS: 能力查询 API")


def test_11_voice_design_template_filter():
    """测试 11: 音色模板筛选"""
    templates = voxcpm_query.get_voice_design_template(emotion="温柔", gender=None)
    assert len(templates) > 0
    for t in templates:
        assert "温柔" in t

    templates2 = voxcpm_query.get_voice_design_template(emotion=None, gender="女性")
    assert len(templates2) > 0
    print(f"✅ Test 11 PASS: 音色模板筛选")


def test_12_cli_dry_run():
    """测试 12: CLI dry-run"""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "voxcpm.py"),
         "--text", "你好", "--mode", "tts", "--dry-run"],
        capture_output=True, text=True, encoding="utf-8"
    )
    assert "Dry-run" in result.stdout or "完成" in result.stdout
    print(f"✅ Test 12 PASS: CLI dry-run")


def test_13_cli_voice_design_auto_detect():
    """测试 13: CLI 自动检测 voice_design"""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "voxcpm.py"),
         "--text", "(年轻女性,温柔甜美)你好", "--dry-run", "--verbose"],
        capture_output=True, text=True, encoding="utf-8"
    )
    assert "voice_design" in result.stdout or "auto-detect" in result.stdout
    print(f"✅ Test 13 PASS: CLI 自动检测 voice_design")


def test_14_cli_clone_missing_consent():
    """测试 14: CLI 克隆模式缺同意书"""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "voxcpm.py"),
         "--text", "你好", "--mode", "controllable_clone",
         "--reference-audio", "/tmp/fake.wav"],
        capture_output=True, text=True, encoding="utf-8"
    )
    assert "伦理" in result.stdout or "同意书" in result.stdout or result.returncode == 2
    print(f"✅ Test 14 PASS: CLI 克隆缺同意书拦截")


def test_15_total_locales():
    """测试 15: 总语种数（30 + 9 = 39）"""
    matrix = voxcpm_query.get_language_matrix()
    assert matrix["total_locales"] == 39
    print(f"✅ Test 15 PASS: 39 语种方言矩阵")


def run_all():
    """运行全部测试"""
    tests = [
        test_1_language_count,
        test_2_dialect_count,
        test_3_modes,
        test_4_backends,
        test_5_voice_design_dimensions,
        test_6_ethics_consent_required,
        test_7_ethics_blocked_keywords,
        test_8_parse_voice_design,
        test_9_build_input_schema,
        test_10_query_capabilities,
        test_11_voice_design_template_filter,
        test_12_cli_dry_run,
        test_13_cli_voice_design_auto_detect,
        test_14_cli_clone_missing_consent,
        test_15_total_locales,
    ]

    print(f"\n🧪 运行 voxcpm-tts-integration 测试 ({len(tests)} 个用例)")
    print("=" * 60)

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__} FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test.__name__} ERROR: {e}")
            failed += 1

    print("=" * 60)
    print(f"📊 结果: {passed}/{len(tests)} PASS, {failed} FAIL")
    return failed == 0


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)