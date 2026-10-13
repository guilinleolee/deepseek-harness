---
license: UNKNOWN
github_repo: firecrawl/firecrawl
github_hash: 0c24965c73d7b8828a4e565035a9f66871d295b1
last_updated: 2026-04-25
source_type: derived
triggers: ["firecrawl api", "Firecrawl API Skill"]
---
# Firecrawl API Skill

## 概述

| 属性 | 值 |
|------|-----|
| **Skill名称** | firecrawl-api |
| **来源** | [firecrawl/firecrawl](https://github.com/firecrawl/firecrawl) (100k+ Stars) |
| **许可证** | MIT / AGPL-3.0 |
| **核心能力** | LLM-Ready网页抓取 + 自然语言数据提取 + Change Tracking |
| **版本** | V1.0 |
| **集成日期** | 2026-03-30 |

## 核心能力矩阵

| 能力 | 命令 | 描述 | 输出格式 |
|------|------|------|---------|
| **Map** | `/firecrawl map` | URL发现（智能sitemap） | URL列表 |
| **Scrape** | `/firecrawl scrape` | 单URL提取 | markdown/html/json/screenshot |
| **Crawl** | `/firecrawl crawl` | 全站异步爬取 | 批量markdown/html |
| **Agent** | `/firecrawl agent` | 自然语言数据提取 | 结构化JSON |
| **Interact** | `/firecrawl interact` | 浏览器自动化交互 | 可交互session |
| **Track** | `/firecrawl track` | 变化追踪监控 | 变更通知 |

## 安装

```bash
# 安装Python SDK
pip install firecrawl-py

# 验证安装
D:/python/python.exe -c "from firecrawl import Firecrawl; print('Firecrawl SDK OK')"
```

## 环境配置

```bash
# 方式1: 设置环境变量
export FIRECRAWL_API_KEY="fc-YOUR-API-KEY"

# 方式2: 编辑配置文件
code ~/.claude/firecrawl_config.json
# 将 "api_key": "YOUR_API_KEY_HERE" 替换为真实API Key

# 获取API Key: https://firecrawl.dev/dashboard (注册送500 credits)
```

## 快速开始

### 统一CLI（推荐）

```bash
# 设置API Key
export FIRECRAWL_API_KEY="fc-YOUR-API-KEY"

# 发现URL
D:/python/python.exe ~/.claude/skills/firecrawl-api/scripts/firecrawl_cli.py map "https://example.com"

# 抓取页面
D:/python/python.exe ~/.claude/skills/firecrawl-api/scripts/firecrawl_cli.py scrape "https://example.com" --format markdown

# 搜索网页
D:/python/python.exe ~/.claude/skills/firecrawl-api/scripts/firecrawl_cli.py search "AI news"

# 结构化提取
D:/python/python.exe ~/.claude/skills/firecrawl-api/scripts/firecrawl_cli.py extract "https://shop.example.com" \
  --prompt "提取所有产品名称和价格"

# 全站爬取
D:/python/python.exe ~/.claude/skills/firecrawl-api/scripts/firecrawl_cli.py crawl "https://docs.example.com" --limit 50
```

### 独立脚本

```bash
# Map - URL发现
python ~/.claude/skills/firecrawl-api/scripts/map_client.py "https://example.com" --limit 100

# Scrape - LLM-Ready提取
python ~/.claude/skills/firecrawl-api/scripts/scrape_client.py "https://example.com" --format markdown

# Search - 网页搜索
python ~/.claude/skills/firecrawl-api/scripts/firecrawl_cli.py search "AI trends"

# Extract - 自然语言提取
python ~/.claude/skills/firecrawl-api/scripts/agent_client.py "https://shop.example.com" \
  --prompt "提取所有产品名称和价格"
```

## 与天龙现有能力协同

```
┌─────────────────────────────────────────────────────────────┐
│               天龙引擎 调研-抓取 能力分层                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Tier 1: 免费基础层                                        │
│   ├── Agent-Reach     → 简单数据采集                       │
│   ├── baoyu-url-to-md → Markdown转换                       │
│   └── GPT-Researcher  → 深度研究                           │
│                                                             │
│   Tier 2: 付费增强层 ⭐ Firecrawl                          │
│   ├── Map            → 专业URL发现                         │
│   ├── Agent          → 自然语言→JSON提取                   │
│   ├── Change Tracking → 变化监控                           │
│   └── Interact       → 登录态自动化                        │
│                                                             │
│   Tier 3: 企业级层                                         │
│   └── Scrapy         → 大规模结构化采集                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 天龙岗位集成

### 01调研师

```markdown
### Firecrawl增强能力

1. **Map URL发现** - 替代手动搜索
   ```bash
   python ~/.claude/skills/firecrawl-api/scripts/map_client.py "https://竞品.com" --limit 200
   ```

2. **Agent自然语言提取** - 结构化数据采集
   ```bash
   python ~/.claude/skills/firecrawl-api/scripts/agent_client.py \
     --urls "urls.json" \
     --prompt "提取所有职位名称和任职要求" \
     --schema '{"title": "string", "requirements": "string[]"}'
   ```

3. **Change Tracking** - 竞品动态监控
   ```bash
   python ~/.claude/skills/firecrawl-api/scripts/track_client.py \
     "https://竞品.com/pricing" \
     --interval daily \
     --notify webhook
   ```
```

### 07记录师

```markdown
### Firecrawl增强能力

1. **高质量Markdown提取** - LLM-Ready >80%覆盖率
   ```bash
   python ~/.claude/skills/firecrawl-api/scripts/scrape_client.py \
     "https://article.example.com" \
     --format markdown
   ```

2. **批量文档采集** - 支持PDF/DOCX/图片
   ```bash
   python ~/.claude/skills/firecrawl-api/scripts/scrape_client.py \
     "https://docs.example.com" \
     --formats markdown,media
   ```
```

## 定价参考

| 操作 | 积分消耗 |
|------|---------|
| Scrape (基础) | 1 credit |
| Scrape (Markdown) | +0.5 credits |
| Scrape (Screenshot) | +1 credit |
| Crawl | 2 credits/页 |
| Map | 1 credit/100 URLs |
| Agent (spark-1-mini) | 5 credits/页 |
| Agent (spark-1-pro) | 10 credits/页 |
| Interact | 2-7 credits/分钟 |

**免费额度**: 注册送 500 credits

## 常见问题

### Q: 如何获取免费API Key?
A: 访问 https://firecrawl.dev/dashboard 注册获取

### Q: 与Scrapy的区别是什么?
A: Firecrawl是API服务（付费+云端），Scrapy是本地框架（免费+自托管）。Firecrawl适合快速原型，Scrapy适合大规模定制。

### Q: 支持登录态抓取吗?
A: 支持。通过 `pageOptions: { auth: { username, password } }` 或 Profile持久化。

### Q: 如何处理反爬?
A: 使用 `onlyMainContent: true` 跳过广告/追踪脚本，或设置代理 `proxy: { url, goesThrough: 'basic' }`。

## 脚本文件

| 文件 | 功能 |
|------|------|
| [map_client.py](scripts/map_client.py) | Map URL发现 |
| [scrape_client.py](scripts/scrape_client.py) | Scrape单页提取 |
| [crawl_client.py](scripts/crawl_client.py) | Crawl全站爬取 |
| [agent_client.py](scripts/agent_client.py) | Agent自然语言提取 |
| [interact_client.py](scripts/interact_client.py) | Interact浏览器交互 |
| [track_client.py](scripts/track_client.py) | Track变化追踪 |
| [firecrawl_cli.py](scripts/firecrawl_cli.py) | 统一CLI入口 |

## 参考资源

- GitHub: https://github.com/firecrawl/firecrawl
- 文档: https://docs.firecrawl.dev
- API: https://api.firecrawl.dev
- Python SDK: https://pypi.org/project/firecrawl-py/
