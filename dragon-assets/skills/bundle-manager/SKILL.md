---
license: UNKNOWN
name: bundle-manager
version: 1.0.0
description: |
  Wiseflow Addon Bundle 全生命周期管理：安装、卸载、查询三大核心操作。
  与crew-lifecycle-manager协同，支持天龙引擎多Agent团队动态编排。
author: 天龙引擎团队
created: 2026-05-05
category: ai
source_type: derived
origin: TeamWiseFlow/wiseflow (addon-bundle)
github_repo: TeamWiseFlow/wiseflow
github_hash: main
last_updated: 2026-05-05
triggers:
  - "bundle管理"
  - "addon bundle"
  - "技能包安装"
  - "技能包卸载"
  - "bundle-list"
  - "bundle-install"
  - "bundle-uninstall"
  - "技能包列表"
  - "插件安装"
---

# Bundle Manager — Addon Bundle 生命周期管理器

## 功能概述

Addon Bundle 是 Wiseflow 的扩展包机制，包含 Agent 配置和 Skill 自动化脚本。
Bundle Manager 提供三大核心操作：

1. **Install Bundle** — 从 URL/路径安装 Addon Bundle
2. **Uninstall Bundle** — 卸载已安装的 Bundle
3. **List Bundles** — 查询当前所有已安装的 Bundle

## 核心能力

### 1. 安装 Bundle (install-bundle)

```bash
./scripts/install-bundle.sh <source> [--name NAME] [--force]
```

**功能**：
- 支持 Git URL、本地路径、Marketplace ID 三种来源
- 验证 Bundle 结构（必须包含 crew/ 和/或 skills/ 目录）
- 安装到 `~/.claude/skills/` 或 `~/.claude/agents/`
- 更新 Bundle 索引 `bundles/index.json`
- 安装依赖（自动执行子目录中的 setup 脚本）

**来源类型**：

| 类型 | 格式 | 示例 |
|------|------|------|
| Git URL | `https://github.com/owner/repo` | GitHub 仓库 |
| Git SSH | `git@github.com:owner/repo.git` | SSH 克隆 |
| 本地路径 | `/path/to/bundle` 或 `./local-bundle` | 本地目录 |
| Marketplace ID | `author/bundle-name@version` | 插件市场 |

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| source | string | 是 | Bundle 来源 |
| --name | string | 否 | 指定安装名称（默认从目录名推断） |
| --force | flag | 否 | 强制覆盖已安装的 Bundle |

### 2. 卸载 Bundle (uninstall-bundle)

```bash
./scripts/uninstall-bundle.sh <bundle-id> [--reason REASON] [--archive] [--force]
```

**功能**：
- 验证 Bundle 是否已安装
- 归档 Bundle 文件（移至 `archive/bundles/`）
- 从 Bundle 索引移除
- 清理依赖关系

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| bundle-id | string | 是 | Bundle 标识符 |
| --reason | string | 否 | 卸载原因（默认：manual） |
| --archive | flag | 否 | 归档而非直接删除（默认：true） |
| --force | flag | 否 | 跳过确认 |

### 3. 查询 Bundle (list-bundles)

```bash
./scripts/list-bundles.sh [--format table|json|yaml] [--status active|archived|all]
```

**功能**：
- 扫描 `~/.claude/skills/` 和 `~/.claude/agents/` 目录
- 解析 Bundle 元数据（名称、版本、包含的 Agents/Skills）
- 按状态/来源分组展示
- 支持格式化输出

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| --format | string | 否 | 输出格式（默认：table） |
| --status | string | 否 | 筛选状态（默认：active） |

## 工作流

