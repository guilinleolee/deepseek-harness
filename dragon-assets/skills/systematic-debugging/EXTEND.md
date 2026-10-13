# Systematic Debugging EXTEND.md

## 默认系统化调试配置

---

## 自定义调试策略 (Custom Debugging Strategy)

### binary-search
- method: divide_conquer
- scope: narrowing
- iterations: logarithmic
- efficiency: high

### incremental-isolation
- method: remove_until_works
- scope: systematic_reduction
- iterations: linear
- efficiency: moderate

### hypothesis-testing
- method: scientific_method
- scope: theory_driven
- iterations: variable
- efficiency: knowledge_dependent

---

## 自定义问题分类 (Custom Problem Classification)

### symptom-based
- categorization: observed_behavior
- diagnosis: symptom_treatment
- root_cause: not_pursued
- prevention: none

### root-cause-analysis
- categorization: underlying_cause
- diagnosis: five_whys
- root_cause: identified
- prevention: addressed

### fault-tree-analysis
- categorization: hierarchical_decomposition
- diagnosis: systematic_elimination
- root_cause: mapped
- prevention: comprehensive

---

## 自定义日志级别 (Custom Logging Level)

### minimal-logging
- output: critical_only
- detail: none
- context: absent
- performance: minimal_impact

### standard-logging
- output: error_warnings_info
- detail: relevant_context
- context: included
- performance: moderate_impact

### verbose-logging
- output: all_levels_with_trace
- detail: exhaustive
- context: complete
- performance: significant_impact

---

## 自定义断言策略 (Custom Assertion Strategy)

### no-assertions
- runtime_checks: none
- assumptions: unchecked
- failures: silent
- debugging: difficult

### critical-assertions
- runtime_checks: key_invariants_only
- assumptions: minimal_validation
- failures: alert_only
- debugging: moderate

### comprehensive-assertions
- runtime_checks: extensive
- assumptions: validated
- failures: detailed_stack_traces
- debugging: supported

---

## 自定义回滚机制 (Custom Rollback Mechanism)

### no-rollback
- state_changes: immediate_permanent
- recovery: manual_restore
- history: not_tracked
- safety: low

### checkpoint-rollback
- state_changes: marked_checkpoints
- recovery: restore_to_checkpoint
- history: checkpoint_log
- safety: medium

### step-by-step-rollback
- state_changes: reversible_steps
- recovery: undo_any_step
- history: complete_history
- safety: high

---

## 自定义隔离技术 (Custom Isolation Technique)

### no-isolation
- environment: shared
- dependencies: all_loaded
- reproducibility: low
- confidence: low

### minimal-isolation
- environment: partially_isolated
- dependencies: selected_loading
- reproducibility: medium
- confidence: medium

### full-isolation
- environment: sandboxed
- dependencies: controlled
- reproducibility: high
- confidence: high

---

## 自定义分析工具 (Custom Analysis Tools)

### manual-analysis
- tools: human_reasoning
- automation: none
- depth: surface
- speed: slow

### basic-tools
- tools: debuggers_printers
- automation: minimal
- depth: moderate
- speed: moderate

### advanced-tools
- tools: profilers_tracers_static_analysis
- automation: extensive
- depth: deep
- speed: fast

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/systematic-debugging/EXTEND.md`
- **用户级**: `~/.claude/skills/systematic-debugging/EXTEND.md`
- **默认级**: `skills/systematic-debugging/EXTEND.md`

---

## 使用示例

### 快速修复
```markdown
## Quick Fix

### quick-fix
- strategy: binary-search
- classification: symptom-based
- logging: minimal-logging
- assertions: no-assertions
- rollback: no-rollback
- isolation: no-isolation
- tools: manual-analysis
```

### 标准调试
```markdown
## Standard Debugging

### standard-debugging
- strategy: incremental-isolation
- classification: root-cause-analysis
- logging: standard-logging
- assertions: critical-assertions
- rollback: checkpoint-rollback
- isolation: minimal-isolation
- tools: basic-tools
```

### 深度分析
```markdown
## Deep Analysis

### deep-analysis
- strategy: hypothesis-testing
- classification: fault-tree-analysis
- logging: verbose-logging
- assertions: comprehensive-assertions
- rollback: step-by-step-rollback
- isolation: full-isolation
- tools: advanced-tools
```
