# Eval Harness EXTEND.md

## 默认评估框架配置

---

## 自定义测试类型 (Custom Test Types)

### unit-tests
- scope: function_level
- isolation: fully_mocked
- speed: milliseconds
- resources: minimal

### integration-tests
- scope: module_boundary
- isolation: partial_mocking
- speed: seconds
- resources: moderate

### e2e-tests
- scope: full_system
- isolation: real_dependencies
- speed: minutes
- resources: significant

---

## 自定义断言策略 (Custom Assertion Strategy)

### exact-match
- comparison: strict_equality
- tolerance: zero
- semantic: value_based
- feedback: binary

### fuzzy-match
- comparison: approximate
- tolerance: configurable_epsilon
- semantic: meaning_based
- feedback: graded

### semantic-match
- comparison: intent_based
- tolerance: context_aware
- semantic: understanding
- feedback: explanatory

---

## 自定义测试数据 (Custom Test Data)

### static-fixtures
- source: hardcoded_values
- variety: single_scenario
- management: version_controlled
- isolation: none

### parametrized
- source: data_driven
- variety: multiple_scenarios
- management: table_based
- isolation: test_independent

### generated-fixtures
- source: programmatic_generation
- variety: comprehensive_coverage
- management: algorithmic
- isolation: fully_isolated

---

## 自定义覆盖率要求 (Custom Coverage Requirements)

### no-coverage
- threshold: 0%
- metrics: none
- enforcement: disabled
- reporting: none

### standard-coverage
- threshold: 80%
- metrics: [line, branch, function]
- enforcement: ci_gate
- reporting: summary_report

### strict-coverage
- threshold: 95%
- metrics: [line, branch, function, condition, path]
- enforcement: blocking
- reporting: detailed_report

### mutation-coverage
- threshold: mutation_score
- metrics: [code_coverage, mutation_killed]
- enforcement: strict
- reporting: mutation_analysis

---

## 自定义性能基准 (Custom Performance Benchmarks)

### no-benchmarks
- enabled: false
- metrics: none
- baseline: none
- regression: none

### basic-benchmarks
- enabled: true
- metrics: [execution_time, memory]
- baseline: historical_average
- regression: percentage_threshold

### advanced-benchmarks
- enabled: true
- metrics: [cpu, memory, io, network]
- baseline: profiled_optimal
- regression: statistical_control

---

## 自定义测试执行 (Custom Test Execution)

### serial-execution
- mode: sequential
- parallelism: 1_worker
- resources: minimal
- duration: longest_test_total

### parallel-execution
- mode: concurrent
- parallelism: cpu_cores
- resources: scaled
- duration: critical_path_optimized

### distributed-execution
- mode: sharded
- parallelism: multi_agent
- resources: elastic
- duration: linear_speedup

---

## 自定义环境配置 (Custom Environment Config)

### single-env
- stages: production_like
- data: anonymized_production
- state: clean_per_test
- reset: full_rebuild

### multi-env
- stages: [dev, staging, prod]
- data: stage_specific
- state: isolated_per_stage
- reset: smart_rollback

### dynamic-env
- stages: on_demand
- data: programmatically_configured
- state: containerized
- reset: container_recreation

---

## 自定义失败处理 (Custom Failure Handling)

### fail-fast
- strategy: stop_on_first_failure
- debugging: immediate_context
- recovery: manual_intervention
- reporting: crash_dump

### continue-on-fail
- strategy: complete_all_tests
- debugging: deferred_analysis
- recovery: none
- reporting: aggregated_summary

### retry-fail
- strategy: retry_then_fail
- debugging: attempt_history
- recovery: automatic_retry
- reporting: flaky_detection

---

## 自定义报告格式 (Custom Report Format)

### console-output
- format: text_dots
- detail: pass_fail_only
- visualization: progress_bar
- export: none

### html-report
- format: interactive_html
- detail: full_context
- visualization: charts_graphs
- export: static_html

### json-report
- format: structured_json
- detail: machine_readable
- visualization: none
- export: ci_integrated

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/eval-harness/EXTEND.md`
- **用户级**: `~/.claude/skills/eval-harness/EXTEND.md`
- **默认级**: `skills/eval-harness/EXTEND.md`

---

## 使用示例

### 快速单元测试
```markdown
## Quick Unit Tests

### quick-unit
- type: unit-tests
- assertions: exact-match
- data: static-fixtures
- coverage: no-coverage
- benchmarks: no-benchmarks
- execution: serial-execution
- environment: single-env
- failures: fail-fast
- reports: console-output
```

### 全面集成测试
```markdown
## Comprehensive Integration Tests

### comprehensive-integration
- type: integration-tests
- assertions: fuzzy-match
- data: parametrized
- coverage: standard-coverage
- benchmarks: basic-benchmarks
- execution: parallel-execution
- environment: multi-env
- failures: continue-on-fail
- reports: html-report
```

### 严格E2E测试套件
```markdown
## Strict E2E Test Suite

### strict-e2e
- type: e2e-tests
- assertions: semantic-match
- data: generated-fixtures
- coverage: mutation-coverage
- benchmarks: advanced-benchmarks
- execution: distributed-execution
- environment: dynamic-env
- failures: retry-fail
- reports: json-report
```
