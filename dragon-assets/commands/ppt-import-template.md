---
name: ppt-import-template
description: PPT模板导入 - 从外部PPT/PDF提取品牌元素并导入到模板库
invokable: true
argument-hint: <源文件> [选项]
allowed-tools: Read, Glob, Grep, Bash, Write
---

# PPT模板导入命令

> 从外部PPT、PDF或设计参考中提取品牌元素，导入到天龙引擎模板库

## 功能概述

| 功能 | 说明 |
|------|------|
| 品牌色提取 | 自动提取主色、辅色、背景色 |
| 字体识别 | 识别并记录使用的字体 |
| Logo提取 | 提取PPT中的Logo元素 |
| 样式规范 | 生成完整的品牌设计规范 |
| 模板验证 | 检查模板完整性和可用性 |

## 使用方式

### 基础用法

```bash
/ppt-import-template ./my-presentation.pptx
/ppt-import-template ./design.pdf --name my-brand
```

### 完整选项

```bash
/ppt-import-template input.pptx \
  --name my-brand \           # 模板名称（必需）
  --type brand \              # 模板类型：brand/layout/deck
  --output ./templates/       # 输出目录
  --validate                  # 验证模板完整性
```

## 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `<源文件>` | - | PPTX/PDF/图片文件路径 |
| `--name` | auto | 模板名称 |
| `--type` | auto | 模板类型 |
| `--output` | templates/ | 输出目录 |
| `--validate` | false | 导入后验证 |
| `--force` | false | 覆盖已存在模板 |

## 提取的元素

### 颜色提取

```json
{
  "primary_color": "#1E3A5F",
  "secondary_color": "#2D5A87",
  "accent_color": "#3182CE",
  "background_color": "#FFFFFF",
  "text_colors": ["#1A202C", "#4A5568", "#718096"],
  "extraction_confidence": 0.92
}
```

### 字体识别

```json
{
  "fonts": [
    {"name": "Microsoft YaHei", "usage": "标题", "confidence": 0.95},
    {"name": "Arial", "usage": "正文", "confidence": 0.88}
  ],
  "extraction_confidence": 0.90
}
```

### Logo处理

```json
{
  "logos": [
    {
      "file": "logo.png",
      "position": "左上角",
      "usage": "主要Logo"
    }
  ]
}
```

## 工作流程

```
输入文件
    ↓
解析源格式
    ↓
颜色提取（主色/辅色/强调色）
    ↓
字体识别
    ↓
Logo提取
    ↓
样式规范生成
    ↓
模板验证
    ↓
输出到模板库
```

## 输出结构

```
templates/brands/<name>/
├── design_spec.md         # 品牌设计规范
├── colors.json           # 颜色配置
├── fonts.json           # 字体配置
└── assets/
    ├── logo.svg         # Logo文件
    └── patterns/        # 背景图案
```

## 示例

### 示例1: 从PPT导入品牌

```bash
/ppt-import-template ./company-deck.pptx --name company-brand
```

**输出**:
```
✅ 品牌提取完成！
📁 输出目录: templates/brands/company-brand/

提取结果:
├── 主色: #1E3A5F (置信度: 92%)
├── 辅色: #2D5A87
├── 强调色: #3182CE
├── 字体: Microsoft YaHei, Arial
└── Logo: 已提取 (2个)
```

### 示例2: 从PDF导入

```bash
/ppt-import-template ./brand-guide.pdf --name new-brand --validate
```

### 示例3: 从图片导入

```bash
/ppt-import-template ./brand-colors.png --name image-brand
```

## 验证清单

导入完成后自动验证：

| 检查项 | 说明 |
|--------|------|
| 颜色完整性 | 主色、辅色、背景色是否齐全 |
| 字体有效性 | 字体名称是否有效 |
| Logo存在性 | Logo文件是否可读 |
| 规范完整性 | design_spec.md是否完整 |
| 格式正确性 | JSON格式是否正确 |

## 冲突处理

### 同名模板

| 选项 | 行为 |
|------|------|
| 默认 | 提示冲突，要求重命名 |
| `--force` | 覆盖已有模板 |
| `--rename` | 自动添加后缀 |

### 颜色相似

检测到与现有模板颜色高度相似时：
- 提示相似度百分比
- 建议保留现有或创建变体

## 常见问题

### Q: 支持哪些格式？

A: PPTX、PDF、图片（PNG/JPG/SVG）

### Q: 提取失败怎么办？

A: 手动编辑生成的 design_spec.md 文件

### Q: 如何验证提取结果？

A: 使用 `--validate` 参数自动验证

## 相关命令

- `/ppt-templates` - 查看所有模板
- `/ppt-master` - 使用模板生成PPT

---

**版本**: V1.0
**维护者**: 00演示架构师
**最后更新**: 2026-08-20
