# Test Driven Development EXTEND.md

## 默认TDD配置

---

## 自定义测试顺序 (Custom Test Order)

### classic-tdd
- order: red_first
- cycle: test_code_refactor
- emphasis: failing_test
- validation: continuous

### test-last
- order: implementation_first
- cycle: code_test_refactor
- emphasis: working_code
- validation: deferred

### alternative-tdd
- order: fake_first
- cycle: fake_test_real_refactor
- emphasis: interface_design
- validation: incremental

---

## 自定义测试粒度 (Custom Test Granularity)

### unit-only
- scope: single_function
- isolation: fully_mocked
- speed: fast
- confidence: low

### integration-first
- scope: component_boundary
- isolation: partial_mocking
- speed: moderate
- confidence: medium

### atdd-style
- scope: user_behavior
- isolation: real_dependencies
- speed: slower
- confidence: high

---

## 自定义重构触发 (Custom Refactoring Trigger)

### test-pass
- trigger: after_green
- frequency: every_cycle
- scope: focused_clean
- confidence: protected_by_tests

### periodic-refactor
- trigger: scheduled
- frequency: after_n_features
- scope: comprehensive
- confidence: manual_review

### urgent-refactor
- trigger: code_smell
- frequency: as_needed
- scope: targeted
- confidence: risk_assessed

---

## 自定义测试隔离 (Custom Test Isolation)

### no-isolation
- method: in_order
- state: shared
- speed: fastest
- flakiness: high

### method-isolation
- method: test_order_randomization
- state: reset_per_test
- speed: moderate
- flakiness: reduced

### full-isolation
- method: test_suites_parallel
- state: sandboxed
- speed: slower_startup
- flakiness: minimal

---

## 自定义断言风格 (Custom Assertion Style)

### simple-assertions
- style: equality_checks
- messages: minimal
- debugging: basic
- framework: jest_style

### behavioral-assertions
- style: given_when_then
- messages: descriptive
- debugging: scenario_based
- framework: cucumber_style

### property-assertions
- style: invariants
- messages: algebraic
- debugging: formal
- framework: quickcheck_style

---

## 自定义测试数据 (Custom Test Data)

### hardcoded-data
- source: literal_values
- variety: single_scenario
- maintenance: inline
- realism: low

### fixture-data
- source: test_fixtures
- variety: multiple_scenarios
- maintenance: separate_files
- realism: medium

### generated-data
- source: property_based
- variety: infinite_combinations
- maintenance: generators
- realism: high

---

## 自定义覆盖率目标 (Custom Coverage Goals)

### no-coverage
- target: 0%
- enforcement: none
- reporting: disabled
- blocking: false

### standard-coverage
- target: 80%
- enforcement: ci_gate
- reporting: summary
- blocking: true

### strict-coverage
- target: 95%
- enforcement: blocking_commit
- reporting: detailed
- blocking: true

### mutation-coverage
- target: mutation_score
- enforcement: strict
- reporting: mutation_analysis
- blocking: true

---

## 自定义CI集成 (Custom CI Integration)

### local-only
- runner: local_developer
- triggers: manual
- reporting: console
- artifacts: none

### basic-ci
- runner: github_actions
- triggers: on_push
- reporting: status_badges
- artifacts: test_results

### full-pipeline
- runner: custom_orchestrated
- triggers: [commit, pr, schedule]
- reporting: comprehensive_dashboards
- artifacts: multi_format_reports

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/test-driven-development/EXTEND.md`
- **用户级**: `~/.claude/skills/test-driven-development/EXTEND.md`
- **默认级**: `skills/test-driven-development/EXTEND.md`

---

## 使用示例

### 快速原型TDD
```markdown
## Quick Prototype TDD

### prototype-tdd
- order: alternative-tdd
- granularity: unit-only
- refactor: test-pass
- isolation: no-isolation
- assertions: simple-assertions
- data: hardcoded-data
- coverage: no-coverage
- ci: local-only
```

### 标准TDD流程
```markdown
## Standard TDD Flow

### standard-tdd
- order: classic-tdd
- granularity: integration-first
- refactor: test-pass
- isolation: method-isolation
- assertions: behavioral-assertions
- data: fixture-data
- coverage: standard-coverage
- ci: basic-ci
```

### 严格企业TDD
```markdown
### strict-enterprise-tdd
- order: classic-tdd
- granularity: atdd-style
- refactor: periodic-refactor
- isolation: full-isolation
- assertions: property-assertions
- data: generated-data
- coverage: mutation-coverage
- ci: full-pipeline
```
