---
license: UNKNOWN
triggers: ["archive", "archive - 跨会话知识归档系统"]
---
# archive - 跨会话知识归档系统

> 跨会话持久化知识，让AI每次对话不再是"从零开始"

## L0: 一句话描述

**跨会话知识归档，AI记忆持久化**

## L1: 使用场景

解决AI每次对话从零开始的问题。当你在一个会话中做出了重要决策、发现了关键代码模式、或积累了项目特定知识时，archive将这些内容持久化存储，在未来的会话中自动检索和应用，实现知识复利效应。

## L2: 详细文档

### 核心价值

```
┌─────────────────────────────────────────────────────────────────────┐
│                    archive 核心定位                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   claude-mem (会话层)                                              │
│   ├── 自动捕获会话内容                                            │
│   ├── 短期记忆 / 当前项目上下文                                    │
│   └── 生命周期: 单次会话                                          │
│              ↓                                                    │
│   archive (归档层)  ⭐ 本技能                                      │
│   ├── 跨会话持久化                                                │
│   ├── 决策/模式/发现归档                                          │
│   └── 生命周期: 永久 / 跨会话                                     │
│              ↓                                                    │
│   lessons.md (经验层)                                              │
│   ├── 经验教训提取                                                │
│   ├── 最佳实践/错误模式                                          │
│   └── 生命周期: 永久 / 可追溯                                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 三层记忆协同矩阵

| 层级 | 系统 | 内容类型 | 生命周期 | 触发时机 |
|------|------|----------|----------|----------|
| **L1** | claude-mem | 会话记忆、工具输出 | 单次会话 | PostToolUse |
| **L2** | archive | 决策、模式、发现 | 跨会话 | 手动/自动识别 |
| **L3** | lessons.md | 经验教训、最佳实践 | 永久 | 用户纠正/三次失败 |

### 自动归档识别规则

以下内容自动触发归档提示：

| 类型 | 识别关键词 | 示例 |
|------|----------|------|
| **架构决策** | "最终决定"、"选择方案"、"我们采用" | 选择PostgreSQL作为主数据库 |
| **设计模式** | "模式"、"最佳实践"、"封装为" | 统一使用仓储模式访问数据 |
| **关键发现** | "发现"、"原来如此"、"居然" | 发现某个API有速率限制 |
| **代码模式** | "抽象为"、"提取为"、"统一为" | 将日志逻辑抽象为装饰器 |
| **项目特定** | "本项目"、"我们项目"、"这个代码库" | 本项目使用pnpm作为包管理器 |
| **外部依赖** | "依赖"、"需要安装"、"版本" | 项目依赖Python 3.11+ |

### 归档分类体系

```
archive/
├── decisions/              # 架构决策
│   ├── {date}-{slug}.md
│   └── index.json         # 决策索引
├── patterns/              # 代码模式
│   ├── {category}/
│   └── index.json
├── discoveries/            # 关键发现
│   ├── {date}-{slug}.md
│   └── index.json
├── projects/              # 项目知识
│   ├── {project-name}/
│   └── index.json
└── .archive_meta.json     # 元数据
```

### 命令使用

#### 归档管理命令

```bash
# 归档当前会话的关键决策
archive save "决策描述" --type decision --project {project}

# 归档代码模式
archive save "模式描述" --type pattern --category {category}

# 归档关键发现
archive save "发现内容" --type discovery

# 搜索归档
archive search "查询内容" [--type {type}] [--project {project}]

# 列出项目归档
archive list [--project {project}] [--type {type}] [--limit {n}]

# 生成归档摘要
archive summarize [--project {project}] [--days {n}]

# 清理过期归档
archive clean [--before {date}] [--keep {n}]
```

#### 与会话协同

```bash
# 从归档加载上下文到当前会话
archive load --project {project} [--type {type}]

# 检查是否有相关归档
archive check "当前任务描述"
```

### 自动归档触发

在以下情况自动提示归档：

| 触发条件 | 提示时机 |
|----------|----------|
| 会话结束 | 询问"是否归档重要决策？" |
| 重要决策做出 | 立即提示归档 |
| 发现关键代码模式 | 立即提示归档 |
| 项目配置确定 | 立即提示归档 |

### 与现有天龙组件协同

#### 与claude-mem协同

```bash
# 1. claude-mem捕获当前会话
# 2. 会话结束时，archive自动扫描并提示归档
# 3. 用户确认后，归档持久化
```

#### 与lessons.md协同

```bash
# archive归档内容 → lessons.md经验提取
# 当同一错误出现3次时，触发lessons.md记录
```

#### 与advanced-memory-sync协同

```bash
# archive归档 → Obsidian同步 → 知识图谱构建
# 形成完整知识循环
```

### 核心脚本

| 脚本 | 功能 |
|------|------|
| `archive_manager.py` | 归档管理核心脚本 |

### 使用示例

#### 示例1: 归档架构决策

```bash
$ archive save "选择PostgreSQL作为主数据库" \
    --type decision \
    --project myapp \
    --reason "需要事务支持、复杂查询能力强"

# 生成的归档文件:
# archive/decisions/2026-04-23-postgresql-selection.md
```

#### 示例2: 归档代码模式

```bash
$ archive save "统一使用仓储模式" \
    --type pattern \
    --category architecture \
    --project myapp

# 生成的归档文件:
# archive/patterns/architecture/2026-04-23-repository-pattern.md
```

#### 示例3: 搜索归档

```bash
$ archive search "数据库选择"

# 输出:
# - [decision] 2026-04-23: PostgreSQL作为主数据库 (项目: myapp)
# - [pattern] 2026-04-20: 数据访问层抽象 (项目: myapp)
# - [discovery] 2026-04-15: Redis比Memcached更适合会话 (项目: myapp)
```

#### 示例4: 生成项目摘要

```bash
$ archive summarize --project myapp --days 30

# 输出:
# 项目 myapp 近30天归档摘要:
# - 3个架构决策
# - 5个代码模式
# - 8个关键发现
# 最近更新: 2026-04-23
```

### 触发钩子配置

建议在 `hooks.json` 中添加archive钩子:

```json
{
  "hooks": {
    "postToolUse": [
      "./archive-hook.js"
    ],
    "Stop": [
      "./archive-session-end.js"
    ]
  }
}
```

### 元数据Schema

```json
{
  "id": "uuid",
  "type": "decision|pattern|discovery|project",
  "title": "归档标题",
  "content": "归档内容",
  "project": "项目名称",
  "category": "分类",
  "tags": ["标签1", "标签2"],
  "created": "ISO8601时间",
  "updated": "ISO8601时间",
  "access_count": 0,
  "last_accessed": null,
  "related": ["相关归档ID列表"],
  "confidence": 0.8,
  "status": "active|archived|stale"
}
```

### 设计理念

1. **知识复利**: 归档的知识应被未来会话检索和应用
2. **自动识别**: 系统自动识别值得归档的内容，而非完全依赖用户
3. **轻量优先**: 归档应简洁，详细信息存储在外部引用中
4. **可检索**: 所有归档可通过多种维度检索
5. **协同而非重复**: 与claude-mem、lessons.md形成互补

### 版本信息

- **版本**: 1.0.0
- **创建日期**: 2026-04-23
- **基于**: archive知识管理系统最佳实践
