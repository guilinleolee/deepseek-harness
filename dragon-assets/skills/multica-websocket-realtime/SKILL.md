---
license: UNKNOWN
github_repo: multica-ai/multica
github_hash: 5eab1dbbe1826616ec57bee57cf939a64b341125
last_updated: 2026-04-25
source_type: derived
triggers: ["multica websocket realtime", "multica-websocket-realtime"]
---
# multica-websocket-realtime

> Multica WebSocket 实时通信 — Agent 执行状态流式推送与客户端订阅

## L0: 一句话描述
WebSocket 双向通信：Agent 执行结果流式推送 + 客户端命令下发 + 心跳保活

## L1: 使用场景

- 需要实时追踪 Agent 任务执行进度
- 需要在浏览器/Web 端展示 Agent 工作状态
- 需要客户端实时下发控制命令（暂停/取消/优先级调整）
- 需要多 Workspace 并行监控

## L2: 详细文档

### WebSocket 通信架构

```
┌─────────────────────────────────────────────────────────────┐
│              Multica WebSocket 双向通信架构                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐           ┌──────────────────┐          │
│  │   Browser    │◄─────────►│   WebSocket     │          │
│  │   (Client)   │  ws://    │   Server        │          │
│  └──────────────┘           └────────┬─────────┘          │
│                                      │                      │
│                           ┌──────────▼──────────┐          │
│                           │   Message Broker    │          │
│                           │   (Pub/Sub)         │          │
│                           └──────────┬──────────┘          │
│                                      │                      │
│                    ┌─────────────────┼─────────────────┐ │
│                    ▼                 ▼                 ▼ │
│              ┌──────────┐    ┌──────────┐    ┌──────────┐│
│              │  Daemon  │    │  Daemon  │    │  Daemon  ││
│              │  (WS-1)  │    │  (WS-2)  │    │  (WS-N)  ││
│              └──────────┘    └──────────┘    └──────────┘│
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 消息类型

| 方向 | 类型 | 说明 | Payload 示例 |
|------|------|------|-------------|
| **Server→Client** | `task.created` | 新任务创建 | `{task_id, title, priority}` |
| **Server→Client** | `task.progress` | 任务进度 | `{task_id, progress, message}` |
| **Server→Client** | `task.completed` | 任务完成 | `{task_id, result, duration}` |
| **Server→Client** | `task.failed` | 任务失败 | `{task_id, error, stack}` |
| **Server→Client** | `agent.heartbeat` | Agent 心跳 | `{agent_id, status, load}` |
| **Server→Client** | `agent.status` | Agent 状态 | `{agent_id, task_id, output}` |
| **Client→Server** | `command.pause` | 暂停任务 | `{task_id}` |
| **Client→Server** | `command.cancel` | 取消任务 | `{task_id, reason}` |
| **Client→Server** | `command.priority` | 调整优先级 | `{task_id, priority}` |
| **Client→Server** | `subscribe.workspace` | 订阅 Workspace | `{workspace_id}` |

### WebSocket 连接管理

```typescript
// 客户端连接示例
const ws = new WebSocket('wss://multica.example.com/ws?token=Bearer xxx');

ws.onopen = () => {
  // 订阅 Workspace 实时更新
  ws.send(JSON.stringify({
    type: 'subscribe.workspace',
    payload: { workspace_id: 'ws-001' }
  }));
};

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  switch (msg.type) {
    case 'task.progress':
      updateProgressBar(msg.payload);
      break;
    case 'task.completed':
      showNotification(msg.payload);
      break;
    case 'agent.heartbeat':
      updateAgentStatus(msg.payload);
      break;
  }
};

// 发送控制命令
function pauseTask(taskId: string) {
  ws.send(JSON.stringify({
    type: 'command.pause',
    payload: { task_id: taskId }
  }));
}
```

### 心跳保活机制

```
┌─────────────────────────────────────────────────────────────┐
│                    心跳保活机制                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Client ──── ping(5s) ────► Server                       │
│  Client ◄──── pong ───────── Server                        │
│                                                             │
│  超时断开: 3 次 ping 无响应 → 自动重连                       │
│  重连策略: 指数退避 (1s → 2s → 4s → 8s → 16s)            │
│  重连上限: 10 次后放弃，提示用户手动重连                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 断线重连处理

```typescript
class MulticaWebSocket {
  private ws: WebSocket;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private reconnectDelay = 1000;

  onClose = () => {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      setTimeout(() => {
        this.reconnectAttempts++;
        this.reconnectDelay *= 2; // 指数退避
        this.connect();
      }, this.reconnectDelay);
    }
  };

  onMessage = (event: MessageEvent) => {
    const msg = JSON.parse(event.data);
    if (msg.type === 'sync.state') {
      // 重连后同步最新状态
      this.syncState(msg.payload);
    }
  };
}
```

### 天龙岗位集成

#### 09-02 编排协调师 (V8.91)

```yaml
实时监控流程:
  1. WebSocket 连接 → 订阅所有活跃 Workspace
  2. 任务进度流式显示 → task.progress 实时推送
  3. Agent 心跳监控 → agent.heartbeat 存活检测
  4. 控制命令下发 → command.pause/cancel/priority
  5. 断线自动重连 → 重连后 sync.state 同步
```

#### 04 验证师 (V8.91)

```yaml
验证监控:
  1. WebSocket 接收测试任务进度
  2. task.failed 时自动创建 Bug Issue
  3. 实时显示测试覆盖率百分比
  4. 验证完成后 task.completed 触发后续流程
```

### 与现有系统对比

| 维度 | 天龙现有方案 | Multica WebSocket | 提升 |
|------|------------|-------------------|------|
| 实时推送 | 无 | WebSocket 流式推送 | **新增能力** |
| 客户端控制 | 无 | pause/cancel/priority命令 | **新增能力** |
| 心跳监控 | 无 | 15s间隔自动心跳 | **新增能力** |
| 断线重连 | 无 | 指数退避自动重连 | **新增能力** |

### 使用示例

```bash
# 启动带 WebSocket 的 Daemon
multica daemon start --ws-port 8080

# WebSocket 端点
wss://localhost:8080/ws?token=xxx

# 订阅 Workspace
{"type": "subscribe.workspace", "payload": {"workspace_id": "ws-001"}}

# 监控所有 Agent 心跳
{"type": "subscribe.agents", "payload": {}}
```

---

*来源: [multica-ai/multica](https://github.com/multica-ai/multica) - WebSocket Server*
