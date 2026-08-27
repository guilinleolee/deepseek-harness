/**
 * Git Status 过滤器
 * 简化 git status 输出
 */
function compressGitStatus(output) {
  const lines = output.split('\n');
  const result = [];

  for (const line of lines) {
    // 保留分支信息
    if (line.includes('On branch') || line.includes('HEAD detached')) {
      result.push(line);
      continue;
    }

    // 简化文件状态
    if (line.startsWith('Changes not staged')) {
      result.push('📝 Unstaged changes:');
      continue;
    }
    if (line.startsWith('Changes to be committed')) {
      result.push('✅ Staged changes:');
      continue;
    }

    // 保留变更文件
    if (line.match(/^\s+[^\s]/)) {
      result.push(line.trim());
    }
  }

  return result.join('\n');
}

module.exports = compressGitStatus;