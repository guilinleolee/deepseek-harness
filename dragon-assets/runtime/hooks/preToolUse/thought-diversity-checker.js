
/**
 * 思维多样性检查器 (Thought Diversity Checker)
 *
 * 功能：确保天龙团各Agent从不同思维角度分析问题，避免思维重叠
 * 原理：基于查理·芒格多元思维模型，检测Agent输出是否偏离其核心思维模型
 *
 * 触发时机：
 * - postToolUse: Agent完成任务后
 * - preResponse: Agent准备回复前
 *
 * @version 7.0
 * @date 2025-02-24
 */

// Agent核心思维模型映射
const THOUGHT_MODELS = {
  '00-analyst': {
    name: '数学思维',
    focus: ['量化', '概率', '统计', '数据'],
    avoid: ['感觉', '可能', '应该', '模糊'],
    checkKeywords: [
      '数据', '统计', '概率', '量化', '样本', '置信区间',
      '显著性', '相关性', '回归', '分布', 'A/B测试'
    ],
    outputFormat: 'quantitative'
  },

  '01-investigator': {
    name: '生物进化思维',
    focus: ['演化', '历史', '遗迹', '适应'],
    avoid: ['垃圾代码', '直接重写'],
    checkKeywords: [
      '演化', '历史', '遗迹', '适应', '选择压力', '技术债',
      '生态', '共生', '寄生', '灭绝', '化石'
    ],
    outputFormat: 'historical'
  },

  '02-architect': {
    name: '第一性原理思维',
    focus: ['本质', '约束', '第一性'],
    avoid: ['业界最佳实践', 'XXX公司这么做'],
    checkKeywords: [
      '第一性原理', '本质', '约束', '物理定律', '守恒',
      '临界点', '相变', '最简化', '剥离类比'
    ],
    outputFormat: 'analytical'
  },

  '03-builder': {
    name: '化学思维',
    focus: ['模块', '反应', '组合', '副作用'],
    avoid: ['强耦合', '全局状态'],
    checkKeywords: [
      '模块', '元素', '反应', '组合', '副作用', '催化',
      '边界条件', '污染', '隔离', '惰性', '活性'
    ],
    outputFormat: 'structural'
  },

  '04-validator': {
    name: '工程可靠性思维',
    focus: ['失效', '冗余', '边界', '最坏情况'],
    avoid: ['正常情况下', '应该没问题'],
    checkKeywords: [
      '失效', '故障', '冗余', '边界', 'FMEA', '最坏情况',
      '压测', 'MTBF', 'MTTR', '单点故障', '熔断'
    ],
    outputFormat: 'engineering'
  },

  '05-security-reviewer': {
    name: '法律风险思维',
    focus: ['威胁', '合规', '风险', '最坏情况'],
    avoid: ['太小不会被黑', '以后再说'],
    checkKeywords: [
      '威胁', '漏洞', '合规', 'GDPR', 'STRIDE', '纵深防御',
      '最坏情况', '风险', '供应链', '渗透测试'
    ],
    outputFormat: 'risk-assessment'
  },

  '06code-reviewer': {
    name: '认知科学思维',
    focus: ['可读性', '认知', '命名', '复杂度'],
    avoid: ['风格偏好', '我喜欢'],
    checkKeywords: [
      '认知', '可读性', '命名', '复杂度', '代码气味',
      'SOLID', '心理模型', '理解', '维护'
    ],
    outputFormat: 'readability'
  },

  '07-scribe': {
    name: '历史模式思维',
    focus: ['历史', '模式', '记录', '经验'],
    avoid: ['第一次出现', '以后写文档'],
    checkKeywords: [
      '历史', '模式', '决策', 'ADR', '经验卡', '记录',
      '文档', '复盘', '循环', '重复', '知识库'
    ],
    outputFormat: 'documentary'
  },

  '08-publisher': {
    name: 'DevOps流程思维',
    focus: ['发布', '自动化', 'CI/CD', '监控'],
    avoid: ['手动操作', '下班前发布'],
    checkKeywords: [
      '发布', 'CI/CD', '流水线', '自动化', '监控', '告警',
      '回滚', '金丝雀', '蓝绿', '部署', '版本'
    ],
    outputFormat: 'operational'
  },

  '10-01-prompt-architect': {
    name: '语言学思维',
    focus: ['语言', '认知', '提示词', '上下文'],
    avoid: ['越长越好', '复杂即好'],
    checkKeywords: [
      '提示词', '语言', '认知', '上下文', 'token', '语法',
      '示例', '思维链', 'Few-shot', '结构'
    ],
    outputFormat: 'linguistic'
  }
};

/**
 * 检测Agent输出是否符合其思维模型
 */
