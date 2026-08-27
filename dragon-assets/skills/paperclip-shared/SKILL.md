---
license: UNKNOWN
name: paperclip-shared
version: 1.0.0
description: Paperclip与天龙引擎集成共享模块
author: 天龙引擎团队
created: 2026-03-15
category: infrastructure

triggers:
  - "paperclip-shared"
  - "paperclip db"
---

# Paperclip共享模块

## 概述

提供Paperclip与天龙引擎集成的基础设施，包括数据模型、数据库客户端和适配器注册表。

## 模块结构

```
paperclip-shared/
├── db/
│   ├── schema.ts    # 数据模型定义
│   └── client.ts    # 数据库客户端
└── adapters/
    └── registry.ts  # 适配器注册表
```

## 数据模型

### 核心实体

| 实体 | 说明 |
|------|------|
| `Agent` | AI Agent实体，包含预算、状态、汇报关系 |
| `HeartbeatConfig` | 心跳配置，支持Cron表达式 |
| `HeartbeatRun` | 心跳运行记录 |
| `Ticket` | 工单实体 |
| `CostEvent` | 成本事件 |
| `Goal` | 目标层级 |
| `Approval` | 审批流程 |

## 使用方式

```typescript
import { AgentDB, HeartbeatConfigDB, TicketDB } from './db/client';

// 创建Agent
const agent = AgentDB.create({
  companyId: 'default',
  name: 'Coding Agent',
  role: 'developer',
  adapterType: 'claude_code',
  budgetMonthlyCents: 10000
});

// 添加心跳配置
const heartbeat = HeartbeatConfigDB.create({
  agentId: agent.id,
  companyId: 'default',
  schedule: '0 */4 * * *',  // 每4小时
  source: 'timer',
  trigger: 'manual',
  timeoutMs: 300000,
  enabled: true
});

// 创建工单
const ticket = TicketDB.create({
  companyId: 'default',
  title: '实现用户认证',
  status: 'backlog',
  priority: 'high'
});
```

## 适配器

支持以下Agent运行时：

| 类型 | 说明 |
|------|------|
| `claude_code` | Claude Code CLI |
| `openclaw` | OpenClaw Gateway |
| `cursor` | Cursor IDE |
| `process` | Shell进程 |
| `http` | HTTP API |

```typescript
import { getAdapter } from './adapters/registry';

const adapter = getAdapter('claude_code');
const result = await adapter.execute(agent, '实现登录功能');
```

## 存储

数据存储在 `~/.paperclip/` 目录：

```
~/.paperclip/
└── instances/
    └── default/
        └── db/
            ├── companies.json
            ├── agents.json
            ├── heartbeat_configs.json
            ├── heartbeat_runs.json
            ├── tickets.json
            ├── cost_events.json
            ├── goals.json
            └── approvals.json
```

## 版本历史

| 版本 | 日期 | 更新 |
|------|------|------|
| 1.0.0 | 2026-03-15 | 初始版本 |