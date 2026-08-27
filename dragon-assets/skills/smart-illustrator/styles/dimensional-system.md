# Smart Illustrator V2 - 三维风格系统

## 风格维度

### Type (信息结构) × Style (视觉美学) × Mood (情感氛围)

```
6 Types × 8 Styles × 4 Moods = 192 种风格组合
```

---

## 维度定义

### Type - 信息结构 (6种)

| Type | 描述 | 最佳场景 |
|------|------|---------|
| `infographic` | 数据可视化、图表、指标 | 技术文章、数据分析 |
| `scene` | 氛围插图、情绪渲染 | 叙事、个人故事 |
| `flowchart` | 流程图、步骤可视化 | 教程、工作流 |
| `comparison` | 对比图、前后对比 | 产品比较 |
| `framework` | 概念图、关系图 | 方法论、架构 |
| `timeline` | 时间线、演进过程 | 历史、项目进度 |

### Style - 视觉美学 (8种)

| Style | 描述 | 最佳场景 |
|-------|------|---------|
| `notion` | 极简手绘线条 | 知识分享、SaaS、生产力 |
| `elegant` | 精致高级 | 商业、思想领导力 |
| `warm` | 友好温暖 | 个人成长、生活方式 |
| `minimal` | 超简禅意 | 哲学、极简主义 |
| `blueprint` | 技术蓝图 | 架构、系统设计 |
| `watercolor` | 轻柔水彩 | 生活方式、旅行、创意 |
| `editorial` | 杂志信息图 | 科技解说、新闻 |
| `scientific` | 学术精确图 | 生物、化学、技术 |

### Mood - 情感氛围 (4种)

| Mood | 描述 | 适用场景 |
|------|------|---------|
| `subtle` | 含蓄低调 | 长篇内容、严肃话题 |
| `balanced` | 平衡适中 (默认) | 通用场景 |
| `bold` | 醒目大胆 | 营销、强调重点 |
| `vibrant` | 活力鲜艳 | 年轻、活力主题 |

---

## 使用示例

### 指定单维度

```bash
# 只指定Type (自动选择Style和Mood)
/smart-illustrator article.md --type infographic

# 只指定Style (自动选择Type和Mood)
/smart-illustrator article.md --style elegant

# 只指定Mood (自动选择Type和Style)
/smart-illustrator article.md --mood bold
```

### 指定多维度

```bash
# 指定Type + Style
/smart-illustrator article.md --type flowchart --style blueprint

# 指定Style + Mood
/smart-illustrator article.md --style watercolor --mood subtle

# 指定全部三维
/smart-illustrator article.md --type scene --style warm --mood vibrant
```

### 预设组合 (快捷方式)

```bash
# 技术文档预设
/smart-illustrator article.md --preset tech-doc
# 等价于: --type infographic --style blueprint --mood balanced

# 生活方式预设
/smart-illustrator article.md --preset lifestyle
# 等价于: --type scene --style watercolor --mood warm

# 商业报告预设
/smart-illustrator article.md --preset business
# 等价于: --type comparison --style elegant --mood subtle
```

---

## 自动推荐逻辑

当用户不指定任何维度时，系统根据文章内容自动推荐：

### 内容分析

| 关键词 | 推荐Type | 推荐Style | 推荐Mood |
|--------|----------|-----------|----------|
| 数据、分析、统计 | infographic | scientific | balanced |
| 故事、经历、回忆 | scene | watercolor | warm |
| 教程、指南、步骤 | flowchart | notion | balanced |
| 比较、对比、区别 | comparison | editorial | bold |
| 架构、系统、设计 | framework | blueprint | balanced |
| 历史、演进、发展 | timeline | elegant | subtle |

### 风格权重计算

```
推荐得分 = 关键词匹配 × 2 + 风格契合度 × 1.5 + 情感基调 × 1
```

---

## EXTEND.md 自定义

用户可以在EXTEND.md中添加自定义风格：

```markdown
## Custom Styles

### my-brand-style
- description: 我的品牌风格
- colors: #primary, #secondary
- best-for: 官方文档、教程

## Custom Presets

### my-tech-preset
- type: infographic
- style: my-brand-style
- mood: balanced
- best-for: 技术博客
```
