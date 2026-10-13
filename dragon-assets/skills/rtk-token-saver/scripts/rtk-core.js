/**
 * RTK Token Saver 核心引擎
 * 来源: decolua/9router RTK Token Saver
 * 集成时间: 2026-05-24
 */

class RTKTokenSaver {
  constructor() {
    this.filters = this.loadFilters();
    this.enabled = true;
    this.stats = {
      totalCompressions: 0,
      totalSaved: 0,
      byType: {}
    };
  }

  loadFilters() {
    return {
      'git-diff': require('./filters/git-diff.js'),
      'git-status': require('./filters/git-status.js'),
      'grep': require('./filters/grep.js'),
      'find': require('./filters/find.js'),
      'ls': require('./filters/ls.js'),
      'tree': require('./filters/ls.js'),
      'dedup-log': require('./filters/dedup-log.js'),
      'smart-truncate': require('./filters/smart-truncate.js'),
      'read-numbered': require('./filters/read-numbered.js'),
      'search-list': require('./filters/search-list.js')
    };
  }

  /**
   * 检测过滤器类型
   * @param {string} header - 输出前1KB
   * @returns {string} 过滤器类型
   */
  detectFilterType(header) {
    // Git diff检测
    if (header.includes('diff --git')) return 'git-diff';

    // Git status检测
    if (header.includes('On branch') || header.includes('HEAD detached')) return 'git-status';

    // Grep检测（行号格式）
    if (header.match(/^\d+:\s/m) || header.includes(' matches')) return 'grep';

    // Find/ls检测（路径格式）
    if (header.match(/\.\/[^\s]/) || header.match(/[a-z]:\\/i)) return 'find';

    // Tree检测（层级格式）
    if (header.match(/^[\s│├└─]+[📁📄]/)) return 'ls';

    // 默认智能截断
    return 'smart-truncate';
  }

  /**
   * 压缩工具输出
   * @param {string} output - 原始输出
   * @returns {string} 压缩后输出
   */
  compress(output) {
    if (!this.enabled || !output || output.length < 100) {
      return output;
    }

    const header = output.slice(0, 1024);
    const filterType = this.detectFilterType(header);
    const filter = this.filters[filterType];

    if (!filter) {
      return output;
    }

    try {
      const compressed = filter(output);

      // 安全检查：压缩后不能变大
      if (compressed && compressed.length < output.length) {
        this.recordStats(filterType, output.length, compressed.length);
        return compressed;
      }
    } catch (e) {
      // 过滤器失败，保留原始
    }

    return output;
  }

  /**
   * 记录统计信息
   */
  recordStats(type, original, compressed) {
    this.stats.totalCompressions++;
    this.stats.totalSaved += (original - compressed);
    this.stats.byType[type] = (this.stats.byType[type] || 0) + (original - compressed);
  }

  /**
   * 获取统计信息
   */
  getStats() {
    return {
      ...this.stats,
      savingsPercent: this.stats.totalSaved > 0
        ? ((this.stats.totalSaved / (this.stats.totalSaved + this.getCurrentSize()) * 100).toFixed(1) + '%')
        : '0%'
    };
  }

  getCurrentSize() {
    return Math.max(1, this.stats.totalSaved);
  }

  /**
   * 启用RTK
   */
  enable() {
    this.enabled = true;
    return 'RTK Token Saver 已启用';
  }

  /**
   * 禁用RTK
   */
  disable() {
    this.enabled = false;
    return 'RTK Token Saver 已禁用';
  }

  /**
   * 重置统计
   */
  reset() {
    this.stats = {
      totalCompressions: 0,
      totalSaved: 0,
      byType: {}
    };
    return '统计已重置';
  }
}

module.exports = new RTKTokenSaver();