---
license: UNKNOWN
github_repo: ruvnet/ruflo
github_hash: 01070ede81fa6fbae93d01c347bec1af5d6c17f0
last_updated: 2026-04-25
source_type: derived
triggers: ["booster", "Agent Booster - WASM加速代码编辑"]
---
# Agent Booster - WASM加速代码编辑

> 基于WASM的超快速代码编辑，352x加速，零API成本

## 触发词

`/booster`, `booster edit`, `booster batch`, `快速编辑`, `批量编辑`

## 功能

### 1. 单文件编辑
```
/booster edit src/app.js "Add error handling"
/booster edit server.ts "Convert to async/await"
```

### 2. 批量编辑
```
/booster batch "src/**/*.js" "Convert var to const"
/booster batch "*.ts" "Add return type annotations"
```

### 3. 性能基准测试
```
/booster benchmark --iterations 100
```

## 支持的操作类型

| 操作 | 复杂度 | 说明 |
|------|--------|------|
| var-to-const | 0.1 | 变量转常量 |
| add-types | 0.2 | 添加类型注解 |
| add-error-handling | 0.3 | 添加错误处理 |
| async-await | 0.25 | 转换异步 |
| remove-console | 0.1 | 移除console |
| format-code | 0.05 | 格式化代码 |

## 3-Tier路由策略

```
Tier 1: Agent Booster (WASM) - 简单编辑，<1ms，$0
Tier 2: Haiku - 简单任务，~500ms，$0.0002
Tier 3: Sonnet/Opus - 复杂推理，2-5s，$0.003-0.015
```

## 性能数据

| 操作 | LLM API | Agent Booster | 提升 |
|------|---------|---------------|------|
| 单文件编辑 | 352ms | 1ms | **352x** |
| 100文件批量 | 35.2s | 100ms | **352x** |
| API成本 | $0.01/次 | $0.00 | **100%节省** |

## 来源

> [ruvnet/ruflo](https://github.com/ruvnet/ruflo) - Agent Booster WASM引擎