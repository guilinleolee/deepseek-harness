---
license: MIT
title: "Skills Administrator"
description: "Multi-platform Skills management, collection orchestration, cross-platform synchronization, and pre-release context_audit gate (V1.1 stage 26)"
version: "1.1.0"
tags: ["skills-admin", "collection-manager", "multi-platform", "symlink-manager", "search-indexer", "context-audit-gate"]
platforms: ["claude", "cursor", "codex", "gemini", "trae", "windsurf", "openclaw", "qclaw", "easyclaw", "workbuddy"]
created: "2026-05-02"
updated: "2026-08-23"
triggers: ["Skills Administrator (09-06)", "skills admin V1.1", "上线前 audit 门禁"]
upstream:
  - V1.0 (2026-05-02 · 27 平台 Skills 全生命周期管理)
downstream:
  - 40-01-context-curator V1.0 (天龙阶段 26 · 2026-08-23 新增 · 提供 audit 能力)
  - 09-03-meta-reviewer (PR 评审必跑 audit)
  - mneme-heat-engine V1.0 (天龙阶段 41 · 2026-08-24 · skills heat 治理协同 · 借鉴 dsh-mneme MIT)
stage: 26
---

# Skills Administrator (09-06) · V1.1

> **版本**：V1.1（2026-08-23）
> **上版**：V1.0（2026-05-02）
> **核心升级**：**V1.1 = V1.0 + 上线前 `context_audit` 门禁**（context-doctor 协同 · 阶段 26 增量）

---

## V1.1 增量：上线前 context_audit 门禁（⭐阶段 26 新增）

### 来源

- 上游：`Zhenyu98/dsh-context-doctor` v0.6.1（BSD-3-Clause ✅）
- 协同岗位：40-01 Context Curator V1.0（提供 audit 数据 + 5 步工作流）

### 核心价值

将 09-06 从"27 平台 Skills 全生命周期管理员"扩展为"**带 context 健康门禁的 Skills 管理员**"——任何新 skill 入库前必须跑 `context_audit`，通过 4 项检查才能入库，**从源头遏制 catalog 膨胀**。

### V1.1 4 项上线前检查（缺一不可）

| # | 检查项 | 触发条件 | 严重度 | 通过条件 |
|---|--------|----------|--------|----------|
| 1 | **catalog 描述 token 增量** | 新 skill 加入后 catalog 总 token | **high** | 增量 ≤ 200 token（单个 skill 上限）|
| 2 | **catalog 总 token 阈值** | 加入新 skill 后 | medium | catalog 总 ≤ 3000 token |
| 3 | **同名 skill shadow 冲突** | 新 skill 与已有 skill 同名 | medium | 优先级 ≥ 被 shadow 者，否则拒绝入库 |
| 4 | **description 与已有重复** | 新 description 与已有 description 完全相同 | medium | 重复率 < 80%（允许少量通用描述）|

### V1.1 上线门禁流程（嵌入 collection add）

```bash
# 原 V1.0 命令
collection add <name> <skill>

# V1.1 新增（自动触发）
collection add <name> <skill>
  └─→ pre-release audit hook
       ├─→ 调 context_audit（detail=summary）
       ├─→ 计算新 skill 加入后的 4 项指标
       ├─→ 4 项全部 PASS → 入库
       └─→ 任一 FAIL → 拒绝入库 + 输出"上线风险评估报告"
```

### 4 项检查的 PASS/FAIL 判定

