---
description: Chart generation workflow for PPT Master
---

# Chart Generation Workflow

> 自然语言图表生成工作流

## 触发条件

用户要求从自然语言描述生成图表时触发。

## 工作流程

### Step 1: 解析描述

解析自然语言输入：
- 识别图表类型
- 提取数据
- 识别样式要求

### Step 2: 模板匹配

从76个图表模板中选择最合适的。

### Step 3: 数据映射

将用户描述映射到图表数据格式。

### Step 4: SVG生成

使用 chart_nlg.py 生成SVG图表。

### Step 5: 输出

返回生成的SVG文件。

---

**版本**: 1.0
**更新日期**: 2026-08-20
