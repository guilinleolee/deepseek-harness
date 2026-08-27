# 用户画像分析报告 - {{ keyword }}

> 生成时间：{{ timestamp }}
> 数据源：{{ sources|join(', ') }}

---

## 📊 执行摘要

### 核心用户画像
{{ core_persona.user_profile }}

### 关键指标
- **主要年龄段**：{{ core_persona.primary_age }}（{{ core_persona.primary_age_pct }}%）
- **性别比例**：{{ core_persona.gender_desc }}
- **核心地域**：{{ core_persona.top_regions|join('、') }}
- **数据来源**：{{ source_count }} 个数据源

### 核心发现
{% for insight in insights %}
- {{ insight }}
{% endfor %}

---

## 👥 人口统计学特征

### 年龄分布

| 年龄段 | 占比 | 特征描述 |
|--------|------|----------|
| 18-24岁 | {{ demographics.age['18-24']*100 }}% | Z世代，学生/职场新人 |
| 25-30岁 | {{ demographics.age['25-30']*100 }}% | 职场青年，消费主力 |
| 31-35岁 | {{ demographics.age['31-35']*100 }}% | 职场中坚，家庭阶段 |
| 36-40岁 | {{ demographics.age['36-40']*100 }}% | 职场资深，稳定阶段 |
| 40+岁 | {{ demographics.age['40+']*100 }}% | 资深用户，决策层 |

**核心年龄段**：{{ core_persona.primary_age }}

### 性别分布

- **男性**：{{ demographics.gender.male*100 }}%
- **女性**：{{ demographics.gender.female*100 }}%
- **性别特征**：{{ core_persona.gender_dominant }}

---

## 🌍 地域分布分析

### TOP 10 省份/城市

| 排名 | 地域 | 占比 |
|------|------|------|
{% for region in demographics.region[:10] %}
| {{ region.rank }} | {{ region.region }} | {{ region.percentage*100 }}% |
{% endfor %}

---

## 💡 策略建议

### 内容策略

- **内容调性**：{{ content_strategy.tone }}
- **内容形式**：{{ content_strategy.format }}
- **话题建议**：{{ content_strategy.topics }}
- **内容长度**：{{ content_strategy.length }}

### 平台投放建议

{% if tier_1_pct > 0.5 %}
- **一线城市用户占比高**（{{ tier_1_pct*100 }}%），用户消费能力强
- **推荐平台**：知乎、B站、小红书
{% else %}
- **推荐平台**：抖音、快手、今日头条
{% endif %}

---

## 📎 附录

### 数据来源详情

{% for source in sources %}
- **{{ source }}**：{{ source_data[source].metadata.data_freshness }}
{% endfor %}

### 报告说明

本报告基于多个数据源的公开数据生成，仅供参考。实际用户画像可能因时间、平台、样本量等因素有所差异。建议结合实际业务数据综合分析。

---

*报告由 用户画像提取器 自动生成*
*数据来源：{{ sources|join(', ') }}*
