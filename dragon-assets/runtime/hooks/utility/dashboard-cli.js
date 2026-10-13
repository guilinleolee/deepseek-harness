#!/usr/bin/env node
/**
 * 天龙引擎 V7.5 - Dashboard CLI
 * 统一仪表板命令行工具
 *
 * 支持：
 * - 系统状态总览
 * - MCP 配置管理
 * - 任务队列可视化
 * - 实时监控
 */

const path = require('path');

// 导入模块
const sessionTokenCli = require('../session-end/session-token-cli.js');
const interactionMode = require('./interaction-mode.js');
const modelSwitcher = require('./model-switcher.js');
const mcpManager = require('./mcp-config-manager.js');
const taskVisualizer = require('./task-queue-visualizer.js');

// 颜色输出
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
  red: '\x1b[31m',
  magenta: '\x1b[35m',
  bold: '\x1b[1m',
  dim: '\x1b[2m'
};

/**
 * 打印帮助信息
 */
function printHelp() {
  console.log(`
${colors.bold}🐉 天龙引擎 V7.5 - Dashboard CLI${colors.reset}

用法: node dashboard-cli.js <command> [args]

${colors.cyan}系统命令${colors.reset}
  status              显示系统状态总览
  health              系统健康检查
  report              生成完整报告

${colors.cyan}会话命令${colors.reset}
  session             查看当前会话状态
  session-list        列出所有会话
  token-stats         Token 使用统计
  token-cost          成本报告

${colors.cyan}交互命令${colors.reset}
  mode                查看当前交互模式
  mode <name>         切换交互模式
  model               查看当前模型
  model <name>        切换模型
  cost                模型成本对比

${colors.cyan}MCP 命令${colors.reset}
  mcp                 列出 MCP 服务器
  mcp-add             添加 MCP 服务器
  mcp-remove <name>   删除 MCP 服务器
  mcp-enable <name>   启用服务器
  mcp-disable <name>  禁用服务器
  mcp-templates       列出可用模板

${colors.cyan}任务命令${colors.reset}
  tasks               显示任务队列
  tasks-visual        可视化展示
  tasks-add <title>   添加任务
  tasks-clear         清理已完成任务

${colors.cyan}监控命令${colors.reset}
  monitor             启动实时监控 (Ctrl+C 退出)
  watch               监控模式别名

示例:
  node dashboard-cli.js status
  node dashboard-cli.js mode code
  node dashboard-cli.js mcp
  node dashboard-cli.js tasks-visual
`);
}

/**
 * 显示系统状态总览
 */
function showStatus() {
  console.log(`\n${colors.bold}🐉 天龙引擎 V7.5 - 系统状态${colors.reset}`);
  console.log('='.repeat(60));

  // 会话状态
  const sessionState = sessionTokenCli.readSessionState ?
    sessionTokenCli.readSessionState() : { currentSessionId: null };
  console.log(`\n${colors.cyan}📋 会话${colors.reset}`);
  console.log(`  当前会话: ${sessionState.currentSessionId || '无'}`);
  console.log(`  会话总数: ${Object.keys(sessionState.sessions || {}).length}`);

  // 交互模式
  const mode = interactionMode.getCurrentMode();
  console.log(`\n${colors.cyan}🎯 交互模式${colors.reset}`);
  console.log(`  当前模式: ${mode.name}`);
  console.log(`  默认 Agent: ${mode.features.defaultAgent}`);
  console.log(`  默认模型: ${mode.features.defaultModel}`);

  // 模型
  const modelInfo = modelSwitcher.getCurrentModel();
  console.log(`\n${colors.cyan}🤖 模型${colors.reset}`);
  console.log(`  当前模型: ${modelInfo.info?.name || modelInfo.model}`);
  console.log(`  定价: $${modelInfo.info?.pricing.input}/$${modelInfo.info?.pricing.output} per 1M tokens`);

  // Token 统计
  const tokenData = sessionTokenCli.readTokenUsage ?
    sessionTokenCli.readTokenUsage() : { stats: {} };
  console.log(`\n${colors.cyan}📊 Token 统计${colors.reset}`);
  console.log(`  总输入: ${(tokenData.stats.totalInputTokens || 0).toLocaleString()}`);
  console.log(`  总输出: ${(tokenData.stats.totalOutputTokens || 0).toLocaleString()}`);
  console.log(`  总成本: $${(tokenData.stats.totalCostUsd || 0).toFixed(4)}`);

  // MCP 服务器
  const servers = mcpManager.listServers();
  const enabledServers = servers.filter(s => s.enabled).length;
  console.log(`\n${colors.cyan}📡 MCP 服务器${colors.reset}`);
  console.log(`  总数: ${servers.length} | 启用: ${enabledServers}`);

  // 任务队列
  const taskStats = taskVisualizer.listTasks().stats;
  console.log(`\n${colors.cyan}📝 任务队列${colors.reset}`);
  console.log(`  总计: ${taskStats.total} | 完成: ${taskStats.completed} | 执行中: ${taskStats.inProgress}`);
  console.log(`  待处理: ${taskStats.pending} | 失败: ${taskStats.failed}`);

  console.log('\n' + '='.repeat(60));
}

