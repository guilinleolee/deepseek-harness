# Builder EXTEND.md

## 默认构建师配置

---

## 自定义代码风格 (Custom Code Style)

### functional-style
- paradigm: functional
- immutability: preferred
- side_effects: minimized
- composition: function_composition
- error_handling: monadic

### oop-style
- paradigm: object_oriented
- encapsulation: class_based
- inheritance: single
- polymorphism: interfaces
- design_patterns: gof_patterns

### procedural-style
- paradigm: procedural
- structure: top_down
- modularity: function_based
- state: explicit
- error_handling: return_codes

---

## 自定义命名约定 (Custom Naming Conventions)

### camelCase-convention
- variables: camelCase
- functions: camelCase
- classes: PascalCase
- constants: UPPER_SNAKE_CASE
- files: kebab-case

### snake_case-convention
- variables: snake_case
- functions: snake_case
- classes: PascalCase
- constants: UPPER_SNAKE_CASE
- files: snake_case

### kebab-case-convention
- variables: kebab-case
- functions: kebab-case
- classes: PascalCase
- constants: UPPER_SNAKE_CASE
- files: kebab-case

---

## 自定义注释风格 (Custom Comment Style)

### jsdoc-style
- format: jsdoc
- file_header: required
- function_comments: required
- param_types: documented
- return_types: documented
- examples: included

### minimal-comments
- format: inline
- file_header: optional
- function_comments: complex_only
- param_types: type_system
- return_types: type_system
- examples: none

### comprehensive-comments
- format: documentation_block
- file_header: required
- function_comments: required
- param_types: documented
- return_types: documented
- examples: required
- edge_cases: documented
- performance_notes: included

---

## 自定义错误处理 (Custom Error Handling)

### try-catch-style
- approach: try_catch_blocks
- error_types: custom_classes
- error_context: included
- logging: error_level
- propagation: explicit

### result-type-style
- approach: result_type
- error_types: discriminated_union
- error_context: included
- logging: conditional
- propagation: explicit

### exception-style
- approach: exceptions
- error_types: exception_classes
- error_context: exception_message
- logging: catch_blocks
- propagation: automatic

---

## 自定义代码组织 (Custom Code Organization)

### flat-structure
- organization: flat
- grouping: none
- index_files: false
- barrel_exports: false

### by-type
- organization: type_based
- folders: [components, utils, hooks, types, services]
- index_files: true
- barrel_exports: true

### by-feature
- organization: feature_based
- folders: features/
- index_files: true
- barrel_exports: true
- co_location: enabled

### by-layer
- organization: layer_based
- folders: [ui, domain, infrastructure, application]
- index_files: true
- barrel_exports: true
- dependency_rule: inward_only

---

## 自定义代码质量 (Custom Code Quality)

### clean-code
- functions: small_single_purpose
- parameters: max_3
- nesting: max_3
- magic_numbers: named_constants
- duplication: zero_tolerance

### solid-principles
- single_responsibility: enforced
- open_closed: interfaces
- liskov_substitution: type_safe
- interface_segregation: granular
- dependency_inversion: depend_on_abstractions

### dry-principle
- duplication: none
- abstraction: appropriate
- reusability: high
- maintainability: prioritized

---

## 自定义防御性编程 (Custom Defensive Programming)

### input-validation
- approach: validate_at_boundary
- sanitization: always
- type_checking: strict
- range_checking: enabled
- whitelist_over_blacklist: true

### assertion-checking
- development: enabled
- production: disabled
- types: [preconditions, postconditions, invariants]
- error_messages: descriptive

### fail-safe
- default_values: safe
- error_handling: graceful
- resource_limits: enforced
- timeouts: configured

---

## 自定义性能优化 (Custom Performance Optimization)

### algorithmic-optimization
- complexity: analyzed
- big_o: considered
- data_structures: optimized
- caching: memoization
- lazy_evaluation: where_appropriate

### memory-optimization
- allocation: minimized
- pooling: used
- leaks: prevented
- gc_pressure: minimized
- large_objects: streamed

### concurrency-strategy
- approach: async_await
- parallelism: task_based
- synchronization: minimal
- deadlocks: prevented
- race_conditions: eliminated

---

## 自定义可测试性 (Custom Testability)

### dependency-injection
- pattern: constructor_injection
- mocks: easily_injectable
- test_doubles: interface_based
- state: isolated
- side_effects: controlled

### pure-functions
- preference: high
- side_effects: isolated
- testability: excellent
- determinism: guaranteed

### test-coverage
- target: 80%
- critical_paths: 100%
- branches: covered
- edge_cases: included

---

## 自定义依赖管理 (Custom Dependency Management)

### minimal-dependencies
- philosophy: minimal
- audit_frequency: weekly
- vulnerabilities: zero_tolerance
- licenses: compatible
- bundle_size: optimized

### standard-dependencies
- philosophy: pragmatic
- audit_frequency: monthly
- vulnerabilities: scan_ci_cd
- licenses: approved_list
- bundle_size: monitored

### framework-agnostic
- philosophy: vanilla
- lock_in: avoided
- abstractions: custom
- migration_path: clear

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/builder/EXTEND.md`
- **用户级**: `~/.claude/skills/builder/EXTEND.md`
- **默认级**: `skills/builder/EXTEND.md`

---

## 使用示例

### React 应用
```markdown
## React Application

### react-app
- style: functional-style
- naming: camelCase-convention
- comments: jsdoc-style
- error_handling: try-catch-style
- organization: by-feature
- quality: clean-code + solid-principles
- defensive: input-validation
- performance: algorithmic-optimization
- testability: dependency-injection
- dependencies: minimal-dependencies
```

### Python 服务
```markdown
## Python Service

### python-service
- style: oop-style
- naming: snake_case-convention
- comments: comprehensive-comments
- error_handling: exception-style
- organization: by-layer
- quality: clean-code + solid-principles
- defensive: input-validation + assertion-checking
- performance: algorithmic-optimization + memory-optimization
- testability: pure-functions
- dependencies: standard-dependencies
```

### Node.js 微服务
```markdown
## Node.js Microservice

### nodejs-microservice
- style: functional-style
- naming: camelCase-convention
- comments: jsdoc-style
- error_handling: result-type-style
- organization: by-type
- quality: clean-code + dry-principle
- defensive: input-validation + fail-safe
- performance: concurrency-strategy
- testability: dependency-injection
- dependencies: minimal-dependencies
```
