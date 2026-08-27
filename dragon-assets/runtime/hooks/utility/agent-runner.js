#!/usr/bin/env node

/**
 * 九部天龙 - Agent智能审查系统
 *
 * 在Git提交前调用agents进行代码审查
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

/**
 * 调用06审查师
 */
function runCodeReview(files) {
  try {
    console.log('🔍 06审查师: 代码质量审查...');

    // 检查是否安装了claude-code
    const claudePath = process.env.CLAUDE_CODE_PATH || 'claude';

    // 构建审查命令
    const fileList = files.join(' ');
    const command = `${claudePath} skill code-reviewer ${fileList} --strict`;

    // 执行审查（设置超时）
    const result = execSync(command, {
      encoding: 'utf8',
      stdio: 'pipe',
      timeout: 30000, // 30秒超时
      cwd: process.cwd()
    });

    // 解析结果
    const output = result.toString();
    const hasErrors = output.includes('❌') || output.includes('ERROR');
    const hasWarnings = output.includes('⚠️');

    return {
      passed: !hasErrors,
      output,
      hasWarnings,
      suggestions: extractSuggestions(output)
    };
  } catch (error) {
    // Claude Code不可用时的降级处理
    if (error.status === 127 || error.message.includes('not found')) {
      console.log('⚠️  Claude Code不可用，跳过智能审查');
      return {
        passed: true,
        skipped: true,
        output: 'Claude Code未安装'
      };
    }

    // 超时或其他错误
    return {
      passed: false,
      output: error.message,
      error: true
    };
  }
}

/**
 * 调用05安全师
 */
function runSecurityCheck(files) {
  try {
    console.log('🔒 05安全师: 安全漏洞检查...');

    const claudePath = process.env.CLAUDE_CODE_PATH || 'claude';
    const fileList = files.join(' ');
    const command = `${claudePath} skill security-reviewer ${fileList} --strict`;

    const result = execSync(command, {
      encoding: 'utf8',
      stdio: 'pipe',
      timeout: 30000,
      cwd: process.cwd()
    });

    const output = result.toString();
    const hasVulnerabilities = output.includes('🚨') || output.includes('vulnerability');

    return {
      passed: !hasVulnerabilities,
      output,
      suggestions: extractSuggestions(output)
    };
  } catch (error) {
    if (error.status === 127) {
      console.log('⚠️  Claude Code不可用，跳过安全检查');
      return {
        passed: true,
        skipped: true
      };
    }

    return {
      passed: false,
      output: error.message,
      error: true
    };
  }
}

/**
 * 提取修复建议
 */
function extractSuggestions(output) {
  const suggestions = [];
  const lines = output.split('\n');

  let inSuggestion = false;
  let currentSuggestion = null;

  lines.forEach(line => {
    // 检测建议开始
    if (line.includes('💡') || line.includes('建议:')) {
      inSuggestion = true;
      currentSuggestion = line.replace(/^[^\s]+\s*/, '').trim();
    } else if (inSuggestion && line.trim().startsWith('-')) {
      if (currentSuggestion) {
        suggestions.push(currentSuggestion);
        currentSuggestion = null;
      }
      suggestions.push(line.trim().replace(/^-\s*/, ''));
    }
  });

  if (currentSuggestion) {
    suggestions.push(currentSuggestion);
  }

  return suggestions;
}

/**
 * 主函数
 */
function main() {
  const args = process.argv.slice(2);
  const files = args.filter(f => f.match(/\.(js|jsx|ts|tsx)$/));

  if (files.length === 0) {
    console.log('✅ 没有需要审查的文件');
    return 0;
  }

  console.log(`\n🤖 九部天龙智能审查系统`);
  console.log(`📁 审查 ${files.length} 个文件...\n`);

  const results = {
    codeReview: null,
    security: null
  };

  // 读取配置
  const configPath = process.env.CODE_RULES_PATH ||
    path.join(process.env.HOME || '', '.claude/hooks/code-rules.json');

  let config = { rules: {} };
  try {
    if (fs.existsSync(configPath)) {
      config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    }
  } catch (err) {
    console.log('⚠️  无法读取配置文件');
  }

  // 运行06审查师
  if (config.rules.code_review?.enabled !== false) {
    results.codeReview = runCodeReview(files);

    if (results.codeReview.skipped) {
      console.log('⏭️  06审查师: 跳过');
    } else if (results.codeReview.passed) {
      console.log('✅ 06审查师: 通过');
      if (results.codeReview.hasWarnings) {
        console.log('⚠️  存在警告，但允许提交');
      }
    } else {
      console.log('❌ 06审查师: 未通过');
      console.log(results.codeReview.output);

      if (results.codeReview.suggestions.length > 0) {
        console.log('\n💡 修复建议:');
        results.codeReview.suggestions.forEach((s, i) => {
          console.log(`  ${i + 1}. ${s}`);
        });
      }

      return 1;
    }
  }

  // 运行05安全师
  if (config.rules.security_check?.enabled !== false) {
    results.security = runSecurityCheck(files);

    if (results.security.skipped) {
      console.log('⏭️  05安全师: 跳过');
    } else if (results.security.passed) {
      console.log('✅ 05安全师: 通过');
    } else {
      console.log('❌ 05安全师: 未通过');
      console.log(results.security.output);

      if (results.security.suggestions.length > 0) {
        console.log('\n💡 修复建议:');
        results.security.suggestions.forEach((s, i) => {
          console.log(`  ${i + 1}. ${s}`);
        });
      }

      return 1;
    }
  }

  console.log('\n✅ 所有智能审查通过\n');
  return 0;
}

const exitCode = main();
process.exit(exitCode);
