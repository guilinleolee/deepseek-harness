
/**
 * session-start Hook
 * 用途：会话开始时加载写作记忆
 * 触发时机：每次启动Claude Code时
 * 超时保护：30秒
 */

const fs = require('fs');
const path = require('path');

// V9.0: 引入天龙引擎 × Obsidian 记忆加载器（与十八子写作并存）
const MemoryLoader = require('../utility/memory-loader');

// 配置
const CONFIG = {
  timeout: 30000, // 30秒超时
  memoryPath: path.join(process.env.HOME || process.env.USERPROFILE, '.claude', 'writing-memory'),
  maxRetries: 3
};

/**
 * 加载写作记忆
 */
function loadWritingMemory() {
  const startTime = Date.now();

  try {
    // 超时保护
    if (Date.now() - startTime > CONFIG.timeout) {
      throw new Error('加载记忆超时');
    }

    // 检查记忆系统是否启用
    const configPath = path.join(CONFIG.memoryPath, '_config.json');
    if (!fs.existsSync(configPath)) {
      console.log('[十八子写作] ⚠️  写作记忆系统未初始化');
      return { enabled: false, reason: 'config_missing' };
    }

    // 读取配置
    const config = JSON.parse(fs.readFileSync(configPath, 'utf-8'));

    // 读取隐性知识
    const memoryPath = path.join(CONFIG.memoryPath, 'MEMORY.md');
    if (!fs.existsSync(memoryPath)) {
      return { enabled: false, reason: 'memory_missing' };
    }

    const memoryContent = fs.readFileSync(memoryPath, 'utf-8');

    // 读取今日笔记（如果存在）
    const today = new Date().toISOString().split('T')[0];
    const todayNotePath = path.join(CONFIG.memoryPath, 'memory', `${today}.md`);
    let todayNote = null;

    if (fs.existsSync(todayNotePath)) {
      todayNote = fs.readFileSync(todayNotePath, 'utf-8');
    }

    const loadTime = Date.now() - startTime;

    return {
      enabled: true,
      memoryLoaded: true,
      config,
      memory: {
        content: memoryContent,
        todayNote
      },
      meta: {
        loadTime,
        timestamp: new Date().toISOString(),
        version: config.version
      }
    };

  } catch (err) {
    // 防御性编程：记录错误但不阻塞会话
    console.error('[十八子写作] ❌ 加载写作记忆失败：', err.message);

    return {
      enabled: false,
      memoryLoaded: false,
      error: err.message,
      fallback: {
        message: '写作记忆系统暂时不可用，但不影响正常使用'
      }
    };
  }
}

/**
 * Hook入口函数
 * @param {Object} context - Claude Code上下文
 * @returns {Object} Hook执行结果
 */
async function hook(context) {
  try {
    const result = loadWritingMemory();

    if (result.enabled && result.memoryLoaded) {
      // 成功加载记忆，注入到上下文
      console.log(`[十八子写作] ✅ 写作记忆已加载 (${result.meta.loadTime}ms)`);

      // 将记忆内容注入到系统提示中
      if (context && context.env) {
        context.env.WRITING_MEMORY_LOADED = 'true';
        context.env.WRITING_MEMORY_VERSION = result.meta.version;
      }

      // V9.0: 同步加载天龙引擎 × Obsidian 记忆（追加到 context，不影响十八子写作流程）
      try {
        const loader = new MemoryLoader();
        const obsidianMemory = await loader.loadForContext();
        if (context && context.env) {
          context.env.OBSIDIAN_MEMORY_LOADED = 'true';
          context.env.OBSIDIAN_MEMORY_CONTENT = obsidianMemory;
        }
        console.log(`[天龙记忆] ✅ Obsidian 记忆已注入 (${obsidianMemory.length} 字符)`);
      } catch (obsidianErr) {
        // 失败兜底：不影响十八子写作
        console.error('[天龙记忆] ⚠️  Obsidian 加载失败：', obsidianErr.message);
        if (context && context.env) {
          context.env.OBSIDIAN_MEMORY_LOADED = 'false';
        }
      }

      return {
        status: 'success',
        ...result,
        injected: true
      };
    }

    // 记忆未启用或加载失败
    return result;

  } catch (err) {
    // 最终兜底：确保Hook不会阻塞Claude Code启动
    console.error('[十八子写作] ⚠️  session-start Hook异常：', err.message);

    return {
      status: 'error',
      enabled: false,
      error: err.message,
      safe: true // 标记为安全异常，不会影响主流程
    };
  }
}

// 导出
module.exports = hook;

// 如果直接运行此文件
if (require.main === module) {
  const result = hook({ cwd: process.cwd(), env: process.env });
  console.log('\nHook执行结果：');
  console.log(JSON.stringify(result, null, 2));
}
