---
license: MIT
name: 40-01-mcp-orchestrator
description: >
  MCP编排器 v2.1 - 智能路由MCP调用请求到最合适的MCP服务。
  支持GEO分析、地理编码、内容采集、SEO审计等 10 个既有 + Stage 40 trajectory-debug 第 11 服务
  + Stage 50.3 dsh-market 第 12 服务（plugin marketplace as MCP）。
  触发词：MCP编排、MCP调用路由、智能MCP、trajectory、dsh-market、plugin market、插件市场。
version: 2.1.0
triggers: ["MCP编排器", "MCP Orchestrator", "40-01 MCP编排器", "trajectory", "trajectory-debug", "dsh-market", "plugin market", "插件市场"]
---

# 40-01 MCP编排器

> MCP Integration Center - 智能路由MCP调用请求

## 角色使命

作为MCP服务的智能编排器，根据用户请求自动路由到最合适的MCP服务。

## 核心能力

### MCP服务路由

| 请求类型 | 路由目标 | 说明 |
|---------|---------|------|
| 地址→坐标 | geo-mcp-server | 地理编码 |
| 坐标→地址 | geo-mcp-server | 逆向编码 |
| GEO分析 | geo-analyzer-mcp | GEO健康度评分 |
| llms.txt | llms-mcp | AI可读文件生成 |
| Schema | schema-mcp | JSON-LD生成 |
| 品牌追踪 | brand-tracker-mcp | 品牌可见性 |
| 引用检查 | citation-mcp | AI引用追踪 |
| SERP分析 | serp-mcp | 搜索结果分析 |
| 内容采集 | firecrawl-mcp | 网页抓取 |
| 语义搜索 | exa-mcp | AI语义搜索 |
| AI搜索 | tavily-mcp | AI搜索API |
| 隐私搜索 | brave-mcp | Brave搜索 |
| **plugin market 搜索** ⭐NEW V2.1 | **dsh-market-mcp** | **DSH 插件市场搜索/详情/安装/更新** |
| **plugin market 详情** ⭐NEW V2.1 | **dsh-market-mcp** | **获取插件元数据** |
| **plugin market 安装** ⭐NEW V2.1 | **dsh-market-mcp** | **触发 6 阶段安装 pipeline** |

### MCP命令映射

```bash
# 地理编码
/geo [地址] → geo-mcp-server
/mcp geocode [地址]

# 逆向编码
/reverse [lat,lng] → geo-mcp-server
/mcp reverse [lat,lng]

# GEO分析
/geo-analyze [url] → geo-analyzer-mcp
/mcp geo-analyze [url]

# llms.txt
/llms-generate [site] → llms-mcp
/mcp llms-generate [site]

# Schema
/schema [type] [params] → schema-mcp
/mcp schema-generate [type]

# 内容采集
/scrape [url] → firecrawl-mcp
/mcp scrape [url]

# 语义搜索
/search [query] → exa-mcp
/mcp search [query]
```

## MCP服务矩阵

### 内置MCP服务

| 服务 | 功能 | 调用方式 |
|------|------|---------|
| geo-mcp-server | 地理编码/逆向编码 | MCPClientPool |
| seo-mcp-server | SEO分析 | MCPClientPool |
| geo-analyzer-mcp | GEO分析 | MCPClientPool |
| llms-mcp | llms.txt生成 | MCPClientPool |
| schema-mcp | Schema生成 | MCPClientPool |
| brand-tracker-mcp | 品牌追踪 | MCPClientPool |
| citation-mcp | 引用检查 | MCPClientPool |
| serp-mcp | SERP分析 | MCPClientPool |
| competitor-mcp | 竞品扫描 | MCPClientPool |
| content-audit-mcp | 内容审计 | MCPClientPool |
| **dsh-market-mcp** ⭐NEW V2.1 | **DSH 插件市场（搜索/详情/安装/更新）** | **MCPClientPool + dsh-market-bridge V2.0** |

### 远程MCP服务

| 服务 | 提供商 | 功能 | 免费额度 |
|------|--------|------|---------|
| firecrawl | firecrawl.dev | 网页抓取 | 500次/月 |
| exa | exa.ai | 语义搜索 | 1000次/月 |
| tavily | tavily.com | AI搜索 | 1000次/月 |
| brave | brave.com | 隐私搜索 | 2000次/月 |
| dataforseo | dataforseo.com | SEO数据 | 受限 |
| geoapify | geoapify.com | 地理编码 | 60万次/月 |
| ipinfo | ipinfo.io | IP定位 | 50k次/月 |

## MCP调用示例

### 示例1：GEO分析工作流

```
用户: 分析 https://example.com 的GEO健康度

编排器:
  1. 路由到 geo-analyzer-mcp
  2. 调用 /mcp geo-analyze https://example.com
  3. 返回GEO分析报告

输出:
  - GEO健康度评分
  - 五维分析结果
  - 优化建议
```