function checkThoughtDiversity(agentId, output) {
  const model = THOUGHT_MODELS[agentId];
  if (!model) {
    return null; // 未知Agent，不检查
  }

  const issues = [];
  const score = { passed: 0, total: 0 };

  // 1. 检查是否包含核心关键词
  score.total += 1;
  const hasKeyword = model.checkKeywords.some(kw =>
    output.toLowerCase().includes(kw.toLowerCase())
  );
  if (hasKeyword) {
    score.passed += 1;
  } else {
    issues.push({
      type: 'missing_keywords',
      message: `输出缺少${model.name}的关键词`,
      expected: model.focus.join('、'),
      suggestion: `应该包含${model.checkKeywords.slice(0, 3).join('、')}等关键词`
    });
  }

  // 2. 检查是否使用了避免的词汇
  score.total += 1;
  const hasAvoidWord = model.avoid.some(word =>
    output.toLowerCase().includes(word.toLowerCase())
  );
  if (!hasAvoidWord) {
    score.passed += 1;
  } else {
    issues.push({
      type: 'forbidden_words',
      message: `输出包含${model.name}应避免的词汇`,
      found: model.avoid.filter(w => output.toLowerCase().includes(w.toLowerCase())),
      suggestion: `避免使用：${model.avoid.join('、')}`
    });
  }

  // 3. 检查输出格式（简化版）
  score.total += 1;
  const hasStructure =
    output.includes('##') ||        // Markdown标题
    output.includes('|') ||          // 表格
    output.includes('```') ||        // 代码块
    output.includes('- ') ||         // 列表
    output.includes('1.');           // 编号

  if (hasStructure) {
    score.passed += 1;
  }

  return {
    model: model.name,
    score: score,
    compliance: score.passed / score.total,
    issues: issues,
    recommendation: issues.length > 0 ? '建议调整输出' : '思维模式符合'
  };
}

/**
 * 生成思维差异报告
 */
function generateDiversityReport(agentResults) {
  const report = {
    timestamp: new Date().toISOString(),
    agents: agentResults,
    summary: {
      totalAgents: agentResults.length,
      compliantAgents: agentResults.filter(r => r.compliance >= 0.67).length,
      avgCompliance: agentResults.reduce((sum, r) => sum + r.compliance, 0) / agentResults.length,
      diversityScore: calculateDiversityScore(agentResults)
    },
    recommendations: []
  };

  // 生成建议
  if (report.summary.avgCompliance < 0.7) {
    report.recommendations.push({
      priority: 'high',
      message: '整体思维符合度较低，建议回顾V7.0思维模型声明'
    });
  }

  if (report.summary.diversityScore < 0.6) {
    report.recommendations.push({
      priority: 'medium',
      message: '思维多样性不足，可能存在重叠，建议加强互补性'
    });
  }

  return report;
}

/**
 * 计算思维多样性分数
 */
function calculateDiversityScore(agentResults) {
  // 简化版：基于不同Agent使用的关键词集合的Jaccard距离
  const keywordSets = agentResults.map(r => {
    const model = THOUGHT_MODELS[r.agentId];
    return new Set(model.checkKeywords);
  });

  if (keywordSets.length < 2) return 1.0;

  let totalSimilarity = 0;
  let comparisons = 0;

  for (let i = 0; i < keywordSets.length; i++) {
    for (let j = i + 1; j < keywordSets.length; j++) {
      const intersection = new Set([...keywordSets[i]].filter(x => keywordSets[j].has(x)));
      const union = new Set([...keywordSets[i], ...keywordSets[j]]);
      const similarity = intersection.size / union.size; // Jaccard相似度
      totalSimilarity += similarity;
      comparisons++;
    }
  }

  const avgSimilarity = totalSimilarity / comparisons;
  return 1 - avgSimilarity; // 多样性 = 1 - 相似度
}

// ============ Hook接口 ============

/**
 * postToolUse Hook
 */
function postToolUseHandler(toolName, toolResult) {
  // 检测是否是Agent任务完成
  if (toolName === 'Task' && toolResult && toolResult.agentId) {
    const agentId = toolResult.agentId;
    const output = JSON.stringify(toolResult);

    const checkResult = checkThoughtDiversity(agentId, output);

    if (checkResult && checkResult.compliance < 0.67) {
      console.warn(`\n🧠 思维模式检查警告：${agentId}`);
      console.warn(`   核心思维：${checkResult.model}`);
      console.warn(`   符合度：${(checkResult.compliance * 100).toFixed(0)}%`);
      console.warn(`   问题：`);
      checkResult.issues.forEach(issue => {
        console.warn(`     - ${issue.message}`);
        console.warn(`       建议：${issue.suggestion}`);
      });
    }
  }

  return toolResult;
}

/**
 * preResponse Hook
 */
function preResponseHandler(responseContent) {
  // 检查当前对话上下文，提醒思维多样性
  // （简化实现，实际需要解析对话历史）

  return responseContent;
}

// 导出（如果需要作为模块使用）
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    THOUGHT_MODELS,
    checkThoughtDiversity,
    generateDiversityReport,
    postToolUseHandler,
    preResponseHandler
  };
}
