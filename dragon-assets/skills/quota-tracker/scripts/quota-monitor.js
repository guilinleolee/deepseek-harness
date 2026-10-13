#!/usr/bin/env node
/**
 * Quota Monitor - 实时轮询守护进程
 * 持续监控提供商配额，超阈值触发告警
 *
 * 来源: decolua/9router
 * 天龙引擎V8.87升级
 */

const QuotaTracker = require('./quota-tracker');

// ============ 告警等级配置 ============
const ALERT_LEVELS = {
  P0: { level: 'critical', color: '🔴', threshold: 0.9 },
  P1: { level: 'warning', color: '🟠', threshold: 0.8 },
  P2: { level: 'notice', color: '🟡', threshold: 0.5 }
};

// ============ 告警消息模板 ============
const ALERT_TEMPLATES = {
  critical: (provider, quota) => `
${ALERT_LEVELS.P0.color} [P0 紧急] ${provider.toUpperCase()} 配额告急！

⚠️ 使用率: ${quota.usage_percent}%
剩余额度: ${quota.quota_remaining}
总额度: ${quota.quota_total}

🚨 建议立即降级到 ${quota.target_provider || '备选服务商'}
  `,
  warning: (provider, quota) => `
${ALERT_LEVELS.P1.color} [P1 警告] ${provider.toUpperCase()} 配额接近阈值

⚠️ 使用率: ${quota.usage_percent}%
剩余额度: ${quota.quota_remaining}
总额度: ${quota.quota_total}

  `,
  notice: (provider, quota) => `
${ALERT_LEVELS.P2.color} [P2 通知] ${provider.toUpperCase()} 配额使用过半

📊 使用率: ${quota.usage_percent}%
剩余额度: ${quota.quota_remaining}
总额度: ${quota.quota_total}

  `
};

// ============ 主监控类 ============
class QuotaMonitor {
  constructor(options = {}) {
    this.tracker = new QuotaTracker(options.configPath);
    this.interval = options.interval || 30000; // 默认30秒
    this.enabled = new Set(options.enabled || ['claude', 'glm', 'minimax']);
    this.alertCallback = options.alertCallback || this.defaultAlert.bind(this);
    this.statusCallback = options.statusCallback || null;
    this.history = [];
    this.maxHistory = 100;
    this.timer = null;
    this.isRunning = false;
    this.lastAlert = {};
    this.alertCooldown = options.alertCooldown || 300000; // 5分钟冷却
  }

  // 默认告警处理 - 输出到控制台
  defaultAlert(provider, level, data) {
    const template = ALERT_TEMPLATES[level];
    if (!template) return;

    console.log(template(provider, data));

    // 同时输出JSON格式便于程序处理
    const alert = {
      timestamp: new Date().toISOString(),
      provider,
      level,
      quota: data,
      action: level === 'critical' ? 'fallback' : 'notify'
    };
    console.log('\n📋 JSON格式:');
    console.log(JSON.stringify(alert, null, 2));
  }

  // 检查是否在冷却期内
  isInCooldown(provider, level) {
    const key = `${provider}_${level}`;
    const last = this.lastAlert[key];
    if (!last) return false;
    return Date.now() - last < this.alertCooldown;
  }

  // 记录告警时间
  recordAlert(provider, level) {
    const key = `${provider}_${level}`;
    this.lastAlert[key] = Date.now();
  }

  // 执行单次检查
  async check() {
    const status = await this.tracker.getStatus();
    const results = { providers: {}, checked: new Date().toISOString() };

    for (const [provider, quota] of Object.entries(status.providers)) {
      // 跳过未启用的提供商
      if (!this.enabled.has(provider)) continue;

      // 跳过disabled状态
      if (quota.status === 'disabled') continue;

      // 检查是否需要告警
      const shouldAlert = await this.checkAlert(provider, quota);
      if (shouldAlert) {
        this.alertCallback(provider, shouldAlert.level, quota);
        this.recordAlert(provider, shouldAlert.level);
      }

      // 记录历史
      this.addHistory(provider, quota);

      results.providers[provider] = quota;
    }

    // 状态回调
    if (this.statusCallback) {
      this.statusCallback(results);
    }

    return results;
  }

  // 检查告警条件
  async checkAlert(provider, quota) {
    // P0: 90%+ 使用率 -> critical
    if (quota.usage_percent >= 90 && !this.isInCooldown(provider, 'critical')) {
      const fallback = this.tracker.checkFallback(provider);
      if (fallback.fallback) {
        return { level: 'critical', data: { ...quota, target_provider: fallback.targetProvider } };
      }
      return { level: 'critical' };
    }

    // P1: 80%+ 使用率 -> warning
    if (quota.usage_percent >= 80 && !this.isInCooldown(provider, 'warning')) {
      return { level: 'warning' };
    }

    // P2: 50%+ 使用率 -> notice
    if (quota.usage_percent >= 50 && !this.isInCooldown(provider, 'notice')) {
      return { level: 'notice' };
    }

    return null;
  }

  // 添加历史记录
  addHistory(provider, quota) {
    this.history.push({
      provider,
      timestamp: new Date().toISOString(),
      usage_percent: quota.usage_percent,
      quota_remaining: quota.quota_remaining,
      status: quota.status
    });

    // 限制历史长度
    if (this.history.length > this.maxHistory) {
      this.history = this.history.slice(-this.maxHistory);
    }
  }

  // 获取历史数据
  getHistory(provider = null, hours = 24) {
    const cutoff = Date.now() - hours * 60 * 60 * 1000;
    return this.history.filter(h => {
      const matchProvider = !provider || h.provider === provider;
      const matchTime = new Date(h.timestamp).getTime() > cutoff;
      return matchProvider && matchTime;
    });
  }

