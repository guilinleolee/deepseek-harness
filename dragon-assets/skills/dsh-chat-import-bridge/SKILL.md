---
name: dsh-chat-import-bridge
description: Nwflower/dsh-chat-import v0.1.0 (MIT, npm) 借鉴档 — 跨 17+ agent (Claude Code / Codex / ChatGPT / Cursor / Gemini / Reasonix / opencode / ZCode / Grok Build / OpenClaw / Pi / Hermes / Kimi CLI / DSH session) 的 chat history 导入 DSH 为 resumable session;反向 export / sync / bundle backup。当用户提到 "导入 chat 历史 / Claude Code 迁移 / Codex 迁移 / ChatGPT 迁移 / 跨 agent 备份 / chat bundle / 迁移到 DSH" 时，**自动加载**天龙自研借鉴档：6 个 CLI（import_chat / scan_discover / export_chat / sync_to_claude / import_agents / import_mcp）+ 17 种 format 路由 + bundle SHA-256 双指纹。
metadata:
  version: V1.0
  stage: 55
  upstream: Nwflower/dsh-chat-import v0.1.x
  license: MIT
  created: 2026-08-26
  strategy: 借鉴档（与 stage 41/45/46/48/49.x/50.x/52 同模式 · 不镜像真源 · 自研 Python）
triggers_zh:
  - "导入 chat 历史"
  - "迁移 Claude Code"
  - "迁移 Codex"
  - "迁移 ChatGPT"
  - "跨 agent 备份"
  - "chat bundle"
  - "迁移到 DSH"
  - "import_chat"
  - "dsh-chat-import"
triggers_en:
  - "import chat history"
  - "migrate Claude Code"
  - "migrate Codex"
  - "migrate ChatGPT"
  - "cross-agent backup"
  - "chat bundle"
  - "migrate to DSH"
  - "import_chat"
  - "dsh-chat-import"
downstream:
  - 28-11-univer-workbench-operator (阶段 47 · 聊天历史可视化)
  - 09-04-chief-of-staff V2.1 (跨 Agent 数据迁移指挥官)
  - 41 阶段 mneme-heat-engine (记忆层 · 跨 session 经验复用)
  - 43 阶段 dsh-agent-teams (协同框架 · captain 处理多源数据)
compliance:
  license: MIT
  notice: 上游 MIT verbatim
  trademark: 不使用 "DSH 官方"
---

# dsh-chat-import-bridge · V1.0 · 天龙引擎阶段 55

> **TL;DR**：借鉴 Nwflower/dsh-chat-import v0.1.x（MIT, npm）的 **17+ agent chat history 跨平台迁移** 范式，自研 Python 桥：6 个 CLI（import_chat / scan_discover / export_chat / sync_to_claude / import_agents / import_mcp）+ 18 种 format 路由 + bundle SHA-256 双指纹。
> **核心能力**：全保真度 chat 迁移（保留 tool calls / reasoning / 模型 / 时间戳）+ matrix export 反向 + 跨 session 经验复用。

---

## 0 · 前置条件

无需外部依赖。纯 Python 3.11+ 标准库（hashlib + json + pathlib）。

---

## 1 · 借鉴清单（10 类核心能力）

| # | 能力 | 上游接口 | 借鉴档实现 |
|---|---|---|---|
| 1 | **批量 chat 导入** | `import_chat(format, path)` × 18 formats | `import_chat.py` + 18 format 路由 |
| 2 | **会话发现** | `scan_discover()` | `scan_discover.py` (只读预览) |
| 3 | **Matrix Export** | `export_chat(format='claude'/'codex'/'kimi')` | `export_chat.py` + 3 format |
| 4 | **Bundle Backup** | `export_bundle` / `restore_bundle` | `bundle.py` + SHA-256 双指纹 |
| 5 | **增量 sync_to_claude** | `sync_to_claude(guarded)` | `sync_to_claude.py` + 防覆盖 |
| 6 | **Agent Asset 迁移** | `import_agents` (pi/opencode/Claude/Codex → DSH skills) | `import_agents.py` |
| 7 | **MCP Mirror** | `import_mcp` / `/mcp-status` | `mcp_mirror.py` |
| 8 | **Settings 翻译** | `import_settings` / `/settings-suggest` | `settings_translate.py` |
| 9 | **Handoff Summaries** | `/resume-claude` / `/resume-codex` | `handoff.py` |
| 10 | **审计 + 健康检查** | `verify_session` / `doctor` | `audit.py` |

---

## 2 · 18 种 format 路由

