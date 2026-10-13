# n8n-mcp 知识库 Layer 3: 节点规划器

## 概述

节点规划器负责将用户需求转换为具体的 n8n 节点配置，包括节点选择、连接规划和参数配置。

## 规划流程

```
用户需求
    ↓
关键词提取 → 标准化映射
    ↓
节点搜索 → search_nodes()
    ↓
节点筛选 → 类型/版本/能力匹配
    ↓
架构设计 → 拓扑结构规划
    ↓
连接规划 → 数据流设计
    ↓
参数配置 → 表单字段填充
    ↓
最终方案 → 可执行节点配置
```

## 关键词到节点映射

### 标准化映射表

```javascript
const keywordToNodeMapping = {
  // 邮件相关
  email: {
    nodes: ['@n8n/n8n-nodes-gmail', 'n8n-nodes-base.emailSend', '@n8n/n8n-nodes-sendgrid'],
    default: '@n8n/n8n-nodes-gmail'
  },
  mail: {
    nodes: ['@n8n/n8n-nodes-gmail', 'n8n-nodes-base.emailSend'],
    default: '@n8n/n8n-nodes-gmail'
  },
  gmail: {
    nodes: ['@n8n/n8n-nodes-gmail'],
    default: '@n8n/n8n-nodes-gmail'
  },

  // 消息相关
  message: {
    nodes: ['@n8n/n8n-nodes-slack', '@n8n/n8n-nodes-discord', '@n8n/n8n-nodes-telegram'],
    default: '@n8n/n8n-nodes-slack'
  },
  slack: {
    nodes: ['@n8n/n8n-nodes-slack'],
    default: '@n8n/n8n-nodes-slack'
  },
  discord: {
    nodes: ['@n8n/n8n-nodes-discord'],
    default: '@n8n/n8n-nodes-discord'
  },

  // 存储相关
  database: {
    nodes: ['n8n-nodes-base.postgres', 'n8n-nodes-base.mySql', 'n8n-nodes-base.mongoDb'],
    default: 'n8n-nodes-base.postgres'
  },
  postgres: {
    nodes: ['n8n-nodes-base.postgres'],
    default: 'n8n-nodes-base.postgres'
  },
  mysql: {
    nodes: ['n8n-nodes-base.mySql'],
    default: 'n8n-nodes-base.mySql'
  },
  mongodb: {
    nodes: ['n8n-nodes-base.mongoDb'],
    default: 'n8n-nodes-base.mongoDb'
  },

  // API 相关
  api: {
    nodes: ['n8n-nodes-base.httpRequest'],
    default: 'n8n-nodes-base.httpRequest'
  },
  webhook: {
    nodes: ['n8n-nodes-base.webhook'],
    default: 'n8n-nodes-base.webhook'
  },
  rest: {
    nodes: ['n8n-nodes-base.httpRequest'],
    default: 'n8n-nodes-base.httpRequest'
  },

  // 数据处理
  transform: {
    nodes: ['n8n-nodes-base.set', 'n8n-nodes-base.code', 'n8n-nodes-base.function'],
    default: 'n8n-nodes-base.set'
  },
  filter: {
    nodes: ['n8n-nodes-base.filter'],
    default: 'n8n-nodes-base.filter'
  },
  split: {
    nodes: ['n8n-nodes-base.splitInBatches'],
    default: 'n8n-nodes-base.splitInBatches'
  },

  // 触发器
  schedule: {
    nodes: ['n8n-nodes-base.scheduleTrigger'],
    default: 'n8n-nodes-base.scheduleTrigger'
  },
  cron: {
    nodes: ['n8n-nodes-base.scheduleTrigger'],
    default: 'n8n-nodes-base.scheduleTrigger'
  },
  interval: {
    nodes: ['n8n-nodes-base.scheduleTrigger'],
    default: 'n8n-nodes-base.scheduleTrigger'
  },

  // AI/ML
  openai: {
    nodes: ['@n8n/n8n-nodes-langchain'],
    default: '@n8n/n8n-nodes-langchain'
  },
  ai: {
    nodes: ['@n8n/n8n-nodes-langchain', 'n8n-nodes-base.openai'],
    default: '@n8n/n8n-nodes-langchain'
  },

  // 文件处理
  file: {
    nodes: ['n8n-nodes-base.readBinaryFile', 'n8n-nodes-base.writeBinaryFile'],
    default: 'n8n-nodes-base.readBinaryFile'
  },
  pdf: {
    nodes: ['@n8n/n8n-nodes-pdf'],
    default: '@n8n/n8n-nodes-pdf'
  }
};
```

