# DeerFlow Chart Visualization Skill

## Overview

图表可视化技能 - 26种图表类型智能生成。

## Chart Selection

| 数据类型 | 推荐图表 |
|---------|---------|
| 时间序列 | line, area |
| 对比 | bar, column |
| 占比 | pie, treemap |
| 关系 | scatter, sankey |
| 地图 | district, pin, path |
| 层级 | org chart, mind map |
| 专业 | radar, funnel, boxplot, word cloud |

## Workflow

### Step 1: Chart Selection

分析数据特征选择图表类型：
- 时间序列 → 折线/面积图
- 对比 → 柱状图
- 占比 → 饼图/树图
- 关系 → 散点图

### Step 2: Parameter Extraction

读取references/目录下的参考文件

### Step 3: Chart Generation

```bash
node scripts/generate.js '<payload_json>'
```

### Payload Format

```json
{
  "tool": "generate_chart_type_name",
  "args": {
    "data": [...],
    "title": "Chart Title",
    "theme": "theme-name",
    "style": {
      "colors": ["#color1", "#color2"],
      "fontSize": 14,
      "width": 800,
      "height": 600
    }
  }
}
```

## Supported Chart Types

| 类型 | 名称 | 用途 |
|------|------|------|
| line | 折线图 | 趋势、随时间变化 |
| area | 面积图 | 累积、堆叠趋势 |
| bar | 条形图 | 横向对比 |
| column | 柱状图 | 纵向对比 |
| pie | 饼图 | 占比展示 |
| donut | 环形图 | 占比+中心数据 |
| scatter | 散点图 | 相关性、分布 |
| bubble | 气泡图 | 三维数据 |
| radar | 雷达图 | 多维度对比 |
| funnel | 漏斗图 | 转化流程 |
| gauge | 仪表盘 | KPI达成 |
| heatmap | 热力图 | 密度、相关性 |
| treemap | 树图 | 层级占比 |
| sankey | 桑基图 | 流向、转化 |
| wordcloud | 词云 | 文本频率 |
| map | 地图 | 地理分布 |

## Chart Generation Example

### Line Chart
```json
{
  "tool": "generate_line_chart",
  "args": {
    "data": [
      {"month": "Jan", "value": 100},
      {"month": "Feb", "value": 150},
      {"month": "Mar", "value": 130}
    ],
    "title": "Monthly Revenue",
    "xField": "month",
    "yField": "value",
    "theme": "professional"
  }
}
```

### Bar Chart
```json
{
  "tool": "generate_bar_chart",
  "args": {
    "data": [
      {"category": "A", "value": 45},
      {"category": "B", "value": 32},
      {"category": "C", "value": 28}
    ],
    "title": "Sales by Category",
    "xField": "category",
    "yField": "value",
    "theme": "professional"
  }
}
```

## Color Themes

| Theme | 适用场景 |
|-------|---------|
| professional | 商业报告、数据分析 |
| vibrant | 演示、演示文稿 |
| pastel | 女性用户、柔和风格 |
| dark | 深色背景、现代化 |

## Usage in Research Report

```markdown
![Monthly Revenue Trend](charts/monthly-revenue.png)

| Metric | Value |
|--------|-------|
| January | 100 |
| February | 150 |
| March | 130 |

综合分析：...
```
