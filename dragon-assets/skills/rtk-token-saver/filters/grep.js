/**
 * Grep 过滤器
 * 去重+行号优化
 * 来源: decolua/9router
 */

/**
 * 压缩 grep 输出
 * @param {string} output - 原始grep输出
 * @returns {string} 压缩后输出
 */
function compressGrep(output) {
  const lines = output.split('\n');
  const result = [];
  const seen = new Set();

  for (const line of lines) {
    // 跳过统计行（会在末尾重新生成）
    if (line.includes(' matches')) continue;

    // 提取关键信息（去除路径重复）
    const key = line.replace(/\/[\w\.\-]+\//g, '/');

    if (!seen.has(key)) {
      seen.add(key);
      result.push(line);
    }
  }

  const compressed = result.join('\n');

  // 加上匹配统计
  const matchCount = seen.size;
  const statsLine = `\n${matchCount} matches`;

  return matchCount > 0 ? compressed + statsLine : compressed;
}

module.exports = compressGrep;