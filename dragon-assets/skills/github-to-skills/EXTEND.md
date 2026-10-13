# GitHub to Skills EXTEND.md

## 默认 GitHub 转 Skills 配置

---

## 自定义仓库分析 (Custom Repository Analysis)

### surface-analysis
- depth: top_level_only
- readme: required_only
- structure: flat
- language: auto_detect

### standard-analysis
- depth: two_levels
- readme: all_readmes
- structure: directory_tree
- language: explicit_detection

### deep-analysis
- depth: full_tree
- readme: all_docs
- structure: semantic_understanding
- language: multi_language_analysis

---

## 自定义代码理解 (Custom Code Understanding)

### signature-only
- functions: signatures_only
- classes: declarations_only
- imports: listed
- comments: ignored

### structure-aware
- functions: signatures_plus_docstrings
- classes: inheritance_hierarchy
- imports: dependency_graph
- comments: documentation_only

### semantic-analysis
- functions: full_analysis
- classes: full_implementation
- imports: usage_analysis
- comments: all_commented_code

---

## 自定义技能模板 (Custom Skill Template)

### minimal-template
- sections: [description, usage]
- examples: 0
- dependencies: listed
- metadata: basic

### standard-template
- sections: all_standard_sections
- examples: 3
- dependencies: categorized
- metadata: comprehensive

### enhanced-template
- sections: all_plus_advanced
- examples: 5_plus
- dependencies: versioned
- metadata: enriched

### custom-template
- sections: user_defined
- examples: user_specified
- dependencies: custom_format
- metadata: custom_schema

---

## 自定义文档生成 (Custom Documentation Generation)

### inline-only
- source: code_comments
- format: markdown
- depth: public_api
- style: minimal

### readme-extraction
- source: existing_readme
- format: original_format
- depth: full_document
- style: preserved

### generated-docs
- source: code_analysis
- format: structured_markdown
- depth: comprehensive
- style: best_practices

### hybrid-docs
- source: multiple_sources
- format: unified_markdown
- depth: smart_merging
- style: enhanced

---

## 自定义测试提取 (Custom Test Extraction)

### no-tests
- extraction: disabled
- adaptation: none
- framework: none
- coverage: 0%

### copy-tests
- extraction: as_is
- adaptation: syntax_only
- framework: original
- coverage: same_as_source

### adapt-tests
- extraction: with_refactoring
- adaptation: skill_format
- framework: standardized
- coverage: optimized

### generate-tests
- extraction: ai_generated
- adaptation: full_rewriting
- framework: best_practice
- coverage: maximum

---

## 自定义依赖处理 (Custom Dependency Handling)

### ignore-dependencies
- mode: skip_all
- installation: manual
- versioning: none
- conflicts: unresolved

### list-dependencies
- mode: document_only
- installation: user_responsible
- versioning: specified
- conflicts: noted

### bundle-dependencies
- mode: include_in_skill
- installation: automatic
- versioning: locked
- conflicts: resolved

### virtual-dependencies
- mode: isolate_per_skill
- installation: isolated_env
- versioning: managed
- conflicts: sandboxed

---

## 自定义质量检查 (Custom Quality Checks)

### no-validation
- enabled: false
- linting: skipped
- standards: none
- security: none

### basic-validation
- enabled: true
- linting: syntax_only
- standards: formatting
- security: obvious_issues

### standard-validation
- enabled: true
- linting: full_lint
- standards: best_practices
- security: known_vulnerabilities

### strict-validation
- enabled: true
- linting: plus_analysis
- standards: style_guide_enforced
- security: full_security_audit

---

## 自定义打包格式 (Custom Packaging Format)

### simple-folder
- format: directory
- compression: none
- metadata: separate_file
- versioning: none

### compressed-package
- format: tar_gz
- compression: max_compression
- metadata: included
- versioning: semver

### skill-package
- format: skill_json
- compression: optimized
- metadata: embedded
- versioning: full_semver

---

## 自定义发布配置 (Custom Publishing Config)

### local-only
- destination: local_directory
- registry: none
- visibility: private
- sharing: manual

### github-release
- destination: github_releases
- registry: github
- visibility: public_private
- sharing: link_based

### skill-registry
- destination: skill_marketplace
- registry: central_registry
- visibility: public
- sharing: discoverable

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/github-to-skills/EXTEND.md`
- **用户级**: `~/.claude/skills/github-to-skills/EXTEND.md`
- **默认级**: `skills/github-to-skills/EXTEND.md`

---

## 使用示例

### 快速转换
```markdown
## Quick Conversion

### quick-conversion
- analysis: surface-analysis
- understanding: signature-only
- template: minimal-template
- documentation: inline-only
- tests: no-tests
- dependencies: ignore-dependencies
- quality: no-validation
- packaging: simple-folder
- publishing: local-only
```

### 标准转换
```markdown
## Standard Conversion

### standard-conversion
- analysis: standard-analysis
- understanding: structure-aware
- template: standard-template
- documentation: readme-extraction
- tests: copy-tests
- dependencies: list-dependencies
- quality: basic-validation
- packaging: compressed-package
- publishing: github-release
```

### 专业级转换
```markdown
## Professional Conversion

### professional-conversion
- analysis: deep-analysis
- understanding: semantic-analysis
- template: enhanced-template
- documentation: hybrid-docs
- tests: adapt-tests
- dependencies: virtual-dependencies
- quality: strict-validation
- packaging: skill-package
- publishing: skill-registry
```
