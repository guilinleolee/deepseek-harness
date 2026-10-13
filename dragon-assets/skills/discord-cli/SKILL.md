---
license: UNKNOWN
name: discord-cli
description: Discord CLI with YAML-first structured output for AI agents — sync messages, search history, AI analysis, export data. Use for ALL Discord community operations.
author: jackwener
version: "1.0.0"
tags: - discord
- chat
- sync
- ai-analysis
- cli
- community-management
- xiaohongshu-cli-family
triggers: ["discord cli", "discord-cli Skill"]
---

# discord-cli Skill

CLI tool for Discord — local-first SQLite storage, message sync, search, AI analysis, structured export.

## 天龙岗位映射

| 天龙岗位 | 编号 | 核心能力 | 使用场景 |
|----------|------|---------|---------|
| **35-02 社媒运营** | ⭐⭐⭐⭐⭐ | 社区运营闭环 | 消息同步、用户分析、AI洞察 |
| **32-01 市场研究** | ⭐⭐⭐⭐⭐ | 社区数据研究 | 用户讨论分析、趋势发现 |
| **32-02 竞品分析** | ⭐⭐⭐⭐ | 竞品社区监控 | 竞品服务器分析、用户洞察 |
| **01 调研师** | ⭐⭐⭐⭐ | 社区调研 | 深度用户讨论分析 |
| **07 记录师** | ⭐⭐⭐⭐ | 数据归档 | 消息导出、历史存档 |

## Agent Defaults

1. **Prefer `--yaml`** for structured output unless strict JSON required
2. **Use `-n`** to limit results and save tokens
3. **Use `-o <file>`** with `export` for large datasets
4. **Specific queries over broad** — e.g., `discord search "keyword" -c general`
5. **Non-TTY defaults to YAML** — override with `OUTPUT=yaml|json|rich|auto`
6. **All output follows SCHEMA.md envelope**

## Prerequisites

```bash
# Install
uv tool install kabi-discord-cli
# Or: pipx install kabi-discord-cli

# Upgrade regularly
uv tool upgrade kabi-discord-cli

# AI commands require
export ANTHROPIC_API_KEY=...
```

## Commands

### Auth & Account

```bash
discord auth --save          # Auto-extract token from browser
discord status               # Check token validity
discord whoami --yaml        # User profile
```

### Servers & Channels

```bash
discord dc guilds --yaml     # List servers
discord dc channels <GUILD> --yaml
discord dc members <GUILD> --json
discord dc info <GUILD>
```

### Message Sync

```bash
discord dc sync-all          # Sync all known channels
discord dc sync <CHANNEL> -n 5000
discord dc history <CHANNEL> -n 2000
discord dc tail <CHANNEL> --once
```

### Query

```bash
discord search "keyword" -c general --yaml
discord today --yaml
discord recent -n 50 --json
discord stats
discord top --hours 24
discord timeline --by hour
```

### AI Analysis

```bash
discord analyze <CHANNEL> --hours 24
discord summary --hours 48
```

### Export

```bash
discord export <CHANNEL> -f json -o out.json
discord purge <CHANNEL> -y
```

## Output Schema

```yaml
# Success
ok: true
schema_version: "1"
data: [...]

# Error
ok: false
schema_version: "1"
error:
  code: channel_resolution_error
  message: "..."
```

## Workflow Examples

### Daily Sync

```bash
discord auth --save
discord status
discord dc sync-all
discord today --yaml
discord summary
```

### Community Research

```bash
discord dc guilds --yaml
discord dc channels <guild_id> --yaml
discord dc history <channel_id> -n 5000
discord analyze <channel> --hours 168
```

### User Feedback Analysis

```bash
discord search "bug" -c feedback --yaml
discord search "feature request" -c feedback --yaml
discord analyze feedback --hours 72
```

## Safety Notes

- Uses Discord **user token** (not bot token)
- Token stored locally, never uploaded
- Do not share raw tokens in chat
- Use `auth --save` for auto-extraction

## Integration with Dragon Engine

### 35-02 社媒运营 (V10.2)
- Community monitoring and analysis
- User feedback collection
- Trend detection in Discord communities
- **核心能力**: 社区运营闭环（消息同步+用户分析+AI洞察）

### 32-01 市场研究 (V2.6)
- Community research
- User insight extraction
- Historical message analysis
- **核心能力**: 社区数据研究（用户讨论分析+趋势发现）

### 01 调研师 (V8.22)
- Community research
- User insight extraction
- Historical message analysis

### 17-01 数据分析师 (V1.2)
- Chat data analytics
- Activity statistics
- Topic extraction

## 与其他CLI对比

| 维度 | xiaohongshu-cli | twitter-cli | discord-cli |
|------|-----------------|-------------|-------------|
| **平台** | 小红书 | X/Twitter | Discord |
| **内容类型** | 图文+短视频 | 短文+图片 | 聊天消息 |
| **运营重点** | 内容创作 | 内容传播 | 社区互动 |
| **消息持久化** | 平台存储 | 平台存储 | **本地SQLite** |
| **AI分析** | ❌ | ❌ | **✅ 内置** |
| **作者** | jackwener | jackwener | jackwener |

## Related Skills

- **bilibili-cli** — B站运营
- **xiaohongshu-cli** — 小红书运营
- **twitter-cli** — Twitter/X运营
- **tg-cli** — Telegram运营

---

**版本历史**:
- V1.0.0 (2026-03-13): 集成到天龙引擎 V8.24