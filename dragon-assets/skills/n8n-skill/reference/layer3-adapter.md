# n8n-mcp 知识库 Layer 3: 用户意图适配器

## 概述

用户意图适配器是 Layer 3 的关键组件，负责将用户的自然语言需求转换为可执行的 MCP 工具调用序列。

## 适配器架构

```
用户输入
    ↓
意图分析 → 类型识别 / 复杂度评估
    ↓
需求提取 → 结构化参数
    ↓
策略选择 → 直接模式 vs. 完整模式
    ↓
MCP 映射 → 工具调用序列
    ↓
结果组装 → 返回用户
```

## 意图分析

### 意图类型识别

```javascript
// 意图分类器
function classifyIntent(userInput) {
  const input = userInput.toLowerCase();

  // 简单查询类意图
  if (isQueryIntent(input)) {
    return {
      type: 'query',
      subType: identifyQueryType(input),
      complexity: 'simple',
      requiresPlanning: false
    };
  }

  // 工作流构建类意图
  if (isBuildIntent(input)) {
    return {
      type: 'build',
      subType: identifyBuildType(input),
      complexity: assessComplexity(input),
      requiresPlanning: true
    };
  }

  // 学习探索类意图
  if (isLearningIntent(input)) {
    return {
      type: 'learning',
      subType: identifyLearningType(input),
      complexity: 'medium',
      requiresPlanning: false
    };
  }

  // 默认为未知意图
  return {
    type: 'unknown',
    complexity: 'unknown',
    requiresPlanning: false
  };
}

// 检测查询意图
function isQueryIntent(input) {
  const queryPatterns = [
    /如何/, /怎么/, /how.*to/i,
    /搜索/, /查找/, /find/i, /search/i,
    /有哪些/, /what/i, /list/i,
    /节点/, /node/i, /template/i
  ];

  return queryPatterns.some(p => p.test(input));
}

// 检测构建意图
function isBuildIntent(input) {
  const buildPatterns = [
    /创建/, /build/i, /create/i, /make/i,
    /设计/, /design/i,
    /工作流/, /workflow/i,
    /自动化/, /automate/i, /automation/i
  ];

  return buildPatterns.some(p => p.test(input));
}

// 检测学习意图
function isLearningIntent(input) {
  const learningPatterns = [
    /学习/, /learn/i, /tutorial/i,
    /示例/, /example/i, /demo/i,
    /最佳实践/, /best.*practice/i,
    /文档/, /doc/i, /guide/i
  ];

  return learningPatterns.some(p => p.test(input));
}
```

### 复杂度评估

```javascript
// 评估需求复杂度
function assessComplexity(input) {
  let score = 0;

  // 节点数量
  const nodeCount = (input.match(/节点|node|api|数据库|邮件/gi) || []).length;
  score += Math.min(nodeCount * 2, 20);

  // 操作复杂度
  if (/转换|处理|聚合|循环/i.test(input)) score += 15;
  if (/条件|分支|判断/i.test(input)) score += 10;
  if (/错误|重试|验证/i.test(input)) score += 10;

  // 集成数量
  const integrations = (input.match(/gmail|slack|discord|database|api|webhook/gi) || []).length;
  score += Math.min(integrations * 5, 15);

  // 数据处理
  if (/批量|大量|多|many/i.test(input)) score += 10;

  // 分类
  if (score >= 50) return 'high';
  if (score >= 30) return 'medium';
  return 'low';
}
```

## 需求提取

### 结构化参数提取

