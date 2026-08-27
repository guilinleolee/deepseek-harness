---
license: UNKNOWN
name: paperclip-heartbeat
description: 心跳调度器，支持24/7自主运行
github_repo: paperclipai/paperclip
github_hash: 70679a33216bae9247b1b6bddc5fcaad1c04e829
last_updated: 2026-04-25
source_type: derived
version: 1.0.0
author: 天龙引擎团队
created: 2026-03-15
category: orchestration
triggers: ["paperclip heartbeat", "Paperclip心跳调度器"]
---

# Paperclip心跳调度器

## 概述

基于 [paperclipai/paperclip](https://github.com/paperclipai/paperclip) 的心跳机制，为天龙引擎提供24/7自主运行能力。

## 核心能力

| 能力 | 说明 |
|------|------|
| **Cron调度** | 支持标准Cron表达式 |
| **事件触发** | 任务分配、@提及、回调 |
| **委托机制** | 上下级Agent任务委托 |
| **状态监控** | alive/idle/stuck状态追踪 |
| **超时控制** | 自动终止超时任务 |

## 与token-optimizer集成

继承 `token-optimizer/scripts/heartbeat_optimizer.py` 的核心逻辑：
- 心跳计划管理
- 心跳检查执行
- 心跳记录追踪
- 缓存TTL管理

## 命令

```bash
# 添加心跳任务
/heartbeat add <agent> <schedule>

# 查看状态
/heartbeat status [agent]

# 暂停心跳
/heartbeat pause <agent>

# 恢复心跳
/heartbeat resume <agent>

# 查看历史
/heartbeat history [agent] [--limit 10]

# 手动触发
/heartbeat trigger <agent>
```

## 数据模型

```typescript
interface HeartbeatConfig {
  id: string;
  agentId: string;
  companyId: string;
  schedule: string;  // cron表达式，如 "0 */4 * * *"
  source: 'timer' | 'assignment' | 'on_demand' | 'automation';
  trigger: 'manual' | 'ping' | 'callback' | 'system';
  timeoutMs: number;
  enabled: boolean;
  createdAt: Date;
  updatedAt: Date;
}

interface HeartbeatRun {
  id: string;
  agentId: string;
  status: 'queued' | 'running' | 'succeeded' | 'failed' | 'cancelled' | 'timed_out';
  startedAt?: Date;
  finishedAt?: Date;
  error?: string;
  usageJson?: Record<string, unknown>;
}
```

## 使用示例

### 1. 添加定时心跳

```bash
# 每4小时执行一次
/heartbeat add 03builder "0 */4 * * *"

# 每天早上9点执行
/heartbeat add 07scribe "0 9 * * *"

# 每15分钟检查一次
/heartbeat add 04validator "*/15 * * * *"
```

### 2. 查看心跳状态

```bash
/heartbeat status

# 输出:
# 📊 心跳状态
# ================
# Agent: 03builder
# Schedule: 0 */4 * * * (每4小时)
# Status: idle
# Last Run: 2026-03-15 12:00:00
# Next Run: 2026-03-15 16:00:00
```

### 3. 事件触发

```typescript
// 任务分配时自动触发
TicketDB.update(ticketId, { assigneeAgentId: agentId });
// → 自动创建心跳请求

// @提及触发
CommentDB.create({ content: "@03builder 请检查这个bug" });
// → 自动唤醒Agent
```

## 与天龙引擎协同

| 天龙组件 | 心跳协同 |
|---------|---------|
| **09-02编排协调师** | 心跳调度集成 |
| **07记录师** | 心跳记录持久化 |
| **08发布师** | 定时发布任务 |

## 心跳生命周期

```
┌─────────────────────────────────────────────────────────────┐
│ 心跳生命周期                                                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. 创建配置                                                  │
│     /heartbeat add agent "schedule"                          │
│         ↓                                                    │
│  2. 调度器监听                                                │
│     定时检查 → 时间到达?                                      │
│         ↓                                                    │
│  3. 创建运行记录                                              │
│     status: queued                                           │
│         ↓                                                    │
│  4. 执行任务                                                  │
│     status: running                                          │
│     → 调用Agent执行                                           │
│         ↓                                                    │
│  5. 完成记录                                                  │
│     status: succeeded | failed | timed_out                   │
│         ↓                                                    │
│  6. 记录成本                                                  │
│     CostEventDB.create(...)                                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 实现文件

- `scripts/heartbeat.ts` - 心跳调度器实现
- `scripts/cron-parser.ts` - Cron解析器
- `scripts/heartbeat-monitor.ts` - 状态监控

## 版本历史

| 版本 | 日期 | 更新 |
|------|------|------|
| 1.0.0 | 2026-03-15 | 初始版本，基于Paperclip心跳机制 |