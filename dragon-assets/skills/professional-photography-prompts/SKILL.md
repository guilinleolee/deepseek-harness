---
license: UNKNOWN
triggers: ["professional photography prompts", "professional-photography-prompts"]
---
# professional-photography-prompts

## L0: 一句话描述 (≤15字)
专业摄影风格提示词库

## L1: 使用场景 (50-100字)
当用户需要生成专业级摄影图像（肖像/街拍/产品/风光）时使用。从社区验证的35mm/Fujifilm/CCD/Korean等摄影风格提示词库中检索高质量提示词，适用于小红书配图、公众号封面、产品摄影参考。

## L2: 详细文档

### 核心能力

**数据来源**：[EvoLinkAI/awesome-gpt-image-2-prompts](https://github.com/EvoLinkAI/awesome-gpt-image-2-prompts) - 社区验证的专业摄影提示词

**支持类别**：
- Portrait（肖像摄影）
- Street（街拍纪实）
- Product（产品摄影）
- Landscape（风光摄影）
- Editorial（时尚编辑）

### 数据结构

```yaml
# 摄影提示词数据格式
category: portrait|street|product|landscape|editorial
style: 35mm|fujifilm|ccd|korean|neon|film|grain|analog...
prompt: 完整的GPT-Image-2摄影提示词
engagement:
  likes: int
  retweets: int
  views: int
author: "@Twitter用户名"
```

### 核心命令

```bash
# 查询肖像摄影
python3 ~/.claude/skills/professional-photography-prompts/scripts/query.py \
  --category portrait --sort engagement --limit 10

# 查询35mm胶片风格
python3 ~/.claude/skills/professional-photography-prompts/scripts/query.py \
  --style 35mm --category portrait

# 获取推荐
python3 ~/.claude/skills/professional-photography-prompts/scripts/query.py \
  --random --limit 5
```

### 摄影风格速查

| 风格 | 关键词 | 适用场景 |
|------|--------|---------|
| **35mm Film** | Kodak Portra, natural grain, warm tones | 纪实肖像 |
| **Fujifilm** | Provia 100F, vibrant pastels, soft contrast | 时尚摄影 |
| **CCD Sensor** | Color bleeding, nostalgic mood, analog warmth | 复古风格 |
| **Korean Idol** | Clean retouch, bright highlights, dreamy | 小红书肖像 |
| **Neon** | Rain reflections, urban夜色, convenience store | 氛围感 |
| **Japanese Onsen** | Steam, shoji screens, amber tones | 日系人像 |

### 天龙岗位升级

| 岗位 | 版本 | 新增能力 |
|------|------|---------|
| **13-01 设计师** | V10.8→V10.9 | 专业摄影风格库 |
| **35-02 社媒运营** | V12.3→V13.0 | 摄影级社媒配图 |
| **07 记录师** | V9.04→V9.05 | 知识可视化摄影 |

### 与现有技能协同

| 现有技能 | 协同方式 |
|---------|---------|
| **gpt-image-2-prompt-library** | 补充专业摄影子集 |
| **qiaomu-mondo-poster-design** | 肖像 vs 海报插画 |
| **manga-style-video** | 静态摄影 vs 动态漫画 |

### 版本信息

- **Version**: 1.0.0
- **Author**: 天龙引擎集成
- **Source**: EvoLinkAI/awesome-gpt-image-2-prompts
- **Last Updated**: 2026-04-28
