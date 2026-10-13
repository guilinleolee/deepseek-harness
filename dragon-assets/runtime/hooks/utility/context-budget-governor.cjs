/**
 * Context Budget Governor
 *
 * 天龙引擎 Token 优化 Phase 2.1
 * 功能：统一管理上下文预算，防止上下文膨胀
 *
 * 核心策略：
 * 1. 从 context window 派生所有预算
 * 2. 分段策略（小模型 vs 大模型）
 * 3. 工具参数/结果限制
 * 4. 溢出预警
 */

const TokenEstimator = require('./token-estimator.cjs');

// 默认配置
const DEFAULT_CONFIG = {
  // 保留量
  contextReserveFloor: 20000,  // 大模型最小保留
  smallModelReserveRatio: 1 / 8,  // 小模型保留 1/8

  // 阈值
  warningThreshold: 0.6,
  criticalThreshold: 0.85,

  // 工具参数限制
  toolArgumentChars: {
    small: 16000,   // 2K tokens
    large: 512000,  // 128K tokens
  },
  toolResultChars: {
    small: 32000,
    large: 160000,
  },

  // 大模型分界线
  largeContextThreshold: 64000,
};

// 模型配置
const MODEL_CONFIGS = {
  // 小模型
  'claude-haiku-4-5': {
    contextWindow: 200000,
    maxOutput: 8192,
    thinkingBudget: 0,
  },
  'claude-haiku': {
    contextWindow: 200000,
    maxOutput: 8192,
    thinkingBudget: 0,
  },

  // 中模型
  'claude-sonnet-4': {
    contextWindow: 200000,
    maxOutput: 8192,
    thinkingBudget: 10240,
  },
  'claude-sonnet-4-6': {
    contextWindow: 200000,
    maxOutput: 8192,
    thinkingBudget: 10240,
  },

  // 大模型
  'claude-opus-4-6': {
    contextWindow: 200000,
    maxOutput: 8192,
    thinkingBudget: 10240,
  },
  'claude-opus-4-7': {
    contextWindow: 200000,
    maxOutput: 8192,
    thinkingBudget: 10240,
  },

  // 其他模型（默认值）
  default: {
    contextWindow: 128000,
    maxOutput: 4096,
    thinkingBudget: 4096,
  },
};

class ContextBudgetGovernor {
  constructor(modelName = 'claude-sonnet-4-6', config = {}) {
    this.modelName = modelName;
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.modelConfig = MODEL_CONFIGS[modelName] || MODEL_CONFIGS.default;
  }

  /**
   * 获取预算快照
   * @returns {ContextBudgetSnapshot}
   */
  snapshot() {
    const { contextWindow, maxOutput, thinkingBudget } = this.modelConfig;
    const isLarge = contextWindow >= this.config.largeContextThreshold;

    // 计算保留量
    let reservedTokens;
    if (isLarge) {
      reservedTokens = Math.min(
        maxOutput + thinkingBudget + this.config.contextReserveFloor,
        Math.floor(contextWindow / 2)
      );
    } else {
      reservedTokens = Math.max(
        512,
        Math.floor(contextWindow * this.config.smallModelReserveRatio)
      );
    }

    const usableTokens = contextWindow - reservedTokens;

    return {
      modelName: this.modelName,
      contextWindow,
      reservedTokens,
      usableTokens,

      // 阈值
      warningThreshold: this.config.warningThreshold,
      criticalThreshold: this.config.criticalThreshold,

      // 工具限制
      toolArgumentMaxChars: isLarge
        ? this.config.toolArgumentChars.large
        : this.config.toolArgumentChars.small,
      toolResultMaxChars: isLarge
        ? this.config.toolResultChars.large
        : this.config.toolResultChars.small,

      // 模型能力
      isLargeModel: isLarge,
      maxOutput,
      thinkingBudget,
    };
  }

  /**
   * 检查当前使用量
   * @param {number} currentTokens
   * @returns {BudgetStatus}
   */
  checkBudget(currentTokens) {
    const snap = this.snapshot();
    const ratio = currentTokens / snap.contextWindow;
    const remaining = snap.contextWindow - currentTokens;

    let status = 'OK';
    let actions = [];

    if (ratio >= snap.criticalThreshold) {
      status = 'CRITICAL';
      actions = [
        '立即压缩历史',
        '拒绝新的大型上下文',
        '触发 Compaction',
      ];
    } else if (ratio >= snap.warningThreshold) {
      status = 'WARNING';
      actions = [
        '建议精简',
        '考虑压缩历史',
      ];
    }

    return {
      status,
      ratio,
      currentTokens,
      remainingTokens: remaining,
      usableTokens: snap.usableTokens,
      actions,
      snapshot: snap,
    };
  }

  /**
   * 检查是否需要触发压缩
   * @param {number} currentTokens
   * @returns {boolean}
   */
  needsCompaction(currentTokens) {
    const snap = this.snapshot();
    return currentTokens > snap.usableTokens * snap.criticalThreshold;
  }

  /**
   * 计算工具参数限制
   * @param {string} type - 'internal' | 'external'
   * @returns {number}
   */
  getToolArgumentLimit(type = 'internal') {
    const snap = this.snapshot();
    const ratio = type === 'external' ? 0.5 : 1;
    return Math.floor(snap.toolArgumentMaxChars * ratio);
  }

