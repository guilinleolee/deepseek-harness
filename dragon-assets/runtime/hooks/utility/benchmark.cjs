/**
 * Token Optimizer 性能基准测试
 *
 * 测试各模块的性能和效果
 */

const fs = require('fs');
const path = require('path');

// 加载模块
const TokenEstimator = require('./token-estimator.cjs');
const ObsidianTruncatorModule = require('./obsidian-truncator.cjs');
const ToolCompressorModule = require('./tool-compressor.cjs');
const SessionCompactorModule = require('./session-compactor.cjs');
const PromptCacheManagerModule = require('./prompt-cache.cjs');
const ModelRouterModule = require('./model-router.cjs');
const ContextBudgetGovernorModule = require('./context-budget-governor.cjs');
const AuditLoggerModule = require('./token-audit.cjs');

// 获取类
const ObsidianTruncator = ObsidianTruncatorModule.ObsidianTruncator;
const ToolCompressor = ToolCompressorModule.ToolCompressor;
const SessionCompactor = SessionCompactorModule.SessionCompactor;
const PromptCacheManager = PromptCacheManagerModule.PromptCacheManager;
const ModelRouter = ModelRouterModule.ModelRouter;
const ContextBudgetGovernor = ContextBudgetGovernorModule.ContextBudgetGovernor;
const AuditLogger = AuditLoggerModule.AuditLogger;

// 加载集成钩子
const TokenOptimizerHook = require('./token-optimizer-hook.cjs');

// ============================================================
// 测试数据
// ============================================================

const TEST_DATA = {
  // 中文文本
  chinese: {
    short: '你好世界，这是一个简单的测试。',
    medium: '这是一段中等长度的中文文本，用于测试Token估算功能。'.repeat(10),
    long: '这是一段很长的中文文本。'.repeat(100),
    mixed: 'Hello你好，world世界。'.repeat(50),
  },

  // 英文文本
  english: {
    short: 'Hello world',
    medium: 'This is a medium length text for testing.'.repeat(10),
    long: 'The quick brown fox jumps over the lazy dog. '.repeat(100),
  },

  // 代码
  code: {
    js: `function hello() {
  console.log('Hello World');
  return true;
}`,
    python: `def hello():
    print("Hello World")
    return True`,
  },

  // 消息数组
  messages: Array(50).fill(null).map((_, i) => ({
    role: i % 2 === 0 ? 'user' : 'assistant',
    content: `这是第 ${i + 1} 条测试消息，内容用于验证会话压缩功能。`.repeat(5),
    timestamp: Date.now() - (50 - i) * 60000,
  })),

  // 工具输出
  toolOutput: {
    small: '成功：文件已创建',
    medium: '查询结果：\n' + '第1条结果\n'.repeat(50),
    large: '执行结果：\n' + '日志行 '.repeat(500) + '\n最终状态：完成',
  },
};

// ============================================================
// 基准测试
// ============================================================

class Benchmark {
  constructor() {
    this.results = [];
    this.startTime = Date.now();
  }

  start(name) {
    this.currentTest = name;
    this.currentStart = Date.now();
  }

  end(data = {}) {
    const duration = Date.now() - this.currentStart;
    this.results.push({
      name: this.currentTest,
      duration,
      ...data,
    });
    return duration;
  }

  summary() {
    const totalDuration = Date.now() - this.startTime;
    return {
      totalDuration,
      tests: this.results.length,
      results: this.results,
    };
  }
}

// ============================================================
// 测试套件
// ============================================================

