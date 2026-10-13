/**
 * SIMPLIFY-IGNORE Hook - 简化跳过拦截器
 *
 * 工作原理:
 * PreToolUse: 检测当前工具调用是否被标记为"简化/跳过"类别
 *   → 识别simplify_/ignore_/skip_前缀的标记
 *   → 提供简化替代方案或直接跳过
 *
 * PostToolUse: 记录被跳过/简化的操作，供后续审计
 *
 * 适用场景:
 * - 非关键路径的工具调用（如日志、美化）
 * - 可延迟到后续阶段的操作
 * - 已被其他工具覆盖的重复调用
 *
 * 缓存Key: sha256(toolName + action)
 * 调试模式: SIMPLIFY_DEBUG=1
 */

const crypto = require('crypto');

const DEBUG = process.env.SIMPLIFY_DEBUG === '1';

// 简化/跳过模式配置
const SIMPLIFY_PATTERNS = [
  // 日志美化类 - 可跳过
  { pattern: /^(format|beautify|prettify)/i, reason: '格式化操作非关键路径', suggest: '跳过或延迟到最终审查阶段' },
  // 文档生成类 - 可延迟
  { pattern: /^(generate_doc|create_doc|write_docs?)$/i, reason: '文档生成非阻塞操作', suggest: '延迟到IMPLEMENT阶段末尾' },
  // 注释美化类 - 可跳过
  { pattern: /^(add_comments|auto_comment|doc_comment)/i, reason: '自动注释不保证质量', suggest: '手动补充关键注释' },
  // 重复工具调用检测
  { pattern: /^(grep|search_find)$/i, reason: '重复搜索操作', suggest: '使用已有搜索结果' },
  // 非关键验证
  { pattern: /^(lint|lint_check)$/i, reason: 'lint非阻塞性检查', suggest: '跳过lint_error工具直接进入关键验证' },
  // 预览类操作
  { pattern: /^(preview|render_preview)/i, reason: '预览非阻塞操作', suggest: '延迟到最终验证阶段' },
];

// 强制跳过模式（Never Do层级）
const NEVER_PATTERNS = [
  // 危险删除操作
  { pattern: /^(rm_rf|delete_all|drop_table)/i, reason: '危险操作需人工确认', action: 'block', requireConfirm: true },
  // 生产环境直接操作
  { pattern: /^(deploy_prod|write_prod|update_prod)/i, reason: '生产环境变更需审批流程', action: 'block', requireConfirm: true },
  // 敏感信息访问
  { pattern: /^(get_secret|read_env_prod|access_credentials)/i, reason: '敏感操作需安全审核', action: 'block', requireConfirm: true },
];

// 简化替代方案映射
const SIMPLIFY_ALTERNATIVES = {
  'format': '直接进入下一工具',
  'beautify': '保持现有格式',
  'prettify': '保持现有格式',
  'generate_doc': '在IMPLEMENT阶段末尾统一生成',
  'create_docs': '在IMPLEMENT阶段末尾统一生成',
  'write_docs': '在IMPLEMENT阶段末尾统一生成',
  'add_comments': '仅在复杂逻辑处手动添加',
  'lint': '在关键路径测试后执行',
  'lint_check': '在关键路径测试后执行',
  'preview': '在最终验证阶段执行',
};

/**
 * 检测工具是否应该被简化/跳过
 */
function shouldSimplify(toolName) {
  const normalized = toolName.toLowerCase().trim();

  for (const { pattern, reason, suggest } of SIMPLIFY_PATTERNS) {
    if (pattern.test(normalized)) {
      return { simplify: true, reason, suggest };
    }
  }

  return { simplify: false };
}

/**
 * 检测工具是否应该被阻止（Never Do）
 */
function shouldBlock(toolName) {
  const normalized = toolName.toLowerCase().trim();

  for (const { pattern, reason, action, requireConfirm } of NEVER_PATTERNS) {
    if (pattern.test(normalized)) {
      return { block: true, reason, action, requireConfirm };
    }
  }

  return { block: false };
}

/**
 * 获取简化建议
 */
