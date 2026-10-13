---
license: UNKNOWN
name: tg-cli
description: CLI skill for Telegram to sync chats, search messages, filter keywords, and monitor groups from the terminal
author: jackwener
version: "1.0.0"
tags: - telegram
- tg
- chat
- monitor
- cli
triggers: ["tg cli", "tg-cli Skill"]
---

# tg-cli Skill

CLI tool for Telegram — sync chats, search messages, filter keywords, send messages, and monitor groups.

## ⚠️ 天龙引擎安全提示

**风险等级**: 🟠 中等

| 风险 | 说明 | 缓解措施 |
|------|------|---------|
| **账号封禁** | 使用个人账号（MTProto），非Bot API | 使用专用账号，非主账号 |
| **速率限制** | 频繁同步可能触发限制 | 每天仅1-2次同步 |
| **隐私风险** | 访问私有频道/群组 | 遵守平台规则 |

**推荐配置**:
```bash
# 使用专用账号
# 限制同步频率
export TG_SYNC_LIMIT=50      # 每次最多同步50个聊天
export TG_SYNC_DELAY=1       # 每个聊天间隔1秒
```

---

## Prerequisites

```bash
# Install (requires Python 3.10+)
uv tool install kabi-tg-cli
# Or: pipx install kabi-tg-cli

# Upgrade to latest (recommended to avoid API errors)
uv tool upgrade kabi-tg-cli
```

## Authentication

Uses your Telegram account (MTProto). Built-in Telegram Desktop API credentials are used by default.

```bash
tg chats              # First run: enter phone + verification code
tg whoami             # Check current user

# Optional: use your own app credentials
export TG_API_ID=123456
export TG_API_HASH=your_telegram_app_hash
```

## Command Reference

### Telegram Operations

```bash
tg chats                          # List joined chats
tg chats --type group             # Filter by type
tg status                         # Check auth/session status
tg status --yaml                  # Structured auth status
tg whoami                         # Show current user info
tg whoami --yaml                  # Preferred structured output for agents
tg history CHAT -n 1000           # Fetch historical messages
tg sync CHAT                      # Incremental sync (only new)
tg sync-all                       # Low-level sync for all current dialogs
tg refresh                        # Recommended daily refresh entrypoint
tg listen                         # Real-time listener
tg listen --persist               # Reconnect automatically for a near-live cache
tg info CHAT                      # Chat details
tg send CHAT "Hello!"             # Send a message
```

### Search & Query

```bash
tg search "Rust"                     # Search stored messages
tg search "Rust" -c "牛油果" --yaml  # Filter by chat + preferred YAML output
tg search "Rust|Golang" --regex      # Regex search
tg search "Rust" --sync-first --yaml # Refresh before querying
tg recent --hours 24 -n 20 --yaml    # Browse latest messages
tg recent --hours 24 --sync-first    # Refresh before browsing recent
tg filter "Rust,Golang,Java"         # Multi-keyword filter (today)
tg filter "招聘,remote" --hours 48   # Filter last N hours
tg today --sync-first                # Refresh before reading today's messages
tg stats --sync-first                # Refresh before aggregate stats
tg top -c "牛油果" --hours 24 --sync-first
tg timeline --by hour --sync-first   # Activity bar chart
```

### Data Management

```bash
tg export CHAT -f json -o out.json   # Export messages
tg export CHAT --hours 24            # Export last 24 hours
tg purge CHAT -y                     # Delete stored messages
```

## Structured Output

Major commands support `--json` and `--yaml` for machine-readable output.
AI agents should prefer `--yaml` unless a strict JSON parser is required:

```bash
tg search "Rust" --yaml
tg status --yaml
tg whoami --yaml
tg today --yaml
tg filter "招聘" --hours 48 --yaml
```

## Refresh Model

`tg-cli` is local-first. Query commands read from the local SQLite cache by default.

- Use `tg refresh` as the normal entrypoint before analysis.
- Use `--sync-first` when a single query should refresh before reading.
- Use `tg listen --persist` if you want a near-real-time local cache.

## Common Patterns for AI Agents

```bash
# Quick daily workflow
tg refresh --yaml                    # Refresh everything
tg today --sync-first --yaml         # See today's messages
tg filter "Rust,Golang" --hours 24 --sync-first --yaml

# Search and export for analysis
tg search "招聘" -n 100 --yaml > jobs.yaml
tg filter "远程,remote,Web3" --hours 72 --yaml > filtered.yaml

# Send messages
tg send "GroupName" "Hello from CLI!"
```

## 与天龙引擎协同

### 岗位映射

| 岗位 | 编号 | 核心命令 | 使用场景 |
|------|------|---------|---------|
| **01调研师** | 01 | `tg search`, `tg history`, `tg export` | 私有频道研究、历史消息分析 |
| **07记录师** | 07 | `tg refresh`, `tg export`, `tg purge` | Telegram数据归档、本地缓存 |
| **32-01市场研究** | 32-01 | `tg search`, `tg filter`, `tg stats` | 竞品群组监控、趋势追踪 |
| **35-02社媒运营** | 35-02 | `tg send`, `tg listen` | 消息发送、实时监控 |

### 与其他Skill协同

| Skill | 协同方式 |
|-------|---------|
| **Agent-Reach** | Agent-Reach处理公开频道，tg-cli处理私有频道 |
| **deep-research** | tg-cli采集数据 → deep-research深度分析 |
| **review-analyzer-skill** | tg-cli导出评论 → review-analyzer分析 |

### 调用示例

```bash
# 天龙岗位调用
[@调研师] 使用tg-cli研究私有频道的技术讨论
[@市场研究] 使用tg-cli监控竞品群组动态
[@记录师] 使用tg-cli归档Telegram数据

# 命令调用
/tg-cli search "关键词" --yaml
/tg-cli export "GroupName" -f yaml -o out.yaml
```

## Error Handling

- Commands exit with code 0 on success, non-zero on failure
- Error messages are prefixed with ✗ or shown in red
- Chat names are fuzzy-matched (partial name works)

## Safety Notes

- Do not ask users to share phone numbers or verification codes in chat logs.
- Session data is stored locally and never uploaded.
- **天龙引擎建议**: 使用专用账号，每天仅1-2次同步，优先使用只读操作。