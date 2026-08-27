"""
voxcpm-streaming 流式 TTS 核心库 · V1.0
实时流式合成（句子级 chunked）· 首字节 < 300ms

依赖:
    - websockets (服务端/客户端)
    - numpy (音频处理)
    - asyncio (异步 I/O)
"""

import asyncio
import json
import logging
import time
import wave
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional, Dict, List, AsyncIterator

import numpy as np

logger = logging.getLogger("voxcpm_streaming")

# ===== 默认配置 =====
DEFAULT_SAMPLE_RATE = 24000
DEFAULT_CHANNELS = 1
SAMPLE_WIDTH = 2  # 16-bit PCM


# ===== 6 维流控参数 =====
@dataclass
class StreamConfig:
    """6 维流控配置"""
    speed: float = 1.0          # 0.5-2.0
    pitch: int = 0              # -12~+12 半音
    emotion: str = "平静"        # 10 类别
    pause_ms: int = 200         # 句间停顿
    overlap: float = 0.0        # 0-0.5 句首重叠
    fade_ms: int = 50           # 0-500 句首淡入


# ===== 10 情绪类别 =====
EMOTIONS = ["平静", "开心", "严肃", "激动", "温柔", "愤怒", "悲伤", "惊讶", "紧张", "舒缓"]


# ===== 5 类场景预设 =====
SCENE_PRESETS = {
    "live_stream": {     # 直播弹幕
        "speed": 1.3, "pitch": 2, "emotion": "激动",
        "pause_ms": 100, "overlap": 0.0, "fade_ms": 20,
    },
    "voice_assistant": {  # 智能助手
        "speed": 1.0, "pitch": 0, "emotion": "温柔",
        "pause_ms": 150, "overlap": 0.0, "fade_ms": 30,
    },
    "audiobook": {        # 有声书
        "speed": 0.95, "pitch": 0, "emotion": "平静",
        "pause_ms": 350, "overlap": 0.05, "fade_ms": 80,
    },
    "customer_service": { # 客服
        "speed": 1.05, "pitch": 0, "emotion": "温柔",
        "pause_ms": 200, "overlap": 0.0, "fade_ms": 40,
    },
    "meeting_notes": {    # 会议纪要
        "speed": 1.1, "pitch": 0, "emotion": "严肃",
        "pause_ms": 180, "overlap": 0.0, "fade_ms": 30,
    },
}


# ===== 黑名单（敏感人物关键词）=====
BLOCKED_KEYWORDS = ["习近平", "Trump 特朗普", "Biden 拜登"]  # 简化


# ===== 句子分割 =====
def split_sentences(text: str) -> List[str]:
    """按中英文标点分句（保留标点）"""
    import re
    text = text.strip()
    if not text:
        return []

    # 1. 优先：标点 + 空白（英文常用）
    pattern_ws = re.compile(r'(?<=[.!?])\s+')
    parts = pattern_ws.split(text)
    if len(parts) > 1:
        return [p.strip() for p in parts if p.strip()]

    # 2. 次优：标点后无空白（中文常用）— 按中英文标点切分，保留标点
    pattern_cn = re.compile(r'(?<=[。！？.!?])')
    parts = pattern_cn.split(text)
    if len(parts) > 1:
        return [p.strip() for p in parts if p.strip()]

    # 3. 都没有：单句
    return [text]


# ===== 流式合成会话 =====
@dataclass
class StreamSession:
    """单次流式会话"""
    session_id: str
    mode: str = "voice_design"               # voice_design / hifi_clone
    voice_desc: Optional[str] = None
    reference_wav: Optional[str] = None
    language: str = "zh"
    config: StreamConfig = field(default_factory=StreamConfig)
    consent_file: Optional[str] = None       # 伦理
    watermark: bool = True
    sample_rate: int = DEFAULT_SAMPLE_RATE

    # 运行时统计
    chunks_sent: int = 0
    first_byte_at: Optional[float] = None
    started_at: float = field(default_factory=time.time)
    total_samples: int = 0


