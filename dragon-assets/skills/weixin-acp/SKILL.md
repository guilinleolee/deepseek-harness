---
license: UNKNOWN
github_repo: wong2/weixin-agent-sdk
github_hash: 74694e31c8b39dee388f1ce824bc44690f6af778
last_updated: 2026-04-25
source_type: derived
triggers: ["weixin acp", "weixin-acp - 微信 Claude Code 桥接"]
---
# weixin-acp - 微信 Claude Code 桥接

基于 [wong2/weixin-agent-sdk](https://github.com/wong2/weixin-agent-sdk) 的微信接入能力，让 Claude Code 可以直接处理微信消息。

## 核心能力

- 📱 **微信消息接收** - 文本、图片、语音、视频、文件
- 💬 **多轮对话** - 支持上下文记忆
- 🔄 **断点续传** - 自动重连，消息不丢失
- 🤖 **ACP协议** - 直接对接 Claude Code

## 快速开始

### 方式一：直接启动（推荐）

```bash
# 一键启动 Claude Code 微信桥接
npx weixin-acp claude-code
```

首次运行会弹出二维码，使用微信扫码登录。

### 方式二：天龙引擎调用

```bash
# 通过天龙命令启动
/weixin-acp start

# 查看状态
/weixin-acp status

# 停止服务
/weixin-acp stop
```

## 环境要求

| 依赖 | 版本 | 说明 |
|------|------|------|
| Node.js | ≥ 22 | 运行环境 |
| 微信账号 | - | 个人微信号（扫码登录） |

## 工作原理

```
┌─────────────────────────────────────────────────────────────┐
│                     微信消息流程                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  微信用户 ──▶ weixin-acp ──▶ Claude Code ──▶ 回复消息      │
│                                                             │
│  支持消息类型：                                              │
│  ✅ 文本消息                                                │
│  ✅ 图片消息                                                │
│  ✅ 语音消息（需 silk-wasm）                                │
│  ✅ 视频消息                                                │
│  ✅ 文件消息                                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 配置选项

### 系统提示词定制

创建 `~/.claude/weixin-prompt.txt` 自定义 Claude 的行为：

```
你是一个微信助手，帮助用户处理各种问题。
回复风格：简洁、友好、专业。
```

### 多账号支持

```bash
# 指定配置目录
WEIXIN_DATA_DIR=~/.weixin-work npx weixin-acp claude-code
```

## 与天龙岗位协同

| 天龙岗位 | 微信场景 | 使用方式 |
|----------|---------|---------|
| **01调研师** | 微信群调研 | `[@调研师] 分析这个微信群的用户画像` |
| **07记录师** | 微信文章 | `[@记录师] 整理这段微信对话为笔记` |
| **35-02社媒运营** | 微信公众号 | `[@社媒运营] 回复用户咨询` |
| **47-03 IM运营师** | 微信客服 | `[@IM运营师] 处理用户反馈` |

## 常见问题

### Q: 扫码登录失败？
确保使用的是**个人微信号**，不支持企业微信。

### Q: 消息收发延迟？
检查网络连接，weixin-acp 会自动重连。

### Q: 如何发送图片？
直接向微信发送图片，Claude Code 会自动处理。

## 相关技能

- [wechat-article-exporter](../wechat-article-exporter/) - 公众号文章导出
- [wechat-article-generator](../wechat-article-generator/) - 公众号文章生成
- [baoyu-post-to-wechat](../baoyu-post-to-wechat/) - 微信发布

## 参考链接

- [wong2/weixin-agent-sdk](https://github.com/wong2/weixin-agent-sdk) - 原始项目
- [ACP协议](https://github.com/wong2/weixin-agent-sdk/tree/main/packages/weixin-acp) - ACP文档