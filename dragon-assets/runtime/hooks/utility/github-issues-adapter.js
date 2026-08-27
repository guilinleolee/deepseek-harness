
/**
 * GitHub Issues Adapter for Nine Dragons
 * 九部天龙GitHub Issues适配器
 *
 * 功能：
 * 1. 自动创建Issue
 * 2. 实时同步状态
 * 3. 标签管理
 * 4. 评论同步
 * 5. 依赖关系管理
 */

const { Octokit } = require('@octokit/rest');

class GitHubIssuesAdapter {
  constructor(config = {}) {
    // 配置
    this.token = config.token || process.env.GITHUB_TOKEN;
    this.owner = config.owner || process.env.GITHUB_OWNER || 'nine-dragons';
    this.repo = config.repo || process.env.GITHUB_REPO || 'tasks';
    this.enabled = config.enabled !== false;
    this.autoCreate = config.autoCreate !== false;
    this.autoSync = config.autoSync !== false;

    // 初始化Octokit
    if (this.enabled && this.token) {
      this.octokit = new Octokit({
        auth: this.token,
        userAgent: 'NineDragons-TaskManager/1.0.0'
      });
      this.authenticated = true;
    } else {
      this.authenticated = false;
      console.warn('⚠️ GitHub Issues适配器未配置Token，将运行在模拟模式');
    }

    // 标签配置
    this.labels = {
      priority: {
        high: { name: 'priority:high', color: 'd73a4a', description: '高优先级' },
        normal: { name: 'priority:normal', color: 'a2eeef', description: '普通优先级' },
        low: { name: 'priority:low', color: '7057ff', description: '低优先级' }
      },
      status: {
        pending: { name: 'status:pending', color: 'e1e1e1', description: '待处理' },
        running: { name: 'status:in-progress', color: 'fbca04', description: '进行中' },
        completed: { name: 'status:completed', color: '2ea44f', description: '已完成' },
        failed: { name: 'status:failed', color: 'd73a4a', description: '失败' }
      },
      agent: {
        '00analyst': { name: 'agent:00analyst', color: '0075ca', description: '00分析师' },
        '01investigator': { name: 'agent:01investigator', color: '0366d6', description: '01调研师' },
        '02architect': { name: 'agent:02architect', color: '6095b7', description: '02架构师' },
        '03builder': { name: 'agent:03builder', color: '1f2428', description: '03构建师' },
        '04validator': { name: 'agent:04validator', color: 'd4c5f9', description: '04验证师' },
        '05security-reviewer': { name: 'agent:05security', color: 'b60205', description: '05安全师' },
        '06code-reviewer': { name: 'agent:06reviewer', color: 'FFA500', description: '06审查师' },
        '07scribe': { name: 'agent:07scribe', color: '5319e7', description: '07记录师' },
        '08publisher': { name: 'agent:08publisher', color: '28a745', description: '08发布师' }
      }
    };
  }

  /**
   * 初始化：创建标签
   */
  async initialize() {
    if (!this.authenticated) {
      console.log('� GitHub Issues适配器运行在模拟模式');
      return true;
    }

    try {
      console.log('🔧 初始化GitHub Issues标签...');

      // 创建所有标签
      for (const category of Object.values(this.labels)) {
        for (const label of Object.values(category)) {
          await this.createLabel(label);
        }
      }

      console.log('✅ GitHub Issues标签初始化完成');
      return true;
    } catch (error) {
      console.error('❌ GitHub Issues标签初始化失败:', error.message);
      return false;
    }
  }

  /**
   * 创建标签
   */
  async createLabel(label) {
    if (!this.authenticated) return true;

    try {
      await this.octokit.issues.createLabel({
        owner: this.owner,
        repo: this.repo,
        name: label.name,
        color: label.color,
        description: label.description
      });
      console.log(`  ✅ 创建标签: ${label.name}`);
    } catch (error) {
      if (error.status === 422) {
        // 标签已存在，忽略
        console.log(`  ⏭️  标签已存在: ${label.name}`);
      } else {
        throw error;
      }
    }
  }

  /**
   * 创建Issue
   */
  async createIssue(task) {
    if (!this.enabled || !this.autoCreate) {
      return null;
    }

    if (this.authenticated) {
      return await this._createRealIssue(task);
    } else {
      return await this._createMockIssue(task);
    }
  }

  /**
   * 创建真实的GitHub Issue
   */
  async _createRealIssue(task) {
    try {
      const issue = await this.octokit.issues.create({
        owner: this.owner,
        repo: this.repo,
        title: this.formatTitle(task),
        body: this.formatBody(task),
        labels: this.generateLabels(task)
      });

      console.log(`✅ GitHub Issue已创建: #${issue.data.number}`);
      return {
        number: issue.data.number,
        url: issue.data.html_url,
        id: issue.data.node_id
      };
    } catch (error) {
      console.error('❌ 创建GitHub Issue失败:', error.message);
      return null;
    }
  }

