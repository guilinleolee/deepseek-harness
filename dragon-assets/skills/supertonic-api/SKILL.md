---
license: UNKNOWN
triggers: ["supertonic api", "Supertonic API - OpenAI兼容语音合成接口"]
---
# Supertonic API - OpenAI兼容语音合成接口

## L0: 一句话描述 (≤15字)
OpenAI兼容TTS API封装

## L1: 使用场景 (50-100字)
适用场景：LLM应用语音输出、API代理服务、第三方TTS集成、多语言语音合成。通过OpenAI兼容接口无缝集成到现有AI应用，支持流式输出和中文语境适配。

## L2: 详细文档

### 来源项目
> [supertone-inc/supertonic](https://github.com/supertone-inc/supertonic) - Lightning-fast on-device multilingual TTS

### API端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/v1/audio/speech` | POST | 流式语音合成 |
| `/v1/tts` | POST | 标准语音合成 |
| `/v1/voices` | GET | 列出可用音色 |
| `/v1/languages` | GET | 列出支持语言 |
| `/health` | GET | 服务健康检查 |

### 请求格式

```python
import requests

# OpenAI兼容格式
response = requests.post(
    "http://localhost:8000/v1/audio/speech",
    headers={
        "Authorization": "Bearer YOUR_API_KEY",
        "Content-Type": "application/json"
    },
    json={
        "model": "supertonic",
        "input": "欢迎使用语音合成服务",
        "voice": "M1",
        "response_format": "mp3",
        "speed": 1.0
    },
    stream=True
)

# 保存音频
with open("output.mp3", "wb") as f:
    for chunk in response.iter_content(chunk_size=8192):
        if chunk:
            f.write(chunk)
```

### 中文语境适配

```python
from supertonic import TTS

tts = TTS(auto_download=True)

# 中文语境适配
style = tts.get_voice_style(voice_name="M1")

# 中文合成
wav, duration = tts.synthesize(
    text="欢迎使用天龙引擎语音合成功能",
    lang="zh",
    voice_style=style,
    total_steps=8,
    speed=1.05,
    enable_context_aware=True,
    context_mode="formal"
)
```

### API配置参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `model` | string | "supertonic" | 模型名称 |
| `input` | string | - | 待合成文本 |
| `voice` | string | "M1" | 音色名称 |
| `response_format` | string | "mp3" | 输出格式: mp3/wav/opus |
| `speed` | float | 1.0 | 语速 0.5-2.0 |
| `temperature` | float | 0.7 | 创造性温度 |
| `enable_context_aware` | bool | false | 语境感知 |

### 天龙引擎协同岗位

| 岗位 | 协同方式 |
|------|---------|
| **10-02 AI研究员** | LLM流式输出+语音合成 |
| **17-04 桌面自动化** | 语音命令识别+响应 |
| **35-05 短视频编导** | 自动配音服务 |
| **47-03 IM运营师** | 语音消息播放 |

### 天龙命令速查

```bash
# API服务启动
[@17-04] 启动TTS API服务

# LLM集成
[@10-02] 将Supertonic API集成到LLM应用

# 第三方集成
[@17-04] 配置Supertonic为OpenAI TTS替代
```

### 与现有技能协同

| 现有技能 | 协同方式 |
|---------|---------|
| **openai-whisper** | 语音转文字→TTS语音回复 |
| **xiaohongshu-mcp** | 文字生成→语音播报 |
| **ppt-generator** | PPT语音讲解 |

### 预期收益

| 指标 | 数值 |
|------|------|
| **API兼容性** | 100% OpenAI |
| **延迟** | <100ms |
| **中文支持** | 31种语言 |

### 文件结构

```
supertonic-api/
├── SKILL.md                    # 本文件
├── scripts/
│   ├── api_client.py          # Python API封装
│   ├── openai_proxy.py        # OpenAI兼容代理
│   └── streaming_client.py    # 流式客户端
└── prompts/
    └── api-integration.md     # 集成提示词
```

### 技术约束

- 需要ONNX Runtime支持
- 网络延迟影响流式输出
- 中文语境需要上下文配置

### 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-19 | 初始集成，基于Supertonic OpenAI兼容API |