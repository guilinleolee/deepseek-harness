# n8n-mcp 知识库 Layer 2: MCP API 完整参考

## 概述

本层提供 n8n-mcp 的完整 API 参考文档，包含所有可用的工具、参数说明和返回格式。

## 工具分类

### 1. 节点发现 (Node Discovery)

#### search_nodes

搜索符合条件的 n8n 节点。

**参数**:
```typescript
interface SearchNodesParams {
  query: string;           // 搜索关键词
  filter?: 'built-in' | 'community' | 'all';  // 节点过滤
  limit?: number;         // 返回数量限制
}
```

**返回**:
```typescript
interface SearchNodesResult {
  nodes: Array<{
    id: string;            // 节点 ID
    name: string;          // 节点名称
    displayName: string;   // 显示名称
    typeVersion: number;   // 版本号
    category: string;      // 分类
    description: string;   // 描述
  }>;
  total: number;          // 总数
}
```

**示例**:
```javascript
const result = await search_nodes({
  query: "gmail",
  filter: "built-in",
  limit: 5
});
```

#### get_node

获取特定节点的详细配置信息。

**参数**:
```typescript
interface GetNodeParams {
  nodeType: string;       // 节点类型 (如 @n8n/n8n-nodes-gmail)
  typeVersion?: number;   // 节点版本（可选，默认最新）
}
```

**返回**:
```typescript
interface NodeDetail {
  id: string;
  name: string;
  displayName: string;
  description: string;
  typeVersion: number;
  inputs?: string[];      // 输入类型
  outputs?: string[];     // 输出类型
  properties: Property[]; // 属性列表
  credentials?: Credential[]; // 凭据需求
  defaults?: Record<string, any>; // 默认值
}
```

### 2. 模板管理 (Template Management)

#### search_templates

搜索 n8n.io 上的工作流模板。

**参数**:
```typescript
interface SearchTemplatesParams {
  query: string;           // 搜索关键词
  category?: string;       // 分类
  limit?: number;         // 返回数量限制
}
```

**返回**:
```typescript
interface SearchTemplatesResult {
  templates: Array<{
    id: string;            // 模板 ID
    name: string;          // 模板名称
    category: string;      // 分类
    description: string;   // 描述
    tags: string[];        // 标签
    url: string;           // 模板 URL
    nodes: number;         // 节点数量
  }>;
}
```

#### get_template

获取特定模板的详细信息。

**参数**:
```typescript
interface GetTemplateParams {
  templateId: string;      // 模板 ID
}
```

**返回**:
```typescript
interface TemplateDetail {
  id: string;
  name: string;
  description: string;
  nodes: Node[];          // 节点列表
  connections: Connections; // 连接配置
  settings: WorkflowSettings;
  tags: string[];
}
```

### 3. 工作流 CRUD (Workflow Management)

#### create_workflow

创建新的工作流。

**参数**:
```typescript
interface CreateWorkflowParams {
  workflow: {
    name: string;          // 工作流名称
    nodes: Node[];         // 节点列表
    connections: Connections; // 连接
    settings?: WorkflowSettings;
    staticData?: any;
    tags?: string[];
  };
}
```

**返回**:
```typescript
interface CreateWorkflowResult {
  id: string;             // 工作流 ID
  name: string;
  active: boolean;
  createdAt: string;
}
```

#### update_workflow

更新现有工作流。

**参数**:
```typescript
interface UpdateWorkflowParams {
  workflowId: string;
  workflow: Partial<Workflow>;
}
```

#### delete_workflow

删除工作流。

**参数**:
```typescript
interface DeleteWorkflowParams {
  workflowId: string;
}
```

#### get_workflow

获取工作流详情。

**参数**:
```typescript
interface GetWorkflowParams {
  workflowId: string;
}
```

#### list_workflows

列出所有工作流。

**参数**:
```typescript
interface ListWorkflowsParams {
  active?: boolean;      // 按激活状态过滤
  tags?: string[];        // 按标签过滤
  limit?: number;         // 返回数量限制
}
```

### 4. 执行与验证 (Execution & Validation)

#### execute_workflow

执行工作流。

**参数**:
```typescript
interface ExecuteWorkflowParams {
  workflowId: string;
  data?: any;             // 输入数据
  mode?: 'manual' | 'trigger'; // 执行模式
}
```

