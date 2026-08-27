/**
 * Read Numbered 过滤器
 * 行号压缩
 */
function compressReadNumbered(output) {
  return output
    .replace(/\s+(\d+)\t/g, ':$1 ')  // 行号格式简化
    .replace(/:\d+\s+/g, ' ');       // 去除多余行号
}

module.exports = compressReadNumbered;