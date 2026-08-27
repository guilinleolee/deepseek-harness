---
license: UNKNOWN
triggers: ["minimax gif sticker maker", "MiniMax GIF Sticker Maker"]
---
# MiniMax GIF Sticker Maker

## Overview

Convert photos into animated GIF stickers in Funko Pop style with customizable expressions and poses.

## Invocation

```
/minimax-gif "生成GIF贴纸"
[@13-01] 使用minimax-gif创建动态贴纸
```

## Workflow

### 1. Input Image
Provide a clear photo (PNG/JPG recommended).

### 2. Style Selection
Choose Funko Pop style parameters.

### 3. Generate
```bash
bash scripts/gif_sticker.sh --input photo.png --style funkopop --output sticker.gif
```

### 4. Customize
Adjust expressions, add accessories, change background.

## Style Options

| Parameter | Values | Description |
|-----------|--------|-------------|
| style | funkopop, chibi, anime | Character style |
| expression | happy, sad, angry, surprised | Facial expression |
| pose | standing, sitting, action | Character pose |
| background | transparent, solid, gradient | Sticker background |
| size | small, medium, large | Output size |

## Output Formats

- GIF: Animated sticker (default)
- PNG: Single frame static sticker
- WebP: Compressed with transparency

## Integration with 天龙引擎

**Upgrades:**
- 13-01设计师 V10.2 → V10.3: Animated sticker creation

**Synergies:**
- qiaomu-mondo-poster-design: Character art
- smart-illustrator: Illustration generation
- manga-style-video: Animation production
