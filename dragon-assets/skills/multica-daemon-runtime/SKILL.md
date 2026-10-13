---
license: UNKNOWN
github_repo: multica-ai/multica
github_hash: 5eab1dbbe1826616ec57bee57cf939a64b341125
last_updated: 2026-04-25
source_type: derived
triggers: ["multica daemon runtime", "multica-daemon-runtime"]
---
# multica-daemon-runtime

> Multica 本地 Agent Daemon 运行时 — 本地机器上的 Agent 自动检测、任务认领和执行管理

## L0: 一句话描述
本地 Agent Daemon 自动检测 Claude Code/Codex，自动认领任务，实时流式返回执行结果

## L1: 使用场景

- 需要在本地机器上运行 Agent 任务
- 需要跨 workspace 自动管理多个 Agent
- 需要实时追踪 Agent 执行进度
- 需要厂商中立的 Agent 执行层

## L2: 详细文档

### Daemon 核心架构

```
┌─────────────────────────────────────────────────────────────┐
│                 Multica Daemon 架构                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐                                          │
│  │   Server     │  ←──── WebSocket ──── 实时推送            │
│  │  (Go Backend)│                                          │
│  └──────┬───────┘                                          │
│         │                                                    │
│  ┌──────▼───────┐     ┌─────────────────┐                │
│  │  Task Queue  │────▶│   Daemon        │                │
│  │  (Polling)   │     │  (Local Host)   │                │
│  └──────────────┘     └────┬────┬────┬───┘                │
│                              │    │    │                    │
│                    ┌─────────┘    │    └─────────┐         │
│                    ▼               ▼                ▼         │
│              ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│              │ Claude   │  │  Codex   │  │ OpenClaw │    │
│              │  Code   │  │          │  │          │    │
│              └──────────┘  └──────────┘  └──────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### CLI 命令

```bash
# Daemon 管理
multica daemon start              # 启动本地 Agent 运行时
multica daemon stop              # 停止 Daemon
multica daemon status            # 查看 Daemon 状态
multica daemon logs              # 查看 Daemon 日志

# 认证
multica login                    # 浏览器 OAuth 登录
multica login --token           # Token 登录（无头环境）
multica auth status             # 检查认证状态

# Workspace 管理
multica workspace list          # 列出所有 workspace
multica workspace watch         # 监视 workspace
multica workspace unwatch       # 取消监视
```

### 配置参数

| 参数 | Flag | 环境变量 | 默认值 |
|------|------|----------|--------|
| 轮询间隔 | `--poll-interval` | `MULTICA_DAEMON_POLL_INTERVAL` | `3s` |
| 心跳间隔 | `--heartbeat-interval` | `MULTICA_DAEMON_HEARTBEAT_INTERVAL` | `15s` |
| Agent 超时 | `--agent-timeout` | `MULTICA_AGENT_TIMEOUT` | `2h` |
| 最大并发 | `--max-concurrent-tasks` | `MULTICA_DAEMON_MAX_CONCURRENT_TASKS` | `20` |
| Workspace 根目录 | — | `MULTICA_WORKSPACES_ROOT` | `~/multica_workspaces` |

### Daemon 工作流程

```
1. 启动
   ├── 检测已安装的 Agent CLIs (claude/codex/openclaw/opencode)
   └── 为每个 workspace 注册 runtimes

2. 轮询
   ├── 按 poll-interval (默认 3s) 轮询服务器
   └── 发现新任务 → claim

3. 执行
   ├── 创建隔离工作目录
   ├── spawn Agent CLI
   └── 流式返回结果 (WebSocket)

4. 心跳
   └── 按 heartbeat-interval (默认 15s) 发送心跳

5. 关闭
   └── 注销所有 runtimes
```

### 支持的 Agent CLI

| CLI | 命令 | 提供商 | 厂商中立 |
|-----|------|--------|---------|
| Claude Code | `claude` | Anthropic | ✅ |
| Codex | `codex` | OpenAI | ✅ |
| OpenClaw | `openclaw` | OpenClaw | ✅ |
| OpenCode | `opencode` | OpenCode | ✅ |

### 天龙岗位集成

#### 03 构建师 (V8.91)

```yaml
本地构建流程:
  1. 启动 Daemon → multica daemon start
  2. 创建任务 → multica issue create
  3. 自动认领 → Daemon 轮询发现
  4. 隔离执行 → 独立工作目录
  5. 实时监控 → WebSocket 流式输出
  6. 结果聚合 → 任务完成状态
```

#### 09-02 编排协调师 (V8.91)

```yaml
多 Agent 编排:
  1. 并行启动多个 Daemon (不同 workspace)
  2. 任务分发 → 按 Agent 专长分配
  3. 实时协调 → WebSocket 监控所有 Agent
  4. 结果汇聚 → 合并多 Agent 输出
  5. 质量验收 → 失败自动重试
```

### 与现有系统对比

| 维度 | 天龙现有方案 | Multica Daemon | 提升 |
|------|------------|----------------|------|
| Agent 执行 | 手动启动 | 自动检测 + 自动认领 | **质的飞跃** |
| 任务轮询 | 无 | 3s 间隔自动轮询 | **新增能力** |
| 厂商支持 | Claude Code | Claude/Codex/OpenClaw/OpenCode | **+300%** |
| 并发控制 | 无 | max-concurrent-tasks 可配置 | **新增能力** |

### 自托管部署

```bash
# Docker Compose 一键部署
git clone https://github.com/multica-ai/multica.git
cd multica
cp .env.example .env
# 编辑 .env - 至少修改 JWT_SECRET
docker compose -f docker-compose.selfhost.yml up -d

# 必需环境变量
DATABASE_URL=postgresql://...
JWT_SECRET=your-secret-key
FRONTEND_ORIGIN=https://your-domain.com
RESEND_API_KEY=your-resend-key
```

---

*来源: [multica-ai/multica](https://github.com/multica-ai/multica) - CLI_AND_DAEMON.md*
