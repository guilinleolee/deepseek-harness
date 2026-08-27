---
license: MIT
name: browser-use-mcp
description: Browser Use MCP Server V2.0 — 阶段 27 ROI-2 升级 · Cloud SDK V4 + 真源镜像 + 健康检查 · 通用浏览器自动化协议服务器
allowed-tools: Bash(browser-use:*)
triggers: ["browser use mcp", "browser-use-mcp"]
metadata:
  version: "2.0"
  author: "dragon-engine"
  upstream: browser-use/browser-use · 110.6k ⭐ · MIT
  upgrade: "2026-08-26"
  v1_legacy: "MCP-only · 10 工具"
  v2_features: ["Cloud SDK V4", "真源镜像", "健康检查 4 PASS", "browser-use-bridge 协同"]
---

# browser-use-mcp

## 版本升级摘要(V1.0 → V2.0 · 2026-08-26)

| 维度 | V1.0 | **V2.0** | 提升 |
|------|------|---------|------|
| **协议覆盖** | MCP stdio only | **MCP stdio + Cloud SDK V4 + REST** | +200% |
| **真源镜像** | ❌ 仅 MCP 协议层 | ✅ 配套 `skills/browser-use-bridge/` 真源 | 完整 SDK 链路 |
| **健康检查** | ❌ 无 | ✅ `browser_use_check.py` 4 PASS(本阶段新增)| CI gate 可用 |
| **Cloud LLM** | ❌ 自带 key | ✅ ChatBrowserUse 一键访问 6+ 模型 | 上游打通 |
| **Profile 复用** | ❌ 临时账号 | ✅ `profile-use` 真实 Chrome profile 同步 | 登录态 |
| **API key 治理** | ❌ 散落 | ✅ `.env.example` 4 key 字段占位 + .gitignore 保护 | 合规 |

> **底座升级**:本 SKILL 不再是孤立 MCP 协议层,而是与 `skills/browser-use-bridge/`(真源镜像) + `skills/browser-harness-core/`(会话管理 V2.0)构成的三件套。

## L0: 一句话描述

Browser Use MCP Server V2.0 — 通用浏览器自动化协议服务器,跨平台MCP客户端集成 + Cloud SDK V4 配套。

## L1: 使用场景

- **构建师**：MCP客户端通用浏览器自动化集成
- **验证师**：跨平台E2E测试、MCP测试框架
- **调研师**：多平台数据采集、登录态网站访问
- **分析师**：MCP感知的数据分析工作流
- **03-builder**:Cloud run API + custom tools 扩展
- **17-04-desktop-automation-engineer V3.0**:浏览器 GUI 部分
- **01-investigator**:登录态站点 + 跨境反爬(配 proxy_country_code)

## V2.0 新增入口

### Cloud SDK V4(配套 browser-use-bridge)

```python
from browser_use_sdk.v4 import BrowserUse

with BrowserUse() as client:
    run = client.runs.create("Find browser-use stars")
    result = client.runs.wait_for_completion(run.id)
```

### REST(curl)

```bash
curl -X POST https://api.browser-use.com/api/v4/runs \
  -H "X-Browser-Use-API-Key: $BROWSER_USE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"task":"Your task"}'
```

### 真实 Chrome Profile 同步

- 安装 `profile-use` 二进制(platform 分发)
- 设置 `BROWSER_USE_PROFILE_SYNC_URL`
- 见 browser-use-bridge SKILL.md §Profiles 段

### 健康检查(本阶段新增)

```bash
# 在 browser-use-bridge 目录
python scripts/browser_use_check.py

# 退出码契约 0/1/2/3
# 0 = 全部健康 · 1 = 工具不可用 · 2 = 限流/API key 缺失 · 3 = schema 不匹配
```

## L2: 详细文档

### 核心架构

```python
┌─────────────────────────────────────────────────────────────┐
│              browser-use MCP Server 架构                       │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────┐        │
│  │           MCP Protocol Layer                     │        │
│  │  stdio / HTTP / WebSocket                       │        │
│  └─────────────────────────────────────────────────┘        │
│                          ↓                                    │
│  ┌─────────────────────────────────────────────────┐        │
│  │           Browser Use Tools                       │        │
│  │  • navigate      • click                       │        │
│  │  • input_text   • screenshot                   │        │
│  │  • extract_content • wait                       │        │
│  │  • scroll       • evaluate                     │        │
│  └─────────────────────────────────────────────────┘        │
│                          ↓                                    │
│  ┌─────────────────────────────────────────────────┐        │
│  │           Browser Controller                       │        │
│  │  Chrome CDP / Playwright / Puppeteer           │        │
│  └─────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### MCP工具列表

| 工具 | 参数 | 功能 |
|------|------|------|
| `navigate` | url, wait_until | 导航到URL |
| `click` | selector, index | 点击元素 |
| `input_text` | selector, text | 输入文本 |
| `extract_content` | selector, pattern | 提取内容 |
| `screenshot` | full_page, path | 截图 |
| `scroll` | direction, amount | 滚动页面 |
| `wait` | selector, timeout | 等待元素 |
| `evaluate` | script | 执行JS脚本 |
| `go_back` | - | 返回上一页 |
| `get_html` | selector | 获取HTML |

### 安装配置

#### Claude Code配置

```json
{
  "mcpServers": {
    "browser-use": {
      "command": "npx",
      "args": ["browser-use-mcp"],
      "env": {
        "BROWSER_USE_HEADLESS": "true"
      }
    }
  }
}
```

#### 手动安装

```bash
# 安装browser-use
uv pip install browser-use

