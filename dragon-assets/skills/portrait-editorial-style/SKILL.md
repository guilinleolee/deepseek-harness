---
license: UNKNOWN
triggers: ["portrait editorial style", "portrait-editorial-style"]
---
# portrait-editorial-style

## L0: 一句话描述 (≤15字)
肖像时尚编辑提示词库

## L1: 使用场景 (50-100字)
当用户需要生成Vogue/Teen Vogue时尚大片、Korean Idol肖像、35mm胶片复古、CCD怀旧等肖像和时尚编辑风格图像时使用。从社区验证的高互动肖像和时尚编辑提示词库中检索，适用于杂志封面、社媒头像、时尚摄影参考。

## L2: 详细文档

### 核心能力

**数据来源**：基于 EvoLinkAI/awesome-gpt-image-2-prompts 肖像+时尚编辑精选

**支持类别**：
- Portrait（肖像摄影）：35mm/CCD/Korean/Neon/Cinematic/Moody
- Editorial（时尚编辑）：Vogue/Teen Vogue/Commercial

### 数据结构

```yaml
# 肖像/时尚编辑提示词数据格式
category: portrait|editorial
style: 35mm|fujifilm|ccd|korean|neon|cinematic|moody|vogue|teen_vogue|commercial
prompt: 完整的GPT-Image-2肖像/时尚编辑提示词
engagement:
  likes: int
  retweets: int
  views: int
author: "@Twitter用户名"
```

### 核心命令

```bash
# 查询肖像摄影
python3 ~/.claude/skills/portrait-editorial-style/scripts/query.py \
  --category portrait --sort engagement --limit 10

# 查询时尚编辑
python3 ~/.claude/skills/portrait-editorial-style/scripts/query.py \
  --category editorial --style vogue

# 获取推荐
python3 ~/.claude/skills/portrait-editorial-style/scripts/query.py \
  --recommend social_media_portrait
```

### 肖像风格速查

| 风格 | 关键词 | 适用场景 |
|------|--------|---------|
| **35mm Film** | Kodak Portra, natural grain, warm tones | 纪实肖像 |
| **Fujifilm** | Provia 100F, vibrant pastels, soft contrast | 时尚摄影 |
| **CCD Sensor** | Color bleeding, nostalgic mood, analog warmth | 复古风格 |
| **Korean Idol** | Clean retouch, bright highlights, dreamy | 小红书肖像 |
| **Neon** | Rain reflections, urban夜色, convenience store | 氛围感 |
| **Cinematic** | Anamorphic lens, dramatic side lighting | 电影感 |
| **Moody** | Rembrandt lighting, fog atmosphere | 艺术肖像 |

### 时尚编辑风格速查

| 风格 | 关键词 | 适用场景 |
|------|--------|---------|
| **Vogue** | High fashion, dramatic makeup, Helmut Newton | 杂志封面 |
| **Teen Vogue** | Gen Z aesthetic, natural makeup, candid | 社媒内容 |
| **Commercial** | Lifestyle brand, aspirational imagery | 商业广告 |

### 天龙岗位升级

| 岗位 | 版本 | 新增能力 |
|------|------|---------|
| **13-01 设计师** | V10.9→V11.0 | 肖像+时尚编辑库 |
| **35-02 社媒运营** | V13.1→V13.2 | 时尚大片生成 |

### 与现有技能协同

| 现有技能 | 协同方式 |
|---------|---------|
| **professional-photography-prompts** | 补充肖像子集 |
| **ui-social-mockup-generator** | UI截图vs肖像摄影 |
| **gpt-image-2-prompt-library** | 主库引用 |

### 版本信息

- **Version**: 1.0.0
- **Author**: 天龙引擎集成
- **Source**: EvoLinkAI/awesome-gpt-image-2-prompts
- **Last Updated**: 2026-04-28