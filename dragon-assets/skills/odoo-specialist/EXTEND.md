# Odoo Specialist EXTEND.md

## 默认 Odoo 配置

---

## 自定义模块类型 (Custom Module Type)

### simple-module
- type: basic
- models: 1_5
- views: standard_crud
- security: basic_access
- dependencies: minimal

### business-module
- type: business_logic
- models: 5_20
- views: advanced_ui
- security: record_rules
- dependencies: layered

### integrated-module
- type: full_integration
- models: 20_plus
- views: custom_complex
- security: acls
- dependencies: comprehensive

---

## 自定义ORM模式 (Custom ORM Patterns)

### basic-crud
- operations: [create, read, write, unlink]
- inheritance: none
- delegation: none
- computed: standard_fields

### advanced-orm
- operations: all_operations
- inheritance: prototype_extension
- delegation: enabled
- computed: stored_computed

### expert-orm
- operations: all_plus_custom
- inheritance: multi_inheritance
- delegation: abstract_delegation
- computed: multi_dependent

---

## 自定义视图设计 (Custom View Design)

### list-form-only
- types: [tree, form]
- inheritance: basic
- widgets: standard_widgets
- layout: simple

### full-views
- types: [tree, form, kanban, calendar, graph, pivot]
- inheritance: view_inheritance
- widgets: custom_widgets
- layout: responsive

### advanced-ui
- types: all_plus_custom
- inheritance: deep_inheritance
- widgets: web_widgets
- layout: adaptive

---

## 自定义安全配置 (Custom Security Config)

### public-access
- auth: none
- groups: everyone
- record_rules: none
- ir_rule: disabled

### user-groups
- auth: user_required
- groups: defined_groups
- record_rules: basic_rules
- ir_rule: record_level

### enterprise-security
- auth: multi_factor
- groups: hierarchical
- record_rules: complex_rules
- ir_rule: field_level

---

## 自定义工作流 (Custom Workflow)

### simple-state
- states: 3_5
- transitions: linear
- conditions: simple
- actions: state_changes

### business-process
- states: 5_10
- transitions: conditional
- conditions: complex
- actions: multi_step

### advanced-workflow
- states: unlimited
- transitions: dynamic
- conditions: server_actions
- actions: automated_chains

---

## 自定义API集成 (Custom API Integration)

### controller-only
- type: http_controller
- auth: public
- validation: basic
- response: json

### rest-api
- type: restful
- auth: api_key
- validation: schema_validated
- response: structured

### external-integration
- type: full_integration
- auth: oauth2
- validation: comprehensive
- response: transformed

---

## 自定义报表引擎 (Custom Report Engine)

### qweb-report
- engine: qweb
- format: pdf
- design: basic
- data: direct_record

### custom-report
- engine: qweb_plus_python
- format: pdf_excel
- design: styled
- data: processed_data

### bi-report
- engine: bi_views
- format: dashboards
- design: interactive
- data: aggregated_analytics

---

## 自定义自动化 (Custom Automation)

### scheduled-actions
- type: ir_cron
- triggers: time_based
- logic: python_code
- error_handling: logging

### server-actions
- type: multi_actions
- triggers: event_based
- logic: builder_plus_code
- error_handling: retry_mechanism

### automated-workflows
- type: full_automation
- triggers: complex_conditions
- logic: business_logic
- error_handling: rollback_recovery

---

## 自定义测试策略 (Custom Testing Strategy)

### no-tests
- unit: none
- integration: none
- ui: none
- coverage: 0%

### standard-tests
- unit: model_tests
- integration: api_tests
- ui: none
- coverage: 60%

### comprehensive-tests
- unit: full_coverage
- integration: all_integrations
- ui: tour_tests
- coverage: 90%+

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/odoo-specialist/EXTEND.md`
- **用户级**: `~/.claude/skills/odoo-specialist/EXTEND.md`
- **默认级**: `skills/odoo-specialist/EXTEND.md`

---

## 使用示例

### 简单模块开发
```markdown
## Simple Module Development

### simple-module-dev
- module: simple-module
- orm: basic-crud
- views: list-form-only
- security: public-access
- workflow: simple-state
- api: controller-only
- reports: qweb-report
- automation: scheduled-actions
- tests: no-tests
```

### 业务模块开发
```markdown
## Business Module Development

### business-module-dev
- module: business-module
- orm: advanced-orm
- views: full-views
- security: user-groups
- workflow: business-process
- api: rest-api
- reports: custom-report
- automation: server-actions
- tests: standard-tests
```

### 企业级解决方案
```markdown
## Enterprise Solution

### enterprise-solution
- module: integrated-module
- orm: expert-orm
- views: advanced-ui
- security: enterprise-security
- workflow: advanced-workflow
- api: external-integration
- reports: bi-report
- automation: automated-workflows
- tests: comprehensive-tests
```
