---
license: UNKNOWN
name: crew-lifecycle-manager
version: 1.0.0
description: |
  Crew生命周期管理：团队列表查询、成员招募、成员解散三大核心操作。
  与Wiseflow Addon Bundle机制深度集成，支持天龙引擎多Agent团队动态编排。
author: 天龙引擎团队
created: 2026-05-05
category: ai
source_type: derived
origin: TeamWiseFlow/wiseflow (crew-lifecycle)
github_repo: TeamWiseFlow/wiseflow
github_hash: main
last_updated: 2026-05-05
triggers:
  - "crew生命周期管理"
  - "团队列表查询"
  - "成员招募"
  - "成员解散"
  - "crew-list"
  - "crew-recruit"
  - "crew-dismiss"
---

# Crew Lifecycle Manager — 团队生命周期管理器

## 功能概述

Crew生命周期管理是Wiseflow Addon Bundle的核心组件，提供三大核心操作：

1. **List Crews** — 查询当前所有活跃的内部Crew团队及其成员
2. **Recruit Crew Member** — 招募新Agent加入指定Crew（通过Agent ID）
3. **Dismiss Crew Member** — 从指定Crew解散/移除某成员（通过Agent ID）

## 核心能力

### 1. 团队列表查询 (list-crews)

```bash
./scripts/list-crews.sh
```

**功能**：
- 扫描 `~/.claude/agents/` 目录下的所有Agent文件
- 解析每个Agent的元数据（编号、名称、描述、状态）
- 按域名分组展示团队成员
- 支持格式化输出（JSON/YAML/表格）

**输出示例**：
```json
{
  "timestamp": "2026-05-05T10:30:00Z",
  "total_agents": 192,
  "domains": {
    "核心九部": ["00分析师", "01调研师", ...],
    "企划中心": ["22-01战略策划", ...],
    ...
  }
}
```

### 2. 成员招募 (recruit-crew)

```bash
./scripts/recruit-crew.sh <agent-id>
```

**功能**：
- 验证Agent ID有效性
- 检查Agent是否已存在
- 创建Agent配置文件（.md格式）
- 更新团队索引
- 发送通知到编排协调师

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| agent-id | string | 是 | 目标Agent编号（如"35-02社媒运营"） |

**流程**：
```
验证Agent ID
    ↓
检查是否已存在
    ↓
创建Agent配置文件
    ↓
更新团队索引 (agents/index.json)
    ↓
通知编排协调师
```

### 3. 成员解散 (dismiss-crew)

```bash
./scripts/dismiss-crew.sh <agent-id>
```

**功能**：
- 验证Agent ID有效性
- 检查Agent是否在团队中
- 归档Agent配置文件（移至 archive/）
- 更新团队索引
- 清理相关依赖

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| agent-id | string | 是 | 目标Agent编号 |

**流程**：
```
验证Agent ID
    ↓
检查是否在团队中
    ↓
归档Agent文件 → archive/<agent-id>-<timestamp>.md
    ↓
更新团队索引（移除）
    ↓
清理依赖关系
```

## 工作流

