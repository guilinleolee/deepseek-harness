# Using Git Worktrees EXTEND.md

## 默认Git工作树配置

---

## 自定义工作树用途

### feature-isolation
- purpose: develop_new_feature
- duration: days_to_weeks
- integration: merged_back
- cleanup: after_merge

### bugfix-isolation
- purpose: fix_production_bug
- duration: hours_to_days
- integration: cherry_pick_or_merge
- cleanup: after_deployment

### experiment-branch
- purpose: try_risky_changes
- duration: indefinite
- integration: maybe_never
- cleanup: when_abandoned

### code-review-isolation
- purpose: parallel_review_work
- duration: while_reviewing
- integration: reference_only
- cleanup: after_review

---

## 自定义创建策略

### manual-creation
- method: git_worktree_manual
- location: user_specified
- naming: manual
- setup: manual_configuration

### script-assisted
- method: helper_script
- location: structured_directory
- naming: automated_pattern
- setup: partially_automated

### full-automation
- method: git_hook_or_cli
- location: predefined_structure
- naming: systematic
- setup: completely_automated

---

## 自定义目录组织

### flat-worktrees
- structure: single_directory_all_trees
- navigation: shallow
- management: simple
- cleanup: manual_pruning

### grouped-worktrees
- structure: by_type_or_team
- navigation: categorized
- management: organized
- cleanup: systematic

### project-root-worktrees
- structure: ../project-worktrees/
- navigation: parallel_to_main
- management: clean_separation
- cleanup: automated_by_age

---

## 自定义环境配置

### shared-environment
- node_modules: symlinked_or_copied
- config: inherited_from_main
- cache: shared
- disk: efficient

### isolated-environment
- node_modules: fresh_install_per_tree
- config: independent
- cache: separate_or_shared
- disk: more_usage

### selective-isolation
- node_modules: dependencies_smart_linked
- config: base_with_overrides
- cache: stratified
- disk: balanced

---

## 自定义分支策略

### main-plus-worktrees
- base: main_branch_only
- branches: feature_from_main
- switching: worktree_based
- merging: pr_based

### multi-branch-worktrees
- base: any_branch
- branches: from_any_existing
- switching: both_worktree_and_checkout
- merging: flexible

### release-worktrees
- base: release_branches
- branches: maintenance_only
- switching: version_specific
- merging: backport_strategy

---

## 自定义清理策略

### manual-cleanup
- trigger: user_initiated
- safety: must_be_done_manually
- automation: none
- risk: abandoned_trees_accumulate

### periodic-cleanup
- trigger: scheduled_cron
- safety: checks_if_merged
- automation: script_removes_old
- risk: low_if_script_correct

### auto-cleanup
- trigger: after_merge_success
- safety: verified_safe_to_remove
- automation: immediate_removal
- risk: requires_verification_logic

---

## 配置优先级

CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置

---

## 使用示例

### 快速功能分支
- usage: feature-isolation
- creation: script-assisted
- organization: project-root-worktrees
- environment: selective-isolation
- branching: main-plus-worktrees
- cleanup: periodic-cleanup

### 并行Bug修复
- usage: bugfix-isolation
- creation: manual-creation
- organization: grouped-worktrees
- environment: isolated-environment
- branching: multi-branch-worktrees
- cleanup: auto-cleanup

### 实验性开发
- usage: experiment-branch
- creation: manual-creation
- organization: flat-worktrees
- environment: isolated-environment
- branching: multi-branch-worktrees
- cleanup: manual-cleanup
