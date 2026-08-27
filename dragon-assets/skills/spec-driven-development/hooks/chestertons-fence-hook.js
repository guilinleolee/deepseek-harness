/**
 * CHESTERTON'S FENCE HOOK - 防删改保护拦截器
 *
 * 核心原则: G.K. Chesterton's Fence (1905)
 *   "Before removing a fence, understand why it was put there first."
 *   (在移除一道围栏之前，先理解它为什么被建在那里。)
 *
 * 工作原理:
 * PreToolUse: 检测删除/修改操作
 *   → 分析危险操作: 删除代码、移除配置、清理文件
 *   → 返回合理性查询，要求理解后再执行
 *
 * PostToolUse: 记录被阻止/质疑的删改操作
 *
 * 适用场景:
 * - 代码清理/重构前的配置理解
 * - 删除未文档化依赖前的原因追溯
 * - 移除"魔法代码"前的目的确认
 *
 * 缓存Key: sha256(toolName + action)
 * 调试模式: FENCE_DEBUG=1
 */

const crypto = require('crypto');

const DEBUG = process.env.FENCE_DEBUG === '1';

// 永远不要删除的模式 (最高优先级)
const NEVER_REMOVE_PATTERNS = [
  // 危险删除操作
  { pattern: /^(delete_code|remove_code|rm_code|code_delete)$/i,
    reason: '删除代码前必须理解其存在理由',
    action: 'block', requireConfirm: true,
    rationale_question: '这段代码删除前需要回答: 为什么当初要写它? 是否有其他地方依赖它? 是否可以用注释替代删除?' },

  { pattern: /^(delete_line|remove_line|rm_line|line_delete)$/i,
    reason: '单行删除可能影响程序逻辑',
    action: 'block', requireConfirm: true,
    rationale_question: '这行代码删除前需要回答: 为什么当初要写它? 是否有其他地方引用它?' },

  { pattern: /^(delete_file|rm_file|file_delete|remove_file)$/i,
    reason: '删除文件是不可逆操作',
    action: 'block', requireConfirm: true,
    rationale_question: '删除此文件前需要回答: 为什么当初要创建它? 是否有版本控制可以恢复? 是否备份了重要内容?' },

  { pattern: /^(delete_dir|rm_dir|dir_delete|remove_directory)$/i,
    reason: '删除目录可能包含重要文件',
    action: 'block', requireConfirm: true,
    rationale_question: '删除此目录前需要回答: 目录内有多少文件? 是否包含重要配置? 是否有版本控制?' },

  { pattern: /^(delete_config|remove_config|rm_config|config_delete)$/i,
    reason: '删除配置前必须理解其影响',
    action: 'block', requireConfirm: true,
    rationale_question: '此配置删除前需要回答: 当初为什么添加它? 删除后会影响哪些功能? 是否有回滚方案?' },

  { pattern: /^(drop_table|delete_table|rm_table|table_delete)$/i,
    reason: '删除数据库表是灾难性操作',
    action: 'block', requireConfirm: true,
    rationale_question: '删除此数据库表前需要回答: 表中有多少数据? 是否已备份? 是否有其他系统依赖此表?' },

  { pattern: /^(drop_database|rm_database|delete_database)$/i,
    reason: '删除数据库是最危险的操作之一',
    action: 'block', requireConfirm: true,
    rationale_question: '删除整个数据库前需要回答: 数据库中有多少表? 数据量多大? 是否已完整备份?' },

  { pattern: /^(remove_dependency|rm_dependency|uninstall_core|delete_package)$/i,
    reason: '删除依赖可能破坏系统完整性',
    action: 'block', requireConfirm: true,
    rationale_question: '删除此依赖前需要回答: 为什么当初要引入它? 是否有其他依赖使用它? 删除后是否测试过?' },

  { pattern: /^(delete_branch|rm_branch|branch_delete|force_push)$/i,
    reason: '删除分支或强制推送会丢失历史',
    action: 'block', requireConfirm: true,
    rationale_question: '删除分支前需要回答: 分支中有多少未合并的提交? 是否已备份重要工作?' },
];

