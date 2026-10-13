
/**
 * 九部天龙Hooks单元测试
 * 测试CompletionEnforcer和LogWatcher功能
 */

const { CompletionEnforcer, LogWatcher } = require('../nine-dragons-hooks');

describe('CompletionEnforcer', () => {
  let enforcer;

  beforeEach(() => {
    enforcer = new CompletionEnforcer();
  });

  describe('hasPendingTasks', () => {
    test('应该检测到待完成任务', () => {
      const state = {
        pendingTasks: [
          { content: '任务1', status: 'pending' },
          { content: '任务2', status: 'in_progress' }
        ],
        completedTasks: []
      };

      expect(enforcer.hasPendingTasks(state)).toBe(true);
    });

    test('应该检测到所有任务完成', () => {
      const state = {
        pendingTasks: [],
        completedTasks: [
          { content: '任务1', status: 'completed' },
          { content: '任务2', status: 'completed' }
        ]
      };

      expect(enforcer.hasPendingTasks(state)).toBe(false);
    });
  });

  describe('isConversationalTurn', () => {
    test('应该检测到对话模式（无工具调用）', () => {
      const context = {
        recentCalls: [
          { toolName: null },
          { toolName: null },
          { toolName: null },
          { toolName: null },
          { toolName: null }
        ]
      };

      expect(enforcer.isConversationalTurn(context)).toBe(true);
    });

    test('应该检测到工作模式（有工具调用）', () => {
      const context = {
        recentCalls: [
          { toolName: null },
          { toolName: 'Read' },
          { toolName: null },
          { toolName: null },
          { toolName: null }
        ]
      };

      expect(enforcer.isConversationalTurn(context)).toBe(false);
    });
  });

  describe('canScheduleContinuation', () => {
    test('高token使用率时应该拒绝续写', () => {
      const context = {
        tokenUsage: {
          total: 180000,
          limit: 200000
        }
      };

      expect(enforcer.canScheduleContinuation(context)).toBe(false);
    });

    test('低token使用率时应该允许续写', () => {
      const context = {
        tokenUsage: {
          total: 50000,
          limit: 200000
        }
      };

      expect(enforcer.canScheduleContinuation(context)).toBe(true);
    });

    test('有错误时应该允许续写', () => {
      const context = {
        tokenUsage: {
          total: 50000,
          limit: 200000
        },
        recentErrors: [
          { message: 'API Error' }
        ]
      };

      expect(enforcer.canScheduleContinuation(context)).toBe(true);
    });
  });

  describe('buildContinuePrompt', () => {
    test('应该生成对话模式提醒', () => {
      const state = {
        pendingTasks: [
          { content: '完成测试', status: 'pending' }
        ],
        retryCount: 0
      };

      const prompt = enforcer.buildContinuePrompt(state, 'conversational');

      expect(prompt.shouldContinue).toBe(true);
      expect(prompt.prompt).toContain('对话模式');
      expect(prompt.prompt).toContain('完成测试');
      expect(prompt.priority).toBe('high');
    });

    test('应该生成续写提醒', () => {
      const state = {
        pendingTasks: [
          { content: '完成任务A', status: 'pending' },
          { content: '完成任务B', status: 'in_progress' }
        ],
        retryCount: 1
      };

      const prompt = enforcer.buildContinuePrompt(state, 'continue');

      expect(prompt.shouldContinue).toBe(true);
      expect(prompt.prompt).toContain('待完成任务');
      expect(prompt.prompt).toContain('2');
      expect(prompt.prompt).toContain('1/3');
    });
  });

  describe('preResponse', () => {
    test('应该检测虚假完成声明', () => {
      const context = {
        todos: [
          { content: '任务1', status: 'pending' },
          { content: '任务2', status: 'completed' }
        ]
      };

      const plannedResponse = '任务已经全部完成了！';

      const result = enforcer.preResponse(context, plannedResponse);

      expect(result).not.toBeNull();
      expect(result.shouldModify).toBe(true);
      expect(result.modification).toContain('尚未完成');
      expect(result.modification).toContain('任务1');
    });

    test('应该允许真实的完成声明', () => {
      const context = {
        todos: [
          { content: '任务1', status: 'completed' },
          { content: '任务2', status: 'completed' }
        ]
      };

      const plannedResponse = '所有任务已完成！';

      const result = enforcer.preResponse(context, plannedResponse);

      expect(result).toBeNull();
    });
  });
});

