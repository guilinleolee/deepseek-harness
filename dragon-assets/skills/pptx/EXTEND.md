# PPTX EXTEND.md

## 默认PPTX处理配置

---

## 自定义读取模式

### slides-text
- content: slide_text_only
- layout: ignored
- notes: excluded
- media: omitted

### full-presentation
- content: everything
- layout: preserved
- notes: included
- media: referenced

---

## 自定义创建策略

### blank-deck
- template: none
- master: default
- theme: plain
- layouts: basic

### template-based
- template: specified_file
- master: inherited
- theme: template_defined
- layouts: template_variants

### design-from-scratch
- template: custom_master
- master: user_created
- theme: custom_colors_fonts
- layouts: custom_variety

---

## 自定义内容组织

### linear-flow
- structure: sequential_slides
- navigation: next_previous_only
- sections: none
- progression: straight_line

### sectioned-deck
- structure: grouped_slides
- navigation: section_based
- sections: clearly_defined
- progression: hierarchical

### interactive-deck
- structure: hyperlinked_slides
- navigation: non_linear
- sections: flexible
- progression: user_controlled

---

## 自定义视觉一致性

### manual-consistency
- approach: creator_responsible
- checking: visual_inspection
- enforcement: none
- maintenance: ongoing_effort

### theme-enforced
- approach: slide_master_rules
- checking: automatic_validation
- enforcement: soft_warnings
- maintenance: theme_updates_only

### strict-standards
- approach: design_system_locked
- checking: pre_submission_validation
- enforcement: blocking_violations
- maintenance: centrally_managed

---

## 自定义媒体处理

### embedded-media
- storage: within_presentation
- portability: single_file
- size: large_file_size
- editing: difficult

### linked-media
- storage: external_references
- portability: requires_files
- size: smaller_deck
- editing: easy

### optimized-media
- storage: compressed_embedded
- portability: single_file
- size: optimized
- editing: moderate

---

## 自定义动画级别

### no-animation
- transitions: none
- builds: all_content_visible
- timing: instant
- focus: static

### subtle-animation
- transitions: simple_fades
- builds: incremental_appear
- timing: gentle
- focus: guided

### rich-animation
- transitions: varied_effects
- builds: complex_sequences
- timing: orchestrated
- focus: dynamic

---

## 配置优先级

CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置

---

## 使用示例

### 快速演示
- reading: slides-text
- creation: blank-deck
- organization: linear-flow
- consistency: manual-consistency
- media: embedded-media
- animation: no-animation

### 专业模板
- reading: full-presentation
- creation: template-based
- organization: sectioned-deck
- consistency: theme-enforced
- media: linked-media
- animation: subtle-animation

### 交互式演示
- reading: full-presentation
- creation: design-from-scratch
- organization: interactive-deck
- consistency: strict-standards
- media: optimized-media
- animation: rich-animation
