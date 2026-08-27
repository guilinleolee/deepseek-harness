# TDD Workflow EXTEND.md

## 默认 TDD 配置

---

## 自定义测试策略 (Custom Test Strategy)

### red-green-refactor
- cycle: strict
- test_first: mandatory
- minimal_implementation: true
- refactoring_frequency: every_pass
- coverage_target: 80%

### test-driven
- cycle: standard
- test_first: mandatory
- minimal_implementation: false
- refactoring_frequency: every_feature
- coverage_target: 90%

### test-supported
- cycle: flexible
- test_first: optional
- minimal_implementation: false
- refactoring_frequency: as_needed
- coverage_target: 70%

---

## 自定义测试类型 (Custom Test Types)

### unit-focused
- unit_tests: required
- integration_tests: optional
- e2e_tests: none
- performance_tests: none

### full-coverage
- unit_tests: required
- integration_tests: required
- e2e_tests: critical_path_only
- performance_tests: none

### comprehensive
- unit_tests: required
- integration_tests: required
- e2e_tests: required
- performance_tests: critical_path_only
- security_tests: required

---

## 自定义断言库 (Custom Assertion Libraries)

### jest-native
- library: jest
- style: expect().toBe()
- async_handling: async/await
- snapshot_testing: enabled

### vitest-modern
- library: vitest
- style: expect().toEqual()
- async_handling: async/await
- snapshot_testing: enabled
- watch_mode: true

### chai-bdd
- library: chai
- style: expect().to.be.a()
- async_handling: promises
- snapshot_testing: disabled

---

## 自定义测试组织 (Custom Test Organization)

### flat-structure
- organization: flat
- naming: {source}.test.{ext}
- co_location: same_directory
- fixtures: inline

### by-feature
- organization: feature_based
- naming: {feature}/{scenario}.test.{ext}
- co_location: separate_directory
- fixtures: shared

### by-layer
- organization: layer_based
- naming: {layer}/{component}.test.{ext}
- co_location: parallel_structure
- fixtures: layer_specific

---

## 自定义测试数据 (Custom Test Data)

### inline-data
- strategy: inline
- fixtures: hardcoded
- factories: none
- fakers: none

### factory-based
- strategy: factory
- fixtures: factory_generated
- factories: factory_bot
- fakers: faker

### scenario-based
- strategy: scenarios
- fixtures: predefined_scenarios
- factories: custom
- fakers: faker
- seed_data: consistent

---

## 自定义模拟策略 (Custom Mocking Strategy)

### no-mocking
- mocks: avoid
- stubs: minimal
- spies: none
- real_dependencies: preferred

### selective-mocking
- mocks: external_services
- stubs: slow_operations
- spies: critical_functions
- real_dependencies: internal

### heavy-mocking
- mocks: all_external
- stubs: deterministic_results_needed
- spies: function_calls_verification
- real_dependencies: none

---

## 自定义覆盖率配置 (Custom Coverage Config)

### basic-coverage
- threshold: 70%
- report: summary
- per_file: false
- branch_coverage: false

### strict-coverage
- threshold: 90%
- report: detailed
- per_file: true
- branch_coverage: true
- enforce: true

### exhaustive-coverage
- threshold: 95%
- report: html + lcov + console
- per_file: true
- branch_coverage: true
- line_coverage: true
- function_coverage: true
- enforce: true
- diff_coverage: true

---

## 自定义 CI/CD 集成 (Custom CI/CD Integration)

### github-actions
- platform: github_actions
- trigger: [push, pull_request]
- parallel_jobs: 4
- coverage_report: automatic
- fail_on_error: true

### gitlab-ci
- platform: gitlab_ci
- trigger: [push, merge_request]
- parallel_jobs: 4
- coverage_report: automatic
- fail_on_error: true

### jenkins
- platform: jenkins
- trigger: scm_poll
- parallel_jobs: 2
- coverage_report: manual
- fail_on_error: true

---

## 自定义测试运行配置 (Custom Test Runner Config)

### watch-mode
- watch: true
- rerun_on_change: true
- related_files: true
- notification: desktop

### single-run
- watch: false
- rerun_on_change: false
- related_files: false
- notification: none

### ci-mode
- watch: false
- rerun_on_change: false
- related_files: false
- max_workers: cpu_cores
- coverage: always
- report: junit + cobertura

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/tdd-workflow/EXTEND.md`
- **用户级**: `~/.claude/skills/tdd-workflow/EXTEND.md`
- **默认级**: `skills/tdd-workflow/EXTEND.md`

---

## 使用示例

### 快速原型项目
```markdown
## Quick Prototype

### prototype-tdd
- strategy: test-supported
- tests: unit-focused
- library: vitest-modern
- organization: flat-structure
- data: inline-data
- mocking: no-mocking
- coverage: basic-coverage
- runner: watch-mode
```

### 标准项目
```markdown
## Standard Project

### standard-tdd
- strategy: test-driven
- tests: full-coverage
- library: jest-native
- organization: by-feature
- data: factory-based
- mocking: selective-mocking
- coverage: strict-coverage
- ci: github-actions
- runner: single-run
```

### 企业级项目
```markdown
## Enterprise Project

### enterprise-tdd
- strategy: red-green-refactor
- tests: comprehensive
- library: jest-native
- organization: by-layer
- data: scenario-based
- mocking: selective-mocking
- coverage: exhaustive-coverage
- ci: github-actions
- runner: ci-mode
```
