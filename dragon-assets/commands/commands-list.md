---
name: commands-list
description: Claude Commands 列表
invokable: true
---
# Claude Commands 列表

本文档列出了当前 Claude Code 环境中可用的所有 commands，包括系统自带和自建命令。

---

## Commands 总览

### 系统自带 Commands

| 序号 | 命令名称 | 功能描述 |
|:---:|:---|:---|
| 1 | `/help` | 列出所有斜杠命令 |
| 2 | `/add-dir` | 把另一个目录加进工作区 |
| 3 | `/bug` | 直接向 Anthropic 报 Bug |
| 4 | `/clear` | 清空当前会话历史 |
| 5 | `/compact` | 压缩对话历史，节省 Token |
| 6 | `/config` | 打开配置面板（可换主题） |
| 7 | `/cost` | 查看本次会话的 Token 花费与时长 |
| 8 | `/doctor` | 诊断本地安装与环境 |
| 9 | `/exit` / `/quit` | 退出 REPL |
| 10 | `/export` | 把当前对话导出成文件或剪贴板 |
| 11 | `/hooks` | 管理 Pre/Post 工具钩子 |
| 12 | `/init` | 生成项目级 `CLAUDE.md` 配置文件 |
| 13 | `/login` / `/logout` | 切换账号身份 |
| 14 | `/mcp` | 管理 MCP（模型上下文协议）服务器 |
| 15 | `/memory` | 编辑跨会话记忆 |
| 16 | `/model` | 切换当前使用的模型 |
| 17 | `/permissions` | 重新设置工具权限 |
| 18 | `/pr_comments` | 查看 GitHub PR 评论 |
| 19 | `/review` | 请求对当前代码进行审查 |
| 20 | `/sessions` | 列出历史会话 |
| 21 | `/status` | 查看系统与账户状态 |
| 22 | `/terminal-setup` | 安装 Shift+Enter 快捷键绑定 |
| 23 | `/vim` | 切换 Vim 编辑模式 |

### 自建 Commands

| 序号 | 命令名称 | 功能描述 |
|:---:|:---|:---|
| 1 | `deepdive` | 探索式迭代思考（中文版）- 用于深度思考和复杂问题分析 |
| 2 | `deepdive-en` | 探索式迭代思考（英文版）- Deep Iterative Thinking |
| 3 | `bmad-init` | BMad-Method 框架初始化命令 |
| 4 | `feat` | 功能开发工作流 - 支持需求规划、讨论迭代和执行实施 |
| 5 | `git-cleanBranches` | Git 分支清理 - 安全删除已合并或过期的分支 |
| 6 | `git-commit` | Git 提交 - 自动生成 Conventional Commits 风格的提交信息 |
| 7 | `git-rollback` | Git 回滚 - 交互式回滚分支到历史版本 |
| 8 | `git-worktree` | Git Worktree 管理 - 管理并行开发工作树 |
| 9 | `init-project` | 项目初始化 - 生成/更新项目 AI 上下文文档 |
| 10 | `workflow` | 专业开发工作流 - 六阶段结构化开发流程 |
| 11 | `release` | 版本发布流程 - 标准化版本发布步骤 |
| 12 | `/00调研师` | **考古摸底**：在开工前查清现有代码逻辑、依赖和技术坑点 |
| 13 | `/01架构师` | **划定蓝图**：将模糊需求拆解为原子化的 `MULTI_AGENT_PLAN.md` |
| 14 | `/02构建师` | **代码施工**：根据蓝图编写高质量、防御性的生产级代码 |
| 15 | `/03验证师` | **极端找茬**：跑压力测试，不让一个 Bug 溜走 |
| 16 | `/04安全师` | **专项排雷**：检查 SQL 注入、秘钥泄露等安全漏洞 |
| 17 | `/05审查师` | **终极审计**：检查安全、性能与代码美感 |
| 18 | `/06记录师` | **文明传承**：自动编写 API 文档、README 和高质量代码注释 |
| 19 | `/07发布师` | **功德圆满**：规范提交 Git，发布到 GitHub |
| 20 | `/00investigator`| 同“00调研师”英文版 |
| 21 | `/01architect`   | 同“01架构师”英文版 |
| 22 | `/02builder`     | 同“02构建师”英文版 |
| 23 | `/03validator`   | 同“03验证师”英文版 |
| 24 | `/04security-reviewer` | 同“04安全师”英文版 |
| 25 | `/05code-reviewer` | 同“05审查师”英文版 |
| 26 | `/06scribe`      | 同“06记录师”英文版 |
| 27 | `/07publisher`   | 同“07发布师”英文版 |
| 28 | `/万能格式转换助手` | **全能工具**：集成了 Pandoc, FFmpeg, ImageMagick 等的格式转换引擎 |
| 29 | `/uc` | **快捷入口**：万能格式转换助手的快捷别名 |
| 30 | `/futures-analysis` | **期货分析**：Pandadata DeepView 38接口（席位博弈/期限结构/仓单库存/跨期套利）|

---

## 详细说明

### 系统自带 Commands

