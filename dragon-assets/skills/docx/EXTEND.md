# DOCX EXTEND.md

## 默认DOCX处理配置

---

## 自定义读取模式 (Custom Reading Mode)

### text-only
- extraction: plain_text
- formatting: stripped
- metadata: ignored
- speed: fastest

### formatted-read
- extraction: rich_text_preserved
- formatting: structure_included
- metadata: basic
- speed: fast

### full-read
- extraction: complete_document
- formatting: fully_preserved
- metadata: all_properties
- speed: moderate

---

## 自定义写入模式 (Custom Writing Mode)

### simple-write
- creation: new_document
- styling: default
- template: none
- compatibility: standard

### styled-write
- creation: formatted_document
- styling: custom_styles
- template: optional
- compatibility: enhanced

### template-write
- creation: template_based
- styling: predefined
- template: required
- compatibility: template_specific

---

## 自定义修订追踪 (Custom Revision Tracking)

### no-tracking
- track_changes: disabled
- authorship: not_recorded
- history: none
- collaboration: sequential

### track-additions
- track_changes: additions_only
- authorship: attributed
- history: insertions_logged
- collaboration: visible

### full-tracking
- track_changes: all_changes
- authorship: fully_attributed
- history: comprehensive
- collaboration: parallel_supported

---

## 自定义批注处理 (Custom Comment Handling)

### no-comments
- comments: ignored
- resolution: none
- export: excluded
- workflow: review_absent

### import-comments
- comments: read_from_doc
- resolution: preserved
- export: as_included
- workflow: review_aware

### manage-comments
- comments: full_crud
- resolution: tracked
- export: resolved_status
- workflow: review_centric

---

## 自定义图片处理 (Custom Image Handling)

### extract-none
- images: ignored
- extraction: none
- quality: na
- storage: external_only

### extract-embedded
- images: extracted_as_base64
- extraction: inline_encoding
- quality: original
- storage: within_file

### extract-external
- images: saved_separately
- extraction: linked_references
- quality: preserved
- storage: external_files

---

## 自定义样式映射 (Custom Style Mapping)

### default-mapping
- approach: word_default_styles
- preservation: minimal
- conversion: basic
- customization: none

### preserve-mapping
- approach: keep_original_styles
- preservation: maximum
- conversion: faithful
- customization: none

### custom-mapping
- approach: user_defined_mapping
- preservation: selective
- conversion: transformed
- customization: extensive

---

## 自定义表格处理 (Custom Table Processing)

### basic-tables
- extraction: simple_grid
- formatting: minimal
- merging: cells_split
- calculation: formulas_lost

### rich-tables
- extraction: formatted_structure
- formatting: preserved
- merging: maintained
- calculation: values_only

### calculated-tables
- extraction: with_formulas
- formatting: full
- merging: complex
- calculation: evaluated

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/docx/EXTEND.md`
- **用户级**: `~/.claude/skills/docx/EXTEND.md`
- **默认级**: `skills/docx/EXTEND.md`

---

## 使用示例

### 简单文档读取
```markdown
## Simple Document Read

### simple-read
- reading: text-only
- writing: simple-write
- revisions: no-tracking
- comments: no-comments
- images: extract-none
- styles: default-mapping
- tables: basic-tables
```

### 协作文档
```markdown
## Collaborative Document

### collaborative-doc
- reading: full-read
- writing: styled-write
- revisions: full-tracking
- comments: manage-comments
- images: extract-external
- styles: preserve-mapping
- tables: rich-tables
```

### 模板工作流
```markdown
## Template Workflow

### template-workflow
- reading: formatted-read
- writing: template-write
- revisions: track-additions
- comments: import-comments
- images: extract-embedded
- styles: custom-mapping
- tables: calculated-tables
```
