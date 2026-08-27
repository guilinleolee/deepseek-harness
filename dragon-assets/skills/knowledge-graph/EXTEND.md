# Knowledge Graph EXTEND.md

## 默认知识图谱配置

---

## 自定义图结构

### simple-graph
- nodes: basic_entities
- edges: direct_relationships
- depth: single_level
- complexity: low

### multi-layer-graph
- nodes: typed_entities
- edges: weighted_relationships
- depth: hierarchical
- complexity: medium

### temporal-graph
- nodes: time_versioned
- edges: time_sensitive
- depth: temporal_evolution
- complexity: high

---

## 自定义实体提取

### keyword-extraction
- method: frequency_based
- context: ignored
- granularity: word_level
- accuracy: basic

### ner-extraction
- method: named_entity_recognition
- context: local_window
- granularity: phrase_level
- accuracy: moderate

### semantic-extraction
- method: embedding_based
- context: document_wide
- granularity: concept_level
- accuracy: high

---

## 自定义关系推断

### co-occurrence
- method: appears_together
- confidence: frequency_based
- direction: undirected
- semantics: none

### syntactic-dependency
- method: grammar_based
- confidence: parse_tree_derived
- direction: directed
- semantics: grammatical

### semantic-relation
- method: meaning_based
- confidence: embedding_similarity
- direction: typed
- semantics: rich

---

## 自定义可视化方式

### force-directed
- layout: physics_simulation
- clusters: emergent
- labels: all_visible
- interactivity: drag_zoom

### hierarchical-tree
- layout: rooted_hierarchy
- clusters: by_branch
- labels: path_labels
- interactivity: expand_collapse

### geographic-map
- layout: spatial_coordinates
- clusters: regional
- labels: location_based
- interactivity: pan_zoom

### timeline-view
- layout: chronological
- clusters: temporal_periods
- labels: time_annotated
- interactivity: scroll_zoom

---

## 自定义查询模式

### adjacency-query
- type: direct_neighbors
- depth: one_hop
- performance: instant
- use_case: local_exploration

### path-query
- type: shortest_path
- depth: variable_hops
- performance: fast
- use_case: connection_finding

### pattern-query
- type: subgraph_matching
- depth: complex_patterns
- performance: moderate
- use_case: relationship_discovery

---

## 自定义持久化策略

### memory-only
- storage: ram
- persistence: session_only
- size: limited_by_memory
- recovery: none

### file-based
- storage: json_graphml
- persistence: manual_save
- size: limited_by_disk
- recovery: restore_from_file

### database-backed
- storage: neo4j_postgresql
- persistence: automatic
- size: scalable
- recovery: transaction_logs

---

## 配置优先级

CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置

---

## 使用示例

### 快速笔记图谱
- structure: simple-graph
- extraction: keyword-extraction
- relations: co-occurrence
- visualization: force-directed
- queries: adjacency-query
- persistence: memory-only

### 学术研究图谱
- structure: multi-layer-graph
- extraction: ner-extraction
- relations: semantic-relation
- visualization: hierarchical-tree
- queries: path-query
- persistence: file-based

### 企业知识库
- structure: temporal-graph
- extraction: semantic-extraction
- relations: semantic-relation
- visualization: timeline-view
- queries: pattern-query
- persistence: database-backed
