/**
 * 模型路由器 (简化版 SquillaRouter)
 *
 * 天龙引擎 Token 优化 Phase 3.1
 * 功能：根据任务复杂度动态选择模型层级
 *
 * 核心策略：
 * 1. 任务复杂度评估
 * 2. 四级分层路由（C0-C3）
 * 3. 推理深度控制
 */

const TokenEstimator = require('./token-estimator.cjs');

// 推理模式
const ThinkingMode = {
  NONE: 'none',
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
};

// 模型层级
const ModelTier = {
  C0: 'c0',  // 简单任务
  C1: 'c1',  // 中等任务
  C2: 'c2',  // 复杂任务
  C3: 'c3',  // 高难任务
};

// 模型配置
const TIER_MODELS = {
  [ModelTier.C0]: {
    name: 'qwen3.7-flash',
    provider: 'openai',
    cost: 0.1,
    capability: 0.3,
    thinking: ThinkingMode.NONE,
  },
  [ModelTier.C1]: {
    name: 'deepseek-v4-flash',
    provider: 'openai',
    cost: 0.2,
    capability: 0.6,
    thinking: ThinkingMode.LOW,
  },
  [ModelTier.C2]: {
    name: 'glm-5.2',
    provider: 'openai',
    cost: 0.5,
    capability: 0.8,
    thinking: ThinkingMode.MEDIUM,
  },
  [ModelTier.C3]: {
    name: 'claude-opus-4-6',
    provider: 'anthropic',
    cost: 1.0,
    capability: 1.0,
    thinking: ThinkingMode.HIGH,
  },
};

// 复杂关键词
const COMPLEX_KEYWORDS = [
  '分析', '设计', '架构', '优化', '实现', 'debug',
  'analyze', 'design', 'architecture', 'optimize',
];

// 简单关键词
const SIMPLE_KEYWORDS = [
  '查询', '格式化', '翻译', '检查',
  'lookup', 'format', 'translate', 'check',
];

// 默认配置
const DEFAULT_CONFIG = {
  complexityThresholds: {
    low: 0.2,
    medium: 0.5,
    high: 0.8,
  },
  defaultTier: ModelTier.C1,
};

class ModelRouter {
  constructor(config = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
  }

  /**
   * 路由决策
   * @param {TaskContext} task - 任务上下文
   * @returns {RouteDecision}
   */
  route(task) {
    const complexity = this.assessComplexity(task);
    const tier = this.complexityToTier(complexity);
    const modelConfig = TIER_MODELS[tier];

    return {
      tier,
      model: modelConfig.name,
      provider: modelConfig.provider,
      cost: modelConfig.cost,
      thinking: modelConfig.thinking,
      complexity,
      promptPolicy: this.getPromptPolicy(complexity),
      reasoning: this.getReasoningHint(complexity),
    };
  }

  /**
   * 评估任务复杂度
   * @param {TaskContext} task
   * @returns {number} 0-1
   */
  assessComplexity(task) {
    let score = 0;

    const input = (task.input || '').toLowerCase();
    const inputLength = (task.input || '').length;

    // 1. 文本长度（越长越复杂）
    const lengthScore = Math.min(inputLength / 5000, 1) * 0.2;
    score += lengthScore;

    // 2. 代码检测
    if (task.hasCode || /```[\s\S]*?```/.test(input)) {
      score += 0.15;
    }

    // 3. 多语言检测
    if (task.languages?.length > 1) {
      score += 0.1;
    }

    // 4. 关键词匹配
    const complexMatches = COMPLEX_KEYWORDS.filter(k => input.includes(k)).length;
    const simpleMatches = SIMPLE_KEYWORDS.filter(k => input.includes(k)).length;

    score += Math.min(complexMatches / 3, 1) * 0.25;
    score -= Math.min(simpleMatches / 2, 1) * 0.1;

    // 5. 工具调用数量
    if (task.relatedTools?.length > 0) {
      const toolScore = Math.min(task.relatedTools.length / 5, 1) * 0.15;
      score += toolScore;
    }

    // 6. 历史上下文
    if (task.historyLength > 10) {
      score += Math.min(task.historyLength / 50, 1) * 0.1;
    }

    // 7. 特殊标记
    if (task.isCritical || task.hasErrors) {
      score += 0.15;
    }

    return Math.max(0, Math.min(1, score));
  }

  /**
   * 复杂度转层级
   */
  complexityToTier(complexity) {
    const { low, medium, high } = this.config.complexityThresholds;

    if (complexity < low) return ModelTier.C0;
    if (complexity < medium) return ModelTier.C1;
    if (complexity < high) return ModelTier.C2;
    return ModelTier.C3;
  }

  /**
   * 获取 Prompt 策略
   */
  getPromptPolicy(complexity) {
    if (complexity < 0.3) return 'minimal';
    if (complexity < 0.7) return 'standard';
    return 'full';
  }

  /**
   * 获取推理提示
   */
  getReasoningHint(complexity) {
    if (complexity < 0.2) {
      return '直接回答，简洁明了';
    }
    if (complexity < 0.5) {
      return '简要分析后回答';
    }
    if (complexity < 0.8) {
      return '详细分析，考虑多种方案';
    }
    return '深度推理，全面分析，考虑边界情况';
  }

  /**
   * 获取层级信息
   */
  getTierInfo(tier) {
    return {
      tier,
      ...TIER_MODELS[tier],
    };
  }

  /**
   * 获取所有层级
   */
  getAllTiers() {
    return Object.entries(TIER_MODELS).map(([tier, config]) => ({
      tier,
      ...config,
    }));
  }

  /**
   * 估算节省
   */
  estimateSavings(task) {
    const routeResult = this.route(task);
    const baseline = TIER_MODELS[ModelTier.C3].cost;

    return {
      selectedModel: routeResult.model,
      selectedCost: routeResult.cost,
      baselineCost: baseline,
      savings: baseline - routeResult.cost,
      savingsPercent: ((baseline - routeResult.cost) / baseline * 100).toFixed(1) + '%',
    };
  }
}

/**
 * 快速路由
 */
function quickRoute(input) {
  const router = new ModelRouter();
  return router.route({ input });
}

/**
 * 任务上下文构建器
 */
class TaskContextBuilder {
  constructor() {
    this.context = {
      input: '',
      hasCode: false,
      languages: [],
      relatedTools: [],
      historyLength: 0,
      isCritical: false,
      hasErrors: false,
    };
  }

  setInput(input) {
    this.context.input = input;
    return this;
  }

  setHasCode(hasCode) {
    this.context.hasCode = hasCode;
    return this;
  }

  setLanguages(languages) {
    this.context.languages = languages;
    return this;
  }

  setRelatedTools(tools) {
    this.context.relatedTools = tools;
    return this;
  }

  setHistoryLength(length) {
    this.context.historyLength = length;
    return this;
  }

  setCritical(isCritical) {
    this.context.isCritical = isCritical;
    return this;
  }

  setHasErrors(hasErrors) {
    this.context.hasErrors = hasErrors;
    return this;
  }

  build() {
    return { ...this.context };
  }
}

module.exports = {
  ModelRouter,
  TaskContextBuilder,
  quickRoute,
  ThinkingMode,
  ModelTier,
  TIER_MODELS,
  DEFAULT_CONFIG,
};