```python
def pre_release_gate(new_skill, current_audit):
    issues = []

    # 1. catalog 描述 token 增量
    delta = estimate_tokens(new_skill.description)
    if delta > 200:
        issues.append(f"[high] description 过长 ({delta} tokens，建议 ≤ 200)")

    # 2. catalog 总 token 阈值
    new_total = current_audit.skills.catalogDescriptionTokens + delta
    if new_total > 3000:
        issues.append(f"[medium] catalog 总 token 预警 ({new_total}/3000)")

    # 3. 同名 skill shadow
    for existing in current_audit.skills.bySource:
        if existing.name == new_skill.name:
            winner_rank = rankOfSource(existing.source)
            new_rank = rankOfSource(new_skill.source)
            if new_rank >= winner_rank:
                issues.append(f"[medium] 同名 shadow 风险：{existing.source} ({winner_rank}) 胜出，新 skill 不会被加载")

    # 4. description 重复
    for dup in current_audit.skills.duplicateDescriptions:
        if new_skill.description == dup.description:
            issues.append(f"[medium] description 与已有 skill「{dup.name}」完全相同")

    return issues  # 空数组 = PASS
```

### V1.1 与 V1.0 的关系

| 维度 | V1.0 | V1.1 增量 |
|------|------|----------|
| 27 平台 Skills 全生命周期 | ✅ | ✅ 不变 |
| 集合编排 + 符号链接同步 | ✅ | ✅ 不变 |
| 跨平台安装（claude/cursor/trae...）| ✅ | ✅ 不变 |
| 索引数据库管理 | ✅ | ✅ 不变 |
| **上线前 context_audit 门禁** | ❌ | ✅ **新增** |
| **与 40-01 自动协同** | ❌ | ✅ **新增** |

### Don't 护栏（V1.1 新增 5 条）

1. ❌ **不要让 catalog 涨破 3000 token**——超 3000 拒绝所有新 skill 入库（需先裁剪）
2. ❌ **不要让单 skill description 超 200 token**——超过必触发 high 告警
3. ❌ **不要新增与 bundled skill 同名的新 skill**——除非 source 优先级更高（project-dsh > bundled）
4. ❌ **不要把 audit JSON 落到 git**——只落 `~/.dsh/audit/`，加 `.gitignore`
5. ❌ **不要在 headless 模式下自动跑 detail=developer**——只在 staging 跑

### 关键调用模板（DSH 模型提示词）

```
我准备发布新 skill「[skill_name]」，请运行 context_audit（detail=summary），
按 V1.1 4 项上线前检查评估：
1. 新 skill description token 增量（应 ≤ 200）
2. catalog 总 token 是否会突破 3000
3. 是否会触发同名 shadow 冲突
4. description 是否与已有 skill 完全相同
输出"上线风险评估"：通过 / 有条件通过 / 不通过。
```

---

# Skills Administrator (09-06) · V1.0 既有能力

## L0: 一句话描述
27平台Skills全生命周期管理员，负责集合编排、符号链接同步与索引管理。

## L1: 使用场景

### 适用场景
- **跨平台部署**：将Skills同步到多个平台（claude/cursor/trae等）
- **集合管理**：创建、管理、打包Skills集合供批量安装
- **索引维护**：保持技能库索引最新，支持快速搜索
- **版本控制**：跟踪Skills版本，确保平台间一致性
- **增量更新**：新增/更新Skills时自动同步到所有目标平台

### 核心功能
| 功能 | 命令 | 说明 |
|------|------|------|
| 列出集合 | `collection list` | 显示所有已创建的集合 |
| 创建集合 | `collection create <name>` | 创建新的Skills集合 |
| 删除集合 | `collection delete <name>` | 删除指定集合 |
| 添加Skill | `collection add <name> <skill>` | 向集合添加Skills |
| 安装集合 | `collection install <name> --platforms claude,cursor` | 同步到目标平台 |
| 扫描Skills | `discover-skills scan --all` | 发现所有平台的Skills |
| 列出Skills | `discover-skills list` | 列出已发现的Skills |
| 审计结构 | `discover-skills audit --platforms claude` | 审计Skills质量 |
| 统计信息 | `discover-skills stats` | 显示发现统计 |

### 快速开始
```bash
# 扫描所有平台Skills
discover-skills scan --all

# 创建集合
collection create my-tools --skills "api-design,python-patterns,testing-patterns"

# 安装到多个平台
collection install my-tools --platforms claude,cursor,trae

# 查看统计
discover-skills stats
```

