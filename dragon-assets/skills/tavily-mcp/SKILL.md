---
license: UNKNOWN
name: tavily-mcp
description: 官方Tavily MCP服务器 - 实时网页搜索 + 智能数据提取 + 网站映射 + 深度爬取。相比tavily-automation更轻量、更直接。
github_repo: tavily-ai/tavily-mcp
github_hash: 7bcf90750ef5180968b78abb891eed837d9f7c20
last_updated: 2026-04-25
source_type: derived
argument-hint: 搜索查询或URL
triggers: ["tavily mcp", "Tavily MCP - 官方搜索与数据提取服务器"]
---

# Tavily MCP - 官方搜索与数据提取服务器

## 🎯 核心价值

提供**实时网页搜索、智能数据提取、网站映射、深度爬取**四大核心能力，作为现有tavily-automation的官方替代方案。

## 📊 与tavily-automation对比

| 维度 | tavily-automation (Composio) | tavily-mcp (官方) |
|------|------------------------------|-------------------|
| **集成方式** | Rube MCP → Composio连接 | 直接Tavily API Key |
| **认证** | Composio账号管理 | API Key直连 |
| **工具发现** | 需要RUBE_SEARCH_TOOLS | 直接调用 |
| **功能覆盖** | 基础搜索 | **search + extract + map + crawl** |
| **部署复杂度** | 需要Composio账号 | 只需Tavily API Key |
| **稳定性** | 依赖Composio | 官方直接支持 |

## 🚀 安装方式

### 方式1: 远程MCP服务器（推荐）

```json
// .claude/mcp.json
{
  "mcpServers": {
    "tavily": {
      "type": "http",
      "url": "https://mcp.tavily.com/mcp/?tavilyApiKey=TAVILY_API_KEY"
    }
  }
}
```

### 方式2: 本地NPX运行

```json
// .claude/mcp.json
{
  "mcpServers": {
    "tavily": {
      "command": "npx",
      "args": ["-y", "tavily-mcp@latest"],
      "env": {
        "TAVILY_API_KEY": "your-api-key"
      }
    }
  }
}
```

### 获取API Key

