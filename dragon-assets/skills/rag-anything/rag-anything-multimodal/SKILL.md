# rag-anything-multimodal - 多模态处理器

## L0: 一句话描述

RAG-Anything的多模态处理器，支持跨模态Embedding、模态融合检索和结果重排序。

## L1: 使用场景

- **混合检索**：文本、表格、公式、图像的联合检索
- **模态自适应排序**：根据查询类型自动调整各模态的权重
- **结果重排序**：使用Cross-Encoder优化检索结果

## L2: 详细文档

### 核心功能

| 功能 | 说明 |
|------|------|
| **跨模态Embedding** | 文本/图像统一向量空间 |
| **模态融合检索** | Vector-Graph Fusion双层检索 |
| **Modality-Aware Ranking** | 模态自适应排序 |
| **Relational Coherence** | 关系一致性维护 |

### API使用

```python
from rag_anything_multimodal import ModalRetriever

retriever = ModalRetriever()

# 检索
results = await retriever.search("查询内容", mode="hybrid")

# 重排序
final = await retriever.rerank_and_summarize(results, query)
```

## L3: API参考

详见 `scripts/modal_retriever.py`
