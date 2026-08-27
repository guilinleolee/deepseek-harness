---
license: UNKNOWN
triggers: ["gbrain hybrid search", "GBrain Hybrid Search"]
---
# GBrain Hybrid Search
# 混合检索引擎 — 三层查询 + 引用溯源

## L0: 一句话描述
三层检索架构（关键词→混合语义→结构化查询），确保每条信息可溯源至原始来源。

## L1: 使用场景

### 核心触发场景
- **问题驱动查询**: 当需要回答"关于X我们知道什么"时
- **实体探索**: 当询问"谁是谁"或"发生了什么"时
- **关系追踪**: 当需要追溯人与人、公司与事件的关系时
- **时序重建**: 当需要按时间线梳理事件发展时

### 天龙九部适用
- **00分析师**: 决策前检索相关知识基础
- **01调研师**: 研究前检查已有知识，避免重复
- **02架构师**: 架构设计参考历史决策记录
- **07记录师**: 归档前检索相关已有知识，建立关联

## L2: 详细文档

### 核心能力

GBrain Hybrid Search 实现**三层检索架构**，确保信息完整性：

```
┌─────────────────────────────────────────────────────────────┐
│           GBrain Hybrid Search 三层检索架构                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Layer 1: 关键词检索 (search)                              │
│  ├── 快速关键词匹配                                        │
│  ├── 适用: 具体术语、数字、日期搜索                         │
│  └── 场景: "查找包含'微服务'的知识"                        │
│                                                             │
│  Layer 2: 混合检索 (query) ⭐核心                         │
│  ├── 语义 + 关键词双重匹配                                  │
│  ├── 适用: 自然语言问题、概念理解                           │
│  └── 场景: "用户认证最佳实践是什么"                        │
│                                                             │
│  Layer 3: 结构化查询 (structured)                          │
│  ├── 回链查询 (backlinks): 谁引用了这个实体                 │
│  ├── 时间线 (timeline): 实体的时间发展                     │
│  └── 图遍历 (graph): 关系网络探索                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 引用溯源铁律

每条输出必须包含来源追溯：

```markdown
**关键发现**: [结论]
**来源**: [page_slug] (置信度: 0.8)
**溯源链**: [主来源] → [支撑来源] → [原始来源]
```

当知识不存在时，明确标注：
> "当前知识库中**没有**关于[实体]的信息" — 而非虚构

### CLI 命令

```bash
# Layer 1: 关键词检索
python ~/.claude/skills/gbrain-hybrid-search/scripts/hybrid_search.py search "微服务架构"

# Layer 2: 混合检索（推荐）
python ~/.claude/skills/gbrain-hybrid-search/scripts/hybrid_search.py query "用户认证最佳实践"
python ~/.claude/skills/gbrain-hybrid-search/scripts/hybrid_search.py query "谁提到了LangGraph" --confidence 0.6

# Layer 3: 结构化查询
python ~/.claude/skills/gbrain-hybrid-search/scripts/hybrid_search.py backlinks "person/sarah-chen"
python ~/.claude/skills/gbrain-hybrid-search/scripts/hybrid_search.py timeline "company/openai" --range 90d
python ~/.claude/skills/gbrain-hybrid-search/scripts/hybrid_search.py graph "person/yann-lecun" --depth 2

# 综合查询（自动选择最优层）
python ~/.claude/skills/gbrain-hybrid-search/scripts/hybrid_search.py resolve "OpenAI最新动态"

# 列出所有页面
python ~/.claude/skills/gbrain-hybrid-search/scripts/hybrid_search.py list --topic "ai-agent"

# Token预算感知检索
python ~/.claude/skills/gbrain-hybrid-search/scripts/hybrid_search.py query "..." --budget 2000
```

### 检索配置文件

```yaml
# gbrain-hybrid-search/config.yaml

