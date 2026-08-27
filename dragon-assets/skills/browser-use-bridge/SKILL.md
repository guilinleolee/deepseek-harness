---
name: browser-use-bridge
license: MIT
description: browser-use/browser-use 桥接 — Odysseys 87.4% 第一 · Cloud SDK V4 + CLI skill install · 阶段 27 ROI-2
metadata:
  version: "1.0"
  author: "dragon-engine"
  upstream: browser-use/browser-use · 110.6k ⭐ · MIT
  upstream_repo: https://github.com/browser-use/browser-use
  modified: 2026-08-26
  triggers: ["browser use", "browser-use-bridge", "Odysseys", "Browser Use Cloud"]
---

# browser-use-bridge Skill

## L0 · 一句话描述

浏览器 AI agent 头部开源项目(Odysseys 87.4% 第一 · 110.6k ⭐)的天龙封装层 — Cloud SDK V4 + CLI skill install 双入口。

## L1 · 使用场景

- 17-04 桌面自动化工程师 V3.0:浏览器 GUI 操作(browser-use 浏览器部分)
- 09-02 编排协调师:多 agent 共享同一云端浏览器
- 28-04 内容策划师:登录态站点数据采集(Gmail/Slack/Notion 等 1000+ 集成)
- 01 调研师:跨境/反爬场景(代理轮换 + captcha solving)
- 04 验证师:E2E 测试 fallback
- 35-02 社媒运营:跨平台账号态操作

## L2 · 详细文档

### 来源与协议

- **上游**:`browser-use/browser-use` · **110,555 ⭐**(2026-08-26 实拉)
- **协议**:MIT ✅(LICENSE verbatim 已落盘 + Modified by 标注)
- **官网**:https://browser-use.com
- **Cloud 文档**:https://docs.browser-use.com
- **Cloud SDK 文档**:https://docs.browser-use.com/cloud/quickstart

### 核心定位(Odysseys leaderboard #1)

- **87.4% 平均成功率** · 超过 OpenAI / Anthropic / Google / Microsoft CUA
- 测于 200 个 long-horizon web 任务
- BU Bench V1(100 个真实浏览器任务)开源

### 双入口架构

```
┌─────────────────────────────────────────────────────────────┐
│              browser-use-bridge 架构(双入口)                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ── 入口 1: agent skill install ──                         │
│   DSH/OpenClaw/Codex/Cursor/Hermes                          │
│       ↓                                                     │
│   "browser-use skill install"                               │
│       ↓                                                     │
│   一次安装 · agent 可直接调:                                  │
│     "Upload this video to YouTube"                          │
│     "Compare these three laptops..."                        │
│     "Fill in this job application..."                       │
│                                                             │
│   ── 入口 2: Python/Node SDK ──                             │
│   自研产品 / 批量爬取 / 调度                                  │
│       ↓                                                     │
│   from browser_use_sdk.v4 import BrowserUse                  │
│   from browser_use_sdk.v3 import BrowserUse  (browser mgmt) │
│       ↓                                                     │
│   Cloud runs / Cloud infrastructure / Profiles               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 8 模块能力矩阵

| # | 模块 | 用途 | CLI / SDK 入口 |
|---|---|---|---|
| 1 | `run_agent` | 一句话任务 | `browser-use run "task"` |
| 2 | `cloud_browser` | 云端浏览器(已 key)| `browser-use cloud start` / SDK V3 `browsers.create` |
| 3 | `cloud_run` | Cloud run API | `POST /api/v4/runs` |
| 4 | `profiles` | 真实 Chrome profile 复用 | `profile-use` binary |
| 5 | `extract` | 结构化数据提取 | `browser-use extract` |
| 6 | `scrape` | 一次性爬取 | `browser-use scrape URL` |
| 7 | `stealth` | 代理轮换 + captcha | Cloud SDK 配置 |
| 8 | `integrations` | 1000+ 集成 | Cloud 平台配置 |

### Cloud SDK V4(推荐生产档 · 用户已配 key)

```python
from browser_use_sdk.v4 import BrowserUse

with BrowserUse() as client:
    run = client.runs.create("Find the top Hacker News story")
    result = client.runs.wait_for_completion(run.id)
    print(result.result)
```

### Cloud Infrastructure V3(浏览器管理)

```python
from browser_use_sdk.v3 import BrowserUse

client = BrowserUse()
browser = client.browsers.create(proxy_country_code="us")
print(browser.cdp_url)
# 用 Playwright/Puppeteer 连 cdp_url
client.browsers.stop(browser.id)
```

### curl REST 入口

```bash
curl -X POST https://api.browser-use.com/api/v4/runs \
  -H "X-Browser-Use-API-Key: $BROWSER_USE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"task":"Your task"}'