```javascript
// 提取结构化需求
function extractRequirements(userInput, intent) {
  const requirements = {
    summary: extractSummary(userInput),
    objectives: extractObjectives(userInput),
    inputs: extractInputs(userInput),
    outputs: extractOutputs(userInput),
    constraints: extractConstraints(userInput),
    trigger: extractTrigger(userInput),
    integrations: extractIntegrations(userInput),
    schedule: extractSchedule(userInput)
  };

  return requirements;
}

// 提取摘要
function extractSummary(input) {
  // 移除语气词和填充词
  const cleaned = input
    .replace(/帮我|我想|需要|可以/g, '')
    .replace(/一个|这个|那个/g, '')
    .trim();

  // 限制长度
  return cleaned.substring(0, 100);
}

// 提取目标
function extractObjectives(input) {
  const objectives = [];

  // 功能目标
  if (/发送|send/i.test(input)) objectives.push('发送消息/通知');
  if (/存储|保存|store|save/i.test(input)) objectives.push('数据持久化');
  if (/转换|transform|convert/i.test(input)) objectives.push('数据转换');
  if (/同步|sync/i.test(input)) objectives.push('数据同步');
  if (/监控|monitor|watch/i.test(input)) objectives.push('监控变化');
  if (/自动化|automate/i.test(input)) objectives.push('流程自动化');

  return objectives;
}

// 提取输入
function extractInputs(input) {
  const inputs = [];

  // 数据源
  if (/webhook|api/i.test(input)) {
    inputs.push({ type: 'webhook', description: 'Webhook 触发' });
  }
  if (/schedule|定时|cron/i.test(input)) {
    inputs.push({ type: 'schedule', description: '定时触发' });
  }
  if (/form|表单/i.test(input)) {
    inputs.push({ type: 'form', description: '表单提交' });
  }
  if (/email|邮件|gmail/i.test(input)) {
    inputs.push({ type: 'email', description: '邮件接收' });
  }

  return inputs;
}

// 提取输出
function extractOutputs(input) {
  const outputs = [];

  // 输出目标
  if (/slack|discord|消息|message/i.test(input)) {
    outputs.push({ type: 'messaging', description: '发送消息' });
  }
  if (/email|发送邮件|send.*mail/i.test(input)) {
    outputs.push({ type: 'email', description: '发送邮件' });
  }
  if (/数据库|database|db/i.test(input)) {
    outputs.push({ type: 'database', description: '写入数据库' });
  }
  if (/文件|file/i.test(input)) {
    outputs.push({ type: 'file', description: '保存文件' });
  }

  return outputs;
}

// 提取约束
function extractConstraints(input) {
  const constraints = [];

  if (/实时|real.*time/i.test(input)) {
    constraints.push({ type: 'performance', value: 'real-time' });
  }
  if (/批量|batch/i.test(input)) {
    constraints.push({ type: 'processing', value: 'batch' });
  }
  if (/错误处理|error.*handling/i.test(input)) {
    constraints.push({ type: 'reliability', value: 'error-handling' });
  }
  if (/安全|加密|security/i.test(input)) {
    constraints.push({ type: 'security', value: 'encrypted' });
  }

  return constraints;
}

// 提取触发器
function extractTrigger(input) {
  if (/webhook/i.test(input)) return 'webhook';
  if (/schedule|定时|每天| hourly|daily/i.test(input)) return 'schedule';
  if (/手动|manual/i.test(input)) return 'manual';
  if (/事件|event/i.test(input)) return 'event';
  return null; // 无触发器（可能是子流程）
}

// 提取集成服务
function extractIntegrations(input) {
  const integrations = [];

  const servicePatterns = {
    'gmail': /gmail|google.*mail/i,
    'slack': /slack/i,
    'discord': /discord/i,
    'telegram': /telegram/i,
    'notion': /notion/i,
    'airtable': /airtable/i,
    'google': /google.*sheet|drive/i,
    'github': /github/i,
    'jira': /jira/i,
    'trello': /trello/i,
    'postgres': /postgres|postgresql/i,
    'mysql': /mysql/i,
    'mongodb': /mongodb/i,
    'openai': /openai|gpt|chatgpt/i,
    'stripe': /stripe/i
  };

  for (const [service, pattern] of Object.entries(servicePatterns)) {
    if (pattern.test(input)) {
      integrations.push(service);
    }
  }

  return integrations;
}

// 提取调度信息
function extractSchedule(input) {
  if (/每天|daily/i.test(input)) return { frequency: 'daily' };
  if (/每小时|hourly/i.test(input)) return { frequency: 'hourly' };
  if (/每周|weekly/i.test(input)) return { frequency: 'weekly' };
  if (/每月|monthly/i.test(input)) return { frequency: 'monthly' };

  // Cron 表达式
  const cronMatch = input.match(/(\d+\s+\d+\s+\*\s+\*\s+\*\*)/);
  if (cronMatch) {
    return { frequency: 'cron', expression: cronMatch[1] };
  }

  return null;
}
```

## 策略选择

### 执行模式选择

```javascript
// 选择执行策略
function selectStrategy(intent, requirements) {
  // 模式 1: 直接查询（简单查询）
  if (intent.type === 'query' && intent.complexity === 'simple') {
    return {
      mode: 'direct',
      workflow: 'single_call',
      reason: '简单查询，直接返回结果'
    };
  }

  // 模式 2: 模板快速路径
  if (isTemplateMatch(requirements)) {
    return {
      mode: 'template',
      workflow: 'template_adaptation',
      reason: '匹配现有模板，快速适配'
    };
  }

  // 模式 3: 完整 10 步流程
  if (intent.type === 'build' && intent.complexity !== 'low') {
    return {
      mode: 'full',
      workflow: 'ten_step_process',
      reason: '复杂构建需求，完整流程'
    };
  }

  // 默认：简化流程
  return {
    mode: 'simplified',
    workflow: 'abbreviated_process',
    reason: '标准流程，简化执行'
  };
}

// 检查模板匹配
function isTemplateMatch(requirements) {
  // 高匹配度特征
  const templateIndicators = [
    requirements.integrations.length === 1, // 单一集成
    requirements.objectives.length <= 2,    // 简单目标
    !requirements.constraints.length        // 无特殊约束
  ];

  return templateIndicators.filter(Boolean).length >= 2;
}
```

