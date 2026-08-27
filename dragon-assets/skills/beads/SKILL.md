---
license: UNKNOWN
triggers: ["beads", "beads — AI-Native Git-Backed Issue Tracker"]
---
# beads — AI-Native Git-Backed Issue Tracker

> **Role**: Unified task entry point for 天龙引擎 V9.06+
> **Version**: 1.0.0 | **Created**: 2026-04-28 | **Source**: [steveyegge/beads](https://github.com/steveyegge/beads)
> **Install**: `bd --help` | **Status**: OPERATIONAL

## L0: 一句话

bd 是天龙引擎的统一任务入口 — Git 原生 Issue 追踪器，以 Dolt 嵌入式数据库为后端，支持 AI Agent 全生命周期任务管理。

## L1: 核心价值

```
┌─────────────────────────────────────────────────────────────┐
│ 天龙引擎任务追踪三层架构                                       │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: beads (V9.06 ⭐ NEW)                           │
│    → Git 原生 Issue 追踪，Dolt 嵌入式数据库               │
│    → 与 git commit 自动同步，支持分支管理                   │
│    → ~88 条命令覆盖全生命周期                               │
│                                                             │
│  Layer 2: paperclip-ticket (V8.36)                       │
│    → 事件驱动任务持久化                                     │
│    → 与 paperclip-heartbeat/cost-control/governance 协同   │
│                                                             │
│  Layer 1: TodoWrite / Agent Task Tracking                │
│    → 会话内任务追踪（短期）                                │
└─────────────────────────────────────────────────────────────┘
```

### 与 paperclip-ticket 数据模型映射

| paperclip-ticket (11字段) | beads 字段 | 备注 |
|--------------------------|-----------|------|
| `id` | `id` (自动生成) | 格式: `dragon-N` |
| `title` | `title` | |
| `description` | `description` / `--body` | |
| `status` | `state` (backlog/todo/in-progress/review/done/cancelled) | beads 状态更丰富 |
| `priority` | `--priority` (lowest/low/medium/high/highest/critical) | 6级 vs 4级 |
| `assigneeAgentId` | `--assignee` | |
| `startedAt` | `--started` | |
| `completedAt` | `--closed` | |
| `createdAt` | auto | |
| `updatedAt` | auto | |
| `executionLockedAt` | `bd gate` | beads 独有：任务门控 |
| `companyId` | `bd context` (multi-repo) | beads 支持多 Repo |

### 升级路径

```
paperclip-ticket (会话层) → beads (持久层) → git commit (归档层)
     ↓                        ↓                    ↓
  当前会话追踪           跨会话持久化           版本控制
```

## L2: 核心命令速查

### 统一入口（每个会话必须运行）

```bash
bd ready              # 查看所有开放 Issue（无阻塞项）
bd prime              # AI 优化的完整工作流上下文
bd status             # 快速状态摘要
```

### Issue 全生命周期

```bash
bd create "任务描述"              # 创建 Issue
bd show <id>                     # 查看详情
bd update <id> --claim           # 认领任务
bd update <id> --state done      # 完成任务
bd close <id>                    # 关闭 Issue
bd reopen <id>                   # 重开 Issue
bd list --state open             # 列出所有开放 Issue
bd list --assignee @me            # 我的任务
bd search "关键词"               # 搜索 Issue
```

### 依赖与结构

```bash
bd dep add <id> --depends-on <parent-id>    # 添加依赖
bd epic create "史诗名称"                     # 创建史诗
bd graph                                       # 可视化依赖图
bd children <id>                               # 查看子任务
bd swarm <id>                                 # 查看同族 Issue
```

### 质量门控

```bash
bd create --validate "任务"      # 创建时验证
bd lint                          # 检查 Issue 质量
bd preflight                     # 提交前检查
bd doctor                        # 诊断数据库健康度
```

### 持久化与同步

```bash
bd dolt push                     # 推送 Dolt 数据库
bd dolt pull                     # 拉取 Dolt 数据库
bd backup                        # 备份
bd export                         # 导出 JSONL
```

### 高级命令

```bash
bd stale                         # 列出陈旧 Issue
bd orphans                       # 列出孤立 Issue（无依赖/被依赖）
bd duplicate <id1> <id2>        # 标记重复
bd gate <id>                    # 设置任务门控
bd defer <id>                   # 推迟 Issue
bd note <id> "备注"             # 添加备注
bd tag <id> --add security      # 添加标签
bd priority <id> --adjust +2    # 调整优先级
```

## L3: 天龙九师集成

### 统一任务入口（所有岗位）

```
每个会话开始时 → bd ready → 查看开放任务
每个会话结束时 → bd prime → 确认上下文已保存
```

| 天龙岗位 | beads 集成方式 | 核心命令 |
|---------|--------------|---------|
| **00分析师** | 问题分解 → bd create | `bd create "分析 X 问题"` |
| **01调研师** | 调研任务 → bd create + dep | `bd dep add` 建立调研依赖链 |
| **02架构师** | 架构任务 → bd epic | `bd epic create "微服务重构"` |
| **03构建师** | 开发任务 → bd update --claim | `bd update --claim` 认领后开始开发 |
| **04验证师** | 测试任务 → bd gate | `bd gate <id>` 门控等待前置完成 |
| **05安全师** | 安全审计 → bd create + label | `bd create --label security` |
| **06审查师** | 审查任务 → bd list --state review | `bd list --state review` |
| **07记录师** | 文档任务 → bd create + 归档 | 任务完成后 `bd dolt push` 持久化 |
| **08发布师** | 发布任务 → bd epic | `bd epic create "v1.0发布"` 史诗管理 |
| **09-02编排** | 任务分发 → bd assign | `bd update <id> --assign 03builder` |
| **09-05求是协调** | 矛盾诊断 → bd list + 优先排序 | `bd list --priority highest` |

### 数据模型映射

```yaml
天龙 Issue 标准格式:
  title: "[岗位简称] 任务描述"
  body: |
    ## 任务目标
    ## 验收标准
    ## 依赖项
    ## 备注
  labels: [urgent, frontend, backend, security, docs]
  priority: highest  # lowest/low/medium/high/highest/critical
  state: backlog     # backlog/todo/in-progress/review/done/cancelled
```

## L4: 会话关闭协议（MANDATORY）

> 每个会话结束时必须执行。**工作未完成 = 未推送 = 未完成。**

```bash
# Step 1: 创建剩余 Issue
bd create "继续 X 开发" --priority high 2>/dev/null || true

# Step 2: 质量门控（如果有代码变更）
# [bd lint]  # 如有代码变更则运行

# Step 3: 更新 Issue 状态
bd update <id> --state done 2>/dev/null || true

# Step 4: Git 提交
git pull --rebase
git add -A
git commit -m "$(cat <<'EOF'
chore: 完成天龙引擎会话

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"

# Step 5: 推送（CRITICAL: 必须成功）
bd dolt push && git push
git status  # 确认 "up to date with origin"
```

### 核心规则

| 规则 | 说明 |
|------|------|
| **禁止 TodoWrite** | 所有任务必须通过 `bd` 追踪 |
| **禁止 MEMORY.md** | 持久知识使用 `bd remember` |
| **必须 git push** | 工作未推送 = 未完成 |
| **失败重试** | push 失败则解决后重试，直到成功 |

## L5: 与现有系统协同

```
┌─────────────────────────────────────────────────────────────┐
│ beads × 天龙引擎 完整协同链路                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  AGENTS.md (会话开始)                                       │
│    ↓ SessionStart Hook                                       │
│  bd prime → 恢复上下文 → bd ready → 查看任务               │
│    ↓                                                         │
│  天龙九师执行任务                                            │
│    ↓                                                         │
│  SessionEnd Hook → bd dolt push → git push                  │
│    ↓                                                         │
│  AGENTS.md (下次会话)                                        │
│    ↓ SessionStart Hook                                       │
│  bd prime → ...循环                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### beads × GitNexus

| 场景 | beads | GitNexus |
|------|-------|-----------|
| 任务追踪 | `bd create / list / update` | — |
| 代码影响分析 | — | `gitnexus_impact()` |
| 提交前检查 | `bd preflight / lint` | `gitnexus_detect_changes()` |
| 上下文恢复 | `bd prime` | — |
| 架构理解 | — | `gitnexus_query()` |

### beads × claude-mem

| beads | claude-mem | 协同 |
|-------|-----------|------|
| `bd remember` | `claude-mem` | 任务级知识 → 系统级记忆 |
| `bd note` | `PostToolUse Hook` | Issue 备注 → 会话记忆 |
| `bd dolt push` | `chromaDB` | 持久化同步 |

## L6: AI 优化命令（会话恢复）

```bash
bd prime              # 会话开始/结束时运行，打印完整工作流上下文
bd context            # 查看当前 Issue 上下文
bd recall "关键词"    # 搜索历史 Issue 和备注
bd remember "知识"    # 添加持久知识（跨会话）
bd history <id>       # 查看 Issue 变更历史
bd diff               # 查看当前分支与 main 的差异
```

### 快速参考

```
✨ bd ready              → 查看开放任务
🎯 bd create "任务"    → 创建 Issue
📋 bd list               → 列出所有 Issue
✅ bd update --claim     → 认领任务
🔒 bd gate <id>          → 设置门控
📤 bd dolt push          → 持久化推送
⚠️  WORK IS NOT COMPLETE UNTIL GIT PUSH SUCCEEDS
```

## L7: 配置与故障排查

### 配置文件

- `.beads/config.yaml` — Dolt 嵌入式配置
- `.beads/metadata.json` — 项目 ID 和数据库元信息
- `.beads/interactions.jsonl` — 交互历史
- `.beads/backup/` — 自动备份

### 常用诊断

```bash
bd doctor              # 诊断数据库健康度
bd info                # 查看当前配置
bd dolt status         # 查看 Dolt 数据库状态
bd version             # 查看 bd 版本

# 如果 push 失败
bd doctor
bd dolt pull --force
bd dolt push
```

### Dolt 嵌入式数据库

```
.beads/
├── embeddeddolt/          # Dolt 嵌入式数据库
├── config.yaml           # 配置 (dolt_mode: embedded)
├── metadata.json         # 项目 ID
└── interactions.jsonl    # 交互历史
```

## L8: 完整命令分类（88条）

| 分类 | 命令数 | 核心命令 |
|------|--------|---------|
| **Issues** | 23 | create, show, update, list, close, reopen, delete, edit, search, query, assign, state, priority, label, tag, note, gate, defer, stale, orphans, duplicate, depend, epic, comment |
| **Views/Reports** | 11 | status, list, count, stale, orphans, diff, history, find-duplicates, lint, preflight, types |
| **Dependencies** | 8 | dep, epic, graph, children, swarm, duplicate, supersede, gate |
| **Sync/Data** | 8 | dolt push, dolt pull, backup, export, import, restore, branch, federation |
| **Setup/Config** | 21 | init, bootstrap, config, context, setup, quickstart, onboard, remember, recall, hooks, dolt, kv, where, human, info, upgrade |
| **Maintenance** | 17 | doctor, gc, compact, migrate, upgrade, sql, prune, purge, flatten, batch, ping, rename-prefix, rules, worktree, compact |

## L9: 升级 paperclip-ticket 行动计划

### Phase 1: SKILL 替换（当前完成 ✅）

- [x] 创建 `beads/SKILL.md`
- [x] 确认 `bd ready` / `bd prime` 工作正常
- [x] 确认 AGENTS.md 集成块已自动插入
- [x] 确认 `settings.json` hooks 已注册

### Phase 2: 九师集成（待执行）

- [ ] 更新 `07记录师` SKILL.md：增加 `bd remember` 作为知识持久化替代 MEMORY.md
- [ ] 更新 `08发布师` SKILL.md：将 paperclip-ticket 命令替换为 beads 命令
- [ ] 更新 `09-02编排协调师` SKILL.md：使用 `bd dep add` 替代手动依赖管理

### Phase 3: 高级集成（规划中）

- [ ] 集成 beads-mcp 12 工具
- [ ] 集成 memory decay 机制与 advanced-memory-sync
- [ ] `bd gate` 作为 paperclip-governance 的轻量替代

## 预期收益

| 指标 | 升级前 (paperclip-ticket) | 升级后 (beads) | 提升 |
|------|--------------------------|----------------|------|
| **任务持久化** | 会话级 | 跨会话 + Git 版本化 | 质的飞跃 |
| **任务追踪** | 11字段 | 灵活字段 + 标签 + 史诗 | +200% |
| **上下文恢复** | 手动 | `bd prime` 自动 | +500% |
| **依赖管理** | 手动 | `bd dep / graph / swarm` | +400% |
| **Git 集成** | 无 | `bd dolt push` 同步 | 质的飞跃 |
| **分支支持** | 无 | Issue 跟分支走 | 新增能力 |
| **会话启动** | 无 | `bd prime` Hook 自动 | 新增能力 |
| **会话关闭** | 无 | MANDATORY 协议 | 新增能力 |
