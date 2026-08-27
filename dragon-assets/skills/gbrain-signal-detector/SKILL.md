---
license: UNKNOWN
github_repo: garrytan/gbrain
github_hash: 11abb24ddd2209f8622870c2e48dc9ef050ad749
last_updated: 2026-04-25
source_type: derived
triggers: ["gbrain signal detector", "gbrain-signal-detector"]
---
# gbrain-signal-detector

## L0: 一句话描述 (≤15字)
Always-on信号捕获与实时并行信息挖掘

## L1: 使用场景 (50-100字)
适用于需要持续监控外部信息源、实时捕获信号、自动触发知识沉淀的场景。当用户需要跟踪特定话题、监控竞品动态、捕捉会议要点时启用。

## L2: 详细文档

### 核心能力

| 能力 | 说明 | 优先级 |
|------|------|--------|
| 并行实时信息挖掘 | 多源信号同时捕获 | P0 |
| 后台持续监控 | 异步信号检测 | P0 |
| 多源信号聚合 | 信号去重与融合 | P1 |
| 智能触发机制 | 时间/关键词/事件触发 | P0 |
| 信号优先级排序 | 相关性评分与过滤 | P1 |

### 信号源类型

```yaml
signal_sources:
  # 外部信息源
  - type: web
    sources: [RSS, API, Webhook]
    priority: high

  - type: social
    sources: [Twitter, Weibo, Zhihu, Xiaohongshu]
    priority: medium

  - type: news
    sources: [News API, RSS Feeds]
    priority: high

  - type: academic
    sources: [arXiv, Papers with Code]
    priority: medium

  - type: business
    sources: [LinkedIn, Company Blogs]
    priority: medium

  # 内部信号源
  - type: memory
    sources: [MemPalace, claude-mem, llm-wiki]
    priority: high

  - type: session
    sources: [conversations, tasks]
    priority: medium
```

### 触发条件配置

```yaml
trigger_conditions:
  time_based:
    - interval: "1h"    # 每小时检查
    - interval: "6h"    # 每6小时深度扫描
    - interval: "24h"  # 每日简报

  keyword_based:
    - watch_list: ["AI", "Claude", "Startup", "Y Combinator"]
    - alert_threshold: 3  # 提及次数阈值

  event_based:
    - new_content: true   # 新内容发布
    - price_change: true  # 价格变动
    - competitor_news: true  # 竞品动态
```

### 信号处理流程

```
┌─────────────────────────────────────────────────────────────┐
│                    信号捕获流程                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. [并行探测] 多源信号同时捕获                            │
│     ├── Web RSS/API  →  [异步并行]                        │
│     ├── Social APIs  →  [异步并行]                        │
│     └── Internal     →  [异步并行]                        │
│                          ↓                                  │
│  2. [信号聚合] 合并去重                                   │
│     ├── 去重(Dedup)                                       │
│     ├── 时序排序                                           │
│     └── 相关性评分                                         │
│                          ↓                                  │
│  3. [智能分类] 实体识别                                   │
│     ├── Person Detection                                   │
│     ├── Company Detection                                  │
│     └── Topic Tagging                                      │
│                          ↓                                  │
│  4. [知识沉淀] 写入记忆系统                               │
│     ├── MemPalace (L3)                                    │
│     ├── llm-wiki-compiler                                 │
│     └── advanced-memory-sync (L0-L1)                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 与天龙引擎协同

```yaml
tianlong_integration:
  # 挂载到07记录师
  attached_role: "07-scribe"

  # 底层存储
  storage_layers:
    - MemPalace (V8.85)      # 实体存储
    - llm-wiki-compiler (V8.85)  # 知识归档
    - advanced-memory-sync (V8.61)  # 分层同步
    - claude-mem (V8.6)      # 会话记忆

  # 上游信号源
  upstream_sources:
    - gbrain-multimodal-ingest  # 多模态摄入
    - follow-builders           # AI Builder追踪
    - last30days              # 时效性研究
```

### 使用方法

```bash
# 启动Always-on信号检测
[@07记录师] 启动信号检测，监控AI和YC相关的关键词

# 手动触发信号捕获
[@07记录师] 捕获当前所有信号源

# 查看信号队列
[@07记录师] 查看信号队列状态

# 停止检测
[@07记录师] 停止信号检测
```

### 配置示例

```yaml
# ~/.claude/skills/gbrain-signal-detector/config.yaml
signal_detector:
  enabled: false  # 默认关闭，用户可选开启

  sources:
    rss_feeds:
      - url: "https://news.ycombinator.com/rss"
        keywords: ["AI", "YC", "startup"]
      - url: "https://blog.samaltman.com/rss"
        keywords: ["OpenAI", "AGI"]

    api_sources:
      - name: "arxiv"
        endpoint: "https://export.arxiv.org/api/query"
        keywords: ["cs.AI", "cs.LG"]

  processing:
    deduplication: true
    relevance_threshold: 0.7
    max_signals_per_day: 100

  storage:
    target: "MemPalace"
    wiki_compile: true
```

## 文件结构

```
gbrain-signal-detector/
├── SKILL.md                    # 本文件
├── config.yaml                 # 配置文件
├── scripts/
│   ├── signal_daemon.py       # 信号守护进程
│   ├── rss_monitor.py         # RSS监控
│   ├── api_poller.py          # API轮询
│   └── signal_aggregator.py    # 信号聚合
└── prompts/
    ├── signal_classifier.md    # 信号分类提示词
    └── relevance_scorer.md     # 相关性评分提示词
```

## 来源参考

本Skill整合自 [garrytan/gbrain](https://github.com/garrytan/gbrain) 的 signal-detector 能力。
