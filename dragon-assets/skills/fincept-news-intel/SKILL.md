---
license: UNKNOWN
triggers: ["fincept news intel", "fincept-news-intel - 新闻智能分析 Skill"]
---
# fincept-news-intel - 新闻智能分析 Skill

## 概述

`fincept-news-intel` 是天龙引擎的新闻智能分析 Skill，封装 FinceptTerminal 的新闻抓取、情感分析、主题聚类、实体关联和 SEC 公告追踪能力。

## 核心能力

| 能力 | 功能 | 使用场景 |
|------|------|---------|
| **新闻抓取** | 多源新闻搜索 | 市场情报、舆情监控 |
| **情感分析** | NLP 新闻情感量化 | 情绪判断、趋势预测 |
| **主题聚类** | HDBSCAN 新闻聚类 | 主题发现、趋势分析 |
| **关联分析** | 实体关系追踪 | 事件归因、影响评估 |
| **SEC 公告** | EDGAR 文件追踪 | 监管动态、重大事件 |
| **财报电话会** | 管理层语调分析 | 业绩评估、预期管理 |

## 数据源

| 数据源 | 用途 | 限制 |
|--------|------|------|
| NewsAPI | 免费新闻搜索 | 100 req/day (免费层) |
| FinnHub | 实时新闻 + 情感 | 60 req/min |
| Polygon.io | 财经新闻 | 订阅制 |
| SEC EDGAR | 公告文件 | 无限制 |
| Alpha Vantage | 新闻情绪 | 25 req/day (免费层) |

## 安装

```bash
# 安装依赖
pip install -r ~/.claude/skills/fincept-news-intel/requirements.txt

# 配置 API Key（可选）
export NEWS_API_KEY="your-news-api-key"
export FINNHUB_API_KEY="your-finnhub-api-key"
```

## 快速开始

### Python API

```python
from fincept_news import NewsIntelligence

# 初始化
intel = NewsIntelligence()

# 搜索新闻
news = intel.search(
    query="AAPL iPhone",
    start_date="2024-01-01",
    end_date="2024-12-31",
    source="all"
)

# 情感分析
sentiment = intel.sentiment(
    text="Apple announces record iPhone sales"
)

# 主题聚类
clusters = intel.cluster(news, n_clusters=5)

# SEC 公告
sec_news = intel.sec_filings(ticker="AAPL", form_type="8-K")
```

### CLI 命令

```bash
# 新闻搜索
python ~/.claude/skills/fincept-news-intel/scripts/cli.py search "Apple iPhone" --source all

# 情感分析
python ~/.claude/skills/fincept-news-intel/scripts/cli.py sentiment "Apple beats expectations"

# 主题聚类
python ~/.claude/skills/fincept-news-intel/scripts/cli.py cluster --input news.json

# SEC 公告
python ~/.claude/skills/fincept-news-intel/scripts/cli.py sec AAPL --form-type 8-K

# 财报电话会
python ~/.claude/skills/fincept-news-intel/scripts/cli.py earnings AAPL --quarter Q1-2024
```

## API 参考

### NewsIntelligence

#### `search()`
新闻搜索。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `query` | str | 是 | 搜索关键词 |
| `start_date` | str | 否 | 开始日期 (YYYY-MM-DD) |
| `end_date` | str | 否 | 结束日期 (YYYY-MM-DD) |
| `source` | str | 否 | bloomberg/reuters/wsj/sec/all |
| `limit` | int | 否 | 返回数量 (默认 50) |

**返回**: `List[NewsArticle]`

```python
news = intel.search(query="AAPL", start_date="2024-01-01", limit=10)
for article in news:
    print(f"{article['title']} - {article['source']} ({article['date']})")
```

#### `sentiment()`
单条文本情感分析。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `text` | str | 是 | 待分析文本 |

**返回**: `SentimentResult`

```python
result = intel.sentiment(text="Apple announces record earnings")
print(f"情感: {result['label']}")      # positive/negative/neutral
print(f"得分: {result['score']:.3f}") # -1 to 1
```

#### `batch_sentiment()`
批量情感分析。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `texts` | List[str] | 是 | 文本列表 |
| `batch_size` | int | 否 | 批大小 (默认 32) |

**返回**: `List[SentimentResult]`

