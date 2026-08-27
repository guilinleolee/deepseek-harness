---
name: browser-harness-core
license: MIT
description: 浏览器自动化核心引擎 V2.0 — 阶段 27 ROI-2 升级 · browser-use-bridge adapter · Cloud 浏览器 + 本地 CDP 双轨
触发场景：需要浏览器执行多步骤任务、跨页面操作、数据采集、表单填写、登录态管理、页面截图等浏览器自动化场景。
与 web-access 的 WebSearch/WebFetch 不同，browser-harness-core 处理需要真实浏览器环境的复杂交互任务。
metadata:
  version: "2.0"
  author: "天龙引擎 + dragon-engine"
  upgrade: "2026-08-26"
  v1_legacy: "本地 CDP only"
  v2_features: ["browser-use-bridge adapter", "Cloud 浏览器", "Profile 同步", "双轨架构"]
triggers: ["browser harness core", "browser-harness-core Skill"]
---

# browser-harness-core Skill

## 版本升级摘要(V1.0 → V2.0 · 2026-08-26)

| 维度 | V1.0 | **V2.0** | 提升 |
|------|------|---------|------|
| **浏览器驱动** | 本地 Chrome CDP only | **本地 CDP + Cloud 浏览器(browser-use)** | 双轨 |
| **会话管理** | 单一持久化 | **持久化 + Cloud 临时 + profile 同步** | 3 档 |
| **Profile 复用** | ❌ 无 | ✅ `profile-use` 真实 Chrome profile 同步 | 登录态 |
| **Cloud 任务** | ❌ 无 | ✅ `browser-use-bridge` runs.create + wait_for_completion | 跨境反爬 |
| **MCP 协议** | ❌ 自建 | ✅ 与 `browser-use-mcp V2.0` 互通 | 协议层 |
| **协同 SKILL** | web-access 单链路 | **+ browser-use-bridge + browser-use-mcp + midscene-bridge + cua-driver-bridge** | 全栈 |

> **架构变化**:V2.0 不再是孤立浏览器会话,而是与 browser-use-bridge(真源镜像) + browser-use-mcp V2.0(协议层) + midscene-bridge(纯视觉备选)构成的全栈。

## 概述

browser-harness-core V2.0 是浏览器自动化核心引擎,提供:
- **会话管理 V2.0** - 持久化浏览器会话 + Cloud 浏览器 + profile 同步
- **双轨驱动** - 本地 CDP + Cloud browser-use(根据场景切换)
- **多步骤任务** - 支持复杂的多页面操作流程
- **状态追踪** - 记录操作历史，支持断点恢复
- **错误恢复** - 智能重试和回退机制
- **与 web-access 协同** - 轻量任务用 web-access，复杂交互用 browser-harness-core

## V2.0 双轨驱动选择

```yaml
browser-harness-core V2.0:
  local_cdp:
    use_when: 本地开发 / 调试 / 无 Cloud key
    driver: chrome-cdp
    skill: agent-browser (Vercel Labs)
  cloud_browser:
    use_when: 跨境反爬 / 多用户 / 登录态复用
    driver: browser-use Cloud SDK V4
    skill: browser-use-bridge (本阶段新增)
    requires: BROWSER_USE_API_KEY
  vision_only:
    use_when: canvas / 跨域 iframe / 无语义标注
    driver: midscene-bridge (本阶段 ROI-3)
```

## 核心架构

```
┌─────────────────────────────────────────────────────────────┐
│              browser-harness-core 架构                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Session Manager ──▶ Browser Pool ──▶ Task Executor        │
│         │                  │                │                │
│         ▼                  ▼                ▼                │
│  State Tracker      CDP Proxy         Action Logger         │
│                                                             │
│  与 web-access 协同层                                      │
│  ├── 轻量任务: WebSearch/WebFetch (web-access)           │
│  └── 复杂交互: 多页面/登录/操作 (browser-harness-core)   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 前置检查

```bash
# 检查依赖
bash ~/.claude/skills/browser-harness-core/scripts/check-deps.sh

# 检查 Chrome CDP 可用性
bash ~/.claude/skills/browser-harness-core/scripts/check-cdp.sh
```

## 快速开始

### 1. 启动浏览器会话

```bash
# 创建新会话
bash ~/.claude/skills/browser-harness-core/scripts/session.sh create --name "research-$(date +%Y%m%d)"

# 列出活跃会话
bash ~/.claude/skills/browser-harness-core/scripts/session.sh list

# 恢复会话
bash ~/.claude/skills/browser-harness-core/scripts/session.sh resume --id <session-id>
```

### 2. 执行多步骤任务

```bash
# 执行任务序列
bash ~/.claude/skills/browser-harness-core/scripts/task.sh execute \
  --session <session-id> \
  --steps '[{"action":"navigate","url":"https://example.com"},{"action":"click","selector":"#login"},{"action":"fill","selector":"#username","value":"user"},{"action":"fill","selector":"#password","value":"pass"},{"action":"click","selector":"#submit"}]'

# 执行文件中的任务序列
bash ~/.claude/skills/browser-harness-core/scripts/task.sh execute-file \
  --session <session-id> \
  --file ./tasks/login-flow.yaml
```

### 3. 数据采集

```bash
# 采集页面数据
bash ~/.claude/skills/browser-harness-core/scripts/harvest.sh \
  --session <session-id> \
  --url "https://example.com/products" \
  --selector ".product-item" \
  --fields '{"title":"h3","price":".price","rating":".stars"}' \
  --output ./data/products.json

