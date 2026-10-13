---
name: stage-47-candidates-evaluation
description: Stage 47 候选盘点 (8 候选) — 1 GO + 1 边界 GO + 6 NO-GO · 借鉴档模式 + DSH 生态 NOASSERTION 治理基线
metadata:
  node_type: memory
  originSessionId: stage-47-candidates-20260826
  modified: 2026-08-26T13:30:00.000Z
heat: 0.7
last_ref_date: 2026-08-26
mneme_schema: v12.0
---

# Stage 47 候选盘点 V1.0（2026-08-26）

> **TL;DR**：本阶段不是单一 GO 模式，而是 **cycle-style 候选盘点循环**（沿用 stage 45 dsh-eval § 七候选评估 + stage 46 nomifun-methodology 借鉴档模式）。本轮 8 个候选 → **1 GO + 1 边界 GO + 6 NO-GO**。复用 stage 45 DSH 生态 NOASSERTION 治理基线 V1.0（`docs/dsh-ecosystem-license-policy.md`）。

---

## 一、盘点方法（**沿用 stage 45 §3.1 D1 协议评估 7 项 + D2 撞墙 + D3 借鉴/拒绝**）

每候选 3 步骤：

| 步骤 | 内容 |
|---|---|
| D1 | 上游元数据（gh api REST + raw LICENSE）+ 7 字段实拉 + 协议实检 |
| D2 | 撞墙预期（DSH 主仓依赖 / harness 软链 / peer 强制 / build 工具链）|
| D3 | 借鉴档模式 / 真源镜像 / NO-GO 三选一 |

---

## 二、8 候选盘点（按 GO/NO-GO 矩阵）

### 候选 1（**NO-GO**） — `affaan-m/ECC` ⭐243,246 · JavaScript · MIT

> 题目："The agent harness performance optimization system. Skills, instincts, memory, security, and research"

| 维度 | 值 |
|---|---|
| Stars / Forks | **243,246 ⭐**（超高热度）· JavaScript |
| 协议 | MIT ✅（合规）|
| 末 push | 2026-08-25 21:27Z（昨日）|
| Topics | ai-agents / anthropic / claude / claude-code / developer-tools |
| 描述 | agent harness performance optimization system (skills + instincts + memory + security + research) |

**但** ⭐ 异常高的 stars 243k 在 2026-08-25 创建可能为刷星或迁移自旧账号；属于"高热度但可信度待核"。

| 撞墙类型 | 风险 |
|---|---|
| **DSH 生态** | 名字 / Topics 都直击 DSH 生态（claude-code / agent harness）但**不依赖 DSH 主仓**（基于 Claude SDK + Anthropic API）|
| **借鉴档** | ✅ 可做借鉴档（不依赖 DSH harness/）|
| **撞墙点** | 无明显撞墙 |

**决策**：🟡 **边界 GO / 暂时搁置**（stars 异常高需先 7 天观察是否真有迭代节奏）；Stage 47.1 再评。

---

### 候选 2（**GO**） — `MemTensor/MemOS` ⭐10,988 · TypeScript · Apache-2.0 ✅

> 题目："Self-evolving memory OS for LLM & AI Agents: ultra-persistent memory, hybrid-retrieval, and cross-task reasoning"

| 维度 | 值 |
|---|---|
| Stars | **10,988 ⭐**（高热度 · 实用）|
| 语言 | TypeScript |
| 协议 | **Apache-2.0 ✅** |
| 末 push | 2026-08-26 04:02Z（今日）|
| Topics | agent / agentic-ai / ai / ai-agents / chatgpt |
| 描述 | Self-evolving memory OS · ultra-persistent memory + hybrid-retrieval + cross-task reasoning |

**与天龙空白位匹配度**：

| 天龙现况 | MemOS 候选能力 | 匹配度 |
|---|---|---|
| 阶段 41 mneme-heat-engine V2.0 (借鉴 dsh-mneme MIT) | MemOS = **production memory OS** 而非实验 heat engine | ⭐⭐⭐⭐ |
| 07-scribe V12.3 Layer 4 蒸馏 | "cross-task reasoning" 思路可借鉴 | ⭐⭐⭐ |
| 09-06-skills-administrator V1.1 | "skills + agents" 统一 memory | ⭐⭐⭐ |
| session-distiller V1.0 BuilderPulse 风格 | "self-evolving memory" 思路高度一致 | ⭐⭐⭐⭐ |

