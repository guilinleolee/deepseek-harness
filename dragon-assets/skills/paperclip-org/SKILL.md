---
license: UNKNOWN
name: paperclip-org
description: 组织架构管理
github_repo: paperclipai/paperclip
github_hash: 70679a33216bae9247b1b6bddc5fcaad1c04e829
last_updated: 2026-04-25
source_type: derived
version: 1.5.0
author: 天龙引擎团队
created: 2026-03-15
updated: 2026-08-10
changelog:
  - 1.5.0 (2026-08-10): CEC v1.5 扩展，新增 customers/customerReportsTo/customerBudgets 字段 + 5 个客户维度命令
  - 1.0.0 (2026-03-15): 初始版本
category: management
triggers: ["paperclip org", "Paperclip组织架构", "天龙 CEC v1.5 客户维度"]
---

# Paperclip组织架构

## 概述

基于 [paperclipai/paperclip](https://github.com/paperclipai/paperclip) 的组织架构管理，为天龙引擎提供团队结构和汇报关系管理。

## 核心能力

| 能力 | 说明 |
|------|------|
| **层级定义** | 定义Agent层级结构 |
| **角色分配** | 为Agent分配角色 |
| **汇报关系** | 设置上下级汇报关系 |
| **预算管理** | 为Agent分配预算 |
| **客户维度（v1.5）** | 为Agent分配客户归属与客户方汇报关系 |

## 命令

```bash
# 显示组织架构
/org show

# 添加成员
/org add <agent> <role> [--reports-to <manager>]

# 设置汇报
/org report <agent> <manager>

# 设置预算
/org budget <agent> <amount>

# 查看团队
/org team <manager>

# ========== v1.5 新增客户维度命令（CEC v1.5） ==========

# 分配客户归属（agent 负责哪个客户）
/org assign-customer <agent> <customer>

# 设置客户方汇报关系（agent 向客户方 owner 汇报）
/org report-customer <agent> <customer>

# 分配客户专属预算
/org budget-customer <agent> <customer> <amount>

# 查看某客户的所有天龙成员
/org customer-team <customer>

# 查看天龙 agent 跨客户分布
/org agent-customers <agent>
```

## 数据模型

```typescript
interface Agent {
  // ========== v1.0 字段（保留） ==========
  id: string;
  name: string;
  role: string;
  title?: string;
  reportsTo?: string;           // 上级Agent ID
  budgetMonthlyCents: number;
  status: 'idle' | 'running' | 'paused';

  // ========== v1.5 新增字段（CEC 客户工程中心） ==========
  // 来源: [[09-天龙-CEC-v1.5-paperclip-ticket-打通方案]]
  // 落地: 2026-08-10 W5
  customers?: string[];             // 该 agent 负责的客户列表
  customerReportsTo?: {             // 客户方汇报关系映射
    [customer: string]: string;     // customer → 客户方 owner 标识
  };
  customerBudgets?: {               // 客户专属预算
    [customer: string]: number;
  };
}
```

### v1.5 字段语义

| 字段 | 类型 | 必填 | 用途 |
|---|---|---|---|
| **customers** | string[] | 否 | 该 agent 服务的所有客户名（关联 `~/customers/<name>/`） |
| **customerReportsTo** | map | 否 | 每个客户的 owner 标识，用于跨客户汇报链 |
| **customerBudgets** | map | 否 | 每个客户的专属预算（cent 单位） |

### v1.5 命令语义

| 命令 | 用途 |
|---|---|
| `/org assign-customer <agent> <customer>` | 把客户分配给 agent，建立 `customers` 数组 |
| `/org report-customer <agent> <customer>` | 设置 agent 向客户方 owner 汇报 |
| `/org budget-customer <agent> <customer> <amount>` | 给某客户的预算独立于通用预算 |
| `/org customer-team <customer>` | 反向查询：哪些天龙 agent 服务此客户 |
| `/org agent-customers <agent>` | 正向查询：此 agent 服务哪些客户 |

## 组织架构示例

```
CEO (00分析师)
├── CTO (02架构师)
│   ├── Tech Lead (03构建师)
│   │   ├── Developer A
│   │   └── Developer B
│   └── QA Lead (04验证师)
│       └── Tester A
└── CMO (30-01营销总监)
    ├── Marketing Lead (35-01数字营销)
    └── Content Lead (07记录师)
```

### v1.5 客户维度架构（CEC v1.5）

```
天龙 CEC 客户工程中心
├── CSO (首席服务官 / 老李本人)
│   ├── [客户] dragon-engine-v1 (天龙自优化)
│   │   ├── FDE Lead (39-forward-deployed-engineer)
│   │   │   └── → 客户方 owner: 老李本人
│   │   ├── CS Architect (41-customer-success-architect)
│   │   │   └── → 客户方 owner: 老李本人
│   │   └── Tech Lead (02-architect + 03-builder)
│   │       └── → 客户方 owner: 老李本人
│   │
│   └── [客户] acme-corp (未来真实客户)
│       ├── FDE Lead (39-forward-deployed-engineer)
│       │   └── → 客户方 owner: 客户 CEO
│       ├── CS Architect (41-customer-success-architect)
│       │   └── → 客户方 owner: 客户 CTO
│       └── Tech Lead (02-architect + 03-builder)
│           └── → 客户方 owner: 客户 CIO
```

**核心思想**：天龙 agent 可同时服务多个客户，每个客户有独立的汇报关系和预算。

## 版本历史

| 版本 | 日期 | 更新 |
|------|------|------|
| 1.0.0 | 2026-03-15 | 初始版本 |