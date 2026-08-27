# Knowledge-Comic EXTEND.md

## 默认配置扩展

---

## 自定义艺术风格 (Custom Art Styles)

在 `~/.claude/skills/knowledge-comic/EXTEND.md` 中添加：

```markdown
### my-custom-art
- description: 我的自定义艺术风格
- style-guide: 风格指导说明
- visual-traits: 视觉特征
- best-for: 特定使用场景
- color-scheme: 配色方案
```

---

## 自定义叙述语气 (Custom Tones)

在 `~/.claude/skills/knowledge-comic/EXTEND.md` 中添加：

```markdown
### my-custom-tone
- description: 我的自定义语气
- voice: 叙述声音特征
- language-style: 语言风格
- best-for: 特定内容类型
- dialogue-examples: 对话示例
```

---

## 自定义预设 (Custom Presets)

```markdown
### my-brand-preset
- art: manga
- tone: educational
- description: 我的品牌预设组合
- best-for: 品牌内容
- target-audience: 目标受众
```

---

## 加载优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/knowledge-comic/EXTEND.md`
- **用户级**: `~/.claude/skills/knowledge-comic/EXTEND.md`
- **默认级**: `skills/knowledge-comic/EXTEND.md`

---

## 使用示例

### 添加自定义艺术风格
```markdown
## Custom Art Styles

### watercolor-art
- description: 水彩艺术风格
- style-guide: 柔和水彩，流动笔触
- visual-traits: 透明水彩效果
- best-for: 文艺清新内容
- color-scheme: 粉嫩水彩配色
```

### 添加自定义语气
```markdown
## Custom Tones

### friendly-tone
- description: 友好亲切语气
- voice: 像朋友聊天
- language-style: 口语化，温暖
- best-for: 社交科普
- dialogue-examples: "嘿，让我告诉你..."
```
