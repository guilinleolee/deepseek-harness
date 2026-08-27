---
license: UNKNOWN
name: anysearch-finance
description: AnySearch融资投资调研专用封装 - 融资动态/投资机构/估值分析/并购交易深度调研
version: 1.0.0
author: 天龙引擎 AnySearch团队
integrations: - anysearch (search/batch_search/extract/list_domains)
- grill-me (追问框架)
triggers: ["anysearch finance", "融资动态追踪"]
---

## L0: 一句话描述

融资投资调研SKILL，支持融资动态追踪、投资机构分析、估值建模、并购交易研究。

## L1: 使用场景 (50-100字)

适用场景：融资事件追踪、投资机构研究、估值对标分析、并购交易研究。
触发条件：用户提到「融资」「投资机构」「估值」「并购」「IPO」「PE/VC」时激活。
与AlphaGBM量化体系形成双轨：AnySearch快速摸底 → AlphaGBM量化分析。

## L2: 详细文档

### 核心能力

| 能力 | 命令 | 说明 |
|------|------|------|
| 融资动态 | `funding_search` | 融资事件/轮次/金额/投资方 |
| 投资机构 | `investor_search` | VC/PE投资偏好/portfolio/业绩 |
| 估值分析 | `valuation_search` | 估值模型/对标分析/倍数比较 |
| 并购交易 | `ma_search` | 并购事件/交易规模/整合效果 |
| 批量投资调研 | `batch_finance` | 多主题并发投资调研 |
| 网页内容提取 | `finance_extract` | 投资页面深度内容 |

### 金融投资参数模板

```bash
# 融资动态追踪
TOPIC="AI Agent创业公司"
node <anysearch>/scripts/anysearch_cli.js search \
  "${TOPIC} 融资 A轮 B轮 C轮 投资金额 投资方" \
  --domain finance \
  --content_types web,news \
  --max_results 10 \
  --freshness month

# 投资机构研究
node <anysearch>/scripts/anysearch_cli.js search \
  "红杉资本 高瓴资本 IDG 投资 AI领域 portfolio 最新动态" \
  --domain finance \
  --max_results 8 \
  --freshness quarter

# 估值对标分析
node <anysearch>/scripts/anysearch_cli.js batch_search \
  --queries '[{"query":"AI Agent公司估值 倍数 PS PE 对标","domain":"finance","max_results":5},{"query":"科技公司并购估值 交易倍数 历史案例","domain":"finance","max_results":5}]'

# 批量投资调研（5个并发）
node <anysearch>/scripts/anysearch_cli.js batch_search \
  --queries '[{"query":"融资动态追踪","domain":"finance","max_results":5},{"query":"投资机构分析","domain":"finance","max_results":5},{"query":"估值对标分析","domain":"finance","max_results":5},{"query":"并购交易研究","domain":"finance","max_results":5}]'
```

### 金融投资查询词模板（关联数组）

| 子领域 | 查询模板 |
|--------|---------|
| `funding` | "${TOPIC} 融资 投资金额 轮次 投资方 最新动态" |
| `investor` | "${TOPIC} VC PE 投资机构 投资偏好 portfolio 业绩" |
| `valuation` | "${TOPIC} 估值 估值倍数 PS PE 对标分析 溢价率" |
| `ma` | "${TOPIC} 并购 收购 交易规模 整合效果 战略价值" |
| `ipo` | "${TOPIC} IPO 上市 估值 市值 资本市场表现" |
| `market_cap` | "${TOPIC} 市值 市盈率 市销率 估值溢价" |

### 投资调研三步工作流

```
Step 1: 快速摸底
  → funding_search "主题" --max_results 10
  → 确认融资动态和投资机构分布

Step 2: 深度采集
  → batch_finance ["主题融资动态","主题投资机构","主题估值分析","主题并购研究"]
  → 批量采集多维投资数据

Step 3: 内容提取
  → finance_extract "高价值URL"
  → 深度提取全文用于AlphaGBM量化分析
```

### 与AlphaGBM量化体系协同

```
AlphaGBM量化体系
  ├─► anysearch-finance → 融资投资快速摸底
  ├─► FearScore恐慌指数 → 市场情绪量化
  ├─► G=B+M五维评分 → 基本面/动量双因子
  └─► Options Analysis → 期权组合评分
```

### 天龙岗位升级

| 岗位 | 版本 | 新增能力 |
|------|------|---------|
| 60-01 投资总监 | V2.1 → V2.2 | 融资动态追踪 + 估值对标分析 |
| 62-02 行业研究员 | V10.2 → V10.3 | 投资机构研究 + 并购交易分析 |
| 64-01 量化研究员 | V8.4 → V8.5 | 投资数据采集 + 量化因子构建 |
| 01调研师 | V8.89 → V8.90 | 投资领域快速摸底 |

### 质量检查点

| 检查点 | 通过条件 |
|--------|---------|
| 融资覆盖 | 返回 ≥5 条近期融资事件 |
| 投资机构 | 主要投资方 ≥3 家分析 |
| 估值数据 | 包含具体估值数字和倍数 |
| 时效性 | 优先 6个月内数据 |
| 来源权威 | 包含 Crunchbase/IT桔子/CVSource/36kr/财新 |
| 边界覆盖 | 融资+投资机构+估值+并购 四维覆盖 |