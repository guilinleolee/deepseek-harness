---
name: comment-analyzer
description: 当用户使用 `/评论分析` 命令，或需要分析热门内容评论、提取用户观点、了解情感倾向时使用此skill。自动分析微博、小红书、抖音、B站、知乎、公众号、视频号等平台的内容评论，提取情感倾向、高频话题、用户画像和关键观点，生成交互式HTML报告。
github_url: 
github_hash: 
license: MIT
metadata: 
version: 1.0.0
author: Claude
created: 2026-02-26
category: analytics
domain: social-media-analysis
updated: 2025-01-15
python-tools: sentiment_analyzer.py, topic_extractor.py, viewpoint_summarizer.py
tech-stack: MCP-Chrome-DevTools, NLP, data-visualization
triggers: ["comment analyzer", "评论分析助手"]
---
# 评论分析助手

## Overview

通过系统化分析各大内容平台的热门内容评论，提取用户情感倾向、高频话题、关键观点和用户画像，生成可交互的HTML分析报告，帮助内容创作者和运营者快速了解用户反馈。

## When to Use

### 触发条件

**使用Slash Command（推荐）：**
```
/评论分析 https://weibo.com/7762107285/QkRZnufTd
/评论分析 https://www.xiaohongshu.com/explore/12345
```

**自然语言触发：**
- "分析一下这个链接的评论"
- "提取这篇内容的评论观点"
- "看看这个内容的评论区在说什么"
- "分析微博/小红书的用户反馈"

### 适用场景

- 内容发布后的用户反馈分析
- 竞品内容的用户情绪调研
- 用户痛点和需求挖掘
- 舆情监控和危机预警
- 内容优化方向参考

### 何时不使用

- 纯粹搜索内容（使用WebSearch即可）
- 分析国外平台内容
- 不需要详细分析的简单统计

## Workflow

### 完整工作流程

```
第一步：输入内容链接
    ↓
第二步：AI智能分析
    ↓
第三步：生成分析报告
```

### 详细步骤

#### 步骤1：输入内容链接
从slash命令或自然语言中提取链接
```
/评论分析 https://weibo.com/7762107285/QkRZnufTd
```

#### 步骤2：平台识别
```bash
# 识别平台类型
weibo.com → 微博
xiaohongshu.com → 小红书
douyin.com → 抖音
bilibili.com → B站
zhihu.com → 知乎
mp.weixin.qq.com → 公众号
```

#### 步骤3：爬取评论数据
```bash
# 使用MCP Chrome DevTools或API拦截
# 微博优先使用API拦截（绕过虚拟滚动）
# 其他平台使用DOM选择器
python scripts/core.py <URL>
```

#### 步骤4：AI智能分析（5个维度）
参考 [references/sentiment_framework.md](references/sentiment_framework.md)

## Quick Reference

### 支持平台

| 平台 | 域名 | 特殊要求 | 数据来源 |
|------|------|---------|---------|
| **微博** | weibo.com, m.weibo.cn, t.cn | 需登录 | API拦截优先 |
| 小红书 | xiaohongshu.com | 需登录 | DOM选择器 |
| 抖音 | douyin.com | 需登录 | DOM选择器 |
| B站 | bilibili.com | 部分需登录 | API/DOM |
| 知乎 | zhihu.com | 需登录 | DOM选择器 |
| 公众号 | mp.weixin.qq.com | 无 | DOM选择器 |
| 视频号 | weixin.qq.com | 需微信环境 | DOM选择器 |

### 分析维度

| 维度 | 输出内容 | 技术方案 |
|------|---------|---------|
| **情感倾向分析** | 整体倾向、分布、时间线 | 词典匹配+规则引擎 |
| **高频话题提取** | TOP50关键词、主题聚类 | TF-IDF+LDA |
| **用户观点挖掘** | 核心观点、支持度、典型评论 | TextRank+聚类 |
| **评论质量评估** | 高/低质量评论列表 | 信息密度检测 |
| **趋势分析**（可选） | 主题/情感时间趋势 | 时间序列分析 |

### 四分类情感体系

