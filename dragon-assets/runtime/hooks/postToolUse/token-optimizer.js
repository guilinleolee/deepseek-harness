
/**
 * Token Optimizer Hook
 *
 * Token追踪、成本分析和优化建议系统。
 *
 * 来源: ruflo (https://github.com/ruvnet/ruflo)
 *
 * 核心功能:
 * 1. 实时Token统计和追踪
 * 2. 成本估算和预警
 * 3. 优化建议生成
 * 4. Agent/Command维度的Token分析
 */

const fs = require('fs');
const path = require('path');

// 配置
const CONFIG = {
  enabled: true,
  metricsDir: path.join(process.cwd(), '.claude', 'metrics'),
  tokenFile: 'token-usage.json',
  warningThreshold: 100000,
  criticalThreshold: 500000,
  historyLimit: 1000,
  claudePricing: {
    // Claude 3 Opus (per 1M tokens)
    opus: { input: 15.00, output: 75.00 },
    // Claude 3 Sonnet (per 1M tokens)
    sonnet: { input: 3.00, output: 15.00 },
    // Claude 3 Haiku (per 1M tokens)
    haiku: { input: 0.25, output: 1.25 }
  }
};

// Token缓存
let tokenCache = {
  sessions: {},
  totals: { input: 0, output: 0, total: 0 },
  byAgent: {},
  byCommand: {},
  history: []
};

/**
 * 确保目录存在
 */
function ensureMetricsDir() {
  if (!fs.existsSync(CONFIG.metricsDir)) {
    fs.mkdirSync(CONFIG.metricsDir, { recursive: true });
  }
}

/**
 * 获取Token文件路径
 * @returns {string} - 文件路径
 */
function getTokenFilePath() {
  return path.join(CONFIG.metricsDir, CONFIG.tokenFile);
}

/**
 * 加载Token数据
 * @returns {TokenData} - Token数据
 */
function loadTokenData() {
  try {
    const filePath = getTokenFilePath();
    if (fs.existsSync(filePath)) {
      const data = fs.readFileSync(filePath, 'utf8');
      tokenCache = JSON.parse(data);
    }
  } catch (error) {
    // 文件不存在或无效，使用默认值
  }
  return tokenCache;
}

/**
 * 保存Token数据
 */
function saveTokenData() {
  try {
    ensureMetricsDir();
    const filePath = getTokenFilePath();
    fs.writeFileSync(filePath, JSON.stringify(tokenCache, null, 2), 'utf8');
  } catch (error) {
    console.error('Failed to save token data:', error.message);
  }
}

/**
 * 追踪Token使用
 * @param {TokenTrackParams} params - 追踪参数
 * @returns {TrackResult} - 追踪结果
 */
function trackTokens(params) {
  const {
    sessionId,
    agentType = 'general',
    command = 'unknown',
    inputTokens = 0,
    outputTokens = 0,
    metadata = {}
  } = params;

  // 更新总计
  tokenCache.totals.input += inputTokens;
  tokenCache.totals.output += outputTokens;
  tokenCache.totals.total += (inputTokens + outputTokens);

  // 按Agent分类
  if (!tokenCache.byAgent[agentType]) {
    tokenCache.byAgent[agentType] = {
      input: 0, output: 0, total: 0, count: 0
    };
  }
  tokenCache.byAgent[agentType].input += inputTokens;
  tokenCache.byAgent[agentType].output += outputTokens;
  tokenCache.byAgent[agentType].total += (inputTokens + outputTokens);
  tokenCache.byAgent[agentType].count++;

  // 按命令分类
  if (!tokenCache.byCommand[command]) {
    tokenCache.byCommand[command] = {
      input: 0, output: 0, total: 0, count: 0
    };
  }
  tokenCache.byCommand[command].input += inputTokens;
  tokenCache.byCommand[command].output += outputTokens;
  tokenCache.byCommand[command].total += (inputTokens + outputTokens);
  tokenCache.byCommand[command].count++;

  // 添加历史记录
  tokenCache.history.push({
    timestamp: Date.now(),
    sessionId,
    agentType,
    command,
    inputTokens,
    outputTokens,
    metadata
  });

  // 限制历史记录数量
  if (tokenCache.history.length > CONFIG.historyLimit) {
    tokenCache.history = tokenCache.history.slice(-CONFIG.historyLimit);
  }

  // 保存数据
  saveTokenData();

  // 检查阈值
  checkThresholds();

  return {
    sessionTotal: inputTokens + outputTokens,
    grandTotal: tokenCache.totals.total
  };
}

