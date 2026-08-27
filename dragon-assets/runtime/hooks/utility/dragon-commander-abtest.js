
/**
 * 🧪 A/B测试系统
 * 用于自动优化提示词和响应格式
 */

class ABTestSystem {
  constructor(dataDir = 'c:/Users/li/.claude/data/commander') {
    this.dataDir = dataDir;
    this.testsFile = `${dataDir}/abtests.json`;
    this.resultsFile = `${dataDir}/abtest-results.json`;

    // 加载测试数据
    this.activeTests = this.loadTests();
    this.testResults = this.loadResults();
    this.winnerVariants = new Map();
  }

  // 加载测试配置
  loadTests() {
    const fs = require('fs');
    try {
      if (fs.existsSync(this.testsFile)) {
        const data = fs.readFileSync(this.testsFile, 'utf8');
        return JSON.parse(data);
      }
    } catch (error) {
      console.error('加载测试数据失败:', error.message);
    }
    return this.initializeDefaultTests();
  }

  // 加载测试结果
  loadResults() {
    const fs = require('fs');
    try {
      if (fs.existsSync(this.resultsFile)) {
        const data = fs.readFileSync(this.resultsFile, 'utf8');
        return JSON.parse(data);
      }
    } catch (error) {
      console.error('加载结果数据失败:', error.message);
    }
    return {};
  }

  // 保存数据
  saveData() {
    const fs = require('fs');
    try {
      fs.writeFileSync(this.testsFile, JSON.stringify(this.activeTests, null, 2));
      fs.writeFileSync(this.resultsFile, JSON.stringify(this.testResults, null, 2));
    } catch (error) {
      console.error('保存测试数据失败:', error.message);
    }
  }

  // 初始化默认测试
  initializeDefaultTests() {
    return {
      'greeting-style-001': {
        testId: 'greeting-style-001',
        name: '开场白风格测试',
        description: '测试不同开场白对用户接受率的影响',
        variants: [
          {
            id: 'casual',
            name: '轻松活泼',
            template: '嘿！又见面了 👋'
          },
          {
            id: 'professional',
            name: '专业正式',
            template: '您好！让我来分析您的需求'
          },
          {
            id: 'direct',
            name: '直接高效',
            template: '来啦！'
          }
        ],
        trafficSplit: [0.33, 0.33, 0.34],
        metrics: ['acceptance_rate', 'response_time'],
        startTime: new Date().toISOString(),
        status: 'running',
        sampleSize: 100
      },
      'core-insight-format-001': {
        testId: 'core-insight-format-001',
        name: '核心洞察格式测试',
        description: '测试不同核心洞察格式对理解时间的影响',
        variants: [
          {
            id: 'single-sentence',
            name: '单句话',
            template: '用 **{agent}** 直接搞定（置信度{confidence}%）'
          },
          {
            id: 'structured',
            name: '结构化',
            template: '**推荐方案**: {agent}\n**置信度**: {confidence}%'
          }
        ],
        trafficSplit: [0.5, 0.5],
        metrics: ['understanding_time', 'satisfaction_score'],
        startTime: new Date().toISOString(),
        status: 'running',
        sampleSize: 100
      },
      'call-to-action-intensity-001': {
        testId: 'call-to-action-intensity-001',
        name: '行动号召强度测试',
        description: '测试不同强度的行动号召对转化率的影响',
        variants: [
          {
            id: 'soft',
            name: '温和建议',
            template: '直接输入 "开始" 我就帮你调用代理？'
          },
          {
            id: 'direct',
            name: '直接建议',
            template: '要我现在就执行吗？回复 "是" 立即开始'
          }
        ],
        trafficSplit: [0.5, 0.5],
        metrics: ['conversion_rate', 'response_time'],
        startTime: new Date().toISOString(),
        status: 'running',
        sampleSize: 100
      }
    };
  }

