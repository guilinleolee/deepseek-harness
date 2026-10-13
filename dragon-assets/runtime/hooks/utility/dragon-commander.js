
/**
 * 🐉 天龙引擎指挥官系统 V1.0
 * 指挥官：李依依（一一）
 * 系统提示词：../../prompts/liyiyi-commander-system-prompt.md
 *
 * 核心功能：
 * 1. 需求解析与分类
 * 2. 任务分解与调度
 * 3. 代理选择与分配
 * 4. 进度监控与追踪
 * 5. 结果整合与交付
 */

class DragonCommander {
  constructor() {
    this.version = '1.0.0';
    this.commander = '李依依（一一）';
    this.engineName = '天龙引擎';
    this.agentRegistry = this.loadAgentRegistry();
    this.taskQueue = [];
    this.activeAgents = new Map();
    this.completedTasks = [];
    this.failedTasks = [];
    // V2 占位字段：dragon-commander-v2.js 缺失，基础版临时挂空对象/空 Map 以避免 TypeError
    this.dependencyGraph = {};
    this.capabilityIndex = new Map();
  }

  /**
   * 加载代理注册表
   */
  loadAgentRegistry() {
    return {
      // 核心九部（00-08）
      '00-analyst': {
        id: '00-analyst',
        name: '00分析师',
        department: '核心九部',
        capabilities: ['需求分析', '问题解构', '可行性评估', '产品分析'],
        triggers: ['分析', '评估', '解构', '研究', '了解'],
        recommendedModel: 'opus',
        priority: 1
      },
      '01-investigator': {
        id: '01-investigator',
        name: '01调研师',
        department: '核心九部',
        capabilities: ['考古摸底', '代码考古', '依赖分析', '技术调研'],
        triggers: ['调研', '了解现状', '检查代码', '查看实现'],
        recommendedModel: 'sonnet',
        priority: 2
      },
      '02-architect': {
        id: '02-architect',
        name: '02架构师',
        department: '核心九部',
        capabilities: ['架构设计', '蓝图规划', '技术选型', '系统设计'],
        triggers: ['设计', '规划', '架构', '方案'],
        recommendedModel: 'opus',
        priority: 3
      },
      '03-builder': {
        id: '03-builder',
        name: '03构建师',
        department: '核心九部',
        capabilities: ['代码实现', '功能开发', '单元测试', '代码编写'],
        triggers: ['实现', '开发', '编写', '创建', '构建'],
        recommendedModel: 'sonnet',
        priority: 4
      },
      '04-validator': {
        id: '04-validator',
        name: '04验证师',
        department: '核心九部',
        capabilities: ['测试验证', '压力测试', 'Bug发现', '行为验证'],
        triggers: ['测试', '验证', '检查bug', '质量保证'],
        recommendedModel: 'sonnet',
        priority: 5
      },
      '05-security-reviewer': {
        id: '05-security-reviewer',
        name: '05安全师',
        department: '核心九部',
        capabilities: ['安全审查', '漏洞检测', '安全加固', '合规检查'],
        triggers: ['安全', '漏洞', '加密', '权限', '认证'],
        recommendedModel: 'sonnet',
        priority: 6
      },
      '06code-reviewer': {
        id: '06code-reviewer',
        name: '06审查师',
        department: '核心九部',
        capabilities: ['代码审查', '质量审计', '性能分析', '最佳实践'],
        triggers: ['审查', '审计', '优化', '重构'],
        recommendedModel: 'opus',
        priority: 7
      },
      '07-scribe': {
        id: '07-scribe',
        name: '07记录师',
        department: '核心九部',
        capabilities: ['文档编写', 'API文档', 'README', '代码注释'],
        triggers: ['文档', '说明', '注释', 'README'],
        recommendedModel: 'sonnet',
        priority: 8
      },
      '08-publisher': {
        id: '08-publisher',
        name: '08发布师',
        department: '核心九部',
        capabilities: ['Git发布', '版本管理', 'PR创建', '提交规范'],
        triggers: ['发布', '提交', 'PR', '版本'],
        recommendedModel: 'sonnet',
        priority: 9
      },

      // 技术中心（10-19）
      '10-01-prompt-architect': {
        id: '10-01-prompt-architect',
        name: '10-01提示词架构师',
        department: '技术中心-研发部',
        capabilities: ['提示词设计', 'Prompt工程', 'AI交互优化'],
        triggers: ['提示词', 'prompt', 'AI指令'],
        recommendedModel: 'opus',
        priority: 10
      },

      // 企划中心（20-29）
      '28-01-copywriter': {
        id: '28-01-copywriter',
        name: '28-01文案策划',
        department: '企划中心-企划支持',
        capabilities: ['文案创作', '内容撰写', '品牌文案'],
        triggers: ['文案', '内容', '撰写', '创作'],
        recommendedModel: 'sonnet',
        priority: 28
      },

      // 营销中心（30-39）
      '32-01-market-research': {
        id: '32-01-market-research',
        name: '32-01市场研究',
        department: '营销中心-市场洞察',
        capabilities: ['市场调研', '竞品分析', '用户洞察'],
        triggers: ['市场调研', '竞品', '用户研究'],
        recommendedModel: 'sonnet',
        priority: 32
      },

      // 运营中心（40-49）
      '35-04-content-operator': {
        id: '35-04-content-operator',
        name: '35-04内容运营',
        department: '运营中心-数字营销',
        capabilities: ['多平台发布', '内容分发', '发布数据分析'],
        triggers: ['发布', '分发', '运营'],
        recommendedModel: 'sonnet',
        priority: 35
      },

      // 产品中心（50-59）
      '50-01-product-planner': {
        id: '50-01-product-planner',
        name: '50-01产品策划',
        department: '产品中心-产品企划',
        capabilities: ['产品规划', '需求管理', '功能设计'],
        triggers: ['产品规划', '需求', '功能设计'],
        recommendedModel: 'opus',
        priority: 50
      }
    };
  }

