
/**
 * 批判性思维Agent检查器 Hook
 * 天龙引擎 V7.4 Layer 2 - Agent层
 *
 * 功能：
 * - PostToolUse: 自动检查Agent输出是否符合批判性思维标准
 * - 评分6大批判性思维维度
 * - 生成改进建议
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
  CRITICAL_MEMORY_DIR: path.join(basePath, 'memory', 'critical'),
  MIN_SCORE_THRESHOLD: 0.6,
  LOG_FILE: path.join(basePath, 'logs', 'critical-thinking-checks.log')
};

// 批判性思维6大维度
const DIMENSIONS = {
  QUESTION_ASSUMPTIONS: {
    name: '质疑假设',
    weight: 0.2,
    patterns: [
      /⚠️\s*假设/i,
      /假设质疑/i,
      /失效条件/i,
      /验证方法/i
    ]
  },
  VERIFY_EVIDENCE: {
    name: '验证证据',
    weight: 0.15,
    patterns: [
      /📊\s*证据/i,
      /证据验证/i,
      /置信度/i,
      /来源[:：]/i
    ]
  },
  CHECK_LOGIC: {
    name: '检查逻辑',
    weight: 0.15,
    patterns: [
      /🔬\s*逻辑/i,
      /逻辑检查/i,
      /推理/i,
      /因果/i
    ]
  },
  COUNTEREXAMPLES: {
    name: '考虑反例',
    weight: 0.15,
    patterns: [
      /🔄\s*反例/i,
      /反例分析/i,
      /失败案例/i,
      /反模式/i
    ]
  },
  SELF_REFLECTION: {
    name: '自我反思',
    weight: 0.1,
    patterns: [
      /🤔\s*自我/i,
      /自我反思/i,
      /认知偏见/i,
      /局限性/i
    ]
  },
  FALSIFIABILITY: {
    name: '可证伪性',
    weight: 0.25,
    patterns: [
      /🔬\s*可证伪/i,
      /证伪方法/i,
      /测试标准/i,
      /什么情况下/i
    ]
  }
};

/**
 * 计算批判性思维得分
 */
function calculateCriticalThinkingScore(text) {
  const scores = {};
  let totalScore = 0;
  let totalWeight = 0;

  for (const [key, dimension] of Object.entries(DIMENSIONS)) {
    let matchCount = 0;
    for (const pattern of dimension.patterns) {
      const matches = text.match(pattern);
      if (matches) {
        matchCount += matches.length;
      }
    }

    // 归一化得分（0-1）
    const score = Math.min(matchCount / 2, 1);
    scores[key] = {
      name: dimension.name,
      score: score,
      weight: dimension.weight,
      weightedScore: score * dimension.weight
    };

    totalScore += score * dimension.weight;
    totalWeight += dimension.weight;
  }

  // 最终得分（0-1）
  const finalScore = totalWeight > 0 ? totalScore / totalWeight : 0;

  return {
    finalScore,
    scores,
    level: getScoreLevel(finalScore)
  };
}

/**
 * 获取得分等级
 */
function getScoreLevel(score) {
  if (score >= 0.9) return { level: '优秀', badge: '🌟', color: 'green' };
  if (score >= 0.75) return { level: '良好', badge: '✅', color: 'blue' };
  if (score >= 0.6) return { level: '及格', badge: '⚠️', color: 'yellow' };
  return { level: '不及格', badge: '❌', color: 'red' };
}

/**
 * 生成批判性思维报告
 */
