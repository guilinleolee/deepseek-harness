/**
 * 🧠 Memory Loader Hook Utility
 * 天龙引擎 V9.0 - SessionStart 记忆加载器
 *
 * 功能：
 * - 封装 ObsidianWriter.query API
 * - 按 token 预算（默认 2000）控制加载量
 * - 按 type 分组（lesson / decision / concept）
 * - 提供 Markdown 渲染 + JSON 模式
 * - 过滤策略：最近 7 天 + confidence ≥ 0.5
 *
 * 用途：SessionStart hook 调用，注入到 Agent context
 * 版本：V9.0 MVP
 * 日期：2026-08-07
 */

const ObsidianWriter = require('./obsidian-writer');

const DEFAULT_CONFIG = {
  vaultPath: 'C:/Users/li/Documents/Obsidian Vault',
  mirrorPath: null, // 不读镜像，只读 Vault
  tokenBudget: 2000, // 总预算
  budgetsByType: {
    lesson: 1000,
    decision: 500,
    concept: 500,
  },
  since: 7, // 天
  minConfidence: 0.5,
  maxItemsPerType: 20,
  agentContext: 'all', // 'all' | '01-investigator' | '02-architect' | ...
};

class MemoryLoader {
  constructor(config = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    // 共用 ObsidianWriter 实例（自动镜像创建）
    this.writer = new ObsidianWriter({
      vaultPath: this.config.vaultPath,
      mirrorPath: this.config.mirrorPath || require('path').join(
        process.env.USERPROFILE || process.env.HOME || '',
        '.claude/projects/dragon-engine/memory/obsidian-mirror'
      ),
    });
  }

  // ===== 公共 API =====

  /**
   * 主入口：加载最近记忆，返回 Markdown 格式（注入 SessionStart context）
   * @returns {Promise<string>} Markdown 字符串
   */
  async loadForContext() {
    const sinceDate = this._daysAgoISO(this.config.since);
    const sections = [];
    let totalTokens = 0;

    // 按优先级加载：lesson > decision > concept
    const priority = ['lesson', 'decision', 'concept'];

    for (const type of priority) {
      const budget = this.config.budgetsByType[type] || 500;
      const items = await this.writer.query({
        type,
        since: sinceDate,
        limit: this.config.maxItemsPerType,
      });

      // 过滤 confidence
      const filtered = items.filter(it => (it.confidence ?? 0.5) >= this.config.minConfidence);

      // 截断到 token 预算
      const truncated = this._truncateByTokens(filtered, budget);

      if (truncated.length > 0) {
        const section = this._renderSection(type, truncated);
        sections.push(section);
        totalTokens += this._estimateTokens(section);
      }
    }

    if (sections.length === 0) {
      return '🧠 [天龙记忆] 最近 7 天无相关长期记忆';
    }

    const header = `🧠 [天龙记忆] 自动加载 ${sections.length} 类共 ${totalTokens} tokens（预算 ${this.config.tokenBudget}）\n\n`;
    return header + sections.join('\n\n---\n\n');
  }

  /**
   * JSON 模式（供 Agent 直接调用，不渲染 Markdown）
   * @param {string} [typeFilter] - 按 type 筛选
   * @returns {Promise<Array>}
   */
  async loadAsJSON(typeFilter = null) {
    const sinceDate = this._daysAgoISO(this.config.since);
    const types = typeFilter ? [typeFilter] : Object.keys(this.config.budgetsByType);

    const result = {};
    for (const type of types) {
      const items = await this.writer.query({ type, since: sinceDate, limit: this.config.maxItemsPerType });
      result[type] = items.filter(it => (it.confidence ?? 0.5) >= this.config.minConfidence);
    }
    return result;
  }

  /**
   * 按关键词搜索（标题包含关键词）
   * @param {string} keyword
   * @param {number} [limit=10]
   * @returns {Promise<Array>}
   */
  async searchByKeyword(keyword, limit = 10) {
    const items = await this.writer.query({ limit: 100 });
    return items.filter(it =>
      (it.title || '').toLowerCase().includes(keyword.toLowerCase()) ||
      (it.tags || []).some(t => t.toLowerCase().includes(keyword.toLowerCase()))
    ).slice(0, limit);
  }

  // ===== 内部方法 =====

  _daysAgoISO(days) {
    const d = new Date();
    d.setDate(d.getDate() - days);
    return d.toISOString().slice(0, 10);
  }

  /**
   * 按 token 预算截断（粗略估算：1 token ≈ 3 字符）
   */
  _truncateByTokens(items, budget) {
    const result = [];
    let usedTokens = 0;
    const maxChars = budget * 3;

    for (const item of items) {
      const itemText = `${item.title || ''}\n${(item.tags || []).map(t => '#' + t).join(' ')}`;
      const itemTokens = this._estimateTokens(itemText);

      if (usedTokens + itemTokens > maxChars) break;

      result.push(item);
      usedTokens += itemTokens;
    }

    return result;
  }

  _estimateTokens(text) {
    // 粗略估算：中文 1.5 字 = 1 token，英文 3 字符 = 1 token
    const chineseChars = (text.match(/[\u4e00-\u9fff]/g) || []).length;
    const otherChars = text.length - chineseChars;
    return Math.ceil(chineseChars / 1.5 + otherChars / 3);
  }

  _renderSection(type, items) {
    const labelMap = {
      lesson: '📚 最近经验教训',
      decision: '⚖️  最近重要决策',
      concept: '💡 最近概念沉淀',
    };
    const iconMap = {
      lesson: '🎓',
      decision: '⚖️ ',
      concept: '💡',
    };

    const lines = [`## ${labelMap[type] || type}`, ''];

    for (const item of items.slice(0, 10)) {
      const date = item.created || '?';
      const conf = (item.confidence ?? 0.5).toFixed(2);
      const tags = (item.tags || []).slice(0, 3).map(t => `#${t}`).join(' ');
      const title = (item.title || '').slice(0, 60);
      lines.push(`${iconMap[type] || '•'} **${date}** [conf=${conf}] ${title}`);
      if (tags) lines.push(`  ${tags}`);
    }

    if (items.length > 10) {
      lines.push(`\n_...还有 ${items.length - 10} 条_`);
    }

    return lines.join('\n');
  }
}

module.exports = MemoryLoader;

// ===== CLI 入口（自检）=====
if (require.main === module) {
  const args = process.argv.slice(2);
  if (args.includes('--test')) {
    console.log('🧪 MemoryLoader 自检开始...\n');
    const loader = new MemoryLoader();

    (async () => {
      try {
        // Test 1: Markdown 模式
        console.log('--- Test 1: loadForContext ---');
        const md = await loader.loadForContext();
        console.log(md);
        console.log(`\n✅ Markdown 长度: ${md.length} 字符`);

        // Test 2: JSON 模式
        console.log('\n--- Test 2: loadAsJSON ---');
        const json = await loader.loadAsJSON('lesson');
        console.log(`✅ lesson 类型: ${json.lesson.length} 条`);

        // Test 3: 关键词搜索
        console.log('\n--- Test 3: searchByKeyword ---');
        const results = await loader.searchByKeyword('test', 5);
        console.log(`✅ 关键词 "test": ${results.length} 条`);

        console.log('\n🎉 所有自检通过！');
      } catch (e) {
        console.error('❌ 自检失败:', e.message);
        process.exit(1);
      }
    })();
  } else {
    console.log('用法: node memory-loader.js --test');
  }
}