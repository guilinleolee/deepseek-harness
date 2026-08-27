---
license: UNKNOWN
triggers: ["news free api", "news-free-api"]
---
# news-free-api

## L0: 一句话描述 (≤15字)
免费新闻API替代付费舆情监控服务

## L1: 使用场景 (50-100字)
替代昂贵的付费新闻数据服务（GNI $300+/月, NewsAPI $449+/月），为零成本舆情监控、竞品新闻追踪、行业资讯聚合提供免费新闻API接口。适合个人开发者和初创产品团队。

## L2: 详细文档

### 来源项目
| 项目 | 核心能力 |
|------|---------|
| [NewsAPI](https://newsapi.org) | 免费新闻API（100请求/天）+ 全球 headlines/search/sources |
| [currentsapi.services](https://currentsapi.services) | 免费新闻API（300请求/天）+ 多语言支持 |

### 核心能力

```
┌─────────────────────────────────────────────────────────────┐
│ Free News Data Stack                                        │
├─────────────────────────────────────────────────────────────┤
│  NewsAPI:      Headlines/Search/Sources（免费100/天）      │
│  CurrentsAPI:   全球新闻+多语言（免费300/天）              │
│  联合使用:     跨平台新闻采集闭环+自动故障切换            │
└─────────────────────────────────────────────────────────────┘
```

### API端点

| 功能 | NewsAPI | CurrentsAPI | 免费额度 |
|------|---------|-------------|---------|
| 热门新闻 | /top-headlines | /latest-news | 100次/天 |
| 关键词搜索 | /everything | /search | 100次/天 |
| 新闻来源 | /sources | - | 100次/天 |
| 分类新闻 | /top-headlines?category= | - | 100次/天 |
| 多语言 | 英文为主 | 中/英/日/德等 | 300次/天 |
| 存档历史 | 3天免费 | 30天存档 | 有限制 |

### 价格对比

| 服务商 | 月费 | 免费替代 | 节省 |
|--------|------|---------|------|
| **免费组合** | **$0** | NewsAPI + CurrentsAPI | **$300+/月** |
| GNI News Intelligence | $300+ | - | - |
| NewsAPI Pro | $449+ | - | - |
| Bing News Search | $40+/月 | - | - |
| NewsCatcherAPI | $299+/月 | - | - |

### 天龙岗位升级

| 岗位 | 版本 | 新增能力 |
|------|------|---------|
| **17-01数据分析师** | V1.4 → V1.5 | 新闻数据采集+舆情分析 |
| **32-01市场研究** | V10.2 → V10.3 | 新闻舆情监控+行业资讯聚合 |
| **01调研师** | V8.89 → V8.90 | 新闻API自动化采集+多语言支持 |
| **35-02社媒运营** | V12.8 → V12.9 | 竞品新闻追踪+热点监控 |

### 核心命令速查

```bash
# 1. 获取API Key (免费)
# NewsAPI: https://newsapi.org/register
# CurrentsAPI: https://currentsapi.services/zh/register

# 2. 设置环境变量
export NEWS_API_KEY="your-key"
export CURRENTS_API_KEY="your-key"

# 3. 获取热门新闻
python3 ~/.claude/skills/news-free-api/scripts/top_headlines.py --country us --category technology

# 4. 关键词搜索
python3 ~/.claude/skills/news-free-api/scripts/search_news.py "AI Agent" --from-date 2026-05-01

# 5. 新闻来源列表
python3 ~/.claude/skills/news-free-api/scripts/news_sources.py --category technology

# 6. 多语言新闻
python3 ~/.claude/skills/news-free-api/scripts/multi_lang_news.py --lang zh --keyword "人工智能"

# 7. 批量舆情采集
python3 ~/.claude/skills/news-free-api/scripts/batch_news.py --keywords "AI,人工智能,Machine Learning" --output news.json
```

### Python API封装

```python
from news_client import NewsClient

client = NewsClient(
    newsapi_key=os.getenv("NEWS_API_KEY"),
    currentsapi_key=os.getenv("CURRENTS_API_KEY")
)

# 获取技术类热门新闻
headlines = client.top_headlines(category="technology", country="us")

# 关键词搜索（自动切换API）
results = client.search("AI Agent", from_date="2026-05-01", language="en")

# 新闻来源
sources = client.get_sources(category="technology")

# 多语言新闻（中文）
zh_news = client.multi_lang_search("人工智能", language="zh")

# 批量舆情采集
batch = client.batch_scrape(["AI", "Machine Learning", "Deep Learning"], days=7)
```

### 舆情分析示例

```python
from news_client import NewsClient

client = NewsClient()

# 采集竞品新闻
competitor_news = client.search("竞品公司名", from_date="2026-05-01", to_date="2026-05-15")

# 情感统计
positive = sum(1 for n in competitor_news if n.get('sentiment') > 0.3)
negative = sum(1 for n in competitor_news if n.get('sentiment') < -0.3)
neutral = len(competitor_news) - positive - negative

print(f"正面: {positive}, 负面: {negative}, 中性: {neutral}")

# 热点追踪
hot_topics = client.get_hot_topics("AI", days=30)
print("最近30天AI热点:", hot_topics)
```

### 成本节省估算

| 使用量 | 付费服务成本 | 免费组合成本 | 节省 |
|--------|------------|-------------|------|
| 个人项目 | $50/月 | **$0** | $600/年 |
| 初创产品 | $150/月 | **$0** | $1,800/年 |
| 企业级 | $500+/月 | **$0** | $6,000+/年 |

### 预期收益

| 指标 | V11.12 | V11.13 | 提升 |
|------|--------|--------|------|
| 新闻数据成本 | $300+/月 | **$0** | **-100%** |
| 舆情分析覆盖 | 手动搜集 | API自动化 | **+300%** |
| 多语言新闻 | 英文为主 | 中英日德等 | **质的飞跃** |
| 热点追踪效率 | 手动 | 自动化 | **+500%** |

### 文件结构

```
news-free-api/
├── SKILL.md                    # 本文件
├── scripts/
│   ├── __init__.py
│   ├── news_client.py          # 统一客户端
│   ├── newsapi_client.py        # NewsAPI封装
│   ├── currentsapi_client.py    # CurrentsAPI封装
│   ├── top_headlines.py         # 热门新闻CLI
│   ├── search_news.py          # 搜索CLI
│   ├── news_sources.py         # 新闻来源CLI
│   ├── multi_lang_news.py      # 多语言CLI
│   └── batch_news.py           # 批量采集CLI
└── README.md                   # 使用指南
```

### 技术约束

- NewsAPI免费: 100请求/天, 仅支持开发环境
- CurrentsAPI免费: 300请求/天, 需要注册获取Key
- 建议: 实现本地缓存+请求去重+延迟控制
- NewsAPI不支持商业使用，需要付费版本

### 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-15 | 初始集成，NewsAPI + CurrentsAPI双API组合 |