```

### LLM provider 策略

| 模型 | 入口 | 说明 |
|---|---|---|
| **bu-2-0-mini-preview** ⭐推荐 | `ChatBrowserUse()` | 浏览器优化 · 3-5× 更快 · SOTA |
| bu-30-0-a3b-preview | 同上 | 开源 preview · 仍用 default agent prompt |
| anthropic/claude-opus-4-8 | `ChatBrowserUse(model=...)` | 通过 BROWSER_USE_API_KEY 一键访问 |
| anthropic/claude-sonnet-4-6 | 同上 | — |
| openai/gpt-5.5 | 同上 | — |
| google/gemini-3-pro | 同上 | — |
| **自带 key 路径** | `ChatOpenAI / ChatAnthropic / ChatGoogle` | 需对应 provider key |

### Profiles 真实 Chrome profile 复用

- 安装 `profile-use` binary · 平台分发
- 与远程浏览器同步认证 profile
- 走 `BROWSER_USE_PROFILE_SYNC_URL`

### Custom Tools 扩展

```python
from browser_use import Tools

tools = Tools()

@tools.action(description='Description of what this tool does.')
def custom_tool(param: str) -> str:
    return f"Result: {param}"

agent = Agent(task="Your task", llm=llm, browser=browser, tools=tools)
```

### AgentMail 临时账号收件

> 用于临时账号 + 收件验证码(注册流程自动化)

### 与既有 skill 协同

| 既有 skill | 协同点 |
|---|---|
| `skills/browser-use-mcp/`(升级 V2.0)| MCP 协议适配(本阶段同步升级)|
| `skills/browser-harness-core/`(升级 V2.0)| 会话管理 + Login 态复用 |
| `skills/agent-browser/` (Vercel Labs) | 确定性 ref 元素选择 · 性能关键 |
| `skills/cua-driver-bridge/`(本阶段 ROI-1)| 桌面代理 · 浏览器外场景 |
| `skills/dsh-computer-use/`(阶段 26)| macOS native action 兜底 |
| `skills/midscene-bridge/`(本阶段 ROI-3)| 纯视觉 GUI 备选 |

### Agent 接入点

- **17-04-desktop-automation-engineer** V3.0:浏览器 GUI 部分走 browser-use
- **09-tool-discovery** V2.0:browser-use + cua + midscene 三选一发现
- **01-investigator**:登录态站点 + 跨境反爬
- **04-validator**:E2E 兜底
- **28-04-content-planner**:社媒数据采集(小红书 / 微博 / 抖音)
- **35-02-laoli**:跨平台账号态操作

### 验证(browser_use_check.py)

```bash
python scripts/browser_use_check.py
# 退出码契约 0/1/2/3
# 0 = 全部健康
# 1 = 工具不可用
# 2 = 限流 / API key 缺失
# 3 = schema 不匹配
```

### 风险与边界

| 风险 | 处置 |
|---|---|
| Cloud API 配额爆(20 req/min 注册档)| 退匿名档 / 自带 provider key |
| profile 同步失败 | 退临时账号 + AgentMail |
| captcha 频繁 | Cloud stealth 档(额外计费)|
| 反爬拦截 | 配 proxy_country_code 轮换 |
| 上游快速迭代(7 天 1 commit)| 月度 skill-updater 检测 |

---

## 累计验证 · 8 PASS

```
test_01_skill_md_exists          PASS
test_02_license_verbatim         PASS
test_03_runtime_conf_paths       PASS
test_04_env_example_4_fields     PASS
test_05_cloud_sdk_import         PASS
test_06_rest_endpoint_schema     PASS
test_07_browser_use_check_4_code PASS
test_08_llm_provider_strategy    PASS

---EXIT: 0---
```

---

## 来源链接

- 上游 README:https://github.com/browser-use/browser-use
- 官方文档:https://docs.browser-use.com
- Cloud 文档:https://docs.browser-use.com/cloud/quickstart
- Cloud 控制台:https://cloud.browser-use.com
- Odysseys leaderboard:https://odysseysbench.com/leaderboard
- Browser Use CLI 安装:https://github.com/browser-use/browser-harness/blob/main/install.md
- 本地路径:`C:\Users\li\.claude\projects\dragon-engine\skills\browser-use-bridge\`
- 主主题文件:`memory/stage27-computer-use-expansion.md`(本阶段)

---

## 版本信息

- **V1.0**(2026-08-26):阶段 27 ROI-2 · 8 模块封装 + Cloud SDK V4 + 8 PASS 验证
- **下次同步点**:browser-use-mcp V2.0 + browser-harness-core V2.0 升级后