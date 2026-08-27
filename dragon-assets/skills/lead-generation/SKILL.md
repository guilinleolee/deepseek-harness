---
license: UNKNOWN
name: lead-generation
description: 线索生成技能 - 支持Google Maps、LinkedIn、Boss直聘、小红书、抖音等多平台的B2B/B2C线索采集。基于天龙自建采集系统，零API费用。
github_repo: apify/agent-skills
github_hash: 28e08de7b3e6da475eeeb985d57e7f51bc76c6c2
last_updated: 2026-04-25
source_type: derived
tags: [线索生成, B2B, 销售线索, 客户挖掘, LinkedIn, Google Maps]
triggers: ["lead generation", "Lead Generation - 线索生成技能"]
---

# Lead Generation - 线索生成技能

基于天龙dragon-scraper + agent-reach技术栈构建的专业线索生成技能，无需第三方API费用。

## 核心能力

| 功能 | 描述 | 平台支持 |
|------|------|---------|
| **商家发现** | 按地点/行业搜索商家，获取联系方式 | Google Maps, 大众点评 |
| **企业查询** | 公司信息、联系方式、员工规模 | LinkedIn, 天眼查 |
| **人才挖掘** | 职位搜索、候选人发现 | LinkedIn, Boss直聘 |
| **社媒线索** | 潜在客户发现、KOL挖掘 | 小红书, 抖音, Instagram |

## 与Apify对比

| 维度 | Apify lead-generation | 天龙 lead-generation |
|------|----------------------|---------------------|
| **成本** | 按结果付费（$0.001-0.01/条） | **零API费用** |
| **国内平台** | 无Boss直聘、小红书 | **全面支持** |
| **数据隐私** | 经Apify云端 | **完全本地** |
| **定制化** | 受限于Actor | **完全可控** |

## 支持平台

### 国际平台

| 平台 | 数据类型 | 技术方案 |
|------|---------|---------|
| Google Maps | 商家、地址、电话、评分 | dragon-scraper |
| LinkedIn | 公司、职位、人员 | agent-reach + Cookie |
| Instagram | 用户、帖子、互动 | dragon-scraper |
| TikTok | 创作者、视频、粉丝 | dragon-scraper |
| Facebook | 页面、帖子、评论 | dragon-scraper |
| YouTube | 频道、视频、订阅者 | agent-reach |

### 国内平台

| 平台 | 数据类型 | 技术方案 |
|------|---------|---------|
| Boss直聘 | 职位、公司、HR | agent-reach |
| 小红书 | 用户、笔记、粉丝 | agent-reach + Cookie |
| 抖音 | 创作者、视频、粉丝 | agent-reach + Cookie |
| 大众点评 | 商家、评价、联系方式 | dragon-scraper |
| 天眼查 | 公司、法人、联系方式 | dragon-scraper |

## 工作流

### Workflow 1: 本地商家发现（Google Maps/大众点评）

```
任务进度:
- [ ] Step 1: 用户输入地点和行业关键词
- [ ] Step 2: 系统选择平台（国内=大众点评，海外=Google Maps）
- [ ] Step 3: 执行商家搜索
- [ ] Step 4: 提取商家信息（名称、地址、电话、评分）
- [ ] Step 5: 导出线索列表（CSV/JSON）
```

### Workflow 2: 企业决策人挖掘（LinkedIn）

```
任务进度:
- [ ] Step 1: 用户输入目标公司或行业
- [ ] Step 2: 搜索公司和员工
- [ ] Step 3: 筛选决策人（CEO/总监/经理）
- [ ] Step 4: 提取联系方式（需付费工具配合）
- [ ] Step 5: 生成线索报告
```

### Workflow 3: KOL/创作者发现（小红书/抖音/Instagram）

```
任务进度:
- [ ] Step 1: 用户输入行业关键词或标签
- [ ] Step 2: 搜索相关创作者
- [ ] Step 3: 分析粉丝数、互动率、内容质量
- [ ] Step 4: 筛选符合条件的KOL
- [ ] Step 5: 生成KOL名单和联系方式
```

### Workflow 4: 招聘线索（Boss直聘/LinkedIn）

```
任务进度:
- [ ] Step 1: 用户输入职位关键词
- [ ] Step 2: 搜索相关职位和公司
- [ ] Step 3: 提取HR信息和公司详情
- [ ] Step 4: 分析招聘需求
- [ ] Step 5: 生成招聘线索报告
```

## 使用方式

### 自然语言调用

```bash
[@销售管理] 找出上海所有咖啡店老板的联系方式
[@招聘配置师] 搜索北京招聘Python开发的HR
[@社媒运营] 找健身领域的小红书KOL，粉丝1-10万
```

### 命令调用

