---
name: rag-knowledge-builder
description: RAG 知识库构建辅助专家。触发词：rag知识库、知识库构建、文档切片、检索优化。当需要帮助客户构建知识库、设计切片策略、优化检索效果时使用。
version: 1.0.0
created: 2026-08-22
tags: [rag, knowledge-base, document, embedding, retrieval]
related:
  - fastgpt-deploy
  - dify-deploy
author: 天龙引擎 / 老李
---

# RAG 知识库构建专家

> 本技能帮助构建高质量的知识库，包括文档处理、切片策略、检索优化和效果评估。

---

## 一、知识库构建流程

```
┌─────────────────────────────────────────────────────────────────┐
│                      RAG 知识库构建流程                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. 文档准备                                                    │
│     └── 收集原始文档 → 格式转换 → 质量检查                        │
│                    ↓                                             │
│  2. 文档处理                                                    │
│     └── 分块/切片 → 清洗 → 去重 → 元数据标注                      │
│                    ↓                                             │
│  3. 向量化                                                      │
│     └── 选择嵌入模型 → 批量向量化 → 向量存储                      │
│                    ↓                                             │
│  4. 检索优化                                                    │
│     └── 混合检索 → 重排序 → 检索评估                             │
│                    ↓                                             │
│  5. 上线维护                                                    │
│     └── 增量更新 → 效果监控 → 持续优化                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 二、文档准备

### 2.1 支持的格式

| 格式 | 支持情况 | 备注 |
|------|---------|------|
| **PDF** | ✅ 完整支持 | 最好用扫描版 |
| **Word (.docx)** | ✅ 完整支持 | 保留格式 |
| **Excel (.xlsx)** | ✅ 表格处理 | 需指定范围 |
| **PPT (.pptx)** | ✅ 提取文字 | 图片需 OCR |
| **Markdown** | ✅ 完整支持 | 结构清晰 |
| **HTML** | ✅ 提取正文 | 去除导航 |
| **纯文本 (.txt)** | ✅ 基础支持 | 需额外处理 |
| **图片 (.png/.jpg)** | ⚠️ 需要 OCR | 额外成本 |
| **扫描 PDF** | ⚠️ 需要 OCR | 额外成本 |

### 2.2 文档质量检查清单

```yaml
检查项:
  内容质量:
    - [ ] 内容是否准确无误
    - [ ] 专业术语是否一致
    - [ ] 是否有错别字或语法错误
    - [ ] 重要信息是否完整
    
  格式规范:
    - [ ] 标题层级是否清晰
    - [ ] 列表编号是否一致
    - [ ] 表格是否有表头
    - [ ] 图片是否有 alt 文字
    
  结构完整:
    - [ ] 是否有目录结构
    - [ ] 章节划分是否合理
    - [ ] 是否有关键词索引
    - [ ] 是否有 FAQ 附录
```

---

## 三、切片策略

### 3.1 切片模式对比

| 模式 | 原理 | 适用场景 | 优缺点 |
|------|------|---------|--------|
| **固定长度** | 按 token 数切分 | 通用场景 | 简单但可能切断语义 |
| **段落切分** | 按自然段落切分 | 结构化文档 | 保留语义但长度不均 |
| **递归切分** | 按层级结构递归切分 | Markdown/HTML | 平衡效果较好 |
| **语义切分** | 按语义相似度切分 | 复杂文档 | 效果好但成本高 |
| **标题切分** | 按标题层级切分 | 规范/手册 | 保持章节完整 |

### 3.2 推荐切片参数

| 文档类型 | 切片大小 | 重叠大小 | 模式 |
|---------|---------|---------|------|
| **FAQ/问答** | 200-300 | 50 | 固定长度 |
| **产品手册** | 500 | 100 | 递归切分 |
| **合同文档** | 1000 | 200 | 段落切分 |
| **培训资料** | 800 | 150 | 标题切分 |
| **技术文档** | 600 | 100 | 递归切分 |

### 3.3 切片代码示例

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 递归切分器配置
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,           # 切片大小（token）
    chunk_overlap=100,        # 重叠大小
    separators=[
        "\n\n",             # 段落分隔
        "\n",               # 行分隔
        "。",               # 中文句号
        "！",               # 中文感叹号
        "？",               # 中文问号
        "；",               # 中文分号
        "，",               # 中文逗号
        " ",                # 英文空格
        ""                  # 字符级别
    ],
    length_function=len       # 或使用 tiktoken 计算 token
)

# 执行切片
chunks = text_splitter.split_documents(documents)

# 添加元数据
for i, chunk in enumerate(chunks):
    chunk.metadata.update({
        "chunk_id": i,
        "source": chunk.metadata.get("source", ""),
        "chapter": extract_chapter(chunk.metadata),
        "keywords": extract_keywords(chunk.page_content)
    })
```