| format | 来源 | 存储路径模式 |
|---|---|---|
| `claude` | Claude Code | `~/.claude/projects/<slug>/<sessionId>.jsonl` |
| `claude-3p` | Claude-3p client | `%LOCALAPPDATA%\Claude-3p\claude-code-sessions` |
| `codex` | Codex / ChatGPT CLI | `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` |
| `chatgpt` | ChatGPT web export | `conversations.json` |
| `cursor` | Cursor | `~/.cursor/projects/<slug>/agent-transcripts` |
| `gemini` | Gemini | `~/.gemini/tmp/<slug>/chats` |
| `reasonix` | Reasonix | `~/.reasonix/sessions/*.json` |
| `opencode` | opencode | `~/.local/share/opencode/storage/` |
| `mimo` | MiMo Code | `~/.mimo/sessions/<id>.json` |
| `zcode` | ZCode | `~/.zcode/logs/<date>/<id>.md` |
| `grok` | Grok Build | `~/.grokx/sessions/<id>.jsonl` |
| `openclaw` | OpenClaw | `~/.openclaw/chats/<id>.md` |
| `pi` | Pi Coding Agent | `~/.pi/sessions/<id>.json` |
| `hermes` | Hermes | `~/.hermes-cli/history.jsonl` |
| `kimi` | Kimi CLI / Kimi Code | `~/.kimi/sessions/<id>.json` |
| `qoder` | Qoder CLI | `~/.qoder/sessions/<id>.jsonl` |
| `workbuddy` | WorkBuddy | `~/.workbuddy/sessions/<id>.json` |
| `dsh` | DSH session logs | `~/.dsh/sessions/<id>.jsonl` |
| `local-jsonl` | 本地 JSONL | 任意路径 |

---

## 3 · Bundle 备份协议（SHA-256 双指纹）

```python
{
  "version": "1.0",
  "source_format": "claude",
  "session_id": "abc-123",
  "created_at": "2026-08-26T15:00:00+08:00",
  "fingerprint_source": "sha256:abc...",  # 源文件指纹
  "fingerprint_content": "sha256:def...", # 序列化后内容指纹
  "messages": [...],
  "tools": [...],
  "metadata": {...}
}
```

---

## 4 · Idempotency & 保护（上游 §Key behaviors）

- **expectedHash** + **restamp**：检测源变更后再导入
- **unchanged sources skip**：未变化源跳过
- **grown sources append**：增长源追加
- **context-budget protection**：超长会话截断保护
- **sub-agent 默认过滤**：排除 sub-agent 转换（避免噪声）

---

## 5 · 工作流

```
1. dsh_chat_scan(path)                  → 会话清单（预览）
2. dsh_chat_import(format, path, ...)    → 导入为 DSH session
3. dsh_chat_export(session_id, format)  → 反向导出（claude/codex/kimi）
4. dsh_chat_sync(session_id, target)    → 增量同步
5. dsh_chat_bundle(session_id)           → bundle 备份
6. dsh_chat_restore(bundle_path)        → 跨机器恢复
```

---

## 6 · 与天龙协同

```
dsh-chat-import-bridge V1.0 (阶段 55)
   │
   ├─ 41 阶段 mneme-heat-engine (跨 session 经验复用 · bundle 持久化)
   ├─ 43 阶段 dsh-agent-teams (captain 协同处理多源数据)
   ├─ 47 阶段 dsh-univer-office-bridge (跨 agent chat 落 .univer 文件可视化)
   └─ 09-04-chief-of-staff V2.1 (跨 Agent 迁移指挥官)
```

---

## 7 · 累计 PASS 贡献（阶段 55）

| 项 | PASS | 说明 |
|---|---|---|
| dsh_chat_scan | 2 | scan_discover + 17 formats |
| dsh_chat_import | 2 | 18 format 路由 + idempotency |
| dsh_chat_export | 1 | matrix export (claude/codex/kimi) |
| dsh_chat_bundle | 1 | SHA-256 双指纹 + 跨机器恢复 |
| dsh_chat_sync | 1 | sync_to_claude 防覆盖 |
| dsh_chat_audit | 1 | doctor + verify_session |
| 端到端（scan→import→bundle→restore）| 2 | 全链路 |
| **小计** | **+10** | 累计 PASS 967 → 977 |

---

## 8 · 关键文件

| 资产 | 路径 |
|---|---|
| 本 skill | `dragon-engine/skills/dsh-chat-import-bridge/SKILL.md` |
| LICENSE (MIT) | `dragon-engine/skills/dsh-chat-import-bridge/LICENSE` |
| NOTICE | `dragon-engine/skills/dsh-chat-import-bridge/NOTICE` |
| 扫描脚本 | `dragon-engine/skills/dsh-chat-import-bridge/scripts/scan.py` |
| 导入脚本 | `dragon-engine/skills/dsh-chat-import-bridge/scripts/importer.py` |
| 导出脚本 | `dragon-engine/skills/dsh-chat-import-bridge/scripts/exporter.py` |
| Bundle 脚本 | `dragon-engine/skills/dsh-chat-import-bridge/scripts/bundle.py` |
| 健康检查 | `dragon-engine/skills/dsh-chat-import-bridge/scripts/check.py` |
| 测试套 | `dragon-engine/skills/dsh-chat-import-bridge/tests/test_*.py` |
| 上游仓库 | https://github.com/Nwflower/dsh-chat-import |
| npm 包 | https://www.npmjs.com/package/dsh-chat-import |

---

## 9 · 决策记录

| # | 决策项 | 选择 |
|---|---|---|
| 1 | 集成形态 | **借鉴档**（与 stage 41/45/46/48/49.x/50.x/52 同模式）|
| 2 | 触发安装 | **无需安装**（pip 即可，借鉴档纯 Python）|
| 3 | 真源安装 | **可选**（npm `dsh-chat-import` 可装 DSH · 与本 skill 并行）|
| 4 | 协同方向 | **与 stage 41 mneme + 43 dsh-agent-teams 协同** |
