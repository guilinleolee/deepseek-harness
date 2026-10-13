---
license: UNKNOWN
triggers: ["minimax multimodal toolkit", "MiniMax Multi-Modal Toolkit"]
---
# MiniMax Multi-Modal Toolkit

## Overview

Generate speech, music, video, and images via MiniMax APIs. Integrated with 03构建师 and 13-01设计师 for asset generation.

## Invocation

```
/minimax-tts "文本" -o output.mp3
/minimax-image "描述" --aspect-ratio 16:9 -o output.png
/minimax-video "场景描述" -o output.mp4
/minimax-music "风格描述" --instrumental -o output.mp3
[@03构建师] 使用minimax-multimodal生成配图
[@13-01] 使用minimax-multimodal生成视频素材
```

## Prerequisites

```bash
# System dependencies required
which ffmpeg jq xxd  # Must exist

# No Python needed - pure shell scripts
```

## API Configuration

```bash
# Set before running scripts
export MINIMAX_API_HOST="https://api.minimax.chat"
export MINIMAX_API_KEY="sk-cp-YOUR_API_KEY"  # or sk-api- prefix
```

**Output Directory:** All files saved to `minimax-output/` in working directory.

## Core Capabilities

### TTS (Text-to-Speech)

```bash
# Single voice synthesis
bash scripts/tts/generate_voice.sh tts "Hello world" -o minimax-output/hello.mp3

# Multi-segment (multiple voices/characters)
bash scripts/tts/generate_voice.sh multi -o minimax-output/dialogue.mp3

# Voice cloning
bash scripts/tts/generate_voice.sh clone --source audio.mp3 --text "New text" -o output.mp3
```

**Defaults:** HD MP3 format, single voice mode.

### Image Generation

```bash
# Text to Image
bash scripts/image/generate_image.sh \
  --prompt "A serene mountain landscape at sunset" \
  --aspect-ratio 16:9 \
  -o minimax-output/landscape.png

# Image to Image (with character reference)
bash scripts/image/generate_image.sh \
  --mode i2i \
  --prompt "Same character in a modern city" \
  --reference character_ref.png \
  -o minimax-output/modern_city.png

# Preset shortcuts
--aspect-ratio 16:9   # Hero sections
--aspect-ratio 1:1   # Thumbnails/social
--aspect-ratio 9:16   # Stories/mobile
```

### Video Generation

```bash
# Text to Video (default: 6s, 768P)
bash scripts/video/generate_video.sh \
  --mode t2v \
  --prompt "A puppy runs on grass, [跟随] tracking shot" \
  -o minimax-output/puppy.mp4

# Image to Video
bash scripts/video/generate_video.sh \
  --mode i2v \
  --prompt "The character walks forward, camera follows" \
  --input character.png \
  -o minimax-output/walking.mp4

# Long video (multi-scene)
bash scripts/video/generate_video.sh \
  --mode t2v \
  --prompt "Scene 1: Morning in forest. Scene 2: Character discovers hidden cave." \
  --long-video \
  -o minimax-output/adventure.mp4
```

### Music Generation

```bash
# Instrumental BGM (default)
bash scripts/music/generate_music.sh \
  --instrumental \
  --prompt "ambient electronic, 80bpm, chill" \
  -o minimax-output/bgm.mp3 \
  --download

# Vocal song (ask user for lyrics)
bash scripts/music/generate_music.sh \
  --prompt "upbeat pop, 120bpm, happy lyrics" \
  --lyrics "La la la, sunshine today..." \
  -o minimax-output/song.mp3

# Duration presets
--duration 30  # 30 seconds
--duration 60  # 60 seconds
--loopable     # Loop-optimized for BGM
```

### Media Tools

```bash
# Convert format
bash scripts/media_tools.sh convert input.mp4 output.webm

# Concatenate videos
bash scripts/media_tools.sh concat "video1.mp4|video2.mp4|video3.mp4" output.mp4

# Trim video
bash scripts/media_tools.sh trim input.mp4 --start 0 --duration 10 output.mp4
```

## Asset Naming Convention

```
{type}-{descriptor}-{timestamp}.{ext}

Examples:
tts-narration-20260330.mp3
image-hero-banner-20260330.png
video-product-demo-20260330.mp4
music-bgm-ambient-20260330.mp3
```

## Integration with 天龙引擎

**Upgrades:**
- 03构建师 V8.72 → V8.73: Asset generation capabilities
- 13-01设计师 V10.2 → V10.3: Multi-modal creative assets
- 10-02 AI研究员 V8.68 → V8.73: Multi-modal AI toolkit

**Synergies:**
- minimax-frontend-dev: Asset generation for web
- ppt-generator: Embed TTS in presentations
- remotion-best-practices: Video generation pipeline
- Seedance2-skill: Alternative video generation

## Important Defaults

| Task | Default | Override |
|------|---------|----------|
| TTS | Single voice | Multi-segment for dialogue |
| Music | Instrumental | Vocal with --lyrics |
| Image | t2i mode | i2i only with character ref |
| Video | 6s/768P | Long video only when requested |

## Error Handling

```bash
# Check API key validity
curl -s -H "Authorization: Bearer $MINIMAX_API_KEY" \
  "$MINIMAX_API_HOST/v1/me" | jq .balance

# Common errors
# 401: Invalid API key - check MINIMAX_API_KEY
# 403: Insufficient credits - check balance
# 429: Rate limit - wait and retry
```
