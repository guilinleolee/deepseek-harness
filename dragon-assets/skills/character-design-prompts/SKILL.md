---
license: UNKNOWN
triggers: ["character design prompts", "character-design-prompts"]
---
# character-design-prompts

## L0: 一句话描述 (≤15字)
角色设计提示词库

## L1: 使用场景 (50-100字)
当用户需要生成动漫角色、二次元人物、迪士尼风格、皮克斯3D角色、Q版萌系等角色设计图像时使用。从社区验证的高互动角色设计提示词库中检索，适用于IP设计、游戏角色、二次元创作、卡通形象参考。

## L2: 详细文档

### 核心能力

**数据来源**：基于 EvoLinkAI/awesome-gpt-image-2-prompts 角色设计精选

**支持类别**：
- Anime/Cartoon（动漫卡通）：anime, manga, comic, chibi
- 3D Character（3D角色）：pixar, disney, dreamworks,3d
- Style（风格）：vintage_cartoon, doodle, sketch, vector

### 数据结构

```yaml
# 角色设计提示词数据格式
category: anime|3d_character|cartoon|style
style: anime|manga|chibi|pixar|disney|dreamworks|vintage_cartoon|doodle|sketch|vector
prompt: 完整的GPT-Image-2角色设计提示词
engagement:
  likes: int
  retweets: int
  views: int
author: "@Twitter用户名"
```

### 核心命令

```bash
# 查询动漫角色
python3 ~/.claude/skills/character-design-prompts/scripts/query.py \
  --category anime --sort engagement --limit 10

# 查询3D角色
python3 ~/.claude/skills/character-design-prompts/scripts/query.py \
  --category 3d_character --style pixar

# 获取推荐
python3 ~/.claude/skills/character-design-prompts/scripts/query.py \
  --recommend ip_design
```

### 角色风格速查

| 风格 | 关键词 | 适用场景 |
|------|--------|---------|
| **Anime** | Japanese anime, Studio Ghibli, cel shading | 日漫风角色 |
| **Manga** | Black and white, halftone dots, comic panels | 漫画风角色 |
| **Chibi** | Super deformed, big head, cute | Q版萌系 |
| **Pixar/Disney** | 3D render, stylized, toon shading | 3D动画角色 |
| **Vintage Cartoon** | 1950s animation, rubber hose style | 复古卡通 |
| **Doodle** | Hand-drawn, line art, sketch style | 涂鸦风角色 |

### 天龙岗位升级

| 岗位 | 版本 | 新增能力 |
|------|------|---------|
| **13-01 设计师** | V11.0→V11.1 | 角色设计提示词库 |
| **35-02 社媒运营** | V13.2→V13.3 | 二次元内容生成 |

### 与现有技能协同

| 现有技能 | 协同方式 |
|---------|---------|
| **portrait-editorial-style** | 肖像摄影vs角色设计 |
| **professional-photography-prompts** | 真人摄影vs角色设计 |
| **gpt-image-2-prompt-library** | 主库引用 |

### 版本信息

- **Version**: 1.0.0
- **Author**: 天龙引擎集成
- **Source**: EvoLinkAI/awesome-gpt-image-2-prompts
- **Last Updated**: 2026-04-28
