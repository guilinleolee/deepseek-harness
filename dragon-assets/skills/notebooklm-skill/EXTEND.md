# NotebookLM Skill EXTEND.md

## 默认NotebookLM配置

---

## 自定义查询模式 (Custom Query Mode)

### direct-query
- method: single_question
- context: minimal_provided
- sources: specified
- format: q_a_pair

### exploratory-query
- method: follow_up_questions
- context: built_conversation
- sources: discovered
- format: dialogue

### research-query
- method: deep_investigation
- context: comprehensive
- sources: all_relevant
- format: structured_report

---

## 自定义来源范围 (Custom Source Scope)

### single-notebook
- scope: one_notebook_only
- cross_reference: none
- breadth: narrow
- depth: thorough

### multi-notebook
- scope: selected_notebooks
- cross_reference: enabled
- breadth: moderate
- depth: balanced

### all-notebooks
- scope: entire_library
- cross_reference: full
- breadth: extensive
- depth: variable

---

## 自定义答案格式 (Custom Answer Format)

### concise-answer
- length: brief
- detail: key_points_only
- citations: minimal
- examples: excluded

### standard-answer
- length: moderate
- detail: balanced
- citations: included
- examples: selective

### comprehensive-answer
- length: extensive
- detail: complete
- citations: thorough
- examples: extensive

---

## 自定义引用样式 (Custom Citation Style)

### inline-citations
- format: parenthetical
- placement: within_text
- links: direct_to_source
- metadata: minimal

### footnote-citations
- format: numbered
- placement: document_end
- links: reference_list
- metadata: detailed

### no-citations
- format: none
- placement: na
- links: none
- metadata: na

---

## 自定义上下文窗口 (Custom Context Window)

### minimal-context
- tokens: essential_only
- history: current_query_only
- background: excluded
- focus: laser_targeted

### standard-context
- tokens: reasonable_amount
- history: recent_exchanges
- background: summarized
- focus: well_rounded

### extensive-context
- tokens: maximum_available
- history: full_conversation
- background: comprehensive
- focus: exploratory

---

## 自定义语言设置 (Custom Language Settings)

### english-only
- input: english_required
- output: english_only
- mixed_language: not_supported
- translation: none

### multilingual
- input: any_language
- output: match_input
- mixed_language: supported
- translation: automatic

### source-preserving
- input: match_source
- output: source_language
- mixed_language: preserve
- translation: minimal

---

## 自定义同步行为 (Custom Sync Behavior)

### manual-sync
- frequency: on_demand
- auto_refresh: disabled
- conflict_handling: user_resolves
- offline_mode: cache_only

### auto-sync
- frequency: change_based
- auto_refresh: enabled
- conflict_handling: last_write_wins
- offline_mode: queue_changes

### real-time-sync
- frequency: continuous
- auto_refresh: instant
- conflict_handling: merge_strategy
- offline_mode: error

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/notebooklm-skill/EXTEND.md`
- **用户级**: `~/.claude/skills/notebooklm-skill/EXTEND.md`
- **默认级**: `skills/notebooklm-skill/EXTEND.md`

---

## 使用示例

### 快速查询
```markdown
## Quick Query

### quick-query
- mode: direct-query
- scope: single-notebook
- answer: concise-answer
- citations: inline-citations
- context: minimal-context
- language: english-only
- sync: manual-sync
```

### 研究探索
```markdown
## Research Exploration

### research-exploration
- mode: research-query
- scope: all-notebooks
- answer: comprehensive-answer
- citations: footnote-citations
- context: extensive-context
- language: multilingual
- sync: real-time-sync
```

### 日常笔记
```markdown
## Daily Notes

### daily-notes
- mode: exploratory-query
- scope: multi-notebook
- answer: standard-answer
- citations: inline-citations
- context: standard-context
- language: source-preserving
- sync: auto-sync
```