| 分类 | 描述 | 关键词 | 颜色 |
|------|------|--------|------|
| 正面 | 支持、喜爱、赞扬 | 支持、喜欢、棒、优秀、推荐 | #4CAF50（绿色） |
| 建议 | 理性反馈、改进意见 | 建议、希望、可以、改进 | #2196F3（蓝色） |
| 中性 | 询问、描述、观望 | 什么、如何、为什么 | #FFC107（黄色） |
| 负面 | 质疑、批评、不满 | 差、失望、批评、不满 | #F44336（红色） |

## Output Format

### 报告文件
**位置：** `~/comment-analysis-reports/[平台]-[时间戳].html`
**内容结构：**
1. **统计概览** - 评论总数、情感分布、核心指标
2. **情感分析** - 饼图、词云、时间线
3. **话题分析** - 关键词列表、主题聚类图
4. **观点挖掘** - 核心观点列表、支持度分布
5. **质量评估** - 高质量评论、质量分布图
6. **趋势分析**（可选）- 主题/情感时间趋势
7. **行动建议** - 基于分析结果的改进建议

## Tips

### 使用技巧

1. **微博分析优先**：微博支持API拦截，速度最快、数据最完整
2. **登录提示**：大部分平台需要登录，系统会提示45秒扫码时间
3. **评论数量**：默认爬取500条评论，可通过参数调整
4. **报告分享**：HTML报告可直接在浏览器中打开分享

### 常见问题

**Q: 为什么有些平台需要登录？**
A: 大部分社交媒体平台需要登录才能查看完整评论，系统会自动提示登录步骤。

**Q: 分析需要多长时间？**
A: 通常3-5分钟（500条评论），微博使用API拦截可缩短至1-2分钟。

**Q: 支持哪些评论格式？**
A: 支持所有可见评论，包括回复、二级评论等。

**Q: 报告可以导出吗？**
A: HTML报告可直接保存，未来版本将支持PDF导出。

## Example Usage

### 示例1：分析微博热点
```bash
/评论分析 https://weibo.com/7762107285/QkRZnufTd

# 输出：
# ✅ 平台识别：微博
# ⏳ 正在爬取评论... (0/500)
# ✅ 成功爬取 500 条评论
# ⏳ 正在进行情感分析...
# ⏳ 正在生成报告...
# ✅ 分析完成！
#
# 报告路径：~/comment-analysis-reports/微博-20250115-123456.html
#
# 🎯 核心洞察：
# • 情感倾向：正面 58.1%、建议 21.5%、中性 12.5%、负面 7.9%
# • 核心话题：支持(120次)、理性(95次)、期待(80次)
# • 主要观点：70%用户支持该观点
```

### 示例2：分析小红书种草笔记
```bash
/评论分析 https://www.xiaohongshu.com/explore/12345

# 分析小红书用户对产品的真实反馈
# 提取用户关注的产品特性、使用体验、购买建议
```

## Technical Details

### 技术栈
- **爬虫**：MCP Chrome DevTools（mcp__chrome-devtools__*）
- **情感分析**：词典匹配 + 规则引擎
- **话题提取**：TF-IDF + jieba分词
- **观点提炼**：TextRank算法
- **前端报告**：HTML5 + Tailwind CSS + Chart.js

### 依赖工具
- **MCP工具**：mcp__chrome-devtools__*（浏览器自动化）
- **Python库**：jieba（分词）、sklearn（TF-IDF）
- **前端库**：Tailwind CSS（CDN）、Chart.js（CDN）

## References

- [references/platform_strategies.md](references/platform_strategies.md) - 各平台抓取策略
- [references/sentiment_framework.md](references/sentiment_framework.md) - 情感分析理论框架
- [references/user_persona_templates.md](references/user_persona_templates.md) - 用户画像模板

## Configuration

配置文件：[config/comment-analyzer.json](config/comment-analyzer.json)

主要参数：
- `scraper.mode`: 'mcp' | 'puppeteer' | 'auto'
- `scraper.max_scroll_count`: 100（最大滚动次数）
- `analysis.min_comments`: 10（最少评论数）
- `output.auto_open`: true（自动打开报告）

#### Evolution Pattern (Maintenance)

To preserve custom improvements when a core skill is upgraded, avoid editing `SKILL.md` directly for individual modifications. Instead:

1. Create or update an `evolution.json` file in the skill's root directory.
2. Store modification suggestions, custom rules, or evolved logic there.
3. This ensures that your custom "evolutions" are preserved even if the base `SKILL.md` is replaced during an upgrade.
