---
license: UNKNOWN
triggers: ["skill manager core", "skill-manager-core"]
---
# skill-manager-core

## L0: 一句话描述 (≤15字)
AI编码Agent Skills多平台统一管理中心

## L1: 使用场景 (50-100字)
当需要管理分布在多个AI编码平台的Skills时使用，如Claude Code/Cursor/VS Code等平台的Skills同步、批量安装、版本治理。本Skill提供27个平台的统一管理能力，支持中心化存储和符号链接同步。

## L2: 详细文档

### 核心能力

| 能力 | 功能 | 命令 |
|------|------|------|
| **平台检测** | 自动检测已安装的AI编码平台 | `skill-manager detect` |
| **平台管理** | 列出/添加/删除平台配置 | `skill-manager platform list/add/remove` |
| **符号链接** | 创建/删除跨平台符号链接 | `skill-manager symlink create/remove` |
| **集合管理** | 创建Skills集合并批量安装 | `skill-manager collection list/create/delete` |
| **搜索索引** | 大库虚拟化搜索+懒加载 | `skill-manager search --query` |

### 支持平台 (27个)

#### Coding平台
```bash
~/.claude/skills/       # Claude Code
~/.agents/skills/        # Codex CLI
~/.cursor/skills/        # Cursor
~/.gemini/skills/        # Gemini CLI
~/.trae/skills/          # Trae
~/.factory/skills/        # Factory Droid
~/.junie/skills/         # Junie
~/.qwen/skills/          # Qwen
~/.trae-cn/skills/       # Trae CN
~/.windsurf/skills/      # Windsurf
~/.qoder/skills/         # Qoder
~/.augment/skills/       # Augment
~/.opencode/skills/      # OpenCode
~/.kilocode/skills/      # KiloCode
~/.ob1/skills/           # OB1
~/.amp/skills/           # Amp
~/.kiro/skills/          # Kiro
~/.codebuddy/skills/     # CodeBuddy
~/.hermes/skills/        # Hermes
~/.copilot/skills/       # Copilot
~/.aider/skills/         # Aider
```

#### Lobster平台 (开爪系列)
```bash
~/.openclaw/skills/      # OpenClaw (开爪)
~/.qclaw/skills/         # QClaw (千爪)
~/.easyclaw/skills/      # EasyClaw (简爪)
~/.workbuddy/skills/     # WorkBuddy (打工搭子)
```

#### Central (中心库)
```bash
~/.agents/skills/        # Central Skills (~/.agents/skills/)
```

### 目录结构

```
skill-manager-core/
├── SKILL.md                    # 本文件
├── scripts/
│   ├── platform-detector.sh    # 平台检测脚本
│   ├── symlink-manager.sh      # 符号链接管理
│   ├── collection-manager.sh    # 集合管理
│   └── search-indexer.sh       # 搜索索引
├── lib/
│   ├── platforms.json           # 27平台配置
│   └── index.db                # SQLite索引 (按需创建)
└── templates/
    └── collection-template.md  # 集合模板
```

### 使用示例

#### 1. 检测已安装平台
```bash
bash ~/.claude/skills/skill-manager-core/scripts/platform-detector.sh detect
# 输出: Claude Code ✓, Cursor ✓, VS Code ✗, ...
```

#### 2. 创建跨平台符号链接
```bash
bash ~/.claude/skills/skill-manager-core/scripts/symlink-manager.sh link \
  --skill ~/.claude/skills/my-skill \
  --platforms claude,cursor,trae
# 输出: ~/.agents/skills/my-skill -> ~/.claude/skills/my-skill
#       ~/.cursor/skills/my-skill -> ~/.claude/skills/my-skill
```

#### 3. 创建Skills集合
```bash
bash ~/.claude/skills/skill-manager-core/scripts/collection-manager.sh create \
  --name "data-analysis" \
  --skills "pandas-skill,sql-skill,visualization-skill"
# 输出: Collection 'data-analysis' 创建成功，包含3个Skills
```

#### 4. 批量安装到平台
```bash
bash ~/.claude/skills/skill-manager-core/scripts/collection-manager.sh install \
  --collection "data-analysis" \
  --platforms claude,cursor
# 输出: 安装进度: [1/3] pandas-skill ✓
#                    [2/3] sql-skill ✓
#                    [3/3] visualization-skill ✓
```

