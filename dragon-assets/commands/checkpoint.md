---
name: checkpoint
description: Claude Code会话快照与回滚管理 - 保存/恢复/对比会话状态
invokable: true
---
# Checkpoint - 会话快照管理

## 功能列表

| 操作 | 命令 |
|------|------|
| 保存快照 | `/checkpoint save [名称]` |
| 列出快照 | `/checkpoint list` |
| 恢复快照 | `/checkpoint restore [ID]` |
| 对比快照 | `/checkpoint diff [ID1] [ID2]` |
| 删除快照 | `/checkpoint delete [ID]` |

## 保存快照

执行以下命令保存当前会话状态：

```bash
python3 ~/.claude/skills/claude-checkpoints/scripts/checkpoint_manager.py save "[快照名称]" --desc "[描述]"
```

## 列出快照

```bash
python3 ~/.claude/skills/claude-checkpoints/scripts/checkpoint_manager.py list
```

## 恢复快照

```bash
python3 ~/.claude/skills/claude-checkpoints/scripts/checkpoint_manager.py restore [快照ID]
```

## 使用场景

### 场景1: 大规模重构前
```
在开始重构前保存快照，以便失败时快速回滚
```

### 场景2: 多方案对比
```
创建多个快照并行尝试不同方案，选择最优后删除其他
```

### 场景3: 架构决策前
```
架构变更前保存状态，记录决策历史
```

## 自动触发规则

以下场景我会自动建议保存快照：
- 文件修改 > 10个
- 涉及架构变更
- 依赖升级
- 数据库迁移
