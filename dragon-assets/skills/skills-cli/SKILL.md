---
license: UNKNOWN
name: skills-cli
description: |
github_repo: vercel-labs/agent-skills
github_hash: ce3e64e468f8fa09a2d075d102771838061fdac0
last_updated: 2026-04-25
source_type: derived
version: 1.0.0
author: 天龙引擎团队
created: 2026-02-26
category: development
triggers: ["skills cli", "Vercel Skills CLI"]
---

# Vercel Skills CLI

**开放代理技能生态系统** 的官方 CLI 工具，支持 40+ AI Agent。

## 核心功能

- **安装技能**：从 GitHub/GitLab/本地路径安装技能到任意 AI Agent
- **多 Agent 支持**：同时管理 Claude Code、Cursor、Copilot 等 40+ 个 Agent
- **灵活部署**：支持项目级和全局安装
- **智能链接**：使用 Symlink 实现单一数据源，便于统一更新

## 触发场景

当用户请求以下操作时使用此技能：
- "安装技能到 Claude Code/Cursor"
- "查找技能"
- "更新已安装的技能"
- "列出所有技能"
- "移除技能"

## 安装技能

### 基础用法

```bash
# 安装技能（交互式选择 Agent 和技能）
npx skills add <owner/repo>

# 示例
npx skills add vercel-labs/agent-skills
```

### 源格式

```bash
# GitHub 简写（所有者/仓库）
npx skills add vercel-labs/agent-skills

# 完整 GitHub URL
npx skills add https://github.com/vercel-labs/agent-skills

# 直接指向仓库中的特定技能
npx skills add https://github.com/vercel-labs/agent-skills/tree/main/skills/web-design-guidelines

# GitLab URL
npx skills add https://gitlab.com/org/repo

# 任意 git URL
npx skills add git@github.com:vercel-labs/agent-skills.git

# 本地路径
npx skills add ./my-local-skills
```

### 常用选项

