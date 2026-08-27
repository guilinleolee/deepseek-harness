"""
voxcpm-multi-speaker 单元测试 · V1.0
10 个测试用例
"""

import sys
import json
import subprocess
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import multi_speaker
from multi_speaker import (
    ROLE_DEFINITIONS,
    PRESET_TEMPLATES,
    DIALOGUE_SCENARIOS,
    list_scenarios,
    get_scenario,
    list_presets,
    validate_speaker_definition,
    parse_dialogue_script,
    parse_simple_yaml,
    validate_script,
    build_utterance_plan,
)


def test_1_four_role_definitions():
    """测试 1: 4 种角色定义方式"""
    assert len(ROLE_DEFINITIONS) == 4
    assert "voice_design" in ROLE_DEFINITIONS
    assert "reference_audio" in ROLE_DEFINITIONS
    assert "fingerprint" in ROLE_DEFINITIONS
    assert "preset_template" in ROLE_DEFINITIONS
    print(f"✅ Test 1 PASS: 4 种角色定义")


def test_2_ten_presets():
    """测试 2: 10 套预设音色模板"""
    presets = list_presets()
    assert len(presets) == 10
    assert "治愈系" in presets
    assert "知识区" in presets
    assert "带货主播" in presets
    print(f"✅ Test 2 PASS: 10 套预设音色模板")


def test_3_six_scenarios():
    """测试 3: 6 套预设对话场景"""
    scs = list_scenarios()
    assert len(scs) == 6
    assert "访谈节目" in scs
    assert "播客3人" in scs
    assert "有声书·旁白+主角" in scs
    assert "有声书·多人" in scs
    assert "广播剧" in scs
    assert "辩论节目" in scs
    print(f"✅ Test 3 PASS: 6 套预设对话场景")


def test_4_scenario_lookup():
    """测试 4: 场景查表"""
    sc = get_scenario("访谈节目")
    assert sc is not None
    assert "host" in sc["speakers"]
    assert "guest" in sc["speakers"]
    assert sc["roles"]["host"]["preset"] == "治愈系"
    assert get_scenario("不存在") is None
    print(f"✅ Test 4 PASS: 场景查表")


def test_5_validate_role_def():
    """测试 5: 角色定义校验"""
    # voice_design
    assert validate_speaker_definition({"definition": "voice_design", "voice_description": "(中年女性,温柔)"}) is True
    # reference_audio
    assert validate_speaker_definition({"definition": "reference_audio", "reference_wav_path": "/tmp/a.wav"}) is True
    # fingerprint
    assert validate_speaker_definition({"definition": "fingerprint", "fingerprint_id": "fp1", "consent_file": "/tmp/c.txt"}) is True
    # preset_template
    assert validate_speaker_definition({"definition": "preset_template", "preset": "治愈系"}) is True
    # 缺字段
    assert validate_speaker_definition({"definition": "voice_design"}) is False
    # 非法类型
    assert validate_speaker_definition({"definition": "unknown"}) is False
    print(f"✅ Test 5 PASS: 4 种角色定义校验")