## L2: 详细文档

### 架构设计

```
┌─────────────────────────────────────────────────────────────────────┐
│              Skills Administrator 架构                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  中心存储 (Central)                                                  │
│  ~/.agents/skills/                                                  │
│       │                                                             │
│       ├── api-design/                                               │
│       ├── python-patterns/                                          │
│       ├── testing-patterns/                                         │
│       └── ...                                                       │
│                                                                     │
│  跨平台同步 (Symlinks)                                              │
│       │                                                             │
│       ├── ~/.claude/skills/ → 符号链接 → 中心                       │
│       ├── ~/.cursor/skills/ → 符号链接 → 中心                       │
│       ├── ~/.trae/skills/ → 符号链接 → 中心                         │
│       └── ~/.windsurf/skills/ → 符号链接 → 中心                      │
│                                                                     │
│  索引数据库 (SQLite)                                                 │
│  ~/.skillsmanage/index.db                                           │
│       ├── collections表 → 集合配置                                  │
│       ├── collection_skills表 → 集合成员                            │
│       └── discovered_skills表 → 发现记录                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 数据库表结构

```sql
-- 集合表
CREATE TABLE collections (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  description TEXT,
  skill_list TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 集合成员表
CREATE TABLE collection_skills (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  collection_id TEXT NOT NULL,
  skill_name TEXT NOT NULL,
  skill_path TEXT,
  FOREIGN KEY (collection_id) REFERENCES collections(id),
  UNIQUE(collection_id, skill_name)
);

-- 发现记录表
CREATE TABLE discovered_skills (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  platform TEXT NOT NULL,
  path TEXT NOT NULL,
  title TEXT,
  description TEXT,
  tags TEXT,
  version TEXT,
  has_skill_md INTEGER DEFAULT 0,
  discovered_at TEXT DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(platform, name)
);
```

### 平台配置 (platforms.json)

```json
{
  "platforms": {
    "coding": {
      "description": "AI Coding Platforms",
      "items": [
        {"id": "claude", "name": "Claude Code", "path": "~/.claude/skills"},
        {"id": "cursor", "name": "Cursor", "path": "~/.cursor/skills"},
        {"id": "trae", "name": "Trae", "path": "~/.trae/skills"},
        {"id": "windsurf", "name": "Windsurf", "path": "~/.windsurf/skills"},
        {"id": "codex", "name": "Codex CLI", "path": "~/.codex/skills"},
        {"id": "gemini", "name": "Gemini CLI", "path": "~/.gemini/skills"}
        // ... 24个coding平台
      ]
    },
    "lobster": {
      "description": "Lobster Series",
      "items": [
        {"id": "openclaw", "name": "OpenClaw", "path": "~/.openclaw/skills"},
        {"id": "qclaw", "name": "QClaw", "path": "~/.qclaw/skills"},
        {"id": "easyclaw", "name": "EasyClaw", "path": "~/.easyclaw/skills"},
        {"id": "workbuddy", "name": "WorkBuddy", "path": "~/.workbuddy/skills"}
      ]
    }
  },
  "defaults": {
    "central_path": "~/.agents/skills",
    "db_path": "~/.skillsmanage/index.db"
  }
}
```

### 核心命令详解

#### collection create - 创建集合
```bash
# 基本创建
collection create my-tools --description "开发工具集"

# 创建时指定Skills
collection create fullstack --skills "api-design,database-migrations,testing-patterns"
```

#### collection add - 添加Skill到集合
```bash
# 添加单个Skill
collection add my-tools python-patterns

# 添加多个Skills
collection add my-tools api-design,golang-patterns
```

#### collection install - 安装到平台
```bash
# 安装到单个平台
collection install my-tools --platforms claude

# 安装到多个平台
collection install my-tools --platforms claude,cursor,trae

# 安装到全部平台
collection install my-tools --platforms all
```

### 符号链接策略

```bash
# 中心存储位置
CENTRAL_PATH=~/.agents/skills

# 平台存储位置
PLATFORM_PATH=~/.{platform}/skills

# 创建符号链接
ln -sf ${CENTRAL_PATH}/${skill_name} ${PLATFORM_PATH}/${skill_name}
```

### 工作流程

```
┌─────────────────────────────────────────────────────────────┐
│                  Skills管理工作流                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 扫描发现 (discover-skills scan --all)                 │
│     └── 更新 discovered_skills 表                           │
│                    ↓                                       │
│  2. 集合创建 (collection create)                          │
│     └── 写入 collections 表                                │
│                    ↓                                       │
│  3. 成员添加 (collection add)                             │
│     └── 写入 collection_skills 表                        │
│                    ↓                                       │
│  4. 跨平台安装 (collection install)                      │
│     └── 创建符号链接到各平台                              │
│                    ↓                                       │
│  5. 验证同步 (discover-skills audit)                     │
│     └── 确认所有平台已正确安装                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 与其他组件集成

| 组件 | 集成方式 |
|------|---------|
| skill-manager-core | 共用 platforms.json 配置 |
| skill-discovery-scanner | 共享 discovered_skills 表 |
| symlink-manager.sh | 共享符号链接逻辑 |
| search-indexer.sh | 共享 index.db 数据库 |

### 故障排除

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 安装失败 | 目录不存在 | 使用 mkdir -p 创建目标目录 |
| 链接已存在 | Skill已安装 | 使用 --force 覆盖 |
| 找不到Skill | Central路径错误 | 检查 ~/.agents/skills 是否存在 |
| 权限错误 | 目录不可写 | 使用 sudo 或更改权限 |
| 数据库锁定 | 多进程冲突 | 使用 sqlite3 --exclusive |

### 扩展开发

添加新的安装策略到 `install_collection()` 函数：

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

---

## 版本历史

| 版本 | 日期 | 核心更新 |
|------|------|---------|
| **V1.1** | 2026-08-23 | 上线前 `context_audit` 门禁（context-doctor 协同 · 阶段 26 增量）|
| **V1.0** | 2026-05-02 | 27 平台 Skills 全生命周期管理（集合编排 + 符号链接同步 + 索引管理）|

---

**版本**: V1.1
**最后更新**: 2026-08-23
**核心升级**: V1.0 + 上线前 audit 门禁（4 项检查：catalog 增量 / 总阈值 / shadow 冲突 / description 重复）
**协同**: 40-01 Context Curator V1.0 + dsh-context-doctor v0.6.1 (BSD-3-Clause)

---

## V1.2 候选增量 · mneme-gate 协同（⭐阶段 41 · 2026-08-24 · 借鉴 dsh-mneme MIT）

> **策略**：最小入侵 —— 09-06 V1.1 已稳态，不重写文档，仅在 downstream 字段加 mneme-heat-engine 依赖 + 新增 4 项 skill heat 治理职责。

### V1.2 新增职责（mneme-gate）

| # | 职责 | 触发条件 | 与 V1.1 关系 |
|---|------|----------|---------------|
| 1 | **每个 skill 注册时初始化 heat=0.7** | skill 入 catalog 时 | 补充 V1.1 上线门禁 |
| 2 | **每日 tick：未触发 skill heat × 0.99** | cron 每日 03:00 | 与 V1.1 audit 互补 |
| 3 | **30 天未触发 → cold 标记** | 命令面板提示"低频" | 与 V1.1 context_audit 共享指标 |
| 4 | **60 天未触发 → 候选退役** | archive/skills/ | 比 V1.1 审计更严 |

### V1.2 不改变

- ❌ 不重写 4 项 context_audit 门禁
- ❌ 不改 27 平台管理范围
- ❌ 不动 collection add 流程

详见：[mneme-integration.md](../memory/mneme-integration.md) + [skills/mneme-heat-engine/](../skills/mneme-heat-engine/)