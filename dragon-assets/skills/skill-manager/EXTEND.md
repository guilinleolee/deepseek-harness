# Skill Manager EXTEND.md

## 默认技能管理配置

---

## 自定义扫描策略 (Custom Scanning Strategy)

### quick-scan
- depth: surface
- scope: local_only
- speed: fast
- update_check: disabled

### standard-scan
- depth: moderate
- scope: local_plus_remote
- speed: balanced
- update_check: version_check

### deep-scan
- depth: comprehensive
- scope: all_sources
- speed: thorough
- update_check: full_metadata

---

## 自定义更新检测 (Custom Update Detection)

### no-check
- enabled: false
- frequency: never
- source: none
- notification: disabled

### version-check
- enabled: true
- frequency: weekly
- source: github_tags
- notification: version_diff

### commit-check
- enabled: true
- frequency: daily
- source: git_commits
- notification: changelog

### prerelease-check
- enabled: true
- frequency: hourly
- source: all_branches
- notification: instant

---

## 自定义升级策略 (Custom Upgrade Strategy)

### manual-upgrade
- mode: manual_prompt
- backup: before_upgrade
- testing: skipped
- rollback: supported

### auto-stable-upgrade
- mode: auto_major_minor
- backup: automatic
- testing: smoke_tests
- rollback: automatic

### auto-all-upgrade
- mode: auto_all_updates
- backup: automatic
- testing: full_suite
- rollback: automatic

### smart-upgrade
- mode: ai_assessed
- backup: conditional
- testing: risk_based
- rollback: selective

---

## 自定义依赖管理 (Custom Dependency Management)

### ignore-dependencies
- mode: install_only
- conflicts: unresolved
- versions: latest
- isolation: none

### version-locked
- mode: specify_versions
- conflicts: fail_fast
- versions: locked
- isolation: none

### dependency-solver
- mode: auto_resolve
- conflicts: negotiate
- versions: compatible
- isolation: virtual_env

---

## 自定义冲突解决 (Custom Conflict Resolution)

### fail-on-conflict
- strategy: error
- intervention: required
- auto_resolve: none
- preference: first_installed

### warn-on-conflict
- strategy: warning
- intervention: optional
- auto_resolve: keep_existing
- preference: existing

### auto-resolve
- strategy: merge
- intervention: on_failure
- auto_resolve: smart_merge
- preference: highest_version

---

## 自定义备份策略 (Custom Backup Strategy)

### no-backup
- enabled: false
- frequency: never
- retention: none
- compression: none

### pre-change-backup
- enabled: true
- frequency: before_changes
- retention: 5_versions
- compression: gzip

### scheduled-backup
- enabled: true
- frequency: daily
- retention: 30_days
- compression: gzip

### git-backup
- enabled: true
- frequency: every_change
- retention: git_history
- compression: git_delta

---

## 自定义测试策略 (Custom Testing Strategy)

### no-testing
- enabled: false
- scope: none
- framework: none
- reporting: none

### smoke-testing
- enabled: true
- scope: basic_functionality
- framework: simple_tests
- reporting: pass_fail

### integration-testing
- enabled: true
- scope: skill_integration
- framework: test_suite
- reporting: detailed

### full-testing
- enabled: true
- scope: comprehensive
- framework: full_ci_cd
- reporting: analytics_dashboard

---

## 自定义通知配置 (Custom Notification Config)

### silent-mode
- method: none
- urgency: none
- channels: disabled
- digest: disabled

### summary-mode
- method: batched
- urgency: low
- channels: console
- digest: daily_summary

### instant-mode
- method: real_time
- urgency: all
- channels: [console, email, webhook]
- digest: instant_alerts

---

## 自定义性能优化 (Custom Performance Optimization)

### minimal-optimization
- caching: none
- parallel: sequential
- compression: none
- index: basic

### standard-optimization
- caching: metadata_cache
- parallel: concurrent_safe
- compression: response_compression
- index: indexed_search

### aggressive-optimization
- caching: multi_level_cache
- parallel: max_parallel
- compression: aggressive
- index: full_text_index

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/skill-manager/EXTEND.md`
- **用户级**: `~/.claude/skills/skill-manager/EXTEND.md`
- **默认级**: `skills/skill-manager/EXTEND.md`

---

## 使用示例

### 轻量级管理
```markdown
## Lightweight Management

### lightweight-management
- scanning: quick-scan
- updates: version-check
- upgrade: manual-upgrade
- dependencies: ignore-dependencies
- conflicts: warn-on-conflict
- backup: no-backup
- testing: no-testing
- notifications: silent-mode
- optimization: minimal-optimization
```

### 标准管理
```markdown
## Standard Management

### standard-management
- scanning: standard-scan
- updates: commit-check
- upgrade: auto-stable-upgrade
- dependencies: version-locked
- conflicts: auto-resolve
- backup: pre-change-backup
- testing: smoke-testing
- notifications: summary-mode
- optimization: standard-optimization
```

### 专业级管理
```markdown
## Professional Management

### professional-management
- scanning: deep-scan
- updates: prerelease-check
- upgrade: smart-upgrade
- dependencies: dependency-solver
- conflicts: auto-resolve
- backup: git-backup
- testing: full-testing
- notifications: instant-mode
- optimization: aggressive-optimization
```
