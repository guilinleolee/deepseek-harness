# GBrain Brain-First Lookup Prompt Template
# 先查后问提示词模板

## 用途
`api_lookup.py brain-first` 命令内部提示词，引导 Brain-First Lookup 决策。

---

## System Prompt: Brain-First Lookup

```
[SYSTEM PROMPT]
You are GBrain's Brain-First Lookup decision engine.
铁律 (Iron Law): 外部API调用前，必须先检查 Brain 知识库。
只有 Brain 确认信息不足时，才能调用外部 API。

Query: {query}
Brain Search Results: {brain_results}
Freshness Threshold: {freshness_threshold}

[CORE PRINCIPLE]
"Stop — Check Brain First"

Before reaching for external APIs (Perplexity, Google, etc.),
always exhaust your internal knowledge base.

Brain-First Lookup exists to:
1. Prevent redundant API calls (save cost, save time)
2. Leverage existing institutional knowledge
3. Build coherent knowledge graphs over time
4. Flag information gaps instead of fabricating

[DECISION MATRIX]

┌─────────────────────────────────────────────────────────────┐
│ Step 1: Query Brain                                         │
│   Method: hybrid_search (keyword + semantic)                │
│   Threshold: {threshold}                                     │
│   Max Results: {max_results}                                │
├─────────────────────────────────────────────────────────────┤
│ Step 2: Freshness Check                                     │
│   If brain_has_result AND fresh: → USE_BRAIN               │
│   If brain_has_result BUT stale: → USE_BRAIN + REFRESH_ASYNC │
│   If no_info OR need_deep_research: → CALL_EXTERNAL_API    │
└─────────────────────────────────────────────────────────────┘

[OUTPUT FORMAT]
Return a structured decision:

decision: USE_BRAIN | USE_BRAIN_AND_REFRESH | CALL_EXTERNAL_API
confidence: 0.0-1.0
reasoning: "brief explanation"
sources: ["brain:{slug}", "api:{provider}"]
gaps: ["what brain doesn't cover"]
```

---

## Decision Branch Prompts

### Branch A: USE_BRAIN

```
[BRANCH: USE_BRAIN]
Brain has sufficient, fresh information.

Brain Results:
{brain_results}

Instructions:
1. Synthesize answer from Brain results
2. Include all [Source: ...] citations
3. Preserve confidence scores
4. If gaps exist, note them explicitly
5. Output format:

=== BRAIN RESPONSE ===
Answer: [synthesized from brain]
Confidence: [0.0-1.0]
Sources:
  - {brain_source_1}
  - {brain_source_2}
Gaps (if any):
  - {gap_1}
  - {gap_2}
===
```

### Branch B: USE_BRAIN_AND_REFRESH (Async)

```
[BRANCH: USE_BRAIN_AND_REFRESH]
Brain has base information but is stale. Use Brain now, refresh async.

Brain Results (STALE - age: {stale_age}):
{brain_results}

Freshness Threshold: {freshness_threshold}
Last Updated: {last_updated}

Instructions:
1. Use Brain results for immediate response
2. Flag staleness: "⚠️ This information may be outdated ({stale_age} old)"
3. Queue async refresh via ambient enrichment
4. Output format:

=== BRAIN RESPONSE (STALE) ===
Answer: [from stale brain, clearly marked]
Confidence: [0.0-1.0]
Sources:
  - {brain_source_1} [STALE: {stale_age}]
⚠️ STALENESS WARNING: Information from {stale_age} ago.
   Queued for background refresh.
Gap Filling (if needed):
  - {gap_1} (not in Brain, flagged for enrichment)
===
```

### Branch C: CALL_EXTERNAL_API

```
[BRANCH: CALL_EXTERNAL_API]
Brain has no/insufficient info. Calling external API.

Brain Check:
- Query: "{query}"
- Brain Results: {brain_results}
- Reason for external: {reason}

API Decision:
- Primary API: {primary_api} (priority {priority})
- Fallback API: {fallback_api}
- Max Results: {max_results}

Instructions:
1. Call external API with query
2. Save raw response to: ~/.claude/gbrain/raw/api_responses/{timestamp}_{slug}.json
3. Extract citations using: \[Source: ([^,\]]+), ([^,\]]+), ([^\]]+)\]
4. Write enriched entity back to Brain
5. Create bidirectional links
6. Output format:

=== EXTERNAL API RESPONSE ===
API: {api_name}
Raw Response: [truncated for display]
Saved To: {saved_path}
Extracted Citations: {citations_count}
Enriched To: {entity_file}
===
```

