# rag-anything-core - RAG-Anything核心管理器

## L0: 一句话描述

RAG-Anything的核心管理器，提供统一的文档处理接口和生命周期管理。

## L1: 使用场景

- 初始化和管理RAG-Anything各子模块
- 协调文档处理流程
- 管理知识库状态
- 提供统一的查询接口

## L2: 详细文档

### 核心类

```python
from rag_anything_core import RAGAnythingManager

# 初始化
manager = RAGAnythingManager(
    data_dir="./data",           # 数据存储目录
    embedding_model="text-embedding-3-small",
    vector_store="chroma",       # 向量存储类型
    enable_kg=True,             # 启用知识图谱
    enable_multimodal=True      # 启用多模态
)

# 处理文档
await manager.process("document.pdf")

# 查询
result = await manager.query("问题是什么?")
```

### 配置选项

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `data_dir` | str | "./data" | 数据存储目录 |
| `embedding_model` | str | "text-embedding-3-small" | Embedding模型 |
| `vector_store` | str | "chroma" | 向量存储类型 |
| `enable_kg` | bool | True | 是否启用知识图谱 |
| `enable_multimodal` | bool | True | 是否启用多模态 |
| `chunk_size` | int | 512 | 文本分块大小 |
| `chunk_overlap` | int | 50 | 块重叠大小 |

### 与天龙引擎协同

- 复用LightRAG的向量存储接口
- 复用lightrag-knowledge-base的配置管理
- 支持与07记录师的Wiki归档联动

## L3: API参考

详见 `scripts/rag_anything_manager.py`
