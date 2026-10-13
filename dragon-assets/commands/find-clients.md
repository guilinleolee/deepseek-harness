---
name: find-clients
description: 搜索客户信息并自动保存CSV，支持国产CRM导入
invokable: true
allowed-tools: WebSearch, mcp__brave_search__*, mcp__exa__*, mcp__web_reader__webReader, mcp__fetch__fetch, Write(~/客户搜索结果/*)
argument-hint: [行业] [地区] [数量]
model: sonnet
---
# 客户信息搜索

使用 client-finder-pro SKILL 搜索行业客户信息。

**注意**：如果 WebSearch 达到月度限额，SKILL 会自动尝试使用 Brave Search 或 Exa MCP。

## 参数

- **行业**: $1 (必需) - 如 "SaaS"、"制造业"、"餐饮"
- **地区**: $2 (可选) - 如 "北京"、"上海"、"广东"
- **数量**: $3 (可选) - 默认50，范围1-100

## 执行流程

使用 client-finder-pro SKILL 执行以下任务：

### 1. 理解需求
- 行业: $1
- 地区: ${2:-"全国"}
- 数量: ${3:-50}

### 2. 执行多源搜索
- 搜索引擎查询（10+种查询模板）
- 招聘网站查询（Boss直聘、拉勾、51job、猎聘）
- 企业信息平台（企查查、天眼查）
- 地图/黄页（高德地图、大众点评）
- LinkedIn查询（国际企业和外向型企业）
- 脉脉查询（中国企业职场信息）

### 3. 搜索工具降级（如 WebSearch 不可用）
- 尝试 Brave Search MCP（独立配额）
- 尝试 Exa MCP（备用搜索）
- 使用 fetch + webReader 直接访问企业信息平台

### 4. 深度挖掘官网
- 使用webReader访问官网Contact/About页面
- 提取邮箱、电话、地址、决策人信息
- 提取招聘信息中的HR联系方式

### 5. 自动保存
- 保存到 ~/客户搜索结果/客户信息_$1_{timestamp}.csv
- UTF-8编码
- 符合国产CRM格式

### 6. 输出结果
- 显示Markdown表格预览
- 显示CSV文件路径
- 显示搜索统计信息

## 备用方案

如果搜索遇到限额问题，参考：`~/.claude/skills/client-finder-pro/SEARCH_ALTERNATIVES.md`

## 使用示例

```bash
# 基础用法
/find-clients SaaS

# 指定地区
/find-clients 制造业 广东

# 指定数量
/find-clients 餐饮 北京 30
```
