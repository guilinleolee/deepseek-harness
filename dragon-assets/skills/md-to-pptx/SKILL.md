---
name: md-to-pptx
description: >
  Markdown转PPT技能 - 将Markdown文件快速转换为专业演示文稿。
  支持标准MD语法、智能布局选择、多风格模板。
  使用场景：快速文档转换、演示文稿生成、内容迁移。
---

# MD-to-PPTX Skill

> 将 Markdown 文件快速转换为专业 PowerPoint 演示文稿

## 核心功能

1. **Markdown 解析**
   - 标题层级识别
   - 列表结构解析
   - 代码块提取
   - 表格转换
   - 图片引用处理

2. **幻灯片规划**
   - 自动内容分割
   - 演讲稿生成
   - 备注添加

3. **模板应用**
   - 风格选择
   - 布局映射
   - 配色应用

4. **PPTX 导出**
   - SVG 生成
   - 格式转换
   - 输出优化

## 工作流程

```python
# 伪代码流程
markdown_content = read_file(input_file)
parsed = parse_markdown(markdown_content)
slides = plan_slides(parsed)
styled = apply_template(slides, style)
svg_pages = render_svg(styled)
output_pptx = export_pptx(svg_pages)
```

## 目录结构

```
md-to-pptx/
├── SKILL.md                    # 本文件
├── scripts/
│   └── md2pptx.py            # 核心脚本
├── references/
│   ├── layout-guide.md        # 布局指南
│   └── quick-start.md         # 快速入门
└── templates/
    └── basic/
        └── design_spec.md     # 默认模板
```

## 脚本参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--input` | str | (必需) | Markdown文件路径 |
| `--output` | str | auto | 输出PPTX路径 |
| `--style` | str | corporate | 风格名称 |
| `--format` | str | ppt169 | 幻灯片比例 |
| `--title` | str | auto | 演示标题 |

## 支持的风格

| 风格ID | 显示名 | 主色 | 适用场景 |
|--------|--------|------|----------|
| corporate | 企业蓝 | #1E3A5F | 商务演示 |
| minimal | 极简白 | #FFFFFF | 高管汇报 |
| academic | 学术灰 | #4A5568 | 论文答辩 |
| tech | 科技蓝 | #3182CE | 技术分享 |
| dark | 暗夜黑 | #1A202C | 夜间演示 |
| creative | 创意彩 | #805AD5 | 营销提案 |

## 布局类型

| 布局 | 内容类型 | 特点 |
|------|----------|------|
| cover | 封面 | 居中大标题 |
| title | 章节标题 | 左对齐标题 |
| content | 内容页 | 标准要点列表 |
| two-column | 双栏 | 左右分栏 |
| code | 代码页 | 代码高亮 |
| chart | 图表页 | 数据可视化 |
| table | 表格页 | 表格展示 |
| ending | 结尾页 | 感谢/联系方式 |

## Markdown 支持

### 标准元素
```markdown
# H1 标题（封面）
## H2 标题（页面标题）
### H3 标题（子标题）

- 无序列表
1. 有序列表

> 引用块

| 表格 | 表头 |
|------|------|
| 内容 | 数据 |

![图片描述](image.png)
```

### 特殊语法

```markdown
<!-- slide:cover -->
<!-- slide:notes:演讲备注 -->
<!-- slide:layout:two-column -->
<!-- slide:transition:fade -->
<!-- slide:background:#000000 -->

```chart
type: bar
data: ...
```
```

## 错误处理

| 错误代码 | 说明 | 处理方式 |
|----------|------|----------|
| E001 | 文件不存在 | 提示用户检查路径 |
| E002 | 解析失败 | 显示错误位置 |
| E003 | 模板缺失 | 使用默认模板 |
| E004 | 导出失败 | 检查依赖环境 |

## 性能指标

| 指标 | 目标值 |
|------|--------|
| 解析速度 | < 1s / 100KB |
| 转换速度 | < 5s / 10页 |
| 内存占用 | < 200MB |

## 依赖项

- python-pptx >= 0.6.21
- markdown >= 3.4
- ppt-master (用于SVG导出)

## 集成说明

本技能可独立使用，也可与 `ppt-master` 集成：

```python
# 集成示例
from ppt_master import svg_to_pptx

def convert_with_style(input_file, style):
    # MD转SVG
    svg_pages = md2svg(input_file, style)
    # SVG转PPTX
    return svg_to_pptx(svg_pages)
```

---

**版本**: 1.0.0
**更新日期**: 2026-08-20
