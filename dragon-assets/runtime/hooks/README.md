# hooks/ · 天龙引擎钩子目录索引

> 按 Claude Code hook trigger 模型分类。`hooks.json`（根目录）是配置入口；
> 9 个子目录分别对应一种触发时机。重构日期：2026-08-05。

## 目录速查

| 子目录 | 触发时机 | 文件数 | 用途 |
|--------|----------|--------|------|
| `postToolUse/`        | 工具调用完成后 | 6 | 日志记录、任务管理、token 监控、用量统计 |
| `preToolUse/`         | 工具调用前/期间 | 13 | 决策门、批判性检查、静态分析、危险命令拦截 |
| `userPromptSubmit/`   | 用户提交 prompt | 7 | 快捷语法、关键词识别、TODO 强制、Claudeception 激活 |
| `session-start/`      | 会话开始时 | 3 | 会话初始化、CLI 监控、commit 前置 |
| `session-end/`        | 会话结束时 | 5 | 共享记忆保存、状态归档、token 报告 |
| `on-demand/`          | 按需手动调用 | 8 | OpenClaw、PaperClip、Baoyu、X-Publisher 等高风险 Skill |
| `utility/`            | 业务模块库 | 38 | dragon-commander / nine-dragons / template / memory / interaction 等供 hook 引用 |
| `docs/`               | 文档 | 5 | README、HOOKS-ANALYSIS、IMPLEMENTATION-COMPLETE、P2-COMPLETE、使用指南 |
| `tests/`              | 测试 | 7 | test-hooks.sh、test-p2.sh、test-p2-fixed.sh、test-openclaw-integration、3 个 *.test.js |
| `bridge/`             | (保持原状) | 7 | bridge-runner / watchdog / 测试 |
| `gitnexus/`           | (保持原状) | 1 | gitnexus-hook.cjs |
| `hooks.json`          | (配置入口) | 1 | 6 个核心 hook 注册 + on_demand 7 个 + commands + settings |

## hooks.json 注册的核心钩子

| trigger | 路径 |
|---------|------|
| `postToolUse`        | `./postToolUse/nine-dragons-log-watcher.js`<br>`./postToolUse/nine-dragons-task-manager-hook.js`<br>`./postToolUse/lessons-logger.js` |
| `preToolUse`         | `./postToolUse/nine-dragons-log-watcher.js` (跨目录复用) |
| `userPromptSubmit`   | `./userPromptSubmit/dragon-shortcut-syntax-hook.js` |
| `SessionEnd`         | `./session-end/shared-memory-session-end.js` |
| `on_demand`          | 7 个高风险 skill 入口（见 hooks.json `on_demand` 段） |

## 各子目录文件清单

### postToolUse/ (6)
- `nine-dragons-log-watcher.js` — 日志监视器（错误检测 + 危险命令拦截）
- `nine-dragons-task-manager-hook.js` — 任务队列 hook 入口
- `lessons-logger.js` — 经验教训自动记录
- `token-hook.js` — token 用量 hook
- `token-optimizer.js` — token 优化器
- `skill-usage-tracker.js` — skill 使用度量

### preToolUse/ (13)
- `decision-gate-trigger.js` — 决策门触发
- `critical-thinking-agent-checker.js` — 批判性思维 Agent 检查
- `critical-thinking-collaboration.js` — 批判性思维协作
- `critical-thinking-memory-layer.js` — 批判性思维记忆层
- `gsd-deviation-handler.js` — GSD 偏差处理
- `hash-anchored-edit.js` — 哈希锚定编辑
- `static-analyzer.js` — 静态分析
- `meta-review-trigger.js` — 元审查触发
- `check-comments.js` / `check-comments.py` — 注释质量检查
- `cbm-code-discovery-gate` — CBM 代码发现门
- `staff-review-trigger.js` — Staff Engineer 审查触发
- `thought-diversity-checker.js` — 思维多样性检查

### userPromptSubmit/ (7)
- `dragon-shortcut-syntax-hook.js` — 快捷语法解析
- `claudeception-activator.sh` — Claudeception 持续学习激活器
- `user-prompt-submit.js` / `.sh` — 用户输入提交 hook
- `prompt-submit.js` — prompt 提交处理
- `todo-enforcer.sh` — TODO 强制器
- `keyword-detector.py` — 关键词检测

### session-start/ (3)
- `session-start.js` — 会话启动
- `claude-code-cli-monitor.js` — CLI 进程监控
- `pre-commit.sh` — commit 前置 hook

