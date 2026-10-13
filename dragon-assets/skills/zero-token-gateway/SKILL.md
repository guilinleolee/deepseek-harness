---
license: UNKNOWN
name: zero-token-gateway
description: |
github_repo: linuxhsj/openclaw-zero-token
github_hash: 45371627469647d8e4be8b9569437b21bffdaed2
last_updated: 2026-04-25
source_type: derived
version: 1.0.0
支持平台: DeepSeek, Claude Web, ChatGPT, Gemini, Qwen(国际/国内), Kimi, 豆包, GLM, Grok, Manus
⚠️ 免责声明: 仅用于技术研究和个人学习目的
triggers: ["zero token gateway", "Zero Token Gateway"]
author: 天龙引擎团队
created: 2026-03-19
category: ai-gateway
---

# Zero Token Gateway

零成本AI访问网关服务，通过浏览器登录方式免费使用11个AI平台。

## 支持平台 (11个)

| 平台 | 模型 | 质量 | 认证方式 |
|------|------|------|---------|
| Claude Web | claude-sonnet-4-6, claude-opus-4-6, claude-haiku-4-6 | 0.95 | sessionKey+cookie |
| ChatGPT Web | gpt-4, gpt-4-turbo | 0.93 | accessToken+cookie |
| Gemini Web | gemini-pro, gemini-ultra | 0.92 | cookie |
| DeepSeek | deepseek-chat, deepseek-reasoner | 0.88 | token+cookie |
| Qwen International | qwen-3.5-plus, qwen-3.5-turbo | 0.85 | token |
| Qwen China | qwen-3.5-plus, qwen-3.5-turbo | 0.85 | token |
| Kimi | moonshot-v1-8k, moonshot-v1-32k, moonshot-v1-128k | 0.82 | token |
| Doubao | doubao-seed-2.0, doubao-pro | 0.80 | token |
| Grok Web | grok-1, grok-2 | 0.85 | cookie |
| GLM Web | glm-4-plus, glm-4-think | 0.82 | token |
| Manus | manus-1, manus-1.6 | 0.88 | apiKey (免费额度) |

## 快速开始

### 1. 启动Chrome调试模式

```bash
# macOS/Linux
google-chrome --remote-debugging-port=9222 --user-data-dir=~/.chrome-openclaw-debug

# Windows
chrome.exe --remote-debugging-port=9222 --user-data-dir=%USERPROFILE%\.chrome-openclaw-debug
```

### 2. 登录平台

在浏览器中登录各平台：
- https://claude.ai/
- https://chatgpt.com/
- https://chat.deepseek.com/
- 等等...

### 3. 捕获认证

```bash
node scripts/auth-capture.js --platform deepseek,claude,gemini
```

### 4. 启动Gateway

```bash
node scripts/gateway.js --port 3002
```

## API端点

### OpenAI兼容API

```bash
# POST /v1/chat/completions
curl -X POST http://localhost:3002/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "auto",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### AskOnce多模型对比

```bash
# POST /v1/ask-once
curl -X POST http://localhost:3002/v1/ask-once \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is AI?",
    "platforms": ["claude", "deepseek", "gemini"]
  }'
```

### 健康检查

```bash
curl http://localhost:3002/health
```

### 可用平台列表

```bash
curl http://localhost:3002/platforms
```

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `ZERO_TOKEN_PORT` | 3002 | Gateway端口 |
| `ZERO_TOKEN_CONFIG_DIR` | ~/.openclaw-zero-state | 配置目录 |
| `ZERO_TOKEN_PRIORITY` | true | Zero Token优先 |
| `ZERO_TOKEN_FALLBACK` | true | 失败时回退到API |

## 与天龙引擎集成

```javascript
const { getRouter } = require('../shared/ai-router.js');

const router = getRouter();

// Zero Token优先选择
const selection = router.selectWithZeroTokenPriority({
  qualityPriority: true
});

// AskOnce多模型对比
const results = await router.askOnce('What is AI?', ['claude', 'deepseek', 'gemini']);
```

## 免责声明

⚠️ **重要提示**

本功能仅用于**技术研究和个人学习目的**。使用本功能访问第三方AI服务可能违反其服务条款。用户需自行承担法律风险。

**建议**:
- 仅用于研究和个人项目
- 生产环境请使用官方API
- 遵守各平台服务条款
- 不用于商业目的

## 相关技能

- [ai-router](../shared/ai-router.js) - AI路由核心
- [zero-token-provider](../shared/zero-token-provider.js) - 零成本Provider
- [chrome-cdp](../shared/chrome-cdp.js) - Chrome CDP工具

## 参考

- [openclaw-zero-token](https://github.com/linuxhsj/openclaw-zero-token) - 上游项目