---
license: UNKNOWN
github_repo: wanikua/boluobobo-ai-court-tutorial
github_hash: 9d30b0e45894f305b4dd689c57299fe8f281bd68
last_updated: 2026-04-25
source_type: derived
triggers: ["discord bot", "Discord Bot 集成"]
---
# Discord Bot 集成

> 天龙引擎 V8.17 Discord 多平台交互能力

## 概述

基于 [boluobobo-ai-court-tutorial](https://github.com/wanikua/boluobobo-ai-court-tutorial) 的 Discord 集成方案，为天龙引擎提供多平台交互能力。

## 核心能力

| 能力 | 描述 |
|------|------|
| **多平台支持** | Discord / 飞书 / Slack / Telegram |
| **@mention 调用** | @Agent名称 触发对应岗位 |
| **会话隔离** | 每个 Agent 独立会话 |
| **移动端支持** | Discord 移动 App 原生支持 |
| **24h 在线** | 定时任务 + 心跳自检 |

## 天龙岗位映射

| Discord 角色 | 天龙岗位 | 职责 |
|-------------|---------|------|
| @分析师 | 00分析师 | 问题解构 |
| @调研师 | 01调研师 | 考古摸底 |
| @架构师 | 02架构师 | 划定蓝图 |
| @构建师 | 03构建师 | 代码施工 |
| @验证师 | 04验证师 | 极端找茬 |
| @安全师 | 05安全师 | 专项排雷 |
| @审查师 | 06审查师 | 终极审计 |
| @记录师 | 07记录师 | 文明传承 |
| @发布师 | 08发布师 | 功德圆满 |

## 安装配置

### 1. 创建 Discord Bot

```bash
# 1. 访问 https://discord.com/developers/applications
# 2. 点击 "New Application" 创建应用
# 3. 进入 Bot 页面，点击 "Add Bot"
# 4. 复制 Bot Token
# 5. 在 OAuth2 > URL Generator 中生成邀请链接
#    - Scopes: bot, applications.commands
#    - Permissions: Send Messages, Read Messages, Mention Everyone
```

### 2. 配置环境变量

```bash
# Discord Bot Token
export DISCORD_BOT_TOKEN="your-bot-token"

# Discord 频道 ID（可选）
export DISCORD_CHANNEL_ID="your-channel-id"
```

### 3. 配置 Gateway

```json
// ~/.openclaw/openclaw.json
{
  "bindings": [
    {
      "channel": "general",
      "accountId": "YOUR_DISCORD_SERVER_ID",
      "agentId": "00analyst"
    }
  ],
  "discord": {
    "token": "${DISCORD_BOT_TOKEN}",
    "prefix": "!"
  }
}
```

## 使用方式

### Discord 中调用

```
@分析师 帮我分析这个需求
@构建师 实现用户登录功能
@发布师 发布到 GitHub
```

### 自然语言触发

| 用户说 | 映射岗位 |
|--------|---------|
| "分析一下" / "分析需求" | 00分析师 |
| "调研代码" / "考古一下" | 01调研师 |
| "设计架构" / "架构方案" | 02架构师 |
| "写代码" / "实现功能" | 03构建师 |
| "测试一下" / "验证功能" | 04验证师 |
| "安全检查" / "安全审计" | 05安全师 |
| "代码审查" / "审查代码" | 06审查师 |
| "记录文档" / "写文档" | 07记录师 |
| "发布代码" / "提交 Git" | 08发布师 |

## 多平台对比

| 平台 | 支持 | 天龙引擎状态 |
|------|------|-------------|
| Discord | ✅ | 本次集成 |
| 飞书 | ✅ | 待配置 |
| Slack | ✅ | 待配置 |
| Telegram | ✅ | 待配置 |
| 微信 | ⚠️ | baoyu-post-to-wechat |

## 预期收益

| 指标 | 提升 |
|------|------|
| **移动端可用性** | **质的飞跃** |
| **24h 在线** | **无人值守** |
| **多人协作** | **团队可用** |
| **响应速度** | **实时通知** |

## 文件结构

```
skills/discord-bot/
├── SKILL.md              # 本文档
└── scripts/
    ├── discord-setup.sh  # 配置向导
    └── discord-gateway.js # Gateway 服务
```

## 相关链接

- [Discord Developer Portal](https://discord.com/developers/applications)
- [OpenClaw Discord 文档](https://github.com/openclaw/openclaw)
- [boluobobo-ai-court-tutorial](https://github.com/wanikua/boluobobo-ai-court-tutorial)