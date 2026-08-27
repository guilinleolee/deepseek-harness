# n8n-mcp 验证与执行工具

## 工具概述

n8n-mcp 提供工作流验证、执行和执行结果获取功能，确保工作流正确运行。

## 可用工具

### 1. validate_workflow

验证工作流配置的正确性。

**参数**:
```javascript
{
  "workflow": {
    "name": "My Workflow",
    "nodes": [...],
    "connections": {...},
    "settings": {...}
  }
}
```

**返回**:
```javascript
{
  "valid": true,                    // 是否通过验证
  "errors": [                       // 错误列表
    {
      "node": "Send Email",
      "type": "MISSING_PARAMETER",
      "message": "Required parameter 'toEmail' is missing"
    }
  ],
  "warnings": [                    // 警告列表
    {
      "node": "Schedule Trigger",
      "type": "DEPRECATED_VERSION",
      "message": "Consider upgrading to version 1.2"
    }
  ]
}
```

**使用示例**:
```javascript
// 验证工作流配置
const validation = await validate_workflow({
  workflow: myWorkflowConfig
});

if (!validation.valid) {
  console.error('Validation failed:');
  validation.errors.forEach(err => {
    console.error(`  [${err.node}] ${err.type}: ${err.message}`);
  });
}

// 检查警告
if (validation.warnings.length > 0) {
  console.warn('Warnings:');
  validation.warnings.forEach(warn => {
    console.warn(`  [${warn.node}] ${warn.type}: ${warn.message}`);
  });
}
```

**验证类型**:
- **节点级验证**: 检查必需参数、数据类型、取值范围
- **连接验证**: 检查节点连接是否有效
- **表达式验证**: 检查表达式语法正确性
- **凭据验证**: 检查所需凭据是否配置
- **性能验证**: 检查潜在的性能问题

### 2. execute_workflow

执行工作流。

**参数**:
```javascript
{
  "workflowId": "1234",             // 工作流 ID
  "data": {                         // 可选：输入数据
    "key": "value"
  },
  "mode": "manual"                  // 执行模式: manual | trigger
}
```

**返回**:
```javascript
{
  "executionId": "exec-5678",       // 执行 ID
  "status": "success",              // 状态: success | error | running
  "data": {...},                    // 输出数据
  "error": null,                    // 错误信息（如果有）
  "finishedAt": "2024-01-01T00:00:01.000Z"
}
```

**使用示例**:
```javascript
// 手动执行工作流
const result = await execute_workflow({
  workflowId: "1234",
  mode: "manual",
  data: {
    email: "user@example.com",
    message: "Hello!"
  }
});

if (result.status === "success") {
  console.log('Workflow executed successfully');
  console.log('Output:', result.data);
} else if (result.status === "error") {
  console.error('Execution failed:', result.error);
} else {
  console.log('Workflow is still running...');
  // 使用 get_execution_result 获取结果
}
```

**执行模式**:
- **manual**: 手动执行，直接触发工作流
- **trigger**: 触发器模式，通过触发器节点启动

### 3. get_execution_result

获取执行结果（用于异步执行）。

**参数**:
```javascript
{
  "executionId": "exec-5678"
}
```

**返回**:
```javascript
{
  "executionId": "exec-5678",
  "status": "success",              // success | error | running
  "data": {...},
  "error": null,
  "finishedAt": "2024-01-01T00:00:01.000Z",
  "startedAt": "2024-01-01T00:00:00.000Z",
  "runtime": "1.234s"               // 运行时长
}
```

**使用示例**:
```javascript
// 轮询执行结果
async function waitForExecution(executionId, timeout = 60000) {
  const startTime = Date.now();

  while (Date.now() - startTime < timeout) {
    const result = await get_execution_result({ executionId });

    if (result.status === 'success') {
      return { success: true, data: result.data };
    } else if (result.status === 'error') {
      return { success: false, error: result.error };
    }

    // 等待 1 秒后重试
    await new Promise(resolve => setTimeout(resolve, 1000));
  }

  throw new Error('Execution timeout');
}

// 使用
const execution = await execute_workflow({
  workflowId: "1234",
  mode: "manual"
});

const finalResult = await waitForExecution(execution.executionId);
```

## 使用场景

### 场景1: 部署前验证

```
验证流程:
1. validate_workflow() - 验证配置
2. 检查错误和警告
3. 修复所有问题
4. 再次验证确保通过
5. 部署工作流
```

### 场景2: 测试执行

```
测试流程:
1. execute_workflow({mode: "manual"}) - 手动测试
2. get_execution_result() - 获取结果
3. 验证输出数据
4. 检查执行日志
5. 修复问题后重测
```

### 场景3: 批量验证

```javascript
// 验证多个工作流
async function batchValidate(workflows) {
  const results = [];

  for (const workflow of workflows) {
    const validation = await validate_workflow({ workflow });
    results.push({
      name: workflow.name,
      valid: validation.valid,
      errors: validation.errors.length,
      warnings: validation.warnings.length
    });
  }

  return results;
}
```

### 场景4: 监控执行

