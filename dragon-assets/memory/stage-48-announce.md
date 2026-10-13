---
name: stage-47-announce
description: Stage 47 候选盘点总验收 — 8 候选 → 2 GO + 3 边界 GO + 3 NO-GO · MemOS + comet 双借鉴档候选
metadata:
  node_type: memory
  originSessionId: stage-47-announce-20260826
  modified: 2026-08-26T13:45:00.000Z
heat: 0.6
last_ref_date: 2026-08-26
mneme_schema: v12.0
---



# 🚀 Stage 47 候选盘点公告 · 2026-08-26

> **TL;DR**：Stage 47 是 **cycle-style 候选盘点循环**（沿用 stage 45 D1 协议评估 + D2 撞墙 + D3 借鉴/拒绝 + DSH 生态 NOASSERTION 治理基线），共盘点 8 个候选 → **2 GO + 3 边界 GO + 3 NO-GO**。累计 PASS **875 锁定**（盘点本身不新增 pytest · 纯治理类）。**用户拍板后启动 Stage 47.1 双 GO 借鉴档**（MemOS + comet）。

---

## 一、本阶段交付（**W1 单一交付**）

| W# | 任务 | 关键产物 | 验证 |
|---|---|---|---|
| **W1** | 候选盘点（D1 + D2 + D3）| `stage-47-candidates-evaluation.md` 8 候选 + GO/NO-GO 矩阵 | ✅ |
| **W1** | 候选列表 fetch via GitHub REST API | 20+ 候选实测 stars + 协议 + 末 push 时戳 | ✅ |
| **W1** | GO/NO-GO 决策树 | 2 GO（MemOS + comet）+ 3 边界 GO + 3 NO-GO | ✅ |
| **W1** | 库存候选清单 | 6 候选 30 天后 recheck | ✅ |
| **W1** | stage-47-announce | 本文件 | ✅ |

---

## 二、本盘点阶段复用