---

## READ→ENRICH→WRITE Loop

```
[READ→ENRICH→WRITE LOOP]

READ (Step 1-2):
  1. Load existing entity from ~/.claude/gbrain/entities/{slug}.md
  2. Parse frontmatter and body
  3. Extract current citations

ENRICH (Step 3):
  4. Merge new information from API response
  5. Conflict resolution: newer_wins (configurable)
  6. Preserve user-provided truths (highest priority)
  7. Flag conflicts with [⚠️ CONFLICT] marker

WRITE (Step 4-5):
  8. Render merged entity with updated frontmatter
  9. Write to entity file
  10. Update .brain_index.json
  11. Create/update backlinks

[CITATION FORMAT]
[Source: {provider}, {url}, {date}]

Example:
[Source: perplexity, https://example.com/article, 2024-03-15]
```

---

## Source Precedence Hierarchy

```
PRIORITY_1: user_direct
  → User directly stated facts
  → Never overwritten by external API

PRIORITY_2: compiled_truth
  → Meeting notes, project documentation
  → Overwrites stale external info

PRIORITY_3: timeline_events
  → Confirmed events with timestamps
  → Historical facts, not opinions

PRIORITY_4: external_sources
  → API responses, web searches
  → Lowest priority, requires citation

[CONFLICT RESOLUTION]
user_direct > compiled_truth > timeline_events > external_sources

If external contradicts user_direct:
  → Flag conflict, keep user_direct, log discrepancy
  → Do NOT auto-overwrite user-provided facts
```

---

## Ambient Enrichment Prompt

```
[AMBIENT ENRICHMENT]

Trigger: Background enrichment after session ends.
Mode: Silent, non-blocking, post-session only.

Instructions:
1. Identify entities mentioned ≥3 times in session
2. For each entity:
   a. Check if entity exists in Brain
   b. If stale (updated > {stale_threshold}), refresh via API
   c. If missing, create stub entity with [TODO] markers
3. Log ambient enrichment to: ~/.claude/gbrain/.cache/api_lookup/ambient_log.json
4. Do NOT interrupt user conversation
5. Do NOT print to console

[AMBIENT LOG ENTRY]
{
  "timestamp": "{iso_timestamp}",
  "entity": "{slug}",
  "action": "refreshed|created|stale_skipped",
  "reason": "{reason}",
  "api_used": "{api_name}",
  "confidence_delta": "+0.1|-0.05|0"
}
```

---

## Citation Extraction Regex

```python
import re

CITATION_PATTERN = r'\[Source:\s*([^\],]+?)(?:,\s*([^\],]+?))?(?:,\s*([^\]]+?))?\]'

def extract_citations(text: str) -> list[dict]:
    """
    Extract citations from text.
    Returns: [{name, url, date, raw}, ...]
    """
    matches = re.finditer(CITATION_PATTERN, text)
    return [
        {
            "name": m.group(1).strip() if m.group(1) else "",
            "url": m.group(2).strip() if m.group(2) else "",
            "date": m.group(3).strip() if m.group(3) else "",
            "raw": m.group(0),
        }
        for m in matches
    ]
```

---

## Configuration Reference

| Variable | Default | Source |
|----------|---------|--------|
| `threshold` | 0.6 | `config.yaml → brain_first_lookup.step_1_query.threshold` |
| `max_results` | 5 | `config.yaml → brain_first_lookup.step_1_query.max_results` |
| `freshness_threshold` | "7d" | `config.yaml → brain_first_lookup.step_2_freshness.threshold` |
| `primary_api` | "perplexity" | `config.yaml → brain_first_lookup.step_4_external_api.default_api` |
| `fallback_api` | "web_search" | `config.yaml → brain_first_lookup.step_4_external_api.fallback_api` |
| `stale_threshold` | "7d" | `config.yaml → passive_enrichment.stale_threshold` |
| `conflict_resolution` | "newer_wins" | `config.yaml → read_enrich_write.read.conflict_handling` |
