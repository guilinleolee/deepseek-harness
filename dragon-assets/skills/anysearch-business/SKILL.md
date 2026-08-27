---
license: UNKNOWN
name: anysearch-business
description: AnySearch商业市场调研专用封装 - 市场规模/竞争格局/商业模式/渠道策略深度调研
version: 1.0.0
author: 天龙引擎 AnySearch团队
integrations: - anysearch (search/batch_search/extract/list_domains)
- grill-me (追问框架)
triggers: ["anysearch business", "市场规模估算"]
---

## L0: 一句话描述

商业市场调研SKILL，支持市场规模分析、竞争格局研究、商业模式评估、渠道策略调研。

## L1: 使用场景 (50-100字)

适用场景：市场规模估算、竞争格局分析、商业模式评估、渠道策略研究。
触发条件：用户提到「市场调研」「竞争分析」「商业模式」「渠道策略」「市场机会」时激活。
与AnySearch三层调研形成双轨：AnySearch快速摸底 → Deep Research深度研究。

## L2: 详细文档

### 核心能力

| 能力 | 命令 | 说明 |
|------|------|------|
| 市场规模 | `market_size_search` | TAM/SAM/SOM三层估算 |
| 竞争格局 | `competitor_search` | 竞品对比/市场份额/竞争壁垒 |
| 商业模式 | `business_model_search` | 盈利模式/单位经济/变现路径 |
| 渠道策略 | `channel_search` | 渠道分析/获客成本/转化漏斗 |
| 批量商业调研 | `batch_business` | 多主题并发商业调研 |
| 网页内容提取 | `business_extract` | 商业页面深度内容 |

### 商业领域参数模板

```bash
# 市场规模估算
TOPIC="AI Agent市场"
node <anysearch>/scripts/anysearch_cli.js search \
  "${TOPIC} 市场规模 增长率 TAM SAM SOM" \
  --domain business \
  --content_types web,news \
  --max_results 8 \
  --freshness year

# 竞争格局分析
node <anysearch>/scripts/anysearch_cli.js search \
  "${TOPIC} 竞争格局 市场份额 主要玩家 竞争壁垒" \
  --domain business \
  --max_results 10 \
  --freshness month

# 商业模式评估
node <anysearch>/scripts/anysearch_cli.js batch_search \
  --queries '[{"query":"AI Agent商业模式 盈利模式 单位经济","domain":"business","max_results":5},{"query":"SaaS定价策略 MRR ARR 续费率","domain":"business","max_results":5}]'

# 批量商业调研（5个并发）
node <anysearch>/scripts/anysearch_cli.js batch_search \
  --queries '[{"query":"市场规模估算","domain":"business","max_results":5},{"query":"竞争格局分析","domain":"business","max_results":5},{"query":"商业模式评估","domain":"business","max_results":5}]'
```

### 商业领域查询词模板（关联数组）

| 子领域 | 查询模板 |
|--------|---------|
| `size` | "${TOPIC} 市场规模 增长率 TAM SAM SOM 预测" |
| `competitor` | "${TOPIC} 竞争格局 市场份额 主要玩家 竞争壁垒" |
| `model` | "${TOPIC} 商业模式 盈利模式 定价策略 单位经济 LTV CAC" |
| `channel` | "${TOPIC} 渠道策略 获客成本 转化率 用户增长" |
| `trend` | "${TOPIC} 行业趋势 发展动态 市场机会 新兴赛道" |
| `regulation` | "${TOPIC} 政策法规 监管动态 合规要求 行业标准" |

### 商业调研三步工作流

```
Step 1: 快速摸底
  → market_size_search "主题" --max_results 10
  → 确认市场规模量级和竞争格局

Step 2: 深度采集
  → batch_business ["主题市场规模","主题竞争格局","主题商业模式","主题渠道策略"]
  → 批量采集多维商业数据

Step 3: 内容提取
  → business_extract "高价值URL"
  → 深度提取全文内容用于报告
```

### 与62-02行业研究员协同

```
62-02行业研究员
  ├─► anysearch-academic → 学术论文调研
  ├─► anysearch-business → 商业市场调研
  └─► anysearch-finance  → 融资投资调研
```

### 天龙岗位升级

| 岗位 | 版本 | 新增能力 |
|------|------|---------|
| 62-02 行业研究员 | V10.2 → V10.3 | 商业市场批量调研 + 竞争格局分析 |
| 60-01 投资总监 | V2.1 → V2.2 | 市场规模估算 + 商业模式评估 |
| 01调研师 | V8.89 → V8.90 | 商业领域快速摸底 |
| 32-01 市场研究 | V10.2 → V10.3 | 批量市场调研 + 竞争分析 |

### 质量检查点

| 检查点 | 通过条件 |
|--------|---------|
| 市场规模 | 返回 ≥3 条数据源（含定量数据） |
| 竞争覆盖 | 主要竞品 ≥3 家分析 |
| 时效性 | 优先 1年内数据 |
| 来源权威 | 包含 McKinsey/Bain/BCG/艾瑞/36kr 等 |
| 边界覆盖 | 市场规模+竞争格局+商业模式+渠道策略 四维覆盖 |