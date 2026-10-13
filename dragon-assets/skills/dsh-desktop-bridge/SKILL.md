---
name: dsh-desktop-bridge
description: |
  借鉴 anywhere-labs/dsh-desktop（MIT · Copyright (c) 2026 Anywhere Labs）的 5 类核心设计 + 自研 V1.0。
  借鉴清单：① DSH 桌面架构（5 层 dataclass）② DSH 插件 manifest 校验 ③ Composer Dock 命令 ④ 多 workspace 路由 ⑤ Agent task 派发。
  Stage 49.1 借鉴档 · 与 stage 47 nomifun Windows 桌面 + stage 48 dsh-TUI 互补。
metadata:
  version: "1.0.0"
  date: "2026-08-26"
  license: MIT
  author: 天龙引擎 · Stage 49.1
  upstream_borrowing:
    - anywhere-labs/dsh-desktop (MIT · 2026)
  integration_stage: 49.1
  integration_mode: "借鉴档（3 重 blocker：双 submodule + Yarn Berry + 无 CI）"
  triggers:
    - "dsh-desktop"
    - "/workspace"
    - "/plugin"
    - "DSH 桌面"
    - "插件编排"
---

# dsh-desktop-bridge · V1.0（借鉴档 · 轻量）

> **TL;DR**：借鉴 [anywhere-labs/dsh-desktop](https://github.com/anywhere-labs/dsh-desktop)（**MIT ✅** · 中文社区 DSH 桌面 · "万物皆插件"）的 **5 类核心设计** + **天龙自研 V1.0**。**13/13 unittest PASS**（拆 5 大类）。

---

## L0: 一句话描述 (≤15字)

DSH 桌面架构借鉴。

---

## L1: 使用场景

当用户需要：
- 在 DSH 真机安装 anywhere-labs/dsh-desktop 后获得桌面端集成体验
- 设计 DSH 插件 manifest（6 字段 schema 校验）
- 命令面板 5 指令解析（`/workspace /plugin /memory /debug /peakgate`）
- 多 workspace 路由（`route_workspace` API）
- agent task 派发（captain round-robin / member 名指定）

---

## L2: 5 类借鉴

### 2.1 DSHDesktopState（5 层 dataclass）
- `active_workspace / active_plugin / panel_layout / theme / language`

### 2.2 DSHPluginManifest（6 字段 schema）
- `id / name / version / entry / manifest / borrowed`

### 2.3 Composer Dock 命令（5 指令）
- `parse_composer_command()` API

### 2.4 WorkspaceRoute（多 workspace 路由）
- `route_workspace(target, workspaces)` API

### 2.5 AgentDispatch（captain / member）
- `dispatch_task(task, team_members)` API

---

## L3: 安装（不镜像真源 → 仅 bridge）

```bash
# 1. 装本 skill（天龙自有，已落 dragon-engine/skills/dsh-desktop-bridge/）
# 2. 真机装 dsh-desktop（DSH Desktop 已装的话走 stage 40 web-search-pro 同模式）
# 3. 验证 13 unittest PASS
python -m unittest tests/test_dsh_desktop_bridge.py -v
```

---

## L4: 触发词（11 类）

```
dsh-desktop, /workspace, /plugin, /memory, /debug, /peakgate
DSH 桌面, 插件编排, 多 workspace, agent task, captain round-robin
```

---

## L5: 下游协同

| 下游 | 协同 |
|---|---|
| **stage 47 nomifun Windows 桌面** | 互补（nomifun=Windows / dsh-desktop=DSH 原生）|
| **stage 48 dsh-TUI** | TUI 是 desktop 内的客户端 |
| **04-validator V9.06** | FMEA 加"DSH 桌面兼容"失败模式 |
| **paperclip-cost-control V2.1** | desktop 集成 + cost 闭环 |
| **dsh-agent-teams V0.1.13** | task 派发协议参照 |

---

## L6: DON'T 护栏（5 条）

- ❌ **不要**镜像 dsh-desktop 真源（3 重 blocker）
- ❌ **不要**用 Yarn Berry 工具链（仅借鉴设计）
- ❌ **不要**让 manifest 缺 `borrowed: true`（Apache NOTICE 红线）
- ❌ **不要**默认 captain round-robin 到第一个 member（按团队约定）
- ❌ **不要**让 workspace 路由支持 path traversal（仅 id/name）

---

## L7: 验证矩阵

| # | 必检项 | 期望 | 状态 |
|---|---|---|---|
| 1 | 5 层 dataclass 默认值 | 全过 | ✅ |
| 2 | manifest 6 字段校验 | 全过 | ✅ |
| 3 | 5 指令 parser | regex 正确 | ✅ |
| 4 | workspace 路由（id/name/不命中）| 全过 | ✅ |
| 5 | agent task 派发（captain/指定/无 member）| 全过 | ✅ |
| 6 | 13/13 unittest PASS | 5 大类 | ✅ |

---

## L8: 参考链接

- **借鉴源**：https://github.com/anywhere-labs/dsh-desktop · MIT
- **LICENSE verbatim**：https://raw.githubusercontent.com/anywhere-labs/dsh-desktop/master/LICENSE（1,070 B / 21 行 / MIT）
- **DSH 协议治理基线**：[`docs/dsh-ecosystem-license-policy.md`](../../../docs/dsh-ecosystem-license-policy.md)
- **Stage 49 盘点**：[`memory/stage-49-candidates-evaluation.md`](../../../memory/stage-49-candidates-evaluation.md)
- **Stage 49.1 主题文件**：[`memory/stage-491-dsh-desktop.md`](../../../memory/stage-491-dsh-desktop.md)