---

## 四、嵌入模型选择

### 4.1 嵌入模型对比

| 模型 | 维度 | 特点 | 适用场景 |
|------|------|------|---------|
| **text-embedding-ada-002** | 1536 | OpenAI 官方，稳定 | 通用场景 |
| **text-embedding-3-small** | 512/1536 | 新版，性价比高 | 通用场景 |
| **text-embedding-3-large** | 256/1024/3072 | 新版，效果好 | 高精度场景 |
| **bge-large-zh** | 1024 | 中文优化，开源 | 中文场景 |
| **m3e-large** | 1024 | 中文优化，开源 | 中文场景 |
| **Jina embeddings** | 1024 | 多语言支持 | 多语言场景 |

### 4.2 中文场景推荐

```yaml
推荐配置:
  基础版:
    模型: bge-large-zh-v1.5
    维度: 1024
    成本: 开源免费
    说明: 中文效果好，兼容 FastGPT/Dify
    
  进阶版:
    模型: text-embedding-3-small
    维度: 1536
    成本: $0.02/1M tokens
    说明: 效果好，成本适中
    
  高端版:
    模型: text-embedding-3-large
    维度: 3072
    成本: $0.13/1M tokens
    说明: 效果最佳，成本较高
```

---

## 五、检索优化

### 5.1 检索模式

| 模式 | 原理 | 适用场景 |
|------|------|---------|
| **向量检索** | 语义相似度匹配 | 语义相关查询 |
| **关键词检索** | BM25/TF-IDF | 精确关键词匹配 |
| **混合检索** | 向量+关键词融合 | 平衡精度和召回 |
| **重排序** | 两阶段检索后重排 | 提升准确性 |

### 5.2 混合检索配置

```yaml
检索配置:
  向量检索:
    top_k: 5
    similarity_threshold: 0.5
    
  关键词检索:
    top_k: 5
    keyword_weight: 0.3
    
  融合策略:
    method: reciprocal_rank_fusion  # RRF 融合
    scores:
      vector: 0.7
      keyword: 0.3
      
  重排序:
    启用: true
    模型: bge-reranker-base
    top_n: 3
```

### 5.3 检索代码示例

```python
# 混合检索实现
def hybrid_search(query, vector_db, keyword_db, top_k=5):
    # 向量检索
    vector_results = vector_db.similarity_search_with_score(
        query, k=top_k
    )
    
    # 关键词检索
    keyword_results = keyword_db.search(query, k=top_k)
    
    # RRF 融合
    fused_scores = {}
    for rank, (doc, score) in enumerate(vector_results):
        doc_id = doc.metadata["id"]
        fused_scores[doc_id] = fused_scores.get(doc_id, 0) + 1 / (60 + rank)
        
    for rank, (doc, score) in enumerate(keyword_results):
        doc_id = doc.metadata["id"]
        fused_scores[doc_id] = fused_scores.get(doc_id, 0) + 1 / (60 + rank)
    
    # 返回融合结果
    sorted_results = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_results[:top_k]
```

---

## 六、效果评估

### 6.1 评估指标

| 指标 | 含义 | 计算方式 | 目标值 |
|------|------|---------|--------|
| **Precision@K** | 前K结果准确率 | 正确结果数/K | >0.8 |
| **Recall@K** | 前K结果召回率 | 召回结果数/总结果数 | >0.7 |
| **MRR** | 平均倒数排名 | 第一个正确结果的倒数平均 | >0.6 |
| **NDCG** | 归一化折扣收益 | 考虑位置加权的相关性 | >0.6 |

