# rag-anything-knowledge-graph - 跨模态知识图谱构建

## L0: 一句话描述

RAG-Anything的知识图谱构建模块，支持文本、表格、公式、图像的跨模态实体识别和关系抽取。

## L1: 使用场景

- **跨模态实体识别**：从文本、表格、公式、图像中提取实体
- **关系抽取**：抽取实体间的关系
- **跨模态边创建**：建立不同模态实体之间的关联
- **层级结构保持**：保持文档的层级结构

## L2: 详细文档

### 核心功能

| 功能 | 说明 |
|------|------|
| **文本实体识别** | 命名实体识别、关键词提取 |
| **表格实体识别** | 表格头、行列实体 |
| **公式实体识别** | 公式中的变量、符号 |
| **图像实体识别** | 图像描述中的实体 |
| **关系抽取** | 实体间关系抽取 |
| **跨模态边** | 不同模态间的关联 |

### API使用

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

## L3: API参考

详见 `scripts/kg_builder.py`
