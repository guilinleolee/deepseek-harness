# Testing Patterns EXTEND.md

## 默认测试模式配置

---

## 自定义测试类型 (Custom Test Type)

### unit-only
- scope: individual_functions
- isolation: fully_mocked
- speed: fast
- confidence: low

### integration-focused
- scope: component_interaction
- isolation: partial_real_dependencies
- speed: moderate
- confidence: medium

### e2e-tests
- scope: complete_user_flows
- isolation: real_environment
- speed: slow
- confidence: high

---

## 自定义测试组织 (Custom Test Organization)

### flat-structure
- organization: single_file_or_folder
- nesting: none
- grouping: by_test_name
- maintenance: difficult_at_scale

### feature-based
- organization: by_feature_module
- nesting: one_level
- grouping: logical_functionality
- maintenance: moderate

### layer-based
- organization: by_architecture_layer
- nesting: multi_level
- grouping: unit_integration_e2e
- maintenance: good

---

## 自定义命名约定 (Custom Naming Convention)

### descriptive-names
- format: should_expected_behavior_when_state
- consistency: high
- readability: excellent
- automation: difficult

### compact-names
- format: short_descriptive
- consistency: moderate
- readability: good
- automation: possible

### pattern-based-names
- format: follows_test_pattern
- consistency: excellent
- readability: requires_learning
- automation: excellent

---

## 自定义断言风格 (Custom Assertion Style)

### simple-assertions
- style: equality_truthy_checks
- messages: generic
- debugging: basic
- framework: jest_like

### behavioral-assertions
- style: given_when_then
- messages: scenario_based
- debugging: story_driven
- framework: cucumber_like

### property-assertions
- style: invariant_based
- messages: mathematical
- debugging: formal
- framework: quickcheck_like

---

## 自定义夹具管理 (Custom Fixture Management)

### no-fixtures
- setup: inline_creation
- sharing: none
- maintenance: repetitive
- consistency: low

### simple-fixtures
- setup: helper_functions
- sharing: within_test_file
- maintenance: moderate
- consistency: medium

### advanced-fixtures
- setup: fixture_factories
- sharing: global_registry
- maintenance: centralized
- consistency: high

---

## 自定义模拟策略 (Custom Mocking Strategy)

### no-mocking
- approach: use_real_dependencies
- control: none
- speed: actual_speed
- complexity: simplest

### selective-mocking
- approach: mock_external_only
- control: partial
- speed: improved
- complexity: moderate

### heavy-mocking
- approach: mock_most_dependencies
- control: extensive
- speed: fastest
- complexity: high

---

## 自定义覆盖率目标 (Custom Coverage Goals)

### no-coverage
- target: not_measured
- enforcement: none
- reporting: absent
- blocking: false

### basic-coverage
- target: 70_80_percent
- enforcement: ci_warning
- reporting: summary
- blocking: false

### strict-coverage
- target: 90_95_percent
- enforcement: ci_blocking
- reporting: detailed_per_file
- blocking: true

### mutation-coverage
- target: mutation_score_above_80
- enforcement: strict
- reporting: mutation_analysis_report
- blocking: true

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/testing-patterns/EXTEND.md`
- **用户级**: `~/.claude/skills/testing-patterns/EXTEND.md`
- **默认级**: `skills/testing-patterns/EXTEND.md`

---

## 使用示例

### 快速单元测试
```markdown
## Quick Unit Tests

### quick-unit
- type: unit-only
- organization: flat-structure
- naming: compact-names
- assertions: simple-assertions
- fixtures: no-fixtures
- mocking: no-mocking
- coverage: no-coverage
```

### 标准测试套件
```markdown
## Standard Test Suite

### standard-suite
- type: integration-focused
- organization: feature-based
- naming: descriptive-names
- assertions: behavioral-assertions
- fixtures: simple-fixtures
- mocking: selective-mocking
- coverage: basic-coverage
```

### 企业级测试
```markdown
## Enterprise Testing

### enterprise-testing
- type: e2e-tests
- organization: layer-based
- naming: pattern-based-names
- assertions: property-assertions
- fixtures: advanced-fixtures
- mocking: heavy-mocking
- coverage: mutation-coverage
```
