---
name: trendradar-core
description: TrendRadar 多平台热点新闻聚合 MCP 客户端。直接调用 trendradar-* 工具做新闻查询/搜索/分析/爬取/存储同步，覆盖知乎/微博/抖音/B站/小红书/36氪/Hacker News 等 50+ 平台。Use when user asks about hot/trending topics, multi-platform news aggregation, or wants daily news briefings. Auto-loads via .claude.json stdio config.
triggers:
  - "今日热点"
  - "热搜"
  - "新闻聚合"
  - "多平台舆情"
  - "TrendRadar"
  - "trendradar"
license: MIT
---

# TrendRadar Core · MCP 客户端

TrendRadar 通过 FastMCP 2.0 stdio 模式已注册到全局 `~/.claude.json` 的 `mcpServers.trendradar`。
所有工具以 `mcp__trendradar__<tool_name>` 命名空间暴露给 Claude / 天龙引擎 agents。

> **来源**：[sansan0/TrendRadar](https://github.com/sansan0/TrendRadar) (MIT ✅)
> **MCP Server 版本**：v4.1.0 · **TrendRadar 本体**：v6.10.0
> **接入文件**：`C:\Users\li\.claude.json` → `mcpServers.trendradar`
> **依赖路径**：`E:\TrendRadar\.venv\Scripts\python.exe`（含 fastmcp 2.12.5）
> **生效方式**：重启 Claude Code / 重新加载插件

---

## L0 · 一句话 (≤15字)
调用 trendradar-* 工具做多平台热点新闻查询与分析。

## L1 · 使用场景 (50-100字)
当用户要"看今天热搜"、"查知乎/微博/抖音热点"、"舆情分析"、"行业趋势摘要"、"跨平台对比"、"AI 过滤新闻噪音"时，调用 trendradar MCP 工具读取本地已爬取数据（output/news/*.db），无需再发起网络爬取。

---

## L2 · 详细文档

### 2.1 接入方式

**已配置**（一次性写入）：

```json
// C:\Users\li\.claude.json → mcpServers.trendradar
{
  "type": "stdio",
  "command": "E:/TrendRadar/.venv/Scripts/python.exe",
  "args": ["-m", "mcp_server.server"],
  "env": { "PYTHONIOENCODING": "utf-8" }
}
```

**项目根自动定位**：MCP server 启动后通过 `Path(__file__).parent.parent.parent` 自动找到 `E:\TrendRadar`，无需设置 cwd。

### 2.2 核心工具清单

调用形式：`mcp__trendradar__<tool_name>(...)`，所有工具返回 JSON 字符串。

| 模块 | 工具 | 用途 | 关键参数 |
|------|------|------|----------|
| **日期解析** | `resolve_date_range` | 解析自然语言日期（推荐先调） | `expression: "本周"/"最近7天"` |
| **数据查询** | `get_latest_news` | 最新一批新闻 | `platforms, limit, include_url` |
| | `get_trending_topics` | 热点话题统计 | `top_n, mode, extract_mode` |
| **RSS** | `get_latest_rss` | 最新 RSS 条目 | `feeds, days, limit` |
| | `search_rss` | RSS 关键词搜索 | `keyword, feeds, days` |
| **搜索** | `search_news` | 统一搜索（热榜+RSS） | `query, search_mode, date_range` |
| **分析** | `analyze_data_insights` | 数据洞察 | `insight_type, topic, date_range` |
| | `analyze_sentiment` | 情感分析 | `topic, date_range` |
| **配置** | `get_current_config` | 获取当前配置 | `section` |
| **系统** | `get_system_status` | 系统状态检查 | — |
| | `check_version` | 检查版本更新 | `proxy_url` |
| | `trigger_crawl` | 手动触发爬取 | `platforms, save_to_local` |
| **存储** | `sync_from_remote` | 拉取远程数据 | `days` |
| | `get_storage_status` | 存储状态 | — |

完整工具列表参见 [e:\TrendRadar\mcp_server\server.py](file:///E:/TrendRadar/mcp_server/server.py)。

### 2.3 MCP Resources（只读）

| URI | 说明 |
|-----|------|
| `config://platforms` | 支持的热榜平台列表 |
| `config://rss-feeds` | RSS 订阅源列表 |
| `data://available-dates` | 本地可查询日期范围 |
| `config://keywords` | 关注词配置 |

### 2.4 调用流程（推荐）

```python
# Step 1: 解析日期（解决 LLM 计算日期不一致问题）
mcp__trendradar__resolve_date_range("最近7天")
# → {"date_range": {"start": "2026-08-05", "end": "2026-08-12"}, ...}

# Step 2: 搜索/分析（用上一步返回的 date_range）
mcp__trendradar__search_news(
    query="AI",
    date_range={"start": "2026-08-05", "end": "2026-08-12"},
    include_rss=True,
    limit=20
)

# Step 3: 情感分析
mcp__trendradar__analyze_sentiment(
    topic="AI",
    date_range={"start": "2026-08-05", "end": "2026-08-12"}
)
```

### 2.5 数据展示建议

- **默认展示完整返回数据**，除非用户明确说"总结"/"挑重点"
- 用户问"为什么只显示部分"→ 默认应当全展示
- 大数据集（>50 条）按平台分组后再摘要

---

## 3. 与天龙引擎协同

| 协同对象 | 用法 |
|----------|------|
| **agent-reach** | 实时网页抓取 → 落库 → TrendRadar 过滤 |
| **requesthunt** | 社交媒体监听 → TrendRadar 聚合分析 |
| **32-01 市场研究** | 调用 trendradar 工具拿原始数据再分析 |
| **35-06 博主蒸馏** | 抽取博主风格做新闻摘要 |
| **lightrag-knowledge-base** | 过滤结果入库长期记忆 |
| **paperclip-heartbeat** | 定时调度爬取任务 |

## 4. 触发词典（自然语言路由）

听到以下关键词，**优先**调用本 skill：
- "今日热点"/"热搜"/"热榜" → `get_trending_topics`
- "查新闻"/"找新闻"/"最近 X 的 X" → `search_news`
- "分析 X"/"X 舆情"/"X 趋势" → `analyze_data_insights` + `analyze_sentiment`
- "刷新一下"/"手动爬取" → `trigger_crawl`
- "数据同步"/"拉最新数据" → `sync_from_remote`

## 5. 注意事项

| 项 | 说明 |
|----|------|
| **本地数据依赖** | 工具读取 `output/news/*.db` 等本地存储；无数据时返回空 |
| **每日自动爬取** | 已有 Windows 计划任务 `TrendRadar-Daily`（每日 10:00） |
| **路径不可移动** | TrendRadar 项目、`.venv/` 必须保留原位（`E:\TrendRadar`） |
| **重启生效** | 写入 `~/.claude.json` 后需重启 Claude Code |
| **HTTP 备选** | 也可启动 `--transport http --port 3333` 通过 URL 调用 |
| **API Key** | AI 过滤功能需 `AI_API_KEY` 环境变量；查询/搜索无需 |

## 6. 故障排查

| 现象 | 排查 |
|------|------|
| 工具不显示 | 重启 Claude Code；检查 `~/.claude.json` 中 trendradar 块语法 |
| 启动报错 | 手动跑 `E:/TrendRadar/.venv/Scripts/python.exe -m mcp_server.server` 看错误 |
| 数据为空 | 跑 `trigger_crawl(save_to_local=True)` 手动爬一次 |
| 路径失效 | TrendRadar 项目被移动 → 更新 `.claude.json` 中 command 路径 |
| 模块找不到 | `.venv` 损坏 → 重跑 `setup-windows.bat` |

## 7. 版本与升级

```bash
# 查看本地版本
cd E:\TrendRadar && .venv\Scripts\python.exe -c "import mcp_server; print(mcp_server.__version__)"

# 检查远端更新
mcp__trendradar__check_version()

# 升级（先备份）
git pull && .venv\Scripts\python.exe -m pip install -r requirements.txt
```

---

**维护者**：天龙引擎 · 32-01 市场研究 + 01 调研师 协同
**关联**：[trending-research skill 升级参考](https://github.com/sansan0/TrendRadar)