#!/usr/bin/env node

/**
 * 九部天龙 - 静态代码分析器
 *
 * 模拟06审查师和05安全师的静态检查功能
 * 无需外部依赖，可直接在Git钩子中运行
 */

const fs = require('fs');

/**
 * 06审查师 - 代码质量检查
 */
function codeReviewCheck(content, filePath) {
  const issues = [];
  const warnings = [];

  const lines = content.split('\n');

  // 检查1: 函数长度
  let currentFunction = null;
  let functionStart = 0;
  let braceCount = 0;

  lines.forEach((line, index) => {
    const trimmed = line.trim();
    const lineNum = index + 1;

    // 检测函数开始
    if (trimmed.match(/^function\s+\w+/) ||
        trimmed.match(/^const\s+\w+\s*=\s*\(/) ||
        trimmed.match(/^class\s+\w+/)) {
      currentFunction = trimmed;
      functionStart = lineNum;
      braceCount = (line.match(/\{/g) || []).length -
                   (line.match(/\}/g) || []).length;
    }

    // 跟踪大括号
    if (currentFunction) {
      braceCount += (line.match(/\{/g) || []).length;
      braceCount -= (line.match(/\}/g) || []).length;

      // 函数结束
      if (braceCount === 0) {
        const funcLength = lineNum - functionStart;
        if (funcLength > 50) {
          warnings.push({
            line: functionStart,
            type: 'function_length',
            message: `${currentFunction} 过长 (${funcLength}行)，建议拆分`,
            severity: 'warning'
          });
        }
        currentFunction = null;
      }
    }

    // 检查2: 复杂表达式
    if (line.length > 120) {
      warnings.push({
        line: lineNum,
        type: 'line_length',
        message: `代码行过长 (${line.length}字符)，建议拆分`,
        severity: 'warning'
      });
    }

    // 检查3: 魔法数字
    const magicNumbers = line.match(/\b\d{2,}\b/g);
    if (magicNumbers && !trimmed.match(/\/\/|\/\*/)) {
      magicNumbers.forEach(num => {
        warnings.push({
          line: lineNum,
          type: 'magic_number',
          message: `发现魔法数字: ${num}，建议使用常量`,
          severity: 'info'
        });
      });
    }

    // 检查4: console.log
    if (trimmed.match(/console\.(log|debug|info)/)) {
      warnings.push({
        line: lineNum,
        type: 'console_log',
        message: '生产代码中不应有console.log',
        severity: 'warning'
      });
    }

    // 检查5: any类型
    if (trimmed.match(/:\s*any\b/)) {
      issues.push({
        line: lineNum,
        type: 'any_type',
        message: '避免使用any类型',
        severity: 'error'
      });
    }
  });

  return { issues, warnings };
}

/**
 * 05安全师 - 安全检查
 */
function securityCheck(content, filePath) {
  const vulnerabilities = [];

  const lines = content.split('\n');

  lines.forEach((line, index) => {
    const trimmed = line.trim();
    const lineNum = index + 1;

    // 检查1: eval
    if (trimmed.match(/\beval\(/)) {
      vulnerabilities.push({
        line: lineNum,
        type: 'eval_usage',
        severity: 'critical',
        message: '使用eval()存在代码注入风险',
        cwe: 'CWE-95'
      });
    }

    // 检查2: innerHTML
    if (trimmed.match(/\.innerHTML\s*=/)) {
      vulnerabilities.push({
        line: lineNum,
        type: 'xss_risk',
        severity: 'high',
        message: '直接设置innerHTML存在XSS风险',
        cwe: 'CWE-79'
      });
    }

    // 检查3: 硬编码密钥
    if (trimmed.match(/(api|secret|key|token)\s*[:=]\s*['"][\w-]+['"]/i)) {
      vulnerabilities.push({
        line: lineNum,
        type: 'hardcoded_secrets',
        severity: 'critical',
        message: '可能包含硬编码的密钥或Token',
        cwe: 'CWE-798'
      });
    }

    // 检查4: SQL注入风险
    if (trimmed.match(/\$\{.*\}/) && trimmed.match(/SELECT|INSERT|UPDATE|DELETE/i)) {
      vulnerabilities.push({
        line: lineNum,
        type: 'sql_injection',
        severity: 'high',
        message: '可能存在SQL注入风险，使用参数化查询',
        cwe: 'CWE-89'
      });
    }

    // 检查5: 正则表达式ReDoS
    if (trimmed.match(/\/\/.*\([\)\*\+\[\{]/)) {
      vulnerabilities.push({
        line: lineNum,
        type: 'redos_risk',
        severity: 'medium',
        message: '正则表达式可能导致ReDoS攻击',
        cwe: 'CWE-1333'
      });
    }
  });

  return vulnerabilities;
}

/**
 * 生成修复建议
 */
function generateSuggestions(issues, vulnerabilities) {
  const suggestions = [];

  const seen = new Set();

  [...issues, ...vulnerabilities].forEach(item => {
    const key = `${item.type}-${item.message}`;
    if (seen.has(key)) return;
    seen.add(key);

    switch (item.type) {
      case 'function_length':
        suggestions.push('将长函数拆分为多个小函数（单一职责）');
        break;
      case 'line_length':
        suggestions.push('将长行拆分为多行，提高可读性');
        break;
      case 'magic_number':
        suggestions.push('使用命名常量替代魔法数字');
        break;
      case 'console_log':
        suggestions.push('移除console.log或使用logger');
        break;
      case 'any_type':
        suggestions.push('使用具体类型或unknown替代any');
        break;
      case 'eval_usage':
        suggestions.push('移除eval()，使用安全的替代方案');
        break;
      case 'xss_risk':
        suggestions.push('使用textContent或DOMPurify净化');
        break;
      case 'hardcoded_secrets':
        suggestions.push('使用环境变量存储密钥');
        break;
      case 'sql_injection':
        suggestions.push('使用参数化查询或ORM');
        break;
      case 'redos_risk':
        suggestions.push('优化正则表达式，避免嵌套量词');
        break;
    }
  });

  return suggestions;
}

/**
 * 主函数
 */
function main() {
  const args = process.argv.slice(2);
  const files = args.filter(f =>
    f.match(/\.(js|jsx|ts|tsx)$/) &&
    !f.match(/\.test\./) &&
    !f.match(/\.spec\./)
  );

  if (files.length === 0) {
    console.log('✅ 没有需要检查的文件');
    return 0;
  }

  console.log(`\n🤖 九部天龙智能审查`);
  console.log(`📁 检查 ${files.length} 个文件...\n`);

  let totalIssues = 0;
  let totalWarnings = 0;
  let totalVulnerabilities = 0;
  let criticalVulns = 0;

  const allSuggestions = new Set();

  files.forEach(file => {
    try {
      const content = fs.readFileSync(file, 'utf8');

      // 06审查师检查
      const { issues, warnings } = codeReviewCheck(content, file);
      totalIssues += issues.length;
      totalWarnings += warnings.length;

      // 05安全师检查
      const vulnerabilities = securityCheck(content, file);
      totalVulnerabilities += vulnerabilities.length;
      criticalVulns += vulnerabilities.filter(v => v.severity === 'critical').length;

      // 显示结果
      if (issues.length > 0 || warnings.length > 0 || vulnerabilities.length > 0) {
        console.log(`📄 ${file}:`);

        [...issues, ...warnings].forEach(item => {
          const icon = item.severity === 'error' ? '❌' : '⚠️';
          console.log(`  ${icon} L${item.line}: ${item.message}`);
        });

        vulnerabilities.forEach(item => {
          const icon = item.severity === 'critical' ? '🚨' : '⚠️';
          console.log(`  ${icon} L${item.line}: ${item.message} [${item.cwe || 'SEC'}]`);
        });

        // 收集建议
        const suggestions = generateSuggestions(issues, vulnerabilities);
        suggestions.forEach(s => allSuggestions.add(s));
      }
    } catch (err) {
      console.log(`⚠️  ${file}: 读取失败 - ${err.message}`);
    }
  });

  // 总结
  console.log(`\n📊 检查结果:`);
  console.log(`  代码质量: ${totalIssues} 错误, ${totalWarnings} 警告`);
  console.log(`  安全检查: ${totalVulnerabilities} 问题 (${criticalVulns} 严重)`);

  // 判断是否通过
  if (criticalVulns > 0) {
    console.log(`\n🚨 严重安全漏洞阻止提交`);
    if (allSuggestions.size > 0) {
      console.log(`\n💡 修复建议:`);
      Array.from(allSuggestions).slice(0, 5).forEach((s, i) => {
        console.log(`  ${i + 1}. ${s}`);
      });
    }
    console.log(`\n使用 git commit --no-verify 跳过检查\n`);
    return 1;
  }

  if (totalIssues > 0) {
    console.log(`\n❌ 代码质量问题阻止提交`);
    if (allSuggestions.size > 0) {
      console.log(`\n💡 修复建议:`);
      Array.from(allSuggestions).slice(0, 5).forEach((s, i) => {
        console.log(`  ${i + 1}. ${s}`);
      });
    }
    console.log(`\n使用 git commit --no-verify 跳过检查\n`);
    return 1;
  }

  if (totalWarnings > 0 || totalVulnerabilities > 0) {
    console.log(`\n⚠️  存在警告，但允许提交`);
  } else {
    console.log(`\n✅ 所有检查通过`);
  }

  console.log('');
  return 0;
}

const exitCode = main();
process.exit(exitCode);
