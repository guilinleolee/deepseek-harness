
/**
 * Hash-Anchored Edit Hook
 *
 * 基于内容哈希的稳定编辑系统，防止上下文不匹配导致的编辑错误。
 *
 * 来源: oh-my-openagent (https://github.com/code-yeongyu/oh-my-openagent)
 *
 * 核心机制:
 * 1. 读取文件时为每行添加哈希锚点 (LINE#HASH)
 * 2. 编辑时验证哈希是否匹配
 * 3. 不匹配则拒绝编辑，防止代码损坏
 */

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

// 配置
const CONFIG = {
  hashAlgorithm: 'fnv1a',
  hashLength: 2,
  maxLineLength: 50,
  enableAutoVerification: true,
  cacheEnabled: true,
  cacheTTL: 30000 // 30秒缓存
};

// 缓存
const fileCache = new Map();

/**
 * FNV-1a 哈希算法（简化版）
 * @param {string} content - 行内容
 * @returns {string} - 2-3字符哈希
 */
function computeLineHash(content) {
  const trimmed = content.trim().slice(0, CONFIG.maxLineLength);
  let hash = 2166136261; // FNV offset basis

  for (let i = 0; i < trimmed.length; i++) {
    hash ^= trimmed.charCodeAt(i);
    hash = Math.imul(hash, 16777619); // FNV prime
  }

  // 转换为36进制（0-9, A-Z）
  return (Math.abs(hash) % 46656).toString(36).toUpperCase().padStart(2, '0');
}

/**
 * 读取文件并添加哈希锚点
 * @param {string} filePath - 文件路径
 * @returns {Array<HashAnchoredLine>} - 带锚点的行数组
 */
function readFileWithAnchors(filePath) {
  const absolutePath = path.resolve(filePath);

  // 检查缓存
  if (CONFIG.cacheEnabled && fileCache.has(absolutePath)) {
    const cached = fileCache.get(absolutePath);
    if (Date.now() - cached.timestamp < CONFIG.cacheTTL) {
      return cached.lines;
    }
  }

  const content = fs.readFileSync(absolutePath, 'utf8');
  const lines = content.split('\n');

  const anchoredLines = lines.map((line, index) => {
    const hash = computeLineHash(line);
    return {
      lineNumber: index + 1,
      hash: hash,
      content: line,
      anchor: `${index + 1}#${hash}`
    };
  });

  // 更新缓存
  if (CONFIG.cacheEnabled) {
    fileCache.set(absolutePath, {
      lines: anchoredLines,
      timestamp: Date.now()
    });
  }

  return anchoredLines;
}

/**
 * 验证编辑锚点
 * @param {string} filePath - 文件路径
 * @param {string} anchor - 锚点 (LINE#HASH)
 * @returns {ValidationResult} - 验证结果
 */
function validateEdit(filePath, anchor) {
  const [lineNumStr, expectedHash] = anchor.split('#');
  const lineNum = parseInt(lineNumStr, 10);

  if (isNaN(lineNum) || !expectedHash) {
    return {
      valid: false,
      error: `Invalid anchor format: ${anchor}. Expected: LINE#HASH`
    };
  }

  const lines = readFileWithAnchors(filePath);

  if (lineNum < 1 || lineNum > lines.length) {
    return {
      valid: false,
      error: `Line ${lineNum} out of range (1-${lines.length})`
    };
  }

  const targetLine = lines[lineNum - 1];
  const actualHash = computeLineHash(targetLine.content);

  if (actualHash !== expectedHash) {
    return {
      valid: false,
      error: `Hash mismatch for anchor ${anchor}. Expected: ${expectedHash}, Actual: ${actualHash}. File may have changed.`,
      currentAnchor: `${lineNum}#${actualHash}`,
      suggestion: 'Please re-read the file to get updated anchors.'
    };
  }

  return {
    valid: true,
    line: targetLine
  };
}

/**
 * 执行带锚点的编辑
 * @param {string} filePath - 文件路径
 * @param {string} anchor - 锚点
 * @param {string} newContent - 新内容
 * @param {Object} options - 选项
 * @returns {EditResult} - 编辑结果
 */
function executeEdit(filePath, anchor, newContent, options = {}) {
  const absolutePath = path.resolve(filePath);
  const { dryRun = false, validateOnly = false } = options;

  // 验证锚点
  const validation = validateEdit(absolutePath, anchor);
  if (!validation.valid) {
    return {
      success: false,
      error: validation.error,
      suggestion: validation.suggestion
    };
  }

  if (validateOnly) {
    return {
      success: true,
      validated: true,
      line: validation.line
    };
  }

  const [lineNumStr] = anchor.split('#');
  const lineNum = parseInt(lineNumStr, 10);

  // 读取当前内容
  const content = fs.readFileSync(absolutePath, 'utf8');
  const lines = content.split('\n');

  // 备份原始行（用于回滚）
  const originalLine = lines[lineNum - 1];

  if (dryRun) {
    return {
      success: true,
      dryRun: true,
      original: originalLine,
      modified: newContent,
      anchor: anchor
    };
  }

  // 执行编辑
  lines[lineNum - 1] = newContent;

  try {
    fs.writeFileSync(absolutePath, lines.join('\n'), 'utf8');

    // 清除缓存
    fileCache.delete(absolutePath);

    return {
      success: true,
      edited: true,
      anchor: anchor,
      originalLine: originalLine,
      newLine: newContent,
      newAnchor: `${lineNum}#${computeLineHash(newContent)}`
    };
  } catch (error) {
    // 尝试回滚
    lines[lineNum - 1] = originalLine;
    try {
      fs.writeFileSync(absolutePath, lines.join('\n'), 'utf8');
    } catch (rollbackError) {
      console.error('Rollback failed:', rollbackError);
    }

    return {
      success: false,
      error: `Write failed: ${error.message}`,
      rollback: true
    };
  }
}