/**
 * 显示健康检查
 */
function showHealth() {
  console.log(`\n${colors.bold}🏥 系统健康检查${colors.reset}`);
  console.log('='.repeat(60));

  const checks = [];

  // 检查会话
  const sessionState = sessionTokenCli.readSessionState ?
    sessionTokenCli.readSessionState() : {};
  checks.push({
    name: '会话管理',
    status: sessionState.currentSessionId ? 'healthy' : 'warning',
    message: sessionState.currentSessionId ? '会话活跃' : '无活跃会话'
  });

  // 检查 MCP
  const servers = mcpManager.listServers();
  const hasError = servers.some(s => s.status === 'error');
  checks.push({
    name: 'MCP 服务',
    status: servers.length === 0 ? 'warning' : hasError ? 'error' : 'healthy',
    message: `${servers.length} 个服务器${hasError ? '，存在错误' : ''}`
  });

  // 检查任务队列
  const taskStats = taskVisualizer.listTasks().stats;
  const failRate = taskStats.total > 0 ? taskStats.failed / taskStats.total : 0;
  checks.push({
    name: '任务队列',
    status: failRate > 0.3 ? 'error' : failRate > 0.1 ? 'warning' : 'healthy',
    message: `失败率: ${(failRate * 100).toFixed(1)}%`
  });

  // 显示结果
  for (const check of checks) {
    const icon = check.status === 'healthy' ? '✅' :
                 check.status === 'warning' ? '⚠️' : '❌';
    const color = check.status === 'healthy' ? colors.green :
                  check.status === 'warning' ? colors.yellow : colors.red;
    console.log(`${icon} ${check.name}: ${color}${check.message}${colors.reset}`);
  }

  console.log('');
}

/**
 * 处理 MCP 命令
 */
function handleMcp(args) {
  if (args.length === 0) {
    console.log(mcpManager.formatServerList());
    return;
  }

  const subCmd = args[0];

  switch (subCmd) {
    case 'templates':
      console.log(mcpManager.formatTemplateList());
      break;
    case 'enable':
      if (args[1]) {
        const result = mcpManager.toggleServer(args[1], true);
        console.log(result.success ?
          `${colors.green}✓ 已启用: ${args[1]}${colors.reset}` :
          `${colors.red}✗ ${result.error}${colors.reset}`);
      }
      break;
    case 'disable':
      if (args[1]) {
        const result = mcpManager.toggleServer(args[1], false);
        console.log(result.success ?
          `${colors.green}✓ 已禁用: ${args[1]}${colors.reset}` :
          `${colors.red}✗ ${result.error}${colors.reset}`);
      }
      break;
    case 'remove':
      if (args[1]) {
        const result = mcpManager.removeServer(args[1]);
        console.log(result.success ?
          `${colors.green}✓ 已删除: ${args[1]}${colors.reset}` :
          `${colors.red}✗ ${result.error}${colors.reset}`);
      }
      break;
    default:
      console.log(mcpManager.formatServerList());
  }
}

/**
 * 处理任务命令
 */
function handleTasks(args) {
  if (args.length === 0) {
    console.log(taskVisualizer.formatQueueReport());
    return;
  }

  const subCmd = args[0];

  switch (subCmd) {
    case 'visual':
    case 'viz':
      console.log(taskVisualizer.generateVisualization());
      break;
    case 'add':
      if (args[1]) {
        const task = taskVisualizer.addTask({ title: args.slice(1).join(' ') });
        console.log(`${colors.green}✓ 已添加任务: ${task.id.slice(0, 8)}${colors.reset}`);
      }
      break;
    case 'clear':
      const result = taskVisualizer.clearCompleted();
      console.log(`${colors.green}✓ 已清理 ${result.cleared} 个已完成任务${colors.reset}`);
      break;
    case 'reset':
      taskVisualizer.resetQueue();
      console.log(`${colors.green}✓ 队列已重置${colors.reset}`);
      break;
    default:
      console.log(taskVisualizer.formatQueueReport());
  }
}