### 6.2 评估数据集

```yaml
评估数据集格式:
  questions:
    - q: "产品A的保修期是多久？"
      answer: "产品A的保修期为2年"
      relevant_docs:
        - doc_id: "manual_v1_p50"
        - page: 50
        
    - q: "如何申请退换货？"
      answer: "7天内可申请退换货，需要联系客服"
      relevant_docs:
        - doc_id: "policy_p10"
        - page: 10
```

### 6.3 评估代码

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall

# 评估配置
metrics = [
    faithfulness,           # 忠实度：答案是否基于上下文
    answer_relevancy,      # 答案相关性
    context_precision,     # 上下文精确度
    context_recall         # 上下文召回率
]

# 执行评估
result = evaluate(
    dataset=eval_dataset,
    metrics=metrics
)

print(result)
```

---

## 七、行业知识库模板

### 7.1 律所知识库

```yaml
文档类型:
  - 合同模板: docx/pdf
  - 法律法规: 法规文本
  - 案例分析: pdf/word
  - 业务指引: markdown

切片策略:
  合同模板:
    模式: 标题切分
    切片大小: 按章节
    元数据: 合同类型、签署方、金额范围
    
  法律法规:
    模式: 固定长度
    切片大小: 1000
    元数据: 法律名称、条款编号、修订日期
    
  案例分析:
    模式: 段落切分
    切片大小: 按自然段落
    元数据: 案件类型、法院、判决年份

推荐模型:
  嵌入: bge-large-zh-v1.5
  重排: bge-reranker-base
```

### 7.2 制造业知识库

```yaml
文档类型:
  - 设备手册: pdf
  - 工艺规程: word/pdf
  - 质量标准: excel/pdf
  - 维修记录: structured data

切片策略:
  设备手册:
    模式: 标题+段落
    切片大小: 800
    元数据: 设备型号、制造商、版本
    
  工艺规程:
    模式: 步骤切分
    切片大小: 按工序
    元数据: 产品类型、工序编号、安全等级
    
检索优化:
  启用: true
  配置:
    vector_weight: 0.6
    keyword_weight: 0.4
    rerank: true
```

---

## 八、知识库健康检查

```yaml
健康检查清单:
  文档层面:
    - [ ] 文档数量充足（>100篇/场景）
    - [ ] 内容覆盖度>80%
    - [ ] 无重复或低质量文档
    - [ ] 元数据完整
    
  切片层面:
    - [ ] 平均切片长度合理（400-800）
    - [ ] 切片重叠度适中（10-20%）
    - [ ] 边界切在语义完整处
    
  检索层面:
    - [ ] 常见问题能检索到
    - [ ] 模糊查询能返回结果
    - [ ] 无明显bad case
    
  效果层面:
    - [ ] Precision@3 > 0.8
    - [ ] 用户满意度 > 80%
    - [ ] 无高优先级投诉
```

---

## 九、下游使用建议

### 9.1 FastGPT 配置

```yaml
fastgpt:
  知识库配置:
    vector_store: pgvector
    embedding_model: bge-large-zh-v1.5
    rerank_model: bge-reranker-base
    
  检索参数:
    limit: 5
    similarity: 0.5
    usingSearch: true
    searchMode: hybrid
    
  回答参数:
    systemPrompt: |
      你是一个专业的知识库助手。请根据提供的参考信息回答用户问题。
      如果参考信息不足以回答，请明确告知。
```

### 9.2 Dify 配置

```yaml
dify:
  知识检索节点:
    dataset_id: ${DATASET_ID}
    retrieval_model:
      type: hybrid_search
      top_k: 5
      similarity_threshold: 0.5
      vector_weight: 0.7
      weighted_score:
        vector: 0.7
        keyword: 0.3
        
  Rerank 节点:
    model: bge-reranker-base
    top_n: 3
```

---

*本文档配套：[[fastgpt-deploy]] [[dify-deploy]]*
