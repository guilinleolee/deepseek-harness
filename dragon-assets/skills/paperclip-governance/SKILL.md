---
license: UNKNOWN
name: paperclip-governance
description: 治理门控，审批+回滚
github_repo: paperclipai/paperclip
github_hash: 70679a33216bae9247b1b6bddc5fcaad1c04e829
last_updated: 2026-04-25
source_type: derived
version: 1.0.0
author: 天龙引擎团队
created: 2026-03-15
category: governance
triggers: ["paperclip governance", "Paperclip治理层"]
---

# Paperclip治理层

## 概述

基于 [paperclipai/paperclip](https://github.com/paperclipai/paperclip) 的治理机制，为天龙引擎提供审批门控和回滚能力。

## 核心能力

| 能力 | 说明 |
|------|------|
| **审批门控** | 关键操作需要审批 |
| **配置版本控制** | 记录配置变更历史 |
| **安全回滚** | 回滚到历史版本 |
| **Agent控制** | 暂停/终止Agent |

## 与09-03元审查师协同

- 复用Meta Review触发条件
- 审批通过后执行
- 审批拒绝后回滚

## 命令

```bash
# 创建审批请求
/governance request <entityType> <entityId> <action>

# 审批
/governance approve <requestId>

# 拒绝
/governance reject <requestId> [--reason "..."]

# 回滚
/governance rollback <entityType> <entityId> <version>

# 暂停Agent
/governance pause <agentId>

# 查看待审批
/governance pending
```

## 数据模型

```typescript
interface Approval {
  id: string;
  entityType: string;      // 'agent', 'config', 'release'
  entityId: string;
  action: string;           // 'create', 'update', 'delete', 'deploy'
  status: 'pending' | 'approved' | 'rejected' | 'cancelled';
  requestedByType: 'agent' | 'user';
  requestedById: string;
  reviewedByType?: 'agent' | 'user';
  reviewedById?: string;
  reviewedAt?: Date;
  reason?: string;
  createdAt: Date;
}
```

## 审批流程

```
┌─────────────────────────────────────────────────────────────┐
│ 审批流程                                                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. 创建请求                                                  │
│     /governance request agent 03builder update               │
│         ↓                                                    │
│  2. 等待审批                                                  │
│     status: pending                                          │
│         ↓                                                    │
│  3. 审批决策                                                  │
│     /governance approve <id>  或  /governance reject <id>    │
│         ↓                       ↓                            │
│  4a. 执行操作              4b. 拒绝操作                       │
│     status: approved          status: rejected               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 触发审批的场景

| 场景 | 实体类型 | 操作 |
|------|---------|------|
| 创建Agent | agent | create |
| 更新Agent配置 | agent | update |
| 部署发布 | release | deploy |
| 修改预算 | budget | update |
| 删除资源 | resource | delete |

## 版本历史

| 版本 | 日期 | 更新 |
|------|------|------|
| 1.0.0 | 2026-03-15 | 初始版本 |