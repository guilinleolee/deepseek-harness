---
license: UNKNOWN
github_repo: daxiangnaoyang/openclaw-advanced-memory
github_hash: 9f346bade231755f2bf0b3d958215c01172519c1
last_updated: 2026-04-25
source_type: derived
triggers: ["advanced memory sync", "advanced-memory-sync"]
---
# advanced-memory-sync

> 分层记忆自动同步到Obsidian，打造AI第二大脑
>
> 整合自 [openclaw-advanced-memory](https://github.com/daxiangnaoyang/openclaw-advanced-memory) 的核心思想

## 核心功能

| 功能 | 描述 | 技术实现 |
|------|------|---------|
| **分层同步** | L0-L3四层记忆自动同步到Obsidian | SQLite + fs模块 |
| **定时同步** | 每15分钟自动同步核心洞察 | setInterval调度 |
| **对话树** | 分支可视化与管理 | Git-like数据结构 |
| **知识图谱** | 生成交互式知识网络 | graph.json |
| **智能压缩** | Token限制下的上下文优化 | AI摘要 + 截断 |

## 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                    天龙记忆系统                               │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐  │
│  │  claude-mem │ ──▶ │ advanced-   │ ──▶ │   Obsidian  │  │
│  │  (存储层)   │     │ memory-sync │     │   (展示层)  │  │
│  └─────────────┘     └─────────────┘     └─────────────┘  │
│         │                   │                   │         │
│         ▼                   ▼                   ▼         │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐  │
│  │ L0:原始记录 │     │ L1:关键点  │     │ L2:结构化  │  │
│  │ L3:核心洞察 │     │ (70%压缩)  │     │ (90%压缩)  │  │
│  └─────────────┘     └─────────────┘     └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 四层记忆架构

| 层级 | 内容 | 压缩率 | 保留方式 | 同步频率 |
|------|------|--------|---------|---------|
| **L0** | 完整原始对话 | 0% | 永远保留 | 不同步 |
| **L1** | 关键句子提取 | 70% | 实时更新 | 每小时 |
| **L2** | 结构化JSON知识 | 90% | 按需检索 | 每日 |
| **L3** | 核心洞察提炼 | 95% | 永远保留 | 每15分钟 |

## Obsidian目录结构

```
{VAULT_PATH}/
├── _系统概览.md                    # 系统状态摘要
├── 核心记忆/                        # L3层洞察
│   ├── {date}-insights.md         # 每日洞察
│   └── {topic}-insights.md        # 主题洞察
├── 结构化知识/                      # L2层知识
│   ├── 技术/                       # 技术知识
│   ├── 业务/                       # 业务知识
│   └── 项目/                       # 项目知识
├── 关键点/                         # L1层关键点
│   └── {date}-keypoints.md        # 每日关键点
├── 对话树/                         # 分支可视化
│   ├── main.md                     # 主线对话
│   └── {branch}/                   # 分支对话
│       ├── conversation.md
│       └── notes.md
└── 知识图谱/
    └── graph.json                  # 实体关系图谱
```

## 同步策略

### 智能上下文组合

```javascript
const CONTEXT_RATIO = {
  L3: 0.3,  // 30% 核心洞察
  L2: 0.4,  // 40% 结构化知识
  L1: 0.3,  // 30% 关键点
  // 总计: 限制在 5000 tokens 内
  MAX_TOKENS: 5000
};
```

### 同步调度

| 任务 | 频率 | 说明 |
|------|------|------|
| `syncInsights` | 每15分钟 | L3核心洞察同步 |
| `syncKeyPoints` | 每小时 | L1关键点同步 |
| `syncStructured` | 每日凌晨 | L2结构化知识同步 |
| `syncGraph` | 每日凌晨 | 知识图谱更新 |
| `memoryCompression` | 每日凌晨 | 记忆压缩整理 |
| `decayRecalculation` | 每小时 | 访问频率衰减 |

## 命令使用

### 自动同步

```bash
# 启动同步服务 (后台运行)
python3 ~/.claude/skills/advanced-memory-sync/scripts/sync_service.py start

# 停止同步服务
python3 ~/.claude/skills/advanced-memory-sync/scripts/sync_service.py stop

# 查看同步状态
python3 ~/.claude/skills/advanced-memory-sync/scripts/sync_service.py status
```

### 手动同步

```bash
# 同步全部
python3 ~/.claude/skills/advanced-memory-sync/scripts/sync.py --all

# 仅同步L3洞察
python3 ~/.claude/skills/advanced-memory-sync/scripts/sync.py --level 3

# 指定日期范围
python3 ~/.claude/skills/advanced-memory-sync/scripts/sync.py --start 2026-03-01 --end 2026-03-29

# 同步到指定vault
python3 ~/.claude/skills/advanced-memory-sync/scripts/sync.py --vault "C:/Vault/MyBrain"
```

### 分支管理

```bash
# 创建实验分支
python3 ~/.claude/skills/advanced-memory-sync/scripts/branch.py create "feature-X"

# 切换到分支
python3 ~/.claude/skills/advanced-memory-sync/scripts/branch.py checkout "feature-X"

# 合并分支
python3 ~/.claude/skills/advanced-memory-sync/scripts/branch.py merge "feature-X" --into main

# 查看分支列表
python3 ~/.claude/skills/advanced-memory-sync/scripts/branch.py list

# 分支对比
python3 ~/.claude/skills/advanced-memory-sync/scripts/branch.py diff main feature-X
```

### 知识图谱

```bash
# 更新知识图谱
python3 ~/.claude/skills/advanced-memory-sync/scripts/graph.py update

# 查询关系
python3 ~/.claude/skills/advanced-memory-sync/scripts/graph.py query "AI-Agent"

# 导出可视化
python3 ~/.claude/skills/advanced-memory-sync/scripts/graph.py export --format html
```

## 配置项

### 环境变量

```bash
# Obsidian Vault路径
export OBSIDIAN_VAULT_PATH="C:/Users/li/Documents/Obsidian/Vault"

# 同步频率 (分钟)
export SYNC_INTERVAL=15

# 最大Token限制
export MAX_CONTEXT_TOKENS=5000

# 数据库路径
export MEMORY_DB_PATH="~/.claude/memory.db"
```

### 配置文件

```yaml
# ~/.claude/config/advanced-memory-sync.yaml
sync:
  interval: 15  # 分钟
  max_tokens: 5000
  levels:
    l3: 0.3   # 核心洞察占比
    l2: 0.4   # 结构化知识占比
    l1: 0.3   # 关键点占比

vault:
  path: "C:/Users/li/Documents/Obsidian/Vault"
  auto_create: true
  folders:
    insights: "核心记忆"
    knowledge: "结构化知识"
    keypoints: "关键点"
    tree: "对话树"
    graph: "知识图谱"

decay:
  enabled: true
  factor: 0.9  # 衰减系数
  interval: 3600  # 秒

compression:
  l0_to_l1: 0.7   # 70%保留
  l1_to_l2: 0.9   # 90%压缩
  l2_to_l3: 0.95  # 95%压缩
```

## 与天龙引擎协同

### 协同岗位

| 岗位 | 协同方式 |
|------|---------|
| **07记录师** | 自动将记忆同步到Obsidian可视化 |
| **01调研师** | 调研结果分层存储+知识图谱 |
| **09-02编排协调师** | 分支管理支持实验探索 |
| **claude-mem** | 补充Obsidian同步能力 |

### 协同流程

```
┌─────────────────────────────────────────────────────────────┐
│ 协同流程示例: 调研任务                                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [01调研师] 执行调研                                         │
│       │                                                    │
│       ▼                                                    │
│  [claude-mem] 存储原始记忆                                  │
│       │                                                    │
│       ▼                                                    │
│  [advanced-memory-sync]                                     │
│       ├── L0 → L1: 提取关键点                              │
│       ├── L1 → L2: 结构化知识                              │
│       └── L2 → L3: 提炼洞察                                │
│       │                                                    │
│       ▼                                                    │
│  [Obsidian] 分层可视化                                      │
│       ├── 核心记忆/ → 深度洞察                              │
│       ├── 结构化知识/ → 分类清晰                            │
│       └── 知识图谱/ → 关系网络                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 性能指标

| 指标 | 数值 | 说明 |
|------|------|------|
| **检索速度** | < 200ms | L1缓存命中 |
| **Token节省** | 90% | vs 完整上下文 |
| **同步延迟** | < 5s | 单次同步 |
| **存储效率** | 10x | vs 原始对话 |

## 安装依赖

```bash
# 核心依赖
pip install watchdog  # 文件监控
pip install obsidianmd  # Obsidian API (可选)

# Node.js依赖 (可选Redis)
npm install better-sqlite3
npm install redis
```

## 故障排除

| 问题 | 解决方案 |
|------|---------|
| 同步失败 | 检查Vault路径权限 |
| Token超限 | 调低压缩率或增加MAX_TOKENS |
| Obsidian卡顿 | 减少同步频率或关闭实时同步 |
| 分支冲突 | 使用`branch.py merge --resolve` |

## 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| V1.0 | 2026-03-29 | 初始版本，整合自openclaw-advanced-memory思想 |

---

**Skill来源**: 整合自 [daxiangnaoyang/openclaw-advanced-memory](https://github.com/daxiangnaoyang/openclaw-advanced-memory)
**整合者**: 天龙引擎 01-调研师
**整合日期**: 2026-03-29