  /**
   * 🧠 需求解析 - 分析用户意图
   */
  analyzeRequirement(userInput) {
    const analysis = {
      originalInput: userInput,
      timestamp: new Date().toISOString(),
      complexity: 'unknown',
      taskType: [],
      suggestedAgents: [],
      priority: 'normal',
      estimatedDuration: 'unknown'
    };

    // 判断任务复杂度（优先级从高到低）
    const complexityKeywords = {
      complex: ['系统', '重构', '整个项目', '完整', '架构'],
      medium: ['实现', '开发', '设计', '分析', '功能', '模块'],
      simple: ['简单', '快速', '改个', '修复', '优化']
    };

    for (const [level, keywords] of Object.entries(complexityKeywords)) {
      if (keywords.some(kw => userInput.includes(kw))) {
        analysis.complexity = level;
        break;
      }
    }

    // 如果没有匹配到，默认为medium
    if (analysis.complexity === 'unknown') {
      analysis.complexity = 'medium';
    }

    // 识别任务类型和推荐代理
    for (const [agentId, agent] of Object.entries(this.agentRegistry)) {
      const matchCount = agent.triggers.filter(trigger =>
        userInput.toLowerCase().includes(trigger.toLowerCase())
      ).length;

      if (matchCount > 0) {
        analysis.taskType.push(...agent.capabilities.slice(0, 1));
        analysis.suggestedAgents.push({
          agentId,
          agentName: agent.name,
          matchScore: matchCount,
          confidence: this.calculateConfidence(matchCount, userInput.length),
          // V1 补字段：基础版原版只返回 matchScore/confidence；commandCommand 等调用方需要 score/estimatedTime/estimatedCost
          score: this.calculateConfidence(matchCount, userInput.length),
          estimatedTime: agent.priority * 30,
          estimatedCost: agent.priority * 0.1,
          recommendedModel: agent.recommendedModel
        });
      }
    }

    // 按匹配度排序
    analysis.suggestedAgents.sort((a, b) => b.matchScore - a.matchScore);

    // V1 补字段：commandCommand 需要顶层 confidence（基础版原版无）
    analysis.confidence = analysis.suggestedAgents.length > 0
      ? analysis.suggestedAgents[0].confidence
      : 0;

    // 推断优先级
    const highPriorityKeywords = ['紧急', '关键', 'bug', '安全', '线上问题'];
    const lowPriorityKeywords = ['优化', '文档', '清理', '可选'];

    if (highPriorityKeywords.some(kw => userInput.includes(kw))) {
      analysis.priority = 'high';
    } else if (lowPriorityKeywords.some(kw => userInput.includes(kw))) {
      analysis.priority = 'low';
    }

    return analysis;
  }

  /**
   * 📊 计算匹配置信度
   */
  calculateConfidence(matchCount, inputLength) {
    const baseScore = matchCount * 0.3;
    const lengthBonus = Math.min(inputLength / 100, 0.4);
    return Math.min(baseScore + lengthBonus, 1.0);
  }

