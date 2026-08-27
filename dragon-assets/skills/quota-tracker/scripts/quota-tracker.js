#!/usr/bin/env node
/**
 * Quota Tracker - 核心监控引擎
 * 实时监控AI提供商配额状态，支持多账户轮询
 *
 * 来源: decolua/9router
 * 天龙引擎V8.87升级
 */

const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');

// ============ 配置 ============
const DEFAULT_CONFIG = {
  pollInterval: 30000, // 30秒
  alertThresholds: {
    critical: 10,  // P0: 立即降级
    warning: 20,   // P1: 建议降级
    notice: 50      // P2: 记录日志
  },
  providers: {
    claude: {
      apiKeyEnv: 'ANTHROPIC_API_KEY',
      quota: 100000,
      pollEnabled: true,
      alertThreshold: 10
    },
    glm: {
      apiKeyEnv: 'ZHIPU_API_KEY',
      quota: 500000,
      pollEnabled: true,
      alertThreshold: 20
    },
    minimax: {
      apiKeyEnv: 'MINIMAX_API_KEY',
      quota: 300000,
      pollEnabled: true,
      alertThreshold: 20
    },
    iflow: {
      apiKeyEnv: 'IFLOW_API_KEY',
      quota: 10000,
      pollEnabled: true,
      alertThreshold: 50
    },
    qwen: {
      apiKeyEnv: 'QWEN_API_KEY',
      quota: 5000,
      pollEnabled: true,
      alertThreshold: 50
    },
    kiro: {
      apiKeyEnv: 'KIRO_API_KEY',
      quota: 3000,
      pollEnabled: true,
      alertThreshold: 50
    }
  }
};

// ============ 状态 ============
let state = {
  providers: {},
  totalCostToday: 0,
  totalCostMonth: 0,
  lastCheck: null,
  costHistory: []
};

// ============ 核心类 ============
class QuotaTracker {
  constructor(configPath = null) {
    this.config = this.loadConfig(configPath);
    this.loadState();
  }

  loadConfig(configPath) {
    const config = { ...DEFAULT_CONFIG };

    // 尝试加载用户配置
    if (configPath && fs.existsSync(configPath)) {
      try {
        const userConfig = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
        Object.assign(config, userConfig);
      } catch (e) {
        console.error('Config parse error:', e.message);
      }
    }

    // 尝试加载YAML配置
    const yamlPath = path.join(
      process.env.HOME || process.env.USERPROFILE,
      '.claude/skills/quota-tracker/config.yaml'
    );

    if (fs.existsSync(yamlPath)) {
      try {
        const yaml = require('js-yaml');
        const yamlConfig = yaml.load(fs.readFileSync(yamlPath, 'utf-8'));
        if (yamlConfig.monitoring) {
          config.pollInterval = yamlConfig.monitoring.poll_interval || config.pollInterval;
          config.alertThresholds = {
            critical: yamlConfig.monitoring.alert_thresholds?.critical || 10,
            warning: yamlConfig.monitoring.alert_thresholds?.warning || 20,
            notice: yamlConfig.monitoring.alert_thresholds?.notice || 50
          };
        }
        if (yamlConfig.providers) {
          config.providers = { ...config.providers, ...yamlConfig.providers };
        }
      } catch (e) {
        // YAML解析失败，使用默认配置
      }
    }

    return config;
  }

  loadState() {
    try {
      const stateFile = this.getStateFile();
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
      const stateFile = this.getStateFile();
      const dir = path.dirname(stateFile);
      if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
      fs.writeFileSync(stateFile, JSON.stringify(state, null, 2));
    } catch (e) {
      console.error('State save error:', e.message);
    }
  }

  getStateFile() {
    return path.join(
      process.env.HOME || process.env.USERPROFILE,
      '.claude/skills/quota-tracker/state.json'
    );
  }

  // 获取配额状态
  async getStatus() {
    const results = {};

    for (const [name, config] of Object.entries(this.config.providers)) {
      if (!config.pollEnabled) continue;

      try {
        const quota = await this.pollProvider(name, config);
        results[name] = quota;
        state.providers[name] = quota;
      } catch (e) {
        results[name] = {
          status: 'error',
          error: e.message,
          lastCheck: new Date().toISOString()
        };
      }
    }

    state.lastCheck = new Date().toISOString();
    this.saveState();

    return {
      providers: results,
      total_cost_today: state.totalCostToday,
      total_cost_month: state.totalCostMonth
    };
  }

