# n8n 工作流验证规则

## 节点级验证

### 必需字段检查

每个节点必须包含以下字段：

```javascript
const requiredFields = ['id', 'name', 'type', 'typeVersion', 'position'];

function validateNode(node) {
  const missing = requiredFields.filter(field => !node[field]);
  if (missing.length > 0) {
    throw new Error(`节点 ${node.name} 缺少必需字段: ${missing.join(', ')}`);
  }
  return true;
}
```

### ID 唯一性验证

节点 ID 必须唯一：

```javascript
function validateUniqueIds(nodes) {
  const ids = nodes.map(n => n.id);
  const duplicates = ids.filter((id, index) => ids.indexOf(id) !== index);

  if (duplicates.length > 0) {
    throw new Error(`重复的节点 ID: ${duplicates.join(', ')}`);
  }
  return true;
}
```

### 位置有效性验证

节点位置必须在合理范围内：

```javascript
function validatePosition(node) {
  const { position } = node;
  if (!position || position.length !== 2) {
    throw new Error(`节点 ${node.name} 位置配置无效`);
  }

  const [x, y] = position;
  if (x < 0 || y < 0 || x > 5000 || y > 5000) {
    throw new Error(`节点 ${node.name} 位置超出合理范围`);
  }
  return true;
}
```

## 连接级验证

### 连接完整性验证

所有连接的节点必须存在：

```javascript
function validateConnections(workflow) {
  const nodeIds = new Set(workflow.nodes.map(n => n.id));

  for (const [sourceId, connections] of Object.entries(workflow.connections)) {
    if (!nodeIds.has(sourceId)) {
      throw new Error(`连接源节点不存在: ${sourceId}`);
    }

    for (const connectionList of Object.values(connections)) {
      for (const connection of connectionList) {
        if (!nodeIds.has(connection.node)) {
          throw new Error(`连接目标节点不存在: ${connection.node}`);
        }
      }
    }
  }
  return true;
}
```

### 连接类型验证

连接类型必须有效：

```javascript
const validConnectionTypes = ['main', 'ai'];

function validateConnectionTypes(workflow) {
  for (const [sourceId, connections] of Object.entries(workflow.connections)) {
    for (const [type, connectionList] of Object.entries(connections)) {
      if (!validConnectionTypes.includes(type)) {
        throw new Error(`无效的连接类型: ${type}`);
      }
    }
  }
  return true;
}
```

### 孤立节点检测

除了触发器，所有节点都应该有连接：

```javascript
function detectOrphanNodes(workflow) {
  const connectedIds = new Set();

  // 收集所有已连接的节点
  for (const connections of Object.values(workflow.connections)) {
    for (const connectionList of Object.values(connections)) {
      for (const connection of connectionList) {
        connectedIds.add(connection.node);
      }
    }
  }

  // 找出孤立节点
  const orphans = workflow.nodes.filter(node => {
    // 触发器可以是孤立的
    if (node.type.includes('Trigger')) return false;
    // 其他节点必须有连接
    return !connectedIds.has(node.id);
  });

  if (orphans.length > 0) {
    console.warn(`发现孤立节点: ${orphans.map(n => n.name).join(', ')}`);
  }

  return orphans;
}
```

## 工作流级验证

### 触发器存在性验证

工作流必须有至少一个触发器：

```javascript
function validateTrigger(workflow) {
  const hasTrigger = workflow.nodes.some(node =>
    node.type.includes('Trigger') || node.type.includes('Webhook')
  );

  if (!hasTrigger) {
    throw new Error('工作流必须包含至少一个触发器');
  }
  return true;
}
```

### 循环依赖检测

检测工作流中是否存在循环：

```javascript
function detectCycles(workflow) {
  const graph = buildGraph(workflow);
  const visited = new Set();
  const recursionStack = new Set();

  function dfs(nodeId) {
    if (recursionStack.has(nodeId)) {
      throw new Error(`检测到循环依赖，涉及节点: ${nodeId}`);
    }
    if (visited.has(nodeId)) return;

    visited.add(nodeId);
    recursionStack.add(nodeId);

    const neighbors = graph[nodeId] || [];
    for (const neighbor of neighbors) {
      dfs(neighbor);
    }

    recursionStack.delete(nodeId);
  }

  for (const nodeId of Object.keys(graph)) {
    if (!visited.has(nodeId)) {
      dfs(nodeId);
    }
  }

  return true;
}

function buildGraph(workflow) {
  const graph = {};
  for (const [sourceId, connections] of Object.entries(workflow.connections)) {
    graph[sourceId] = [];
    for (const connectionList of Object.values(connections)) {
      for (const connection of connectionList) {
        graph[sourceId].push(connection.node);
      }
    }
  }
  return graph;
}
```

## 表达式验证

### 语法验证

验证 n8n 表达式语法：

```javascript
function validateExpression(expression) {
  // 检查基本格式
  if (!expression.startsWith('{{') || !expression.endsWith('}}')) {
    if (expression.includes('{{')) {
      throw new Error('表达式格式错误: 必须以 {{ 开始 }} 结束');
    }
  }

  // 检查嵌套表达式
  const nestedCount = (expression.match(/\{\{/g) || []).length;
  if (nestedCount > 1) {
    throw new Error('不支持嵌套表达式');
  }

  return true;
}
```

