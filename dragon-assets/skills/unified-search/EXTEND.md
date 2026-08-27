# Unified Search EXTEND.md

## 默认统一搜索配置

---

## 自定义搜索策略 (Custom Search Strategy)

### smart-routing
- analysis: intent_detection
- routing: automatic
- fallback: enabled
- learning: adaptive

### manual-selection
- analysis: user_choice
- routing: explicit
- fallback: ask_user
- learning: disabled

### parallel-search
- analysis: none
- routing: all_sources
- fallback: none
- learning: aggregate

---

## 自定义数据源 (Custom Data Sources)

### local-code
- type: codebase
- index: realtime
- scope: project_root
- format: syntax_aware

### web-search
- type: internet
- index: external
- scope: world_wide_web
- format: html

### knowledge-graph
- type: graph
- index: prebuilt
- scope: learned_skills
- format: node_edges

### vector-db
- type: semantic
- index: embeddings
- scope: embeddings_db
- format: vector

### documentation
- type: docs
- index: cached
- scope: official_docs
- format: markdown

---

## 自定义结果聚合 (Custom Result Aggregation)

### best-match
- strategy: rank_and_pick
- diversity: low
- threshold: top_3
- deduplication: strict

### diverse-results
- strategy: balance_sources
- diversity: high
- threshold: top_10
- deduplication: fuzzy

### comprehensive
- strategy: include_all
- diversity: maximum
- threshold: no_limit
- deduplication: URL_based

---

## 自定义排序算法 (Custom Ranking Algorithm)

### relevance-sort
- factor: semantic_similarity
- weight: 100%
- personalization: disabled
- freshness: ignored

### hybrid-sort
- factor: mixed_signals
- weight: balanced
- personalization: enabled
- freshness: considered

### popularity-sort
- factor: usage_stats
- weight: popularity_weighted
- personalization: enabled
- freshness: significant

---

## 自定义缓存策略 (Custom Caching Strategy)

### no-cache
- enabled: false
- ttl: 0
- storage: none
- invalidation: none

### session-cache
- enabled: true
- ttl: 1_hour
- storage: memory
- invalidation: session_end

### persistent-cache
- enabled: true
- ttl: 24_hours
- storage: disk
- invalidation: smart

---

## 自定义查询增强 (Custom Query Enhancement)

### literal-query
- expansion: disabled
- correction: disabled
- synonyms: none
- context: minimal

### enhanced-query
- expansion: enabled
- correction: spelling
- synonyms: related
- context: query_history

### semantic-query
- expansion: embedding_based
- correction: semantic
- synonyms: vector_based
- context: full_context

---

## 自定义结果显示 (Custom Result Display)

### compact-display
- format: list
- snippets: disabled
- highlights: disabled
- grouping: none

### standard-display
- format: cards
- snippets: 2_lines
- highlights: keywords
- grouping: by_source

### rich-display
- format: detailed
- snippets: 5_lines
- highlights: matched
- grouping: by_category

---

## 自定义过滤规则 (Custom Filtering Rules)

### basic-filter
- safe_search: moderate
- date_range: any
- file_type: any
- language: auto

### strict-filter
- safe_search: strict
- date_range: past_year
- file_type: specific
- language: user_selected

### custom-filter
- safe_search: custom_level
- date_range: custom_range
- file_type: whitelist
- language: multi_language

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/unified-search/EXTEND.md`
- **用户级**: `~/.claude/skills/unified-search/EXTEND.md`
- **默认级**: `skills/unified-search/EXTEND.md`

---

## 使用示例

### 快速代码搜索
```markdown
## Quick Code Search

### quick-code-search
- strategy: smart-routing
- sources: local-code
- aggregation: best-match
- ranking: relevance-sort
- cache: session-cache
- enhancement: literal-query
- display: compact-display
- filter: basic-filter
```

### 全面知识搜索
```markdown
## Comprehensive Knowledge Search

### comprehensive-search
- strategy: parallel-search
- sources: all_sources
- aggregation: comprehensive
- ranking: hybrid-sort
- cache: persistent-cache
- enhancement: semantic-query
- display: rich-display
- filter: custom-filter
```

### 智能网页搜索
```markdown
## Smart Web Search

### smart-web-search
- strategy: smart-routing
- sources: web-search + documentation
- aggregation: diverse-results
- ranking: popularity-sort
- cache: persistent-cache
- enhancement: enhanced-query
- display: standard-display
- filter: basic-filter
```
