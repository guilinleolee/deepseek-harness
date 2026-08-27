/**
 * 懒加载 Skill 加载器
 *
 * 天龙引擎 Token 优化 Phase 1.4
 * 功能：按需加载 Skill，避免预加载浪费 token
 *
 * 核心策略：
 * 1. 延迟加载（首次引用时才加载）
 * 2. LRU 缓存
 * 3. 预算感知（检查剩余 token）
 * 4. 智能预取
 */

const fs = require('fs');
const path = require('path');

// 默认配置
const DEFAULT_CONFIG = {
  maxCacheSize: 10,           // 最多缓存10个Skill
  maxCacheBytes: 512 * 1024, // 最多缓存512KB
  budgetThreshold: 0.3,       // 剩余预算低于30%时拒绝加载
  preloadPatterns: [],         // 预加载模式
  skillsDir: null,            // Skill目录
};

class LazySkillLoader {
  constructor(config = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.cache = new Map();      // id → { content, tokens, size, lastAccess }
    this.accessOrder = [];       // LRU 顺序
    this.pending = new Map();    // 正在加载的 Promise
    this.stats = {
      hits: 0,
      misses: 0,
      loads: 0,
      evictions: 0,
    };
  }

  /**
   * 加载 Skill
   * @param {string} skillId - Skill ID
   * @param {number} availableBudget - 可用 token 预算
   * @returns {Promise<Object|null>}
   */
  async load(skillId, availableBudget = Infinity) {
    // 1. 命中缓存
    if (this.cache.has(skillId)) {
      this._updateAccess(skillId);
      this.stats.hits++;
      return this.cache.get(skillId).content;
    }

    // 2. 正在加载中
    if (this.pending.has(skillId)) {
      return this.pending.get(skillId);
    }

    // 3. 预算检查
    const estimatedTokens = this._estimateSkillTokens(skillId);
    const budgetRatio = estimatedTokens / availableBudget;

    if (budgetRatio > this.config.budgetThreshold) {
      console.warn(`[LazyLoader] Skill ${skillId} (${estimatedTokens} tokens) exceeds budget (${budgetRatio.toFixed(1)}%)`);
      return null;
    }

    // 4. 加载并缓存
    const loadPromise = this._doLoad(skillId);
    this.pending.set(skillId, loadPromise);

    try {
      const result = await loadPromise;
      this.pending.delete(skillId);
      return result;
    } catch (error) {
      this.pending.delete(skillId);
      throw error;
    }
  }

  /**
   * 执行加载
   * @param {string} skillId
   * @returns {Promise<Object>}
   */
  async _doLoad(skillId) {
    this.stats.loads++;

    const skillPath = this._resolveSkillPath(skillId);
    if (!skillPath) {
      throw new Error(`Skill not found: ${skillId}`);
    }

    // 读取文件
    const content = fs.readFileSync(skillPath, 'utf-8');
    const size = Buffer.byteLength(content, 'utf-8');
    const tokens = this._estimateTokens(content);

    // 检查缓存容量
    this._ensureCapacity(size);

    // 存入缓存
    const entry = {
      content,
      tokens,
      size,
      lastAccess: Date.now(),
      path: skillPath,
    };

    this.cache.set(skillId, entry);
    this._updateAccess(skillId);

    return content;
  }

  /**
   * 解析 Skill 路径
   * @param {string} skillId
   * @returns {string|null}
   */
  _resolveSkillPath(skillId) {
    if (this.config.skillsDir) {
      const basePath = path.join(this.config.skillsDir, skillId, 'SKILL.md');
      if (fs.existsSync(basePath)) return basePath;

      // 尝试其他扩展名
      for (const ext of ['.md', '.js', '.json']) {
        const altPath = path.join(this.config.skillsDir, skillId + ext);
        if (fs.existsSync(altPath)) return altPath;
      }
    }

    // 尝试天龙引擎标准路径
    const standardPaths = [
      path.join(process.cwd(), 'skills', skillId, 'SKILL.md'),
      path.join(process.cwd(), 'skills', skillId + '.md'),
      path.join(__dirname, '..', '..', 'skills', skillId, 'SKILL.md'),
    ];

    for (const p of standardPaths) {
      if (fs.existsSync(p)) return p;
    }

    return null;
  }

