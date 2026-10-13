---
license: MIT
name: mcp-integration
description: >
  MCP (Model Context Protocol) 集成中心 - 按需调用各种MCP服务器。
  支持GEO分析、地理编码、SEO审计、内容优化等MCP服务。
  触发词：MCP集成、调用MCP、MCP服务器、GEO分析、数据采集。
user-invocable: true
argument-hint: "[server_name] [operation] [params...]"
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - WebFetch
triggers:
  - "mcp"
  - "MCP集成"
  - "MCP: 按需调用"
  - "mcp-integration"
---

# MCP Integration Center — 按需调用MCP服务

## L0: 一句话描述 (≤15字)

MCP按需调用中心，GEO/SEO/地理一站集成

## L1: 使用场景 (50-100字)

**适用场景**：
- 按需调用GEO分析MCP服务（网站分析、SEO审计、引用追踪）
- 按需调用地理空间MCP服务（地理编码，逆向编码、路径规划）
- 按需调用内容优化MCP服务（Schema生成、llms.txt创建）
- 按需调用多平台AI搜索追踪（ChatGPT、Perplexity、Claude、Gemini）

**触发关键词**：`/mcp`、`mcp-integration`、`MCP调用`、`按需MCP`

## L2: 详细文档

### MCP按需调用架构

```
┌─────────────────────────────────────────────────────────────┐
│              MCP Integration Center — 按需调用架构              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │          按需调用入口 (按需激活，按需释放)              │    │
│  │                                                     │    │
│  │  /mcp geo-analyze [url]        → GEO分析服务        │    │
│  │  /mcp geocode [address]        → 地理编码服务        │    │
│  │  /mcp llms-generate [site]     → llms.txt生成       │    │
│  │  /mcp schema-generate [url]     → Schema生成         │    │
│  │  /mcp brand-track [domain]     → 品牌追踪           │    │
│  │  /mcp citation-check [url]      → 引用检查           │    │
│  │  /mcp serp-analyze [keyword]   → SERP分析           │    │
│  │  /mcp competitor-scan [domain] → 竞品扫描           │    │
│  │                                                     │    │
│  └─────────────────────────────────────────────────────┘    │
│                          ↓                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              MCP Client Pool (按需实例化)              │    │
│  │                                                     │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌───────────┐ │    │
│  │  │ MCP-GEO    │  │ MCP-GEO     │  │ MCP-SEO   │ │    │
│  │  │ (GEO分析)   │  │ (地理空间)   │  │ (内容优化) │ │    │
│  │  └─────────────┘  └─────────────┘  └───────────┘ │    │
│  │                                                     │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌───────────┐ │    │
│  │  │ MCP-Brand  │  │ MCP-Citation│  │ MCP-SERP  │ │    │
│  │  │ (品牌追踪)   │  │ (引用追踪)   │  │ (搜索分析) │ │    │
│  │  └─────────────┘  └─────────────┘  └───────────┘ │    │
│  │                                                     │    │
│  └─────────────────────────────────────────────────────┘    │
│                          ↓                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              MCP Servers Registry                    │    │
│  │                                                     │    │
│  │  本地MCP服务器:  • geo-mcp-server (自建)            │    │
│  │                   • seo-mcp-server (自建)            │    │
│  │                                                     │    │
│  │  远程MCP服务器:  • DataForSEO MCP                   │    │
│  │                   • Firecrawl MCP                    │    │
│  │                   • Exa MCP                          │    │
│  │                   • Brave Search MCP                  │    │
│  │                   • Geoapify MCP                     │    │
│  │                   • Tavily MCP                       │    │
│  │                                                     │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 可用MCP服务矩阵

| 服务类型 | MCP服务器 | 功能 | 调用命令 |
|---------|----------|------|---------|
| **GEO分析** | seo-geo-mcp | 网站GEO健康度分析 | `/mcp geo-analyze [url]` |
| **地理编码** | geo-mcp-server | 地址↔坐标转换 | `/mcp geocode [地址]` |
| **逆向编码** | geo-mcp-server | 坐标→地址 | `/mcp reverse [lat,lng]` |
| **llms.txt** | llms-mcp | 自动化生成llms.txt | `/mcp llms-generate [site]` |
| **Schema生成** | schema-mcp | JSON-LD自动生成 | `/mcp schema-generate [url]` |
| **品牌追踪** | brand-tracker-mcp | 品牌AI可见性追踪 | `/mcp brand-track [domain]` |
| **引用检查** | citation-mcp | AI引用检查 | `/mcp citation-check [url]` |
| **SERP分析** | serp-mcp | 搜索结果分析 | `/mcp serp-analyze [keyword]` |
| **竞品扫描** | competitor-mcp | 竞品GEO分析 | `/mcp competitor-scan [domain]` |
| **内容审计** | content-audit-mcp | 内容质量审计 | `/mcp content-audit [url]` |
| **IP定位** | ipinfo-mcp | IP地理位置 | `/mcp ip-lookup [IP]` |
| **路由规划** | routing-mcp | 路径规划 | `/mcp route [from] [to]` |

### 按需调用命令速查

```bash
# 1. GEO分析
/mcp geo-analyze https://example.com          # 单页面分析
/mcp geo-analyze --site https://example.com   # 全站扫描

