---
license: UNKNOWN
triggers: ["rss aggregator", "RSS Aggregator Skill"]
---
# RSS Aggregator Skill

> RSS/Atom 订阅聚合 + 多源合并 + 定时摘要
> 借鉴自 Huginn RSS Agent 设计理念

## 核心价值

| 维度 | 数据 |
|------|------|
| **定位** | 天龙引擎信息聚合中心 |
| **核心能力** | 多源订阅 + 定时拉取 + 内容去重 + 摘要生成 |
| **借鉴来源** | Huginn RSS Agent |
| **优先级** | ⭐⭐ 中优先级 |

## 功能矩阵

| 功能 | 说明 | 命令 |
|------|------|------|
| **订阅管理** | 添加/删除/分类 RSS 源 | `rss add` |
| **定时拉取** | Cron 调度 + 间隔模式 | `rss fetch` |
| **内容去重** | 基于 URL/标题/内容去重 | `rss dedup` |
| **摘要生成** | AI 驱动的多源摘要 | `rss digest` |
| **全文提取** | 完整文章内容抓取 | `rss fulltext` |

## 支持格式

| 格式 | 支持 | 说明 |
|------|------|------|
| **RSS 2.0** | ✅ | 最常见格式 |
| **Atom** | ✅ | 多数博客支持 |
| **JSON Feed** | ✅ | 新兴格式 |
| **RSS 1.0** | ✅ | RDF 格式 |

## 快速开始

```bash
# 添加订阅源
rss add "https://blog.example.com/feed.xml" --tag tech
rss add "https://news.site/rss" --tag news

# 拉取更新
rss fetch --all
rss fetch --tag tech

# 生成摘要
rss digest --hours 24 --format markdown

# 查看内容
rss list --tag news --limit 10
rss read <item_id>
```

## 核心命令

```bash
# 订阅管理
rss add <url> [--tag] [--category] [--interval]
rss list [--tag] [--format json|table|markdown]
rss delete <id>
rss import opml <file.opml>

# 内容拉取
rss fetch [--all] [--tag] [--since]
rss fetch --parallel 5        # 并行拉取
rss fetch --force              # 强制刷新

# 内容处理
rss read <item_id> [--fulltext]
rss search <keyword> [--tag]
rss dedup --strategy url|title|content
rss filter --keywords --exclude-tags

# 摘要生成
rss digest --hours 24 --format markdown|html|json
rss digest --sources <id>... --hours 48
rss digest --ai --provider openai --model gpt-4

# 导出
rss export opml > subscriptions.opml
rss export json > feed.json
```

## 订阅分类

```yaml
# ~/.claude/rss-config.yaml
categories:
  tech:
    - name: Hacker News
      url: https://hnrss.org/frontpage
      interval: 30m
    - name: 技术栈
      url: https://blog.example.com/feed.xml

  news:
    - name: 科技新闻
      url: https://news.site/rss
      interval: 1h

  ai:
    - name: AI News
      url: https://AINews.com/feed
      interval: 15m
```

## 与其他 Skill 协同

| Skill | 协同方式 |
|-------|---------|
| **paperclip-heartbeat** | Cron 调度自动拉取 |
| **Agent-Reach** | 补充全文内容抓取 |
| **summarize** | AI 摘要生成 |
| **lark-docs** | 摘要同步到飞书文档 |
| **wechat-article-generator** | 生成公众号文章 |

## 实现架构

```
┌─────────────────────────────────────────────────────────────┐
│ RSS Aggregator 架构                                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐            │
│  │  Feed    │───▶│  Parser  │───▶│  Store   │            │
│  │  List    │    │  (multi) │    │  (SQLite)│            │
│  └──────────┘    └──────────┘    └──────────┘            │
│       │               │               │                    │
│       ▼               ▼               ▼                    │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐            │
│  │ Scheduler│    │  Dedup   │    │  Digest  │            │
│  │(Cron/Int)│    │  Engine  │    │ Generator│            │
│  └──────────┘    └──────────┘    └──────────┘            │
│                                              │              │
│                                              ▼              │
│                                       ┌──────────┐         │
│                                       │ Notifier │         │
│                                       │ Webhook  │         │
│                                       └──────────┘         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 使用示例

```bash
# 天龙引擎自然语言调用
[@01调研师] 聚合 AI 相关的 RSS 源，每天生成摘要
[@07记录师] 将昨天的技术新闻汇总成一篇公众号文章

# 完整工作流
rss add "https://hnrss.org/frontpage" --tag ai
rss add "https://AINews.com/feed" --tag ai
rss fetch --tag ai --parallel
rss digest --tag ai --hours 24 --ai --provider openai
```

## 摘要模板

```markdown
# {{date}} {{category}} 资讯摘要

## 今日要点
{{summary}}

## 详细列表
{{items}}

## 来源
{{sources}}
```

## 与 Huginn 协同

```yaml
# 如果部署 Huginn，可以使用 Huginn RSS Agent 作为数据源
# 通过 Webhook 将 Huginn 事件传入天龙引擎
rss watch --source huginn --webhook http://huginn:5000/webhooks/webhook/123
```

## 预期收益

| 指标 | 提升 |
|------|------|
| **信息获取效率** | +500%（多源聚合） |
| **去重效果** | -70%（重复内容） |
| **摘要生成** | +300%（AI 驱动） |
| **时间节省** | -80%（自动化） |

## 安装

```bash
# 初始化
rss init --db ~/.claude/rss.db

# 导入 OPML
rss import opml ~/Downloads/subscriptions.opml

# 启动定时拉取（使用 paperclip-heartbeat）
rss daemon --interval 30m
```
