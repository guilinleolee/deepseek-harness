/**
 * 智能截断过滤器
 * 大文件输出智能截断+摘要
 * 来源: decolua/9router
 */

/**
 * 智能截断大输出
 * @param {string} output - 原始输出
 * @param {number} maxLength - 最大长度（默认10KB）
 * @returns {string} 截断后输出
 */
function smartTruncate(output, maxLength = 10240) {
  if (output.length <= maxLength) {
    return output;
  }

  const lines = output.split('\n');
  const result = [];
  let currentLength = 0;

  // 从头尾各取一部分
  const headLines = Math.min(50, lines.length);
  const tailLines = Math.min(30, lines.length);

  // 添加头部
  for (let i = 0; i < headLines; i++) {
    if (currentLength + lines[i].length > maxLength * 0.7) break;
    result.push(lines[i]);
    currentLength += lines[i].length + 1;
  }

  // 添加省略标记
  const omitted = lines.length - headLines - tailLines;
  if (omitted > 0) {
    result.push(`\n... [${omitted} lines omitted] ...\n`);
    currentLength += 50;
  }

  // 添加尾部
  for (let i = lines.length - tailLines; i < lines.length; i++) {
    if (currentLength + lines[i].length > maxLength) break;
    result.push(lines[i]);
  }

  return result.join('\n');
}

module.exports = smartTruncate;