function generateCriticalThinkingReport(text, agentId) {
  const result = calculateCriticalThinkingScore(text);
  const { finalScore, scores, level } = result;

  let report = '';
  report += `\n## 🧠 批判性思维检查报告\n\n`;
  report += `**Agent**: ${agentId}\n`;
  report += `**得分**: ${finalScore.toFixed(2)} / 1.00\n`;
  report += `**等级**: ${level.badge} ${level.level}\n`;
  report += `**检查时间**: ${new Date().toISOString()}\n\n`;

  report += `### 📊 各维度得分\n\n`;

  for (const [key, score] of Object.entries(scores)) {
    const level = getScoreLevel(score.score);
    report += `- **${score.name}**: ${(score.score * 100).toFixed(0)}% `;
    report += `(权重 ${(score.weight * 100).toFixed(0)}%) `;
    report += `${level.badge}\n`;
  }

  report += `\n### 💡 改进建议\n\n`;

  for (const [key, score] of Object.entries(scores)) {
    if (score.score < 0.5) {
      report += `#### ⚠️ ${score.name} (得分${(score.score * 100).toFixed(0)}%)\n`;
      report += `${getImprovementSuggestion(key)}\n\n`;
    }
  }

  if (finalScore < CONFIG.MIN_SCORE_THRESHOLD) {
    report += `### 🚨 批判性思维不足\n\n`;
    report += `当前得分 (${finalScore.toFixed(2)}) 低于最低标准 (${CONFIG.MIN_SCORE_THRESHOLD})。\n\n`;
    report += `**建议**：\n`;
    report += `1. 检查Agent配置文件是否包含V7.4批判性思维维度\n`;
    report += `2. 确保输出包含6大批判性思维维度\n`;
    report += `3. 参考Agent V7.4模板：agents/*-v74.md\n\n`;
  }

  return report;
}

/**
 * 获取改进建议
 */
function getImprovementSuggestion(dimension) {
  const suggestions = {
    QUESTION_ASSUMPTIONS: `- 隐含假设未明确列出
- 建议格式："⚠️ 假设：[X]，验证方法：[Y]"
- 询问：这个方案基于什么假设？什么情况下失效？`,

    VERIFY_EVIDENCE: `- 证据来源未明确标注
- 建议格式："📊 证据：[X]，置信度：[Y/1.0]"
- 询问：结论有什么证据支持？证据质量如何？`,

    CHECK_LOGIC: `- 推理逻辑未经过验证
- 建议格式："🔬 逻辑检查：[推理]，验证：[...]"
- 询问：推理是否严密？有逻辑漏洞吗？`,

    COUNTEREXAMPLES: `- 未考虑反例或失败案例
- 建议格式："🔄 反例：[X]，避免方法：[Y]"
- 询问：什么情况下这个方案不成立？有失败案例吗？`,

    SELF_REFLECTION: `- 未进行自我反思或偏见检查
- 建议格式："🤔 自我反思：[认知偏见/局限性]"
- 询问：我的判断有什么偏见？有什么局限？`,

    FALSIFIABILITY: `- **核心缺失**：无可证伪性声明
- 建议格式："🔬 证伪方法：[如何证明我是错的]"
- 询问：如何证明这个决策是错的？什么情况下被推翻？`
  };

  return suggestions[dimension] || '- 请参考批判性思维6大维度';
}

/**
 * 记录检查结果
 */
function logCheck(agentId, score, level) {
  const logDir = path.dirname(CONFIG.LOG_FILE);
  if (!fs.existsSync(logDir)) {
    fs.mkdirSync(logDir, { recursive: true });
  }

  const logEntry = {
    timestamp: new Date().toISOString(),
    agentId,
    score,
    level: level.level
  };

  const logLine = JSON.stringify(logEntry) + '\n';
  fs.appendFileSync(CONFIG.LOG_FILE, logLine);
}

/**
 * 主函数
 */
function main() {
  const args = process.argv.slice(2);
  const mode = args[0] || 'check';

  if (mode === 'check') {
    const agentId = args[1] || 'unknown';
    const text = args[2] || '';

    if (!text) {
      console.error('Usage: node critical-thinking-agent-checker.js check <agent-id> <text>');
      process.exit(1);
    }

    const report = generateCriticalThinkingReport(text, agentId);
    console.log(report);

    const result = calculateCriticalThinkingScore(text);
    logCheck(agentId, result.finalScore, result.level);

    // 返回退出码
    const exitCode = result.finalScore >= CONFIG.MIN_SCORE_THRESHOLD ? 0 : 1;
    process.exit(exitCode);
  } else {
    console.error('Usage: node critical-thinking-agent-checker.js [check]');
    process.exit(1);
  }
}

// 导出函数
module.exports = {
  calculateCriticalThinkingScore,
  generateCriticalThinkingReport,
  DIMENSIONS
};

// 如果直接运行
if (require.main === module) {
  main();
}
