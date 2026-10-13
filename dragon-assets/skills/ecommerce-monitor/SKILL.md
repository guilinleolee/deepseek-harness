---
license: UNKNOWN
name: ecommerce-monitor
description: 电商价格监控技能 - 支持Amazon、京东、淘宝、拼多多、eBay等50+平台的价格追踪、评论分析、卖家发现。基于天龙自建采集系统，零API费用。
github_repo: apify/agent-skills
github_hash: 28e08de7b3e6da475eeeb985d57e7f51bc76c6c2
last_updated: 2026-04-25
source_type: derived
tags: [电商, 价格监控, 评论分析, 竞品追踪, Amazon, 京东, 淘宝]
triggers: ["ecommerce monitor", "Ecommerce Monitor - 电商价格监控技能"]
---

# Ecommerce Monitor - 电商价格监控技能

基于天龙dragon-scraper + agent-reach技术栈构建的专业电商监控技能，无需第三方API费用。

## 核心能力

| 功能 | 描述 | 平台支持 |
|------|------|---------|
| **价格监控** | 实时价格追踪、历史价格对比、降价提醒 | Amazon, 京东, 淘宝, 拼多多, eBay, Walmart |
| **评论分析** | 情感分析、关键词提取、趋势识别 | 全平台 |
| **卖家发现** | 店铺发现、卖家评估、授权经销商验证 | Amazon, 淘宝, 京东 |
| **库存监控** | 库存状态追踪、缺货提醒 | Amazon, 京东 |

## 与Apify对比

| 维度 | Apify ecommerce | 天龙 ecommerce-monitor |
|------|-----------------|----------------------|
| **成本** | 按结果付费（$0.001-0.01/条） | **零API费用** |
| **数据隐私** | 经Apify云端 | **完全本地** |
| **国内平台** | 有限支持 | **全面支持（京东/淘宝/拼多多）** |
| **定制化** | 受限于Actor | **完全可控** |

## 支持平台

### 国际平台

| 平台 | 数据类型 | 技术方案 |
|------|---------|---------|
| Amazon | 产品、价格、评论、卖家 | dragon-scraper + Playwright |
| eBay | 商品、价格、卖家 | dragon-scraper |
| Walmart | 产品、价格、库存 | dragon-scraper |
| IKEA | 产品、价格、库存 | dragon-scraper |

### 国内平台

| 平台 | 数据类型 | 技术方案 |
|------|---------|---------|
| 京东 | 产品、价格、评论、店铺 | dragon-scraper + Playwright |
| 淘宝 | 商品、价格、评价、卖家 | dragon-scraper + Cookie |
| 淘宝 | 商品、价格、评价、卖家 | dragon-scraper + Cookie |
| 拼多多 | 商品、价格、销量 | dragon-scraper |

## 工作流

### Workflow 1: 价格监控

```
任务进度:
- [ ] Step 1: 用户输入产品URL或关键词
- [ ] Step 2: 系统识别平台，选择对应模板
- [ ] Step 3: 执行价格采集
- [ ] Step 4: 与历史价格对比，生成报告
- [ ] Step 5: 可选：设置降价提醒
```

### Workflow 2: 评论分析

```
任务进度:
- [ ] Step 1: 用户输入产品URL
- [ ] Step 2: 采集评论数据（支持分页）
- [ ] Step 3: 情感分析（正面/负面/中性）
- [ ] Step 4: 关键词提取和趋势识别
- [ ] Step 5: 生成评论洞察报告
```

### Workflow 3: 卖家发现

```
任务进度:
- [ ] Step 1: 用户输入产品关键词或品牌
- [ ] Step 2: 在Google Shopping搜索跨店铺卖家
- [ ] Step 3: 提取卖家信息、价格、评分
- [ ] Step 4: 识别未授权经销商
- [ ] Step 5: 生成卖家情报报告
```

## 使用方式

### 自然语言调用

```bash
[@电商运营] 监控这款Amazon产品的价格变化
[@电商运营] 分析京东这个产品的评论情感
[@电商运营] 找出淘宝上卖我们品牌的所有店铺
```

### 命令调用

