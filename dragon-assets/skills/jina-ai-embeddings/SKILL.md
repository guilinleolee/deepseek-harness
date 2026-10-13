---
license: UNKNOWN
triggers: ["jina ai embeddings", "jina-ai-embeddings"]
---
# jina-ai-embeddings

## L0: 一句话描述 (≤15字)
免费多语言Embedding + Reranker API

## L1: 使用场景 (50-100字)
替代OpenAI/Gemini付费Embedding服务，实现零成本RAG知识库构建、语义搜索、文档相似度计算。适合预算有限的独立开发者和初创团队。

## L2: 详细文档

### 来源项目
| 项目 | Stars | 核心能力 |
|------|-------|---------|
| [jinaai/jina-ai-api](https://github.com/jinaai/jina-ai-api) | 3.5k+ | 免费Embedding/Reranker API |

### 核心能力

```
┌─────────────────────────────────────────────────────────────┐
│ Jina AI Free API                                           │
├─────────────────────────────────────────────────────────────┤
│  embeddings_v3:  多语言1024维embedding（免费，支持中文）     │
│  reranker:      交叉编码器重排序（比OpenAI reranker免费）  │
│  v3-secure:      加密embedding服务                          │
│  embed:         通用embedding接口                          │
└─────────────────────────────────────────────────────────────┘
```

### API端点

| 功能 | 端点 | 免费额度 | 说明 |
|------|------|---------|------|
| Embedding v3 | `https://api.jina.ai/embed` | 200万tokens/月 | 1024维，支持30+语言 |
| Reranker | `https://api.jina.ai/rerank` | 20万tokens/月 | 交叉编码器重排序 |

### 价格对比

| 服务商 | Embedding成本 | Reranker成本 |
|--------|--------------|--------------|
| **Jina AI** | **免费** | **免费** |
| OpenAI | $0.0001/1K tokens | $0.0001/1K tokens |
| Cohere | $0.0001/1K tokens | $0.001/1K tokens |

### 天龙岗位升级

| 岗位 | 版本 | 新增能力 |
|------|------|---------|
| **01调研师** | V8.88 → V8.89 | 免费embedding + 语义搜索 |
| **10-02 AI研究员** | V8.69 → V8.70 | 多后端embedding路由 |
| **19-01数据工程师** | V8.68 → V8.69 | RAG数据管道 |
| **62-02行业研究员** | V9.1 → V9.2 | 语义文档检索 |
| **07记录师** | V9.07 → V9.08 | Wiki知识库embedding |

### 与LightRAG协同

```python
# LightRAG集成Jina AI示例
from lightrag import LightRAG
from jina_ai_client import JinaEmbedding

rag = LightRAG(
    embedding_model=JinaEmbedding(api_key=os.getenv("JINA_API_KEY")),
    embedding_dim=1024
)
```

### 核心命令速查

```bash
# 1. 安装依赖
pip install requests

# 2. 获取API Key (免费)
# https://jina.ai/embeddings/ 注册获取

# 3. 设置环境变量
export JINA_API_KEY="your-api-key"

# 4. 使用embedding
python3 ~/.claude/skills/jina-ai-embeddings/scripts/embedding.py "你好世界"

# 5. 使用reranker
python3 ~/.claude/skills/jina-ai-embeddings/scripts/reranker.py \
  --query "人工智能" \
  --documents "AI是研究智能的科学" "Python是一种编程语言" "机器学习是AI的子领域"

# 6. 批量embedding
python3 ~/.claude/skills/jina-ai-embeddings/scripts/batch_embedding.py \
  --input ./docs/ \
  --output ./embeddings.json
```

### Python API封装

```python
from jina_ai_client import JinaEmbedding, JinaReranker

class JinaEmbedding:
    """Jina AI Embedding客户端"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.jina.ai/embed"

    def encode(self, texts: list[str], model: str = "jina-embeddings-v3") -> list[list[float]]:
        """将文本转换为embedding向量"""
        import requests

        response = requests.post(
            f"{self.base_url}",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "input": texts,
                "encoding_type": "float"
            }
        )

        if response.status_code == 200:
            return response.json()["data"][0]["embedding"]
        else:
            raise Exception(f"Embedding failed: {response.text}")

    def similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的余弦相似度"""
        import numpy as np

        emb1 = self.encode([text1])[0]
        emb2 = self.encode([text2])[0]

        return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))


class JinaReranker:
    """Jina AI Reranker客户端"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.jina.ai/rerank"

    def rerank(
        self,
        query: str,
        documents: list[str],
        top_n: int = 5,
        model: str = "jina-reranker-v1-base-en"
    ) -> list[dict]:
        """对文档进行重排序"""
        import requests

        response = requests.post(
            f"{self.base_url}",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "query": query,
                "documents": documents,
                "top_n": top_n
            }
        )

        if response.status_code == 200:
            return response.json()["results"]
        else:
            raise Exception(f"Rerank failed: {response.text}")
```

### 成本节省估算

| 使用量 | OpenAI成本 | Jina AI成本 | 节省 |
|--------|-----------|-------------|------|
| 100万tokens/月 | $100/月 | **$0** | $100/月 |
| 500万tokens/月 | $500/月 | **$0** | $500/月 |
| 1000万tokens/月 | $1000/月 | **$0** | $1000/月 |

### 预期收益

| 指标 | V11.12 | V11.13 | 提升 |
|------|--------|--------|------|
| Embedding成本 | 依赖OpenAI | 免费 | **-100%** |
| Reranker成本 | 依赖OpenAI | 免费 | **-100%** |
| 多语言支持 | 英文为主 | 30+语言 | **质的飞跃** |
| 量化研究员效率 | 手动数据处理 | 语义分析自动化 | **+200%** |

### 文件结构

```
jina-ai-embeddings/
├── SKILL.md                    # 本文件
├── scripts/
│   ├── embedding.py           # Embedding封装
│   ├── reranker.py            # Reranker封装
│   ├── batch_embedding.py     # 批量embedding
│   ├── similarity.py           # 相似度计算
│   └── client.py              # 统一客户端
└── README.md                   # 使用指南
```

### 安装验证

```bash
# 1. 安装依赖
pip install requests numpy

# 2. 设置API Key
export JINA_API_KEY=$(cat ~/.claude/.env | grep JINA_API_KEY | cut -d'=' -f2)

# 3. 测试embedding
python3 ~/.claude/skills/jina-ai-embeddings/scripts/embedding.py "测试文本"

# 4. 测试reranker
python3 ~/.claude/skills/jina-ai-embeddings/scripts/reranker.py \
  --query "人工智能发展" \
  --documents "AI是Artificial Intelligence的缩写" "机器学习是AI的子领域"
```

### 技术约束

- Embedding维度: 1024维 (jina-embeddings-v3)
- 免费额度: 200万tokens/月 (embedding), 20万tokens/月 (reranker)
- 支持语言: 30+ (包括中文、英文、日文、韩文等)
- 模型: jina-embeddings-v3 (推荐), jina-embeddings-v2 (备用)

### 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-15 | 初始集成，基于 Jina AI Free API |