### 关键词提取与标准化

```javascript
// 提取关键词
function extractKeywords(userInput) {
  const text = userInput.toLowerCase();

  // 使用正则提取关键词
  const patterns = {
    email: /\b(email|mail|send.*mail|gmail)\b/g,
    message: /\b(message|notify|send.*message|slack|discord)\b/g,
    database: /\b(database|db|store|save|persist)\b/g,
    api: /\b(api|request|fetch|http|rest|webhook)\b/g,
    schedule: /\b(schedule|cron|interval|daily|hourly)\b/g,
    transform: /\b(transform|convert|map|format)\b/g,
    filter: /\b(filter|where|only|if)\b/g,
    ai: /\b(ai|openai|gpt|chat|llm)\b/g
  };

  const keywords = new Set();

  for (const [type, pattern] of Object.entries(patterns)) {
    const matches = text.match(pattern);
    if (matches) {
      matches.forEach(m => keywords.add(type));
    }
  }

  return Array.from(keywords);
}

// 标准化关键词
function standardizeKeywords(keywords) {
  const normalized = new Map();

  for (const keyword of keywords) {
    const mapping = keywordToNodeMapping[keyword];
    if (mapping) {
      normalized.set(keyword, mapping);
    }
  }

  return normalized;
}
```

## 节点搜索与选择

### 智能节点搜索

```javascript
// 搜索候选节点
async function findCandidateNodes(keywords) {
  const candidates = new Map();

  for (const [keyword, mapping] of keywords.entries()) {
    // 使用 MCP 搜索节点
    const searchResult = await search_nodes({
      query: keyword,
      filter: 'all',
      limit: 10
    });

    // 合并结果
    for (const node of searchResult.nodes) {
      if (!candidates.has(node.id)) {
        candidates.set(node.id, {
          ...node,
          matchedKeywords: [],
          score: 0
        });
      }

      const candidate = candidates.get(node.id);
      candidate.matchedKeywords.push(keyword);
      candidate.score += calculateRelevanceScore(node, keyword);
    }
  }

  // 按得分排序
  return Array.from(candidates.values())
    .sort((a, b) => b.score - a.score);
}

// 计算相关性得分
function calculateRelevanceScore(node, keyword) {
  let score = 0;

  // 名称匹配
  if (node.name.toLowerCase().includes(keyword)) {
    score += 10;
  }

  // 描述匹配
  if (node.description && node.description.toLowerCase().includes(keyword)))) {
    score += 5;
  }

  // 类别匹配
  if (node.category && node.category.toLowerCase().includes(keyword)) {
    score += 3;
  }

  // 内置节点优先
  if (!node.id.startsWith('@n8n/n8n-nodes-community')) {
    score += 2;
  }

  return score;
}
```

### 节点筛选策略

```javascript
// 筛选最佳节点
async function selectBestNodes(candidates, requirements) {
  const selections = [];

  // 按功能分组
  const grouped = groupByFunction(candidates);

  for (const [function_, nodes] of Object.entries(grouped)) {
    // 应用筛选规则
    let filtered = nodes;

    // 1. 类型匹配
    filtered = filterByType(filtered, requirements.expectedType);

    // 2. 版本兼容性
    filtered = filterByVersion(filtered, requirements.n8nVersion);

    // 3. 能力匹配
    filtered = filterByCapability(filtered, requirements.capabilities);

    // 4. 凭据可用性
    filtered = await filterByCredentials(filtered);

    // 选择最高分的节点
    if (filtered.length > 0) {
      selections.push({
        function: function_,
        selected: filtered[0],
        alternatives: filtered.slice(1, 4) // 保留备选
      });
    }
  }

  return selections;
}

// 按功能分组
function groupByFunction(nodes) {
  const groups = {};

  for (const node of nodes) {
    const func = inferNodeFunction(node);
    if (!groups[func]) {
      groups[func] = [];
    }
    groups[func].push(node);
  }

  return groups;
}

// 推断节点功能
function inferNodeFunction(node) {
  const name = node.name.toLowerCase();

  if (name.includes('trigger') || name.includes('schedule')) {
    return 'trigger';
  } else if (name.includes('webhook')) {
    return 'webhook';
  } else if (name.includes('email') || name.includes('mail')) {
    return 'email';
  } else if (name.includes('slack') || name.includes('discord')) {
    return 'messaging';
  } else if (name.includes('database') || name.includes('postgres') || name.includes('mysql')) {
    return 'database';
  } else if (name.includes('http') || name.includes('request')) {
    return 'api';
  } else if (name.includes('code') || name.includes('function')) {
    return 'transformation';
  } else if (name.includes('filter') || name.includes('if')) {
    return 'conditional';
  } else {
    return 'general';
  }
}
```

