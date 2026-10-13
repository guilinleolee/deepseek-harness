# Investigator EXTEND.md

## 默认调研师配置

---

## 自定义调研范围 (Custom Investigation Scope)

### quick-survey
- depth: surface
- time: 15min
- sources: 3-5
- verification: basic
- documentation: minimal

### standard-investigation
- depth: moderate
- time: 1_hour
- sources: 5-10
- verification: cross_reference
- documentation: standard

### deep-dive
- depth: comprehensive
- time: 3_hours
- sources: 10+
- verification: thorough
- documentation: extensive

---

## 自定义代码考古 (Custom Code Archaeology)

### git-history
- commits: analyze
- blame: identify_authors
- timeline: construct
- patterns: find
- rationale: understand

### dependency-analysis
- direct: map
- transitive: analyze
- outdated: identify
- vulnerabilities: check
- alternatives: suggest

### code-coverage
- executed: measure
- untested: find
- dead_code: identify
- duplication: detect
- complexity: analyze

---

## 自定义文档调研 (Custom Documentation Investigation)

### readme-files
- existence: check
- completeness: evaluate
- accuracy: verify
- updates: check_date
- clarity: assess

### api-docs
- existence: check
- completeness: evaluate
- examples: test
- versioning: check
- consistency: verify

### code-comments
- density: measure
- quality: assess
- accuracy: verify
- outdated: find
- style: evaluate

### architecture-docs
- existence: check
- diagrams: find
- decisions: understand
- rationale: document
- outdated: identify

---

## 自定义技术债务发现 (Custom Technical Debt Discovery)

### code-smells
- long_methods: find
- god_classes: identify
- duplicate_code: detect
- complex_conditional: find
- magic_numbers: locate

### design-issues
- coupling: analyze
- cohesion: measure
- abstraction: evaluate
- encapsulation: check
- modularity: assess

### performance-issues
- n+1_queries: detect
- missing_indexes: find
- memory_leaks: identify
- inefficient_algorithms: locate
- unnecessary_computation: find

### security-issues
- sql_injection: check
- xss_vulnerabilities: detect
- hard_coded_secrets: find
- insecure_dependencies: identify
- auth_flaws: locate

---

## 自定义依赖分析 (Custom Dependency Analysis)

### package-analysis
- direct_dependencies: list
- version_constraints: check
- outdated_packages: find
- vulnerable_packages: identify
- license_compatibility: verify

### dependency-graph
- structure: visualize
- circular_dependencies: detect
- unused_dependencies: find
- duplicate_dependencies: identify
- bundle_size: analyze

### supply-chain
- upstream_sources: trace
- maintainers: identify
- activity: check
- security_practices: evaluate
- alternative_sources: consider

---

## 自定义模式发现 (Custom Pattern Discovery)

### design-patterns
- gang_of_four: identify
- enterprise_patterns: find
- domain_patterns: discover
- anti_patterns: detect
- custom_patterns: document

### architectural-patterns
- layering: identify
- separation: analyze
- boundaries: find
- communication: understand
- data_flow: trace

### coding-patterns
- idioms: discover
- conventions: identify
- habits: find
- shortcuts: detect
- workarounds: understand

---

## 自定义根因分析 (Custom Root Cause Analysis)

### bug-tracing
- bug_reports: review
- stack_traces: analyze
- reproduction: attempt
- related_code: examine
- fixes: identify

### issue-investigation
- reported_issues: review
- related_commits: find
- patterns: detect
- root_causes: identify
- systemic_issues: find

### failure-analysis
- crash_logs: analyze
- error_patterns: detect
- environmental_factors: consider
- correlation: find
- causation: establish

---

## 自定义知识提取 (Custom Knowledge Extraction)

### implicit-knowledge
- code_assumptions: extract
- domain_knowledge: identify
- business_rules: discover
- constraints: find
- requirements: infer

### tribal-knowledge
- unwritten_rules: discover
- historical_context: understand
- rationale: capture
- lessons_learned: document
- best_practices: extract

### expertise-areas
- subject_matter_experts: identify
- knowledge_owners: find
- documentation_sources: locate
- tacit_knowledge: capture
- expertise_transfer: facilitate

---

## 自定义报告输出 (Custom Report Output)

### executive-summary
- audience: management
- length: 1_page
- focus: key_findings
- recommendations: prioritized
- detail_level: high

### technical-report
- audience: engineers
- length: 5-10_pages
- focus: technical_details
- recommendations: actionable
- detail_level: comprehensive

### findings-database
- format: searchable
- tags: applied
- relationships: mapped
- updates: ongoing
- access: controlled

---

## 自定义调研方法 (Custom Investigation Methods)

### static-analysis
- tools: [sonarqube, eslint, pylint]
- focus: code_quality
- automation: high
- depth: surface_to_moderate

### dynamic-analysis
- tools: [profiler, debugger, monitoring]
- focus: runtime_behavior
- automation: medium
- depth: moderate_to_deep

### manual-analysis
- methods: [code_reading, experimentation, interviews]
- focus: understanding
- automation: low
- depth: comprehensive

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/investigator/EXTEND.md`
- **用户级**: `~/.claude/skills/investigator/EXTEND.md`
- **默认级**: `skills/investigator/EXTEND.md`

---

## 使用示例

### 快速代码概览
```markdown
## Quick Code Overview

### quick-overview
- investigation: quick-survey
- archaeology: git-history + dependency-analysis
- documentation: readme-files + code-comments
- tech_debt: code-smells
- dependencies: package-analysis
- patterns: design-patterns
- root_cause: none
- knowledge: implicit-knowledge
- output: executive-summary
- methods: static-analysis
```

### 全面技术审计
```markdown
## Comprehensive Technical Audit

### tech-audit
- investigation: deep-dive
- archaeology: git-history + dependency-analysis + code-coverage
- documentation: all_documentation
- tech_debt: all_debt_types
- dependencies: package-analysis + dependency-graph + supply-chain
- patterns: all_patterns
- root_cause: bug-tracing + issue-investigation + failure-analysis
- knowledge: all_knowledge_types
- output: technical-report + findings-database
- methods: static-analysis + dynamic-analysis + manual-analysis
```

### 依赖健康检查
```markdown
## Dependency Health Check

### dependency-health
- investigation: standard-investigation
- archaeology: dependency-analysis
- documentation: readme-files
- tech_debt: design-issues + security-issues
- dependencies: full_dependency_analysis
- patterns: architectural-patterns
- root_cause: issue-investigation
- knowledge: implicit-knowledge
- output: technical-report
- methods: static-analysis + manual-analysis
```
