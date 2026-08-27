# Magazine-Layout EXTEND.md

## 默认风格扩展

---

## 自定义风格 (Custom Styles)

在 `~/.claude/skills/magazine-layout/EXTEND.md` 中添加自定义风格：

```markdown
### my-magazine-style
- name: 我的杂志风格
- description: 自定义杂志排版风格
- typography: 字体配置
- colors: 配色方案
- layout: 布局规则
```

---

## 自定义配色方案 (Custom Color Palettes)

```markdown
### my-color-palette
- primary: #3B82F6
- secondary: #10B981
- accent: #F59E0B
- background: #FFFFFF
- text: #1F2937
- muted: #6B7280
```

---

## 自定义排版 (Custom Typography)

```markdown
### my-typography
- heading_font: Georgia
- body_font: system-ui
- mono_font: monospace
- heading_scale: 2.5
- line_height: 1.6
- letter_spacing: normal
```

---

## 自定义组件 (Custom Components)

```markdown
### my-components
- pullquote_style: bordered
- code_block: themed
- list_style: minimal
- table_style: striped
```

---

## 自定义分页规则 (Custom Pagination)

```markdown
### my-pagination
- max_height: 1200px
- break_before: h1, h2
- widow_control: true
- orphans: 2
```

---

## 加载优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/magazine-layout/EXTEND.md`
- **用户级**: `~/.claude/skills/magazine-layout/EXTEND.md`
- **默认级**: `skills/magazine-layout/EXTEND.md`

---

## 使用示例

### 自定义杂志风格
```markdown
## Magazine Styles

### tech-magazine
- name: 科技杂志风格
- description: 现代科技感杂志排版
- primary: #0EA5E9
- heading_font: Inter
- layout: grid-3-column
```

### 自定义组件
```markdown
## Component Styles

### minimal-components
- pullquote: simple-left
- code: github-dark
- tables: clean-borders
- lists: custom-bullets
```

### 自定义PDF输出
```markdown
## PDF Export

### my-pdf-settings
- page_size: A4
- margin: 20mm
- toc: true
- page_numbers: footer-center
