# n8n-mcp 知识库 Layer 3: 10步流程编排器

## 概述

Layer 3 是中间层适配的核心，负责编排完整的 10 步工作流构建流程，协调用户需求、MCP 工具和最终输出。

## 编排器架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    10 步流程编排器 (Orchestrator)                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Step 01: 需求规格 → Step 02: 研究发现 → Step 03: 讨论确认        │
│       ↓                                                           │
│  Step 04: 知识库查询 → Step 05: 架构设计 → Step 06: 工作流构建    │
│       ↓                                                           │
│  Step 07: 凭据报告 → Step 08: 验证测试 → Step 09: 部署激活        │
│       ↓                                                           │
│  Step 10: 输出交付                                                 │
│                                                                   │
├─────────────────────────────────────────────────────────────────┤
│                      状态管理                                      │
│  - runs/{timestamp}/progress.json - 进度追踪                     │
│  - 断点恢复机制                                                    │
│  - 错误回滚策略                                                    │
└─────────────────────────────────────────────────────────────────┘
```

## 核心编排逻辑

### 初始化阶段

```javascript
// 初始化运行目录
async function initializeRun(userInput) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const slug = generateSlug(userInput.summary || 'workflow');
  const runDir = `runs/${timestamp}-${slug}`;

  // 创建目录结构
  await fs.mkdir(runDir, { recursive: true });

  // 初始化进度文件
  const progress = {
    runId: `${timestamp}-${slug}`,
    startTime: new Date().toISOString(),
    currentStep: 0,
    completedSteps: [],
    status: 'initialized',
    errors: [],
    userInput: userInput
  };

  await fs.writeFile(
    `${runDir}/progress.json`,
    JSON.stringify(progress, null, 2)
  );

  return { runDir, progress };
}
```

### 步骤执行模板

```javascript
// 通用步骤执行函数
async function executeStep(stepNumber, stepName, context) {
  const { runDir, progress } = context;

  try {
    // 更新进度
    progress.currentStep = stepNumber;
    progress.status = `running_step_${stepNumber}`;
    await saveProgress(runDir, progress);

    // 加载步骤配置
    const stepConfig = await loadStepConfig(stepNumber);
    const stepFile = `${runDir}/${stepConfig.filename}`;

    // 执行步骤逻辑
    const result = await runStepLogic(stepNumber, context);

    // 保存结果
    await fs.writeFile(stepFile, formatResult(result));

    // 更新进度
    progress.completedSteps.push(stepNumber);
    progress.status = `completed_step_${stepNumber}`;
    await saveProgress(runDir, progress);

    return result;

  } catch (error) {
    // 错误处理
    progress.errors.push({
      step: stepNumber,
      name: stepName,
      error: error.message,
      timestamp: new Date().toISOString()
    });

    // 根据错误类型决定是否继续
    if (isFatalError(error)) {
      progress.status = 'failed';
      await saveProgress(runDir, progress);
      throw error;
    } else {
      // 非致命错误，记录并继续
      await saveProgress(runDir, progress);
      return { error: error.message, warning: true };
    }
  }
}
```

## 完整编排流程

### 主编排函数

```javascript
async function orchestrateWorkflowBuild(userInput, options = {}) {
  // 1. 初始化
  const { runDir, progress } = await initializeRun(userInput);

  const context = {
    runDir,
    progress,
    userInput,
    options,
    sharedData: {}
  };

  try {
    // Step 01: 需求规格
    context.sharedData.requirements = await executeStep(
      1, 'requirements', context
    );

    // Step 02: 研究发现
    context.sharedData.research = await executeStep(
      2, 'research', context
    );

    // Step 03: 讨论确认
    context.sharedData.plan = await executeStep(
      3, 'discussion', context
    );

    // 检查用户是否确认
    if (!context.sharedData.plan.confirmed) {
      throw new Error('Plan not confirmed by user');
    }

    // Step 04: 知识库查询
    context.sharedData.knowledge = await executeStep(
      4, 'knowledge', context
    );

    // Step 05: 架构设计
    context.sharedData.design = await executeStep(
      5, 'design', context
    );

    // Step 06: 工作流构建
    context.sharedData.workflow = await executeStep(
      6, 'build', context
    );

    // Step 07: 凭据报告
    context.sharedData.credentials = await executeStep(
      7, 'credentials', context
    );

    // Step 08: 验证测试
    context.sharedData.validation = await executeStep(
      8, 'validate', context
    );

    // 如果验证失败，进入修复循环
    if (!context.sharedData.validation.valid) {
      context.sharedData.validation = await handleValidationErrors(
        context.sharedData.validation,
        context
      );
    }

    // Step 09: 部署激活
    context.sharedData.deployment = await executeStep(
      9, 'deploy', context
    );

    // Step 10: 输出交付
    context.sharedData.output = await executeStep(
      10, 'output', context
    );

    // 完成
    progress.status = 'completed';
    progress.endTime = new Date().toISOString();
    await saveProgress(runDir, progress);

    return {
      success: true,
      runDir,
      output: context.sharedData.output
    };

  } catch (error) {
    progress.status = 'failed';
    progress.endTime = new Date().toISOString();
    progress.errors.push({
      fatal: true,
      error: error.message,
      stack: error.stack
    });
    await saveProgress(runDir, progress);

    return {
      success: false,
      runDir,
      error: error.message
    };
  }
}
```

## 断点恢复机制

```javascript
// 从断点恢复
async function resumeRun(runDir) {
  // 加载进度
  const progress = JSON.parse(
    await fs.readFile(`${runDir}/progress.json`)
  );

  // 恢复上下文
  const context = {
    runDir,
    progress,
    userInput: progress.userInput,
    options: progress.options || {},
    sharedData: {}
  };

  // 恢复已完成步骤的数据
  for (const stepNum of progress.completedSteps) {
    const stepConfig = getStepConfig(stepNum);
    const stepFile = `${runDir}/${stepConfig.filename}`;
    const stepData = JSON.parse(await fs.readFile(stepFile));
    context.sharedData[stepConfig.dataKey] = stepData;
  }

  // 从下一个未完成的步骤继续
  const nextStep = progress.currentStep + 1;

  try {
    // 继续执行剩余步骤
    const result = await continueFromStep(nextStep, context);

    progress.status = 'resumed_and_completed';
    await saveProgress(runDir, progress);

    return result;

  } catch (error) {
    progress.status = 'resumed_and_failed';
    await saveProgress(runDir, progress);
    throw error;
  }
}
```

## 错误处理策略

### 错误分类与处理

```javascript
// 错误分类
function classifyError(error) {
  const fatalPatterns = [
    /user.*cancel/i,
    /plan.*not.*confirmed/i,
    /invalid.*mcp.*response/i
  ];

  const recoverablePatterns = [
    /api.*rate.*limit/i,
    /network.*timeout/i,
    /temporary.*failure/i
  ];

  const errorStr = error.message.toLowerCase();

  if (fatalPatterns.some(p => p.test(errorStr))) {
    return 'fatal';
  } else if (recoverablePatterns.some(p => p.test(errorStr))) {
    return 'recoverable';
  } else {
    return 'unknown';
  }
}

