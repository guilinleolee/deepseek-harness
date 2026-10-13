/**
 * Search List 过滤器
 * 搜索结果列表精简
 */
function compressSearchList(output) {
  const lines = output.split('\n');
  const result = [];
  const seen = new Set();

  for (const line of lines) {
    const key = line.split('→')[0]?.trim() || line;
    if (!seen.has(key)) {
      seen.add(key);
      result.push(line);
    }
  }

  return result.join('\n');
}

module.exports = compressSearchList;