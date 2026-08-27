#!/usr/bin/env node
/**
 * AI Three-Tier Fallback Router
 * 三层自动降级路由核心引擎
 *
 * 来源: decolua/9router
 * 天龙引擎V8.87升级
 */

const https = require('https');
const http = require('http');

// ============ 配置 ============
const CONFIG = {
  tiers: {
    1: {
      name: 'Subscription',
      providers: [
        { name: 'claude', priority: 1, quota: 100000 },
        { name: 'codex', priority: 2, quota: 50000 }
      ]
    },
    2: {
      name: 'Cheap',
      providers: [
        { name: 'glm-4.7', priority: 1, quota: 500000 },
        { name: 'minimax', priority: 2, quota: 300000 },
        { name: 'kimi-k2', priority: 3, quota: 200000 }
      ]
    },
    3: {
      name: 'Free',
      providers: [
        { name: 'iflow', priority: 1, quota: 10000 },
        { name: 'qwen', priority: 2, quota: 5000 },
        { name: 'kiro', priority: 3, quota: 3000 }
      ]
    }
  },
  routing: {
    defaultStrategy: 'balanced',
    timeoutMs: 30000,
    maxRetries: 3
  },
  monitoring: {
    healthCheckInterval: 300,
    quotaAlertThreshold: 0.1
  }
};

// ============ 状态 ============
let state = {
  currentTier: 1,
  currentProvider: 'claude',
  quotaUsed: {},
  fallbackHistory: [],
  costSavings: { total: 0, saved: 0 },
  healthStatus: {}
};

// ============ 核心类 ============
class AIThreeTierFallback {
  constructor(config = CONFIG) {
    this.config = config;
    this.loadState();
  }

  loadState() {
    try {
      const fs = require('fs');
      const stateFile = process.env.HOME + '/.claude/skills/ai-three-tier-fallback/state.json';
      if (fs.existsSync(stateFile)) {
        const data = fs.readFileSync(stateFile, 'utf-8');
        state = { ...state, ...JSON.parse(data) };
      }
    } catch (e) {
      // 使用默认状态
    }
  }

  saveState() {
    try {
      const fs = require('fs');
      const stateFile = process.env.HOME + '/.claude/skills/ai-three-tier-fallback/state.json';
      const dir = require('path').dirname(stateFile);
      if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
      fs.writeFileSync(stateFile, JSON.stringify(state, null, 2));
    } catch (e) {
      console.error('Failed to save state:', e.message);
    }
  }

  // 路由请求
  async route(options) {
    const { prompt, type = 'balanced', tier = 1 } = options;
    let currentTier = tier;
    let lastError = null;

    for (let attempt = 0; attempt < this.config.routing.maxRetries; attempt++) {
      try {
        const result = await this._tryTier(currentTier, prompt);
        return result;
      } catch (error) {
        lastError = error;
        const trigger = this._classifyError(error);

        if (this._shouldFallback(trigger)) {
          const previousTier = currentTier;
          currentTier = this._getNextTier(currentTier);

          if (currentTier > 3) {
            throw new Error('All tiers exhausted: ' + lastError.message);
          }

          this._logFallback({
            requestId: this._generateId(),
            originalTier: previousTier,
            originalProvider: state.currentProvider,
            targetTier: currentTier,
            targetProvider: this._getNextProvider(currentTier),
            trigger,
            originalError: lastError.message
          });
        }
      }
    }

    throw lastError;
  }

  // 尝试指定Tier
  async _tryTier(tier, prompt) {
    const provider = this._getNextProvider(tier);
    const config = this._getProviderConfig(provider);

    if (!config) {
      throw new Error(`No provider available for tier ${tier}`);
    }

    // 更新状态
    state.currentTier = tier;
    state.currentProvider = provider;

    // 根据提供商调用
    switch (provider) {
      case 'claude':
        return this._callClaude(config, prompt);
      case 'glm-4.7':
        return this._callGLM(config, prompt);
      case 'minimax':
        return this._callMinimax(config, prompt);
      case 'iflow':
      case 'qwen':
      case 'kiro':
        return this._callFreeProvider(config, prompt);
      default:
        throw new Error(`Unsupported provider: ${provider}`);
    }
  }

