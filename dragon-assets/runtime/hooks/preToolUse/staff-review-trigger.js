
/**
 * Staff Review Trigger
 * Staff Engineer审查触发器
 *
 * 功能：在满足特定条件时自动触发Staff Engineer战略审查
 * 效果：预防技术债务、提升长期可维护性、确保决策记录完整
 *
 * 触发条件：
 * 1. 文件修改数量 > 5
 * 2. 代码行数 > 200
 * 3. 涉及核心文件（CLAUDE.md、核心Agent、关键配置）
 * 4. PR创建/合并事件
 * 5. 引入新依赖包
 * 6. 架构级变更
 * 7. 性能关键路径修改
 *
 * 原理：
 * 1. Hook Post-ToolUse事件
 * 2. 分析工具调用结果
 * 3. 评估是否满足触发条件
 * 4. 输出审查建议或自动触发审查
 */

const fs = require('fs');
const path = require('path');

module.exports = {
  hookName: 'StaffReviewTrigger',
  version: '1.0.0',
  description: '在满足特定条件时自动触发Staff Engineer战略审查',

  /**
   * 配置项
   * 可通过环境变量或配置文件覆盖
   */
  config: {
    // 触发阈值
    thresholds: {
      maxFiles: 5,              // 最大文件修改数（超过触发）
      maxLines: 200,            // 最大代码行数（超过触发）
      maxComplexity: 15,        // 最大复杂度（超过触发）
    },

    // 核心文件列表（修改即触发）
    coreFiles: [
      'CLAUDE.md',
      'hooks/hooks.json',
      'package.json',
      'tsconfig.json',
      '.env',
      'docker-compose.yml',
      'nginx.conf',
    ],

    // 核心目录（修改即触发）
    coreDirs: [
      'agents/',
      'hooks/',
      'skills/',
      'templates/',
      'dashboard-api/',
      'dashboard/',
    ],

    // 新依赖关键词
    dependencyKeywords: [
      'npm install',
      'npm add',
      'yarn add',
      'pnpm add',
      'requirements.txt',
      'Gemfile',
      'go.mod',
      'Cargo.toml',
    ],

    // 架构级变更关键词
    architectureKeywords: [
      'refactor',
      'restructure',
      'rewrite',
      'architecture',
      'migration',
      'upgrade',
      'deprecated',
    ],

    // 性能关键词
    performanceKeywords: [
      'performance',
      'optimization',
      'cache',
      'async',
      'parallel',
      'concurrent',
    ],
  },

  /**
   * 加载用户自定义配置
   */
  loadConfig() {
    const configPath = path.join(process.env.HOME || process.env.USERPROFILE, '.claude', 'staff-review-config.json');

    if (fs.existsSync(configPath)) {
      try {
        const userConfig = JSON.parse(fs.readFileSync(configPath, 'utf8'));
        this.config = { ...this.config, ...userConfig };
      } catch (error) {
        console.warn(`[StaffReviewTrigger] 加载配置失败: ${error.message}`);
      }
    }
  },

  /**
   * 检查是否涉及核心文件
   */
  checkCoreFiles(files) {
    if (!Array.isArray(files)) return false;

    return files.some(file => {
      const filePath = file.path || file;

      // 检查核心文件列表
      if (this.config.coreFiles.some(coreFile => filePath.includes(coreFile))) {
        return true;
      }

      // 检查核心目录
      if (this.config.coreDirs.some(coreDir => filePath.startsWith(coreDir))) {
        return true;
      }

      return false;
    });
  },

  /**
   * 估算代码行数
   */
  estimateLines(files) {
    if (!Array.isArray(files)) return 0;

    return files.reduce((total, file) => {
      const filePath = file.path || file;
      const additions = file.additions || file.lines_added || 0;
      const deletions = file.deletions || file.lines_deleted || 0;

      // 计算变更行数（新增+删除）
      return total + additions + deletions;
    }, 0);
  },

  /**
   * 检查是否包含依赖变更
   */
  checkDependencyChanges(command, output) {
    const text = (command + ' ' + JSON.stringify(output)).toLowerCase();

    return this.config.dependencyKeywords.some(keyword =>
      text.includes(keyword.toLowerCase())
    );
  },

  /**
   * 检查是否是架构级变更
   */
  checkArchitectureChanges(command, output) {
    const text = (command + ' ' + JSON.stringify(output)).toLowerCase();

    return this.config.architectureKeywords.some(keyword =>
      text.includes(keyword.toLowerCase())
    );
  },

  /**
   * 检查是否是性能关键路径
   */
  checkPerformanceChanges(command, output) {
    const text = (command + ' ' + JSON.stringify(output)).toLowerCase();

    return this.config.performanceKeywords.some(keyword =>
      text.includes(keyword.toLowerCase())
    );
  },

  /**
   * 评估触发条件
   * 返回：{ triggered: boolean, reason: string, priority: 'high'|'medium'|'low' }
   */
  evaluateTrigger(context, toolName, params, result) {
    // 加载用户配置
    this.loadConfig();

    const triggers = [];
    let priority = 'low';

    // 条件1：文件修改数量 > 5
    if (toolName === 'Bash' && params.command?.includes('git')) {
      // 尝试解析git输出获取文件数量
      const output = result?.stdout || result?.stderr || '';
      const fileMatches = output.match(/(\d+)\s*files? changed/i);

      if (fileMatches) {
        const fileCount = parseInt(fileMatches[1], 10);
        if (fileCount > this.config.thresholds.maxFiles) {
          triggers.push(`文件修改数量过多 (${fileCount}个文件)`);
          priority = 'medium';
        }
      }
    }

    // 条件2：代码行数 > 200
    if (toolName === 'Write' || toolName === 'Edit') {
      const content = params.content || '';
      const lineCount = content.split('\n').length;

      if (lineCount > this.config.thresholds.maxLines) {
        triggers.push(`代码行数过多 (${lineCount}行)`);
        priority = 'medium';
      }
    }

    // 条件3：涉及核心文件
    if (toolName === 'Write' || toolName === 'Edit' || toolName === 'Read') {
      const filePath = params.file_path || '';
      if (this.checkCoreFiles([filePath])) {
        triggers.push(`涉及核心文件 (${path.basename(filePath)})`);
        priority = 'high';
      }
    }

    // 条件4：PR创建/合并事件（通过Bash命令检测）
    if (toolName === 'Bash') {
      const command = params.command || '';
      if (command.includes('pr create') || command.includes('pr merge')) {
        triggers.push('创建/合并PR');
        priority = 'high';
      }
    }

    // 条件5：引入新依赖包
    if (toolName === 'Bash') {
      const command = params.command || '';
      const output = result?.stdout || result?.stderr || '';

      if (this.checkDependencyChanges(command, output)) {
        triggers.push('引入新依赖包');
        priority = 'medium';
      }
    }

    // 条件6：架构级变更
    if (toolName === 'Bash' || toolName === 'Write' || toolName === 'Edit') {
      const command = params.command || '';
      const content = params.content || '';
      const output = result?.stdout || result?.stderr || '';

      if (this.checkArchitectureChanges(command + content, output)) {
        triggers.push('架构级变更');
        priority = 'high';
      }
    }

    // 条件7：性能关键路径修改
    if (toolName === 'Write' || toolName === 'Edit') {
      const filePath = params.file_path || '';
      const content = params.content || '';

      // 性能相关文件
      const perfFiles = ['cache', 'async', 'worker', 'queue', 'job'];
      if (perfFiles.some(keyword => filePath.toLowerCase().includes(keyword))) {
        triggers.push('性能关键路径修改');
        priority = 'medium';
      }

      // 性能相关代码
      if (this.checkPerformanceChanges('', content)) {
        triggers.push('性能关键代码修改');
        priority = 'medium';
      }
    }

    // 返回评估结果
    return {
      triggered: triggers.length > 0,
      reason: triggers.join(', '),
      priority: triggers.length > 1 ? 'high' : priority, // 多个触发条件则提升优先级
      triggers: triggers,
    };
  },

  /**
   * Post-ToolUse Hook
   * 在工具使用后检查触发条件
   */
  postToolUse(context, toolName, params, result) {
    // 评估触发条件
    const evaluation = this.evaluateTrigger(context, toolName, params, result);

    if (!evaluation.triggered) {
      return null;
    }

    // 生成审查建议
    const reviewSuggestion = {
      agent: 'staff-engineer-reviewer',
      reason: evaluation.reason,
      priority: evaluation.priority,
      triggers: evaluation.triggers,
      timestamp: new Date().toISOString(),
    };

    // 输出审查建议（根据优先级决定输出详细程度）
    if (evaluation.priority === 'high') {
      console.log('\n🚨 [StaffReviewTrigger] 检测到高风险变更，强烈建议进行Staff Engineer审查');
      console.log('📋 触发条件:', evaluation.reason);
      console.log('⚡ 优先级:', evaluation.priority);
      console.log('💡 执行命令: Task({ subagent_type: "staff-engineer-reviewer" })');
      console.log('   或使用斜杠命令: /staff-review\n');
    } else if (evaluation.priority === 'medium') {
      console.log('\n⚠️  [StaffReviewTrigger] 检测到中等风险变更，建议进行Staff Engineer审查');
      console.log('📋 触发条件:', evaluation.reason);
      console.log('💡 可选命令: /staff-review\n');
    } else {
      console.log('\n💡 [StaffReviewTrigger] 检测到低风险变更，可选择进行Staff Engineer审查');
      console.log('📋 触发条件:', evaluation.reason);
      console.log('💡 可选命令: /staff-review\n');
    }

    // 高优先级自动触发（可选，默认不自动触发）
    // if (evaluation.priority === 'high') {
    //   return {
    //     triggerAgent: 'staff-engineer-reviewer',
    //     reason: evaluation.reason,
    //   };
    // }

    return null;
  },

  /**
   * 获取配置模板
   * 帮助用户创建自定义配置
   */
  getConfigTemplate() {
    return {
      thresholds: {
        maxFiles: 5,
        maxLines: 200,
        maxComplexity: 15,
      },
      coreFiles: [
        'CLAUDE.md',
        'package.json',
      ],
      coreDirs: [
        'agents/',
        'hooks/',
      ],
      dependencyKeywords: [
        'npm install',
      ],
      architectureKeywords: [
        'refactor',
      ],
      performanceKeywords: [
        'performance',
      ],
      autoTrigger: {
        high: false,    // 高风险是否自动触发
        medium: false,  // 中风险是否自动触发
        low: false,     // 低风险是否自动触发
      },
    };
  },

  /**
   * 生成配置文件
   */
  generateConfigFile() {
    const configPath = path.join(process.env.HOME || process.env.USERPROFILE, '.claude', 'staff-review-config.json');
    const template = this.getConfigTemplate();

    fs.writeFileSync(
      configPath,
      JSON.stringify(template, null, 2),
      'utf8'
    );

    console.log(`✅ 配置文件已生成: ${configPath}`);
    console.log('💡 你可以根据需要修改配置\n');
  },
};

// 导出配置生成器（供命令行使用）
if (require.main === module) {
  const hook = module.exports;
  hook.generateConfigFile();
}
