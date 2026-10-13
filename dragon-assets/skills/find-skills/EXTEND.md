# Find Skills EXTEND.md

## 默认技能发现配置

---

## 自定义搜索策略 (Custom Search Strategy)

### keyword-search
- method: keyword_matching
- fields: [name, description, tags]
- case_sensitive: false
- fuzzy_matching: false
- threshold: exact_match

### fuzzy-search
- method: fuzzy_matching
- fields: [name, description, tags]
- case_sensitive: false
- fuzzy_matching: true
- threshold: 0.7

### semantic-search
- method: embedding_similarity
- fields: [description, content]
- case_sensitive: false
- fuzzy_matching: false
- threshold: 0.75

### hybrid-search
- method: keyword + semantic
- fields: all_fields
- case_sensitive: false
- fuzzy_matching: true
- threshold: adaptive

---

## 自定义技能库配置 (Custom Skill Repository Config)

### local-repository
- path: ~/.claude/skills
- recursive: true
- index: built_on_search
- update: manual

### github-repository
- url: https://github.com/anthropics/claude-code-skills
- branch: main
- index: cached
- update: daily

### tencent-skillhub
- url: https://skillhub.tencent.com/
- provider: Tencent
- description: 腾讯技能中心 - Claude/OpenClaw 技能仓库
- categories: [Claude Code, OpenClaw, AI Agent, 腾讯混元]
- auth: optional_login
- index: cached
- update: weekly
- features:
    - Claude Code 技能
    - OpenClaw 协议技能
    - 腾讯混元 Agent 技能
    - 中文优化技能
    - 企业级技能模板
- lang: zh-CN
- priority: high

### custom-repository
- url: custom_url
- auth: token_based
- index: cached
- update: weekly

---

## 自定义过滤选项 (Custom Filter Options)

### category-filter
- enabled: true
- categories: [development, design, writing, automation]
- mode: inclusive

### tag-filter
- enabled: true
- tags: [frontend, backend, testing, documentation]
- mode: inclusive

### language-filter
- enabled: true
- languages: [javascript, python, typescript]
- mode: inclusive

### maturity-filter
- enabled: true
- levels: [stable, experimental, deprecated]
- mode: exclusive

---

## 自定义排序选项 (Custom Sort Options)

### relevance-sort
- primary: relevance_score
- secondary: name
- tertiary: last_updated

### popularity-sort
- primary: usage_count
- secondary: rating
- tertiary: name

### recent-sort
- primary: last_updated
- secondary: created_date
- tertiary: name

### alphabetical-sort
- primary: name
- secondary: category
- tertiary: tags

---

## 自定义结果显示 (Custom Result Display)

### minimal-display
- fields: [name, description]
- truncate: 100_chars
- tags: none
- examples: none

### standard-display
- fields: [name, description, tags, examples]
- truncate: 200_chars
- tags: top_5
- examples: 2

### detailed-display
- fields: [name, description, tags, examples, author, version, dependencies]
- truncate: none
- tags: all
- examples: 5
- metadata: included

---

## 自定义技能推荐 (Custom Skill Recommendation)

### usage-based
- strategy: collaborative_filtering
- data: [installation_history, usage_patterns]
- personalization: true
- fallback: popularity

### content-based
- strategy: similarity_matching
- data: [skill_tags, descriptions, examples]
- personalization: false
- fallback: random

### hybrid-recommendation
- strategy: usage + content
- data: all_available
- personalization: true
- fallback: category_based

---

## 自定义安装选项 (Custom Installation Options)

### git-install
- method: git_clone
- destination: ~/.claude/skills
- shallow: true
- recursive: false

### copy-install
- method: file_copy
- destination: ~/.claude/skills
- overwrite: confirm
- backup: created

### link-install
- method: symbolic_link
- destination: ~/.claude/skills
- overwrite: confirm
- backup: created

---

## 自定义更新机制 (Custom Update Mechanism)

### manual-update
- frequency: manual
- check: user_initiated
- auto_install: false
- notifications: none

### scheduled-update
- frequency: daily
- check: automatic
- auto_install: false
- notifications: available_updates

### auto-update
- frequency: real_time
- check: automatic
- auto_install: non_breaking
- notifications: all_changes

---

## 自定义技能验证 (Custom Skill Validation)

### basic-validation
- checks: [syntax, structure, required_files]
- on: install
- strictness: warning_only

### strict-validation
- checks: [syntax, structure, required_files, naming_conventions, documentation]
- on: install + update
- strictness: error_on_fail

### full-validation
- checks: [syntax, structure, required_files, naming_conventions, documentation, examples, tests]
- on: install + update + run
- strictness: error_on_fail
- linting: enabled

---

## 自定义技能分析 (Custom Skill Analysis)

### dependency-analysis
- enabled: true
- type: [skills, commands, hooks]
- circular_detection: true
- orphan_detection: true

### usage-analysis
- enabled: true
- metrics: [invocation_count, success_rate, avg_duration]
- retention: 30_days

### compatibility-analysis
- enabled: true
- version_check: true
- api_check: true
- breaking_changes: flagged

---

## 自定义搜索历史 (Custom Search History)

### no-history
- enabled: false
- storage: none
- max_entries: 0

### session-history
- enabled: true
- storage: memory
- max_entries: 100
- retention: session_only

### persistent-history
- enabled: true
- storage: file
- location: ~/.claude/skills/history.json
- max_entries: 1000
- retention: 90_days

---

## 自定义缓存策略 (Custom Cache Strategy)

### no-cache
- enabled: false
- ttl: 0
- size: 0

### memory-cache
- enabled: true
- ttl: 1_hour
- size: 100_mb
- invalidation: time_based

### disk-cache
- enabled: true
- ttl: 24_hours
- size: 1gb
- invalidation: smart
- location: ~/.claude/skills/cache/

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/find-skills/EXTEND.md`
- **用户级**: `~/.claude/skills/find-skills/EXTEND.md`
- **默认级**: `skills/find-skills/EXTEND.md`

---

## 使用示例

### 快速查找
```markdown
## Quick Find

### quick-find
- search: keyword-search
- repository: local-repository
- filter: category-filter
- sort: relevance-sort
- display: minimal-display
- recommendation: none
- install: git-install
- update: manual-update
- validation: basic-validation
- analysis: none
- history: no-history
- cache: no-cache
```

### 智能发现
```markdown
## Smart Discovery

### smart-discovery
- search: semantic-search
- repository: github-repository + local-repository
- filter: category-filter + tag-filter
- sort: relevance-sort
- display: detailed-display
- recommendation: hybrid-recommendation
- install: copy-install
- update: scheduled-update
- validation: strict-validation
- analysis: dependency-analysis + usage-analysis
- history: session-history
- cache: memory-cache
```

### 专业研究
```markdown
## Professional Research

### professional-research
- search: hybrid-search
- repository: all_repositories
- filter: all_filters
- sort: popularity-sort
- display: detailed-display
- recommendation: content-based
- install: link-install
- update: auto-update
- validation: full-validation
- analysis: full_analysis
- history: persistent-history
- cache: disk-cache
```