## MCP 工具映射

### 直接模式映射

```javascript
// 直接模式：单个 MCP 调用
async function handleDirectMode(userInput, intent) {
  // 确定要调用的工具
  const tool = mapToTool(intent);

  // 准备参数
  const params = extractToolParams(userInput, tool);

  // 调用 MCP 工具
  const result = await callMCPTool(tool, params);

  // 格式化结果
  return formatResult(result, intent);
}

// 映射到工具
function mapToTool(intent) {
  const toolMap = {
    'search_nodes': 'search_nodes',
    'get_node': 'get_node',
    'search_templates': 'search_templates',
    'get_template': 'get_template',
    'list_workflows': 'list_workflows'
  };

  const queryType = intent.subType;
  return toolMap[queryType] || 'search_nodes';
}

// 提取工具参数
function extractToolParams(input, tool) {
  switch (tool) {
    case 'search_nodes':
      return {
        query: extractSearchQuery(input),
        filter: 'all',
        limit: 10
      };

    case 'search_templates':
      return {
        query: extractSearchQuery(input),
        limit: 5
      };

    case 'get_node':
      return {
        nodeType: extractNodeType(input)
      };

    case 'list_workflows':
      return {
        active: extractActiveOnly(input),
        limit: 20
      };

    default:
      return {};
  }
}

// 执行工具调用
async function callMCPTool(tool, params) {
  // 这里调用实际的 MCP 工具
  // 例如：await search_nodes(params)
  return await mcpTools[tool](params);
}
```

### 完整模式映射

```javascript
// 完整模式：10 步流程
async function handleFullMode(requirements) {
  const runDir = await initializeRun(requirements);

  const results = {
    requirements: await step01_requirements(requirements),
    research: await step02_research(requirements),
    discussion: await step03_discuss(requirements),
    knowledge: await step04_knowledge(requirements),
    design: await step05_design(requirements),
    workflow: await step06_build(requirements),
    credentials: await step07_credentials(requirements),
    validation: await step08_validate(requirements),
    deployment: await step09_deploy(requirements),
    output: await step10_output(requirements)
  };

  return results;
}
```

### 模板模式映射

```javascript
// 模板模式：快速适配
async function handleTemplateMode(requirements) {
  // 1. 搜索匹配的模板
  const templates = await search_templates({
    query: generateTemplateQuery(requirements),
    limit: 3
  });

  // 2. 选择最佳匹配
  const bestTemplate = selectBestTemplate(templates, requirements);

  // 3. 获取模板详情
  const template = await get_template({
    templateId: bestTemplate.id
  });

  // 4. 适配模板
  const adapted = adaptTemplate(template, requirements);

  // 5. 创建工作流
  const workflow = await create_workflow({
    workflow: adapted
  });

  // 6. 生成凭据报告
  const credentials = analyzeCredentials(adapted);

  return {
    workflow,
    credentials,
    source: 'template',
    templateId: template.id
  };
}

// 生成模板搜索查询
function generateTemplateQuery(requirements) {
  const keywords = [];

  // 添加集成关键词
  keywords.push(...requirements.integrations);

  // 添加目标关键词
  keywords.push(...requirements.objectives);

  // 组合成查询
  return keywords.join(' ');
}

// 选择最佳模板
function selectBestTemplate(templates, requirements) {
  // 评分算法
  const scored = templates.map(t => ({
    ...t,
    score: calculateTemplateScore(t, requirements)
  }));

  // 返回最高分
  return scored.sort((a, b) => b.score - a.score)[0];
}

// 计算模板匹配分数
function calculateTemplateScore(template, requirements) {
  let score = 0;

  // 集成匹配（每匹配一个 +10）
  const templateIntegrations = extractIntegrationsFromTemplate(template);
  const matchedIntegrations = requirements.integrations.filter(i =>
    templateIntegrations.includes(i)
  );
  score += matchedIntegrations.length * 10;

  // 目标匹配（每匹配一个 +5）
  const templateObjectives = extractObjectivesFromTemplate(template);
  const matchedObjectives = requirements.objectives.filter(o =>
    templateObjectives.includes(o)
  );
  score += matchedObjectives.length * 5;

  // 节点数量相似度
  const nodeDiff = Math.abs(template.nodes - estimateNodeCount(requirements));
  score += Math.max(0, 10 - nodeDiff);

  return score;
}
```

## 结果组装

### 响应格式化

