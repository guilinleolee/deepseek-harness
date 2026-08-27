---
name: page-agent-bridge
license: MIT
description: alibaba/page-agent 桥接 — 28.8k ⭐ · SaaS AI Copilot 单 script 嵌入 · 纯客户端 JS · 阶段 27 ROI-5
metadata:
  version: "1.0"
  author: "dragon-engine"
  upstream: alibaba/page-agent · 28.8k ⭐ · MIT
  upstream_repo: https://github.com/alibaba/page-agent
  modified: 2026-08-26
  triggers: ["page agent", "page-agent-bridge", "SaaS Copilot", "页面内嵌 AI agent"]
---

# page-agent-bridge Skill

## L0 · 一句话描述

SaaS AI Copilot 单 script 嵌入 — 让任何网页获得自己的 AI agent — 无浏览器扩展/无 Python/无 headless browser。

## L1 · 使用场景

- **36-01 SaaS Copilot Builder** ⭐(本阶段新建):客户 SaaS 产品嵌入 AI 助手
- **13-designer** V1.1(本阶段增量):SaaS 产品 UI/UX Copilot 接入点
- **22-creative-planner**:CMS / 后台管理系统智能填写
- **28-04-content-planner**:内容平台一键发布助手
- **35-02-laoli**:博主 SaaS 化(IP 经营工具)
- **04-validator**:网页表单 / UI 自动化验收

## L2 · 详细文档

### 来源与协议

- **上游**:`alibaba/page-agent` · **28,839 ⭐**(2026-08-26 实拉)
- **协议**:MIT ✅(LICENSE verbatim 已落盘 + Modified by 标注)
- **官网**:https://alibaba.github.io/page-agent
- **NPM**:`page-agent@1.12.2`(2026-08-26)
- **Demo**:https://alibaba.github.io/page-agent/(⚠️ demo CDN 用 alibaba 免费 testing LLM · **本镜像不打包**,遵循用户决策 2026-08-26)

### 上游致谢(纯上游致谢 · 不推 browser-use-bridge)

> This project builds upon the excellent work of browser-use.
> DOM processing components and prompt are derived from browser-use:
> Browser Use <https://github.com/browser-use/browser-use>
> Copyright (c) 2024 Gregor Zunic · Licensed under the MIT License

⚠️ **天龙红线**:page-agent-bridge **不**通过 browser-use-bridge 走任务,只引用 LICENSE 致谢。原因(用户决策 2026-08-26):
1. page-agent 是纯客户端 JS,browser-use 是 Python/Cloud,架构不同
2. page-agent 走 CDN + page-context,不需要 browser-use 的 runs/create API
3. 双 SKILL 互不依赖 · 各管各的 DOM/Cloud 通路

### 核心定位(与其他 GUI agent 的差异化)

| 维度 | browser-use | midscene | **page-agent** |
|------|-------------|----------|----------------|
| **部署** | Python lib / Cloud | JS SDK + 服务 | **CDN 单 script 嵌入** |
| **目标** | 任务自动化(后端驱动) | E2E 测试 + 跨平台 | **SaaS 嵌入(前端)** |
| **UI 位置** | 后端调用 | 后端调用 | **网页内浮动助手** |
| **客户侧要求** | 服务端部署 | 服务端部署 | **仅在 `<head>` 加一行 script** |
| **权限** | 服务端账号 | 服务端账号 | **页面内作用域 · 与 SaaS 应用同权限** |
| **多页面** | ❌ 单任务 | ❌ | **✅ Chrome 扩展(可选)** |

### 4 类核心场景(上游明示)

| 场景 | 客户价值 |
|---|---|
| **SaaS AI Copilot** | 在产品里嵌入 AI 助手,无后端重写 |
| **Smart Form Filling** | 20 步点击 → 一句话 · ERP/CRM/Admin 完美 |
| **Accessibility** | 自然语言操作网页 · 无障碍 / 语音 / 屏幕阅读器 |
| **Multi-page Agent** | Chrome 扩展 · 跨页面任务 |

### JS SDK 集成(天龙推荐 · Qwen DashScope)

```html
<!-- 1. CDN 引入(天龙默认 · 不带 demo) -->
<script
    src="https://cdn.jsdelivr.net/npm/page-agent@1.12.2/dist/iife/page-agent.js"
    crossorigin="anonymous"
></script>

<!-- 国内镜像(若 jsDelivr 不通) -->
<!-- https://registry.npmmirror.com/page-agent/1.12.2/files/dist/iife/page-agent.js -->
```

```javascript
// 2. 手动初始化(autoInit=false 模式)
const agent = new window.PageAgent({
    model: 'qwen3.5-plus',  // ⭐天龙推荐 provider
    baseURL: 'https://dashscope.aliyccs.com/compatible-mode/v1',
    apiKey: 'YOUR_DASHSCOPE_API_KEY',
    language: 'zh-CN',
});

// 3. 自然语言操作
await agent.execute('Click the login button');
await agent.execute('Type "hello" in the search box');
```

