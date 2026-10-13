# XLSX EXTEND.md

## 默认XLSX处理配置

---

## 自定义读取模式 (Custom Reading Mode)

### values-only
- extraction: cell_values
- formatting: ignored
- formulas: evaluated_values
- metadata: none

### data-frame
- extraction: structured_data
- formatting: type_inference
- formulas: values_or_formulas
- metadata: basic_headers

### full-workbook
- extraction: everything
- formatting: fully_preserved
- formulas: both_value_and_formula
- metadata: comprehensive

---

## 自定义写入策略 (Custom Writing Strategy)

### simple-write
- approach: overwrite_existing
- formatting: minimal
- formulas: as_values
- validation: none

### update-write
- approach: modify_existing
- formatting: preserve_surrounding
- formulas: maintain_references
- validation: basic

### template-write
- approach: populate_template
- formatting: follow_template
- formulas: preserved_unchanged
- validation: schema_based

---

## 自定义单元格处理 (Custom Cell Handling)

### loose-typing
- inference: per_cell_guess
- coercion: automatic_conversion
- nulls: empty_strings
- errors: as_is

### strict-typing
- inference: explicit_declaration
- coercion: type_must_match
- nulls: null_values
- errors: raise_exception

### smart-typing
- inference: column_based_consistency
- coercion: best_effort
- nulls: configurable
- errors: flag_and_continue

---

## 自定义范围选择 (Custom Range Selection)

### entire-sheet
- scope: full_worksheet
- limits: sheet_boundaries
- filtering: none
- selection: automatic

### named-range
- scope: predefined_names
- limits: range_definition
- filtering: none
- selection: by_name

### query-range
- scope: dynamic_selection
- limits: criteria_based
- filtering: applied
- selection: conditional

---

## 自定义公式处理 (Custom Formula Handling)

### evaluate-only
- approach: compute_values
- storage: results_only
- dependencies: not_tracked
- recalculation: static

### preserve-formulas
- approach: keep_formulas
- storage: formula_text
- dependencies: maintained
- recalculation: excel_based

### hybrid-formulas
- approach: value_with_backup
- storage: both_formats
- dependencies: tracked
- recalculation: configurable

---

## 自定义样式处理 (Custom Style Handling)

### ignore-styles
- approach: plain_data
- preservation: none
- inheritance: flat
- templates: not_applied

### preserve-styles
- approach: keep_existing
- preservation: cell_level
- inheritance: maintained
- templates: source_based

### apply-styles
- approach: use_style_rules
- preservation: selective
- inheritance: rule_based
- templates: pattern_matching

---

## 自定义多工作表处理 (Custom Multi-Sheet Handling)

### first-sheet-only
- scope: single_worksheet
- selection: first_or_named
- cross_sheet: none
- relationships: ignored

### all-sheets
- scope: entire_workbook
- selection: iterate_all
- cross_sheet: sequential
- relationships: flattened

### linked-sheets
- scope: workbook_with_references
- selection: dependency_aware
- cross_sheet: resolved
- relationships: maintained

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/xlsx/EXTEND.md`
- **用户级**: `~/.claude/skills/xlsx/EXTEND.md`
- **默认级**: `skills/xlsx/EXTEND.md`

---

## 使用示例

### 快速数据读取
```markdown
## Quick Data Read

### quick-data
- reading: values-only
- writing: simple-write
- cells: loose-typing
- range: entire-sheet
- formulas: evaluate-only
- styles: ignore-styles
- sheets: first-sheet-only
```

### 数据分析管道
```markdown
## Data Analysis Pipeline

### data-pipeline
- reading: data-frame
- writing: update-write
- cells: smart-typing
- range: named-range
- formulas: preserve-formulas
- styles: preserve-styles
- sheets: all-sheets
```

### 报表模板系统
```markdown
## Report Template System

### report-template
- reading: full-workbook
- writing: template-write
- cells: strict-typing
- range: query-range
- formulas: hybrid-formulas
- styles: apply-styles
- sheets: linked-sheets
```
