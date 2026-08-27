---
name: basic
kind: layout
summary: Basic presentation template with clean design
canvas_format: ppt169
page_count: 1
page_types: [content]
---

# Basic Template

> 基础演示模板，简洁专业的设计风格

## 设计规范

### 颜色系统

| 角色 | 颜色 | 用途 |
|------|------|------|
| Primary | #1E3A5F | 主色调、标题 |
| Secondary | #2D5A87 | 次要元素 |
| Accent | #3182CE | 高亮、强调 |
| Background | #FFFFFF | 背景色 |
| Text | #1A202C | 正文颜色 |
| Muted | #718096 | 次要文字 |

### 字体系统

| 角色 | 字体 | 字号 |
|------|------|------|
| 标题 | Microsoft YaHei | 44pt |
| 副标题 | Microsoft YaHei | 32pt |
| 正文 | Microsoft YaHei | 24pt |
| 代码 | Consolas | 16pt |

### 布局规范

- 页面边距: 60px
- 标题区域: 顶部 60px
- 内容区域: 居中，垂直居中
- 列表缩进: 40px

### 动画效果

- 页面转场: 淡入淡出
- 元素入场: 无
- 切换时长: 0.5s

## 页面结构

```
┌─────────────────────────────────────┐
│                                     │
│           页面标题                    │
│                                     │
│  ┌─────────────────────────────┐   │
│  │                             │   │
│  │         内容区域              │   │
│  │                             │   │
│  └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

## 使用说明

1. 标题自动提取 Markdown 的 `#` 标题
2. 内容自动提取列表、段落
3. 代码块自动高亮
4. 图片自动居中显示

## 适用场景

- 快速文档转换
- 临时演示需求
- 内容预览
