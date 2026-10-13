#!/usr/bin/env node
/**
 * Meta Review Trigger - 元审查触发器
 * 天龙引擎 V8.14 Meta治理层
 *
 * 核心理念：审查审查者，验证验证者，治理治理者
 * 递归深度限制：≤3层（避免无限递归）
 */

const fs = require('fs');
const path = require('path');

// ============== 配置 ==============

const CONFIG = {
  // 最大递归深度
  MAX_META_DEPTH: 3,

  // 触发条件权重
  TRIGGER_WEIGHTS: {
    reviewer_blind_spot: { weight: 0.9, priority: 'HIGH' },
    high_risk_decision: { weight: 0.85, priority: 'HIGH' },
    user_dissatisfaction: { weight: 0.6, priority: 'MEDIUM' },
    governance_incomplete: { weight: 0.7, priority: 'MEDIUM' },
    triple_failure: { weight: 0.95, priority: 'HIGH' }
  },

  // 需要元审查的Agent列表
  REVIEWABLE_AGENTS: ['06code-reviewer', '04validator', '05security-reviewer', '02architect'],

  // 高风险决策阈值
  HIGH_RISK_THRESHOLD: {
    cost: 1000,      // 成本 > $1000
    duration: 14,    // 工期 > 2周
    files: 10        // 文件数 > 10
  },

  // 元经验存储路径
  META_LESSONS_PATH: path.join(process.env.HOME || process.env.USERPROFILE, '.claude', 'memory', 'meta-lessons.yaml')
};

// ============== 状态管理 ==============

let metaReviewState = {
  currentDepth: 0,
  reviewHistory: [],
  pendingReviews: [],
  metaLessons: []
};

// ============== 核心函数 ==============

/**
 * 主入口：检测是否需要触发元审查
 */
function checkMetaReviewNeeded(context) {
  const { toolName, toolResult, previousMessages } = context;

  // 1. 检查递归深度
  if (metaReviewState.currentDepth >= CONFIG.MAX_META_DEPTH) {
    return {
      needed: false,
      reason: 'max_depth_reached',
      message: `已达到最大递归深度 ${CONFIG.MAX_META_DEPTH}，停止元审查`
    };
  }

  // 2. 检查触发条件
  const triggers = detectTriggers(context);

  if (triggers.length === 0) {
    return { needed: false, reason: 'no_triggers' };
  }

  // 3. 计算触发权重
  const totalWeight = triggers.reduce((sum, t) => sum + CONFIG.TRIGGER_WEIGHTS[t.type]?.weight || 0, 0);

  // 4. 决定是否触发
  if (totalWeight >= 0.6) {
    return {
      needed: true,
      triggers,
      totalWeight,
      priority: getPriority(triggers),
      recommendation: generateRecommendation(triggers)
    };
  }

  return { needed: false, reason: 'weight_below_threshold', totalWeight };
}

/**
 * 检测触发条件
 */
function detectTriggers(context) {
  const triggers = [];
  const { toolName, toolResult, previousMessages } = context;

  // 1. 审查盲区检测
  if (detectReviewerBlindSpot(toolResult)) {
    triggers.push({
      type: 'reviewer_blind_spot',
      evidence: extractBlindSpotEvidence(toolResult),
      severity: 'HIGH'
    });
  }

  // 2. 高风险决策检测
  if (detectHighRiskDecision(context)) {
    triggers.push({
      type: 'high_risk_decision',
      evidence: extractHighRiskEvidence(context),
      severity: 'HIGH'
    });
  }

  // 3. 用户不满检测
  if (detectUserDissatisfaction(previousMessages)) {
    triggers.push({
      type: 'user_dissatisfaction',
      evidence: 'User expressed dissatisfaction with review result',
      severity: 'MEDIUM'
    });
  }

  // 4. 治理不完备检测
  if (detectGovernanceIncomplete(toolResult)) {
    triggers.push({
      type: 'governance_incomplete',
      evidence: 'Missing governance steps detected',
      severity: 'MEDIUM'
    });
  }

  // 5. 三次失败检测
  if (detectTripleFailure(previousMessages)) {
    triggers.push({
      type: 'triple_failure',
      evidence: 'Same issue failed 3 times',
      severity: 'HIGH'
    });
  }

  return triggers;
}

/**
 * 审查盲区检测
 */
