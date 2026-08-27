# 天龙引擎 · Prompts 入口 V1.3

> **用途**：本目录是天龙引擎的 6 类 prompt 模板集，每一类解决一个具体场景。
> **版本**：V1.3 · 2026-08-06（新增 `local-sync-upstream.md` · 上游同步；+`local-claude-symlink.md`）
> **配合**：`scripts/sync-dragon.py` 自动检测升级 + `skills/skill-updater/` 上游指纹扫描

---

## 📂 6 类 Prompt 一览

| 文件 | 场景 | 适用 AI | 加载内容 | 耗时 |
|------|------|---------|---------|------|
| **local-sync-upstream.md** 🔄 | **完整同步上游资产（755 skills + agents + LICENSE 监控）** | **Claude / CODEX / Cursor** | **9 步 · skill-updater + 4 类资产指纹 + 仓库状态** | **1-2 小时（月度）** |
| **local-claude-symlink.md** 🐉 | **首次配置 Claude Desktop 软链接天龙** | **Claude Desktop / Claude Code** | **9 类资产 symlink + claude.md + 4 个 MCP + Project** | **15 分钟** |
| **local-codex-symlink.md** 🐉 | **首次配置 CODEX 软链接天龙** | **CODEX DESKTOP** | **8 类资产 symlink + AGENTS.md 追加** | **10 分钟** |
| **local-replicate.md** ⭐ | 日常让本地 AI 复刻天龙能力 | Claude desktop / Cursor / CODEX | 4 份本地 spec | 5 分钟 |
| **local-upgrade.md** ⭐ | 日常让本地 AI 帮你升级天龙 | Claude desktop / Cursor / CODEX | VERSION + BIBLE + README + MEMORY | 10 分钟 |
| *(memory/)* cross-ai-replication-prompt.md | 远程复刻（无本地文件）| 任何 AI（GitHub URL）| BIBLE + README + MEMORY | 5 分钟 |

---

## 🎯 选哪个？

### "我想批量同步天龙所有上游资产（skill / agent / LICENSE）"
→ 用 **`local-sync-upstream.md`** 🔄（月度巡检 · 补 4 类资产指纹 + LICENSE 监控）

### "**首次配置** Claude Desktop（Mac/Win 应用）/ Claude Code（CLI）"
→ 用 **`local-claude-symlink.md`** 🐉（一次性配置，永久生效 + MCP 注册）

### "**首次配置** CODEX DESKTOP"
→ 用 **`local-codex-symlink.md`** 🐉（一次性配置，永久生效）

### "我想让 CODEX / Cursor 帮我做天龙任务"
→ 用 **`local-replicate.md`**

### "我想让 AI 当 co-pilot 帮我升级天龙"
→ 用 **`local-upgrade.md`**

### "AI 不在我本地，只能 fetch URL"
→ 用 **`memory/cross-ai-replication-prompt.md`**

---

## 🚀 3 步日常使用

### 步骤 1 · 选 prompt

| 你想做什么 | 复制哪份 |
|----------|---------|
| 完整同步天龙所有上游资产（月度巡检）| `local-sync-upstream.md` 🔄 |
| 首次配置 Claude Desktop 永久加载天龙 | `local-claude-symlink.md` 🐉 |
| 首次配置 CODEX 永久加载天龙 | `local-codex-symlink.md` 🐉 |
| 让 AI 出图 / 写文案 / 跑 skill | `local-replicate.md` 🎯 |
| 加新 skill / 修 bug / 升级版本 | `local-upgrade.md` 🔧 |
| 让远程 AI 也能用天龙 | `memory/cross-ai-replication-prompt.md` 🌐 |

### 步骤 2 · 粘到 AI

把【🎯 Prompt（直接复制 ↓）】整段粘到：
- **Claude desktop**: Project Instructions
- **Cursor**: `@codebase` + 整段 prompt
- **CODEX**: `codex --prompt` 或 prompt 文件
- **Aider**: `--read <prompt_file>`
- **ChatGPT**: 直接粘第一条 message

### 步骤 3 · 等 AI "就绪"

```
🎉 输出："天龙引擎 V2.0 就绪"
```

之后说你的任务。

---

## 📊 prompt 协同矩阵

| 你做 | 用哪份 | 预期效果 |
|------|--------|---------|
| 月度完整同步天龙所有上游资产 | local-sync-upstream | 9 步 · VERSION + skill-updater + 4 类资产指纹 + LICENSE + 仓库状态 |
| 首次让 Claude Desktop 永久加载天龙 | local-claude-symlink | 9 类资产 symlink + claude.md + 4 个 MCP + 20/20 PASS |
| 首次让 CODEX 永久加载天龙 | local-codex-symlink | 8 类资产 symlink + AGENTS.md 追加 + 20/20 PASS |
| 出 1 张小红书封面 | local-replicate | 6/6 PASS 推理 brief + 调 muapi |
| 加新 skill X | local-upgrade | 7 步升级流程 + 跑 smoke + push |
| 远程让 AI 用天龙 | cross-ai | AI fetch GitHub URL |
| 修某个 skill bug | local-upgrade | 走 Step 2-3 修 + 验证 |
| 同步到本地 AI | （不用 prompt）| `python scripts/sync-dragon.py` |
| 检测新版本 | （不用 prompt）| `python scripts/sync-dragon.py --check` |

---

