# Obsidian Markdown EXTEND.md

## 默认 Obsidian 配置

---

## 自定义双链配置 (Custom WikiLinks Config)

### basic-wikilinks
- format: [[wikilink]]
- preview: hover
- autocomplete: enabled
- case_sensitive: false

### alias-wikilinks
- format: [[wikilink|alias]]
- preview: hover
- autocomplete: enabled
- case_sensitive: false

### header-wikilinks
- format: [[file#header]]
- preview: hover
- autocomplete: enabled
- case_sensitive: true

### block-wikilinks
- format: [[file^block]]
- preview: hover
- autocomplete: enabled
- case_sensitive: false

---

## 自定义嵌入配置 (Custom Embed Config)

### file-embed
- syntax: ![[file]]
- transclusion: full_content
- resize: none
- scrolling: none

### header-embed
- syntax: ![[file#header]]
- transclusion: section_only
- resize: none
- scrolling: auto

### block-embed
- syntax: ![[file^block_id]]
- transclusion: block_only
- resize: none
- scrolling: auto

### image-embed
- syntax: ![[image|alt]]
- resize: enabled
- width: fit_content
- height: auto

---

## 自定义提醒框配置 (Custom Callout Config)

### note-callout
- type: note
- icon: info
- color: blue
- collapse: false
- title: enabled

### warning-callout
- type: warning
- icon: alert-triangle
- color: orange
- collapse: true
- title: optional

### tip-callout
- type: tip
- icon: lightbulb
- color: yellow
- collapse: true
- title: optional

### important-callout
- type: important
- icon: exclamation-mark
- color: red
- collapse: false
- title: required

### custom-callout
- type: custom
- icon: user_defined
- color: user_defined
- collapse: optional
- title: user_defined

---

## 自定义标签配置 (Custom Tags Config)

### basic-tags
- format: #tag
- color: auto_assigned
- nesting: flat
- suggest: popular

### nested-tags
- format: #parent/tag
- color: inherited
- nesting: hierarchical
- suggest: contextual

### colored-tags
- format: #tag
- color: user_defined
- nesting: flat
- suggest: all_tags

---

## 自定义属性配置 (Custom Properties Config)

### basic-properties
- format: key:: value
- types: [text, number, checkbox]
- display: inline
- validation: none

### multi-properties
- format: key:: value1, value2
- types: [list, multi]
- display: inline
- validation: comma_separated

### frontmatter-properties
- format: yaml_frontmatter
- types: [yaml_types]
- display: separate
- validation: yaml_schema

---

## 自定义模板配置 (Custom Template Config)

### daily-note
- template: daily_note
- trigger: daily
- location: Daily/
- naming: YYYY-MM-DD
- content: [date, tasks, notes]

### meeting-note
- template: meeting_note
- trigger: manual
- location: Meetings/
- naming: YYYY-MM-DD - Meeting
- content: [attendees, agenda, notes, action_items]

### project-note
- template: project_note
- trigger: manual
- location: Projects/{project}
- naming: {topic}
- content: [status, notes, next_steps]

### zettelkasten
- template: zettelkasten
- trigger: manual
- location: Zettel/
- naming: {timestamp}_{title}
- content: [notes, references, tags]

---

## 自定义插件配置 (Custom Plugin Config)

### core-plugins
- enabled: [graph, backlinks, outgoing-links, search]
- settings: default
- updates: automatic

### editing-plugins
- enabled: [daily-notes, templates, command-palette]
- settings: customized
- updates: manual

### appearance-plugins
- enabled: [themes, style-settings]
- settings: customized
- updates: manual

---

## 自定义图形配置 (Custom Graph Config)

### local-graph
- scope: current_file
- depth: 1
- filters: none
- layout: force_directed
- animation: enabled

### global-graph
- scope: entire_vault
- depth: 2
- filters: tags
- layout: hierarchical
- animation: enabled

### backlink-graph
- type: backlinks_only
- depth: unlimited
- filters: none
- layout: force_directed
- animation: enabled

---

## 自定义搜索配置 (Custom Search Config)

### simple-search
- mode: simple
- scope: all_files
- fields: [name, body]
- ranking: relevance
- preview: line_snippet

### regex-search
- mode: regex
- scope: all_files
- fields: [body]
- ranking: match_count
- preview: context_lines

### advanced-search
- mode: advanced
- scope: selectable
- fields: [name, body, tags, properties]
- ranking: weighted
- preview: full_snippet

---

## 自定义发布配置 (Custom Publish Config)

### local-publish
- method: copy
- destination: local_folder
- format: markdown
- images: copied
- links: preserved

### html-publish
- method: convert
- destination: web_folder
- format: html
- images: embedded
- links: converted
- theme: custom

### pdf-publish
- method: convert
- destination: pdf_folder
- format: pdf
- images: embedded
- links: clickable
- template: styled

---

## 自定义同步配置 (Custom Sync Config)

### obsidian-sync
- service: obsidian_sync
- encryption: enabled
- conflict_resolution: local
- sync_interval: immediate

### git-sync
- service: git
- encryption: none
- conflict_resolution: manual
- sync_interval: on_commit

### third-party-sync
- service: [dropbox, gdrive, onedrive]
- encryption: provider
- conflict_resolution: newest
- sync_interval: periodic

---

## 自定义工作流配置 (Custom Workflow Config)

### reading-workflow
- plugins: [reading-view, advanced-toolbar]
- settings: focused_mode
- shortcuts: reading_optimized
- theme: sepia

### writing-workflow
- plugins: [daily-notes, templates, word-count]
- settings: distraction_free
- shortcuts: writing_optimized
- theme: clean

### research-workflow
- plugins: [graph, canvas, dataview]
- settings: insight_focused
- shortcuts: research_optimized
- theme: high_contrast

---

## 自定义主题配置 (Custom Theme Config)

### default-theme
- name: Default
- mode: light
- base: minimal
- accent: blue
- font: system

### minimal-theme
- name: Minimal
- mode: light
- base: minimal
- accent: none
- font: sans_serif

### dark-theme
- name: Dark
- mode: dark
- base: minimal
- accent: purple
- font: sans_serif

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/obsidian-markdown/EXTEND.md`
- **用户级**: `~/.claude/skills/obsidian-markdown/EXTEND.md`
- **默认级**: `skills/obsidian-markdown/EXTEND.md`

---

## 使用示例

### 个人笔记系统
```markdown
## Personal Notes

### personal-notes
- wikilinks: basic-wikilinks
- embeds: all_embed_types
- callouts: all_callout_types
- tags: basic-tags
- properties: basic-properties
- templates: daily-note
- plugins: core-plugins
- graph: local-graph
- search: simple-search
- publish: local-publish
- sync: obsidian-sync
- workflow: reading-workflow
- theme: default-theme
```

### 学术研究系统
```markdown
## Research System

### research-system
- wikilinks: header-wikilinks + block-wikilinks
- embeds: all_embed_types
- callouts: all_callout_types
- tags: nested-tags + colored-tags
- properties: frontmatter-properties
- templates: zettelkasten
- plugins: core-plugins + editing-plugins
- graph: global-graph + backlink-graph
- search: advanced-search
- publish: html-publish + pdf-publish
- sync: git-sync
- workflow: research-workflow
- theme: minimal-theme
```

### 项目管理系统
```markdown
## Project Management

### project-management
- wikilinks: all_wikilink_types
- embeds: all_embed_types
- callouts: important-callout
- tags: colored-tags
- properties: frontmatter-properties
- templates: meeting-note + project-note
- plugins: core-plugins + appearance-plugins
- graph: local-graph
- search: advanced-search
- publish: html-publish
- sync: third-party-sync
- workflow: writing-workflow
- theme: custom-theme
```