  /**
   * 创建模拟Issue（用于测试）
   */
  async _createMockIssue(task) {
    const mockNumber = Math.floor(Math.random() * 1000) + 100;
    console.log(`🎭 模拟创建GitHub Issue: #${mockNumber}`);
    return {
      number: mockNumber,
      url: `https://github.com/${this.owner}/${this.repo}/issues/${mockNumber}`,
      id: `mock_${mockNumber}`,
      mock: true
    };
  }

  /**
   * 格式化Issue标题
   */
  formatTitle(task) {
    const priorityEmoji = {
      high: '🔴',
      normal: '🟢',
      low: '⚪'
    };

    const priority = this.getPriorityName(task.priority);
    const emoji = priorityEmoji[priority] || '⚪';

    return `${emoji} [${priority.toUpperCase()}] ${task.content}`;
  }

  /**
   * 格式化Issue内容
   */
  formatBody(task) {
    const sections = [];

    // 标题
    sections.push('## 🎯 任务详情');
    sections.push('');

    // 基本信息
    sections.push('### 基本信息');
    sections.push(`- **任务ID**: #${task.id}`);
    sections.push(`- **优先级**: ${this.getPriorityName(task.priority).toUpperCase()}`);
    sections.push(`- **状态**: ${task.status || 'pending'}`);
    sections.push(`- **创建时间**: ${new Date(task.createdAt).toLocaleString('zh-CN')}`);
    sections.push('');

    // Agent信息
    if (task.agent) {
      sections.push('### 执行Agent');
      sections.push(`- **Agent**: ${task.agent}`);
      sections.push('');
    }

    // 依赖关系
    if (task.dependencies && task.dependencies.length > 0) {
      sections.push('### 🔗 依赖关系');
      task.dependencies.forEach(depId => {
        sections.push(`- 依赖: #${depId}`);
      });
      sections.push('');
    }

    // 元数据
    sections.push('### 📊 元数据');
    sections.push(`- **预估Token**: ${task.estimatedTokens || 'N/A'}`);
    sections.push(`- **超时时间**: ${task.timeout || 300}s`);
    sections.push(`- **重试次数**: ${task.retryCount || 0}/3`);
    sections.push('');

    // 描述
    if (task.description) {
      sections.push('### 📝 描述');
      sections.push(task.description);
      sections.push('');
    }

    // 九部天龙标记
    sections.push('---');
    sections.push('*由九部天龙自动创建 | 九部天龙 V6.3*');

    return sections.join('\n');
  }

  /**
   * 生成标签列表
   */
  generateLabels(task) {
    const labels = [];

    // 优先级标签
    const priority = this.getPriorityName(task.priority);
    if (this.labels.priority[priority]) {
      labels.push(this.labels.priority[priority].name);
    }

    // 状态标签
    const status = task.status || 'pending';
    if (this.labels.status[status]) {
      labels.push(this.labels.status[status].name);
    }

    // Agent标签
    if (task.agent && this.labels.agent[task.agent]) {
      labels.push(this.labels.agent[task.agent].name);
    }

    return labels;
  }

  /**
   * 更新Issue状态
   */
  async updateStatus(issueNumber, status, result = null) {
    if (!this.enabled || !this.autoSync || !issueNumber) {
      return false;
    }

    if (this.authenticated) {
      return await this._updateRealStatus(issueNumber, status, result);
    } else {
      return await this._updateMockStatus(issueNumber, status);
    }
  }

  /**
   * 更新真实Issue状态
   */
  async _updateRealStatus(issueNumber, status, result) {
    try {
      const updateData = {
        owner: this.owner,
        repo: this.repo,
        issue_number: issueNumber,
        state: status === 'completed' ? 'closed' : 'open'
      };

      // 更新标签
      const labels = this.labels.status[status] ? [this.labels.status[status].name] : [];

      if (labels.length > 0) {
        // 需要先获取现有标签
        const { data: issue } = await this.octokit.issues.get({
          owner: this.owner,
          repo: this.repo,
          issue_number: issueNumber
        });

        // 保留优先级和Agent标签，只更新状态标签
        const existingLabels = issue.labels.filter(label =>
          !label.name.startsWith('status:')
        ).map(label => label.name);

        updateData.labels = [...existingLabels, ...labels];
      }

      await this.octokit.issues.update(updateData);

      // 如果有结果，添加评论
      if (result) {
        await this.addComment(issueNumber, this.formatResultComment(result));
      }

      console.log(`✅ GitHub Issue状态已更新: #${issueNumber} → ${status}`);
      return true;
    } catch (error) {
      console.error('❌ 更新GitHub Issue状态失败:', error.message);
      return false;
    }
  }

