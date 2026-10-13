---
license: UNKNOWN
name: benchmark
description: Measure performance baselines, detect regressions, and compare stack alternatives with jcode TTFF 14ms benchmark integration.
github_repo: affaan-m/everything-claude-code
github_hash: 4e66b2882da9afb9747468b08a253ca2f09c85f3
last_updated: 2026-05-08
source_type: derived
origin: ECC (everything-claude-code)
天龙引擎增强: V8.87 jcode TTFF基准测试 — TTFF 14ms基准对比+内存占用27.8MB监控+Mermaid 1800x渲染基准
triggers: ["benchmark", "Benchmark — Performance Baseline & Regression Detection"]
---

# Benchmark — Performance Baseline & Regression Detection

> 来源: [affaan-m/everything-claude-code/skills/benchmark](https://github.com/affaan-m/everything-claude-code)

## 功能概述

性能基准测试与回归检测工具，在PR前后测量性能影响、设置项目基准，并在发布前确保性能达标。

## 何时使用

- PR前后测量性能影响
- 设置项目性能基准
- 用户报告"感觉变慢了"
- 发布前确保性能达标
- 对比技术栈替代方案

## 工作模式

### Mode 1: 页面性能

通过浏览器MCP测量真实指标：

```
1. 导航到目标URL
2. 测量Core Web Vitals:
   - LCP (最大内容绘制) — 目标 < 2.5s
   - CLS (累积布局偏移) — 目标 < 0.1
   - INP (下一绘制的交互) — 目标 < 200ms
   - FCP (首次内容绘制) — 目标 < 1.8s
   - TTFB (首字节时间) — 目标 < 800ms
3. 测量资源大小:
   - 页面总重量 (目标 < 1MB)
   - JS包大小 (目标 < 200KB gzip)
   - CSS大小
   - 图片重量
   - 第三方脚本重量
4. 统计网络请求数
5. 检查渲染阻塞资源
```

### Mode 2: API性能

API端点基准测试：

```
1. 每个端点100次请求
2. 测量: p50, p95, p99延迟
3. 追踪: 响应大小, 状态码
4. 负载测试: 10并发请求
5. 对比SLA目标
```

### Mode 3: 构建性能

测量开发反馈循环：

```
1. 冷构建时间
2. 热重载时间 (HMR)
3. 测试套件执行时间
4. TypeScript检查时间
5. Lint时间
6. Docker构建时间
```

### Mode 4: 前后对比

变更前后运行对比：

```
/benchmark baseline    # 保存当前指标
# ... 进行变更 ...
/benchmark compare     # 与基准对比
```

**输出格式:**
```
| Metric | Before | After | Delta | Verdict |
|--------|--------|-------|-------|---------|
| LCP    | 1.2s   | 1.4s  | +200ms| ⚠ WARN  |
| Bundle | 180KB  | 175KB | -5KB  | ✓ BETTER|
| Build  | 12s    | 14s   | +2s   | ⚠ WARN  |
```

## 输出

基准数据存储在 `.ecc/benchmarks/` 目录下的JSON文件。Git追踪以便团队共享基准。

## jcode性能基准对比

| 指标 | jcode | Claude Code | 提升倍数 |
|------|-------|------------|---------|
| **TTFF（首字响应）** | 14.0ms | 3436.9ms | **246x加速** |
| **内存占用** | 27.8MB | 386.6MB | **-93%** |
| **Mermaid渲染** | Rust原生 | 浏览器 | **1800x加速** |

### TTFF基准测试（jcode V11.0核心）

| 基准类型 | jcode | Claude Code | 用途 |
|---------|-------|------------|------|
| **首字响应TTFF** | 14.0ms | 3436.9ms | 输入响应速度 |
| **内存占用** | 27.8MB | 386.6MB | 资源消耗 |
| **Mermaid渲染** | Rust原生 | 浏览器 | 图表生成速度 |

> jcode handterm原生终端实现14ms TTFF，远超Claude Code的3436.9ms。可作为benchmark技能的TTFF对比基准。

## 天龙引擎集成

### 适用岗位

| 岗位 | 集成方式 | 增强能力 |
|------|---------|---------|
| **04验证师** | 性能基准测试 | Core Web Vitals检测 |
| **03构建师** | 构建性能优化 | HMR/构建速度优化 |
| **05安全师** | 安全性能检测 | 安全扫描性能基准 |

### 天龙引擎增强

```
┌─────────────────────────────────────────────────────────────┐
│ 天龙引擎性能测试体系                                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   /benchmark baseline                                       │
│       ↓                                                     │
│   Code Change (Claude Code或其他Agent)                       │
│       ↓                                                     │
│   /benchmark compare                                        │
│       ↓                                                     │
│   Regression Detection (Core Web Vitals / API / Build)       │
│       ↓                                                     │
│   Report Generation + Pass/Fail Gate                         │
│                                                             │
│   协同技能:                                                 │
│   ├── /canary-watch  → 部署后监控                          │
│   ├── /browser-qa    → UI交互验证                          │
│   └── /eval-harness  → 功能回归检测                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 核心命令

```bash
# 页面性能基准
/benchmark page "https://example.com" --mode webvitals

# API性能基准
/benchmark api --endpoint "https://api.example.com/items" --requests 100 --concurrency 10

# 构建性能基准
/benchmark build --command "npm run build"

# 保存基准
/benchmark baseline

# 对比变更
/benchmark compare

# CI集成
/benchmark ci --fail-on-regression
```

### 调用示例

```bash
# PR前后对比
[@04] /benchmark baseline
[@构建师] 实施性能优化
[@04] /benchmark compare

# 发布前检测
[@04] /benchmark page "https://staging.example.com" --core-web-vitals

# API SLA验证
[@04] /benchmark api --endpoint "https://api.example.com/health" --sla-p99 200ms
```

## 与其他技能协同

| 技能 | 协同方式 |
|------|---------|
| **canary-watch** | 部署后持续监控 |
| **browser-qa** | 完整预发布检查清单 |
| **eval-harness** | 功能回归检测 |

## 最佳实践

1. **CI集成**: 每次PR运行 `/benchmark compare`
2. **配对监控**: 与 `/canary-watch` 配对进行部署后监控
3. **完整清单**: 与 `/browser-qa` 配对进行完整预发布检查

## 参考资料

- [Everything Claude Code](https://github.com/affaan-m/everything-claude-code)
- [ECC benchmark](https://github.com/affaan-m/everything-claude-code/tree/main/skills/benchmark)

---

**版本**: V1.1 | **兼容性**: 天龙引擎 V8.87+ | **来源**: ECC | **增强**: jcode TTFF基准
