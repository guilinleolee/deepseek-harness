
/**
 * Lessons Logger Hook
 * 经验教训记录器
 *
 * 功能：自动检测并记录AI Agent在执行过程中学到的经验教训
 * 效果：避免重复错误，持续优化性能
 *
 * 原理：
 * 1. extractLesson(): 检测可记录的经验教训
 * 2. appendLesson(): 追加到lessons.md
 * 3. 检测触发条件（用户纠正、三次失败、重复错误）
 * 4. 质量门槛验证（四条铁律）
 *
 * 质量门槛（四条铁律）：
 * - 需要发现：非显而易见的解决方案
 * - 可复用：有助于未来任务
 * - 明确触发条件：具体错误/症状
 * - 已验证：实际有效
 */

const fs = require('fs');
const path = require('path');

// V9.0: 引入 Obsidian Writer 做双写（Vault 端独立文件，自动 frontmatter）
const ObsidianWriter = require('../utility/obsidian-writer');
let _obsidianWriter = null;
function getWriter() {
  if (!_obsidianWriter) {
    _obsidianWriter = new ObsidianWriter({
      vaultPath: 'C:/Users/li/Documents/Obsidian Vault',
      mirrorPath: path.join(process.env.USERPROFILE || process.env.HOME || '', '.claude/projects/dragon-engine/memory/obsidian-mirror'),
      defaultArea: 'Dragon-Engine',
      preserveManualEdits: true,
    });
  }
  return _obsidianWriter;
}

