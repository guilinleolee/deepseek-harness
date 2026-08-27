---
license: UNKNOWN
triggers: ["rag anything", "RAG-Anything - All-in-One多模态RAG框架"]
---
# RAG-Anything - All-in-One多模态RAG框架

## L0: 一句话描述

RAG-Anything是HKUDS实验室开源的All-in-One多模态RAG框架，基于LightRAG实现，支持PDF文档的多模态解析、跨模态知识图谱构建和模态感知检索。

## L1: 使用场景

- **多模态文档处理**：PDF文档的表格、公式、图像理解
- **知识图谱构建**：跨模态实体识别和关系抽取
- **智能问答**：支持文本、表格、公式、图像的混合问答
- **复杂文档理解**：学术论文、技术文档、财务报告等多模态内容

## L2: 详细文档

### 核心架构

```
┌─────────────────────────────────────────────────────────────┐
│                 RAG-Anything 多模态RAG架构                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐   │
│  │ MinerU     │───▶│   KG Builder │───▶│Modal        │   │
│  │ Parser     │    │             │    │ Retriever   │   │
│  │ (PDF解析)  │    │ (跨模态KG)  │    │ (混合检索)  │   │
│  └─────────────┘    └─────────────┘    └─────────────┘   │
│         │                  │                  │              │
│         ▼                  ▼                  ▼              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐   │
│  │  Text       │    │  Table      │    │  Formula    │   │
│  │  Entity     │    │  Entity     │    │  Entity     │   │
│  └─────────────┘    └─────────────┘    └─────────────┘   │
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐   │
│  │  Image      │    │  Relation   │    │  Cross-Modal│   │
│  │  Entity     │    │  Extractor  │    │  Edges      │   │
│  └─────────────┘    └─────────────┘    └─────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 子模块说明

| 模块 | 功能 | 核心能力 |
|------|------|---------|
| **rag-anything-core** | 核心管理器和配置 | 统一入口、配置管理、生命周期管理 |
| **rag-anything-mineru** | MinerU多模态解析器 | PDF解析、表格提取、公式提取、图像理解 |
| **rag-anything-multimodal** | 多模态处理器 | 跨模态Embedding、模态融合、结果重排序 |
| **rag-anything-knowledge-graph** | 知识图谱构建 | 实体识别、关系抽取、跨模态边创建 |

### 安装命令

```bash
# 基础安装
pip install raganything

# 完整安装（包含所有依赖）
pip install 'raganything[all]'

# 验证安装
python -c "import raganything; print(raganything.__version__)"
```

### 快速使用

```python
from rag_anything_core import RAGAnythingManager

# 初始化管理器
manager = RAGAnythingManager()

# 处理文档
result = await manager.process("document.pdf")

# 问答查询
answer = await manager.query("文档中的主要结论是什么?")
```

### 与天龙引擎现有组件协同

| 现有组件 | 协同方式 | 效果 |
|---------|---------|------|
| **LightRAG (V8.55)** | 底层检索引擎复用 | 向量+图谱双层检索 |
| **lightrag-knowledge-base** | 接口兼容 | 无缝集成 |
| **DSPy (V10.0)** | 多模态Signature定义 | 联合优化 |
| **MIPROv2** | 多变量自动优化 | +34-49%性能提升 |
| **source-verifier** | 来源验证 | 多模态来源追溯 |
| **citation-verify** | 引用网络 | 跨模态引用追踪 |

### 测试命令

```bash
# 运行全部测试
pytest skills/rag-anything/tests/ -v

# 模块测试
pytest skills/rag-anything/tests/core_test.py -v
pytest skills/rag-anything/tests/mineru_test.py -v
pytest skills/rag-anything/tests/multimodal_test.py -v
pytest skills/rag-anything/tests/kg_test.py -v
```

### 测试覆盖（55个测试用例）

| 测试类 | 测试数 | 覆盖功能 |
|--------|--------|---------|
| TestRAGAnythingCore | 6 | 管理器初始化、文档处理、查询 |
| TestConfig | 5 | 配置管理 |
| TestUtils | 7 | 工具函数 |
| TestMinerUParser | 2 | 解析器初始化 |
| TestTableExtractor | 3 | 表格提取、格式转换 |
| TestFormulaExtractor | 4 | 公式提取、LaTeX转换 |
| TestImageUnderstanding | 4 | 布局检测、Alt文本生成 |
| TestMultimodalProcessor | 6 | 多模态块处理 |
| TestModalRetriever | 5 | 检索、重排序、摘要生成 |
| TestCrossModalEmbedder | 4 | 嵌入计算、相似度 |
| TestKGBuilder | 5 | 知识图谱构建 |
| TestEntityLinker | 2 | 实体链接、消歧 |
| TestRelationExtractor | 2 | 关系抽取 |

### 核心命令（AI研究员调用）

```bash
# 文档处理
[@AI研究员] 使用rag-anything-core处理"paper.pdf"
[@AI研究员] 使用rag-anything-mineru提取论文公式和表格

# 多模态检索
[@AI研究员] 使用rag-anything-multimodal检索"查询内容" --mode hybrid
[@AI研究员] 对检索结果进行模态自适应重排序

# 知识图谱
[@AI研究员] 使用rag-anything-knowledge-graph构建论文知识图谱
[@AI研究员] 抽取实体间的关系并创建跨模态边

# 评估
[@AI研究员] /research-rag-anything --evaluate-multimodal
[@AI研究员] /benchmark-mm-rag --dataset multimodal-benchmark
```

### 版本信息

- **版本**: V1.0.0
- **来源**: HKUDS/RAG-Anything (18.7k Stars)
- **Phase**: Phase 1完成
- **集成日期**: 2026-04-26
- **天龙引擎版本**: V9.02

## L3: API参考

### RAGAnythingManager

```python
class RAGAnythingManager:
    """RAG-Anything核心管理器"""

    async def process(self, doc_path: str, **kwargs) -> ProcessResult:
        """处理文档并构建知识图谱"""
        pass

    async def query(self, question: str, mode: str = "hybrid") -> QueryResult:
        """多模态问答查询"""
        pass

    async def add_document(self, doc_path: str) -> bool:
        """添加文档到知识库"""
        pass

    async def remove_document(self, doc_id: str) -> bool:
        """从知识库移除文档"""
        pass

    async def get_stats(self) -> dict:
        """获取知识库统计信息"""
        pass
```
