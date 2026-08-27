# PDF EXTEND.md

## 默认PDF处理配置

---

## 自定义提取模式 (Custom Extraction Mode)

### text-only
- content: text_characters_only
- images: ignored
- tables: linearized
- layout: stripped

### structured-text
- content: reading_order_preserved
- images: captions_only
- tables: structure_detected
- layout: approximate

### full-content
- content: everything_extracted
- images: included_references
- tables: fully_parsed
- layout: position_aware

---

## 自定义OCR策略 (Custom OCR Strategy)

### no-ocr
- method: text_extraction_only
- languages: not_applicable
- accuracy: depends_on_pdf
- speed: fast

### basic-ocr
- method: tesseract_based
- languages: single_language
- accuracy: moderate
- speed: moderate

### advanced-ocr
- method: ai_enhanced
- languages: multi_language
- accuracy: high
- speed: slow

---

## 自定义表格解析 (Custom Table Parsing)

### no-parsing
- method: extract_as_text
- structure: lost
- headers: not_identified
- cells: linear

### stream-parsing
- method: whitespace_separated
- structure: approximate
- headers: inferred
- cells: detected

### lattice-parsing
- method: line_based_detection
- structure: preserved
- headers: identified
- cells: bounded

---

## 自定义图像提取 (Custom Image Extraction)

### none
- extraction: skipped
- quality: na
- format: na
- storage: na

### low-resolution
- extraction: quick_preview
- quality: screen_dpi
- format: jpeg
- storage: embedded

### high-resolution
- extraction: full_quality
- quality: original_dpi
- format: png_tiff
- storage: separate_files

---

## 自定义元数据处理 (Custom Metadata Handling)

### ignore-metadata
- extraction: content_only
- properties: discarded
- encryption: skipped
- permissions: not_respected

### basic-metadata
- extraction: standard_properties
- properties: author_title_dates
- encryption: noted
- permissions: read_only

### full-metadata
- extraction: all_properties
- properties: complete_xmp
- encryption: documented
- permissions: enforced

---

## 自定义合并行为 (Custom Merging Behavior)

### append-only
- method: simple_concatenation
- page_numbers: reset_per_file
- bookmarks: not_preserved
- consistency: loose

### intelligent-merge
- method: page_renumbering
- page_numbers: continuous
- bookmarks: merged_hierarchy
- consistency: maintained

### overlay-merge
- method: layered_composition
- page_numbers: overlaid
- bookmarks: source_preserved
- consistency: complex

---

## 自定义分割策略 (Custom Splitting Strategy)

### single-page
- unit: individual_pages
- naming: page_based
- batching: one_by_one
- output: many_files

### page-range
- unit: specified_ranges
- naming: range_based
- batching: grouped
- output: selective_files

### bookmark-split
- unit: chapter_sections
- naming: bookmark_based
- batching: logical_sections
- output: structured_files

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/pdf/EXTEND.md`
- **用户级**: `~/.claude/skills/pdf/EXTEND.md`
- **默认级**: `skills/pdf/EXTEND.md`

---

## 使用示例

### 快速文本提取
```markdown
## Quick Text Extraction

### quick-text
- extraction: text-only
- ocr: no-ocr
- tables: no-parsing
- images: none
- metadata: ignore-metadata
- merge: append-only
- split: single-page
```

### 文档归档
```markdown
## Document Archiving

### document-archive
- extraction: full-content
- ocr: advanced-ocr
- tables: lattice-parsing
- images: high-resolution
- metadata: full-metadata
- merge: intelligent-merge
- split: bookmark-split
```

### 搜索索引
```markdown
## Search Indexing

### search-index
- extraction: structured-text
- ocr: basic-ocr
- tables: stream-parsing
- images: low-resolution
- metadata: basic-metadata
- merge: append-only
- split: page-range
```