// 警告级删改模式
const WARN_REMOVE_PATTERNS = [
  // 重构相关
  { pattern: /^(refactor_cleanup|clean_up_code|code_cleanup|remove_dead_code)$/i,
    reason: '代码清理前需要理解哪些代码"死"了',
    action: 'warn',
    rationale_question: '这段代码被标记为"死代码"前需要验证: 是否有反射调用? 是否有动态引用? 是否在测试中被覆盖?' },

  { pattern: /^(rename_file|move_file|relocate_file)$/i,
    reason: '文件重命名可能破坏外部引用',
    action: 'warn',
    rationale_question: '重命名此文件前需要确认: 是否有硬编码路径引用它? 是否已更新所有import?' },

  { pattern: /^(rename_function|rename_variable|rename_class|refactor_rename)$/i,
    reason: '重命名可能破坏动态调用',
    action: 'warn',
    rationale_question: '重命名前需要确认: 是否有eval/动态调用? 是否有反射使用? 是否已更新所有引用?' },

  { pattern: /^(linter_autofix|format_code|auto_format)$/i,
    reason: '自动格式化可能改变代码语义',
    action: 'warn',
    rationale_question: '自动格式化前需要确认: 是否理解格式变更的范围? 是否有特殊格式的代码片段?' },

  { pattern: /^(remove_comment|delete_comment|strip_comments)$/i,
    reason: '删除注释可能丢失重要上下文',
    action: 'warn',
    rationale_question: '删除注释前需要确认: 注释是否包含重要说明? 是否可以通过重构代码替代注释?' },

  { pattern: /^(delete_backup|rm_backup|cleanup_backup)$/i,
    reason: '删除备份前需要确认原始文件已安全',
    action: 'warn',
    rationale_question: '删除备份前需要确认: 原始文件是否已验证正确? 是否需要保留多版本备份?' },

  { pattern: /^(delete_log|rm_log|clear_log|truncate_log)$/i,
    reason: '删除日志前可能丢失重要调试信息',
    action: 'warn',
    rationale_question: '删除日志前需要确认: 是否已提取需要的调试信息? 是否需要保留最近一段时间的日志?' },

  { pattern: /^(delete_cache|rm_cache|clear_cache|flush_cache)$/i,
    reason: '清除缓存可能导致性能下降',
    action: 'warn',
    rationale_question: '清除缓存前需要确认: 是否已记录当前缓存状态? 是否会影响正在运行的进程?' },

  { pattern: /^(delete_env|rm_env|remove_env|unset_variable)$/i,
    reason: '删除环境变量可能破坏应用配置',
    action: 'warn',
    rationale_question: '删除此环境变量前需要确认: 是否有应用依赖它? 是否已在代码中硬编码了替代值?' },
];

/**
 * 检测是否应该阻止删除操作
 */
function shouldBlock(toolName) {
  const normalized = toolName.toLowerCase().trim();
  for (const { pattern, reason, action, requireConfirm, rationale_question } of NEVER_REMOVE_PATTERNS) {
    if (pattern.test(normalized)) {
      return { block: true, reason, action, requireConfirm, rationale_question };
    }
  }
  return { block: false };
}

/**
 * 检测是否应该警告删除操作
 */
function shouldWarn(toolName) {
  const normalized = toolName.toLowerCase().trim();
  for (const { pattern, reason, action, rationale_question } of WARN_REMOVE_PATTERNS) {
    if (pattern.test(normalized)) {
      return { warn: true, reason, action, rationale_question };
    }
  }
  return { warn: false };
}

/**
 * 获取删除操作的理由要求
 */
function getRationale(toolName) {
  const normalized = toolName.toLowerCase().trim();

  for (const item of NEVER_REMOVE_PATTERNS) {
    if (item.pattern.test(normalized)) {
      return {
        level: 'MUST_ANSWER',
        question: item.rationale_question,
        reason: item.reason,
      };
    }
  }

  for (const item of WARN_REMOVE_PATTERNS) {
    if (item.pattern.test(normalized)) {
      return {
        level: 'SHOULD_ANSWER',
        question: item.rationale_question,
        reason: item.reason,
      };
    }
  }

  return null;
}

/**
 * 计算缓存Key
 */
function getFenceKey(toolName, context) {
  const data = `${toolName}:${context || ''}`;
  return crypto.createHash('sha256').update(data).digest('hex').substring(0, 16);
}

