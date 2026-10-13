# Finishing Development Branch EXTEND.md

## 默认分支完成配置

---

## 自定义整合策略 (Custom Integration Strategy)

### rebase-strategy
- method: rebase
- conflicts: resolve_interactively
- preserve: feature_history
- fallback: merge

### merge-strategy
- method: merge_commit
- conflicts: resolve_interactively
- preserve: merge_commit
- fallback: rebase

### squash-strategy
- method: squash_and_merge
- conflicts: resolve_before_merge
- preserve: single_commit
- fallback: merge

### fast-forward-strategy
- method: fast_forward_only
- conflicts: n/a
- preserve: linear_history
- fallback: merge

---

## 自定义完成检查清单 (Custom Completion Checklist)

### code-review
- item: [code_review_approved, self_review_done, no_review_comments]
- required: all
- verification: manual
- blocking: true

### testing-checks
- item: [tests_passing, coverage_adequate, e2e_passing]
- required: all
- verification: automated
- blocking: true

### documentation-checks
- item: [readme_updated, changelog_updated, api_docs_current]
- required: all
- verification: manual
- blocking: false

### quality-checks
- item: [linting_clean, no_warnings, formatted_properly]
- required: all
- verification: automated
- blocking: false

---

## 自定义清理任务 (Custom Cleanup Tasks)

### branch-cleanup
- delete: feature_branch
- remote: deleted
- local: optional
- tracking: cleanup

### workspace-cleanup
- artifacts: removed
- cache: cleared
- temp_files: deleted
- dependencies: unused

### cleanup-script
- script: custom_cleanup
- execution: automatic
- verification: logged

---

## 自定义备份策略 (Custom Backup Strategy)

### no-backup
- backup: none
- before: false
- after: false
- retention: none

### local-backup
- backup: file_copy
- before: true
- after: true
- retention: 7_days

### remote-backup
- backup: git_tag
- before: true
- after: true
- retention: permanent

---

## 自定义通知配置 (Custom Notification Config)

### minimal-notifications
- events: [completion, failure]
- channels: console
- format: concise
- frequency: real_time

### standard-notifications
- events: [start, progress, completion, failure]
- channels: console + slack
- format: detailed
- frequency: milestone_based

### verbose-notifications
- events: all_events
- channels: all_channels
- format: comprehensive
- frequency: real_time

---

## 自定义审查选项 (Custom Review Options)

### no-review
- review: none
- approvers: none
- required: 0
- timeout: none

### peer-review
- review: required
- approvers: 1
- required: 1
- timeout: 48_hours

### team-review
- review: required
- approvers: 2
- required: 2
- timeout: 72_hours

### formal-review
- review: required
- approvers: code_owners
- required: all
- timeout: 1_week

---

## 自定义部署准备 (Custom Deployment Preparation)

### local-deployment
- environment: local
- steps: [build, test, start]
- verification: manual
- rollback: manual

### staging-deployment
- environment: staging
- steps: [build, deploy, smoke_test]
- verification: automated
- rollback: automatic

### production-deployment
- environment: production
- steps: [build, deploy, smoke_test, monitor]
- verification: automated + manual
- rollback: automatic

---

## 自定义庆祝与分享 (Custom Celebration & Sharing)

### silent-completion
- celebration: none
- sharing: none
- announcement: none

### team-celebration
- celebration: emoji_reaction
- sharing: team_channel
- announcement: summary

### public-celebration
- celebration: release_notes
- sharing: organization_wide
- announcement: full_announcement

---

## 自定义文档更新 (Custom Documentation Updates)

### automatic-updates
- changelog: generated
- version: auto_incremented
- contributors: auto_listed
- release_notes: generated

### manual-updates
- changelog: manual
- version: manual
- contributors: manual
- release_notes: manual

### template-updates
- changelog: template_filled
- version: following_template
- contributors: manual
- release_notes: template_based

---

## 自定义分支保护 (Custom Branch Protection)

### no-protection
- rules: none
- enforcement: none
- bypass: allowed

### basic-protection
- rules: [require_status_checks, up_to_date_branch]
- enforcement: soft
- bypass: allowed_with_admin

### strict-protection
- rules: [require_status_checks, up_to_date_branch, require_linear_history, no_forced_push]
- enforcement: hard
- bypass: admin_only

---

## 自定义后续步骤 (Custom Next Steps)

### create-related-branch
- trigger: manual
- naming: feature/{name}-followup
- tracking: linked

### create-milestone
- trigger: manual
- title: next_phase
- tracking: project_managed

### archive-task
- trigger: automatic
- system: project_management
- tracking: closed

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/finishing-a-development-branch/EXTEND.md`
- **用户级**: `~/.claude/skills/finishing-a-development-branch/EXTEND.md`
- **默认级**: `skills/finishing-a-development-branch/EXTEND.md`

---

## 使用示例

### 个人项目
```markdown
## Personal Project

### personal-project
- integration: rebase-strategy
- checks: code-review + testing-checks
- cleanup: branch-cleanup
- backup: no-backup
- notifications: minimal-notifications
- review: no-review
- deployment: local-deployment
- celebration: silent-completion
- docs: automatic-updates
- protection: no-protection
- next_steps: archive-task
```

### 团队项目
```markdown
## Team Project

### team-project
- integration: merge-strategy
- checks: all_checks
- cleanup: workspace-cleanup
- backup: remote-backup
- notifications: standard-notifications
- review: peer-review
- deployment: staging-deployment
- celebration: team-celebration
- docs: automatic-updates
- protection: basic-protection
- next_steps: create-related-branch
```

### 企业项目
```markdown
## Enterprise Project

### enterprise-project
- integration: squash-strategy
- checks: all_checks
- cleanup: cleanup-script
- backup: remote-backup
- notifications: verbose-notifications
- review: team-review
- deployment: production-deployment
- celebration: public-celebration
- docs: template-updates
- protection: strict-protection
- next_steps: create-milestone
```
