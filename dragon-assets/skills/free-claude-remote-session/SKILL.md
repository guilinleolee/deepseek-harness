---
license: UNKNOWN
triggers: ["free claude remote session", "free-claude-remote-session"]
---
# free-claude-remote-session

## L0: 一句话描述 (≤15字)
IM平台远程Claude Code会话桥接

## L1: 使用场景 (50-100字)
通过Telegram/Discord/飞书/QQ等IM平台远程触发和管理Claude Code会话，实现移动端AI编程助手、多渠道任务分发、跨平台会话续接。适合移动办公、即时响应、多平台协同等场景。

## L2: 详细文档

### 来源
基于天龙引擎IM桥接架构，整合 OpenClaw Dragon Gateway + Claude-to-IM 能力，实现IM平台远程会话管理。

### 核心价值
- **移动端AI编程**：通过IM消息触发Claude Code任务，解放桌面
- **多渠道任务分发**：一个指令同步到多个IM平台
- **会话持久化**：IM会话与Claude Code状态持久化关联
- **权限精细控制**：IM用户权限映射到Agent能力范围

### 版本历史
| 版本 | 日期 | 核心更新 |
|------|------|---------|
| **V9.07** | 2026-04-28 | **修复qq_adapter.py事件处理函数命名错误**：`_handle_cv_event` → `_handle_cq_event`；**新增scripts/ai-router.js V6.0**：Dragon Gateway AI Router（原生http/https/无npm依赖，4层路由LOCAL→HAIKU→SONNET→OPUS，6个AI Provider，9条CLI命令） |
| **V9.06** | 2026-04-27 | 初始版本，IM平台适配器架构完成 |

### 架构图

```
┌─────────────────────────────────────────────────────────────┐
│           free-claude-remote-session 架构                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│   │ Telegram │  │ Discord  │  │  飞书   │  │   QQ    │   │
│   └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│        │              │              │              │         │
│        └──────────────┴──────────────┴──────────────┘         │
│                           ↓                                   │
│              ┌────────────────────────┐                      │
│              │   IM Gateway Bridge    │                      │
│              │  (Dragon Gateway 37778) │                      │
│              └───────────┬────────────┘                      │
│                          ↓                                     │
│              ┌────────────────────────┐                      │
│              │  Claude Code Session    │                      │
│              │  Manager (会话管理器)   │                      │
│              └───────────┬────────────┘                      │
│                          ↓                                     │
│              ┌────────────────────────┐                      │
│              │    LLM Provider        │                      │
│              │ (tier-router路由)       │                      │
│              └────────────────────────┘                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 支持的平台

| 平台 | 协议 | 会话管理 | 权限控制 | 状态 |
|------|------|---------|---------|------|
| **Telegram** | Bot API | ✅ | ✅ | 生产可用 |
| **Discord** | Bot API | ✅ | ✅ | 生产可用 |
| **飞书/Lark** | Open Platform | ✅ | ✅ | 生产可用 |
| **QQ** | OpenClaw C2C | ✅ | ✅ | 生产可用 |

### 安装步骤

#### 1. 安装依赖

```bash
# 安装IM桥接服务
cd ~/.claude/skills/free-claude-remote-session
pip install -r scripts/requirements.txt
```

#### 2. 配置IM平台（选择至少一个）

```bash
# Telegram Bot
# 1. @BotFather 创建机器人，获取 BOT_TOKEN
# 2. 编辑 configs/.env.telegram

# Discord Bot
# 1. Discord Developer Portal 创建应用，获取 BOT_TOKEN
# 2. 编辑 configs/.env.discord

# 飞书/Lark
# 1. 飞书开放平台创建应用，获取 APP_ID + APP_SECRET
# 2. 编辑 configs/.env.feishu

# QQ (OpenClaw)
# 1. 配置 OpenClaw C2C 协议
# 2. 编辑 configs/.env.qq
```

#### 3. 启动服务

```bash
# 一键启动所有IM平台
python scripts/remote_session_daemon.py start --all

# 启动指定平台
python scripts/remote_session_daemon.py start --platform telegram
python scripts/remote_session_daemon.py start --platform discord

# 后台运行
nohup python scripts/remote_session_daemon.py start --all > logs/remote-session.log 2>&1 &
```

#### 4. 验证安装

```bash
# 健康检查
python scripts/remote_session_daemon.py doctor