  // Claude API
  async _callClaude(config, prompt) {
    const apiKey = process.env.ANTHROPIC_API_KEY || process.env.CLAUDE_API_KEY;
    if (!apiKey) throw new Error('Claude API key not set');

    const response = await this._httpRequest({
      hostname: 'api.anthropic.com',
      path: '/v1/messages',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
        'anthropic-dangerous-direct-sse': 'enable'
      },
      body: {
        model: 'claude-opus-4-5',
        max_tokens: 4096,
        messages: [{ role: 'user', content: prompt }]
      }
    }, this.config.routing.timeoutMs);

    return {
      provider: 'claude',
      tier: 1,
      response: response.content[0].text,
      tokens: response.usage.output_tokens + response.usage.input_tokens
    };
  }

  // GLM API (OpenAI兼容)
  async _callGLM(config, prompt) {
    const apiKey = process.env.ZHIPU_API_KEY;
    if (!apiKey) throw new Error('GLM API key not set');

    const response = await this._httpRequest({
      hostname: 'open.bigmodel.cn',
      path: '/api/paas/v4/chat/completions',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: {
        model: 'glm-4-0520',
        messages: [{ role: 'user', content: prompt }],
        max_tokens: 4096
      }
    }, this.config.routing.timeoutMs);

    return {
      provider: 'glm-4.7',
      tier: 2,
      response: response.choices[0].message.content,
      tokens: response.usage.total_tokens
    };
  }

  // MiniMax API
  async _callMinimax(config, prompt) {
    const apiKey = process.env.MINIMAX_API_KEY;
    if (!apiKey) throw new Error('MiniMax API key not set');

    const response = await this._httpRequest({
      hostname: 'api.minimax.chat',
      path: '/v1/text/chatcompletion_pro',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: {
        model: 'abab6.5s-chat',
        messages: [{ role: 'user', content: prompt }],
        max_tokens: 4096
      }
    }, this.config.routing.timeoutMs);

    return {
      provider: 'minimax',
      tier: 2,
      response: response.choices[0].message.content,
      tokens: response.usage.total_tokens
    };
  }

  // 免费提供商
  async _callFreeProvider(config, prompt) {
    const apiKey = config.api_key || process.env[`${config.name.toUpperCase()}_API_KEY`];
    if (!apiKey) throw new Error(`${config.name} API key not set`);

    // iFlow / Qwen / Kiro 使用OpenAI兼容接口
    const response = await this._httpRequest({
      hostname: config.base_url || 'api.moonshot.cn',
      path: '/v1/chat/completions',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: {
        model: config.model || 'moonshot-v1-8k',
        messages: [{ role: 'user', content: prompt }],
        max_tokens: 2048
      }
    }, this.config.routing.timeoutMs);

    return {
      provider: config.name,
      tier: 3,
      response: response.choices[0].message.content,
      tokens: response.usage.total_tokens
    };
  }

  // HTTP请求封装
  async _httpRequest(options, timeout = 30000) {
    return new Promise((resolve, reject) => {
      const req = (options.hostname.includes('api.anthropic.com') ? https : http)
        .request(options, (res) => {
          let data = '';
          res.on('data', chunk => data += chunk);
          res.on('end', () => {
            if (res.statusCode >= 400) {
              reject(new Error(`HTTP ${res.statusCode}: ${data}`));
            } else {
              try {
                resolve(JSON.parse(data));
              } catch (e) {
                resolve(data);
              }
            }
          });
        });

      req.on('error', reject);
      req.on('timeout', () => {
        req.destroy();
        reject(new Error('Request timeout'));
      });

      req.setTimeout(timeout);
      req.write(JSON.stringify(options.body));
      req.end();
    });
  }

  // 获取下一个可用提供商
  _getNextProvider(tier) {
    const tierConfig = this.config.tiers[tier];
    if (!tierConfig) return null;

    // 按优先级排序
    const providers = [...tierConfig.providers].sort((a, b) => a.priority - b.priority);

    for (const p of providers) {
      if (this._checkQuota(p.name)) {
        return p.name;
      }
    }

    return providers[0]?.name;
  }

  // 检查配额
  _checkQuota(provider) {
    const tier = this.config.tiers[1].providers.find(p => p.name === provider);
    if (!tier) {
      // 可能是Tier 2/3的提供商
      const tier2 = this.config.tiers[2].providers.find(p => p.name === provider);
      const tier3 = this.config.tiers[3].providers.find(p => p.name === provider);
      const found = tier2 || tier3;
      return found ? found.quota > (state.quotaUsed[provider] || 0) : true;
    }
    return tier.quota > (state.quotaUsed[provider] || 0);
  }

  // 分类错误
  _classifyError(error) {
    if (error.message.includes('quota') || error.message.includes('limit')) {
      return 'quota_exceeded';
    }
    if (error.message.includes('timeout')) {
      return 'timeout';
    }
    if (error.message.includes('429') || error.message.includes('rate')) {
      return 'rate_limit';
    }
    if (error.message.match(/5\d{2}/)) {
      return 'api_error';
    }
    return 'unknown';
  }

  // 是否应该降级
  _shouldFallback(trigger) {
    return ['quota_exceeded', 'rate_limit', 'timeout', 'api_error'].includes(trigger);
  }

  // 获取下一个Tier
  _getNextTier(currentTier) {
    if (currentTier < 3) return currentTier + 1;
    return 4; // 所有Tier耗尽
  }

  // 获取提供商配置
  _getProviderConfig(provider) {
    for (const tier of Object.values(this.config.tiers)) {
      const found = tier.providers.find(p => p.name === provider);
      if (found) return found;
    }
    return null;
  }

  // 记录降级日志
  _logFallback(entry) {
    state.fallbackHistory.push({
      ...entry,
      timestamp: new Date().toISOString()
    });

    // 只保留最近100条
    if (state.fallbackHistory.length > 100) {
      state.fallbackHistory = state.fallbackHistory.slice(-100);
    }

    this.saveState();
    console.log(`[Fallback] ${entry.original_provider} → ${entry.target_provider} (${entry.trigger})`);
  }

  // 获取状态
  getStatus() {
    return {
      currentTier: state.currentTier,
      currentProvider: state.currentProvider,
      quotaUsed: state.quotaUsed,
      fallbackHistory: state.fallbackHistory.slice(-10),
      costSavings: state.costSavings,
      healthStatus: state.healthStatus
    };
  }

  // 切换Tier
  async switchToTier(tier) {
    if (tier < 1 || tier > 3) {
      throw new Error('Invalid tier: ' + tier);
    }
    state.currentTier = tier;
    state.currentProvider = this._getNextProvider(tier);
    this.saveState();
    return { tier, provider: state.currentProvider };
  }

  // 生成ID
  _generateId() {
    return 'req_' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
  }
}

// ============ 导出 ============
module.exports = AIThreeTierFallback;

// CLI模式
if (require.main === module) {
  const fallback = new AIThreeTierFallback();
  const command = process.argv[2];

  switch (command) {
    case 'status':
      console.log(JSON.stringify(fallback.getStatus(), null, 2));
      break;
    case 'switch':
      const tier = parseInt(process.argv[3]) || 1;
      console.log(fallback.switchToTier(tier));
      break;
    case 'route':
      const prompt = process.argv.slice(3).join(' ') || '你好';
      fallback.route({ prompt }).then(console.log).catch(console.error);
      break;
    default:
      console.log(`
AI Three-Tier Fallback Router
Usage:
  rtk ai-three-tier-fallback status     # 查看状态
  rtk ai-three-tier-fallback switch <1-3>  # 切换Tier
  rtk ai-three-tier-fallback route <prompt> # 测试路由
      `);
  }
}