#### 5. 搜索Skills
```bash
bash ~/.claude/skills/skill-manager-core/scripts/search-indexer.sh \
  --query "data analysis" \
  --platforms claude,cursor \
  --limit 10
# 输出: 1. pandas-skill (相似度: 0.95)
#       2. numpy-skill (相似度: 0.82)
```

### 架构设计

```bash
┌─────────────────────────────────────────────────────────────┐
│              Skills Manager Core Architecture                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │   Central   │    │  Platform  │    │ Collection  │ │
│  │   Skills    │◄──►│   Detect   │◄──►│   Manager   │ │
│  │   (~/.agents│    │            │    │             │ │
│  └─────────────┘    └─────────────┘    └─────────────┘ │
│         │                  │                  │           │
│         ▼                  ▼                  ▼           │
│  ┌─────────────────────────────────────────────────┐     │
│  │              Symlink Manager                      │     │
│  │    符号链接 ↔ 跨平台同步 ↔ 版本治理          │     │
│  └─────────────────────────────────────────────────┘     │
│                           │                             │
│                           ▼                             │
│  ┌─────────────────────────────────────────────────┐     │
│  │              Search Index                        │     │
│  │    懒加载 ↔ 虚拟化 ↔ SQLite索引             │     │
│  └─────────────────────────────────────────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 与天龙引擎协同

| 天龙组件 | 协同方式 | 效果 |
|---------|---------|------|
| **09-02 编排协调师** | Skills多平台编排 | 跨平台Skills统一调度 |
| **09-06 Skills管理员** | 全生命周期管理 | Skills治理闭环 |
| **07 记录师** | Skills归档 | 知识库结构化管理 |
| **08 发布师** | Skills发布 | 多平台同步发布 |

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `SKILL_MANAGER_HOME` | 中心Skills目录 | `~/.agents/skills/` |
| `SKILL_MANAGER_INDEX` | 索引数据库 | `~/.skillsmanage/index.db` |
| `SKILL_MANAGER_PLATFORMS` | 启用平台列表 | 全部27平台 |

### 数据库Schema (SQLite)

```sql
CREATE TABLE skills (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    path TEXT NOT NULL,
    platform TEXT,
    collection_id TEXT,
    created_at TEXT,
    updated_at TEXT,
    metadata TEXT  -- JSON格式额外信息
);

CREATE TABLE collections (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TEXT
);

CREATE TABLE platforms (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    path TEXT NOT NULL,
    enabled INTEGER DEFAULT 1,
    last_sync TEXT
);

CREATE INDEX idx_skills_name ON skills(name);
CREATE INDEX idx_skills_platform ON skills(platform);
CREATE INDEX idx_skills_collection ON skills(collection_id);
```

### 错误处理

| 错误码 | 说明 | 处理建议 |
|--------|------|---------|
| `E_NOPLATFORM` | 平台未检测到 | 检查平台是否安装 |
| `E_NOSKILL` | Skill不存在 | 检查路径或先安装 |
| `E_LINKFAIL` | 符号链接失败 | 检查权限或路径冲突 |
| `E_DUP_SKILL` | Skill重复安装 | 使用 `--force` 覆盖 |
| `E_DBERROR` | 数据库错误 | 重建索引 `skill-manager rebuild-index` |

### 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-02 | 初始集成，27平台支持 |

---

## 命令速查

```bash
# 平台管理
skill-manager detect                    # 检测已安装平台
skill-manager platform list            # 列出所有平台
skill-manager platform add <name> <path>  # 添加平台
skill-manager platform remove <name>   # 删除平台

# 符号链接
skill-manager link <skill> --platforms <list>   # 创建链接
skill-manager unlink <skill> --platforms <list> # 删除链接
skill-manager sync                         # 同步所有链接

# 集合管理
skill-manager collection list           # 列出集合
skill-manager collection create <name>   # 创建集合
skill-manager collection add <col> <skill>  # 添加到集合
skill-manager collection install <col> --platforms <list>  # 批量安装

# 搜索
skill-manager search <query>           # 搜索Skills
skill-manager rebuild-index            # 重建索引

# 状态
skill-manager status                   # 查看整体状态
skill-manager stats                    # 查看统计信息
```
