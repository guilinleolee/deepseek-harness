# React useEffect EXTEND.md

## 默认 useEffect 最佳实践配置

---

## 自定义依赖数组 (Custom Dependency Array)

### no-deps
- deps: []
- behavior: mount_only
- cleanup: on_unmount
- pattern: mount_effect

### empty-deps
- deps: []
- behavior: mount_only
- cleanup: on_unmount
- pattern: no_prop_warning

### all-deps
- deps: [all_used_vars]
- behavior: re_render
- cleanup: each_update
- pattern: standard

### specific-deps
- deps: [explicit_list]
- behavior: conditional_render
- cleanup: on_dep_change
- pattern: controlled

---

## 自定义清理函数 (Custom Cleanup Function)

### no-cleanup
- cleanup: none
- pattern: no_return
- use_case: side_effects_only
- memory: safe

### basic-cleanup
- cleanup: simple_function
- pattern: return_function
- use_case: event_listeners
- memory: managed

### async-cleanup
- cleanup: promise_abort
- pattern: abort_controller
- use_case: async_operations
- memory: carefully_managed

---

## 自定义Effect时机 (Custom Effect Timing)

### passive-effect
- phase: after_paint
- priority: low
- use_case: analytics_logging
- performance: non_blocking

### layout-effect
- phase: before_paint
- priority: high
- use_case: dom_measurements
- performance: blocking

### immediate-effect
- phase: synchronous
- priority: critical
- use_case: state_updates
- performance: careful

---

## 自定义条件执行 (Custom Conditional Execution)

### unconditional
- condition: none
- runs: every_render
- complexity: simple
- performance: may_suffer

### guard-clause
- condition: early_return
- runs: condition_met
- complexity: clear
- performance: optimized

### conditional-hooks
- condition: separate_hooks
- runs: specific_conditions
- complexity: structured
- performance: clean

---

## 自定义异步处理 (Custom Async Handling)

### async-iife
- pattern: async_iife
- error: try_catch_internal
- cleanup: not_supported
- complexity: simple

### promise-effect
- pattern: direct_promise
- error: then_catch
- cleanup: manual
- complexity: standard

### custom-hook
- pattern: use_async
- error: built_in_handling
- cleanup: automatic
- complexity: reusable

---

## 自定义性能优化 (Custom Performance Optimization)

### no-memo
- memoization: none
- deps: all_renders
- overhead: minimal
- complexity: simple

### use-memo
- memoization: useMemo
- deps: explicit
- overhead: computed_once
- complexity: moderate

### use-callback
- memoization: useCallback
- deps: stable_refs
- overhead: stable_functions
- complexity: functional

---

## 自定义错误处理 (Custom Error Handling)

### ignore-errors
- strategy: silent_fail
- logging: none
- recovery: none
- ux: degraded

### log-errors
- strategy: console_error
- logging: standard
- recovery: none
- ux: degraded

### error-boundary
- strategy: throw_to_boundary
- logging: service
- recovery: fallback_ui
- ux: graceful

### custom-recovery
- strategy: try_catch_recover
- logging: service
- recovery: retry_alternative
- ux: resilient

---

## 自定义测试策略 (Custom Testing Strategy)

### no-testing
- approach: manual
- coverage: none
- tools: none
- confidence: low

### rtl-testing
- approach: react_testing_library
- coverage: effect_scenarios
- tools: [jest, rtl]
- confidence: medium

### custom-hook-testing
- approach: hook_testing
- coverage: all_branches
- tools: [jest, rtl_hook]
- confidence: high

---

## 配置优先级

```
CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置
```

- **项目级**: `.claude/skills/react-useeffect/EXTEND.md`
- **用户级**: `~/.claude/skills/react-useeffect/EXTEND.md`
- **默认级**: `skills/react-useeffect/EXTEND.md`

---

## 使用示例

### 基础数据获取
```markdown
## Basic Data Fetching

### basic-fetch
- deps: specific-deps
- cleanup: no-cleanup
- timing: passive-effect
- conditional: guard-clause
- async: async-iife
- memo: no-memo
- errors: log-errors
- testing: rtl-testing
```

### 事件监听器
```markdown
## Event Listener

### event-listener
- deps: empty-deps
- cleanup: basic-cleanup
- timing: passive-effect
- conditional: unconditional
- async: none
- memo: no-memo
- errors: error-boundary
- testing: rtl-testing
```

### 高性能Effect
```markdown
## High Performance Effect

### high-performance
- deps: specific-deps
- cleanup: async-cleanup
- timing: passive-effect
- conditional: guard-clause
- async: custom-hook
- memo: use-memo + use-callback
- errors: custom-recovery
- testing: custom-hook-testing
```
