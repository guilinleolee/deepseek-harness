---
license: UNKNOWN
name: canary-watch
description: Use this skill to monitor a deployed URL for regressions after deploys, merges, or dependency upgrades.
github_repo: affaan-m/everything-claude-code
github_hash: 4e66b2882da9afb9747468b08a253ca2f09c85f3
last_updated: 2026-04-25
source_type: derived
origin: ECC (everything-claude-code)
triggers: ["canary watch", "Canary Watch — Post-Deploy Monitoring"]
---

# Canary Watch — Post-Deploy Monitoring

> 来源: [affaan-m/everything-claude-code/skills/canary-watch](https://github.com/affaan-m/everything-claude-code)

## 功能概述

在部署后、合并高风险PR后、依赖升级后监控部署URL的回归情况。以循环方式运行直到停止或监控窗口过期。

## 何时使用

- 部署到生产或staging后
- 合并高风险PR后
- 需要验证修复是否真正解决了问题
- 发布窗口期间持续监控
- 依赖升级后

## 监控维度

```
1. HTTP状态 — 页面是否返回200?
2. 控制台错误 — 新出现的错误?
3. 网络失败 — 失败的API调用、5xx响应?
4. 性能 — LCP/CLS/INP相对基线回归?
5. 内容 — 关键元素是否消失?(h1, nav, footer, CTA)
6. API健康 — 关键端点是否在SLA内响应?
```

## 监控模式

### 快速检查 (默认)

```
/canary-watch https://myapp.com
```

### 持续监控

```
/canary-watch https://myapp.com --interval 5m --duration 2h
```

### Diff模式

```
/canary-watch --compare https://staging.myapp.com https://myapp.com
```

## 告警阈值

| 指标 | 阈值 |
|------|------|
| HTTP状态 | 非200 |
| 控制台错误 | > 0 新错误 |
| LCP | > 2.5s |
| CLS | > 0.1 |
| API延迟 | > SLA p99 |

## 天龙引擎集成

### 适用岗位

| 岗位 | 集成方式 | 增强能力 |
|------|---------|---------|
| **08发布师** | 部署后监控 | 持续监控 + 告警 |
| **04验证师** | 发布验证 | 回归检测 + 修复确认 |
| **16-02监控运维师** | 运营监控 | API健康 + SLA追踪 |

### 天龙引擎增强

```
┌─────────────────────────────────────────────────────────────┐
│ 天龙引擎 灰度发布监控体系                                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   部署后:                                                  │
│   /canary-watch --duration 1h --interval 5m               │
│       ↓                                                     │
│   持续监控 → 回归检测 → 告警通知                            │
│                                                             │
│   协同技能:                                                 │
│   ├── /benchmark     → 性能基线对比                       │
│   ├── /browser-qa    → 交互验证                           │
│   └── /eval-harness  → 功能回归检测                        │
│                                                             │
│   告警级别:                                                │
│   🔴 CRITICAL: HTTP非200 / 新错误 / SLA违规                │
│   🟡 WARNING: 性能轻微下降 / 非关键元素缺失                 │
│   🟢 PASS: 所有指标正常                                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 核心命令

```bash
# 快速检查
/canary-watch https://myapp.com

# 持续监控1小时
/canary-watch https://myapp.com --interval 5m --duration 1h

# Staging vs Production对比
/canary-watch --compare https://staging.myapp.com https://myapp.com

# 带告警阈值
/canary-watch https://myapp.com \
  --lcp-threshold 2000 \
  --cls-threshold 0.1 \
  --api-sla-p99 200ms

# 发布后自动触发
[@08] 部署完成后启用canary-watch监控
```

## 与其他技能协同

| 技能 | 协同方式 |
|------|---------|
| **benchmark** | 性能基线设置和对比 |
| **browser-qa** | 完整UI验证 |
| **eval-harness** | 功能回归检测 |

## 参考资料

- [Everything Claude Code](https://github.com/affaan-m/everything-claude-code)
- [ECC canary-watch](https://github.com/affaan-m/everything-claude-code/tree/main/skills/canary-watch)

---

**版本**: V1.0 | **兼容性**: 天龙引擎 V8.67+ | **来源**: ECC
