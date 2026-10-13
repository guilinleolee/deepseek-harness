# MCP服务器列表

本文档列出了天龙引擎MCP集成支持的MCP服务器，包括内置服务器和远程服务器。

## 内置MCP服务器

### geo-mcp-server

**地理编码MCP服务器**

| 功能 | 描述 | 端点 |
|------|------|------|
| geocode | 地址转坐标 | /geocode |
| reverse | 坐标转地址 | /reverse |
| ip_lookup | IP地理位置 | /ip |
| batch_geocode | 批量地理编码 | /batch |
| route_planning | 路径规划 | /route |

**提供商**:
- Nominatim (免费, OpenStreetMap)
- Geoapify (免费60万次/月)
- IPinfo (免费50k次/月)

### seo-mcp-server

**SEO分析MCP服务器**

| 功能 | 描述 |
|------|------|
| site_audit | 全站审计 |
| page_analysis | 页面分析 |
| technical_seo | 技术SEO检查 |
| keyword_analysis | 关键词分析 |
| backlink_check | 外链检查 |

### geo-analyzer-mcp

**GEO分析MCP服务器**

| 功能 | 描述 |
|------|------|
| geo_score | GEO健康度评分 |
| citability_analysis | 可引用性分析 |
| authority_analysis | 权威性分析 |
| ai_crawler_check | AI爬虫检查 |
| llms_txt_analysis | llms.txt分析 |
| platform_specific | 平台特定优化 |

### llms-mcp

**llms.txt生成MCP服务器**

| 功能 | 描述 |
|------|------|
| generate_llms_txt | 生成llms.txt |
| preview_llms_txt | 预览llms.txt |
| validate_llms_txt | 验证llms.txt |
| update_llms_txt | 更新llms.txt |

### schema-mcp

**Schema生成MCP服务器**

| 功能 | 描述 |
|------|------|
| generate_schema | 生成JSON-LD |
| validate_schema | 验证Schema |
| suggest_schema | Schema建议 |

**支持的Schema类型**:
- Article
- FAQPage
- Organization
- Person
- Product
- Service
- Event
- LocalBusiness

### brand-tracker-mcp

**品牌追踪MCP服务器**

| 功能 | 描述 |
|------|------|
| track_mentions | 提及追踪 |
| sentiment_analysis | 情感分析 |
| citation_tracking | 引用追踪 |
| trend_analysis | 趋势分析 |
| competitor_comparison | 竞品对比 |

### citation-mcp

**引用检查MCP服务器**

| 功能 | 描述 |
|------|------|
| check_citations | 检查引用 |
| citation_context | 引用上下文 |
| citation_trends | 引用趋势 |
| attribution_analysis | 归因分析 |

### serp-mcp

**SERP分析MCP服务器**

| 功能 | 描述 |
|------|------|
| serp_analysis | SERP分析 |
| keyword_research | 关键词研究 |
| competitor_analysis | 竞品分析 |
| intent_classification | 意图分类 |
| featured_snippet | 精选摘要分析 |

### competitor-mcp

**竞品扫描MCP服务器**

| 功能 | 描述 |
|------|------|
| scan_competitor | 扫描竞品 |
| compare_competitors | 竞品对比 |
| gap_analysis | 差距分析 |
| opportunity_identification | 机会识别 |

### content-audit-mcp

**内容审计MCP服务器**

| 功能 | 描述 |
|------|------|
| audit_content | 内容审计 |
| score_content | 内容评分 |
| suggest_improvements | 改进建议 |
| readability_check | 可读性检查 |
| seo_check | SEO检查 |
| geo_check | GEO检查 |

## 远程MCP服务器

### DataForSEO MCP

**专业SEO数据API**

- 网站: https://dataforseo.com
- 认证: API Key
- 免费额度: 受限
- 功能:
  - SERP API
  - Keywords API
  - Backlinks API
  - Domain Analytics

### Firecrawl MCP

**网页抓取和内容提取**