// 内存缓存: 记录被质疑的删改操作
const fenceLog = new Map();
const MAX_LOG_SIZE = 100;

/**
 * 记录围栏质疑
 */
function logFence(toolName, level, question, reason) {
  const key = getFenceKey(toolName, 'fence');
  const entry = {
    toolName,
    level,
    question,
    reason,
    timestamp: new Date().toISOString(),
    challenged: true,
  };

  fenceLog.set(key, entry);

  // 防止内存溢出
  if (fenceLog.size > MAX_LOG_SIZE) {
    const firstKey = fenceLog.keys().next().value;
    fenceLog.delete(firstKey);
  }

  if (DEBUG) console.log('[CHESTERTON-FENCE]', toolName, '→ challenged:', reason);
}

// Hook: PreToolUse - 检测删改操作
async function preToolUseHook(params) {
  const toolName = params.toolName || params.arguments?.tool;
  if (!toolName) return null;

  // 最高优先级: NEVER_REMOVE 检查
  const blockCheck = shouldBlock(toolName);
  if (blockCheck.block) {
    if (DEBUG) {
      console.log('[CHESTERTON-FENCE] BLOCKED:', toolName);
      console.log('[CHESTERTON-FENCE] Reason:', blockCheck.reason);
      console.log('[CHESTERTON-FENCE] Rationale Required:', blockCheck.rationale_question);
    }

    logFence(toolName, 'MUST_ANSWER', blockCheck.rationale_question, blockCheck.reason);

    return {
      intercepted: true,
      result: {
        error: `删除操作被阻止: ${blockCheck.reason}`,
        toolName,
        action: 'blocked',
        requireConfirm: blockCheck.requireConfirm,
        rationale_required: blockCheck.rationale_question,
        principle: 'Chesterton\'s Fence: 理解为什么它在那里, 才能决定是否移除它',
      },
    };
  }

  // 次优先级: WARN_REMOVE 检查
  const warnCheck = shouldWarn(toolName);
  if (warnCheck.warn) {
    if (DEBUG) {
      console.log('[CHESTERTON-FENCE] WARN:', toolName);
      console.log('[CHESTERTON-FENCE] Reason:', warnCheck.reason);
      console.log('[CHESTERTON-FENCE] Rationale Question:', warnCheck.rationale_question);
    }

    logFence(toolName, 'SHOULD_ANSWER', warnCheck.rationale_question, warnCheck.reason);

    return {
      intercepted: true,
      result: {
        warning: `此操作需要谨慎: ${warnCheck.reason}`,
        toolName,
        action: 'warned',
        rationale_required: warnCheck.rationale_question,
        principle: 'Chesterton\'s Fence: 理解为什么它在那里',
        suggestion: '请先回答合理性质疑, 再决定是否继续执行',
      },
    };
  }

  return null;
}

// Hook: PostToolUse - 记录执行统计
async function postToolUseHook(params) {
  const toolName = params.toolName || params.arguments?.tool;
  if (!toolName) return null;

  const result = params.result;

  // 记录实际执行的删改操作(可能之前被警告但仍执行)
  if (result && !result.blocked && !result.skipped && !result.error) {
    const key = getFenceKey(toolName, 'executed');
    fenceLog.set(key, {
      toolName,
      timestamp: new Date().toISOString(),
      executed: true,
      rationale_provided: params.arguments?.rationale || null,
    });
  }

  return null;
}

/**
 * 获取围栏统计摘要
 */
function getFenceStats() {
  let challenged = 0;
  let executed = 0;

  for (const entry of fenceLog.values()) {
    if (entry.challenged) challenged++;
    else if (entry.executed) executed++;
  }

  return {
    total: fenceLog.size,
    challenged,
    executed,
    challengeRate: fenceLog.size > 0 ? (challenged / fenceLog.size * 100).toFixed(1) + '%' : '0%',
  };
}

module.exports = {
  preToolUseHook,
  postToolUseHook,
  shouldBlock,
  shouldWarn,
  getRationale,
  getFenceStats,
  NEVER_REMOVE_PATTERNS,
  WARN_REMOVE_PATTERNS,
};