#### 1. /help
- **功能**: 列出所有可用的斜杠命令及其简要说明
- **用法**: `/help`

#### 2. /add-dir
- **功能**: 将另一个目录添加到当前工作区，方便跨目录操作
- **用法**: `/add-dir <目录路径>`

#### 3. /bug
- **功能**: 直接向 Anthropic 提交 Bug 报告
- **用法**: `/bug`

#### 4. /clear
- **功能**: 清空当前会话的对话历史
- **用法**: `/clear`

#### 5. /compact
- **功能**: 压缩对话历史以节省 Token 使用量
- **用法**: `/compact`

#### 6. /config
- **功能**: 打开配置面板，可更改主题等设置
- **用法**: `/config`

#### 7. /cost
- **功能**: 查看本次会话的 Token 花费和时长统计
- **用法**: `/cost`

#### 8. /doctor
- **功能**: 诊断本地安装环境和配置问题
- **用法**: `/doctor`

#### 9. /exit / /quit
- **功能**: 退出 REPL 模式
- **用法**: `/exit` 或 `/quit`

#### 10. /export
- **功能**: 将当前对话导出为文件或复制到剪贴板
- **用法**: `/export`

#### 11. /hooks
- **功能**: 管理 Pre/Post 工具钩子
- **用法**: `/hooks`

#### 12. /init
- **功能**: 生成项目级 `CLAUDE.md` 配置文件
- **用法**: `/init`

#### 13. /login / /logout
- **功能**: 切换账号身份
- **用法**: `/login` 或 `/logout`

#### 14. /mcp
- **功能**: 管理 MCP（模型上下文协议）服务器
- **用法**: `/mcp`

#### 15. /memory
- **功能**: 编辑跨会话的记忆内容
- **用法**: `/memory`

#### 16. /model
- **功能**: 切换当前使用的模型
- **用法**: `/model`

#### 17. /permissions
- **功能**: 重新设置工具权限
- **用法**: `/permissions`

#### 18. /pr_comments
- **功能**: 查看 GitHub PR 的评论
- **用法**: `/pr_comments`

#### 19. /review
- **功能**: 请求对当前代码进行审查
- **用法**: `/review`

#### 20. /sessions
- **功能**: 列出历史会话记录
- **用法**: `/sessions`

#### 21. /status
- **功能**: 查看系统与账户状态信息
- **用法**: `/status`

#### 22. /terminal-setup
- **功能**: 安装 Shift+Enter 快捷键绑定
- **用法**: `/terminal-setup`

#### 23. /vim
- **功能**: 切换 Vim 编辑模式
- **用法**: `/vim`

---

### 自建 Commands

#### 1. deepdive（自建）
- **触发关键词**: 探索式迭代思考、深度迭代、非线性迭代思考
- **功能描述**: 提供结构化的深度思考方法论，包括问题理解、建立探索性 TODO、执行真实迭代、案例验证和总结记录
- **适用场景**: 复杂设计问题、需要深度理解本质的问题、系统架构设计
- **文件路径**: [commands/deepdive/commands/deepdive.md](deepdive/commands/deepdive.md)

#### 2. deepdive-en（自建）
- **触发关键词**: deep iterative thinking, exploratory iteration, non-linear iteration
- **功能描述**: 同 deepdive 的英文版本
- **适用场景**: 同 deepdive，英文环境
- **文件路径**: [commands/deepdive/commands/deepdive-en.md](deepdive/commands/deepdive-en.md)

#### 3. bmad-init（自建）
- **命令**: `/bmad-init`
- **功能描述**: 在项目中初始化 BMad-Method 框架，自动检测版本并安装最新版本
- **特性**: 支持 expect 自动化安装、版本检查、交互式降级方案
- **文件路径**: [commands/zcf/bmad-init.md](zcf/bmad-init.md)

#### 4. feat（自建）
- **命令**: `/feat <任务描述>`
- **功能描述**: 功能开发完整工作流，支持需求规划、讨论迭代和执行实施三种类型处理
- **核心功能**:
  - 需求规划：生成详细的 markdown 规划文档
  - 讨论迭代：检索并分析上次规划，生成新版本文档
  - 执行实施：按规划文档执行任务，前端任务需 UI 设计
- **文件路径**: [commands/zcf/feat.md](zcf/feat.md)

#### 5. git-cleanBranches（自建）
- **命令**: `/git-cleanBranches [选项]`
- **功能描述**: 安全识别并清理已合并或长期未更新的 Git 分支
- **选项**:
  - `--base <branch>`: 指定基准分支
  - `--stale <days>`: 清理超过指定天数的分支
  - `--remote`: 同时清理远程分支
  - `--dry-run`: 预览模式（默认）
  - `--yes`: 自动确认
  - `--force`: 强制删除未合并分支
- **文件路径**: [commands/zcf/git-cleanBranches.md](zcf/git-cleanBranches.md)

