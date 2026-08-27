---
name: llamaindex-rag
description: LlamaIndex RAG CLI - 知识库创建/检索/管理/同步Obsidian
invokable: true
---
# /llamaindex-rag

基于 LlamaIndex 的知识库构建与检索 CLI 工具。

## 命令

```bash
D:/Python310/python.exe c:/Users/li/.claude/skills/llamaindex-rag/scripts/llamaindex_rag_cli.py <command> [args]
```

## 子命令

| 命令 | 功能 | 示例 |
|------|------|------|
| `create` | 创建知识库 | `create --name my_kb --persist-dir ./kb_data` |
| `add` | 添加文档 | `add --kb-name my_kb --files ./docs/*.md` |
| `list` | 列出知识库 | `list` |
| `info` | 知识库信息 | `info --kb-name my_kb` |
| `delete` | 删除知识库 | `delete --kb-name my_kb` |
| `query` | 检索查询 | `query --kb-name my_kb "查询内容"` |
| `export` | 导出结果 | `export --kb-name my_kb --query "x" --format json` |
| `sync-obsidian` | 同步Obsidian | `sync-obsidian --vault-path ./vault --kb-name my_kb` |

## 天龙引擎调用

```bash
[@07记录师] 用llamaindex-rag创建项目知识库并导入文档
[@01调研师] 用llamaindex-rag检索关于"注意力机制"的技术文档
[@19-01] 用llamaindex-rag同步Obsidian笔记到知识库
```

## 依赖

```bash
pip install llama-index llama-index-llms-openai llama-index-vector-stores-chroma
```