# 采集翻页数据
bash ~/.claude/skills/browser-harness-core/scripts/harvest.sh \
  --session <session-id> \
  --url "https://example.com/products" \
  --selector ".product-item" \
  --pagination '{"next_button":".next-page","max_pages":10}' \
  --output ./data/products-all.json
```

### 4. 页面截图

```bash
# 全页面截图
bash ~/.claude/skills/browser-harness-core/scripts/screenshot.sh \
  --session <session-id> \
  --url "https://example.com" \
  --full-page \
  --output ./screenshots/page.png

# 指定区域截图
bash ~/.claude/skills/browser-harness-core/scripts/screenshot.sh \
  --session <session-id> \
  --selector ".content-area" \
  --output ./screenshots/content.png
```

## 任务序列格式

### YAML 格式

```yaml
# tasks/login-flow.yaml
name: 登录流程
session: persistent  # persistent | new | resume
timeout: 30000

steps:
  - action: navigate
    url: "https://example.com/login"
    wait: networkidle

  - action: click
    selector: "#username-field"
    wait: visible

  - action: fill
    selector: "#username"
    value: "{{USERNAME}}"
    wait: stable

  - action: fill
    selector: "#password"
    value: "{{PASSWORD}}"

  - action: click
    selector: "#login-button"

  - action: wait
    condition: url_contains
    value: "/dashboard"

  - action: screenshot
    selector: "#dashboard-content"
    output: "./screenshots/dashboard.png"

on_failure:
  action: screenshot
  output: "./screenshots/error.png"
  continue: false
```

### JSON 格式

```json
{
  "name": "数据采集流程",
  "session": "persistent",
  "steps": [
    {"action": "navigate", "url": "https://example.com", "wait": "networkidle"},
    {"action": "wait", "selector": ".content", "state": "visible"},
    {"action": "scroll", "distance": 500},
    {"action": "extract", "selector": ".item", "multiple": true, "fields": {"title": "h3", "link": "a@href"}}
  ]
}
```

## 与 web-access 协同策略

| 任务类型 | 推荐工具 | 理由 |
|----------|---------|------|
| 简单搜索/信息获取 | **web-access** | 轻量、快速、无需浏览器 |
| 登录后内容访问 | **browser-harness-core** | 需要会话管理 |
| 多页面操作流程 | **browser-harness-core** | 状态追踪、断点恢复 |
| 复杂表单填写 | **browser-harness-core** | 验证、重试机制 |
| 动态渲染页面抓取 | **browser-harness-core** | JavaScript 执行环境 |
| 社交媒体操作 | **browser-harness-core** | 登录态、复杂交互 |

## 错误处理

### 自动重试配置

```yaml
retry:
  max_attempts: 3
  backoff: exponential
  initial_delay: 1000
  max_delay: 30000
  retry_on:
    - timeout
    - network_error
    - element_not_found
```

### 错误恢复策略

```bash
# 启用错误恢复
bash ~/.claude/skills/browser-harness-core/scripts/task.sh execute \
  --session <session-id> \
  --file ./tasks/complex-flow.yaml \
  --retry \
  --checkpoint ./checkpoints/complex-flow.cpt
```

## 会话管理

### 会话类型

| 类型 | 说明 | 使用场景 |
|------|------|---------|
| `persistent` | 持久化会话，可恢复 | 长时间任务、跨会话操作 |
| `new` | 新会话，执行后清理 | 一次性任务 |
| `resume` | 恢复指定会话 | 断点续传 |

### 会话操作

```bash
# 创建持久会话
session.sh create --name "research-001" --type persistent

# 查看会话状态
session.sh status --id <session-id>

# 保存检查点
session.sh checkpoint --id <session-id> --name "step-3-done"

# 恢复检查点
session.sh restore --checkpoint <checkpoint-id>

# 关闭会话
session.sh close --id <session-id>
```

## 环境变量

```bash
# CDP 连接配置
export CDP_HOST=localhost
export CDP_PORT=9222
export CDP_PROTOCOL=ws

# 浏览器配置
export BROWSER_HEADLESS=false
export BROWSER_USER_DATA_DIR=~/.claude/browser-harness/sessions

# 超时配置
export DEFAULT_TIMEOUT=30000
export NAVIGATION_TIMEOUT=60000
```

## 最佳实践

1. **优先使用 web-access** - 简单任务避免启动浏览器
2. **会话复用** - 同一网站操作复用会话，避免重复登录
3. **设置检查点** - 长时间任务定期保存检查点
4. **错误截图** - 失败时自动截图，便于调试
5. **限制并发** - 避免同时运行过多浏览器实例

## 文件结构

```
browser-harness-core/
├── SKILL.md                    # 本文件
├── scripts/
│   ├── check-deps.sh          # 依赖检查
│   ├── check-cdp.sh           # CDP 可用性检查
│   ├── session.sh             # 会话管理
│   ├── task.sh                # 任务执行
│   ├── harvest.sh             # 数据采集
│   └── screenshot.sh          # 页面截图
├── templates/
│   ├── login-flow.yaml       # 登录流程模板
│   ├── scrape-flow.yaml       # 采集流程模板
│   └── multi-step.yaml       # 多步骤模板
└── docs/
    └── EXAMPLES.md            # 使用示例
```

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0 | 2026-05-01 | 初始版本 |