# 启动MCP Server
browser-use-mcp

# 或使用Python直接运行
python -m browser_use.mcp
```

### 使用示例

#### Claude Code中使用

```
用户: 帮我访问GitHub，搜索browser-use项目，提取Star数量

MCP调用:
→ navigate: url="https://github.com"
→ click: selector="[placeholder='Search GitHub']"
→ input_text: selector="[placeholder='Search GitHub']", text="browser-use"
→ click: selector="button[type='submit']"
→ extract_content: selector=".h3", pattern="Stars"
```

#### Python MCP客户端

```python
from browser_use.mcp import MCPClient

client = MCPClient("browser-use-mcp")

# 连接MCP Server
await client.connect()

# 执行工具
result = await client.call_tool("navigate", {
    "url": "https://github.com",
})

# 截图
screenshot = await client.call_tool("screenshot", {
    "path": "screenshot.png",
})
```

#### HTTP Server模式

```python
from browser_use.mcp.server import HTTPServer

server = HTTPServer(
    host="0.0.0.0",
    port=8080,
    auth="your-api-key",
)

await server.start()
```

### 工具使用详解

#### 1. navigate - 页面导航

```python
await mcp.navigate(
    url="https://example.com",
    wait_until="networkidle",  # load/domcontentloaded/networkidle
)
```

#### 2. click - 点击元素

```python
await mcp.click(
    selector="button.submit",  # CSS selector
    index=0,  # 如果有多个匹配，点击第几个
)
```

#### 3. input_text - 输入文本

```python
await mcp.input_text(
    selector="#search-input",
    text="Hello World",
    blur=True,  # 输入后失去焦点
)
```

#### 4. extract_content - 内容提取

```python
# 提取文本
result = await mcp.extract_content(
    selector=".product-card",
    pattern=None,
)

# 使用正则提取
result = await mcp.extract_content(
    selector=".price",
    pattern=r"\$\d+\.\d{2}",
)
```

#### 5. screenshot - 页面截图

```python
# 当前视口截图
await mcp.screenshot(
    path="screenshot.png",
    full_page=False,
)

# 整页截图
await mcp.screenshot(
    path="full-page.png",
    full_page=True,
)
```

#### 6. scroll - 页面滚动

```python
# 向下滚动
await mcp.scroll(
    direction="down",
    amount=500,  # 像素
)

# 向上滚动
await mcp.scroll(
    direction="up",
    amount=1000,
)
```

#### 7. evaluate - 执行JavaScript

```python
result = await mcp.evaluate(
    script="""
    () => {
        return {
            title: document.title,
            links: document.querySelectorAll('a').length,
            scrollHeight: document.body.scrollHeight,
        };
    }
    """
)
```

### 反检测配置

```python
from browser_use.mcp import MCPConfig

config = MCPConfig(
    headless=True,
    undetectable=True,  # 启用反检测
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    viewport={"width": 1920, "height": 1080},
    locale="zh-CN",
    timezone="Asia/Shanghai",
)

mcp = MCPClient("browser-use-mcp", config=config)
```

### 与其他MCP协同

```yaml
MCP协同矩阵:
  browser-use:
    - 多平台浏览器自动化
    - 登录态网站访问

  firecrawl:
    - 网页内容抓取
    - 结构化数据提取
    - 对比: browser-use=交互操作 / firecrawl=内容抓取

  tavily:
    - 搜索和新闻
    - 对比: tavily=搜索 / browser-use=交互操作

  playwright:
    - E2E测试
    - 对比: playwright=测试专用 / browser-use=通用自动化
```

### 故障排除

| 问题 | 解决方案 |
|------|---------|
| MCP Server启动失败 | 运行 `browser-use install chromium` |
| 元素找不到 | 使用 `wait` 等待元素出现 |
| 被网站检测 | 启用 `undetectable=True` |
| 截图空白 | 增加等待时间或使用 `wait_until="networkidle"` |
| Session中断 | 配置 `keep_alive=True` |

### 性能优化

```python
# 批量操作优化
async with mcp.batch() as batch:
    await batch.navigate(url)
    await batch.wait(selector=".content")
    await batch.screenshot()

# 并行执行
results = await mcp.gather(
    mcp.screenshot(path="1.png"),
    mcp.screenshot(path="2.png"),
    mcp.screenshot(path="3.png"),
)
```

## 技能元数据

- **版本**: V1.0
- **来源**: browser-use/browser-use (87k Stars, MIT License)
- **依赖**: browser-use>=0.2.0, Python 3.11+
- **MCP协议**: stdio, HTTP, WebSocket
- **兼容性**: Claude Code, Cursor, Windsurf, VS Code, 通用MCP客户端
