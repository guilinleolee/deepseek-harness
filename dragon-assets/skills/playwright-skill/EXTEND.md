# Playwright Skill EXTEND.md

## 默认Playwright配置

---

## 自定义浏览器选择 (Custom Browser Selection)

### chromium-only
- browser: chromium
- platforms: cross_platform
- features: fastest_chrome_engine
- testing: focused

### multi-browser
- browser: chromium_firefox_webkit
- platforms: comprehensive
- features: full_coverage
- testing: thorough

### custom-browser
- browser: user_specified_channel
- platforms: selective
- features: specific_version
- testing: targeted

---

## 自定义执行模式 (Custom Execution Mode)

### headed
- mode: visible_browser
- debugging: easy_visual
- speed: normal
- use_case: development_debugging

### headless
- mode: background_execution
- debugging: screenshot_video_only
- speed: faster
- use_case: ci_pipeline

### debug-mode
- mode: slow_motion_with_inspection
- debugging: full_control
- speed: very_slow
- use_case: test_creation_troubleshooting

---

## 自定义等待策略 (Custom Waiting Strategy)

### hard-waits
- method: fixed_timeouts
- reliability: low
- speed: slow
- simplicity: high

### explicit-waits
- method: wait_for_specific_conditions
- reliability: high
- speed: optimal
- simplicity: moderate

### smart-waits
- method: auto_waiting_for_elements
- reliability: very_high
- speed: fast
- simplicity: high

---

## 自定义选择器策略 (Custom Selector Strategy)

### css-selectors
- type: css_based
- resilience: moderate
- readability: good
- maintenance: moderate

### text-selectors
- type: text_content_based
- resilience: low
- readability: excellent
- maintenance: high

### role-selectors
- type: aria_role_based
- resilience: high
- readability: excellent
- maintenance: low

### xpath-selectors
- type: xpath_expressions
- resilience: high
- readability: poor
- maintenance: moderate

---

## 自定义断言风格 (Custom Assertion Style)

### basic-assertions
- checks: simple_truthy_equality
- feedback: generic_messages
- retries: none
- debugging: basic

### soft-assertions
- checks: collect_all_failures
- feedback: grouped_report
- retries: configurable
- debugging: comprehensive

### web-first-assertions
- checks: auto_waiting_assertions
- feedback: detailed_locator_info
- retries: built_in
- debugging: enhanced

---

## 自定义测试组织 (Custom Test Organization)

### flat-files
- structure: single_test_files
- grouping: by_file
- fixtures: per_file
- parallelization: none

### page-object-model
- structure: separated_pages_actions
- grouping: by_feature
- fixtures: shared_fixtures
- parallelization: worker_level

### fixtures-based
- structure: fixture_driven_tests
- grouping: by_fixture_scope
- fixtures: hierarchical
- parallelization: highly_parallel

---

## 自定义追踪记录 (Custom Tracing Recording)

### no-tracing
- trace: disabled
- screenshots: on_failure_only
- videos: none
- memory: minimal

### basic-tracing
- trace: disabled
- screenshots: each_test
- videos: on_failure
- memory: standard

### full-tracing
- trace: enabled_with_timeline
- screenshots: every_action
- videos: always_recording
- memory: detailed_snapshots

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/playwright-skill/EXTEND.md`
- **用户级**: `~/.claude/skills/playwright-skill/EXTEND.md`
- **默认级**: `skills/playwright-skill/EXTEND.md`

---

## 使用示例

### 快速脚本
```markdown
## Quick Script

### quick-script
- browser: chromium-only
- execution: headless
- waiting: smart-waits
- selectors: css-selectors
- assertions: basic-assertions
- organization: flat-files
- tracing: no-tracing
```

### 标准E2E测试
```markdown
## Standard E2E Tests

### standard-e2e
- browser: multi-browser
- execution: headless
- waiting: explicit-waits
- selectors: role-selectors
- assertions: web-first-assertions
- organization: page-object-model
- tracing: basic-tracing
```

### 调试会话
```markdown
## Debugging Session

### debug-session
- browser: custom-browser
- execution: debug-mode
- waiting: explicit-waits
- selectors: text-selectors
- assertions: soft-assertions
- organization: fixtures-based
- tracing: full-tracing
```
