#!/usr/bin/env node
/**
 * AskOnce - 多模型对比工具
 *
 * 一次性向多个AI平台发送相同问题，对比回答质量
 *
 * @version 1.0.0
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

// 引入Zero Token Provider
let zeroTokenProvider = null;
try {
  zeroTokenProvider = require('../shared/zero-token-provider.js');
} catch (e) {
  console.error('[AskOnce] Failed to load zero-token-provider:', e.message);
  process.exit(1);
}

const provider = zeroTokenProvider.getProvider();

// 配置
const CONFIG_DIR = process.env.ZERO_TOKEN_CONFIG_DIR ||
  path.join(os.homedir(), '.openclaw-zero-state');
const OUTPUT_DIR = process.env.ASKONCE_OUTPUT_DIR || path.join(CONFIG_DIR, 'askonce-results');

/**
 * AskOnce执行器
 */
class AskOnceExecutor {
  constructor(options = {}) {
    this.outputDir = options.outputDir || OUTPUT_DIR;
    this.timeout = options.timeout || 120000; // 2分钟超时
    this.concurrency = options.concurrency || 5; // 并发数
    this.compareMode = options.compareMode || 'all'; // all, available, custom
    this.saveResults = options.saveResults !== false;
  }

  /**
   * 获取可用平台列表
   */
  getAvailablePlatforms() {
    return provider.getAvailablePlatforms();
  }

  /**
   * 获取所有支持的平台
   */
  getAllPlatforms() {
    return Object.keys(provider.platforms);
  }

  /**
   * 执行AskOnce
   */
  async execute(prompt, options = {}) {
    const startTime = Date.now();

    // 确定目标平台
    let targetPlatforms;
    if (options.platforms && options.platforms.length > 0) {
      targetPlatforms = options.platforms;
    } else if (this.compareMode === 'available') {
      targetPlatforms = this.getAvailablePlatforms();
    } else if (this.compareMode === 'all') {
      targetPlatforms = this.getAllPlatforms();
    } else {
      targetPlatforms = this.getAvailablePlatforms();
    }

    if (targetPlatforms.length === 0) {
      throw new Error('No platforms available for AskOnce');
    }

    console.log('\n🎯 AskOnce: Multi-Model Comparison');
    console.log('='.repeat(60));
    console.log(`📝 Prompt: ${prompt.substring(0, 100)}${prompt.length > 100 ? '...' : ''}`);
    console.log(`🔗 Platforms: ${targetPlatforms.join(', ')}`);
    console.log('');

    // 执行查询
    const results = await this.executeParallel(prompt, targetPlatforms, options);

    // 生成对比报告
    const report = this.generateReport(prompt, results, startTime);

    // 保存结果
    if (this.saveResults) {
      this.saveReport(report);
    }

    // 显示摘要
    this.displaySummary(report);

    return report;
  }

  /**
   * 并行执行查询
   */
  async executeParallel(prompt, platforms, options = {}) {
    const results = [];
    const concurrency = options.concurrency || this.concurrency;

    // 分批执行
    for (let i = 0; i < platforms.length; i += concurrency) {
      const batch = platforms.slice(i, i + concurrency);
      const batchResults = await Promise.allSettled(
        batch.map(p => this.executeSingle(p, prompt, options))
      );

      for (let j = 0; j < batch.length; j++) {
        const result = batchResults[j];
        const platform = batch[j];

        if (result.status === 'fulfilled') {
          results.push(result.value);
        } else {
          results.push({
            platform,
            success: false,
            error: result.reason?.message || 'Unknown error',
            latency: 0
          });
        }
      }
    }

    return results;
  }

  /**
   * 执行单个平台查询
   */
  async executeSingle(platform, prompt, options = {}) {
    const startTime = Date.now();
    const platformConfig = provider.platforms[platform];

    console.log(`  🔄 [${platformConfig?.name || platform}] Processing...`);

    try {
      // 调用平台API
      const result = await Promise.race([
        provider.chat(platform, [{ role: 'user', content: prompt }], options),
        new Promise((_, reject) =>
          setTimeout(() => reject(new Error('Timeout')), this.timeout)
        )
      ]);

      const latency = Date.now() - startTime;
      const content = result.response?.content || result.content;

      console.log(`  ✅ [${platformConfig?.name || platform}] Done (${latency}ms)`);

      return {
        platform,
        name: platformConfig?.name || platform,
        success: true,
        content,
        model: result.model,
        latency,
        quality: platformConfig?.quality || 0.8,
        wordCount: content?.length || 0,
        timestamp: new Date().toISOString()
      };

    } catch (error) {
      const latency = Date.now() - startTime;
      console.log(`  ❌ [${platformConfig?.name || platform}] Failed: ${error.message}`);

      return {
        platform,
        name: platformConfig?.name || platform,
        success: false,
        error: error.message,
        latency
      };
    }
  }

