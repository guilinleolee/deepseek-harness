
/**
 * Nine Dragons Task Manager Hook
 * 九部天龙任务队列管理Hook
 *
 * 功能：
 * - 集成TaskManager到九部天龙
 * - 自动管理TodoWrite任务
 * - 智能优先级分配
 * - 任务依赖关系自动推断
 */

const TaskManager = require('../utility/nine-dragons-task-manager');

module.exports = {
  hookName: 'NineDragonsTaskManager',
  version: '1.0.0',
  description: '智能任务队列管理，支持优先级、依赖和重试',

  // 全局TaskManager实例
  taskManager: null,

  /**
   * 初始化Hook
   */
  init(context) {
    if (!this.taskManager) {
      // 读取GitHub配置
      const fs = require('fs');
      const path = require('path');
      const hooksConfigPath = path.join(process.env.HOME || process.env.USERPROFILE, '.claude', 'hooks', 'hooks.json');

      let githubConfig = { enabled: false };

      try {
        if (fs.existsSync(hooksConfigPath)) {
          const hooksConfig = JSON.parse(fs.readFileSync(hooksConfigPath, 'utf8'));
          if (hooksConfig.settings && hooksConfig.settings.taskManager && hooksConfig.settings.taskManager.github) {
            githubConfig = hooksConfig.settings.taskManager.github;
          }
        }
      } catch (error) {
        console.warn('⚠️ 读取GitHub配置失败:', error.message);
      }

      this.taskManager = new TaskManager({
        maxParallelTasks: 3,
        maxRetries: 3,
        persistencePath: path.join(
          process.env.HOME || process.env.USERPROFILE,
          '.claude',
          'task-queue.json'
        ),
        github: githubConfig
      });

      console.log('✅ TaskManager Hook已初始化');
      if (githubConfig.enabled) {
        console.log('✅ GitHub Issues集成已启用');
      }
    }
    return this.taskManager;
  },

  /**
   * UserPromptSubmit Hook
   * 在用户提交提示时初始化TaskManager
   */
  userPromptSubmit(context, userPrompt) {
    this.init(context);

    // 自动清理旧任务（超过24小时）
    this.taskManager.cleanup(24 * 60 * 60 * 1000);

    return null;
  },

  /**
   * Post-ToolUse Hook (TodoWrite)
   * 自动将TodoWrite任务加入队列
   */
  postToolUse(context, toolName, result) {
    if (toolName !== 'TodoWrite') {
      return null;
    }

    const tm = this.init();

    // 获取todo列表
    const todos = result && result.todos ? result.todos : [];

    // 分析任务并推断优先级和依赖
    const taskAnalysis = this.analyzeTasks(todos, context);

    // 将新任务加入队列
    taskAnalysis.newTasks.forEach(task => {
      tm.enqueue(task);
    });

    // 如果有高优先级任务，建议用户
    if (taskAnalysis.highPriorityCount > 0) {
      return {
        shouldAlert: true,
        alert: {
          level: 'info',
          message: `检测到 ${taskAnalysis.highPriorityCount} 个高优先级任务`,
          suggestion: '这些任务将被优先执行'
        }
      };
    }

    return null;
  },

  /**
   * Pre-ToolUse Hook (Task)
   * 在启动Task前检查队列状态
   */
  preToolUse(context, toolName, params) {
    if (toolName !== 'Task') {
      return null;
    }

    const tm = this.init();

    // 如果队列已满，警告
    if (tm.activeTasks.length >= tm.maxParallelTasks) {
      return {
        shouldWarn: true,
        warning: `
⚠️ 【九部天龙队列警告】

当前已有 ${tm.activeTasks.length} 个活跃任务（最大限制：${tm.maxParallelTasks}）

活跃任务：
${tm.activeTasks.map(t => `  - [ID:${t.id}] ${t.content}`).join('\n')}

建议：
1. 等待当前任务完成
2. 或使用 /nine-dragons-plan-status 查看详情
        `
      };
    }

    // 获取下一个任务建议
    const nextTask = tm.getNextTask();
    if (nextTask) {
      return {
        shouldSuggest: true,
        suggestion: `
💡 【九部天龙任务建议】

下一个推荐任务：[ID:${nextTask.id}]
${nextTask.content}

优先级：${tm.getPriorityName(nextTask.priority)}
预估Token：${nextTask.estimatedTokens}

是否执行此任务？（回复"yes"确认）
        `
      };
    }

    return null;
  },

  /**
   * 分析任务列表
   */
  analyzeTasks(todos, context) {
    const newTasks = [];
    let highPriorityCount = 0;

    // 获取现有任务ID
    const existingTaskIds = new Set([
      ...this.taskManager.taskQueue.map(t => t.id),
      ...this.taskManager.activeTasks.map(t => t.id),
      ...this.taskManager.completedTasks.map(t => t.id)
    ]);

    todos.forEach((todo, index) => {
      // 跳过已完成的任务
      if (todo.status === 'completed') {
        return;
      }

      // 跳过已存在的任务
      if (existingTaskIds.has(todo.id)) {
        return;
      }

      // 推断优先级
      const priority = this.inferPriority(todo, context, index);

      // 推断依赖关系
      const dependencies = this.inferDependencies(todo, todos, index);

      // 估算Token消耗
      const estimatedTokens = this.estimateTokens(todo, context);

      const task = {
        content: todo.content || todo.activeForm,
        priority: priority,
        dependencies: dependencies,
        estimatedTokens: estimatedTokens,
        agent: this.suggestAgent(todo, context),
        metadata: {
          originalTodo: todo,
          context: context
        }
      };

      newTasks.push(task);

      if (priority === 'high') {
        highPriorityCount++;
      }
    });

    return {
      newTasks,
      highPriorityCount
    };
  },

  /**
   * 推断任务优先级
   */
  inferPriority(todo, context, index) {
    const content = (todo.content || todo.activeForm || '').toLowerCase();

    // 高优先级关键词
    const highKeywords = [
      '紧急',
      '关键',
      '重要',
      'bug',
      'fix',
      'hotfix',
      'security',
      '安全',
      'blocker',
      'p0',
      '立即',
      'urgent',
      'critical'
    ];

    // 低优先级关键词
    const lowKeywords = [
      '优化',
      'refactor',
      '文档',
      'document',
      '清理',
      'cleanup',
      '可选',
      'optional',
      '低优先级',
      'low'
    ];

    // 检查高优先级
    if (highKeywords.some(kw => content.includes(kw))) {
      return 'high';
    }

    // 检查低优先级
    if (lowKeywords.some(kw => content.includes(kw))) {
      return 'low';
    }

    // 根据位置判断（越靠前优先级越高）
    if (index === 0) {
      return 'high';
    } else if (index <= 2) {
      return 'normal';
    }

    return 'normal';
  },

  /**
   * 推断任务依赖关系
   */
  inferDependencies(todo, todos, currentIndex) {
    const dependencies = [];

    // 简单策略：后续任务依赖前面的任务
    // 更复杂的策略可以分析任务内容

    // 检查是否有显式依赖标记
    const content = todo.content || todo.activeForm || '';
    const depMatch = content.match(/依赖[：:]\s*(\d+)/);
    if (depMatch) {
      const depId = parseInt(depMatch[1]);
      dependencies.push(depId);
    }

    // 检查是否有"after"标记
    const afterMatch = content.match(/after[：:]\s*(\d+)/);
    if (afterMatch) {
      const depId = parseInt(afterMatch[1]);
      dependencies.push(depId);
    }

    // 默认：依赖前面的1-2个任务
    if (dependencies.length === 0 && currentIndex > 0) {
      // 只依赖紧邻的前一个任务
      const prevTodo = todos[currentIndex - 1];
      if (prevTodo && prevTodo.id) {
        dependencies.push(prevTodo.id);
      }
    }

    return dependencies;
  },

  /**
   * 估算Token消耗
   */
  estimateTokens(todo, context) {
    const content = todo.content || todo.activeForm || '';

    // 基础Token消耗
    let baseTokens = 5000;

    // 根据内容长度调整
    const contentLength = content.length;
    if (contentLength > 100) {
      baseTokens += 5000;
    } else if (contentLength > 50) {
      baseTokens += 2000;
    }

    // 根据任务类型调整
    const lowerContent = content.toLowerCase();
    if (lowerContent.includes('测试') || lowerContent.includes('test')) {
      baseTokens += 3000;
    } else if (lowerContent.includes('文档') || lowerContent.includes('document')) {
      baseTokens += 2000;
    } else if (lowerContent.includes('重构') || lowerContent.includes('refactor')) {
      baseTokens += 8000;
    } else if (lowerContent.includes('实现') || lowerContent.includes('implement')) {
      baseTokens += 10000;
    }

    return baseTokens;
  },

  /**
   * 建议执行Agent
   */
  suggestAgent(todo, context) {
    const content = (todo.content || todo.activeForm || '').toLowerCase();

    // 根据任务内容建议Agent
    if (content.includes('分析') || content.includes('analyze') || content.includes('调研')) {
      return '00analyst';
    } else if (content.includes('架构') || content.includes('architect') || content.includes('设计')) {
      return '02architect';
    } else if (content.includes('实现') || content.includes('implement') || content.includes('开发')) {
      return '03builder';
    } else if (content.includes('测试') || content.includes('test') || content.includes('验证')) {
      return '04validator';
    } else if (content.includes('安全') || content.includes('security')) {
      return '05security-reviewer';
    } else if (content.includes('审查') || content.includes('review')) {
      return '06code-reviewer';
    } else if (content.includes('文档') || content.includes('document')) {
      return '07scribe';
    } else if (content.includes('发布') || content.includes('publish') || content.includes('deploy')) {
      return '08publisher';
    }

    return null; // 自动选择
  },

  /**
   * 命令：查看队列状态
   */
  handleCommand(context, command) {
    const tm = this.init();

    if (command === 'queue-status' || command === 'queue') {
      tm.printReport();
      return {
        shouldStop: true,
        response: '✅ 队列状态已显示'
      };
    }

    if (command === 'queue-reset') {
      tm.reset();
      return {
        shouldStop: true,
        response: '✅ 队列已重置'
      };
    }

    if (command.startsWith('queue-cancel ')) {
      const taskId = parseInt(command.replace('queue-cancel ', ''));
      const success = tm.cancelTask(taskId);
      return {
        shouldStop: true,
        response: success ? `✅ 任务 ${taskId} 已取消` : `❌ 未找到任务 ${taskId}`
      };
    }

    if (command === 'queue-pause') {
      tm.pause();
      return {
        shouldStop: true,
        response: '✅ 队列已暂停'
      };
    }

    if (command === 'queue-resume') {
      tm.resume();
      return {
        shouldStop: true,
        response: '✅ 队列已恢复'
      };
    }

    return null;
  }
};

/**
 * 使用说明
 *
 * 1. 将此文件放入 $CLAUDE/hooks/ 目录
 * 2. 在 hooks.json 中注册：
 *    {
 *      "userPromptSubmit": "../utility/nine-dragons-task-manager-hook.js",
 *      "postToolUse": "../utility/nine-dragons-task-manager-hook.js",
 *      "preToolUse": "../utility/nine-dragons-task-manager-hook.js"
 *    }
 * 3. 重启Claude Code
 *
 * 命令：
 * - /queue-status 或 /queue - 查看队列状态
 * - /queue-reset - 重置队列
 * - /queue-cancel <id> - 取消任务
 * - /queue-pause - 暂停队列
 * - /queue-resume - 恢复队列
 *
 * 预期效果：
 * - 自动管理任务优先级
 * - 自动推断任务依赖
 * - 限制并行任务数≤3
 * - 失败任务自动重试
 * - 任务状态持久化
 */
