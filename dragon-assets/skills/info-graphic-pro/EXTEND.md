# Info-Graphic-Pro EXTEND.md

## 默认配置扩展

---

## 自定义布局 (Custom Layouts)

在 `~/.claude/skills/info-graphic-pro/EXTEND.md` 中添加自定义布局：

```markdown
### my-custom-layout
- description: 我的自定义布局
- structure: 网格/列表/流程/其他
- best-for: 特定使用场景
- elements: 元素说明
```

---

## 自定义风格 (Custom Styles)

在 `~/.claude/skills/info-graphic-pro/EXTEND.md` 中添加自定义风格：

```markdown
### my-brand-style
- description: 我的品牌风格
- colors: 主色 #FFFFFF, 辅助色 #000000
- typography: 字体选择
- best-for: 特定内容类型
```

---

## 自定义预设 (Custom Presets)

```markdown
### my-brand-preset
- layout: grid-2x2
- style: minimal
- description: 我的品牌预设组合
- best-for: 品牌内容
```

---

## 加载优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/info-graphic-pro/EXTEND.md`
- **用户级**: `~/.claude/skills/info-graphic-pro/EXTEND.md`
- **默认级**: `skills/info-graphic-pro/EXTEND.md`

---

## 使用示例

### 在项目级配置中添加品牌风格
```markdown
## Custom Styles

### tech-brand-style
- description: 科技品牌风格
- colors: #3B82F6 (蓝), #10B981 (绿)
- typography: 科技感无衬线
- best-for: 技术文档、产品介绍
```

### 在用户级配置中添加个人偏好
```markdown
## Custom Presets

### my-favorite-preset
- layout: timeline-vertical
- style: pastel
- description: 个人最爱的组合
```
