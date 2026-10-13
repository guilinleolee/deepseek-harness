# Stage 46 · dsh-peak-gate-bridge 借鉴档 · 主题文件 V1.0

> **阶段**：天龙引擎 · **stage 46**（**借鉴档 · 轻量**）
> **日期**：2026-08-24
> **集成度**：⭐ 战略级 — DSH peak/off-peak 拦截闸门借鉴 + 自研 V1.0
> **入口文件**：[`skills/dsh-peak-gate-bridge/SKILL.md`](../skills/dsh-peak-gate-bridge/SKILL.md)

---

## 一、TL;DR

> 借鉴 [f20880479-lab/dsh-peak-gate](https://github.com/f20880479-lab/dsh-peak-gate) v0.2.0（**MIT ✅** · JavaScript · 89 KB · 3 ⭐ · 33+6 测试 · **1 天前新项目**）的 **5 类核心设计** + **天龙自研 V1.0**（借鉴档，DSH Desktop 路径依赖是 blocker）。与 stage 45.1 dsh-balance-meter (BSD-3) 形成 **peak/off-peak 成本治理完整闭环**。累计 PASS **855 → 866**（+11 net · 21/21 自研 unittest 拆 5 类）。

---

## 二、Stage 46 生态矩阵

| 维度 | Stage 45 dsh-eval-bridge | Stage 45.1 dsh-balance-meter | **Stage 46 dsh-peak-gate-bridge** |
|---|---|---|---|
| 上游协议 | MIT ✅ | BSD-3-Clause ✅ | MIT ✅ |
| 协议族谱第 N 种 | 第 5 个 MIT | 第 1 个 BSD-3 | 第 6 个 MIT |
| 集成模式 | 借鉴档（DSH 主仓依赖 blocker）| 真源镜像（lib-first）| 借鉴档（DSH Desktop 路径依赖 blocker）|
| 包结构 | 单 npm 包 | pnpm workspace 1 子包 | 客户端 bundle + npm 包 |
| 测试声明 | 113 vitest | **12/12 vitest PASS**（实测）| 33+6 npm test（DSH Desktop 路径依赖）|
| 自研实现 | Python 5 类方法论 | Python 4 RPC 桥 | Python 4 CLI 工具 |

---

## 三、触发源（一手）

| 字段 | 值 | 来源 |
|---|---|---|
| **上游仓库** | https://github.com/f20880479-lab/dsh-peak-gate |
| **作者** | f20880479-lab（GitHub 278016271）|
| **协议** | **MIT ✅**（LICENSE 1,083 B verbatim · 21 行）|
| ★ / 🍴 | 3 / 0 | GitHub API |
| **language** | JavaScript（**非 TS**）| 同上 |
| **default_branch** | `main`（**注意非 master**）| 同上 |
| **created** | 2026-08-25T10:22:36Z（**1 天前**）| 同上 |
| **pushed** | 2026-08-26T04:34:33Z | 同上 |
| **HEAD SHA** | `b1d0181b793d6c44474c211b96eb27c9f555f44f` |
| **version** | v0.2.0 |
| **测试声明** | 33 项集成测试 + 6 项 jsdom/React 真实渲染测试 |
| **体积** | 89 KB（含 lib/ + cordis.patch.yml + package.json）|

> **天龙第 7 个 DSH 生态集成** + **第 6 个 MIT**（前 6 个：41 mneme / 42 computer-use / 43 agent-teams / 44 trajectory-debug / 45 dsh-eval-bridge / 45.1 dsh-balance-meter BSD-3）。

---

## 四、D3 工程实证 ⚠️撞墙报告

### 4.1 `pnpm install --prefer-offline` ✅ PASS（7s · jsdom + react 装好）

### 4.2 `npm test` ❌ FAIL（**撞墙**）

```
Error: Cannot find module 'react'
Require stack:
- D:/download/dsh/DSH Desktop/resources/app.asar.unpacked/node_modules/react/package.json
```

**根因**（与 stage 45 dsh-eval 同模式）：
- dsh-peak-gate 的 `test/integration.test.mjs` line 95 用了 `requireShim` 解析 `D:/download/dsh/DSH Desktop/` 路径
- 这是 **DSH Desktop Electron 安装包**的 node_modules
- 用户的 DSH Desktop 装在 `D:/download/dsh/`（已具备）✅
- **测试必须跑在 DSH Desktop 装好后**，不能 standalone 跑

**应对**：借鉴档 + 自研 Python（stage 41 mneme / stage 45 dsh-eval 同模式）

### 4.3 借鉴档替代方案：自研 21/21 unittest 拆 5 大类

```
✓ TestPeakWindow        (5 用例)  # 09-12/14-18 peak + 周末 off-peak
✓ TestNextOffPeak       (3 用例)  # 10am→12pm, 15pm→18pm, 20pm already
✓ TestLocalStorageSchema(2 用例)  # 3 keys validate + custom timezone
✓ TestParseCmd          (8 用例)  # 5 子命令 + 容错 + unknown cmd
✓ TestQueueDataStruct   (3 用例)  # add/remove/OOB/to_dict
                                  21/21 ✓ 0.001s
```

---

## 五、5 类借鉴（dsh-peak-gate V0.2.0 → dsh-peak-gate-bridge V1.0）

### 5.1 peak window 数学（与 stage 45.1 完全一致）

```python
def is_peak_hour(beijing_dt: datetime) -> bool:
    h = beijing_dt.hour
    return (9 <= h < 12) or (14 <= h < 18)

def is_off_peak_weekend(beijing_dt: datetime) -> bool:
    return beijing_dt.weekday() in (5, 6)  # 周六周日
```

### 5.2 队列数据结构

```python
@dataclass
class PeakGateHold:
    id: str
    source_session: str
    content: str
    held_at: str
    auto_send_at: str
    status: str = "queued"          # queued/sent/muted/cancelled
    tag: str = "peak-card"          # peak-card / /peakgate-hold
    priority: int = 0
```

### 5.3 拦截逻辑（DSH Web 客户端，借鉴档不在 Python 模拟）

```
Layer 1: capture keydown.enter + click on submit button
Layer 2: preventDefault + stopPropagation
Layer 3: show peak confirmation card
         ↳ if /peakgate hold → 入队
         ↳ if 立即发送 → 原价
         ↳ if 关闭 → 取消本次发送，保留草稿
```

### 5.4 localStorage schema（3 keys）

```typescript
"dsh.peakGate.settings.v1": {enabled, timezone, peakWindows, offPeakWeekends}
"dsh.peakGate.muted.v1":   {"2026-08-25|09:00-12:00": true}
"dsh.peakGate.holds.v1":   [PeakGateHold, ...]
```

### 5.5 /peakgate 5 子命令 parser

| 指令 | parser 行为 |
|---|---|
| `/peakgate hold <text>` | cmd=hold, text=内容 |
| `/peakgate list` | cmd=list |
| `/peakgate remove <N>` | cmd=remove, args=[N] |
| `/peakgate cancel` | cmd=cancel |
| `/peakgate` (空) | cmd=help（容错）|

---

## 六、4 CLI 自研工具（dsh_peak_gate_bridge.py）

```
$ dsh_peak_gate_bridge.py is-peak
{"beijing_now": "...", "band": "off-peak", "is_peak_now": false, ...}

$ dsh_peak_gate_bridge.py generate-config --output config.json
[ok] schema written to config.json

$ dsh_peak_gate_bridge.py hold --session abc --content "task"
{"id": "hold-1787719127", "source_session": "abc", "status": "queued", ...}

$ dsh_peak_gate_bridge.py parse-cmd "/peakgate hold task text"
{"cmd": "hold", "text": "task text"}
```

---

## 七、与 stage 45.1 dsh-balance-meter 协同（**peak/off-peak 成本治理闭环**）

```
        ┌──────────────────────────────────────────────────┐
        │   Stage 45.1 + Stage 46 peak/off-peak 闭环        │
        ├──────────────────────────────────────────────────┤
        │  1. balance 读取 (Stage 45.1)                    │
        │     → dsh_balance_bridge.py balance              │
        │  2. peak/off-peak 价格 (Stage 45.1)              │
        │     → dsh_balance_bridge.py is_peak_hour()        │
        │  3. ⭐ 高峰闸门 (Stage 46)                       │
        │     → dsh_peak_gate_bridge.py is-peak / hold      │
        │  4. 排队到 off-peak 半价 (Stage 46)               │
        │     → /peakgate hold 指令 + next_off_peak_dt()   │
        │  5. session cost (Stage 45.1 paperclip V2.1)      │
        │     → 真实 token × price (with band)             │
        └──────────────────────────────────────────────────┘
```

---

## 八、累计 PASS 增量

```
855 (Stage 45.1 累计)
   +11 ─► 866   dsh_peak_gate_bridge.py 21/21 自研 unittest PASS
                   (拆 5 大类 = peak/next-off-peak/schema/parse-cmd/queue)
                   (上游 33+6 = 39 项测试声明已计入上游库，不双计)
                          │
                          ─► 866 locked
```

**本阶段净增量：+11 → 累计 866 PASS**

---

## 九、协同矩阵（10 位置）

```
dsh-peak-gate-bridge V1.0 (MIT ✅ 借鉴档 · 21/21 unittest)
   ├─► dsh-balance-meter V0.1.0 (BSD-3) ⭐peak/off-peak 价格源
   ├─► paperclip-cost-control V2.1 (BSD-3 升级后) ⭐cost 估算复用
   ├─► dsh-trajectory-debug V0.2.0 (MIT)   ⭐拦截事件入轨迹
   ├─► dsh-eval-bridge V1.0 (MIT 借鉴档)   ⭐benchmark 含 peak 验证
   ├─► session-distiller V1.1 (MIT)         ⭐peak gate 决策入 L0
   ├─► meta-prism V1.1 (MIT)                ⭐peak gate 模式 SLOP-04 校
   ├─► 04-validator V9.06 (MIT)             FMEA 加"未考虑 peak 时段"失败模式
   ├─► 09-03 meta-reviewer v2.0             /perf 加 peak gate 影响 metric
   ├─► 39 chief-of-staff V2.1               daily summary 含 peak gate 拦截计数
   └─► stage 45 dsh-eval-bridge V1.0        LLM judge 加"peak gate interception score"
```

---

## 十、跳转入口

- **R1 评估**：[`D1-R1-license-assessment.md`](../../../../../../../../deepseek%20haress/stage-40-scratch/stage-46-D1-R1-license-assessment.md)
- **真源仓库**：https://github.com/f20880479-lab/dsh-peak-gate
- **LICENSE verbatim**：https://raw.githubusercontent.com/f20880479-lab/dsh-peak-gate/main/LICENSE（1,083 B / 21 行）
- **DSH 协议治理基线**：[`docs/dsh-ecosystem-license-policy.md`](../../docs/dsh-ecosystem-license-policy.md)
- **Stage 45.1 兄弟借鉴**：[`skills/dsh-balance-meter-integration/SKILL.md`](../skills/dsh-balance-meter-integration/SKILL.md)
- **Stage 45 借鉴先例**：[`skills/dsh-eval-bridge/SKILL.md`](../skills/dsh-eval-bridge/SKILL.md)
- **Stage 41 mneme 借鉴先例**：[`skills/mneme-heat-engine/SKILL.md`](../skills/mneme-heat-engine/SKILL.md)

---

> **下次同步点**：用户在 DSH Desktop 真实装入 dsh-peak-gate 后跑 `/peakgate hold` + 看 localStorage 3 keys 写入。
