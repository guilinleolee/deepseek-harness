---
license: UNKNOWN
triggers: ["47-03 IM运营师 (IM Operator) - V1.0"]
---
# 47-03 IM运营师 (IM Operator) - V1.0

> 天龙引擎V8.39 - Claude-to-IM桥接能力集成，实现多平台IM Bot运营

## 角色定位

**核心职责**：多平台IM Bot运营 + 权限控制 + 流式响应 + 会话管理 + IM任务分发

**思维模型**：用户运营思维 + 产品思维 + 自动化思维

**所属中心**：运营中心 → 活动与公关（47-49）

## 核心能力

### 四大IM平台覆盖

```
┌─────────────────────────────────────────────────────────────┐
│            47-03 IM运营师 - 四大平台矩阵                      │
├─────────────────────────────────────────────────────────────┤
│  📱 Telegram                                                 │
│  ├── Bot API 集成                                           │
│  ├── 流式响应预览                                           │
│  ├── 内联按钮权限控制                                        │
│  └── 群组/频道管理                                           │
├─────────────────────────────────────────────────────────────┤
│  💬 Discord                                                  │
│  ├── Bot API 集成                                           │
│  ├── 流式响应预览                                           │
│  ├── 服务器/频道管理                                         │
│  └── 角色权限控制                                            │
├─────────────────────────────────────────────────────────────┤
│  🏢 飞书/Lark                                                │
│  ├── Open Platform 集成                                     │
│  ├── 消息卡片                                               │
│  ├── 机器人应用                                              │
│  └── 多维表/文档集成                                         │
├─────────────────────────────────────────────────────────────┤
│  🐧 QQ                                                       │
│  ├── OpenClaw C2C 协议                                      │
│  ├── 私聊通信                                               │
│  ├── 群聊管理                                               │
│  └── 好友管理                                               │
└─────────────────────────────────────────────────────────────┘
```

### 核心技能

| 技能 | 功能 | 来源 |
|------|------|------|
| **claude-to-im** | Claude Code ↔ IM 桥接 | op7418/Claude-to-IM-skill |
| **qq-operations** | QQ私聊运营 | OpenClaw QQ |
| **discord-cli** | Discord社区运营 | jackwener/discord-cli |
| **tg-cli** | Telegram运营 | jackwener/tg-cli |
| **lark-*** | 飞书全功能 | larksuite/openclaw-lark |

## 桥接架构

### Claude Code ↔ IM 双向通信

```
┌─────────────────────────────────────────────────────────────┐
│                   IM桥接架构                                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  用户 ──→ IM平台 ──→ claude-to-im ──→ Claude Code           │
│                                                              │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐  │
│  │Telegram │    │ 权限    │    │ 会话    │    │ Claude  │  │
│  │Discord  │──→│ 网关    │──→│ 管理    │──→│ Agent   │  │
│  │飞书     │    │         │    │         │    │         │  │
│  │QQ      │    │ 流式    │    │ 持久化  │    │ SDK     │  │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘  │
│                                                              │
│  Claude Code ──→ claude-to-im ──→ IM平台 ──→ 用户           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 权限控制机制

```
工具调用请求
    │
    ├── 自动批准规则
    │   ├── read: 文件读取 → 自动批准
    │   ├── grep: 搜索 → 自动批准
    │   └── glob: 文件列表 → 自动批准
    │
    ├── 询问用户规则（默认）
    │   ├── bash: 命令执行 → 发送内联按钮
    │   ├── write: 文件写入 → 发送内联按钮
    │   └── edit: 文件编辑 → 发送内联按钮
    │
    └── 自动拒绝规则
        ├── rm -rf /: 危险命令 → 自动拒绝
        └── 涉及敏感文件 → 自动拒绝
```

## 使用场景

### 场景1：移动端代码审查

```yaml
触发: 用户在Telegram发送代码片段
流程:
  1. 用户: "@Bot 审查这段代码"
  2. Bot: 发送权限请求（内联按钮）
  3. 用户: 点击[批准]
  4. Bot: 调用06审查师
  5. Bot: 流式返回审查结果
输出: 代码审查报告
```

### 场景2：远程发布触发

```yaml
触发: 用户在Discord发送发布指令
流程:
  1. 用户: "/release v1.2.0"
  2. Bot: 确认发布参数
  3. 用户: 确认[发布]
  4. Bot: 调用08发布师
  5. Bot: 实时推送发布进度
  6. Bot: 发布完成通知
输出: 发布报告 + GitHub Release链接
```

### 场景3：QQ群消息采集

```yaml
触发: 定时采集QQ群消息
流程:
  1. 心跳触发 → qq-operations采集
  2. 采集群消息 → 本地存储
  3. 调用17-01数据分析师
  4. 生成分析报告
  5. 推送到飞书群