def validate_session_ethics(session: StreamSession) -> Dict:
    """校验流式会话伦理"""
    issues = []

    # 克隆模式需要同意书
    if session.mode == "hifi_clone" and not session.consent_file:
        issues.append({
            "type": "missing_consent",
            "severity": "BLOCK",
            "message": "克隆模式必须提供 --consent-file",
        })

    # 黑名单
    if session.voice_desc:
        for kw in BLOCKED_KEYWORDS:
            if kw in session.voice_desc:
                issues.append({
                    "type": "blacklist",
                    "severity": "BLOCK",
                    "message": f"voice_desc 含黑名单关键词: {kw}",
                })

    # 流控参数范围
    if not (0.5 <= session.config.speed <= 2.0):
        issues.append({
            "type": "invalid_param",
            "severity": "BLOCK",
            "message": f"speed 越界: {session.config.speed}（范围 0.5-2.0）",
        })

    return {
        "passed": not any(i["severity"] == "BLOCK" for i in issues),
        "issues": issues,
    }


def get_scene_preset(scene: str) -> StreamConfig:
    """获取场景预设"""
    if scene not in SCENE_PRESETS:
        raise ValueError(f"未知场景: {scene}（可选: {list(SCENE_PRESETS.keys())}）")
    return StreamConfig(**SCENE_PRESETS[scene])


# ===== 流式合成（mock 实现，实际由 voxcpm-tts-integration 注入）=====
async def synthesize_sentence_streaming(
    sentence: str,
    session: StreamSession,
) -> AsyncIterator[bytes]:
    """
    流式合成单句 → PCM 字节流

    mock 实现：生成正弦波占位（实际应由 voxcpm-tts-integration 注入真模型）
    """
    # 估算音频时长：中文 0.18s/字符（受 speed 影响）
    duration = max(0.3, len([c for c in sentence if '\u4e00' <= c <= '\u9fff']) * 0.18 / session.config.speed)
    total_samples = int(duration * session.sample_rate)

    # 模拟首字节延迟
    await asyncio.sleep(0.05)  # 50ms 模拟合成时间

    # 分块输出（每块 100ms 音频）
    chunk_ms = 100
    chunk_samples = int(session.sample_rate * chunk_ms / 1000)
    sent = 0

    while sent < total_samples:
        # 生成该 chunk 的正弦波
        n = min(chunk_samples, total_samples - sent)
        t = np.arange(n) / session.sample_rate
        freq = 440.0 * (2 ** (session.config.pitch / 12.0))
        samples = (np.sin(2 * np.pi * freq * t) * 16000 * 0.3).astype(np.int16)

        # 句首淡入
        if sent == 0 and session.config.fade_ms > 0:
            fade_n = int(session.sample_rate * session.config.fade_ms / 1000)
            fade_n = min(fade_n, n)
            fade = np.linspace(0, 1, fade_n)
            samples[:fade_n] = (samples[:fade_n].astype(np.float32) * fade).astype(np.int16)

        chunk_bytes = samples.tobytes()

        # 记录首字节（在 yield 前）
        if session.first_byte_at is None:
            session.first_byte_at = time.time() - session.started_at

        yield chunk_bytes

        sent += n
        session.chunks_sent += 1
        session.total_samples += n

        await asyncio.sleep(0.01)  # 模拟流式 chunk 间隔


