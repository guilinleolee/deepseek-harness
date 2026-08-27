---
license: UNKNOWN
name: skill-info-graphic-pro
description: |
github_repo: anthropics/claude-code
github_hash: ab3ce06c9ac0a6a0405850e642b80b0bb2c9fb25
last_updated: 2026-04-25
source_type: derived
version: 2.0.0
author: 天龙引擎团队 (基于baoyu-skills)
created: 2026-02-28
updated: 2026-03-13
category: design
triggers: ["info graphic pro", "SKILL: Info-Graphic-Pro V2"]
---

# SKILL: Info-Graphic-Pro V2

专业信息图生成器，支持21种布局×20种风格=420种组合。

## 触发词
- 信息图
- infographic
- 数据可视化
- 图表设计
- 可视化报告
- visual summary
- 高密度信息大图

## 核心能力

### 维度系统
```
21 Layouts × 20 Styles = 420 种风格组合
```

| 维度 | 数量 | 说明 |
|------|------|------|
| Layout | 21种 | 信息布局结构 |
| Style | 20种 | 视觉表现风格 |

## Layout类型 (21种)

| Layout | 描述 | 最佳场景 |
|--------|------|---------|
| `linear-progression` | 线性进程 | 时间线、流程、教程 |
| `binary-comparison` | 二元对比 | A vs B、前后对比、优缺点 |
| `comparison-matrix` | 对比矩阵 | 多因素对比 |
| `hierarchical-layers` | 层级结构 | 金字塔、优先级 |
| `tree-branching` | 树形分支 | 分类、层级 |
| `hub-spoke` | 中心辐射 | 核心概念 + 关联项 |
| `structural-breakdown` | 结构分解 | 分解图、剖面 |
| `bento-grid` | 便当盒网格 | 多主题概览（默认） |
| `iceberg` | 冰山模型 | 表面 vs 隐藏 |
| `bridge` | 桥梁 | 问题-解决方案 |
| `funnel` | 漏斗 | 转化、筛选 |
| `isometric-map` | 等距地图 | 空间关系 |
| `dashboard` | 仪表盘 | 指标、KPI |
| `periodic-table` | 元素表 | 分类集合 |
| `comic-strip` | 漫画条 | 叙事、序列 |
| `story-mountain` | 故事山 | 剧情结构、张力弧 |
| `jigsaw` | 拼图 | 相互关联的部分 |
| `venn-diagram` | 韦恩图 | 重叠概念 |
| `winding-roadmap` | 蜿蜒路线 | 旅程、里程碑 |
| `circular-flow` | 循环流程 | 循环、周期 |
| `dense-modules` | 密集模块 | 高密度模块、数据丰富指南 |
| `gauge` | 仪表盘 | 进度、百分比 |
| `tree` | 树状图 | 组织结构、层级 |
| `matrix-swot` | SWOT矩阵 | 战略分析 |
| `canvas-lean` | 精益画布 | 商业模式 |

## Style风格 (17种)

| Style | 描述 | 配色特点 |
|-------|------|---------|
| `minimal` | 极简 | 黑白灰，单色强调 |
| `flat` | 扁平 | 纯色，无渐变阴影 |
| `material` | Material Design | Google材料设计 |
| `neumorphic` | 新拟态 | 柔和阴影，立体感 |
| `glassmorphism` | 玻璃拟态 | 磨砂玻璃，模糊背景 |
| `brutalism` | 粗野主义 | 高对比，原始粗犷 |
| `gradient` | 渐变 | 流动渐变 |
| `dark` | 暗色 | 深色背景，霓虹强调 |
| `pastel` | 粉彩 | 柔和马卡龙色 |
| `vibrant` | 鲜艳 | 高饱和度，活力 |
| `monochrome` | 单色 | 同色系深浅 |
| `duotone` | 双色 | 两种颜色组合 |
| `retro` | 复古 | 复古配色，怀旧感 |
| `cyberpunk` | 赛博朋克 | 霓虹粉绿，暗底 |
| `swiss` | 瑞士风格 | 国际主义设计 |
| `bauhaus` | 包豪斯 | 几何抽象 |
| `art-deco` | 装饰艺术 | 金色黑色，奢华 |

## 使用示例

### 指定单维度
```bash
/info-graphic-pro "产品发布流程" --layout timeline-linear

/info-graphic-pro "市场分析报告" --style vibrant
```

### 指定多维度
```bash
/info-graphic-pro "SWOT分析" --layout matrix-swot --style swiss
```

### 预设组合
```bash
# 商务预设
/info-graphic-pro "季度报告" --preset business

# 科技预设
/info-graphic-pro "技术架构" --preset tech

# 教育预设
/info-graphic-pro "知识点梳理" --preset education
```

## EXTEND.md 自定义

在 `~/.claude/skills/info-graphic-pro/EXTEND.md` 中添加：

```markdown
## Custom Layouts

### my-custom-layout
- description: 我的自定义布局
- structure: 网格/列表/其他
- best-for: 特定场景

## Custom Styles

### my-brand-style
- description: 品牌风格
- colors: #primary, #secondary
- best-for: 品牌内容

## Custom Presets

### my-brand-preset
- layout: my-custom-layout
- style: my-brand-style
```

## 自动推荐逻辑

| 内容类型 | 推荐Layout | 推荐Style |
|---------|-----------|----------|
| 流程、步骤 | flowchart-linear, timeline-linear | minimal, flat |
| 对比分析 | comparison-side, comparison-table | swiss, brutalism |
| 战略分析 | matrix-swot, pyramid | material, bauhaus |
| 项目进度 | timeline-vertical, gauge | gradient, vibrant |
| 知识梳理 | mind-map, tree | pastel, minimal |
| 数据报告 | grid-2x2, radar | material, flat |
| 产品介绍 | list-horizontal, cycle | neumorphic, glassmorphism |

## 集成功能

### 多后端AI路由器
自动选择最优AI后端（OpenAI/Google/DashScope）生成图像。

### EXTEND.md机制
支持项目级和用户级两级自定义配置。

### Chrome CDP支持
可用于网页抓取和自动化发布。

## 文件结构

```
info-graphic-pro/
├── SKILL.md                 # 技能定义
├── EXTEND.md                # 默认配置
├── dimensional-system.md    # 维度系统详细说明
├── layouts/                 # 布局系统
│   ├── layout-list-vertical.md
│   ├── layout-grid-2x2.md
│   └── ...
└── styles/                  # 风格系统
    ├── style-minimal.md
    ├── style-flat.md
    └── ...
```

## 最佳实践

1. **内容优先**：先分析内容结构，选择合适的Layout
2. **风格匹配**：根据受众和场景选择Style
3. **预设优先**：使用preset快速开始
4. **自定义扩展**：通过EXTEND.md添加品牌风格

---

🤖 Generated with [Claude Code](https://github.com/anthropics/claude-code)
