
/**
 * 批判性思维协作层 Hook
 * 天龙引擎 V7.4 Layer 3 - 协作层
 *
 * 功能：
 * - PostToolUse: 检测重大决策，自动触发魔鬼代言人
 * - 管理双线协作（主线 + 质疑线）
 * - 记录质疑-回应-修正过程
 *
 * @version 1.0.0
 * @date 2026-02-28
 */

const fs = require('fs');
const path = require('path');

// 配置
const isInClaudeDir = process.cwd().endsWith('.claude');
const basePath = isInClaudeDir ? process.cwd() : path.join(process.cwd(), '.claude');

const CONFIG = {
  AGENTS_DIR: path.join(basePath, 'agents'),
  COLLABORATION_LOG: path.join(basePath, 'logs', 'collaboration.log'),
  DECISIONS_DIR: path.join(basePath, 'memory', 'critical', 'decisions')
};

// 触发条件
const TRIGGER_CONDITIONS = {
  architectureDecision: {
    patterns: [
      /架构决策/i,
      /技术选型/i,
      /系统设计/i,
      /microservice/i,
      /monolith/i
    ],
    agent: '02-architect',
    requireDevilsAdvocate: true
  },
  bestPractice: {
    patterns: [
      /最佳实践/i,
      /best practice/i,
      /standard/i,
      /pattern/i
    ],
    agent: 'any',
    requireDevilsAdvocate: true
  },
  highImpact: {
    patterns: [],
    agent: 'any',
    requireDevilsAdvocate: true,
    costThreshold: 1000, // $1000
    durationThreshold: 120960000 // 2 weeks (ms)
  },
  noCounterexample: {
    patterns: [],
    agent: 'any',
    requireDevilsAdvocate: false,
    checkReport: true // 检查是否有反例维度
  }
};

/**
 * 检测是否需要触发魔鬼代言人
 */
function shouldTriggerDevilsAdvocate(toolResult, agentId) {
  const resultText = JSON.stringify(toolResult);

  // 检查架构决策
  if (TRIGGER_CONDITIONS.architectureDecision.patterns.some(p => p.test(resultText))) {
    if (TRIGGER_CONDITIONS.architectureDecision.agent === 'any' ||
        TRIGGER_CONDITIONS.architectureDecision.agent === agentId) {
      return {
        trigger: true,
        reason: 'architecture_decision',
        agent: agentId
      };
    }
  }

  // 检查最佳实践声明
  if (TRIGGER_CONDITIONS.bestPractice.patterns.some(p => p.test(resultText))) {
    return {
      trigger: true,
      reason: 'best_practice_claim',
      agent: agentId
    };
  }

  // TODO: 检查成本和时间（需要从其他渠道获取）

  // TODO: 检查批判性思维报告（需要与Layer 2集成）

  return {
    trigger: false
  };
}

/**
 * 生成魔鬼代言人触发提示
 */
function generateDevilsAdvocatePrompt(triggerInfo, toolResult) {
  let prompt = '';

  prompt += `\n## 🎭 魔鬼代言人触发\n\n`;
  prompt += `**触发原因**: ${getTriggerReasonText(triggerInfo.reason)}\n`;
  prompt += `**原Agent**: ${triggerInfo.agent}\n`;
  prompt += `**触发时间**: ${new Date().toISOString()}\n\n`;

  prompt += `### 📜 原决策摘要\n\n`;
  prompt += `[需要从原Agent输出中提取决策摘要]\n\n`;

  prompt += `### ⚠️ 魔鬼代言人任务\n\n`;
  prompt += `请使用 09-01魔鬼代言人Agent 质疑以上决策：\n\n`;
  prompt += `1. **质疑盲点**：场景/规模/团队/技术/业务盲点\n`;
  prompt += `2. **提供反例**：失败案例、反模式、历史教训\n`;
  prompt += `3. **设计实验**：可证伪的实验方案\n`;
  prompt += `4. **最终判断**：原决策是否成立\n\n`;

  prompt += `**调用方式**：\n`;
  prompt += `Task({ subagent_type: "09-01-devils-advocate", prompt: "[原决策内容]" })\n`;

  return prompt;
}

/**
 * 获取触发原因文本
 */
function getTriggerReasonText(reason) {
  const reasons = {
    'architecture_decision': '架构决策（02架构师输出）',
    'best_practice_claim': '最佳实践声明',
    'high_impact': '高影响决策（成本>$1000或工期>2周）',
    'no_counterexample': '分析报告缺少反例维度'
  };

  return reasons[reason] || reason;
}

/**
 * 记录协作事件
 */
function logCollaborationEvent(event) {
  const logDir = path.dirname(CONFIG.COLLABORATION_LOG);
  if (!fs.existsSync(logDir)) {
    fs.mkdirSync(logDir, { recursive: true });
  }

  const logEntry = {
    timestamp: new Date().toISOString(),
    ...event
  };

  const logLine = JSON.stringify(logEntry) + '\n';
  fs.appendFileSync(CONFIG.COLLABORATION_LOG, logLine);
}

/**
 * 检查Agent是否已回应质疑
 */
function hasAgentResponded(agentId, decisionId) {
  // TODO: 实现回应检查逻辑
  // 需要与决策存储系统集成
  return false;
}

/**
 * 生成协作状态报告
 */
function generateCollaborationStatusReport() {
  let report = '';

  report += `\n## 🔄 双线协作状态报告\n\n`;
  report += `**生成时间**: ${new Date().toISOString()}\n\n`;

  // TODO: 从日志中读取协作状态
  report += `### 📊 协作统计\n\n`;
  report += `- 待回应的质疑: 0\n`;
  report += `- 已回应的质疑: 0\n`;
  report += `- 修正的决策: 0\n`;
  report += `- 推翻的决策: 0\n\n`;

  return report;
}

/**
 * 主函数
 */
function main() {
  const args = process.argv.slice(2);
  const mode = args[0] || 'check';

  if (mode === 'check') {
    const agentId = args[1] || 'unknown';
    const toolResultJson = args[2] || '{}';

    try {
      const toolResult = JSON.parse(toolResultJson);
      const triggerInfo = shouldTriggerDevilsAdvocate(toolResult, agentId);

      if (triggerInfo.trigger) {
        const prompt = generateDevilsAdvocatePrompt(triggerInfo, toolResult);
        console.log(prompt);

        // 记录触发事件
        logCollaborationEvent({
          type: 'devils_advocate_triggered',
          agentId,
          reason: triggerInfo.reason,
          timestamp: new Date().toISOString()
        });

        process.exit(1); // 返回非0退出码表示需要触发魔鬼代言人
      } else {
        console.log('✅ 不需要触发魔鬼代言人');
        process.exit(0);
      }
    } catch (error) {
      console.error(`Error: ${error.message}`);
      process.exit(1);
    }
  } else if (mode === 'status') {
    const report = generateCollaborationStatusReport();
    console.log(report);
    process.exit(0);
  } else {
    console.error('Usage: node critical-thinking-collaboration.js [check|status]');
    process.exit(1);
  }
}

// 导出函数
module.exports = {
  shouldTriggerDevilsAdvocate,
  generateDevilsAdvocatePrompt,
  logCollaborationEvent,
  TRIGGER_CONDITIONS
};

// 如果直接运行
if (require.main === module) {
  main();
}
