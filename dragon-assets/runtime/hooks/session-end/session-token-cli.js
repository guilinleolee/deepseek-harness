#!/usr/bin/env node
/**
 * 天龙引擎 V7.5 - 会话和 Token 管理命令
 * 支持: session-status, session-list, token-stats, token-cost
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

const STATE_PATH = path.join(os.homedir(), '.claude', '.session-state.json');
const TOKEN_PATH = path.join(os.homedir(), '.claude', '.token-usage.json');

// 颜色输出
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
  red: '\x1b[31m',
  bold: '\x1b[1m',
};

function readSessionState() {
  try {
    if (fs.existsSync(STATE_PATH)) {
      return JSON.parse(fs.readFileSync(STATE_PATH, 'utf-8'));
    }
  } catch (e) {
    // ignore
  }
  return { currentSessionId: null, sessions: {} };
}

function readTokenUsage() {
  try {
    if (fs.existsSync(TOKEN_PATH)) {
      return JSON.parse(fs.readFileSync(TOKEN_PATH, 'utf-8'));
    }
  } catch (e) {
    // ignore
  }
  return { records: [], stats: { totalInputTokens: 0, totalOutputTokens: 0, totalCostUsd: 0 } };
}

function formatTimestamp(ts) {
  return new Date(ts).toLocaleString('zh-CN');
}

// 会话状态
function sessionStatus() {
  const state = readSessionState();
  const currentId = state.currentSessionId;

  if (!currentId || !state.sessions[currentId]) {
    console.log(`${colors.yellow}⚠️ 无活跃会话${colors.reset}`);
    return;
  }

  const session = state.sessions[currentId];
  console.log(`\n${colors.bold}📋 当前会话${colors.reset}`);
  console.log('='.repeat(50));
  console.log(`${colors.cyan}ID:${colors.reset}    ${session.id}`);
  console.log(`${colors.cyan}标题:${colors.reset}  ${session.title || '无标题'}`);
  console.log(`${colors.cyan}状态:${colors.reset}  ${session.status}`);
  console.log(`${colors.cyan}创建:${colors.reset}  ${formatTimestamp(session.createdAt)}`);
  console.log(`${colors.cyan}活动:${colors.reset}  ${formatTimestamp(session.lastActiveAt)}`);
  console.log(`${colors.cyan}消息:${colors.reset}  ${session.messageCount || 0} 条`);

  if (session.metadata?.projectPath) {
    console.log(`${colors.cyan}项目:${colors.reset}  ${session.metadata.projectPath}`);
  }
  console.log();
}

// 会话列表
function sessionList() {
  const state = readSessionState();
  const sessions = Object.values(state.sessions).sort((a, b) => b.lastActiveAt - a.lastActiveAt);

  console.log(`\n${colors.bold}📋 会话列表${colors.reset}`);
  console.log('='.repeat(60));

  if (sessions.length === 0) {
    console.log(`${colors.yellow}暂无会话记录${colors.reset}`);
    return;
  }

  for (let i = 0; i < Math.min(sessions.length, 10); i++) {
    const s = sessions[i];
    const isCurrent = s.id === state.currentSessionId;
    const statusEmoji = s.status === 'active' ? '🟢' : s.status === 'archived' ? '📦' : '🔴';
    const currentMark = isCurrent ? `${colors.green}[当前]${colors.reset} ` : '';

    console.log(`${statusEmoji} ${currentMark}${colors.cyan}[${s.id.slice(0, 8)}]${colors.reset} ${(s.title || '无标题').slice(0, 30)} - ${formatTimestamp(s.lastActiveAt)}`);
  }

  if (sessions.length > 10) {
    console.log(`\n... 还有 ${sessions.length - 10} 个会话`);
  }
  console.log();
}

// Token 统计
function tokenStats() {
  const tokenData = readTokenUsage();
  const stats = tokenData.stats;

  console.log(`\n${colors.bold}📊 Token 使用统计${colors.reset}`);
  console.log('='.repeat(40));
  console.log(`${colors.cyan}总输入 Token:${colors.reset}  ${stats.totalInputTokens.toLocaleString()}`);
  console.log(`${colors.cyan}总输出 Token:${colors.reset}  ${stats.totalOutputTokens.toLocaleString()}`);
  console.log(`${colors.cyan}总 Token:${colors.reset}      ${(stats.totalInputTokens + stats.totalOutputTokens).toLocaleString()}`);
  console.log(`${colors.cyan}总成本:${colors.reset}        ${colors.green}$${stats.totalCostUsd.toFixed(4)}${colors.reset}`);
  console.log('-'.repeat(40));
  console.log(`${colors.cyan}记录数:${colors.reset}        ${tokenData.records.length}`);
  console.log();
}

// Token 成本
function tokenCost() {
  const tokenData = readTokenUsage();
  const stats = tokenData.stats;
  const totalTokens = stats.totalInputTokens + stats.totalOutputTokens;

  console.log(`\n${colors.bold}💰 成本报告${colors.reset}`);
  console.log('='.repeat(40));
  console.log(`${colors.cyan}总成本:${colors.reset}        ${colors.green}$${stats.totalCostUsd.toFixed(4)}${colors.reset}`);
  console.log(`${colors.cyan}总 Token:${colors.reset}      ${totalTokens.toLocaleString()}`);

  if (totalTokens > 0) {
    const avgCost = (stats.totalCostUsd / (totalTokens / 1000)).toFixed(4);
    console.log(`${colors.cyan}平均成本/1K:${colors.reset}   $${avgCost}`);
  }

  // 按模型分组统计
  const byModel = {};
  for (const record of tokenData.records) {
    if (!byModel[record.model]) {
      byModel[record.model] = { input: 0, output: 0, cost: 0 };
    }
    byModel[record.model].input += record.inputTokens;
    byModel[record.model].output += record.outputTokens;
    byModel[record.model].cost += record.costUsd;
  }

  if (Object.keys(byModel).length > 0) {
    console.log('\n按模型分组:');
    console.log('-'.repeat(40));
    for (const [model, data] of Object.entries(byModel)) {
      console.log(`${colors.cyan}${model}:${colors.reset}`);
      console.log(`  输入: ${data.input.toLocaleString()} | 输出: ${data.output.toLocaleString()} | 成本: $${data.cost.toFixed(4)}`);
    }
  }
  console.log();
}

// Token 每日统计
function tokenDaily() {
  const tokenData = readTokenUsage();
  const records = tokenData.records;

  // 按日期分组
  const byDate = {};
  for (const record of records) {
    const date = new Date(record.timestamp).toISOString().split('T')[0];
    if (!byDate[date]) {
      byDate[date] = { input: 0, output: 0, cost: 0 };
    }
    byDate[date].input += record.inputTokens;
    byDate[date].output += record.outputTokens;
    byDate[date].cost += record.costUsd;
  }

  const dates = Object.keys(byDate).sort().reverse().slice(0, 7);

  console.log(`\n${colors.bold}📅 每日 Token 使用${colors.reset}`);
  console.log('='.repeat(60));
  console.log('日期          | 输入 Token  | 输出 Token  | 成本 (USD)');
  console.log('-'.repeat(60));

  for (const date of dates) {
    const data = byDate[date];
    console.log(`${date} | ${data.input.toString().padStart(11)} | ${data.output.toString().padStart(11)} | $${data.cost.toFixed(4)}`);
  }
  console.log();
}

// 主函数
function main() {
  const command = process.argv[2] || 'status';

  switch (command) {
    case 'status':
    case 'session-status':
      sessionStatus();
      break;
    case 'list':
    case 'session-list':
      sessionList();
      break;
    case 'stats':
    case 'token-stats':
      tokenStats();
      break;
    case 'cost':
    case 'token-cost':
      tokenCost();
      break;
    case 'daily':
    case 'token-daily':
      tokenDaily();
      break;
    default:
      console.log(`用法: node session-token-cli.js <command>`);
      console.log('命令:');
      console.log('  session-status  查看当前会话状态');
      console.log('  session-list    列出所有会话');
      console.log('  token-stats     查看 Token 统计');
      console.log('  token-cost      查看成本报告');
      console.log('  token-daily     查看每日统计');
  }
}

main();