# Drucker Writer EXTEND.md

## 默认德鲁克写作配置

---

## 自定义写作风格 (Custom Writing Style)

### management-principles
- tone: authoritative
- voice: mentorship
- perspective: experienced_manager
- style: principle_based

### narrative-style
- tone: storytelling
- voice: observational
- perspective: business_historian
- style: anecdote_rich

### analytical-style
- tone: objective
- voice: consulting
- perspective: strategic_analyst
- style: data_driven

---

## 自定义内容结构 (Custom Content Structure)

### problem-solution
- framework: situation_complication_resolution
- elements: [context, problem, analysis, solution]
- flow: logical_progression
- emphasis: actionable_insights

### five-questions
- framework: 5_questions
- elements: [what, why, who, when, how]
- flow: interrogative
- emphasis: clarity

### management-by-objectives
- framework: smart_goals
- elements: [objective, measurement, action, review]
- flow: cyclical
- emphasis: results

---

## 自定义主题范围 (Custom Topic Scope)

### general-management
- focus: broad_principles
- depth: introductory
- examples: cross_industry
- application: universal

### specialized-function
- focus: [marketing, finance, operations, hr]
- depth: intermediate
- examples: function_specific
- application: targeted

### industry-specific
- focus: single_industry
- depth: expert
- examples: domain_relevant
- application: specialized

---

## 自定义引用习惯 (Custom Citation Habits)

### no-citations
- style: original_thought
- references: none
- attribution: none
- authority: internal

### light-citations
- style: casual_mentions
- references: key_concepts
- attribution: implied
- authority: recognized_experts

### academic-citations
- style: formal_footnotes
- references: comprehensive
- attribution: explicit
- authority: peer_reviewed

---

## 自定义目标受众 (Custom Target Audience)

### executives
- level: c_suite
- background: business_school
- constraints: time_limited
- format: executive_summary

### middle-managers
- level: director_manager
- background: experienced_operational
- constraints: practical_focus
- format: actionable_guidance

### students
- level: mba_undergraduate
- background: theoretical
- constraints: learning_mode
- format: educational

---

## 自定义篇幅控制 (Custom Length Control)

### brief-insight
- length: 300_500_words
- focus: single_concept
- detail: high_level
- time: 2_min_read

### standard-article
- length: 800_1200_words
- focus: explored_concept
- detail: moderate_depth
- time: 5_min_read

### comprehensive-analysis
- length: 2000_3000_words
- focus: deep_exploration
- detail: thorough
- time: 12_min_read

---

## 自定义实践建议 (Custom Actionable Advice)

### theoretical-only
- practicality: conceptual
- examples: abstract
- application: reader_interpretation
- tools: none

### framework-provided
- practicality: structured
- examples: generic_templates
- application: fill_in_blanks
- tools: worksheets

### step-by-step
- practicality: prescriptive
- examples: detailed_case_studies
- application: follow_instructions
- tools: checklists_templates

---

## 自定义时代适配 (Custom Era Adaptation)

### vintage-1950s
- context: post_war_america
- language: formal
- examples: manufacturing_corp
- technology: pre_digital

### classic-1980s
- context: knowledge_economy
- language: professional
- examples: services_finance
- technology: early_computing

### modern-2020s
- context: digital_transformation
- language: contemporary
- examples: tech_platforms
- technology: ai_distributed

### timeless-adaptation
- context: universal_principles
- language: era_agnostic
- examples: updated_relevant
- technology: appropriate

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/drucker-writer/EXTEND.md`
- **用户级**: `~/.claude/skills/drucker-writer/EXTEND.md`
- **默认级**: `skills/drucker-writer/EXTEND.md`

---

## 使用示例

### 快速管理建议
```markdown
## Quick Management Advice

### quick-advice
- style: management-principles
- structure: problem-solution
- scope: general-management
- citations: no-citations
- audience: executives
- length: brief-insight
- advice: theoretical-only
- era: modern-2020s
```

### 深度管理文章
```markdown
## In-depth Management Article

### deep-article
- style: analytical-style
- structure: five-questions
- scope: specialized-function
- citations: light-citations
- audience: middle-managers
- length: standard-article
- advice: framework-provided
- era: timeless-adaptation
```

### 经典德鲁克风格
```markdown
## Classic Drucker Style

### classic-drucker
- style: narrative-style
- structure: management-by-objectives
- scope: general-management
- citations: academic-citations
- audience: students
- length: comprehensive-analysis
- advice: step-by-step
- era: vintage-1950s
```