  /**
   * 计算工具结果限制
   * @param {string} type - 'internal' | 'external'
   * @returns {number}
   */
  getToolResultLimit(type = 'internal') {
    const snap = this.snapshot();
    const ratio = type === 'external' ? 0.5 : 1;
    return Math.floor(snap.toolResultMaxChars * ratio);
  }

  /**
   * 估算消息数组的 token 消耗
   * @param {Array} messages
   * @returns {number}
   */
  estimateMessages(messages) {
    return TokenEstimator.estimateMessages(messages, {
      systemOverhead: 200,
      messageOverhead: 50,
    });
  }

  /**
   * 截断消息到预算内
   * @param {Array} messages
   * @param {number} maxTokens
   * @returns {{messages: Array, summary: string}}
   */
  truncateMessages(messages, maxTokens) {
    const result = [];
    let usedTokens = 0;
    const systemOverhead = 200;
    const messageOverhead = 50;

    for (let i = messages.length - 1; i >= 0; i--) {
      const msg = messages[i];
      const contentTokens = typeof msg.content === 'string'
        ? TokenEstimator.estimate(msg.content)
        : 1000; // 多模态估计

      const totalTokens = systemOverhead + messageOverhead + contentTokens + usedTokens;

      if (totalTokens <= maxTokens) {
        result.unshift(msg);
        usedTokens = totalTokens;
      } else {
        break;
      }
    }

    const dropped = messages.length - result.length;
    const summary = dropped > 0
      ? `[压缩摘要] 保留 ${result.length} 条消息，丢弃 ${dropped} 条历史消息`
      : '';

    return { messages: result, summary };
  }

  /**
   * 生成优化建议
   * @param {BudgetStatus} status
   * @returns {Array<string>}
   */
  getSuggestions(status) {
    const suggestions = [];

    if (status.ratio > 0.9) {
      suggestions.push('立即执行 Compaction');
      suggestions.push('考虑使用更短的 System Prompt');
    }

    if (status.ratio > 0.8) {
      suggestions.push('压缩历史消息，保留最近 N 条');
      suggestions.push('移除不必要的工作文件引用');
    }

    if (status.ratio > 0.6) {
      suggestions.push('检查是否有重复的工具调用');
      suggestions.push('考虑精简 Tool Definitions');
    }

    if (status.remainingTokens < 10000) {
      suggestions.push('剩余空间不足 10K，避免新增大型上下文');
    }

    return suggestions;
  }

  /**
   * 分配 Agent 链预算
   * @param {number} totalBudget
   * @param {number} agentCount
   * @returns {Array<number>}
   */
  allocateChainBudget(totalBudget, agentCount) {
    // 前重后轻原则
    const weights = [];
    for (let i = 0; i < agentCount; i++) {
      weights.push((agentCount - i) * 2);
    }

    const totalWeight = weights.reduce((a, b) => a + b, 0);
    return weights.map(w => Math.floor(totalBudget * w / totalWeight));
  }

  /**
   * 获取模型列表
   * @returns {Array<string>}
   */
  static getSupportedModels() {
    return Object.keys(MODEL_CONFIGS);
  }

  /**
   * 快速创建预算检查
   * @param {string} modelName
   * @param {number} currentTokens
   * @returns {BudgetStatus}
   */
  static quickCheck(modelName, currentTokens) {
    const gov = new ContextBudgetGovernor(modelName);
    return gov.checkBudget(currentTokens);
  }
}

/**
 * 预算装饰器
 * @param {ContextBudgetGovernor} gov
 * @param {Function} fn
 */
function withBudgetGuard(gov) {
  return async (fn, ...args) => {
    const result = await fn(...args);

    // 检查结果大小
    if (typeof result === 'string') {
      const tokens = TokenEstimator.estimate(result);
      const limit = gov.getToolResultLimit();

      if (tokens > limit) {
        return TokenEstimator.truncate(
          result,
          limit,
          'auto',
          '\n[...结果已截断...]'
        );
      }
    }

    return result;
  };
}

/**
 * 链式预算管理
 */
class ChainBudgetManager {
  constructor(config = {}) {
    this.governor = new ContextBudgetGovernor(config.model || 'claude-sonnet-4-6', config);
    this.budgets = [];
    this.history = [];
  }

  /**
   * 设置链预算
   * @param {Array<{name: string, weight: number}>} agents
   */
  setupChain(agents) {
    const snap = this.governor.snapshot();
    const totalBudget = snap.usableTokens;

    this.budgets = this.governor.allocateChainBudget(totalBudget, agents.length);

    return agents.map((agent, i) => ({
      ...agent,
      budget: this.budgets[i],
    }));
  }

  /**
   * 记录使用
   * @param {string} agentId
   * @param {number} tokens
   */
  recordUsage(agentId, tokens) {
    this.history.push({
      timestamp: Date.now(),
      agentId,
      tokens,
    });
  }

  /**
   * 获取统计
   */
  getStats() {
    const byAgent = {};
    for (const entry of this.history) {
      if (!byAgent[entry.agentId]) {
        byAgent[entry.agentId] = { total: 0, count: 0 };
      }
      byAgent[entry.agentId].total += entry.tokens;
      byAgent[entry.agentId].count++;
    }

    return {
      totalUsed: this.history.reduce((sum, e) => sum + e.tokens, 0),
      byAgent,
      snapshots: this.budgets.length,
    };
  }
}

module.exports = {
  ContextBudgetGovernor,
  ChainBudgetManager,
  withBudgetGuard,
  MODEL_CONFIGS,
  DEFAULT_CONFIG,
};
