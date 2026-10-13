# Skill Creator EXTEND.md

## 默认技能创建配置

---

## 自定义技能模板 (Custom Skill Templates)

### minimal-skill
- files: [SKILL.md]
- structure: flat
- documentation: basic
- examples: 0
- tests: none

### standard-skill
- files: [SKILL.md, EXTEND.md, README.md]
- structure: organized
- documentation: comprehensive
- examples: 2-3
- tests: optional

### advanced-skill
- files: [SKILL.md, EXTEND.md, README.md, examples/, tests/]
- structure: modular
- documentation: exhaustive
- examples: 5+
- tests: comprehensive

### enterprise-skill
- files: [SKILL.md, EXTEND.md, README.md, CHANGELOG.md, CONTRIBUTING.md, examples/, tests/, docs/]
- structure: enterprise
- documentation: professional
- examples: 10+
- tests: full_coverage

---

## 自定义 SKILL.md 模板 (Custom SKILL.md Template)

### basic-template
- sections: [name, description, usage]
- examples: 1
- parameter_docs: minimal
- return_docs: none

### standard-template
- sections: [name, description, parameters, usage, examples, notes]
- examples: 3
- parameter_docs: full
- return_docs: included

### comprehensive-template
- sections: [name, description, parameters, usage, examples, notes, see_also, limitations, troubleshooting]
- examples: 5
- parameter_docs: with_types_and_defaults
- return_docs: with_types

---

## 自定义代码生成 (Custom Code Generation)

### no-code
- code_generation: none
- examples: manual
- stubs: none

### basic-stubs
- code_generation: function_signatures
- examples: manual
- stubs: type_signatures_only

### full-implementation
- code_generation: working_code
- examples: generated
- stubs: working_examples

### best-practices
- code_generation: production_ready
- examples: extensive
- stubs: production_quality_with_error_handling

---

## 自定义测试模板 (Custom Test Template)

### no-tests
- tests: none
- framework: none
- coverage: 0%

### basic-tests
- tests: smoke_tests
- framework: minimal
- coverage: 20%

### standard-tests
- tests: unit_tests
- framework: jest/vitest
- coverage: 60%

### comprehensive-tests
- tests: [unit, integration, e2e]
- framework: full_stack
- coverage: 80%

---

## 自定义文档风格 (Custom Documentation Style)

### minimal-docs
- style: concise
- sections: [description, usage]
- examples: inline
- api_docs: none

### standard-docs
- style: detailed
- sections: [overview, installation, usage, api, examples, troubleshooting]
- examples: separate_section
- api_docs: auto_generated

### comprehensive-docs
- style: exhaustive
- sections: [overview, installation, usage, api, examples, best_practices, troubleshooting, changelog, contributing]
- examples: multiple_sections
- api_docs: detailed_with_versions

---

## 自定义依赖声明 (Custom Dependency Declaration)

### no-dependencies
- dependencies: none
- dev_dependencies: none
- peer_dependencies: none
- optional_dependencies: none

### skill-dependencies
- dependencies: declared
- version_ranges: flexible
- validation: warning_only

### strict-dependencies
- dependencies: declared
- version_ranges: exact
- validation: error_on_mismatch

---

## 自定义版本控制 (Custom Version Control)

### none
- versioning: none
- changelog: none
- migration: none

### semantic-versioning
- versioning: semver
- changelog: keep_a_changelog
- migration: automated
- breaking_changes: major_version

### calendar-versioning
- versioning: calver
- changelog: date_based
- migration: manual

---

## 自定义元数据 (Custom Metadata)

### minimal-metadata
- fields: [name, author, created]
- validation: none

### standard-metadata
- fields: [name, version, author, description, tags, created, updated]
- validation: required_fields

### comprehensive-metadata
- fields: [name, version, author, description, tags, keywords, created, updated, license, repository, compatibility, dependencies]
- validation: strict
- schema: json_schema

---

## 自定义示例格式 (Custom Example Format)

### text-only
- format: markdown
- code_blocks: included
- outputs: described
- interactive: false

### interactive-examples
- format: markdown_with_playground
- code_blocks: runnable
- outputs: actual
- interactive: true

### multi-scenario
- format: use_cases
- scenarios: 5+
- complexity: real_world
- interactive: optional

---

## 自定义最佳实践 (Custom Best Practices)

### none
- best_practices: not_included
- anti_patterns: not_included
- patterns: not_included

### basic-guidance
- best_practices: listed
- anti_patterns: listed
- patterns: listed
- examples: minimal

### detailed-guidance
- best_practices: explained
- anti_patterns: explained
- patterns: explained
- examples: comprehensive

---

## 自定义发布流程 (Custom Publishing Workflow)

### local-only
- publishing: none
- sharing: manual
- repository: none

### git-publish
- publishing: git_push
- sharing: repository_url
- repository: github
- pr: required

### package-publish
- publishing: npm_publish
- sharing: npm_registry
- repository: git_based
- pr: optional

---

## 自定义质量门禁 (Custom Quality Gates)

### no-gates
- checks: none
- blocking: none
- warnings: none

### basic-gates
- checks: [syntax, structure]
- blocking: syntax_only
- warnings: structure_issues

### strict-gates
- checks: [syntax, structure, documentation, tests]
- blocking: all_checks
- warnings: none

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/skill-creator/EXTEND.md`
- **用户级**: `~/.claude/skills/skill-creator/EXTEND.md`
- **默认级**: `skills/skill-creator/EXTEND.md`

---

## 使用示例

### 快速原型
```markdown
## Quick Prototype

### quick-prototype
- template: minimal-skill
- skill_md: basic-template
- code: no-code
- tests: no-tests
- docs: minimal-docs
- dependencies: no-dependencies
- versioning: none
- metadata: minimal-metadata
- examples: text-only
- best_practices: none
- publishing: local-only
- gates: no-gates
```

### 标准技能
```markdown
## Standard Skill

### standard-skill
- template: standard-skill
- skill_md: standard-template
- code: basic-stubs
- tests: standard-tests
- docs: standard-docs
- dependencies: skill-dependencies
- versioning: semantic-versioning
- metadata: standard-metadata
- examples: text-only
- best_practices: basic-guidance
- publishing: git-publish
- gates: basic-gates
```

### 企业级技能
```markdown
## Enterprise Skill

### enterprise-skill
- template: enterprise-skill
- skill_md: comprehensive-template
- code: best-practices
- tests: comprehensive-tests
- docs: comprehensive-docs
- dependencies: strict-dependencies
- versioning: semantic-versioning
- metadata: comprehensive-metadata
- examples: interactive-examples
- best_practices: detailed-guidance
- publishing: package-publish
- gates: strict-gates
```
