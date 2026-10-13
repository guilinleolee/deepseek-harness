# GBrain Person Enrichment Template
# 人物实体充实模板

## 用途
`entity_enricher.py person` 命令渲染人物实体页面。

---

## YAML Frontmatter

```yaml
---
title: "{name}"
entity_type: person
summary: "{one_line_description}"
tags: [{tags}]
created: {created_date}
updated: {updated_date}
confidence: {confidence_score}
tier: {tier}
tier_criteria: "{tier_criteria}"
```

---

## Markdown Body

# {name}

## 基本信息

| 字段 | 内容 |
|------|------|
| **职位/头衔** | {title} |
| **所属组织** | {organization} |
| **角色类型** | {role_type} |
| **首次提及** | {first_mention_date} |
| **提及次数** | {mention_count} |
| **数据来源** | {source} |

{photo_block}

## 个人简介

{personal_bio}

## 关键背景

{key_background}

## 专业领域

{professional_domains}

## 与本项目的关联

{project_relevance}

## 近期动态

{recent_developments}

## 人脉网络

{personal_network}

### 直接关联

{直接关联人员列表}

### 间接关联

{间接关联人员列表}

## 公开言论

### 核心观点

{public_statements}

### 演讲/访谈

{interviews}

## 争议与评价

{controversy}

### 正面评价

{positive_remarks}

### 质疑/批评

{negative_remarks}

## 可靠性评估

| 维度 | 评分 | 说明 |
|------|------|------|
| 来源权威性 | {source_score}/10 | {source_explanation} |
| 信息时效性 | {freshness_score}/10 | {freshness_explanation} |
| 交叉验证度 | {cross_validation_score}/10 | {cross_validation_explanation} |
| **综合置信度** | **{overall_confidence}/10** | {overall_explanation} |

## 数据溯源

{references_section}

---

## 配置参考

| 占位符 | 来源 | 示例 |
|---------|------|------|
| `{name}` | 用户输入/LLM识别 | "Sam Altman" |
| `{title}` | 外部API或手动 | "CEO, OpenAI" |
| `{organization}` | 外部API或手动 | "OpenAI" |
| `{role_type}` | 推断 | "企业家/投资人/研究员" |
| `{tier}` | tier_assignment规则 | "tier1/tier2/tier3" |
| `{confidence_score}` | 来源质量评估 | "0.75" |
| `{personal_bio}` | Perplexity API 响应 | "Sam Altman is..." |
| `{photo_block}` | 可选，LinkedIn/网络 | `![photo](url)` |

---

## Tier 填充规则

### Tier 1 (Inner Circle)
直接提及 ≥3次 或 属于核心项目成员 或 担任决策角色
- 填充: 全部字段
- API调用: perplexity + linkedin

### Tier 2 (Middle Ring)
偶发提及 或 间接关联
- 填充: 基本信息 + 关键背景 + 专业领域
- API调用: web_search

### Tier 3 (Outer Ring)
单次提及 或 背景信息
- 填充: 基本信息 + 简要描述
- API调用: 仅brain交叉引用

---

## 双向链接示例

```markdown
## 与本项目的关联

{entity.name} 是 {project_name} 的{tier}级关联人员：
- 担任角色: {role_description}
- 关联方式: {relationship_type}
- 最近互动: {last_interaction}

### 相关页面
- [[{project_slug}|{project_title}]]
- [[{context_slug}|Context: {context_title}]]
```

---

## 反向链接自动生成

```markdown
## 被以下页面引用

<!-- backlinks -->
- [[source_page_1|{source_page_1_title}]]
- [[source_page_2|{source_page_2_title}]]
<!-- backlinks_end -->
```
