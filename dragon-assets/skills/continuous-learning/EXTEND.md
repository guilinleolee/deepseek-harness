# Continuous Learning EXTEND.md

## 默认持续学习配置

---

## 自定义学习模式 (Custom Learning Modes)

### just-in-time-learning
- trigger: task_encounter
- depth: solution_focused
- retention: task_duration
- documentation: minimal
- sharing: optional

### deliberate-learning
- trigger: scheduled
- depth: comprehensive
- retention: long_term
- documentation: detailed
- sharing: encouraged

### exploratory-learning
- trigger: curiosity_driven
- depth: open_ended
- retention: contextual
- documentation: optional
- sharing: collaborative

---

## 自定义知识提取 (Custom Knowledge Extraction)

### pattern-extraction
- focus: recurring_patterns
- generalization: applicable
- validation: tested
- documentation: structured
- indexing: by_domain

### lesson-extraction
- focus: mistakes_and_insights
- generalization: principle_based
- validation: experienced
- documentation: narrative
- indexing: by_context

### solution-extraction
- focus: working_solutions
- generalization: reusable
- validation: proven
- documentation: step_by_step
- indexing: by_problem

---

## 自定义知识存储 (Custom Knowledge Storage)

### memory-bank
- storage: internal_memory
- capacity: limited
- retrieval: conversation_based
- persistence: session_only
- sharing: none

### skill-repository
- storage: file_based
- capacity: unlimited
- retrieval: semantic_search
- persistence: permanent
- sharing: optional

### knowledge-graph
- storage: graph_database
- capacity: unlimited
- retrieval: relationship_based
- persistence: permanent
- sharing: collaborative

---

## 自定义学习优先级 (Custom Learning Priorities)

### frequency-based
- criteria: usage_frequency
- threshold: 3_occurrences
- urgency: immediate
- validation: automatic

### impact-based
- criteria: business_impact
- threshold: significant
- urgency: scheduled
- validation: manual

### complexity-based
- criteria: technical_complexity
- threshold: high
- urgency: as_needed
- validation: optional

---

## 自定义知识验证 (Custom Knowledge Validation)

### automatic-validation
- method: test_execution
- frequency: on_extraction
- strictness: pass_fail
- rollback: automatic
- documentation: auto_generated

### peer-validation
- method: human_review
- frequency: on_request
- strictness: consensus
- rollback: manual
- documentation: reviewed

### empirical-validation
- method: real_world_application
- frequency: continuous
- strictness: effectiveness
- rollback: conditional
- documentation: results_based

---

## 自定义知识分享 (Custom Knowledge Sharing)

### personal-sharing
- scope: private
- audience: self
- format: personal_notes
- frequency: on_demand
- discoverability: none

### team-sharing
- scope: team
- audience: colleagues
- format: team_wiki
- frequency: weekly
- discoverability: searchable

### community-sharing
- scope: public
- audience: community
- format: open_source
- frequency: milestone_based
- discoverability: indexed

---

## 自定义学习评估 (Custom Learning Assessment)

### retention-check
- method: recall_test
- frequency: periodic
- threshold: 80%
- reinforcement: spaced_repetition
- documentation: tracked

### application-check
- method: usage_analysis
- frequency: continuous
- threshold: applied_once
- reinforcement: successful_application
- documentation: case_study

### quality-check
- method: peer_review
- frequency: on_share
- threshold: approved
- reinforcement: feedback_loop
- documentation: rating

---

## 自定义知识组织 (Custom Knowledge Organization)

### flat-structure
- organization: flat
- categories: none
- tagging: auto_generated
- search: full_text
- hierarchy: none

### category-structure
- organization: categorical
- categories: predefined
- tagging: manual
- search: filtered
- hierarchy: 2_levels

### network-structure
- organization: graph
- categories: emergent
- tagging: auto_and_manual
- search: relationship_based
- hierarchy: none

---

## 自定义学习触发器 (Custom Learning Triggers)

### error-triggered
- event: error_encountered
- analysis: root_cause
- learning: solution_pattern
- documentation: error_lesson
- priority: high

### repetition-triggered
- event: pattern_repeated
- analysis: abstraction_opportunity
- learning: generalized_solution
- documentation: reusable_component
- priority: medium

### curiosity-triggered
- event: interesting_discovery
- analysis: deep_dive
- learning: domain_knowledge
- documentation: exploration_notes
- priority: low

---

## 自定义学习回顾 (Custom Learning Review)

### daily-review
- frequency: daily
- scope: last_24_hours
- duration: 5min
- action: quick_capture
- archive: daily_log

### weekly-review
- frequency: weekly
- scope: last_week
- duration: 30min
- action: synthesis_and_sharing
- archive: weekly_summary

### monthly-review
- frequency: monthly
- scope: last_month
- duration: 2_hours
- action: comprehensive_review
- archive: monthly_report

---

## 自定义技能进化 (Custom Skill Evolution)

### versioning
- scheme: semantic_versioning
- increments: [major, minor, patch]
- automation: on_improvement
- rollback: supported
- deprecation: phased

### a-b-testing
- method: parallel_versions
- duration: 2_weeks
- metric: success_rate
- selection: better_performing
- retirement: graceful

### continuous-improvement
- method: iterative_refinement
- frequency: on_usage
- metric: effectiveness
- selection: gradual
- retirement: manual

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/continuous-learning/EXTEND.md`
- **用户级**: `~/.claude/skills/continuous-learning/EXTEND.md`
- **默认级**: `skills/continuous-learning/EXTEND.md`

---

## 使用示例

### 即时学习模式
```markdown
## Just-in-Time Learning

### jit-learning
- mode: just-in-time-learning
- extraction: pattern-extraction + lesson-extraction
- storage: memory-bank
- priorities: frequency-based
- validation: automatic-validation
- sharing: personal-sharing
- assessment: application-check
- organization: flat-structure
- triggers: error-triggered + repetition-triggered
- review: daily-review
- evolution: continuous-improvement
```

### 团队学习模式
```markdown
## Team Learning

### team-learning
- mode: deliberate-learning
- extraction: all_extraction_types
- storage: knowledge-graph
- priorities: impact-based
- validation: peer-validation
- sharing: team-sharing
- assessment: quality-check + application-check
- organization: category-structure
- triggers: all_triggers
- review: weekly-review
- evolution: versioning + a-b-testing
```

### 探索式学习模式
```markdown
## Exploratory Learning

### exploratory-learning
- mode: exploratory-learning
- extraction: solution-extraction + pattern-extraction
- storage: skill-repository
- priorities: complexity-based
- validation: empirical-validation
- sharing: community-sharing
- assessment: all_assessments
- organization: network-structure
- triggers: curiosity-triggered
- review: monthly-review
- evolution: continuous-improvement
```