### 示例2：内容采集工作流

```
用户: 采集 https://example.com/article 的内容

编排器:
  1. 检查是否配置了firecrawl API
  2. 路由到 firecrawl-mcp（远程）或使用内置爬虫
  3. 返回Markdown格式内容

输出:
  - Markdown内容
  - 元数据
  - 链接列表
```

### 示例3：多MCP协同

```
用户: 分析竞品的GEO策略

编排器:
  1. serp-mcp → 获取竞品搜索排名
  2. exa-mcp → 语义搜索竞品相关内容
  3. geo-analyzer-mcp → 分析竞品GEO健康度
  4. citation-mcp → 检查竞品AI引用情况

输出:
  - 竞品SERP分析
  - 竞品内容策略
  - GEO差距分析
  - 引用对比
```

## MCP调用语法

### 内置MCP调用

```bash
# 地理编码
python3 scripts/mcp_client.py geocode "北京市朝阳区"

# 逆向编码
python3 scripts/mcp_client.py reverse 39.908,-116.397

# IP定位
python3 scripts/mcp_client.py ip-lookup 8.8.8.8

# GEO分析
python3 scripts/mcp_client.py geo-analyze https://example.com

# llms.txt生成
python3 scripts/mcp_client.py llms-generate https://example.com

# Schema生成
python3 scripts/mcp_client.py schema-generate Article --title "标题" --url "https://example.com"

# 品牌追踪
python3 scripts/mcp_client.py brand-track "品牌名" --period 30d

# 引用检查
python3 scripts/mcp_client.py citation-check https://example.com
```

### 远程MCP调用

```bash
# Firecrawl - 网页抓取
python3 scripts/mcp_remote.py firecrawl scrape --url https://example.com

# Exa - 语义搜索
python3 scripts/mcp_remote.py exa search --query "AI搜索引擎趋势"

# Tavily - AI搜索
python3 scripts/mcp_remote.py tavily search --query "GEO优化最佳实践"

# Brave - 隐私搜索
python3 scripts/mcp_remote.py brave search --query "生成引擎优化"

# DataForSEO - SERP分析
python3 scripts/mcp_remote.py dataforseo serp --query "best CRM software"
```

### dsh-market MCP 调用（⭐NEW V2.1 · Stage 50.3 联动）

```bash
# 搜索 DSH 插件市场（5 维度 filter · V2.0 升级）
python3 scripts/mcp_client.py dsh-market search --query '{"text":"redis","category":"frontend","min_stars":10,"language":"zh"}'

# 获取插件详情
python3 scripts/mcp_client.py dsh-market detail --name dsh-tui-bridge

# 触发 6 阶段安装 pipeline（resolve → preflight → download → verify → register → activation-check）
python3 scripts/mcp_client.py dsh-market install --name dsh-tui-bridge --version 0.9.2

# 更新插件（pnpm v10/v11 allowBuilds 兼容 · V2.0 借鉴）
python3 scripts/mcp_client.py dsh-market update --name dsh-tui-bridge

# 备份 profile（含 bundles + cordis.patch.yml + settings · V2.0 backup.ts）
python3 scripts/mcp_client.py dsh-market backup --profile web

# restore 备份（merge 模式：保留 backup 之后的安装 · V2.0 backup.ts）
python3 scripts/mcp_client.py dsh-market restore --backup-file ./web-backup-20260826.json
```

**dsh-market MCP 路由决策树**：

```python
def route_to_dsh_market(query: str) -> str:
    triggers = ["插件市场", "plugin market", "dsh-market", "/market", "/install",
                "market search", "plugin install", "一键安装"]
    q = query.lower()
    if any(t in q for t in triggers):
        return "dsh-market-mcp"
    return None
```

**与 dsh-market-bridge V2.0 协同**：
- `dsh-market-bridge/scripts/dsh_market_bridge.py` 作为本地 Python 引擎
- MCPClientPool 包装为 dsh-market-mcp 服务
- 6 阶段 install pipeline（preflight + activation-check）是 V2.0 独有

## MCP服务配置

### 环境变量

```bash
# MCP集成根目录
export MCP_INTEGRATION_HOME="$HOME/.claude/mcp-integration"

# 远程MCP服务
export FIRECRAWL_API_KEY="your-firecrawl-key"
export EXA_API_KEY="your-exa-key"
export TAVILY_API_KEY="your-tavily-key"
export BRAVE_API_KEY="your-brave-key"
export DATAFORSEO_LOGIN="your-login"
export DATAFORSEO_PASSWORD="your-password"

# 内置MCP服务
export GEOAPIFY_KEY="your-geoapify-key"
export IPINFO_KEY="your-ipinfo-key"
```

