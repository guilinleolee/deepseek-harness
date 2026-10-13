---
github_repo: anthropics/skills
github_path: skills/theme-factory
source_type: official
license: Complete terms in LICENSE.txt
triggers: ["theme-factory", "主题工厂", "主题生成", "PPT主题"]
---

# Theme Factory - 主题工厂

> **来源**: [Anthropic官方技能](https://github.com/anthropics/skills/tree/main/skills/theme-factory)
> **版本**: V1.0 | **集成**: 天龙引擎 V9.1
> **说明**: 专业配色和字体主题集合，可应用于幻灯片、文档、HTML页面等

## L0: 一句话描述

专业配色和字体主题工具箱，10+预设主题+自定义主题生成

## L1: 10个预设主题

| # | 主题名称 | 风格描述 | 适用场景 |
|---|---------|---------|---------|
| 1 | **Ocean Depths** | 专业沉静的海事风格 | 企业报告、海洋相关 |
| 2 | **Sunset Boulevard** | 温暖活力的日落色彩 | 创意展示、生活方式 |
| 3 | **Forest Canopy** | 自然接地的大地色调 | 环保、自然产品 |
| 4 | **Modern Minimalist** | 干净当代的灰度风格 | 科技、SaaS产品 |
| 5 | **Golden Hour** | 丰富温暖的秋日调色板 | 高端品牌、奢华服务 |
| 6 | **Arctic Frost** | 清凉清爽的冬日灵感 | 冰雪、高科技 |
| 7 | **Desert Rose** | 柔和精致的玫瑰尘色调 | 美容、时尚 |
| 8 | **Tech Innovation** | 大胆现代的科技美学 | 科技产品、创新创业 |
| 9 | **Botanical Garden** | 新鲜有机的花园色彩 | 健康、有机产品 |
| 10 | **Midnight Galaxy** | 戏剧性的宇宙深色调 | 太空、神秘、高端 |

## L2: 使用流程

```
1. 展示主题展示: 显示 theme-showcase.pdf
2. 询问选择: 询问用户选择哪个主题
3. 等待确认: 获取明确的主题选择
4. 应用主题: 将选定主题的颜色和字体应用到作品
```

### 预览主题

```bash
# 打开主题展示PDF
open theme-showcase.pdf   # macOS
xdg-open theme-showcase.pdf  # Linux
start theme-showcase.pdf   # Windows
```

## L3: 自定义主题生成

当预设主题都不合适时，可以生成自定义主题：

```markdown
# 自定义主题流程

1. 收集输入:
   - 品牌/产品描述
   - 目标受众
   - 使用场景
   - 情感调性

2. 生成主题:
   - 命名（描述性名称）
   - 配色方案（5-7色）
   - 字体配对（标题+正文）
   - 视觉标识

3. 展示并验证
4. 应用到作品
```

## L4: 天龙岗位映射

| 天龙岗位 | 匹配度 | 核心收益 |
|----------|--------|---------|
| **13-01 设计师** | ⭐⭐⭐⭐⭐ | 快速主题应用 |
| **35-内容运营** | ⭐⭐⭐⭐ | PPT/文档统一风格 |
| **03 构建师** | ⭐⭐⭐ | 演示文稿风格 |

## L5: 与天龙技能协同

| 天龙技能 | 协同方式 |
|---------|---------|
| `ppt-master` | 主题应用到PPT |
| `frontend-design` | 前端配色方案 |
| `impeccable` | `/colorize` 色彩策略 |
| `ui-ux-pro-max` | 192套行业配色 |

### 协同流程

```bash
# 方案1: 主题工厂 + PPT
/theme-factory select  # 选择主题
/ppt-master apply-theme  # 应用到PPT

# 方案2: ui-ux-pro-max + theme-factory
ui-ux-pro-max --design-system  # 获取行业配色
theme-factory --create-custom  # 创建自定义主题

# 方案3: impeccable + theme-factory
/impeccable /colorize  # 战略配色
/theme-factory apply  # 应用主题
```

## L6: 文件结构

```
theme-factory/
├── SKILL.md              # 本文件
├── theme-showcase.pdf    # 10主题可视化展示
├── theme-gallery.html    # 在线主题画廊
├── themes/              # 主题定义文件
│   ├── ocean-depths.json
│   ├── sunset-boulevard.json
│   └── ...
└── LICENSE.txt
```

## L7: 主题JSON结构

```json
{
  "name": "Ocean Depths",
  "description": "专业沉静的海事风格",
  "colors": {
    "primary": "#1e3a5f",
    "secondary": "#2d5a87",
    "accent": "#4a90a4",
    "background": "#f5f7fa",
    "text": "#2c3e50"
  },
  "fonts": {
    "heading": "Playfair Display",
    "body": "Source Sans Pro"
  }
}
```

## 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-08-20 | 天龙引擎V9.1初始集成，Anthropic官方技能 |
