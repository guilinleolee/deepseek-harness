# rag-anything-multimodal

## 简介

RAG-Anything的多模态处理器，支持跨模态Embedding、模态融合检索和结果重排序。

## 快速开始

```python
from rag_anything_multimodal import ModalRetriever

retriever = ModalRetriever()

# 索引文档
await retriever.index(parsed_document)

# 检索
results = await retriever.search("查询内容", mode="hybrid")

# 重排序和摘要
final = await retriever.rerank_and_summarize(results, query)
```

## 依赖安装

```bash
pip install chromadb  # 向量存储
pip install openai    # OpenAI嵌入
```

## 许可

MIT License