  // 轮询单个提供商
  async pollProvider(name, config) {
    const apiKey = process.env[config.apiKeyEnv];
    if (!apiKey) {
      return { status: 'disabled', reason: 'API key not set' };
    }

    // 根据提供商类型调用不同的API
    switch (name) {
      case 'claude':
        return await this.pollClaude(apiKey, config);
      case 'glm':
        return await this.pollGLM(apiKey, config);
      case 'minimax':
        return await this.pollMinimax(apiKey, config);
      default:
        return await this.pollOpenAICompatible(name, apiKey, config);
    }
  }

  // Claude配额查询
  async pollClaude(apiKey, config) {
    try {
      const response = await this.httpRequest({
        hostname: 'api.anthropic.com',
        path: '/v1/organizations',
        method: 'GET',
        headers: {
          'x-api-key': apiKey,
          'anthropic-version': '2023-06-01'
        }
      });

      // Claude API不直接返回配额，需要估算
      // 使用usage记录来估算
      const usage = response.usage || {};
      const used = usage.total_usage || 0;

      return {
        quota_total: config.quota,
        quota_used: used,
        quota_remaining: config.quota - used,
        usage_percent: Math.round((used / config.quota) * 100),
        status: this.getStatus(used / config.quota),
        lastCheck: new Date().toISOString()
      };
    } catch (e) {
      // 尝试从错误消息中提取配额信息
      if (e.message.includes('quota') || e.message.includes('limit')) {
        return {
          quota_total: config.quota,
          quota_used: config.quota,
          quota_remaining: 0,
          usage_percent: 100,
          status: 'exhausted',
          error: e.message,
          lastCheck: new Date().toISOString()
        };
      }
      throw e;
    }
  }