## 架构设计

### 拓扑结构规划

```javascript
// 设计工作流拓扑
function designTopology(requirements, selectedNodes) {
  const topology = {
    nodes: [],
    connections: {}
  };

  // 1. 确定触发节点
  const triggerNode = findTriggerNode(selectedNodes, requirements.trigger);
  if (triggerNode) {
    topology.nodes.push(createNodeConfig(triggerNode, 'trigger'));
  }

  // 2. 确定输入处理节点
  const inputNodes = findInputNodes(selectedNodes, requirements.inputs);
  inputNodes.forEach(node => {
    topology.nodes.push(createNodeConfig(node, 'input'));
  });

  // 3. 确定处理节点
  const processNodes = findProcessNodes(selectedNodes, requirements.processing);
  processNodes.forEach(node => {
    topology.nodes.push(createNodeConfig(node, 'process'));
  });

  // 4. 确定输出节点
  const outputNodes = findOutputNodes(selectedNodes, requirements.outputs);
  outputNodes.forEach(node => {
    topology.nodes.push(createNodeConfig(node, 'output'));
  });

  // 5. 设计连接
  topology.connections = designConnections(topology.nodes, requirements);

  return topology;
}

// 设计连接
function designConnections(nodes, requirements) {
  const connections = {};
  const nodeIds = nodes.map(n => n.id);

  // 创建线性连接链
  for (let i = 0; i < nodeIds.length - 1; i++) {
    const from = nodes[i];
    const to = nodes[i + 1];

    connections[from.name] = {
      main: [[{
        node: to.name,
        type: 'main',
        index: 0
      }]]
    };
  }

  // 添加分支连接（如果需要）
  if (requirements.branching) {
    addBranchConnections(connections, nodes, requirements.branching);
  }

  return connections;
}
```

### 数据流设计

```javascript
// 设计数据流
function designDataFlow(topology, requirements) {
  const dataFlow = {
    stages: [],
    transformations: []
  };

  // 分析每个阶段的数据转换
  for (let i = 0; i < topology.nodes.length; i++) {
    const node = topology.nodes[i];
    const stage = {
      nodeId: node.id,
      nodeName: node.name,
      inputSchema: inferInputSchema(node),
      outputSchema: inferOutputSchema(node),
      transformation: inferTransformation(node)
    };

    dataFlow.stages.push(stage);

    if (stage.transformation) {
      dataFlow.transformations.push(stage.transformation);
    }
  }

  return dataFlow;
}

// 推断输入模式
function inferInputSchema(node) {
  // 根据节点类型推断输入结构
  const typeInference = {
    'trigger': null, // 触发器无输入
    'webhook': { body: 'object', query: 'object', headers: 'object' },
    'httpRequest': { url: 'string', method: 'string', body: 'object' },
    'email': { to: 'string', subject: 'string', text: 'string' },
    'database': { query: 'string', params: 'array' },
    'code': { json: 'object' }, // Code 节点接受任意 JSON
    'set': { json: 'object' }
  };

  const func = inferNodeFunction(node);
  return typeInference[func] || { json: 'object' };
}
```

## 参数配置规划

### 表单字段生成

