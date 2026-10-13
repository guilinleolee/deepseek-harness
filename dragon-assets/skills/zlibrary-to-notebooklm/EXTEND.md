# Z-Library to NotebookLM EXTEND.md

## 默认 Z-Library 转 NotebookLM 配置

---

## 自定义搜索策略 (Custom Search Strategy)

### title-search
- field: title_only
- fuzzy: exact_match
- language: all_languages
- sort: relevance

### advanced-search
- field: all_fields
- fuzzy: fuzzy_match
- language: user_specified
- sort: year_descending

### isbn-search
- field: isbn
- fuzzy: exact_match
- language: n/a
- sort: single_result

---

## 自定义文件格式 (Custom File Format)

### pdf-only
- formats: [PDF]
- quality: any
- size_limit: none
- conversion: none

### pdf-epub
- formats: [PDF, EPUB]
- quality: high_quality
- size_limit: 50mb
- conversion: automatic

### all-formats
- formats: [PDF, EPUB, MOBI, DJVU]
- quality: best_available
- size_limit: 100mb
- conversion: smart

---

## 自定义下载策略 (Custom Download Strategy)

### direct-download
- method: direct_link
- retry: 0
- speed: unlimited
- verification: none

### retry-download
- method: mirror_fallback
- retry: 3
- speed: throttled
- verification: checksum

### smart-download
- method: adaptive
- retry: 5_with_backoff
- speed: optimal
- verification: full_validation

---

## 自定义转换选项 (Custom Conversion Options)

### no-conversion
- enabled: false
- target_format: as_is
- quality: original
- ocr: disabled

### pdf-to-epub
- enabled: pdf_to_epub
- target_format: epub
- quality: high
- ocr: if_needed

### text-extraction
- enabled: text_only
- target_format: txt_md
- quality: readability
- ocr: full

---

## 自定义上传策略 (Custom Upload Strategy)

### manual-upload
- method: manual_drag
- batching: single_file
- metadata: minimal
- organization: manual

### batch-upload
- method: bulk_import
- batching: 10_files
- metadata: auto_extracted
- organization: auto_folder

### smart-upload
- method: intelligent
- batching: adaptive
- metadata: enhanced
- organization: auto_categorized

---

## 自定义元数据提取 (Custom Metadata Extraction)

### basic-metadata
- fields: [title, author]
- source: filename_only
- validation: none
- enhancement: disabled

### standard-metadata
- fields: [title, author, year, publisher]
- source: file_metadata
- validation: sanity_check
- enhancement: google_books

### rich-metadata
- fields: all_fields
- source: multiple_sources
- validation: cross_reference
- enhancement: full_enrichment

---

## 自定义笔记本组织 (Custom Notebook Organization)

### single-notebook
- strategy: all_in_one
- name: Z-Library Imports
- sections: none
- tags: basic

### categorized-notebooks
- strategy: by_category
- name: auto_generated
- sections: by_topic
- tags: auto_tags

### smart-organization
- strategy: semantic_clustering
- name: intelligent
- sections: by_theme
- tags: nlp_generated

---

## 自定义质量控制 (Custom Quality Control)

### no-validation
- checks: none
- corruption: ignored
- completeness: not_checked
- action: proceed_anyway

### standard-validation
- checks: file_integrity
- corruption: basic_check
- completeness: page_count
- action: warn_only

### thorough-validation
- checks: comprehensive
- corruption: deep_scan
- completeness: content_analysis
- action: quarantine_issues

---

## 自定义进度跟踪 (Custom Progress Tracking)

### silent-mode
- display: none
- logging: disabled
- notifications: disabled
- summary: final_only

### progress-bar
- display: percentage
- logging: errors_only
- notifications: milestones
- summary: detailed

### verbose-mode
- display: step_by_step
- logging: full_detail
- notifications: real_time
- summary: comprehensive

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/zlibrary-to-notebooklm/EXTEND.md`
- **用户级**: `~/.claude/skills/zlibrary-to-notebooklm/EXTEND.md`
- **默认级**: `skills/zlibrary-to-notebooklm/EXTEND.md`

---

## 使用示例

### 快速单本书籍导入
```markdown
## Quick Single Book Import

### quick-single-import
- search: title-search
- formats: pdf-only
- download: direct-download
- conversion: no-conversion
- upload: manual-upload
- metadata: basic-metadata
- organization: single-notebook
- quality: no-validation
- tracking: silent-mode
```

### 批量学术文献导入
```markdown
## Batch Academic Import

### batch-academic-import
- search: advanced-search
- formats: pdf-epub
- download: retry-download
- conversion: pdf-to-epub
- upload: batch-upload
- metadata: rich-metadata
- organization: categorized-notebooks
- quality: standard-validation
- tracking: progress-bar
```

### 智能图书馆建设
```markdown
## Smart Library Building

### smart-library
- search: advanced-search
- formats: all-formats
- download: smart-download
- conversion: smart
- upload: smart-upload
- metadata: rich-metadata
- organization: smart-organization
- quality: thorough-validation
- tracking: verbose-mode
```
