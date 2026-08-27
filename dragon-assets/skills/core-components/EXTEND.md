# Core Components EXTEND.md

## 默认核心组件配置

---

## 自定义组件粒度

### atomic-components
- size: single_purpose
- reusability: universal
- testing: isolated
- composition: extensive

### feature-components
- size: business_capability
- reusability: domain_specific
- testing: integrated
- composition: moderate

### page-components
- size: complete_view
- reusability: minimal
- testing: end_to_end
- composition: minimal

---

## 自定义样式方法

### css-in-js
- approach: styled_components_emotion
- scoping: component_level
- theming: prop_based
- extraction: build_step

### css-modules
- approach: modular_css
- scoping: class_level
- theming: css_variables
- extraction: automatic

### tailwind-utility
- approach: utility_classes
- scoping: none_prevent_conflict
- theming: config_based
- extraction: purge_unused

---

## 自定义状态管理

### local-state
- scope: component_only
- sharing: props_drilling
- persistence: none
- complexity: low

### context-state
- scope: feature_tree
- sharing: react_context
- persistence: none
- complexity: medium

### global-state
- scope: entire_app
- sharing: state_management_library
- persistence: optional
- complexity: high

---

## 自定义API集成

### direct-fetch
- method: fetch_api
- abstraction: none
- caching: browser_cache
- error_handling: try_catch

### custom-hooks
- method: wrapper_hooks
- abstraction: encapsulated
- caching: optional_state
- error_handling: hook_based

### data-library
- method: react_query_swr_apollo
- abstraction: comprehensive
- caching: built_in_smart
- error_handling: library_features

---

## 自定义表单处理

### controlled-forms
- state: react_state_per_field
- validation: manual
- submission: callback_based
- complexity: verbose

### form-library
- state: library_managed
- validation: schema_based
- submission: library_handled
- complexity: simplified

### uncontrolled-forms
- state: dom_refs
- validation: browser_native
- submission: form_data
- complexity: minimal

---

## 自定义测试策略

### no-tests
- coverage: none
- tooling: none
- automation: manual_only
- confidence: low

### visual-tests
- coverage: screenshot_regression
- tooling: storybook_playwright
- automation: automated_visual
- confidence: visual_only

### unit-tests
- coverage: component_logic
- tooling: jest_vitest
- automation: automated_unit
- confidence: moderate

### comprehensive-tests
- coverage: unit_visual_e2e
- tooling: full_suite
- automation: all_automated
- confidence: high

---

## 配置优先级

CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置

---

## 使用示例

### 快速原型
- granularity: feature-components
- styling: tailwind-utility
- state: local-state
- api: direct-fetch
- forms: uncontrolled-forms
- tests: no-tests

### 标准应用
- granularity: atomic-components
- styling: css-modules
- state: context-state
- api: custom-hooks
- forms: form-library
- tests: unit-tests

### 企业级组件库
- granularity: atomic-components
- styling: css-in-js
- state: global-state
- api: data-library
- forms: form-library
- tests: comprehensive-tests
