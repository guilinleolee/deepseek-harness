/**
 * Free LLM Provider Aggregator (V1.0)
 *
 * 聚合14个免费LLM API提供商和15个试用额度提供商
 *
 * 来源: https://github.com/cheahjs/free-llm-api-resources (16,644 ⭐)
 *
 * @author 天龙引擎团队
 * @version 1.0.0
 */

class FreeLLMAggregator {
  constructor() {
    // 免费提供商配置
    this.freeProviders = {
      // ========== P0优先级 (推荐集成) ==========
      groq: {
        name: 'Groq',
        apiKeyEnv: 'GROQ_API_KEY',
        baseUrl: 'https://api.groq.com/openai/v1',
        limits: {
          rpm: 30,
          tpm: 6000,
          rpd: 14400  // 不同模型不同限制
        },
        models: {
          chat: [
            'llama-3.3-70b-versatile',
            'llama-3.1-8b-instant',
            'llama-4-scout-17b-16e-instruct',
            'llama-4-maverick-17b-128e-instruct'
          ],
          reasoning: ['deepseek-r1-distill-llama-70b', 'qwen-qwq-32b'],
          code: ['codestral-2501']
        },
        features: {
          latency: 'ultra-low',  // 毫秒级
          multimodal: false,
          streaming: true
        },
        priority: 'P0',
        quality: {
          chat: 0.90,
          reasoning: 0.88,
          code: 0.92
        },
        openaiCompatible: true
      },

      googleStudio: {
        name: 'Google AI Studio',
        apiKeyEnv: 'GOOGLE_AI_STUDIO_API_KEY',
        baseUrl: 'https://generativelanguage.googleapis.com/v1beta',
        limits: {
          rpm: 5,
          tpm: 250000,  // 250K tokens/分钟
          rpd: null
        },
        models: {
          chat: ['gemini-3-flash', 'gemini-2.5-flash'],
          reasoning: ['gemini-2.5-pro'],
          multimodal: ['gemini-3-flash', 'gemma-3-27b-it']
        },
        features: {
          latency: 'low',
          multimodal: true,
          streaming: true
        },
        priority: 'P0',
        quality: {
          chat: 0.92,
          reasoning: 0.90,
          multimodal: 0.88
        },
        openaiCompatible: false,
        note: '非UK/CH/EEA/EU地区数据用于训练'
      },

      openrouter: {
        name: 'OpenRouter',
        apiKeyEnv: 'OPENROUTER_API_KEY',
        baseUrl: 'https://openrouter.ai/api/v1',
        limits: {
          rpm: 20,
          tpm: null,
          rpd: 50  // 免费层
        },
        models: {
          chat: [
            'meta-llama/llama-3.3-70b-instruct:free',
            'google/gemma-3-27b-it:free',
            'mistralai/mistral-small-3.1-24b-instruct:free',
            'qwen/qwen3-4b:free'
          ],
          reasoning: ['deepseek/deepseek-r1:free', 'qwen/qwq-32b:free'],
          code: ['mistralai/codestral-2501:free']
        },
        features: {
          latency: 'medium',
          multimodal: false,
          streaming: true
        },
        priority: 'P0',
        quality: {
          chat: 0.88,
          reasoning: 0.90,
          code: 0.88
        },
        openaiCompatible: true,
        headers: {
          'HTTP-Referer': process.env.OPENROUTER_REFERER || 'https://claude.local',
          'X-Title': process.env.OPENROUTER_TITLE || 'Dragon Engine'
        }
      },

      // ========== P1优先级 ==========
      cerebras: {
        name: 'Cerebras',
        apiKeyEnv: 'CEREBRAS_API_KEY',
        baseUrl: 'https://api.cerebras.ai/v1',
        limits: {
          rpm: 30,
          tpm: 60000,
          rpd: null,
          tpd: 1000000  // 1M tokens/天
        },
        models: {
          chat: ['llama-3.1-8b', 'llama-3.3-70b'],
          reasoning: []
        },
        features: {
          latency: 'low',
          multimodal: false,
          streaming: true
        },
        priority: 'P1',
        quality: {
          chat: 0.85
        },
        openaiCompatible: true
      },

      cloudflare: {
        name: 'Cloudflare Workers AI',
        apiKeyEnv: 'CLOUDFLARE_API_TOKEN',
        baseUrl: 'https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1',
        limits: {
          rpm: null,
          tpm: null,
          neuronsPerDay: 10000
        },
        models: {
          chat: ['@cf/meta/llama-3.3-70b-instruct-fp8-fast'],
          reasoning: ['@cf/deepseek-ai/deepseek-r1-distill-llama-70b']
        },
        features: {
          latency: 'medium',
          multimodal: false,
          streaming: true,
          edgeDeploy: true
        },
        priority: 'P1',
        quality: {
          chat: 0.82
        },
        openaiCompatible: true
      },

      mistral: {
        name: 'Mistral La Plateforme',
        apiKeyEnv: 'MISTRAL_API_KEY',
        baseUrl: 'https://api.mistral.ai/v1',
        limits: {
          rpm: 1,
          tpm: 500000,
          tpmMonth: 1000000000  // 1B tokens/月
        },
        models: {
          chat: ['mistral-small-3.1-24b-instruct-2503'],
          code: ['codestral-2501']
        },
        features: {
          latency: 'medium',
          multimodal: false,
          streaming: true
        },
        priority: 'P1',
        quality: {
          chat: 0.88,
          code: 0.90
        },
        openaiCompatible: true,
        requiresPhone: true
      },

      // ========== P2优先级 ==========
      nvidia: {
        name: 'NVIDIA NIM',
        apiKeyEnv: 'NVIDIA_API_KEY',
        baseUrl: 'https://integrate.api.nvidia.com/v1',
        limits: {
          rpm: 40,
          tpm: null,
          rpd: null
        },
        models: {
          chat: ['meta/llama-3.3-70b-instruct'],
          reasoning: ['deepseek-ai/deepseek-r1']
        },
        features: {
          latency: 'medium',
          multimodal: false,
          streaming: true
        },
        priority: 'P2',
        quality: {
          chat: 0.85
        },
        openaiCompatible: true,
        requiresPhone: true
      },

      github: {
        name: 'GitHub Models',
        apiKeyEnv: 'GITHUB_TOKEN',
        baseUrl: 'https://models.inference.ai.azure.com',
        limits: {
          rpm: null,  // 依赖Copilot订阅等级
          tpm: null,
          rpd: null
        },
        models: {
          chat: ['gpt-4o', 'gpt-4o-mini'],
          reasoning: ['DeepSeek-R1', 'o1-preview', 'o3-mini'],
          code: ['Codestral-2501']
        },
        features: {
          latency: 'medium',
          multimodal: false,
          streaming: true
        },
        priority: 'P2',
        quality: {
          chat: 0.93,
          reasoning: 0.92
        },
        openaiCompatible: true,
        requiresCopilot: true
      },

      cohere: {
        name: 'Cohere',
        apiKeyEnv: 'COHERE_API_KEY',
        baseUrl: 'https://api.cohere.ai/v2',
        limits: {
          rpm: 20,
          tpm: null,
          rpmMonth: 1000
        },
        models: {
          chat: ['command-a-03-2025', 'command-r7b-12-2024'],
          multilingual: ['aya-exa-3-8b', 'aya-vision-8b']
        },
        features: {
          latency: 'medium',
          multimodal: false,
          streaming: true
        },
        priority: 'P2',
        quality: {
          chat: 0.85,
          multilingual: 0.88
        },
        openaiCompatible: false
      }
    };

    // 试用额度提供商
    this.trialProviders = {
      hyperbolic: {
        name: 'Hyperbolic',
        apiKeyEnv: 'HYPERBOLIC_API_KEY',
        baseUrl: 'https://api.hyperbolic.xyz/v1',
        trialCredits: '$1',
        models: ['deepseek-ai/DeepSeek-V3', 'meta-llama/Meta-Llama-3.1-405B-Instruct'],
        priority: 'P1'
      },
      sambanova: {
        name: 'SambaNova Cloud',
        apiKeyEnv: 'SAMBANOVA_API_KEY',
        baseUrl: 'https://api.sambanova.ai/v1',
        trialCredits: '$5/3月',
        models: ['DeepSeek-V3.2', 'Llama-4-Maverick-17B-128E'],
        priority: 'P1'
      },
      alibaba: {
        name: 'Alibaba Cloud',
        apiKeyEnv: 'DASHSCOPE_API_KEY',
        baseUrl: 'https://dashscope.aliyuncs.com/api/v1',
        trialCredits: '100万tokens/模型',
        models: ['qwen-turbo', 'qwen-plus', 'qwen-max'],
        priority: 'P1'
      },
      scaleway: {
        name: 'Scaleway',
        apiKeyEnv: 'SCALEWAY_API_KEY',
        baseUrl: 'https://api.scaleway.com/ai/v1',
        trialCredits: '100万tokens',
        models: ['qwen3-235b-a22b', 'gemma-3-27b-it', 'deepseek-r1-distill-llama-70b'],
        priority: 'P2'
      },
      fireworks: {
        name: 'Fireworks AI',
        apiKeyEnv: 'FIREWORKS_API_KEY',
        baseUrl: 'https://api.fireworks.ai/inference/v1',
        trialCredits: '$1',
        models: ['accounts/fireworks/models/llama-v3p3-70b-instruct'],
        priority: 'P2'
      }
    };

    // 模型能力映射
    this.modelCapabilities = {
      // 推理模型
      'deepseek-r1': { reasoning: true, quality: 0.92, providers: ['groq', 'openrouter', 'nvidia', 'cloudflare'] },
      'qwq-32b': { reasoning: true, quality: 0.88, providers: ['groq', 'openrouter'] },
      'o1-preview': { reasoning: true, quality: 0.95, providers: ['github'] },
      'o3-mini': { reasoning: true, quality: 0.90, providers: ['github'] },

      // 大模型 (70B+)
      'llama-3.3-70b': { quality: 0.90, providers: ['groq', 'openrouter', 'cerebras', 'nvidia', 'cloudflare'] },
      'llama-4-maverick': { quality: 0.92, providers: ['groq', 'sambanova'] },
      'llama-4-scout': { quality: 0.90, multimodal: true, providers: ['groq'] },

      // 多模态
      'gemma-3-27b': { multimodal: true, quality: 0.85, providers: ['googleStudio', 'openrouter'] },
      'qwen2.5-vl': { multimodal: true, quality: 0.88, providers: ['alibaba'] },

      // 代码
      'codestral': { code: true, quality: 0.92, providers: ['groq', 'mistral', 'openrouter', 'github'] },
      'qwen3-coder': { code: true, quality: 0.88, providers: ['alibaba'] }
    };
  }

