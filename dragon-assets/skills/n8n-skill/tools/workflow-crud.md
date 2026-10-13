# n8n-mcp 工作流 CRUD 工具

## 工具概述

n8n-mcp 提供完整的工作流生命周期管理功能，包括创建、读取、更新、删除（CRUD）操作。

## 可用工具

### 1. create_workflow

创建新的工作流。

**参数**:
```javascript
{
  "workflow": {
    "name": "My Workflow",           // 工作流名称
    "nodes": [...],                   // 节点数组
    "connections": {...},             // 连接配置
    "settings": {...},                // 可选设置
    "staticData": {...},              // 可选静态数据
    "tags": ["automation"]            // 可选标签
  }
}
```

**使用示例**:
```javascript
// 创建简单工作流
const result = await create_workflow({
  workflow: {
    name: "Email Notification",
    nodes: [
      {
        id: "node-1",
        name: "Schedule Trigger",
        type: "n8n-nodes-base.scheduleTrigger",
        typeVersion: 1.1,
        position: [250, 300],
        parameters: {
          rule: {
            interval: [{ "field": "hours", "hoursInterval": 1 }]
          }
        }
      },
      {
        id: "node-2",
        name: "Send Email",
        type: "n8n-nodes-base.emailSend",
        typeVersion: 2,
        position: [450, 300],
        parameters: {
          fromEmail: "sender@example.com",
          toEmail: "receiver@example.com",
          subject: "Test Email",
          text: "Hello from n8n!"
        }
      }
    ],
    connections: {
      "Schedule Trigger": {
        main: [[{ "node": "Send Email", "type": "main", "index": 0 }]]
      }
    },
    settings: {
      executionOrder: "v1"
    }
  }
});

// 返回
{
  "id": "1234",
  "name": "Email Notification",
  "active": false,
  "createdAt": "2024-01-01T00:00:00.000Z"
}
```

### 2. get_workflow

获取工作流详情。

**参数**:
```javascript
{
  "workflowId": "1234"
}
```

**使用示例**:
```javascript
const workflow = await get_workflow({ workflowId: "1234" });

// 返回完整工作流配置
{
  "id": "1234",
  "name": "Email Notification",
  "nodes": [...],
  "connections": {...},
  "settings": {...},
  "active": true,
  "createdAt": "2024-01-01T00:00:00.000Z",
  "updatedAt": "2024-01-01T01:00:00.000Z"
}
```

### 3. update_workflow

更新现有工作流。

**参数**:
```javascript
{
  "workflowId": "1234",
  "workflow": {
    "name": "Updated Name",           // 可选：仅更新名称
    "active": true,                   // 可选：激活工作流
    "nodes": [...],                   // 可选：更新节点
    "connections": {...}              // 可选：更新连接
  }
}
```

**使用示例**:
```javascript
// 激活工作流
await update_workflow({
  workflowId: "1234",
  workflow: { active: true }
});

// 更新单个节点
await update_workflow({
  workflowId: "1234",
  workflow: {
    nodes: [
      {
        id: "node-1",
        name: "Updated Trigger",
        type: "n8n-nodes-base.scheduleTrigger",
        typeVersion: 1.1,
        position: [250, 300],
        parameters: {
          rule: {
            interval: [{ "field": "hours", "hoursInterval": 2 }]
          }
        }
      }
    ]
  }
});
```

### 4. delete_workflow

删除工作流。

**参数**:
```javascript
{
  "workflowId": "1234"
}
```

**使用示例**:
```javascript
await delete_workflow({ workflowId: "1234" });

// ⚠️ 警告：此操作不可逆
```

### 5. list_workflows

列出所有工作流。

**参数**:
```javascript
{
  "active": true,               // 可选：按激活状态过滤
  "tags": ["automation"],       // 可选：按标签过滤
  "limit": 10                  // 可选：返回数量限制
}
```