  /**
   * 生成对比报告
   */
  generateReport(prompt, results, startTime) {
    const successfulResults = results.filter(r => r.success);
    const failedResults = results.filter(r => !r.success);

    // 质量排序
    successfulResults.sort((a, b) => b.quality - a.quality);

    // 速度排序
    const speedSorted = [...successfulResults].sort((a, b) => a.latency - b.latency);

    // 推荐平台
    let recommendation = null;
    if (successfulResults.length > 0) {
      // 综合质量、速度、内容长度评分
      const scored = successfulResults.map(r => ({
        ...r,
        score: this.calculateScore(r)
      }));
      scored.sort((a, b) => b.score - a.score);
      recommendation = scored[0];
    }

    return {
      prompt,
      executedAt: new Date().toISOString(),
      totalLatency: Date.now() - startTime,
      summary: {
        total: results.length,
        success: successfulResults.length,
        failed: failedResults.length
      },
      results,
      successfulResults,
      failedResults,
      speedRanking: speedSorted.map(r => ({
        platform: r.platform,
        name: r.name,
        latency: r.latency
      })),
      qualityRanking: successfulResults.map(r => ({
        platform: r.platform,
        name: r.name,
        quality: r.quality
      })),
      recommendation: recommendation ? {
        platform: recommendation.platform,
        name: recommendation.name,
        reason: this.getRecommendationReason(recommendation),
        score: recommendation.score
      } : null
    };
  }

  /**
   * 计算综合评分
   */
  calculateScore(result) {
    const qualityScore = result.quality * 40; // 质量占40%
    const speedScore = Math.max(0, 100 - result.latency / 100) * 0.3; // 速度占30%
    const lengthScore = Math.min(result.wordCount / 500, 1) * 30; // 内容长度占30%

    return qualityScore + speedScore + lengthScore;
  }

  /**
   * 获取推荐原因
   */
  getRecommendationReason(result) {
    const reasons = [];

    if (result.quality >= 0.9) {
      reasons.push('highest quality');
    } else if (result.quality >= 0.85) {
      reasons.push('excellent quality');
    }

    if (result.latency < 5000) {
      reasons.push('fast response');
    }

    if (result.wordCount > 1000) {
      reasons.push('comprehensive answer');
    }

    return reasons.length > 0 ? reasons.join(', ') : 'balanced performance';
  }

  /**
   * 保存报告
   */
  saveReport(report) {
    if (!fs.existsSync(this.outputDir)) {
      fs.mkdirSync(this.outputDir, { recursive: true });
    }

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `askonce-${timestamp}.json`;
    const filepath = path.join(this.outputDir, filename);

    fs.writeFileSync(filepath, JSON.stringify(report, null, 2));
    console.log(`\n💾 Report saved: ${filepath}`);
  }

  /**
   * 显示摘要
   */
  displaySummary(report) {
    console.log('\n' + '='.repeat(60));
    console.log('📊 AskOnce Summary');
    console.log('='.repeat(60));
    console.log(`\n📈 Results: ${report.summary.success}/${report.summary.total} successful`);
    console.log(`⏱️  Total Time: ${report.totalLatency}ms`);

    if (report.recommendation) {
      console.log(`\n🏆 Recommendation: ${report.recommendation.name}`);
      console.log(`   Reason: ${report.recommendation.reason}`);
      console.log(`   Score: ${report.recommendation.score.toFixed(1)}`);
    }

    // 速度排行
    console.log('\n⚡ Speed Ranking:');
    report.speedRanking.slice(0, 5).forEach((r, i) => {
      console.log(`   ${i + 1}. ${r.name}: ${r.latency}ms`);
    });

    // 质量排行
    console.log('\n🎯 Quality Ranking:');
    report.qualityRanking.slice(0, 5).forEach((r, i) => {
      console.log(`   ${i + 1}. ${r.name}: ${(r.quality * 100).toFixed(0)}%`);
    });

    // 失败信息
    if (report.failedResults.length > 0) {
      console.log('\n❌ Failed Platforms:');
      report.failedResults.forEach(r => {
        console.log(`   ${r.name}: ${r.error}`);
      });
    }

    console.log('\n' + '='.repeat(60));
  }