  // 获取汇总报告
  getReport() {
    const providers = {};
    for (const entry of this.history) {
      if (!providers[entry.provider]) {
        providers[entry.provider] = {
          current: null,
          peak: 0,
          avg: 0,
          samples: 0,
          sum: 0
        };
      }
      const p = providers[entry.provider];
      p.samples++;
      p.sum += entry.usage_percent;
      p.avg = Math.round(p.sum / p.samples);
      if (entry.usage_percent > p.peak) p.peak = entry.usage_percent;
    }

    // 获取最新状态
    const status = this.tracker.state?.providers || {};
    for (const [name, quota] of Object.entries(status)) {
      if (providers[name]) {
        providers[name].current = quota.usage_percent;
      }
    }

    return {
      monitored: Array.from(this.enabled),
      interval: this.interval,
      isRunning: this.isRunning,
      lastCheck: this.tracker.state?.lastCheck,
      providers
    };
  }

  // 启动监控
  async start() {
    if (this.isRunning) {
      console.log('⚠️ 监控已经在运行中');
      return;
    }

    console.log(`🚀 启动配额监控守护进程`);
    console.log(`📊 轮询间隔: ${this.interval / 1000}秒`);
    console.log(`🔔 监控提供商: ${Array.from(this.enabled).join(', ')}`);
    console.log('---');

    this.isRunning = true;

    // 立即执行一次检查
    await this.check();

    // 设置定时器
    this.timer = setInterval(async () => {
      try {
        await this.check();
      } catch (e) {
        console.error('❌ 检查执行失败:', e.message);
      }
    }, this.interval);

    console.log('✅ 监控守护进程已启动');
  }

  // 停止监控
  stop() {
    if (!this.isRunning) {
      console.log('⚠️ 监控未在运行');
      return;
    }

    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }

    this.isRunning = false;
    console.log('🛑 监控守护进程已停止');
  }

  // 重启监控
  async restart() {
    this.stop();
    await new Promise(r => setTimeout(r, 1000));
    await this.start();
  }

  // 启用提供商
  enable(provider) {
    this.enabled.add(provider);
    console.log(`✅ 已启用 ${provider} 监控`);
  }

  // 禁用提供商
  disable(provider) {
    this.enabled.delete(provider);
    console.log(`🚫 已禁用 ${provider} 监控`);
  }

  // 切换提供商状态
  toggle(provider) {
    if (this.enabled.has(provider)) {
      this.disable(provider);
    } else {
      this.enable(provider);
    }
  }

  // 设置轮询间隔
  setInterval(ms) {
    this.interval = ms;
    if (this.isRunning) {
      console.log(`⏱️ 轮询间隔已更新为 ${ms / 1000}秒`);
      // 如果正在运行，需要重启以应用新间隔
      // 不自动重启，让用户决定
    }
  }
}

// ============ 导出 ============
module.exports = QuotaMonitor;

// ============ CLI模式 ============
if (require.main === module) {
  const args = process.argv.slice(2);
  const command = args[0];

  // 默认配置
  const monitor = new QuotaMonitor({
    interval: 30000,
    alertCooldown: 300000,
    alertCallback: (provider, level, data) => {
      // CLI模式使用控制台输出
      console.log(`\n${'='.repeat(50)}`);
      console.log(`📢 告警通知: ${provider}`);
      console.log(`等级: ${level.toUpperCase()}`);
      console.log(`使用率: ${data.usage_percent}%`);
      console.log(`剩余: ${data.quota_remaining}`);
      if (data.target_provider) {
        console.log(`建议降级: ${data.target_provider}`);
      }
      console.log('='.repeat(50));
    }
  });

  switch (command) {
    case 'start':
      monitor.start().catch(console.error);
      break;

    case 'stop':
      monitor.stop();
      break;

    case 'status':
      console.log(JSON.stringify(monitor.getReport(), null, 2));
      break;

    case 'enable':
      if (args[1]) monitor.enable(args[1]);
      else console.log('用法: quota-monitor.js enable <provider>');
      break;

    case 'disable':
      if (args[1]) monitor.disable(args[1]);
      else console.log('用法: quota-monitor.js disable <provider>');
      break;

    case 'toggle':
      if (args[1]) monitor.toggle(args[1]);
      else console.log('用法: quota-monitor.js toggle <provider>');
      break;

    case 'history':
      const provider = args[1] || null;
      const hours = parseInt(args[2]) || 24;
      console.log(JSON.stringify(monitor.getHistory(provider, hours), null, 2));
      break;

    case 'check':
      // 单次检查
      monitor.check().then(r => {
        console.log('检查完成');
        process.exit(0);
      }).catch(e => {
        console.error(e);
        process.exit(1);
      });
      break;

    default:
      console.log(`
Quota Monitor - 实时轮询守护进程

用法:
  node quota-monitor.js start          # 启动监控守护进程
  node quota-monitor.js stop           # 停止监控
  node quota-monitor.js status        # 查看监控状态
  node quota-monitor.js check         # 单次检查
  node quota-monitor.js enable <provider>   # 启用提供商
  node quota-monitor.js disable <provider> # 禁用提供商
  node quota-monitor.js toggle <provider>   # 切换状态
  node quota-monitor.js history [provider] [hours]  # 查看历史

示例:
  node quota-monitor.js start              # 启动监控
  node quota-monitor.js enable claude      # 启用Claude监控
  node quota-monitor.js history glm 48    # 查看GLM 48小时历史
      `);
  }
}
