/**
 * 日志去重过滤器
 * dedup-log: 合并重复行
 * 来源: decolua/9router
 */

/**
 * 压缩日志输出
 * @param {string} output - 原始日志输出
 * @returns {string} 去重后输出
 */
function compressDedupLog(output) {
  const lines = output.split('\n');
  const result = [];
  let lastLine = null;
  let dupCount = 0;

  for (const line of lines) {
    // 保留空行
    if (line.trim() === '') {
      if (dupCount > 0) {
        result.push(`  [repeated ${dupCount} times]`);
        dupCount = 0;
      }
      result.push(line);
      lastLine = null;
      continue;
    }

    // 检测重复
    if (line === lastLine) {
      dupCount++;
    } else {
      if (dupCount > 0) {
        result.push(`  [repeated ${dupCount} times]`);
        dupCount = 0;
      }
      result.push(line);
      lastLine = line;
    }
  }

  if (dupCount > 0) {
    result.push(`  [repeated ${dupCount} times]`);
  }

  return result.join('\n');
}

module.exports = compressDedupLog;