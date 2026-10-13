---
license: UNKNOWN
name: skill-collection-manager
description: 跨27平台Skills集合管理 - 一键安装与同步，支持collection命令族和符号链接策略
version: "1.0.0"
created: "2026-05-02"
tags: ["Skills管理", "跨平台", "集合安装", "符号链接", "09-06-Skills管理员"]
platforms: ["claude", "cursor", "codex", "gemini", "trae", "windsurf"]
source: "custom"
天龙岗位: ["09-06-Skills管理员"]
triggers: ["skill collection manager", "Skill Collection Manager"]
---

# Skill Collection Manager

## L0: 一句话描述
跨27平台Skills集合管理、一键安装与同步工具。

## L1: 使用场景

### 适用场景
- **批量安装**：将一组Skills同时安装到多个平台
- **版本同步**：保持跨平台Skills版本一致性
- **快速部署**：新平台快速配置常用Skills集合
- **集合管理**：创建、管理、分享Skills打包

### 核心功能
| 功能 | 命令 | 说明 |
|------|------|------|
| 列出集合 | `collection list` | 列出所有已创建的集合 |
| 创建集合 | `collection create` | 创建新的Skills集合 |
| 删除集合 | `collection delete` | 删除指定集合 |
| 添加Skill | `collection add` | 向集合添加Skills |
| 安装集合 | `collection install` | 将集合安装到指定平台 |
| 生成文档 | `collection export` | 导出集合说明文档 |

### 快速开始
```bash
# 创建集合
collection create my-tools --skills "data-analysis,web-scraper,api-design"

# 向集合添加Skill
collection add my-tools another-skill

# 安装到多个平台
collection install my-tools --platforms claude,cursor,trae

# 列出所有集合
collection list

# 删除集合
collection delete my-tools
```

## L2: 详细文档

### 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│ skill-collection-manager 架构                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  collections.db ──► collection-manager.sh ──► symlinks       │
│  (SQLite)          (管理脚本)          (跨平台安装)         │
│       │                  │                  │                   │
│       ▼                  ▼                  ▼                   │
│  collections表        CRUD操作           ~/.{platform}/skills │
│  collection_skills表  集合操作          ~/.claude/skills     │
│                       安装操作          ~/.cursor/skills       │
│                                         ...                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 数据库表结构

```sql
CREATE TABLE collections (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  description TEXT,
  skill_list TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE collection_skills (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  collection_id TEXT NOT NULL,
  skill_name TEXT NOT NULL,
  skill_path TEXT,
  FOREIGN KEY (collection_id) REFERENCES collections(id),
  UNIQUE(collection_id, skill_name)
);
```

### 配置文件

**platforms.json** 关键配置：

```json
{
  "defaults": {
    "central_path": "~/.agents/skills",
    "db_path": "~/.skillsmanage/index.db"
  }
}
```

### 安装流程

```
┌─────────────────────────────────────────────────────────────┐
│ 集合安装流程                                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 读取集合配置                                           │
│     └── 从数据库获取 skill_list                             │
│                    ↓                                       │
│  2. 解析平台列表                                           │
│     └── 解析 --platforms 参数                              │
│                    ↓                                       │
│  3. 遍历每个平台                                           │
│     ├── 展开 ~ 为实际路径                                  │
│     ├── 创建目标目录                                       │
│     └── 创建符号链接 (central → platform)                  │
│                    ↓                                       │
│  4. 输出安装结果                                           │
│     └── 成功数 / 失败数                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 核心命令详解

#### list - 列出所有集合

```bash
# 列出所有集合
collection list

# 示例输出:
# ┌─────────────────┬────────────────────────────────────┐
# │ Collection       │ Skills                             │
# ├─────────────────┼────────────────────────────────────┤
# │ dev-tools        │ python-dev, api-design, testing   │
# │ data-analysis    │ pandas, visualization, ml-basics  │
# └─────────────────┴────────────────────────────────────┘
```

#### create - 创建新集合

```bash
# 基本创建
collection create dev-tools --description "开发工具集"

# 创建时指定Skills
collection create my-stack \
  --skills "api-design,database-migrations,testing-patterns" \
  --description "全栈开发必备Skills"
```

#### add - 添加Skill到集合

```bash
# 添加单个Skill
collection add dev-tools git-workflow

# 添加多个Skills
collection add dev-tools python-patterns,golang-patterns
```

#### install - 安装到平台

```bash
# 安装到单个平台
collection install dev-tools --platforms claude

# 安装到多个平台
collection install dev-tools --platforms claude,cursor,trae

# 安装到全部平台(危险!)
collection install dev-tools --platforms all

# 使用配置文件
collection install dev-tools --config platforms.json
```

#### delete - 删除集合

```bash
# 删除集合(不会删除已安装的Skills)
collection delete old-collection

# 强制删除(同时清理符号链接)
collection delete old-collection --force
```

### 符号链接策略

```bash
# 中心存储位置
CENTRAL_PATH=~/.agents/skills

# 平台存储位置
PLATFORM_PATH=~/.{platform}/skills

# 链接创建
ln -sf ${CENTRAL_PATH}/${skill_name} ${PLATFORM_PATH}/${skill_name}
```

### 与其他组件集成

| 组件 | 集成方式 |
|------|---------|
| skill-manager-core | 共用platforms.json配置 |
| skill-discovery-scanner | 发现Skills → 添加到集合 |
| symlink-manager.sh | 共享符号链接逻辑 |
| search-indexer.sh | 共享index.db数据库 |

### 故障排除

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 安装失败 | 目录不存在 | 使用 mkdir -p 创建目标目录 |
| 链接已存在 | Skill已安装 | 使用 --force 覆盖 |
| 找不到Skill | Central路径错误 | 检查 ~/.agents/skills 是否存在 |
| 权限错误 | 目录不可写 | 使用 sudo 或更改权限 |

### 扩展开发

添加新的安装策略到 `install_collection()` 函数:

```bash
# 示例: 添加 rsync 备份策略
install_with_backup() {
  local collection="$1"
  local platform="$2"

  # 先备份
  rsync -av ${PLATFORM_PATH}/ ${BACKUP_DIR}/

  # 然后安装
  install_collection "$collection" "$platform"
}
```

---

*Generated by skill-manager-core*