def test_6_json_parse():
    """测试 6: JSON 脚本解析"""
    script_data = {
        "title": "测试对话",
        "language": "zh",
        "speakers": {
            "host": {"definition": "voice_design", "voice_description": "(中年女性,温柔)"},
            "guest": {"definition": "preset_template", "preset": "知识区"},
        },
        "dialogue": [
            {"speaker": "host", "text": "欢迎收听本期节目", "emotion": "开心"},
            {"speaker": "guest", "text": "谢谢邀请", "emotion": "平静", "pause_ms": 500},
        ],
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(script_data, f, ensure_ascii=False)
        json_path = f.name
    try:
        script = parse_dialogue_script(json_path)
        assert script["title"] == "测试对话"
        assert len(script["speakers"]) == 2
        assert len(script["dialogue"]) == 2
    finally:
        Path(json_path).unlink()
    print(f"✅ Test 6 PASS: JSON 解析")


def test_7_yaml_parse():
    """测试 7: YAML 脚本解析"""
    yaml_content = """\
title: 测试对话
language: zh
speakers:
  host:
    definition: voice_design
    voice_description: (中年女性,温柔)
  guest:
    definition: preset_template
    preset: 知识区
dialogue:
  - speaker: host
    text: 欢迎收听
    emotion: 开心
  - speaker: guest
    text: 谢谢邀请
    emotion: 平静
    pause_ms: 500
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
        f.write(yaml_content)
        yaml_path = f.name
    try:
        script = parse_dialogue_script(yaml_path)
        assert script["title"] == "测试对话"
        assert "host" in script["speakers"]
        assert len(script["dialogue"]) == 2
        assert script["dialogue"][1]["pause_ms"] == "500"
    finally:
        Path(yaml_path).unlink()
    print(f"✅ Test 7 PASS: YAML 解析")


def test_8_validate_script_ethics():
    """测试 8: 脚本校验 - 伦理 + 完整性"""
    # 合法脚本
    good_script = {
        "title": "合法对话",
        "language": "zh",
        "speakers": {
            "host": {"definition": "voice_design", "voice_description": "(中年女性,温柔)"},
        },
        "dialogue": [
            {"speaker": "host", "text": "你好", "emotion": "平静"},
        ],
    }
    result = validate_script(good_script)
    assert result["passed"] is True

    # 缺同意书
    bad_script = {
        "speakers": {
            "speaker1": {"definition": "fingerprint", "fingerprint_id": "fp1", "consent_file": "/nonexistent_consent.txt"},
        },
        "dialogue": [
            {"speaker": "speaker1", "text": "test"},
        ],
    }
    result = validate_script(bad_script)
    assert result["passed"] is False
    assert any(i["type"] == "missing_consent" for i in result["issues"])

    # 未定义角色
    bad_script2 = {
        "speakers": {
            "host": {"definition": "voice_design", "voice_description": "(女性)"},
        },
        "dialogue": [
            {"speaker": "ghost", "text": "test"},
        ],
    }
    result = validate_script(bad_script2)
    assert result["passed"] is False
    print(f"✅ Test 8 PASS: 脚本校验（伦理 + 完整性）")


def test_9_utterance_plan():
    """测试 9: utterance 计划生成"""
    script = {
        "title": "test",
        "language": "zh",
        "speakers": {
            "host": {"definition": "voice_design", "voice_description": "(中年女性)"},
            "guest": {"definition": "preset_template", "preset": "知识区"},
        },
        "dialogue": [
            {"speaker": "host", "text": "大家好欢迎收听", "emotion": "开心", "pause_ms": 300},
            {"speaker": "guest", "text": "今天我们来讨论 AI", "emotion": "理性", "pause_ms": 200},
            {"speaker": "host", "text": "请坐", "emotion": "平静"},
        ],
    }
    plan = build_utterance_plan(script)
    assert len(plan) == 3
    assert plan[0]["index"] == 0
    assert plan[0]["speaker"] == "host"
    assert plan[0]["start_seconds"] == 0.0
    assert plan[0]["pause_after_ms"] == 300
    assert plan[1]["start_seconds"] > 0
    # 总时长累加正确
    total_dur = plan[-1]["end_seconds"]
    assert total_dur > 0
    print(f"✅ Test 9 PASS: utterance 计划生成（共 {total_dur:.2f}s）")


def test_10_cli_dry_run():
    """测试 10: CLI dry-run"""
    script_data = {
        "title": "CLI 测试",
        "language": "zh",
        "speakers": {
            "host": {"definition": "voice_design", "voice_description": "(中年女性,温柔)"},
            "guest": {"definition": "preset_template", "preset": "知识区"},
        },
        "dialogue": [
            {"speaker": "host", "text": "欢迎收听", "emotion": "开心"},
            {"speaker": "guest", "text": "大家好", "emotion": "平静"},
        ],
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(script_data, f, ensure_ascii=False)
        json_path = f.name
    try:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "multi_speaker.py"),
             "--script", json_path,
             "--dry-run"],
            capture_output=True, text=True, encoding="utf-8"
        )
        assert result.returncode == 0
        assert "Dry-run 完成" in result.stdout
        assert "角色数: 2" in result.stdout
        assert "对话条数: 2" in result.stdout
    finally:
        Path(json_path).unlink()
    print(f"✅ Test 10 PASS: CLI dry-run")


def test_11_cli_list_scenarios():
    """测试 11: CLI 列出场景（额外）"""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "multi_speaker.py"), "--list-scenarios"],
        capture_output=True, text=True, encoding="utf-8"
    )
    assert "6 套预设对话场景" in result.stdout
    assert "访谈节目" in result.stdout
    assert "辩论节目" in result.stdout
    print(f"✅ Test 11 PASS: CLI 列出场景")


def test_12_cli_validation_error():
    """测试 12: CLI 校验失败拦截（额外）"""
    bad_script = {
        "title": "坏脚本",
        "speakers": {
            "ghost": {"definition": "voice_design", "voice_description": "(x)"},
        },
        "dialogue": [
            {"speaker": "ghost", "text": ""},  # 空文本
        ],
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(bad_script, f, ensure_ascii=False)
        json_path = f.name
    try:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "multi_speaker.py"),
             "--script", json_path, "--dry-run"],
            capture_output=True, text=True, encoding="utf-8"
        )
        # 应该因校验失败而 exit code 2
        assert result.returncode == 2
        assert "校验失败" in result.stdout
        assert "空" in result.stdout  # empty_text
    finally:
        Path(json_path).unlink()
    print(f"✅ Test 12 PASS: CLI 校验拦截")


def run_all():
    """运行全部测试"""
    tests = [
        test_1_four_role_definitions,
        test_2_ten_presets,
        test_3_six_scenarios,
        test_4_scenario_lookup,
        test_5_validate_role_def,
        test_6_json_parse,
        test_7_yaml_parse,
        test_8_validate_script_ethics,
        test_9_utterance_plan,
        test_10_cli_dry_run,
        test_11_cli_list_scenarios,
        test_12_cli_validation_error,
    ]

    print(f"\n🧪 运行 voxcpm-multi-speaker 测试 ({len(tests)} 个用例)")
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
            print(f"❌ {test.__name__} ERROR: {type(e).__name__}: {e}")
            failed += 1

    print("=" * 60)
    print(f"📊 结果: {passed}/{len(tests)} PASS, {failed} FAIL")
    return failed == 0


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
