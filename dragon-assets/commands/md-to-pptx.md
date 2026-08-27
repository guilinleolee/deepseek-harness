---
name: md-to-pptx
description: Markdown转PPT - 快速将Markdown文件转换为专业演示文稿
invokable: true
argument-hint: <markdown文件> [选项]
allowed-tools: Read, Glob, Grep, Bash, Write, Edit
model: opus
---

# Markdown 转 PPT

> 将 Markdown 文件快速转换为专业 PowerPoint 演示文稿

## 功能特性

### 核心能力
- 📄 **Markdown解析** - 支持标准MD语法（标题、列表、代码块、表格、链接）
- 🎨 **智能布局** - 根据内容自动选择最佳布局
- 📊 **图表支持** - 识别数据并生成图表占位符
- 🔢 **幻灯片规划** - 自动生成演讲稿拆分
- 🎯 **多种风格** - 支持 corporate/minimal/academic/tech 等风格

### 支持的 Markdown 元素

| 元素 | 处理方式 |
|------|----------|
| `# 标题` | 第一级标题 = 封面标题 |
| `## 二级标题` | 幻灯片标题 |
| `- 无序列表` | 要点列表 |
| `1. 有序列表` | 编号列表 |
| `> 引用` | 引用块/callout |
| ```代码块``` | 代码高亮 |
| `\| 表格 \|` | 表格元素 |
| `---` | 幻灯片分隔 |
| `![图片](url)` | 图片引用 |

## 使用方式

```bash
/md-to-pptx content.md
/md-to-pptx content.md --style corporate
/md-to-pptx content.md --output ./slides.pptx
/md-to-pptx content.md --title "演示标题"
```

## 参数说明

### 必需参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `<markdown文件>` | Markdown文件路径 | `content.md` |

### 可选参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--style` | `corporate` | 演示风格 |
| `--output` | `auto` | 输出文件路径 |
| `--title` | 源文件名 | 演示文稿标题 |
| `--format` | `ppt169` | 幻灯片比例 |
| `--no-image` | `false` | 跳过图片处理 |
| `--split-mode` | `auto` | 演讲稿分割模式 |

## 风格选项

| 风格 | 特点 | 适用场景 |
|------|------|----------|
| `corporate` | 简洁专业、蓝色主调 | 企业汇报、商务演示 |
| `minimal` | 极简风格、大量留白 | 高管演讲、简洁报告 |
| `academic` | 学术规范、清晰层次 | 论文答辩、学术分享 |
| `tech` | 科技感、代码友好 | 技术分享、开发者会议 |
| `dark` | 深色背景、高对比 | 夜间演示、影视制作 |
| `creative` | 色彩丰富、创意版式 | 创意展示、营销提案 |

## 工作流程

```
输入 Markdown
    ↓
解析内容结构
    ↓
规划幻灯片
    ↓
应用样式模板
    ↓
生成 SVG 页面
    ↓
导出 PPTX 文件
```

## 输出示例

### 输入 `content.md`
```markdown
# 产品发布会

## 核心功能
- AI智能助手
- 实时协作
- 数据可视化

## 技术架构
```python
def main():
    print("Hello")
```
```

### 输出 `slides.pptx`
```
📄 幻灯片结构：

Slide 1: 封面
  标题: 产品发布会
  副标题: [自动生成日期]

Slide 2: 核心功能
  要点: AI智能助手
  要点: 实时协作
  要点: 数据可视化

Slide 3: 技术架构
  代码块: Python示例
```

## 使用示例

### 示例1：基础转换
```bash
/md-to-pptx readme.md
```
**输出**：`readme.pptx`

### 示例2：指定风格
```bash
/md-to-pptx report.md --style academic
```
**输出**：`report_academic.pptx`

### 示例3：自定义输出
```bash
/md-to-pptx content.md --output ./presentation.pptx --title "2024年度报告"
```

### 示例4：批量转换
```bash
# 转换目录下所有MD文件
for f in *.md; do /md-to-pptx "$f"; done
```

## 高级用法

### 幻灯片分隔符
使用 `---` 手动分隔幻灯片：
```markdown
# 第一页内容

---

# 第二页内容
```

### 幻灯片元数据
```markdown
<!-- slide:cover -->
# 封面标题

<!-- slide:notes -->
这是演讲备注...

<!-- slide:transition:fade -->
# 淡入效果
```

### 图表数据
```markdown
```chart
type: bar
title: 季度销售额
data: |
  Q1 100
  Q2 150
  Q3 200
  Q4 250
```
```

## 与 ppt-master 的关系

- **md-to-pptx**: 快速通道，适合简单内容
- **ppt-master**: 完整流程，适合复杂设计

**建议**：
- 简单文档 → 使用 `/md-to-pptx`
- 复杂设计 → 使用 `/ppt-master`

## 常见问题

### Q: 如何指定多个标题？
A: 使用 `---` 分隔符或一级标题自动分割

### Q: 代码块如何处理？
A: 代码块会保留原始格式，可在演示时手动调整

### Q: 支持哪些图片格式？
A: 支持 PNG、JPG、SVG，GIF 转为静态

### Q: 如何添加演讲备注？
A: 使用 `<!-- slide:notes -->` 语法

## 相关命令

- `/ppt-master` - 完整PPT生成流程
- `/ppt-templates` - 列出可用模板
- `/ppt-import-template` - 导入外部模板

---

**版本**: V1.0
**维护者**: 00演示架构师
**最后更新**: 2026-08-20
