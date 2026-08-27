# n8n-mcp 节点发现工具

## 工具概述

n8n-mcp 提供的节点发现功能用于查找和获取 n8n 节点信息。

## 可用工具

### 1. search_nodes

搜索符合条件的 n8n 节点。

**参数**:
```javascript
{
  "query": "gmail",           // 搜索关键词
  "filter": "built-in"       // 过滤器: built-in | community | all
}
```

**使用示例**:
```javascript
// 搜索 Gmail 相关节点
const result = await search_nodes({
  query: "gmail",
  filter: "built-in"
});

// 返回
{
  "nodes": [
    {
      "id": "@n8n/n8n-nodes-gmail",
      "name": "Gmail",
      "version": "2",
      "category": "output",
      "description": "..."
    }
  ]
}
```

**搜索技巧**:
- 使用完整节点名称获得精确匹配
- 使用功能关键词（如 "email", "database"）查找相关节点
- 使用 "all" 过滤器同时搜索内置和社区节点

### 2. get_node

获取特定节点的详细配置信息。

**参数**:
```javascript
{
  "nodeType": "@n8n/n8n-nodes-gmail",
  "typeVersion": 2
}
```

**使用示例**:
```javascript
// 获取 Gmail 节点详细信息
const nodeDetails = await get_node({
  nodeType: "@n8n/n8n-nodes-gmail",
  typeVersion: 2
});

// 返回
{
  "id": "@n8n/n8n-nodes-gmail",
  "name": "Gmail",
  "displayName": "Gmail",
  "description": "Gmail email node",
  "typeVersion": 2,
  "inputs": ["main"],
  "outputs": ["main"],
  "properties": [
    {
      "name": "operation",
      "type": "options",
      "options": [
        { "name": "getAll", "value": "getAll" },
        { "name": "get", "value": "get" }
      ]
    }
  ],
  "credentials": [
    {
      "name": "gmailOAuth2",
      "required": true
    }
  ]
}
```

## 使用场景

### 场景1: 查找特定功能节点

```
用户需求: "我需要一个发送邮件的节点"

搜索策略:
1. search_nodes({ query: "email" })
2. 查看返回的节点列表
3. 选择合适的节点（如 Gmail, SMTP, SendGrid）
4. 使用 get_node 获取详细配置
```

### 场景2: 验证节点版本

```
验证流程:
1. get_node({ nodeType: "@n8n/n8n-nodes-gmail", typeVersion: 2 })
2. 检查 typeVersion 是否匹配
3. 如果版本不存在，使用默认版本
```

### 场景3: 发现社区节点

```
搜索流程:
1. search_nodes({ query: "slack", filter: "community" })
2. 查看可用的 Slack 社区节点
3. 评估节点功能和版本
4. 决定是否安装社区节点
```

## 最佳实践

1. **先搜索后获取**: 使用 `search_nodes` 发现节点，再用 `get_node` 获取详情
2. **版本检查**: 始终检查 typeVersion 兼容性
3. **过滤使用**: 根据需要使用不同的过滤器
4. **缓存结果**: 节点信息变化不频繁，可以缓存结果

## 错误处理

```javascript
try {
  const nodes = await search_nodes({ query: "gmail" });
  console.log(`Found ${nodes.nodes.length} nodes`);
} catch (error) {
  if (error.message.includes("not found")) {
    console.log("No nodes found, try different keywords");
  } else {
    throw error;
  }
}
```

## 相关文档

- [模板管理工具](template-management.md)
- [工作流 CRUD](workflow-crud.md)
- [验证执行工具](validation.md)
- [完整 API 参考](../reference/layer2-mcp.md)
