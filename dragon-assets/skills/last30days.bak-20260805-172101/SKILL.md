---
license: UNKNOWN
name: last30days
description: Research any topic from the last 30 days across 10+ platforms (Reddit, X, YouTube, TikTok, Instagram, Hacker News, Polymarket, Bluesky, Truth Social, Web). Provides time-boxed research with relevance scoring.
github_repo: mvanhorn/last30days-skill
github_hash: d1823a2d05d6eb1b701ec176e8f937f4cb27e596
last_updated: 2026-04-25
source_type: derived
version: 2.9.5
argument-hint: last30 AI video tools, last30 best project management tools, last30 cursor vs windsurf
allowed-tools: Bash, Read, Write, AskUserQuestion, WebSearch
user-invocable: true
metadata: 
openclaw: 
requires: 
env: [SCRAPECREATORS_API_KEY]
optionalEnv: [OPENAI_API_KEY, XAI_API_KEY, BRAVE_API_KEY, AUTH_TOKEN, CT0, BSKY_HANDLE, BSKY_APP_PASSWORD, TRUTHSOCIAL_TOKEN, APIFY_API_TOKEN]
triggers: ["last30days", "last30days - 30天时效性研究技能"]
---

# last30days - 30天时效性研究技能

## 核心价值

填补大语言模型在**时效性信息**方面的空白，让AI能够回答"最近30天发生了什么"这类问题。

## 平台覆盖（10+）

| 平台 | 数据类型 | 认证方式 | 免费 |
|------|---------|---------|------|
| **Reddit** | 帖子+评论+互动 | ScrapeCreators/OpenAI | 部分免费 |
| **X/Twitter** | 推文+转发+点赞 | xAI API/Token | 部分免费 |
| **YouTube** | 视频+字幕+观看量 | yt-dlp本地 | ✅ |
| **TikTok** | 视频+字幕+观看量 | ScrapeCreators | 部分免费 |
| **Instagram Reels** | 视频+字幕+观看量 | ScrapeCreators | 部分免费 |
| **Hacker News** | 帖子+评论+积分 | Algolia API | ✅ |
| **Polymarket** | 预测市场赔率 | Gamma API | ✅ |
| **Bluesky** | 帖子+互动 | App Password | ✅ |
| **Truth Social** | 帖子+互动 | Bearer Token | 部分 |
| **Web** | 博客/新闻/文档 | Brave/OpenRouter | 部分 |

## 使用方式

```bash
# 基础调用
/last30days AI code editors

# 对比研究
/last30days cursor vs windsurf

# 指定平台
/last30days --search=reddit,x,youtube best project management tools

# 深度模式
/last30days --deep what's new with Claude Code

# 快速模式
/last30days --quick trending AI tools
```

## 执行流程

### Step 0: 解析用户意图
提取研究主题和查询类型：
- TOPIC = 研究主题
- TARGET_TOOL = 目标工具（如"Cursor"）
- QUERY_TYPE = PROMPTING|RECOMMENDATIONS|NEWS|COMPARISON|GENERAL

### Step 0.5: 解析X账号（如适用）
使用WebSearch查找官方X账号（如@cursor_ai）

### Step 1: 运行研究脚本
```bash
python3 scripts/last30days.py "$TOPIC" --emit=compact
```

### Step 2: WebSearch补充
根据QUERY_TYPE选择搜索词进行补充研究

### Step 3: 综合分析
权重分配：Reddit/X > YouTube/TikTok > Web
引用优先级：@handle > r/subreddit > 频道名 > Web

### Step 4: 输出报告
生成Markdown报告并邀请用户进一步探索

## 三维评分系统

```
score = relevance * 0.4 + recency * 0.3 + engagement * 0.3

# relevance: 标题/内容与主题的相关性（0-100）
# recency: 发布时间距今天数（30天=0分，今天=100分）
# engagement: 互动指标归一化（点赞/评论/转发）
```

## API密钥配置

### 必需
```bash
export SCRAPECREATORS_API_KEY="your-key"  # 100免费额度
```

### 可选（增强功能）
```bash
export OPENAI_API_KEY="your-key"      # Reddit搜索回退
export XAI_API_KEY="your-key"         # X搜索
export BRAVE_API_KEY="your-key"       # Web搜索
```

## 与天龙引擎协同

| 天龙Skill | 协同方式 |
|-----------|---------|
| **deep-research** | last30days作为Step 0时效性预调研 |
| **Agent-Reach** | last30days并行调用Agent-Reach |
| **xiaohongshu-cli** | last30days触发CLI深度采集 |
| **swarm-intelligence** | last30days作为舆情输入源 |

## 适用场景

1. **产品研究**: "最近30天哪个AI编辑器最火？"
2. **趋势追踪**: "最近Claude Code有什么新功能？"
3. **对比分析**: "Cursor vs Windsurf对比"
4. **预测验证**: "Polymarket上的赔率变化"

## 输出文件

所有输出写入 `~/Documents/Last30Days/`：
- `report.md` - 人类可读报告
- `report.json` - 标准化JSON数据
- `last30days.context.md` - 紧凑上下文片段

## 来源

> [mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill) - Research any topic from the last 30 days