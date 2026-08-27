---
license: UNKNOWN
triggers: ["aitoearn mcp", "AiToEarn MCP Protocol Skill"]
---
# AiToEarn MCP Protocol Skill

## L0 一句话描述（≤15字）
> AiToEarn MCP Server标准接口，Claude/Cursor等AI助手接入

## L1 使用场景（50-100字）
适用于需要在各种AI助手中集成AiToEarn能力的场景。通过MCP协议，Claude Code、Cursor、Windsurf等AI助手可以直接调用AiToEarn的内容变现、发布、互动功能，实现AI原生的工作流自动化。

## L2 详细文档

### MCP服务器信息

| 属性 | 值 |
|------|-----|
| **Server Name** | aitoearn |
| **Protocol** | MCP (Model Context Protocol) |
| **Runtime** | Node.js 20+ |
| **Package** | @aitoearn/openclaw-plugin-cli |
| **API版本** | v1 |

### MCP工具列表

| 工具名 | 功能 | 输入参数 |
|--------|------|----------|
| `monetize_cps` | CPS变现 | content, platforms, commissionRate |
| `monetize_cpe` | CPE变现 | content, platforms, engagementTypes, rate |
| `monetize_cpm` | CPM变现 | content, platforms, cpmRate |
| `publish_single` | 单平台发布 | platform, contentType, filePath, title, description |
| `publish_batch` | 多平台分发 | platforms[], contentType, filePath, titles |
| `schedule_create` | 创建排期 | platform, contentPath, publishTime, timezone |
| `schedule_list` | 列出排期 | platform, startDate, endDate |
| `engage_like` | 自动点赞 | platform, targetId, count |
| `engage_comment` | 自动评论 | platform, contentId, commentText, aiGenerate |
| `engage_follow` | 自动关注 | platform, targetId, count |
| `engage_reply_setup` | AI回复配置 | platform, mode, replyTemplate |
| `earnings_query` | 收益查询 | platform, period |
| `stats_overview` | 数据概览 | platform, period |

### 配置方法

#### Claude Desktop配置

```json
// ~/.claude/settings.json (Windows: %USERPROFILE%\.claude\settings.json)
{
  "mcpServers": {
    "aitoearn": {
      "command": "npx",
      "args": ["-y", "@aitoearn/openclaw-plugin-cli"],
      "env": {
        "X_API_KEY": "your-api-key-from-aitoearn.cn-or-aitoearn.ai"
      }
    }
  }
}
```

#### Cursor配置

```json
// .cursor/mcp.json
{
  "mcpServers": {
    "aitoearn": {
      "command": "npx",
      "args": ["-y", "@aitoearn/openclaw-plugin-cli"],
      "env": {
        "X_API_KEY": "your-api-key"
      }
    }
  }
}
```

#### Windsurf配置

```json
// ~/.windsurf/config.json
{
  "mcpServers": {
    "aitoearn": {
      "command": "npx",
      "args": ["-y", "@aitoearn/openclaw-plugin-cli"],
      "env": {
        "X_API_KEY": "your-api-key"
      }
    }
  }
}
```

### 环境变量

| 变量 | 说明 | 默认值 | 可选值 |
|------|------|--------|--------|
| `X_API_KEY` | API密钥 | - | 从aitoearn.cn获取 |
| `AITOERN_ENV` | 环境 | `cn` | `cn`（中国版）/ `ai`（国际版） |
| `AITOERN_TIMEOUT` | 超时时间 | 30000 | 毫秒 |

### API端点

| 环境 | Base URL | 说明 |
|------|----------|------|
| **中国版** | `https://api.aitoearn.cn/v1` | 使用aitoearn.cn的API Key |
| **国际版** | `https://api.aitoearn.ai/v1` | 使用aitoearn.ai的API Key |

### MCP工具使用示例

```typescript
// 在Claude Code中使用
[@35-06] 使用AiToEarn变现 "AI工具评测" --mode CPS --platforms "douyin,xiaohongshu"

[@35-02] 使用AiToEarn分发内容到抖音和小红书

[@38-02] 查询抖音平台近30天收益数据

// MCP调用格式
{
  "tool": "monetize_cps",
  "arguments": {
    "content": "产品推广内容",
    "platforms": ["douyin", "xiaohongshu"],
    "commissionRate": 0.15
  }
}
```

### 与天龙引擎协同

| 天龙岗位 | MCP工具 | 协同效果 |
|---------|---------|---------|
| **35-06 变现运营师** | monetize_cps/cpe/cpm, earnings_query | 变现全流程 |
| **35-02 社媒运营** | publish_single/batch, schedule_* | 分发自动化 |
| **38-02 销售管理** | earnings_query, stats_overview | 收益监控 |
| **09-02 编排协调师** | 所有工具 | 跨平台编排 |

### MCP资源

| 资源类型 | URI | 说明 |
|----------|-----|------|
| `aitoearn://platforms` | 平台列表 | 支持的所有平台 |
| `aitoearn://earnings/{platform}` | 收益数据 | 各平台收益统计 |
| `aitoearn://schedules/{platform}` | 排期列表 | 内容排期计划 |

### 错误处理

| 错误码 | 说明 | 处理建议 |
|--------|------|----------|
| `401` | API Key无效或过期 | 检查并更新API Key |
| `403` | 平台授权过期 | 重新OAuth授权 |
| `429` | 请求频率超限 | 降低请求频率 |
| `500` | 服务器内部错误 | 重试或联系支持 |

### 部署方式

| 方式 | 说明 | 适用场景 |
|------|------|---------|
| **NPM直接安装** | `npx -y @aitoearn/openclaw-plugin-cli` | 快速测试 |
| **Docker本地部署** | `docker run aitoearn/mcp-server` | 私有化部署 |
| **源码构建** | `pnpm build && node dist/server.js` | 开发者定制 |

### 注意事项

1. **API Key匹配**：中国版和國際版Key不能混用
2. **平台授权**：每个平台需要单独OAuth授权
3. **请求限制**：注意API调用频率限制
4. **数据安全**：API Key请妥善保管，不要硬编码

### 版本信息

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-15 | 初始集成 |

### 文件结构

```
aitoearn-mcp/
├── SKILL.md              # 本文件
├── config/
│   ├── claude-desktop.json
│   ├── cursor.json
│   └── windsurf.json
└── README.md             # 详细配置说明