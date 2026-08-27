---
description: Template import workflow for PPT Master
---

# Import Template Workflow

> 模板导入工作流

## 触发条件

用户要求从外部文件导入模板时触发。

## 工作流程

### Step 1: 文件验证

检查源文件格式：
- PPTX
- PDF
- 图片（PNG/JPG/SVG）

### Step 2: 提取元素

使用 template_importer.py 提取：
- 颜色（主色/辅色/强调色）
- 字体（标题字体/正文字体）
- Logo
- 样式规范

### Step 3: 生成模板

创建模板文件：
- design_spec.md
- colors.json
- fonts.json
- assets/

### Step 4: 验证

验证模板完整性。

### Step 5: 导入完成

将模板添加到模板库。

---

**版本**: 1.0
**更新日期**: 2026-08-20