### session-end/ (5)
- `shared-memory-session-end.js` — 共享记忆保存（hooks.json 注册）
- `session-stop.js` — 会话停止
- `session-hook.js` — 会话 hook
- `session-token-cli.js` — session token CLI
- `shared-memory-commands.js` — 共享记忆命令

### on-demand/ (8)
- `on-demand-handler.js` — 按需调用处理器
- `openclaw-zero-polling-hook.js` / `.ps1` — OpenClaw 零轮询
- `openclaw-dragon-engine-adapter.js` — OpenClaw 适配器
- `limei-openclaw-adapter.js` — 李秘 OpenClaw 适配
- `LIMEI-OPENCLAW-INTEGRATION.md` — 李秘 OpenClaw 集成文档
- `OPENCLAW-INTEGRATION-SUMMARY.md` — OpenClaw 集成摘要
- `OPENCLAW-ZERO-POLLING-README.md` — OpenClaw 零轮询 README

### utility/ (38)
- `agent-runner.js`, `agent-booster.js`
- `dragon-commander.js` + 6 个变体（v8-wrapper / abtest / multimodal / api-bridge / hook-wrapper / test / v2-test）+ `dragon-commander.config.json`
- `dragon-protocol.js`, `dragon-communication-manager.js`, `dragon-communication-test.js`
- `nine-dragons-enhancer-v5.js`, `nine-dragons-task-manager.js`, `nine-dragons-completion-enforcer.js`
- `template-manager.js`, `template-cli.js`, `task-template-system.js`, `task-queue-visualizer.js`
- `recommend-engine.js`, `dashboard-cli.js`
- `interaction-cli.js`, `interaction-mode.js`, `model-switcher.js`, `mcp-config-manager.js`
- `memory-layer-v8.js`, `memory-layer-v9.js`
- `v74-performance-monitor.js`, `plan-health-checker.js`
- `github-issues-adapter.js`
- `code-rules.json`, `dragon-shortcut-syntax.md`

### docs/ (5)
- `README.md` — (原 hooks/README.md 已迁移至此)
- `HOOKS-ANALYSIS.md` — Hooks 分析文档
- `IMPLEMENTATION-COMPLETE.md` — 实施完成文档
- `P2-COMPLETE.md` — P2 完成报告
- `hooks使用指南.md` — 使用指南（原 PUA 误码名 `hooks浣跨敤鎸囧崡.md` 已修复）

### tests/ (7)
- `test-hooks.sh` — hooks 测试脚本
- `test-p2.sh` / `test-p2-fixed.sh` — P2 测试
- `test-openclaw-integration.js` — OpenClaw 集成测试
- `task-manager.test.js` — task-manager 单元测试
- `github-issues-adapter.test.js` — GitHub issues adapter 测试
- `nine-dragons-hooks.test.js` — nine-dragons hooks 测试

## 跨目录 require() 改写

重构时同步修改了 5 处 require() 跨目录引用：

| 文件 | 原 require | 新 require |
|------|-----------|-----------|
| `utility/dashboard-cli.js`                          | `./session-token-cli.js`           | `../session-end/session-token-cli.js` |
| `utility/nine-dragons-task-manager.js`              | `./bridge/bridge-runner.js`        | `../bridge/bridge-runner.js`          |
| `postToolUse/nine-dragons-task-manager-hook.js`     | `./nine-dragons-task-manager`      | `../utility/nine-dragons-task-manager`|
| `tests/task-manager.test.js`                        | `../nine-dragons-task-manager`     | `../utility/nine-dragons-task-manager`|
| `tests/github-issues-adapter.test.js`               | `../github-issues-adapter`         | `../utility/github-issues-adapter`    |

## 已知遗留坏引用（重构前已存在，未在本次修复）

- `utility/dragon-commander-v2-test.js` 引用 `./dragon-commander-v2.js`（文件不存在）
- `utility/dragon-commander-hook-wrapper.js` 引用 `./dragon-commander-v2.js`（文件不存在）
- `utility/dragon-commander-v8-wrapper.js` 引用 `./dragon-commander-v8.js`（文件不存在）
- `tests/nine-dragons-hooks.test.js` 引用 `../nine-dragons-hooks`（文件不存在）

这些坏引用在重构前已存在（属于历史未完成功能），不在本次重构范围。

## 重构脚本

`scripts/_reorg_hooks.py` — 完整迁移计划（PLAN 字典）+ git mv + hooks.json 改写 + require 改写。
可重复执行（幂等）：默认 dry-run，`--apply` 真改。