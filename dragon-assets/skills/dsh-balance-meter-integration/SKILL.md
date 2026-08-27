---
name: dsh-balance-meter-integration
description: |
  DSH 生态首个 **BSD-3-Clause** 集成。提供 DeepSeek 账户余额 + 单 session cost 估算。
  镜像真源（lib-first 模式 · 不需要 DSH 主仓 harness/ 软链）。
  与 stage 44 trajectory-debug (MIT) + stage 45 dsh-eval-bridge (MIT 借鉴档) 形成 3 类协议 × 3 类集成模式全谱。
metadata:
  version: "1.0.0"
  date: "2026-08-24"
  license: BSD-3-Clause
  author: 天龙引擎 · Stage 45.1
  upstream:
    - Ghost011118/dsh-balance-meter v0.1.0 (BSD-3-Clause)
  integration_stage: 45.1
  integration_mode: "真源镜像（lib-first）"
  license_template: bsd3-attribution-statements §一
  triggers:
    - "dsh-balance-meter"
    - "DSH 余额"
    - "/balance"
    - "session cost"
    - "余额读取"
    - "peak/off-peak"
---

# dsh-balance-meter-integration · V1.0

> **TL;DR**：天龙引擎 Stage 45.1 集成 [Ghost011118/dsh-balance-meter](https://github.com/Ghost011118/dsh-balance-meter) v0.1.0（**BSD-3-Clause ✅** · TypeScript · 275 KB · 0 ⭐ · 12/12 vitest PASS · lib-first 模式）。天龙首个 **BSD-3-Clause** 集成 + 首个 DSH 生态**真源镜像轻量档**（与 stage 45 dsh-eval-bridge 借鉴档互补）。

---

## L0: 一句话描述 (≤15字)

DSH 余额读取 + cost 估算。

---

## L1: 使用场景

当用户需要：
- 在 DSH Web UI 的 composer dock 显示账户余额 + 当前 session cost
- 配置 3 种余额来源：official API / proxy / manual local ledger
- 启用 per-model 智能定价（auto / flash / pro 切换）
- 自动应用 peak/off-peak 分时定价（北京时间 09:00-12:00 / 14:00-18:00）
- 与 paperclip-cost-control V2.0 + dsh-trajectory-debug 协同：**cost + balance + trace** 三源 cost 治理闭环

---

## L2: 能力矩阵（6 项 · 与上游 README §Features 对齐）

### 2.1 余额读取（3 种 source）

| Source | 端点 | 行为 |
|---|---|---|
| **`official`** (default) | DeepSeek official `/user/balance` | API key 注入 → 真余额 |
| **`proxy`** | 用户自定义 endpoint + Bearer | 兼容第三方 relay |
| **`manual`** | 用户在 DSH settings 写 `manualBalance` | 本地 ledger 维护 |

### 2.2 单 session cost 估算（4 buckets）

```
session_cost = input_uncached + cache_read + cache_write + output
             (USD)
```
- 4 buckets 与 paperclip-cost-control V2.0 兼容
- cache_write 默认 0（DeepSeek 不单独收费）

### 2.3 per-model pricing 自动切换

| Model ID | 映射 |
|---|---|
| `deepseek-v4-flash` | flash |
| `deepseek-v4-pro` | pro |
| (未知 / 无 header) | auto fallback → flash |

可通过 `model: 'auto'\|'flash'\|'pro'` 强制预设。

### 2.4 peak/off-peak 分时定价

| 北京时间 | Band |
|---|---|
| 09:00 - 12:00 | peak |
| 14:00 - 18:00 | peak |
| 其他 | off-peak |

`pricingRefreshHours: 6`（默认）自动拉取官方定价页。

### 2.5 Web UI composer dock chip 显示

```
Balance CNY 4.16 · This session CNY 2.57
```
点击展开 per-currency（granted + top-up）+ per-bucket（input/cache read/output）双 breakdown。

### 2.6 manual 模式本地 ledger

`balance` settings namespace 下存 baseline + remaining + spent + checkpoint · 不写独立 plaintext · 不进浏览器响应。

---

## L3: 安装

```bash
# 1. 装本 skill（天龙自有，已落 dragon-engine/skills/dsh-balance-meter-integration/）
# 2. 装 stage 44 trajectory-debug-bridge（前置，trace export）
# 3. 装 stage 45 dsh-eval-bridge（前置，benchmark cost 复用）
# 4. 装 stage 45 paperclip-cost-control V2.0+（cost 数学复用）

# 5. 配置 DeepSeek API key
export DEEPSEEK_API_KEY="sk-..."

# 6. 安装到 DSH web profile
dsh plugin --profile web add dsh-balance-meter-bundle
# 或者从天龙镜像
dsh plugin --profile web add dragon-engine/skills/dsh-balance-meter-integration

# 7. 重启 dsh web，refresh 页面，composer dock 显示余额 chip
```

---

## L4: 触发词

```
/balance · dsh-balance-meter · 余额 · session cost
peak/off-peak · proxy balance · manual balance
per-model pricing · flash / pro / auto
```

---

## L5: 下游协同（10 位置）

| 下游 | 协同 |
|---|---|
| **paperclip-cost-control V2.0 → V2.1** | session cost + balance 闭环治理 |
| **09-03 meta-reviewer v2.0 → v2.1** | `/balance` 加入 daily cron summary |
| **00-analyst V13.1** | 决策含余额约束 |
| **04-validator V9.06** | 余额 < 阈值 强制警告 |
| **dsh-trajectory-debug V0.2.0** | trace 维度 + balance 维度双 dashboard |
| **dsh-eval-bridge V1.0** | benchmark 含 balance 约束 |
| **39 chief-of-staff V2.1** | daily summary 含余额 |
| **30-01 marketing** | 余额告警驱动商业决策 |
| **stage 45 dsh-eval** | LLM judge 评估时含 balance 约束 |
| **session-distiller V1.1** | balance event 入 L0 raw |

---

## L6: DON'T 护栏（BSD-3-Clause 增量 · 5 条）

- ❌ **不要**用 Ghost011118 名字做推广或背书（**BSD-3 § 3 明示**）
- ❌ **不要**省 LICENSE 头段 `Copyright (c) 2026, Ghost011118` 和免责声明段
- ❌ **不要**默认开启 cron balance-poll（每 6h 即可 · 30s 是 hard floor）
- ❌ **不要**把余额数字与 cost 数字混淆（一个是 **API provider 余额**，一个是 **session 已用 cost**）
- ❌ **不要**让余额为负时继续发请求（必须 fail-closed 阻断下游）

---

## L7: 验证矩阵

| # | 必检项 | 期望 | 状态 |
|---|---|---|---|
| 1 | LICENSE verbatim 字节一致 | 1,548 B（CRLF）| ✅ Stage 45.1 D4 |
| 2 | pnpm install / build / typecheck / test 4/4 exit 0 | 全过 | ✅ Stage 45.1 D3 |
| 3 | vitest 12/12 PASS | 与上游声明一致 | ✅ 721ms |
| 4 | lib/ 4 个 .js 字节一致（client/index/invariant/service）| src=dst | ✅ Stage 45.1 D4 |
| 5 | package.json license 字段 = BSD-3-Clause | 显式 | ✅ |
| 6 | 6/6 BSD-3 红线检查 | 全过 | ✅ |

---

## L8: BSD-3-Clause 与 Stage 44 MIT 对照

| 维度 | trajectory-debug (Stage 44, MIT) | **dsh-balance-meter (Stage 45.1, BSD-3)** |
|---|---|---|
| LICENSE verbatim | 1,117 B / 21 行 | **1,519 B / 22+7 行** |
| 协议核心约束 | 4 条（拷贝/版权/免责/商标模糊）| **3 条强约束**（拷贝/版权/免责 + §3 **明示**不得背书）|
| NOTICE 段 | MIT **不要求** | BSD-3 **不要求** |
| 自研 vs 镜像 | 双镜像 | 单真源镜像（**lib-first**）|
| 累计 PASS | +63 | +3（本阶段轻量档）|

详见：[`bsd3-attribution-statements.md §二`](../../../memory/bsd3-attribution-statements.md)（BSD-3 vs MIT 关键差异）

---

## L9: 参考链接

- **上游仓库**：https://github.com/Ghost011118/dsh-balance-meter v0.1.0 · BSD-3-Clause
- **LICENSE verbatim**：https://raw.githubusercontent.com/Ghost011118/dsh-balance-meter/master/LICENSE（1,519 B）
- **BSD-3-Clause 全文**：https://opensource.org/licenses/BSD-3-Clause
- **BSD-3 合规模板**：[`memory/bsd3-attribution-statements.md`](../../../memory/bsd3-attribution-statements.md)（5 模板 + 4 约束 + 11 检查清单）
- **DSH 协议治理基线**：[`docs/dsh-ecosystem-license-policy.md`](../../../docs/dsh-ecosystem-license-policy.md)（含 BSD-3 接受）
- **Stage 45.0 dsh-eval 借鉴档**：[`skills/dsh-eval-bridge/SKILL.md`](../dsh-eval-bridge/SKILL.md)
- **Stage 45.1 主题文件**：[`memory/stage-451-dsh-balance-meter.md`](../../../memory/stage-451-dsh-balance-meter.md)
- **Stage 45.1 D2 撞墙报告**：本目录 scratch 路径