```bash
/lead-gen local --location "上海" --industry "咖啡店"
/lead-gen company --keyword "科技公司" --platform linkedin
/lead-gen kol --keyword "健身" --platform xiaohongshu --followers "1万-10万"
/lead-gen hr --keyword "Python开发" --location "北京"
```

## 输出格式

| 格式 | 说明 |
|------|------|
| `quick` | 快速预览（前5条） |
| `json` | JSON格式导出 |
| `csv` | CSV格式导出（CRM兼容） |
| `enrich` | 增强线索（额外联系方式） |

## 输出字段

### 商家线索

| 字段 | 说明 |
|------|------|
| name | 商家名称 |
| address | 地址 |
| phone | 电话 |
| rating | 评分 |
| reviews | 评论数 |
| category | 分类 |
| website | 网站 |

### KOL线索

| 字段 | 说明 |
|------|------|
| username | 用户名 |
| followers | 粉丝数 |
| engagement | 互动率 |
| niche | 领域 |
| contact | 联系方式（如有） |

## 配置文件

```json
// ~/.claude/skills/lead-generation/config.json
{
  "platforms": {
    "googleMaps": {
      "enabled": true,
      "region": "cn"
    },
    "linkedin": {
      "enabled": true,
      "useCookie": true
    },
    "bossZhipin": {
      "enabled": true
    },
    "xiaohongshu": {
      "enabled": true,
      "useCookie": true
    }
  },
  "filters": {
    "minFollowers": 1000,
    "maxFollowers": 100000,
    "minRating": 4.0
  },
  "storage": {
    "type": "sqlite",
    "path": "~/.claude/data/leads.db"
  }
}
```

## 与天龙岗位协同

| 岗位 | 使用场景 |
|------|---------|
| **38-02 销售管理** | 客户挖掘、线索生成 |
| **93-01 招聘配置师** | HR线索、候选人发现 |
| **35-01 数字营销** | KOL发现、合作伙伴挖掘 |
| **35-02 社媒运营** | 创作者合作、达人营销 |
| **40-01 用户增长** | 潜在用户发现 |

## 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                   Lead Generation 架构                       │
├─────────────────────────────────────────────────────────────┤
│  调度层 - 天龙任务管理器                                      │
│  - 线索去重                                                  │
│  - 增强查询                                                  │
├─────────────────────────────────────────────────────────────┤
│  采集层 - dragon-scraper + agent-reach                       │
│  - 平台适配器                                                │
│  - 反爬策略                                                  │
│  - Cookie管理                                                │
├─────────────────────────────────────────────────────────────┤
│  分析层 - Claude API                                         │
│  - 线索评分                                                  │
│  - 匹配度分析                                                │
├─────────────────────────────────────────────────────────────┤
│  存储层 - SQLite                                             │
│  - 线索数据库                                                │
│  - 去重索引                                                  │
└─────────────────────────────────────────────────────────────┘
```

## 线索增强

通过第三方服务增强线索质量：

| 服务 | 功能 | 成本 |
|------|------|------|
| Hunter.io | 邮箱验证 | 免费额度 |
| Clearbit | 公司信息增强 | 付费 |
| Apollo.io | 联系方式查找 | 免费额度 |

## 常见问题

### Q: 如何避免被封？
A: 系统内置请求间隔随机化和代理支持，建议配置代理池。

### Q: 如何处理重复线索？
A: 系统自动去重，基于名称+电话/邮箱组合。

### Q: 数据可以导入CRM吗？
A: 支持导出CSV格式，兼容Salesforce、HubSpot、国产CRM。

## 🆕 V1.1 天龙增强版说明

本技能为天龙增强版，在原上游apify-lead-generation基础上增强了以下能力：

| 维度 | 原上游版本 | 天龙增强版 |
|------|-----------|-----------|
| **国内平台** | 有限支持 | **全面支持（小红书/Boss直聘）** |
| **数据隐私** | 经Apify云端 | **完全本地** |
| **定制化** | 受限于Actor | **完全可控** |
| **技术栈** | Apify官方 | **dragon-scraper + agent-reach** |

### 远程仓库结构差异说明

远程仓库(apify/agent-skills)采用`apify-ultimate-scraper`单一技能结构，而非本地的独立技能文件夹结构。本地版本为天龙自建的完整实现，保留全部中文平台支持。

## 更新日志

- v1.1.0 (2026-04-25) - 天龙增强版确认，保留中文平台支持
- v1.0.0 (2026-03-09) - 初始版本，支持Google Maps/LinkedIn/Boss直聘/小红书

## 参考

- 上游技能: [apify-lead-generation](https://github.com/apify/agent-skills/tree/main/skills/apify-lead-generation)
- 技术基础: [dragon-scraper](../dragon-scraper/), [agent-reach](../agent-reach/)
- 天龙版本: V8.98 (2026-04-25)