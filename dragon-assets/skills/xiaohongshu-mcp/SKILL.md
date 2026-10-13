---
license: UNKNOWN
name: xiaohongshu-mcp
description: >
github_repo: xpzouying/xiaohongshu-mcp
github_hash: c63748f6a96d0dafba6d3acdd67947711837de22
last_updated: 2026-04-25
source_type: derived
Use for: (1) Publishing image, text, and video content, (2) Searching for notes and trends,
Triggers: xiaohongshu automation, rednote content, publish to xiaohongshu, xiaohongshu search, social media management.
triggers: ["xiaohongshu mcp", "Xiaohongshu MCP Skill (with Python Client)"]
---

# Xiaohongshu MCP Skill (with Python Client)

Automate content operations on Xiaohongshu (小红书) using a bundled Python script that interacts with the `xpzouying/xiaohongshu-mcp` server (8.4k+ stars).

**Project:** [xpzouying/xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp)

## 1. Local Server Setup

This skill requires the `xiaohongshu-mcp` server to be running on your local machine.

### Step 1: Download Binaries

Download the appropriate binaries for your system from the [GitHub Releases](https://github.com/xpzouying/xiaohongshu-mcp/releases) page.

| Platform | MCP Server | Login Tool |
| -------- | ---------- | ---------- |
| macOS (Apple Silicon) | `xiaohongshu-mcp-darwin-arm64` | `xiaohongshu-login-darwin-arm64` |
| macOS (Intel) | `xiaohongshu-mcp-darwin-amd64` | `xiaohongshu-login-darwin-amd64` |
| Windows | `xiaohongshu-mcp-windows-amd64.exe` | `xiaohongshu-login-windows-amd64.exe` |
| Linux | `xiaohongshu-mcp-linux-amd64` | `xiaohongshu-login-linux-amd64` |

Grant execute permission to the downloaded files:
```shell
chmod +x xiaohongshu-mcp-darwin-arm64 xiaohongshu-login-darwin-arm64
```

### Step 2: Login (First Time Only)

Run the login tool. It will open a browser window with a QR code. Scan it with your Xiaohongshu mobile app.

```shell
./xiaohongshu-login-darwin-arm64
```

> **Important**: Do not log into the same Xiaohongshu account on any other web browser, as this will invalidate the server's session.

### Step 3: Start the MCP Server

Run the MCP server in a separate terminal window. It will run in the background.

```shell
# Run in headless mode (recommended)
./xiaohongshu-mcp-darwin-arm64

# Or, run with a visible browser for debugging
./xiaohongshu-mcp-darwin-arm64 -headless=false
```

The server will be available at `http://localhost:18060`.

## 2. Using the Skill

This skill includes a Python client (`scripts/xhs_client.py`) to interact with the local server. You can use it directly from the shell.

### Available Commands

| Command | Description | Example |
| --- | --- | --- |
| `status` | Check login status | `python scripts/xhs_client.py status` |
| `search <keyword>` | Search for notes | `python scripts/xhs_client.py search "咖啡"` |
| `detail <id> <token>` | Get note details | `python scripts/xhs_client.py detail "note_id" "xsec_token"` |
| `feeds` | Get recommended feed | `python scripts/xhs_client.py feeds` |
| `publish <title> <content> <images>` | Publish a note | `python scripts/xhs_client.py publish "Title" "Content" "url1,url2"` |

### Example Workflow: Market Research

1.  **Check Status**: First, ensure the server is running and you are logged in.
    ```shell
    python ~/clawd/skills/xiaohongshu-mcp/scripts/xhs_client.py status
    ```

2.  **Search for a Keyword**: Find notes related to your research topic. The output will include the `feed_id` and `xsec_token` needed for the next step.
    ```shell
    python ~/clawd/skills/xiaohongshu-mcp/scripts/xhs_client.py search "户外电源"
    ```

3.  **Get Note Details**: Use the `feed_id` and `xsec_token` from the search results to get the full content and comments of a specific note.
    ```shell
    python ~/clawd/skills/xiaohongshu-mcp/scripts/xhs_client.py detail "64f1a2b3c4d5e6f7a8b9c0d1" "security_token_here"
    ```

4.  **Analyze**: Review the note's content, comments, and engagement data to gather insights.

## 本地锁定模板（nieao）

- Top10 图文文字模板（LOCKED）：`templates/xhs_top10_text_template.md`
- 发布排错与复盘模板：`templates/xhs_publish_sop.md`
- 使用规则：默认直接套用；仅在用户明确要求时改写。

## 小红书发布实战坑位（Browser 自动化）

当用户反馈“发布了但看不到 / 图片不全 / 只看到首图”时，按下面顺序排查。

1. 状态延迟：先看「全部笔记」与「审核中」，不要只看「已发布」。
2. 图集异常：同时检查“编辑页图片计数”和“右侧预览页数”，两者都要合理。
3. 叠加上传：若出现 `22/18` 这类异常计数，说明发生了叠加，不是干净重传。
4. 旧帖干扰：同标题可能有多条，需按发布时间辨认新旧版本。
5. 外链延迟：`/explore/{note_id}` 可能短时显示“暂时无法浏览”，通常是审核/缓存延迟。

## 推荐恢复策略（优先级）

- 首选：新建「上传图文」重新发布（最稳，避免脏状态）。
- 次选：在编辑页“清空图片后重传”，再核验计数。
- 收尾：发布后到笔记管理确认状态，再删旧留新，最后给外链。

执行细则与检查清单见：`templates/xhs_publish_sop.md`
