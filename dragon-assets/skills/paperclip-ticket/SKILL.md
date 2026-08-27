---
license: UNKNOWN
name: paperclip-ticket
description: 工单系统，持久化追踪+审计
github_repo: paperclipai/paperclip
github_hash: 70679a33216bae9247b1b6bddc5fcaad1c04e829
last_updated: 2026-04-25
source_type: derived
version: 1.5.0
author: 天龙引擎团队
created: 2026-03-15
updated: 2026-08-10
changelog:
  - 1.5.0 (2026-08-10): CEC v1.5 扩展，新增 customer/fdeStage/sourceType/sourceFile/healthImpact/cancelReason 字段
  - 1.0.0 (2026-03-15): 初始版本
category: management
triggers: ["paperclip ticket", "Paperclip工单系统", "天龙 CEC v1.5 工单"]
---

# Paperclip工单系统

## 概述

基于 [paperclipai/paperclip](https://github.com/paperclipai/paperclip) 的工单系统，为天龙引擎提供任务持久化和审计追踪能力。

## 核心能力

| 能力 | 说明 |
|------|------|
| **工单CRUD** | 创建、读取、更新、删除工单 |
| **状态流转** | backlog → in_progress → review → completed |
| **执行锁定** | 防止多个Agent同时执行同一任务 |
| **审计日志** | 完整的操作历史记录 |

## 命令

```bash
# 创建工单
/ticket create <title> [--priority high] [--assignee agent]

# 查看状态
/ticket status <id>

# 查看历史
/ticket history <id>

# 分配工单
/ticket assign <id> <agent>

# 更新状态
/ticket update <id> --status in_progress

# 查看列表
/ticket list [--status backlog] [--assignee agent]
```

## 数据模型

```typescript
interface Ticket {
  // ========== v1.0 字段（保留） ==========
  id: string;
  companyId: string;
  title: string;
  description?: string;
  status: 'backlog' | 'in_progress' | 'review' | 'completed' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  assigneeAgentId?: string;
  executionLockedAt?: Date;
  startedAt?: Date;
  completedAt?: Date;
  createdAt: Date;
  updatedAt: Date;

  // ========== v1.5 新增字段（CEC 客户工程中心） ==========
  // 来源: [[09-天龙-CEC-v1.5-paperclip-ticket-打通方案]]
  // 落地: 2026-08-10 W5
  customer?: string;           // 客户名（关联 ~/customers/<name>/）
  fdeStage?: 'land' | 'discover' | 'plan' | 'build' | 'ship' | 'close';  // FDE 阶段
  sourceType?: 'fieldbook' | 'aar' | 'manual';   // 触发来源类型
  sourceFile?: string;         // 触发源文件路径
  healthImpact?: 'positive' | 'neutral' | 'negative';  // 健康度影响
  cancelReason?: string;       // 取消原因（仅 status=cancelled 时使用）
}
```

### v1.5 字段语义

| 字段 | 类型 | 必填 | 用途 |
|---|---|---|---|
| **customer** | string | 否 | 关联 `~/customers/<name>/`，用于跨工单聚合客户视图 |
| **fdeStage** | enum | 否 | 标识工单所属 FDE 阶段，用于自动状态机校验 |
| **sourceType** | enum | 否 | 区分天龙自动创建（fieldbook/aar）vs 手动创建 |
| **sourceFile** | string | 否 | 触发源文件路径，便于溯源 |
| **healthImpact** | enum | 否 | 联动 [[account-health-dashboard]] 时使用 |
| **cancelReason** | string | 否 | 异常工单的取消原因，写入 dashboard.md |

### 状态流转

```
backlog → in_progress → review → completed
    ↓         ↓          ↓
    └─────────┴──────────→ cancelled
```

### v1.5 联动规则（与 [[cec-ticket-flow]] skill 协同）

| 状态变化 | 联动 |
|---|---|
| → `in_progress` | 调用 [[paperclip-heartbeat]] 创建心跳监控 |
| → `review` | 准备 AAR 提醒（打印 `/aar <customer> <stage>` 建议） |
| → `completed` | 调用 ticket-health-bridge hook 更新 [[account-health-dashboard]] |
| → `cancelled` | 写入 dashboard.md 异常项（保留 `cancelReason`） |

## 使用示例

### 1. 创建工单

```bash
/ticket create "实现用户认证" --priority high --assignee 03builder

# 输出:
# ✅ 工单已创建
# ID: ticket-123
# Title: 实现用户认证
# Status: backlog
# Priority: high
# Assignee: 03builder
```

### 2. 查看状态

```bash
/ticket status ticket-123

# 输出:
# 📋 工单详情
# ================
# ID: ticket-123
# Title: 实现用户认证
# Status: in_progress
# Priority: high
# Assignee: 03builder
# Created: 2026-03-15 10:00:00
# Updated: 2026-03-15 11:30:00
```

## 与天龙引擎协同

| 天龙组件 | 工单协同 |
|---------|---------|
| **07记录师** | 工单持久化 |
| **08发布师** | 发布任务追踪 |
| **09-02编排协调师** | 任务分配 |

## 版本历史

| 版本 | 日期 | 更新 |
|------|------|------|
| 1.0.0 | 2026-03-15 | 初始版本 |