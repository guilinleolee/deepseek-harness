---
name: 17-04-v22-smart-router-placeholder
description: 阶段 42.7 占位 · 17-04 V2.2 整合 4 层智能路由设计 · 等用户拍板
version: 0.0.0 (placeholder)
integration_stage: 42.7
integration_date: 2026-08-24
status: pending_user_decision
depends_on: user_decision
base_version: 17-04 V2.1(2026-05-08 · 现有)
modified_by: dragon-engine (user老李)
---

# 阶段 42.7 · 17-04 V2.2 整合 4 层智能路由占位

> **TL;DR**:本文件是阶段 42.7 的**占位标记**。当前 17-04 V2.1 用 TuriX-CUA 单层 GUI 模拟。本占位等**用户拍板**"是否升级 V2.2 整合 desktop-pilot-mcp 的 4 层智能路由设计"(AX → AppleScript → CGEvent → Screenshot)。

---

## 1. 触发条件

- [ ] **用户决策**"17-04 V2.2 是否升级整合 4 层路由"
- 暂**无**外部依赖,可独立实施

---

## 2. 4 层智能路由设计(借鉴 desktop-pilot-mcp)

```
                 ┌────────────────────┐
                 │   Smart Router     │
                 │(per-app + per-     │
                 │ action routing)    │
                 └─────────┬──────────┘
                           │
       ┌─────────┬─────────┼─────────┬─────────┐
       │         │         │         │         │
   ┌───▼───┐ ┌───▼───┐ ┌───▼───┐ ┌───▼───┐
   │AX     │ │Apple   │ │CGE    │ │Screen │
   │Layer  │ │Script  │ │vent   │ │shot   │
   │Pri:0  │ │Pri:20  │ │Pri:40 │ │Pri:50 │
   │Universal│ │Script- │ │Raw    │ │Last   │
   │  apps  │ │able    │ │input  │ │resort │
   └───────┘ └────────┘ └───────┘ └───────┘
```

### 2.1 4 层决策表

| 操作 | Scriptable app | Electron app | Native app |
|------|----------------|--------------|------------|
| Snapshot / Read / Find | AX | AX | AX |
| Click | AX | AX | AX |
| Type | CGEvent | AX | CGEvent |
| Script | AppleScript | AX | AX |
| Menu | AX | AX | AX |

---

## 3. 阶段 42.7 决策矩阵

详见 [`../skills/dsh-computer-use/docs/stage-42-4-7-roadmap.md`](../skills/dsh-computer-use/docs/stage-42-4-7-roadmap.md) § 阶段 42.7。

**当前建议**:**待用户决策**。17-04 V2.2 是大升级,建议先评估 V2.1 在三平台的实际稳定性,再决定 V2.2 升级节奏。

---

## 4. 当用户拍板后的实跑步骤

### 4.1 路径 A · 完整 4 层 + smart router(高投入)

```sh
# 1. 备份 V2.1
cp agents/17-04-desktop-automation-engineer.md \
   agents/_archive/17-04-desktop-automation-engineer-V2.1.md

# 2. 创建 V2.2
# 路径: dragon-engine/agents/17-04-desktop-automation-engineer-V2.2.md

# 3. V2.2 加 smart router 子模块
# - 4 层路由决策表
# - per-app classification
# - speedup 验证(30-100x)
```

### 4.2 路径 B · 简化 2 层 + AppleScript 优先(中等投入)

```sh
# 1. 保留 TuriX-CUA 单层
# 2. 加 AppleScript 优先层(macOS only)
# 3. 其他平台保持 TuriX-CUA 兜底
```

### 4.3 路径 C · 不升级

17-04 V2.1 已够用,等 V2.1 在三平台实测稳态后再决定。

---

## 5. 关键参考

| 资源 | 路径 |
|------|------|
| 17-04 V2.1(现有) | `dragon-engine/agents/17-04-desktop-automation-engineer.md` |
| desktop-pilot-mcp | https://github.com/VersoXBT/desktop-pilot-mcp |
| 阶段 42.4-42.7 决策矩阵 | `dragon-engine/skills/dsh-computer-use/docs/stage-42-4-7-roadmap.md` |

---

## 6. 风险与未决项

1. **17-04 V2.2 升级是产品级大改** — 建议先稳态 V2.1 再决策
2. **路径 A 高投入 vs 路径 B 中等** — 路径选择待定
3. **desktop-pilot-mcp 协议未稳定** — 借鉴设计而非镜像代码
4. **TuriX-CUA 框架依赖** — V2.2 是否保持 TuriX 兼容性待定

---

## 版本信息

- **V0.0.0(占位)**(2026-08-24):天龙侧占位 · 等用户拍板
- **预计 V1.0.0**:用户拍板后落地 4 层路由设计

---

> **下次同步点**:用户拍板"升级 17-04 V2.2 整合 4 层路由" → 启动阶段 42.7 实跑。