#!/usr/bin/env node
/**
 * Alert Dispatcher - 告警分发引擎
 * 多通道告警路由，支持去重、聚合、限流
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
  channels: {
    console: { enabled: true },
    webhook: { enabled: false, url: '', method: 'POST' },
    email: { enabled: false, smtp: {}, recipients: [] },
    file: { enabled: true, path: '~/.claude/skills/quota-tracker/alerts.jsonl' }
  },
  dedup: { enabled: true, ttl: 300000 }, // 5分钟去重窗口
  aggregation: { enabled: true, window: 60000, maxCount: 10 }
};

// ============ 状态 ============
let state = {
  recentAlerts: [],
  aggregatedAlerts: [],
  dispatchStats: { success: 0, failed: 0, dedup: 0 }
};

// ============ 主类 ============
class AlertDispatcher {
  constructor(config = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.loadState();
  }

  loadState() {
    try {
      const stateFile = this.getStateFile();
      if (fs.existsSync(stateFile)) {
        const data = JSON.parse(fs.readFileSync(stateFile, 'utf-8'));
        state = { ...state, ...data };
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
      '.claude/skills/quota-tracker/alert-state.json'
    );
  }

  // 标准化告警格式
  normalizeAlert(alert) {
    return {
      id: alert.id || `${alert.provider}_${alert.level}_${Date.now()}`,
      timestamp: alert.timestamp || new Date().toISOString(),
      provider: alert.provider?.toLowerCase(),
      level: alert.level || 'notice',
      message: alert.message || '',
      quota: {
        usage_percent: alert.quota?.usage_percent || 0,
        quota_remaining: alert.quota?.quota_remaining || 0,
        quota_total: alert.quota?.quota_total || 0
      },
      action: alert.action || 'notify',
      target_provider: alert.target_provider || null,
      metadata: alert.metadata || {}
    };
  }

  // 去重检查
  isDuplicate(alert) {
    if (!this.config.dedup.enabled) return false;

    // 清理过期告警
    const cutoff = Date.now() - this.config.dedup.ttl;
    state.recentAlerts = state.recentAlerts.filter(a => new Date(a.timestamp).getTime() > cutoff);

    // 检查是否存在相同告警
    const exists = state.recentAlerts.find(a =>
      a.provider === alert.provider &&
      a.level === alert.level
    );

    return !!exists;
  }

  // 记录告警（用于去重）
  recordAlert(alert) {
    state.recentAlerts.push({
      ...alert,
      timestamp: alert.timestamp || new Date().toISOString()
    });
    this.saveState();
  }

  // 聚合告警
  async aggregate(alert) {
    if (!this.config.aggregation.enabled) return [alert];

    const now = Date.now();
    const window = this.config.aggregation.window;
    const maxCount = this.config.aggregation.maxCount;

    // 查找可聚合的窗口
    const windowStart = now - window;
    const existing = state.aggregatedAlerts.find(a =>
      new Date(a.timestamp).getTime() > windowStart &&
      a.provider === alert.provider
    );

    if (existing) {
      existing.alerts.push(alert);
      existing.count++;
      existing.latest = alert.timestamp;
      existing.highestLevel = this.getSeverity(existing.level) > this.getSeverity(alert.level)
        ? existing.level : alert.level;
      return null; // 已聚合，不单独发送
    }

    // 创建新聚合窗口
    const aggregated = {
      id: `agg_${Date.now()}`,
      timestamp: alert.timestamp,
      provider: alert.provider,
      level: alert.level,
      alerts: [alert],
      count: 1,
      latest: alert.timestamp,
      highestLevel: alert.level,
      aggregated: true
    };

    state.aggregatedAlerts.push(aggregated);
    this.saveState();

    // 清理过期聚合
    const aggCutoff = now - window * 2;
    state.aggregatedAlerts = state.aggregatedAlerts.filter(a =>
      new Date(a.timestamp).getTime() > aggCutoff
    );

    return [aggregated];
  }

  // 获取告警级别数值
  getSeverity(level) {
    const levels = { critical: 3, warning: 2, notice: 1, info: 0 };
    return levels[level] || 0;
  }

  // 分发到所有通道
  async dispatch(alert) {
    const normalized = this.normalizeAlert(alert);

    // 去重检查
    if (this.isDuplicate(normalized)) {
      state.dispatchStats.dedup++;
      return { dispatched: false, reason: 'duplicate', alert: normalized };
    }

    // 记录告警
    this.recordAlert(normalized);

    // 聚合
    const alerts = await this.aggregate(normalized);
    if (!alerts) {
      return { dispatched: false, reason: 'aggregated', alert: normalized };
    }

    // 分发到各通道
    const results = [];
    for (const [channel, config] of Object.entries(this.config.channels)) {
      if (!config.enabled) continue;
      try {
        const result = await this.dispatchToChannel(channel, config, alerts);
        results.push({ channel, success: true, result });
      } catch (e) {
        results.push({ channel, success: false, error: e.message });
        state.dispatchStats.failed++;
      }
    }

    state.dispatchStats.success++;
    this.saveState();

    return { dispatched: true, alert: normalized, alerts, results };
  }

  // 分发到指定通道
  async dispatchToChannel(channel, config, alerts) {
    switch (channel) {
      case 'console':
        return this.dispatchToConsole(alerts);
      case 'webhook':
        return this.dispatchToWebhook(config, alerts);
      case 'email':
        return this.dispatchToEmail(config, alerts);
      case 'file':
        return this.dispatchToFile(config, alerts);
      default:
        throw new Error(`Unknown channel: ${channel}`);
    }
  }

  // 控制台输出
  dispatchToConsole(alerts) {
    for (const alert of alerts) {
      const emoji = this.getEmoji(alert.level);
      const provider = (alert.provider || '').toUpperCase();

      console.log(`\n${emoji} [${alert.level.toUpperCase()}] ${provider} Alert`);
      console.log(`   Time: ${alert.timestamp}`);
      console.log(`   Usage: ${alert.quota?.usage_percent || 0}%`);

      if (alert.target_provider) {
        console.log(`   Action: Fallback to ${alert.target_provider}`);
      }
    }
  }

  // Webhook通知
  async dispatchToWebhook(config, alerts) {
    if (!config.url) return;

    const payload = {
      alerts: alerts.map(a => ({
        id: a.id,
        timestamp: a.timestamp,
        provider: a.provider,
        level: a.level,
        message: a.message,
        quota: a.quota,
        action: a.action,
        target_provider: a.target_provider
      })),
      count: alerts.length,
      highestLevel: alerts.reduce((max, a) =>
        this.getSeverity(a.level) > this.getSeverity(max) ? a.level : max, 'info')
    };

    return new Promise((resolve, reject) => {
      const url = new URL(config.url);
      const options = {
        hostname: url.hostname,
        path: url.pathname,
        method: config.method || 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      };

      const req = (url.protocol === 'https:' ? https : http).request(options, res => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve({ statusCode: res.statusCode, body: data });
          } else {
            reject(new Error(`Webhook failed: ${res.statusCode}`));
          }
        });
      });

      req.on('error', reject);
      req.write(JSON.stringify(payload));
      req.end();
    });
  }

  // 邮件通知
  async dispatchToEmail(config, alerts) {
    // 需要 nodemailer 可用
    try {
      const nodemailer = require('nodemailer');
      const transporter = nodemailer.createTransport(config.smtp);

      const subject = `[${alerts[0].level.toUpperCase()}] Quota Alert: ${alerts[0].provider}`;
      const html = alerts.map(a => `
        <h2>${this.getEmoji(a.level)} ${a.provider} - ${a.level}</h2>
        <p>Usage: ${a.quota?.usage_percent || 0}%</p>
        <p>Remaining: ${a.quota?.quota_remaining || 0}</p>
        ${a.target_provider ? `<p>Fallback to: ${a.target_provider}</p>` : ''}
        <hr/>
      `).join('');

      const info = await transporter.sendMail({
        from: config.from || 'quota-monitor@localhost',
        to: config.recipients.join(', '),
        subject,
        html
      });

      return { messageId: info.messageId };
    } catch (e) {
      throw new Error(`Email send failed: ${e.message}`);
    }
  }

  // 文件记录
  dispatchToFile(config, alerts) {
    const filePath = path.resolve(config.path.replace('~', process.env.HOME || process.env.USERPROFILE));
    const dir = path.dirname(filePath);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });

    const lines = alerts.map(a => JSON.stringify(a)).join('\n') + '\n';
    fs.appendFileSync(filePath, lines);

    return { path: filePath, count: alerts.length };
  }

  // 获取表情
  getEmoji(level) {
    const emojis = { critical: '🔴', warning: '🟠', notice: '🟡', info: '🔵' };
    return emojis[level] || '⚪';
  }

  // 统计信息
  getStats() {
    return {
      ...state.dispatchStats,
      recentAlertsCount: state.recentAlerts.length,
      aggregatedCount: state.aggregatedAlerts.length
    };
  }

  // 历史告警查询
  getHistory(hours = 24, provider = null) {
    const cutoff = Date.now() - hours * 60 * 60 * 1000;
    return state.recentAlerts.filter(a => {
      const matchTime = new Date(a.timestamp).getTime() > cutoff;
      const matchProvider = !provider || a.provider === provider.toLowerCase();
      return matchTime && matchProvider;
    });
  }

  // 清除历史
  clearHistory() {
    state.recentAlerts = [];
    state.aggregatedAlerts = [];
    this.saveState();
    return { cleared: true };
  }
}

// ============ 导出 ============
module.exports = AlertDispatcher;

// ============ CLI模式 ============
if (require.main === module) {
  const dispatcher = new AlertDispatcher();

  const command = process.argv[2];

  switch (command) {
    case 'dispatch':
      const alert = JSON.parse(process.argv[3] || '{}');
      dispatcher.dispatch(alert).then(result => {
        console.log(JSON.stringify(result, null, 2));
      }).catch(console.error);
      break;

    case 'stats':
      console.log(JSON.stringify(dispatcher.getStats(), null, 2));
      break;

    case 'history':
      const hours = parseInt(process.argv[3]) || 24;
      const provider = process.argv[4] || null;
      console.log(JSON.stringify(dispatcher.getHistory(hours, provider), null, 2));
      break;

    case 'clear':
      console.log(JSON.stringify(dispatcher.clearHistory(), null, 2));
      break;

    default:
      console.log(`
Alert Dispatcher - 告警分发引擎

用法:
  node alert-dispatcher.js dispatch <alert_json>  # 分发告警
  node alert-dispatcher.js stats               # 查看统计
  node alert-dispatcher.js history [hours] [provider]  # 查看历史
  node alert-dispatcher.js clear               # 清除历史

示例:
  node alert-dispatcher.js dispatch '{"provider":"claude","level":"warning","quota":{"usage_percent":85}}'
      `);
  }
}
