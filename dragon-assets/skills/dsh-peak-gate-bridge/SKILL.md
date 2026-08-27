---
name: dsh-peak-gate-bridge
description: |
  借鉴 f20880479-lab/dsh-peak-gate v0.2.0（MIT ✅）的 5 类核心设计 + 自研 V1.0（不镜像真源 · DSH Desktop 路径依赖 blocker）。
  5 类借鉴：① peak window 数学 ② 队列数据结构 ③ 拦截逻辑 ④ localStorage schema ⑤ /peakgate 指令表。
  Stage 46 借鉴档轻量 · 与 stage 45.1 dsh-balance-meter (BSD-3) 形成完整 peak/off-peak 成本闭环。
metadata:
  version: "1.0.0"
  date: "2026-08-24"
  license: MIT
  author: 天龙引擎 · Stage 46
  upstream_borrowing:
    - f20880479-lab/dsh-peak-gate v0.2.0 (MIT · 1 天前 · 33+6 测试)
  integration_stage: 46
  integration_mode: "借鉴档（DSH Desktop 路径依赖）"
  triggers:
    - "dsh-peak-gate"
    - "peak gate"
    - "/peakgate"
    - "高峰时段"
    - "排队发送"
    - "off-peak"
    - "半价"
    - "off-peak queue"
---

# dsh-peak-gate-bridge · V1.0（借鉴档 · 轻量）

