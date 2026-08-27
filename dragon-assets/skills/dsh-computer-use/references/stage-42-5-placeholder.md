---
name: stage-42-5-desktop-pilot-bridge-placeholder
description: 阶段 42.5 占位 · desktop-pilot-mcp MCP bridge 引入评估 · 30-100x 快但需 DSH MCP-adapter
version: 0.0.0 (placeholder)
integration_stage: 42.5
integration_date: 2026-08-24
status: pending_dependency
depends_on: DSH MCP-adapter upstream
modified_by: dragon-engine (user老李)
---

# 阶段 42.5 · desktop-pilot-mcp MCP bridge 引入评估 · 占位

> **TL;DR**:本文件是阶段 42.5 的**占位标记**。[desktop-pilot-mcp](https://github.com/VersoXBT/desktop-pilot-mcp) 提供 **30-100x 速度提升** + 4 层智能路由 + AppleScript 集成,但需 DSH 上游 MCP-adapter。当前阻塞。

---

## 1. 触发条件

- [ ] **DSH 上游开放 MCP-adapter** — 主依赖
- [ ] **用户决策**"是否引入 desktop-pilot-mcp 替代/补充 dsh-computer-use"
- [ ] (可选)desktop-pilot-mcp 上游升级到 1.0 GA(当前早期)

---

## 2. 阶段 42.5 决策矩阵

详见 [`../docs/stage-42-4-7-roadmap.md`](../docs/stage-42-4-7-roadmap.md) § 阶段 42.5。

**当前建议**:选项 D 观望 — 每月 skill-updater 检测 DSH 上游。

### 2.1 速度对比(关键决策依据)

| 操作 | dsh-computer-use | desktop-pilot-mcp | 提速 |
|------|-----------------|-------------------|------|
| Snapshot 读 UI tree | SkyLight 慢 | **20ms vs 3000ms** | 150x |
| Click element | SkyLight | **50ms vs 3000ms** | 60x |
| Read element value | SkyLight | **<1ms vs 3000ms** | 3000x |
| Find buttons by role | SkyLight | **4ms vs 3000ms** | 750x |
| Type text | SkyLight | **20ms vs 4000ms** | 200x |
| Full flow | 14s | **450ms** | 30x |

### 2.2 4 层智能路由(借鉴设计)

```
                 ┌────────────────────┐
                 │   Smart Router     │
                 └─────────┬──────────┘
                           │
       ┌─────────┬─────────┼─────────┬─────────┐
   ┌───▼───┐ ┌───▼───┐ ┌───▼───┐ ┌───▼───┐
   │AX     │ │Apple   │ │CGE    │ │Screen │
   │Layer  │ │Script  │ │vent   │ │shot   │
   │Pri:0  │ │Pri:20  │ │Pri:40 │ │Pri:50 │
   └───────┘ └────────┘ └───────┘ └───────┘
```

---

## 3. 当依赖出现后的实跑步骤

```sh
# 1. 装 desktop-pilot-mcp
npx desktop-pilot-mcp

# 2. 写天龙侧 wrapper(路径 A / B / C 决策待定)
# 路径: dragon-engine/skills/desktop-pilot-bridge/

# 3. 在 17-04 V2.2 / dsh-computer-use 加协同段
# (核心设计借鉴)
```

---

## 4. 关键参考

| 资源 | 链接 |
|------|------|
| desktop-pilot-mcp | https://github.com/VersoXBT/desktop-pilot-mcp |
| 阶段 42.4-42.7 决策矩阵 | `../docs/stage-42-4-7-roadmap.md` |
| 生态位对比 | `../references/ecosystem-comparison.md` |
| 主 SKILL.md | `../../SKILL.md` |

---

## 5. 风险与未决项

1. **DSH MCP-adapter 未开放** — 阻塞
2. **路径 A 替代 vs 路径 B 补充** — 决策待定
3. **30-100x 速度优势诱人** — 但需 DSH MCP-adapter 配合

---

## 版本信息

- **V0.0.0(占位)**(2026-08-24):天龙侧占位 · 依赖 DSH 上游 MCP-adapter
- **预计 V1.0.0**:DSH 上游 MCP-adapter 开放后 · 路径 A 或 B 落地

---

> **下次同步点**:DSH 上游发布 MCP-adapter 后,从 DSH release notes 检测 → 启动阶段 42.5 实跑。