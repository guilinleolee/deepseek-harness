# fincept-news-intel

新闻智能分析 Skill，封装 FinceptTerminal 的新闻抓取、情感分析、主题聚类、实体关联和 SEC 公告追踪能力。

## 安装

```bash
pip install -r ~/.claude/skills/fincept-news-intel/requirements.txt
```

## 快速开始

### Python API

```python
from fincept_news import NewsIntelligence

intel = NewsIntelligence()

# 搜索新闻
news = intel.search(query="Apple iPhone", limit=10)

# 情感分析
result = intel.sentiment(text="Apple announces record earnings")
print(f"情感: {result['label']}, 得分: {result['score']}")

# 主题聚类
clusters = intel.cluster(news, n_clusters=5)

# SEC 公告
filings = intel.sec_filings(ticker="AAPL", form_type="8-K")
```

### CLI

```bash
# 新闻搜索
python ~/.claude/skills/fincept-news-intel/scripts/cli.py search "Apple iPhone" --limit 5

# 情感分析
python ~/.claude/skills/fincept-news-intel/scripts/cli.py sentiment --text "Apple beats expectations"

# 主题聚类
python ~/.claude/skills/fincept-news-intel/scripts/cli.py cluster -i news.json -n 5

# SEC 公告
python ~/.claude/skills/fincept-news-intel/scripts/cli.py sec AAPL --form-type 8-K

# 关联分析
python ~/.claude/skills/fincept-news-intel/scripts/cli.py correlate AAPL

# 财报电话会
python ~/.claude/skills/fincept-news-intel/scripts/cli.py earnings AAPL --quarter Q1-2024
```

## 天龙岗位协同

| 岗位 | 使用场景 |
|------|---------|
| **62-02 行业研究员** | 新闻情感 + 主题聚类 → 行业趋势报告 |
| **64-01 量化研究员** | SEC 公告 + 财报电话会 → 因子构建 |
| **32-01 市场研究** | 关联分析 + 新闻聚类 → 竞争情报 |
| **60-01 投资总监** | 情感分析 + SEC 追踪 → 投资决策支持 |

## 文件结构

```
fincept-news-intel/
├── SKILL.md           # 技能文档
├── scripts/
│   ├── __init__.py
│   ├── client.py      # NewsIntelligence 主类
│   ├── sentiment.py   # 情感分析模块
│   ├── clustering.py  # 主题聚类模块
│   ├── correlation.py # 关联分析模块
│   ├── sec_filings.py # SEC 公告模块
│   └── cli.py         # CLI 入口
├── requirements.txt
└── README.md
```

## 版本

- **V1.0** (2026-04-27): 初始版本
