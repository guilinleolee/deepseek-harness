# GEO机会分析报告模板

> **报告ID**: `geo_report_{timestamp}`
> **生成时间**: {generated_at}
> **分析引擎**: dageno-api-bridge v1.0
> **分析师**: Tianlong Engine

---

## 执行摘要

{executive_summary}

**整体评估**: {overall_score}/10 | **{grade}**

| 维度 | 评分 | 状态 |
|------|------|------|
| 机会价值 | {opportunity_score}/10 | {opportunity_status} |
| 权威来源 | {authority_score}/10 | {authority_status} |
| 内容覆盖 | {coverage_score}/10 | {coverage_status} |
| 执行难度 | {difficulty_score}/10 | {difficulty_status} |

---

## 1. 机会概述

### 1.1 基本信息

| 字段 | 值 |
|------|---|
| 机会ID | `{opportunity_id}` |
| 主题 | {topic} |
| 查询量 | {query_volume:,}/月 |
| 机会类型 | {opportunity_type} |
| 发现时间 | {discovered_at} |

### 1.2 机会评分

```
┌─────────────────────────────────────────────────────────────┐
│                    机会评分卡                                │
├─────────────────────────────────────────────────────────────┤
│  查询量权重 (25%)    ████████████████████░░░ 8.0/10        │
│  竞争度权重 (20%)    ██████████████░░░░░░░░ 6.0/10        │
│  趋势性权重 (15%)    ██████████████████░░░░ 7.5/10        │
│  权威性权重 (20%)    ████████████░░░░░░░░░░ 5.5/10        │
│  可执行性权重 (20%)  ██████████████████░░░░ 7.8/10        │
│                                                             │
│  📊 综合得分: {total_score}/10 | 评级: {grade}              │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 查询意图分析

```
用户主要意图分布:
- 信息型 (informational): {info_pct}%
- 对比型 (comparison): {comparison_pct}%
- 评测型 (evaluation): {eval_pct}%
- 实践型 (practical): {practical_pct}%

核心问题:
{user_core_questions}

推荐内容类型: {recommended_content_type}
```

---

## 2. Fanout传播路径分析

### 2.1 现有传播路径

| Fanout ID | 平台 | 标题 | 引用数 | 权威性 |
|-----------|------|------|--------|--------|
{fanouts_table}

### 2.2 平台覆盖分析

```
✅ 已覆盖平台:
{covered_platforms}

⚠️ 覆盖不足平台:
{undercovered_platforms}

❌ 未覆盖平台:
{missing_platforms}
```

### 2.3 传播路径评分

| 维度 | 得分 | 说明 |
|------|------|------|
| 深度平台 | {deep_score}/10 | {deep_explanation} |
| 社区覆盖 | {community_score}/10 | {community_explanation} |
| 权威背书 | {authority_score}/10 | {authority_explanation} |
| 时效更新 | {freshness_score}/10 | {freshness_explanation} |

---

## 3. 引用质量分析

### 3.1 引用来源分布

```
引用来源Tier分布:
┌─────────────────────────────────────────────────────────────┐
│  Tier 1 (顶级权威) ██████████████████░░░░░░░░░░ 40%       │
│  Tier 2 (高可信)   █████████████████████████████ 50%        │
│  Tier 3 (中等)     ██░░░░░░░░░░░░░░░░░░░░░░░ 10%       │
│  Tier 4 (一般)     ░░░░░░░░░░░░░░░░░░░░░░░░ 0%         │
└─────────────────────────────────────────────────────────────┘

权威来源比例: {authority_ratio}% (目标 ≥50%)
平均权威分: {avg_authority_score}/100
加权权威分: {weighted_authority_score}/100
```

### 3.2 引用密度评估

| 指标 | 当前值 | 最低要求 | 优秀标准 | 状态 |
|------|--------|----------|----------|------|
| 总引用数 | {total_citations} | 5 | 10+ | {citation_count_status} |
| 学术引用 | {academic_citations} | 2 | 5+ | {academic_status} |
| 官方引用 | {official_citations} | 1 | 3+ | {official_status} |
| 引用密度 | {citation_density}/词 | 1/400词 | 1/300词 | {density_status} |

### 3.3 权威来源列表

{authority_citations_list}

---

## 4. 内容差距识别

### 4.1 Gap分析总览

| Gap ID | 类型 | 严重度 | 描述 | 修复建议 |
|--------|------|--------|------|----------|
{gaps_table}

### 4.2 内容深度差距

```
当前深度评分: {depth_score}/10

深度不足区域:
{depth_gaps}

建议补充内容:
{depth_recommendations}
```

### 4.3 来源权威差距

```
权威来源缺口:
{authority_gaps}

建议补充来源:
{authority_recommendations}
```

### 4.4 平台覆盖差距

```
覆盖缺口平台:
{platform_gaps}

建议覆盖策略:
{platform_recommendations}
```

---

## 5. 内容优化建议

### 5.1 立即修复 (高优先级)

```
问题1: {issue_1}
修复: {fix_1}
工作量: {effort_1}

问题2: {issue_2}
修复: {fix_2}
工作量: {effort_2}
```

### 5.2 建议优化 (中优先级)

```
问题3: {issue_3}
修复: {fix_3}
工作量: {effort_3}
```

### 5.3 可选增强 (低优先级)

```
问题4: {issue_4}
修复: {fix_4}
工作量: {effort_4}
```

---

## 6. 决策引擎

### 6.1 必须元素检查

| 元素 | 要求 | 当前状态 | 状态 |
|------|------|----------|------|
| [not ideal when] | ≥1 | {not_ideal_count} | {not_ideal_status} |
| [default recommendation] | 1 | {default_rec_count} | {default_rec_status} |
| [comparison] | ≥1 | {comparison_count} | {comparison_status} |
| [decision engine] | ≥1 | {decision_count} | {decision_status} |
| [convergence] | 1 | {convergence_count} | {convergence_status} |

### 6.2 决策树

```
[not ideal when]
{not_ideal_when}

[default recommendation]
{default_recommendation}

[comparison]
{comparison}

[decision engine]
{decision_engine}

[convergence]
{convergence}
```

---

## 7. 实施计划

### 7.1 时间线

```
Week 1: 深度内容创作
├── 完成主要文章 (2000词)
├── 添加权威引用
└── 包含决策引擎元素

Week 2: 辅助内容分发
├── GitHub代码库 + README
├── 技术社区帖子
└── 社交媒体预告

Week 3: 推广与迭代
├── 社区互动
├── 收集反馈
└── 内容迭代更新
```

### 7.2 工作量估算

| 任务 | 预计时间 | 优先级 |
|------|----------|--------|
| {task_1} | {time_1} | {priority_1} |
| {task_2} | {time_2} | {priority_2} |
| {task_3} | {time_3} | {priority_3} |

---

## 8. 附录

### 8.1 原始数据

**机会数据**:
```json
{opportunity_json}
```

**Fanout数据**:
```json
{fanouts_json}
```

**引用数据**:
```json
{citations_json}
```

### 8.2 分析方法论

本报告基于以下分析方法论:
1. DAGENO API三层调用 (机会发现 → Fanout获取 → 引用获取)
2. 5层质量门控 (L1-L5)
3. 权威来源评分体系 (Tier1-Tier4)
4. Gap分析四维度 (平台/来源/深度/时效)

---

> **报告生成**: Tianlong Engine | dageno-api-bridge v1.0
> **分析时间**: {analysis_timestamp}
> **数据截止**: {data_cutoff}
