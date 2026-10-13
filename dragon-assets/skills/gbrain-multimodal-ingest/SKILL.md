---
license: UNKNOWN
github_repo: garrytan/gbrain
github_hash: 11abb24ddd2209f8622870c2e48dc9ef050ad749
last_updated: 2026-04-25
source_type: derived
triggers: ["gbrain multimodal ingest", "gbrain-multimodal-ingest"]
---
# gbrain-multimodal-ingest

## L0: 一句话描述 (≤15字)
视频/音频/会议自动转录并记忆存储

## L1: 使用场景 (50-100字)
适用于需要处理视频、音频、会议录音等多模态内容，并将其转换为可搜索、可记忆的知识资产。当用户上传视频、录制会议、或需要分析音频内容时启用。

## L2: 详细文档

### 核心能力

| 能力 | 说明 | 优先级 |
|------|------|--------|
| 视频转录 | 视频→文字转录 | P0 |
| 音频转录 | 音频→文字转录 | P0 |
| 会议摄入 | 会议录音→结构化笔记 | P0 |
| 多语言支持 | 中/英/日等多语言转录 | P1 |
| 说话人识别 | 自动识别不同说话人 | P1 |
| 关键内容提取 | 自动提取关键信息和摘要 | P1 |

### 支持格式

```yaml
supported_formats:
  video:
    - mp4, avi, mov, mkv, webm
    - max_size: 2GB
    - codec: h264, h265, vp9

  audio:
    - mp3, wav, m4a, flac, ogg
    - max_size: 500MB

  meeting:
    - Zoom recordings
    - Teams recordings
    - Google Meet recordings
    - 飞书会议
    - 腾讯会议
```

### 处理流程

```
┌─────────────────────────────────────────────────────────────┐
│                    多模态摄入流程                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. [格式检测] 识别输入类型                               │
│     ├── Video (mp4/avi/mov)                              │
│     ├── Audio (mp3/wav/m4a)                              │
│     └── Meeting (zoom/teams/飞书)                          │
│                          ↓                                  │
│  2. [转录处理] 语音转文字                                 │
│     ├── Whisper API / 本地模型                            │
│     ├── 说话人分离（Diarization）                        │
│     └── 时间戳同步                                         │
│                          ↓                                  │
│  3. [结构化处理] 生成可读格式                           │
│     ├── 自动摘要                                          │
│     ├── 关键点提取                                        │
│     └── 问答生成                                          │
│                          ↓                                  │
│  4. [知识沉淀] 写入记忆系统                              │
│     ├── MemPalace (L3)                                  │
│     ├── llm-wiki-compiler                                │
│     └── advanced-memory-sync (L0原文)                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 与天龙引擎协同

```yaml
tianlong_integration:
  # 挂载到07记录师
  attached_role: "07-scribe"

  # 下游处理
  downstream:
    - gbrain-signal-detector  # 信号检测
    - gbrain-daily-briefing  # 每日简报

  # 底层存储
  storage_layers:
    - MemPalace (V8.85)        # 结构化存储
    - llm-wiki-compiler (V8.85)  # 知识归档
    - advanced-memory-sync (V8.61)  # L0原文存储

  # 依赖技能
  dependencies:
    - openai-whisper         # 语音转录
    - long-audio-transcript-processor  # 长音频处理
    - tg-cli                  # 会议摄入
```

### 使用方法

```bash
# 转录视频
[@07记录师] 转录这个视频文件 ./meeting.mp4

# 转录音频
[@07记录师] 转录音频 ./podcast.mp3

# 会议摄入
[@07记录师] 摄入飞书会议记录

# 批量处理
[@07记录师] 批量转录 ./videos/ 目录下所有视频
```

### 配置示例

```yaml
# ~/.claude/skills/gbrain-multimodal-ingest/config.yaml
multimodal_ingest:
  # 转录设置
  transcription:
    # 语音模型
    model: "whisper-1"  # OpenAI Whisper
    # model: "local"    # 本地Whisper

    # 语言设置
    language: "auto"  # 自动检测
    # language: "zh"   # 中文
    # language: "en"   # 英文

  # 处理设置
  processing:
    # 自动摘要
    auto_summary: true

    # 关键词提取
    extract_keywords: true

    # 问答生成
    generate_qa: false

    # 说话人识别
    speaker_diarization: true

  # 存储设置
  storage:
    # L0原文存储位置
    raw_storage: "advanced-memory-sync/L0"

    # 结构化存储位置
    structured_storage: "MemPalace"

    # Wiki编译
    wiki_compile: true
```

## 文件结构

```
gbrain-multimodal-ingest/
├── SKILL.md                    # 本文件
├── config.yaml                 # 配置文件
├── scripts/
│   ├── video_transcriber.py   # 视频转录
│   ├── audio_transcriber.py   # 音频转录
│   ├── meeting_ingester.py     # 会议摄入
│   └── processor.py           # 处理器
└── prompts/
    ├── summarizer.md          # 摘要生成提示词
    └── qa_generator.md        # 问答生成提示词
```

## 来源参考

本Skill整合自 [garrytan/gbrain](https://github.com/garrytan/gbrain) 的 media-ingest 和 meeting-ingestion 能力。
