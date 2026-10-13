# Strategic Compact EXTEND.md

## 默认战略压缩配置

---

## 自定义压缩触发 (Custom Compact Trigger)

### manual-trigger
- activation: user_initiated
- threshold: none
- schedule: on_demand
- context: user_controlled

### token-threshold
- activation: automatic
- threshold: percentage_based
- schedule: continuous_monitoring
- context: token_count

### context-threshold
- activation: smart_detection
- threshold: complexity_based
- schedule: periodic_check
- context: conversation_state

---

## 自定义压缩策略 (Custom Compact Strategy)

### lossless-compact
- goal: preserve_everything
- method: semantic_compression
- detail: all_essentials
- reconstruction: full_restore

### lossy-compact
- goal: key_insights_only
- method: summary_extraction
- detail: main_points
- reconstruction: approximate

### selective-compact
- goal: preserve_important
- method: importance_weighted
- detail: variable
- reconstruction: tiered_restore

---

## 自定义保留策略 (Custom Preservation Strategy)

### keep-decisions
- preserve: [decisions, commits, code]
- discard: [exploration, failed_attempts]
- rationale: outcomes_matter
- compression: moderate

### keep-code
- preserve: [all_code, tests, docs]
- discard: [conversation, reasoning]
- rationale: code_is_primary
- compression: aggressive

### keep-minimal
- preserve: [final_state_only]
- discard: [process, most_conversation]
- rationale: state_sufficient
- compression: maximum

---

## 自定义摘要粒度 (Custom Summary Granularity)

### fine-grained
- detail: conversation_thread
- links: full_context
- examples: included
- retrieval: precise

### medium-grained
- detail: key_decisions
- links: important_only
- examples: selective
- retrieval: accurate

### coarse-grained
- detail: executive_summary
- links: minimal
- examples: excluded
- retrieval: approximate

---

## 自定义索引创建 (Custom Index Creation)

### no-index
- enabled: false
- scope: none
- format: none
- lookup: linear_search

### auto-index
- enabled: true
- scope: key_topics
- format: keyword_index
- lookup: fast_access

### semantic-index
- enabled: true
- scope: concepts_entities
- format: vector_index
- lookup: semantic_search

---

## 自定义分层压缩 (Custom Layered Compression)

### single-layer
- layers: 1
- organization: flat
- navigation: scroll
- retrieval: direct

### two-layer
- layers: [summary, detail]
- organization: hierarchical
- navigation: expandable
- retrieval: drill_down

### multi-layer
- layers: [executive, technical, detail]
- organization: multi_level
- navigation: guided
- retrieval: progressive_disclosure

---

## 自定义恢复方法 (Custom Restoration Method)

### full-restore
- method: decompress_all
- fidelity: original
- speed: slower
- use_case: resume_work

### selective-restore
- method: decompress_selected
- fidelity: partial
- speed: faster
- use_case: quick_reference

### on-demand-restore
- method: streaming_decompress
- fidelity: as_needed
- speed: optimized
- use_case: query_based

---

## 自定义元数据保留 (Custom Metadata Retention)

### minimal-metadata
- timestamp: creation_only
- participants: none
- context: stripped
- lineage: not_tracked

### standard-metadata
- timestamp: full_timeline
- participants: listed
- context: summarized
- lineage: tracked

### rich-metadata
- timestamp: precise
- participants: with_roles
- context: detailed
- lineage: full_provenance

---

## 自定义验证机制 (Custom Verification Mechanism)

### no-verification
- checks: none
- correction: impossible
- confidence: unknown
- rollback: not_supported

### checksum-verify
- checks: hash_verification
- correction: detect_corruption
- confidence: high
- rollback: restore_backup

### semantic-verify
- checks: meaning_preservation
- correction: manual_review
- confidence: medium
- rollback: selective_rollback

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/strategic-compact/EXTEND.md`
- **用户级**: `~/.claude/skills/strategic-compact/EXTEND.md`
- **默认级**: `skills/strategic-compact/EXTEND.md`

---

## 使用示例

### 轻量压缩
```markdown
## Lightweight Compact

### lightweight-compact
- trigger: manual-trigger
- strategy: lossy-compact
- preservation: keep-minimal
- granularity: coarse-grained
- index: no-index
- layers: single-layer
- restoration: on-demand-restore
- metadata: minimal-metadata
- verification: no-verification
```

### 智能压缩
```markdown
## Smart Compact

### smart-compact
- trigger: token-threshold
- strategy: selective-compact
- preservation: keep-code
- granularity: medium-grained
- index: auto-index
- layers: two-layer
- restoration: selective-restore
- metadata: standard-metadata
- verification: checksum-verify
```

### 完整归档压缩
```markdown
## Full Archive Compact

### archive-compact
- trigger: context-threshold
- strategy: lossless-compact
- preservation: keep-decisions
- granularity: fine-grained
- index: semantic-index
- layers: multi-layer
- restoration: full-restore
- metadata: rich-metadata
- verification: semantic-verify
```
