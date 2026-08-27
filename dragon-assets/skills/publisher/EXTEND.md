# Publisher EXTEND.md

## 默认发布师配置

---

## 自定义提交风格

### basic-commit
- format: simple_messages
- conventional: not_enforced
- emojis: none
- signing: none

### conventional-commit
- format: type_scope_description_body_footer
- conventional: strictly_followed
- emojis: type_based
- signing: optional

### enhanced-commit
- format: full_conventional_with_refs
- conventional: extended_with_custom_types
- emojis: extensive_emoji_set
- signing: gpg_signed

---

## 自定义分支策略

### no-strategy
- workflow: ad_hoc
- protection: none
- merging: any_to_any
- releases: unmanaged

### github-flow
- workflow: feature_branch_main
- protection: main_protected
- merging: pr_required
- releases: main_deploys

### git-flow
- workflow: feature_develop_release_main
- protection: multiple_branches
- merging: strict_hierarchy
- releases: tagged_releases

### trunk-based
- workflow: commit_directly
- protection: ci_gated
- merging: none_rebased
- releases: continuous

---

## 自定义PR工作流

### simple-pr
- creation: basic_description
- review: single_reviewer
- approval: one_approver
- merge: merge_commit

### structured-pr
- creation: template_based
- review: required_reviewers
- approval: code_owners
- merge: squash_rebase

### quality-gate-pr
- creation: comprehensive_checklist
- review: multiple_rounds
- approval: all_requirements_met
- merge: strict_checks_ci_status

---

## 自定义版本管理

### no-versioning
- scheme: none
- tags: none
- releases: commits_only
- changelog: none

### semantic-versioning
- scheme: major_minor_patch
- tags: git_tags
- releases: versioned_releases
- changelog: auto_generated

### calendar-versioning
- scheme: calver
- tags: date_based
- releases: scheduled_releases
- changelog: date_marked

---

## 自定义发布流程

### direct-push
- method: git_push
- ci: none
- staging: none
- production: push_deploys

### ci-based
- method: push_triggers_ci
- ci: automated_tests_build
- staging: automatic_promotion
- production: manual_approval

### pipeline-based
- method: full_deployment_pipeline
- ci: multi_stage_pipeline
- staging: environment_gates
- production: progressive_delivery

---

## 自定义Changelog生成

### manual-changelog
- method: hand_written
- commits: curated
- categorization: author_choice
- formatting: markdown

### auto-changelog
- method: commit_parsed
- commits: conventional_filtered
- categorization: commit_type
- formatting: structured_template

### ai-changelog
- method: llm_summarized
- commits: semantically_grouped
- categorization: intelligent
- formatting: user_friendly_language

---

## 配置优先级

CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置

---

## 使用示例

### 个人项目
- commit: basic-commit
- branch: no-strategy
- pr: simple-pr
- version: no-versioning
- release: direct-push
- changelog: manual-changelog

### 团队项目
- commit: conventional-commit
- branch: github-flow
- pr: structured-pr
- version: semantic-versioning
- release: ci-based
- changelog: auto-changelog

### 企业级项目
- commit: enhanced-commit
- branch: git-flow
- pr: quality-gate-pr
- version: semantic-versioning
- release: pipeline-based
- changelog: ai-changelog
