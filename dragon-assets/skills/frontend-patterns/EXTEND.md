# Frontend Patterns EXTEND.md

## 默认前端模式配置

---

## 自定义架构模式

### component-based
- structure: react_components
- organization: by_feature
- state: local_first
- scalability: moderate

### atomic-design
- structure: atoms_molecules_organisms
- organization: hierarchical
- state: lifting_up
- scalability: high

### feature-based
- structure: feature_modules
- organization: by_domain
- state: collocated
- scalability: very_high

---

## 自定义状态管理模式

### redux-pattern
- store: centralized_single_source
- actions: plain_objects
- reducers: pure_functions
- middleware: extensive

### zustand-pattern
- store: simplified_stores
- actions: direct_mutation
- reducers: not_needed
- middleware: minimal

### context-pattern
- store: distributed_contexts
- actions: dispatch_based
- reducers: embedded_reducers
- middleware: none

---

## 自定义数据获取模式

### fetch-on-render
- timing: component_mount
- caching: none
- loading: manual
- stale_data: possible

### react-query-swr
- timing: smart_caching
- caching: automatic_stale_time
- loading: built_in_states
- stale_data: handled_gracefully

### rtk-query-apollo
- timing: normalized_cache
- caching: store_integrated
- loading: atomic_requests
- stale_data: cache_invalidation

---

## 自定义代码分割策略

### no-splitting
- bundling: single_bundle
- loading: initial_fully_loaded
- performance: slow_start
- complexity: none

### route-based
- bundling: per_route_chunks
- loading: lazy_on_navigation
- performance: faster_start
- complexity: moderate

### component-based
- bundling: fine_grained_chunks
- loading: lazy_on_demand
- performance: optimal
- complexity: high

---

## 自定义性能优化

### no-optimization
- memoization: none
- virtualization: none
- lazy: none
- profiling: none

### basic-optimization
- memoization: react_memo
- virtualization: selective
- lazy: code_splitting
- profiling: dev_tools

### aggressive-optimization
- memoization: memo_usememo_callback
- virtualization: all_lists
- lazy: everything_possible
- profiling: continuous_monitoring

---

## 自定义样式模式

### css-modules
- scoping: local_classes
- composition: composable
- runtime: build_time
- maintenance: moderate

### styled-components
- scoping: component_level
- composition: styled_components
- runtime: javascript
- maintenance: high_flexibility

### tailwind-css
- scoping: utility_classes
- composition: class_combinations
- runtime: none_purged
- maintenance: low_consistency

---

## 配置优先级

CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置

---

## 使用示例

### 小型应用
- architecture: component-based
- state: context-pattern
- data: fetch-on-render
- splitting: no-splitting
- performance: no-optimization
- styles: css-modules

### 中型应用
- architecture: atomic-design
- state: zustand-pattern
- data: react-query-swr
- splitting: route-based
- performance: basic-optimization
- styles: styled-components

### 大型应用
- architecture: feature-based
- state: redux-pattern
- data: rtk-query-apollo
- splitting: component-based
- performance: aggressive-optimization
- styles: tailwind-css
