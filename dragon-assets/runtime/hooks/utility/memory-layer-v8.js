
/**
 * 天龙引擎V8.0 - 记忆层Hook集成
 *
 * 功能：在会话开始时自动加载相关记忆层
 * 触发：userPromptSubmit Hook
 * 版本：v1.0-alpha
 */

const { execSync } = require('child_process');
const path = require('path');

/**
 * Hook处理器
 */
class MemoryLayerHook {
  constructor() {
    this.scriptPath = path.join(__dirname, '../memory/scripts/progressive-disclosure.js');
  }

  /**
   * 处理用户输入
   */
  handleUserInput(input) {
    try {
      // 调用渐进式披露脚本
      const memory = execSync(`node "${this.scriptPath}" "${input}"`, {
        encoding: 'utf8',
        cwd: path.join(__dirname, '..')
      });

      console.log('\n✅ 三层记忆已加载\n');
      return memory;

    } catch (error) {
      console.error('❌ 记忆加载失败:', error.message);
      return '';
    }
  }
}

// Hook入口函数
function handleUserPromptSubmit(input) {
  const hook = new MemoryLayerHook();
  return hook.handleUserInput(input);
}

// 导出
module.exports = { handleUserPromptSubmit, MemoryLayerHook };