function getAlternative(toolName) {
  const normalized = toolName.toLowerCase().trim();
  return SIMPLIFY_ALTERNATIVES[normalized] || null;
}

/**
 * 缓存标识计算
 */
function getSimplifyKey(toolName, context) {
  const data = `${toolName}:${context || ''}`;
  return crypto.createHash('sha256').update(data).digest('hex').substring(0, 16);
}

// 简化操作记录（内存缓存）
const simplifyLog = new Map();
const MAX_LOG_SIZE = 100;

/**
 * 记录简化操作
 */
function logSimplify(toolName, reason, suggestion) {
  const key = getSimplifyKey(toolName, 'log');
  const entry = {
    toolName,
    reason,
    suggestion,
    timestamp: new Date().toISOString(),
    skipped: true,
  };

  simplifyLog.set(key, entry);

  // 防止内存溢出
  if (simplifyLog.size > MAX_LOG_SIZE) {
    const firstKey = simplifyLog.keys().next().value;
    simplifyLog.delete(firstKey);
  }

  if (DEBUG) console.log('[SIMPLIFY-IGNORE]', toolName, '→ skipped:', reason);
}

// Hook: PreToolUse - 检测简化/阻止模式
async function preToolUseHook(params) {
  const toolName = params.toolName || params.arguments?.tool;
  if (!toolName) return null;

  // 检查Never Do模式（最高优先级）
  const blockCheck = shouldBlock(toolName);
  if (blockCheck.block) {
    if (DEBUG) {
      console.log('[SIMPLIFY-IGNORE] BLOCKED:', toolName);
      console.log('[SIMPLIFY-IGNORE] Reason:', blockCheck.reason);
    }

    return {
      intercepted: true,
      result: {
        error: `工具调用被阻止: ${blockCheck.reason}`,
        toolName,
        action: 'blocked',
        requireConfirm: blockCheck.requireConfirm,
        suggestion: '请通过人工审批流程执行此操作',
      },
    };
  }

  // 检查简化模式
  const simplifyCheck = shouldSimplify(toolName);
  if (simplifyCheck.simplify) {
    const alternative = getAlternative(toolName);

    if (DEBUG) {
      console.log('[SIMPLIFY-IGNORE] SIMPLIFY:', toolName);
      console.log('[SIMPLIFY-IGNORE] Reason:', simplifyCheck.reason);
      console.log('[SIMPLIFY-IGNORE] Suggestion:', simplifyCheck.suggest);
    }

    // 记录简化操作
    logSimplify(toolName, simplifyCheck.reason, simplifyCheck.suggest);

    return {
      intercepted: true,
      result: {
        skipped: true,
        toolName,
        reason: simplifyCheck.reason,
        suggestion: simplifyCheck.suggest,
        alternative: alternative,
      },
    };
  }

  return null;
}

// Hook: PostToolUse - 记录跳过统计
async function postToolUseHook(params) {
  const toolName = params.toolName || params.arguments?.tool;
  if (!toolName) return null;

  const result = params.result;

  // 记录成功执行的工具（可能与简化操作对比）
  if (result && !result.skipped && !result.blocked) {
    const key = getSimplifyKey(toolName, 'executed');
    simplifyLog.set(key, {
      toolName,
      timestamp: new Date().toISOString(),
      executed: true,
    });
  }

  return null;
}

/**
 * 获取简化统计摘要
 */
function getSimplifyStats() {
  let skipped = 0;
  let executed = 0;

  for (const entry of simplifyLog.values()) {
    if (entry.skipped) skipped++;
    else if (entry.executed) executed++;
  }

  return {
    total: simplifyLog.size,
    skipped,
    executed,
    skipRate: simplifyLog.size > 0 ? (skipped / simplifyLog.size * 100).toFixed(1) + '%' : '0%',
  };
}

module.exports = {
  preToolUseHook,
  postToolUseHook,
  shouldSimplify,
  shouldBlock,
  getAlternative,
  getSimplifyStats,
  SIMPLIFY_PATTERNS,
  NEVER_PATTERNS,
};
