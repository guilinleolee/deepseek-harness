# Obsidian Bases EXTEND.md

## 默认Obsidian数据库配置

---

## 自定义数据结构 (Custom Data Structure)

### flat-schema
- hierarchy: single_level
- relationships: links_only
- metadata: minimal
- normalization: none

### relational-schema
- hierarchy: multi_level
- relationships: foreign_keys
- metadata: standardized
- normalization: partial

### graph-schema
- hierarchy: network
- relationships: bidirectional_edges
- metadata: extensive
- normalization: full

---

## 自定义字段类型 (Custom Field Types)

### basic-fields
- types: [text, number, boolean]
- validation: loose
- defaults: optional
- indexing: basic

### extended-fields
- types: [text, number, boolean, date, list]
- validation: type_checking
- defaults: recommended
- indexing: full_text

### advanced-fields
- types: [all_supported]
- validation: schema_enforced
- defaults: required
- indexing: multi_field

---

## 自定义视图模式 (Custom View Mode)

### table-view
- layout: spreadsheet_like
- sorting: column_based
- filtering: header_filters
- grouping: none

### board-view
- layout: kanban_columns
- sorting: manual_order
- filtering: card_badges
- grouping: status_columns

### calendar-view
- layout: monthly_grid
- sorting: chronological
- filtering: date_ranges
- grouping: daily

### gallery-view
- layout: visual_cards
- sorting: grid_order
- filtering: metadata_tags
- grouping: none

---

## 自定义查询引擎 (Custom Query Engine)

### dataview-basic
- language: dataview_query
- complexity: simple_queries
- aggregation: basic
- performance: fast

### dataview-advanced
- language: dataview_query
- complexity: complex_nested
- aggregation: full_sql_like
- performance: moderate

### custom-plugin
- language: plugin_specific
- complexity: depends_on_plugin
- aggregation: variable
- performance: variable

---

## 自定义关系管理 (Custom Relationship Management)

### manual-links
- creation: manual_wikilinks
- discovery: visual_scan
- validation: none
- backlinks: automatic

### suggested-links
- creation: ai_suggested
- discovery: autocomplete
- validation: confidence_scored
- backlinks: automatic

### auto-linked
- creation: automatic_detection
- discovery: relationship_panel
- validation: semantic
- backlinks: bidirectional

---

## 自定义数据完整性 (Custom Data Integrity)

### loose-integrity
- validation: none
- required_fields: optional
- type_checking: absent
- constraints: unenforced

### standard-integrity
- validation: on_save
- required_fields: marked
- type_checking: warning
- constraints: soft

### strict-integrity
- validation: real_time
- required_fields: enforced
- type_checking: blocking
- constraints: hard

---

## 自定义备份策略 (Custom Backup Strategy)

### no-backup
- frequency: none
- retention: na
- versioning: none
- export: manual

### periodic-backup
- frequency: daily_weekly
- retention: rolling_window
- versioning: major_versions
- export: automated

### continuous-backup
- frequency: every_change
- retention: full_history
- versioning: incremental
- export:实时同步

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/obsidian-bases/EXTEND.md`
- **用户级**: `~/.claude/skills/obsidian-bases/EXTEND.md`
- **默认级**: `skills/obsidian-bases/EXTEND.md`

---

## 使用示例

### 简单联系人管理
```markdown
## Simple Contact Manager

### contact-manager
- structure: flat-schema
- fields: basic-fields
- view: table-view
- query: dataview-basic
- relationships: manual-links
- integrity: loose-integrity
- backup: no-backup
```

### 项目追踪器
```markdown
## Project Tracker

### project-tracker
- structure: relational-schema
- fields: extended-fields
- view: board-view
- query: dataview-advanced
- relationships: suggested-links
- integrity: standard-integrity
- backup: periodic-backup
```

### 知识图谱
```markdown
## Knowledge Graph

### knowledge-graph
- structure: graph-schema
- fields: advanced-fields
- view: gallery-view
- query: custom-plugin
- relationships: auto-linked
- integrity: strict-integrity
- backup: continuous-backup
```
