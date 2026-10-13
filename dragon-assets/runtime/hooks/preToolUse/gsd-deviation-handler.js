#!/usr/bin/env node
/**
 * GSD Deviation Handler Hook
 *
 * Implements GSD's 4 deviation rules for automatic handling:
 * - Rule 1: Auto-fix bugs (自动修复Bug)
 * - Rule 2: Auto-add missing critical functionality (自动添加关键功能)
 * - Rule 3: Auto-fix blocking issues (自动修复阻塞问题)
 * - Rule 4: Ask about architectural changes (架构变更询问)
 *
 * @version 1.0.0
 * @author Dragon Engine Team
 */

const fs = require('fs');
const path = require('path');

// Deviation patterns for detection
const DEVIATION_PATTERNS = {
  // Rule 1: Bug indicators
  bug: [
    /error:/i,
    /exception:/i,
    /failed:/i,
    /TypeError:/,
    /ReferenceError:/,
    /SyntaxError:/,
    /AssertionError:/,
    /test.*failed/i,
    /expected.*but.*got/i,
    /unexpected.*result/i,
    /bug:/i,
    /fix:/i,
    /broken/i,
    /crash/i,
    /segfault/i,
    /null.*pointer/i,
    /undefined.*is not/i,
    /cannot read property/i,
    /is not a function/i,
    /is not defined/i,
  ],

  // Rule 2: Missing functionality indicators
  missing: [
    /not implemented/i,
    /missing.*feature/i,
    /todo:/i,
    /fixme:/i,
    /hack:/i,
    /not supported/i,
    /unsupported/i,
    /required.*but.*missing/i,
    /缺少.*功能/i,
    /未实现/i,
    /待实现/i,
  ],

  // Rule 3: Blocking issues
  blocking: [
    /blocked/i,
    /blocking/i,
    /cannot proceed/i,
    /stuck/i,
    /waiting for/i,
    /dependency.*failed/i,
    /permission denied/i,
    /access denied/i,
    /timeout/i,
    /connection refused/i,
    /service unavailable/i,
    /rate limit/i,
    /quota exceeded/i,
    /阻塞/i,
    /卡住/i,
    /无法继续/i,
  ],

  // Rule 4: Architectural changes
  architectural: [
    /refactor/i,
    /restructure/i,
    /redesign/i,
    /migrate/i,
    /upgrade.*to/i,
    /breaking change/i,
    /deprecated/i,
    /remove.*support/i,
    /change.*api/i,
    /modify.*interface/i,
    /重构/i,
    /架构调整/i,
    /重大变更/i,
    /破坏性/i,
  ]
};

// State file path for logging deviations
const STATE_FILE = path.join(process.cwd(), '.planning', 'STATE.md');
const LESSONS_FILE = path.join(process.cwd(), 'lessons.md');

/**
 * Detect deviation type from tool result
 */
function detectDeviation(result) {
  if (!result || typeof result !== 'string') {
    return null;
  }

  const resultStr = String(result);

  for (const [type, patterns] of Object.entries(DEVIATION_PATTERNS)) {
    for (const pattern of patterns) {
      if (pattern.test(resultStr)) {
        return {
          type,
          pattern: pattern.toString(),
          matched: resultStr.match(pattern)?.[0] || '',
          timestamp: new Date().toISOString()
        };
      }
    }
  }

  return null;
}

/**
 * Handle deviation based on rules
 */
function handleDeviation(deviation, context) {
  const { toolName } = context;

  switch (deviation.type) {
    case 'bug':
      // Rule 1: Auto-fix bugs
      return {
        action: 'auto_fix',
        rule: 'Rule 1',
        message: `[GSD Deviation] 检测到Bug，自动修复模式激活`,
        suggestion: `建议：使用systematic-debugging技能进行根因分析`,
        shouldContinue: true,
        logEntry: createLogEntry(deviation, 'auto_fix')
      };

    case 'missing':
      // Rule 2: Auto-add missing functionality
      return {
        action: 'auto_add',
        rule: 'Rule 2',
        message: `[GSD Deviation] 检测到缺失功能，自动添加模式激活`,
        suggestion: `建议：评估功能必要性后自动实现`,
        shouldContinue: true,
        logEntry: createLogEntry(deviation, 'auto_add')
      };

    case 'blocking':
      // Rule 3: Auto-fix blocking issues
      return {
        action: 'auto_resolve',
        rule: 'Rule 3',
        message: `[GSD Deviation] 检测到阻塞问题，自动解决模式激活`,
        suggestion: `建议：尝试替代方案或自动修复依赖`,
        shouldContinue: true,
        logEntry: createLogEntry(deviation, 'auto_resolve')
      };

    case 'architectural':
      // Rule 4: Ask about architectural changes
      return {
        action: 'ask_user',
        rule: 'Rule 4',
        message: `[GSD Deviation] 检测到架构变更需求，需要用户确认`,
        suggestion: `⚠️ 架构变更可能影响整体系统，建议：\n1. 停止当前操作\n2. 评估变更影响\n3. 获取用户明确授权`,
        shouldContinue: false,
        requiresConfirmation: true,
        logEntry: createLogEntry(deviation, 'architectural_change')
      };

    default:
      return null;
  }
}

