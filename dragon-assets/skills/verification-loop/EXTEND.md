# Verification Loop EXTEND.md

## 默认验证循环配置

---

## 自定义验证类型 (Custom Verification Type)

### semantic-verification
- focus: meaning_preservation
- method: llm_evaluation
- threshold: semantic_similarity
- feedback: qualitative

### functional-verification
- focus: behavior_equivalence
- method: test_execution
- threshold: pass_rate
- feedback: quantitative

### formal-verification
- focus: logical_correctness
- method: proof_checking
- threshold: zero_bugs
- feedback: mathematical

---

## 自定义循环策略 (Custom Loop Strategy)

### single-pass
- iterations: 1
- feedback: none
- adaptation: static
- termination: after_verification

### iterative-loop
- iterations: fixed_n
- feedback: incorporated
- adaptation: incremental
- termination: after_n_iterations

### adaptive-loop
- iterations: until_satisfied
- feedback: continuous
- adaptation: dynamic
- termination: convergence_criteria

---

## 自定义评估指标 (Custom Evaluation Metrics)

### correctness-metric
- dimension: accuracy
- measurement: [precision, recall, f1]
- threshold: 0.9
- weight: 1.0

### efficiency-metric
- dimension: resource_usage
- measurement: [time, memory, cost]
- threshold: acceptable
- weight: 0.5

### robustness-metric
- dimension: error_handling
- measurement: [recovery, degradation]
- threshold: graceful
- weight: 0.7

---

## 自定义样本策略 (Custom Sampling Strategy)

### deterministic-sample
- selection: fixed_set
- size: representative
- reproducibility: high
- coverage: controlled

### random-sample
- selection: probability_based
- size: statistically_significant
- reproducibility: seed_dependent
- coverage: probabilistic

### adaptive-sample
- selection: uncertainty_driven
- size: dynamic
- reproducibility: conditioned
- coverage: efficient

---

## 自定义置信区间 (Custom Confidence Interval)

### point-estimate
- method: single_value
- interval: none
- confidence: not_measured
- interpretation: deterministic

### frequentist-ci
- method: bootstrap
- interval: percentile_based
- confidence: 95%
- interpretation: long_run_frequency

### bayesian-ci
- method: posterior
- interval: credible_region
- confidence: posterior_mass
- interpretation: degree_of_belief

---

## 自定义基线比较 (Custom Baseline Comparison)

### no-baseline
- comparison: none
- reference: absolute
- improvement: not_measured
- reporting: standalone

### simple-baseline
- comparison: against_previous
- reference: historic
- improvement: delta_reported
- reporting: relative_change

### competitive-baseline
- comparison: against_alternatives
- reference: state_of_art
- improvement: ranking
- reporting: benchmark_position

---

## 自定义停止条件 (Custom Stopping Condition)

### fixed-stops
- condition: max_iterations
- value: predetermined
- flexibility: none
- optimization: none

### threshold-stops
- condition: target_met
- value: quality_threshold
- flexibility: adaptive
- optimization: early_termination

### convergence-stops
- condition: diminishing_returns
- value: minimal_improvement
- flexibility: dynamic
- optimization: resource_optimized

---

## 自定义历史记录 (Custom History Tracking)

### current-state-only
- storage: volatile
- history: discarded
- comparison: none
- learning: none

### sliding-window
- storage: ring_buffer
- history: recent_n_iterations
- comparison: windowed_trends
- learning: short_term_patterns

### full-history
- storage: persistent_log
- history: complete_trajectory
- comparison: longitudinal
- learning: lifelong_adaptation

---

## 自定义可视化 (Custom Visualization)

### text-summary
- format: plain_text
- detail: key_metrics
- interactivity: none
- update_frequency: final_only

### progress-chart
- format: line_graph
- detail: metric_over_time
- interactivity: zoom_hover
- update_frequency: real_time

### dashboard
- format: multi_panel
- detail: comprehensive_view
- interactivity: drill_down
- update_frequency: live_stream

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/verification-loop/EXTEND.md`
- **用户级**: `~/.claude/skills/verification-loop/EXTEND.md`
- **默认级**: `skills/verification-loop/EXTEND.md`

---

## 使用示例

### 快速语义验证
```markdown
## Quick Semantic Verification

### quick-semantic
- type: semantic-verification
- loop: single-pass
- metrics: correctness-metric
- sampling: deterministic-sample
- confidence: point-estimate
- baseline: no-baseline
- stopping: fixed-stops
- history: current-state-only
- visualization: text-summary
```

### 迭代功能测试
```markdown
## Iterative Functional Testing

### iterative-functional
- type: functional-verification
- loop: iterative-loop
- metrics: [correctness, efficiency]
- sampling: random-sample
- confidence: frequentist-ci
- baseline: simple-baseline
- stopping: threshold-stops
- history: sliding-window
- visualization: progress-chart
```

### 自适应质量保证
```markdown
## Adaptive Quality Assurance

### adaptive-qa
- type: hybrid-verification
- loop: adaptive-loop
- metrics: all_metrics
- sampling: adaptive-sample
- confidence: bayesian-ci
- baseline: competitive-baseline
- stopping: convergence-stops
- history: full-history
- visualization: dashboard
```
