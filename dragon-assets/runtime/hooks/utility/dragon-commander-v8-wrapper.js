
/**
 * 🐉 天龙引擎指挥官Hook包装器 V8.0
 * 指挥官：李依依（一一）
 * 系统提示词：../../prompts/liyiyi-commander-system-prompt.md
 *
 * V8.0 全面重构版
 * - 人设系统
 * - 对话历史记忆
 * - 个性化响应生成
 */

const DragonCommanderV8 = require('./dragon-commander.js');  // Part 3 重构修复：dragon-commander-v8.js 不存在，v8-wrapper 实际可用基础版

// 全局指挥官实例
let globalCommanderV8 = null;

/**
 * 初始化指挥官（如果还没有初始化）
 */
function ensureCommander() {
  if (!globalCommanderV8) {
    globalCommanderV8 = new DragonCommanderV8();
    console.log('🐉 天龙引擎指挥官李依依（一一）V8.0已就位！');
  }
  return globalCommanderV8;
}

/**
 * Hook: 用户提交提示时触发（V8.0增强版）
 * 分析用户输入，提供智能建议和个性化响应
 */
async function userPromptSubmitHookV8(input, context = {}) {
  try {
    const commander = ensureCommander();

    // 增强版需求分析
    const result = await commander.analyzeRequirementEnhanced(input, context);

    // 格式化输出
    const output = commander.formatOutput(result);

    console.log(output);

    return result;
  } catch (error) {
    console.error('指挥官分析失败:', error.message);
    return { analysis: null, personalizedResponse: null };
  }
}

/**
 * Hook: 工具使用后触发（V8.0增强版）
 * 记录任务结果，学习用户反馈
 */
function postToolUseHookV8(toolName, toolResult, sessionId) {
  try {
    const commander = ensureCommander();

    // 记录任务执行
    if (toolName === 'Task' && sessionId) {
      commander.memory.recordTask(sessionId, {
        tool: toolName,
        result: toolResult,
        status: toolResult ? 'completed' : 'failed'
      });
    }
  } catch (error) {
    console.error('任务记录失败:', error.message);
  }
}

/**
 * 获取用户画像
 */
function getUserProfile(userId) {
  const commander = ensureCommander();
  return commander.memory.getUserProfile(userId);
}

/**
 * 更新用户偏好
 */
function updateUserPreference(userId, key, value) {
  const commander = ensureCommander();
  commander.memory.updatePreference(userId, key, value);
}

/**
 * 获取对话历史
 */
function getConversationHistory(userId, limit = 10) {
  const commander = ensureCommander();
  const sessions = commander.memory.sessions.filter(s => s.userId === userId);
  const messages = sessions.flatMap(s => s.messages || []);
  return messages.slice(-limit);
}

// 导出Hook函数
module.exports = {
  userPromptSubmitHookV8,
  postToolUseHookV8,
  getUserProfile,
  updateUserPreference,
  getConversationHistory,
  ensureCommander
};