  // 一致性哈希（用于分配用户到测试组）
  consistentHash(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32bit integer
    }
    return Math.abs(hash);
  }

  // 分配用户到测试组
  assignUserToVariant(testId, userId) {
    const test = this.activeTests[testId];
    if (!test) return null;

    // 基于用户ID的一致性哈希
    const hash = this.consistentHash(userId + testId);
    const bucket = hash % 100;

    let cumulative = 0;
    for (let i = 0; i < test.trafficSplit.length; i++) {
      cumulative += test.trafficSplit[i] * 100;
      if (bucket < cumulative) {
        return test.variants[i];
      }
    }

    return test.variants[0];
  }

  // 获取测试的模板
  getTestTemplate(testId, userId) {
    const variant = this.assignUserToVariant(testId, userId);
    return variant ? variant.template : null;
  }

  // 记录测试指标
  trackMetric(testId, variantId, metric, value) {
    if (!this.testResults[testId]) {
      this.testResults[testId] = {};
    }

    if (!this.testResults[testId][variantId]) {
      this.testResults[testId][variantId] = {
        metrics: {},
        sampleCount: 0
      };
    }

    const variantResult = this.testResults[testId][variantId];

    if (!variantResult.metrics[metric]) {
      variantResult.metrics[metric] = { sum: 0, count: 0, avg: 0 };
    }

    const metricData = variantResult.metrics[metric];
    metricData.sum += value;
    metricData.count += 1;
    metricData.avg = metricData.sum / metricData.count;
    variantResult.sampleCount += 1;

    this.saveData();
  }

  // 记录用户接受建议
  trackAcceptance(testId, variantId, accepted) {
    this.trackMetric(testId, variantId, 'acceptance_rate', accepted ? 1 : 0);
  }

  // 记录响应时间
  trackResponseTime(testId, variantId, timeMs) {
    this.trackMetric(testId, variantId, 'response_time', timeMs);
  }

  // 记录理解时间
  trackUnderstandingTime(testId, variantId, timeMs) {
    this.trackMetric(testId, variantId, 'understanding_time', timeMs);
  }

  // 记录满意度评分
  trackSatisfaction(testId, variantId, score) {
    this.trackMetric(testId, variantId, 'satisfaction_score', score);
  }

  // 分析测试结果
  analyzeTest(testId) {
    const test = this.activeTests[testId];
    const results = this.testResults[testId];

    if (!test || !results) {
      return null;
    }

    const analysis = {
      testId,
      testName: test.name,
      variants: [],
      winner: null,
      confidence: 0,
      recommendation: ''
    };

    // 分析每个变体
    for (const variant of test.variants) {
      const variantResult = results[variant.id];
      if (!variantResult) continue;

      const variantAnalysis = {
        id: variant.id,
        name: variant.name,
        sampleCount: variantResult.sampleCount,
        metrics: {}
      };

      // 计算各指标
      for (const metric of test.metrics) {
        if (variantResult.metrics[metric]) {
          variantAnalysis.metrics[metric] = variantResult.metrics[metric].avg;
        }
      }

      analysis.variants.push(variantAnalysis);
    }

    // 判断获胜者
    if (analysis.variants.length >= 2) {
      // 简单判断：以第一个指标为主
      const primaryMetric = test.metrics[0];
      analysis.variants.sort((a, b) => {
        const aVal = a.metrics[primaryMetric] || 0;
        const bVal = b.metrics[primaryMetric] || 0;
        return bVal - aVal; // 降序
      });

      analysis.winner = analysis.variants[0];
      analysis.improvement = this.calculateImprovement(
        analysis.variants[0],
        analysis.variants[analysis.variants.length - 1],
        primaryMetric
      );
    }

    return analysis;
  }

  // 计算提升百分比
  calculateImprovement(winner, loser, metric) {
    const winnerVal = winner.metrics[metric] || 0;
    const loserVal = loser.metrics[metric] || 0;

    if (loserVal === 0) return 0;

    return ((winnerVal - loserVal) / loserVal * 100).toFixed(2) + '%';
  }

  // 生成测试报告
  generateReport() {
    const report = {
      timestamp: new Date().toISOString(),
      tests: []
    };

    for (const testId in this.activeTests) {
      const analysis = this.analyzeTest(testId);
      if (analysis) {
        report.tests.push(analysis);
      }
    }

    return report;
  }

  // 获取获胜变体
  getWinnerVariant(testId) {
    // 先检查是否有确定的获胜者
    if (this.winnerVariants.has(testId)) {
      return this.winnerVariants.get(testId);
    }

    // 分析当前数据
    const analysis = this.analyzeTest(testId);
    if (analysis && analysis.winner) {
      // 如果样本量足够，确定获胜者
      if (analysis.winner.sampleCount >= 50) {
        this.winnerVariants.set(testId, analysis.winner);
        return analysis.winner;
      }
    }

    // 否则返回null，继续测试
    return null;
  }
}

module.exports = ABTestSystem;
