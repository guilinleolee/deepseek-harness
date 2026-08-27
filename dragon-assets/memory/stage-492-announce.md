---
name: stage-492-announce
description: Stage 49.2 总验收公告 — memsearch-bridge V1.0（借鉴档 · 轻量 · MIT · Milvus 出品）
metadata:
  node_type: memory
  originSessionId: stage-492-memsearch-20260826
  modified: 2026-08-26T11:38:08.000Z
---

# 🚀 Stage 49.2 总验收公告 · 2026-08-26

> **TL;DR**：天龙引擎 Stage 49.2 借鉴 [zilliztech/memsearch](https://github.com/zilliztech/memsearch)（**MIT ✅** · Copyright (c) 2025 Zilliz Inc. · **Milvus 出品 · 已原生支持 DSH**）的 **5 类核心设计** + **天龙自研 V1.0**。累计 **PASS 885 → 890**（+5 net · 20/20 自研 unittest 拆 6 大类）。

---

## 一、本阶段交付

| W# | 任务 | 关键产物 | 验证 |
|---|---|---|---|
| **W1** | D1 R1 协议评估 | MIT ✅ · 1,068 B verbatim · Copyright (c) 2025 Zilliz Inc. | ✅ |
| **W1** | memsearch-bridge V1.0 + 5 类借鉴 + 4 CLI | `SKILL.md V1.0` + `memsearch_bridge.py` + 20/20 unittest PASS | ✅ 自检通过 |
| **W1** | 主题文件 + MEMORY row + 本文件 | `memory/stage-492-memsearch.md` (10 KB) + MEMORY 890 PASS | ✅ |

---

## 二、5 类借鉴

### 2.1 Markdown source-of-truth + SHA-256 dedup
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

### 2.4 Skills-from-memory procedural
```python
def extract_skill_candidate(memory, min_steps=3):
    steps = re.findall(r"^\s*\d+[\.、]\s*(.+?)$", memory.content, re.M)
    if len(steps) >= min_steps:
        return SkillCandidate(name=f"auto-skill-{memory.sha256[:8]}", ...)
```

### 2.5 PyPI + DSH plugin 双发布
- `pip install memsearch` · `uv tool install "memsearch[onnx]"`
- `dsh plugin --profile web add @zilliz/memsearch-dsh`

---

## 三、20/20 自研 unittest PASS 拆 6 大类

```
✓ TestSHA256Dedup         (2 用例)  # SHA-256 内容 hash 验证
✓ TestParseMarkdown       (5 用例)  # tags / no-tags / empty / multiple / path
✓ TestProgressiveRetrieve (5 用例)  # search / empty / empty-query / sort / expand
✓ TestRRFRerank           (4 用例)  # basic / disjoint / empty / one-side
✓ TestSkillExtract        (3 用例)  # with-steps / no-steps / exactly-3
✓ TestMemsearchEndToEnd   (1 用例)  # full workflow
                                   20/20 ✓ 0.003s
```

---

## 四、累计 PASS 锁定

```
882 (Stage 48 累计)
   +3 ─► 885 (stage 49.1)
   +5 ─► 890 (stage 49.2)
                          │
                          ─► 890 locked
```

---

> **下次同步点**：用户在 DSH 真机装入 `@zilliz/memsearch-dsh` 后跑 `/memory-recall what did we decide about ...`。
