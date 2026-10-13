---
license: MIT
name: mcp
description: >
  MCP (Model Context Protocol) 命令入口 - 按需调用MCP服务。
  支持地理编码、GEO分析、Schema生成、品牌追踪等MCP服务。
  触发词：/mcp、mcp命令、MCP调用。
user-invokable: true
argument-hint: "[command] [args...]"
allowed-tools:
  - Read
  - Bash
triggers:
  - "/mcp"
  - "mcp命令"
  - "MCP调用"
---

# MCP命令

## 命令列表

| 命令 | 功能 | 示例 |
|------|------|------|
| `mcp geocode [地址]` | 地址转坐标 | `/mcp geocode 北京天安门` |
| `mcp reverse [lat,lng]` | 坐标转地址 | `/mcp reverse 39.908,-116.397` |
| `mcp ip-lookup [IP]` | IP定位 | `/mcp ip-lookup 8.8.8.8` |
| `mcp llms-generate [site]` | 生成llms.txt | `/mcp llms-generate https://example.com` |
| `mcp schema-generate [type]` | 生成Schema | `/mcp schema-generate Article` |
| `mcp geo-analyze [url]` | GEO分析 | `/mcp geo-analyze https://example.com` |
| `mcp brand-track [brand]` | 品牌追踪 | `/mcp brand-track MyBrand` |
| `mcp citation-check [url]` | 引用检查 | `/mcp citation-check https://example.com` |
| `mcp status` | MCP状态 | `/mcp status` |
| `mcp list` | 列出MCP服务 | `/mcp list` |

## 使用方法

### 直接调用Python脚本

```bash
python3 "$HOME/.claude/projects/dragon-engine/skills/mcp-integration/scripts/cli.py" <command> [args]
```

### 示例

```bash
# 地理编码
python3 "$HOME/.claude/projects/dragon-engine/skills/mcp-integration/scripts/cli.py" geocode "北京天安门"

# 逆向编码
python3 "$HOME/.claude/projects/dragon-engine/skills/mcp-integration/scripts/cli.py" reverse "39.908,-116.397"

# IP定位
python3 "$HOME/.claude/projects/dragon-engine/skills/mcp-integration/scripts/cli.py" ip-lookup "8.8.8.8"

# 生成llms.txt
python3 "$HOME/.claude/projects/dragon-engine/skills/mcp-integration/scripts/cli.py" llms-generate "https://example.com"

# 生成Schema
python3 "$HOME/.claude/projects/dragon-engine/skills/mcp-integration/scripts/cli.py" schema-generate "Article" --title "My Article"

# GEO分析
python3 "$HOME/.claude/projects/dragon-engine/skills/mcp-integration/scripts/cli.py" geo-analyze "https://example.com"

# 品牌追踪
python3 "$HOME/.claude/projects/dragon-engine/skills/mcp-integration/scripts/cli.py" brand-track "MyBrand"

# 查看状态
python3 "$HOME/.claude/projects/dragon-engine/skills/mcp-integration/scripts/cli.py" status
```

## 依赖

- Python 3.8+
- 标准库: json, os, sys, asyncio, logging, dataclasses, enum, datetime, pathlib, hashlib, urllib

## 认证

某些MCP服务需要API密钥，请在环境变量中配置：

```bash
# 地理编码
export GEOAPIFY_KEY="your-geoapify-key"

# IP定位
export IPINFO_KEY="your-ipinfo-key"

# SEO服务
export DATAFORSEO_LOGIN="your-login"
export DATAFORSEO_PASSWORD="your-password"
export FIRECRAWL_API_KEY="your-firecrawl-key"
export EXA_API_KEY="your-exa-key"
export TAVILY_API_KEY="your-tavily-key"
export BRAVE_API_KEY="your-brave-key"
```
