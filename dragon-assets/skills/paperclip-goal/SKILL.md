---
license: UNKNOWN
name: paperclip-goal
description: 目标对齐，战略一致性
github_repo: paperclipai/paperclip
github_hash: 70679a33216bae9247b1b6bddc5fcaad1c04e829
last_updated: 2026-04-25
source_type: derived
version: 1.0.0
author: 天龙引擎团队
created: 2026-03-15
category: strategy
triggers: ["paperclip goal", "Paperclip目标对齐"]
---

# Paperclip目标对齐

## 概述

基于 [paperclipai/paperclip](https://github.com/paperclipai/paperclip) 的目标对齐机制，为天龙引擎提供战略一致性检查能力。

## 核心能力

| 能力 | 说明 |
|------|------|
| **目标层级** | Company → Team → Agent → Task |
| **目标追溯** | 任务追溯到公司使命 |
| **一致性检查** | 验证决策是否符合目标 |

## 命令

```bash
# 设置公司目标
/goal set "成为行业领先的AI公司"

# 创建团队目标
/goal create --level team --title "提升产品质量" --parent <companyGoalId>

# 追溯任务目标
/goal trace <taskId>

# 对齐Agent目标
/goal align <agentId> <goalId>

# 查看目标树
/goal tree
```

## 数据模型

```typescript
interface Goal {
  id: string;
  title: string;
  description?: string;
  level: 'company' | 'team' | 'agent' | 'task';
  status: 'planned' | 'active' | 'completed' | 'cancelled';
  parentId?: string;
  ownerAgentId?: string;
}
```

## 目标层级示例

```
Company: "成为行业领先的AI公司"
├── Team (产品): "打造用户体验最佳的产品"
│   ├── Agent (产品经理): "定义产品路线图"
│   │   └── Task: "完成Q2版本规划"
│   └── Agent (设计师): "提升界面美感"
│       └── Task: "重新设计首页"
└── Team (技术): "构建稳定可靠的技术平台"
    ├── Agent (架构师): "设计可扩展架构"
    │   └── Task: "完成微服务拆分方案"
    └── Agent (开发): "高质量交付功能"
        └── Task: "实现用户认证模块"
```

## 与天龙引擎协同

| 天龙组件 | 目标协同 |
|---------|---------|
| **00分析师** | 目标定义 |
| **02架构师** | 架构决策追溯 |
| **09-02编排协调师** | 任务分配对齐 |

## 版本历史

| 版本 | 日期 | 更新 |
|------|------|------|
| 1.0.0 | 2026-03-15 | 初始版本 |