  // GLM配额查询
  async pollGLM(apiKey, config) {
    try {
      // GLM API查询余额
      const response = await this.httpRequest({
        hostname: 'open.bigmodel.cn',
        path: '/api/paas/v4/quota',
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${apiKey}`
        }
      });

      const used = response.used || 0;
      const total = response.total || config.quota;

      return {
        quota_total: total,
        quota_used: used,
        quota_remaining: total - used,
        usage_percent: Math.round((used / total) * 100),
        status: this.getStatus(used / total),
        daily_cost: response.daily_cost || 0,
        lastCheck: new Date().toISOString()
      };
    } catch (e) {
      // 尝试估算
      return {
        quota_total: config.quota,
        quota_used: state.providers.glm?.quota_used || 0,
        quota_remaining: config.quota - (state.providers.glm?.quota_used || 0),
        usage_percent: Math.round(((state.providers.glm?.quota_used || 0) / config.quota) * 100),
        status: 'unknown',
        error: e.message,
        lastCheck: new Date().toISOString()
      };
    }
  }

  // MiniMax配额查询
  async pollMinimax(apiKey, config) {
    try {
      const response = await this.httpRequest({
        hostname: 'api.minimax.chat',
        path: '/v1/balance',
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${apiKey}`
        }
      });

      const used = response.total || config.quota;
      const remaining = response.balance || 0;

      return {
        quota_total: used,
        quota_used: used - remaining,
        quota_remaining: remaining,
        usage_percent: Math.round(((used - remaining) / used) * 100),
        status: this.getStatus((used - remaining) / used),
        lastCheck: new Date().toISOString()
      };
    } catch (e) {
      return {
        quota_total: config.quota,
        quota_used: state.providers.minimax?.quota_used || 0,
        quota_remaining: config.quota - (state.providers.minimax?.quota_used || 0),
        usage_percent: Math.round(((state.providers.minimax?.quota_used || 0) / config.quota) * 100),
        status: 'unknown',
        error: e.message,
        lastCheck: new Date().toISOString()
      };
    }
  }

  // OpenAI兼容API配额查询
  async pollOpenAICompatible(name, apiKey, config) {
    const baseUrl = this.getProviderBaseUrl(name);
    try {
      const response = await this.httpRequest({
        hostname: baseUrl.hostname,
        path: '/dashboard/billing/credit_grants',
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${apiKey}`
        }
      });

      const total = response.total_granted || config.quota;
      const used = response.total_used || 0;
      const remaining = total - used;

      return {
        quota_total: total,
        quota_used: used,
        quota_remaining: remaining,
        usage_percent: Math.round((used / total) * 100),
        status: this.getStatus(used / total),
        lastCheck: new Date().toISOString()
      };
    } catch (e) {
      // 估算
      return {
        quota_total: config.quota,
        quota_used: state.providers[name]?.quota_used || 0,
        quota_remaining: config.quota - (state.providers[name]?.quota_used || 0),
        usage_percent: Math.round(((state.providers[name]?.quota_used || 0) / config.quota) * 100),
        status: 'unknown',
        lastCheck: new Date().toISOString()
      };
    }
  }

  getProviderBaseUrl(name) {
    const urls = {
      iflow: { hostname: 'api.moonshot.cn', path: '/v1/quota' },
      qwen: { hostname: 'dashscope.aliyuncs.com', path: '/api/v1/quota' },
      kiro: { hostname: 'api.kiro.ai', path: '/v1/quota' }
    };
    return urls[name] || { hostname: 'api.openai.com', path: '/v1/quota' };
  }

  // 获取状态
  getStatus(percent) {
    if (percent >= 0.9) return 'critical';
    if (percent >= 0.8) return 'warning';
    if (percent >= 0.5) return 'notice';
    return 'healthy';
  }

  // 检查是否需要降级
  checkFallback(provider) {
    const quota = state.providers[provider];
    if (!quota) return { fallback: false };

    const config = this.config.providers[provider];
    const percent = quota.usage_percent;

    if (percent >= this.config.alertThresholds.critical) {
      const targetTier = this.getFallbackTarget(provider);
      return {
        fallback: true,
        currentTier: this.getProviderTier(provider),
        targetTier: this.getProviderTier(targetTier),
        targetProvider: targetTier,
        reason: 'quota_exceeded',
        severity: 'critical',
        quota: quota
      };
    }

    if (percent >= this.config.alertThresholds.warning) {
      return {
        fallback: false,
        reason: 'quota_warning',
        severity: 'warning',
        quota: quota
      };
    }

    return { fallback: false, severity: 'healthy' };
  }

  getProviderTier(provider) {
    const tiers = {
      claude: 1, codex: 1,
      'glm-4.7': 2, minimax: 2, 'kimi-k2': 2,
      iflow: 3, qwen: 3, kiro: 3
    };
    return tiers[provider] || 1;
  }

  getFallbackTarget(provider) {
    const tier = this.getProviderTier(provider);
    const nextProviders = {
      1: ['glm-4.7', 'minimax', 'kimi-k2'],
      2: ['iflow', 'qwen', 'kiro']
    };
    return nextProviders[tier]?.[0] || provider;
  }

  // 多账户轮询
  async pollMultiple(providers) {
    const results = [];

    for (const provider of providers) {
      const config = this.config.providers[provider];
      if (!config) continue;

      try {
        const quota = await this.pollProvider(provider, config);
        results.push({
          provider,
          available: quota.status !== 'exhausted' && quota.status !== 'error',
          quota
        });
      } catch (e) {
        results.push({
          provider,
          available: false,
          error: e.message
        });
      }
    }

    // 按可用性排序
    return results.sort((a, b) => (b.available ? 1 : 0) - (a.available ? 1 : 0));
  }

  // HTTP请求封装
  httpRequest(options, timeout = 10000) {
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
      req.end();
    });
  }
}

module.exports = QuotaTracker;

// CLI模式
if (require.main === module) {
  const tracker = new QuotaTracker();
  const command = process.argv[2];

  switch (command) {
    case 'status':
      tracker.getStatus().then(status => {
        console.log(JSON.stringify(status, null, 2));
      }).catch(console.error);
      break;
    case 'check':
      const provider = process.argv[3] || 'claude';
      console.log(JSON.stringify(tracker.checkFallback(provider), null, 2));
      break;
    case 'poll':
      const providers = process.argv.slice(3) || ['claude', 'glm', 'minimax'];
      tracker.pollMultiple(providers).then(console.log).catch(console.error);
      break;
    default:
      console.log(`
Quota Tracker - 核心监控引擎

Usage:
  node quota-tracker.js status          # 查看配额状态
  node quota-tracker.js check [provider] # 检查是否需要降级
  node quota-tracker.js poll [providers] # 轮询多个提供商
      `);
  }
}
