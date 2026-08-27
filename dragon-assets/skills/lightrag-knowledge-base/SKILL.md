---
license: UNKNOWN
github_repo: HKUDS/LightRAG
github_hash: 6c85f26d21cef93936f2d97d7010227d3ba56542
last_updated: 2026-04-25
source_type: derived
triggers: ["lightrag knowledge base", "LightRAG Knowledge Base Skill"]
---
# LightRAG Knowledge Base Skill

## Overview

LightRAG is a lightweight, efficient Retrieval-Augmented Generation system from HKUDS (EMNLP 2025). Core innovation: **Dual-Level Retrieval** combining local text chunks + global knowledge graph.

## Performance Benchmarks

| Dataset | NaiveRAG | LightRAG | Improvement |
|---------|----------|----------|-------------|
| Agriculture | 32.4% | 67.6% | +109% |
| CS | 38.8% | 61.2% | +58% |
| Legal | 15.2% | 84.8% | +458% |
| Mix | 40.0% | 60.0% | +50% |

## Core Capabilities

### 1. Dual-Level Retrieval

| Mode | Description | Best For |
|------|-------------|----------|
| **local** | Text chunk similarity search | Specific facts, details |
| **global** | Knowledge graph traversal | Relationships, overview |
| **hybrid** | Local + Global combined | Balanced queries |
| **mix** | Graph + Vector + Reranker | Best quality (default) |

### 2. Knowledge Graph Extraction

- Automatic entity and relationship extraction
- Support incremental updates (add/delete documents)
- Auto-reconstruct KG on changes

### 3. Storage Backends

| Type | Supported Backends |
|------|-------------------|
| **KV Store** | JsonKV, PGKV, Redis, MongoDB, OpenSearch |
| **Vector Store** | NanoVector, PGVector, Milvus, Chroma, Faiss, Qdrant |
| **Graph Store** | NetworkX, Neo4J, PGGraph, AGE |

### 4. Multimodal Support

- Video processing (via RAG-Anything)
- Image analysis
- Audio transcription

## Installation

```bash
# Basic installation
pip install "lightrag-hku"

# With API support
pip install "lightrag-hku[api]"

# Full installation
pip install "lightrag-hku[api,webui]"
```

## Commands

### Initialize Knowledge Base

```bash
/lightrag-init --working-dir ./rag_storage --backend postgresql
```

### Insert Documents

```bash
# Single file
/lightrag-insert --file ./doc.md

# Directory
/lightrag-insert --dir ./docs/ --mode hybrid

# With chunking config
/lightrag-insert --dir ./docs/ --chunk-size 1200 --overlap 100
```

### Query

```bash
# Basic query
/lightrag-query "What is the architecture?"

# With mode
/lightrag-query "What is the architecture?" --mode hybrid

# Stream output
/lightrag-query "Explain the system" --stream

# Only context (no generation)
/lightrag-query "Find related info" --only-context
```

### Incremental Update

```bash
# Add documents
/lightrag-update --add ./new_docs/

# Remove documents
/lightrag-update --remove ./old_docs/

# Replace
/lightrag-update --replace ./old_doc.md ./new_doc.md
```

### Knowledge Graph

```bash
# Visualize KG
/lightrag-kg --output kg.html

# Export KG
/lightrag-kg --export graph.json

# Import KG
/lightrag-kg --import graph.json
```

## Python API

```python
from lightrag import LightRAG, QueryParam

# Initialize
rag = LightRAG(working_dir="./rag_storage")
await rag.initialize_storages()

# Insert documents
await rag.ainsert("Your document text here")

# Query
result = await rag.aquery(
    "Your question",
    param=QueryParam(mode="hybrid")
)

# Stream query
async for chunk in rag.aquery_stream("Your question"):
    print(chunk, end="")

# Incremental update
await rag.ainsert("New document")
await rag.adelete_by_ids(["doc_id"])
```

## Configuration

```yaml
# config.yaml
working_dir: ./rag_storage

# LLM Settings
llm:
  model: qwen3-30b-a3b  # Recommended >= 32B
  context_window: 64000  # Recommended >= 32KB

# Embedding Settings
embedding:
  model: BAAI/bge-m3
  dimension: 1024

# Reranker Settings
reranker:
  enabled: true
  model: BAAI/bge-reranker-v2-m3

# Chunking Settings
chunk:
  size: 1200
  overlap: 100

# Storage Backends
storage:
  kv: postgresql
  vector: pgvector
  graph: neo4j
```

## Dragon Engine Integration

### Agent Usage

```bash
# 01 Investigator - Research with LightRAG
[@Investigator] Use lightrag to research this technical domain

# 07 Scribe - Build knowledge base
[@Scribe] Build project knowledge base using lightrag

# 19-01 Data Engineer - RAG pipeline
[@Data Engineer] Set up lightrag data pipeline

# 10-02 AI Researcher - RAG research
[@AI Researcher] Research RAG systems using lightrag
```

### Synergy with Existing Skills

| Skill | Integration |
|-------|-------------|
| **graph-rag-builder** | LightRAG replaces underlying implementation |
| **enterprise-docs-search** | LightRAG enhances retrieval |
| **deep-research** | LightRAG as Step 3 retrieval engine |
| **claude-mem** | LightRAG enhances memory retrieval |
| **source-verifier** | KG + source verification |

## Best Practices

### 1. Chunking Strategy

- Default: 1200 tokens, 100 overlap
- Technical docs: 800 tokens for precision
- Long articles: 1500 tokens for context

### 2. Query Mode Selection

| Query Type | Recommended Mode |
|------------|------------------|
| "What is X?" | local |
| "How does X relate to Y?" | global |
| "Explain X in detail" | hybrid |
| "Compare X and Y" | mix |

### 3. Model Selection

| Use Case | Recommended Model |
|----------|------------------|
| Production | Qwen3-30B-A3B |
| Fast iteration | GPT-4o-mini |
| Local | Ollama with Qwen2.5 |

### 4. Storage Selection

| Scale | Recommended Backend |
|-------|---------------------|
| <10K docs | JsonKV + NanoVector + NetworkX |
| 10K-1M docs | PostgreSQL + PGVector + Neo4J |
| >1M docs | OpenSearch + Milvus + Neo4J |

## Troubleshooting

### Common Issues

1. **`__aenter__` error**: Call `await rag.initialize_storages()` first
2. **Slow queries**: Enable reranker, use hybrid mode
3. **Memory issues**: Reduce chunk size, use external storage

### Performance Tuning

```yaml
# For better accuracy
chunk:
  size: 800
  overlap: 150

reranker:
  enabled: true

# For faster queries
query:
  top_k: 10  # Reduce from default 60
```

## References

- [GitHub](https://github.com/HKUDS/LightRAG)
- [Paper](https://arxiv.org/abs/2410.05779) (EMNLP 2025)
- [Documentation](https://github.com/HKUDS/LightRAG/wiki)