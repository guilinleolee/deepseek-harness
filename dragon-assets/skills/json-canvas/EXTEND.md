# JSON Canvas EXTEND.md

## 默认JSON Canvas配置

---

## 自定义节点类型

### basic-nodes
- types: [text, file]
- complexity: simple
- data: minimal
- rendering: fast

### rich-nodes
- types: [text, file, link, image]
- complexity: moderate
- data: enhanced
- rendering: balanced

### advanced-nodes
- types: [all_supported]
- complexity: high
- data: comprehensive
- rendering: full_featured

---

## 自定义布局策略

### manual-layout
- positioning: user_dragged
- algorithm: none
- auto_arrange: off
- control: complete

### force-directed
- positioning: physics_simulation
- algorithm: force_atlas
- auto_arrange: continuous
- control: parameters_only

### hierarchical
- positioning: tree_structure
- algorithm: sugiyama_reingold_tilford
- auto_arrange: on_change
- control: directional

### grid-based
- positioning: regular_grid
- algorithm: rectangular_packing
- auto_arrange: initial
- control: snap_to_grid

---

## 自定义连接风格

### straight-lines
- type: direct
- curvature: none
- routing: euclidean
- aesthetics: minimal

### bezier-curves
- type: curved
- curvature: smooth
- routing: natural
- aesthetics: organic

### orthogonal
- type: right_angles
- curvature: none
- routing: manhattan
- aesthetics: technical

### animated
- type: dynamic_flow
- curvature: variable
- routing: path_following
- aesthetics: engaging

---

## 自定义视图控制

### fixed-view
- zoom: manual_set
- pan: drag_based
- selection: single
- focus: user_controlled

### smart-view
- zoom: fit_to_content
- pan: auto_center
- selection: multi_select
- focus: context_aware

### presentation-view
- zoom: animated_transitions
- pan: path_based
- selection: step_by_step
- focus: scripted

---

## 自定义数据存储

### single-file
- format: single_canvas_file
- portability: excellent
- collaboration: diff_friendly
- versioning: git_compatible

### split-storage
- format: canvas_with_external_data
- portability: moderate
- collaboration: partial_merge
- versioning: complex

### database-backed
- format: stored_in_database
- portability: export_required
- collaboration: real_time
- versioning: revision_history

---

## 自定义扩展能力

### canvas-only
- features: core_visualization
- plugins: none
- scripting: not_supported
- integration: limited

### plugin-ecosystem
- features: extensible
- plugins: community_contributed
- scripting: javascript_api
- integration: moderate

### programmable
- features: fully_customizable
- plugins: custom_development
- scripting: full_automation
- integration: deep

---

## 配置优先级

CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置

---

## 使用示例

### 简单笔记
- nodes: basic-nodes
- layout: manual-layout
- connections: straight-lines
- view: fixed-view
- storage: single-file
- extensions: canvas-only

### 知识图谱
- nodes: rich-nodes
- layout: force-directed
- connections: bezier-curves
- view: smart-view
- storage: single-file
- extensions: plugin-ecosystem

### 项目管理看板
- nodes: advanced-nodes
- layout: grid-based
- connections: orthogonal
- view: presentation-view
- storage: database-backed
- extensions: programmable