# 2. 地理编码
/mcp geocode "北京天安门"                     # 地址→坐标
/mcp reverse 39.908,-116.397                  # 坐标→地址

# 3. llms.txt生成
/mcp llms-generate https://example.com        # 生成llms.txt
/mcp llms-preview [site]                      # 预览llms.txt

# 4. Schema生成
/mcp schema-generate --type Article           # Article Schema
/mcp schema-generate --type FAQPage           # FAQ Schema
/mcp schema-generate --type Product           # Product Schema

# 5. 品牌追踪
/mcp brand-track your-brand                   # 追踪品牌可见性
/mcp brand-report --period 30d                # 30天报告

# 6. 引用检查
/mcp citation-check https://example.com        # 检查AI引用
/mcp citation-trend [keyword]                 # 关键词引用趋势

# 7. SERP分析
/mcp serp-analyze "best CRM software"         # 分析搜索结果
/mcp serp-keywords [domain]                   # 关键词排名

# 8. 竞品扫描
/mcp competitor-scan competitor.com           # 竞品GEO分析
/mcp competitor-compare domain1,domain2       # 对比分析

# 9. 内容审计
/mcp content-audit [url]                      # 内容质量审计
/mcp content-score [url]                      # 内容评分

# 10. IP定位
/mcp ip-lookup 8.8.8.8                        # Google DNS IP
/mcp asn-lookup 1.1.1.1                       # ASN查询

# 11. 路由规划
/mcp route "北京站" "上海站"                  # 路径规划
/mcp distance [lat1,lng1] [lat2,lng2]        # 距离计算

# 12. MCP状态
/mcp status                                  # 查看MCP服务器状态
/mcp list                                    # 列出可用MCP服务
/mcp install [server-name]                   # 安装MCP服务器
/mcp update                                  # 更新MCP服务器
```

### MCP服务器安装

```bash
# 安装GEO相关MCP服务器
/mcp install seo-geo-mcp
/mcp install geo-mcp-server
/mcp install llms-mcp
/mcp install schema-mcp
/mcp install brand-tracker-mcp
/mcp install citation-mcp
/mcp install serp-mcp

# 批量安装所有GEO相关MCP
/mcp install --all geo

# 查看已安装的MCP
/mcp list --installed

# 查看可用MCP
/mcp list --available
```

### 环境变量配置

```bash
# MCP集成必需
export MCP_INTEGRATION_HOME="$HOME/.claude/mcp-integration"

# 地理编码服务
export GEOAPIFY_KEY="your-geoapify-key"        # 免费60万次/月
export IPINFO_KEY="your-ipinfo-key"             # 免费50k次/月

# SEO/GEO服务
export DATAFORSEO_LOGIN="your-login"
export DATAFORSEO_PASSWORD="your-password"
export FIRECRAWL_API_KEY="your-firecrawl-key"
export EXA_API_KEY="your-exa-key"
export TAVILY_API_KEY="your-tavily-key"
export BRAVE_API_KEY="your-brave-key"