/**
 * 检查阈值并发出警告
 */
function checkThresholds() {
  const total = tokenCache.totals.total;

  if (total >= CONFIG.criticalThreshold) {
    console.warn(`\n🚨 [Token Warning] Critical threshold reached: ${total.toLocaleString()} tokens`);
    console.warn(`   Estimated cost: $${calculateCost(tokenCache.totals).total.toFixed(2)}`);
    console.warn(`   💡 Consider using /token-optimize for suggestions\n`);
  } else if (total >= CONFIG.warningThreshold) {
    console.warn(`\n⚠️  [Token Warning] Approaching threshold: ${total.toLocaleString()} tokens`);
    console.warn(`   💡 Use /token-usage to see detailed statistics\n`);
  }
}

/**
 * 计算成本
 * @param {TokenData} tokenData - Token数据
 * @param {string} model - 模型名称
 * @returns {CostBreakdown} - 成本分解
 */
function calculateCost(tokenData, model = 'opus') {
  const pricing = CONFIG.claudePricing[model] || CONFIG.claudePricing.opus;

  const inputCost = (tokenData.input / 1000000) * pricing.input;
  const outputCost = (tokenData.output / 1000000) * pricing.output;

  return {
    input: inputCost,
    output: outputCost,
    total: inputCost + outputCost
  };
}

/**
 * 获取Token使用统计
 * @param {string} filter - 筛选条件
 * @returns {TokenUsageStats} - 使用统计
 */
function getTokenUsage(filter = 'all') {
  loadTokenData();

  if (filter !== 'all' && tokenCache.byAgent[filter]) {
    const agentData = tokenCache.byAgent[filter];
    return {
      total: agentData.total,
      input: agentData.input,
      output: agentData.output,
      count: agentData.count,
      byAgent: { [filter]: agentData.total }
    };
  }

  // 构建byAgent摘要
  const byAgent = {};
  for (const [agent, data] of Object.entries(tokenCache.byAgent)) {
    byAgent[agent] = data.total;
  }

  return {
    total: tokenCache.totals.total,
    input: tokenCache.totals.input,
    output: tokenCache.totals.output,
    byAgent,
    byCommand: tokenCache.byCommand,
    history: tokenCache.history
  };
}

/**
 * 生成优化建议
 * @param {TokenData} tokenData - Token数据
 * @returns {Array<string>} - 建议列表
 */
function generateOptimizationSuggestions(tokenData) {
  const suggestions = [];

  if (tokenData.total === 0) {
    return ['No token usage data available. Start using Claude Code to track tokens.'];
  }

  // 分析输出比例
  const outputRatio = tokenData.output / tokenData.total;
  if (outputRatio > 0.6) {
    suggestions.push({
      priority: 'high',
      message: 'High output ratio detected. Consider more concise prompts to reduce generation.',
      impact: `${((outputRatio - 0.5) * 100).toFixed(0)}% potential savings`
    });
  }

  // 分析Agent使用
  const sortedAgents = Object.entries(tokenCache.byAgent || {})
    .sort((a, b) => b[1].total - a[1].total);

  if (sortedAgents.length > 0) {
    const [topAgent, topUsage] = sortedAgents[0];
    const percentage = (topUsage.total / tokenData.total) * 100;

    if (percentage > 50) {
      suggestions.push({
        priority: 'medium',
        message: `${topAgent} agents consume ${percentage.toFixed(0)}% of tokens. Consider optimization or caching.`,
        impact: 'Up to 30% savings with caching'
      });
    }
  }

  // 检查重复命令
  if (tokenCache.history && tokenCache.history.length > 10) {
    const recentCommands = tokenCache.history.slice(-20).map(h => h.command);
    const duplicates = recentCommands.filter((cmd, i) => recentCommands.indexOf(cmd) !== i);

    if (duplicates.length > 5) {
      suggestions.push({
        priority: 'medium',
        message: 'Repeated commands detected. Consider implementing result caching.',
        impact: '20-40% savings with effective caching'
      });
    }
  }

  // 成本优化建议
  if (tokenData.total > 100000) {
    suggestions.push({
      priority: 'low',
      message: 'Consider using Claude Haiku for non-critical tasks to reduce costs by ~90%.',
      impact: 'Up to 90% cost reduction for simple tasks'
    });
  }

  // 使用Agent Booster建议
  const editCommands = Object.entries(tokenCache.byCommand || {})
    .filter(([cmd]) => cmd.includes('edit') || cmd.includes('write'));

  if (editCommands.length > 0) {
    const editTotal = editCommands.reduce((sum, [, data]) => sum + data.total, 0);
    if (editTotal > 10000) {
      suggestions.push({
        priority: 'high',
        message: 'High token usage on edit operations. Consider using Agent Booster for simple edits.',
        impact: '100% savings on Booster-eligible edits (352x faster)'
      });
    }
  }

  return suggestions;
}

