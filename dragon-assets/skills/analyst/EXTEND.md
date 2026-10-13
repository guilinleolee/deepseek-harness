# Analyst EXTEND.md

## 默认分析师配置

---

## 自定义问题分析 (Custom Problem Analysis)

### quick-analysis
- depth: surface
- time_limit: 5min
- questions: 3
- root_cause: single
- alternatives: 2

### standard-analysis
- depth: moderate
- time_limit: 15min
- questions: 5
- root_cause: multiple
- alternatives: 3-5

### deep-analysis
- depth: comprehensive
- time_limit: 30min
- questions: 7+
- root_cause: systematic
- alternatives: 5+

---

## 自定义需求分析 (Custom Requirements Analysis)

### user-stories
- format: user_story
- template: As a {role}, I want {feature}, So that {benefit}
- acceptance_criteria: 3-5 per story
- priority: mo_scow_method
- estimation: story_points

### functional-specs
- format: functional_specification
- sections: [overview, requirements, constraints, acceptance]
- detail_level: high
- use_cases: included
- user_flows: included

### technical-specs
- format: technical_specification
- sections: [architecture, api, data, security, performance]
- detail_level: high
- diagrams: included
- dependencies: mapped

---

## 自定义问题解构 (Custom Problem Decomposition)

### 5-whys-method
- iterations: 5
- focus: root_cause
- documentation: chain_of_why
- validation: each_level

### first-principles
- approach: fundamental_truths
- assumptions: challenge_all
- decomposition: to_basic_elements
- reconstruction: from_fundamentals

### issue-mapping
- method: issue_mapping
- structure: problem_statement
- branches: 5-7
- depth: 3-4_levels
- format: text_map

---

## 自定义数据分析 (Custom Data Analysis)

### descriptive-analysis
- statistics: [mean, median, mode, std_dev]
- visualizations: [histogram, bar_chart, pie_chart]
- insights: surface_patterns
- predictions: none

### diagnostic-analysis
- statistics: correlation_analysis
- visualizations: [scatter_plot, heat_map]
- insights: root_causes
- predictions: none

### predictive-analysis
- statistics: regression_analysis
- visualizations: [trend_lines, confidence_intervals]
- insights: future_forecasts
- predictions: included

---

## 自定义根因分析 (Custom Root Cause Analysis)

### fishbone-diagram
- categories: [man, machine, material, method, environment, measurement]
- depth: 3_levels
- verification: data_driven
- format: diagram

### five-whys
- iterations: 5
- focus: single_chain
- verification: logical
- format: text

### fault-tree-analysis
- approach: top_down
- gates: [AND, OR, NOT]
- probability: included
- format: tree

---

## 自定义优先级评估 (Custom Priority Assessment)

### mo_scow-method
- must_have: critical_path
- should_have: high_value
- could_have: nice_to_have
- wont_have: out_of_scope
- rationale: documented

### rice-scoring
- reach: audience_size
- impact: value_per_user
- confidence: data_driven
- effort: person_months
- threshold: 10

### kano-model
- categories: [must_be, performance, delight, indifferent]
- survey: included
- analysis: satisfaction_vs_functionality
- prioritization: delight_first

---

## 自定义风险评估 (Custom Risk Assessment)

### qualitative-risk
- probability: [low, medium, high]
- impact: [low, medium, high]
- matrix: 3x3
- response: [avoid, mitigate, transfer, accept]

### quantitative-risk
- probability: percentage
- impact: monetary_value
- expected_value: calculated
- monte_carlo: optional

### fmea
- severity: 1-10
- occurrence: 1-10
- detection: 1-10
- rpn: calculated
- threshold: 100

---

## 自定义决策框架 (Custom Decision Framework)

### swot-analysis
- strengths: internal_positive
- weaknesses: internal_negative
- opportunities: external_positive
- threats: external_negative
- tows: strategies_generated

### decision-matrix
- criteria: weighted
- alternatives: 3-5
- scoring: 1-5
- sensitivity: included

### cost-benefit-analysis
- costs: all_identified
- benefits: quantified
- discount_rate: included
- payback_period: calculated
- roi: calculated

---

## 自定义输出格式 (Custom Output Format)

### executive-summary
- audience: executives
- length: 1-2_pages
- detail_level: high_level
- recommendations: action_oriented
- appendices: detailed_data

### technical-report
- audience: engineers
- length: 5-20_pages
- detail_level: comprehensive
- recommendations: technical
- appendices: code_samples

### presentation
- audience: stakeholders
- length: 10-20_slides
- detail_level: visual
- recommendations: bulleted
- format: slide_deck

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/analyst/EXTEND.md`
- **用户级**: `~/.claude/skills/analyst/EXTEND.md`
- **默认级**: `skills/analyst/EXTEND.md`

---

## 使用示例

### 快速需求分析
```markdown
## Quick Requirements

### quick-requirements
- analysis: quick-analysis
- requirements: user-stories
- decomposition: 5-whys-method
- priority: mo_scow-method
- risk: qualitative-risk
- decision: decision-matrix
- output: executive-summary
```

### 深度技术分析
```markdown
## Deep Technical Analysis

### deep-technical
- analysis: deep-analysis
- requirements: technical-specs
- decomposition: first-principles
- data: predictive-analysis
- root_cause: fault-tree-analysis
- priority: rice-scoring
- risk: quantitative-risk
- decision: cost-benefit-analysis
- output: technical-report
```

### 战略决策分析
```markdown
## Strategic Decision

### strategic-decision
- analysis: standard-analysis
- requirements: functional-specs
- decomposition: issue-mapping
- data: diagnostic-analysis
- root_cause: fishbone-diagram
- priority: kano-model
- risk: fmea
- decision: swot-analysis
- output: presentation
```
