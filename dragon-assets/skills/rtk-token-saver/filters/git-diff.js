/**
 * Git Diff 过滤器
 * 去除上下文行，仅保留变更
 * 来源: decolua/9router
 */

/**
 * 压缩 git diff 输出
 * @param {string} output - 原始diff输出
 * @returns {string} 压缩后输出
 */
function compressGitDiff(output) {
  const lines = output.split('\n');
  const result = [];
  let inHunk = false;
  let hunkHeader = null;

  for (const line of lines) {
    // 保留文件头
    if (line.startsWith('diff --git') || line.startsWith('index ') || line.startsWith('---')) {
      result.push(line);
      continue;
    }

    // 保留hunk头
    if (line.startsWith('@@')) {
      inHunk = true;
      hunkHeader = line;
      result.push(line);
      continue;
    }

    // 在hunk内
    if (inHunk) {
      // 保留变更行
      if (line.startsWith('+') || line.startsWith('-')) {
        result.push(line);
      }
      // 空行保留（保持结构）
      else if (line.trim() === '') {
        result.push(line);
      }
      // 上下文行简化（只保留关键上下文）
      else if (result.length > 0 && result[result.length - 1].startsWith('+') ||
               result[result.length - 1].startsWith('-')) {
        result.push(line);
      }
    }
  }

  // 如果压缩效果不好，返回原始
  const compressed = result.join('\n');
  if (compressed.length > output.length * 0.9) {
    return output;
  }

  return compressed;
}

module.exports = compressGitDiff;