```
┌─────────────────────────────────────────────────────────────┐
│           Bundle Manager 工作流                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   09-02 编排协调师                                        │
│       │                                                     │
│       ├── list-bundles.sh ──▶ 全 Bundle 视图              │
│       │                                                     │
│       ├── install-bundle.sh ──▶ 新 Bundle 安装            │
│       │         ↓                                          │
│       │    验证结构 → 安装文件 → 注册索引 → 安装依赖      │
│       │                                                     │
│       └── uninstall-bundle.sh ──▶ Bundle 卸载              │
│             ↓                                              │
│          归档/删除 → 清理索引 → 清理依赖                  │
│                                                             │
│   Bundle Index (bundles/index.json)                        │
│       │                                                     │
│       └── 自动同步 ──▶ 编排协调师实时感知 Bundle 变化    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 规则

### 基本规则

1. **Bundle ID 格式**：`[author]-[bundle-name]`
   - 示例：`wiseflow-crew-lifecycle`
   - 有效字符：字母、数字、连字符

2. **Bundle 结构**：
   ```
   bundle-name/
   ├── SKILL.md           # 必须：Bundle 定义
   ├── agents/            # 可选：Agent 配置目录
   ├── skills/           # 可选：Skill 自动化目录
   ├── hooks/            # 可选：生命周期钩子
   ├── setup.sh          # 可选：安装脚本
   └── teardown.sh       # 可选：卸载脚本
   ```

3. **归档保留**：卸载的 Bundle 移至 `archive/bundles/`，保留 90 天

4. **索引同步**：所有操作后必须更新 `bundles/index.json`

### 安全规则

1. **禁止删除系统 Bundle**：`system` 前缀的 Bundle 不可卸载
2. **权限验证**：需要编排协调师授权才能执行安装/卸载
3. **审计日志**：所有操作记录到 `logs/bundle-lifecycle.log`

## 配置文件

### Bundle Index (bundles/index.json)

```json
{
  "version": "1.0",
  "updated": "2026-05-05T10:30:00Z",
  "bundles": [
    {
      "id": "wiseflow-crew-lifecycle",
      "name": "Crew Lifecycle Manager",
      "author": "wiseflow",
      "version": "1.0.0",
      "source": "https://github.com/TeamWiseFlow/wiseflow",
      "installed_at": "2026-05-05T10:30:00Z",
      "status": "active",
      "components": {
        "agents": ["00", "01", "02"],
        "skills": ["crew-lifecycle"]
      },
      "dependencies": []
    }
  ],
  "archives": []
}
```

## 与 crew-lifecycle-manager 协同

```
Wiseflow Addon Bundle 扩展体系：
├── crew-lifecycle-manager  → Agent 团队生命周期管理
│     └── recruit / dismiss / list Crew Members
└── bundle-manager         → Addon Bundle 生命周期管理
      └── install / uninstall / list Bundles
```

## 核心命令

```bash
# 安装 Bundle
./scripts/install-bundle.sh https://github.com/owner/bundle-name
./scripts/install-bundle.sh ./local-bundle --name custom-bundle
./scripts/install-bundle.sh author/bundle-name@v1.0 --force

# 卸载 Bundle
./scripts/uninstall-bundle.sh wiseflow-crew-lifecycle
./scripts/uninstall-bundle.sh wiseflow-crew-lifecycle --reason "upgraded"

# 查询 Bundle
./scripts/list-bundles.sh
./scripts/list-bundles.sh --format json
./scripts/list-bundles.sh --status archived
```

## 示例

### 示例1：安装 Bundle

**输入**：
```
[@编排协调师] 安装 crew-lifecycle-manager Bundle
```

**执行**：
```bash
./scripts/install-bundle.sh https://github.com/TeamWiseFlow/wiseflow --name crew-lifecycle
```

**输出**：
```
✅ Bundle 安装成功
📦 Bundle ID:   wiseflow-crew-lifecycle
📁 安装路径:     skills/crew-lifecycle-manager/
📝 索引已更新:  bundles/index.json
🔔 通知已发送:  09-02 编排协调师
```

### 示例2：查询全部 Bundle

**执行**：
```bash
./scripts/list-bundles.sh --format table
```

**输出**：
```
┌─────────────────────────────────────────────────────────────┐
│         Wiseflow Addon Bundle 全景                        │
├─────────────────────────────────────────────────────────────┤
│ installed (3)                                              │
│────────────────────────────────────────────────────────────│
│ wiseflow-crew-lifecycle  │ v1.0.0 │ active │ 3 agents  │
│ wiseflow-valuecell      │ v2.1.0 │ active │ 5 agents  │
│ custom-my-bundle       │ v1.2.0 │ active │ 1 agent   │
├─────────────────────────────────────────────────────────────┤
│ archived (1)                                              │
│────────────────────────────────────────────────────────────│
│ old-bundle-xyz           │ v0.9.0 │ archived│ -          │
├─────────────────────────────────────────────────────────────┤
│ 总计: 4 个 Bundle │ 活跃: 3 │ 已归档: 1              │
└─────────────────────────────────────────────────────────────┘
```

### 示例3：卸载 Bundle

**执行**：
```bash
./scripts/uninstall-bundle.sh custom-my-bundle --reason "replaced"
```

**输出**：
```
⚠️ 确认卸载 Bundle: custom-my-bundle
   原因: replaced
   影响: 将归档至 archive/bundles/custom-my-bundle-20260505.bak
确认卸载? (y/n): y

✅ Bundle 已卸载
📦 归档: archive/bundles/custom-my-bundle-20260505.bak
🧹 索引已清理
📝 审计日志已记录
```

## 天龙引擎版本记录

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-05 | 初始集成，基于 Wiseflow addon-bundle |

---

**版本**: V1.0 | **兼容性**: 天龙引擎 V11.05+ | **来源**: TeamWiseFlow/wiseflow
