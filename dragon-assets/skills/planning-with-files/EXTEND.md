# Planning with Files EXTEND.md

## 默认文件持久化配置

---

## 自定义文件结构

### minimal-files
- files: [plan.md]
- content: essentials_only
- organization: flat
- maintenance: simple

### standard-files
- files: [plan.md, findings.md, progress.md]
- content: comprehensive
- organization: separated_concerns
- maintenance: moderate

### elaborate-files
- files: [plan.md, findings.md, progress.md, decisions.md, blockers.md]
- content: exhaustive
- organization: highly_structured
- maintenance: intensive

---

## 自定义更新频率

### manual-updates
- trigger: user_initiated
- automation: none
- versioning: manual_commits
- context_loss: possible

### milestone-updates
- trigger: phase_completion
- automation: semi_automatic
- versioning: automatic_commits
- context_loss: minimized

### continuous-updates
- trigger: every_significant_action
- automation: fully_automatic
- versioning: frequent_commits
- context_loss: virtually_none

---

## 自定义追踪粒度

### high-level-tracking
- detail: major_phases
- subtasks: not_tracked
- time: coarse
- status: binary

### task-level-tracking
- detail: individual_tasks
- subtasks: tracked
- time: estimated_ranges
- status: multi_state

### granular-tracking
- detail: subtask_steps
- subtasks: fully_broken_down
- time: specific_estimates
- status: detailed_progress

---

## 自定义错误记录

### summary-only
- capture: error_count
- detail: minimal
- patterns: not_analyzed
- learning: limited

### detailed-errors
- capture: full_context
- detail: stack_traces_logs
- patterns: identified
- learning: moderate

### analytical-errors
- capture: comprehensive_diagnosis
- detail: root_cause_analysis
- patterns: categorized_trends
- learning: high

---

## 自定义发现管理

### linear-log
- structure: chronological_append
- organization: time_based
- retrieval: scroll_search
- synthesis: manual

### categorized-findings
- structure: thematic_sections
- organization: topic_based
- retrieval: section_navigation
- synthesis: semi_automatic

### knowledge-graph
- structure: linked_entities
- organization: relational
- retrieval: semantic_search
- synthesis: ai_assisted

---

## 自定义可视化

### text-only
- format: markdown
- rendering: raw_text
- interactivity: none
- accessibility: universal

### progress-bars
- format: markdown_with_indicators
- rendering: formatted_text
- interactivity: checkboxes
- accessibility: good

### dashboard-views
- format: html_or_specialized
- rendering: rich_visualization
- interactivity: clickable_filters
- accessibility: requires_support

---

## 配置优先级

CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置

---

## 使用示例

### 简单任务
- structure: minimal-files
- updates: manual-updates
- tracking: high-level-tracking
- errors: summary-only
- findings: linear-log
- visualization: text-only

### 标准项目
- structure: standard-files
- updates: milestone-updates
- tracking: task-level-tracking
- errors: detailed-errors
- findings: categorized-findings
- visualization: progress-bars

### 复杂项目
- structure: elaborate-files
- updates: continuous-updates
- tracking: granular-tracking
- errors: analytical-errors
- findings: knowledge-graph
- visualization: dashboard-views
