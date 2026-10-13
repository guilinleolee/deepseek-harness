---
license: UNKNOWN
name: requesthunt
description: >
ReScienceLab's multi-platform user research engine. Hunt user opinions, feedback,
and sentiment across Reddit, X/Twitter, GitHub, YouTube, LinkedIn, Amazon.
Use when: (1) user asks about user opinions or feedback on a product/topic,
(2) user asks for sentiment analysis on a brand or feature,
(3) user asks for competitor research across platforms,
(4) user asks to monitor user discussions or reviews.
Triggers: "用户研究", "用户反馈", "情感分析", "竞品监控", "用户评论",
"user research", "sentiment analysis", "competitor monitoring",
"user opinions", "product feedback", "review analysis".
天龙: version: V1.0
date: 2026-04-23
upstream: https://github.com/ReScienceLab/requesthunt
triggers: ["requesthunt", "RequestHunt - 多平台用户研究引擎"]
---

# RequestHunt - 多平台用户研究引擎

## L0: 一句话描述 (≤15字)
多平台用户研究，情感分析与竞品监控

## L1: 使用场景 (50-100字)
当你需要了解用户对产品/功能的真实反馈、分析品牌情感倾向、监控竞品在各平台的舆论动态、收集用户评论和意见时使用。支持Reddit/X等6大平台的结构化用户研究，输出可操作的洞察报告。与agent-reach互补：agent-reach负责数据采集，requesthunt负责用户洞察分析。

## L2: 详细文档

### 核心能力矩阵

| 平台 | 用户研究 | 内容采集 | 情感分析 | 竞品监控 |
|------|---------|---------|---------|---------|
| Reddit | ✅ | ✅ | ✅ | ✅ |
| X/Twitter | ✅ | ✅ | ✅ | ✅ |
| GitHub | ✅ | ✅ | ✅ | ✅ |
| YouTube | ✅ | ✅ | ✅ | ✅ |
| LinkedIn | ✅ | ✅ | ✅ | ✅ |
| Amazon | ✅ | ✅ | ✅ | ✅ |

### 与天龙现有技能协同

```
agent-reach (V8.19)     → 数据采集层（原始数据获取）
requesthunt (⭐新增)     → 洞察分析层（情感+意图+趋势）
deep-research (V8.59)    → 深度研究层（结构化报告）
MiroFish (V8.25)       → 预测推演层（舆情预测）

协同链路:
agent-reach采集 → requesthunt分析 → deep-research报告 → MiroFish预测
```

### 工作流程

```
1. 确定研究目标 → 选择平台 → 设置关键词
2. 并行采集数据 → 内容清洗 → 分类整理
3. 情感分析 → 意图识别 → 趋势提取
4. 生成洞察报告 → 竞品对比 → 行动建议
```

### 使用示例

```bash
# 用户反馈研究
requesthunt research "Claude AI" --platforms reddit,twitter --limit 100

# 情感分析
requesthunt sentiment "Tesla FSD" --platforms all --time-range 30d

# 竞品监控
requesthunt monitor "Apple,Samsung" --platforms twitter,reddit --alert on

# 用户评论采集
requesthunt reviews "MacBook Pro" --platform amazon --limit 200
```

### API参考

#### 研究模式
```bash
requesthunt research <query> --platforms <platforms> --limit <n>
```

#### 情感分析
```bash
requesthunt sentiment <topic> --platforms <platforms> --time-range <range>
```

#### 竞品监控
```bash
requesthunt monitor <brands> --platforms <platforms> --alert <on|off>
```

#### 评论采集
```bash
requesthunt reviews <product> --platform <platform> --limit <n>
```

### 平台特定功能

#### Reddit
- Subreddit搜索（按热门/最新/最佳排序）
- 评论树采集（深度最多10层）
- 用户画像提取（karma、活跃度，专业领域）
- 情感分布统计（正面/负面/中性比例）

#### X/Twitter
- 关键词追踪（历史30天）
- 转发路径分析
- KOL识别（按粉丝数和互动率）
- 情感时间线（按小时/天聚合）

#### GitHub
- Issue评论采集（按标签/状态筛选）
- Star历史分析（增长趋势）
- Contributor活跃度（提交频率）
- 情感倾向（功能请求vs Bug报告）

#### YouTube
- 视频评论采集（按点赞排序）
- 评论者画像（频道订阅数）
- 情感分段（0-10秒区间）
- 话题聚类（自动归纳主题）

#### LinkedIn
- 公司帖子采集（按行业/规模筛选）
- 互动分析（点赞/评论/分享）
- 评论意图分类（咨询/投诉/赞美）
- 竞品对比（多公司同时分析）

#### Amazon
- 产品评论采集（按评分/时间排序）
- 评论者历史（评论数、 Helpful票）
- 属性情感（价格/质量/服务/物流）
- 竞品比价（多产品横向对比）

### 输出格式

```json
{
  "query": "Claude AI",
  "platforms": ["reddit", "twitter"],
  "time_range": "30d",
  "total_results": 1250,
  "sentiment": {
    "positive": 0.62,
    "negative": 0.18,
    "neutral": 0.20
  },
  "top_themes": [
    {"theme": "代码生成能力强", "count": 342, "sentiment": "positive"},
    {"theme": "上下文窗口太小", "count": 156, "sentiment": "negative"}
  ],
  "kols": [
    {"platform": "twitter", "username": "...", "followers": 50000, "influence": 0.85}
  ],
  "insights": [
    "用户对代码生成能力满意度最高",
    "上下文长度是主要痛点"
  ]
}
```

### 局限性说明

1. **数据限制**：部分平台有API访问限制，结果可能不完整
2. **情感分析**：基于关键词和规则，准确率约75-85%
3. **语言支持**：主要优化英文，中文情感分析需额外配置
4. **实时性**：历史数据有延迟（通常1-24小时）

### 与天龙岗位协同

| 岗位 | requesthunt使用场景 |
|------|-------------------|
| 01调研师 | 用户调研、反馈收集、市场声音 |
| 32-01市场研究 | 竞品监控、行业舆情，品牌感知 |
| 32-02竞品分析 | 多平台竞品对比、用户评价分析 |
| 35-02社媒运营 | 用户反馈监控、危机预警 |
| 62-02行业研究员 | 行业趋势、用户偏好演变 |
