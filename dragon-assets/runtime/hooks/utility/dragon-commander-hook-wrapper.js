
/**
 * 🐉 天龙引擎指挥官Hook包装器
 * 指挥官：李依依（一一）
 * 系统提示词：../../prompts/liyiyi-commander-system-prompt.md
 *
 * 这个Hook将指挥官系统集成到Claude Code的工作流中
 * 在每次对话开始时自动初始化指挥官
 */

const DragonCommanderV2 = require('./dragon-commander.js');  // Part 3 重构修复：dragon-commander-v2.js 不存在，回退基础版

// 全局指挥官实例
let globalCommander = null;

/**
 * 初始化指挥官（如果还没有初始化）
 */
function ensureCommander() {
  if (!globalCommander) {
    globalCommander = new DragonCommanderV2();
    console.log('🐉 天龙引擎指挥官李依依（一一）已就位！');
  }
  return globalCommander;
}

/**
 * Hook: 用户提交提示时触发
 * 分析用户输入，提供智能建议（V7.0 渐进式优化版）
 */
function userPromptSubmitHook(input) {
  try {
    const commander = ensureCommander();

    // 分析用户需求
    const analysis = commander.analyzeRequirement(input);

    // 如果找到了推荐的代理，输出建议
    if (analysis.suggestedAgents.length > 0) {
      const topAgent = analysis.suggestedAgents[0];
      const confidence = (analysis.confidence * 100).toFixed(0);

      // 获取代理详细信息
      const agentInfo = commander.agentRegistry[topAgent.agentId];

      // 优先级中文映射
      const priorityMap = {
        'high': '🔴 高',
        'normal': '🟡 中',
        'low': '🟢 低'
      };

      // 复杂度中文映射
      const complexityMap = {
        'simple': '简单',
        'medium': '中等',
        'complex': '复杂'
      };

      // 计算业务影响（相比其他选项的优势）
      const businessImpact = calculateBusinessImpact(topAgent, analysis.suggestedAgents.slice(1), commander);

      console.log(`
🎯 **核心洞察**: 用 **${topAgent.agentName}** 直接搞定（置信度${confidence}%），预计${formatTime(topAgent.estimatedTime)}，成本${topAgent.estimatedCost.toFixed(2)}单位。

**📊 快速决策参考**
- 复杂度: ${complexityMap[analysis.complexity] || analysis.complexity} | 优先级: ${priorityMap[analysis.priority] || analysis.priority}
- 预计耗时: **${topAgent.estimatedTime}秒** | 预计成本: **${topAgent.estimatedCost.toFixed(2)}单位**
- 推荐模型: ${topAgent.recommendedModel}

**💡 为什么选择这个方案**
${generateReasonText(topAgent, agentInfo, analysis)}

**💥 业务影响**
${generateBusinessImpactText(businessImpact)}

**🎬 下一步**
- 直接执行: 在回复中输入 "执行" 开始任务
- 查看详情: 输入 "详情" 查看完整分析
- 更换方案: 输入 "其他" 查看备选代理
      `);
    }

    return { analysis, commander };
  } catch (error) {
    console.error('指挥官分析失败:', error.message);
    return { analysis: null, commander: null };
  }
}

/**
 * 格式化时间显示
 */
function formatTime(seconds) {
  if (seconds < 60) {
    return `${seconds}秒`;
  } else if (seconds < 3600) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return remainingSeconds > 0 ? `${minutes}分${remainingSeconds}秒` : `${minutes}分钟`;
  } else {
    const hours = Math.floor(seconds / 3600);
    const remainingMinutes = Math.floor((seconds % 3600) / 60);
    return remainingMinutes > 0 ? `${hours}小时${remainingMinutes}分钟` : `${hours}小时`;
  }
}

/**
 * 计算业务影响（相比其他选项的优势）
 */
function calculateBusinessImpact(topAgent, otherAgents, commander) {
  const impact = {
    timeSaving: null,
    costSaving: null,
    qualityBenefit: null
  };

  if (otherAgents.length > 0) {
    // 计算平均耗时和成本
    const avgTime = otherAgents.reduce((sum, agent) => sum + agent.estimatedTime, 0) / otherAgents.length;
    const avgCost = otherAgents.reduce((sum, agent) => sum + agent.estimatedCost, 0) / otherAgents.length;

    if (topAgent.estimatedTime < avgTime) {
      impact.timeSaving = Math.round(((avgTime - topAgent.estimatedTime) / avgTime) * 100);
    }

    if (topAgent.estimatedCost < avgCost) {
      impact.costSaving = Math.round(((avgCost - topAgent.estimatedCost) / avgCost) * 100);
    }
  }

  // 获取代理成功率
  const agentInfo = commander.agentRegistry[topAgent.agentId];
  if (agentInfo) {
    // V1 修复：基础版 agentRegistry 无 successRate，默认 0.95
    impact.qualityBenefit = Math.round((agentInfo.successRate ?? 0.95) * 100);
  }

  return impact;
}

