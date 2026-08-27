/**
 * Smart Provider Router (V1.0)
 *
 * 智能LLM提供商路由器 - 根据任务需求自动选择最优提供商
 *
 * @author 天龙引擎团队
 * @version 1.0.0
 */

const FreeLLMAggregator = require('../free-llm-provider-aggregator/free_llm_aggregator.js');

class SmartProviderRouter {
  constructor(options = {}) {
    this.aggregator = new FreeLLMAggregator();
    this.strategy = options.strategy || 'cost';
    this.fallback = options.fallback !== false;
    this.debug = options.debug || false;

    // 路由历史（用于学习）
    this.history = [];

    // 提供商健康状态
    this.health = {};

    // 配额追踪
    this.quotaUsage = {};
  }

  /**
   * 智能路由选择
   */
  async route(options = {}) {
    const {
      prompt,
      taskType = 'text',
      qualityRequirement = 'normal',
      latencyRequirement = 'normal',
      model,
      strategy = this.strategy
    } = options;

    if (this.debug) {
      console.log('[SmartRouter] Routing request:', {
        taskType,
        qualityRequirement,
        latencyRequirement,
        model,
        strategy
      });
    }

    // Step 1: 获取候选提供商
    let candidates = this.getCandidates(taskType, model);

    if (candidates.length === 0) {
      throw new Error('No available providers for this task');
    }

    // Step 2: 按策略排序
    candidates = this.sortByStrategy(candidates, strategy, {
      taskType,
      qualityRequirement,
      latencyRequirement
    });

    // Step 3: 选择最优提供商
    const selected = candidates[0];

    // Step 4: 构建响应
    const result = {
      provider: selected.id,
      model: this.selectModel(selected, taskType, model),
      reason: this.getReason(selected, strategy),
      alternatives: candidates.slice(1, 3).map(c => ({
        provider: c.id,
        model: this.selectModel(c, taskType, model)
      })),
      estimatedCost: 0,  // 免费提供商
      estimatedLatency: this.getEstimatedLatency(selected),
      quality: selected.quality?.[taskType] || 0.85
    };

    // 记录历史
    this.recordHistory(result);

    if (this.debug) {
      console.log('[SmartRouter] Selected:', result);
    }

    return result;
  }

  /**
   * 获取候选提供商
   */
  getCandidates(taskType, model) {
    let candidates = this.aggregator.getAvailableProviders();

    // 按模型筛选
    if (model) {
      const modelProviders = this.aggregator.getProvidersForModel(model);
      if (modelProviders.length > 0) {
        candidates = candidates.filter(c =>
          modelProviders.some(mp => mp.provider === c.id)
        );
      }
    }

    // 按任务类型筛选
    if (taskType && taskType !== 'text') {
      candidates = candidates.filter(c =>
        c.models[taskType] && c.models[taskType].length > 0
      );
    }

    // 过滤不健康的提供商
    candidates = candidates.filter(c => {
      const health = this.health[c.id];
      return !health || health.status !== 'down';
    });

    return candidates;
  }

  /**
   * 按策略排序
   */
  sortByStrategy(candidates, strategy, context) {
    const { taskType, qualityRequirement, latencyRequirement } = context;

    switch (strategy) {
      case 'latency':
        // 延迟优先：Groq > Cerebras > 其他
        return candidates.sort((a, b) => {
          const latencyScore = { 'ultra-low': 0, 'low': 1, 'medium': 2, 'high': 3 };
          const aScore = latencyScore[a.features?.latency] || 2;
          const bScore = latencyScore[b.features?.latency] || 2;
          return aScore - bScore;
        });

      case 'quality':
        // 质量优先：按质量评分排序
        return candidates.sort((a, b) => {
          const aQuality = a.quality?.[taskType] || 0.8;
          const bQuality = b.quality?.[taskType] || 0.8;
          return bQuality - aQuality;
        });

      case 'reasoning':
        // 推理优先：有推理模型的提供商优先
        return candidates.sort((a, b) => {
          const hasReasoningA = a.models.reasoning && a.models.reasoning.length > 0;
          const hasReasoningB = b.models.reasoning && b.models.reasoning.length > 0;
          if (hasReasoningA && !hasReasoningB) return -1;
          if (!hasReasoningA && hasReasoningB) return 1;
          return (b.quality?.reasoning || 0) - (a.quality?.reasoning || 0);
        });

      case 'quota':
        // 配额优先：按日配额排序
        return candidates.sort((a, b) => {
          const aQuota = a.limits?.tpd || a.limits?.rpd || 0;
          const bQuota = b.limits?.tpd || b.limits?.rpd || 0;
          return bQuota - aQuota;
        });

      case 'cost':
      default:
        // 成本优先：按优先级排序（P0 > P1 > P2）
        const priorityOrder = { P0: 0, P1: 1, P2: 2 };
        return candidates.sort((a, b) => {
          const aPriority = priorityOrder[a.priority] || 2;
          const bPriority = priorityOrder[b.priority] || 2;
          if (aPriority !== bPriority) return aPriority - bPriority;
          // 同优先级按延迟排序
          const latencyScore = { 'ultra-low': 0, 'low': 1, 'medium': 2 };
          const aScore = latencyScore[a.features?.latency] || 2;
          const bScore = latencyScore[b.features?.latency] || 2;
          return aScore - bScore;
        });
    }
  }