  /**
   * 估算 Skill token
   * @param {string} skillId
   * @returns {number}
   */
  _estimateSkillTokens(skillId) {
    // 小型 < 10KB ≈ 2.5K tokens
    // 中型 10-50KB ≈ 12.5K tokens
    // 大型 > 50KB ≈ 50K+ tokens

    const sizeMap = {
      small: 2500,
      medium: 12500,
      large: 50000,
    };

    // 简单估算：基于 ID 长度
    const estimatedSize = Math.min(skillId.length * 1000, 50000);
    if (estimatedSize < 10000) return sizeMap.small;
    if (estimatedSize < 50000) return sizeMap.medium;
    return sizeMap.large;
  }

  /**
   * 估算文本 token
   * @param {string} text
   * @returns {number}
   */
  _estimateTokens(text) {
    // 简单估算
    const cjkChars = (text.match(/[一-鿿]/g) || []).length;
    const otherChars = text.length - cjkChars;
    return cjkChars + Math.ceil(otherChars / 4);
  }

  /**
   * 确保缓存容量
   * @param {number} newSize
   */
  _ensureCapacity(newSize) {
    // 清理过期条目
    while (this.cache.size >= this.config.maxCacheSize) {
      this._evictLRU();
    }

    // 清理超出大小限制
    let totalSize = this._getTotalCacheSize();
    while (totalSize + newSize > this.config.maxCacheBytes && this.cache.size > 0) {
      this._evictLRU();
      totalSize = this._getTotalCacheSize();
    }
  }

  /**
   * 获取总缓存大小
   * @returns {number}
   */
  _getTotalCacheSize() {
    let total = 0;
    for (const entry of this.cache.values()) {
      total += entry.size;
    }
    return total;
  }

  /**
   * 驱逐 LRU 条目
   */
  _evictLRU() {
    if (this.accessOrder.length === 0) return;

    const lruId = this.accessOrder.shift();
    if (this.cache.has(lruId)) {
      this.cache.delete(lruId);
      this.stats.evictions++;
    }
  }

  /**
   * 更新访问顺序
   * @param {string} skillId
   */
  _updateAccess(skillId) {
    const idx = this.accessOrder.indexOf(skillId);
    if (idx !== -1) {
      this.accessOrder.splice(idx, 1);
    }
    this.accessOrder.push(skillId);

    const entry = this.cache.get(skillId);
    if (entry) {
      entry.lastAccess = Date.now();
    }
  }

  /**
   * 预加载 Skill
   * @param {string[]} skillIds
   * @param {number} budget
   */
  async preload(skillIds, budget = Infinity) {
    const promises = skillIds.map(id => this.load(id, budget));
    return Promise.allSettled(promises);
  }

  /**
   * 预取（基于历史使用）
   * @param {Array} recentSkills - 最近使用的 Skill
   * @param {number} budget
   */
  async prefetch(recentSkills, budget = Infinity) {
    // 简单策略：预取最近使用的
    const toPreload = recentSkills.slice(0, 3);
    await this.preload(toPreload, budget);
  }

  /**
   * 卸载 Skill
   * @param {string} skillId
   */
  unload(skillId) {
    if (this.cache.has(skillId)) {
      this.cache.delete(skillId);
      const idx = this.accessOrder.indexOf(skillId);
      if (idx !== -1) {
        this.accessOrder.splice(idx, 1);
      }
    }
  }

  /**
   * 清理所有缓存
   */
  clear() {
    this.cache.clear();
    this.accessOrder = [];
  }

  /**
   * 获取统计信息
   */
  getStats() {
    return {
      ...this.stats,
      cacheSize: this.cache.size,
      cacheBytes: this._getTotalCacheSize(),
      hitRate: this.stats.hits / (this.stats.hits + this.stats.misses) || 0,
    };
  }

  /**
   * 获取缓存状态
   */
  getCacheStatus() {
    return {
      entries: Array.from(this.cache.keys()),
      size: this.cache.size,
      maxSize: this.config.maxCacheSize,
      bytes: this._getTotalCacheSize(),
      maxBytes: this.config.maxCacheBytes,
    };
  }
}

/**
 * 创建懒加载器（便捷函数）
 * @param {Object} config
 * @returns {LazySkillLoader}
 */
function createLoader(config) {
  return new LazySkillLoader(config);
}

/**
 * 预算检查装饰器
 * @param {number} budget - 可用预算
 * @returns {Function}
 */
function withBudgetCheck(budget) {
  return (loader) => {
    const originalLoad = loader.load.bind(loader);
    loader.load = async (skillId) => {
      const estimated = loader._estimateSkillTokens(skillId);
      if (estimated > budget) {
        return null;
      }
      return originalLoad(skillId, budget);
    };
    return loader;
  };
}

module.exports = {
  LazySkillLoader,
  createLoader,
  withBudgetCheck,
  DEFAULT_CONFIG,
};
