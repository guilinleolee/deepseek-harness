
/**
 * prompt-submit Hook
 * 用途：提交prompt时提取写作事实
 * 触发时机：用户每次提交prompt后
 * 超时保护：30秒
 */

const fs = require('fs');
const path = require('path');

// 配置
const CONFIG = {
  timeout: 30000,
  memoryPath: path.join(process.env.HOME || process.env.USERPROFILE, '.claude', 'writing-memory'),
  factPatterns: {
    // 写作相关关键词
    writing: ['写', '文章', '标题', '大纲', '正文', '排版', '发布'],
    // 方法论相关
    methods: ['方法', '技巧', '策略', '原理', '公式'],
    // 数据相关
    metrics: ['数据', '表现', '转化', '阅读', '转发'],
    // 受众相关
    audience: ['读者', '用户', '受众', '人群']
  }
};

/**
 * 提取写作事实
 * @param {string} prompt - 用户输入的prompt
 * @returns {Array} 提取的事实列表
 */
function extractFacts(prompt) {
  const facts = [];
  const startTime = Date.now();

  try {
    // 超时保护
    if (Date.now() - startTime > CONFIG.timeout) {
      throw new Error('提取事实超时');
    }

    const lowerPrompt = prompt.toLowerCase();

    // 1. 检测写作意图
    const hasWritingIntent = CONFIG.factPatterns.writing.some(keyword =>
      lowerPrompt.includes(keyword)
    );

    if (hasWritingIntent) {
      facts.push({
        type: 'writing_intent',
        confidence: 0.9,
        evidence: '检测到写作相关关键词',
        timestamp: new Date().toISOString()
      });
    }

    // 2. 提取主题（简单版：提取名词短语）
    const topicMatch = prompt.match(/(?:写|关于|一篇)([^，。？！]{2,10})(?:的文章|内容)/);
    if (topicMatch) {
      facts.push({
        type: 'topic',
        value: topicMatch[1],
        confidence: 0.8,
        timestamp: new Date().toISOString()
      });
    }

    // 3. 检测阶段（选题/大纲/正文/标题/排版）
    const stageMap = {
      '选题': '选题',
      '大纲': '大纲',
      '正文': '正文',
      '标题': '标题',
      '排版': '排版',
      '检查': '检查'
    };

    for (const [keyword, stage] of Object.entries(stageMap)) {
      if (lowerPrompt.includes(keyword)) {
        facts.push({
          type: 'writing_stage',
          value: stage,
          confidence: 0.85,
          timestamp: new Date().toISOString()
        });
        break;
      }
    }

    // 4. 检测受众提及
    const audienceMatch = prompt.match(/(?:给|面向|针对)([^，。？！]{2,8})(?:的人|读者|用户)/);
    if (audienceMatch) {
      facts.push({
        type: 'audience',
        value: audienceMatch[1],
        confidence: 0.75,
        timestamp: new Date().toISOString()
      });
    }

    // 5. 检测数据关注
    if (CONFIG.factPatterns.metrics.some(keyword => lowerPrompt.includes(keyword))) {
      facts.push({
        type: 'metrics_focus',
        confidence: 0.7,
        evidence: '提及数据指标',
        timestamp: new Date().toISOString()
      });
    }

    const extractionTime = Date.now() - startTime;

    return {
      success: true,
      facts,
      meta: {
        extractionTime,
        promptLength: prompt.length,
        factCount: facts.length
      }
    };

  } catch (err) {
    console.error('[十八子写作] ❌ 提取事实失败：', err.message);

    return {
      success: false,
      facts: [],
      error: err.message
    };
  }
}

/**
 * 保存事实到今日笔记
 * @param {Array} facts - 提取的事实列表
 */