## 🔧 适配你的 AI 工具

### Claude desktop
```
Settings → Projects → "天龙引擎"
Project Knowledge: 拖入 BIBLE.md + README.md + memory/MEMORY.md + agents/35-06-blogger-distiller-v14-style.md
Project Instructions: 复制粘贴 local-replicate.md 的【🎯 Prompt】整段
```

### Claude Desktop（永久软链接 · MCP 注册 · 一次性配置）🐉
```bash
# 把 local-claude-symlink.md 的【🎯 Prompt】整段发给 Claude Desktop
# 它会自己：
# 1. ln -s 9 类资产到 ~/.claude/（含 mcp/）
# 2. 追加 ~/.claude/claude.md 小节（不覆盖原内容）
# 3. 注册 4 个天龙 MCP 到 claude_desktop_config.json
# 4. 跑 smoke test 验证 20/20 PASS
# ⚠️ 然后手动：重启 Claude Desktop + 创建 Project "天龙引擎"
```
⚠️ 配完后日常任务用 `local-replicate.md` 唤醒；Claude Desktop 加载的就是真天龙资产 + MCP 工具。

### Cursor IDE
```
@codebase ~/projects/c--Users-li--claude/dragon-engine/
+ 把 local-replicate.md 内容复制到 .cursor/rules/dragon-engine.mdc
（sync-dragon.py --target cursor 已自动写入 7.4 KB 到 ~/.cursor/rules/dragon-engine.mdc）
```

### CODEX DESKTOP（永久软链接 · 一次性配置）🐉
```bash
# 把 local-codex-symlink.md 的【🎯 Prompt】整段发给 CODEX
# 它会自己：
# 1. ln -s 8 类资产到 ~/.codex/
# 2. 追加 AGENTS.md 小节（不覆盖原内容）
# 3. 跑 smoke test 验证 20/20 PASS
# 4. 输出软链接清单
```
⚠️ 配完后日常任务用 `local-replicate.md` 唤醒；CODEX 加载的就是真天龙资产。

### Aider / ChatGPT CLI
```bash
cat prompts/local-replicate.md | aider
```

---

## 🛠 维护

### 当天龙升级时
1. `python scripts/sync-dragon.py` 自动同步
2. prompts/ 内的 6 个 prompt 会随 BIBLE 同步更新（generate-cross-ai-prompt.py）
3. **月度完整上游巡检**：跑 `local-sync-upstream.md`（补 4 类资产指纹 + LICENSE 监控）
4. **Claude Desktop 软链接场景**：天龙主仓升级后软链接**不用重做**（指针自动跟随），只需 `python scripts/sync-dragon.py --target claude` 同步 `claude.md` 末尾小节
5. **CODEX 软链接场景**：同上，跑 `--target codex` 同步 AGENTS.md 末尾小节

### 当新增 prompt 类型时
在 prompts/ 新建 `.md` 文件 + 在本 README 添加一行表格条目。

### 当 prompt 不工作时
- 检查路径前缀 `~/projects/c--Users-li--claude/`
- 检查 4 份 spec 是否齐全
- 检查 AI 工具版本（CODEX ≥ 0.40 / Cursor ≥ 0.30 / Claude desktop ≥ 1.0）
- **Claude Desktop 软链接**：检查 `ls -la ~/.claude/` 软链接是否还在；检查 `claude_desktop_config.json` 格式 JSON 合法；检查 Windows `Developer Mode`
- **CODEX 软链接**：检查 `ls -la ~/.codex/` 软链接是否还在；Windows `Developer Mode` 是否启用
- **上游同步**：检查 `bash skills/skill-updater/scripts/scan.sh --no-network`（无网络跑通）；检查 GitHub 连通性 `curl -sI https://api.github.com`

---

## 📋 6 个 prompt 互斥场景

| 场景 | 用哪个 | 不用哪个 |
|------|--------|---------|
| **月度完整上游同步**（755 skills + 4 类资产 + LICENSE）| `local-sync-upstream.md` 🔄 | 其它（无 skill-updater 集成）|
| **首次配置** Claude Desktop 永久加载天龙 | `local-claude-symlink.md` 🐉 | 其它（无 MCP 注册）|
| **首次配置** CODEX 永久加载天龙 | `local-codex-symlink.md` 🐉 | 其它（无 symlink 步骤）|
| 临时让 AI 帮个小忙 | `local-replicate.md` | `local-upgrade.md`（过重）|
| 完整升级天龙（含 push）| `local-upgrade.md` | `local-replicate.md`（无升级流程）|
| AI 远程无本地访问 | `cross-ai-replication-prompt.md` | 其它（要本地文件）|

> 💡 **最佳组合（完整生命周期）**：
>
> | 阶段 | 频率 | 用哪个 |
> |------|------|--------|
> | 首次配置 Claude Desktop | 一次性 | `local-claude-symlink.md` 🐉 |
> | 首次配置 CODEX | 一次性 | `local-codex-symlink.md` 🐉 |
> | 日常任务 | 每次会话 | `local-replicate.md` ⭐ |
> | 月度上游巡检 | 月度 | `local-sync-upstream.md` 🔄 |
> | 版本升级 | 按需 | `local-upgrade.md` 🔧 |
> | 远程 AI | 按需 | `cross-ai-replication-prompt.md` 🌐 |

---

🤖 Generated by [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>