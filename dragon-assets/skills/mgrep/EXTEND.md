# MGrep EXTEND.md

## 默认语义搜索配置

---

## 自定义搜索模式 (Custom Search Mode)

### semantic-search
- type: vector_based
- model: embedding_model
- similarity: cosine
- threshold: 0.7

### hybrid-search
- type: semantic_plus_keyword
- model: combined
- similarity: weighted_score
- threshold: 0.6

### keyword-search
- type: traditional_regex
- model: none
- similarity: exact_match
- threshold: n/a

---

## 自定义搜索范围 (Custom Search Scope)

### current-project
- scope: project_root
- depth: recursive
- exclude: node_modules, .git
- follow_symlinks: false

### workspace-wide
- scope: workspace
- depth: recursive
- exclude: build_artifacts
- follow_symlinks: true

### directory-specific
- scope: user_specified
- depth: user_configurable
- exclude: user_defined
- follow_symlinks: user_choice

---

## 自定义结果排序 (Custom Result Ranking)

### relevance-ranking
- factor: semantic_similarity
- boost: none
- diversity: disabled
- limit: top_20

### freshness-ranking
- factor: recency
- boost: recent_files
- diversity: disabled
- limit: top_20

### diverse-ranking
- factor: similarity_plus_path
- boost: different_directories
- diversity: enabled
- limit: top_30

---

## 自定义上下文窗口 (Custom Context Window)

### minimal-context
- lines: 2
- mode: centered_on_match
- syntax: none
- highlights: disabled

### standard-context
- lines: 5
- mode: centered_on_match
- syntax: language_specific
- highlights: matched_terms

### full-context
- lines: 10
- mode: include_surrounding_functions
- syntax: full_syntax
- highlights: matched_plus_related

---

## 自定义文件过滤 (Custom File Filtering)

### no-filter
- extensions: all
- languages: all
- size_limit: none
- binary_mode: skip

### code-filter
- extensions: [js, ts, py, java, go, rs]
- languages: programming_languages
- size_limit: 1mb
- binary_mode: skip

### custom-filter
- extensions: user_specified
- languages: user_selected
- size_limit: user_defined
- binary_mode: user_choice

---

## 自定义显示格式 (Custom Display Format)

### compact-display
- format: single_line
- path: relative
- line_numbers: shown
- highlights: minimal

### standard-display
- format: multi_line
- path: relative_with_highlight
- line_numbers: shown
- highlights: color_coded

### verbose-display
- format: full_context
- path: absolute
- line_numbers: shown
- highlights: color_coded_plus_surrounding

---

## 自定义索引策略 (Custom Indexing Strategy)

### no-index
- indexing: disabled
- cache: none
- update: real_time_scan
- storage: none

### memory-index
- indexing: in_memory
- cache: ram_based
- update: on_demand
- storage: temporary

### persistent-index
- indexing: on_disk
- cache: hybrid
- update: incremental
- storage: index_files

---

## 自定义查询增强 (Custom Query Enhancement)

### literal-query
- expansion: disabled
- correction: off
- synonyms: none
- context: none

### expanded-query
- expansion: related_terms
- correction: spelling
- synonyms: thesaurus_based
- context: minimal

### intelligent-query
- expansion: semantic_neighbors
- correction: semantic
- synonyms: embedding_based
- context: full_history

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/mgrep/EXTEND.md`
- **用户级**: `~/.claude/skills/mgrep/EXTEND.md`
- **默认级**: `skills/mgrep/EXTEND.md`

---

## 使用示例

### 快速代码搜索
```markdown
## Quick Code Search

### quick-code-search
- mode: semantic-search
- scope: current-project
- ranking: relevance-ranking
- context: standard-context
- filter: code-filter
- display: standard-display
- index: memory-index
- enhancement: expanded-query
```

### 全项目深度搜索
```markdown
## Full Project Deep Search

### full-project-search
- mode: hybrid-search
- scope: workspace-wide
- ranking: diverse-ranking
- context: full-context
- filter: custom-filter
- display: verbose-display
- index: persistent-index
- enhancement: intelligent-query
```

### 即时文件查找
```markdown
## Instant File Lookup

### instant-lookup
- mode: keyword-search
- scope: directory-specific
- ranking: relevance-ranking
- context: minimal-context
- filter: no-filter
- display: compact-display
- index: no-index
- enhancement: literal-query
```
