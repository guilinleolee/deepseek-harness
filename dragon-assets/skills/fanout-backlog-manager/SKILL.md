---
license: UNKNOWN
triggers: ["fanout backlog manager", "Fanout Backlog Manager SKILL"]
---
# Fanout Backlog Manager SKILL

## L0: 一句话描述
GEO内容生产任务队列管理，支持Fanout工作流和多层级优先级调度。

## L1: 使用场景

### 核心功能
- **任务创建**: 从Editorial Brief创建GEO内容任务
- **Fanout分发**: 将任务分发到多个平台（WordPress、公众号等）
- **状态追踪**: 5层质量门控状态监控
- **优先级调度**: P0/P1/P2/P3四级优先级

### 适用场景
- 批量GEO内容生产管理
- 多平台发布协调
- 质量门控流程控制

## L2: 详细文档

### 命令

```bash
# 创建新任务
fanout-add --brief <editorial_brief_id> --priority P0

# 查看队列
fanout-list --status all --priority P0,P1

# 更新状态
fanout-update <task_id> --status drafting --gate L2

# 执行Fanout
fanout-execute <task_id> --targets wordpress,wechat

# 质量门控检查
fanout-qc <task_id> --gate L1,L2,L3,L4,L5
```

### 核心字段

| 字段 | 类型 | 说明 |
|------|------|------|
| task_id | string | 唯一标识(UUID) |
| brief_id | string | 关联的Editorial Brief |
| status | enum | drafting/reviewing/published/archived |
| priority | enum | P0/P1/P2/P3 |
| gates | dict | 各层质量门控状态 |
| fanout_targets | list | 发布目标列表 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### 质量门控状态

```
L1: 事实核查 ──── □ PASS / □ FAIL
L2: 引用质量 ──── □ PASS / □ FAIL
L3: 结构化 ───── □ PASS / □ FAIL
L4: 实体清晰 ──── □ PASS / □ FAIL
L5: 人类可读 ──── □ PASS / □ FAIL
```

### 数据存储

- 主文件: `~/.claude/skills/fanout-backlog-manager/data/backlog.json`
- 历史归档: `~/.claude/skills/fanout-backlog-manager/data/archive/`

## 脚本文件

- [scripts/backlog_cli.py](scripts/backlog_cli.py) - CLI命令行工具
- [scripts/fanout_executor.py](scripts/fanout_executor.py) - Fanout执行器
- [scripts/qc_checker.py](scripts/qc_checker.py) - 质量门控检查器
