# Agent Teams Playbook EXTEND.md

## 默认团队配置

---

## 自定义团队模式 (Custom Team Patterns)

### small-squad
- max_members: 3
- communication_style: direct
- decision_making: consensus
- parallel_tasks: 2
- review_mode: peer

### large-team
- max_members: 8
- communication_style: hierarchical
- decision_making: lead_approval
- parallel_tasks: 4
- review_mode: two_stage

### cross-functional
- max_members: 5
- communication_style: broadcast
- decision_making: specialist_consult
- parallel_tasks: 3
- review_mode: domain_expert

---

## 自定义角色分配 (Custom Role Assignment)

### frontend-team
- roles: [builder, validator, code-reviewer]
- focus: ui_components, state_management, accessibility
- testing: visual_regression, unit_tests
- review_criteria: design_compliance, performance

### backend-team
- roles: [architect, builder, security-reviewer]
- focus: api_design, database, authentication
- testing: integration_tests, load_tests
- review_criteria: scalability, security

### fullstack-team
- roles: [architect, builder, validator, security-reviewer, code-reviewer]
- focus: end_to_end_features
- testing: tdd, e2e, security
- review_criteria: best_practices, maintainability

---

## 自定义通信协议 (Custom Communication Protocols)

### async-communication
- response_timeout: 300s
- max_retries: 3
- message_format: structured
- context_sharing: selective
- broadcast_threshold: critical_only

### sync-communication
- response_timeout: 60s
- max_retries: 1
- message_format: conversational
- context_sharing: full
- broadcast_threshold: all_updates

### minimal-communication
- response_timeout: 120s
- max_retries: 2
- message_format: brief
- context_sharing: on_demand
- broadcast_threshold: errors_only

---

## 自定义工作流阶段 (Custom Workflow Stages)

### rapid-development
- stages: [plan, implement, validate]
- stage_duration: short
- approval_required: false
- documentation: minimal
- testing: basic

### thorough-development
- stages: [analyze, plan, implement, validate, review, document]
- stage_duration: adequate
- approval_required: true
- documentation: comprehensive
- testing: full_coverage

### experimental-development
- stages: [hypothesize, experiment, analyze, iterate]
- stage_duration: flexible
- approval_required: false
- documentation: lab_notes
- testing: exploratory

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/agent-teams-playbook/EXTEND.md`
- **用户级**: `~/.claude/skills/agent-teams-playbook/EXTEND.md`
- **默认级**: `skills/agent-teams-playbook/EXTEND.md`

---

## 使用示例

### 创建前端小队
```markdown
## Frontend Squad

### react-experts
- team_pattern: small-squad
- role_assignment: frontend-team
- communication: async-communication
- workflow: rapid-development
```

### 创建跨职能团队
```markdown
## Feature Team

### feature-x-team
- team_pattern: cross-functional
- role_assignment: fullstack-team
- communication: sync-communication
- workflow: thorough-development
```
