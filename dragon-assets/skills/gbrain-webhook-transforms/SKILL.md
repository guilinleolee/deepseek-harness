---
license: UNKNOWN
triggers: ["gbrain webhook transforms", "GBrain Webhook Transforms Skill"]
---
# GBrain Webhook Transforms Skill
# Webhook 数据转换技能

## 用途
`webhook_transforms.py serve` 命令 — 将外部 Webhook 事件（GitHub、Slack、Email、RSS 等）转换为 GBrain 知识库条目，实现知识库的实时增量更新。

---

## 核心能力

### 支持的 Webhook 源

| 来源 | 事件类型 | 转换行为 |
|------|-----------|----------|
| **GitHub** | push, PR, issue, star | 实体页更新 / 时间线事件 |
| **Slack** | message, reaction | 讨论记录 / 决策条目 |
| **Email** | inbox | 重要对话归档 |
| **RSS/Atom** | new entry | 外部信息同步 |
| **Calendar** | event | 时间线事件 |
| **Custom** | JSON POST | 通用转换器 |

### 核心转换逻辑

```
┌─────────────────────────────────────────────────────────────┐
│ Webhook → GBrain 转换管道                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐    ┌────────────┐    ┌─────────────────┐  │
│  │ Webhook  │───▶│  Parser   │───▶│  Transformer    │  │
│  │  Source  │    │  (解析)    │    │  (转换为条目)    │  │
│  └──────────┘    └────────────┘    └────────┬────────┘  │
│                                              │            │
│  ┌──────────┐    ┌────────────┐    ┌────────▼────────┐  │
│  │  GBrain  │◀───│   Write   │◀───│  Enricher      │  │
│  │  KB      │    │  (写入)    │    │  (充实元数据)   │  │
│  └──────────┘    └────────────┘    └─────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## CLI 命令

```bash
# 启动 Webhook 服务器
python webhook_transforms.py serve [--port 8080]

# 测试 Webhook (发送测试事件)
python webhook_transforms.py test --source github --event push

# 列出已注册的 Webhook
python webhook_transforms.py list

# 手动触发 RSS 同步
python webhook_transforms.py sync --source rss --feed "https://example.com/rss"

# 转换测试 (不写入)
python webhook_transforms.py transform --source github --payload @event.json --dry-run

# 添加新的 Webhook 源
python webhook_transforms.py add --source github --events "push,pr,issue" --transform "standard"

# 移除 Webhook 源
python webhook_transforms.py remove --source github
```

---

## 脚本实现

脚本路径: `scripts/webhook_transforms.py`

### 核心架构

#### HTTP Server (serve 命令)
- 使用 Flask 或内置 http.server
- 端点: `POST /webhook/<source>`
- 签名验证: GitHub (HMAC-SHA256), Slack (Signing Secret)
- 请求体解析 → Transform → Write-back

#### Transform Engine
```python
# 每种来源的 Transform 函数
def transform_github_push(payload: dict) -> list[EntityUpdate]:
    # push event → 提取 repo, commits, author
    # 生成实体更新: project/commits, person/authors

def transform_github_issue(payload: dict) -> list[EntityUpdate]:
    # issue event → 提取 project, issue, assignees
    # 生成实体更新: project/issues, person/assignees

def transform_slack_message(payload: dict) -> list[EntityUpdate]:
    # message event → 提取 channel, user, text
    # 生成决策条目或讨论记录

def transform_rss_entry(payload: dict) -> list[EntityUpdate]:
    # RSS item → 提取 title, link, description, date
    # 生成外部信息条目

def transform_calendar_event(payload: dict) -> list[EntityUpdate]:
    # Calendar event → 提取 title, time, attendees
    # 生成时间线事件
```

#### Write-back 模块
调用 `entity_enricher.py` 的 API:
```python
def write_to_brain(updates: list[EntityUpdate]) -> None:
    for update in updates:
        entity_type = update.entity_type
        slug = update.slug
        # 调用 entity_enricher.py add/update 命令
        enricher.add(entity_type, slug, update.frontmatter, update.body)
        # 添加时间线事件
        enricher.timeline_add(slug, update.event)
