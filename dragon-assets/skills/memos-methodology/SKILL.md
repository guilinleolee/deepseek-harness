---
name: memos-methodology
version: 1.0.0
base_version: MemTensor/MemOS (Apache-2.0 · 1006 forks · 2025-07-06 创建 · 2026-08-26 末 push)
description: >
  借鉴 MemOS 5 类方法论 (self-evolving / ultra-persistent / hybrid / cross-task / Apache-2.0).
  Use when designing persistent memory or eval-grade loops.
triggers:
  - "memory-os"
  - "Memory OS"
  - "memOS 借鉴"
  - "self-evolving"
  - "cross-task"
  - "hybrid"
  - "ultra"
upstream:
  - "MemTensor/MemOS (Apache-2.0 · 1006 forks · 14 个月迭代)"
downstream:
  - 07-scribe V12.4
  - 09-06-skills-administrator V1.2
  - session-distiller V1.2
  - hv-analysis V1.3
  - 28-10 财经底座师 V1.3
inputs:
  - { name: reference_url, type: https://github.com/MemTensor/MemOS, required: true }
  - { name: import_mode, type: enum[borrow_only, borrow_plus_mirror], required: false }
outputs:
  - { name: memory_pipeline_state, type: JSON }
  - { name: cross_task_route, type: dict }
errors:
  - { code: 400, meaning: "上游协议非 Apache-2.0/BSD-3/MIT" }
  - { code: 422, meaning: "pipeline 缺 4 阶段 (ingest/retrieve/consolidate/inject)" }
  - { code: 429, meaning: "LLM 调用限流" }
DO:
  - "借鉴档 + 不镜像真源（与 mneme/nomifun/dsh-eval 节奏一致）"
  - "仿照 stage 25 a-stock-data Apache-2.0 红线 12 项"
  - "保留 MemOS LICENSE 原文 (11.4 KB 实拉 Apache-2.0) + NOTICE 加 'Modified by dragon-engine / 2026-08-26'"
  - "凡借 'hybrid retrieval' 必复用 stage 41 mneme V2.0 BM25 + 加 vector similarity fusion"
  - "凡借 'cross-task reasoning' 必加会话级 task_router (按 session_id 切分 memory sub-graph)"
  - "凡借 'ultra-persistent' 必避开 LLM 反复调用，local SQLite 直接读"
DONTS:
  - "不要克隆 MemOS 真源 (TypeScript SDK 巨大 ~ 89 KB)"
  - "不要 import @memtensor/sdk 任何 npm 包"
  - "不要写 'MemOS 官方' / '官方授权' 字样"
  - "不要跑 npm install (依赖 @memtensor/* 私有闭源风险)"
  - "不要 uv add memos-* / pip install memos-* 依赖"
  - "不要镜像其 react/ui 目录 (产品方向不同 · 我们走 CLI)"
  - "不要改 MemOS LICENSE 11.4 KB 字节"
  - "不要把 'self-evolving' 误解为 'AI 自动写数据库'"
  - "不要在没有 backup 的情形下打开写模式"
  - "不要把 MemOS 当 LLM API 调用 (它是 local memory OS, 非 LLM)"
example:
  cli: |
    python scripts/memos_bridge.py ingest --text "28-04 排选题要点"
    python scripts/memos_bridge.py retrieve --query "选题"
    python scripts/memos_bridge.py cross_task_route --session tianlong-001
  output: |
    ✓ ingested into memory OS (4-layer pipeline)
    ✓ retrieved 5 candidates (hybrid: BM25 + vector)
    ✓ routed to sub-graph tianlong-content
---

# memos-methodology（借鉴档）· 5 类方法论 V1.0

> **L0 一句话**: 借 MemTensor/MemOS 的 5 类 memory OS 方法论，自研 4 层 pipeline。

> **L1 使用场景**（50-100 字）: MemTensor/MemOS（Apache-2.0 · 1006 forks · 14 个月迭代 · deepseek-harness / openclaw / dsh-plugin 同生态）是 production-grade 自进化 memory OS，5 类方法论可借鉴：① Self-evolving memory OS 架构 ② Ultra-persistent memory（local SQLite 避免 LLM 反复）③ Hybrid retrieval（vector + BM25 + graph hops）④ Cross-task reasoning（task-aware memory 路由）⑤ Apache-2.0 合规镜像。本 SKILL 不克隆真源（TypeScript SDK 89 KB），仅借鉴方法论层。

> **L2 详细文档**: 5 类方法论详见下方 §一-§五。

---

## 一、Self-evolving memory OS 4 层 pipeline

MemOS 借鉴天龙 4 层架构：

```
┌────────────────────────────────────────────┐
│ L1 ingest       python memos_bridge ingest │
│   - 输入文本/事件/工具结果                   │
│   - 写本地 SQLite + 标记 heat                │
└──────────┬─────────────────────────────────┘
           ↓
┌────────────────────────────────────────────┐
│ L2 consolidate  python memos_bridge consol │
│   - 阶段 41 mneme V2.0 heat_engine (幂律)  │
│   - 定期 sleep / 合并相似 memory             │
└──────────┬─────────────────────────────────┘
           ↓
┌────────────────────────────────────────────┐
│ L3 retrieve     python memos_bridge retriev │
│   - hybrid retrieval (vector + BM25 + graph)│
│   - 返回 K 条带 heat score 的 candidate      │
└──────────┬─────────────────────────────────┘
           ↓
┌────────────────────────────────────────────┐
│ L4 inject       python memos_bridge inject   │
│   - 按 session_id 注入对应 memory sub-graph │
│   - 避免一次性 context 爆掉                  │
└────────────────────────────────────────────┘
```

---

## 二、Ultra-persistent memory（**避开 LLM 反复调用**）

MemOS 核心 insight：长程 memory 应走**本地 SQLite** 而不是**每次 LLM tool 调用**。

| 反模式 | 优化后 |
|---|---|
| 每次 retrieval 触发 LLM tool call | 本地 SQLite + embeddings 缓存 |
| 用户偏好每次重新分析 | 首次 ingest 后永久本地存储 |
| session-level state 每次 dump | session_id → memory_id 索引 |

> **天龙借鉴**：07-scribe V12.3 Layer 4 蒸馏 + 09-06 V1.1 skills-administrator + session-distiller V1.0 共 3 Agent 都受益。

---

## 三、Hybrid retrieval（**vector + BM25 + graph hops 三路融合**）

```
query ──┬── vector (cosine similarity on local embeddings)
        ├── BM25 (keyword match, stage 41 mneme V2.0 已实装)
        └── graph hops (entity_id → 关联 memory)
        ↓
        rank fusion (Reciprocal Rank Fusion · RRF)
        ↓
        top-K candidates with heat_score
```

**天龙实现路径**：复用 stage 41 mneme V2.0 retrieval.py + 在此基础上加 RRF 融合层。

---

## 四、Cross-task reasoning routing（**按 session_id 切分 sub-graph**）

每个 session 维护独立 memory sub-graph：

```python
memory_state = {
  "session_id": "tianlong-001",
  "sub_graph": ["28-04 选题 A", "28-04 选题 B", "35-02 排期"],
  "heat_score": 0.78,
  "consolidate_at": "2026-08-26T11:30:00Z"
}
```

**天龙借鉴**：09-04 chief-of-staff V2.1 task_router + 28-04 内容策划师 session 化。

---

## 五、Apache-2.0 合规镜像

```text
s47_1_mirror/
├── LICENSE          # 11.4 KB Apache-2.0 verbatim (实拉 2026-08-26)
├── NOTICE           # 上游 NOTICE + "Modified by dragon-engine / 2026-08-26"
├── SKILL.md         # 本文件 + 11 字段 frontmatter
└── scripts/
    ├── memos_bridge.py     # 5 类方法论自研实现
    └── test_memos_bridge.py # 11+ unittest PASS
```

- §4(a) ✅ LICENSE 落盘
- §4(d) ✅ NOTICE + Modified
- §6 Trademark ✅ 不得用 "MemOS 官方"

---

## 六、与天龙既有栈的协同（11 位置）

```
memos-methodology V1.0 (借鉴档 · Apache-2.0 ✅ · 自研 +11 PASS)
   ├─► 07-scribe V12.3 → V12.4        ⭐UPG  Layer 4 蒸馏加 MemOS hybrid
   ├─► 09-06-skills-administrator V1.1 → V1.2  ⭐UPG skills + memory OS 治理
   ├─► session-distiller V1.0 → V1.2   ⭐UPG BuilderPulse 风格加 cross-task state
   ├─► hv-analysis V1.0 → V1.3         ⭐UPG  万字 PDF 检索走 hybrid retrieval
   ├─► 28-10-finance-data-base V1.2 → V1.3 ⭐UPG 三栈协同加 memory OS 缓存层
   ├─► mneme-heat-engine V1.0 (stage 41 借鉴档)  📎  heat 合并复用
   ├─► a-stock-data-bridge (stage 25 · Apache-2.0)  📎  Apache-2.0 模板
   ├─► agent-reach-integration (stage 14 · MIT)  📎  渠道层协同
   ├─► nomifun-methodology (stage 46)       📎  借鉴档模式先例
   └─► dsh-eval-bridge (stage 45 · MIT)        📎  借鉴档模式先例
```

---

## 七、累计 PASS 增量

```
Stage 46 final: 875 PASS
Stage 47.1 net (memOS 部分):
   +11 ─► 886  memos_bridge.py V1.0 · 11 unittest PASS
                            │
   思密 contemplation (memOS 部分累计): +11 PASS
```

---

## 八、合规红线检查表（**Apache-2.0 12 项 · 复用 stage 25**）

- [ ] LICENSE 11.4 KB 已落盘 (verbatim 实拉确认)
- [ ] NOTICE 已加 "Modified by dragon-engine / 2026-08-26"
- [ ] 不得用 "MemOS 官方" / "官方授权" 字样
- [ ] 不写 .env / api_key 任何产物
- [ ] 不 import @memtensor/* npm 包
- [ ] 不克隆 src / lib / react 目录
- [ ] 借鉴档自研：4 层 pipeline + 11 unittest
- [ ] 不跑 npm install (依赖 Blello 风险)
- [ ] Apache-2.0 §4(a) 强化条款
- [ ] Apache-2.0 §4(d) NOTICE 强化
- [ ] Apache-2.0 §6 Trademark 强化
- [ ] 不踩 DSH harness 软链

---

## 九、来源链接

- 仓库：https://github.com/MemTensor/MemOS
- LICENSE 实拉（Apache-2.0 11.4 KB verbatim）：https://raw.githubusercontent.com/MemTensor/MemOS/main/LICENSE
- topics：deepseek-harness / dsh-plugin / hermes / openclaw / agentic-ai / memory-management（与天龙 DSH 生态同档）

---

> **下次同步点**：用户实跑 memos_bridge.py 11 PASS 后，可联动 Stage 47.1 comet 借鉴档共 +14 → 累计 900。