```javascript
// 格式化查询结果
function formatQueryResult(result, intent) {
  switch (intent.subType) {
    case 'search_nodes':
      return formatNodeSearchResult(result);

    case 'search_templates':
      return formatTemplateSearchResult(result);

    case 'get_node':
      return formatNodeDetailResult(result);

    case 'list_workflows':
      return formatWorkflowListResult(result);

    default:
      return result;
  }
}

// 格式化节点搜索结果
function formatNodeSearchResult(result) {
  const nodes = result.nodes || [];

  return {
    summary: `找到 ${nodes.length} 个节点`,
    nodes: nodes.map(n => ({
      name: n.displayName || n.name,
      type: n.id,
      category: n.category,
      description: n.description
    })),
    suggestions: generateNodeSuggestions(nodes)
  };
}

// 格式化模板搜索结果
function formatTemplateSearchResult(result) {
  const templates = result.templates || [];

  return {
    summary: `找到 ${templates.length} 个模板`,
    templates: templates.map(t => ({
      name: t.name,
      category: t.category,
      description: t.description,
      nodes: t.nodes,
      url: t.url
    })),
    recommendations: generateTemplateRecommendations(templates)
  };
}

// 格式化构建结果
function formatBuildResult(results, mode) {
  const base = {
    mode: mode,
    status: results.workflow ? 'success' : 'failed',
    workflow: results.workflow,
    summary: results.output?.summary
  };

  if (mode === 'template') {
    base.templateUsed = results.templateId;
  }

  if (results.credentials) {
    base.credentials = {
      required: results.credentials.required.length,
      configured: results.credentials.configured.length,
      missing: results.credentials.missing.map(c => c.name)
    };
  }

  if (results.validation) {
    base.validation = {
      valid: results.validation.valid,
      errors: results.validation.errors.length,
      warnings: results.validation.warnings.length
    };
  }

  return base;
}
```

### 辅助信息生成

```javascript
// 生成节点建议
function generateNodeSuggestions(nodes) {
  const suggestions = [];

  if (nodes.length === 0) {
    suggestions.push('尝试使用更通用的关键词搜索');
  } else if (nodes.length < 5) {
    suggestions.push('搜索结果较少，可以尝试相关的同义词');
  }

  // 推荐相似节点
  const categories = groupByCategory(nodes);
  for (const [category, categoryNodes] of Object.entries(categories)) {
    if (categoryNodes.length > 1) {
      suggestions.push(`你也可以考虑 ${category} 类型的其他节点`);
    }
  }

  return suggestions;
}

// 生成模板推荐
function generateTemplateRecommendations(templates) {
  const recommendations = [];

  // 推荐最相似的模板
  const sortedByPopularity = templates
    .sort((a, b) => (b.popularity || 0) - (a.popularity || 0))
    .slice(0, 3);

  for (const template of sortedByPopularity) {
    recommendations.push({
      template: template.name,
      reason: '热门模板，经过验证'
    });
  }

  return recommendations;
}
```

## 完整适配流程

### 主适配器函数

```javascript
// 用户意图适配器主入口
async function adaptUserIntent(userInput, options = {}) {
  // 1. 分析意图
  const intent = classifyIntent(userInput);

  // 2. 提取需求
  const requirements = extractRequirements(userInput, intent);

  // 3. 选择策略
  const strategy = selectStrategy(intent, requirements);

  // 4. 执行适配
  let result;
  switch (strategy.mode) {
    case 'direct':
      result = await handleDirectMode(userInput, intent);
      break;

    case 'template':
      result = await handleTemplateMode(requirements);
      break;

    case 'full':
      result = await handleFullMode(requirements);
      break;

    default:
      result = await handleSimplifiedMode(requirements);
  }

  // 5. 格式化响应
  const response = formatResponse(result, strategy, intent);

  return response;
}

// 格式化最终响应
function formatResponse(result, strategy, intent) {
  return {
    strategy: strategy.mode,
    reason: strategy.reason,
    intent: intent.type,
    result: result,
    nextSteps: generateNextSteps(result, intent)
  };
}

// 生成后续步骤
function generateNextSteps(result, intent) {
  const steps = [];

  if (intent.type === 'build' && result.status === 'success') {
    steps.push({
      action: 'test_workflow',
      description: '测试工作流',
      command: `execute_workflow({ workflowId: "${result.workflow.id}" })`
    });

    steps.push({
      action: 'activate_workflow',
      description: '激活工作流',
      command: `update_workflow({ workflowId: "${result.workflow.id}", workflow: { active: true } })`
    });
  }

  if (result.credentials?.missing?.length > 0) {
    steps.push({
      action: 'configure_credentials',
      description: '配置缺失的凭据',
      credentials: result.credentials.missing
    });
  }

  return steps;
}
```

## 相关文档

- [10步流程编排器](layer3-orchestrator.md)
- [节点规划器](layer3-planner.md)
- [MCP 工具参考](layer2-mcp.md)
- [10步工作流](../workflow/)