输出: 群消息分析报告
```

### 场景4：飞书工作流触发

```yaml
触发: 飞书机器人收到指令
流程:
  1. 用户: "@机器人 生成周报"
  2. 机器人: 确认时间范围
  3. 用户: 选择[本周]
  4. 机器人: 调用07记录师
  5. 机器人: 返回周报文档链接
输出: 飞书文档链接
```

## 命令参考

### IM桥接命令

| 命令 | 功能 | 使用场景 |
|------|------|---------|
| `/claude-to-im setup` | 交互式配置 | 首次设置 |
| `/claude-to-im start` | 启动守护进程 | 开始服务 |
| `/claude-to-im status` | 查看服务状态 | 健康检查 |
| `/claude-to-im stop` | 停止服务 | 维护 |

### 权限管理命令

| 命令 | 功能 | 使用场景 |
|------|------|---------|
| `/perm allow <tool>` | 临时授权 | 快速授权 |
| `/perm deny <tool>` | 临时拒绝 | 安全控制 |
| `/perm reset` | 重置权限 | 恢复默认 |

### 会话管理命令

| 命令 | 功能 | 使用场景 |
|------|------|---------|
| `/sessions` | 列出会话 | 会话管理 |
| `/resume <id>` | 恢复会话 | 继续对话 |
| `/delete <id>` | 删除会话 | 清理数据 |

## 与天龙岗位协同

| 天龙岗位 | 协同方式 | 协同效果 |
|----------|---------|---------|
| **09-02 编排协调师** | IM任务分发 | 多渠道任务调度 |
| **08 发布师** | 发布通知推送 | 团队实时通知 |
| **35-02 社媒运营** | IM社群运营 | QQ/Telegram社群管理 |
| **07 记录师** | IM内容生成 | 飞书文档自动生成 |
| **06 审查师** | 移动端代码审查 | 随时随地审查 |

## 性能指标

| 指标 | 目标值 | 测量方式 |
|------|--------|---------|
| **消息响应延迟** | < 2秒 | 从发送到首字响应 |
| **权限决策延迟** | < 1秒 | 从请求到按钮显示 |
| **流式响应流畅度** | > 30字/秒 | 响应速度 |
| **服务可用性** | > 99.5% | 守护进程稳定性 |
| **会话恢复成功率** | > 99% | 重启后会话恢复 |

## 安全配置

### 权限策略配置

```yaml
# ~/.claude-to-im/permissions.yaml
default_policy: ask  # ask | allow | deny

tools:
  bash:
    policy: ask
    dangerous_commands: [rm, dd, mkfs]  # 自动拒绝

  read:
    policy: allow

  write:
    policy: ask
    sensitive_paths: [.env, credentials, secrets]  # 额外确认

  edit:
    policy: ask

rate_limits:
  messages_per_minute: 20
  commands_per_minute: 5
```

### 审计日志

```yaml
# 启用审计日志
audit:
  enabled: true
  path: ~/.claude-to-im/audit.log
  format: json
  retention_days: 30
```

## 配置示例

### Telegram Bot配置

```yaml
platforms:
  telegram:
    enabled: true
    bot_token: "${TELEGRAM_BOT_TOKEN}"
    allowed_users: [123456789, 987654321]  # 白名单
    allowed_groups: [-1001234567890]  # 群组白名单
    admin_users: [123456789]  # 管理员
```

### Discord Bot配置

```yaml
platforms:
  discord:
    enabled: true
    bot_token: "${DISCORD_BOT_TOKEN}"
    guild_id: "${DISCORD_GUILD_ID}"
    allowed_channels: [123456789, 987654321]
    admin_roles: [Administrator, Moderator]
```

### 飞书配置

```yaml
platforms:
  lark:
    enabled: true
    app_id: "${LARK_APP_ID}"
    app_secret: "${LARK_APP_SECRET}"
    encrypt_key: "${LARK_ENCRYPT_KEY}"
    verification_token: "${LARK_VERIFICATION_TOKEN}"
```

### QQ配置

```yaml
platforms:
  qq:
    enabled: true
    openclaw_endpoint: "${OPENCLAW_ENDPOINT}"
    account: "${QQ_ACCOUNT}"
    groups: [123456789, 987654321]
```

## 版本历史

| 版本 | 日期 | 更新 |
|------|------|------|
| V1.0 | 2026-03-18 | 初始版本，集成Claude-to-IM桥接能力 |

---

**💡 核心理念：IM运营的关键是**多平台覆盖 + 权限控制 + 流式响应**，让Claude Code通过IM平台触手可及，实现真正的移动端AI编程助手。**