```javascript
// 生成节点参数配置
async function generateNodeParameters(node, requirements) {
  // 获取节点详细信息
  const nodeDetails = await get_node({
    nodeType: node.id,
    typeVersion: node.typeVersion
  });

  const parameters = {};

  // 分析必需参数
  for (const prop of nodeDetails.properties) {
    if (prop.required) {
      parameters[prop.name] = await planParameterValue(prop, requirements);
    }
  }

  // 添加可选参数（如果有默认值）
  for (const prop of nodeDetails.properties) {
    if (!prop.required && prop.default !== undefined) {
      parameters[prop.name] = prop.default;
    }
  }

  return parameters;
}

// 规划参数值
async function planParameterValue(property, requirements) {
  const { name, type, options } = property;

  switch (type) {
    case 'string':
      return planStringValue(name, requirements);

    case 'number':
      return planNumberValue(name, requirements);

    case 'boolean':
      return planBooleanValue(name, requirements);

    case 'options':
      return planOptionsValue(name, options, requirements);

    case 'collection':
      return planCollectionValue(name, requirements);

    default:
      return null;
  }
}
```

### 表达式规划

```javascript
// 规划表达式使用
function planExpressions(topology, requirements) {
  const expressions = [];

  for (const node of topology.nodes) {
    // 查找需要动态值的参数
    const dynamicParams = findDynamicParameters(node);

    for (const param of dynamicParams) {
      const expression = {
        nodeId: node.id,
        parameter: param.name,
        expression: generateExpression(param, requirements),
        sourceNode: findSourceNode(node, param, topology)
      };

      expressions.push(expression);
    }
  }

  return expressions;
}

// 生成表达式
function generateExpression(parameter, requirements) {
  // 根据参数类型生成适当的表达式
  switch (parameter.type) {
    case 'string':
      return `{{ $json.${parameter.name} }}`;

    case 'number':
      return `{{ $json.${parameter.name} || 0 }}`;

    case 'dateTime':
      return '={{ $now.toISO() }}';

    default:
      return `{{ $json.${parameter.name} }}`;
  }
}
```

## Code 节点规划

### Code 节点生成

```javascript
// 为复杂逻辑规划 Code 节点
function planCodeNodes(requirements, topology) {
  const codeNodes = [];

  // 1. 数据转换节点
  if (needsDataTransformation(requirements)) {
    codeNodes.push({
      name: 'Transform Data',
      language: detectLanguage(requirements),
      code: generateTransformationCode(requirements.transform),
      position: calculatePosition(topology, 'transform')
    });
  }

  // 2. 聚合节点
  if (needsAggregation(requirements)) {
    codeNodes.push({
      name: 'Aggregate Data',
      language: 'javascript',
      code: generateAggregationCode(requirements.aggregation),
      position: calculatePosition(topology, 'aggregate')
    });
  }

  // 3. 验证节点
  if (needsValidation(requirements)) {
    codeNodes.push({
      name: 'Validate Data',
      language: 'javascript',
      code: generateValidationCode(requirements.validation),
      position: calculatePosition(topology, 'validate')
    });
  }

  return codeNodes;
}
```

## 完整规划输出

### 生成规划文档

```javascript
// 生成完整规划
async function generatePlan(requirements) {
  // 1. 提取关键词
  const keywords = extractKeywords(requirements.description);
  const normalized = standardizeKeywords(keywords);

  // 2. 搜索节点
  const candidates = await findCandidateNodes(normalized);

  // 3. 选择最佳节点
  const selectedNodes = await selectBestNodes(candidates, requirements);

  // 4. 设计拓扑
  const topology = designTopology(requirements, selectedNodes);

  // 5. 规划数据流
  const dataFlow = designDataFlow(topology, requirements);

  // 6. 规划参数
  const parameters = await Promise.all(
    selectedNodes.map(node =>
      generateNodeParameters(node, requirements)
    )
  );

  // 7. 规划表达式
  const expressions = planExpressions(topology, requirements);

  // 8. 规划 Code 节点
  const codeNodes = planCodeNodes(requirements, topology);

  return {
    summary: generatePlanSummary(selectedNodes, topology),
    nodes: selectedNodes,
    topology: topology,
    dataFlow: dataFlow,
    parameters: parameters,
    expressions: expressions,
    codeNodes: codeNodes,
    estimatedComplexity: calculateComplexity(topology),
    recommendations: generateRecommendations(selectedNodes, requirements)
  };
}
```

## 相关文档

- [10步流程编排器](layer3-orchestrator.md)
- [用户意图适配器](layer3-adapter.md)
- [节点发现工具](../tools/node-discovery.md)
- [核心模式](../patterns/core-patterns.md)