- 网站: https://firecrawl.dev
- 认证: API Key
- 免费额度: 有限
- 功能:
  - Scrape
  - Crawl
  - Extract
  - Batch Scrape

### Exa MCP

**AI语义搜索**

- 网站: https://exa.ai
- 认证: API Key
- 免费额度: 有限
- 功能:
  - Semantic Search
  - Content Search
  - Find Similar

### Tavily MCP

**AI搜索API**

- 网站: https://tavily.com
- 认证: API Key
- 免费额度: 有限
- 功能:
  - Search
  - Deep Search
  - Extract

### Brave Search MCP

**隐私搜索API**

- 网站: https://brave.com
- 认证: API Key
- 免费额度: 有限
- 功能:
  - Web Search
  - News Search
  - Local Search

### Geoapify MCP

**地理编码和地图服务**

- 网站: https://geoapify.com
- 认证: API Key
- 免费额度: 60万次/月
- 功能:
  - Geocoding
  - Reverse Geocoding
  - Routing
  - Places
  - Map Tiles

### IPinfo MCP

**IP地理位置和ASN信息**

- 网站: https://ipinfo.io
- 认证: API Key
- 免费额度: 50k次/月
- 功能:
  - IP Lookup
  - ASN Lookup
  - IP Type
  - Bulk Lookup

## 地理空间MCP服务器

### Nominatim

**OpenStreetMap地理编码**

- 网站: https://nominatim.openstreetmap.org
- 认证: 无
- 限速: 1请求/秒
- 功能:
  - Geocoding
  - Reverse Geocoding

### OSRM

**开源路由引擎**

- 网站: https://router.project-osrm.org
- 认证: 无
- 功能:
  - Route
  - Table
  - Nearest
  - Trip
  - Match

### Photons

**轻量级OpenStreetMap搜索**

- 网站: https://photon.komoot.io
- 认证: 无
- 功能:
  - Search
  - Autocomplete

## 参考项目

以下是GitHub上相关的开源MCP项目：

| 项目 | Stars | 描述 |
|------|-------|------|
| modelcontextprotocol/python-sdk | 24049 | MCP官方Python SDK |
| modelcontextprotocol/typescript-sdk | 13200 | MCP官方TS SDK |
| modelcontextprotocol/registry | 7172 | MCP服务器注册表 |
| appcypher/awesome-mcp-servers | 5750 | MCP服务器精选列表 |
| sparkgeo/geo-mcp-servers | 69 | 地理MCP服务器列表 |
| hangwin/mcp-chrome | 12323 | Chrome MCP服务器 |
| executeautomation/mcp-playwright | 5633 | Playwright MCP |

## 安装指南

### 安装内置MCP服务器

```bash
# 内置服务器无需安装，已集成到 mcp_client.py
```

### 安装远程MCP服务器

```bash
# DataForSEO
export DATAFORSEO_LOGIN="your-login"
export DATAFORSEO_PASSWORD="your-password"

# Firecrawl
export FIRECRAWL_API_KEY="your-key"

# Exa
export EXA_API_KEY="your-key"

# Tavily
export TAVILY_API_KEY="your-key"

# Brave
export BRAVE_API_KEY="your-key"

# Geoapify
export GEOAPIFY_KEY="your-key"

# IPinfo
export IPINFO_KEY="your-key"
```

## 使用示例

```python
from mcp_client import MCPClientPool, MCPServerType, MCPRequest
import asyncio

async def main():
    pool = MCPClientPool()

    # 地理编码
    request = MCPRequest(
        server_type=MCPServerType.GEOCODER,
        operation="geocode",
        params={"address": "北京市朝阳区"}
    )
    response = await pool.call(request)
    print(response.data)

    # GEO分析
    request = MCPRequest(
        server_type=MCPServerType.GEO_ANALYZER,
        operation="analyze",
        params={"url": "https://example.com"}
    )
    response = await pool.call(request)
    print(response.data)

    pool.close_all()

asyncio.run(main())
```
