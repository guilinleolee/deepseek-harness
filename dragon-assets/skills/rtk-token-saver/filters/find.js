/**
 * Find/ls 过滤器
 * 路径压缩+排序
 * 来源: decolua/9router
 */

/**
 * 压缩 find/ls 输出
 * @param {string} output - 原始输出
 * @returns {string} 压缩后输出
 */
function compressFindLs(output) {
  const lines = output.split('\n');
  const result = [];
  const maxLines = 100; // 限制最大行数

  for (let i = 0; i < Math.min(lines.length, maxLines); i++) {
    let line = lines[i];

    // 路径压缩（简化常见前缀）
    line = line
      .replace(/\/Users\/[\w]+\//g, '~/')
      .replace(/\/home\/[\w]+\//g, '~/')
      .replace(/[a-z]:\\[\w\\]+\\/gi, (m) => m.replace(/[a-z]:\\/i, '').replace(/\\/g, '/'));

    result.push(line);
  }

  // 如果被截断，添加省略提示
  if (lines.length > maxLines) {
    result.push(`\n... ${lines.length - maxLines} more files`);
  }

  return result.join('\n');
}

module.exports = compressFindLs;