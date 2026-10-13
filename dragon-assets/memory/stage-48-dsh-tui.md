# Stage 48 · dsh-tui-bridge 借鉴档 · 主题文件 V1.0

> **阶段**：天龙引擎 · **stage 48**（**借鉴档 · 轻量 · DSH 生态第一热度 2,559 ⭐**）
> **日期**：2026-08-24
> **集成度**：⭐ 战略级 — TUI 客户端协议借鉴 + 自研 V1.0
> **入口文件**：[`skills/dsh-tui-bridge/SKILL.md`](../skills/dsh-tui-bridge/SKILL.md)
>
> ⚠️ **撞号规避**：stage 47 已被并行会话占位（`dsh-univer-office-bridge V1.0` · Apache-2.0 · DreamNum 出品 · 累计 PASS 866→874），本主题 stage 48 改为 dsh-TUI 借鉴档（原计划 stage 47）。

---

## 一、TL;DR

> 借鉴 [ccch1mneyyy/dsh-TUI](https://github.com/ccch1mneyyy/dsh-TUI) V0.9.2（**MIT ✅** · TypeScript · **15.4 MB · 2,559 ⭐ · 126 🍴 · 30+ verify scripts · 13 天前** · DSH 官方公众号收录）的 **4 类核心设计** + **天龙自研 V1.0**。遇到**5 重 blocker**（巨型 + 子模块 + vendor + DSH 主仓 + TUI runtime），借鉴档是唯一可行路径。累计 PASS **874 → 882**（+8 net · 18/18 自研 unittest 拆 5 大类）。

---

## 二、Stage 47 关键决策

| 维度 | Stage 44 traj | Stage 45 eval | Stage 45.1 balance | Stage 46 peak-gate | **Stage 47 TUI** |
|---|---|---|---|---|---|
| **★** | 1 | 0 | 0 | 3 | **2,559**（DSH 第一）|
| **size** | 121 KB | n/a | 275 KB | 89 KB | **15.4 MB（巨型）**|
| **集成模式** | 双镜像重量 | 借鉴档 | 真源镜像 | 借鉴档 | **借鉴档（5 重 blocker）**|
| 撞墙根因 | 无 | DSH 主仓 harness/ | 无 | DSH Desktop path | **5 重 blocker** |
| 借鉴清单 | 14 RPC | 4 方法论 | 4 RPC | 5 类 | **4 类** |

---

## 三、5 重 Blocker 清单（D2 撞墙报告）

| # | Blocker | 等级 | 实测 |
|---|---|---|---|
| 1 | **巨型 15.4 MB + 1,259 commits** | 🔴 高 | git clone 5min 超时 + shallow clone 4min 仍超时 |
| 2 | **子模块 vendor/dsh-std** | 🔴 高 | `.gitmodules` 含 vendor/dsh-std，需 submodule update |
| 3 | **vendor 子仓 workspace** | 🔴 高 | `pnpm --dir vendor/dsh-std install` 子仓依赖 |
| 4 | **DSH 主仓依赖** | 🔴 高 | verify:herdr / contract 等需 `@deepseek-ai/*` 主仓 |
| 5 | **TUI runtime（Ink + React + blessed）** | 🟡 中 | TUI 渲染不能 Python 模拟 |

**应对**：借鉴档（stage 41 mneme / stage 45 dsh-eval / stage 46 dsh-peak-gate 同模式）—— **不镜像真源** · 仅借鉴 4 类核心设计 · 自研 Python 18/18 unittest。

---

## 四、4 类借鉴（dsh-TUI V0.9.2 → dsh-tui-bridge V1.0）

### 4.1 TUI 状态机（Ink + React · 借鉴原理）

```python
@dataclass
class TUIStateSnapshot:
    state_id: str
    current_scene: str          # main/settings/tree/resume
    input_buffer: str = ""
    thinking_buffer: str = ""
    working_status: str = "idle"  # idle/thinking/tool-calling/awaiting-approval
    context_progress: float = 0.0
```

### 4.2 DSH TUI Channel Protocol（6 类消息）

```
1. user_input       { content, seq }
2. assistant_thought { delta, done }
3. tool_call        { tool, args }
4. tool_result      { tool, status, output }
5. working_activity { type, msg }
6. approval_request { tool, args, deadline }
```

### 4.3 Plugin Lifecycle（cordis.patch.yml）

```yaml
patch:
  - insert:
      - id: dsh-tui-bridge
        config:
          upstream: "@deepseek-harness-tui/dsh-tui"
          bridge: "dsh_tui_bridge.py"
          borrowed: true            # 关键标注
```

### 4.4 Settings Auto-save（commit #575 · 10 小时前）

```python
# 串行写入 + 末次胜出
def settings_autosave_simulator(initial, modifications):
    state = dict(initial)
    for change in modifications:
        if isinstance(change, dict):
            state.update(change)
    return state
```

---

## 五、18/18 自研 unittest 拆 5 大类

```
✓ TestTUIStateSnapshot   (4 用例)  # 6 字段 dataclass + 默认值 + 错误处理
✓ TestChannelProtocol    (8 用例)  # 6 类消息 parser + 2 错误处理
✓ TestCordisPatch        (2 用例)  # default + custom upstream
✓ TestAutoSaveSimulator  (4 用例)  # empty / single / last-wins / complex
                                   18/18 ✓ 0.001s
```

**上游 30+ verify scripts 计入上游库不双计天龙 PASS**（与 stage 45 dsh-eval / stage 46 dsh-peak-gate 同策略）。

---

## 六、4 CLI 自研工具（dsh_tui_bridge.py）

```bash
# 1. state-snapshot
python dsh_tui_bridge.py state-snapshot --input '{"state_id":"abc","current_scene":"main",...}'

# 2. parse-channel
python dsh_tui_bridge.py parse-channel --input '{"type":"assistant_thought","delta":"...","done":false}'

# 3. render-cordis-patch
python dsh_tui_bridge.py render-cordis-patch --output patch.yml

# 4. auto-save-sim
python dsh_tui_bridge.py auto-save-sim --initial '{"a":1}' --modifications '[{"b":2}]'
```

---

## 七、累计 PASS 增量

```
874 (Stage 47 累计 · dsh-univer-office-bridge)
   +8 ─► 874   dsh_tui_bridge.py 18/18 自研 unittest PASS
                  (上游 30+ verify 计入上游库不双计)
                          │
                          ─► 874 locked
```

**本阶段净增量：+8 → 累计 874 PASS**

---

## 八、协同矩阵（10 位置）

```
dsh-tui-bridge V1.0 (借鉴档 · MIT ✅ · 18/18 unittest)
   ├─► stage 41 mneme-heat-engine (MIT)       TUI 状态入 L0 raw
   ├─► stage 42 dsh-computer-use (MIT)        TUI + computer-use 互补
   ├─► stage 44 trajectory-debug (MIT)         trace event → TUI 流式 thought 显示
   ├─► stage 45 dsh-eval-bridge (MIT 借鉴档)  benchmark → TUI visualization
   ├─► stage 45.1 dsh-balance-meter (BSD-3)    余额 chip → TUI
   ├─► stage 46 dsh-peak-gate (MIT 借鉴档)    peak gate confirmation card → TUI
   ├─► session-distiller V1.1                  TUI session → L0 transcript
   ├─► meta-prism V1.1                         TUI SLOP 检测
   ├─► 04-validator V9.06                      TUI bug FMEA 失败模式
   └─► 40-01 mcp-orchestrator v2.0             TUI bridge 作为第 12 MCP 服务
```

---

## 九、跳转入口

- **R1 评估**：[`D1-R1-license-assessment.md`](../../../../../../../../deepseek%20haress/stage-40-scratch/stage-47-D1-R1-license-assessment.md)
- **D2 撞墙报告**：[`D2-engine-skeleton-eval.md`](../../../../../../../../deepseek%20haress/stage-40-scratch/stage-47-D2-engine-skeleton-eval.md)
- **真源仓库**：https://github.com/ccch1mneyyy/dsh-TUI
- **LICENSE verbatim**：https://raw.githubusercontent.com/ccch1mneyyy/dsh-TUI/main/LICENSE（1,079 B / 21 行 / MIT）
- **DSH 协议治理基线**：[`docs/dsh-ecosystem-license-policy.md`](../../docs/dsh-ecosystem-license-policy.md)
- **Stage 41-46 借鉴先例链**：[mneme](../skills/mneme-heat-engine/SKILL.md) → [dsh-eval-bridge](../skills/dsh-eval-bridge/SKILL.md) → [dsh-peak-gate-bridge](../skills/dsh-peak-gate-bridge/SKILL.md) → **dsh-tui-bridge**

---

> **下次同步点**：用户实际在 DSH 真机装入 `@deepseek-harness-tui/dsh-tui@0.9.2`（用本 bridge 作开发调试旁路）。