  /**
   * 更新模拟Issue状态
   */
  async _updateMockStatus(issueNumber, status) {
    console.log(`🎭 模拟更新GitHub Issue状态: #${issueNumber} → ${status}`);
    return true;
  }

  /**
   * 添加评论
   */
  async addComment(issueNumber, comment) {
    if (!this.enabled || !issueNumber) {
      return false;
    }

    if (this.authenticated) {
      return await this._addRealComment(issueNumber, comment);
    } else {
      return await this._addMockComment(issueNumber, comment);
    }
  }

  /**
   * 添加真实评论
   */
  async _addRealComment(issueNumber, comment) {
    try {
      await this.octokit.issues.createComment({
        owner: this.owner,
        repo: this.repo,
        issue_number: issueNumber,
        body: comment
      });
      console.log(`💬 GitHub Issue评论已添加: #${issueNumber}`);
      return true;
    } catch (error) {
      console.error('❌ 添加GitHub Issue评论失败:', error.message);
      return false;
    }
  }

  /**
   * 添加模拟评论
   */
  async _addMockComment(issueNumber, comment) {
    console.log(`🎭 模拟添加GitHub Issue评论: #${issueNumber}`);
    console.log(`   评论内容: ${comment.substring(0, 50)}...`);
    return true;
  }

  /**
   * 格式化结果评论
   */
  formatResultComment(result) {
    const sections = [];

    sections.push('## ✅ 任务完成');
    sections.push('');

    if (result.duration) {
      sections.push(`**耗时**: ${Math.round(result.duration / 1000)}秒`);
    }

    if (result.tokens) {
      sections.push(`**Token消耗**: ${result.tokens}`);
    }

    if (result.output) {
      sections.push('');
      sections.push('### 输出');
      sections.push('```');
      sections.push(result.output);
      sections.push('```');
    }

    sections.push('');
    sections.push('*由九部天龙自动更新*');

    return sections.join('\n');
  }

  /**
   * 添加错误评论
   */
  async addErrorComment(issueNumber, error, retryCount) {
    const sections = [];

    sections.push('## ❌ 任务失败');
    sections.push('');
    sections.push(`**错误**: ${error}`);
    sections.push(`**重试次数**: ${retryCount}/3`);
    sections.push('');
    sections.push('*由九部天龙自动更新*');

    return await this.addComment(issueNumber, sections.join('\n'));
  }

  /**
   * 获取优先级名称
   */
  getPriorityName(priority) {
    const map = {
      3: 'high',
      2: 'normal',
      1: 'low'
    };
    return map[priority] || 'normal';
  }

  /**
   * 批量创建Issues（用于初始化）
   */
  async batchCreateIssues(tasks) {
    const results = [];

    for (const task of tasks) {
      const issue = await this.createIssue(task);
      results.push({
        taskId: task.id,
        issueNumber: issue ? issue.number : null,
        success: !!issue
      });

      // 避免触发GitHub API限流
      await this.sleep(1000);
    }

    return results;
  }

  /**
   * 延迟函数
   */
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * 检查连接状态
   */
  async checkConnection() {
    if (!this.authenticated) {
      return {
        connected: false,
        mode: 'mock',
        message: '未配置Token，运行在模拟模式'
      };
    }

    try {
      const { data } = await this.octokit.repos.get({
        owner: this.owner,
        repo: this.repo
      });

      return {
        connected: true,
        mode: 'authenticated',
        repository: data.full_name,
        url: data.html_url,
        message: '已连接到GitHub'
      };
    } catch (error) {
      return {
        connected: false,
        mode: 'error',
        message: `连接失败: ${error.message}`
      };
    }
  }
}

module.exports = GitHubIssuesAdapter;

/**
 * 使用示例
 *
 * ```javascript
 * const GitHubIssuesAdapter = require('./github-issues-adapter');
 *
 * // 创建适配器
 * const adapter = new GitHubIssuesAdapter({
 *   token: 'ghp_xxx',
 *   owner: 'your-org',
 *   repo: 'tasks',
 *   enabled: true,
 *   autoCreate: true,
 *   autoSync: true
 * });
 *
 * // 初始化标签
 * await adapter.initialize();
 *
 * // 创建Issue
 * const issue = await adapter.createIssue({
 *   id: 1,
 *   content: '实现用户认证功能',
 *   priority: 3, // high
 *   status: 'pending',
 *   agent: '03builder',
 *   estimatedTokens: 10000,
 *   createdAt: Date.now()
 * });
 *
 * // 更新状态
 * await adapter.updateStatus(issue.number, 'completed', {
 *   duration: 45000,
 *   tokens: 12500,
 *   output: '功能已实现'
 * });
 * ```
 */
