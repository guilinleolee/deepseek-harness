# rag-anything-knowledge-graph

## 简介

RAG-Anything的知识图谱构建模块，支持跨模态实体识别和关系抽取。

## 快速开始

```python
from rag_anything_knowledge_graph import KGBuilder

kg_builder = KGBuilder()

# 构建知识图谱
kg_data = await kg_builder.build(parsed_doc)

# 访问结果
print(f"实体数: {len(kg_data.entities)}")
print(f"关系数: {len(kg_data.relations)}")
print(f"跨模态边: {len(kg_data.cross_modal_edges)}")
```

## 许可

MIT License