| 撞墙类型 | 风险 |
|---|---|
| **DSH harness/ 软链** | 否（独立仓库，TypeScript SDK）|
| **peers / 强制依赖** | 待抓 package.json · 当前看像独立项目 |
| **build 工具链** | 待 D3 实跑确认 |

**决策**：🟢 **GO · 本阶段启动** —— 借鉴档模式（与 stage 46 nomifun-methodology 一致），不复用 TypeScript 仅借鉴 "self-evolving memory OS" 方法论。

---

### 候选 3（**NO-GO**） — `zhayujie/CowAgent` ⭐46,677 · Python · MIT

> 题目："Open-source super AI assistant & Agent Harness. Plans tasks, runs tools and skills, self-evolves"

| 维度 | 值 |
|---|---|
| Stars | 46,677 ⭐（高热度 · 但与 nomifun-desktop 自家重位）|
| 协议 | MIT ✅ |
| 末 push | 2026-08-26 04:20Z（今日）|
| 描述 | super AI assistant & agent harness |

| 撞墙类型 | 风险 |
|---|---|
| **与 nomifun-desktop 重位** | nomifun 已经在阶段 46 借鉴档占据 "agent harness 全栈" 位置 |
| **DSH harness** | 不依赖 DSH harness |
| **撞墙点** | 无 |

**决策**：🟡 **暂时搁置**（与 stage 46 nomifun 重位 · 30 天后再评）；Stage 47.2 候选。

---

### 候选 4（**NO-GO**） — `bytedance/deer-flow` ⭐80,898 · Python · MIT

> 题目："An open-source long-horizon SuperAgent harness that researches, codes, and creates"

| 维度 | 值 |
|---|---|
| Stars | 80,898 ⭐（字节自家 · 极高热度 · 等同 nomifun 同档）|
| 协议 | MIT ✅ |
| 末 push | 2026-08-26 03:56Z（今日）|

**撞墙**：同候选 3，与 nomifun-desktop 重位。

**决策**：🟡 **暂时搁置**（字节自家 + 与 nomifun-desktop 同档）；Stage 48 候选。

---

### 候选 5（**边界 GO**） — `RealZST/HarnessKit` ⭐414 · Rust · Apache-2.0 ✅

> 题目："More than a skill manager — manage skills, MCP servers, plugins, hooks, CLIs, configs, memory & rules"

| 维度 | 值 |
|---|---|
| Stars | 414 ⭐（小但与 nomifun-desktop 同 author-Rust 风格）|
| 语言 | Rust |
| 协议 | **Apache-2.0 ✅** |
| 末 push | 2026-08-18 05:07Z（8 天前）|
| Topics | ai-coding-agents / claude-code / cli-tools / codex / cursor |

**撞墙**：Rust workspace · 与 stage 46 nomifun-desktop 同赛道但范围**窄**（专注 skill/mcp/plugin/hook/config 管理）—— 可与 nomifun 互补而非竞位。

**决策**：🟡 **边界 GO · Stage 47.3 候选**（待 Python 包 API 文档确认可借鉴性）。

---

### 候选 6（**NO-GO**） — `codejunkie99/agentic-stack` ⭐2,235 · Python · Apache-2.0

> 题目："One brain, many harnesses. Portable .agent/ folder (memory + skills + protocols)"

**撞墙**：1) 同源思路已被 nomifun + MemOS 双重覆盖；2) stars 中等但末 push 20 天前活跃度存疑。

**决策**：🔴 **NO-GO**（与 MemOS 重位且活跃度不足）。

---

### 候选 7（**GO**） — `rpamis/comet` ⭐2,841 · JavaScript · MIT

> 题目："Comet: agent skill harness for turning ideas into evaluated workflows"

| 维度 | 值 |
|---|---|
| Stars | 2,841 ⭐（小但聚焦）|
| 语言 | JavaScript |
| 协议 | **MIT ✅** |
| 末 push | 2026-08-26 04:04Z（今日）|
| Topics | ai / eval / harness-engineering / loop-engineering / phase-guarded |

