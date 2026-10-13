# GBrain Company Enrichment Template
# 公司实体充实模板

## 用途
`entity_enricher.py company` 命令渲染公司实体页面。

---

## YAML Frontmatter

```yaml
---
title: "{company_name}"
entity_type: company
summary: "{one_line_value_proposition}"
tags: [{tags}]
created: {created_date}
updated: {updated_date}
confidence: {confidence_score}
tier: {tier}
tier_criteria: "{tier_criteria}"
industry: "{industry}"
stage: "{company_stage}"
founded: "{founded_year}"
hq: "{headquarters}"
```

---

## Markdown Body

# {company_name}

## 基本信息

| 字段 | 内容 |
|------|------|
| **全称** | {full_name} |
| **简称/代号** | {short_name} |
| **官方网站** | {website} |
| **所属行业** | {industry} |
| **公司阶段** | {stage} |
| **成立年份** | {founded_year} |
| **总部所在地** | {headquarters} |
| **员工规模** | {company_size} |
| **核心业务** | {core_business} |

{logo_block}

## 公司简介

{company_description}

## 商业模式

{business_model}

## 核心产品/服务

{products_services}

### 主要产品

{product_list}

### 竞争优势

{competitive_advantages}

## 团队信息

{team_info}

### 创始团队

{founding_team}

### 核心管理层

{key_management}

## 融资历程

{funding_history}

| 轮次 | 时间 | 金额 | 投资方 | 估值 |
|------|------|------|--------|------|
{funding_table_rows}

## 财务状况

{financial_status}

## 市场地位

{market_position}

### 主要竞争对手

{competitors}

### 差异化定位

{differentiation}

## 近期动态

{recent_news}

### 重大事件

{key_events}

### 产品更新

{product_updates}

## 技术栈

{tech_stack}

## 合作生态

{ecosystem}

### 合作伙伴

{partners}

### 投资关系

{investments}

## 合规与风险

{compliance_risks}

## 数据溯源

{references_section}

---

## 配置参考

| 占位符 | 来源 | 示例 |
|---------|------|------|
| `{company_name}` | 用户输入/实体识别 | "OpenAI" |
| `{full_name}` | 外部API | "OpenAI, Inc." |
| `{stage}` | 外部API或推断 | "Pre-Seed/Series A/Public" |
| `{industry}` | 推断或API | "AI/SAAS/Fintech" |
| `{confidence_score}` | 来源质量评估 | "0.85" |
| `{company_description}` | Perplexity API | "OpenAI is an AI research..." |
| `{funding_table_rows}` | Crunchbase/API | "Series B\|2024-01\|$1B\|..." |

---

## Tier 填充规则

### Tier 1 (Inner Circle)
- 条件: 属于当前项目直接相关公司 或 高频提及 或 投资/合作方
- 填充: 全部字段
- API调用: perplexity + linkedin + web_search
- 更新频率: 实时

### Tier 2 (Middle Ring)
- 条件: 偶发提及 或 间接关联
- 填充: 基本信息 + 商业模式 + 融资历程 + 近期动态
- API调用: web_search
- 更新频率: 周更

### Tier 3 (Outer Ring)
- 条件: 单次提及 或 背景信息
- 填充: 基本信息 + 简介
- API调用: 仅brain交叉引用
- 更新频率: 按需

---

## 关系映射表

```markdown
## 关联实体

### 人员关联
{关联人员列表，使用双向链接}

### 竞品关联
- [[{competitor_slug}|{competitor_name}]] — 竞争关系: {nature_of_competition}

### 投资关系
- [[{portfolio_slug}|{portfolio_name}]] — 投资/被投: {investment_relationship}

### 合作关联
- [[{partner_slug}|{partner_name}]] — 合作关系: {partnership_type}
```

---

## 双向链接示例

```markdown
## 与本项目的关联

{company_name} 是 {project_name} 的{tier}级关联公司：
- 关联类型: {relationship_type}
- 合作内容: {collaboration_details}
- 最新进展: {latest_development}

### 相关页面
- [[{project_slug}|{project_title}]]
- [[{team_member_slug}|{team_member_name}]] — 核心联系人
```