function detectReviewerBlindSpot(toolResult) {
  if (!toolResult || typeof toolResult !== 'string') return false;

  const blindSpotIndicators = [
    /遗漏|missed|overlooked/i,
    /未覆盖|not covered/i,
    /边界条件|edge case/i,
    /异常路径|error path/i,
    /未考虑|not considered/i
  ];

  // 检查是否遗漏了关键检查
  const hasBlindSpot = blindSpotIndicators.some(pattern => pattern.test(toolResult));

  // 检查是否声明了边界条件检查
  const hasBoundaryCheck = /边界|boundary|edge case/i.test(toolResult);

  return hasBlindSpot || !hasBoundaryCheck;
}

/**
 * 高风险决策检测
 */
function detectHighRiskDecision(context) {
  const { toolResult } = context;

  // 检查决策规模
  if (toolResult) {
    // 文件数检查
    const fileCount = (toolResult.match(/file|文件/gi) || []).length;
    if (fileCount > CONFIG.HIGH_RISK_THRESHOLD.files) return true;

    // 成本检查
    const costMatch = toolResult.match(/\$(\d+)/);
    if (costMatch && parseInt(costMatch[1]) > CONFIG.HIGH_RISK_THRESHOLD.cost) return true;

    // 工期检查
    const durationMatch = toolResult.match(/(\d+)\s*(周|week|天|day)/i);
    if (durationMatch && parseInt(durationMatch[1]) > CONFIG.HIGH_RISK_THRESHOLD.duration) return true;
  }

  return false;
}

/**
 * 用户不满检测
 */
function detectUserDissatisfaction(messages) {
  if (!messages || messages.length === 0) return false;

  const lastUserMessage = [...messages].reverse().find(m => m.role === 'user');
  if (!lastUserMessage) return false;

  const dissatisfactionIndicators = [
    /不满意|not satisfied|不满意|不满意/,
    /不对|wrong|错误|incorrect/,
    /漏了|missed|遗漏/,
    /重新审查|review again|re-review/,
    /太草率|too hasty|不够严谨/
  ];

  return dissatisfactionIndicators.some(pattern => pattern.test(lastUserMessage.content || ''));
}

/**
 * 治理不完备检测
 */
function detectGovernanceIncomplete(toolResult) {
  if (!toolResult || typeof toolResult !== 'string') return false;

  // 检查治理链路完整性
  const governanceSteps = ['review', 'verify', 'security', 'rollback'];
  const missingSteps = governanceSteps.filter(step =>
    !toolResult.toLowerCase().includes(step)
  );

  return missingSteps.length > 2;
}

/**
 * 三次失败检测
 */
function detectTripleFailure(messages) {
  if (!messages || messages.length < 6) return false;

  // 统计最近的错误模式
  const recentErrors = messages.filter(m =>
    m.role === 'assistant' &&
    /error|fail|失败|错误/i.test(m.content || '')
  );

  return recentErrors.length >= 3;
}

/**
 * 提取盲区证据
 */
function extractBlindSpotEvidence(toolResult) {
  if (!toolResult) return 'No evidence available';

  const blindSpotPatterns = [
    /遗漏[：:]\s*(.+)/i,
    /未覆盖[：:]\s*(.+)/i,
    /边界条件[：:]\s*(.+)/i
  ];

  for (const pattern of blindSpotPatterns) {
    const match = toolResult.match(pattern);
    if (match) return match[1];
  }

  return 'Potential blind spots in review coverage';
}

/**
 * 提取高风险证据
 */
function extractHighRiskEvidence(context) {
  const evidences = [];

  if (context.fileCount > CONFIG.HIGH_RISK_THRESHOLD.files) {
    evidences.push(`Files: ${context.fileCount}`);
  }

  if (context.cost > CONFIG.HIGH_RISK_THRESHOLD.cost) {
    evidences.push(`Cost: $${context.cost}`);
  }

  if (context.duration > CONFIG.HIGH_RISK_THRESHOLD.duration) {
    evidences.push(`Duration: ${context.duration} days`);
  }

  return evidences.join(', ') || 'High risk decision detected';
}

/**
 * 获取优先级
 */
function getPriority(triggers) {
  const priorities = triggers.map(t => CONFIG.TRIGGER_WEIGHTS[t.type]?.priority || 'LOW');
  if (priorities.includes('HIGH')) return 'HIGH';
  if (priorities.includes('MEDIUM')) return 'MEDIUM';
  return 'LOW';
}

/**
 * 生成建议
 */