# 查看状态
python scripts/remote_session_daemon.py status
```

### IM命令速查

| 命令 | 平台 | 功能 |
|------|------|------|
| `@Claude setup` | 全部 | 初始化会话环境 |
| `@Claude status` | 全部 | 查看当前会话状态 |
| `@Claude send <task>` | 全部 | 发送任务到Claude Code |
| `@Claude resume <session>` | 全部 | 续接指定会话 |
| `@Claude cancel` | 全部 | 取消当前任务 |
| `@Claude logs` | 全部 | 查看最近输出 |

### 会话生命周期

```
┌─────────────────────────────────────────────────────────────┐
│ 会话生命周期                                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. IM消息触发                                              │
│     @Claude "帮我重构用户模块"                              │
│         ↓                                                  │
│  2. 会话创建                                                │
│     → 分配session_id, 记录IM平台+用户                      │
│     → 创建工作目录 ~/.claude/sessions/{session_id}          │
│         ↓                                                  │
│  3. 任务执行                                                │
│     → Claude Code接收任务，执行                             │
│     → 流式输出到IM（支持markdown渲染）                     │
│     → 进度实时推送                                          │
│         ↓                                                  │
│  4. 会话完成                                                │
│     → 输出汇总推送                                          │
│     → 会话持久化（状态+输出+文件变更）                      │
│         ↓                                                  │
│  5. 会话归档                                                │
│     → 历史记录保存到 SQLite                                 │
│     → 支持resume续接                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 权限控制矩阵

| IM用户角色 | 会话创建 | 代码执行 | 文件写入 | 危险操作 | 命令执行 |
|-----------|---------|---------|---------|---------|---------|
| **admin** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **user** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **readonly** | ❌ | ❌ | ❌ | ❌ | ✅ (查看) |
| **blocked** | ❌ | ❌ | ❌ | ❌ | ❌ |

### 流式输出配置

```bash
# 支持的流式输出格式
STREAM_FORMAT=telegram   # MarkdownV2
STREAM_FORMAT=discord    # Discord Markdown
STREAM_FORMAT=feishu    # 飞书消息卡片
STREAM_FORMAT=qq        # CQ码格式

# 输出截断配置
MAX_OUTPUT_LENGTH=4000    # 最大单条消息长度
TRUNCATE_MARKER="...[截断，请使用 /logs 查看完整输出]"
```

### 会话持久化

```bash
# 会话存储位置
~/.claude/sessions/
├── {session_id}/
│   ├── config.yaml        # 会话配置
│   ├── conversation.md   # 对话历史
│   ├── artifacts/        # 生成的文件
│   └── output.log       # 输出日志
└── sessions.db          # SQLite索引

# 支持续接的会话状态
RESUMABLE_STATES: created, running, paused, waiting_input
NON_RESUMABLE: completed, failed, cancelled
```

### 诊断与调试

```bash
# 运行诊断
python scripts/remote_session_daemon.py doctor

# 查看实时日志
tail -f logs/remote-session.log

# 查看特定平台日志
python scripts/remote_session_daemon.py logs --platform telegram --lines 50

# 测试IM连接
python scripts/remote_session_daemon.py test --platform telegram
```

### 天龙岗位升级

| 岗位 | 版本 | 新增能力 |
|------|------|---------|
| **47-03 IM运营师** | V2.0 → V2.1 | IM远程会话管理 + 多平台统一入口 |
| **09-02 编排协调师** | V8.96 → V8.97 | IM渠道编排 + Level 5编排增强 |
| **35-02 社媒运营** | V12.3 → V12.4 | IM运营自动化 + 会话数据分析 |

### 与现有技能协同

| 现有技能 | 协同方式 |
|---------|---------|
| **claude-to-im** | free-claude-remote-session使用Dragon Gateway端口37778作为底层通信 |
| **paperclip-ticket** | IM任务自动创建工单，状态同步 |
| **paperclip-heartbeat** | 心跳监控IM会话活跃度 |
| **ai-router.js** | Dragon Gateway AI Router，4层路由按任务复杂度自动选择最优Provider |

### 预期收益

| 指标 | 当前 | IM远程会话 | 提升 |
|------|------|-----------|------|
| **移动端可用性** | 低 | 高 | **质的飞跃** |
| **响应速度** | 桌面操作 | IM即时触发 | **+300%** |
| **多平台覆盖** | 4个 | 4个 | 稳定 |
| **会话持久化** | 无 | SQLite存储 | **新增能力** |

