"""
voxcpm-streaming 单元测试 · V1.0
10 个测试用例
"""

import sys
import json
import asyncio
import subprocess
import tempfile
import wave
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import streaming
from streaming import (
    StreamConfig,
    StreamSession,
    SCENE_PRESETS,
    EMOTIONS,
    BLOCKED_KEYWORDS,
    split_sentences,
    validate_session_ethics,
    get_scene_preset,
    synthesize_sentence_streaming,
    StreamingWAVEncoder,
    stream_text_to_audio,
    stream_to_wav_file,
    make_handshake_msg,
    make_end_msg,
    DEFAULT_SAMPLE_RATE,
)


def test_1_scene_presets():
    """测试 1: 5 类场景预设"""
    assert len(SCENE_PRESETS) == 5
    assert "live_stream" in SCENE_PRESETS
    assert "voice_assistant" in SCENE_PRESETS
    assert "audiobook" in SCENE_PRESETS
    assert "customer_service" in SCENE_PRESETS
    assert "meeting_notes" in SCENE_PRESETS
    print(f"✅ Test 1 PASS: 5 类场景预设")


def test_2_stream_config():
    """测试 2: 6 维流控配置"""
    cfg = StreamConfig()
    assert cfg.speed == 1.0
    assert cfg.pitch == 0
    assert cfg.emotion == "平静"
    assert cfg.pause_ms == 200
    assert cfg.overlap == 0.0
    assert cfg.fade_ms == 50
    print(f"✅ Test 2 PASS: 6 维流控配置")


def test_3_split_sentences():
    """测试 3: 句子分割"""
    s1 = "你好世界。今天天气不错。"
    assert len(split_sentences(s1)) == 2
    s2 = "Hello world. How are you?"
    assert len(split_sentences(s2)) == 2
    s3 = "单句无标点"
    assert len(split_sentences(s3)) == 1
    print(f"✅ Test 3 PASS: 句子分割")


def test_4_ethics_validation():
    """测试 4: 伦理校验"""
    # 合法：voice_design 不需要 consent
    s1 = StreamSession(session_id="t1", mode="voice_design", voice_desc="(年轻女性,活泼)")
    eth1 = validate_session_ethics(s1)
    assert eth1["passed"] is True

    # 非法：hifi_clone 无 consent
    s2 = StreamSession(session_id="t2", mode="hifi_clone", reference_wav="/tmp/x.wav")
    eth2 = validate_session_ethics(s2)
    assert eth2["passed"] is False
    assert any(i["type"] == "missing_consent" for i in eth2["issues"])

    # 非法：黑名单
    s3 = StreamSession(session_id="t3", mode="voice_design", voice_desc="(Trump 特朗普,男声)")
    eth3 = validate_session_ethics(s3)
    assert eth3["passed"] is False
    assert any(i["type"] == "blacklist" for i in eth3["issues"])

    # 非法：speed 越界
    s4 = StreamSession(session_id="t4", config=StreamConfig(speed=3.0))
    eth4 = validate_session_ethics(s4)
    assert eth4["passed"] is False
    print(f"✅ Test 4 PASS: 伦理校验（4 类场景）")


def test_5_scene_preset_lookup():
    """测试 5: 场景查表"""
    cfg = get_scene_preset("live_stream")
    assert cfg.speed == 1.3
    assert cfg.emotion == "激动"
    try:
        get_scene_preset("nonexistent")
        assert False, "应抛异常"
    except ValueError:
        pass
    print(f"✅ Test 5 PASS: 场景查表")


def test_6_async_streaming():
    """测试 6: 异步流式合成"""
    async def run():
        session = StreamSession(
            session_id="async_test",
            mode="voice_design",
            voice_desc="(年轻女性,活泼)",
            sample_rate=24000,
        )
        chunks = []
        async for chunk in stream_text_to_audio("你好世界。今天天气不错。", session):
            chunks.append(chunk)
        return chunks, session

    chunks, session = asyncio.run(run())
    assert len(chunks) > 0
    assert session.chunks_sent > 0
    assert session.first_byte_at is not None
    assert session.first_byte_at < 0.5  # < 500ms
    print(f"✅ Test 6 PASS: 异步流式合成（{len(chunks)} chunks, 首字节 {session.first_byte_at*1000:.1f}ms）")


