---
license: UNKNOWN
github_repo: bytedance/deer-flow
github_hash: f394c0d8c8de8821ac6a5becc73f5a9587a03e42
triggers: ["podcast generation", "podcast-generation"]
---
# podcast-generation

## Overview

AI播客内容生成技能 - 从文本生成专业播客音频。

**来源**: [bytedance/deer-flow](https://github.com/bytedance/deer-flow) - 播客生成模块

## When to Use

- 需要将研究报告转化为播客
- 需要多角色对话式内容
- 需要内容多渠道分发（音频）
- 需要专业级音频生成
- 需要背景音乐和音效

## Core Capabilities

### 1. Script Generation
- 文本转播客脚本
- 多角色对话生成
- 结构化叙事
- 专家访谈模拟

### 2. Voice Synthesis
- 多角色配音
- 情感表达
- 语速控制
- 停顿和强调

### 3. Audio Production
- 背景音乐添加
- 音效插入
- 音频混音
- 格式转换

## Workflow

### Step 1: Script Generation

```bash
python scripts/generate_script.py \
  --input research-report.md \
  --output podcast-script.md \
  --format dialogue \
  --speakers 2 \
  --duration 15
```

### Step 2: Voice Synthesis

```bash
python scripts/text_to_speech.py \
  --script podcast-script.md \
  --output podcast-audio.mp3 \
  --voice_preset professional \
  --add_music
```

### Step 3: Audio Production

```bash
python scripts/audio_production.py \
  --input podcast-audio.mp3 \
  --background_music ambient/tech \
  --add_intro_outro \
  --output final-podcast.mp3
```

## Script Templates

### Template 1: News Style
```markdown
# [Episode Title]

## Intro
[Host introduction, episode overview]

## Main Story
[News content, expert opinions, analysis]

## Discussion
[Host-guest dialogue, insights]

## Outro
[Summary, call to action]
```

### Template 2: Interview Style
```markdown
# [Interview Title]

## Introduction
[Host introduces guest and topic]

## Background
[Guest background, expertise]

## Deep Dive
[Core discussion questions and answers]

## Key Takeaways
[3-5 main points]

## Closing
[Thank you, next episode preview]
```

### Template 3: Tutorial Style
```markdown
# [Tutorial Title]

## Introduction
[What listeners will learn]

## Overview
[Topic introduction, prerequisites]

## Main Content
[Step-by-step explanation]

## Examples
[Practical examples, demonstrations]

## Summary
[Key points recap, next steps]
```

## Voice Presets

| Preset | Description | Best For |
|--------|------------|---------|
| professional | 正式播客腔调 | 新闻、访谈 |
| casual | 轻松随意的对话 | 生活、娱乐 |
| technical | 技术专家风格 | 技术深度内容 |
| storytelling | 叙事风格 | 故事类内容 |
| educational | 教育风格 | 教程、知识讲解 |

## Background Music

| Category | Mood | Use Case |
|---------|------|---------|
| ambient/tech | 科技感、轻松 | 技术播客 |
| ambient/warm | 温暖、亲切 | 生活类 |
| ambient/energetic | 活力、动感 | 商业财经 |
| ambient/calm | 平静、专注 | 冥想、健康 |
| corporate/professional | 专业商务 | 企业内容 |

## Output Formats

| Format | Extension | Bitrate | Use Case |
|--------|----------|---------|---------|
| MP3 High | .mp3 | 320kbps | 发布平台 |
| MP3 Standard | .mp3 | 128kbps | 日常收听 |
| AAC | .m4a | 256kbps | Apple Podcasts |
| WAV | .wav | lossless | 后期制作 |

## Complete Example

```bash
# 1. 从研究报告生成播客脚本
python scripts/generate_script.py \
  --input ai-trends-report.md \
  --output ai-podcast.md \
  --format interview \
  --speakers "Host,AI Expert" \
  --duration 20

# 2. 生成语音
python scripts/text_to_speech.py \
  --script ai-podcast.md \
  --output ai-podcast.mp3 \
  --voice_preset professional \
  --add_music ambient/tech

# 3. 添加开场和结束
python scripts/audio_production.py \
  --input ai-podcast.mp3 \
  --add_intro_outro \
  --intro_text "欢迎收听AI深度解读节目" \
  --outro_text "感谢收听，更多内容请访问..." \
  --output final-ai-podcast.mp3
```

## Integration with Research

```bash
# 完整研究-播客工作流
[@调研师] 使用deep-research研究AI Agent趋势

[@记录师] 使用consulting-analysis生成报告

[@记录师] 使用podcast-generation转换为播客
"将AI Agent趋势报告转换为20分钟播客"
```

## Audio Processing Options

### Noise Reduction
```bash
python scripts/audio_production.py \
  --input podcast.mp3 \
  --noise_reduction_level medium \
  --output clean-podcast.mp3
```

### Volume Normalization
```bash
python scripts/audio_production.py \
  --input podcast.mp3 \
  --normalize true \
  --target_lufs -16 \
  --output normalized-podcast.mp3
```

### Chapter Markers
```bash
python scripts/audio_production.py \
  --input podcast.mp3 \
  --add_chapters chapters.json \
  --output chaptered-podcast.mp3
```

## Expected Benefits

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| 内容创作效率 | 手动录制 | 自动生成 | +300% |
| 多渠道分发 | 仅文本 | +音频 | +100% |
| 播客产量 | 1/周 | 3/天 | +2100% |
| 内容一致性 | 低 | 高 | +200% |

## Version

- **V1.0** (2026-04-02): 初始集成播客生成技能
