---
license: UNKNOWN
name: paperclip-cost-control
description: 成本控制器 v2，预算分配+节流+trajectory 真实成本估算
github_repo: paperclipai/paperclip
github_hash: 70679a33216bae9247b1b6bddc5fcaad1c04e829
last_updated: 2026-08-24
source_type: derived
version: 2.0.0
author: 天龙引擎团队
created: 2026-03-15
updated: 2026-08-24
category: management
upstream:
  - paperclipai/paperclip 70679a3 (天龙自研 fork)
  - devmom/dsh-trajectory-debug v0.2.0 (MIT · Stage 40)
integration_stage: 40
triggers:
  - "paperclip cost control"
  - "Paperclip成本控制器"
  - "trajectory cost"
  - "/cost"
  - "DSH 真实成本"
---

# Paperclip成本控制器 V2.0

## 概述

基于 [paperclipai/paperclip](https://github.com/paperclipai/paperclip) 的成本控制机制，**V2.0 集成 DSH trajectory-debug**：把"真实 token 消耗 × 价格表"做实，给出每个 session 真实花了多少钱。

## 核心能力（V2.0 升级）

| 能力 | V1.0 | V2.0 |
|------|------|------|
| **月度预算** | 已有 | ✓ 保留 |
| **实时追踪** | 已有 | ✓ 保留 |
| **自动节流** | 已有 | ✓ 保留 |
| **审批续费** | 已有 | ✓ 保留 |
| **⭐ Session 真实成本** | ❌ 无 | ✅ 接 trajectory-debug RPC 拉 token + 价格表 = USD |
| **⭐ 月环比** | ❌ 无 | ✅ 30 天 vs 60 天对比 |
| **⭐ 报价生成** | ❌ 无 | ✅ retail_markup_pct 加价后给客户 |

## 与token-optimizer集成

继承 `token-optimizer/scripts/token_tracker.py` 的核心逻辑：
- Token追踪
- 成本计算
- 预算检查
- 节流建议

## 命令

```bash
# 设置预算
/budget set <agent> <amount>

# 查看状态
/budget status [agent]

# 查看历史
/budget history [agent] [--days 30]

# 审批续费
/budget approve <agent> <amount>

# 重置月度预算
/budget reset [agent]
```

## 数据模型

```typescript
interface CostEvent {
  id: string;
  agentId: string;
  provider: string;      // claude, openai, etc.
  model: string;         // claude-sonnet-4-6, gpt-4, etc.
  inputTokens: number;
  outputTokens: number;
  costCents: number;     // 成本（美分）
  ticketId?: string;
  projectId?: string;
  goalId?: string;
  occurredAt: Date;
}

interface AgentBudget {
  agentId: string;
  budgetMonthlyCents: number;
  spentMonthlyCents: number;
  remainingCents: number;
  percentUsed: number;
  status: 'ok' | 'warning' | 'exceeded';
}
```

## 使用示例

### 1. 设置预算

```bash
# 为Agent设置月度预算 $100
/budget set 03builder 10000

# 输出:
# ✅ 预算已设置
# Agent: 03builder
# 月度预算: $100.00
```

### 2. 查看状态

```bash
/budget status

# 输出:
# 📊 预算状态
# ================
# Agent: 03builder
# 月度预算: $100.00
# 已使用: $45.23
# 剩余: $54.77
# 使用率: 45.23%
# 状态: ✅ 正常
```

### 3. 成本追踪

```typescript
// Agent执行任务后自动记录
CostEventDB.create({
  agentId: '03builder',
  provider: 'claude',
  model: 'claude-sonnet-4-6',
  inputTokens: 15000,
  outputTokens: 3000,
  costCents: 45,  // $0.45
  ticketId: 'ticket-123'
});

// 自动更新Agent的spentMonthlyCents
AgentDB.update(agentId, {
  spentMonthlyCents: currentSpent + 45
});
```

## 预算告警

| 使用率 | 状态 | 行为 |
|--------|------|------|
| 0-70% | ✅ 正常 | 无限制 |
| 70-90% | ⚠️ 警告 | 发送通知 |
| 90-100% | 🔴 临界 | 准备暂停 |
| >100% | ❌ 超限 | 自动暂停 |

## 节流机制

```typescript
// 检查预算
function checkBudget(agentId: string): { allowed: boolean; reason?: string } {
  const agent = AgentDB.get(agentId);
  if (!agent) return { allowed: false, reason: 'Agent not found' };

  if (agent.spentMonthlyCents >= agent.budgetMonthlyCents) {
    // 预算耗尽，暂停Agent
    AgentDB.update(agentId, { status: 'paused' });
    return { allowed: false, reason: 'Budget exceeded' };
  }

  if (agent.spentMonthlyCents >= agent.budgetMonthlyCents * 0.9) {
    // 接近预算上限，发送警告
    console.warn(`Agent ${agentId} is at 90% of monthly budget`);
  }

  return { allowed: true };
}
```

## 与天龙引擎协同

| 天龙组件 | 成本协同 |
|---------|---------|
| **全部Agent** | 预算检查 |
| **08发布师** | 审批续费 |
| **07记录师** | 成本报告 |

## 成本模型

### Claude模型定价（2026）

| 模型 | Input | Output |
|------|-------|--------|
| claude-opus-4-6 | $15/1M | $75/1M |
| claude-sonnet-4-6 | $3/1M | $15/1M |
| claude-haiku-4-5 | $0.80/1M | $4/1M |

### 成本计算

```typescript
function calculateCost(
  model: string,
  inputTokens: number,
  outputTokens: number
): number {
  const pricing = {
    'claude-opus-4-6': { input: 15, output: 75 },
    'claude-sonnet-4-6': { input: 3, output: 15 },
    'claude-haiku-4-5': { input: 0.8, output: 4 }
  };

  const p = pricing[model] || pricing['claude-sonnet-4-6'];
  const inputCost = (inputTokens / 1000000) * p.input;
  const outputCost = (outputTokens / 1000000) * p.output;
  return Math.round((inputCost + outputCost) * 100); // 美分
}
```

## 实现文件

- `scripts/cost.ts` - 成本控制器实现
- `scripts/pricing.ts` - 定价模型

## 版本历史

| 版本 | 日期 | 更新 |
|------|------|------|
| **2.1.0** | 2026-08-24 | **Stage 45.1 协同（dsh-balance-meter · BSD-3-Clause）** · 4 RPC: balance/session-cost/pricing-demo/ledger-demo · peak/off-peak 自动判定（Beijing 09-12 / 14-18）· 14/14 自研 unittest PASS · 与 V2.0 trajectory cost 形成 cost + balance 闭环 |
| **2.0.0** | 2026-08-24 | **Stage 40 协同（dsh-trajectory-debug）** · 接 trajectory-debug RPC 拉真实 token / 加 Session 真实成本估算 / 月环比 / 报价生成 / DON'T 护栏 / 5 条验证矩阵 |
| 1.0.0 | 2026-03-15 | 初始版本（基于 paperclipai/paperclip 衍生） |

---

## 🔗 V2.0 · Stage 40 协同增量

> **触发源**：[devmom/dsh-trajectory-debug](https://github.com/devmom/dsh-trajectory-debug) v0.2.0 · MIT ✅ · 镜像在 `skills/dsh-trajectory-debug-integration/`
>
> **协同目标**：V1.0 已经有 budget / 节流 / 告警三个模块。V2.0 把"真实成本"这件事**接进 trajectory-debug RPC**，让预算基于真实数据而非经验值。

### V2.0 §1. session 真实成本估算（新模块）

```python
# scripts/cost-trajectory.py 新增
from cost_control import estimate_session_cost

result = estimate_session_cost(
    session_id="abc",
    dsh_url="http://127.0.0.1:3080",
    price_table={
        "deepseek": {"input": 0.14, "output": 0.28},
        "openai":   {"input": 2.50, "output": 10.00},
    },
)

# result:
# {
#   "session_id": "abc",
#   "provider": "deepseek",
#   "input_tokens": 41203,
#   "output_tokens": 18402,
#   "input_cost_usd": 0.00577,
#   "output_cost_usd": 0.00515,
#   "total_cost_usd": 0.01092,
#   "cost_per_token_usd": 1.83e-7,
# }
```

### V2.0 §2. 与 V1.0 三模块协同

| V1.0 模块 | V2.0 协同方式 |
|---|---|
| **月度预算** | 真实 cost 替代估算（trajectory RPC → token × price） |
| **实时追踪** | trajectory data 替代 mock data（不双源） |
| **自动节流** | 节流触发条件改为"**真实成本 > 预算**"而非"估算成本 > 预算" |
| **审批续费** | 续费审批时附"上次真实成本"作为依据 |

### V2.0 §3. 月环比（新增）

```python
from cost_control import monthly_cost_compare

result = monthly_cost_compare(
    days=30,
    dsh_url="http://127.0.0.1:3080",
    price_table=...
)

# 输出:
# {
#   "current_month_cost_usd": 12.34,
#   "previous_month_cost_usd": 18.56,
#   "delta_pct": -33.5,           # 节省
#   "by_provider": {"deepseek": 8.20, "openai": 4.14},
#   "by_session_top_5": [...],
# }
```

### V2.0 §4. 报价生成（新增，给客户报价时用）

```python
from cost_control import generate_quote

quote = generate_quote(
    session_id="abc",
    retail_markup_pct=30,         # 30% 加价
    currency="CNY",
)
# → 报价单 markdown，可直接渲染为客户发票
```

### V2.0 §5. DON'T 护栏（trajectory-debug 增量）

- ❌ **不要**把 trajectory 估算 cost 当真实账单（仅估算，最终账单以 LLM Provider 实际扣款为准）
- ❌ **不要**默认开启 `enableModelTools`（cost 估算纯本地算 + trajectory RPC，不需要额外 LLM）
- ❌ **不要**用 USD/CNY 单价直接给客户报（必须先 retail_markup_pct 加价；B2B 商单默认 30%）
- ❌ **不要**让 cost dashboard 阻塞 trajectory-debug 主流程（cost 是旁路观测，不动主流量）
- ❌ **不要**用 mock 数据写入真实价格表（必须环境变量 `PAPERCLIP_DRY_RUN=1` 隔离）

### V2.0 §6. 验证矩阵

| # | 必检项 | 期望 | 状态 |
|---|---|---|---|
| 1 | `estimate_session_cost()` 数字合理 | 与 trajectory-debug RPC ±5% 误差 | ⏳ |
| 2 | 价格表 fallback 无 provider 时 | 走默认 `deepseek` | ⏳ |
| 3 | 月环比准确 | current + previous 两月独立算 | ⏳ |
| 4 | 预算告警 ≤3s | webhook 调用 < 3s 返回 | ⏳ |
| 5 | 5 个 pytest 用例 | cost/math/mock/webhook/scheduler | ⏳ |

---

## V2.0 实现路径

新增脚本 `scripts/cost-trajectory.py`（V2.0 增量），保留 V1.0 原 4 文件不动：

| 文件 | V1.0 → V2.0 |
|---|---|
| `scripts/cost.ts` | ⚠️ 待改名 `cost.ts` → `cost-budget.ts`（避免与 cost-trajectory.py 名字冲突） |
| `scripts/pricing.ts` | ⚠️ 抽出 `pricing.ts` → `pricing-v2.yaml`（YAML 化方便非 TS 调用方用） |
| `scripts/cost-trajectory.py` ⭐NEW | V2.0 新增：trajectory RPC 调用 + 价格表 × token = USD |
| `scripts/monthly-compare.py` ⭐NEW | V2.0 新增：30 天环比 |
| `scripts/quote-generator.py` ⭐NEW | V2.0 新增：客户报价 markdown 渲染 |

---

## 参考链接

- **DSH trajectory-debug**：[devmom/dsh-trajectory-debug](https://github.com/devmom/dsh-trajectory-debug) v0.2.0 · MIT
- **DSH balance-meter**：[Ghost011118/dsh-balance-meter](https://github.com/Ghost011118/dsh-balance-meter) v0.1.0 · BSD-3-Clause
- **天龙 dsh-trajectory-bridge**：[`skills/dsh-trajectory-debug-integration/scripts/dsh_trajectory_bridge.py`](../dsh-trajectory-debug-integration/scripts/dsh_trajectory_bridge.py)
- **天龙 dsh-balance-bridge**：[`skills/dsh-balance-meter-integration/scripts/dsh_balance_bridge.py`](../dsh-balance-meter-integration/scripts/dsh_balance_bridge.py)
- **paperclipai/paperclip**（上游灵感）：https://github.com/paperclipai/paperclip · 70679a3
- **天龙主题文件**：[`memory/stage-44-trajectory-debug.md`](../../memory/stage-44-trajectory-debug.md) + [`memory/stage-451-dsh-balance-meter.md`](../../memory/stage-451-dsh-balance-meter.md)

---

## 🔗 V2.1 · Stage 45.1 协同增量（dsh-balance-meter BSD-3-Clause）

> **触发源**：[Ghost011118/dsh-balance-meter](https://github.com/Ghost011118/dsh-balance-meter) v0.1.0 · **BSD-3-Clause**（R1 评估 2026-08-24 · 12/12 vitest PASS）· 真源镜像 + lib-first 模式 · 落 `skills/dsh-balance-meter-integration/`
>
> **协同目标**：把 paperclip V2.0 的"session cost 估算"与 dsh-balance-meter 的"账户余额读取"打通，形成 **cost + balance 闭环治理**。

### V2.1 §1. 3 维成本治理闭环

```
        ┌─────────────────────────────────────────────┐
        │   paperclip V2.1 cost + balance + trace 闭环  │
        ├─────────────────────────────────────────────┤
        │ 1. session cost (V2.0 已有)                  │
        │    → cost_trajectory.py + tokenPriceTable    │
        │ 2. ⭐ balance (Stage 45.1 新增)             │
        │    → dsh_balance_bridge.py (4 RPC)           │
        │ 3. trace (Stage 44 trajectory-debug)        │
        │    → dsh_trajectory_bridge.py + perf()       │
        │                                               │
        │ → 完整闭环：消费 + 余额 + 性能 三维度      │
        └─────────────────────────────────────────────┘
```

### V2.1 §2. peak/off-peak 自动判定（北京时间）

| 北京时间 | Band |
|---|---|
| 09:00 - 12:00 | **peak** |
| 12:00 - 14:00 | off-peak |
| 14:00 - 18:00 | **peak** |
| 18:00 - 09:00 | off-peak |

**flash 输入价**：peak=0.04 CNY/M / off_peak=0.02 CNY/M（**2 倍差**）
**pro 输入价**：peak=0.40 / off_peak=0.20 CNY/M

### V2.1 §3. 新增 4 CLI（借 dsh_balance_bridge.py）

```bash
# 1. 读余额（3 source：official / proxy / manual）
python skills/dsh-balance-meter-integration/scripts/dsh_balance_bridge.py balance --source official

# 2. 单 session cost 估算（4 buckets + peak/off-peak）
python skills/dsh-balance-meter-integration/scripts/dsh_balance_bridge.py session-cost \
    --input 1000000 --output 500000 \
    --model deepseek-v4-flash --band off_peak

# 3. peak/off-peak 价格 demo
python skills/dsh-balance-meter-integration/scripts/dsh_balance_bridge.py pricing-demo --model deepseek-v4-pro

# 4. local ledger 快照（manual 模式持久化）
python skills/dsh-balance-meter-integration/scripts/dsh_balance_bridge.py ledger-demo --ledger-path ./balance.json
```

### V2.1 §4. 与 V2.0 既有模块协同

| V2.0 模块 | V2.1 协同 |
|---|---|
| `cost_trajectory.py` estimate_session_cost | **复用** `dsh_balance_bridge.estimate_session_cost` 4-bucket 公式（与上游 README §How the cost is estimated 一致）|
| `monthly_cost_compare` | **新增** `dsh_balance_bridge.balance` 配合出"月余额变化" |
| `paperclip.price_table` | **复用** `dsh_balance_bridge.DEFAULT_PRICING`（peak/off-peak 双价）|

### V2.1 §5. DON'T 护栏（BSD-3-Clause 增量 · 5 条）

- ❌ **不要**用 Ghost011118 名字做推广（**BSD-3 § 3 明示不得背书**）
- ❌ **不要**省 LICENSE 头段 `Copyright (c) 2026, Ghost011118` 和免责声明段
- ❌ **不要**把 cache_write 单独计费（DeepSeek 不单独收费 cache_write）
- ❌ **不要**把余额数字与 cost 数字混淆（一个是 **API provider 余额**，一个是 **session 已用 cost**）
- ❌ **不要**让余额为负时继续发请求（必须 fail-closed 阻断下游）

### V2.1 §6. 验证矩阵

| # | 必检项 | 期望 | 状态 |
|---|---|---|---|
| 1 | LICENSE verbatim 字节一致（1,548 B / 29 行）| 完全一致 | ✅ Stage 45.1 D4 |
| 2 | pnpm install/build/typecheck/test 4/4 exit 0 | 全过 | ✅ Stage 45.1 D3 |
| 3 | vitest 12/12 PASS（上游）| 12/12 | ✅ 721ms |
| 4 | dsh_balance_bridge.py 14/14 自研 unittest PASS | 14/14 | ✅ Stage 45.1 W1 |
| 5 | --band off_peak / peak 价格差 2 倍 | input cost 0.02 vs 0.04 CNY/M | ✅ |
| 6 | peak hour 自动判定 | is_peak_hour() 09:00 / 14:00 / 23:00 测试 | ✅ |