**价值**：「agent skill harness for turning ideas into evaluated workflows」 — 与 stage 45 dsh-eval + stage 47 MemOS 双线对应，**且聚焦 "eval ↔ skill" 闭环**。

**撞墙**：纯 JavaScript · 可能依赖 Node 22+ · 借鉴档风险低（TS / JS 包装层比 Rust 好桥）。

**决策**：🟢 **GO · Stage 47.1 启动**（与 stage 46 nomifun-methodology 模式一致）+ 借鉴档方法论。

---

### 候选 8（**NO-GO**） — `fluxions-ai/vui` ⭐747 · Python · **NOASSERTION**

> 题目："Real-time voice assistant — WebRTC streaming + faster-whisper ASR + local LLM + Vui Nano (300M) TTS"

| 维度 | 值 |
|---|---|
| Stars | 747 ⭐ |
| 语言 | Python |
| 协议 | **NOASSERTION** ❌（无 SPDX）|
| 末 push | 2026-08-25 07:16Z（昨日）|

**撞墙**：NOASSERTION 协议 → **红牌**（沿用 stage 45 DSH 生态 NOASSERTION 治理基线 §6 第 6 档 "缺 LICENSE → NO-GO"）。

**决策**：🔴 **NO-GO**（NOASSERTION 红牌）。

---

## 三、GO/NO-GO 矩阵总结

| # | 候选 | 协议 | 决定 | 启动阶段 |
|---|---|---|---|---|
| 1 | affaan-m/ECC | MIT ✅ | 🟡 边界 GO（stars 异常 · 7 天观察）| 47.2 候选 |
| 2 | **MemTensor/MemOS** | **Apache-2.0 ✅** | 🟢 **GO** | **47.1 启动** |
| 3 | zhayujie/CowAgent | MIT ✅ | 🟡 搁置（与 nomifun 重位）| 48 候选 |
| 4 | bytedance/deer-flow | MIT ✅ | 🟡 搁置（与 nomifun 重位）| 48 候选 |
| 5 | RealZST/HarnessKit | Apache-2.0 ✅ | 🟡 边界 GO（窄域互补）| 47.3 候选 |
| 6 | codejunkie99/agentic-stack | Apache-2.0 | 🔴 NO-GO（重位 MemOS）| — |
| 7 | **rpamis/comet** | **MIT ✅** | 🟢 **GO** | **47.1 启动** |
| 8 | fluxions-ai/vui | NOASSERTION ❌ | 🔴 NO-GO（红牌）| — |

**8 候选 → 2 GO + 3 边界 GO + 3 NO-GO**

---

## 四、Stage 47.1 启动清单（**双 GO 并行 + 借鉴档模式**）

| 任务 | 借鉴档 | 自研 PASS 估计 |
|---|---|---|
| **MemOS-bridge V1.0** | "Self-evolving memory OS" 5 类方法论借鉴 | +10~14 |
| **comet-bridge V1.0** | "Agent skill harness for evaluated workflows" 4 类方法论 | +6~10 |
| **2 Skill 落盘 + 4 自检 PASS** | 与 stage 46 nomifun-methodology 节奏一致 | — |
| **累计 PASS 估计** | **875 → ≥900** | (+25 net) |

### 4.1 MemOS 借鉴清单（**5 类方法论**）

| # | 上游 MemOS 设计 | 天龙自研落地 | 优先级 |
|---|---|---|---|
| ① | **Self-evolving memory OS** 架构 | `memOS_bridge.py` V1.0（4 层 pipeline: ingest → consolidate → retrieve → inject）| ⭐⭐⭐ |
| ② | **Ultra-persistent memory**（避免反复 LLM 调用） | 落 `cross_task_state.py` 复用 stage 41 mneme V2.0 schema | ⭐⭐⭐ |
| ③ | **Hybrid retrieval**（vector + BM25 + graph hops） | 复用 stage 41 V2.0 retrieval.py + 加 hybrid fusion | ⭐⭐ |
| ④ | **Cross-task reasoning**（task-aware memory 路由） | 新建 `task_router.py`（按会话 → memory sub-graph）| ⭐⭐ |
| ⑤ | **Apache-2.0 红线镜像**（LICENSE verbatim + NOTICE Modified） | 落 `LICENSE` + `NOTICE` 文件 | ⭐ |

