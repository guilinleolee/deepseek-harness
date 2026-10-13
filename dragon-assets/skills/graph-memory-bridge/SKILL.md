---
name: graph-memory-bridge
description: adoresever/graph-memory v1.6.0-beta.9 (MIT 576⭐, 清华大学 2026-04) 借鉴档 — Knowledge Graph Context Engine for DeepSeek Harness,75% token 压缩,跨 session 经验复用。当用户提到 "知识图谱记忆 / gm_search / gm_record / gm_status / 跨 session 经验 / 实体抽取 / triple 抽取 / graph memory / OpenClaw" 时,自动加载天龙自研借鉴档:4 个 gm_* 工具 + 3 类节点(TASK/SKILL/EVENT) + 5 类边(USED_SKILL/SOLVED_BY/REQUIRES/PATCHES/CONFLICTS_WITH) + 双路径召回(Exact + Generalized) + Personalized PageRank + recallTokenBudget (4096)。
metadata:
  version: V1.0
  stage: 55.1
  upstream: adoresever/graph-memory v1.6.0-beta.9
  license: MIT
  created: 2026-08-26
  strategy: 借鉴档（与 stage 41/45/46/48/49.x/50.x/52/53.2 同模式 · 不镜像真源 · 自研 Python）
triggers_zh:
  - "知识图谱记忆"
  - "gm_search"
  - "gm_record"
  - "gm_status"
  - "跨 session 经验"
  - "实体抽取"
  - "triple 抽取"
  - "图谱记忆"
  - "OpenClaw"
  - "上下文压缩"
  - "PageRank"
triggers_en:
  - "knowledge graph memory"
  - "cross-session memory"
  - "triple extraction"
  - "gm_search"
  - "gm_record"
  - "gm_status"
  - "personalized PageRank"
  - "graph memory"
  - "context compression"
downstream:
  - 41 阶段 mneme-heat-engine (heat 衰减 + graph 持久化双轨记忆)
  - 43 阶段 dsh-agent-teams (captain 决策用 gm_search 调取过往经验)
  - 55 阶段 dsh-chat-import-bridge (导入历史后用 gm_record 持久化跨 session)
  - 47 阶段 dsh-univer-office-bridge (Board 可视化 graph)
  - 09-04-chief-of-staff V2.1 (multi-source context 用 graph 整合)
compliance:
  license: MIT
  notice: 上游 MIT verbatim
  trademark: 仅"借鉴 adoresever/graph-memory 范式"，不使用"清华大学官方"等
---

# graph-memory-bridge · V1.0 · 天龙引擎阶段 55.1

> **TL;DR**：借鉴 adoresever/graph-memory v1.6.0-beta.9（MIT 576⭐ · 清华大学 2026-04 邀请发布 · 130 自动化测试 PASS · 75% token 压缩 · DSH native 集成）的 Knowledge Graph Context Engine，自研 Python 桥。
> **核心能力**：3 类节点（TASK / SKILL / EVENT）+ 5 类边（USED_SKILL / SOLVED_BY / REQUIRES / PATCHES / CONFLICTS_WITH）+ 双路径召回（Exact path + Generalized path）+ Personalized PageRank + recallTokenBudget 4096。
> **天龙协同**：升级 stage 41 mneme-heat-engine（heat 衰减 → graph 持久化双轨记忆）。

---

## 0 · 前置条件

无需外部依赖。纯 Python 3.11+ 标准库。

---

## 1 · 借鉴清单（9 大核心能力）

| # | 能力 | 上游接口 | 借鉴档实现 |
|---|---|---|---|
| 1 | **结构化抽取**（conversation → TASK/SKILL/EVENT）| `extractor/` | `extractor.py`（regex + keyword 启发式） |
| 2 | **双路径召回**（Exact + Generalized）| `recaller/dual_path` | `recaller.py`（vector mock + lexical fallback） |
| 3 | **Personalized PageRank**（PPR）| `graph/ppr` | `ppr.py` |
| 4 | **社区检测** | `graph/community` | `community.py`（label propagation） |
| 5 | **4 个 gm_* 工具** | `gm_status` / `gm_search` / `gm_record` / `gm_stats` | `gm_tools.py` |
| 6 | **rolling checkpoint**（持久 prefix 模型）| `freshTurnCount=5` | `checkpoint.py` |
| 7 | **75% token 压缩** | Vector + community expansion | `compressor.py` |
| 8 | **idempotent event ID**（HMR/resume 安全）| Stable event IDs | `event_id.py` |
| 9 | **recallTokenBudget 4096** | `recallTokenBudget` 配置 | `budget.py` |

