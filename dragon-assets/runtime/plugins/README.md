# plugins/ · 天龙引擎插件分类索引

> **版本**: V1.0 · **生成日期**: 2026-08-05

按功能用途分 5 个子目录。

---

## dev-tool/ (6 个)

| 名称 | 说明 |
|------|------|
| `agent-sdk-dev` | Agent SDK 开发工具包 |
| `code-review` | 代码审查 |
| `commit-commands` | Git commit 命令集 |
| `plugin-dev` | plugin 开发脚手架 |
| `pr-review-toolkit` | PR review 工具集 |
| `security-guidance` | 安全策略指引 |

## workflow/ (4 个)

| 名称 | 说明 |
|------|------|
| `claude-opus-4-5-migration` | Opus 4.5 迁移工具 |
| `feature-dev` | 功能开发工作流 |
| `hookify` | Hook 配置工具 |
| `ralph-wiggum` | Ralph Wiggum 任务自动化 |

## ui/ (4 个)

| 名称 | 说明 |
|------|------|
| `claude-hud` | CLI HUD 状态条 |
| `explanatory-output-style` | 解释型输出样式 |
| `frontend-design` | 前端设计辅助 |
| `learning-output-style` | 学习型输出样式 |

## integration/ (2 个)

| 名称 | 说明 |
|------|------|
| `marketplaces` | Plugin 市场索引 |
| `repos` | 外部 repo 引用 |

## config/ (7 个)

| 名称 | 说明 |
|------|------|
| `blocklist.json` | 插件黑名单 |
| `config.json` | 插件配置 |
| `installed_plugins.json` | 已安装插件清单 |
| `known_marketplaces.json` | 已知 marketplace 列表 |
| `CLAUDE-PLUGINS-OFFICIAL-使用说明.md` | 官方 plugin 说明 |
| `Ralph-Wiggum-使用说明.md` | Ralph Wiggum 使用说明 |
| `使用说明.md` | 通用使用说明 |

---

**总计**: 23 项

## tikhub/ (2026-08-11 新增 · 自媒体工作台采集层)

| 项目 | 说明 |
|------|------|
| `tikhub` | TikHub 官方插件 v1.1.0（MIT）：19 个 skills（已桥接至 skills/_tikhub）+ 7 平台 MCP 配置（已注册 ~/.claude.json） |

**使用前提**：在 `~/.claude/settings.json` 的 env 配置 `TIKHUB_API_KEY`（注册 https://user.tikhub.io 获取）
**核心技能**：social-listening（用户需求采集）/ comments-analysis（评论分析）/ trend-research（爆款挖掘）
**关联**：秉凌自媒体工作台 · TikHub采集层选型决策
