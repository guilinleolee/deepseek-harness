---
name: ppt-templates
description: PPT模板索引 - 列出所有可用PPT模板、品牌预设和图表
invokable: true
argument-hint: [选项]
allowed-tools: Read, Glob, Grep, Bash
---

# PPT模板索引

> 一键列出天龙引擎中所有可用的PPT模板、品牌预设和图表

## 功能概述

`/ppt-templates` 命令可以快速查看所有PPT相关资源：

| 资源类型 | 说明 | 数量 |
|----------|------|------|
| 品牌预设 | 企业品牌身份标识（颜色/字体/Logo） | 4+ |
| 布局模板 | 通用页面结构模板 | 7+ |
| 图表模板 | 数据可视化模板 | 76+ |

## 使用方式

### 基础用法

```bash
# 列出所有模板
/ppt-templates

# 列出所有模板（JSON格式）
/ppt-templates --format json

# 列出所有模板（详细格式）
/ppt-templates --verbose
```

### 按类型筛选

```bash
# 仅列出品牌预设
/ppt-templates --type brand

# 仅列出布局模板
/ppt-templates --type layout

# 仅列出图表模板
/ppt-templates --type chart
```

### 搜索功能

```bash
# 关键词搜索
/ppt-templates --search "学术"

/# 搜索并显示详情
/ppt-templates --search "企业" --verbose
```

### 组合使用

```bash
# 在品牌中搜索
/ppt-templates --type brand --search "技术"

/# 在图表中搜索
/ppt-templates --type chart --search "柱状图"
```

## 输出格式

### 默认格式（终端友好）

```
📁 品牌预设 (4)
/ppt-templates --type brand
├── anthropic
│   └── AI/LLM技术演示 | #D97757
├── google
│   └── 多产品企业演示 | #4285F4
├── 中国电建
│   └── 工程报告 | #00418D
└── 中汽研
    └── 产品认证 | #004098

📁 布局模板 (7)
/ppt-templates --type layout
├── academic_defense    5页  学术答辩
├── ai_ops             6页  AI运维架构
├── government_blue    5页  政府蓝调
├── government_red     5页  政府红调
├── medical_university 5页  医学学术
├── pixel_retro        5页  像素复古
└── psychology_attachment 5页 心理治疗

📊 图表模板 (76)
/ppt-templates --type chart
├── 图表类 (35)
│   ├── area_chart              面积图
│   ├── bar_chart               条形图
│   ├── column_chart            柱状图
│   ├── line_chart              折线图
│   ├── pie_chart               饼图
│   └── ...
├── 信息图类 (25)
│   ├── process_flow            流程图
│   ├── pyramid_chart          金字塔图
│   └── ...
├── 框架类 (10)
│   ├── swot_template           SWOT分析
│   ├── bcg_matrix             BCG矩阵
│   └── ...
└── 图示类 (6)
    ├── icon_grid               图标网格
    └── ...
```

### JSON格式

```bash
/ppt-templates --format json
```

```json
{
  "total": 87,
  "brands": [
    {
      "id": "anthropic",
      "summary": "AI/LLM技术演示",
      "primary_color": "#D97757",
      "path": "templates/brands/anthropic"
    }
  ],
  "layouts": [
    {
      "id": "academic_defense",
      "summary": "学术答辩",
      "page_count": 5,
      "page_types": ["cover", "toc", "chapter", "content", "ending"],
      "path": "templates/layouts/academic_defense"
    }
  ],
  "charts": [
    {
      "id": "column_chart",
      "summary": "柱状图",
      "category": "图表类",
      "path": "templates/charts/column_chart.svg"
    }
  ]
}
```

## 模板详情

### 品牌预设

| ID | 名称 | 主色 | 适用场景 |
|----|------|------|----------|
| anthropic | Anthropic | #D97757 | AI/LLM技术演示 |
| google | Google | #4285F4 | 多产品企业演示 |
| 中国电建 | 中国电建 | #00418D | 工程报告 |
| 中汽研 | 中汽研 | #004098 | 产品认证 |

### 布局模板

| ID | 名称 | 页数 | 适用场景 |
|----|------|------|----------|
| academic_defense | 学术答辩 | 5 | 论文答辩、研究汇报 |
| ai_ops | AI运维架构 | 6 | 电信AI运维、系统架构 |
| government_blue | 政府蓝调 | 5 | 政府汇报、政策解读 |
| government_red | 政府红调 | 5 | 政府会议、项目介绍 |
| medical_university | 医学学术 | 5 | 医学报告、病例讨论 |
| pixel_retro | 像素复古 | 5 | 技术分享、极客风格 |
| psychology_attachment | 心理治疗 | 5 | 心理咨询、培训讲座 |

### 图表模板分类

#### 图表类 (35)

| 类型 | 模板 |
|------|------|
| 时间序列 | area_chart, line_chart, stacked_area_chart |
| 比较类 | column_chart, bar_chart, horizontal_bar |
| 占比类 | pie_chart, donut_chart, treemap |
| 分布类 | scatter_chart, bubble_chart, histogram |
| 流程类 | funnel_chart, gantt_chart, timeline |

#### 信息图类 (25)

| 类型 | 模板 |
|------|------|
| 流程 | process_flow, numbered_steps |
| 循环 | circular_stages, hub_spoke |
| 层级 | pyramid_chart, top_down_tree |
| 矩阵 | quadrant_bullets, matrix_2x2 |

#### 框架类 (10)

| 类型 | 模板 |
|------|------|
| 战略 | swot_template, bcg_matrix, pest_analysis |
| 对比 | comparison_table, pros_cons_chart |

#### 图示类 (6)

| 类型 | 模板 |
|------|------|
| 列表 | icon_grid, vertical_list |
| 表格 | basic_table, consulting_table |
| 其他 | mind_map, journey_map |

## 使用技巧

### 快速查找

1. **按用途搜索**: `/ppt-templates --search "学术"`
2. **按颜色搜索**: 在品牌中搜索特定颜色
3. **按页数筛选**: 查找指定页数的布局

### 选择模板

找到需要的模板后，使用以下命令：

```bash
# 在 ppt-master 中使用模板
/ppt-master content.md --template-path templates/layouts/academic_defense

# 在 md-to-pptx 中指定风格
/md-to-pptx content.md --style corporate
```

### 模板路径

| 类型 | 路径格式 |
|------|----------|
| 品牌 | `templates/brands/<id>/` |
| 布局 | `templates/layouts/<id>/` |
| 图表 | `templates/charts/<id>.svg` |

## 常见问题

### Q: 如何查看模板预览？

A: 模板预览可以在 ppt-master 的 live preview 中查看

### Q: 可以自定义模板吗？

A: 可以，使用 `/ppt-import-template` 导入自定义模板

### Q: 如何获取模板的详细信息？

A: 使用 `--verbose` 参数显示详细信息

### Q: 图表模板如何使用？

A: 在 design_spec.md §VII 中引用图表模板

## 相关命令

- `/md-to-pptx` - Markdown快速转PPT
- `/ppt-master` - 完整PPT生成流程
- `/ppt-import-template` - 导入外部模板

---

**版本**: V1.0
**维护者**: 00演示架构师
**最后更新**: 2026-08-20
