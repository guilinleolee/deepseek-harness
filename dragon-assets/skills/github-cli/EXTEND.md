# GitHub CLI EXTEND.md

## 默认GitHub CLI配置

---

## 自定义认证方式

### token-auth
- method: personal_access_token
- scope: user_defined
- expiry: manual_rotation
- security: token_responsibility

### oauth-auth
- method: github_oauth_flow
- scope: permission_granted
- expiry: token_refresh
- security: managed_by_github

### enterprise-auth
- method: sso_saml
- scope: enterprise_policies
- expiry: session_based
- security: corporate_managed

---

## 自定义仓库操作

### read-only
- operations: [view, clone, issue_read]
- permissions: read
- risk: none
- use_case: information_gathering

### standard-operations
- operations: [clone, commit, push, pr]
- permissions: read_write
- risk: standard
- use_case:日常开发

### admin-operations
- operations: [all_commands]
- permissions: full_access
- risk: elevated
- use_case: repository_management

---

## 自定义PR工作流

### simple-pr
- creation: draft_first
- review: single_reviewer
- merge: merge_commit
- automation: minimal

### structured-pr
- creation: template_based
- review: required_approvers
- merge: squash_merge
- automation: status_checks

### strict-pr
- creation: detailed_checklist
- review: code_owners
- merge: rebase_then_merge
- automation: ci_cd_gate

---

## 自定义Issue管理

### basic-issues
- creation: simple_title_body
- tracking: open_closed
- labels: optional
- automation: none

### project-issues
- creation: templated_with_checklist
- tracking: kanban_columns
- labels: categorized
- automation: workflows

### agile-issues
- creation: story_pointed
- tracking: sprint_planning
- labels: epic_theme
- automation: burndown_charts

---

## 自定义搜索策略

### basic-search
- scope: current_repo
- qualifiers: simple
- results: limited
- sorting: relevance

### advanced-search
- scope: org_or_all
- qualifiers: complex_boolean
- results: paginated
- sorting: flexible_sorting

### saved-searches
- scope: predefined_queries
- qualifiers: curated
- results: dashboards
- sorting: custom_views

---

## 自定义通知设置

### all-notifications
- types: everything
- delivery: instant
- filtering: none
- volume: high

### relevant-notifications
- types: mentions_assignments
- delivery: periodic_digest
- filtering: smart_filters
- volume: manageable

### minimal-notifications
- types: critical_only
- delivery: daily_summary
- filtering: aggressive
- volume: low

---

## 配置优先级

CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置

---

## 使用示例

### 个人开发
- auth: token-auth
- operations: standard-operations
- pr: simple-pr
- issues: basic-issues
- search: basic-search
- notifications: relevant-notifications

### 团队协作
- auth: oauth-auth
- operations: standard-operations
- pr: structured-pr
- issues: project-issues
- search: advanced-search
- notifications: relevant-notifications

### 企业管理
- auth: enterprise-auth
- operations: admin-operations
- pr: strict-pr
- issues: agile-issues
- search: saved-searches
- notifications: minimal-notifications