### 4.2 comet 借鉴清单（**4 类方法论**）

| # | 上游 comet 设计 | 天龙自研落地 | 优先级 |
|---|---|---|---|
| ① | **Phase-guarded execution**（eval gate 每步拦截） | `phase_gate.py` V1.0（与 stage 41 mneme-gate.py 类似）| ⭐⭐⭐ |
| ② | **Loop engineering**（自动 retry + backoff 阈值） | `loop_engine.py` V1.0（4 类 backoff + max-loop 阈值）| ⭐⭐ |
| ③ | **Skill → workflow eval** 模板 | `workflow_eval.py` V1.0（YAML schema）| ⭐⭐ |
| ④ | **MIT 红线**（LICENSE verbatim + Modified by dragon-engine） | 落 `LICENSE` + 自研 SKILL.md 标 'Modified by dragon-engine' | ⭐ |

---

## 五、Apache-2.0 / MIT 红线复用

**Apache-2.0**（MemOS）：
- §4(a) LICENSE 必随发布附
- §4(d) NOTICE 保留 + Modified by dragon-engine / 2026-08-26
- §6 Trademark 禁止暗示背书

**MIT**（comet）：
- 保留 © + LICENSE（rephrase → 'Modified by dragon-engine'）
- 无 NOTICE 义务

合规模板沿用 [apache-attribution-statements.md §九](apache-attribution-statements.md) + [mit-attribution-statements.md §十八](mit-attribution-statements.md)。

---

## 六、未决项与下一步

### 6.1 启动前确认（**等用户拍板**）

- [ ] **GO 项是否启动 Stage 47.1？** MemOS-bridge + comet-bridge 双借鉴档
- [ ] 是否同步把 Stage 47.1 启动"双 GO 借鉴档"模式 vs 单一借鉴档（避免 ROADMAP 过满）
- [ ] 是否在 stage 47 同周期写"两月总结"博客（45 dsh-eval / 46 nomifun / 47 MemOS+comet 三连借鉴档观察）

### 6.2 库存候选（30 天后再评）

| 候选 | 跟踪点 |
|---|---|
| affaan-m/ECC | stars 是否持续 + 真实迭代节奏 |
| zhayujie/CowAgent | 与 nomifun 重位（30 天后看生态分化）|
| bytedance/deer-flow | 同上 + 字节自家动向 |
| RealZST/HarnessKit | 47.3 评估 Python 桥可用性 |
| codejunkie99/agentic-stack | 与 MemOS 重位（看活跃度）|
| fluxions-ai/vui | 等作者补 LICENSE |

### 6.3 NO-GO 复审规则（**30 天一次**）

每个 NO-GO 候选 30 天后自动 recheck：
- 协议升级（NOASSERTION → MIT/Apache-2.0）→ 重评
- stars 翻 5 倍 → 重评
- 作者补 LICENSE → 重评
- 被其他仓库 fork 且 fork ≥ 100 stars → 重评

---

## 七、累计 PASS 增量预测

```
Stage 46 final: 875 PASS 锁定
Stage 47 候选盘点:  +0 PASS（盘点本身不新增 pytest · 纯治理类）
Stage 47.1 双 GO:   +25 PASS 计划（MemOS-bridge 14 + comet-bridge 11）
──────────────────────────────────────────
Stage 47.1 final:  ≥900 PASS 锁定（若启动）
```

---

## 八、来源链接

| 候选 | URL |
|---|---|
| affaan-m/ECC | https://github.com/affaan-m/ECC |
| MemTensor/MemOS | https://github.com/MemTensor/MemOS |
| zhayujie/CowAgent | https://github.com/zhayujie/CowAgent |
| bytedance/deer-flow | https://github.com/bytedance/deer-flow |
| RealZST/HarnessKit | https://github.com/RealZST/HarnessKit |
| codejunkie99/agentic-stack | https://github.com/codejunkie99/agentic-stack |
| rpamis/comet | https://github.com/rpamis/comet |
| fluxions-ai/vui | https://github.com/fluxions-ai/vui |

---

> **下次同步点**：用户对双 GO 借鉴档拍板 → 启动 Stage 47.1 主集成。