function saveFactsToTodayNote(facts) {
  try {
    const today = new Date().toISOString().split('T')[0];
    const notesDir = path.join(CONFIG.memoryPath, 'memory');
    const notePath = path.join(notesDir, `${today}.md`);

    // 确保目录存在
    if (!fs.existsSync(notesDir)) {
      fs.mkdirSync(notesDir, { recursive: true });
    }

    // 读取或创建笔记
    let content = '';
    if (fs.existsSync(notePath)) {
      content = fs.readFileSync(notePath, 'utf-8');
    } else {
      // 从模板创建
      const templatePath = path.join(CONFIG.memoryPath, 'memory', '_template.md');
      if (fs.existsSync(templatePath)) {
        content = fs.readFileSync(templatePath, 'utf-8')
          .replace(/{{date}}/g, today)
          .replace(/{{week_progress}}/g, '第1天')
          .replace(/{{month_goal}}/g, '待设定');
      }
    }

    // 追加事实
    const timestamp = new Date().toLocaleTimeString('zh-CN');
    const factEntry = `\n\n## 📝 ${timestamp} - 自动提取\n\n`;

    const factsList = facts
      .map(f => `- **${f.type}**: ${f.value || '检测到'} (置信度: ${f.confidence || 0})`)
      .join('\n');

    fs.appendFileSync(notePath, factEntry + factsList);

    return { saved: true, path: notePath };

  } catch (err) {
    console.error('[十八子写作] ⚠️  保存事实失败：', err.message);
    return { saved: false, error: err.message };
  }
}

/**
 * Hook入口函数
 * @param {Object} context - Claude Code上下文
 * @returns {Object} Hook执行结果
 */
function hook(context) {
  try {
    // 检查是否启用
    const configPath = path.join(CONFIG.memoryPath, '_config.json');
    if (!fs.existsSync(configPath)) {
      return { enabled: false, reason: 'config_missing' };
    }

    const config = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
    if (!config.hooks?.promptSubmit) {
      return { enabled: false, reason: 'hook_disabled' };
    }

    // 获取prompt
    const prompt = context?.prompt || '';
    if (!prompt || prompt.length < 5) {
      return { enabled: true, factsExtracted: 0, reason: 'prompt_too_short' };
    }

    // 1. 提取事实
    const result = extractFacts(prompt);
    let output = {
      status: 'success',
      enabled: true,
      factsExtracted: result.facts.length,
      facts: result.facts,
      meta: result.meta
    };

    // 2. 检测审稿意图
    const reviewKeywords = ['审稿', '检查', '帮我看看', '建议', '修改'];
    const isReviewMode = reviewKeywords.some(kw => prompt.toLowerCase().includes(kw));

    if (isReviewMode) {
      if (prompt.includes('老李')) {
        const LaoLi = require(path.join(CONFIG.memoryPath, 'styles', '_analyzers', 'lao-li-analyzer.js'));
        const editor = new LaoLi();
        output.promptInfusion = editor.getPromptOverlay();
        console.log('[十八子写作] 👴 老李拎着酒瓶子上场了');
      } else {
        const SeniorEditor = require(path.join(CONFIG.memoryPath, 'hooks', 'reviewer-persona.js'));
        const editor = new SeniorEditor();
        output.promptInfusion = editor.getPromptOverlay();
        console.log('[十八子写作] 🕵️ 已激活资深主编审稿模式');
      }
    }

    if (result.success && result.facts.length > 0) {
      // 保存到今日笔记
      const saveResult = saveFactsToTodayNote(result.facts);
      output.saved = saveResult.saved;
    }

    return output;

  } catch (err) {
    // 防御性编程：不阻塞用户输入
    console.error('[十八子写作] ⚠️  prompt-submit Hook异常：', err.message);

    return {
      status: 'error',
      enabled: false,
      error: err.message,
      safe: true
    };
  }
}

// 导出
module.exports = hook;

// 如果直接运行此文件
if (require.main === module) {
  const testContext = {
    prompt: '帮我写一篇关于AI写作的文章，面向新手读者',
    cwd: process.cwd(),
    env: process.env
  };

  const result = hook(testContext);
  console.log('\nHook执行结果：');
  console.log(JSON.stringify(result, null, 2));
}