  /**
   * 对比两个回答
   */
  compareAnswers(platform1, platform2) {
    const result1 = this.results?.find(r => r.platform === platform1);
    const result2 = this.results?.find(r => r.platform === platform2);

    if (!result1 || !result2) {
      console.error('One or both platforms not found in results');
      return null;
    }

    console.log('\n' + '='.repeat(60));
    console.log(`📊 Comparing: ${result1.name} vs ${result2.name}`);
    console.log('='.repeat(60));

    console.log(`\n🎯 ${result1.name}:`);
    console.log(`   Quality: ${(result1.quality * 100).toFixed(0)}%`);
    console.log(`   Speed: ${result1.latency}ms`);
    console.log(`   Length: ${result1.wordCount} chars`);

    console.log(`\n🎯 ${result2.name}:`);
    console.log(`   Quality: ${(result2.quality * 100).toFixed(0)}%`);
    console.log(`   Speed: ${result2.latency}ms`);
    console.log(`   Length: ${result2.wordCount} chars`);

    return {
      platform1: result1,
      platform2: result2,
      winner: result1.quality > result2.quality ? result1 :
              result2.quality > result1.quality ? result2 : null
    };
  }
}

/**
 * 命令行入口
 */
async function main() {
  const args = process.argv.slice(2);

  // 解析参数
  const options = {
    platforms: [],
    prompt: null,
    concurrency: 5,
    timeout: 120000,
    list: false,
    file: null
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];

    if (arg === '--platform' || arg === '-p') {
      options.platforms = args[++i]?.split(',') || [];
    } else if (arg === '--concurrency' || arg === '-c') {
      options.concurrency = parseInt(args[++i]) || 5;
    } else if (arg === '--timeout' || arg === '-t') {
      options.timeout = parseInt(args[++i]) * 1000 || 120000;
    } else if (arg === '--list' || arg === '-l') {
      options.list = true;
    } else if (arg === '--file' || arg === '-f') {
      options.file = args[++i];
    } else if (!arg.startsWith('-')) {
      options.prompt = arg;
    }
  }

  // 创建执行器
  const executor = new AskOnceExecutor(options);

  // 执行操作
  if (options.list) {
    // 列出可用平台
    console.log('\n📋 Available Platforms:');
    const available = executor.getAvailablePlatforms();
    const all = executor.getAllPlatforms();

    for (const platform of all) {
      const config = provider.platforms[platform];
      const isAvailable = available.includes(platform);
      const status = isAvailable ? '✅' : '❌';
      console.log(`   ${status} ${platform.padEnd(12)} - ${config?.name || platform}`);
      if (config?.quality) {
        console.log(`      Quality: ${(config.quality * 100).toFixed(0)}%`);
      }
    }
  } else if (options.file) {
    // 从文件读取prompt
    if (fs.existsSync(options.file)) {
      options.prompt = fs.readFileSync(options.file, 'utf-8');
    } else {
      console.error(`File not found: ${options.file}`);
      process.exit(1);
    }
  }

  if (options.prompt) {
    // 执行AskOnce
    try {
      await executor.execute(options.prompt, {
        platforms: options.platforms,
        concurrency: options.concurrency,
        timeout: options.timeout
      });
    } catch (error) {
      console.error(`\n❌ Error: ${error.message}`);
      process.exit(1);
    }
  } else if (!options.list) {
    // 显示帮助
    console.log('\nUsage:');
    console.log('  node ask-once.js <prompt>                     Execute AskOnce with prompt');
    console.log('  node ask-once.js --file <file>                Read prompt from file');
    console.log('  node ask-once.js -p <platforms> <prompt>      Use specific platforms');
    console.log('  node ask-once.js --list                       List available platforms');
    console.log('\nOptions:');
    console.log('  -p, --platform <list>     Comma-separated platform list');
    console.log('  -c, --concurrency <n>     Parallel execution limit (default: 5)');
    console.log('  -t, --timeout <seconds>   Request timeout (default: 120)');
    console.log('  -f, --file <path>         Read prompt from file');
    console.log('  -l, --list                List available platforms');
  }
}

// 导出
module.exports = { AskOnceExecutor };

// 运行
if (require.main === module) {
  main().catch(console.error);
}