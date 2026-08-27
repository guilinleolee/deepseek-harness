---
name: stage-56-candidates-evaluation
description: Stage 56 候选盘点 · 7 候选 → 1 GO + 4 边界 GO + 2 NO-GO · 关注 Soren-ABT/dsh-knowledge 本地 RAG 插件
metadata:
  node_type: memory
  type: evaluation
  originSessionId: stage-56-candidates-20260826
  modified: 2026-08-26T22:30:00.000Z
---

# Stage 56 候选盘点 · 2026-08-26

> **盘点日期**：2026-08-26
> **盘点类型**：cycle-style · 与 stage 47/49/50/51/53/54 节奏一致
> **依据**：[`docs/dsh-ecosystem-license-policy.md`](../docs/dsh-ecosystem-license-policy.md) 6 条基线
> **结论**：共盘点 **7 个新候选** → **1 GO + 4 边界 GO + 2 NO-GO**。累计 PASS **1000 锁定**（盘点本身 0 PASS）。

---

## 一、本盘点候选清单（7 个 · GitHub REST API 实拉 · 2 个查询）

### 1.1 查询 1 · topic:ai-agents+deepseek-harness（top 2）

| # | 仓库 | ★ | 协议 | 决定 | 备注 |
|---|---|---|---|---|---|
| 1 | Herdeny/awesome-dsh-plugins-2026 | 7 | CC0 | 🔴 **NO-GO**（**重复项** · stage 54 已评估为边界 GO · 治理类）| — |
| 2 | **Asaka-RUM/dsh-digital-oracle** | **1** | MIT | 🟡 **边界 GO**（"Digital Oracle: probability estimates for macro/prediction from 15 financial data providers" · 移植 komako-workshop/digital-oracle · 0 forks）| 2026-08-19 |

### 1.2 查询 2 · dsh-embed OR dsh-vector OR dsh-rag OR dsh-context topic:rag（top 5）

| # | 仓库 | ★ | 协议 | 决定 | 备注 |
|---|---|---|---|---|---|
| 3 | **Soren-ABT/dsh-knowledge** | **16** | n/a | 🟢 **GO 候选** | "**Knowledge base & RAG plugin for DeepSeek Harness: chunking, local embeddings, hybrid search, management panel**" · 2026-08-26 |
| 4 | Breeze136/dsh-kb-rag | 7 | n/a | 🟡 **边界 GO**（"本地优先文献知识库 RAG · 混合检索正文+图注 · DOI 一键直达" · 文献垂直领域）| 2026-08-26 |
| 5 | Spirtxiaoqi7/mindspace-dsh-local-rag | 3 | n/a | 🟡 **边界 GO**（"ARPM-derived local hybrid RAG plugin" · ARPM 算法新颖）| 2026-08-21 |
| 6 | wly8691-jpg/knowlp-rag | 3 | n/a | 🟡 **边界 GO**（"KnowLP-RAG: dual knowledge-graph RAG for Markdown notes · MCP + native Cordis plugin" · 双图谱 RAG）| 2026-08-26 |
| 7 | TecFancy/dsh-deeptutor | 3 | n/a | 🔴 **NO-GO**（"DeepTutor tutoring 移植" · 教育领域窄 + 与 stage 47 univer 工作台重叠低）| 2026-08-21 |

> 注：YuMu247/dsh-kb-rag (2⭐) + Fisfzy/zotero-wave-rag (3⭐) + mervyn-teo/dsh-plugin-rag (1⭐) 候选数 ≤ 3，归入"重复/超小项目"未单列。

---

## 二、1 GO 候选（Stage 57 主目标）

### 2.1 Soren-ABT/dsh-knowledge 🟢 **GO 候选**（**16⭐ · MIT 待确认 · 知识库 RAG 插件**）

| 字段 | 值 |
|---|---|
| **上游** | https://github.com/Soren-ABT/dsh-knowledge |
| **特性** | "Knowledge base & RAG plugin for DeepSeek Harness: chunking, local embeddings, hybrid search, management panel" |
| **意义** | **天龙 stage 41 mneme-heat-engine 升级路线 · 本地 RAG + 混合检索 · 与 55.1 graph-memory 协同（graph + vector 双轨记忆）** |
| **核心能力** | 4 维度：① chunking（文档切片）② local embeddings（本地向量化）③ hybrid search（向量 + 关键词混合）④ management panel（DSH UI 集成） |
| **下一步** | Stage 57 启动：4 周借鉴档 |

