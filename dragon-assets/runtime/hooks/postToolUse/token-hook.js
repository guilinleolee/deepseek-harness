#!/usr/bin/env node
/**
 * 天龙引擎 V7.5 - Token Hook (JavaScript 包装器)
 * postToolUse 触发点
 *
 * 功能：
 * - 从工具响应中提取 Token 用量
 * - 记录到 token_usage 表
 * - 关联当前会话和消息
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

// 状态文件路径
const STATE_PATH = path.join(os.homedir(), '.claude', '.session-state.json');
const TOKEN_PATH = path.join(os.homedir(), '.claude', '.token-usage.json');

// 模型定价 ($/1M tokens)
const MODEL_PRICING = {
  'claude-opus-4-6': { input: 15, output: 75 },
  'claude-sonnet-4-6': { input: 3, output: 15 },
  'claude-sonnet-4': { input: 3, output: 15 },
  'claude-haiku-4-5': { input: 0.80, output: 4 },
  'claude-haiku': { input: 0.80, output: 4 },
  'qwen3.5-plus': { input: 0.5, output: 2 },  // 添加当前模型
};

/**
 * 生成 UUID
 */
function uuidv4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

/**
 * 读取会话状态
 */
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

/**
 * 读取 Token 使用记录
 */
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

/**
 * 写入 Token 使用记录
 */
function writeTokenUsage(data) {
  const dir = path.dirname(TOKEN_PATH);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  fs.writeFileSync(TOKEN_PATH, JSON.stringify(data, null, 2));
}

/**
 * 计算成本
 */
function calculateCost(model, inputTokens, outputTokens) {
  const pricing = MODEL_PRICING[model] || MODEL_PRICING['claude-sonnet-4'];
  const inputCost = (inputTokens / 1_000_000) * pricing.input;
  const outputCost = (outputTokens / 1_000_000) * pricing.output;
  return Number((inputCost + outputCost).toFixed(6));
}

/**
 * Hook 主函数
 */
function main() {
  const args = process.argv.slice(2);

  // 解析参数
  let toolResult = {};
  let context = {};

  try {
    if (args[0]) toolResult = JSON.parse(args[0]);
    if (args[1]) context = JSON.parse(args[1]);
  } catch (e) {
    // ignore parse errors
  }

  // 获取当前会话
  const sessionState = readSessionState();
  const sessionId = sessionState.currentSessionId;

  if (!sessionId) {
    // 无活跃会话，跳过
    console.log(JSON.stringify({ recorded: false, reason: 'no_active_session' }));
    return;
  }

  // 提取 Token 用量（从响应头或上下文）
  const headers = toolResult.responseHeaders || toolResult.headers || {};
  const inputTokens = parseInt(headers['anthropic-input-tokens'] || headers['x-input-tokens'] || '0', 10);
  const outputTokens = parseInt(headers['anthropic-output-tokens'] || headers['x-output-tokens'] || '0', 10);

  // 如果没有 Token 数据，尝试从 usage 字段提取
  const usage = toolResult.usage || {};
  const finalInputTokens = inputTokens || usage.input_tokens || usage.inputTokens || 0;
  const finalOutputTokens = outputTokens || usage.output_tokens || usage.outputTokens || 0;

  if (finalInputTokens === 0 && finalOutputTokens === 0) {
    // 无 Token 数据，跳过
    console.log(JSON.stringify({ recorded: false, reason: 'no_token_data' }));
    return;
  }

  // 确定模型
  const model = headers['anthropic-model'] || headers['x-model'] || context.model || 'qwen3.5-plus';

  // 计算成本
  const costUsd = calculateCost(model, finalInputTokens, finalOutputTokens);

  // 记录 Token 使用
  const tokenData = readTokenUsage();
  const record = {
    id: uuidv4(),
    sessionId,
    timestamp: Date.now(),
    inputTokens: finalInputTokens,
    outputTokens: finalOutputTokens,
    costUsd,
    model,
    operation: 'tool_use',
    agentId: context.agentId || null,
    toolName: context.toolName || null,
  };

  // 添加记录
  tokenData.records.push(record);

  // 更新统计
  tokenData.stats.totalInputTokens += finalInputTokens;
  tokenData.stats.totalOutputTokens += finalOutputTokens;
  tokenData.stats.totalCostUsd += costUsd;

  // 只保留最近 1000 条记录
  if (tokenData.records.length > 1000) {
    tokenData.records = tokenData.records.slice(-1000);
  }

  writeTokenUsage(tokenData);

  // 输出结果
  console.log(JSON.stringify({
    recorded: true,
    sessionId,
    inputTokens: finalInputTokens,
    outputTokens: finalOutputTokens,
    costUsd,
    model,
    totalCost: tokenData.stats.totalCostUsd,
  }));
}

// 如果直接运行
if (require.main === module) {
  main();
}

module.exports = { main, readTokenUsage, writeTokenUsage, calculateCost, MODEL_PRICING };