| 选项                    | 描述                                                                                                                                |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `-g, --global`        | 安装到用户目录而非项目目录                                                                                                            |
| `-a, --agent <agents...>` | 目标特定 Agent（例如 `claude-code`、`codex`）。见[可用 Agent 列表](#可用-agent)                                                                 |
| `-s, --skill <skills...>` | 按名称安装特定技能（使用 `'*'` 表示全部技能）                                                                                                  |
| `-l, --list`          | 列出可用技能但不安装                                                                                                                   |
| `-y, --yes`           | 跳过所有确认提示                                                                                                                     |
| `--all`               | 无提示地将所有技能安装到所有 Agent                                                                                                          |

### 使用示例

```bash
# 列出仓库中的技能
npx skills add vercel-labs/agent-skills --list

# 安装特定技能
npx skills add vercel-labs/agent-skills --skill frontend-design --skill skill-creator

# 安装名称中带空格的技能（必须加引号）
npx skills add owner/repo --skill "Convex Best Practices"

# 安装到特定 Agent
npx skills add vercel-labs/agent-skills -a claude-code -a opencode

# 非交互式安装（CI/CD 友好）
npx skills add vercel-labs/agent-skills --skill frontend-design -g -a claude-code -y

# 将仓库中的所有技能安装到所有 Agent
npx skills add vercel-labs/agent-skills --all

# 将所有技能安装到特定 Agent
npx skills add vercel-labs/agent-skills --skill '*' -a claude-code

# 将特定技能安装到所有 Agent
npx skills add vercel-labs/agent-skills --agent '*' --skill frontend-design
```

### 安装范围

| 范围          | 标志       | 位置                       | 用例                              |
| ----------- | -------- | ------------------------ | ------------------------------- |
| **项目**       | (默认)     | `./<agent>/skills/`       | 随项目提交，与团队共享                    |
| **全局**       | `-g`     | `~/<agent>/skills/`       | 在所有项目中可用                        |

### 安装方式

交互式安装时，可选择：

| 方向                      | 描述                                                    |
| ----------------------- | ----------------------------------------------------- |
| **符号链接**（推荐）            | 为每个 Agent 创建指向规范副本的符号链接。单一数据源，便于更新。                      |
| **复制**                   | 为每个 Agent 创建独立副本。当符号链接不支持时使用。                             |

## 其他命令

| 命令                        | 描述                   |
| ------------------------- | -------------------- |
| `npx skills list`         | 列出已安装技能（别名：`ls`）    |
| `npx skills find [query]` | 交互式或按关键词搜索技能        |
| `npx skills remove [skills]` | 从 Agent 中移除已安装技能    |
| `npx skills check`        | 检查可用的技能更新           |
| `npx skills update`       | 将所有已安装技能更新到最新版本      |
| `npx skills init [name]`  | 创建新的 SKILL.md 模板     |

### `skills list`

列出所有已安装技能。类似于 `npm ls`。

```bash
# 列出所有已安装技能（项目和全局）
npx skills list

# 仅列出全局技能
npx skills ls -g

# 按特定 Agent 过滤
npx skills ls -a claude-code -a cursor
```

### `skills find`

交互式或按关键词搜索技能。

```bash
# 交互式搜索（fzf 风格）
npx skills find

# 按关键词搜索
npx skills find typescript
```

### `skills check` / `skills update`

```bash
# 检查是否有任何已安装技能有更新
npx skills check

# 将所有技能更新到最新版本
npx skills update
```

### `skills init`

```bash
# 在当前目录创建 SKILL.md
npx skills init

# 在子目录创建新技能
npx skills init my-skill
```

### `skills remove`

从 Agent 中移除已安装技能。

```bash
# 交互式移除（从已安装技能中选择）
npx skills remove

# 按名称移除特定技能
npx skills remove web-design-guidelines

# 移除多个技能
npx skills remove frontend-design web-design-guidelines

# 从全局范围移除
npx skills remove --global web-design-guidelines

# 仅从特定 Agent 移除
npx skills remove --agent claude-code cursor my-skill

# 无确认地移除所有已安装技能
npx skills remove --all

# 从特定 Agent 移除所有技能
npx skills remove --skill '*' -a cursor

# 从所有 Agent 移除特定技能
npx skills remove my-skill --agent '*'

# 使用 'rm' 别名
npx skills rm my-skill
```

| 选项           | 描述                              |
| ------------ | ------------------------------- |
| `-g, --global` | 从全局范围（~/）而非项目移除               |
| `-a, --agent`  | 从特定 Agent 移除（使用 `'*'` 表示所有）   |
| `-s, --skill`  | 指定要移除的技能（使用 `'*'` 表示所有）       |
| `-y, --yes`    | 跳过确认提示                          |
| `--all`       | `--skill '*' --agent '*' -y` 的简写 |

## 什么是 Agent 技能？

Agent 技能是可扩展编码 Agent 功能的可复用指令集。它们在 `SKILL.md` 文件中定义，包含 `name` 和 `description` 的 YAML frontmatter。

技能让 Agent 能够执行专门任务，例如：
- 从 git 历史生成发布说明
- 按照团队约定创建 PR
- 与外部工具集成（Linear、Notion 等）

在 **[skills.sh](https://skills.sh)** 发现技能。

## 可用 Agent

技能可安装到以下任一 Agent：

| Agent                | `--agent`       | 项目路径                   | 全局路径                        |
| -------------------- | -------------- | ---------------------- | --------------------------- |
| Claude Code          | `claude-code`  | `.claude/skills/`       | `~/.claude/skills/`         |
| Cursor               | `cursor`       | `.cursor/skills/`       | `~/.cursor/skills/`         |
| GitHub Copilot       | `github-copilot` | `.agents/skills/`     | `~/.copilot/skills/`        |
| Windsurf             | `windsurf`     | `.windsurf/skills/`     | `~/.codeium/windsurf/skills/` |
| Cline                | `cline`        | `.cline/skills/`        | `~/.cline/skills/`          |
| Continue             | `continue`     | `.continue/skills/`     | `~/.continue/skills/`       |
| OpenCode             | `opencode`     | `.agents/skills/`       | `~/.config/opencode/skills/` |
| Codex                | `codex`        | `.agents/skills/`       | `~/.codex/skills/`          |
| Amp                  | `amp`          | `.agents/skills/`       | `~/.config/agents/skills/`  |
| Augment              | `augment`      | `.augment/skills/`      | `~/.augment/skills/`        |
| Crush                | `crush`        | `.crush/skills/`        | `~/.config/crush/skills/`   |
| ... (35+ 更多)       | ...            | ...                    | ...                         |

**查看完整列表**：[支持的 Agent](https://github.com/vercel-labs/skills#supported-agents)

## 常见用例

### 1. 安装单个技能到 Claude Code

```bash
npx skills add vercel-labs/agent-skills --skill frontend-design -a claude-code -g
```

### 2. 批量安装多个技能

```bash
npx skills add owner/repo --skill frontend-design --skill web-design-guidelines --skill react-patterns -a claude-code cursor -g
```

### 3. 查找新技能

```bash
# 交互式搜索
npx skills find

# 关键词搜索
npx skills find "testing"
```

### 4. 更新所有已安装技能

```bash
npx skills update
```

### 5. 检查技能更新

```bash
npx skills check
```

## 技术细节

- **依赖**：Node.js, npm, npx
- **安装方式**：通过 npx 直接运行，无需全局安装
- **配置存储**：技能链接信息存储在 `.agents/skills.json` 或 `~/.config/agents/skills.json`
- **符号链接**：优先使用符号链接以实现单一数据源管理

## 相关资源

- 官方网站：[skills.sh](https://skills.sh)
- GitHub：[vercel-labs/skills](https://github.com/vercel-labs/skills)
- 技能市场：[skills.sh](https://skills.sh)

## 故障排除

### 符号链接失败
在 Windows 上，可能需要**以管理员身份运行**终端或启用开发者模式才能创建符号链接。如果失败，CLI 会自动回退到复制模式。

### 权限错误
确保对目标目录有写权限：
- 项目级：`./.claude/skills/`
- 全局级：`~/.claude/skills/`

### Agent 未识别
检查 `--agent` 参数是否使用正确的标识符（见上表）。