/**
 * Create log entry for deviation
 */
function createLogEntry(deviation, action) {
  return {
    timestamp: deviation.timestamp,
    type: deviation.type,
    matched: deviation.matched,
    action,
    pattern: deviation.pattern
  };
}

/**
 * Log deviation to STATE.md
 */
function logToState(deviation, handler) {
  try {
    const stateDir = path.dirname(STATE_FILE);
    if (!fs.existsSync(stateDir)) {
      return; // No GSD project, skip logging
    }

    let content = '';
    if (fs.existsSync(STATE_FILE)) {
      content = fs.readFileSync(STATE_FILE, 'utf8');
    }

    const deviationEntry = `
## Deviation Log Entry
- **Timestamp**: ${deviation.timestamp}
- **Type**: ${deviation.type}
- **Rule**: ${handler.rule}
- **Action**: ${handler.action}
- **Matched**: "${deviation.matched}"
- **Suggestion**: ${handler.suggestion}
`;

    // Append to Deviations section or create it
    if (content.includes('## Deviations')) {
      content = content.replace(
        /## Deviations\n/,
        `## Deviations\n${deviationEntry}`
      );
    } else {
      content += `\n## Deviations\n${deviationEntry}`;
    }

    fs.writeFileSync(STATE_FILE, content);
  } catch (error) {
    // Silent fail - logging is not critical
  }
}

/**
 * Log deviation to lessons.md
 */
function logToLessons(deviation, handler) {
  try {
    if (!fs.existsSync(LESSONS_FILE)) {
      return; // No lessons file, skip logging
    }

    let content = fs.readFileSync(LESSONS_FILE, 'utf8');

    const today = new Date().toISOString().split('T')[0];
    const deviationEntry = `
### ${today} - GSD偏差处理
- **类型**: ${deviation.type}
- **规则**: ${handler.rule}
- **动作**: ${handler.action}
- **触发**: "${deviation.matched}"
- **建议**: ${handler.suggestion}
`;

    // Append to file
    content += deviationEntry;
    fs.writeFileSync(LESSONS_FILE, content);
  } catch (error) {
    // Silent fail - logging is not critical
  }
}

/**
 * Main hook handler
 */
module.exports = {
  name: 'gsd-deviation-handler',

  // Hook triggers
  triggers: ['postToolUse'],

  // Main handler
  handler: async (context) => {
    const { toolName, result, config } = context;

    // Skip non-relevant tools
    const relevantTools = ['Bash', 'Write', 'Edit', 'Task', 'Agent'];
    if (!relevantTools.includes(toolName)) {
      return { action: 'continue' };
    }

    // Detect deviation
    const deviation = detectDeviation(result);

    if (!deviation) {
      return { action: 'continue' };
    }

    // Handle deviation
    const handler = handleDeviation(deviation, context);

    if (!handler) {
      return { action: 'continue' };
    }

    // Log deviation
    logToState(deviation, handler);
    logToLessons(deviation, handler);

    // Return appropriate action
    console.log(`\n${handler.message}`);
    console.log(handler.suggestion);

    if (handler.requiresConfirmation) {
      return {
        action: 'pause',
        message: handler.message,
        suggestion: handler.suggestion,
        deviation: deviation
      };
    }

    return {
      action: 'continue',
      message: handler.message,
      log: handler.logEntry
    };
  },

  // Export utilities for testing
  utils: {
    detectDeviation,
    handleDeviation,
    DEVIATION_PATTERNS
  }
};

// CLI entry point for testing
if (require.main === module) {
  const args = process.argv.slice(2);

  if (args[0] === 'test') {
    console.log('Testing GSD Deviation Handler...\n');

    const testCases = [
      'Error: Cannot read property "x" of undefined',
      'TypeError: foo is not a function',
      'TODO: Implement this feature',
      'FIXME: This is a hack',
      'Blocked: Waiting for API response',
      'Refactor: Need to restructure the module',
    ];

    testCases.forEach((testCase, i) => {
      const deviation = detectDeviation(testCase);
      if (deviation) {
        const handler = handleDeviation(deviation, { toolName: 'Bash' });
        console.log(`Test ${i + 1}: "${testCase}"`);
        console.log(`  Type: ${deviation.type}`);
        console.log(`  Rule: ${handler.rule}`);
        console.log(`  Action: ${handler.action}\n`);
      }
    });
  } else if (args[0] === 'help') {
    console.log(`
GSD Deviation Handler Hook

Usage:
  node gsd-deviation-handler.js test    Run test cases
  node gsd-deviation-handler.js help    Show this help

Deviation Rules:
  Rule 1: Auto-fix bugs
  Rule 2: Auto-add missing functionality
  Rule 3: Auto-fix blocking issues
  Rule 4: Ask about architectural changes

Configuration:
  Add to hooks.json:
  {
    "postToolUse": ["./gsd-deviation-handler.js"]
  }
`);
  }
}