**返回**:
```typescript
interface ExecutionResult {
  executionId: string;
  status: 'success' | 'error';
  data?: any;
  error?: string;
  finishedAt?: string;
}
```

#### validate_workflow

验证工作流配置。

**参数**:
```typescript
interface ValidateWorkflowParams {
  workflow: Workflow;     // 工作流对象
}
```

**返回**:
```typescript
interface ValidationResult {
  valid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
}
```

#### get_execution_result

获取执行结果。

**参数**:
```typescript
interface GetExecutionResultParams {
  executionId: string;
}
```

### 5. 版本管理 (Version Management)

#### create_version

创建工作流版本。

**参数**:
```typescript
interface CreateVersionParams {
  workflowId: string;
}
```

#### list_versions

列出版本历史。

**参数**:
```typescript
interface ListVersionsParams {
  workflowId: string;
}
```

#### restore_version

恢复到指定版本。

**参数**:
```typescript
interface RestoreVersionParams {
  workflowId: string;
  versionId: string;
}
```

### 6. 凭据管理 (Credentials Management)

#### list_credentials

列出所有凭据。

**返回**:
```typescript
interface ListCredentialsResult {
  credentials: Array<{
    id: string;
    name: string;
    type: string;
  }>;
}
```

#### create_credential

创建新凭据。

**参数**:
```typescript
interface CreateCredentialParams {
  name: string;
  type: string;
  data: Record<string, any>;
}
```

**注意**: 当前 n8n-mcp 不支持凭据管理，建议使用 REST API。

### 7. 系统工具 (System)

#### health_check

检查 n8n-mcp 服务器健康状态。

**返回**:
```typescript
interface HealthCheckResult {
  status: 'healthy' | 'unhealthy';
  version: string;
  n8nVersion: string;
  connected: boolean;
}
```

## 错误处理

所有工具都可能返回错误：

```typescript
interface MCPError {
  code: string;
  message: string;
  details?: any;
}
```

### 常见错误代码

| 错误代码 | 描述 | 解决方案 |
|----------|------|----------|
| `CONNECTION_ERROR` | 无法连接到 n8n | 检查 URL 和端口 |
| `AUTHENTICATION_ERROR` | 认证失败 | 验证 API Key |
| `NODE_NOT_FOUND` | 节点不存在 | 检查节点类型和版本 |
| `INVALID_WORKFLOW` | 工作流配置无效 | 修正配置错误 |
| `EXECUTION_FAILED` | 工作流执行失败 | 查看执行日志 |

## 使用示例

### 完整工作流创建

```javascript
// 1. 搜索节点
const nodes = await search_nodes({ query: "gmail slack" });

// 2. 获取节点详情
const gmailNode = await get_node({ nodeType: "@n8n/n8n-nodes-gmail" });
const slackNode = await get_node({ nodeType: "@n8n/n8n-nodes-slack" });

// 3. 创建工作流
const workflow = {
  name: "Email to Slack",
  nodes: [
    {
      id: "node-1",
      name: "Schedule Trigger",
      type: "n8n-nodes-base.scheduleTrigger",
      typeVersion: 1.1,
      position: [250, 300]
    },
    // ... 更多节点
  ],
  connections: {}
};

// 4. 创建工作流
const result = await create_workflow({ workflow });

// 5. 验证工作流
const validation = await validate_workflow({ workflow });
console.log('Valid:', validation.valid);

// 6. 激活工作流
await update_workflow({
  workflowId: result.id,
  workflow: { active: true }
});
```

## 速率限制

n8n-mcp 实施以下速率限制：

| 操作类型 | 限制 |
|----------|------|
| 节点搜索 | 60次/分钟 |
| 工作流创建 | 10次/分钟 |
| 工作流执行 | 30次/分钟 |
| 其他操作 | 100次/分钟 |

## 最佳实践

1. **批量操作**: 使用 `search_nodes` 一次性获取所有需要的信息
2. **缓存结果**: 节点和模板信息变化不频繁，可以缓存
3. **错误重试**: 实现指数退避重试机制
4. **验证优先**: 创建工作流前先验证配置
5. **日志记录**: 记录所有 API 调用以便调试

## 相关文档

- [节点发现工具](../tools/node-discovery.md)
- [模板管理工具](../tools/template-management.md)
- [工作流 CRUD](../tools/workflow-crud.md)
- [配置指南](../docs/setup.md)