describe('LogWatcher', () => {
  let watcher;

  beforeEach(() => {
    watcher = new LogWatcher();
  });

  describe('analyzeError', () => {
    test('应该识别API错误', () => {
      const result = {
        stderr: 'Error: 429 Too Many Requests',
        exitCode: 1
      };

      const analysis = watcher.analyzeError(result);

      expect(analysis.type).toBe('api');
      expect(analysis.severity).toBe('error');
      expect(analysis.recoverable).toBe(true);
      expect(analysis.match).toContain('429');
    });

    test('应该识别依赖错误', () => {
      const result = {
        stderr: 'Error: Cannot find module \'express\'',
        exitCode: 1
      };

      const analysis = watcher.analyzeError(result);

      expect(analysis.type).toBe('dependency');
      expect(analysis.severity).toBe('critical');
      expect(analysis.recoverable).toBe(false);
    });

    test('应该识别权限错误', () => {
      const result = {
        stderr: 'Error: EACCES: permission denied',
        exitCode: 1
      };

      const analysis = watcher.analyzeError(result);

      expect(analysis.type).toBe('permission');
      expect(analysis.recoverable).toBe(true);
    });

    test('应该识别语法错误', () => {
      const result = {
        stderr: 'SyntaxError: Unexpected token',
        exitCode: 1
      };

      const analysis = watcher.analyzeError(result);

      expect(analysis.type).toBe('syntax');
      expect(analysis.severity).toBe('warning');
      expect(analysis.recoverable).toBe(true);
    });

    test('应该识别测试失败', () => {
      const result = {
        stderr: '✗ test failed: should return true',
        exitCode: 1
      };

      const analysis = watcher.analyzeError(result);

      expect(analysis.type).toBe('test');
      expect(analysis.recoverable).toBe(true);
    });

    test('应该处理未知错误', () => {
      const result = {
        stderr: 'Some unknown error occurred',
        exitCode: 1
      };

      const analysis = watcher.analyzeError(result);

      expect(analysis.type).toBe('unknown');
      expect(analysis.severity).toBe('warning');
      expect(analysis.recoverable).toBe(true);
    });
  });

  describe('isDangerousCommand', () => {
    test('应该检测rm -rf /', () => {
      expect(watcher.isDangerousCommand('rm -rf /')).toBe(true);
    });

    test('应该检测rm -rf /**', () => {
      expect(watcher.isDangerousCommand('rm -rf /**')).toBe(true);
    });

    test('应该检测dd命令', () => {
      expect(watcher.isDangerousCommand('dd if=/dev/zero of=/dev/sda')).toBe(true);
    });

    test('应该检测mkfs命令', () => {
      expect(watcher.isDangerousCommand('mkfs.ext4 /dev/sda1')).toBe(true);
    });

    test('应该允许安全命令', () => {
      expect(watcher.isDangerousCommand('ls -la')).toBe(false);
      expect(watcher.isDangerousCommand('npm install')).toBe(false);
      expect(watcher.isDangerousCommand('git status')).toBe(false);
    });
  });

  describe('generateSuggestion', () => {
    test('应该为API错误生成建议', () => {
      const error = {
        type: 'api',
        recoverable: true
      };

      const suggestion = watcher.generateSuggestion(error);

      expect(suggestion).toContain('API错误');
      expect(suggestion).toContain('可恢复');
      expect(suggestion).toContain('重试');
    });

    test('应该为依赖错误生成建议', () => {
      const error = {
        type: 'dependency',
        recoverable: false
      };

      const suggestion = watcher.generateSuggestion(error);

      expect(suggestion).toContain('依赖错误');
      expect(suggestion).toContain('手动干预');
      expect(suggestion).toContain('npm install');
    });

    test('应该为权限错误生成建议', () => {
      const error = {
        type: 'permission',
        recoverable: true
      };

      const suggestion = watcher.generateSuggestion(error);

      expect(suggestion).toContain('权限错误');
      expect(suggestion).toContain('sudo');
    });

    test('应该为语法错误生成建议', () => {
      const error = {
        type: 'syntax',
        recoverable: true
      };

      const suggestion = watcher.generateSuggestion(error);

      expect(suggestion).toContain('语法错误');
      expect(suggestion).toContain('Edit工具');
    });
  });

  describe('scanForErrors', () => {
    test('应该扫描多个错误', () => {
      const output = `
Error: Cannot find module 'express'
Warning: 429 Too Many Requests
SyntaxError: Unexpected token
      `;

      const errors = watcher.scanForErrors(output);

      expect(errors.length).toBeGreaterThanOrEqual(2);
      expect(errors.some(e => e.type === 'dependency')).toBe(true);
      expect(errors.some(e => e.type === 'api')).toBe(true);
      expect(errors.some(e => e.type === 'syntax')).toBe(true);
    });

    test('应该处理空输出', () => {
      const errors = watcher.scanForErrors('');
      expect(errors.length).toBe(0);
    });
  });
});

describe('Integration Tests', () => {
  describe('CompletionEnforcer + LogWatcher', () => {
    test('应该协同工作：错误后强制完成', () => {
      const context = {
        todos: [
          { content: '修复依赖', status: 'in_progress' }
        ],
        recentCalls: [
          { toolName: 'Bash', result: { exitCode: 1, stderr: 'Cannot find module' } }
        ],
        tokenUsage: { total: 50000, limit: 200000 }
      };

      const enforcer = new CompletionEnforcer();
      const watcher = new LogWatcher();

      // LogWatcher检测错误
      const errorAnalysis = watcher.analyzeError(context.recentCalls[0].result);
      expect(errorAnalysis.type).toBe('dependency');

      // CompletionEnforcer应该要求继续
      const state = enforcer.extractState(context);
      expect(enforcer.hasPendingTasks(state)).toBe(true);

      const shouldContinue = enforcer.canScheduleContinuation(context);
      expect(shouldContinue).toBe(true);
    });
  });
});