```
┌─────────────────────────────────────────────────────────────┐
│         Crew Lifecycle Manager 工作流                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   编排协调师 (09-02)                                        │
│       │                                                     │
│       ├──▶ list-crews.sh ──▶ 团队全景视图                 │
│       │                                                     │
│       ├──▶ recruit-crew.sh ──▶ 新Agent加入                │
│       │                                                     │
│       └──▶ dismiss-crew.sh ──▶ 成员离开                    │
│                                                             │
│   团队索引 (agents/index.json)                             │
│       │                                                     │
│       └──▶ 自动同步 ──▶ 编排协调师实时感知团队变化          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 规则

### 基本规则

1. **Agent ID格式**：`[中心十位][部门个位]-[序号]`
   - 示例：`35-02` = 企划中心-社媒运营
   - 有效范围：`00-99`

2. **配置文件命名**：`[agent-id].md`
   - 示例：`35-02-social-media.md`

3. **归档保留**：解散的Agent移至 `archive/`，保留90天

4. **索引同步**：所有操作后必须更新 `agents/index.json`

### 安全规则

1. **禁止删除核心九部**：`00`~`08` 编号的Agent不可解散
2. **权限验证**：需要编排协调师授权才能执行招募/解散
3. **审计日志**：所有操作记录到 `logs/crew-lifecycle.log`

## 配置文件

### Team Index (agents/index.json)

```json
{
  "version": "1.0",
  "updated": "2026-05-05T10:30:00Z",
  "agents": [
    {
      "id": "00-01",
      "name": "分析师",
      "domain": "核心九部",
      "status": "active",
      "file": "agents/00-analyst.md"
    }
  ],
  "domains": ["核心九部", "企划中心", "营销中心", ...]
}
```

### Archive Index (archive/index.json)

```json
{
  "archived": [
    {
      "id": "35-02",
      "name": "社媒运营",
      "archived_at": "2026-05-05T10:30:00Z",
      "reason": "dismissed",
      "restored_at": null
    }
  ]
}
```

## 与天龙引擎协作

### 适用岗位

| 岗位 | 集成方式 | 增强能力 |
|------|---------|---------|
| **09-02 编排协调师** | 直接调用 | Crew生命周期协议 |
| **09-03 元审查师** | 团队健康检查 | 异常检测 |
| **09-04 首席幕僚长** | 团队报告 | 全景视图 |

### 天龙引擎增强

```
┌─────────────────────────────────────────────────────────────┐
│ 天龙引擎 Crew Lifecycle 体系                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   09-02 编排协调师                                          │
│       │                                                     │
│       ├── list-crews    → 全团队视图                       │
│       ├── recruit-crew  → 动态扩张                         │
│       └── dismiss-crew  → 动态收缩                         │
│                                                             │
│   Wiseflow 集成:                                           │
│   ├── SOUL.md          → 主Agent工作流                    │
│   ├── Addon Bundle     → 技能包机制                       │
│   └── crew-lifecycle   → 团队生命周期管理                  │
│                                                             │
│   协同技能:                                                 │
│   ├── /agents-list        → Agent清单                    │
│   ├── /crewai-orchestration → CrewAI多Agent              │
│   ├── /dispatching-parallel-agents → 并行调度             │
│   └── /crew-lifecycle     → 生命周期管理 ⭐新增           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 核心命令

```bash
# 列表查询
/crew-list                      # 列出所有团队
/crew-list --domain 企划中心    # 按域名筛选
/crew-list --format json        # JSON格式输出

# 成员招募
/crew-recruit 35-02            # 招募社媒运营Agent
/crew-recruit 35-02 --notify   # 招募并通知编排协调师

# 成员解散
/crew-dismiss 35-02             # 解散社媒运营Agent
/crew-dismiss 35-02 --archive  # 解散并归档

# 编排协调师集成
[@编排协调师] 查看当前团队列表
[@编排协调师] 招募新成员 35-02
[@编排协调师] 解散成员 35-02
[@编排协调师] Crew生命周期状态报告
```

## 示例

### 示例1：查询团队全景

**输入**：
```
[@编排协调师] 查看当前全部团队成员
```

**执行**：
```bash
./scripts/list-crews.sh --format table
```

**输出**：
```
┌─────────────────────────────────────────────────────────────┐
│ 天龙引擎团队全景                                            │
├─────────────────────────────────────────────────────────────┤
│ 核心九部 (9)    │ 企划中心 (12)  │ 营销中心 (15)          │
│────────────────────────────────────────────────────────────│
│ 00分析师 ✓      │ 22-01战略策划  │ 32-01市场研究 ✓       │
│ 01调研师 ✓      │ 25-02精益创业  │ 35-02社媒运营 ⭐NEW   │
│ 02架构师 ✓      │ ...            │ ...                    │
├─────────────────────────────────────────────────────────────┤
│ 总计: 192个Agent │ 活跃: 190    │ 已归档: 2              │
└─────────────────────────────────────────────────────────────┘
```

### 示例2：招募新成员

**输入**：
```
[@编排协调师] 招募一个新的数据分析师，编号17-01
```

**执行**：
```bash
./scripts/recruit-crew.sh 17-01
```

**输出**：
```
✅ Agent 17-01 招募成功
📁 配置文件: agents/17-01-data-analyst.md
📝 索引已更新: agents/index.json
🔔 通知已发送: 09-02编排协调师
```

### 示例3：解散成员

**输入**：
```
[@编排协调师] 解散35-02社媒运营（已升级至新版本）
```

**执行**：
```bash
./scripts/dismiss-crew.sh 35-02 --reason "upgraded"
```

**输出**：
```
⚠️ 确认操作：解散 Agent 35-02 社媒运营
   原因: upgraded
   影响: 将归档至 archive/35-02-20260505.md
   依赖: 3个依赖关系将清理

确认解散? (y/n): y

✅ Agent 35-02 已解散
📦 归档: archive/35-02-20260505.md
🧹 依赖已清理: 3个
📝 索引已更新: agents/index.json
```

## 天龙引擎版本记录

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-05 | 初始集成，基于Wiseflow crew-lifecycle |

---

**版本**: V1.0 | **兼容性**: 天龙引擎 V11.05+ | **来源**: TeamWiseFlow/wiseflow