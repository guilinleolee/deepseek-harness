# Verification Before Completion EXTEND.md

## 默认完成前验证配置

---

## 自定义验证清单 (Custom Verification Checklist)

### basic-checklist
- items: 5_core_checks
- customization: none
- enforcement: optional
- blocking: non_blocking

### standard-checklist
- items: 15_comprehensive_checks
- customization: category_specific
- enforcement: required
- blocking: soft_block

### strict-checklist
- items: 50_detailed_checks
- customization: fully_customizable
- enforcement: mandatory
- blocking: hard_block

---

## 自定义检查类别 (Custom Check Categories)

### code-quality
- linting: enabled
- formatting: enforced
- complexity: measured
- documentation: required

### functionality
- unit_tests: passing
- integration_tests: passing
- edge_cases: covered
- performance: benchmarked

### security
- vulnerabilities: scanned
- secrets: detected
- permissions: reviewed
- compliance: verified

---

## 自定义验证时机 (Custom Verification Timing)

### manual-trigger
- activation: user_initiated
- frequency: on_demand
- scope: full_check
- feedback: immediate

### pre-commit-trigger
- activation: git_hook
- frequency: every_commit
- scope: changed_files
- feedback: blocking

### pre-push-trigger
- activation: git_hook
- frequency: before_push
- scope: full_repository
- feedback: blocking

### ci-trigger
- activation: pipeline
- frequency: every_pr
- scope: full_suite
- feedback: non_blocking_reporting

---

## 自定义修复行为 (Custom Remediation Behavior)

### manual-fix
- action: report_only
- automation: none
- suggestions: provided
- retry: manual_retrigger

### semi-auto-fix
- action: report_with_quick_fixes
- automation: safe_fixes_only
- suggestions: prioritized
- retry: auto_retest_safe

### full-auto-fix
- action: auto_fix_all
- automation: all_fixes
- suggestions: auto_applied
- retry: auto_retest_all

---

## 自定义上下文感知 (Custom Context Awareness)

### context-blind
- awareness: none
- adaptation: static
- learning: disabled
- personalization: generic

### context-aware
- awareness: project_type
- adaptation: category_based
- learning: pattern_based
- personalization: team_habits

### fully-adaptive
- awareness: comprehensive
- adaptation: real_time
- learning: continuous
- personalization: individual

---

## 自定义性能影响 (Custom Performance Impact)

### minimal-impact
- parallelization: disabled
- caching: none
- incremental: false
- speed: fastest

### balanced-impact
- parallelization: smart
- caching: incremental_results
- incremental: supported
- speed: optimized

### thorough-impact
- parallelization: maximum
- caching: aggressive
- incremental: true
- speed: comprehensive

---

## 自定义历史分析 (Custom History Analysis)

### no-history
- lookback: none
- pattern_detection: disabled
- trending: disabled
- learning: none

### short-history
- lookback: 10_commits
- pattern_detection: basic
- trending: simple
- learning: adaptive

### full-history
- lookback: full_history
- pattern_detection: advanced
- trending: statistical
- learning: predictive

---

## 自定义通知系统 (Custom Notification System)

### console-only
- channel: stdout
- format: text
- detail: summary
- persistence: none

### desktop-notify
- channel: system_notification
- format: visual
- detail: key_findings
- persistence: session_only

### team-notify
- channel: slack_email_webhook
- format: structured
- detail: comprehensive
- persistence: logged

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/verification-before-completion/EXTEND.md`
- **用户级**: `~/.claude/skills/verification-before-completion/EXTEND.md`
- **默认级**: `skills/verification-before-completion/EXTEND.md`

---

## 使用示例

### 开发者快速检查
```markdown
## Developer Quick Check

### dev-quick-check
- checklist: basic-checklist
- categories: code-quality
- timing: manual-trigger
- remediation: manual-fix
- context: context-blind
- performance: minimal-impact
- history: no-history
- notifications: console-only
```

### PR前完整验证
```markdown
## Pre-PR Full Verification

### pre-pr-verification
- checklist: standard-checklist
- categories: [code-quality, functionality]
- timing: pre-push-trigger
- remediation: semi-auto-fix
- context: context-aware
- performance: balanced-impact
- history: short-history
- notifications: desktop-notify
```

### 严格质量门禁
```markdown
## Strict Quality Gate

### strict-quality-gate
- checklist: strict-checklist
- categories: all_categories
- timing: ci-trigger
- remediation: full-auto-fix
- context: fully-adaptive
- performance: thorough-impact
- history: full-history
- notifications: team-notify
```
