
/**
 * 🐉 天龙引擎指挥官系统 - API桥接层
 * 指挥官：李依依（一一）
 * 系统提示词：../../prompts/liyiyi-commander-system-prompt.md
 */

const fs = require('fs');
const path = require('path');

// 状态文件路径
const STATE_DIR = path.join(process.cwd(), '.dragon-state');
const STATE_FILE = path.join(STATE_DIR, 'commander-state.json');

class DragonCommanderAPIBridge {
  constructor(commander) {
    this.commander = commander;
    this.enabled = true;
    this.syncInterval = 5000; // 每5秒同步一次
    this.syncTimer = null;

    this.init();
  }

  /**
   * 初始化桥接器
   */
  init() {
    // 确保状态目录存在
    this.ensureStateDir();

    // 启动自动同步
    this.startAutoSync();

    console.log('🐉 天龙引擎API桥接器已启动');
    console.log('📁 状态文件:', STATE_FILE);
    console.log('🔄 自动同步间隔:', this.syncInterval, 'ms');
  }

  /**
   * 确保状态目录存在
   */
  ensureStateDir() {
    if (!fs.existsSync(STATE_DIR)) {
      fs.mkdirSync(STATE_DIR, { recursive: true });
    }
  }

  /**
   * 启动自动同步
   */
  startAutoSync() {
    if (this.syncTimer) {
      clearInterval(this.syncTimer);
    }

    this.syncTimer = setInterval(() => {
      this.syncState();
    }, this.syncInterval);

    // 立即同步一次
    this.syncState();
  }

  /**
   * 停止自动同步
   */
  stopAutoSync() {
    if (this.syncTimer) {
      clearInterval(this.syncTimer);
      this.syncTimer = null;
    }
  }

  /**
   * 同步状态到文件
   */
  syncState() {
    if (!this.enabled) return;

    try {
      const state = this.buildState();
      fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
      // console.log('✅ 状态已同步');
    } catch (error) {
      console.error('❌ 状态同步失败:', error.message);
    }
  }

  /**
   * 构建状态对象
   */
  buildState() {
    const report = this.commander.generateProgressReport();

    return {
      timestamp: new Date().toISOString(),
      commander: this.commander.commander,
      engine: this.commander.engineName,
      version: this.commander.version,

      summary: report.summary,

      // 待处理任务
      pendingTasks: this.commander.taskQueue.map(task => ({
        id: task.id,
        description: task.description,
        priority: task.priority,
        agent: task.recommendedAgent || 'auto',
        status: 'pending',
        createdAt: task.createdAt || new Date().toISOString(),
        estimatedTime: task.estimatedTime || 120,
        estimatedCost: task.estimatedCost || 0.7
      })),

      // 运行中的代理
      activeAgents: report.activeAgents,

      // 已完成任务
      completedTasks: this.commander.completedTasks,

      // 失败任务
      failedTasks: this.commander.failedTasks,

      // 代理性能
      agentPerformance: Array.from(this.commander.agentPerformance.values()).map(perf => ({
        agentId: perf.agentId,
        agentName: perf.agentName,
        department: perf.department || '核心九部',
        successRate: Math.round(perf.successRate * 100),
        avgResponseTime: Math.round(perf.avgResponseTime),
        totalTasks: perf.totalTasks,
        costPerTask: perf.costPerTask || 0.7,
        trend: perf.trend || [],
        lastUpdated: perf.lastUpdated
      })),

      system: {
        uptime: process.uptime(),
        environment: process.env.NODE_ENV || 'development',
        nodeVersion: process.version,
        platform: process.platform,
        arch: process.arch
      }
    };
  }

  /**
   * 手动触发同步
   */
  forceSync() {
    this.syncState();
  }

  /**
   * 禁用桥接器
   */
  disable() {
    this.enabled = false;
    this.stopAutoSync();
    console.log('⚠️ API桥接器已禁用');
  }

  /**
   * 启用桥接器
   */
  enable() {
    this.enabled = true;
    this.startAutoSync();
    console.log('✅ API桥接器已启用');
  }
}

// 导出给Hook系统使用
if (typeof module !== 'undefined' && module.exports) {
  module.exports = DragonCommanderAPIBridge;
}

// 如果直接运行此文件
if (require.main === module) {
  console.log('🐉 天龙引擎API桥接器');
  console.log('这是一个桥接层，不直接运行');
  console.log('请在Hook系统中引入使用');
}
