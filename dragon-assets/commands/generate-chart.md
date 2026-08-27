---
name: generate-chart
description: 图表智能生成 - 自然语言描述自动生成专业图表
invokable: true
argument-hint: <图表描述> [选项]
allowed-tools: Read, Glob, Grep, Bash, Write
---

# 图表智能生成命令

> 通过自然语言描述，自动生成专业的SVG图表

## 功能概述

| 功能 | 说明 |
|------|------|
| 自然语言解析 | 理解图表类型、数据、样式要求 |
| 模板匹配 | 从76个图表模板中选择最合适的 |
| 数据映射 | 将描述映射到图表数据格式 |
| SVG生成 | 生成高质量SVG图表 |

## 使用方式

### 基础用法

```bash
/generate-chart "显示2024年Q1-Q4销售额对比，柱状图"
/generate-chart "展示用户增长趋势，折线图"
```

### 完整选项

```bash
/generate-chart "季度销售额柱状图" \
  --type bar \
  --title "2024年季度销售额" \
  --data "Q1:100 Q2:150 Q3:200 Q4:250" \
  --output ./chart.svg \
  --style professional
```

## 参数说明

### 必需参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `<图表描述>` | 自然语言描述 | "显示销售数据的柱状图" |

### 可选参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--type` | auto | 图表类型 |
| `--title` | "" | 图表标题 |
| `--data` | "" | 数据内容 |
| `--output` | auto | 输出文件 |
| `--style` | corporate | 图表风格 |
| `--colors` | "" | 自定义颜色 |

## 支持的图表类型

### 图表类

| 类型 | 英文 | 说明 |
|------|------|------|
| 柱状图 | bar, column | 分类数据对比 |
| 条形图 | horizontal_bar | 横向对比 |
| 折线图 | line | 趋势变化 |
| 面积图 | area | 累积趋势 |
| 饼图 | pie | 占比展示 |
| 环形图 | donut | 占比展示（空心） |
| 散点图 | scatter | 分布关系 |
| 气泡图 | bubble | 三维数据 |
| 漏斗图 | funnel | 流程转化 |
| 甘特图 | gantt | 项目进度 |
| 旭日图 | sunburst | 多级占比 |

### 信息图类

| 类型 | 英文 | 说明 |
|------|------|------|
| 流程图 | flow, process | 步骤流程 |
| 金字塔 | pyramid | 层级结构 |
| 思维导图 | mind_map | 脑图结构 |
| 时间线 | timeline | 时间序列 |

### 框架类

| 类型 | 英文 | 说明 |
|------|------|------|
| SWOT分析 | swot | 战略分析 |
| BCG矩阵 | bcg | 投资组合 |
| 对比表 | comparison | 选项对比 |

## 示例

### 示例1: 柱状图

```bash
/generate-chart "显示各产品销售额对比" \
  --type column \
  --title "产品销售额" \
  --data "产品A:100|产品B:150|产品C:200|产品D:120"
```

### 示例2: 折线图

```bash
/generate-chart "展示用户增长趋势" \
  --type line \
  --title "月活用户趋势" \
  --data "1月:10000|2月:12000|3月:15000|4月:18000|5月:22000"
```

### 示例3: 饼图

```bash
/generate-chart "市场份额占比" \
  --type pie \
  --title "市场份额" \
  --data "我们:35%|竞品A:25%|竞品B:20%|其他:20%"
```

### 示例4: SWOT分析

```bash
/generate-chart "SWOT分析" \
  --type swot \
  --title "公司SWOT分析" \
  --data "S:技术优势|品牌影响力 W:资金不足|人才流失 O:市场扩大|政策支持 T:竞争加剧|技术变革"
```

## 自然语言解析

系统会自动解析自然语言中的关键信息：

| 关键词 | 解析结果 |
|--------|----------|
| "对比" | → 柱状图/条形图 |
| "趋势" | → 折线图/面积图 |
| "占比"/"份额" | → 饼图/环形图 |
| "增长"/"下降" | → 折线图 |
| "流程"/"步骤" | → 流程图 |
| "层次"/"分级" | → 金字塔图 |

## 数据格式

### 简单格式

```
# 键值对
key:value|key:value|key:value

# 示例
Q1:100|Q2:150|Q3:200|Q4:250
```

### 带名称格式

```
# 系列数据
series1:10,20,30,40|series2:15,25,35,45
categories:Q1,Q2,Q3,Q4
```

### JSON格式

```json
{
  "type": "bar",
  "title": "季度销售额",
  "categories": ["Q1", "Q2", "Q3", "Q4"],
  "series": [
    {"name": "销售额", "values": [100, 150, 200, 250]}
  ]
}
```

## 输出格式

### SVG输出

```bash
# 生成SVG
/generate-chart "销售数据" --output ./chart.svg
```

### PNG输出

```bash
# 生成PNG（需要转换）
/generate-chart "销售数据" --output ./chart.png
```

## 样式选项

| 样式 | 说明 |
|------|------|
| corporate | 企业蓝，专业严谨 |
| modern | 现代感，渐变色彩 |
| minimal | 极简风格，少即是多 |
| dark | 暗色背景，高对比 |
| gradient | 渐变填充，视觉丰富 |

## 常见问题

### Q: 如何指定多个数据系列？

A: 使用 `series1:10,20,30|series2:15,25,35` 格式

### Q: 支持中文标签吗？

A: 支持，系统自动处理UTF-8编码

### Q: 如何自定义颜色？

A: 使用 `--colors` 参数：`#FF5733,#3498DB,#2ECC71`

## 相关命令

- `/ppt-master` - 完整PPT生成
- `/ppt-templates` - 查看图表模板

---

**版本**: V1.0
**维护者**: 00演示架构师
**最后更新**: 2026-08-20