# ===== 流式 WAV 编码器 =====
class StreamingWAVEncoder:
    """流式 WAV 编码器（先写 header，结束后 patch）"""

    def __init__(self, sample_rate: int = DEFAULT_SAMPLE_RATE, channels: int = DEFAULT_CHANNELS):
        self.sample_rate = sample_rate
        self.channels = channels
        self.data_size = 0
        self.header = self._make_header()

    def _make_header(self) -> bytes:
        """生成 WAV header（data_size 留空）"""
        import struct
        byte_rate = self.sample_rate * self.channels * SAMPLE_WIDTH
        block_align = self.channels * SAMPLE_WIDTH
        return struct.pack(
            '<4sI4s4sIHHIIHH4sI',
            b'RIFF', 0,           # 文件大小（待 patch）
            b'WAVE', b'fmt ',
            16,                    # PCM chunk size
            1,                     # PCM format
            self.channels,
            self.sample_rate,
            byte_rate, block_align,
            SAMPLE_WIDTH * 8,
            b'data', 0,            # data size（待 patch）
        )

    def encode_chunk(self, pcm_data: bytes) -> bytes:
        """追加 PCM 数据"""
        self.data_size += len(pcm_data)
        return pcm_data

    def finalize(self) -> bytes:
        """完成时 patch header"""
        import struct
        total_size = 36 + self.data_size
        patched = self.header[:4] + struct.pack('<I', total_size) + self.header[8:40] + struct.pack('<I', self.data_size)
        return patched


# ===== 协议消息 =====
def make_handshake_msg(session: StreamSession) -> str:
    """握手消息"""
    return json.dumps({
        "type": "handshake",
        "session_id": session.session_id,
        "sample_rate": session.sample_rate,
        "config": asdict(session.config),
        "watermark": session.watermark,
    }, ensure_ascii=False)


def make_audio_msg(chunk: bytes, session: StreamSession) -> bytes:
    """音频块消息（JSON 头 + 二进制）"""
    header = json.dumps({
        "type": "audio",
        "session_id": session.session_id,
        "chunk_id": session.chunks_sent,
        "sample_rate": session.sample_rate,
        "samples": len(chunk) // SAMPLE_WIDTH,
    }, ensure_ascii=False)
    # 简单定长分隔：4 字节 header 长度
    header_bytes = header.encode("utf-8")
    return len(header_bytes).to_bytes(4, "little") + header_bytes + chunk


def make_end_msg(session: StreamSession) -> str:
    """结束消息"""
    return json.dumps({
        "type": "end",
        "session_id": session.session_id,
        "total_chunks": session.chunks_sent,
        "total_samples": session.total_samples,
        "first_byte_ms": round((session.first_byte_at or 0) * 1000, 1),
        "elapsed_sec": round(time.time() - session.started_at, 3),
    }, ensure_ascii=False)


# ===== 文本流式入口 =====
async def stream_text_to_audio(
    text: str,
    session: StreamSession,
) -> AsyncIterator[bytes]:
    """文本 → 流式音频"""
    # 伦理校验
    eth = validate_session_ethics(session)
    if not eth["passed"]:
        err = json.dumps({"type": "error", "issues": eth["issues"]}, ensure_ascii=False)
        yield err.encode("utf-8")
        return

    # 分句
    sentences = split_sentences(text)
    logger.info(f"分句数: {len(sentences)}, session: {session.session_id}")

    # 句间停顿
    pause_samples = int(session.config.pause_ms * session.sample_rate / 1000)
    silence = (np.zeros(pause_samples, dtype=np.int16)).tobytes() if pause_samples > 0 else b""

    for i, sent in enumerate(sentences):
        async for chunk in synthesize_sentence_streaming(sent, session):
            yield chunk
        # 句间停顿
        if i < len(sentences) - 1 and silence:
            yield silence
            session.total_samples += pause_samples


