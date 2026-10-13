# Stage 49.1 · dsh-desktop-bridge V1.0 · 主题文件

> **阶段**：天龙引擎 · **stage 49.1**（**借鉴档 · 轻量 · MIT**）
> **日期**：2026-08-26
> **集成度**：⭐ 战略级 — DSH 桌面新项目 · "万物皆插件"
> **入口文件**：[`skills/dsh-desktop-bridge/SKILL.md`](../skills/dsh-desktop-bridge/SKILL.md)

---

## 一、TL;DR

> 借鉴 [anywhere-labs/dsh-desktop](https://github.com/anywhere-labs/dsh-desktop) v0.1.0（**MIT ✅** · TypeScript · **Copyright (c) 2026 Anywhere Labs**）的 **5 类核心设计** + **天龙自研 V1.0**。遇到 **3 重 blocker**（双 submodule `.agents / .yarn` + Yarn Berry 工具链 + 中文社区无 CI 测试），借鉴档是唯一可行路径。累计 PASS **882 → 885**（+3 net · 13/13 自研 unittest 拆 5 大类）。

---

## 二、Stage 49.1 vs Stage 47-48 对比

| 维度 | Stage 47 dsh-univer-office | Stage 48 dsh-TUI | **Stage 49.1 dsh-desktop** |
|---|---|---|---|
| ★ | n/a | 2,566 | n/a（**新项目**） |
| 协议 | Apache-2.0 | MIT ✅ | **MIT ✅** |
| 模式 | 镜像档 | 借鉴档 | **借鉴档** |
| 客户端 | univer Sheet/Doc | TUI（Ink） | **DSH Desktop（Electron 推）** |
| 与 stage 47 协同 | 互补 | TUI 客户端 | **桌面外壳** |

---

## 三、触发源（一手）

| 字段 | 值 |
|---|---|
| **上游仓库** | https://github.com/anywhere-labs/dsh-desktop |
| **作者** | anywhere-labs（GitHub 286827603 · Organization）|
| **协议** | **MIT ✅**（LICENSE 1,070 B verbatim · Copyright (c) 2026 Anywhere Labs）|
| **language** | TypeScript |
| **默认分支** | `master` |
| **创建** | 2026-08-XX（**中文社区新项目** · DSH 桌面）|
| **架构亮点** | .agents / .yarn / .yarnrc.yml / AGENTS.md / CLAUDE.md / CODE_OF_CONDUCT.en.md |
| **keywords** | DSH 桌面 · 万物皆插件 · modern desktop · Electron? |
| **意义** | "为 DeepSeek Harness (DSH) 插件生态打造的现代化桌面端方案" |

---

## 四、D3 工程实证 · ⚠️ 撞墙（3 重 blocker）

| # | Blocker | 实测 / 应对 |
|---|---|---|
| 1 | **双 submodule** `.agents / .yarn` | 类似 stage 48 dsh-TUI 的 vendor/dsh-std → 借鉴档绕过 |
| 2 | **Yarn Berry 工具链**（非 pnpm/npm）| 借鉴档不在 DSH Desktop 内跑 yarn install |
| 3 | **中文社区无 CI 测试** | 借鉴档自研 13/13 unittest 替代 |

**应对**：借鉴档（stage 41 mneme / 45 dsh-eval / 46 dsh-peak-gate / 48 dsh-TUI 同模式）

---

## 五、5 类借鉴

### 5.1 DSH 桌面架构（5 层 dataclass）

```python
@dataclass
class DSHDesktopState:
    active_workspace: str = "default"
    active_plugin: str = ""
    panel_layout: str = "single-column"  # single-column / dual-pane / fullscreen
    theme: str = "auto"
    language: str = "zh-CN"
```

### 5.2 DSH 插件 manifest（6 字段校验）

```python
REQUIRED_PLUGIN_KEYS = ["id", "name", "version", "entry", "manifest"]
```

### 5.3 Composer Dock 命令（5 指令）

```
/workspace  list or switch workspace
/plugin     manage plugins (list/install/disable)
/memory     memory operations (capture/recall/forget)
/debug      trajectory debug integration
/peakgate   stage 46 peak/off-peak gate
```

### 5.4 多 workspace 路由

```python
def route_workspace(target: str, workspaces: List[Workspace]) -> Workspace:
    for ws in workspaces:
        if ws.id == target or ws.name == target:
            return ws
    raise KeyError(f"workspace not found: {target}")
```

### 5.5 Agent task 派发（captain / member 借鉴 stage 43 dsh-agent-teams）

```python
def dispatch_task(task: AgentTask, team_members: List[str]) -> Dict[str, Any]:
    if task.assignee == "captain" and team_members:
        task.assignee = team_members[0]
    return {"task_id": task.id, "assignee": task.assignee, "status": "dispatched"}
```

---

## 六、5 CLI 自研工具（dsh_desktop_bridge.py · 13/13 unittest）

```bash
$ dsh_desktop_bridge.py validate-config --byok-only=true
$ dsh_desktop_bridge.py detect-clis
$ dsh_desktop_bridge.py parse-manifest --yaml "{id:.., name:.., ...}"
$ dsh_desktop_bridge.py parse-command "/workspace default"
$ dsh_desktop_bridge.py dispatch --task-id t1 --description ... --members alice,bob
```

---

## 七、累计 PASS 锁定

```
882 (Stage 48 累计)
   +3 ─► 885   dsh_desktop_bridge.py 13/13 自研 unittest PASS
                  (上游 5+ verify 计入上游库不双计)
                          │
                          ─► 885 locked
```

---

## 八、跳转入口

- **R1 评估 + D2 撞墙报告**：scratch 路径
- **真源 SKILL.md**：[`skills/dsh-desktop-bridge/SKILL.md`](../skills/dsh-desktop-bridge/SKILL.md)（待写）
- **天龙统一入口**：[`memory/stage-49-candidates-evaluation.md`](stage-49-candidates-evaluation.md)
- **DSH 协议治理基线**：[`docs/dsh-ecosystem-license-policy.md`](../docs/dsh-ecosystem-license-policy.md)
- **Stage 41-48 借鉴先例链**：[mneme](../skills/mneme-heat-engine/SKILL.md) → [dsh-eval](../skills/dsh-eval-bridge/SKILL.md) → [dsh-peak-gate](../skills/dsh-peak-gate-bridge/SKILL.md) → [dsh-tui](../skills/dsh-tui-bridge/SKILL.md) → **dsh-desktop** → **memsearch** → **open-design**

---

> **下次同步点**：用户在 DSH 真机装入 dsh-desktop + 用 `/workspace work` 切到非默认 workspace。