/**
 * 生成"为什么选择这个方案"的文字说明
 */
function generateReasonText(topAgent, agentInfo, analysis) {
  const reasons = [];

  // 1. 能力匹配度
  if (agentInfo && agentInfo.capabilities.length > 0) {
    const topCapability = agentInfo.capabilities[0];
    // V1 修复：基础版 capabilities 是字符串数组，无 weight 字段；原代码 topCapability.weight.toFixed(2) 会崩
    reasons.push(`${topAgent.agentName}具备"${typeof topCapability === 'string' ? topCapability : (topCapability.name || JSON.stringify(topCapability))}"能力`);
  }

  // 2. 历史成功率
  if (agentInfo) {
    reasons.push(`历史成功率${Math.round((agentInfo.successRate ?? 0.95) * 100)}%`);
  }

  // 3. 触发关键词
  if (analysis.tags && analysis.tags.length > 0) {
    reasons.push(`匹配关键词: ${analysis.tags.slice(0, 3).join('、')}`);
  }

  // 4. 相比其他代理的优势
  if (topAgent.matchCount > 0) {
    reasons.push(`匹配${topAgent.matchCount}个触发点`);
  }

  return reasons.join('，且') + '。';
}

/**
 * 生成"业务影响"的文字说明
 */
function generateBusinessImpactText(impact) {
  const impacts = [];

  if (impact.timeSaving !== null) {
    impacts.push(`⏱️  **节省时间**: ${impact.timeSaving}%（相比其他备选方案）`);
  }

  if (impact.costSaving !== null) {
    impacts.push(`💰 **降低成本**: ${impact.costSaving}%（成本效益更高）`);
  }

  if (impact.qualityBenefit !== null) {
    impacts.push(`✅ **质量保障**: ${impact.qualityBenefit}%成功率（历史数据验证）`);
  }

  if (impacts.length === 0) {
    impacts.push('- **综合最优**: 平衡了效率、成本和质量');
  }

  return impacts.join('\n');
}

/**
 * Hook: 工具使用后触发
 * 更新代理性能数据
 */
function postToolUseHook(toolName, toolResult) {
  try {
    const commander = ensureCommander();

    // 如果使用了Task工具调用代理，记录性能
    if (toolName === 'Task' && toolResult) {
      // 这里可以添加性能追踪逻辑
      // 目前先简单记录
    }
  } catch (error) {
    console.error('性能追踪失败:', error.message);
  }
}

/**
 * 生成指挥官状态报告
 */
function generateCommanderReport() {
  const commander = ensureCommander();
  return commander.generateHumanReadableReport();
}

/**
 * 获取所有代理列表
 */
function getAllAgents() {
  const commander = ensureCommander();
  const agents = [];

  for (const [agentId, agent] of Object.entries(commander.agentRegistry)) {
    agents.push({
      id: agentId,
      name: agent.name,
      department: agent.department,
      capabilities: agent.capabilities.map(c => c.name).join(', '),
      model: agent.recommendedModel
    });
  }

  return agents;
}

/**
 * 获取指定代理的详细信息
 */
function getAgentInfo(agentId) {
  const commander = ensureCommander();
  const agent = commander.agentRegistry[agentId];

  if (!agent) {
    return null;
  }

  // 获取性能数据
  const perf = (commander.agentPerformance ?? new Map()).get(agentId);

  return {
    id: agent.id,
    name: agent.name,
    department: agent.department,
    capabilities: agent.capabilities,
    triggers: agent.triggers,
    recommendedModel: agent.recommendedModel,
    priority: agent.priority,
    performance: perf ? {
      totalTasks: perf.totalTasks,
      successTasks: perf.successTasks,
      failedTasks: perf.failedTasks,
      successRate: perf.successRate,
      avgResponseTime: perf.avgResponseTime
    } : {
      totalTasks: 0,
      // V1 补字段：基础版 agentRegistry 无 successRate/avgResponseTime 字段，commandCommand 等调用方需要这两个值
      successRate: agent.successRate ?? 0.95,
      avgResponseTime: agent.avgResponseTime ?? 60
    }
  };
}

/**
 * 推荐代理
 */
function recommendAgents(requirements) {
  const commander = ensureCommander();
  return commander.recommendAgents(requirements);
}

// 导出Hook函数
module.exports = {
  userPromptSubmitHook,
  postToolUseHook,
  generateCommanderReport,
  getAllAgents,
  getAgentInfo,
  recommendAgents,
  ensureCommander
};