```bash
/ecommerce-monitor price --url "https://www.amazon.com/dp/B09V3KXJPB"
/ecommerce-monitor reviews --url "https://item.jd.com/100012345.html" --analysis
/ecommerce-monitor sellers --keyword "品牌名" --platform taobao
```

## 输出格式

| 格式 | 说明 |
|------|------|
| `quick` | 快速预览（前5条） |
| `json` | JSON格式导出 |
| `csv` | CSV格式导出（Excel兼容） |
| `report` | 分析报告（Markdown） |

## 配置文件

```json
// ~/.claude/skills/ecommerce-monitor/config.json
{
  "platforms": {
    "amazon": {
      "enabled": true,
      "region": "com",
      "useProxy": true
    },
    "jd": {
      "enabled": true,
      "useCookie": true
    },
    "taobao": {
      "enabled": true,
      "useCookie": true
    }
  },
  "monitoring": {
    "interval": "daily",
    "priceAlert": {
      "enabled": true,
      "threshold": 10
    }
  },
  "storage": {
    "type": "sqlite",
    "path": "~/.claude/data/ecommerce.db"
  }
}
```

## 与天龙岗位协同

| 岗位 | 使用场景 |
|------|---------|
| **45-01 电商运营** | 价格监控、评论分析、竞品追踪 |
| **32-02 竞品分析** | 竞品定价策略、评论对比 |
| **38-02 销售管理** | 渠道发现、经销商管理 |
| **30-01 营销总监** | 品牌保护、未授权销售检测 |

## 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                   Ecommerce Monitor 架构                      │
├─────────────────────────────────────────────────────────────┤
│  调度层 - 天龙任务管理器                                      │
│  - 定时监控任务                                              │
│  - 降价提醒推送                                              │
├─────────────────────────────────────────────────────────────┤
│  采集层 - dragon-scraper + agent-reach                       │
│  - 平台适配器（Amazon/京东/淘宝等）                           │
│  - 反爬策略                                                  │
│  - Cookie管理                                                │
├─────────────────────────────────────────────────────────────┤
│  分析层 - Claude API                                         │
│  - 情感分析                                                  │
│  - 关键词提取                                                │
│  - 趋势识别                                                  │
├─────────────────────────────────────────────────────────────┤
│  存储层 - SQLite                                             │
│  - 价格历史                                                  │
│  - 评论数据                                                  │
│  - 卖家信息                                                  │
└─────────────────────────────────────────────────────────────┘
```

## 常见问题

### Q: 如何处理登录验证？
A: 国内平台（淘宝/京东/拼多多）需要配置Cookie。使用 `--login` 参数打开浏览器手动登录。

### Q: 如何设置降价提醒？
A: 在配置文件中启用 `priceAlert`，设置阈值百分比。

### Q: 数据存储在哪里？
A: 默认存储在 `~/.claude/data/ecommerce.db` SQLite数据库中。

## 🆕 V1.1 天龙增强版说明

本技能为天龙增强版，在原上游apify-ecommerce基础上增强了以下能力：

| 维度 | 原上游版本 | 天龙增强版 |
|------|-----------|-----------|
| **国内平台** | 有限支持 | **全面支持（京东/淘宝/拼多多）** |
| **数据隐私** | 经Apify云端 | **完全本地** |
| **定制化** | 受限于Actor | **完全可控** |
| **技术栈** | Apify官方 | **dragon-scraper + agent-reach** |

### 远程仓库结构差异说明

远程仓库(apify/agent-skills)采用`apify-ultimate-scraper`单一技能结构，而非本地的独立技能文件夹结构。本地版本为天龙自建的完整实现，保留全部中文平台支持。

## 更新日志

- v1.1.0 (2026-04-25) - 天龙增强版确认，保留中文平台支持
- v1.0.0 (2026-03-09) - 初始版本，支持Amazon/京东/淘宝/拼多多

## 参考

- 上游技能: [apify-ecommerce](https://github.com/apify/agent-skills/tree/main/skills/apify-ecommerce)
- 技术基础: [dragon-scraper](../dragon-scraper/)
- 天龙版本: V8.98 (2026-04-25)