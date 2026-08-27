---
license: UNKNOWN
triggers: ["ai news radar scout", "AI News Radar Scout - 伯乐信息源评估技能"]
---
# AI News Radar Scout - 伯乐信息源评估技能

## L0: 一句话描述 (≤15字)
AI新闻雷达 - 智能识别优质信息源

## L1: 使用场景 (50-100字)
用于AI/科技领域的新闻追踪和信息源评估。伯乐Skill自动判断信息源类型（官方RSS/OPML/GitHub Feed/静态页面），过滤噪音，保留AI强相关内容。零成本运行（无需API Key），每30分钟自动更新。

## L2: 详细文档

### 核心能力

```
┌─────────────────────────────────────────────────────────────┐
│ AI News Radar 伯乐Skill流程                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  信息源清单 → 伯乐Skill判断类型 → 分流处理               │
│       ↓                                                     │
│  official["官方 RSS/changelog"] → 高优先级抓取             │
│  opml["私人 OPML/RSS"] → 标准处理                        │
│  publicFeed["公开 GitHub Feed"] → 常规处理                │
│  staticPage["公开页面"] → Jina Reader兜底                │
│  privateMail["AgentMail邮箱"] → 需API                    │
│  skip["跳过高风险来源"] → 过滤                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 数据处理Pipeline

```
抓取 → 去重与归一化 → AI强相关过滤 → 源健康统计 → 输出JSON
```

### 支持的信息源类型

| 源类型 | 实现方式 | API Key | 优先级 |
|--------|----------|---------|--------|
| 官方RSS/changelog | feedparser | ❌ | P0 |
| OPML批量订阅 | feedparser | ❌ | P1 |
| GitHub公开Feed | fetch API | ❌ | P2 |
| 静态页面 | Jina Reader | ❌ | P3 |
| AgentMail邮箱 | API调用 | ✅ | P4 |
| X/Twitter | 官方API | ✅ | P5 |

### 追踪的官方节点

- **OpenAI**: API changelog, research papers
- **Anthropic**: Claude updates, safety research
- **Google DeepMind**: Gemini, AlphaFold updates
- **Meta AI**: Llama, research publications
- **Mistral AI**: Model releases
- **Perplexity**: API updates
- **Groq**: API announcements

### 快速启动

```bash
# 初始化环境
cd ~/.claude/skills/ai-news-radar-scout
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 更新新闻数据
python scripts/update_news.py --output-dir data --window-hours 24

# 伯乐评估信息源
python scripts/scout.py --source-list feeds/opml/custom.opml

# 本地预览
python -m http.server 8080 --directory .
```

### GitHub Actions自动化

```yaml
# .github/workflows/ai-news-radar.yml
name: AI News Radar
on:
  schedule:
    - cron: '*/30 * * * *'  # 每30分钟运行
  workflow_dispatch:  # 手动触发

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Update news
        run: python scripts/update_news.py --output-dir data
      - name: Commit and push
        uses: EndBug/add-commit-commit@v10
        with:
          message: 'chore: auto-update AI news $(date)'
```

### CLI命令

```bash
# 伯乐评估信息源质量
python scripts/scout.py evaluate --source https://example.com/feed.xml

# 批量评估OPML
python scripts/scout.py batch --opml feeds/opml/custom.opml

# 生成审计报告
python scripts/scout.py audit --report-dir reports

# 查看源健康状态
python scripts/scout.py health --sources data/sources.json

# AI相关性评分
python scripts/score.py --input data/news.json --output data/scored.json
```

### 输出格式

```json
{
  "timestamp": "2026-05-13T10:30:00Z",
  "window_hours": 24,
  "total_sources": 45,
  "healthy_sources": 42,
  "unhealthy_sources": 3,
  "articles": [
    {
      "title": "Claude 4 Release Notes",
      "title_zh": "Claude 4发布说明",
      "source": "Anthropic Official",
      "source_type": "official",
      "url": "https://...",
      "published": "2026-05-13T08:00:00Z",
      "ai_relevance_score": 0.95,
      "ai_relevance_reason": "官方发布重要模型更新，AI相关性极高",
      "tags": ["model-release", "claude", "anthropic"]
    }
  ]
}
```

### 与天龙引擎协同

| 天龙组件 | 协同方式 | 效果 |
|---------|---------|------|
| `rss-feed-manager` (V10.0) | 叠加伯乐评估层 | 优先级调度优化 |
| `trendradar-core` (V10.0) | 叠加AI相关性评分 | TrendRadar增强 |
| `last30days` (V8.54) | 叠加30分钟更新 | 时效性研究增强 |
| `follow-builders` (V8.58) | 叠加官方节点追踪 | AI Builder增强 |

### 适用场景

| 场景 | 命令 |
|------|------|
| AI领域时效性研究 | 使用ai-news-radar追踪最新AI新闻 |
| 信息源质量评估 | 使用伯乐Skill评估新信源 |
| 市场趋势监控 | 使用AI相关性评分筛选高价值内容 |
| 竞品动态追踪 | 配置竞品官方RSS源 |

### 依赖

```
feedparser>=6.0.0
requests>=2.31.0
jinja2>=3.1.0
pytz>=2024.1
```

### 文件结构

```
ai-news-radar-scout/
├── SKILL.md                    # 本文件
├── requirements.txt           # Python依赖
├── scripts/
│   ├── __init__.py
│   ├── scout.py               # 伯乐信息源评估
│   ├── update_news.py         # 新闻更新Pipeline
│   ├── score.py               # AI相关性评分
│   └── health_check.py         # 源健康检查
├── feeds/
│   ├── opml/
│   │   ├── official.opml     # 官方源订阅
│   │   └── custom.opml        # 自定义源
│   └── sources.json            # 源配置
├── data/
│   ├── news.json              # 生成新闻数据
│   ├── scored.json             # 评分后数据
│   └── sources.json            # 源状态
├── reports/
│   └── audit_*.json          # 审计报告
└── workflows/
    └── ai-news-radar.yml     # GitHub Actions
```

### 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-13 | 初始集成，基于LearnPrompt/ai-news-radar |