```javascript
// 监控长时间运行的工作流
async function monitorExecution(executionId) {
  let lastStatus = 'unknown';

  while (true) {
    const result = await get_execution_result({ executionId });

    if (result.status !== lastStatus) {
      console.log(`Status changed: ${lastStatus} → ${result.status}`);
      lastStatus = result.status;
    }

    if (result.status === 'success') {
      console.log('Execution completed successfully');
      return result.data;
    } else if (result.status === 'error') {
      console.error('Execution failed:', result.error);
      throw new Error(result.error);
    }

    // 等待 2 秒后检查
    await new Promise(resolve => setTimeout(resolve, 2000));
  }
}
```

## 错误类型与处理

### 常见验证错误

| 错误类型 | 描述 | 解决方案 |
|----------|------|----------|
| `MISSING_PARAMETER` | 缺少必需参数 | 补充参数值 |
| `INVALID_TYPE` | 参数类型错误 | 修正参数类型 |
| `INVALID_CONNECTION` | 连接无效 | 检查节点 ID 和连接类型 |
| `EXPRESSION_SYNTAX` | 表达式语法错误 | 修正表达式 |
| `CREDENTIAL_MISSING` | 凭据未配置 | 配置所需凭据 |
| `NODE_NOT_FOUND` | 节点不存在 | 检查节点类型 |

### 常见执行错误

| 错误类型 | 描述 | 解决方案 |
|----------|------|----------|
| `TIMEOUT` | 执行超时 | 增加 timeout 或优化工作流 |
| `RATE_LIMIT` | API 速率限制 | 添加延迟或重试逻辑 |
| `AUTHENTICATION` | 认证失败 | 检查凭据配置 |
| `DATA_ERROR` | 数据处理错误 | 验证输入数据格式 |
| `NODE_ERROR` | 节点执行失败 | 查看节点日志和错误消息 |

## 最佳实践

### 1. 验证优先

```javascript
// 总是先验证再执行
async function safeExecute(workflowId, data) {
  // 1. 获取工作流
  const workflow = await get_workflow({ workflowId });

  // 2. 验证配置
  const validation = await validate_workflow({ workflow });
  if (!validation.valid) {
    throw new Error('Workflow validation failed');
  }

  // 3. 执行工作流
  return await execute_workflow({ workflowId, data });
}
```

### 2. 错误重试

```javascript
// 指数退避重试
async function executeWithRetry(workflowId, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const result = await execute_workflow({ workflowId });

      if (result.status === 'success') {
        return result.data;
      }

      // 如果是特定错误，重试
      if (isRetryableError(result.error)) {
        const delay = Math.pow(2, attempt) * 1000;
        console.log(`Attempt ${attempt} failed, retrying in ${delay}ms...`);
        await new Promise(resolve => setTimeout(resolve, delay));
        continue;
      }

      throw new Error(result.error);

    } catch (error) {
      if (attempt === maxRetries) {
        throw error;
      }
      console.error(`Attempt ${attempt} error:`, error.message);
    }
  }
}

function isRetryableError(error) {
  const retryableErrors = [
    'TIMEOUT',
    'RATE_LIMIT',
    'CONNECTION_ERROR'
  ];
  return retryableErrors.some(type => error.includes(type));
}
```

### 3. 数据验证

```javascript
// 验证执行结果
async function executeAndValidate(workflowId, input, schema) {
  const result = await execute_workflow({
    workflowId,
    data: input
  });

  if (result.status !== 'success') {
    throw new Error(result.error);
  }

  // 验证输出数据
  const validationResult = validateSchema(result.data, schema);
  if (!validationResult.valid) {
    throw new Error('Output validation failed');
  }

  return result.data;
}
```

### 4. 执行历史记录

```javascript
// 记录执行历史
const executionLog = [];

async function executeWithLogging(workflowId, data) {
  const startTime = Date.now();

  try {
    const result = await execute_workflow({ workflowId, data });

    executionLog.push({
      timestamp: new Date().toISOString(),
      workflowId,
      status: result.status,
      runtime: Date.now() - startTime,
      success: result.status === 'success'
    });

    return result;

  } catch (error) {
    executionLog.push({
      timestamp: new Date().toISOString(),
      workflowId,
      status: 'error',
      runtime: Date.now() - startTime,
      error: error.message
    });

    throw error;
  }
}
```

## 性能优化

### 1. 批量执行

```javascript
// 并行执行多个工作流
async function batchExecute(workflowIds, concurrency = 5) {
  const results = [];
  const chunks = chunk(workflowIds, concurrency);

  for (const chunk of chunks) {
    const chunkResults = await Promise.all(
      chunk.map(id => execute_workflow({ workflowId: id }))
    );
    results.push(...chunkResults);
  }

  return results;
}

function chunk(array, size) {
  const chunks = [];
  for (let i = 0; i < array.length; i += size) {
    chunks.push(array.slice(i, i + size));
  }
  return chunks;
}
```

### 2. 缓存验证结果

```javascript
// 缓存验证结果
const validationCache = new Map();

async function cachedValidation(workflow) {
  const cacheKey = JSON.stringify(workflow);

  if (validationCache.has(cacheKey)) {
    return validationCache.get(cacheKey);
  }

  const result = await validate_workflow({ workflow });
  validationCache.set(cacheKey, result);

  return result;
}
```

## 相关文档

- [节点发现工具](node-discovery.md)
- [模板管理工具](template-management.md)
- [工作流 CRUD](workflow-crud.md)
- [完整 API 参考](../reference/layer2-mcp.md)
- [验证规则](../rules/validation-rules.md)
- [错误目录](../rules/error-catalog.md)
