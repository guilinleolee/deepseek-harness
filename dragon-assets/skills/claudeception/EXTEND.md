# Claudeception EXTEND.md

## 默认持续学习配置

---

## 自定义学习策略 (Custom Learning Strategies)

### aggressive-learning
- extraction_frequency: always
- quality_threshold: strict
- skill_pruning: daily
- context_window: large
- learning_rate: high

### balanced-learning
- extraction_frequency: smart
- quality_threshold: medium
- skill_pruning: weekly
- context_window: medium
- learning_rate: medium

### conservative-learning
- extraction_frequency: rare
- quality_threshold: lenient
- skill_pruning: monthly
- context_window: small
- learning_rate: low

---

## 自定义质量门槛 (Custom Quality Thresholds)

### strict-quality
- requires_discovery: true
- requires_reusability: true
- requires_trigger: true
- requires_validation: true
- min_confidence: 0.9

### medium-quality
- requires_discovery: true
- requires_reusability: true
- requires_trigger: true
- requires_validation: false
- min_confidence: 0.7

### lenient-quality
- requires_discovery: false
- requires_reusability: true
- requires_trigger: false
- requires_validation: false
- min_confidence: 0.5

---

## 自定义技能分类 (Custom Skill Categories)

### technical-skills
- patterns: [regex, syntax, api_integration]
- priority: high
- retention: permanent
- sharing: private

### workflow-skills
- patterns: [process, checklist, template]
- priority: medium
- retention: long_term
- sharing: team

### knowledge-skills
- patterns: [documentation, explanation, concept]
- priority: low
- retention: medium_term
- sharing: public

### project-skills
- patterns: [config, setup, debug]
- priority: high
- retention: project_specific
- sharing: private

---

## 自定义触发条件 (Custom Trigger Conditions)

### error-based
- trigger_on_error: true
- trigger_on_retry: true
- trigger_on_user_correction: true
- min_occurrences: 2

### success-based
- trigger_on_completion: true
- trigger_on_optimization: true
- trigger_on_praise: false
- min_complexity: medium

### time-based
- trigger_on_session_end: true
- trigger_on_milestone: false
- trigger_interval: 30min
- max_session_skills: 10

---

## 自定义存储策略 (Custom Storage Strategies)

### local-storage
- storage_path: ~/.claude/learned-skills/
- format: markdown
- versioning: enabled
- backup: automatic
- max_size: 100MB

### team-storage
- storage_path: .claude/team-skills/
- format: json
- versioning: git_tracked
- backup: manual
- max_size: unlimited

### cloud-storage
- storage_path: cloud://skills/
- format: encrypted
- versioning: continuous
- backup: distributed
- max_size: unlimited

---

## 自定义复用策略 (Custom Reuse Strategies)

### exact-match
- similarity_threshold: 1.0
- fuzzy_matching: false
- context_required: true
- auto_apply: true

### semantic-match
- similarity_threshold: 0.7
- fuzzy_matching: true
- context_required: true
- auto_apply: suggest

### creative-match
- similarity_threshold: 0.5
- fuzzy_matching: true
- context_required: false
- auto_apply: false

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/claudeception/EXTEND.md`
- **用户级**: `~/.claude/skills/claudeception/EXTEND.md`
- **默认级**: `skills/claudeception/EXTEND.md`

---

## 使用示例

### 激进学习模式
```markdown
## Learning Mode

### startup-learning
- strategy: aggressive-learning
- quality: strict-quality
- storage: local-storage
- reuse: semantic-match
- triggers: error-based
```

### 团队协作学习
```markdown
## Team Learning

### collaborative-learning
- strategy: balanced-learning
- quality: medium-quality
- storage: team-storage
- reuse: exact-match
- triggers: success-based
```

### 保守学习模式
```markdown
## Conservative Learning

### minimal-learning
- strategy: conservative-learning
- quality: lenient-quality
- storage: local-storage
- reuse: creative-match
- triggers: time-based
```
