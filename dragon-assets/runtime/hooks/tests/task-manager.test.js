
/**
 * TaskManager单元测试
 * 测试任务队列管理功能
 */

const TaskManager = require('../utility/nine-dragons-task-manager');

describe('TaskManager', () => {
  let tm;

  beforeEach(() => {
    // 每个测试前创建新的TaskManager实例
    tm = new TaskManager({
      maxParallelTasks: 3,
      maxRetries: 3,
      persistencePath: '/tmp/test-task-queue.json'
    });
  });

  describe('enqueue', () => {
    test('应该成功添加任务到队列', () => {
      const taskId = tm.enqueue({
        content: '测试任务',
        priority: 'high'
      });

      expect(taskId).toBe(1);
      expect(tm.taskQueue.length).toBe(1);
      expect(tm.taskQueue[0].content).toBe('测试任务');
      expect(tm.taskQueue[0].priority).toBe(3); // high = 3
    });

    test('应该按优先级排序任务', () => {
      tm.enqueue({ content: '低优先级任务', priority: 'low' });
      tm.enqueue({ content: '高优先级任务', priority: 'high' });
      tm.enqueue({ content: '普通任务', priority: 'normal' });

      expect(tm.taskQueue[0].priority).toBe(3); // high
      expect(tm.taskQueue[1].priority).toBe(2); // normal
      expect(tm.taskQueue[2].priority).toBe(1); // low
    });

    test('应该处理任务依赖', () => {
      const taskId1 = tm.enqueue({ content: '任务1' });
      const taskId2 = tm.enqueue({
        content: '任务2',
        dependencies: [taskId1]
      });

      expect(tm.taskQueue[1].dependencies).toContain(taskId1);
    });
  });

  describe('getNextTask', () => {
    test('应该返回下一个待处理任务', () => {
      tm.enqueue({ content: '任务1', priority: 'high' });
      tm.enqueue({ content: '任务2', priority: 'normal' });

      const task = tm.getNextTask();

      expect(task).not.toBeNull();
      expect(task.content).toBe('任务1');
      expect(task.status).toBe('running');
      expect(tm.activeTasks.length).toBe(1);
      expect(tm.taskQueue.length).toBe(1);
    });

    test('应该尊重最大并行任务限制', () => {
      tm.enqueue({ content: '任务1' });
      tm.enqueue({ content: '任务2' });
      tm.enqueue({ content: '任务3' });
      tm.enqueue({ content: '任务4' });

      tm.getNextTask();
      tm.getNextTask();
      tm.getNextTask();

      expect(tm.activeTasks.length).toBe(3);

      const task4 = tm.getNextTask();
      expect(task4).toBeNull(); // 达到限制
    });

    test('应该等待依赖任务完成', () => {
      const taskId1 = tm.enqueue({ content: '任务1' });
      tm.enqueue({ content: '任务2', dependencies: [taskId1] });

      // 获取任务1（没有依赖）
      const task1 = tm.getNextTask();
      expect(task1.id).toBe(taskId1);

      // 任务2不能执行，因为依赖任务1
      const task2 = tm.getNextTask();
      expect(task2).toBeNull();

      expect(tm.taskQueue.length).toBe(1);
    });

    test('依赖完成后应该解锁后续任务', () => {
      const taskId1 = tm.enqueue({ content: '任务1' });
      const taskId2 = tm.enqueue({ content: '任务2', dependencies: [taskId1] });

      // 执行并完成任务1
      const task1 = tm.getNextTask();
      tm.completeTask(task1.id);

      // 现在任务2应该可以执行了
      const task2 = tm.getNextTask();
      expect(task2).not.toBeNull();
      expect(task2.id).toBe(taskId2);
    });
  });

  describe('completeTask', () => {
    test('应该标记任务为完成', () => {
      const taskId = tm.enqueue({ content: '任务1' });
      tm.getNextTask();

      const result = tm.completeTask(taskId, { output: 'success' });

      expect(result).toBe(true);
      expect(tm.activeTasks.length).toBe(0);
      expect(tm.completedTasks.length).toBe(1);
      expect(tm.completedTasks[0].status).toBe('completed');
      expect(tm.completedTasks[0].result).toEqual({ output: 'success' });
    });

    test('应该记录任务耗时', () => {
      const taskId = tm.enqueue({ content: '任务1' });
      tm.getNextTask();

      // 模拟耗时
      setTimeout(() => {
        tm.completeTask(taskId);
        const duration = tm.completedTasks[0].duration;
        expect(duration).toBeGreaterThan(0);
      }, 100);
    });
  });

  describe('failTask', () => {
    test('应该在重试限制内重新排队', () => {
      const taskId = tm.enqueue({ content: '任务1' });
      tm.getNextTask();

      const result = tm.failTask(taskId, '测试错误');

      expect(result).toBe('retry');
      expect(tm.activeTasks.length).toBe(0);
      expect(tm.taskQueue.length).toBe(1);
      expect(tm.taskQueue[0].retryCount).toBe(1);
    });

    test('应该在达到重试限制后标记为失败', () => {
      const taskId = tm.enqueue({ content: '任务1' });
      tm.getNextTask();

      // 重试3次
      tm.failTask(taskId, '错误1');
      tm.getNextTask();
      tm.failTask(taskId, '错误2');
      tm.getNextTask();
      tm.failTask(taskId, '错误3');

      expect(tm.failedTasks.length).toBe(1);
      expect(tm.failedTasks[0].retryCount).toBe(3);
    });
  });

  describe('getStatus', () => {
    test('应该返回正确的状态统计', () => {
      tm.enqueue({ content: '任务1' });
      tm.enqueue({ content: '任务2' });
      tm.getNextTask();

      const status = tm.getStatus();

      expect(status.pending).toBe(1);
      expect(status.running).toBe(1);
      expect(status.completed).toBe(0);
      expect(status.failed).toBe(0);
      expect(status.total).toBe(2);
    });
  });

  describe('getReport', () => {
    test('应该返回详细的任务报告', () => {
      const taskId1 = tm.enqueue({ content: '高优先级任务', priority: 'high' });
      const taskId2 = tm.enqueue({ content: '普通任务', priority: 'normal' });
      tm.getNextTask();

      const report = tm.getReport();

      expect(report.summary.running).toBe(1);
      expect(report.summary.pending).toBe(1);
      expect(report.activeTasks.length).toBe(1);
      expect(report.activeTasks[0].id).toBe(taskId1);
      expect(report.activeTasks[0].priority).toBe('high');
    });
  });

  describe('cancelTask', () => {
    test('应该取消待处理任务', () => {
      const taskId = tm.enqueue({ content: '任务1' });

      const result = tm.cancelTask(taskId);

      expect(result).toBe(true);
      expect(tm.taskQueue.length).toBe(0);
    });

    test('应该取消活跃任务', () => {
      const taskId = tm.enqueue({ content: '任务1' });
      tm.getNextTask();

      const result = tm.cancelTask(taskId);

      expect(result).toBe(true);
      expect(tm.activeTasks.length).toBe(0);
    });

    test('取消不存在的任务应该返回false', () => {
      const result = tm.cancelTask(999);

      expect(result).toBe(false);
    });
  });

  describe('pause/resume', () => {
    test('应该暂停和恢复队列', () => {
      tm.pause();
      expect(tm.isPaused()).toBe(true);

      tm.resume();
      expect(tm.isPaused()).toBe(false);
    });
  });

  describe('cleanup', () => {
    test('应该清理旧任务', () => {
      // 添加并完成一些任务
      const taskId1 = tm.enqueue({ content: '任务1' });
      tm.getNextTask();
      tm.completeTask(taskId1);

      // 修改完成时间为很久以前
      tm.completedTasks[0].completedAt = Date.now() - (25 * 60 * 60 * 1000);

      // 清理
      const cleaned = tm.cleanup(24 * 60 * 60 * 1000);

      expect(cleaned).toBe(1);
      expect(tm.completedTasks.length).toBe(0);
    });
  });

  describe('reset', () => {
    test('应该重置所有状态', () => {
      tm.enqueue({ content: '任务1' });
      tm.getNextTask();

      tm.reset();

      expect(tm.taskQueue.length).toBe(0);
      expect(tm.activeTasks.length).toBe(0);
      expect(tm.completedTasks.length).toBe(0);
      expect(tm.failedTasks.length).toBe(0);
      expect(tm.taskIdCounter).toBe(1);
    });
  });

  describe('priority normalization', () => {
    test('应该标准化不同的优先级输入', () => {
      const testCases = [
        { input: 'high', expected: 3 },
        { input: 'critical', expected: 3 },
        { input: 'urgent', expected: 3 },
        { input: 'normal', expected: 2 },
        { input: 'medium', expected: 2 },
        { input: 'low', expected: 1 },
        { input: 'background', expected: 1 },
        { input: 'invalid', expected: 2 } // 默认为normal
      ];

      testCases.forEach(({ input, expected }) => {
        expect(tm.normalizePriority(input)).toBe(expected);
      });
    });
  });

  describe('persistence', () => {
    test('应该保存和加载状态', () => {
      // 添加一些任务
      tm.enqueue({ content: '任务1', priority: 'high' });
      tm.enqueue({ content: '任务2', priority: 'normal' });

      // 保存状态
      tm.saveState();

      // 创建新实例并加载
      const tm2 = new TaskManager({
        persistencePath: '/tmp/test-task-queue.json'
      });
      tm2.loadState();

      expect(tm2.taskQueue.length).toBe(2);
      expect(tm2.taskQueue[0].content).toBe('任务1');
      expect(tm2.taskQueue[0].priority).toBe(3);
    });
  });
});

describe('TaskManager Statistics', () => {
  let tm;

  beforeEach(() => {
    tm = new TaskManager({
      persistencePath: '/tmp/test-task-queue-stats.json'
    });
  });

  test('应该计算正确的统计信息', () => {
    // 添加并完成一些任务
    for (let i = 0; i < 5; i++) {
      const taskId = tm.enqueue({ content: `任务${i}` });
      tm.getNextTask();
      tm.completeTask(taskId);
    }

    // 添加一个失败任务
    const failTaskId = tm.enqueue({ content: '失败任务' });
    tm.getNextTask();
    tm.failTask(failTaskId, '错误');
    tm.getNextTask();
    tm.failTask(failTaskId, '错误');
    tm.getNextTask();
    tm.failTask(failTaskId, '错误');

    const stats = tm.getStatistics();

    expect(stats.totalCompleted).toBe(5);
    expect(stats.totalFailed).toBe(1);
    expect(stats.successRate).toBe('83.33%'); // 5/6
  });
});
