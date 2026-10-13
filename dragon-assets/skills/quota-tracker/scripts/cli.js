#!/usr/bin/env node
/**
 * Quota Tracker CLI - 命令行工具入口
 * 统一调度 quota-tracker / quota-monitor / alert-dispatcher
 *
 * 来源: decolua/9router
 * 天龙引擎V8.87升级
 */

const path = require('path');
const fs = require('fs');

// ============ 子模块路径 ============
const SCRIPTS_DIR = path.dirname(__filename);
const quotaTracker = require('./quota-tracker');
const quotaMonitor = require('./quota-monitor');
const alertDispatcher = require('./alert-dispatcher');

// ============ CLI帮助信息 ============
const HELP_TEXT = `
Quota Tracker CLI - AI配额实时监控系统

用法:
  rtk quota-tracker <command> [options]

命令:
  # 状态查询
  status                    查看所有提供商配额状态
  status <provider>         查看指定提供商配额状态
  check [provider]          检查是否需要降级

  # 实时监控
  monitor start             启动监控守护进程
  monitor stop              停止监控守护进程
  monitor status            查看监控状态
  monitor check             单次检查

  # 告警管理
  alert dispatch <json>    分发告警
  alert stats              查看告警统计
  alert history [hours]    查看告警历史
  alert clear              清除告警历史

  # 提供商管理
  enable <provider>         启用提供商监控
  disable <provider>        禁用提供商监控
  toggle <provider>         切换提供商状态

  # 报告
  report [hours]           生成汇总报告
  history [provider] [hours] 查看历史记录
  cost [--period day|month] 查看成本统计

示例:
  rtk quota-tracker status
  rtk quota-tracker monitor start
  rtk quota-tracker enable claude
  rtk quota-tracker alert dispatch '{"provider":"claude","level":"warning","quota":{"usage_percent":85}}'
`.trim();

// ============ 颜色输出 ============
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
  bold: '\x1b[1m'
};

function color(str, c) {
  return `${colors[c]}${str}${colors.reset}`;
}

function statusIcon(percent) {
  if (percent >= 90) return color('🔴', 'red');
  if (percent >= 80) return color('🟠', 'yellow');
  if (percent >= 50) return color('🟡', 'yellow');
  return color('🟢', 'green');
}

function printStatus(status) {
  console.log(color('\n┌─────────────────────────────────────────────────┐', 'cyan'));
  console.log(color('│           AI配额状态监控面板                     │', 'cyan'));
  console.log(color('└─────────────────────────────────────────────────┘', 'cyan'));

  for (const [provider, quota] of Object.entries(status.providers || {})) {
    if (quota.status === 'disabled') {
      console.log(`  ${color('○', 'yellow')} ${provider.padEnd(12)} ${color('[未配置API Key]', 'yellow')}`);
      continue;
    }

    if (quota.status === 'error') {
      console.log(`  ${color('✗', 'red')} ${provider.padEnd(12)} ${color(`[错误: ${quota.error || '未知'}]`, 'red')}`);
      continue;
    }

    const pct = quota.usage_percent || 0;
    const icon = statusIcon(pct);
    const bar = renderBar(pct);

    console.log(`\n  ${icon} ${color(provider.toUpperCase().padEnd(12), 'bold')} ${bar} ${pct}%`);
    console.log(`     剩余: ${color(String(quota.quota_remaining || 0).padStart(8), pct >= 80 ? 'red' : 'green'} / ${quota.quota_total || 0}`);
  }

  console.log(color('\n  统计:', 'cyan'));
  console.log(`    今日成本: ¥${(status.total_cost_today || 0).toFixed(2)}`);
  console.log(`    本月成本: ¥${(status.total_cost_month || 0).toFixed(2)}`);
  console.log(color('─'.repeat(50), 'cyan'));
}

function renderBar(percent) {
  const width = 20;
  const filled = Math.round((percent / 100) * width);
  const empty = width - filled;
  const bar = color('█'.repeat(filled), percent >= 90 ? 'red' : percent >= 80 ? 'yellow' : 'green') +
              color('░'.repeat(empty), 'reset');
  return `[${bar}]`;
}

// ============ 监控守护进程管理 ============
let monitorInstance = null;

async function startMonitor(options = {}) {
  if (monitorInstance) {
    console.log(color('⚠️  监控已在运行中', 'yellow'));
    return;
  }

  monitorInstance = new quotaMonitor({
    interval: options.interval || 30000,
    alertCooldown: options.cooldown || 300000,
    alertCallback: (provider, level, data) => {
      const icon = level === 'critical' ? '🔴' : level === 'warning' ? '🟠' : '🟡';
      console.log(`\n${icon} [${level.toUpperCase()}] ${provider.toUpperCase()} 告警`);
      console.log(`   使用率: ${data.usage_percent}%`);
      if (data.target_provider) {
        console.log(`   建议降级: ${data.target_provider}`);
      }
    }
  });

  await monitorInstance.start();
  console.log(color('\n✅ 监控守护进程已启动', 'green'));
  console.log(color('   使用 "rtk quota-tracker monitor stop" 停止\n', 'cyan'));
}

function stopMonitor() {
  if (!monitorInstance) {
    console.log(color('⚠️  监控未在运行', 'yellow'));
    return;
  }
  monitorInstance.stop();
  monitorInstance = null;
  console.log(color('🛑 监控守护进程已停止', 'green'));
}

