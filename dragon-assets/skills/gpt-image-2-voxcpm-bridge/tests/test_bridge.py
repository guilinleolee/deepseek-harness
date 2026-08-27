"""
gpt-image-2-voxcpm-bridge 单元测试 · V1.0
10 个测试用例
"""

import sys
import json
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import bridge
from bridge import (
    ADAPTERS, SCENARIOS,
    list_scenarios, get_scenario, consistency_score,
    build_adapter, build_manifest,
)


def test_1_five_adapters():
    """测试 1: 5 个 adapter"""
    assert len(ADAPTERS) == 5
    assert "tts_voxcpm" in ADAPTERS
    assert "cover_mondo" in ADAPTERS
    assert "cover_baoyu" in ADAPTERS
    assert "illustrations" in ADAPTERS
    assert "storyboard" in ADAPTERS
    print(f"✅ Test 1 PASS: 5 个 adapter（+tts_voxcpm）")


def test_2_eleven_scenarios():
    """测试 2: 11 类工作流场景"""
    scenarios = list_scenarios()
    assert len(scenarios) == 11
    assert "博主视频号自动化" in scenarios
    assert "多语言出海广告" in scenarios
    assert "有声书" in scenarios
    print(f"✅ Test 2 PASS: 11 类工作流场景")


def test_3_scenario_adapters():
    """测试 3: 场景 adapter 配置"""
    sc = get_scenario("博主视频号自动化")
    assert "storyboard" in sc["adapters"]
    assert "tts_voxcpm" in sc["adapters"]
    assert sc["audio_mode"] == "hifi_clone"

    sc2 = get_scenario("电商详情页")
    assert "illustrations" in sc2["adapters"]
    assert "tts_voxcpm" not in sc2["adapters"]
    print(f"✅ Test 3 PASS: 场景 adapter 配置")


def test_4_consistency_score():
    """测试 4: 协同打分算法"""
    # 完全匹配
    s1 = consistency_score("平静", "柔和", "平静", "中", "中", True)
    assert s1 >= 0.85

    # 部分匹配
    s2 = consistency_score("开心", "明快", "欢快", "快", "快", True)
    assert s2 >= 0.85

    # 不匹配（语言不一致）
    s3 = consistency_score("严肃", "暗调", "严肃", "慢", "快", False)
    assert s3 < 0.85
    print(f"✅ Test 4 PASS: 协同打分（4 维度）")


def test_5_adapter_schema():
    """测试 5: adapter schema"""
    for adapter_name in ADAPTERS:
        ad = build_adapter(adapter_name=adapter_name, script="test", task_id="t1")
        assert "adapter" in ad
        assert "downstream_skill" in ad
        assert "filename" in ad
    print(f"✅ Test 5 PASS: 5 adapter schema 完整")


def test_6_build_manifest():
    """测试 6: 构建 manifest"""
    manifest = build_manifest(
        scenario="抖音短视频",
        script="今天我们来聊 AI",
        visual_template="storyboard-cinematic",
        audio_mode="tts",
        voice_desc="(年轻女性,活泼)",
        reference_wav=None,
    )
    assert manifest["scenario"] == "抖音短视频"
    assert "adapters" in manifest
    assert len(manifest["adapters"]) >= 2
    assert "consistency_score" in manifest
    print(f"✅ Test 6 PASS: manifest 构建")


def test_7_ethics_check():
    """测试 7: 伦理检查"""
    manifest = build_manifest(
        scenario="博主视频号自动化",
        script="...",
        visual_template=None,
        audio_mode="hifi_clone",
        voice_desc=None,
        reference_wav=None,
        consent_file=None,  # 缺同意书
    )
    assert manifest["ethics"]["passed"] is False
    assert any(i["type"] == "missing_consent" for i in manifest["ethics"]["issues"])
    print(f"✅ Test 7 PASS: 伦理护栏（克隆需同意书）")


def test_8_unknown_scenario():
    """测试 8: 未知场景"""
    manifest = build_manifest(
        scenario="不存在的场景",
        script="...",
        visual_template=None,
        audio_mode=None,
        voice_desc=None,
        reference_wav=None,
    )
    assert "error" in manifest
    assert "available" in manifest
    assert len(manifest["available"]) == 11
    print(f"✅ Test 8 PASS: 未知场景错误处理")


def test_9_cli_list_scenarios():
    """测试 9: CLI 列出场景"""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "bridge.py"), "--list-scenarios"],
        capture_output=True, text=True, encoding="utf-8"
    )
    assert "11 类工作流场景" in result.stdout
    assert "博主视频号自动化" in result.stdout
    assert "多语言出海广告" in result.stdout
    print(f"✅ Test 9 PASS: CLI 列出场景")


def test_10_cli_full_workflow():
    """测试 10: CLI 完整工作流（dry-run）"""
    with open("/tmp/test_consent.txt", "w", encoding="utf-8") as f:
        f.write("I consent to use this audio.")
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "bridge.py"),
         "--scenario", "抖音短视频",
         "--script", "今天我们来聊 AI",
         "--audio-mode", "tts",
         "--consent-file", "/tmp/test_consent.txt",
         "--dry-run"],
        capture_output=True, text=True, encoding="utf-8"
    )
    assert "Manifest 生成完成" in result.stdout or "Dry-run" in result.stdout
    Path("/tmp/test_consent.txt").unlink()
    print(f"✅ Test 10 PASS: CLI 完整工作流")


def test_11_cli_missing_scenario():
    """测试 11: CLI 缺场景参数"""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "bridge.py"), "--script", "test"],
        capture_output=True, text=True, encoding="utf-8"
    )
    assert "scenario" in result.stdout.lower() or result.returncode == 1
    print(f"✅ Test 11 PASS: CLI 缺场景拦截")


def test_12_iso_with_gpt_image_2_bridge():
    """测试 12: 与 gpt-image-2-bridge adapter schema 同构"""
    # 4 个共有 adapter
    shared = ["cover_mondo", "cover_baoyu", "illustrations", "storyboard"]
    for adapter in shared:
        ad = build_adapter(adapter_name=adapter, script="test", task_id="t1")
        assert "adapter" in ad
        assert "downstream_skill" in ad
        assert "filename" in ad
    print(f"✅ Test 12 PASS: 与 gpt-image-2-bridge schema 同构")


def run_all():
    """运行全部测试"""
    tests = [
        test_1_five_adapters,
        test_2_eleven_scenarios,
        test_3_scenario_adapters,
        test_4_consistency_score,
        test_5_adapter_schema,
        test_6_build_manifest,
        test_7_ethics_check,
        test_8_unknown_scenario,
        test_9_cli_list_scenarios,
        test_10_cli_full_workflow,
        test_11_cli_missing_scenario,
        test_12_iso_with_gpt_image_2_bridge,
    ]

    print(f"\n🧪 运行 gpt-image-2-voxcpm-bridge 测试 ({len(tests)} 个用例)")
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