  /**
   * 获取所有免费提供商
   */
  getFreeProviders() {
    return Object.entries(this.freeProviders).map(([key, config]) => ({
      id: key,
      ...config,
      hasApiKey: !!process.env[config.apiKeyEnv]
    }));
  }

  /**
   * 获取可用提供商（有API Key）
   */
  getAvailableProviders() {
    return this.getFreeProviders().filter(p => p.hasApiKey);
  }

  /**
   * 获取支持特定模型的提供商
   */
  getProvidersForModel(modelId) {
    const capability = this.modelCapabilities[modelId];
    if (!capability) return [];

    return capability.providers.map(p => ({
      provider: p,
      config: this.freeProviders[p],
      quality: capability.quality
    })).filter(p => p.config);
  }

  /**
   * 获取支持特定任务类型的提供商
   */
  getProvidersForTask(taskType) {
    return this.getFreeProviders().filter(p => {
      if (!p.models[taskType]) return false;
      return p.models[taskType].length > 0;
    });
  }

  /**
   * 按限制筛选提供商
   */
  getProvidersByLimits(requirements) {
    const { minRpm, minTpm, minRpd } = requirements;

    return this.getFreeProviders().filter(p => {
      if (minRpm && p.limits.rpm && p.limits.rpm < minRpm) return false;
      if (minTpm && p.limits.tpm && p.limits.tpm < minTpm) return false;
      if (minRpd && p.limits.rpd && p.limits.rpd < minRpd) return false;
      return true;
    });
  }

