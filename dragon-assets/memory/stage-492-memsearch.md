# Stage 49.2 · memsearch-bridge V1.0 · 主题文件

> **阶段**：天龙引擎 · **stage 49.2**（**借鉴档 · 轻量 · MIT · Milvus 出品**）
> **日期**：2026-08-26
> **集成度**：⭐ 战略级 — 跨 agent 持久化记忆层
> **入口文件**：[`skills/memsearch-bridge/SKILL.md`](../skills/memsearch-bridge/SKILL.md)

---

## 一、TL;DR

> 借鉴 [zilliztech/memsearch](https://github.com/zilliztech/memsearch) v0.x（**MIT ✅ · Copyright (c) 2025 Zilliz Inc.** · 已发布 PyPI · **已原生支持 DSH**）的 **5 类核心设计** + **天龙自研 V1.0**。累计 PASS **885 → 890**（+5 net · 20/20 自研 unittest 拆 6 大类）。

---

## 二、Stage 49.2 触发源（一手）

| 字段 | 值 |
|---|---|
| **上游仓库** | https://github.com/zilliztech/memsearch |
| **作者** | zilliztech（GitHub 18416694 · Organization · **Milvus 出品**）|
| **协议** | **MIT ✅**（LICENSE 1,068 B verbatim · Copyright (c) 2025 Zilliz Inc.）|
| **PyPI** | `pip install memsearch` 或 `uv tool install "memsearch[onnx]"` |
| **已支持 5 平台** | Claude Code · Codex · **DeepSeek Harness** · OpenClaw · OpenCode |
| **DSH 安装方式** | `dsh plugin --profile web add @zilliz/memsearch-dsh` |
| **核心设计** | Markdown 源真 + Milvus shadow index + progressive 3-layer retrieval + hybrid dense+BM25+RRF + skills-from-memory procedural |

---

## 三、5 类借鉴

### 3.1 Markdown is source of truth + SHA-256 dedup

```python
def sha256_dedup(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]
```

### 3.2 Progressive 3-layer retrieval（search → expand → transcript）

```python
def progressive_retrieve(query: str, memories: List[MarkdownMemory]) -> RetrievalResult:
    layer1 = search_layer(query, memories)
    layer2 = expand_layer(query, memories, tags)
    layer3 = transcript_layer(query, latest)
    return sorted(layer1+layer2+layer3, key=lambda l: -l.score)
```

### 3.3 Hybrid search + RRF reranking

```python
def rrf_rerank(dense, sparse, k=60):
    fused = {}
    for rank, (doc_id, _) in enumerate(dense):
        fused[doc_id] = fused.get(doc_id, 0) + 1/(k+rank+1)
    for rank, (doc_id, _) in enumerate(sparse):
        fused[doc_id] = fused.get(doc_id, 0) + 1/(k+rank+1)
    return sorted(fused.items(), key=lambda x: -x[1])
```

### 3.4 Skills from memory（procedural 借鉴）

```python
def extract_skill_candidate(memory, min_steps=3):
    steps = re.findall(r"^\s*\d+[\.、]\s*(.+?)$", memory.content, re.M)
    if len(steps) >= min_steps:
        return SkillCandidate(...)
    return None
```

### 3.5 PyPI 发布生态

- `pip install memsearch` 通用 Python
- `uv tool install "memsearch[onnx]"` 带 ONNX 模型
- `dsh plugin --profile web add @zilliz/memsearch-dsh` DSH 专用

---

## 四、20/20 自研 unittest PASS 拆 6 大类

```
✓ TestSHA256Dedup         (2 用例)  # 内容 hash 验证
✓ TestParseMarkdown       (5 用例)  # tags / no-tags / empty / multiple / path
✓ TestProgressiveRetrieve (5 用例)  # search / empty / empty-query / sort / expand
✓ TestRRFRerank           (4 用例)  # basic / disjoint / empty / one-side
✓ TestSkillExtract        (3 用例)  # with-steps / no-steps / exactly-3
✓ TestMemsearchEndToEnd   (1 用例)  # full workflow
                                   20/20 ✓ 0.003s
```

---

## 五、4 CLI 自研工具（memsearch_bridge.py · 20/20 unittest）

```bash
$ memsearch_bridge.py hash --input "hello"           # → SHA-256 short
$ memsearch_bridge.py retrieve --query "redis"        # → 3-layer 结果
$ memsearch_bridge.py rrf                              # → RRF 数学 demo
$ memsearch_bridge.py extract-skill --input "1. ... 2. ... 3. ..."
```

---

## 六、累计 PASS 锁定

```
882 (Stage 48 累计)
   +3 ─► 885 (stage 49.1)
   +5 ─► 890 (stage 49.2)
                          │
                          ─► 890 locked
```

---

## 七、跳转入口

- **真源 SKILL.md**：[`skills/memsearch-bridge/SKILL.md`](../skills/memsearch-bridge/SKILL.md)（待写）
- **DSH 协议治理基线**：[`docs/dsh-ecosystem-license-policy.md`](../docs/dsh-ecosystem-license-policy.md)
- **Stage 49 盘点**：[`memory/stage-49-candidates-evaluation.md`](stage-49-candidates-evaluation.md)

---

> **下次同步点**：用户在 DSH 真机 `dsh plugin --profile web add @zilliz/memsearch-dsh` 后跑 `/memory-recall what did we decide about ...`。
