# Webapp Testing EXTEND.md

## 默认 Web 应用测试配置

---

## 自定义测试类型 (Custom Test Types)

### smoke-tests
- scope: critical_paths
- depth: shallow
- coverage: happy_path_only
- duration: quick

### integration-tests
- scope: user_flows
- depth: moderate
- coverage: main_scenarios
- duration: standard

### e2e-tests
- scope: full_journeys
- depth: comprehensive
- coverage: all_scenarios
- duration: extended

---

## 自定义浏览器选择 (Custom Browser Selection)

### chromium-only
- browsers: [chromium]
- channels: stable
- versions: latest
- parallel: single

### modern-browsers
- browsers: [chromium, firefox, webkit]
- channels: stable
- versions: latest_minus_1
- parallel: 3_instances

### cross-browser
- browsers: all_browsers
- channels: [stable, beta]
- versions: multiple_versions
- parallel: max_parallel

---

## 自定义元素定位 (Custom Element Locators)

### id-only
- strategy: by_id
- fallback: none
- waiting: fixed
- fragility: high

### robust-locators
- strategy: data_test_id
- fallback: role_text
- waiting: smart_wait
- fragility: low

### ai-locators
- strategy: semantic_understanding
- fallback: multiple_strategies
- waiting: adaptive
- fragility: minimal

---

## 自定义等待策略 (Custom Waiting Strategy)

### fixed-waits
- type: hard_coded
- duration: 5_seconds
- condition: none
- reliability: low

### explicit-waits
- type: wait_for_selector
- duration: 30_seconds
- condition: element_visible
- reliability: high

### smart-waits
- type: auto_waiting
- duration: adaptive
- condition: actionable
- reliability: maximum

---

## 自定义断言策略 (Custom Assertion Strategy)

### basic-assertions
- checks: visibility_only
- tolerance: exact_match
- snapshot: none
- validation: minimal

### standard-assertions
- checks: [visibility, text, attributes]
- tolerance: partial_match
- snapshot: visual_snapshots
- validation: comprehensive

### advanced-assertions
- checks: all_possible
- tolerance: regex_fuzzy
- snapshot: visual_plus_dom
- validation: schema_based

---

## 自定义测试数据 (Custom Test Data)

### static-data
- source: hardcoded_values
- variety: single_dataset
- isolation: none
- cleanup: manual

### fixture-data
- source: json_files
- variety: multiple_scenarios
- isolation: test_isolated
- cleanup: automatic

### generated-data
- source: factories_fakers
- variety: infinite_combinations
- isolation: fully_isolated
- cleanup: complete_rollback

---

## 自定义网络控制 (Custom Network Control)

### live-network
- mode: pass_through
- throttling: none
- mocking: disabled
- monitoring: none

### throttled-network
- mode: throttled
- throttling: 3g_speed
- mocking: disabled
- monitoring: basic

### controlled-network
- mode: full_control
- throttling: custom_profile
- mocking: api_mocking
- monitoring: request_response_logging

---

## 自定义视觉测试 (Custom Visual Testing)

### no-visual
- enabled: false
- diff: none
- baseline: none
- approval: automatic

### screenshot-comparison
- enabled: true
- diff: pixel_diff
- baseline: committed
- approval: manual_review

### ai-visual
- enabled: true
- diff: semantic_diff
- baseline: cloud_managed
- approval: ai_assisted

---

## 自定义并行执行 (Custom Parallel Execution)

### sequential
- workers: 1
- sharding: none
- balance: static
- reporting: aggregated

### parallel-workers
- workers: cpu_cores
- sharding: file_based
- balance: round_robin
- reporting: real_time

### dynamic-scaling
- workers: auto_scaled
- sharding: intelligent
- balance: workload_based
- reporting: live_dashboard

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/webapp-testing/EXTEND.md`
- **用户级**: `~/.claude/skills/webapp-testing/EXTEND.md`
- **默认级**: `skills/webapp-testing/EXTEND.md`

---

## 使用示例

### 快速冒烟测试
```markdown
## Quick Smoke Tests

### smoke-tests
- type: smoke-tests
- browsers: chromium-only
- locators: id-only
- waiting: fixed-waits
- assertions: basic-assertions
- data: static-data
- network: live-network
- visual: no-visual
- parallel: sequential
```

### 标准回归测试
```markdown
## Standard Regression Tests

### regression-tests
- type: integration-tests
- browsers: modern-browsers
- locators: robust-locators
- waiting: explicit-waits
- assertions: standard-assertions
- data: fixture-data
- network: throttled-network
- visual: screenshot-comparison
- parallel: parallel-workers
```

### 完整E2E测试套件
```markdown
## Full E2E Test Suite

### full-e2e-suite
- type: e2e-tests
- browsers: cross-browser
- locators: ai-locators
- waiting: smart-waits
- assertions: advanced-assertions
- data: generated-data
- network: controlled-network
- visual: ai-visual
- parallel: dynamic-scaling
```
