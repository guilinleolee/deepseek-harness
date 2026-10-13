---
description: 测试 Brave Search MCP 是否可用
argument-hint: [测试查询词]
allowed-tools: mcp__brave_search__*
---

# Brave Search MCP 测试

## 测试目的

验证 Brave Search MCP 服务器是否已正确加载并可用。

## 测试步骤

### 1. 检查 MCP 工具列表

查看当前会话中是否有 Brave Search 相关工具：
- `mcp__brave_search__search`
- 或类似的 brave search 工具

### 2. 执行测试搜索

使用查询词：${1:-"桂林 制造业 公司"}

```
正在测试 Brave Search MCP...

查询：{查询词}
```

### 3. 查看结果

如果看到搜索结果，说明 Brave Search MCP 可用。
如果返回错误，可能需要：
- 重启 Claude Code
- 检查 MCP 配置文件

## MCP 配置检查

配置文件路径：`~/.claude/mcp_servers.json`

检查内容：
```json
{
  "mcpServers": {
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@brave/brave-search-mcp-server"],
      "env": {
        "BRAVE_API_KEY": "BSAAXosKZM5x1_vIjBY3j2kBKOtI3Fx"
      }
    }
  }
}
```

## 如果不可用

### 重启 Claude Code

1. 退出 Claude Code
2. 重新启动
3. 再次运行测试

### 检查 MCP 服务器日志

查看是否有错误信息：
```
检查 Claude Code 设置 → MCP 服务器 → 查看日志
```

## 备用方案

如果 Brave Search 不可用，使用：
- WebSearch（如未达限额）
- 手动搜索（参考 SEARCH_ALTERNATIVES.md）
