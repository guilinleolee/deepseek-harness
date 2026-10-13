
/**
 * 天龙引擎 V7.5 - 交互模式管理
 * Code / Plan / Ask 三模式切换
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

// 模式状态文件
const MODE_PATH = path.join(os.homedir(), '.claude', '.interaction-mode.json');

/**
 * 交互模式定义
 */
const INTERACTION_MODES = {
  code: {
    name: 'Code',
    description: '代码编写模式 - 直接执行、快速迭代',
    features: {
      autoPlan: false,        // 不自动生成计划
      quickExecution: true,   // 快速执行
      skipReview: false,      // 不跳过审查
      defaultAgent: '03builder',
      defaultModel: 'claude-sonnet-4-6',
      systemPrompt: `你是一个高效的代码构建师。直接执行用户请求，快速迭代。
- 跳过详细规划，直接开始编码
- 遇到问题时快速调整
- 完成后简要总结`
    }
  },
  plan: {
    name: 'Plan',
    description: '任务规划模式 - 生成计划、分步执行',
    features: {
      autoPlan: true,         // 自动生成计划
      quickExecution: false,  // 按计划执行
      skipReview: false,      // 需要审查
      defaultAgent: '02architect',
      defaultModel: 'claude-opus-4-6',
      systemPrompt: `你是一个严谨的架构师。先规划再执行。
- 分析需求，生成详细计划
- 分步骤执行，每步确认
- 完成后全面审查`
    }
  },
  ask: {
    name: 'Ask',
    description: '问答咨询模式 - 详细解释、提供参考',
    features: {
      autoPlan: false,        // 不生成计划
      quickExecution: false,  // 详细回答
      skipReview: true,       // 跳过代码审查
      defaultAgent: '00analyst',
      defaultModel: 'claude-sonnet-4-6',
      systemPrompt: `你是一个专业的分析师。详细解答用户问题。
- 提供全面的分析和解释
- 引用相关参考资料
- 给出专业建议`
    }
  }
};

/**
 * 读取当前模式
 */
function readMode() {
  try {
    if (fs.existsSync(MODE_PATH)) {
      return JSON.parse(fs.readFileSync(MODE_PATH, 'utf-8'));
    }
  } catch (e) {
    // ignore
  }
  return { currentMode: 'code', previousMode: null };
}

/**
 * 写入模式状态
 */
function writeMode(state) {
  const dir = path.dirname(MODE_PATH);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  fs.writeFileSync(MODE_PATH, JSON.stringify(state, null, 2));
}

/**
 * 获取当前模式
 */
function getCurrentMode() {
  const state = readMode();
  return INTERACTION_MODES[state.currentMode] || INTERACTION_MODES.code;
}

/**
 * 切换模式
 */
function switchMode(newMode) {
  if (!INTERACTION_MODES[newMode]) {
    return { success: false, error: `未知模式: ${newMode}` };
  }

  const state = readMode();
  const previousMode = state.currentMode;

  state.currentMode = newMode;
  state.previousMode = previousMode;
  state.switchedAt = Date.now();

  writeMode(state);

  return {
    success: true,
    previousMode,
    currentMode: newMode,
    modeInfo: INTERACTION_MODES[newMode]
  };
}

/**
 * 获取模式列表
 */
function listModes() {
  return Object.entries(INTERACTION_MODES).map(([key, mode]) => ({
    key,
    name: mode.name,
    description: mode.description,
    defaultAgent: mode.features.defaultAgent,
    defaultModel: mode.features.defaultModel
  }));
}

/**
 * 格式化模式报告
 */
function formatModeReport() {
  const state = readMode();
  const currentMode = INTERACTION_MODES[state.currentMode];

  const lines = [
    `🎯 当前交互模式: ${currentMode.name}`,
    '='.repeat(50),
    `描述: ${currentMode.description}`,
    '',
    `默认 Agent: ${currentMode.features.defaultAgent}`,
    `默认模型: ${currentMode.features.defaultModel}`,
    '',
    '可用模式:',
    ...Object.entries(INTERACTION_MODES).map(([key, mode]) => {
      const isActive = key === state.currentMode;
      return `  ${isActive ? '✓' : ' '} ${key.padEnd(6)} - ${mode.name}: ${mode.description}`;
    }),
    '',
    '切换命令: /mode <code|plan|ask>'
  ];

  return lines.join('\n');
}

/**
 * 根据任务内容推荐模式
 */
function recommendMode(prompt) {
  const promptLower = prompt.toLowerCase();

  // 关键词匹配
  const codeKeywords = ['写代码', '实现', '修复', 'bug', 'debug', '重构', 'code', 'implement', 'fix'];
  const planKeywords = ['计划', '规划', '设计', '架构', 'plan', 'design', 'architect'];
  const askKeywords = ['什么是', '为什么', '怎么', '解释', '分析', 'what', 'why', 'how', 'explain'];

  let codeScore = 0;
  let planScore = 0;
  let askScore = 0;

  for (const kw of codeKeywords) {
    if (promptLower.includes(kw)) codeScore += 2;
  }
  for (const kw of planKeywords) {
    if (promptLower.includes(kw)) planScore += 2;
  }
  for (const kw of askKeywords) {
    if (promptLower.includes(kw)) askScore += 2;
  }

  // 返回得分最高的模式
  if (codeScore >= planScore && codeScore >= askScore) return 'code';
  if (planScore >= askScore) return 'plan';
  return 'ask';
}

module.exports = {
  INTERACTION_MODES,
  readMode,
  writeMode,
  getCurrentMode,
  switchMode,
  listModes,
  formatModeReport,
  recommendMode
};