// 错误处理
async function handleError(error, context) {
  const classification = classifyError(error);

  switch (classification) {
    case 'fatal':
      // 致命错误：停止执行
      throw error;

    case 'recoverable':
      // 可恢复错误：重试或跳过
      return await handleRecoverableError(error, context);

    default:
      // 未知错误：询问用户
      return await handleUnknownError(error, context);
  }
}
```

### 验证错误修复循环

```javascript
// 处理验证错误
async function handleValidationErrors(validationResult, context) {
  const { errors, warnings } = validationResult;
  let attempts = 0;
  const maxAttempts = 10;

  while (errors.length > 0 && attempts < maxAttempts) {
    attempts++;

    console.log(`\n修复尝试 ${attempts}/${maxAttempts}`);
    console.log(`剩余错误: ${errors.length}`);

    // 分析错误类型
    const errorType = categorizeErrors(errors);

    // 尝试修复
    const fixResult = await attemptFix(errorType, errors, context);

    if (fixResult.success) {
      // 重新验证
      validationResult = await validate_workflow({
        workflow: context.sharedData.workflow
      });

      if (validationResult.valid) {
        return validationResult;
      }
    } else {
      // 无法自动修复，询问用户
      console.log('无法自动修复，需要人工干预');
      break;
    }
  }

  return validationResult;
}
```

## 步骤间数据传递

### 共享数据结构

```javascript
// 共享数据容器
const sharedDataStructure = {
  // Step 01
  requirements: {
    summary: string,
    objectives: string[],
    inputs: object[],
    outputs: object[],
    constraints: string[],
    schedule: object
  },

  // Step 02
  research: {
    webResults: object[],
    nodeOptions: object[],
    templateOptions: object[],
    recommendations: string[]
  },

  // Step 03
  plan: {
    confirmed: boolean,
    selectedNodes: string[],
    architecture: string,
    adjustments: string[]
  },

  // Step 04
  knowledge: {
    nodeDetails: object,
    bestPractices: string[],
    examples: object[]
  },

  // Step 05
  design: {
    nodes: object[],
    connections: object,
    expressions: object[],
    codeNodes: object[]
  },

  // Step 06
  workflow: {
    id: string,
    name: string,
    nodes: object[],
    connections: object,
    settings: object
  },

  // Step 07
  credentials: {
    required: object[],
    configured: object[],
    missing: object[]
  },

  // Step 08
  validation: {
    valid: boolean,
    errors: object[],
    warnings: object[]
  },

  // Step 09
  deployment: {
    deployed: boolean,
    active: boolean,
    workflowId: string,
    testResults: object
  },

  // Step 10
  output: {
    workflowJson: object,
    summary: string,
    documentation: string
  }
};
```

## 优化与性能

### 并行执行

```javascript
// 并行执行独立步骤
async function executeParallelSteps(steps, context) {
  const results = await Promise.all(
    steps.map(step => executeStep(step.number, step.name, context))
  );

  return results;
}
```

### 缓存机制

```javascript
// 缓存 MCP 调用结果
const cache = new Map();

async function cachedMCPCall(tool, params) {
  const cacheKey = JSON.stringify({ tool, params });

  if (cache.has(cacheKey)) {
    return cache.get(cacheKey);
  }

  const result = await callMCPTool(tool, params);
  cache.set(cacheKey, result);

  return result;
}
```

## 相关文档

- [节点规划器](layer3-planner.md)
- [用户意图适配器](layer3-adapter.md)
- [10步工作流](../workflow/)
- [MCP 工具参考](layer2-mcp.md)
