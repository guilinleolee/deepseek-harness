# Validation Loop EXTEND.md

## 默认验证循环配置

---

## 自定义验证模式 (Custom Validation Mode)

### pass@k
- metric: at_least_one_success
- evaluation: k_trials
- success: 1+_success
- reporting: pass_rate

### pass^k
- metric: all_success
- evaluation: k_trials
- success: 100%_success
- reporting: strict_pass

### hybrid-validation
- metric: weighted_score
- evaluation: k_trials
- success: threshold_based
- reporting: confidence_interval

---

## 自定义样本大小 (Custom Sample Size)

### minimal-sampling
- trials: n=3
- confidence: low
- duration: quick
- cost: minimal

### standard-sampling
- trials: n=10
- confidence: medium
- duration: moderate
- cost: balanced

### rigorous-sampling
- trials: n=100
- confidence: high
- duration: extensive
- cost: significant

### adaptive-sampling
- trials: sequential
- confidence: dynamic
- duration: optimized
- cost: efficient

---

## 自定义失败分析 (Custom Failure Analysis)

### count-only
- depth: pass_fail_count
- categorization: none
- root_cause: not_analyzed
- patterns: undetected

### categorized-failures
- depth: error_types
- categorization: predefined_buckets
- root_cause: surface_level
- patterns: basic_detection

### deep-analysis
- depth: full_taxonomy
- categorization: multi_dimensional
- root_cause: investigated
- patterns: advanced_detection

---

## 自定义迭代策略 (Custom Iteration Strategy)

### fixed-iterations
- approach: n_trials_fixed
- adaptation: none
- stopping: after_n_trials
- learning: no_feedback

### adaptive-iterations
- approach: sequential_testing
- adaptation: based_on_results
- stopping: confidence_achieved
- learning: continuous_improvement

### bayesian-iterations
- approach: bayesian_update
- adaptation: posterior_based
- stopping: posterior_threshold
- learning: probabilistic_reasoning

---

## 自定义成本控制 (Custom Cost Control)

### unlimited-budget
- cap: none
- prioritization: none
- optimization: not_required
- tracking: total_only

### fixed-budget
- cap: trial_limit
- prioritization: early_tests_first
- optimization: optional
- tracking: per_trial

### smart-budget
- cap: value_optimized
- prioritization: roi_based
- optimization: early_stopping
- tracking: real_time

---

## 自定义并行执行 (Custom Parallel Execution)

### serial-validation
- mode: sequential
- resource: minimal
- speed: slowest_path
- coordination: none

### parallel-validation
- mode: concurrent
- resource: scaled
- speed: linear_speedup
- coordination: result_aggregation

### distributed-validation
- mode: multi_agent
- resource: elastic
- speed: optimal
- coordination: complex_orchestration

---

## 自定义多样性保证 (Custom Diversity Assurance)

### single-method
- approach: one_technique
- variety: none
- robustness: method_specific
- comparison: baseline_only

### multi-method
- approach: multiple_techniques
- variety: complementary
- robustness: cross_validated
- comparison: method_comparison

### ensemble-method
- approach: combined_techniques
- variety: diverse
- robustness: consensus_driven
- comparison: weighted_voting

---

## 自定义报告粒度 (Custom Reporting Granularity)

### summary-only
- detail: high_level
- metrics: pass_rate_only
- trends: none
- recommendations: generic

### standard-reporting
- detail: moderate
- metrics: comprehensive
- trends: basic_visualization
- recommendations: specific

### detailed-reporting
- detail: exhaustive
- metrics: all_available
- trends: advanced_analytics
- recommendations: actionable

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/validation-loop/EXTEND.md`
- **用户级**: `~/.claude/skills/validation-loop/EXTEND.md`
- **默认级**: `skills/validation-loop/EXTEND.md`

---

## 使用示例

### 快速原型验证
```markdown
## Quick Prototype Validation

### quick-prototype
- mode: pass@k
- sampling: minimal-sampling
- failures: count-only
- iterations: fixed-iterations
- cost: unlimited-budget
- execution: serial-validation
- diversity: single-method
- reporting: summary-only
```

### 标准功能测试
```markdown
## Standard Feature Testing

### standard-testing
- mode: pass^k
- sampling: standard-sampling
- failures: categorized-failures
- iterations: adaptive-iterations
- cost: fixed-budget
- execution: parallel-validation
- diversity: multi-method
- reporting: standard-reporting
```

### 严格质量保证
```markdown
## Strict Quality Assurance

### strict-qa
- mode: hybrid-validation
- sampling: rigorous-sampling
- failures: deep-analysis
- iterations: bayesian-iterations
- cost: smart-budget
- execution: distributed-validation
- diversity: ensemble-method
- reporting: detailed-reporting
```