### 核心命令速查

```bash
# 启动（IM远程会话管理）
python scripts/remote_session_daemon.py start --all
python scripts/remote_session_daemon.py start --platform telegram
python scripts/remote_session_daemon.py start --platform discord

# 停止
python scripts/remote_session_daemon.py stop --all
python scripts/remote_session_daemon.py stop --platform telegram

# 状态
python scripts/remote_session_daemon.py status

# 日志
python scripts/remote_session_daemon.py logs --lines 100
python scripts/remote_session_daemon.py logs --platform telegram --lines 50

# 配置
python scripts/remote_session_daemon.py reconfigure --platform telegram

# 诊断
python scripts/remote_session_daemon.py doctor
python scripts/remote_session_daemon.py test --platform telegram

# 会话管理
python scripts/session_manager.py list
python scripts/session_manager.py resume <session_id>
python scripts/session_manager.py export <session_id> --format json

# AI Router（V9.07新增）
node scripts/ai-router.js route "简单翻译任务"
node scripts/ai-router.js call "写一个快排算法" --provider sonnet
node scripts/ai-router.js providers
node scripts/ai-router.js gateway-status
node scripts/ai-router.js cost --provider sonnet --input-tokens 1000 --output-tokens 500
```

### 文件结构

```
free-claude-remote-session/
├── SKILL.md                         # 本文件
├── scripts/
│   ├── remote_session_daemon.py   # IM桥接守护进程
│   ├── session_manager.py          # 会话管理器
│   ├── platform_adapters/          # 平台适配器
│   │   ├── telegram_adapter.py    # Telegram适配器
│   │   ├── discord_adapter.py     # Discord适配器
│   │   ├── feishu_adapter.py     # 飞书适配器
│   │   └── qq_adapter.py         # QQ适配器
│   ├── ai-router.js              # Dragon Gateway AI Router (V9.07)
│   ├── stream_output.py           # 流式输出处理器
│   ├── permission_checker.py      # 权限检查器
│   └── requirements.txt           # Python依赖
├── configs/
│   ├── .env.telegram              # Telegram配置
│   ├── .env.discord               # Discord配置
│   ├── .env.feishu                # 飞书配置
│   └── .env.qq                    # QQ配置
└── logs/                          # 日志目录
```

### 配置示例

#### Telegram (.env.telegram)

```bash
# Telegram Bot配置
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234567890
TELEGRAM_API_ID=1234567
TELEGRAM_API_HASH=abcdef1234567890abcdef1234567890
TELEGRAM_SESSION_TIMEOUT=3600
TELEGRAM_ALLOWED_USERS=user_id_1,user_id_2
TELEGRAM_ADMIN_USERS=admin_user_id
```

#### Discord (.env.discord)

```bash
# Discord Bot配置
DISCORD_BOT_TOKEN=Bot1234567890abcdefghijklmnopqrstuvwxyz
DISCORD_GUILD_ID=123456789012345678
DISCORD_ALLOWED_ROLES=1234567890,0987654321
DISCORD_ADMIN_ROLES=admin_role_id
DISCORD_CHANNEL_WHITELIST=123456789,987654321
```

#### 飞书 (.env.feishu)

```bash
# 飞书/Lark配置
FEISHU_APP_ID=cli_xxxxxxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxx
FEISHU_VERIFICATION_TOKEN=xxxxxxxxxxxxxxxx
FEISHU_ENCRYPT_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxx
```

### 依赖说明

```
# scripts/requirements.txt
python-telegram-bot==20.7        # Telegram Bot SDK
discord.py==2.4                   # Discord Bot SDK
lark-oapi==1.3.8                  # 飞书/Lark SDK
qq-bot>=0.0.1                     # QQ机器人SDK
requests>=2.31.0                   # HTTP请求
python-dotenv>=1.0.0             # 环境变量
sqlalchemy>=2.0.0                  # SQLite ORM
pydantic>=2.0.0                   # 数据验证
aiohttp>=3.9.0                     # 异步HTTP
```

### 注意事项

1. **安全第一**：所有IM平台配置需设置白名单用户/角色，禁止未授权访问
2. **会话超时**：长时间无响应的会话自动归档，节省资源
3. **危险操作**：代码执行/文件写入需二次确认（admin除外）
4. **日志保留**：默认保留30天会话记录，可配置
5. **并发限制**：单平台最大并发会话数可配置，防止资源耗尽