/**
 * 批量编辑
 * @param {string} filePath - 文件路径
 * @param {Array<BatchEdit>} edits - 编辑数组 [{anchor, newContent}]
 * @param {Object} options - 选项
 * @returns {BatchEditResult} - 批量编辑结果
 */
function executeBatchEdit(filePath, edits, options = {}) {
  const absolutePath = path.resolve(filePath);
  const results = [];
  let allValid = true;

  // 先验证所有编辑
  for (const edit of edits) {
    const validation = validateEdit(absolutePath, edit.anchor);
    results.push({
      anchor: edit.anchor,
      valid: validation.valid,
      error: validation.error
    });
    if (!validation.valid) {
      allValid = false;
    }
  }

  if (!allValid) {
    return {
      success: false,
      results: results,
      error: 'Some anchors are invalid. No changes were made.'
    };
  }

  // 按行号倒序排序（从后往前编辑，避免行号变化）
  const sortedEdits = [...edits].sort((a, b) => {
    const lineA = parseInt(a.anchor.split('#')[0], 10);
    const lineB = parseInt(b.anchor.split('#')[0], 10);
    return lineB - lineA;
  });

  // 执行编辑
  const content = fs.readFileSync(absolutePath, 'utf8');
  const lines = content.split('\n');
  const originalLines = [...lines];

  for (const edit of sortedEdits) {
    const [lineNumStr] = edit.anchor.split('#');
    const lineNum = parseInt(lineNumStr, 10);
    lines[lineNum - 1] = edit.newContent;
  }

  if (options.dryRun) {
    return {
      success: true,
      dryRun: true,
      editCount: edits.length,
      results: results
    };
  }

  try {
    fs.writeFileSync(absolutePath, lines.join('\n'), 'utf8');
    fileCache.delete(absolutePath);

    return {
      success: true,
      editCount: edits.length,
      results: results
    };
  } catch (error) {
    // 回滚
    try {
      fs.writeFileSync(absolutePath, originalLines.join('\n'), 'utf8');
    } catch (rollbackError) {
      console.error('Rollback failed:', rollbackError);
    }

    return {
      success: false,
      error: `Write failed: ${error.message}`,
      rollback: true
    };
  }
}

/**
 * 格式化输出带锚点的文件
 * @param {string} filePath - 文件路径
 * @returns {string} - 格式化的输出
 */
function formatFileWithAnchors(filePath) {
  const lines = readFileWithAnchors(filePath);
  const fileName = path.basename(filePath);

  let output = `📄 ${fileName} (Hash-Anchored View)\n`;
  output += `${'='.repeat(50)}\n\n`;

  for (const line of lines) {
    output += `${line.anchor}| ${line.content}\n`;
  }

  output += `\n${'='.repeat(50)}\n`;
  output += `Anchors: ${lines.length} lines, Hash algorithm: FNV-1a (${CONFIG.hashLength}-char)`;

  return output;
}

/**
 * Hook主函数
 * @param {Object} context - Hook上下文
 */
function hashAnchoredEditHook(context) {
  const { toolName, toolInput } = context;

  // 只处理Edit工具
  if (toolName !== 'Edit') {
    return;
  }

  // 检查是否启用了Hash-Anchored模式
  if (!process.env.HASH_ANCHORED_MODE && !context.flags?.hashAnchored) {
    return;
  }

  const { file_path, old_string, new_string } = toolInput;

  // 验证old_string是否包含锚点
  const anchorMatch = old_string.match(/^(\d+#\w{2,3})\|?\s*/);

  if (anchorMatch) {
    const anchor = anchorMatch[1];
    const actualOldString = old_string.replace(anchorMatch[0], '');

    const validation = validateEdit(file_path, anchor);

    if (!validation.valid) {
      console.warn(`\n⚠️  Hash-Anchored Edit Warning:`);
      console.warn(`   ${validation.error}`);
      if (validation.suggestion) {
        console.warn(`   💡 ${validation.suggestion}`);
      }
      console.warn(`\n   Use /hash-read ${file_path} to get updated anchors.\n`);
    }
  }
}

// 导出
module.exports = {
  computeLineHash,
  readFileWithAnchors,
  validateEdit,
  executeEdit,
  executeBatchEdit,
  formatFileWithAnchors,
  hashAnchoredEditHook,
  CONFIG
};