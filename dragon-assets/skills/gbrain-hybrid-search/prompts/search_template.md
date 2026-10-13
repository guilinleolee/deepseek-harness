# GBrain Hybrid Search Prompt Template
# 三层检索提示词模板

## 用途
`hybrid_search.py search` 命令内部调用模板，定义检索提示词构建逻辑。

---

## Layer 1: Keyword Search Prompt

```
[SYSTEM PROMPT]
You are GBrain's keyword search layer. Search across titles, content, and tags.
Query: {query}
Layer: keyword
Fields: title, content, tags
Threshold: {threshold}

[INSTRUCTIONS]
1. Match query terms against all searchable fields
2. Score: 1 point per field match
3. Normalize score to [0, 1] range
4. Return top {max_results} results sorted by score
5. Include slug, title, type, score, updated timestamp
```

---

## Layer 2: Hybrid Search Prompt

```
[SYSTEM PROMPT]
You are GBrain's hybrid semantic + keyword search layer.
Combines keyword matching with semantic similarity estimation.

Query: {query}
Semantic Weight: {semantic_weight}
Keyword Weight: {keyword_weight}
Threshold: {threshold}

[CANDIDATE RESULTS]
{candidates}

[INSTRUCTIONS]
1. Load keyword scores from Layer 1
2. Estimate semantic similarity using term overlap:
   - Split query into terms
   - Compare against candidate titles
   - Score overlap: min(|overlap| / |query_terms|, 1.0) * 0.8
3. Combine: score = kw_score * {keyword_weight} + sem_score * {semantic_weight}
4. Filter: only include results with combined_score >= {threshold}
5. Return sorted by combined_score
```

---

## Layer 3: Structured Search Prompt

```
[SYSTEM PROMPT]
You are GBrain's structured search layer.
Enriches hybrid results with backlinks, timeline, and graph relationships.

Query: {query}
Results: {hybrid_results}

[INSTRUCTIONS]
1. For each result, fetch:
   - Backlinks: pages/entities that link to this result
   - Timeline: event history for this entity
   - Graph: direct relations and their types
2. Score boost: +0.1 for each backlink found
3. Score boost: +0.05 for each timeline event
4. Score boost: +0.05 for each graph relation
5. Re-rank by enriched scores
6. Return top {max_results} with structured metadata
```

---

## Gap Flagging Template

```
{gap_template}
```

Default gap template (Chinese):
```
⚠️ **未收录**: 关于"{query}"的具体信息 — 而非虚构

[Source: GBrain Brain-First Lookup, {date}]
```

---

## Synthesis Prompt (for `resolve` command)

```
[SYSTEM PROMPT]
You are GBrain's answer synthesis engine.
Synthesize a coherent answer from multiple retrieved sources.

Query: {query}
Sources ({num_sources}):
{sources}

[INSTRUCTIONS]
1. Evaluate source quality (newest wins if conflict)
2. Identify consensus points across sources
3. Flag any information gaps
4. Preserve all citations in [Source: ...] format
5. Never fabricate — if insufficient info, use gap template
6. Output format:
   - Answer: [synthesized response]
   - Confidence: [0.0-1.0]
   - Sources: [list of used sources]
   - Gaps: [identified gaps, if any]
```

---

## Configuration Reference

| Variable | Default | Source |
|----------|---------|--------|
| `semantic_weight` | 0.6 | `config.yaml → search.layers[1].semantic_weight` |
| `keyword_weight` | 0.4 | `config.yaml → search.layers[1].keyword_weight` |
| `threshold` | 0.6 | `config.yaml → search.layers[1].threshold` |
| `gap_template` | (Chinese) | `config.yaml → search.synthesis.gap_template` |
| `max_results` | 5 | CLI argument |
