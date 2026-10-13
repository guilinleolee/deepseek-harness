---
name: booster
description: booster - 天龙Agent Booster命令
invokable: true
---
# /booster - 天龙Agent Booster命令

基于WASM的超快速代码编辑（352x加速，零API成本）。

## 使用方式

```bash
/booster edit <file> "<instruction>"     # 单文件编辑
/booster batch <pattern> "<instruction>" # 批量编辑
/booster parse <markdown-file>           # 解析Markdown代码块
/booster benchmark                       # 性能基准测试
```

## 功能说明

### 1. 单文件编辑 (edit)

```bash
/booster edit src/app.js "Add error handling"
/booster edit server.ts "Convert to async/await"
/booster edit utils.py "Add type hints"
```

**性能**:
- 延迟: <5ms
- 成本: $0
- 相比LLM API: 352x加速

### 2. 批量编辑 (batch)

```bash
/booster batch "src/**/*.js" "Convert var to const"
/booster batch "*.ts" "Add return type annotations"
/booster batch "tests/**/*.test.js" "Remove console.log"
```

**性能**:
- 100文件: ~100ms
- 1000文件: ~1s
- 成本: $0

### 3. Markdown解析 (parse)

解析包含代码块的Markdown文件，自动应用编辑：

```bash
/booster parse refactor-plan.md
/booster parse code-review.md --dry-run
```

### 4. 性能基准测试 (benchmark)

```bash
/booster benchmark --iterations 100
/booster benchmark --file test.js
```

## 支持的操作类型

| 操作 | 说明 | 示例 |
|------|------|------|
| `var-to-const` | 变量转常量 | `var x = 1` → `const x = 1` |
| `add-types` | 添加类型 | `function add(a, b)` → `function add(a: number, b: number)` |
| `add-error-handling` | 添加错误处理 | 添加 try-catch |
| `async-await` | 转换异步 | callback → async/await |
| `add-logging` | 添加日志 | 添加 console.log |
| `remove-console` | 移除console | 删除 console.log |
| `add-comments` | 添加注释 | 函数注释 |
| `format-code` | 格式化代码 | Prettier风格 |

## 3-Tier路由策略

```
┌─────────────────────────────────────────────────────────┐
│ Tier 1: Agent Booster (WASM)                            │
│   延迟: <1ms  |  成本: $0  |  场景: 简单转换            │
├─────────────────────────────────────────────────────────┤
│ Tier 2: Haiku                                           │
│   延迟: ~500ms  |  成本: $0.0002  |  场景: 简单任务     │
├─────────────────────────────────────────────────────────┤
│ Tier 3: Sonnet/Opus                                     │
│   延迟: 2-5s  |  成本: $0.003-0.015  |  场景: 复杂推理  │
└─────────────────────────────────────────────────────────┘
```

**自动路由**:
- 简单编辑（<30%复杂度）→ Agent Booster
- 中等任务（30-70%复杂度）→ Haiku
- 复杂任务（>70%复杂度）→ Sonnet/Opus

## 选项

```bash
--language <lang>       # 覆盖语言检测
--dry-run, --dry        # 预览变更，不实际修改
--benchmark             # 显示性能对比
--verbose               # 详细输出
--iterations <n>        # 基准测试迭代次数（默认100）
--file <path>           # 基准测试文件
```

## 天龙岗位映射

| 岗位 | 用途 | 效果 |
|------|------|------|
| **03构建师** | 简单编辑用Booster | 效率+200% |
| **06审查师** | 批量代码质量检查 | 检查速度+352x |
| **04验证师** | 批量测试生成 | 测试效率+100% |
| **07记录师** | 文档格式化 | 格式化速度+352x |

## 示例工作流

```bash
# 1. 批量重构：var → const
/booster batch "src/**/*.js" "Convert var to const"

# 2. 添加类型注解
/booster batch "*.ts" "Add return type annotations"

# 3. 移除调试代码
/booster batch "src/**/*.js" "Remove console.log statements"

# 4. 预览变更
/booster edit app.js "Add error handling" --dry-run

# 5. 性能测试
/booster benchmark --iterations 100
```

## 性能对比

| 操作 | LLM API | Agent Booster | 提升 |
|------|---------|---------------|------|
| 单文件编辑 | 352ms | 1ms | **352x** |
| 100文件批量 | 35.2s | 100ms | **352x** |
| 1000文件批量 | 5.9min | 1s | **352x** |
| API成本 | $0.01/次 | $0.00 | **100%节省** |

## 来源

> [ruvnet/ruflo](https://github.com/ruvnet/ruflo) - Agent Booster WASM引擎
> 集成方案: [analysis/RUFLO-P0-INTEGRATION-PLAN.md](analysis/RUFLO-P0-INTEGRATION-PLAN.md)