#### `cluster()`
新闻主题聚类。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `news` | List[NewsArticle] | 是 | 新闻列表 |
| `n_clusters` | int | 否 | 聚类数量 |
| `method` | str | 否 | hdbscan/kmeans (默认 hdbscan) |

**返回**: `List[NewsCluster]`

```python
clusters = intel.cluster(news, n_clusters=5)
for cluster in clusters:
    print(f"主题: {cluster['topic']}")
    print(f"文章数: {cluster['size']}")
    print(f"关键词: {cluster['keywords']}")
```

#### `correlate()`
实体关联分析。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `entity` | str | 是 | 实体名称 |
| `date_range` | tuple | 否 | 日期范围 |

**返回**: `CorrelationResult`

#### `sec_filings()`
SEC 公告追踪。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `ticker` | str | 是 | 股票代码 |
| `form_type` | str | 否 | 8-K/10-K/10-Q/4 |
| `limit` | int | 否 | 返回数量 (默认 20) |

**返回**: `List[SECFiling]`

#### `earnings_call()`
财报电话会分析。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `ticker` | str | 是 | 股票代码 |
| `quarter` | str | 否 | 季度 (Q1-2024) |

**返回**: `EarningsCall`

## 数据模型

### NewsArticle

```python
{
    "title": str,       # 标题
    "source": str,      # 来源
    "date": str,        # 日期 (YYYY-MM-DD)
    "url": str,         # 原文链接
    "summary": str,     # 摘要
    "content": str,     # 正文
    "entities": List[str]  # 提及实体
}
```

### SentimentResult

```python
{
    "label": str,       # positive/negative/neutral
    "score": float,    # -1 to 1
    "confidence": float  # 0 to 1
}
```

### NewsCluster

```python
{
    "topic": str,           # 主题描述
    "size": int,            # 文章数量
    "keywords": List[str],  # 核心关键词
    "articles": List[NewsArticle]  # 文章列表
}
```

### SECFiling

```python
{
    "form_type": str,       # 8-K/10-K/10-Q/4
    "filing_date": str,     # 提交日期
    "description": str,      # 描述
    "url": str             # EDGAR 链接
}
```

### EarningsCall

```python
{
    "date": str,
    "ticker": str,
    "quarter": str,
    "mgmt_sentiment": str,  # positive/negative/neutral
    "highlights": List[{
        "name": str,
        "value": str
    }]
}
```

## 天龙岗位协同

| 岗位 | 协同方式 |
|------|---------|
| **62-02 行业研究员** | 新闻情感 + 主题聚类 → 行业趋势报告 |
| **64-01 量化研究员** | SEC 公告 + 财报电话会 → 因子构建 |
| **32-01 市场研究** | 关联分析 + 新闻聚类 → 竞争情报 |
| **60-01 投资总监** | 情感分析 + SEC 追踪 → 投资决策支持 |

## 文件结构

```
fincept-news-intel/
├── SKILL.md
├── scripts/
│   ├── __init__.py
│   ├── client.py       # NewsIntelligence 主类
│   ├── sentiment.py    # 情感分析模块
│   ├── clustering.py   # 主题聚类模块
│   ├── correlation.py   # 关联分析模块
│   ├── sec_filings.py # SEC 公告模块
│   └── cli.py          # CLI 入口
├── requirements.txt
└── README.md
```

## 依赖

```
newsapi-python>=0.2.0
finnhub-python>=2.0.0
polygon>=1.0.0
alpha_vantage>=1.0.0
requests>=2.28.0
beautifulsoup4>=4.12.0
scikit-learn>=1.3.0
hdbscan>=0.8.1
numpy>=1.24.0
pandas>=2.0.0
textblob>=0.17.0
lxml>=4.9.0
```

## 限制与注意事项

1. **API 限额**: 免费层有严格限制，生产环境建议使用订阅账户
2. **情感模型**: 使用 TextBlob，默认模型，适用于英文新闻
3. **中文支持**: 情感分析需翻译或使用中文 NLP 模型
4. **缓存建议**: 大量请求时添加本地缓存避免重复调用

## 错误处理

所有 API 调用强制设置 `timeout=30`，错误时抛出 `NewsIntelError`:

```python
from fincept_news import NewsIntelligence, NewsIntelError

intel = NewsIntelligence()
try:
    news = intel.search(query="AAPL")
except NewsIntelError as e:
    print(f"API 错误: {e}")
```

## 版本

- **V1.0** (2026-04-27): 初始版本
