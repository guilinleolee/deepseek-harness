# Infographic-Designer EXTEND.md

## 默认品牌配置

---

## 自定义品牌元素 (Custom Brand Elements)

在 `~/.claude/skills/infographic-designer/EXTEND.md` 中添加自定义品牌：

```markdown
### my-brand-config
- wateremark_text: 我的品牌
- watermark_opacity: 10
- topleft_label: 品牌名称
- topright_label: SYSTEM v2.0
- footer_slogan: 品牌Slogan
```

---

## 自定义配色方案 (Custom Color Schemes)

```markdown
### my-color-scheme
- primary: #1E3A5F
- secondary: #C8102E
- background: #F5F5F0
- text_primary: #1F2937
- text_secondary: #6B7C93
- accent: #3B82F6
```

---

## 自定义布局 (Custom Layouts)

```markdown
### my-layout-3x3
- structure: 3x3 grid
- title_position: top
- summary_position: bottom
- node_style: red-line
```

---

## 自定义字体 (Custom Typography)

```markdown
### my-typography
- title_font: font-black
- title_size: 60pt
- subtitle_size: 20px
- body_size: 15px
- tracking: tracking-tighter
```

---

## 加载优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/infographic-designer/EXTEND.md`
- **用户级**: `~/.claude/skills/infographic-designer/EXTEND.md`
- **默认级**: `skills/infographic-designer/EXTEND.md`

---

## 使用示例

### 自定义品牌配置
```markdown
## Brand Configurations

### company-brand
- watermark_text: XX公司
- topleft_label: XX企业培训
- topright_label: PRO v1.0
- footer_slogan: 从团队到卓越
```

### 自定义配色
```markdown
## Color Schemes

### tech-blue
- primary: #0EA5E9 (Sky Blue)
- secondary: #6366F1 (Indigo)
- background: #F8FAFC
- accent: #06B6D4 (Cyan)
```

### 自定义布局
```markdown
## Layouts

### minimal-2x2
- structure: 2x2 grid
- padding: generous
- borders: minimal
```
