# n8n-mcp 模板管理工具

## 工具概述

n8n-mcp 提供的模板管理功能用于搜索和获取 n8n 工作流模板。

## 可用工具

### 1. search_templates

搜索 n8n.io 上的工作流模板。

**参数**:
```javascript
{
  "query": "email automation",  // 搜索关键词
  "category": "communication", // 分类（可选）
  "limit": 10                  // 返回数量限制
}
```

**可用分类**:
- `ai-chatbots`: AI & 聊天机器人
- `communication`: 通信与协作
- `data-processing`: 数据处理
- `social-media`: 社交媒体
- `productivity`: 生产力

**使用示例**:
```javascript
// 搜索邮件自动化模板
const templates = await search_templates({
  query: "email automation",
  category: "communication",
  limit: 5
});

// 返回
{
  "templates": [
    {
      "id": "1234",
      "name": "Email to Slack Notification",
      "category": "communication",
      "description": "Send email to Slack",
      "tags": ["email", "slack", "notification"],
      "url": "https://n8n.io/workflows/1234"
    }
  ]
}
```

### 2. get_template

获取特定模板的详细信息和工作流 JSON。

**参数**:
```javascript
{
  "templateId": "1234"
}
```

**使用示例**:
```javascript
// 获取模板详情
const template = await get_template({ templateId: "1234" });

// 返回
{
  "id": "1234",
  "name": "Email to Slack Notification",
  "description": "Send email to Slack",
  "nodes": [...],
  "connections": {...},
  "tags": ["email", "slack"]
}
```

## 使用场景

### 场景1: 快速开始模板

```
用户需求: "我需要一个 AI 聊天机器人"

操作流程:
1. search_templates({ category: "ai-chatbots" })
2. 查看可用模板
3. 选择合适的模板
4. get_template() 获取完整配置
5. 根据需求修改
```

### 场景2: 学习最佳实践

```
学习流程:
1. 搜索特定功能模板
2. 获取模板详情
3. 分析节点配置
4. 学习架构设计
```

### 场景3: 快速原型开发

```
原型开发:
1. 找到最接近需求的模板
2. 导入模板到工作流
3. 快速修改和测试
4. 完成原型
```

## 模板差异对比

```javascript
// 获取多个模板进行对比
const templates = await search_templates({
  query: "gmail slack",
  limit: 3
});

// 对比差异
for (const t of templates.templates) {
  const detail = await get_template({ templateId: t.id });
  console.log(`${t.name}: ${detail.nodes.length} nodes`);
  console.log(`  使用节点: ${detail.nodes.map(n => n.type).join(', ')}`);
}
```

## 最佳实践

1. **先搜索后获取**: 总是先搜索再获取详情
2. **检查标签**: 查看模板标签确认功能匹配
3. **版本注意**: 模板可能基于旧版 n8n，注意兼容性
4. **自定义修改**: 模板只是起点，需要根据需求调整

## 模板到工作流转换

```javascript
// 从模板创建工作流
async function createFromTemplate(templateId, customizations) {
  // 1. 获取模板
  const template = await get_template({ templateId });

  // 2. 应用自定义
  const workflow = {
    name: customizations.name || template.name,
    nodes: template.nodes.map(node => ({
      ...node,
      // 应用节点级别的自定义
      ...customizations.nodeChanges?.[node.name]
    })),
    connections: template.connections,
    settings: {
      ...template.settings,
      ...customizations.settings
    }
  };

  // 3. 创建工作流
  const result = await create_workflow(workflow);

  return result;
}
```

## 相关文档

- [节点发现工具](node-discovery.md)
- [工作流 CRUD](workflow-crud.md)
- [验证执行工具](validation.md)
- [完整 API 参考](../reference/layer2-mcp.md)