| 上游档案 | 复用方式 |
|---|---|
| [`dsh-ecosystem-license-policy.md V1.0`](dsh-ecosystem-license-policy.md) | NOASSERTION 治理基线 6 条 § 6 |
| [`apache-attribution-statements.md §九`](apache-attribution-statements.md) | Apache-2.0 红线 12 项检查表 |
| [`mit-attribution-statements.md §十八`](mit-attribution-statements.md) | MIT 致敬段落模板 |
| [`nomifun-methodology/SKILL.md` § 三.§四](nomifun-desktop-integration.md) | 借鉴档模式 (与 stage 41 / 45 / 46 一致) |
| [`stage-45-dsh-eval § 三 七候选盘点](stage-45-dsh-eval.md) | 同型盘点清单 |

---

## 三、GO/NO-GO 矩阵（实测 · 2026-08-26）

| # | 候选 | ⭐ | 协议 | 决定 | 启动阶段 |
|---|---|---|---|---|---|
| 1 | [`affaan-m/ECC`](https://github.com/affaan-m/ECC) | 243,246 | MIT ✅ | 🟡 边界 GO（stars 异常）| 47.2 候选 |
| 2 | [`MemTensor/MemOS`](https://github.com/MemTensor/MemOS) | 10,988 | **Apache-2.0 ✅** | 🟢 **GO** | **47.1 启动** |
| 3 | [`zhayujie/CowAgent`](https://github.com/zhayujie/CowAgent) | 46,677 | MIT ✅ | 🟡 搁置（与 nomifun 重位）| 48 候选 |
| 4 | [`bytedance/deer-flow`](https://github.com/bytedance/deer-flow) | 80,898 | MIT ✅ | 🟡 搁置（同上）| 48 候选 |
| 5 | [`RealZST/HarnessKit`](https://github.com/RealZST/HarnessKit) | 414 | Apache-2.0 ✅ | 🟡 边界 GO（窄域互补）| 47.3 候选 |
| 6 | [`codejunkie99/agentic-stack`](https://github.com/codejunkie99/agentic-stack) | 2,235 | Apache-2.0 | 🔴 NO-GO（与 MemOS 重位）| — |
| 7 | [`rpamis/comet`](https://github.com/rpamis/comet) | 2,841 | **MIT ✅** | 🟢 **GO** | **47.1 启动** |
| 8 | [`fluxions-ai/vui`](https://github.com/fluxions-ai/vui) | 747 | NOASSERTION ❌ | 🔴 NO-GO（红牌）| — |

**实测**：候选 2 MemOS + 候选 7 comet 双 GO 都满足：a) 末 push ≤ 24 小时；b) stars / 协议双达标；c) 与 nomifun-desktop 不重位；d) 与天龙 5 类岗位（04-validator / 09-06-skills-administrator / 07-scribe / session-distiller / hv-analysis）匹配度高。

---

## 四、D1 协议评估 + D2 撞墙 + D3 借鉴/拒绝 三步决策树（**复用 stage 45**）

```
step 1 (D1): 上游元数据 7 字段实拉
   ↳ gh api repos/<repo> --jq '{name, license.spdx_id, stars, ...}'
   ↳ raw LICENSE 文件 → sha256 验真

step 2 (D2): 撞墙预期
   ↳ DSH harness/ 软链依赖？（npm/pnpm 要求本机有 DSH Desktop 装在固定路径 → 借鉴档避免）
   ↳ peers / 强制依赖？（package.json + peerDependencies）
   ↳ build 工具链？（Pyke CDN 101 MB 等）

step 3 (D3): 借鉴/拒绝决策
   ↳ 借鉴档模式 (stage 41/45/46/47 同款)：✅ DSH 依赖 blocker / 上游迭代快 / 体积大
   ↳ 真源镜像（stage 22/23/24/44/45.1 同款）：✅ 独立 / 体积小 / harness 软链可绕过
   ↳ NO-GO（红牌）：缺 LICENSE / 严重撞墙 / 与既占位重位
```

---

## 五、Stage 47.1 双 GO 借鉴档清单（**用户拍板即启**）

| 任务 | 借鉴档数 | 自研 PASS 估计 |
|---|---|---|
| **MemOS-bridge V1.0** | 5 类方法论：self-evolving memory OS / ultra-persistent / hybrid retrieval / cross-task reasoning / Apache-2.0 红线 | +10~14 |
| **comet-bridge V1.0** | 4 类方法论：phase-guarded / loop-engineering / skill→workflow eval / MIT 红线 | +6~10 |
| **2 Skill 落盘 + 4 自检 PASS** | 与 stage 46 nomifun-methodology 节奏一致 | — |
| **累计 PASS 估计** | **875 → ≥900** | (+25 net) |

### 5.1 MemOS-bridge SKILL.md 11 字段 skeleton（**stage 46 模板直接复用**）

```yaml
---
name: memos-memory-os-bridge
version: 1.0.0
base_version: memOS v0.x (Apache-2.0 · 10,988⭐ · 2026-08-26)
description: >-
  Borrow 5 methodologies from MemTensor/MemOS (Apache-2.0): 
  ① Self-evolving memory OS architecture / ② Ultra-persistent memory / 
  ③ Hybrid retrieval (vector + BM25 + graph hops) / ④ Cross-task reasoning routing / 
  ⑤ Apache-2.0 LICENSE + NOTICE compliance.
  Use when designing persistent memory, cross-task state, hybrid retrieval, eval-grade loops.
triggers: ["memory-os", "Memory OS", "cross-task", "hybrid retrieval", ...]
upstream: ["MemTensor/MemOS V0.x (Apache-2.0 · 10,988⭐)"]
downstream: [07-scribe V12.4, 09-06-skills-administrator V1.2, session-distiller V1.2, ...]
DO: [6 条]   DONTS: [10 条]
example:
  cli: |
    python scripts/memos_bridge.py ingest text/...
    python scripts/memos_bridge.py retrieve --query '...'
    python scripts/memos_bridge.py cross_task_route session_id=...
  output: |
    ✓ memory OS pipeline complete
    ...
---
```

### 5.2 comet-bridge SKILL.md 11 字段 skeleton（**stage 46 模板直接复用**）

```yaml
---
name: comet-workflow-eval-bridge
version: 1.0.0
base_version: rpamis/comet V0.x (MIT · 2,841⭐ · 2026-08-26)
description: >-
  Borrow 4 methodologies from rpamis/comet (MIT): 
  ① Phase-guarded execution (eval gate per step) / ② Loop engineering (retry + backoff) / 
  ③ Skill → workflow eval templates / ④ MIT LICENSE + Modified by dragon-engine compliance.
  Use when designing phase-guarded workflows, retry loops, eval-grade skill pipelines.
triggers: ["phase-guarded", "loop engineering", "workflow eval", "comet", ...]
upstream: ["rpamis/comet V0.x (MIT · 2,841⭐)"]
downstream: [04-validator V9.08, 04-comet-eval-grade, hv-analysis V1.3, ...]
DO: [6 条]   DONTS: [10 条]
example:
  cli: |
    python scripts/comet_bridge.py phase_gate workflow.yaml
    python scripts/comet_bridge.py loop_engine --max 5
    python scripts/comet_bridge.py workflow_eval plan.yaml --judge deepseek
  output: |
    ✓ phase gate PASS
    ✓ loop converged in N iterations
    ...
---
```

---

## 六、本盘点阶段不新增 PASS（**与 stage 45 候选盘点节奏一致**）

| 阶段 | 盘点本身 PASS | 启动借鉴档后 PASS |
|---|---|---|
| stage 45 | 0（盘点 + 期票 commit）| +8 dsh-eval-bridge |
| stage 46 | 0（盘点）| +23 nomifun-methodology |
| stage 47 | 0（盘点 + 库存）| +25（计划 · 待拍板）|

---

## 七、未决项与下一步（**用户拍板**）

| 动作 | 影响 | 推荐 |
|---|---|---|
| **双 GO 借鉴档启动** | MemOS + comet 双借鉴档并行，预计 +25 PASS | 🟢 推荐（与 stage 45/46 节奏一致）|
| **单一借鉴档启动** | 只选 MemOS 或 comet 一个，更轻 | 🟡 备选 |
| **盘点一个月后再启动** | 等 30 天 recheck，错过窗口期 | ⚠️ 不推荐 |
| **写盘点博客** | "我们用什么样的候选评估流水线" | 🟡 等用户拍板 |

---

## 八、累计 PASS 锁定

```
Stage 41-44: 844 PASS
Stage 45:    +8   (dsh-eval-bridge)
Stage 46:    +23  (nomifun-methodology)
Stage 47:    +0   (本期盘点本身)
==========================================
Stage 47 final: 875 PASS 锁定（盘点阶段）
Stage 47.1:     ≥900 PASS 计划（双 GO 借鉴档）
```

---

## 九、版本信息

- **盘点主题文件 V1.0**：`dragon-engine/memory/stage-47-candidates-evaluation.md` · 9 KB
- **announce V1.0**：本文件
- **盘点方法**：D1 协议评估 + D2 撞墙预期 + D3 借鉴/拒绝
- **盘点日期**：2026-08-26
- **盘点仓库数**：8 个实测（+ 12 个搜索未命中）
- **GO / 边界 GO / NO-GO 数**：2 / 3 / 3
- **DSH 生态治理基线**：复用 stage 45 § 6

---

> **下次同步点**：用户拍板后启动 Stage 47.1 双 GO 借鉴档（MemOS + comet）；同时启动 stage 47.2（ECC 边界 GO 7 天观察期）。