/**
 * 生成Token报告
 * @param {Object} options - 报告选项
 * @returns {TokenReport} - Token报告
 */
function generateReport(options = {}) {
  const { period = 'all', agent = null, format = 'text' } = options;
  loadTokenData();

  const usage = getTokenUsage(agent || 'all');
  const cost = calculateCost(usage);
  const suggestions = generateOptimizationSuggestions(usage);

  // 计算趋势
  const history = tokenCache.history || [];
  const recentHistory = history.slice(-100);

  let trend = 'stable';
  if (recentHistory.length >= 10) {
    const recentTotal = recentHistory.slice(-10).reduce((sum, h) => sum + h.inputTokens + h.outputTokens, 0);
    const previousTotal = recentHistory.slice(-20, -10).reduce((sum, h) => sum + h.inputTokens + h.outputTokens, 0);

    if (previousTotal > 0) {
      const change = (recentTotal - previousTotal) / previousTotal;
      trend = change > 0.1 ? 'increasing' : change < -0.1 ? 'decreasing' : 'stable';
    }
  }

  const report = {
    summary: {
      total: usage.total,
      input: usage.input,
      output: usage.output,
      cost: cost.total.toFixed(2)
    },
    byAgent: usage.byAgent,
    byCommand: usage.byCommand,
    cost,
    suggestions,
    trend
  };

  if (format === 'text') {
    return formatReportAsText(report);
  }

  return report;
}

/**
 * 格式化报告为文本
 * @param {TokenReport} report - Token报告
 * @returns {string} - 格式化的文本
 */
function formatReportAsText(report) {
  let output = `📊 Token Usage Report\n`;
  output += `${'='.repeat(50)}\n\n`;

  output += `Total Tokens: ${report.summary.total.toLocaleString()}\n`;
  output += `  Input:  ${report.summary.input.toLocaleString()}\n`;
  output += `  Output: ${report.summary.output.toLocaleString()}\n`;
  output += `  Cost:   $${report.summary.cost}\n\n`;

  output += `By Agent:\n`;
  const sortedAgents = Object.entries(report.byAgent).sort((a, b) => b[1] - a[1]);
  for (const [agent, total] of sortedAgents.slice(0, 5)) {
    const percentage = (total / report.summary.total * 100).toFixed(1);
    output += `  ${agent}: ${total.toLocaleString()} (${percentage}%)\n`;
  }

  output += `\n💡 Suggestions:\n`;
  for (const suggestion of report.suggestions.slice(0, 3)) {
    if (typeof suggestion === 'object') {
      output += `  [${suggestion.priority}] ${suggestion.message}\n`;
    } else {
      output += `  ${suggestion}\n`;
    }
  }

  return output;
}

/**
 * Hook主函数
 * @param {Object} context - Hook上下文
 */
function tokenOptimizerHook(context) {
  if (!CONFIG.enabled) {
    return;
  }

  const { toolName, toolInput, toolResult } = context;

  // 尝试从工具结果中提取Token信息
  if (toolResult && toolResult.usage) {
    trackTokens({
      sessionId: context.sessionId || 'default',
      agentType: context.agentType || 'general',
      command: toolName,
      inputTokens: toolResult.usage.input_tokens || toolResult.usage.input || 0,
      outputTokens: toolResult.usage.output_tokens || toolResult.usage.output || 0
    });
  }
}

/**
 * 重置统计数据
 */
function resetStats() {
  tokenCache = {
    sessions: {},
    totals: { input: 0, output: 0, total: 0 },
    byAgent: {},
    byCommand: {},
    history: []
  };
  saveTokenData();
}

// 导出
module.exports = {
  trackTokens,
  getTokenUsage,
  calculateCost,
  generateOptimizationSuggestions,
  generateReport,
  tokenOptimizerHook,
  resetStats,
  CONFIG
};