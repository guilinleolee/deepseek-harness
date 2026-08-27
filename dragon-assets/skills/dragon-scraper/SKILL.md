---
license: UNKNOWN
name: dragon-scraper
description: 天龙自建抓取系统 - 基于Crawlee+Playwright的多平台数据采集。支持Instagram、TikTok、YouTube、Twitter/X、电商平台等55+平台的自动化抓取。无需第三方API，完全自托管。
triggers: ["dragon scraper", "Dragon Scraper - 天龙自建抓取系统"]
---

# Dragon Scraper - 天龙自建抓取系统

基于Crawlee开源框架构建的专业级多平台抓取系统，无需依赖Apify等第三方服务。

## 核心优势

| 特性 | 说明 |
|------|------|
| **零API费用** | 完全自托管，无第三方费用 |
| **反爬能力** | Playwright + Stealth插件 + 代理轮换 |
| **智能解析** | LLM辅助结构化数据提取 |
| **队列管理** | 天龙任务管理器集成 |
| **断点续传** | SQLite持久化，支持中断恢复 |

## 前置条件

```bash
# 安装依赖
npm install crawlee playwright @anthropic-ai/sdk

# 安装Playwright浏览器
npx playwright install chromium

# 可选：安装代理支持
npm install proxy-chain
```

## 工作流

```
任务进度:
- [ ] Step 1: 分析目标平台，选择模板
- [ ] Step 2: 配置抓取参数（URL、选择器、分页）
- [ ] Step 3: 执行抓取
- [ ] Step 4: 数据解析与存储
- [ ] Step 5: 导出结果
```

## 支持平台

### 社交媒体平台

| 平台 | 模板 | 数据类型 |
|------|------|---------|
| Instagram | `instagram-profile` | 用户资料、帖子、评论 |
| TikTok | `tiktok-profile` | 视频、用户、评论 |
| Twitter/X | `twitter-profile` | 推文、用户、趋势 |
| YouTube | `youtube-channel` | 视频、评论、频道 |
| LinkedIn | `linkedin-company` | 公司、职位、人员 |
| Facebook | `facebook-page` | 页面、帖子、评论 |
| Reddit | `reddit-subreddit` | 帖子、评论、用户 |

### 电商平台

| 平台 | 模板 | 数据类型 |
|------|------|---------|
| Amazon | `amazon-product` | 产品、价格、评论 |
| eBay | `ebay-listing` | 商品、价格、卖家 |
| 京东 | `jd-product` | 产品、价格、评论 |
| 淘宝 | `taobao-product` | 商品、价格、评价 |
| 拼多多 | `pdd-product` | 商品、价格、销量 |

### 其他平台

| 平台 | 模板 | 数据类型 |
|------|------|---------|
| Google Maps | `google-maps` | 商家、评价、联系方式 |
| Google Search | `google-search` | 搜索结果、排名 |
| Booking.com | `booking-hotel` | 酒店、价格、评价 |
| TripAdvisor | `tripadvisor-venue` | 景点、餐厅、评价 |
| 小红书 | `xiaohongshu-note` | 笔记、用户、评论 |
| B站 | `bilibili-video` | 视频、评论、UP主 |

## 使用方式

### 方式1：自然语言调用

```bash
[@调研师] 抓取Instagram用户 @username 的所有帖子
[@市场研究] 抓取Amazon产品 B09V3KXJPB 的价格和评论
[@竞品分析] 抓取竞品网站的所有产品页面
```

### 方式2：命令调用

```bash
/dragon-scraper instagram --username "target_user"
/dragon-scraper amazon --asin "B09V3KXJPB"
/dragon-scraper custom --url "https://example.com" --selector ".product"
```

## 输出格式

| 格式 | 说明 |
|------|------|
| `quick` | 快速预览（前5条，无文件） |
| `json` | JSON格式导出 |
| `csv` | CSV格式导出 |
| `sqlite` | 存入本地数据库 |

## 反爬策略

系统内置多层反爬机制：

1. **浏览器指纹伪装** - Playwright Stealth
2. **请求间隔随机化** - 避免频率检测
3. **User-Agent轮换** - 模拟真实用户
4. **代理支持** - 可配置代理池
5. **Cookie管理** - 登录状态保持

## 配置文件

```json
// ~/.claude/skills/dragon-scraper/config.json
{
  "concurrency": 3,
  "requestDelay": [1000, 3000],
  "timeout": 30000,
  "retries": 3,
  "proxy": {
    "enabled": false,
    "list": []
  },
  "storage": {
    "type": "sqlite",
    "path": "~/.claude/data/scraper.db"
  }
}
```

## 与天龙引擎集成

| 天龙岗位 | 使用场景 |
|----------|---------|
| 01调研师 | 竞品调研、市场分析 |
| 32-01市场研究 | 行业数据采集 |
| 35-02社媒运营 | 内容监控、竞品分析 |
| 38-02销售管理 | 线索采集、客户挖掘 |

## 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                   Dragon Scraper 架构                        │
├─────────────────────────────────────────────────────────────┤
│  调度层 - 天龙任务管理器                                      │
│  - 优先级队列                                                │
│  - 失败重试                                                  │
│  - 状态持久化                                                │
├─────────────────────────────────────────────────────────────┤
│  采集层 - Crawlee + Playwright                               │
│  - 浏览器自动化                                              │
│  - 反爬虫策略                                                │
│  - 代理轮换                                                  │
├─────────────────────────────────────────────────────────────┤
│  解析层 - Claude API                                         │
│  - 智能数据提取                                              │
│  - 结构化输出                                                │
├─────────────────────────────────────────────────────────────┤
│  存储层 - SQLite / JSON / CSV                                │
│  - 本地持久化                                                │
│  - 多格式导出                                                │
└─────────────────────────────────────────────────────────────┘
```

## 常见问题

### Q: 如何处理登录验证？
A: 使用 `--login` 参数，系统会打开浏览器让你手动登录，然后保存Cookie。

### Q: 如何配置代理？
A: 编辑 `config.json` 中的 `proxy.list`，支持HTTP/SOCKS5代理。

### Q: 抓取速度太慢怎么办？
A: 调整 `concurrency` 和 `requestDelay` 参数，但注意不要触发反爬。

## 更新日志

- v1.0.0 (2026-03-09) - 初始版本，支持12个核心平台