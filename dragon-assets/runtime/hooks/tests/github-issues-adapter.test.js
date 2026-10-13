
/**
 * GitHub Issues Adapter 单元测试
 */

const GitHubIssuesAdapter = require('../utility/github-issues-adapter');

describe('GitHubIssuesAdapter', () => {
  let adapter;

  beforeEach(() => {
    // 创建模拟模式的适配器
    adapter = new GitHubIssuesAdapter({
      enabled: true,
      owner: 'test-org',
      repo: 'test-tasks',
      token: null // 模拟模式
    });
  });

  describe('构造函数', () => {
    test('应该创建适配器实例', () => {
      expect(adapter).toBeInstanceOf(GitHubIssuesAdapter);
      expect(adapter.enabled).toBe(true);
      expect(adapter.authenticated).toBe(false);
    });

    test('应该使用环境变量作为默认值', () => {
      const envAdapter = new GitHubIssuesAdapter({
        token: 'test-token'
      });
      expect(envAdapter.token).toBe('test-token');
    });
  });

  describe('formatTitle', () => {
    test('应该格式化高优先级任务标题', () => {
      const task = {
        id: 1,
        content: '修复登录bug',
        priority: 3
      };
      const title = adapter.formatTitle(task);
      expect(title).toContain('🔴');
      expect(title).toContain('[HIGH]');
      expect(title).toContain('修复登录bug');
    });

    test('应该格式化普通优先级任务标题', () => {
      const task = {
        id: 2,
        content: '编写单元测试',
        priority: 2
      };
      const title = adapter.formatTitle(task);
      expect(title).toContain('🟢');
      expect(title).toContain('[NORMAL]');
    });

    test('应该格式化低优先级任务标题', () => {
      const task = {
        id: 3,
        content: '更新文档',
        priority: 1
      };
      const title = adapter.formatTitle(task);
      expect(title).toContain('⚪');
      expect(title).toContain('[LOW]');
    });
  });

  describe('formatBody', () => {
    test('应该格式化完整的任务内容', () => {
      const task = {
        id: 1,
        content: '实现用户认证',
        priority: 3,
        status: 'pending',
        agent: '03builder',
        createdAt: Date.now(),
        estimatedTokens: 10000,
        timeout: 300,
        retryCount: 0,
        dependencies: [2, 3],
        description: '实现JWT认证'
      };

      const body = adapter.formatBody(task);

      expect(body).toContain('## 🎯 任务详情');
      expect(body).toContain('### 基本信息');
      expect(body).toContain('- **任务ID**: #1');
      expect(body).toContain('- **优先级**: HIGH');
      expect(body).toContain('### 🔗 依赖关系');
      expect(body).toContain('- 依赖: #2');
      expect(body).toContain('### 📊 元数据');
      expect(body).toContain('- **预估Token**: 10000');
      expect(body).toContain('九部天龙');
    });

    test('应该处理最小任务对象', () => {
      const task = {
        id: 1,
        content: '简单任务',
        priority: 2,
        createdAt: Date.now()
      };

      const body = adapter.formatBody(task);
      expect(body).toContain('#1');
      expect(body).toContain('简单任务');
    });
  });

  describe('generateLabels', () => {
    test('应该生成完整的标签列表', () => {
      const task = {
        id: 1,
        content: '任务',
        priority: 3,
        status: 'pending',
        agent: '03builder'
      };

      const labels = adapter.generateLabels(task);

      expect(labels).toContain('priority:high');
      expect(labels).toContain('status:pending');
      expect(labels).toContain('agent:03builder');
    });

    test('应该只生成有效的标签', () => {
      const task = {
        id: 1,
        content: '任务',
        priority: 2,
        status: 'completed'
      };

      const labels = adapter.generateLabels(task);

      expect(labels).toContain('priority:normal');
      expect(labels).toContain('status:completed');
      expect(labels.length).toBe(2);
    });

    test('应该处理缺少agent的任务', () => {
      const task = {
        id: 1,
        content: '任务',
        priority: 1,
        status: 'running'
      };

      const labels = adapter.generateLabels(task);

      expect(labels).toContain('priority:low');
      expect(labels).toContain('status:in-progress');
      expect(labels).not.toContain('agent:');
    });
  });

  describe('getPriorityName', () => {
    test('应该正确映射优先级', () => {
      expect(adapter.getPriorityName(3)).toBe('high');
      expect(adapter.getPriorityName(2)).toBe('normal');
      expect(adapter.getPriorityName(1)).toBe('low');
      expect(adapter.getPriorityName(0)).toBe('normal');
      expect(adapter.getPriorityName(999)).toBe('normal');
    });
  });

  describe('模拟模式测试', () => {
    test('应该创建模拟Issue', async () => {
      const task = {
        id: 1,
        content: '测试任务',
        priority: 2,
        status: 'pending',
        createdAt: Date.now()
      };

      const issue = await adapter.createIssue(task);

      expect(issue).not.toBeNull();
      expect(issue.number).toBeGreaterThan(100);
      expect(issue.mock).toBe(true);
      expect(issue.url).toContain('github.com');
    });

    test('应该更新模拟Issue状态', async () => {
      const result = await adapter.updateStatus(123, 'completed');
      expect(result).toBe(true);
    });

    test('应该添加模拟评论', async () => {
      const result = await adapter.addComment(123, '测试评论');
      expect(result).toBe(true);
    });
  });

  describe('formatResultComment', () => {
    test('应该格式化成功结果', () => {
      const result = {
        duration: 45000,
        tokens: 12500,
        output: '功能已实现'
      };

      const comment = adapter.formatResultComment(result);

      expect(comment).toContain('## ✅ 任务完成');
      expect(comment).toContain('**耗时**: 45秒');
      expect(comment).toContain('**Token消耗**: 12500');
      expect(comment).toContain('功能已实现');
    });

    test('应该处理最小结果对象', () => {
      const result = {};

      const comment = adapter.formatResultComment(result);

      expect(comment).toContain('## ✅ 任务完成');
    });
  });

  describe('checkConnection', () => {
    test('模拟模式应该返回未连接', async () => {
      const status = await adapter.checkConnection();

      expect(status.connected).toBe(false);
      expect(status.mode).toBe('mock');
      expect(status.message).toContain('模拟模式');
    });
  });

  describe('标签系统', () => {
    test('应该包含所有必要的标签', () => {
      expect(adapter.labels.priority.high).toBeDefined();
      expect(adapter.labels.priority.normal).toBeDefined();
      expect(adapter.labels.priority.low).toBeDefined();

      expect(adapter.labels.status.pending).toBeDefined();
      expect(adapter.labels.status.running).toBeDefined();
      expect(adapter.labels.status.completed).toBeDefined();
      expect(adapter.labels.status.failed).toBeDefined();

      expect(adapter.labels.agent['03builder']).toBeDefined();
      expect(adapter.labels.agent['04validator']).toBeDefined();
    });

    test('标签应该有正确的属性', () => {
      const label = adapter.labels.priority.high;

      expect(label.name).toBe('priority:high');
      expect(label.color).toBe('d73a4a');
      expect(label.description).toBe('高优先级');
    });
  });

  describe('批量操作', () => {
    test('应该批量创建模拟Issues', async () => {
      const tasks = [
        { id: 1, content: '任务1', priority: 2, createdAt: Date.now() },
        { id: 2, content: '任务2', priority: 3, createdAt: Date.now() },
        { id: 3, content: '任务3', priority: 1, createdAt: Date.now() }
      ];

      const results = await adapter.batchCreateIssues(tasks);

      expect(results).toHaveLength(3);
      expect(results[0].success).toBe(true);
      expect(results[1].success).toBe(true);
      expect(results[2].success).toBe(true);
      expect(results[0].taskId).toBe(1);
      expect(results[1].taskId).toBe(2);
      expect(results[2].taskId).toBe(3);
    });
  });

  describe('错误处理', () => {
    test('应该处理禁用的适配器', async () => {
      const disabledAdapter = new GitHubIssuesAdapter({
        enabled: false
      });

      const issue = await disabledAdapter.createIssue({
        id: 1,
        content: '任务',
        createdAt: Date.now()
      });

      expect(issue).toBeNull();
    });

    test('应该处理不自动创建的情况', async () => {
      const noAutoAdapter = new GitHubIssuesAdapter({
        enabled: true,
        autoCreate: false
      });

      const issue = await noAutoAdapter.createIssue({
        id: 1,
        content: '任务',
        createdAt: Date.now()
      });

      expect(issue).toBeNull();
    });
  });
});
