# Agents List EXTEND.md

## 默认Agents列表配置

---

## 自定义列表格式 (Custom List Format)

### compact-list
- format: names_only
- detail: minimal
- grouping: none
- description: omitted

### detailed-list
- format: name_with_description
- detail: full
- grouping: by_type
- description: included

### table-view
- format: markdown_table
- detail: key_attributes
- grouping: by_department
- description: summarized

---

## 自定义分组策略 (Custom Grouping Strategy)

### no-grouping
- organization: flat_list
- hierarchy: none
- navigation: scroll
- filtering: manual

### by-department
- organization: functional_areas
- hierarchy: one_level
- navigation: section_headers
- filtering: by_specialty

### by-hierarchy
- organization: tiered_structure
- hierarchy: multi_level
- navigation: nested_sections
- filtering: by_level

### by-workflow
- organization: sequential_stages
- hierarchy: pipeline
- navigation: ordered_steps
- filtering: by_phase

---

## 自定义筛选条件 (Custom Filtering Criteria)

### show-all
- filter: none
- scope: all_agents
- visibility: complete
- selection: manual

### active-only
- filter: production_ready
- scope: available_agents
- visibility: operational
- selection: ready_to_use

### by-expertise
- filter: skill_based
- scope: matched_to_task
- visibility: relevant
- selection: intelligent

---

## 自定义排序规则 (Custom Sorting Rules)

### alphabetical
- order: a_to_z
- priority: none
- custom_order: none
- locale: unicode

### workflow-order
- order: sequential
- priority: process_based
- custom_order: defined_sequence
- locale: not_applicable

### popularity-order
- order: frequency_based
- priority: usage_stats
- custom_order: most_used_first
- locale: not_applicable

---

## 自定义交互模式 (Custom Interaction Mode)

### reference-only
- purpose: information_only
- invocation: manual
- guidance: minimal
- examples: none

### guided-invoke
- purpose: assisted_usage
- invocation: suggested_commands
- guidance: contextual_tips
- examples: included

### auto-dispatch
- purpose: intelligent_routing
- invocation: automatic_selection
- guidance: full_support
- examples: extensive

---

## 自定义更新频率 (Custom Update Frequency)

### static-list
- source: hardcoded
- updates: manual_only
- sync: none
- freshness: outdated_risk

### dynamic-sync
- source: scanned_from_files
- updates: automatic_on_load
- sync: real_time
- freshness: always_current

### periodic-sync
- source: scanned_with_cache
- updates: scheduled_intervals
- sync: time_based
- freshness: reasonably_current

---

## 自定义版本信息 (Custom Version Info)

### no-versioning
- display: none
- tracking: none
- comparisons: impossible
- migration: manual

### basic-versioning
- display: major_only
- tracking: release_number
- comparisons: major_breaks
- migration: documented

### full-versioning
- display: full_semver
- tracking: detailed_history
- comparisons: precise
- migration: automated_hints

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/agents-list/EXTEND.md`
- **用户级**: `~/.claude/skills/agents-list/EXTEND.md`
- **默认级**: `skills/agents-list/EXTEND.md`

---

## 使用示例

### 快速参考
```markdown
## Quick Reference

### quick-ref
- format: compact-list
- grouping: no-grouping
- filtering: show-all
- sorting: alphabetical
- interaction: reference-only
- updates: static-list
- versioning: no-versioning
```

### 工作流指南
```markdown
## Workflow Guide

### workflow-guide
- format: detailed-list
- grouping: by-workflow
- filtering: active-only
- sorting: workflow-order
- interaction: guided-invoke
- updates: dynamic-sync
- versioning: basic-versioning
```

### 智能助手
```markdown
## Smart Assistant

### smart-assistant
- format: table-view
- grouping: by-department
- filtering: by-expertise
- sorting: popularity-order
- interaction: auto-dispatch
- updates: periodic-sync
- versioning: full-versioning
```
