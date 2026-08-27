---
license: UNKNOWN
triggers: ["ui social mockup generator", "ui-social-mockup-generator"]
---
# ui-social-mockup-generator

## L0: 一句话描述 (≤15字)
UI界面+社媒配图生成器

## L1: 使用场景 (50-100字)
当用户需要生成UI界面截图、产品演示界面、小红书/Instagram/X社媒配图时使用。从精选的Keynote/iPhone/手写笔记本/小红书/Instagram等UI和社媒风格提示词库中检索，适用于产品展示、App Store截图、社媒运营配图。

## L2: 详细文档

### 核心能力

**数据来源**：基于 EvoLinkAI/awesome-gpt-image-2-prompts UI和社媒分类精选

**支持类别**：
- UI Mockup（Keynote/iPhone/手写笔记本/Android）
- Chinese Social Media（小红书/X/微博）
- Western Social Media（Instagram/X-Twitter/YouTube）

### 数据结构

```yaml
# UI/社媒提示词数据格式
category: ui|chinese_social|western_social
style: keynote|iphone|handwritten|xhs|instagram等
prompt: 完整的GPT-Image-2 UI/社媒提示词
engagement:
  likes: int
  retweets: int
  views: int
author: "@Twitter用户名"
```

### 核心命令

```bash
# 查询UI界面
python3 ~/.claude/skills/ui-social-mockup-generator/scripts/query.py \
  --category ui --style keynote --sort engagement --limit 10

# 查询小红书风格
python3 ~/.claude/skills/ui-social-mockup-generator/scripts/query.py \
  --category chinese_social --style xhs

# 获取推荐
python3 ~/.claude/skills/ui-social-mockup-generator/scripts/query.py \
  --recommend product_screenshot
```

### UI风格速查

| 风格 | 关键词 | 适用场景 |
|------|--------|---------|
| **Keynote Snapshot** | Apple keynote, modern design, blur background | 演示文稿 |
| **iPhone Screenshot** | iOS 17, dynamic island, glass morphism | App展示 |
| **Handwritten Notebook** | Fountain pen, cream paper, ink bleeding | 学习笔记 |
| **Chinese Social Media** | 小红书style, calligraphy elements | 社媒配图 |

### 社媒风格速查

| 平台 | 风格 | 适用场景 |
|------|------|---------|
| **小红书** | 文艺风/韩系风/国潮风 | 种草/探店/穿搭 |
| **X/Twitter** | Bold typography, gradient, viral | 社媒帖子 |
| **Instagram** | Aesthetic lifestyle, warm lighting | 生活分享 |
| **微博** | Chinese characters, traditional ink | 品牌传播 |

### 天龙岗位升级

| 岗位 | 版本 | 新增能力 |
|------|------|---------|
| **13-01 设计师** | V10.9→V11.0 | UI截图+社媒配图 |
| **35-02 社媒运营** | V13.0→V13.1 | 社媒配图生成 |

### 与现有技能协同

| 现有技能 | 协同方式 |
|---------|---------|
| **gpt-image-2-prompt-library** | UI/社媒子集补充 |
| **professional-photography-prompts** | 摄影vs UI界面 |
| **xiaohongshu-mcp** | 配图生成→发布闭环 |

### 版本信息

- **Version**: 1.0.0
- **Author**: 天龙引擎集成
- **Source**: EvoLinkAI/awesome-gpt-image-2-prompts
- **Last Updated**: 2026-04-28
