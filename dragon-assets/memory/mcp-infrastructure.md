---
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---
# MCP 基础设施笔记 · dragon-engine

> 天龙引擎 MCP 服务器配置的基础设施笔记。所有稳定的基础设施变更记录在这里，
> 避免 MEMORY.md（200 行限制）被基础设施细节挤占。

---

## 配置文件位置（2026-06-26）

| 优先级 | 路径 | 用途 |
|--------|------|------|
| P0（项目主配置） | `C:\Users\li\.claude\projects\dragon-engine\mcp_servers.json` | 6 个核心 MCP：memory / chrome / chrome-devtools / sequential-thinking / context7 / agentdb / skill-runner |
| P1（项目级 .mcp.json） | `C:\Users\li\.claude\projects\dragon-engine\.mcp.json` | 2 个项目本地 MCP：codebase-memory-mcp / tone-router |
| 备份目录 | `C:\Users\li\.claude\projects\dragon-engine\mcp-backups\` | 命名规范 `mcp_servers_backup_YYYYMMDD_HHMMSS_<原因>.json` |
| 全局文档 | `C:\Users\li\.claude\projects\mcp\mcp-list.md` | 14 个 MCP 服务的中文说明文档 |

---

## chrome-devtools-mcp 安装记录（2026-06-26）

### 触发
用户要求安装 https://github.com/ChromeDevTools/chrome-devtools-mcp（44,438 ⭐）

### 决策
- **name = `chrome-devtools`**（与现有 `chrome` = mcp-chrome-bridge 区分）
- **`--no-usage-statistics`**：关闭 Google 遥测（用户选择）
- **`CHROME_DEVTOOLS_MCP_NO_UPDATE_CHECKS=1`**：禁用 npm registry 升级检查
- **共存策略**：与现有 `chrome` MCP 互补，**不替换**
  - `chrome` (mcp-chrome-bridge)：浏览器扩展模式 + WebSocket 实时桥接
  - `chrome-devtools` (Google 官方)：CDP + Puppeteer + 性能分析 + Lighthouse

### 最终配置（mcp_servers.json 23-33 行）
```json
"chrome-devtools": {
  "command": "npx",
  "args": ["-y", "chrome-devtools-mcp@latest", "--no-usage-statistics"],
  "env": { "CHROME_DEVTOOLS_MCP_NO_UPDATE_CHECKS": "1" }
}
```

### 验证
- ✅ JSON 语法验证通过（python json.load）
- ✅ `npx -y chrome-devtools-mcp@latest --help` 成功执行（包版本 1.4.0，2026-06-22 发布）
- ✅ 7 个 MCP 服务全部注册
- ⚠️ **必须重启 Claude Code** 才能加载新 MCP

### 备份
`mcp-backups/mcp_servers_backup_20260626_083046_chrome-devtools.json`

---

## MCP 命名规范（避免冲突）

- 服务名 = 项目/功能简写，不含连字符嵌套（如 `chrome-devtools` 而不是 `chrome_devtools`）
- 与已有 MCP 命名冲突时，加后缀区分（如 `chrome-devtools` vs `chrome`）
- `_retained_services` 注释中必须记录每个 MCP 的"保留理由"

---

## 隐私默认值

天龙引擎默认开启以下隐私/噪声控制：

| MCP | 隐私配置 |
|-----|----------|
| chrome-devtools | `--no-usage-statistics` + `CHROME_DEVTOOLS_MCP_NO_UPDATE_CHECKS=1` |
| memory | 本地存储 `./ai-automation-memory/`（不上云） |
| agentdb | 本地向量库 `./agentdb-data/` |
| 其他 | 公共 API Key 走代理（`ANTHROPIC_BASE_URL=http://127.0.0.1:15721`） |