---
license: UNKNOWN
github_repo: multica-ai/multica
github_hash: 5eab1dbbe1826616ec57bee57cf939a64b341125
last_updated: 2026-04-25
source_type: derived
triggers: ["multica task lifecycle", "multica-task-lifecycle"]
---
# multica-task-lifecycle

> Multica 任务生命周期管理 — 完整的 Agent 任务从创建到完成的闭环管理

## L0: 一句话描述
Agent 任务生命周期管理：`enqueue → claim → start → complete/fail` 完整闭环

## L1: 使用场景

- 需要管理复杂多步骤任务的执行
- 需要追踪 Agent 任务的实时状态
- 需要为不同 Agent 分配和管理任务队列
- 需要建立任务执行的可追溯性

## L2: 详细文档

### 任务状态机

```
┌─────────────────────────────────────────────────────────────┐
│              Multica 任务生命周期状态机                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  enqueue  →  claim  →  start  →  complete               │
│     │          │          │          │                     │
│     │          │          │          ↓                     │
│     │          │          │        fail  ←── 失败         │
│     │          │          │                               │
│     │          │          └──  progress (实时进度) ─┘     │
│     │          │                                             │
│     └──────────┴─── abandoned (超时/放弃)                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 核心状态说明

| 状态 | 说明 | 触发条件 |
|------|------|---------|
| `enqueued` | 已入队，等待认领 | `multica issue assign <agent>` |
| `claimed` | 已被 Agent 认领 | Daemon 轮询发现任务 |
| `in_progress` | 执行中 | Agent 开始工作 |
| `complete` | 已完成 | 任务成功结束 |
| `failed` | 失败 | 执行出错 |
| `abandoned` | 放弃 | 超时或 Agent 离线 |

### CLI 命令

```bash
# 创建 Issue
multica issue create --title "实现用户认证" --description "..."

# 分配给 Agent
multica issue assign <issue_id> --agent <agent_id>

# 查看状态
multica issue status <issue_id>

# 查看执行历史
multica issue runs <issue_id>

# 查看执行详情
multica issue run-messages <issue_id> --run-id <run_id>

# 添加评论
multica issue comment <issue_id> --message "进展更新"
```

### 状态变更触发器

| 触发器 | 条件 | 自动动作 |
|--------|------|---------|
| 任务创建 | `issue create` | 状态 → `enqueued` |
| Daemon 认领 | `daemon poll` | 状态 → `claimed` → `in_progress` |
| 执行成功 | `task complete` | 状态 → `complete` |
| 执行失败 | `task fail` | 状态 → `failed` + 错误日志 |
| 超时 | `timeout` | 状态 → `abandoned` |
| Agent 心跳缺失 | `heartbeat miss` | 状态 → `abandoned` |

### 天龙岗位集成

#### 09-02 编排协调师 (V8.91)

```yaml
任务编排流程:
  1. 问题分析 → 识别任务类型
  2. 任务拆分 → 分解为子任务
  3. 任务入队 → multica issue create
  4. 分配执行 → multica issue assign
  5. 进度追踪 → WebSocket 实时监控
  6. 结果聚合 → 合并子任务输出
  7. 质量验收 → 04验证师验证
```

#### 04 验证师 (V8.91)

```yaml
验证流程:
  1. 验证任务 → 创建验证 Issue
  2. 分配验证 → assign 给 验证Agent
  3. 执行验证 → 并行验证多个测试用例
  4. 结果记录 → 自动生成验证报告
  5. 问题追踪 → failed → 自动创建 Bug Issue
```

### 与现有系统协同

| 天龙组件 | 协同方式 | 效果 |
|---------|---------|------|
| TodoWrite | 任务拆分 | 前置分析 |
| lessons.md | 经验沉淀 | 任务模式积累 |
| WebSocket 实时 | 进度推送 | 实时可见 |
| Issue 追踪 | 持久化 | 历史可查 |

### 最佳实践

1. **任务原子化**：每个 Issue 尽量单一职责
2. **描述清晰**：使用 `context → task → definition` 格式
3. **进度透明**：定期 `issue comment` 更新状态
4. **失败追溯**：failed 状态必须记录根因
5. **超时保护**：设置合理的 `agent_timeout`

---

*来源: [multica-ai/multica](https://github.com/multica-ai/multica) - CLI_AND_DAEMON.md*
