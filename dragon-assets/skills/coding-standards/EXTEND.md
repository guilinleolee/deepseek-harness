# Coding Standards EXTEND.md

## 默认编码标准配置

---

## 自定义命名约定

### camel-case
- variables: lowerCamelCase
- constants: UPPER_SNAKE_CASE
- functions: lowerCamelCase
- classes: PascalCase
- consistency: javascript_typescript

### snake-case
- variables: snake_case
- constants: UPPER_SNAKE_CASE
- functions: snake_case
- classes: PascalCase
- consistency: python_ruby

### kebab-case
- variables: kebab_case
- constants: UPPER_KEBAB_CASE
- functions: kebab_case
- classes: PascalCase
- consistency: lisp_clojure

---

## 自定义缩进风格

### spaces
- type: spaces
- width: 2_or_4
- tab_width: expand_to_spaces
- consistency: enforced_by_linter

### tabs
- type: hard_tabs
- width: visual_preference
- tab_width: as_is
- consistency: enforced_by_linter

### mixed
- type: tabs_for_indentation_spaces_for_alignment
- width: tab_for_indent
- tab_width: respect
- consistency: complex_rule

---

## 自定义注释风格

### minimal-comments
- approach: self_documenting_code
- inline: rare_why_only
- docstrings: public_api_only
- examples: none

### standard-comments
- approach: explain_complex_logic
- inline: why_and_what
- docstrings: all_functions
- examples: key_functions

### extensive-comments
- approach: educational_documentation
- inline: comprehensive
- docstrings: full_documentation
- examples: everywhere

---

## 自定义文件组织

### flat-structure
- depth: minimal_nesting
- grouping: by_type
- imports: alphabetical
- consistency: simple

### domain-driven
- depth: feature_based
- grouping: by_domain
- imports: grouped_by_type
- consistency: modular

### layered-architecture
- depth: multi_level
- grouping: by_layer
- imports: strict_layer_rules
- consistency: architectural

---

## 自定义Lint严格度

### permissive-linting
- rules: best_practices_only
- warnings: few
- errors: critical_bugs_only
- enforcement: suggestions

### standard-linting
- rules: community_standards
- warnings: style_issues
- errors: code_quality
- enforcement: ci_checks

### strict-linting
- rules: opinionated_ruleset
- warnings: treated_as_errors
- errors: any_deviation
- enforcement: blocking

---

## 自定义类型检查

### no-type-checking
- typing: none_or_jsdoc
- validation: runtime_only
- coverage: not_tracked
- confidence: low

### basic-type-checking
- typing: partial_annotations
- validation: compile_time_loose
- coverage: key_areas
- confidence: moderate

### strict-type-checking
- typing: fully_annotated
- validation: compile_time_strict
- coverage: 100_percent
- confidence: high

---

## 自定义格式化

### manual-formatting
- approach: human_maintained
- consistency: variable
- pre-commit: not_enforced
- team_alignment: requires_discipline

### auto-formatting
- approach: prettier_black
- consistency: guaranteed
- pre-commit: enforced
- team_alignment: automatic

---

## 配置优先级

CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置

---

## 使用示例

### 快速脚本
- naming: camel-case
- indent: spaces_2
- comments: minimal-comments
- structure: flat-structure
- lint: permissive-linting
- types: no-type-checking
- format: manual-formatting

### 标准项目
- naming: camel-case
- indent: spaces_4
- comments: standard-comments
- structure: domain-driven
- lint: standard-linting
- types: basic-type-checking
- format: auto-formatting

### 企业级代码
- naming: language_standard
- indent: tabs
- comments: extensive-comments
- structure: layered-architecture
- lint: strict-linting
- types: strict-type-checking
- format: auto-formatting
