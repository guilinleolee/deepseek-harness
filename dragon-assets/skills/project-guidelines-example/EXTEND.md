# Project Guidelines Example EXTEND.md

## 默认项目指南配置

---

## 自定义项目规模

### small-project
- team_size: 1_3_people
- duration: weeks
- complexity: low
- documentation: minimal_essential

### medium-project
- team_size: 3_10_people
- duration: months
- complexity: moderate
- documentation: standard_practices

### large-project
- team_size: 10_50_people
- duration: quarters
- complexity: high
- documentation: comprehensive

### enterprise-project
- team_size: 50_plus_people
- duration: years
- complexity: very_high
- documentation: extensive

---

## 自定义开发流程

### waterfall
- phases: [requirements, design, implementation, testing, deployment]
- feedback: end_of_phase
- flexibility: low
- predictability: high

### agile-scrum
- phases: [sprint_planning, daily_standup, sprint_review, retrospective]
- feedback: continuous
- flexibility: high
- predictability: medium

### lean-kanban
- phases: continuous_flow
- feedback: real_time
- flexibility: very_high
- predictability: variable

### hybrid
- phases: mixed_approach
- feedback: staged_checkpoints
- flexibility: adjustable
- predictability: balanced

---

## 自定义代码标准

### strict
- style: enforced_linter
- review: mandatory_pr
- testing: full_coverage
- ci: required

### moderate
- style: guidelines_with_exceptions
- review: peer_review_optional
- testing: critical_coverage
- ci: recommended

### relaxed
- style: conventions_only
- review: self_review
- testing: minimal_coverage
- ci: optional

---

## 配置优先级

CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置

---

## 使用示例

### 小型个人项目
- scale: small-project
- process: lean-kanban
- standards: relaxed

### 中型团队项目
- scale: medium-project
- process: agile-scrum
- standards: moderate

### 企业级项目
- scale: enterprise-project
- process: hybrid
- standards: strict