  /**
   * 🔨 任务分解 - 将需求拆解为子任务
   */
  decomposeTask(analysis) {
    const tasks = [];
    const taskId = `task-${Date.now()}`;

    // 根据复杂度决定分解策略
    switch (analysis.complexity) {
      case 'simple':
        tasks.push({
          id: `${taskId}-01`,
          type: 'single',
          description: analysis.originalInput,
          assignedTo: analysis.suggestedAgents[0]?.agentId || '00-analyst',
          priority: analysis.priority,
          estimatedTime: '1-2分钟'
        });
        break;

      case 'medium':
        tasks.push({
          id: `${taskId}-01`,
          type: 'analysis',
          description: '分析需求和现状',
          assignedTo: '00-analyst',
          priority: 'high',
          dependencies: []
        },
        {
          id: `${taskId}-02`,
          type: 'investigation',
          description: '调研现有实现',
          assignedTo: '01-investigator',
          priority: 'normal',
          dependencies: [`${taskId}-01`]
        },
        {
          id: `${taskId}-03`,
          type: 'implementation',
          description: '实现核心功能',
          assignedTo: analysis.suggestedAgents[0]?.agentId || '03-builder',
          priority: 'normal',
          dependencies: [`${taskId}-02`]
        });
        break;

      case 'complex':
        tasks.push({
          id: `${taskId}-01`,
          type: 'analysis',
          description: '深度需求分析',
          assignedTo: '00-analyst',
          priority: 'high',
          dependencies: []
        },
        {
          id: `${taskId}-02`,
          type: 'investigation',
          description: '全面调研',
          assignedTo: '01-investigator',
          priority: 'high',
          dependencies: [`${taskId}-01`]
        },
        {
          id: `${taskId}-03`,
          type: 'architecture',
          description: '架构设计',
          assignedTo: '02-architect',
          priority: 'high',
          dependencies: [`${taskId}-01`]
        },
        {
          id: `${taskId}-04`,
          type: 'implementation',
          description: '分步实现',
          assignedTo: '03-builder',
          priority: 'normal',
          dependencies: [`${taskId}-02`, `${taskId}-03`]
        },
        {
          id: `${taskId}-05`,
          type: 'validation',
          description: '测试验证',
          assignedTo: '04-validator',
          priority: 'normal',
          dependencies: [`${taskId}-04`]
        },
        {
          id: `${taskId}-06`,
          type: 'review',
          description: '代码审查',
          assignedTo: '06code-reviewer',
          priority: 'normal',
          dependencies: [`${taskId}-05`]
        });
        break;
    }

    return {
      taskId,
      parentTask: analysis.originalInput,
      tasks,
      createdAt: new Date().toISOString()
    };
  }

  /**
   * 🎯 代理调度 - 选择并启动合适的代理
   */
  async dispatchAgent(task) {
    const agent = this.agentRegistry[task.assignedTo];

    if (!agent) {
      return {
        success: false,
        error: `代理 ${task.assignedTo} 不存在`
      };
    }

    this.activeAgents.set(task.id, {
      taskId: task.id,
      agentId: agent.id,
      agentName: agent.name,
      startTime: new Date(),
      status: 'running'
    });

    return {
      success: true,
      task,
      agent: {
        id: agent.id,
        name: agent.name,
        department: agent.department,
        recommendedModel: agent.recommendedModel
      },
      message: `🎯 已调度 ${agent.name} 执行任务 ${task.id}`
    };
  }

  /**
   * 📈 生成进度报告
   */
  generateProgressReport() {
    const report = {
      timestamp: new Date().toISOString(),
      commander: this.commander,
      engine: this.engineName,
      version: this.version,

      summary: {
        total: this.taskQueue.length + this.activeAgents.size + this.completedTasks.length,
        pending: this.taskQueue.length,
        running: this.activeAgents.size,
        completed: this.completedTasks.length,
        failed: this.failedTasks.length
      },

      activeAgents: Array.from(this.activeAgents.values()).map(agent => ({
        taskId: agent.taskId,
        agentName: agent.agentName,
        duration: `${Math.round((new Date() - agent.startTime) / 1000)}s`,
        status: agent.status
      })),

      completedTasks: this.completedTasks.slice(-5),

      statistics: {
        successRate: this.completedTasks.length > 0
          ? Math.round((this.completedTasks.length / (this.completedTasks.length + this.failedTasks.length)) * 100)
          : 0,
        totalTasks: this.completedTasks.length + this.failedTasks.length
      }
    };

    return report;
  }

  /**
   * 📋 生成人类可读的报告
   */
  generateHumanReadableReport() {
    const report = this.generateProgressReport();

    let output = `
🐉 ${this.engineName} 指挥官报告
==================================================
指挥官：${this.commander}
时间：${new Date().toLocaleString('zh-CN')}

📊 任务统计:
   待处理: ${report.summary.pending}
   执行中: ${report.summary.running}
   已完成: ${report.summary.completed}
   已失败: ${report.summary.failed}
   总计:   ${report.summary.total}
`;

    if (report.summary.running > 0) {
      output += `\n▶️  执行中任务:\n`;
      for (const agent of report.activeAgents) {
        output += `   [${agent.taskId}] ${agent.agentName} - 耗时: ${agent.duration}\n`;
      }
    }

    if (report.summary.completed > 0) {
      output += `\n✅ 最近完成:\n`;
      for (const task of report.completedTasks) {
        output += `   [${task.id}] ${task.description}\n`;
      }
    }

    output += `
📈 统计信息:
   成功率: ${report.statistics.successRate}%
   总任务: ${report.statistics.totalTasks}
`;

    return output;
  }
}

// 导出供Hook系统使用
module.exports = DragonCommander;