1. 访问 [tavily.com](https://tavily.com)
2. 注册账号
3. 在Dashboard获取API Key

## 📋 四大核心工具

### 1. tavily-search - 实时网页搜索

```bash
# 基础搜索
mcp__tavily__tavily-search(query="AI Agent发展趋势")

# 高级搜索参数
mcp__tavily__tavily-search(
  query="Next.js 14新特性",
  search_depth="advanced",  # basic | advanced
  include_domains=["github.com", "vercel.com"],
  exclude_domains=["medium.com"],
  max_results=10,
  include_answer=true,
  include_raw_content=false
)
```

### 2. tavily-extract - 智能数据提取

```bash
# 从URL提取数据
mcp__tavily__tavily-extract(urls=[
  "https://example.com/product/1",
  "https://example.com/product/2"
])

# 提取特定字段
mcp__tavily__tavily-extract(
  urls=["https://news.ycombinator.com"],
  extract_depth="advanced",
  query="提取文章标题、链接和评论数"
)
```

### 3. tavily-map - 网站结构映射

```bash
# 映射网站结构
mcp__tavily__tavily-map(url="https://example.com")

# 参数
mcp__tavily__tavily-map(
  url="https://docs.example.com",
  max_depth=3,
  max_breadth=50,
  query="API文档页面"
)
```

### 4. tavily-crawl - 深度爬取

```bash
# 深度爬取网站
mcp__tavily__tavily-crawl(
  url="https://example.com/docs",
  max_depth=2,
  max_breadth=20,
  query="技术文档",
  extract_depth="advanced"
)
```

## 🔄 与天龙引擎协同

### 与01调研师协同

```yaml
调研流程:
  1. 初步调研
     - tavily-search 获取概览

  2. 深度调研
     - tavily-crawl 爬取相关网站
     - tavily-extract 提取关键数据

  3. 结构化输出
     - 整合搜索结果
     - 引用来源标注
```

### 与32-01市场研究协同

```yaml
市场研究流程:
  1. 趋势搜索
     mcp__tavily__tavily-search(
       query="AI Agent市场趋势 2024",
       search_depth="advanced",
       max_results=20
     )

  2. 竞品分析
     mcp__tavily__tavily-extract(
       urls=["竞品官网1", "竞品官网2"],
       query="产品功能、定价、用户评价"
     )

  3. 网站结构分析
     mcp__tavily__tavily-map(
       url="竞品官网",
       max_depth=2
     )
```

### 与35-02社媒运营协同

```yaml
社媒内容研究:
  热点搜索:
    mcp__tavily__tavily-search(
      query="小红书 美妆 热门话题",
      include_domains=["xiaohongshu.com"]
    )

  内容提取:
    mcp__tavily__tavily-extract(
      urls=["热门笔记URL"],
      extract_depth="advanced"
    )
```

## 📝 使用示例

### 示例1：技术调研

```bash
# 调研React Server Components
[@调研师] 调研React Server Components最新发展

# 工作流
1. mcp__tavily__tavily-search(
     query="React Server Components 2024",
     search_depth="advanced",
     include_domains=["react.dev", "github.com"]
   )

2. mcp__tavily__tavily-map(
     url="https://react.dev/reference/rsc",
     max_depth=2
   )

3. 整合输出调研报告
```

### 示例2：竞品分析

```bash
# 分析竞品网站
[@市场研究] 分析竞品XYZ的产品功能

# 工作流
1. mcp__tavily__tavily-search(query="XYZ product features")

2. mcp__tavily__tavily-crawl(
     url="https://xyz.com",
     max_depth=2,
     query="产品功能、定价、案例"
   )

3. mcp__tavily__tavily-extract(
     urls=["https://xyz.com/pricing", "https://xyz.com/features"]
   )
```

### 示例3：内容研究

```bash
# 研究某主题的最新内容
[@调研师] 收集AI Agent的最新研究和文章

# 工作流
mcp__tavily__tavily-search(
  query="AI Agent research 2024",
  search_depth="advanced",
  max_results=20,
  include_answer=true
)

# 输出示例
## Search Results
1. "A Survey on AI Agents" - arxiv.org
2. "Building Autonomous Agents" - openai.com
3. "Agent Architecture Patterns" - github.com

## AI Generated Answer
AI Agents are software systems that can perceive, reason, and act...
```

## ⚙️ 高级配置

### 搜索深度配置

```yaml
search_depth:
  basic:
    - 快速搜索
    - 适合简单查询
    - 成本低

  advanced:
    - 深度搜索
    - 更多来源
    - 更详细结果
```

### 提取深度配置

```yaml
extract_depth:
  basic:
    - 提取主要内容
    - 快速处理

  advanced:
    - 提取结构化数据
    - 包含元数据
    - 适合复杂数据
```

### 领域过滤

```bash
# 只搜索特定领域
mcp__tavily__tavily-search(
  query="TypeScript best practices",
  include_domains=["typescriptlang.org", "github.com"]
)

# 排除特定领域
mcp__tavily__tavily-search(
  query="JavaScript tutorials",
  exclude_domains=["medium.com", "dev.to"]
)
```

## 🔧 与现有tavily-automation协同

### 使用建议

| 场景 | 推荐方案 |
|------|---------|
| **已有Composio账号** | 继续使用tavily-automation |
| **仅需Tavily功能** | 使用tavily-mcp（更轻量） |
| **需要map/crawl功能** | 使用tavily-mcp（功能更全） |
| **多工具编排需求** | 使用tavily-automation（通过Composio） |

### 平行共存

```json
// 可以同时配置两个
{
  "mcpServers": {
    "tavily": {
      "command": "npx",
      "args": ["-y", "tavily-mcp@latest"],
      "env": {"TAVILY_API_KEY": "key"}
    },
    "rube": {
      "type": "http",
      "url": "https://rube.app/mcp"
    }
  }
}
```

## 📊 预期收益

| 指标 | 无Tavily | tavily-mcp | 提升 |
|------|---------|-----------|------|
| **搜索实时性** | 依赖索引 | **实时搜索** | 质的飞跃 |
| **数据提取效率** | 手动 | **自动化** | +300% |
| **网站分析** | 无 | **map+crawl** | 新增能力 |
| **配置复杂度** | - | **仅需API Key** | 极简 |

## 🔗 相关资源

- **官网**: https://tavily.com
- **Dashboard**: https://app.tavily.com
- **GitHub**: https://github.com/tavily-ai/tavily-mcp
- **NPM**: https://www.npmjs.com/package/tavily-mcp

---

**版本**: v1.0.0
**创建时间**: 2026-03-27
**集成版本**: 天龙引擎 V8.57

---

## 协同：与 dsh-web-search-pro（阶段 40.2 · 2026-08-24）

> **TL;DR**：本 skill 在天龙 DSH 化后应**降级为 Tavily MCP 专用通路**。`dsh-web-search-pro@0.1.8` 的 `exa` 引擎底层协议与 Tavily MCP 类似，但走 DSH Credentials（不入浏览器）+ SQLite 持久化。

### 何时仍用本 skill（不降级）

1. **非 DSH 环境**（纯 Claude Code / 纯 IDE）
2. **已经配置好 Tavily MCP server** + 本地有 stdio/HTTP 客户端
3. **需要 Tavily 深度研究 / 网站映射 / 爬取** —— dsh-web-search-pro 的 `web_exa_contents` 类似但不覆盖 `crawl` / `map` API

### 何时不再用本 skill（降级）

- DSH GUI 用户 + 装好 `dsh-web-search-pro@0.1.8` → 走 web_search_pro / web_exa_contents
- 需要持久化时 → 走 dsh-web-search-pro SQLite 缓存
- 需要中文社区 → 走 dsh-web-search-pro 19 平台

### 关联

- `dragon-engine/skills/dsh-web-search-pro-bridge/SKILL.md` — 天龙侧桥 V1.0
- `dragon-engine/skills/anysearch/SKILL.md` V3.1 — DSH bridge 探测
- `memory/stage-40-announce.md` — 阶段 40 总验收