function generateRecommendation(triggers) {
  const recommendations = {
    reviewer_blind_spot: '触发09-03元审查师对06审查师进行元审查',
    high_risk_decision: '触发双重确认机制，建议02架构师+09-03元审查师联合评审',
    user_dissatisfaction: '重新启动审查流程，09-03元审查师监督',
    governance_incomplete: '补全治理链路，确保review-verify-security-rollback完整',
    triple_failure: '停止当前方案，触发架构级反思，建议09-03元审查师深度介入'
  };

  const uniqueRecommendations = [...new Set(
    triggers.map(t => recommendations[t.type] || '启动元审查流程')
  )];

  return uniqueRecommendations.join('\n');
}

// ============== 元审查执行 ==============

/**
 * 执行元审查
 */
function executeMetaReview(target, depth = 1) {
  // 深度检查
  if (depth > CONFIG.MAX_META_DEPTH) {
    return {
      status: 'depth_exceeded',
      message: `递归深度 ${depth} 超过最大值 ${CONFIG.MAX_META_DEPTH}`,
      recommendation: '人工介入或简化治理链路'
    };
  }

  // 更新状态
  metaReviewState.currentDepth = depth;

  // 生成元审查报告
  const report = generateMetaReviewReport(target, depth);

  // 记录历史
  metaReviewState.reviewHistory.push({
    timestamp: new Date().toISOString(),
    target,
    depth,
    report
  });

  // 提取元经验
  extractMetaLessons(report);

  return report;
}

/**
 * 生成元审查报告
 */
function generateMetaReviewReport(target, depth) {
  return {
    header: {
      reportId: `meta-review-${Date.now()}`,
      timestamp: new Date().toISOString(),
      target,
      depth,
      maxDepth: CONFIG.MAX_META_DEPTH
    },
    sections: {
      blindSpots: {
        codeCoverage: '待填充：代码路径覆盖分析',
        testCoverage: '待填充：测试覆盖分析',
        governanceCoverage: '待填充：治理链路完整性分析'
      },
      findings: [],
      metaLessons: [],
      recursiveCheck: {
        depthWithinLimit: depth < CONFIG.MAX_META_DEPTH,
        needsDeeperReview: false,
        recommendation: depth < CONFIG.MAX_META_DEPTH ? '可以进行更深层元审查' : '已达最大深度'
      }
    },
    signature: {
      reviewer: '09-03-meta-reviewer',
      version: 'V8.14',
      depth
    }
  };
}

/**
 * 提取元经验
 */
function extractMetaLessons(report) {
  // 简化版元经验提取
  const lesson = {
    timestamp: report.header.timestamp,
    pattern: '元审查发现',
    depth: report.header.depth,
    target: report.header.target
  };

  metaReviewState.metaLessons.push(lesson);

  // 持久化
  persistMetaLessons();
}

/**
 * 持久化元经验
 */
function persistMetaLessons() {
  try {
    const dir = path.dirname(CONFIG.META_LESSONS_PATH);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    const yamlContent = `# Meta Lessons - 元审查经验库
# 天龙引擎 V8.14
# 最后更新: ${new Date().toISOString()}

meta_lessons:
${metaReviewState.metaLessons.map((l, i) => `  - id: meta-lesson-${i + 1}
    timestamp: ${l.timestamp}
    pattern: "${l.pattern}"
    depth: ${l.depth}
    target: ${l.target}`).join('\n')}
`;

    fs.writeFileSync(CONFIG.META_LESSONS_PATH, yamlContent, 'utf8');
  } catch (error) {
    // 静默失败，不影响主流程
  }
}

// ============== Hook 接口 ==============

/**
 * Hook 入口函数
 * 用于 hooks.json 配置
 */
function metaReviewHook(context) {
  const result = checkMetaReviewNeeded(context);

  if (result.needed) {
    return {
      action: 'trigger_meta_review',
      priority: result.priority,
      triggers: result.triggers,
      recommendation: result.recommendation,
      command: '/meta-review'
    };
  }

  return {
    action: 'no_action',
    reason: result.reason
  };
}

// ============== 导出 ==============

module.exports = {
  checkMetaReviewNeeded,
  executeMetaReview,
  metaReviewHook,
  CONFIG,
  metaReviewState
};

// ============== CLI 测试 ==============

if (require.main === module) {
  console.log('='.repeat(60));
  console.log('天龙引擎 V8.14 - Meta Review Trigger');
  console.log('='.repeat(60));

  // 测试场景
  const testContext = {
    toolName: 'Read',
    toolResult: '代码审查完成，未发现明显问题。',
    previousMessages: [
      { role: 'user', content: '请审查这段代码' },
      { role: 'assistant', content: '审查完成' }
    ]
  };

  const result = checkMetaReviewNeeded(testContext);
  console.log('\n测试结果:');
  console.log(JSON.stringify(result, null, 2));
}