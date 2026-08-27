---
name: stage-42-4-ghost-os-bridge-placeholder
description: 阶段 42.4 占位 · ghost-os MCP bridge 引入评估 · 当前依赖 DSH 上游 MCP-adapter 未开放
version: 0.0.0 (placeholder)
integration_stage: 42.4
integration_date: 2026-08-24
status: pending_dependency
depends_on: DSH MCP-adapter upstream
modified_by: dragon-engine (user老李)
---

# 阶段 42.4 · ghost-os MCP bridge 引入评估 · 占位

> **TL;DR**:本文件是阶段 42.4 的**占位标记**。当前依赖 **DSH 上游开放 MCP-adapter**(未开放 · 阻塞中)。本占位不实跑任何代码,只提供依赖追踪与决策记录。

---

## 1. 触发条件

- [ ] **DSH 上游开放 MCP-adapter** — 主依赖
- [ ] **用户决策**"是否引入 ghost-os MCP server 作为 DSH 可选 MCP provider"
- [ ] (可选)ghost-os 上游升级到 1.0 GA(当前 v2.1.2 · 已相对稳定)

---

## 2. 阶段 42.4 决策矩阵

详见 [`../docs/stage-42-4-7-roadmap.md`](../docs/stage-42-4-7-roadmap.md) § 阶段 42.4。

**当前建议**:选项 D 观望 — 每月 skill-updater 检测 DSH 上游 MCP-adapter 状态。

---

## 3. 当依赖出现后的实跑步骤

### 3.1 路径 A:DSH MCP plugin 模式(推荐)

```sh
# 1. 装 ghost-os(等依赖满足)
brew install ghostwright/ghost-os/ghost-os
ghost setup

# 2. 写天龙侧 ghost-os → DSH MCP adapter
# 路径: dragon-engine/skills/ghost-os-bridge/
mkdir -p dragon-engine/skills/ghost-os-bridge/{references,scripts,tests}
# SKILL.md:写包装层
# scripts/ghost_cli.py:CLI wrapper
# tests/test_installation.py:验证 5 PASS

# 3. dsh plugin add
dsh plugin --profile web add ./dragon-engine/skills/ghost-os-bridge/

# 4. 集成测试
python tests/test_installation.py
```

### 3.2 路径 B:天龙 SKILL 包装(降级方案)

```sh
# 1. 写天龙侧 wrapper
# 路径: dragon-engine/skills/ghost-os-bridge/scripts/ghost_cli.py
# 调 ghost-os CLI(MCP protocol via JSON-RPC)

# 2. 在 17-04 V2.2 / dsh-computer-use 加 ghost-os 协同段
```

---

## 4. 关键参考

| 资源 | 链接 |
|------|------|
| ghost-os GitHub | https://github.com/ghostwright/ghost-os |
| 阶段 42.4-42.7 决策矩阵 | `../docs/stage-42-4-7-roadmap.md` |
| 生态位对比 | `../references/ecosystem-comparison.md` |
| 主 SKILL.md | `../../SKILL.md` |
| 阶段 42 主题文件 | `../../../../memory/dsh-computer-use-integration.md` |

---

## 5. 风险与未决项

1. **DSH MCP-adapter 开放时间未知** — 等上游决策
2. **ghost-os 与 dsh-computer-use 重叠度大**(都是 macOS Computer Use)— 引入后需明确边界
3. **路径 A 依赖 DSH 上游** — 当前**阻塞**
4. **路径 B 不在 DSH 原生体系内** — 维护成本高

---

## 版本信息

- **V0.0.0(占位)**(2026-08-24):天龙侧占位标记 · 依赖 DSH 上游 MCP-adapter
- **预计 V1.0.0**:DSH 上游 MCP-adapter 开放后 · 路径 A 落地

---

> **下次同步点**:DSH 上游发布 MCP-adapter 后,从 DSH release notes / changelog 检测 → 启动阶段 42.4 实跑。