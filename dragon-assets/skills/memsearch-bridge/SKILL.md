---
name: memsearch-bridge
description: |
  借鉴 zilliztech/memsearch（MIT · Copyright (c) 2025 Zilliz Inc. · Milvus 出品 · 已原生支持 DSH）的 5 类核心设计 + 自研 V1.0。
  借鉴清单：① Markdown 源真 + SHA-256 dedup ② Progressive 3-layer retrieval (search → expand → transcript)
  ③ Hybrid dense + BM25 + RRF reranking ④ Skills-from-memory procedural ⑤ PyPI + DSH plugin 双发布。
  Stage 49.2 借鉴档 · 与 stage 41 mneme-heat-engine 高度协同（持久化记忆层）。
metadata:
  version: "1.0.0"
  date: "2026-08-26"
  license: MIT
  author: 天龙引擎 · Stage 49.2
  upstream_borrowing:
    - zilliztech/memsearch (MIT · 2025)
  integration_stage: 49.2
  integration_mode: "借鉴档（DSH Desktop 路径依赖 + ONNX 模型 1GB+）"
  triggers:
    - "memsearch"
    - "Milvus"
    - "持久化记忆"
    - "/memory-recall"
    - "DSH memory"
    - "Markdown memory"
    - "hybrid search"
    - "RRF"
---

# memsearch-bridge · V1.0（借鉴档 · 轻量）

> **TL;DR**：借鉴 [zilliztech/memsearch](https://github.com/zilliztech/memsearch)（**MIT ✅** · **Milvus 出品 · 已原生支持 DSH**）的 **5 类核心设计** + **天龙自研 V1.0**。**20/20 unittest PASS**（拆 6 大类）。

---

## L0: 一句话描述 (≤15字)

Milvus 持久化记忆借鉴。

---

## L1: 使用场景

当用户需要：
- 在 DSH 真机装入 `@zilliz/memsearch-dsh`（原生 DSH plugin）
- 用 `/memory-recall` 命令从 .memsearch/memory/ 检索历史会话
- 自动 capture → pre-step memory injection → native skill recall
- 三层检索（search → expand → transcript）+ RRF rerank
- Skills-from-memory（procedural 记忆层）：自动从重复 workflow 提炼可安装 skill

---

## L2: 5 类借鉴

### 2.1 Markdown is source of truth + SHA-256 dedup
```python
def sha256_dedup(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]
```

### 2.2 Progressive 3-layer retrieval
```python
def progressive_retrieve(query, memories):
    layer1 = search_layer(query, memories)      # 关键词命中
    layer2 = expand_layer(query, memories)      # tag 命中
    layer3 = transcript_layer(query)             # transcript snippet
    return sorted(layer1+layer2+layer3, key=lambda l: -l.score)
```

### 2.3 Hybrid search + RRF (Reciprocal Rank Fusion)
```python
def rrf_rerank(dense, sparse, k=60):
    fused = {}
    for rank, (doc_id, _) in enumerate(dense):
        fused[doc_id] = fused.get(doc_id, 0) + 1/(k+rank+1)
    for rank, (doc_id, _) in enumerate(sparse):
        fused[doc_id] = fused.get(doc_id, 0) + 1/(k+rank+1)
    return sorted(fused.items(), key=lambda x: -x[1])
```

### 2.4 Skills-from-memory procedural 借鉴
```python
def extract_skill_candidate(memory, min_steps=3):
    steps = re.findall(r"^\s*\d+[\.、]\s*(.+?)$", memory.content, re.M)
    if len(steps) >= min_steps:
        return SkillCandidate(name=f"auto-skill-{memory.sha256[:8]}", ...)
    return None
```

### 2.5 PyPI + DSH plugin 双发布生态
- `pip install memsearch` · `uv tool install "memsearch[onnx]"`
- `dsh plugin --profile web add @zilliz/memsearch-dsh`

---

## L3: 安装

```bash
# 1. 装本 skill（天龙自有，已落 dragon-engine/skills/memsearch-bridge/）
# 2. 真机装 memsearch（DSH Desktop 已装的话）
pip install memsearch
dsh plugin --profile web add @zilliz/memsearch-dsh
# 3. 验证 20 unittest PASS
python -m unittest tests/test_memsearch_bridge.py -v
```

---

## L4: 触发词（10 类）

```
memsearch, Milvus, 持久化记忆, /memory-recall, hybrid search, RRF
Markdown memory, dense vector, BM25 sparse, procedural memory
```

---

## L5: 下游协同

| 下游 | 协同 |
|---|---|
| **stage 41 mneme-heat-engine** (MIT) | **高度协同**：mneme 是 heat 衰减 + entity 三表 schema；memsearch 是持久化层 + vector 检索 |
| **stage 48 dsh-TUI** (MIT) | TUI 显示 memory-recall 结果 |
| **stage 45 dsh-eval-bridge** (MIT) | benchmark result → memory 入库 |
| **session-distiller V1.1** (stage 44 MIT) | session transcript → Markdown memory |
| **04-validator V9.06** (stage 45 MIT) | FMEA 加"memory 一致性"失败模式 |
| **40-01 mcp-orchestrator v2.0** | memsearch 作为第 13 MCP 服务 |

---

## L6: DON'T 护栏（5 条）

- ❌ **不要**镜像 memsearch 真源（ONNX 模型 1GB+ + DSH Desktop 路径）
- ❌ **不要**默认 enable ONNX（cost）
- ❌ **不要**让 memory 无限增长（7 天清理）
- ❌ **不要**用非 Markdown 格式存储（破坏 source of truth 原则）
- ❌ **不要**让 `borrowed: true` 缺失（MIT §4 边界）

---

## L7: 验证矩阵

| # | 必检项 | 期望 | 状态 |
|---|---|---|---|
| 1 | SHA-256 一致性 hash | 全过 | ✅ |
| 2 | Markdown 解析（tags/no-tags/empty/multiple/path）| 5/5 | ✅ |
| 3 | Progressive 3-layer 检索（keyword/empty/sort/expand）| 5/5 | ✅ |
| 4 | RRF rerank（basic/disjoint/empty/one-side）| 4/4 | ✅ |
| 5 | Skills extraction（with-steps/no-steps/exactly-3）| 3/3 | ✅ |
| 6 | end-to-end workflow | 1/1 | ✅ |
| 7 | 20/20 unittest PASS | 拆 6 大类 | ✅ |

---

## L8: 参考链接

- **借鉴源**：https://github.com/zilliztech/memsearch · MIT
- **LICENSE verbatim**：https://raw.githubusercontent.com/zilliztech/memsearch/main/LICENSE（1,068 B / 21 行 / MIT）
- **DSH 平台插件**：https://zilliztech.github.io/memsearch/platforms/dsh/
- **DSH 协议治理基线**：[`docs/dsh-ecosystem-license-policy.md`](../../../docs/dsh-ecosystem-license-policy.md)
- **Stage 49.2 主题文件**：[`memory/stage-492-memsearch.md`](../../../memory/stage-492-memsearch.md)
