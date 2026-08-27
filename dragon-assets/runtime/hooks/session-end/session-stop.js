
/**
 * session-stop Hook
 * 用途：会话结束时更新日志
 * 触发时机：每次关闭Claude Code时
 * 超时保护：30秒
 */

const fs = require('fs');
const path = require('path');

// 配置
const CONFIG = {
  timeout: 30000,
  memoryPath: path.join(process.env.HOME || process.env.USERPROFILE, '.claude', 'writing-memory'),
  logsDir: path.join(process.env.HOME || process.env.USERPROFILE, '.claude', 'writing-memory', 'logs')
};

/**
 * 更新今日笔记
 * @param {Object} sessionData - 会话数据
 */
function updateTodayNote(sessionData) {
  const startTime = Date.now();

  try {
    // 超时保护
    if (Date.now() - startTime > CONFIG.timeout) {
      throw new Error('更新笔记超时');
    }

    const today = new Date().toISOString().split('T')[0];
    const notePath = path.join(CONFIG.memoryPath, 'memory', `${today}.md`);

    if (!fs.existsSync(notePath)) {
      return { updated: false, reason: 'note_not_exists' };
    }

    // 追加会话总结
    const timestamp = new Date().toLocaleTimeString('zh-CN');
    const sessionSummary = `
\`\`\`
## 🔄 会话结束 - ${timestamp}

- 会话时长：${Math.round(sessionData.duration / 60)} 分钟
- Prompt次数：${sessionData.promptCount || 0}
- 主要主题：${sessionData.topics?.join(', ') || '无'}
\`\`\`
`;

    fs.appendFileSync(notePath, sessionSummary);

    return {
      updated: true,
      path: notePath,
      updateTime: Date.now() - startTime
    };

  } catch (err) {
    console.error('[十八子写作] ❌ 更新今日笔记失败：', err.message);
    return { updated: false, error: err.message };
  }
}

/**
 * 更新系统日志
 * @param {Object} sessionData - 会话数据
 */
function updateSystemLog(sessionData) {
  try {
    // 确保日志目录存在
    if (!fs.existsSync(CONFIG.logsDir)) {
      fs.mkdirSync(CONFIG.logsDir, { recursive: true });
    }

    const logFile = path.join(CONFIG.logsDir, 'sessions.log');
    const logEntry = {
      timestamp: new Date().toISOString(),
      duration: sessionData.duration,
      promptCount: sessionData.promptCount || 0,
      topics: sessionData.topics || [],
      status: 'completed'
    };

    // 追加到日志文件
    const logLine = JSON.stringify(logEntry) + '\n';
    fs.appendFileSync(logFile, logLine);

    return { logged: true, path: logFile };

  } catch (err) {
    console.error('[十八子写作] ⚠️  更新系统日志失败：', err.message);
    return { logged: false, error: err.message };
  }
}

/**
 * 生成会话报告
 * @param {Object} sessionData - 会话数据
 */
function generateSessionReport(sessionData) {
  try {
    const durationMinutes = Math.round(sessionData.duration / 60);

    let report = `
## 📊 会话报告

- **时长**：${durationMinutes} 分钟
- **交互次数**：${sessionData.promptCount || 0}
- **时间**：${new Date().toLocaleString('zh-CN')}
`;

    if (sessionData.topics && sessionData.topics.length > 0) {
      report += `- **涉及主题**：${sessionData.topics.join(', ')}\n`;
    }

    // 写作建议
    if (durationMinutes > 60) {
      report += `\n💡 **建议**：已连续工作${durationMinutes}分钟，建议休息后再继续\n`;
    }

    console.log(report);

    return { generated: true, report };

  } catch (err) {
    console.error('[十八子写作] ⚠️  生成报告失败：', err.message);
    return { generated: false, error: err.message };
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
    if (!config.hooks?.sessionStop) {
      return { enabled: false, reason: 'hook_disabled' };
    }

    // 收集会话数据
    const sessionData = {
      duration: context?.sessionDuration || 0,
      promptCount: context?.promptCount || 0,
      topics: context?.topics || [],
      timestamp: new Date().toISOString()
    };

    // 更新今日笔记
    const noteResult = updateTodayNote(sessionData);

    // 更新系统日志
    const logResult = updateSystemLog(sessionData);

    // 生成报告（可选）
    const reportResult = generateSessionReport(sessionData);

    return {
      status: 'success',
      enabled: true,
      logUpdated: noteResult.updated || logResult.logged,
      results: {
        note: noteResult,
        log: logResult,
        report: reportResult
      },
      meta: {
        duration: sessionData.duration,
        timestamp: sessionData.timestamp
      }
    };

  } catch (err) {
    // 防御性编程：不阻塞正常退出
    console.error('[十八子写作] ⚠️  session-stop Hook异常：', err.message);

    return {
      status: 'error',
      enabled: false,
      error: err.message,
      safe: true // 标记为安全异常
    };
  }
}

// 导出
module.exports = hook;

// 如果直接运行此文件
if (require.main === module) {
  const testContext = {
    sessionDuration: 3600, // 1小时
    promptCount: 15,
    topics: ['AI写作', '标题优化'],
    cwd: process.cwd(),
    env: process.env
  };

  const result = hook(testContext);
  console.log('\nHook执行结果：');
  console.log(JSON.stringify(result, null, 2));
}
