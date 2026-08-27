#!/usr/bin/env node

/**
 * 九部天龙 - 代码注释覆盖率检查器
 *
 * 检查JavaScript/TypeScript文件的注释覆盖率
 * 不达标的文件将阻止Git提交
 */

const fs = require('fs');
const path = require('path');

/**
 * 计算单个文件的注释覆盖率
 */
function checkComments(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split('\n');

    let codeLines = 0;
    let commentLines = 0;
    let inBlockComment = false;

    lines.forEach(line => {
      const trimmed = line.trim();

      // 空行跳过
      if (trimmed.length === 0) return;

      // 块注释开始
      if (trimmed.startsWith('/*')) {
        inBlockComment = true;
      }

      // 块注释中
      if (inBlockComment) {
        commentLines++;
        if (trimmed.endsWith('*/')) {
          inBlockComment = false;
        }
        return;
      }

      // 单行注释
      if (trimmed.startsWith('//') || trimmed.startsWith('*') || trimmed.startsWith('/*')) {
        commentLines++;
        return;
      }

      // 代码行
      codeLines++;
    });

    if (codeLines === 0) return { coverage: 1.0, codeLines: 0, commentLines: 0 };

    return {
      coverage: commentLines / (codeLines + commentLines),
      codeLines,
      commentLines,
      totalLines: codeLines + commentLines
    };
  } catch (err) {
    return { error: err.message };
  }
}

/**
 * 主函数
 */
function main() {
  const args = process.argv.slice(2);
  const minCoverage = parseFloat(process.env.COMMENT_MIN_COVERAGE || '0.2');
  const changedFiles = args.filter(f =>
    f.match(/\.(js|jsx|ts|tsx)$/) &&
    !f.match(/\.test\./) &&
    !f.match(/\.spec\./) &&
    !f.includes('node_modules')
  );

  if (changedFiles.length === 0) {
    console.log('✅ 没有需要检查的代码文件');
    return 0;
  }

  console.log(`\n📝 检查 ${changedFiles.length} 个文件的注释覆盖率...`);
  console.log(`🎯 要求覆盖率: ${(minCoverage * 100).toFixed(0)}%\n`);

  let totalCoverage = 0;
  let fileCount = 0;
  let failedFiles = [];

  changedFiles.forEach(file => {
    const result = checkComments(file);

    if (result.error) {
      console.log(`⚠️  ${file}: 检查失败 - ${result.error}`);
      return;
    }

    totalCoverage += result.coverage;
    fileCount++;

    const percentage = (result.coverage * 100).toFixed(1);
    const status = result.coverage >= minCoverage ? '✅' : '❌';

    console.log(`${status} ${file}: ${percentage}% (${result.commentLines}/${result.totalLines} 行)`);

    if (result.coverage < minCoverage) {
      failedFiles.push({ file, coverage: result.coverage, required: minCoverage });
    }
  });

  if (fileCount === 0) {
    console.log('\n✅ 所有文件跳过检查');
    return 0;
  }

  const avgCoverage = totalCoverage / fileCount;
  console.log(`\n📊 平均注释覆盖率: ${(avgCoverage * 100).toFixed(1)}%`);

  if (failedFiles.length > 0) {
    console.log(`\n❌ ${failedFiles.length} 个文件未达标:\n`);
    failedFiles.forEach(({ file, coverage, required }) => {
      console.log(`  - ${path.basename(file)}`);
      console.log(`    当前: ${(coverage * 100).toFixed(1)}%, 要求: ${(required * 100).toFixed(0)}%`);
    });
    console.log('\n💡 提示: 请添加注释后重试,或使用 git commit --no-verify 跳过检查\n');
    return 1;
  }

  console.log('\n✅ 所有文件注释覆盖率达标\n');
  return 0;
}

const exitCode = main();
process.exit(exitCode);
