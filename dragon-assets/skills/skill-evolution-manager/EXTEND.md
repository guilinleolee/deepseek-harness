# Skill Evolution Manager EXTEND.md

## 默认技能进化管理器配置

---

## 自定义触发时机

### manual-trigger
- activation: user_initiated
- frequency: on_demand
- automation: none
- discovery: explicit_request

### conversation-end
- activation: automatic_on_session_end
- frequency: once_per_conversation
- automation: full_detection
- discovery: pattern_analysis

### periodic-trigger
- activation: scheduled_intervals
- frequency: daily_weekly
- automation: cron_based
- discovery: batch_scan

---

## 自定义提取模式

### conservative-extraction
- threshold: high_confidence_only
- scope: explicit_learnings
- validation: strict_criteria
- yield: few_high_quality

### balanced-extraction
- threshold: medium_confidence
- scope: key_insights_plus_context
- validation: standard_checks
- yield: moderate_quality

### aggressive-extraction
- threshold: low_confidence
- scope: everything_possibly_useful
- validation: minimal_filters
- yield: quantity_over_quality

---

## 自定义分类方式

### flat-list
- structure: no_categories
- organization: chronological
- retrieval: search_based
- maintenance: simple

### tagged-categories
- structure: keyword_tags
- organization: tag_based_grouping
- retrieval: tag_filtered
- maintenance: tag_management

### hierarchical-taxonomy
- structure: multi_level_categories
- organization: domain_tree
- retrieval: category_navigation
- maintenance: taxonomy_evolution

---

## 自定义验证级别

### no-validation
- checks: accept_all
- testing: none
- refinement: raw_output
- quality: variable

### basic-validation
- checks: format_syntax
- testing: spot_checks
- refinement: minimal_cleanup
- quality: improved

### rigorous-validation
- checks: semantic_correctness
- testing: execution_verified
- refinement: comprehensive_editing
- quality: high

---

## 自定义进化策略

### static-skills
- updates: manual_only
- versioning: none
- deprecation: manual_removal
- evolution: human_driven

### versioned-evolution
- updates: versioned_updates
- versioning: semantic_versioning
- deprecation: grace_period_then_remove
- evolution: tracked_iterations

### continuous-evolution
- updates: real_time_refinement
- versioning: automatic_increments
- deprecation: usage_based_retirement
- evolution: ai_driven_adaptation

---

## 自定义共享方式

### private-only
- visibility: creator_only
- collaboration: none
- learning: personal
- discovery: local_only

### team-shared
- visibility: team_members
- collaboration: peer_review
- learning: group_knowledge
- discovery: team_repository

### community-shared
- visibility: public_or_org_wide
- collaboration: open_contributions
- learning: ecosystem_growth
- discovery: public_marketplace

---

## 配置优先级

CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置

---

## 使用示例

### 个人技能库
- trigger: manual-trigger
- extraction: conservative-extraction
- classification: flat-list
- validation: no-validation
- evolution: static-skills
- sharing: private-only

### 团队知识管理
- trigger: conversation-end
- extraction: balanced-extraction
- classification: tagged-categories
- validation: basic-validation
- evolution: versioned-evolution
- sharing: team-shared

### 组织学习系统
- trigger: periodic-trigger
- extraction: aggressive-extraction
- classification: hierarchical-taxonomy
- validation: rigorous-validation
- evolution: continuous-evolution
- sharing: community-shared
