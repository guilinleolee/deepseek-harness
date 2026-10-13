---
license: UNKNOWN
name: claude-checkpoints
description: Claude Code会话快照与回滚能力 - 保存/恢复/对比会话状态
triggers: ["claude checkpoints", "Claude Checkpoints - 会话快照与回滚系统"]
---

# Claude Checkpoints - 会话快照与回滚系统

## L0: 一句话描述 (≤15字)
会话快照保存与恢复

## L1: 使用场景 (50-100字)

**适用场景**：
- 长任务执行前保存会话状态，失败后可回滚
- 尝试性修改前创建检查点，保留回退能力
- 多方案对比时创建多个快照，并行尝试后选择最优

**触发关键词**：`/checkpoint`、`/checkpoint-save`、`/checkpoint-restore`、`会话快照`、`回滚`

## L2: 详细文档

### 核心能力

| 功能 | 命令 | 说明 |
|------|------|------|
| **保存快照** | `/checkpoint save [name]` | 保存当前会话状态 |
| **列出快照** | `/checkpoint list` | 查看所有快照 |
| **恢复快照** | `/checkpoint restore [id]` | 恢复到指定快照 |
| **对比快照** | `/checkpoint diff [id1] [id2]` | 对比两个快照差异 |
| **删除快照** | `/checkpoint delete [id]` | 删除指定快照 |

### 实现原理

```
Checkpoint = 会话状态 + 文件系统状态 + 元数据
├── 会话状态: 对话历史、TodoWrite、上下文
├── 文件系统: git status、工作目录变化
└── 元数据: 时间戳、描述、标签
```

### 使用示例

```bash
# 保存当前会话状态
/checkpoint save before-refactor

# 尝试重构
[@03构建师] 开始重构支付模块

# 如果失败，恢复到保存点
/checkpoint restore before-refactor

# 对比两个版本
/checkpoint diff checkpoint-001 checkpoint-002
```

### 与 claude-mem 协同

| 组件 | 职责 |
|------|------|
| **Checkpoint** | 短期会话快照（<7天） |
| **claude-mem** | 长期记忆持久化 |
| **lessons.md** | 经验教训沉淀 |

### 自动触发规则

| 场景 | 自动保存 |
|------|---------|
| 架构决策前 | ✅ 保存为 `before-architecture-[timestamp]` |
| 大规模重构前 | ✅ 保存为 `before-refactor-[timestamp]` |
| 依赖升级前 | ✅ 保存为 `before-upgrade-[timestamp]` |

### 数据存储

```yaml
~/.claude/checkpoints/
├── checkpoint-[uuid]/
│   ├── session.json      # 会话状态
│   ├── git-state.json    # Git状态
│   ├── todos.json        # TodoWrite状态
│   ├── context.json      # 上下文摘要
│   └── meta.yaml         # 元数据
└── index.json            # 快照索引
```

## 与官方 Checkpoints API 对齐

Claude Code 内置 Checkpoints 支持以下事件：

| 事件 | 触发时机 | 自动行为 |
|------|---------|---------|
| `SessionStart` | 新会话开始 | 记录初始状态 |
| `Stop` | 会话结束 | 提示保存检查点 |
| `CheckpointCreate` | 手动创建 | 保存完整状态 |
| `CheckpointRestore` | 恢复快照 | 加载历史状态 |

## 安全考虑

- 快照包含完整上下文，确保敏感信息不外泄
- 本地存储在 `~/.claude/checkpoints/`
- 自动清理超过 30 天的快照

## 相关技能

- `claude-mem` - 长期记忆系统
- `lessons-logger` - 经验教训记录
