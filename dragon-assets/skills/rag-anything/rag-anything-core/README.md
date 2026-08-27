# rag-anything-core

## 简介

RAG-Anything的核心管理器，提供统一的文档处理接口和生命周期管理。

## 快速开始

```python
from rag_anything_core import RAGAnythingManager

# 创建管理器
manager = RAGAnythingManager()

# 处理文档
result = await manager.process("document.pdf")
print(f"处理结果: {result.success}")

# 查询
answer = await manager.query("文档的主要内容是什么?")
print(f"答案: {answer.answer}")
```

## 配置

```python
from rag_anything_core import RAGAnythingConfig

config = RAGAnythingConfig(
    data_dir="./data",
    embedding_model="text-embedding-3-small",
    vector_store="chroma",
    enable_kg=True,
    enable_multimodal=True,
)

manager = RAGAnythingManager(config=config)
```

## 许可

MIT License