// ============ 告警分发 ============
async function dispatchAlert(alertJson) {
  let alert;
  try {
    alert = JSON.parse(alertJson);
  } catch (e) {
    console.log(color('❌ JSON解析失败: ' + e.message, 'red'));
    process.exit(1);
  }

  const dispatcher = new alertDispatcher();
  const result = await dispatcher.dispatch(alert);

  if (result.dispatched) {
    console.log(color('✅ 告警已分发', 'green'));
    console.log(`   通道: ${result.results.map(r => r.channel).join(', ')}`);
  } else {
    console.log(color(`⏭️  告警已跳过: ${result.reason}`, 'yellow'));
  }
}

// ============ 主函数 ============
async function main() {
  const args = process.argv.slice(2);
  const command = args[0] || 'help';
  const subCommand = args[1];
  const options = args.slice(2);

  switch (command) {
    case 'status': {
      const tracker = new quotaTracker();
      const status = await tracker.getStatus();
      printStatus(status);
      break;
    }

    case 'check': {
      const tracker = new quotaTracker();
      const provider = args[1] || 'claude';
      const result = tracker.checkFallback(provider);
      console.log('\n降级检查结果:');
      console.log(JSON.stringify(result, null, 2));
      break;
    }

    case 'monitor': {
      switch (subCommand) {
        case 'start': {
          const interval = parseInt(args.find(a => a.startsWith('--interval='))?.split('=')[1]) || 30000;
          const cooldown = parseInt(args.find(a => a.startsWith('--cooldown='))?.split('=')[1]) || 300000;
          await startMonitor({ interval, cooldown });
          break;
        }
        case 'stop':
          stopMonitor();
          break;
        case 'status': {
          if (monitorInstance) {
            console.log(color('🟢 监控运行中', 'green'));
            const report = monitorInstance.getReport();
            console.log(`   提供商: ${report.monitored.join(', ')}`);
            console.log(`   间隔: ${report.interval / 1000}秒`);
          } else {
            console.log(color('⚫ 监控未运行', 'yellow'));
          }
          break;
        }
        case 'check': {
          const monitor = new quotaMonitor();
          await monitor.check();
          console.log(color('✅ 检查完成', 'green'));
          break;
        }
        default:
          console.log(HELP_TEXT);
      }
      break;
    }

    case 'alert': {
      switch (subCommand) {
        case 'dispatch':
          await dispatchAlert(args.slice(2).join(' '));
          break;
        case 'stats': {
          const dispatcher = new alertDispatcher();
          console.log(dispatcher.getStats());
          break;
        }
        case 'history': {
          const dispatcher = new alertDispatcher();
          const hours = parseInt(args[2]) || 24;
          const provider = args[3] || null;
          const history = dispatcher.getHistory(hours, provider);
          console.log(JSON.stringify(history, null, 2));
          break;
        }
        case 'clear': {
          const dispatcher = new alertDispatcher();
          console.log(dispatcher.clearHistory());
          break;
        }
        default:
          console.log(HELP_TEXT);
      }
      break;
    }

    case 'enable': {
      const provider = args[1];
      if (!provider) {
        console.log(color('❌ 请指定提供商', 'red'));
        console.log('   用法: rtk quota-tracker enable <provider>');
        break;
      }
      const monitor = new quotaMonitor();
      monitor.enable(provider);
      break;
    }

    case 'disable': {
      const provider = args[1];
      if (!provider) {
        console.log(color('❌ 请指定提供商', 'red'));
        console.log('   用法: rtk quota-tracker disable <provider>');
        break;
      }
      const monitor = new quotaMonitor();
      monitor.disable(provider);
      break;
    }

    case 'toggle': {
      const provider = args[1];
      if (!provider) {
        console.log(color('❌ 请指定提供商', 'red'));
        console.log('   用法: rtk quota-tracker toggle <provider>');
        break;
      }
      const monitor = new quotaMonitor();
      monitor.toggle(provider);
      break;
    }

    case 'report': {
      const monitor = new quotaMonitor();
      const hours = parseInt(args[1]) || 24;
      const history = monitor.getHistory(null, hours);
      console.log(color(`\n📊 ${hours}小时汇总报告`, 'cyan'));
      console.log(color('─'.repeat(50), 'cyan'));

      const byProvider = {};
      for (const entry of history) {
        if (!byProvider[entry.provider]) {
          byProvider[entry.provider] = { samples: 0, sum: 0, peak: 0 };
        }
        const p = byProvider[entry.provider];
        p.samples++;
        p.sum += entry.usage_percent;
        if (entry.usage_percent > p.peak) p.peak = entry.usage_percent;
      }

      for (const [provider, stats] of Object.entries(byProvider)) {
        const avg = Math.round(stats.sum / stats.samples);
        console.log(`\n  ${provider.toUpperCase()}:`);
        console.log(`    平均: ${avg}%  峰值: ${stats.peak}%  样本: ${stats.samples}`);
      }
      console.log(color('\n' + '─'.repeat(50), 'cyan'));
      break;
    }

    case 'history': {
      const monitor = new quotaMonitor();
      const provider = args[1] || null;
      const hours = parseInt(args[2]) || 24;
      const history = monitor.getHistory(provider, hours);
      console.log(JSON.stringify(history, null, 2));
      break;
    }

    case 'cost': {
      const period = args.find(a => a.startsWith('--period='))?.split('=')[1] || 'day';
      const tracker = new quotaTracker();
      const status = await tracker.getStatus();
      const cost = period === 'month' ? status.total_cost_month : status.total_cost_today;
      console.log(`\n${period === 'month' ? '本月' : '今日'}成本: ¥${(cost || 0).toFixed(2)}`);
      break;
    }

    case 'help':
    case '--help':
    case '-h':
    default:
      console.log(HELP_TEXT);
  }
}

// ============ 运行 ============
main().catch(e => {
  console.error(color(`\n❌ 错误: ${e.message}`, 'red'));
  process.exit(1);
});