def test_7_wav_encoder():
    """测试 7: WAV 编码器"""
    encoder = StreamingWAVEncoder(sample_rate=24000)
    # 模拟 24000 samples 音频（1 秒）
    import numpy as np
    samples = (np.zeros(24000, dtype=np.int16)).tobytes()
    chunks = [samples[:8000], samples[8000:16000], samples[16000:]]
    for c in chunks:
        encoder.encode_chunk(c)
    # final header
    final = encoder.finalize()
    # 验证：total = 36 + 数据字节数（int16 24000 样本 = 48000 字节）
    import struct
    total_size = struct.unpack('<I', final[4:8])[0]
    assert total_size == 36 + 24000 * 2  # 2 bytes per int16 sample
    print(f"✅ Test 7 PASS: WAV 编码器（total_size={total_size}）")


def test_8_protocol_messages():
    """测试 8: 协议消息"""
    session = StreamSession(session_id="proto_test", mode="voice_design", voice_desc="(女性)")
    handshake = make_handshake_msg(session)
    assert "handshake" in handshake
    assert "proto_test" in handshake

    end = make_end_msg(session)
    assert "end" in end
    print(f"✅ Test 8 PASS: 协议消息")


def test_9_save_to_wav():
    """测试 9: 保存流式结果为 WAV"""
    async def run():
        session = StreamSession(
            session_id="save_test",
            mode="voice_design",
            voice_desc="(年轻女性,活泼)",
            sample_rate=16000,  # 用低采样率加快测试
        )
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            out = f.name
        await stream_to_wav_file("你好世界。", session, out)
        return out, session

    out_path, session = asyncio.run(run())
    # 验证 WAV 文件
    assert Path(out_path).exists()
    with wave.open(out_path, "rb") as w:
        nchannels = w.getnchannels()
        sampwidth = w.getsampwidth()
        framerate = w.getframerate()
        nframes = w.getnframes()
    assert nchannels == 1
    assert sampwidth == 2
    assert framerate == 16000
    assert nframes > 0
    Path(out_path).unlink()
    print(f"✅ Test 9 PASS: 保存 WAV（{nframes} frames @ {framerate}Hz）")


def test_10_cli_dry_run():
    """测试 10: CLI dry-run"""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "streaming.py"),
         "--text", "测试流式合成",
         "--scene", "live_stream",
         "--dry-run"],
        capture_output=True, text=True, encoding="utf-8"
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["mode"] == "voice_design"
    assert data["sentences"] >= 1
    assert "estimated_duration_sec" in data
    assert data["watermark"] == "ai_generated_streaming"
    print(f"✅ Test 10 PASS: CLI dry-run")


def test_11_cli_list_scenes():
    """测试 11: CLI 列出场景"""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "streaming.py"), "--list-scenes"],
        capture_output=True, text=True, encoding="utf-8"
    )
    assert "5 类实时场景预设" in result.stdout
    assert "live_stream" in result.stdout
    print(f"✅ Test 11 PASS: CLI 列出场景")


def test_12_performance_first_byte():
    """测试 12: 性能基线 - 首字节延迟 < 500ms"""
    async def run():
        session = StreamSession(
            session_id="perf_test",
            mode="voice_design",
            voice_desc="(女性)",
            sample_rate=24000,
        )
        async for _ in stream_text_to_audio("短句测试。", session):
            break  # 只取第一个 chunk
        return session

    session = asyncio.run(run())
    assert session.first_byte_at is not None
    # mock 模型（正弦波）首字节应 < 100ms
    assert session.first_byte_at < 0.3
    print(f"✅ Test 12 PASS: 首字节 {session.first_byte_at*1000:.1f}ms（< 300ms）")


def run_all():
    """运行全部测试"""
    tests = [
        test_1_scene_presets,
        test_2_stream_config,
        test_3_split_sentences,
        test_4_ethics_validation,
        test_5_scene_preset_lookup,
        test_6_async_streaming,
        test_7_wav_encoder,
        test_8_protocol_messages,
        test_9_save_to_wav,
        test_10_cli_dry_run,
        test_11_cli_list_scenes,
        test_12_performance_first_byte,
    ]

    print(f"\n🧪 运行 voxcpm-streaming 测试 ({len(tests)} 个用例)")
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
            import traceback
            print(f"❌ {test.__name__} ERROR: {type(e).__name__}: {e}")
            traceback.print_exc()
            failed += 1

    print("=" * 60)
    print(f"📊 结果: {passed}/{len(tests)} PASS, {failed} FAIL")
    return failed == 0


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