/**
 * 启动实时监控
 */
function startMonitor() {
  console.log(`\n${colors.bold}📊 实时监控${colors.reset} (按 Ctrl+C 退出)`);
  console.log('='.repeat(60));

  let count = 0;

  const interval = setInterval(() => {
    // 清屏
    process.stdout.write('\x1b[2J\x1b[H');

    console.log(`\n${colors.bold}📊 实时监控 - 更新 #${++count}${colors.reset}`);
    console.log('='.repeat(60));
    console.log(`时间: ${new Date().toLocaleString('zh-CN')}`);
    console.log('');

    // 显示任务可视化
    console.log(taskVisualizer.generateVisualization());
    console.log('');

    // 显示 Token 统计
    const tokenData = sessionTokenCli.readTokenUsage ?
      sessionTokenCli.readTokenUsage() : { stats: {} };
    console.log(`${colors.cyan}💰 成本: $${(tokenData.stats.totalCostUsd || 0).toFixed(4)}${colors.reset}`);

  }, 3000);

  // 处理退出
  process.on('SIGINT', () => {
    clearInterval(interval);
    console.log(`\n${colors.green}监控已停止${colors.reset}`);
    process.exit(0);
  });
}

/**
 * 主函数
 */
function main() {
  const command = process.argv[2];
  const args = process.argv.slice(3);

  switch (command) {
    case 'status':
      showStatus();
      break;
    case 'health':
      showHealth();
      break;
    case 'report':
      showStatus();
      showHealth();
      console.log(taskVisualizer.generateVisualization());
      break;

    case 'session':
    case 'session-status':
      sessionTokenCli.main ? sessionTokenCli.main(['status']) :
        console.log('会话状态功能不可用');
      break;
    case 'session-list':
      sessionTokenCli.main ? sessionTokenCli.main(['list']) :
        console.log('会话列表功能不可用');
      break;
    case 'token-stats':
      sessionTokenCli.main ? sessionTokenCli.main(['stats']) :
        console.log('Token 统计功能不可用');
      break;
    case 'token-cost':
      sessionTokenCli.main ? sessionTokenCli.main(['cost']) :
        console.log('成本报告功能不可用');
      break;

    case 'mode':
      if (args.length > 0) {
        const result = interactionMode.switchMode(args[0]);
        if (result.success) {
          console.log(`\n${colors.green}✓ 模式已切换: ${result.currentMode}${colors.reset}`);
        } else {
          console.log(`${colors.red}✗ ${result.error}${colors.reset}`);
        }
      } else {
        console.log(interactionMode.formatModeReport());
      }
      break;

    case 'model':
      if (args.length > 0 && args[0] !== 'list') {
        const result = modelSwitcher.switchModel(args[0]);
        if (result.success) {
          console.log(`\n${colors.green}✓ 模型已切换: ${result.modelInfo?.name}${colors.reset}`);
        } else {
          console.log(`${colors.red}✗ ${result.error}${colors.reset}`);
        }
      } else {
        console.log(modelSwitcher.formatModelReport());
      }
      break;

    case 'cost':
      const input = parseInt(args[0], 10) || 10000;
      const output = parseInt(args[1], 10) || 5000;
      console.log(modelSwitcher.formatCostComparison(input, output));
      break;

    case 'mcp':
    case 'mcp-list':
      handleMcp(args);
      break;
    case 'mcp-templates':
      console.log(mcpManager.formatTemplateList());
      break;
    case 'mcp-enable':
      handleMcp(['enable', args[0]]);
      break;
    case 'mcp-disable':
      handleMcp(['disable', args[0]]);
      break;
    case 'mcp-remove':
      handleMcp(['remove', args[0]]);
      break;

    case 'tasks':
    case 'tasks-list':
      handleTasks(args);
      break;
    case 'tasks-visual':
    case 'tasks-viz':
      console.log(taskVisualizer.generateVisualization());
      break;
    case 'tasks-add':
      handleTasks(['add', ...args]);
      break;
    case 'tasks-clear':
      handleTasks(['clear']);
      break;

    case 'monitor':
    case 'watch':
      startMonitor();
      break;

    case 'help':
    case '--help':
    case '-h':
    default:
      if (command) {
        console.log(`${colors.red}未知命令: ${command}${colors.reset}`);
      }
      printHelp();
  }
}

main();