  /**
   * 获取最优提供商
   */
  getBestProvider(options = {}) {
    const { model, taskType, priority = 'cost' } = options;

    let candidates = this.getAvailableProviders();

    // 按模型筛选
    if (model) {
      const modelProviders = this.getProvidersForModel(model);
      candidates = candidates.filter(c =>
        modelProviders.some(mp => mp.provider === c.id)
      );
    }

    // 按任务类型筛选
    if (taskType) {
      candidates = candidates.filter(c =>
        c.models[taskType] && c.models[taskType].length > 0
      );
    }

    if (candidates.length === 0) {
      return null;
    }

    // 按优先级排序
    const priorityOrder = { P0: 0, P1: 1, P2: 2 };
    candidates.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);

    // 按策略选择
    switch (priority) {
      case 'latency':
        return candidates.find(c => c.features?.latency === 'ultra-low') || candidates[0];
      case 'quality':
        return candidates.sort((a, b) =>
          (b.quality?.[taskType] || 0.8) - (a.quality?.[taskType] || 0.8)
        )[0];
      case 'quota':
        return candidates.sort((a, b) =>
          (b.limits?.tpd || b.limits?.rpd || 0) - (a.limits?.tpd || a.limits?.rpd || 0)
        )[0];
      case 'cost':
      default:
        return candidates[0];  // 已经按优先级排序
    }
  }

  /**
   * 获取提供商配置
   */
  getProviderConfig(providerId) {
    const provider = this.freeProviders[providerId];
    if (!provider) {
      throw new Error(`Unknown provider: ${providerId}`);
    }
    return provider;
  }

  /**
   * 检查API Key是否可用
   */
  hasApiKey(providerId) {
    const provider = this.freeProviders[providerId];
    if (!provider) return false;
    return !!process.env[provider.apiKeyEnv];
  }

  /**
   * 打印提供商摘要
   */
  printSummary() {
    console.log('\n🆓 Free LLM Providers Summary');
    console.log('='.repeat(60));

    const providers = this.getFreeProviders();
    const available = providers.filter(p => p.hasApiKey);

    console.log(`\n📊 Total: ${providers.length} providers, ${available.length} available\n`);

    const priorityGroups = { P0: [], P1: [], P2: [] };
    providers.forEach(p => {
      priorityGroups[p.priority].push(p);
    });

    for (const [priority, items] of Object.entries(priorityGroups)) {
      if (items.length === 0) continue;
      console.log(`\n### Priority ${priority}`);
      for (const p of items) {
        const status = p.hasApiKey ? '✅' : '❌';
        console.log(`  ${status} ${p.name}`);
        console.log(`     Limits: ${p.limits.rpm || '?'} RPM, ${p.limits.tpm || '?'} TPM`);
      }
    }

    console.log('\n' + '='.repeat(60));
  }
}

// 单例
let aggregatorInstance = null;

function getAggregator() {
  if (!aggregatorInstance) {
    aggregatorInstance = new FreeLLMAggregator();
  }
  return aggregatorInstance;
}

module.exports = {
  FreeLLMAggregator,
  getAggregator
};