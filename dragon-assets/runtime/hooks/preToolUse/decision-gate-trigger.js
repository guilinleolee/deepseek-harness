
/**
 * Decision Gate Trigger Hook
 *
 * 借鉴自 GSD-2 的强制门控机制
 * 在关键决策点暂停并等待用户确认
 */

const DECISION_GATES = {
  analysis_complete: {
    name: "📊 分析完成",
    emoji: "📊",
    options: [
      "立即执行",
      "创建发现文档",
      "进一步探索",
      "获取第二意见",
      "其他"
    ]
  },
  high_risk: {
    name: "⚠️ 高风险操作警告",
    emoji: "⚠️",
    options: [
      "确认执行（了解风险）",
      "先创建备份再执行",
      "查看详细影响分析",
      "取消操作"
    ]
  },
  multi_path: {
    name: "🔀 多路径选择",
    emoji: "🔀",
    options: [
      "选择方案A（推荐）",
      "选择方案B",
      "选择方案C",
      "查看详细对比",
      "自定义方案"
    ]
  },
  release: {
    name: "🚀 发布确认",
    emoji: "🚀",
    options: [
      "确认发布",
      "查看完整变更",
      "运行额外测试",
      "创建Release Note",
      "取消"
    ]
  }
};

// 高风险操作检测模式
const HIGH_RISK_PATTERNS = {
  files_modified: {
    threshold: 5,
    description: "修改文件数超过阈值"
  },
  lines_changed: {
    threshold: 100,
    description: "代码变更行数超过阈值"
  },
  delete_operations: {
    patterns: [/rm\s+-rf/, /git\s+push\s+--force/, /DROP\s+TABLE/i],
    description: "包含删除/强制操作"
  },
  architecture_change: {
    patterns: [/refactor/i, /migrate/i, /upgrade/i, /architecture/i],
    description: "架构变更相关操作"
  }
};

// 门控状态存储
let gateState = {
  pendingGates: [],
  lastGateTime: null,
  totalGatesTriggered: 0
};

/**
 * 检测是否需要触发门控
 */
function shouldTriggerGate(context) {
  const { toolName, toolInput, output } = context;

  // 分析完成检测
  if (isAnalysisComplete(output)) {
    return { type: 'analysis_complete', context: extractAnalysisContext(output) };
  }

  // 高风险操作检测
  if (isHighRiskOperation(toolName, toolInput)) {
    return { type: 'high_risk', context: extractRiskContext(toolName, toolInput) };
  }

  // 多路径检测
  if (hasMultipleSolutions(output)) {
    return { type: 'multi_path', context: extractSolutionsContext(output) };
  }

  return null;
}

/**
 * 检测分析是否完成
 */
function isAnalysisComplete(output) {
  if (!output || typeof output !== 'string') return false;

  const analysisPatterns = [
    /分析完成/i,
    /analysis complete/i,
    /root cause identified/i,
    /问题已定位/i,
    /调查完成/i,
    /根本原因/i
  ];

  return analysisPatterns.some(p => p.test(output));
}

/**
 * 检测高风险操作
 */
function isHighRiskOperation(toolName, toolInput) {
  // 检查删除操作
  if (toolName === 'Bash') {
    const command = toolInput.command || '';
    for (const pattern of HIGH_RISK_PATTERNS.delete_operations.patterns) {
      if (pattern.test(command)) {
        return true;
      }
    }
  }

  // 检查文件操作数量
  if (toolName === 'Edit' || toolName === 'Write') {
    // 可扩展：跟踪文件修改数量
  }

  return false;
}

/**
 * 检测是否有多路径解决方案
 */
function hasMultipleSolutions(output) {
  if (!output || typeof output !== 'string') return false;

  const solutionPatterns = [
    /方案[一二三ABC]/i,
    /option [123]/i,
    /solution [123]/i,
    /建议.*选择/i,
    /推荐.*方案/i
  ];

  let solutionCount = 0;
  for (const pattern of solutionPatterns) {
    const matches = output.match(pattern);
    if (matches) solutionCount += matches.length;
  }

  return solutionCount >= 2;
}

/**
 * 提取分析上下文
 */
function extractAnalysisContext(output) {
  // 简单提取，实际可使用更复杂的解析
  const lines = output.split('\n').slice(0, 5);
  return {
    summary: lines.join('\n')
  };
}

/**
 * 提取风险上下文
 */
function extractRiskContext(toolName, toolInput) {
  return {
    operation: toolName,
    details: toolInput.command || toolInput.file_path || '未知操作'
  };
}

/**
 * 提取解决方案上下文
 */
function extractSolutionsContext(output) {
  return {
    solutions: [] // 可扩展解析具体方案
  };
}

/**
 * 格式化门控UI
 */
function formatGateUI(gateType, context) {
  const gate = DECISION_GATES[gateType];
  if (!gate) return null;

  const divider = "━".repeat(50);
  let ui = `\n${divider}\n${gate.name}\n${divider}\n\n`;

  if (context.summary) {
    ui += `📋 发现摘要：\n${context.summary}\n\n`;
  }

  if (context.details) {
    ui += `⚠️ 操作详情：${context.details}\n\n`;
  }

  ui += `🎯 请选择下一步：\n`;
  gate.options.forEach((opt, i) => {
    ui += `${i + 1}. ${opt}\n`;
  });

  ui += `\n请输入选项编号 [1-${gate.options.length}]：\n${divider}`;

  return ui;
}

/**
 * 触发门控（返回门控提示）
 */
function triggerGate(gateType, context) {
  const gate = DECISION_GATES[gateType];
  if (!gate) return null;

  gateState.totalGatesTriggered++;
  gateState.lastGateTime = new Date().toISOString();
  gateState.pendingGates.push({
    type: gateType,
    time: gateState.lastGateTime,
    context
  });

  return {
    gateType,
    gateName: gate.name,
    options: gate.options,
    formattedUI: formatGateUI(gateType, context),
    required: gateType !== 'multi_path' // 多路径可选，其他强制
  };
}

/**
 * 获取门控状态
 */
function getGateState() {
  return { ...gateState };
}

/**
 * 清除待处理门控
 */
function clearPendingGates() {
  gateState.pendingGates = [];
}

/**
 * Hook主函数
 */
function decisionGateHook(context) {
  const { event, toolName, toolInput, output } = context;

  // 只在postToolUse事件检查
  if (event !== 'postToolUse') return null;

  // 检测是否需要触发门控
  const gateResult = shouldTriggerGate({ toolName, toolInput, output });

  if (gateResult) {
    return triggerGate(gateResult.type, gateResult.context);
  }

  return null;
}

// 导出
module.exports = {
  decisionGateHook,
  DECISION_GATES,
  HIGH_RISK_PATTERNS,
  shouldTriggerGate,
  triggerGate,
  getGateState,
  clearPendingGates
};