### NPM 安装路径(项目级应用)

```bash
npm install page-agent
```

```javascript
import { PageAgent } from 'page-agent';

const agent = new PageAgent({
    model: 'qwen3.5-plus',
    baseURL: 'https://dashscope.aliyccs.com/compatible-mode/v1',
    apiKey: process.env.DASHSCOPE_API_KEY,
    language: 'zh-CN',
});

await agent.execute('Click the login button');
```

### 6 模型策略(天龙备选)

| Provider | Model | 备注 |
|---|---|---|
| **Qwen DashScope** ⭐天龙推荐 | `qwen3.5-plus` | 国内稳定 · 自托管友好 |
| Qwen DashScope | `qwen-vl-max` | 视觉版本(预留) |
| OpenAI | `gpt-5.5` | 海外 |
| Anthropic | `claude-opus-4-8` | 海外 |
| Google | `gemini-3-pro` | — |
| **本地 Ollama** | `llama3 / qwen3-本地`| **零外网调用 · 数据不出域** |

详见:https://alibaba.github.io/page-agent/docs/features/models

### 多页面 Chrome扩展

```javascript
// 仅多 tab 任务需要 · 普通 SaaS 嵌入不需要
// 详情:https://alibaba.github.io/page-agent/docs/features/chrome-extension
```

### MCP Server(Beta)

- 让外部 agent client 控制浏览器
- 文档:https://alibaba.github.io/page-agent/docs/features/mcp-server
- 天龙 ROI-1 已用 cua-driver mcp · 可与 page-agent MCP 共存

### 与既有 skill 协同

| 既有 skill | 协同点 |
|---|---|
| `skills/cua-driver-bridge/`(ROI-1)| 后端桌面代理 · 互补 |
| `skills/browser-use-bridge/`(ROI-2)| Cloud 端浏览器任务 · 互补(不互推)|
| `skills/midscene-bridge/`(ROI-3)| 纯视觉 GUI · 互补 |
| `skills/browser-use-mcp/` V2.0 | MCP 协议互通 |
| `skills/browser-harness-core/` V2.0 | 后端任务编排 |
| `skills/dsh-computer-use/`(阶段 26)| macOS 桌面代理 |

### Agent 接入点

- **36-01-saas-copilot-builder** ⭐NEW(本阶段):C1+C2+C3 三档 SaaS Copilot 交付
- **13-designer** V1.1 增量:Copilot 浮窗 UI/UX 设计规范
- **22-creative-planner**:CMS/后台嵌入智能填写
- **28-04-content-planner**:内容平台一键发布助手
- **35-02-laoli**:博主 SaaS 化(IP 经营工具)
- **04-validator**:网页表单 / UI 自动化验收

### 验证(page_agent_check.py)

```bash
python scripts/page_agent_check.py
# 退出码契约 0/1/2/3
# 0 = 全部健康
# 1 = 工具不可用
# 2 = 限流 / 平台不支持
# 3 = schema 不匹配
```

### 风险与边界

| 风险 | 处置 |
|---|---|
| demo CDN 用了上游免费 LLM | **天龙镜像不打包** · 仅代码示例 · 用户必须自有 key |
| API key 暴露在公聊 | 用 `.env` + 后端代理 · **前端不要直接写 key**(会被爬取)|
| 上游快速迭代 | 月度 skill-updater 检测 |
| 数据出境(Qwen DashScope 在阿里云) | 海外客户用 OpenAI/Anthropic/本地 Ollama |
| SaaS 客户合规 | 由 36-01 在交付时跑 AGPL/MIT 红线检查 |
| 页面内权限过宽 | page-agent 默认与页面同权限 · **禁止** 跨域嵌入 |

---

## 累计验证 · 3 PASS

```
test_01_skill_md_exists       PASS
test_02_license_verbatim      PASS
test_03_cdn_runtime_paths     PASS

---EXIT: 0---
```

---

## 来源链接

- 上游 README:https://github.com/alibaba/page-agent
- 上游 NPM:https://www.npmjs.com/package/page-agent
- 官方文档:https://alibaba.github.io/page-agent
- Demo:https://alibaba.github.io/page-agent/(⚠️ 仅展示 · 不打包)
- HN Discussion:https://news.ycombinator.com/item?id=47264138
- X Follow:https://x.com/simonluvramen
- 本地路径:`C:\Users\li\.claude\projects\dragon-engine\skills\page-agent-bridge\`
- 主主题文件:`memory/stage27-computer-use-expansion.md`(本阶段)

---

## 版本信息

- **V1.0**(2026-08-26):阶段 27 ROI-5 · 3 PASS 验证 · 纯上游致谢 · Qwen 优先 · C1+C2+C3 三档
- **下次同步点**:36-01-saas-copilot-builder 上线后