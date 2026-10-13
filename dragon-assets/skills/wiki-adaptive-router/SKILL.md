---
license: UNKNOWN
triggers: ["wiki adaptive router", "Wiki 自适应检索路由"]
---
# Wiki 自适应检索路由

基于知识库规模和内容特征，智能路由检索请求到最优检索引擎，实现 Karpathy LLM Wiki Pattern 的规模感知检索策略。

## 核心原理

Karpathy 提出的 LLM Wiki Pattern 核心理念：**个人规模不需要向量数据库**。根据知识库规模自动选择检索策略：

| 规模 | 笔记数量 | 检索策略 |
|------|----------|-----------|
| 个人级 | <100 | 直接读取（full-scan） |
| 团队级 | 100-1000 | 标题 grep 过滤 |
| 企业级 | >1000 | LightRAG 向量检索 |

## 功能

- **规模感知路由**：根据笔记总数自动选择检索策略
- **内容特征检测**：识别笔记类型（技术/概念/经验/参考）
- **多策略融合**：支持 full-scan / grep / vector 三层检索
- **性能预算**：根据检索时间预算自动降级
- **结果聚合**：合并多策略结果，按相关性排序

## 目录结构

```
wiki-adaptive-router/
├── SKILL.md                      # 本文件
├── prompts/
│   └── routing_prompt.md         # 路由决策提示词
└── scripts/
    ├── router.py                 # 核心路由逻辑
    └── cache.py                  # 检索缓存
```

## 检索策略详解

### 1. Full-Scan（个人级）

适用于 <100 篇笔记的知识库。

```python
# 直接读取所有笔记，按关键词过滤
for note in wiki_dir.glob("*.md"):
    content = note.read_text()
    if query in content.lower():
        results.append(note)
```

**优势**：
- 零延迟（无索引开销）
- 完整上下文（无 chunk 截断）
- 无向量模型依赖

**适用场景**：
- 个人笔记库
- 主题集中（<10 个领域）
- 检索频率低（<10次/天）

### 2. Grep-Scan（团队级）

适用于 100-1000 篇笔记的知识库。

```python
# 标题索引 + 内容 grep 两阶段
title_index = {note.stem: note for note in wiki_dir.glob("*.md")}

# 阶段1：标题匹配
candidates = [title_index[k] for k in title_index if query.lower() in k.lower()]

# 阶段2：内容 grep
for note in candidates:
    if query in note.read_text().lower():
        results.append(note)
```

**优势**：
- O(√n) 复杂度（标题索引减少扫描范围）
- 保留完整笔记（无 chunk 截断）
- 支持正则表达式

**适用场景**：
- 团队知识库
- 主题分散（10-50 个领域）
- 中等检索频率（10-100次/天）

### 3. Vector-Search（企业级）

适用于 >1000 篇笔记的知识库。

```python
# 使用 LightRAG 进行语义向量检索
from lightrag import LightRAG

rag = LightRAG(working_dir="./lightrag_cache")
results = rag.query(query, mode="hybrid")  # local + global
```

**优势**：
- O(1) 语义匹配（向量最近邻）
- 跨领域关联发现
- 支持复杂查询

**适用场景**：
- 企业知识库
- 主题极分散（>50 个领域）
- 高检索频率（>100次/天）

## 使用方法

### 基本检索

```bash
# 自动选择最优检索策略
python3 ~/.claude/skills/wiki-adaptive-router/scripts/router.py query "微服务架构"

# 指定检索策略（覆盖自动选择）
python3 ~/.claude/skills/wiki-adaptive-router/scripts/router.py query "微服务" --strategy full-scan
```

### 批量检索

```bash
# 批量查询
python3 ~/.claude/skills/wiki-adaptive-router/scripts/router.py batch queries.txt

# 带时间预算
python3 ~/.claude/skills/wiki-adaptive-router/scripts/router.py query "微服务" --budget 2000
```

### 缓存管理

```bash
# 查看缓存状态
python3 ~/.claude/skills/wiki-adaptive-router/scripts/cache.py status

# 清理过期缓存
python3 ~/.claude/skills/wiki-adaptive-router/scripts/cache.py clean --older 7d

# 预热缓存
python3 ~/.claude/skills/wiki-adaptive-router/scripts/cache.py warm --queries recent.txt
```

## 路由决策流程

```
┌─────────────────────────────────────────────────────────────┐
│                    检索请求进入                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 1: 规模评估                                           │
│ - 统计笔记总数                                             │
│ - 检测索引是否存在                                         │
│ - 计算覆盖度                                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 2: 策略选择                                           │
│ - <100 → full-scan                                        │
│ - 100-1000 → grep-scan                                    │
│ - >1000 → vector-search                                    │
│ - 缓存命中 → 直接返回                                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 3: 执行检索                                           │
│ - 调用对应检索引擎                                         │
│ - 设置超时保护                                             │
│ - 记录性能指标                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 4: 结果聚合                                           │
│ - 去重（相同笔记）                                        │
│ - 排序（相关性/时间/复利值）                              │
│ - 截断（按 top_k 参数）                                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 5: 缓存更新                                           │
│ - 写入查询缓存                                             │
│ - 更新热点统计                                             │
│ - 清理过期条目                                             │
└─────────────────────────────────────────────────────────────┘
```

## 性能指标

| 策略 | 平均延迟 | P95延迟 | 吞吐量 |
|------|----------|---------|--------|
| full-scan | 5ms | 15ms | 10K/day |
| grep-scan | 50ms | 200ms | 50K/day |
| vector-search | 200ms | 500ms | 100K/day |

## 配置参数

```json
{
  "router": {
    "thresholds": {
      "full_scan_max": 100,
      "grep_scan_max": 1000
    },
    "budget_ms": 3000,
    "cache_ttl_hours": 24,
    "top_k": 10
  }
}
```

## 与 Wiki-MemPalace 桥接集成

```python
from wiki_mempalace_bridge.scripts.auto_sync import WikiMemPalaceBridge

bridge = WikiMemPalaceBridge()

# 检索结果自动映射到 MemPalace 房间
results = router.query("微服务架构")
for note in results:
    mapping = bridge.get_mapping(note.note_id)
    print(f"{note.title} → {mapping.room}")
```

## 适用场景

- 个人 Wiki 知识库（<100 篇）
- 团队 Wiki 知识库（100-1000 篇）
- 企业 Wiki 知识库（>1000 篇）
- 混合检索（MemPalace + Wiki）
- 检索性能优化
- 冷启动知识库