```

---

## 支持的事件类型详细映射

### GitHub 事件

| GitHub 事件 | GBrain 条目类型 | 写入位置 |
|-------------|----------------|----------|
| `push` | 时间线事件 | `entities/<repo>/timeline.json` |
| `pull_request` | 时间线事件 + 实体更新 | `entities/<repo>/` + backlinks |
| `issues` | 讨论记录 | `entities/<repo>/issues/` |
| `star` | 关系更新 | `entities/<repo>/` links |
| `release` | 时间线事件 | `entities/<repo>/timeline.json` |
| `fork` | 关系记录 | `entities/<repo>/forks/` |

### Slack 事件

| Slack 事件 | GBrain 条目类型 | 写入位置 |
|------------|----------------|----------|
| `message` (特定频道) | 决策条目 | `pages/decisions/<date>.md` |
| `reaction_added` | 讨论记录 | `pages/discussions/<thread>.md` |
| `channel_created` | 上下文页面 | `pages/context/<channel>.md` |

### RSS 事件

| RSS 条目 | GBrain 条目类型 | 写入位置 |
|----------|----------------|----------|
| 新文章 | 外部信息条目 | `entities/<source>/rss/<slug>.md` |
| 更新文章 | 充实现有条目 | 更新 frontmatter.updated |

### 自定义 Webhook

```json
// POST /webhook/custom 接收格式
{
  "source": "custom",
  "entity_type": "company",
  "slug": "acme-corp",
  "event": {
    "type": "funding_round",
    "data": {
      "round": "Series C",
      "amount": "$100M",
      "date": "2026-01-15",
      "investors": ["a16z", "Sequoia"]
    }
  },
  "confidence": 0.95,
  "raw": { ... }
}
```

---

## Webhook 服务器配置

### config.yaml 示例

```yaml
webhook_transforms:
  enabled: true
  server:
    host: "0.0.0.0"
    port: 8080
    workers: 2

  # GitHub 配置
  github:
    secret: "${GITHUB_WEBHOOK_SECRET}"   # 环境变量
    allowed_repos:
      - "owner/repo1"
      - "owner/repo2"
    event_transforms:
      push: "standard"
      pull_request: "standard"
      issues: "standard"
      release: "minimal"

  # Slack 配置
  slack:
    signing_secret: "${SLACK_SIGNING_SECRET}"
    allowed_channels:
      - "C01_DECISIONS"      # 决策频道 → 写入决策条目
      - "C02_DISCUSSIONS"    # 讨论频道 → 写入讨论记录
    ignore_bots: true
    min_reaction_count: 2    # 至少2个 reaction 才记录

  # RSS 配置
  rss:
    feeds:
      - url: "https://example.com/rss"
        slug: "example-blog"
        entity: "blog"
        poll_interval: 3600   # 秒
      - url: "https://news.example.com/feed"
        slug: "example-news"
        entity: "news"
        poll_interval: 1800

  # Calendar 配置
  calendar:
    provider: "google"       # google | outlook | ics
    credentials_file: "~/.claude/gbrain/credentials/calendar.json"
    watched_calendars:
      - "primary"
      - "project-meetings"

  # 通用配置
  general:
    dry_run: false           # true: 不写入, 仅日志
    confidence_threshold: 0.5  # 低于此置信度不写入
    transform_mode: "standard"  # standard | minimal | verbose
    max_events_per_source: 100  # 单次最多处理事件数
    deduplicate_window: 3600   # 秒内去重窗口
```

### 环境变量

```bash
export GITHUB_WEBHOOK_SECRET="whsec_xxx"
export SLACK_SIGNING_SECRET="xxx"
export GBRAIN_WEBHOOK_PORT=8080
```

---

## 与其他 GBrain 技能的协作

```
webhook_transforms.py
       │
       ├── 事件丰富
       │        └── api_learn_loop.py READ→ENRICH→WRITE
       │
       ├── 实体创建/更新
       │        └── entity_enricher.py add/update
       │
       ├── 实体关系建立
       │        └── entity_enricher.py link
       │
       └── 审查触发
                └── cross_modal_review.py (检测到新内容时触发审查)
```

---

## 文件结构

```
gbrain-webhook-transforms/
├── SKILL.md                           # 本文件
├── config.yaml                        # 配置文件
├── scripts/
│   ├── webhook_transforms.py          # 核心脚本 (serve + transform)
│   └── webhook_server.py             # HTTP 服务器封装 (可选)
└── prompts/
    └── webhook_template.md            # Webhook 事件模板
```

---

## 天龙九部角色映射

| 角色 | 关联方式 |
|------|----------|
| **00分析师** | 决策条目自动归档 → 战略决策分析 |
| **01调研师** | RSS/外部信息自动同步 → 实时情报 |
| **03构建师** | GitHub push/PR 自动记录 → 代码变更追踪 |
| **07记录师** | 决策/讨论自动归档 → 知识库增量更新 |
| **08发布师** | GitHub release 事件 → 发布记录时间线 |

---

## 安全考虑

| 风险 | 缓解措施 |
|------|----------|
| Webhook 伪造 | HMAC 签名验证 (GitHub/Slack 提供) |
| 恶意 payload | 输入验证 + sandboxed 执行 |
| 信息泄露 | 仅记录授权 repo/channel 的事件 |
| 拒绝服务 | 请求速率限制 + 队列缓冲 |
| 环境污染 | dry_run 模式 + 置信度阈值过滤 |

---

## 预期收益

| 指标 | 效果 |
|------|------|
| 决策记录完整性 | +300% |
| GitHub 活动追踪 | 实时自动 |
| 外部信息同步延迟 | <1 分钟 |
| 知识库增量更新 | 无需手动录入 |
