# Scribe EXTEND.md

## 默认记录师配置

---

## 自定义文档范围

### code-only
- focus: source_code_documentation
- apis: excluded
- guides: excluded
- examples: minimal

### comprehensive
- focus: everything
- apis: full_reference
- guides: extensive
- examples: abundant

### user-centric
- focus: getting_started
- apis: quick_reference
- guides: tutorial_style
- examples: real_world_scenarios

---

## 自定义文档风格

### technical-style
- language: formal_precise
- audience: developers
- depth: implementation_details
- diagrams: uml_architecture

### tutorial-style
- language: conversational
- audience: learners
- depth: step_by_step
- diagrams: screenshots_illustrations

### reference-style
- language: concise
- audience: experienced_users
- depth: complete_api
- diagrams: minimal

---

## 自定义API文档

### jsdoc-style
- method: inline_comments
- extraction: automated
- output: html_or_json
- examples: from_comments

### openapi-spec
- method: spec_first_or_code_generation
- extraction: framework_based
- output: yaml_or_json
- examples: in_spec

### graphql-docs
- method: schema_commented
- extraction: introspection
- output: graphql_playground_docs
- examples: embedded_queries

---

## 自定义README生成

### minimal-readme
- sections: [title, description, install, usage]
- badges: none
- examples: none
- contributing: omitted

### standard-readme
- sections: full_github_standard
- badges: build_coverage_license
- examples: basic
- contributing: included

### comprehensive-readme
- sections: exhaustive_sections
- badges: extensive_ecosystem
- examples: multiple_scenarios
- contributing: detailed_guidelines

---

## 自定义代码注释

### sparse-comments
- philosophy: code_is_self_documenting
- inline: only_non_obvious
- headers: minimal
- todos: none

### moderate-comments
- philosophy: explain_why_not_what
- inline: complex_logic_only
- headers: function_purpose
- todos: tracked

### extensive-comments
- philosophy: documentation_part_of_code
- inline: thorough_explanations
- headers: detailed_javadoc
- todos: todo_tags_everywhere

---

## 自定义示例生成

### no-examples
- approach: none
- complexity: na
- realism: na
- testing: not_included

### basic-examples
- approach: simplified_snippets
- complexity: happy_path
- realism: sanitized
- testing: not_shown

### realistic-examples
- approach: production_like
- complexity: includes_edge_cases
- realism: authentic
- testing: test_included

---

## 自定义文档维护

### manual-maintenance
- updates: developer_responsible
- synchronization: manual
- accuracy: degrades_over_time
- effort: high_initial_low_ongoing

### semi-automated
- updates: code_to_docs_sync
- synchronization: automated_generation
- accuracy: mostly_current
- effort: moderate_ongoing

### docs-as-code
- updates: docs_version_controlled
- synchronization: ci_validated
- accuracy: always_in_sync
- effort: continuous_integration

---

## 配置优先级

CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置

---

## 使用示例

### 快速API文档
- scope: code-only
- style: reference-style
- api: jsdoc-style
- readme: minimal-readme
- comments: sparse-comments
- examples: no-examples
- maintenance: manual-maintenance

### 用户指南
- scope: user-centric
- style: tutorial-style
- api: openapi-spec
- readme: standard-readme
- comments: moderate-comments
- examples: basic-examples
- maintenance: semi-automated

### 企业文档中心
- scope: comprehensive
- style: technical-style
- api: openapi-spec
- readme: comprehensive-readme
- comments: extensive-comments
- examples: realistic-examples
- maintenance: docs-as-code