search:
  layers:
    - name: "keyword"
      threshold: 0.5
      max_results: 20
    - name: "hybrid"
      threshold: 0.6
      max_results: 10
      semantic_weight: 0.6
      keyword_weight: 0.4
    - name: "structured"
      threshold: 0.7
      max_results: 5

  citation:
    required: true
    format: "inline"  # inline | footnote | bracket
    confidence_threshold: 0.5

  synthesis:
    max_sources: 5
    conflict_resolution: "newest_wins"  # newest_wins | confidence_wins | manual
    hallucination_guard: true

  token_budget:
    search_chunk: 500     # 先用小Chunk预览
    full_page: 2000       # 确认需要时再加载完整页面
    synthesis: 1000      # 综合输出Token预算
```

### 天龙引擎集成配置

```yaml
# 天龙引擎集成
tianlong_integration:
  attached_role: "01-investigator"
  triggers:
    - "关于X我们知道什么"
    - "tell me about"
    - "who is"
    - "搜索"
    - "查找"
    - "查询"
  upstream:
    - gbrain-signal-detector
    - gbrain-multimodal-ingest
    - gbrain-daily-briefing
  downstream:
    - gbrain-entity-enrich     # 发现新实体后触发充实
    - gbrain-identity-audit      # 发现身份变更后触发审计

  # 天龙引擎上下文注入
  context_injection:
    agent_id: true
    conversation_id: true
    recent_entities: true       # 最近涉及的实体

  # 与九部协同
  collaboration:
    auto_link: true            # 自动建立双向链接
    cross_reference: true       # 跨领域交叉引用
    conflict_detection: true     # 矛盾检测
```

### 来源优先级

| 优先级 | 来源 | 说明 |
|--------|------|------|
| 1 | 用户直接陈述 | 用户明确表达的偏好、决策、历史 |
| 2 | 编译后的真相 | 经过整理的会议记录、决策文档 |
| 3 | 时间线事件 | 按时间排序的事实条目 |
| 4 | 外部来源 | 网页、文档等，需要标注`[Source: url]` |

### 检索结果格式

```markdown
## 检索结果: "[查询内容]"

**置信度**: 0.82 | **来源数**: 3 | **Token消耗**: 1850

### 关键发现

1. [来源: memory/architecture/microservices]
   **微服务网关选择**: 当前生产环境使用Kong，测试环境使用Tyk
   - 决策时间: 2026-03-15
   - 参与人: 02架构师

2. [来源: memory/architecture/api-design]
   **认证方案**: OAuth2 + JWT，Bearer Token
   - 评估时间: 2026-02-20
   - 评估人: 03构建师

### 知识缺口

⚠️ **未收录**: 关于"微服务可观测性"的具体实践
   → 建议补充: 当前是否实施了APM监控？

### 溯源链

person/yang-san → memory/architecture/microservices
memory/architecture/microservices → memory/architecture/api-design
```

## 与天龙引擎协同

### 组织架构映射

| 天龙 Agent | 协同方式 | 协同内容 |
|-----------|---------|---------|
| 01调研师 | 上游触发 | 研究前先检索已有知识 |
| 00分析师 | 决策支持 | 决策前检索相关历史 |
| 02架构师 | 架构参考 | 设计前检索架构决策 |
| 07记录师 | 归档前检查 | 归档前建立关联 |
| 09-02编排协调师 | 编排辅助 | 任务编排参考历史 |

### 情报闭环

```
gbrain-signal-detector (信号检测)
    ↓
gbrain-multimodal-ingest (知识摄入)
    ↓
gbrain-hybrid-search (检索) ← 当前技能 ⭐
    ↓
gbrain-entity-enrich (实体充实) ← 触发下游
    ↓
gbrain-daily-briefing (简报生成)
    ↓
09-02编排协调师 (行动项编排)
```

## 预期收益

| 指标 | 集成前 | 集成后 | 提升 |
|------|--------|--------|------|
| 检索准确率 | 基准 | 三层架构 | +40% |
| 引用可溯源率 | 无 | 100%强制 | 质的飞跃 |
| 幻觉检测率 | 无 | 强制标注缺口 | +60% |
| 知识复用率 | 碎片化 | 体系化 | +200% |

## 技能文件

- [SKILL.md](SKILL.md) - 本文件
- [config.yaml](config.yaml) - 配置文件
- [scripts/hybrid_search.py](scripts/hybrid_search.py) - 检索CLI
- [prompts/search_template.md](prompts/search_template.md) - 检索提示词模板
