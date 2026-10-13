---
license: UNKNOWN
triggers: ["llamaindex rag", "LlamaIndex RAG - 知识库构建与检索"]
---
# LlamaIndex RAG - 知识库构建与检索

## L0: 一句话 (≤15字)
PDF/笔记 → RAG知识库 → 智能问答

## L1: 使用场景 (50-100字)

### 触发词
- 构建知识库 / 索引文档
- 基于我的笔记回答 / 检索知识库
- upload / 导入资料 / 建立知识库

### 适用场景
- 学习资料太多难以检索
- 需要从PDF/笔记中提取信息
- 构建个人知识库
- 与AI导师配合使用

### 不适用
- 简单常识性问题
- 需要实时信息的查询
- 纯计算类问题

## L2: 详细文档

### 核心能力

```python
class KnowledgeBaseManager(dspy.Signature):
    """LlamaIndex驱动的RAG知识库管理"""
    action: str = dspy.InputField(
        desc="操作: create/index/query/summary/delete",
        prefix="操作"
    )
    kb_name: str = dspy.InputField(desc="知识库名称")
    documents: list = dspy.InputField(
        desc="文档路径列表",
        default=[]
    )
    query: str = dspy.InputField(desc="查询内容", default="")

    result: str = dspy.OutputField(desc="执行结果")
    retrieved_context: list = dspy.OutputField(desc="检索到的上下文")
    summary: str = dspy.OutputField(desc="知识库摘要")


class HybridRetriever(dspy.Signature):
    """混合检索: 向量+关键词"""
    query: str = dspy.InputField(desc="查询")
    kb_name: str = dspy.InputField(desc="知识库名")
    top_k: int = dspy.InputField(desc="返回数量", default=5)

    results: list = dspy.OutputField(desc="检索结果")
    sources: list = dspy.OutputField(desc="来源标注")


class KnowledgeSynthesis(dspy.Signature):
    """基于检索内容生成回答"""
    query: str = dspy.InputField(desc="用户问题")
    context: list = dspy.InputField(desc="检索到的上下文")

    answer: str = dspy.OutputField(desc="回答")
    citations: list = dspy.OutputField(desc="引用标注")
    confidence: float = dspy.OutputField(desc="置信度 0-1")
```

### 支持的文档格式

| 格式 | 支持 | 处理方式 |
|------|------|---------|
| **PDF** | ✅ | PyMuPDF提取文本/表格 |
| **Markdown** | ✅ | 直接解析 |
| **TXT** | ✅ | UTF-8编码 |
| **DOCX** | ✅ | python-docx解析 |
| **PPTX** | ✅ | 提取文本+图片说明 |
| **EPUB** | ✅ | ebooklib解析 |
| **HTML** | ✅ | BeautifulSoup提取 |
| **JSON** | ✅ | 结构化解析 |

### 检索模式

```yaml
检索模式:
  vector:      # 向量检索（语义相似）
  keyword:     # 关键词检索（BM25）
  hybrid:      # 混合模式（推荐）
  parent_doc:  # 父文档检索（整篇返回）
```

### 使用示例

```bash
# ===== 知识库管理 =====
kb create my-kb                    # 创建知识库
kb add my-kb --docs ./papers/     # 添加文档
kb list                            # 列出所有知识库
kb info my-kb                      # 知识库信息
kb delete my-kb                    # 删除知识库

# ===== 检索查询 =====
kb query my-kb "梯度下降原理"      # 检索
kb query my-kb "attention" --mode hybrid  # 混合检索

# ===== 与Obsidian集成 =====
kb sync obsidian --vault ~/Obsidian --kb my-kb  # 同步Obsidian笔记

# ===== 导出 =====
kb export my-kb --format json      # 导出为JSON
kb export my-kb --format markdown  # 导出为Markdown
```

### Python API

```python
from llamaindex_rag import KnowledgeBase, HybridRetriever

# 创建知识库
kb = KnowledgeBase(name="machine-learning")
kb.add_documents([
    "papers/lecun-deep-learning.pdf",
    "notes/optimization.md",
    "books/bengio-dl-book.txt"
])

# 混合检索
retriever = HybridRetriever()
results = retriever.search(
    kb_name="machine-learning",
    query="解释梯度下降和Adam的区别",
    top_k=5
)

for r in results:
    print(f"[来源: {r.source}] {r.content[:200]}...")

# 智能问答
answer = kb.ask("为什么Adam通常比SGD收敛更快？")
print(f"答案: {answer.text}")
print(f"引用: {answer.citations}")
```

### 与学习师集成

```yaml
学习师工作流:
  诊断阶段:
    - 检索知识库 → llamaindex-rag
    - 了解用户已有知识

  学习阶段:
    - RAG问答 → 辅助理解
    - 引用原文 → 增强可信度

  巩固阶段:
    - 生成知识卡片 → Anki
    - 知识图谱构建 → 知识点关联
```

### 索引配置

```yaml
索引配置:
  chunk_size: 512
  chunk_overlap: 50

  embedding:
    provider: openai  # 或 minimax/huggingface
    model: text-embedding-3-small
    dimension: 1536

  reranker:
    enabled: true
    model: bge-reranker-base
```

### 质量标准

1. **检索准确性**: 相关文档召回率 > 80%
2. **上下文完整性**: 检索片段语义完整
3. **引用准确性**: 引用指向正确来源
4. **响应时效**: 检索 < 2秒

### 自检清单

- [ ] 文档已成功索引
- [ ] 检索结果与问题相关
- [ ] 引用标注正确
- [ ] 支持增量更新
- [ ] 与Obsidian双向同步