---

## 2 · 3 类节点 + 5 类边 schema

### 节点类型
```python
{
  "type": "TASK",         # 目标/执行/结果
  "content": "...",
  "session_id": "...",
  "outcome": "success" | "fail",
  "epoch": 1234567890
}
{
  "type": "SKILL",        # 验证过的可复用方法
  "content": "...",
  "confidence": 0.85,      # 0~1
  "reuse_count": 3
}
{
  "type": "EVENT",        # 错误/修复/决策/变更/事实
  "content": "...",
  "category": "error" | "fix" | "decision" | "change" | "fact",
  "severity": "info" | "warn" | "error"
}
```

### 边类型
```python
USED_SKILL       (TASK → SKILL)
SOLVED_BY        (TASK → EVENT)
REQUIRES         (SKILL → SKILL)
PATCHES          (EVENT → SKILL)
CONFLICTS_WITH   (SKILL → SKILL)
```

---

## 3 · 双路径召回（Dual-Path Recall）

```
Query
  ├─ Exact path:    vector/FTS5 → community expansion → PPR
  └─ General path:  community summary match → members

Both merge → Deduplicated local context → recallTokenBudget (4096) truncation
```

**auto-recall 阈值**：`autoRecallMinScore=0.6`（高 precision gate；从不 fallback 到 query-independent community representatives）

---

## 4 · 4 个 gm_* 工具

| 工具 | 用途 | 返回 |
|---|---|---|
| `gm_status` | 插件 + store + extraction + recall + vector 状态 | `{store_path, graph_counts, vector_coverage, mode, dimensions}` |
| `gm_search` | 显式长期 graph 搜索 | `{nodes: [...], edges: [...], sub_graph: {...}}` |
| `gm_record` | 持久化 TASK / SKILL / EVENT | `{node_id, type, deduplicated: bool}` |
| `gm_stats` | 节点/边/类型/社区统计 | `{nodes, edges, by_type, communities}` |

---

## 5 · 累计 PASS 贡献（阶段 55.1）

| 项 | PASS | 说明 |
|---|---|---|
| extractor (TASK/SKILL/EVENT 抽取) | 2 | 3 类节点 + 触发词 |
| recaller (双路径召回) | 2 | Exact + Generalized merge |
| ppr (Personalized PageRank) | 1 | 收敛 + top-k |
| gm_status / gm_search / gm_record / gm_stats | 2 | 4 工具 |
| 端到端（session → extract → store → recall → PPR → budget truncate）| 1 | 全链路 |
| **小计** | **+8** | 累计 PASS 996 → 1004 |

---

## 6 · 关键文件

| 资产 | 路径 |
|---|---|
| 本 skill | `dragon-engine/skills/graph-memory-bridge/SKILL.md` |
| LICENSE (MIT) | `dragon-engine/skills/graph-memory-bridge/LICENSE` |
| NOTICE | `dragon-engine/skills/graph-memory-bridge/NOTICE` |
| 抽取器 | `dragon-engine/skills/graph-memory-bridge/scripts/extractor.py` |
| 召回器 | `dragon-engine/skills/graph-memory-bridge/scripts/recaller.py` |
| PPR 算法 | `dragon-engine/skills/graph-memory-bridge/scripts/ppr.py` |
| gm_* 工具 | `dragon-engine/skills/graph-memory-bridge/scripts/gm_tools.py` |
| 健康检查 | `dragon-engine/skills/graph-memory-bridge/scripts/check.py` |
| 测试套 | `dragon-engine/skills/graph-memory-bridge/tests/test_*.py` |
| 上游仓库 | https://github.com/adoresever/graph-memory |
| 上游 DSH adapter | `graph-memory/dsh.ts` |

---

## 7 · 决策记录

| # | 决策项 | 选择 |
|---|---|---|
| 1 | 集成形态 | **借鉴档**（与 stage 41/45/46/48/49.x/50.x/52/53.2 同模式）|
| 2 | 触发安装 | **无需安装**（pip 即可）|
| 3 | 真源安装 | **可选**（npm + DSH plugin 流程 · 与本 skill 并行）|
| 4 | 协同方向 | **天龙 stage 41 mneme-heat-engine 升级**（heat 衰减 + graph 持久化双轨记忆）|
| 5 | 商标 | 仅"借鉴 adoresever/graph-memory 范式"，不用"清华大学官方" |