## 性能指标

| 指标 | 目标 | 说明 |
|------|------|------|
| 路由准确率 | >98% | 正确路由到目标服务 |
| 调用成功率 | >95% | MCP调用成功率 |
| 平均响应时间 | <3s | 热调用响应时间 |
| 并发限制 | ≤10 | 避免资源耗尽 |

## 与天龙引擎协同

| 天龙组件 | 协同方式 |
|---------|---------|
| seo-geo | MCP调用 → GEO分析数据 |
| geo-optimizer | MCP调用 → Schema生成 |
| geo-content-generator | MCP调用 → 内容采集 |
| 35-04 GEO内容优化师 | MCP调用 → 品牌追踪 |
| 01调研师 | MCP调用 → 竞品扫描 |
| 04验证师 | MCP调用 → 引用检查 |
| 32-01市场研究 | MCP调用 → 语义搜索 |
| **trajectory-debug ⭐Stage 40** | **第 11 MCP 服务 · webserver RPC `POST /api/trajectory-debug/rpc`** |
| **dsh-market ⭐Stage 50.3** | **第 12 MCP 服务 · dsh-market-bridge V2.0 Python 引擎 + 6 阶段 install pipeline** |

## 版本信息

- **版本**: 2.1.0
- **创建时间**: 2026-08-19
- **升级时间**: 2026-08-26（Stage 50.3 协同增量 · dsh-market-as-MCP）
- **MCP集成**: MCP Integration Center V1.0 + Stage 40 trajectory-debug 第 11 服务 + Stage 50.3 dsh-market 第 12 服务

---

## 🔗 Stage 40 协同（⭐ v2.0 增量 · 第 11 MCP 服务注册）

> **触发源**：[devmom/dsh-trajectory-debug](https://github.com/devmom/dsh-trajectory-debug) v0.2.0 · MIT ✅ · 56/56 vitest PASS · 镜像在 `skills/dsh-trajectory-debug-integration/`
>
> **协同目标**：把 DSH trajectory-debug 14 RPC 方法 **注册成第 11 MCP 服务**（typert-无关 webserver 自定义路由）。

### v2.0 §1. 11 个 MCP 服务（含 trajectory-debug）

| # | 服务 | 类型 | 触发 |
|---|---|---|---|
| 1-10 | geo / llms / schema / brand / citation / serp / firecrawl / exa / tavily / brave | 既有 | 既有路由 |
| **11 ⭐NEW** | **trajectory-debug** | **HTTP RPC** | **`POST /api/trajectory-debug/rpc`** + 14 方法 |

### v2.0 §2. trajectory-debug 路由决策树

```python
# v2.0 · captain 调用流程
def route_to_trajectory(query: str) -> str:
    if "轨迹" in query or "trajectory" in query.lower():
        return "trajectory-debug"
    if "性能" in query or "perf" in query.lower():
        return "trajectory-debug"  # /perf
    if "回放" in query or "断点" in query.lower() or "replay" in query.lower():
        return "trajectory-debug"  # breakpoint.set / replay.step
    return None  # 其他 MCP 服务
```

### v2.0 §3. 14 RPC 方法映射

```bash
# 调用方式：通过 dsh_trajectory_bridge.py 调用
python skills/dsh-trajectory-debug-integration/scripts/dsh_trajectory_bridge.py call <method> --json '<params>'

# 14 RPC：
#   trajectory.list / step.context / perf
#   replay.start / replay.step / replay.seek
#   breakpoint.set / breakpoint.remove / breakpoint.list / breakpoint.resume
#   intervention.rerunTool
#   variant.fork / variant.list / variant.compare
#   export (OTel GenAI trace)
```

### v2.0 §4. DON'T 护栏（trajectory-debug 增量）

- ❌ **不要**把 trajectory-debug 当常规 MCP 服务用（仅在调试场景路由）
- ❌ **不要**让其他 10 个 MCP 服务内部递归调用 trajectory-debug（容易死循环）
- ❌ **不要**默认开启 `enableModelTools`（每 step 多一次 LLM 调用；opt-in）
- ❌ **不要**把 trajectory 数据与 firecrawl/exa 抓取的网页数据混合（语义层不一致）

### v2.0 §5. 验证矩阵增量

| # | 必检项 | 期望 | 状态 |
|---|---|---|---|
| 1 | 11 服务全部注册成功 | mcporter list 中出现 trajectory-debug | ⏳ |
| 2 | 路由决策树命中轨迹/性能/回放 3 类 query | trajectory-debug 通道激活 | ⏳ |
| 3 | 14 RPC 方法都能经 dsh_trajectory_bridge.py 调用 | 退出码契约 0/1/2/3/4 | ⏳ |
| 4 | 不影响其他 10 个 MCP 服务的既有路由 | 0 回归 | ⏳ |

---
