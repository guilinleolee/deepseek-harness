
/**
 * On-Demand Hooks Handler - 危险操作保护机制
 *
 * 功能：在执行危险操作前弹出确认提示，让用户明确批准
 * 基于 Anthropic Skills 最佳实践实现
 */

const fs = require('fs');
const path = require('path');

// 危险命令模式匹配
const DANGEROUS_PATTERNS = [
  { pattern: /restore\.sh/i, message: '⚠️ 恢复操作将覆盖当前数据', level: 'high' },
  { pattern: /rollback\.sh/i, message: '⚠️ 回滚操作可能丢失工作', level: 'high' },
  { pattern: /deploy.*production/i, message: '🚀 部署到生产环境', level: 'high' },
  { pattern: /rm\s+(-rf|--recursive)/i, message: '🗑️ 递归删除操作', level: 'critical' },
  { pattern: /mkfs/i, message: '💿 格式化磁盘', level: 'critical' },
  { pattern: /dd\s+if=/i, message: '💿 磁盘写入操作', level: 'critical' },
  { pattern: /:\(\)\{\s*:\|:\s*&\s*\};\s*:/i, message: '💣 Fork炸弹检测', level: 'critical' },
  { pattern: /publish\.(sh|py)/i, message: '📤 发布到外部平台', level: 'medium' },
  { pattern: /post-to-(wechat|weibo|x)/i, message: '📤 发布到社交媒体', level: 'medium' },
  { pattern: /drop\s+(table|database)/i, message: '🗃️ 删除数据库表/库', level: 'high' },
  { pattern: /truncate\s+table/i, message: '🗃️ 清空数据表', level: 'high' },
  { pattern: /git\s+push\s+(-f|--force)/i, message: '🔥 强制推送到远程', level: 'high' },
  { pattern: /git\s+reset\s+--hard/i, message: '⏪ 硬重置Git状态', level: 'high' },
];

// Skill级别保护配置
const SKILL_PROTECTION = {
  'openclaw-backup': {
    commands: ['restore.sh'],
    confirm: '⚠️ 确定要恢复备份吗？这将覆盖当前数据！',
    requireDryRun: true,
    dryRunFlag: '--dry-run'
  },
  'paperclip-governance': {
    commands: ['rollback.sh'],
    confirm: '⚠️ 确定要回滚到指定版本吗？此操作不可逆！',
    requireApproval: true
  },
  'paperclip-heartbeat': {
    commands: ['heartbeat.ts'],
    confirm: '⏰ 确定要修改心跳调度吗？可能影响生产任务。',
    level: 'medium'
  },
  'x-publisher': {
    commands: ['publish.sh'],
    confirm: '📤 确定要发布到X/Twitter吗？内容将公开可见。',
    requireApproval: true
  },
  'baoyu-post-to-wechat': {
    commands: ['post_to_wechat.py'],
    confirm: '📤 确定要发布到微信公众号吗？',
    requireApproval: true
  },
  'baoyu-post-to-weibo': {
    commands: ['post_to_weibo.py'],
    confirm: '📤 确定要发布到微博吗？内容将公开可见。',
    requireApproval: true
  },
  'scrapy-anti-ban': {
    commands: ['spider.py'],
    confirm: '🕷️ 确定要启动爬虫吗？请确保符合目标网站服务条款。',
    level: 'medium'
  }
};

// 安全等级配置
const SAFETY_LEVELS = {
  critical: {
    requirePassword: true,
    countdown: 10,
    logAudit: true
  },
  high: {
    requireApproval: true,
    countdown: 5,
    logAudit: true
  },
  medium: {
    requireApproval: true,
    countdown: 0,
    logAudit: false
  },
  low: {
    requireApproval: false,
    countdown: 0,
    logAudit: false
  }
};

/**
 * 检测命令是否为危险操作
 */
function detectDangerousOperation(command) {
  const detections = [];

  for (const { pattern, message, level } of DANGEROUS_PATTERNS) {
    if (pattern.test(command)) {
      detections.push({ pattern: pattern.source, message, level });
    }
  }

  return detections;
}

/**
 * 检测Skill相关操作
 */
function detectSkillOperation(command) {
  for (const [skillName, config] of Object.entries(SKILL_PROTECTION)) {
    for (const cmd of config.commands) {
      if (command.includes(cmd)) {
        return { skillName, ...config };
      }
    }
  }
  return null;
}

/**
 * 生成确认消息
 */
function generateConfirmation(detections, skillOp) {
  const lines = ['\n🛡️ 天龙引擎 - 危险操作保护\n'];
  lines.push('═'.repeat(50));

  if (detections.length > 0) {
    lines.push('\n⚠️ 检测到危险操作:');
    detections.forEach((d, i) => {
      lines.push(`  ${i + 1}. ${d.message} [${d.level.toUpperCase()}]`);
    });
  }

  if (skillOp) {
    lines.push(`\n📦 Skill: ${skillOp.skillName}`);
    lines.push(`❓ ${skillOp.confirm}`);
    if (skillOp.requireDryRun) {
      lines.push(`💡 建议: 先执行 --dry-run 预览`);
    }
  }

  lines.push('\n' + '═'.repeat(50));
  lines.push('请确认是否继续? [y/N]: ');

  return lines.join('\n');
}

/**
 * 主处理函数
 */
async function handleOnDemandHook(command, context = {}) {
  // 1. 检测危险模式
  const detections = detectDangerousOperation(command);

  // 2. 检测Skill操作
  const skillOp = detectSkillOperation(command);

  // 3. 如果无危险操作，直接放行
  if (detections.length === 0 && !skillOp) {
    return { allowed: true, reason: 'safe' };
  }

  // 4. 确定最高危险等级
  const levels = detections.map(d => d.level);
  const highestLevel = levels.includes('critical') ? 'critical' :
                       levels.includes('high') ? 'high' :
                       levels.includes('medium') ? 'medium' : 'low';

  const safetyConfig = SAFETY_LEVELS[highestLevel];

  // 5. 生成确认消息
  const confirmation = generateConfirmation(detections, skillOp);

  // 6. 返回需要用户确认
  return {
    allowed: false,
    pending: true,
    confirmation,
    safetyConfig,
    detections,
    skillOp,
    originalCommand: command
  };
}

/**
 * 记录审计日志
 */
function logAuditEntry(command, detections, approved, user) {
  const logPath = path.join(
    process.env.CLAUDE_PLUGIN_DATA || path.join(process.env.HOME, '.claude/plugins/data'),
    'audit-log.json'
  );

  const entry = {
    timestamp: new Date().toISOString(),
    command,
    detections: detections.map(d => d.message),
    approved,
    user: user || 'unknown',
    sessionId: process.env.CLAUDE_SESSION_ID || 'unknown'
  };

  let logs = [];
  try {
    if (fs.existsSync(logPath)) {
      logs = JSON.parse(fs.readFileSync(logPath, 'utf8'));
    }
  } catch (e) {
    logs = [];
  }

  logs.push(entry);

  // 保留最近1000条记录
  if (logs.length > 1000) {
    logs = logs.slice(-1000);
  }

  fs.mkdirSync(path.dirname(logPath), { recursive: true });
  fs.writeFileSync(logPath, JSON.stringify(logs, null, 2));
}

// 导出
module.exports = {
  handleOnDemandHook,
  detectDangerousOperation,
  detectSkillOperation,
  generateConfirmation,
  logAuditEntry,
  DANGEROUS_PATTERNS,
  SKILL_PROTECTION,
  SAFETY_LEVELS
};