module.exports = {
  hookName: 'LessonsLogger',
  version: '1.0.0',
  description: '自动记录和索引经验教训，构建持续改进循环',

  // 配置
  config: {
    lessonsPath: path.resolve(__dirname, '../lessons.md'),
    minRetryCount: 3, // 最少重试次数触发
    checkUserCorrections: true, // 检测用户纠正
    checkRepetitiveErrors: true, // 检测重复错误
    maxLessonsPerSession: 5, // 每次会话最多记录数量
  },

  // 状态追踪
  state: {
    errorCounts: new Map(), // 错误计数
    userCorrections: [], // 用户纠正历史
    lessonsRecorded: 0, // 本次会话已记录数量
    lastErrors: [], // 最近的错误
  },

  /**
   * Post-ToolUse Hook
   * 在工具使用后检测是否需要记录经验教训
   */
  postToolUse(context, toolName, result) {
    // 只在关键工具后检查
    const criticalTools = ['Bash', 'Read', 'Write', 'Edit'];

    if (!criticalTools.includes(toolName)) {
      return null;
    }

    // 检查是否达到本次会话记录上限
    if (this.state.lessonsRecorded >= this.config.maxLessonsPerSession) {
      return null;
    }

    // 检测触发条件
    const lesson = this.detectLessonOpportunity(context, toolName, result);

    if (lesson && this.passesQualityGates(lesson)) {
      this.appendLesson(lesson);
      this.state.lessonsRecorded++;

      return {
        shouldInform: true,
        message: `📚 已记录经验教训: ${lesson.title}`
      };
    }

    return null;
  },

  /**
   * UserPromptSubmit Hook
   * 检测用户纠正
   */
  userPromptSubmit(context, userPrompt) {
    if (!this.config.checkUserCorrections) {
      return null;
    }

    // 检测纠正关键词
    const correctionPatterns = [
      /不对/i,
      /错误/i,
      /不是这样/i,
      /应该是/i,
      /修正/i,
      /改用/i,
      /不要.*?用/i
    ];

    const isCorrection = correctionPatterns.some(pattern =>
      pattern.test(userPrompt)
    );

    if (isCorrection) {
      const lastError = this.state.lastErrors[this.state.lastErrors.length - 1];

      if (lastError) {
        const lesson = {
          type: 'user-correction',
          title: `用户纠正: ${lastError.error}`,
          error: lastError.error,
          correction: userPrompt,
          context: lastError.context,
          agent: context.currentAgent || 'unknown',
          priority: 'P0',
          tags: this.extractTags(userPrompt)
        };

        if (this.passesQualityGates(lesson)) {
          this.appendLesson(lesson);
          this.state.lessonsRecorded++;

          return {
            shouldInform: true,
            message: `📚 已记录用户纠正: ${lesson.title}`
          };
        }
      }
    }

    return null;
  },

  /**
   * 检测经验教训机会
   */
  detectLessonOpportunity(context, toolName, result) {
    // 检测Bash错误
    if (toolName === 'Bash' && result && result.stderr) {
      const errorPatterns = [
        { pattern: /ENOENT.*?not found/i, type: 'dependency', solution: '安装缺失的依赖' },
        { pattern: /EACCES.*?permission denied/i, type: 'permission', solution: '检查文件权限' },
        { pattern: /SyntaxError/i, type: 'syntax', solution: '修复语法错误' },
        { pattern: /Cannot find module/i, type: 'module', solution: '安装缺失的模块' },
        { pattern: /test.*?failed/i, type: 'test', solution: '修复测试失败' },
      ];

      for (const { pattern, type, solution } of errorPatterns) {
        if (pattern.test(result.stderr)) {
          // 记录错误
          this.trackError(result.stderr, context);

          // 检查是否重复
          if (this.isRepetitiveError(result.stderr)) {
            return {
              type: 'repetitive-error',
              title: `重复错误: ${type}`,
              error: result.stderr,
              solution: solution,
              context: {
                tool: toolName,
                command: context.lastCommand
              },
              agent: context.currentAgent || 'unknown',
              priority: 'P0',
              tags: [type, 'repetitive', 'error']
            };
          }
        }
      }
    }

    // 检测三次失败模式
    if (this.hasTripleFailure(context)) {
      return {
        type: 'triple-failure',
        title: '三次失败：需要替代方案',
        error: '连续三次尝试失败',
        solution: '重新审视假设，考虑替代实现',
        context: {
          attempts: this.getRecentAttempts(context)
        },
        agent: context.currentAgent || 'unknown',
        priority: 'P0',
        tags: ['systematic-debugging', 'alternative-approach']
      };
    }

    return null;
  },

  /**
   * 追踪错误
   */
  trackError(error, context) {
    const errorHash = this.hashError(error);

    this.state.errorCounts.set(errorHash, {
      count: (this.state.errorCounts.get(errorHash)?.count || 0) + 1,
      firstSeen: this.state.errorCounts.get(errorHash)?.firstSeen || Date.now(),
      lastSeen: Date.now(),
      error: error,
      context: context
    });

    // 记录最近的错误
    this.state.lastErrors.push({
      error: error,
      context: context,
      timestamp: Date.now()
    });

    // 只保留最近10个错误
    if (this.state.lastErrors.length > 10) {
      this.state.lastErrors.shift();
    }
  },

  /**
   * 检查是否重复错误
   */
  isRepetitiveError(error) {
    const errorHash = this.hashError(error);
    const errorData = this.state.errorCounts.get(errorHash);

    return errorData && errorData.count >= this.config.minRetryCount;
  },

  /**
   * 检查是否三次失败
   */
  hasTripleFailure(context) {
    const recentAttempts = this.getRecentAttempts(context);
    const failedAttempts = recentAttempts.filter(attempt =>
      attempt.status === 'failed'
    );

    return failedAttempts.length >= 3;
  },

  /**
   * 获取最近的尝试
   */
  getRecentAttempts(context) {
    // 从context中提取最近的工具调用结果
    const recentCalls = context.recentCalls || [];
    return recentCalls.slice(-5).map(call => ({
      tool: call.toolName,
      status: call.error ? 'failed' : 'success',
      timestamp: call.timestamp
    }));
  },

  /**
   * 错误哈希（用于去重）
   */
  hashError(error) {
    // 提取错误的关键部分作为哈希
    const keyParts = error
      .replace(/\d+/g, 'N') // 替换数字
      .replace(/[a-f0-9]{8,}/gi, 'HEX') // 替换哈希值
      .replace(/\/.*?\//g, 'PATH') // 替换路径
      .split('\n')[0]; // 只取第一行

    return keyParts.substring(0, 100);
  },

  /**
   * 提取标签
   */
  extractTags(text) {
    const tags = [];

    // 技术标签
    const techTags = ['react', 'typescript', 'node', 'python', 'git', 'docker'];
    techTags.forEach(tag => {
      if (text.toLowerCase().includes(tag)) {
        tags.push(tag);
      }
    });

    // 问题类型标签
    const typeTags = ['error', 'warning', 'performance', 'security', 'architecture'];
    typeTags.forEach(tag => {
      if (text.toLowerCase().includes(tag)) {
        tags.push(tag);
      }
    });

    return tags;
  },

  /**
   * 质量门槛验证（四条铁律）
   */
  passesQualityGates(lesson) {
    // 1. 需要发现：非显而易见的解决方案
    const isNonObvious = !this.isObvious(lesson);
    if (!isNonObvious) {
      return false;
    }

    // 2. 可复用：有助于未来任务
    const isReusable = this.isReusable(lesson);
    if (!isReusable) {
      return false;
    }

    // 3. 明确触发条件：具体错误/症状
    const hasTriggers = this.hasTriggers(lesson);
    if (!hasTriggers) {
      return false;
    }

    // 4. 已验证：实际有效
    const isVerified = this.isVerified(lesson);
    if (!isVerified) {
      return false;
    }

    return true;
  },

  /**
   * 检查是否显而易见
   */
  isObvious(lesson) {
    const obviousPatterns = [
      /^安装.*/, // "安装xxx"
      /^运行.*/, // "运行xxx"
      /^检查.*/, // "检查xxx"
      /^重启.*/  // "重启xxx"
    ];

    return obviousPatterns.some(pattern =>
      pattern.test(lesson.solution || '')
    );
  },

  /**
   * 检查是否可复用
   */
  isReusable(lesson) {
    // 必须有明确的错误模式和解决方案
    return !!(lesson.error && lesson.solution);
  },

  /**
   * 检查是否有明确触发条件
   */
  hasTriggers(lesson) {
    // 必须有具体的错误信息或纠正内容
    return !!(lesson.error || lesson.correction);
  },

  /**
   * 检查是否已验证
   */
  isVerified(lesson) {
    // 用户纠正或三次失败都视为已验证
    return lesson.type === 'user-correction' ||
           lesson.type === 'triple-failure' ||
           lesson.type === 'repetitive-error';
  },

  /**
   * 追加经验教训到lessons.md
   */
  appendLesson(lesson) {
    // V9.0: 把 lessonEntry 提到外层，供 Obsidian 双写复用
    let lessonEntry = '';
    try {
      // 确保lessons.md存在
      if (!fs.existsSync(this.config.lessonsPath)) {
        this.createLessonsFile();
      }

      // 生成经验教训条目
      lessonEntry = this.formatLessonEntry(lesson);

      // 追加到文件
      fs.appendFileSync(this.config.lessonsPath, lessonEntry + '\n\n');

      console.log(`✅ LessonsLogger: 已记录经验教训 - ${lesson.title}`);

    } catch (error) {
      console.error(`❌ LessonsLogger: 写入失败 - ${error.message}`);
      return; // 主流程失败，不双写
    }

    // V9.0: 双写 - 同步到 Obsidian Vault 的 10-Areas/Dragon-Engine/Lessons/
    // 失败兜底：不影响主流程
    try {
      const writer = getWriter();
      writer.write({
        type: 'lesson',
        title: lesson.title,
        content: lessonEntry,
        area: 'Dragon-Engine',
        tags: ['dragon-engine', 'auto-extracted', ...(lesson.tags || [])],
        meta: {
          source: 'lessons-logger',
          confidence: 0.6,
          agent: lesson.agent || 'unknown',
        },
      }).then(r => {
        console.log(`📚 Obsidian 双写: ${r.path} (mode=${r.mode})`);
      }).catch(e => {
        console.error(`❌ Obsidian 双写失败: ${e.message}`);
      });
    } catch (e) {
      console.error(`❌ Obsidian 双写初始化失败: ${e.message}`);
    }
  },

  /**
   * 格式化经验教训条目
   */
  formatLessonEntry(lesson) {
    const now = new Date().toISOString().split('T')[0];
    const tags = lesson.tags.map(t => `#${t}`).join(' ');

    return `
### [${lesson.type.toUpperCase()}] ${lesson.title}

**日期**: ${now}
**Agent**: ${lesson.agent}
**优先级**: ${lesson.priority}
**标签**: ${tags}

**问题**:
${this.wrapText(lesson.error || lesson.correction, 80)}

**解决方案**:
${this.wrapText(lesson.solution, 80)}

**上下文**:
\`\`\`
${JSON.stringify(lesson.context, null, 2)}
\`\`\`

**记录方式**: ${lesson.type}
`;
  },

  /**
   * 文本换行
   */
  wrapText(text, width) {
    if (!text) return '无';
    return text.match(new RegExp(`.{1,${width}}`, 'g'))?.join('\n') || text;
  },

  /**
   * 创建lessons.md文件（如果不存在）
   */
  createLessonsFile() {
    const initialContent = `# Lessons Learned - 系统经验教训库

> **目的**: 集中存储AI Agent在执行过程中学到的经验教训，避免重复错误，持续优化性能
>
> **维护**: 自动由 \`lessons-logger.js\` Hook 维护，也可手动编辑
>
> **版本**: 1.0.0
>
> **创建**: ${new Date().toISOString().split('T')[0]}

---

## 📋 说明

此文件由 \`lessons-logger.js\` Hook 自动维护，记录：
- 用户纠正的问题
- 重复出现的错误
- 三次失败后的模式
- 验证有效的最佳实践

每个条目包含：
- 问题描述
- 解决方案
- 触发条件
- 相关上下文

---

## 📚 经验教训条目

`;
    fs.writeFileSync(this.config.lessonsPath, initialContent, 'utf8');
  }
};

/**
 * 使用说明
 *
 * 1. 将此文件放入 $CLAUDE/hooks/ 目录
 * 2. 在 hooks.json 中注册：
 *    {
 *      "postToolUse": "./lessons-logger.js",
 *      "userPromptSubmit": "./lessons-logger.js"
 *    }
 * 3. 重启Claude Code
 *
 * 预期效果：
 * - 自动记录用户纠正
 * - 自动检测重复错误
 * - 自动记录三次失败模式
 * - 构建持续改进的知识库
 *
 * 质量门槛（四条铁律）：
 * - 需要发现：非显而易见的解决方案
 * - 可复用：有助于未来任务
 * - 明确触发条件：具体错误/症状
 * - 已验证：实际有效
 */
