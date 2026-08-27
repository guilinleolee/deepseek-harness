# Executing Plans EXTEND.md

## 默认执行计划配置

---

## 自定义执行模式 (Custom Execution Modes)

### interactive-mode
- interaction: required
- confirmation: at_milestones
- feedback: continuous
- stop_on_error: true

### autonomous-mode
- interaction: none
- confirmation: initial_only
- feedback: summary_only
- stop_on_error: false

### semi-autonomous-mode
- interaction: at_checkpoints
- confirmation: at_critical_steps
- feedback: periodic
- stop_on_error: configurable

---

## 自定义计划阶段 (Custom Plan Stages)

### minimal-stages
- stages: 2-3
- detail_level: high_level
- checkpoints: none
- approval: initial

### standard-stages
- stages: 4-6
- detail_level: moderate
- checkpoints: stage_boundaries
- approval: at_checkpoints

### granular-stages
- stages: 10+
- detail_level: detailed
- checkpoints: multiple_per_stage
- approval: at_checkpoints

---

## 自定义检查点配置 (Custom Checkpoint Config)

### no-checkpoints
- checkpoints: disabled
- validation: end_only
- reporting: summary

### milestone-checkpoints
- checkpoints: at_milestones
- validation: deliverable_based
- reporting: milestone_report

### stage-checkpoints
- checkpoints: between_stages
- validation: deliverable_based
- reporting: stage_report

### task-checkpoints
- checkpoints: after_tasks
- validation: completion_based
- reporting: task_report

---

## 自定义进度跟踪 (Custom Progress Tracking)

### basic-tracking
- metrics: [completion_percentage]
- reporting: manual
- visualization: text
- alerts: none

### standard-tracking
- metrics: [completion_percentage, time_remaining, blockages]
- reporting: automatic
- visualization: progress_bar
- alerts: on_blockage

### comprehensive-tracking
- metrics: [completion_percentage, time_remaining, blockages, resources, risks]
- reporting: real_time
- visualization: dashboard
- alerts: multiple_triggers

---

## 自定义错误处理 (Custom Error Handling)

### fail-fast
- strategy: stop_on_error
- reporting: immediate
- recovery: manual
- rollback: none

### continue-on-error
- strategy: log_and_continue
- reporting: deferred
- recovery: attempt_continue
- rollback: optional

### retry-with-backoff
- strategy: retry
- reporting: accumulated
- recovery: exponential_backoff
- rollback: after_max_retries

---

## 自定义资源分配 (Custom Resource Allocation)

### time-boxing
- resource: time
- allocation: per_stage
- tracking: timer
- overflow: requires_approval

### task-pooling
- resource: parallel_tasks
- allocation: dynamic
- tracking: utilization
- overflow: queue

### budget-allocation
- resource: budget
- allocation: per_stage
- tracking: spent_vs_budget
- overflow: requires_approval

---

## 自定义依赖管理 (Custom Dependency Management)

### sequential-dependencies
- type: sequential
- validation: pre_execution
- blocking: strict
- visualization: linear

### parallel-dependencies
- type: parallel
- validation: pre_execution
- blocking: none
- visualization: dag

### conditional-dependencies
- type: conditional
- validation: runtime
- blocking: conditional
- visualization: dynamic

---

## 自定义验证标准 (Custom Validation Criteria)

### output-validation
- criteria: deliverable_based
- strictness: moderate
- owner: executor
- approval: automatic

### quality-validation
- criteria: quality_standards
- strictness: high
- owner: reviewer
- approval: required

### sign-off-validation
- criteria: stakeholder_approval
- strictness: very_high
- owner: stakeholders
- approval: consensus

---

## 自定义报告格式 (Custom Reporting Format)

### minimal-report
- sections: [status, progress, blockers]
- detail_level: summary
- frequency: milestone
- audience: team

### standard-report
- sections: [status, progress, blockers, metrics, next_steps]
- detail_level: moderate
- frequency: checkpoint
- audience: team + stakeholders

### comprehensive-report
- sections: [status, progress, blockers, metrics, risks, decisions, lessons_learned, next_steps]
- detail_level: detailed
- frequency: daily
- audience: team + stakeholders + management

---

## 自定义通信协议 (Custom Communication Protocol)

### synchronous-communication
- method: meetings
- frequency: daily
- participants: core_team
- recording: minutes

### asynchronous-communication
- method: async_updates
- frequency: real_time
- participants: all
- recording: logs

### hybrid-communication
- method: mixed
- frequency: milestone_based
- participants: varied
- recording: comprehensive

---

## 自定义适应策略 (Custom Adaptation Strategy)

### rigid-plan
- flexibility: none
- changes: blocked
- approval: required
- impact: full_replan

### flexible-plan
- flexibility: moderate
- changes: allowed_with_reason
- approval: automatic_for_minor
- impact: partial_replan

### agile-plan
- flexibility: high
- changes: encouraged
- approval: automatic
- impact: incremental_update

---

## 自定义回顾机制 (Custom Review Mechanism)

### milestone-review
- frequency: at_milestones
- participants: all
- format: retrospective
- action_items: documented

### stage-review
- frequency: between_stages
- participants: relevant_team
- format: checkpoint_meeting
- action_items: documented

### post-mortem
- frequency: on_completion
- participants: all
- format: lessons_learned
- action_items: archived

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/executing-plans/EXTEND.md`
- **用户级**: `~/.claude/skills/executing-plans/EXTEND.md`
- **默认级**: `skills/executing-plans/EXTEND.md`

---

## 使用示例

### 快速任务执行
```markdown
## Quick Task Execution

### quick-execution
- mode: autonomous-mode
- stages: minimal-stages
- checkpoints: no-checkpoints
- tracking: basic-tracking
- error_handling: continue-on-error
- resources: time-boxing
- dependencies: parallel-dependencies
- validation: output-validation
- reports: minimal-report
- communication: asynchronous-communication
- adaptation: agile-plan
- reviews: post-mortem
```

### 标准项目执行
```markdown
## Standard Project Execution

### standard-execution
- mode: semi-autonomous-mode
- stages: standard-stages
- checkpoints: milestone-checkpoints
- tracking: standard-tracking
- error_handling: retry-with-backoff
- resources: time-boxing + task-pooling
- dependencies: parallel-dependencies
- validation: quality-validation
- reports: standard-report
- communication: hybrid-communication
- adaptation: flexible-plan
- reviews: milestone-review + stage-review
```

### 企业级执行
```markdown
## Enterprise Execution

### enterprise-execution
- mode: interactive-mode
- stages: granular-stages
- checkpoints: task-checkpoints
- tracking: comprehensive-tracking
- error_handling: fail-fast
- resources: budget-allocation + task-pooling
- dependencies: conditional-dependencies
- validation: sign-off-validation
- reports: comprehensive-report
- communication: synchronous-communication
- adaptation: agile-plan
- reviews: all_reviews
```