### 节点引用验证

验证节点引用是否存在：

```javascript
function validateNodeReferences(workflow) {
  const nodeNames = new Set(workflow.nodes.map(n => n.name));

  // 在所有表达式和字段中查找节点引用
  for (const node of workflow.nodes) {
    const nodeJson = JSON.stringify(node);
    const references = nodeJson.match(/\$node\[['"]([^'"]+)['"]\]/g);

    if (references) {
      for (const ref of references) {
        const match = ref.match(/\$node\[['"]([^'"]+)['"]\]/);
        if (match && !nodeNames.has(match[1])) {
          throw new Error(`无效的节点引用: ${match[1]}`);
        }
      }
    }
  }

  return true;
}
```

## 凭据验证

### 凭据类型匹配

凭据类型必须与节点匹配：

```javascript
function validateCredentials(workflow) {
  const credentialTypes = {
    'n8n-nodes-base.gmail': ['gmailOAuth2'],
    'n8n-nodes-base.slack': ['slackApi'],
    'n8n-nodes-base.openAi': ['openAiApi'],
    // ... 更多映射
  };

  for (const node of workflow.nodes) {
    if (node.credentials) {
      const nodeType = node.type.split('.').pop();
      const expectedTypes = credentialTypes[nodeType];

      if (!expectedTypes) {
        console.warn(`未知节点类型的凭据要求: ${nodeType}`);
        continue;
      }

      for (const [credType] of Object.entries(node.credentials)) {
        if (!expectedTypes.includes(credType)) {
          throw new Error(`节点 ${node.name} 的凭据类型不匹配: 期望 ${expectedTypes.join(' 或 ')}, 实际 ${credType}`);
        }
      }
    }
  }

  return true;
}
```

## 性能验证

### 批量处理验证

检查是否有合理的批量配置：

```javascript
function validateBatchProcessing(workflow) {
  const splitBatchNodes = workflow.nodes.filter(n =>
    n.type === 'n8n-nodes-base.splitInBatches'
  );

  for (const node of splitBatchNodes) {
    const batchSize = node.parameters?.batchSize;
    if (!batchSize || batchSize < 1 || batchSize > 1000) {
      throw new Error(`Split In Batches 节点 ${node.name} 的批量大小无效: ${batchSize}`);
    }
  }

  return true;
}
```

### API 限流检查

检查是否有可能触发限流：

```javascript
function checkRateLimitRisk(workflow) {
  const apiCallNodes = workflow.nodes.filter(n =>
    n.type === 'n8n-nodes-base.httpRequest' ||
    n.type.includes('api')
  );

  if (apiCallNodes.length > 10) {
    console.warn('工作流包含大量 API 调用节点，可能触发限流');
  }

  // 检查是否有 Wait 节点防止限流
  const hasWaitNodes = workflow.nodes.some(n =>
    n.type === 'n8n-nodes-base.wait'
  );

  if (apiCallNodes.length > 5 && !hasWaitNodes) {
    console.warn('多个 API 调用但没有 Wait 节点，建议添加延迟');
  }

  return true;
}
```

## 安全验证

### 敏感信息检查

检查是否有硬编码的敏感信息：

```javascript
function validateSecurity(workflow) {
  const sensitivePatterns = [
    /"apiKey":\s*"[^"]+"/i,
    /"secret":\s*"[^"]+"/i,
    /"password":\s*"[^"]+"/i,
    /"token":\s*"[^"]+"/i,
    /sk-[a-zA-Z0-9]{32,}/,  // OpenAI API key
    /xox[bap]-[a-zA-Z0-9-]{10,}/,  // Slack token
  ];

  const workflowJson = JSON.stringify(workflow);

  for (const pattern of sensitivePatterns) {
    const matches = workflowJson.match(pattern);
    if (matches) {
      throw new Error(`检测到可能的硬编码敏感信息: ${matches[0]}`);
    }
  }

  return true;
}
```

## 完整验证函数

```javascript
function validateWorkflow(workflow) {
  const validations = [
    validateNodeStructure,
    validateConnections,
    validateTrigger,
    validateNoCycles,
    validateExpressions,
    validateCredentials,
    validateSecurity,
    validatePerformance
  ];

  const results = [];

  for (const validation of validations) {
    try {
      validation(workflow);
      results.push({ name: validation.name, status: 'pass' });
    } catch (error) {
      results.push({ name: validation.name, status: 'fail', error: error.message });
    }
  }

  return {
    valid: results.every(r => r.status === 'pass'),
    results
  };
}
```

## 验证报告示例

```json
{
  "valid": true,
  "results": [
    { "name": "validateNodeStructure", "status": "pass" },
    { "name": "validateConnections", "status": "pass" },
    { "name": "validateTrigger", "status": "pass" },
    { "name": "validateNoCycles", "status": "pass" },
    { "name": "validateExpressions", "status": "pass" },
    { "name": "validateCredentials", "status": "pass" },
    { "name": "validateSecurity", "status": "pass" },
    { "name": "validatePerformance", "status": "warning", "message": "建议添加 Wait 节点" }
  ]
}
```

## 相关文档

- [错误目录](error-catalog.md)
- [编排模式](../patterns/orchestration-patterns.md)
- [节点配置规范](../specs/node-configuration.md)