**使用示例**:
```javascript
// 列出所有活跃工作流
const activeWorkflows = await list_workflows({ active: true });

// 列出特定标签的工作流
const automationWorkflows = await list_workflows({
  tags: ["automation"],
  limit: 5
});

// 返回
{
  "workflows": [
    {
      "id": "1234",
      "name": "Email Notification",
      "active": true,
      "tags": ["automation"],
      "createdAt": "2024-01-01T00:00:00.000Z"
    }
  ],
  "total": 10
}
```

## 高级操作

### 批量操作

```javascript
// 批量激活
async function batchActivate(workflowIds) {
  for (const id of workflowIds) {
    await update_workflow({
      workflowId: id,
      workflow: { active: true }
    });
  }
}

// 批量导出
async function batchExport(workflowIds) {
  const workflows = [];
  for (const id of workflowIds) {
    const workflow = await get_workflow({ workflowId: id });
    workflows.push(workflow);
  }
  return workflows;
}
```

### 克隆工作流

```javascript
async function cloneWorkflow(workflowId, newName) {
  // 1. 获取原工作流
  const original = await get_workflow({ workflowId: workflowId });

  // 2. 创建副本
  const clone = await create_workflow({
    workflow: {
      ...original,
      name: newName,
      id: undefined  // 清除 ID 以创建新工作流
    }
  });

  return clone;
}
```

### 版本管理

```javascript
// 创建版本快照
async function createSnapshot(workflowId) {
  const workflow = await get_workflow({ workflowId: workflowId });

  // 保存到文件
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const filename = `workflow-${workflowId}-${timestamp}.json`;

  await fs.writeFile(filename, JSON.stringify(workflow, null, 2));

  return filename;
}
```

## 使用场景

### 场景1: 工作流生命周期管理

```
创建流程:
1. create_workflow() - 创建草稿
2. validate_workflow() - 验证配置
3. execute_workflow() - 测试运行
4. update_workflow({active:true}) - 激活生产
```

### 场景2: 工作流更新

```
更新流程:
1. get_workflow() - 获取当前配置
2. 本地修改节点/连接
3. validate_workflow() - 验证更改
4. update_workflow() - 应用更新
5. execute_workflow() - 测试新版本
```

### 场景3: 清理维护

```
维护流程:
1. list_workflows({active:false}) - 查找非活跃工作流
2. 检查最后使用时间
3. delete_workflow() - 删除过期工作流
```

## 最佳实践

1. **先验证后更新**: 使用 `validate_workflow` 确保配置正确
2. **版本控制**: 定期导出工作流配置作为备份
3. **标签管理**: 使用标签组织和过滤工作流
4. **批量操作谨慎**: 批量删除/更新前先测试
5. **错误处理**: 始终包装 CRUD 操作在 try-catch 中

```javascript
// 安全更新模板
async function safeUpdate(workflowId, updates) {
  try {
    // 1. 验证更新
    const validation = await validate_workflow({
      workflow: updates
    });

    if (!validation.valid) {
      console.error('Validation failed:', validation.errors);
      return false;
    }

    // 2. 应用更新
    await update_workflow({
      workflowId,
      workflow: updates
    });

    // 3. 测试运行
    const result = await execute_workflow({
      workflowId,
      mode: 'manual'
    });

    return result.status === 'success';

  } catch (error) {
    console.error('Update failed:', error);
    return false;
  }
}
```

## 错误处理

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `WORKFLOW_NOT_FOUND` | 工作流不存在 | 检查 workflowId |
| `INVALID_WORKFLOW` | 配置无效 | 修正节点/连接配置 |
| `VALIDATION_FAILED` | 验证失败 | 查看错误详情并修复 |
| `UPDATE_CONFLICT` | 并发更新冲突 | 重新获取工作流后重试 |

## 相关文档

- [节点发现工具](node-discovery.md)
- [模板管理工具](template-management.md)
- [验证执行工具](validation.md)
- [完整 API 参考](../reference/layer2-mcp.md)