> **TL;DR**：借鉴 [f20880479-lab/dsh-peak-gate](https://github.com/f20880479-lab/dsh-peak-gate) v0.2.0（**MIT ✅** · JavaScript · 89 KB · 3 ⭐ · 33+6 测试 · **1 天前新项目**）的 **5 类核心设计** + **天龙自研 V1.0**（不镜像真源 · DSH Desktop `D:/download/dsh/` 路径依赖是 blocker · 与 stage 45 dsh-eval-bridge 同模式）。

---

## L0: 一句话描述 (≤15字)

peak/off-peak 排队桥。

---

## L1: 使用场景

当用户需要：
- 在高峰时段（peak 09:00-12:00 / 14:00-18:00 北京时间）拦截发送 + 提示确认
- 排队消息到空闲时段自动以半价发送
- 与 dsh-balance-meter (stage 45.1) 形成 peak/off-peak 价格显示闭环
- 周末全天按空闲价（off-peak）计费
- 在确认卡片上提供 3 个选项：立即发送（高峰价）/ 排队（半价）/ 关闭

---

## L2: 5 类借鉴（dsh-peak-gate V0.2.0 → dsh-peak-gate-bridge V1.0）

### 2.1 peak window 数学（与 stage 45.1 完全一致）

```python
# 参考 stage 45.1 dsh_balance_bridge.is_peak_hour
def is_peak_hour(beijing_dt: datetime) -> bool:
    h = beijing_dt.hour
    return (9 <= h < 12) or (14 <= h < 18)
```

### 2.2 队列数据结构（FIFO with priority + source session + status）

```python
@dataclass
class PeakGateHold:
    id: str
    source_session: str
    content: str
    held_at: str               # ISO timestamp
    auto_send_at: str          # next off-peak time
    status: str                # 'queued' | 'sent' | 'muted' | 'cancelled'
    tag: str                   # 'peak-card' | '/peakgate-hold'
    priority: int = 0
```

### 2.3 拦截逻辑（3 层 · 客户端 API）

```
Layer 1: capture keydown.enter + click on submit button
Layer 2: preventDefault + stopPropagation
Layer 3: show peak confirmation card
         ↳ if /peakgate hold → 入队
         ↳ if 立即发送 → 原价
         ↳ if 关闭 → 取消本次发送，保留草稿
```

> **注**：拦截逻辑是 DSH Web 客户端强耦合，借鉴档**不在 Python 端模拟** —— 改为 CLI 工具**生成 DSH 兼容的 localStorage 配置文件** + 给出 DSH Web 应如何在 capture 阶段插入 3 行 JS 的伪代码参考。

### 2.4 localStorage schema

```typescript
localStorage["dsh.peakGate.settings.v1"] = {
  enabled: boolean,
  timezone: "Asia/Shanghai",
  peakWindows: [
    { start: "09:00", end: "12:00" },
    { start: "14:00", end: "18:00" }
  ],
  offPeakWeekends: boolean
}
localStorage["dsh.peakGate.muted.v1"] = { "2026-08-25|09:00-12:00": true }
localStorage["dsh.peakGate.holds.v1"] = [PeakGateHold, ...]
```

### 2.5 /peakgate 指令表（5 子命令）

| 指令 | 行为 |
|---|---|
| `/peakgate hold <text>` | 把消息排入队列，空闲时段自动发出（半价） |
| `/peakgate list` | 展开队列卡片 |
| `/peakgate remove <seq>` | 按序号删除 |
| `/peakgate cancel` | 清空队列 |
| `/peakgate` | 显示帮助 |

---

## L3: 安装（不镜像真源 → 仅配置 + CLI）

```bash
# 1. 装本 skill（天龙自有，已落 dragon-engine/skills/dsh-peak-gate-bridge/）
# 2. 生成 localStorage 配置文件（DSH Web 导入）
python skills/dsh-peak-gate-bridge/scripts/dsh_peak_gate_bridge.py generate-config \
    --timezone Asia/Shanghai --off-peak-weekends \
    --output ~/.dsh/peak-gate-config.json

# 3. 用户在 DSH Web DevTools console 导入：
#    fetch('/api/peak-gate/config').then(r=>r.json()).then(c=>localStorage.setItem('dsh.peakGate.settings.v1', JSON.stringify(c)))

# 4. 队列管理（CLI 替代 DSH Web 内置 /peakgate 指令）
python skills/dsh-peak-gate-bridge/scripts/dsh_peak_gate_bridge.py hold \
    --session abc --content "task: process docs" \
    --auto-send-at 2026-08-24T18:00
```

---

## L4: 触发词

```
/peakgate · dsh-peak-gate · 高峰闸门 · 排队发送
peak / off-peak · 半价 · 队列管理 · 时段确认
hold / list / remove / cancel
```

---

## L5: 下游协同（10 位置）

| 下游 | 协同 |
|---|---|
| **dsh-balance-meter V0.1.0** (stage 45.1 BSD-3) | **peak/off-peak 价格源**（同步 peak window 数学）|
| **paperclip-cost-control V2.1** (stage 45.1 BSD-3 升级后) | **cost 估算复用** + 月环比含 peak gate 影响 |
| **dsh-trajectory-debug V0.2.0** (stage 44 MIT) | **拦截事件入轨迹**（peak hold → trajectory event）|
| **dsh-eval-bridge V1.0** (stage 45 MIT 借鉴档) | **benchmark 含 peak 验证**（test suite 加 peak window）|
| **session-distiller V1.1** (stage 44 MIT) | **peak gate 决策入 L0**（hold 决策写入 raw）|
| **meta-prism V1.1** (stage 45 MIT) | **peak gate 模式做 SLOP-04 校**（user 是否 bypass peak gate）|
| **04-validator V9.06** (stage 45 MIT) | FMEA 加 "未考虑 peak 时段" 失败模式 |
| **09-03 meta-reviewer v2.0** | /perf 加 peak gate 影响 metric |
| **39 chief-of-staff V2.1** | daily summary 含 peak gate 拦截计数 |
| **stage 45 dsh-eval-bridge V1.0** | LLM judge 评估时含 "peak gate interception score" |

---

## L6: DON'T 护栏（5 条）

- ❌ **不要**镜像 dsh-peak-gate 真源（DSH Desktop 路径依赖 blocker）
- ❌ **不要**默认开启 peak gate（每个用户的发送节奏不同，opt-in）
- ❌ **不要**在 IME 中文输入时拦截（`isComposing` 检测是 DSH Web 端必做）
- ❌ **不要**让 hold 队列无限增长（TTL 默认 7 天，到期清理）
- ❌ **不要**peak window 与官方政策脱节时（**`/peakgate` 需有"以官方价格表为准"免责**）

---

## L7: 验证矩阵

| # | 必检项 | 期望 | 状态 |
|---|---|---|---|
| 1 | peak window 数学（与 stage 45.1 一致）| Beijing 09-12 / 14-18 | ✅ |
| 2 | 队列数据结构（FIFO + status + tag）| 4 字段校验 | ✅ |
| 3 | localStorage schema 生成 | 3 keys 校验 | ✅ |
| 4 | /peakgate 5 指令 parser | regex 解析 5 模式 | ✅ |
| 5 | 5 个 unittest PASS（math/queue/schema/parser/integrate）| 5/5 | ⏳ |

---

## L8: 与 Stage 45.1 dsh-balance-meter 协同矩阵

| 维度 | dsh-balance-meter V0.1.0 (BSD-3) | **dsh-peak-gate V0.2.0 (MIT)** |
|---|---|---|
| 聚焦 | 余额读取 + 4 buckets cost | **高峰拦截 + 排队 + 半价** |
| 客户端技术 | service.js + Web UI | client.js + 拦截器 |
| peak/off-peak 数学 | ✅ 一致 | ✅ 一致 |
| 单元测试 | 12/12 (实测) | 33+6 (上游声明 · DSH Desktop 路径依赖) |
| 集成模式 | 真源镜像轻量 | **借鉴档轻量** |
| 共同点 | 同一个 time window（Beijing 09-12 / 14-18）官方政策 | **= peak/off-peak 成本治理闭环** |

---

## L9: 参考链接

- **借鉴源**：https://github.com/f20880479-lab/dsh-peak-gate v0.2.0 · MIT
- **借鉴模式先例**：[`skills/dsh-eval-bridge/SKILL.md`](../dsh-eval-bridge/SKILL.md)（Stage 45 借鉴档）
- **上游协议治理基线**：[`docs/dsh-ecosystem-license-policy.md`](../../../docs/dsh-ecosystem-license-policy.md)
- **Stage 45.1 兄弟借鉴**：[`skills/dsh-balance-meter-integration/SKILL.md`](../dsh-balance-meter-integration/SKILL.md)
- **Stage 46 主题文件**：[`memory/stage-46-dsh-peak-gate.md`](../../../memory/stage-46-dsh-peak-gate.md)
- **Stage 46 评估报告**：本目录 scratch 路径
