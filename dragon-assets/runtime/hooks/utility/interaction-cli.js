#!/usr/bin/env node
/**
 * 天龙引擎 V7.5 - 交互优化 CLI
 * 支持: mode, model, cost 命令
 */

const {
  getCurrentMode,
  switchMode,
  listModes,
  formatModeReport,
  recommendMode
} = require('./interaction-mode.js');

const {
  getCurrentModel,
  switchModel,
  getAgentRecommendedModel,
  formatModelReport,
  formatCostComparison,
  formatAgentModelReport,
  AVAILABLE_MODELS
} = require('./model-switcher.js');

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

function printHelp() {
  console.log(`
${colors.bold}天龙引擎 V7.5 - 交互优化 CLI${colors.reset}

用法: node interaction-cli.js <command> [args]

命令:
  ${colors.cyan}mode${colors.reset}                 显示当前交互模式
  mode <name>          切换交互模式 (code|plan|ask)
  mode recommend <prompt>  根据提示词推荐模式

  ${colors.cyan}model${colors.reset}                显示当前模型
  model <name>         切换模型
  model agent <id>     显示 Agent 推荐模型
  model list           列出所有可用模型

  ${colors.cyan}cost${colors.reset}                 显示成本对比
  cost <input> <output>  计算指定 token 数量的成本

示例:
  node interaction-cli.js mode code
  node interaction-cli.js model claude-sonnet-4-6
  node interaction-cli.js model agent 02-architect
  node interaction-cli.js cost 10000 5000
`);
}

function handleMode(args) {
  if (args.length === 0) {
    console.log(formatModeReport());
    return;
  }

  const subCommand = args[0];

  if (subCommand === 'recommend' && args[1]) {
    const prompt = args.slice(1).join(' ');
    const recommended = recommendMode(prompt);
    console.log(`\n${colors.cyan}推荐模式:${colors.reset} ${recommended}`);
    return;
  }

  const validModes = ['code', 'plan', 'ask'];
  if (!validModes.includes(subCommand)) {
    console.log(`${colors.red}错误: 无效模式 "${subCommand}"${colors.reset}`);
    console.log(`有效模式: ${validModes.join(', ')}`);
    return;
  }

  const result = switchMode(subCommand);
  if (result.success) {
    console.log(`\n${colors.green}✓ 模式已切换${colors.reset}`);
    console.log(`  ${colors.cyan}之前:${colors.reset} ${result.previousMode}`);
    console.log(`  ${colors.cyan}当前:${colors.reset} ${result.currentMode}`);
    console.log(`  ${colors.cyan}描述:${colors.reset} ${result.modeInfo.description}`);
    console.log(`  ${colors.cyan}默认 Agent:${colors.reset} ${result.modeInfo.features.defaultAgent}`);
    console.log(`  ${colors.cyan}默认模型:${colors.reset} ${result.modeInfo.features.defaultModel}`);
  } else {
    console.log(`${colors.red}错误: ${result.error}${colors.reset}`);
  }
}

function handleModel(args) {
  if (args.length === 0) {
    console.log(formatModelReport());
    return;
  }

  const subCommand = args[0];

  if (subCommand === 'list') {
    console.log(`\n${colors.bold}可用模型列表${colors.reset}`);
    console.log('='.repeat(60));
    for (const [key, model] of Object.entries(AVAILABLE_MODELS)) {
      console.log(`${colors.cyan}${key}${colors.reset}`);
      console.log(`  名称: ${model.name}`);
      console.log(`  描述: ${model.description}`);
      console.log(`  定价: $${model.pricing.input}/$${model.pricing.output} per 1M tokens`);
      console.log(`  能力: ${model.capabilities.join(', ')}`);
      console.log();
    }
    return;
  }

  if (subCommand === 'agent' && args[1]) {
    const agentId = args[1];
    const rec = getAgentRecommendedModel(agentId);
    console.log(`\n${colors.bold}Agent 模型推荐${colors.reset}`);
    console.log('='.repeat(40));
    console.log(`${colors.cyan}Agent ID:${colors.reset} ${agentId}`);
    console.log(`${colors.cyan}推荐模型:${colors.reset} ${rec.model}`);
    console.log(`${colors.cyan}来源:${colors.reset} ${rec.source}`);
    if (rec.reason) {
      console.log(`${colors.cyan}原因:${colors.reset} ${rec.reason}`);
    }
    if (rec.alternatives) {
      console.log(`${colors.cyan}备选:${colors.reset} ${rec.alternatives.join(', ')}`);
    }
    return;
  }

  if (AVAILABLE_MODELS[subCommand]) {
    const result = switchModel(subCommand);
    if (result.success) {
      console.log(`\n${colors.green}✓ 模型已切换${colors.reset}`);
      console.log(`  ${colors.cyan}之前:${colors.reset} ${result.previousModel}`);
      console.log(`  ${colors.cyan}当前:${colors.reset} ${result.currentModel}`);
      console.log(`  ${colors.cyan}名称:${colors.reset} ${result.modelInfo.name}`);
      console.log(`  ${colors.cyan}描述:${colors.reset} ${result.modelInfo.description}`);
    } else {
      console.log(`${colors.red}错误: ${result.error}${colors.reset}`);
    }
  } else {
    console.log(`${colors.red}错误: 未知模型 "${subCommand}"${colors.reset}`);
    console.log(`运行 "node interaction-cli.js model list" 查看可用模型`);
  }
}

function handleCost(args) {
  const inputTokens = parseInt(args[0], 10) || 10000;
  const outputTokens = parseInt(args[1], 10) || 5000;

  console.log(formatCostComparison(inputTokens, outputTokens));
}

function handleAgentReport() {
  console.log(formatAgentModelReport());
}

// 主函数
function main() {
  const command = process.argv[2];
  const args = process.argv.slice(3);

  switch (command) {
    case 'mode':
      handleMode(args);
      break;
    case 'model':
      handleModel(args);
      break;
    case 'cost':
      handleCost(args);
      break;
    case 'agents':
      handleAgentReport();
      break;
    case 'help':
    case '--help':
    case '-h':
      printHelp();
      break;
    default:
      if (command) {
        console.log(`${colors.red}未知命令: ${command}${colors.reset}`);
      }
      printHelp();
  }
}

main();