# MCP服务器配置
export MCP_SERVER_PORT=3100
export MCP_TIMEOUT=30
```

### 与天龙引擎协同

| 天龙组件 | 协同方式 | 效果 |
|---------|---------|------|
| **seo-geo** | MCP调用 → GEO分析数据 | 数据采集自动化 |
| **geo-optimizer** | MCP调用 → Schema生成 | 结构化数据自动化 |
| **geo-content-generator** | MCP调用 → llms.txt生成 | AI可发现性提升 |
| **35-04 GEO内容优化师** | MCP调用 → 品牌追踪 | 效果监控自动化 |
| **01调研师** | MCP调用 → 竞品扫描 | 竞品分析效率提升 |
| **04验证师** | MCP调用 → 引用检查 | 质量验证自动化 |

### MCP按需调用工作流

```
┌─────────────────────────────────────────────────────────────┐
│              MCP按需调用工作流 (On-Demand Pattern)            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Step 1: 需求识别                                           │
│  ├── 用户说"分析这个网站的GEO健康度"                          │
│  ├── 识别需要: seo-geo-mcp                                  │
│  └── 按需实例化MCP客户端                                     │
│                    ↓                                        │
│  Step 2: MCP调用                                            │
│  ├── 调用 /mcp geo-analyze [url]                           │
│  ├── MCP服务器处理请求                                       │
│  ├── 返回结构化结果                                          │
│  └── 调用完成 → 释放MCP连接                                  │
│                    ↓                                        │
│  Step 3: 结果处理                                           │
│  ├── 解析MCP返回结果                                         │
│  ├── 格式化输出报告                                          │
│  └── 触发后续天龙引擎流程                                     │
│                    ↓                                        │
│  Step 4: 资源释放                                           │
│  ├── 关闭MCP连接                                            │
│  ├── 记录调用日志                                            │
│  └── 更新使用统计                                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 性能指标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| MCP连接建立时间 | <500ms | 冷启动 |
| MCP调用响应时间 | <3s | 热调用 |
| MCP连接复用率 | >80% | 连接池复用 |
| 并发MCP调用数 | ≤10 | 避免资源耗尽 |
| MCP调用成功率 | >98% | 高可用性 |

### 文件结构

```
mcp-integration/
├── SKILL.md                    # 本文件
├── scripts/
│   ├── __init__.py
│   ├── mcp_client.py          # MCP客户端核心
│   ├── mcp_registry.py        # MCP服务器注册表
│   ├── mcp_pool.py            # MCP连接池
│   ├── geo_analyzer.py        # GEO分析调用
│   ├── geocoder.py            # 地理编码调用
│   ├── llms_generator.py      # llms.txt生成
│   ├── schema_generator.py    # Schema生成
│   ├── brand_tracker.py       # 品牌追踪
│   ├── citation_checker.py     # 引用检查
│   ├── serp_analyzer.py       # SERP分析
│   ├── competitor_scanner.py   # 竞品扫描
│   ├── content_auditor.py     # 内容审计
│   ├── ip_lookup.py           # IP定位
│   ├── route_planner.py       # 路由规划
│   └── cli.py                 # CLI入口
├── prompts/
│   ├── mcp-call-template.md   # MCP调用提示词
│   ├── geo-analysis-template.md # GEO分析报告模板
│   └── report-template.md     # 报告模板
└── references/
    ├── mcp-protocol.md        # MCP协议参考
    ├── mcp-servers-list.md   # MCP服务器列表
    └── mcp-best-practices.md  # MCP最佳实践
```

### MCP服务器列表 (参考 geo-mcp-servers)

#### GEO/SEO MCP服务器

| 服务器 | 来源 | 功能 | 链接 |
|--------|------|------|------|
| seo-geo-mcp | 自建 | GEO分析 | 内置 |
| llms-mcp | 自建 | llms.txt生成 | 内置 |
| schema-mcp | 自建 | Schema生成 | 内置 |
| brand-tracker-mcp | 自建 | 品牌追踪 | 内置 |
| citation-mcp | 自建 | 引用检查 | 内置 |
| serp-mcp | 自建 | SERP分析 | 内置 |
| content-audit-mcp | 自建 | 内容审计 | 内置 |
| DataForSEO MCP | 第三方 | SEO数据 | dataforseo.com |
| Firecrawl MCP | 第三方 | 网页抓取 | firecrawl.dev |
| Exa MCP | 第三方 | 语义搜索 | exa.ai |
| Tavily MCP | 第三方 | AI搜索 | tavily.com |

#### 地理空间MCP服务器

| 服务器 | 来源 | 功能 | 链接 |
|--------|------|------|------|
| geo-mcp-server | 自建 | 地理编码/逆向编码 | 内置 |
| ipinfo-mcp | 自建 | IP定位 | 内置 |
| routing-mcp | 自建 | 路由规划 | 内置 |
| Geoapify | 官方 | 地理编码 | geoapify.com |
| Nominatim | 官方 | OpenStreetMap地理编码 | openstreetmap.org |
| OSRM | 官方 | 路由引擎 | project-osrm.org |
| PostGIS | 官方 | 地理数据库 | postgis.net |
| STAC | 官方 | 卫星影像 | stacspec.org |

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-08-19 | 初始MCP集成中心，按需调用架构 |
