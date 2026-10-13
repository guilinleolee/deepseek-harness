---
license: UNKNOWN
github_repo: thedotmack/claude-mem
github_hash: 8ace1d9c84e5ce455356cf852c370ea625e3b1d1
last_updated: 2026-04-25
source_type: derived
triggers: ["claude mem", "Claude-Mem - 持久化记忆系统"]
---
# Claude-Mem - 持久化记忆系统

## 概述

Claude-Mem是一个持久化记忆压缩系统，实现会话间知识不丢失。与LightRAG协同，提供双层记忆检索能力。

## 核心能力

### 双层记忆架构

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: LightRAG知识库（大规模知识存储）                    │
│   - 自动知识图谱构建                                         │
│   - 双层级检索（local/global/hybrid/mix）                   │
│   - 增量更新                                                 │
│   - 适合：代码仓库、文档库、知识库                           │
├─────────────────────────────────────────────────────────────┤
│ Layer 1: claude-mem（会话记忆）                              │
│   - 自动捕获 + AI压缩                                        │
│   - ChromaDB向量存储                                         │
│   - RAG检索                                                  │
│   - 适合：日常对话、临时笔记                                 │
└─────────────────────────────────────────────────────────────┘
```

### 五大生命周期钩子

| 钩子 | 触发时机 | 功能 |
|------|---------|------|
| **SessionStart** | 会话开始 | 加载历史记忆上下文 |
| **PostToolUse** | 工具调用后 | 捕获工具输出 |
| **Stop** | 用户停止 | 保存会话状态 |
| **SessionEnd** | 会话结束 | 压缩并存储记忆 |
| **PreResponse** | 响应前 | 注入相关记忆 |

## 🆕 V1.1 新特性：LightRAG双层检索协同

### 核心价值
LightRAG的**双层级检索**能力增强记忆系统，提供更深层次的知识发现和关联。

### 双层检索协同

```
┌─────────────────────────────────────────────────────────────┐
│ 记忆检索流程                                                 │
│                                                              │
│   1. 会话记忆查询（claude-mem）                               │
│      → ChromaDB向量相似性搜索                                │
│      → 快速、轻量、近期上下文                                │
│                                                              │
│   2. 知识库深度查询（LightRAG）                               │
│      → local模式：文本块相似性搜索                           │
│      → global模式：知识图谱遍历                              │
│      → mix模式：图 + 向量 + 重排序                           │
│      → 深度、全面、历史知识                                  │
│                                                              │
│   3. 结果融合                                                │
│      → 会话记忆优先（时效性高）                              │
│      → 知识库补充（深度全面）                                │
└─────────────────────────────────────────────────────────────┘
```

### 能力对比与协同

| 能力维度 | claude-mem | LightRAG | 协同效果 |
|---------|-----------|----------|---------|
| **会话记忆** | ✅ 自动捕获 | - | 核心能力 |
| **向量检索** | ✅ ChromaDB | ✅ 多后端 | 双层检索 |
| **知识图谱** | ❌ 无 | ✅ 自动构建 | **新增能力** |
| **双层检索** | ❌ 单层 | ✅ 四模式 | **质的飞跃** |
| **增量更新** | ✅ 自动 | ✅ 自动 | 双层更新 |

### 协同工作流

```bash
# 1. 会话记忆检索（claude-mem）
curl http://localhost:37777/api/search?q="之前的讨论"

# 2. 知识库深度检索（LightRAG）
python ~/.claude/skills/lightrag-knowledge-base/scripts/lightrag_query.py "相关历史知识" --mode mix

# 3. 知识图谱遍历（LightRAG global模式）
python ~/.claude/skills/lightrag-knowledge-base/scripts/lightrag_query.py "概念关联关系" --mode global
```

### 3层Token高效工作流

```
Layer 1: search()      ─── 获取紧凑索引（~50-100 tokens/result）
    │
    ▼
Layer 2: timeline()    ─── 获取时间线上下文
    │
    ▼
Layer 3: get_observations() ─── 获取完整详情（~500-1000 tokens/result）

收益: ~10x Token节省（先过滤再获取详情）
```

### CLI命令速查

```bash
# 记忆管理
/remember [query]       # 搜索历史记忆
/timeline [id]          # 获取时间线上下文
/memory-stats           # 查看记忆统计

# LightRAG协同
/lightrag-query "知识库查询" --mode mix
/lightrag-query "关联分析" --mode global
```

## Web UI

访问地址：http://localhost:37777

功能：
- 记忆可视化
- 时间线浏览
- 搜索界面
- 统计分析

## 预期收益

| 指标 | V1.0 | V1.1 + LightRAG | 提升 |
|------|------|-----------------|------|
| **知识留存率** | +300% | **+600%** | 翻倍 |
| **记忆检索深度** | 单层 | **双层** | 质的飞跃 |
| **关联发现** | 无 | **自动** | 质的飞跃 |
| **Token效率** | +60% | **+120%** | 翻倍 |

## 文件结构

```
skills/claude-mem/
├── SKILL.md                    # 本文档
└── (与thedotmack/claude-mem集成)

~/.claude-mem/
├── memories.db                 # SQLite数据库
├── chroma/                     # ChromaDB向量存储
└── config.json                 # 配置文件
```

## 来源

- 原项目: [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem)
- Stars: 33.5k+
- 天龙版本: V8.6
- LightRAG协同: V8.55 (2026-03-27)