#### 6. git-commit（自建）
- **命令**: `/git-commit [选项]`
- **功能描述**: 仅用 Git 分析改动并自动生成 Conventional Commits 风格的提交信息
- **选项**:
  - `--no-verify`: 跳过 Git 钩子
  - `--all`: 暂存所有改动
  - `--amend`: 修补上次提交
  - `--signoff`: 附加签名
  - `--emoji`: 包含 emoji 前缀
  - `--scope <scope>`: 指定作用域
  - `--type <type>`: 指定提交类型
- **文件路径**: [commands/zcf/git-commit.md](zcf/git-commit.md)

#### 7. git-rollback（自建）
- **命令**: `/git-rollback [选项]`
- **功能描述**: 交互式回滚 Git 分支到历史版本
- **选项**:
  - `--branch <branch>`: 指定分支
  - `--target <rev>`: 目标版本
  - `--mode reset|revert`: 回滚模式
  - `--depth <n>`: 显示版本数量
  - `--dry-run`: 预览模式（默认）
  - `--yes`: 自动确认
- **文件路径**: [commands/zcf/git-rollback.md](zcf/git-rollback.md)

#### 8. git-worktree（自建）
- **命令**: `/git-worktree <操作> [选项]`
- **功能描述**: 管理 Git worktree，支持智能默认、IDE 集成和内容迁移
- **操作**:
  - `add <path>`: 添加新 worktree
  - `migrate <target>`: 迁移内容
  - `list`: 列出所有 worktree
  - `remove <path>`: 删除 worktree
  - `prune`: 清理无效引用
- **文件路径**: [commands/zcf/git-worktree.md](zcf/git-worktree.md)

#### 9. init-project（自建）
- **命令**: `/init-project <项目摘要或名称>`
- **功能描述**: 初始化项目 AI 上下文，生成/更新根级与模块级 CLAUDE.md 索引
- **特性**:
  - 根级简明 + 模块级详尽的混合策略
  - 自动生成 Mermaid 结构图
  - 为模块添加导航面包屑
  - 增量更新与断点续扫
- **文件路径**: [commands/zcf/init-project.md](zcf/init-project.md)

#### 10. workflow（自建）
- **命令**: `/workflow <任务描述>`
- **功能描述**: 专业开发助手，提供结构化六阶段开发工作流
- **六阶段**:
  1. 研究与分析 - 需求完整性评分
  2. 方案构思 - 多方案评估
  3. 详细规划 - 创建执行路线图
  4. 实施 - 代码开发
  5. 代码优化 - 质量改进
  6. 质量审查 - 最终评估
- **文件路径**: [commands/zcf/workflow.md](zcf/workflow.md)

#### 11. release（自建）
- **命令**: `/release`
- **功能描述**: 标准化版本发布流程
- **流程步骤**:
  1. 拉最新代码确认版本号
  2. 触发 Skills 检查（代码审查、完整测试、资源检查）
  3. 生成 changelog
  4. 预发布测试
  5. 人工确认
  6. 正式发布
  7. 发通知
- **文件路径**: [commands/release.md](release.md)

#### 12. 编程宗师系列 (Programming Masters)
- **命令**: `/00调研师` (investigator), `/01架构师` (architect), `/02构建师` (builder), `/03验证师` (validator), `/04安全师` (security-reviewer), `/05审查师` (code-reviewer), `/06记录师` (scribe), `/07发布师` (publisher)
- **功能描述**: 全自动人工智能开发军团，覆盖软件开发全生命周期。
- **核心逻辑**:
  - **00调研师**: 考古摸底，查清现有代码逻辑与技术坑点。
  - **01架构师**: 划定蓝图，将模糊需求拆解为原子化计划。
  - **02构建师**: 代码施工，编写高质量、防御性的生产级代码。
  - **03验证师**: 极端找茬，跑压力测试与全方位行为验证。
  - **04安全师**: 专项排雷，扫描 SQL 注入、秘钥泄露等安全漏洞。
  - **05审查师**: 终极审计，由专家视角检查安全、性能与代码美感。
  - **06记录师**: 文明传承，自动维护 API 文档、README 与注释。
  - **07发布师**: 功德圆满，规范提交 Git 并发布到 GitHub。
- **文件路径**: `commands/[名称].md`

---

## 统计信息

- **总计**: 52 个 commands
- **系统自带**: 23 个
- **自建**: 29 个

### 分类统计

#### 系统自带分类
- **会话管理**: help, clear, compact, export, sessions, exit/quit
- **配置管理**: config, init, login/logout, model, permissions, vim, memory
- **系统工具**: add-dir, bug, cost, doctor, hooks, mcp, pr_comments, review, status, terminal-setup

#### 自建分类
- **思考方法论**: 2 个（deepdive、deepdive-en）
- **项目/工作流**: 4 个（bmad-init、feat、init-project、workflow）
- **Git 操作**: 4 个（git-cleanBranches、git-commit、git-rollback、git-worktree）
- **发布流程**: 1 个（release）
- **编程宗师 (天龙八部)**: 16 个（8 中文 + 8 英文）
- **工具扩展**: 2 个（万能格式转换助手、uc）

---

> 最后更新时间: 2026-01-27