  /**
   * 选择模型
   */
  selectModel(provider, taskType, preferredModel) {
    // 如果指定了模型且提供商支持
    if (preferredModel) {
      const allModels = [
        ...(provider.models.chat || []),
        ...(provider.models.reasoning || []),
        ...(provider.models.code || []),
        ...(provider.models.multimodal || [])
      ];
      if (allModels.some(m => m.includes(preferredModel) || preferredModel.includes(m))) {
        return preferredModel;
      }
    }

    // 按任务类型选择
    const models = provider.models[taskType];
    if (models && models.length > 0) {
      // 选择第一个（通常是默认模型）
      return models[0];
    }

    // 回退到chat模型
    return provider.models.chat?.[0] || 'unknown';
  }

  /**
   * 获取选择原因
   */
  getReason(provider, strategy) {
    const reasons = {
      cost: provider.priority === 'P0' ? '最高优先级免费提供商' : '免费提供商',
      latency: provider.features?.latency === 'ultra-low' ? '毫秒级延迟' : '低延迟',
      quality: `高质量评分 (${(provider.quality?.chat || 0.85).toFixed(2)})`,
      reasoning: provider.models.reasoning?.length > 0 ? '支持推理模型' : '推理能力',
      quota: `高配额 (${provider.limits?.tpd || provider.limits?.rpd || '?'}/天)`
    };
    return reasons[strategy] || reasons.cost;
  }

  /**
   * 获取预估延迟
   */
  getEstimatedLatency(provider) {
    const latencyMap = {
      'ultra-low': '100-500ms',
      'low': '500ms-2s',
      'medium': '2-5s',
      'high': '5s+'
    };
    return latencyMap[provider.features?.latency] || '2-5s';
  }

  /**
   * 记录历史
   */
  recordHistory(result) {
    this.history.push({
      timestamp: Date.now(),
      ...result
    });

    // 保留最近100条
    if (this.history.length > 100) {
      this.history.shift();
    }
  }

  /**
   * 更新提供商健康状态
   */
  updateHealth(providerId, status, latency = null, error = null) {
    this.health[providerId] = {
      status,  // 'healthy', 'degraded', 'down'
      lastCheck: Date.now(),
      latency,
      error
    };
  }

  /**
   * 获取提供商统计
   */
  getStats() {
    const stats = {
      totalRequests: this.history.length,
      providerUsage: {},
      avgLatency: {},
      errorRate: {}
    };

    // 统计使用情况
    for (const record of this.history) {
      const provider = record.provider;
      stats.providerUsage[provider] = (stats.providerUsage[provider] || 0) + 1;
    }

    return stats;
  }

  /**
   * 打印摘要
   */
  printSummary() {
    const stats = this.getStats();

    console.log('\n📊 Smart Router Statistics');
    console.log('='.repeat(50));
    console.log(`Total Requests: ${stats.totalRequests}`);
    console.log('\nProvider Usage:');

    for (const [provider, count] of Object.entries(stats.providerUsage)) {
      const pct = ((count / stats.totalRequests) * 100).toFixed(1);
      console.log(`  ${provider}: ${count} (${pct}%)`);
    }

    console.log('\nHealth Status:');
    for (const [provider, health] of Object.entries(this.health)) {
      const statusIcon = health.status === 'healthy' ? '✅' :
                         health.status === 'degraded' ? '⚠️' : '❌';
      console.log(`  ${statusIcon} ${provider}: ${health.status}`);
    }

    console.log('='.repeat(50));
  }
}

// 单例
let routerInstance = null;

function getSmartRouter(options) {
  if (!routerInstance) {
    routerInstance = new SmartProviderRouter(options);
  }
  return routerInstance;
}

module.exports = {
  SmartProviderRouter,
  getSmartRouter
};