### 2.2 借鉴档策略

- **不镜像真源**（TypeScript 复杂度）
- **借鉴清单**：
  1. **chunker**：按段落 / 句子 / 滑动窗口 3 种切片策略
  2. **embedder**：本地 sentence-transformers（all-MiniLM-L6-v2 384d 默认）
  3. **hybrid search**：BM25 + vector cosine + RRF（Reciprocal Rank Fusion）
  4. **management panel**：DSH client 侧 UI 集成（不引入 React 复杂度，纯 CLI + .json 配置）

---

## 三、4 边界 GO + 2 NO-GO

### 3.1 边界 GO（4 个 · 待 D1+D2 详尽评估）

| # | 仓库 | 待评估项 | 协同方向 |
|---|---|---|---|
| 2 | Asaka-RUM/dsh-digital-oracle | D1 协议 · D2 金融数据源集成 | 与 stage 25 a-stock-data-bridge 互补 |
| 4 | Breeze136/dsh-kb-rag | D1 协议 · D2 文献 + DOI 集成 | 学术内容方向 |
| 5 | Spirtxiaoqi7/mindspace-dsh-local-rag | D1 协议 · D2 ARPM 算法新颖性 | 检索算法创新 |
| 6 | wly8691-jpg/knowlp-rag | D1 协议 · D2 双图谱 RAG（双层叠加）| 与 55.1 graph-memory 协同（图 + 图谱） |

### 3.2 NO-GO 红牌（2 个）

| # | 仓库 | NO-GO 原因 |
|---|---|---|
| 1 | Herdeny/awesome-dsh-plugins-2026 | **重复项**（stage 54 已评估）· 治理类不增量 PASS |
| 7 | TecFancy/dsh-deeptutor | 教育领域窄 · 与 stage 47 univer 工作台重叠低 · 3⭐ 边际贡献小 |

---

## 四、Stage 57 启动建议

### 4.1 推荐路径

```bash
# 借鉴档（4 周节奏）
Stage 57.1 · Soren-ABT/dsh-knowledge 借鉴档
  ├─ W1: chunker.py (3 种切片策略)
  ├─ W2: embedder.py (本地 sentence-transformers mock)
  ├─ W3: hybrid_search.py (BM25 + vector cosine + RRF)
  └─ W4: 端到端 + 8 PASS pytest
```

### 4.2 预期收益

- **累计 PASS +8**：chunking + embedding + hybrid_search + RRF + 端到端 + 兼容性
- **协同 stage 55.1 graph-memory**：graph + vector 双轨记忆
- **协同 stage 41 mneme-heat-engine**：RAG 补强检索层

### 4.3 风险

| 风险 | 缓解 |
|---|---|
| TypeScript monorepo 复杂度 | 借鉴档模式（纯 Python）|
| 本地 embedding 依赖 torch（~800MB）| 借鉴档用 mock 量化指标，不真跑模型 |
| hybrid search 排序算法复杂 | RRF 是公认最简有效（Reciprocal Rank Fusion）|

---

## 五、本盘点不新增 PASS

按 stage 47/49/50/51/53/54 节奏：盘点本身 0 PASS（治理类）。

**累计 PASS 1000 锁定**（维持）。

---

## 六、来源链接

- 上游 dsh-knowledge：https://github.com/Soren-ABT/dsh-knowledge
- 上游 dsh-digital-oracle：https://github.com/Asaka-RUM/dsh-digital-oracle
- 上游 dsh-kb-rag：https://github.com/Breeze136/dsh-kb-rag
- 上游 mindspace-dsh-local-rag：https://github.com/Spirtxiaoqi7/mindspace-dsh-local-rag
- 上游 knowlp-rag：https://github.com/wly8691-jpg/knowlp-rag
- DSH 协议治理基线：`docs/dsh-ecosystem-license-policy.md`