async function runBenchmarks() {
  console.log('🧪 Token Optimizer 性能基准测试\n');
  console.log('=' .repeat(60));

  const benchmark = new Benchmark();

  // ========================================
  // 1. Token 估算性能
  // ========================================
  console.log('\n📊 1. Token 估算性能测试');

  // 短文本
  benchmark.start('估算-短中文(20字符)');
  for (let i = 0; i < 1000; i++) {
    TokenEstimator.estimate(TEST_DATA.chinese.short);
  }
  const t1 = benchmark.end({ text: '短中文', size: 20, ops: 1000 });

  // 中文本
  benchmark.start('估算-中文(500字符)');
  for (let i = 0; i < 1000; i++) {
    TokenEstimator.estimate(TEST_DATA.chinese.medium);
  }
  const t2 = benchmark.end({ text: '中文', size: 500, ops: 1000 });

  // 长文本
  benchmark.start('估算-中文(5000字符)');
  for (let i = 0; i < 100; i++) {
    TokenEstimator.estimate(TEST_DATA.chinese.long);
  }
  const t3 = benchmark.end({ text: '中文', size: 5000, ops: 100 });

  // 混合文本
  benchmark.start('估算-中英混合(2000字符)');
  for (let i = 0; i < 500; i++) {
    TokenEstimator.estimate(TEST_DATA.chinese.mixed);
  }
  const t4 = benchmark.end({ text: '混合', size: 2000, ops: 500 });

  console.log(`  短中文(20字符): ${(t1 / 1000).toFixed(2)} ms/次`);
  console.log(`  中文(500字符): ${(t2 / 1000).toFixed(2)} ms/次`);
  console.log(`  中文(5000字符): ${(t3 / 100).toFixed(2)} ms/次`);
  console.log(`  混合(2000字符): ${(t4 / 500).toFixed(2)} ms/次`);

  // ========================================
  // 2. 截断性能
  // ========================================
  console.log('\n📊 2. 截断性能测试');

  benchmark.start('截断-中文(5000→500)');
  for (let i = 0; i < 100; i++) {
    TokenEstimator.truncate(TEST_DATA.chinese.long, 500);
  }
  const t5 = benchmark.end({ input: 5000, output: 500, ops: 100 });

  benchmark.start('截断-英文(10000→1000)');
  for (let i = 0; i < 100; i++) {
    TokenEstimator.truncate(TEST_DATA.english.long, 1000);
  }
  const t6 = benchmark.end({ input: 10000, output: 1000, ops: 100 });

  console.log(`  中文(5000→500): ${(t5 / 100).toFixed(2)} ms/次`);
  console.log(`  英文(10000→1000): ${(t6 / 100).toFixed(2)} ms/次`);

  // ========================================
  // 3. Obsidian 截断效果
  // ========================================
  console.log('\n📊 3. Obsidian 截断效果测试');

  const memoryItems = Array(100).fill(null).map((_, i) => ({
    type: ['lesson', 'decision', 'concept'][i % 3],
    title: `记忆条目 ${i + 1}`,
    content: '这是记忆内容。'.repeat(50),
    created: new Date(Date.now() - i * 24 * 60 * 60 * 1000).toISOString(),
    confidence: 0.5 + Math.random() * 0.5,
  }));

  const truncator = new ObsidianTruncator({ maxTokens: 2000 });
  benchmark.start('Obsidian截断-100条→2K');
  const truncateResult = truncator.truncate(memoryItems);
  const t7 = benchmark.end({
    inputItems: 100,
    outputItems: truncateResult.truncated.length,
    savedTokens: truncateResult.stats.savedTokens,
  });

  console.log(`  100条→${truncateResult.truncated.length}条: ${t7.toFixed(2)} ms`);
  console.log(`  节省: ${truncateResult.stats.savedTokens} tokens`);
  console.log(`  保留率: ${((truncateResult.truncated.length / 100) * 100).toFixed(1)}%`);

  // ========================================
  // 4. 工具压缩效果
  // ========================================
  console.log('\n📊 4. 工具压缩效果测试');

  const compressor = new ToolCompressor();

  benchmark.start('压缩-大输出(20K→4K)');
  const largeOutput = '执行结果：\n' + '日志行 '.repeat(5000) + '\n完成';
  const compressResult = compressor.compress(largeOutput, 'truncate');
  const t8 = benchmark.end({
    originalSize: largeOutput.length,
    compressedSize: compressResult.provider.content.length,
  });

  console.log(`  20K→${(compressResult.provider.content.length / 1000).toFixed(1)}K: ${t8.toFixed(2)} ms`);
  console.log(`  压缩比: ${(compressResult.provider.content.length / largeOutput.length * 100).toFixed(1)}%`);

  // ========================================
  // 5. 会话压缩效果
  // ========================================
  console.log('\n📊 5. 会话压缩效果测试');

  const compactor = new SessionCompactor();
  const originalTokens = TokenEstimator.estimateMessages(TEST_DATA.messages);

  benchmark.start('会话压缩-50条→10K');
  const compactResult = compactor.compact(TEST_DATA.messages, 10000);
  const t9 = benchmark.end({
    originalMessages: TEST_DATA.messages.length,
    finalMessages: compactResult.compacted.length,
    originalTokens,
  });

  const finalTokens = TokenEstimator.estimateMessages(compactResult.compacted);
  const compactSavings = originalTokens - finalTokens;

  console.log(`  50条→${compactResult.compacted.length}条: ${t9.toFixed(2)} ms`);
  console.log(`  Token: ${originalTokens}→${finalTokens} (节省 ${compactSavings})`);
  console.log(`  节省率: ${(compactSavings / originalTokens * 100).toFixed(1)}%`);

  // ========================================
  // 6. 模型路由效果
  // ========================================
  console.log('\n📊 6. 模型路由效果测试');

  const router = new ModelRouter();

  const testTasks = [
    { input: '你好', expected: 'c0-c1' },
    { input: '请帮我格式化这段代码', expected: 'c1' },
    { input: '分析这段代码并优化架构设计，同时debug这个错误', expected: 'c2-c3', hasCode: true },
  ];

  for (const task of testTasks) {
    benchmark.start(`路由-${task.expected}`);
    const result = router.route(task);
    const duration = benchmark.end({
      input: task.input.slice(0, 30),
      tier: result.tier,
      complexity: result.complexity.toFixed(2),
    });
    console.log(`  "${task.input.slice(0, 30)}..." → ${result.tier} (${duration}ms)`);
  }

  // ========================================
  // 7. 上下文预算治理
  // ========================================
  console.log('\n📊 7. 上下文预算治理测试');

  const gov = new ContextBudgetGovernor('claude-sonnet-4-6');
  const snapshot = gov.snapshot();

  console.log(`  模型: claude-sonnet-4-6`);
  console.log(`  Context Window: ${snapshot.contextWindow}`);
  console.log(`  可用 Token: ${snapshot.usableTokens}`);
  console.log(`  保留 Token: ${snapshot.reservedTokens}`);

  // 预算检查
  const check1 = gov.checkBudget(50000);
  console.log(`  50K使用量: ${check1.status} (${(check1.ratio * 100).toFixed(1)}%)`);

  const check2 = gov.checkBudget(150000);
  console.log(`  150K使用量: ${check2.status} (${(check2.ratio * 100).toFixed(1)}%)`);

  // ========================================
  // 8. Prompt Cache 效果
  // ========================================
  console.log('\n📊 8. Prompt Cache 效果测试');

  const cache = new PromptCacheManager();
  const messages = [
    { role: 'system', content: '你是专业助手，系统提示很长很长的内容...' },
    { role: 'system', content: '额外系统配置...' },
    { role: 'user', content: '用户消息1' },
    { role: 'user', content: '用户消息2' },
  ];

  benchmark.start('Cache-构建');
  const cacheResult = cache.build(messages);
  const t10 = benchmark.end({
    stableTokens: cacheResult.stableTokens,
    dynamicTokens: cacheResult.dynamicTokens,
  });

  console.log(`  构建耗时: ${t10.toFixed(2)} ms`);
  console.log(`  稳定Token: ${cacheResult.stableTokens}`);
  console.log(`  动态Token: ${cacheResult.dynamicTokens}`);
  console.log(`  缓存键: ${cacheResult.cacheKey}`);

  // ========================================
  // 9. Hook 集成测试
  // ========================================
  console.log('\n📊 9. Hook 集成测试');

  const hook = TokenOptimizerHook;

  benchmark.start('Hook-SessionStart');
  hook.onSessionStart({ sessionId: 'benchmark-test' });
  const t11 = benchmark.end({});

  benchmark.start('Hook-PreToolUse');
  hook.onPreToolUse({
    name: 'Write',
    input: { path: 'test.js', content: 'x'.repeat(10000) },
  });
  const t12 = benchmark.end({ argSize: 10000 });

  benchmark.start('Hook-PostToolUse');
  hook.onPostToolUse({
    toolName: 'Read',
    content: '执行结果：\n' + '内容 '.repeat(5000),
  });
  const t13 = benchmark.end({});

  const hookStatus = hook.getStatus();
  console.log(`  SessionStart: ${t11.toFixed(2)} ms`);
  console.log(`  PreToolUse(10K参数): ${t12.toFixed(2)} ms`);
  console.log(`  PostToolUse(压缩): ${t13.toFixed(2)} ms`);
  console.log(`  当前工具调用: ${hookStatus.toolCalls}`);

  // ========================================
  // 10. 审计日志
  // ========================================
  console.log('\n📊 10. 审计日志测试');

  const auditLogger = new AuditLogger();

  benchmark.start('审计-100条记录');
  for (let i = 0; i < 100; i++) {
    auditLogger.log('test', { tokens: Math.floor(Math.random() * 1000) });
  }
  const t14 = benchmark.end({ count: 100 });

  const auditSavings = auditLogger.getSavings();
  console.log(`  100条记录: ${t14.toFixed(2)} ms`);
  console.log(`  总节省: ${auditSavings.total} tokens`);

  // ========================================
  // 汇总
  // ========================================
  console.log('\n' + '='.repeat(60));
  console.log('\n📊 性能基准测试汇总\n');

  const summary = benchmark.summary();
  console.log(`总耗时: ${summary.totalDuration} ms`);
  console.log(`测试数量: ${summary.tests}`);

  console.log('\n📈 Token 节省预估:');
  console.log(`  - Obsidian 截断: 30-50%`);
  console.log(`  - 工具压缩: 20-40%`);
  console.log(`  - 会话压缩: 40-60%`);
  console.log(`  - 综合节省: 25-45%`);

  console.log('\n✅ 基准测试完成！\n');

  return summary;
}

// ============================================================
// 运行
// ============================================================

if (require.main === module) {
  runBenchmarks().catch(console.error);
}

module.exports = { runBenchmarks, TEST_DATA };