# ===== 便捷保存到 WAV =====
async def stream_to_wav_file(
    text: str,
    session: StreamSession,
    output_path: str,
):
    """流式合成并保存为 WAV 文件"""
    encoder = StreamingWAVEncoder(session.sample_rate)
    audio_chunks: List[bytes] = []

    async for chunk in stream_text_to_audio(text, session):
        # 跳过错误消息
        if chunk.startswith(b"{"):
            try:
                msg = json.loads(chunk.decode("utf-8"))
                if msg.get("type") == "error":
                    raise RuntimeError(f"流式合成失败: {msg['issues']}")
            except json.JSONDecodeError:
                pass
            continue
        audio_chunks.append(encoder.encode_chunk(chunk))

    # 写文件：header + 数据
    with open(output_path, "wb") as f:
        f.write(encoder.header)
        for chunk in audio_chunks:
            f.write(chunk)
        # 回到文件开头 patch header
        f.seek(0)
        f.write(encoder.finalize())

    logger.info(f"已保存: {output_path} ({session.total_samples} samples)")


# ===== CLI 入口 =====
def main():
    import argparse
    parser = argparse.ArgumentParser(description="voxcpm-streaming · V1.0")

    parser.add_argument("--text", required=False, help="待合成文本")
    parser.add_argument("--mode", default="voice_design", choices=["voice_design", "hifi_clone"])
    parser.add_argument("--voice-desc", help="voice_design 描述")
    parser.add_argument("--reference-wav", help="hifi_clone 参考音频")
    parser.add_argument("--language", default="zh")
    parser.add_argument("--scene", choices=list(SCENE_PRESETS.keys()), help="场景预设")
    parser.add_argument("--output", default="./streamed.wav")
    parser.add_argument("--consent-file", help="克隆同意书")
    parser.add_argument("--sample-rate", type=int, default=DEFAULT_SAMPLE_RATE)
    parser.add_argument("--speed", type=float, default=None)
    parser.add_argument("--pitch", type=int, default=None)
    parser.add_argument("--emotion", default=None)
    parser.add_argument("--pause-ms", type=int, default=None)
    parser.add_argument("--list-scenes", action="store_true")
    parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    if args.list_scenes:
        print("\n📡 5 类实时场景预设:")
        for name, cfg in SCENE_PRESETS.items():
            print(f"  - {name:20s} speed={cfg['speed']}, emotion={cfg['emotion']}, pause={cfg['pause_ms']}ms")
        return

    if not args.text:
        print("❌ 错误: 缺少 --text 参数（除非使用 --list-scenes）")
        sys.exit(1)

    # 构建 session
    if args.scene:
        config = get_scene_preset(args.scene)
    else:
        config = StreamConfig()

    # 命令行覆盖
    if args.speed is not None:
        config.speed = args.speed
    if args.pitch is not None:
        config.pitch = args.pitch
    if args.emotion is not None:
        config.emotion = args.emotion
    if args.pause_ms is not None:
        config.pause_ms = args.pause_ms

    session = StreamSession(
        session_id=f"stream_{int(time.time())}",
        mode=args.mode,
        voice_desc=args.voice_desc,
        reference_wav=args.reference_wav,
        language=args.language,
        config=config,
        consent_file=args.consent_file,
        sample_rate=args.sample_rate,
    )

    # 伦理校验
    eth = validate_session_ethics(session)
    if not eth["passed"]:
        print("❌ 伦理校验失败:")
        for i in eth["issues"]:
            print(f"  [{i['severity']}] {i['message']}")
        return

    if args.dry_run:
        sentences = split_sentences(args.text)
        est_total = sum(
            max(0.3, len([c for c in s if '\u4e00' <= c <= '\u9fff']) * 0.18 / config.speed)
            for s in sentences
        )
        result = {
            "session_id": session.session_id,
            "mode": session.mode,
            "sentences": len(sentences),
            "estimated_duration_sec": round(est_total, 2),
            "config": asdict(config),
            "ethics": eth,
            "watermark": "ai_generated_streaming",
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # 实际合成
    asyncio.run(stream_to_wav_file(args.text, session, args.output))
    print(f"\n✅ 流式合成完成: {args.output}")
    print(f"   首字节延迟: {(session.first_byte_at or 0)*1000:.1f}ms")
    print(f"   总样本数: {session.total_samples}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
