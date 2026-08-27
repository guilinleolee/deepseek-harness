"""
voxcpm-voice-distillery 单元测试 · V1.0
8 个测试用例
"""

import sys
import json
import tempfile
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import distill
from distill import (
    FINGERPRINT_DIMENSIONS, BLOGGER_TEMPLATES,
    list_templates, get_template, match_template, build_fingerprint,
    validate_audio, validate_consent, check_blacklist, build_lora_training,
)


def test_1_six_dimensions():
    """测试 1: 6 维指纹模型"""
    assert len(FINGERPRINT_DIMENSIONS) == 6
    assert set(FINGERPRINT_DIMENSIONS) == {
        "timbre", "speed", "dialect", "emotion", "prosody", "vocabulary"
    }
    print(f"✅ Test 1 PASS: 6 维声音指纹模型")


def test_2_ten_templates():
    """测试 2: 10 套博主模板"""
    templates = list_templates()
    assert len(templates) == 10
    expected = ["治愈系", "知识区", "搞笑博主", "带货主播", "影视解说",
                "美食博主", "科技评测", "二次元", "母婴", "古风"]
    assert set(templates) == set(expected)
    print(f"✅ Test 2 PASS: 10 套博主音色模板")


def test_3_template_structure():
    """测试 3: 模板字段完整性"""
    for name, tpl in BLOGGER_TEMPLATES.items():
        assert "timbre" in tpl
        assert "speed" in tpl
        assert "dialect" in tpl
        assert "emotion" in tpl
        assert "prosody" in tpl
        assert "vocabulary" in tpl
        assert "keywords" in tpl
    print(f"✅ Test 3 PASS: 模板字段完整")


def test_4_template_match():
    """测试 4: 模板匹配算法"""
    fp = build_fingerprint(
        timbre={"label": "温柔细腻"},
        speed={"label": "慢速"},
        dialect={"label": "普通话"},
        emotion={"label": "平静/温暖"},
        prosody={"label": "平稳柔和"},
        vocabulary={"label": "温暖、陪伴、治愈"},
    )
    assert "matched_template" in fp
    assert "template_score" in fp
    # 应该匹配到 治愈系
    assert fp["matched_template"] == "治愈系"
    assert fp["template_score"] > 0.5
    print(f"✅ Test 4 PASS: 模板匹配（治愈系 → 相似度 {fp['template_score']}）")


def test_5_audio_validate():
    """测试 5: 音频格式校验"""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wav_path = f.name
    assert validate_audio(wav_path) is True
    Path(wav_path).unlink()

    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
        txt_path = f.name
    assert validate_audio(txt_path) is False
    Path(txt_path).unlink()

    assert validate_audio("/nonexistent.wav") is False
    print(f"✅ Test 5 PASS: 音频格式校验")


def test_6_consent_validate():
    """测试 6: 同意书校验"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write("I consent to use this audio for voice cloning.\n")
        consent_path = f.name
    assert validate_consent(consent_path) is True
    Path(consent_path).unlink()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write("这是一段随便的文本\n")
        bad_path = f.name
    assert validate_consent(bad_path) is False
    Path(bad_path).unlink()

    assert validate_consent("/nonexistent.txt") is False
    print(f"✅ Test 6 PASS: 同意书强制校验")


def test_7_blacklist():
    """测试 7: 黑名单拦截"""
    # 默认空名单
    result = check_blacklist("普通博主", [])
    assert result["passed"] is True

    # 自定义名单
    result2 = check_blacklist("敏感人物_张三", ["敏感人物_张三"])
    assert result2["passed"] is False
    assert any(i["severity"] == "BLOCK" for i in result2["issues"])
    print(f"✅ Test 7 PASS: 黑名单拦截")


def test_8_lora_training_package():
    """测试 8: LoRA 训练包结构"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        audio_path = str(tmp_path / "fake.wav")
        Path(audio_path).touch()

        fp = build_fingerprint(
            timbre={"label": "磁性"},
            speed={"label": "中等"},
            dialect={"label": "普通话"},
            emotion={"label": "理性"},
            prosody={"label": "稳定"},
            vocabulary={"label": "专业"},
        )

        result = build_lora_training(
            audio_path=audio_path,
            blogger_id="test_001",
            blogger_name="测试博主",
            fingerprint=fp,
            output_dir=tmp_path,
        )

        # 校验结构
        lora_dir = Path(result["lora_dir"])
        assert (lora_dir / "conf" / "voxcpm_v2" / "voxcpm_finetune_lora.yaml").exists()
        assert (lora_dir / "scripts" / "train.sh").exists()
        assert (lora_dir / "README.md").exists()
        assert (lora_dir / "data" / "train_chunks").exists()
        assert (lora_dir / "data" / "val_chunks").exists()
        assert (lora_dir / "webui").exists()

        # 校验 YAML 内容
        config = (lora_dir / "conf" / "voxcpm_v2" / "voxcpm_finetune_lora.yaml").read_text(encoding="utf-8")
        assert "openbmb/VoxCPM2" in config
        assert "test_001" in config
        assert "lora:" in config
    print(f"✅ Test 8 PASS: LoRA 训练包结构")


def test_9_cli_list_templates():
    """测试 9: CLI 列出模板"""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "distill.py"), "--list-templates"],
        capture_output=True, text=True, encoding="utf-8"
    )
    assert "10 套博主音色模板" in result.stdout
    assert "治愈系" in result.stdout
    assert "古风" in result.stdout
    print(f"✅ Test 9 PASS: CLI 列出模板")


def test_10_cli_missing_consent():
    """测试 10: CLI 缺同意书拦截"""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        audio_path = f.name

    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "distill.py"),
         "--audio", audio_path, "--blogger-name", "test"],
        capture_output=True, text=True, encoding="utf-8"
    )
    assert "同意书" in result.stdout or "consent" in result.stdout.lower() or result.returncode == 2
    Path(audio_path).unlink()
    print(f"✅ Test 10 PASS: CLI 缺同意书拦截")


def run_all():
    """运行全部测试"""
    tests = [
        test_1_six_dimensions,
        test_2_ten_templates,
        test_3_template_structure,
        test_4_template_match,
        test_5_audio_validate,
        test_6_consent_validate,
        test_7_blacklist,
        test_8_lora_training_package,
        test_9_cli_list_templates,
        test_10_cli_missing_consent,
    ]

    print(f"\n🧪 运行 voxcpm-voice-distillery 测试 ({len(tests)} 个用例)")
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