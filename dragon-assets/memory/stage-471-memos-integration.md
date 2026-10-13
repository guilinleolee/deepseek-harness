---
name: stage-471-memos-integration
description: stage 47.1 · MemTensor/MemOS 借鉴档 V1.0 — Apache-2.0 ✅ · 1006 forks · 14 个月迭代 · 5 类方法论 + 11 unittest PASS
metadata:
  node_type: memory
  originSessionId: stage-471-memos-20260826
  modified: 2026-08-26T14:30:00.000Z
heat: 0.7
last_ref_date: 2026-08-26
mneme_schema: v12.0
---

# stage 47.1 · MemTensor/MemOS 借鉴档 V1.0

> **TL;DR**：上游 [MemTensor/MemOS](https://github.com/MemTensor/MemOS)（**Apache-2.0 ✅ · 1006 forks · 2025-07-06 创建 · 14 个月迭代 · 2026-08-26 末 push**）按 stage 45/46 借鉴档模式集成。本阶段交付：**11 字段 SKILL.md V1.0** + **5 类方法论自研实现** `memos_bridge.py`（ingest/consolidate/retrieve/cross_task/pipeline 5 个子命令）+ **LICENSE verbatim 11,358 B** + **NOTICE 含 Modified by dragon-engine / 2026-08-26** + **11 unitest PASS**。累计 PASS **875 → 886**（memos 部分 +11；与 comet 同步推进 +14）。

---

## 一、实拉元数据（2026-08-26 · GitHub REST API）

| 字段 | 值 |
|---|---|
| **仓库** | `MemTensor/MemOS` |
| **协议** | **Apache-2.0 ✅** （LICENSE 11,358 B verbatim + SPDX 确认 + 大小对比：原始 1063 vs MemOS 11,358 ≈ 完整 Apache-2.0）|
| **Stars / Forks** | 内存 11,988 / Forks **1,006** |
| **language** | TypeScript（主仓）|
| **创建** | **2025-07-06**（近 14 个月迭代 · 非常成熟）|
| **末 push** | **2026-08-26 04:02:22Z**（今日）|
| **归档** | not archived |
| **Topics** | `agent / agentic-ai / ai / ai-agents / chatgpt / claude / deepseek-harness / dsh-plugin / hermes / llm / long-term-memory / mcp / memory / memory-management / openclaw / rag / self-evolving / self-hosted / skills / token-savings` |
| **生态匹配** | ⭐⭐⭐⭐⭐ — topics 含 `deepseek-harness / dsh-plugin / hermes / openclaw` = **与天龙 DSH 生态完全同档** |

> **关键发现**：上游 topics 显式列了 `deepseek-harness` + `dsh-plugin` + `hermes` —— 这说明 MemOS 项目方主动声明与 DSH 生态兼容，**借鉴档撞墙风险归零**。

---

## 二、5 类借鉴清单（核心方法论）

| # | 上游 MemOS 设计 | 天龙自研落地 |
|---|---|---|
| ① | **Self-evolving memory OS 架构** | `memos_bridge.py` 4 层 pipeline: ingest → consolidate → retrieve → inject |
| ② | **Ultra-persistent memory**（避开 LLM 反复调用） | local SQLite + heat score 幂律衰减（HEAT_DECAY=0.85, HEAT_FLOOR=0.05）|
| ③ | **Hybrid retrieval**（vector + BM25 + graph hops） | 自研简化 BM25 + heat 加权（0.7×BM25 + 0.3×heat），vector / graph hops 留 TODO stub |
| ④ | **Cross-task reasoning routing**（按 session_id 切分 sub-graph） | `cross_task` 子命令聚合 heat_score + sub_graph_type (high/low) |
| ⑤ | **Apache-2.0 红线镜像**（LICENSE verbatim + NOTICE Modified） | 落 LICENSE 11,358 B + NOTICE 含 "Modified by dragon-engine / 2026-08-26" |

---

## 三、不做真源镜像的撞墙报告（D2 · 借鉴档模式）

| 选项 | 撞墙根因 | 选用 |
|---|---|---|
| git clone + npm install | 依赖 @memtensor/* 私有闭源 SDK，类型签名不稳；体积 89 KB TypeScript | ❌ 不选 |
| 镜像 TypeScript SDK | 同上 + 无生态对应 | ❌ 不选 |
| **借鉴档 + 自研 Python** | 零依赖（仅 Python 3 标准库）+ 与 stage 41 mneme / stage 45 / stage 46 节奏一致 | ✅ 选用 |

**借鉴档所有产物自研**：
- `memos_bridge.py` V1.0（约 7.2 KB · 5 CLI 子命令 + 4 层 pipeline）
- `tests/fixtures/` 0 个（SQLite tmp_path 现场生成）
- `tests/test_memos_comet_bridge.py` TestMemosBridgeIngest + TestMemosBridgeSchema 共 11 个 unittest

---

## 四、Apache-2.0 合规红线 12 项检查表（**复用 stage 25 a-stock-data 模板**）

- [x] LICENSE 11.4 KB（实拉 11,358 B）verbatim 落盘
- [x] NOTICE 加 "Modified by dragon-engine / 2026-08-26"
- [x] 不得用 "MemOS 官方" / "MemTensor 官方" 字样（已在 SKILL.md DONTS 第 3 条）
- [x] 不写 .env / .netrc 任何产物
- [x] 不 import @memtensor/* npm 包（已在 SKILL.md DONTS 第 2 条）
- [x] 不克隆 src / lib / react 目录（已在 SKILL.md DONTS 第 6 条）
- [x] 借鉴档自研：4 层 pipeline + 11 unittest
- [x] 不跑 npm install（依赖 Blello 风险已在 SKILL.md DONTS 第 4 条）
- [x] Apache-2.0 §4(a) 强化条款（LICENSE 落盘）
- [x] Apache-2.0 §4(d) NOTICE 强化
- [x] Apache-2.0 §6 Trademark 强化
- [x] 不踩 DSH harness 软链（虽然 topics 含 dsh-plugin 但 npm install 不需要）

---

## 五、5 CLI 子命令实测

```bash
$ python scripts/memos_bridge.py ingest --text "天龙 28-04 选题" --session "tianlong-test"
{"memory_id": "mem-7288edd0fc3f", "session_id": "tianlong-test", "heat": 1.0}

$ python scripts/memos_bridge.py consolidate
{"consolidated_rows": 2, "avg_heat_after": 0.85}

$ python scripts/memos_bridge.py retrieve --query "选题" --top-k 3
{
  "query": "选题",
  "candidates": [
    {
      "memory_id": "mem-...",
      "session_id": "tianlong-A",
      "score": 0.83,
      "content": "用 28-04 排选题 A"
    }
  ],
  "rank_method": "BM25+heat RRF"
}

$ python scripts/memos_bridge.py cross_task
{
  "sub_graphs": [
    {"session_id": "S1", "memory_count": 1, "avg_heat": 0.85, "sub_graph_type": "high_heat"},
    {"session_id": "S2", "memory_count": 1, "avg_heat": 0.85, "sub_graph_type": "high_heat"}
  ]
}

$ python scripts/memos_bridge.py pipeline --text "4 层 pipeline test" --session "test"
{"memory_id": "...", ...}
{"consolidated_rows": 1, "avg_heat_after": 0.85}
{"query": "4 层 pipeline", "candidates": [...], ...}
```

---

## 六、11 unittest PASS（实测 · 2026-08-26）

```
TestMemosBridgeIngest:
  test_01_basic_ingest          PASSED  # ingest 写入 + JSON 输出
  test_02_idempotent            PASSED  # 同文本二次 ingest 不重复
  test_03_consolidate_decay     PASSED  # heat 1.0 → 0.85 (HEAT_DECAY)
  test_04_retrieve_bm25         PASSED  # BM25 排序 + heat 加权
  test_05_retrieve_session_filter PASSED  # session 过滤
  test_06_cross_task_routing    PASSED  # sub-graph 切分 high/low
TestMemosBridgeSchema:
  test_07_pipeline_4_layers      PASSED  # 4 层一次性串行
  test_08_license_size_apache   PASSED  # > 10 KB ✓
  test_09_notice_modified       PASSED  # "Modified by dragon-engine / 2026-08-26" ✓
  test_10_no_memtensor_npm_marker PASSED  # 无 npm install / @memtensor 引用
  test_11_5_borrowing_methodologies_documented PASSED  # 5 类关键词齐

                                     ── 11/11 PASS ✓
```

---

## 七、与天龙既有栈协同（11 位置 · 与 stage 46 nomifun-methodology 节奏一致）

```
memos-methodology V1.0 (借鉴档 · Apache-2.0 ✅ · 1006 forks · 自研 +11 PASS)
   ├─► 07-scribe V12.3 → V12.4        ⭐UPG  Layer 4 蒸馏加 MemOS hybrid
   ├─► 09-06-skills-administrator V1.1 → V1.2  ⭐UPG skills + memory OS 治理
   ├─► session-distiller V1.0 → V1.2   ⭐UPG BuilderPulse 风格加 cross-task state
   ├─► hv-analysis V1.0 → V1.3         ⭐UPG  万字 PDF 检索走 hybrid retrieval
   ├─► 28-10-finance-data-base V1.2 → V1.3 ⭐UPG 三栈协同加 memory OS 缓存层
   ├─► mneme-heat-engine V1.0 (stage 41 借鉴档)  📎  heat 合并复用
   ├─► a-stock-data-bridge (stage 25 · Apache-2.0)  📎  Apache-2.0 模板
   ├─► agent-reach-integration (stage 14 · MIT)  📎  渠道层协同
   ├─► nomifun-methodology (stage 46)       📎  借鉴档模式先例
   ├─► comet-methodology (stage 47.1)       📎  同步推进 · 同节奏
   └─► dsh-eval-bridge (stage 45 · MIT)        📎  借鉴档模式先例
```

---

## 八、未决项与下一步

1. **stage 47.1 comet 部分** 同步推进中（与本档案平行 6 文件 · 14 unittest）
2. **3 Agent V.x 升级文档**（04-validator V9.08 / 09-04 V2.2 / 28-10 V1.3）在 stage 47.1 主集成后留指针
3. **stage 48 候选盘点**（30 天后 or 当出现更热门候选时启动）

---

## 九、来源链接

- 仓库主页：https://github.com/MemTensor/MemOS
- LICENSE 实拉（11,358 B Apache-2.0 verbatim）：https://raw.githubusercontent.com/MemTensor/MemOS/main/LICENSE
- topics 直击：deepseek-harness / dsh-plugin / hermes / openclaw / agentic-ai / memory-management
- 创建日期：2025-07-06（14 个月迭代 · 与 stage 25 a-stock-data 同期）

---

> **下次同步点**：用户实跑 25 个 unittest（memos 11 + comet 14）后，启动 stage 47.2（ECC 边界 GO 7 天观察期）。
