#!/usr/bin/env node

/**
 * Git提交信息验证工具
 * 用于验证Git提交信息是否符合规范格式
 */

const fs = require('fs');
const path = require('path');

class GitCommitValidator {
  constructor(configPath = null) {
    this.config = this.loadConfig(configPath);
  }

  loadConfig(configPath) {
    const defaultConfig = {
      format: 'conventional',
      types: ['feat', 'fix', 'docs', 'style', 'refactor', 'test', 'chore', 'perf', 'ci', 'build'],
      scopes: [],
      maxLength: 100,
      requireScope: false,
      requireDescription: true,
      maxLineLength: 72
    };

    if (!configPath) {
      configPath = this.findConfigFile();
    }

    if (configPath && fs.existsSync(configPath)) {
      try {
        const userConfig = JSON.parse(fs.readFileSync(configPath, 'utf8'));
        return { ...defaultConfig, ...userConfig };
      } catch (error) {
        console.warn(`警告: 配置文件解析失败，使用默认配置: ${error.message}`);
      }
    }

    return defaultConfig;
  }

  findConfigFile() {
    const possiblePaths = [
      '.git-commit-standard.json',
      '.gitcommitrc.json',
      'package.json'
    ];

    for (const configPath of possiblePaths) {
      if (fs.existsSync(configPath)) {
        return configPath;
      }
    }

    return null;
  }

  validate(commitMessage) {
    const errors = [];
    const warnings = [];

    // 基本格式检查
    if (!commitMessage || commitMessage.trim().length === 0) {
      errors.push('提交信息不能为空');
      return { valid: false, errors, warnings };
    }

    // 分割标题和正文
    const lines = commitMessage.split('\n');
    const header = lines[0].trim();
    const body = lines.slice(1).join('\n').trim();

    // 检查标题长度
    if (header.length > this.config.maxLength) {
      errors.push(`标题长度不能超过 ${this.config.maxLength} 字符 (当前: ${header.length})`);
    }

    // 检查Conventional Commits格式
    if (this.config.format === 'conventional') {
      const conventionalResult = this.validateConventional(header);
      errors.push(...conventionalResult.errors);
      warnings.push(...conventionalResult.warnings);
    }

    // 检查正文行长度
    if (body) {
      const bodyLines = body.split('\n');
      for (let i = 0; i < bodyLines.length; i++) {
        const line = bodyLines[i];
        if (line.length > this.config.maxLineLength) {
          warnings.push(`第 ${i + 2} 行长度超过 ${this.config.maxLineLength} 字符 (当前: ${line.length})`);
        }
      }
    }

    // 检查描述要求
    if (this.config.requireDescription && body.length === 0) {
      warnings.push('建议添加详细的提交描述');
    }

    return {
      valid: errors.length === 0,
      errors,
      warnings,
      header,
      body
    };
  }

  validateConventional(header) {
    const errors = [];
    const warnings = [];

    // Conventional Commits正则表达式
    // <type>[optional scope]: <description>
    const conventionalRegex = /^(\w+)(?:\(([^)]+)\))?: (.+)$/i;
    const match = header.match(conventionalRegex);

    if (!match) {
      errors.push('提交信息格式不符合 Conventional Commits 规范');
      errors.push('正确格式: <type>[optional scope]: <description>');
      return { errors, warnings };
    }

    const [, type, scope, description] = match;

    // 检查类型
    if (!this.config.types.includes(type.toLowerCase())) {
      errors.push(`无效的提交类型: "${type}"`);
      errors.push(`允许的类型: ${this.config.types.join(', ')}`);
    }

    // 检查作用域
    if (scope) {
      if (this.config.scopes.length > 0 && !this.config.scopes.includes(scope)) {
        warnings.push(`未知的作用域: "${scope}"`);
        warnings.push(`已知的作用域: ${this.config.scopes.join(', ')}`);
      }
    } else if (this.config.requireScope) {
      errors.push('提交信息必须包含作用域');
    }

    // 检查描述
    if (!description || description.trim().length === 0) {
      errors.push('提交描述不能为空');
    } else {
      // 检查描述是否以小写字母开头
      if (description[0] !== description[0].toLowerCase()) {
        warnings.push('建议描述以小写字母开头');
      }

      // 检查描述是否以句号结尾
      if (description.endsWith('.')) {
        warnings.push('建议描述不以句号结尾');
      }
    }

    return { errors, warnings };
  }

  generateTemplate(type, scope = null, description = '') {
    if (!this.config.types.includes(type)) {
      throw new Error(`无效的提交类型: ${type}`);
    }

    let template = `${type}`;
    if (scope) {
      template += `(${scope})`;
    }
    template += ': ';
    if (description) {
      template += description;
    }

    return template;
  }

  interactivePrompt() {
    const readline = require('readline');
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });

    return new Promise((resolve) => {
      const questions = [
        {
          name: 'type',
          message: '选择提交类型:',
          choices: this.config.types
        },
        {
          name: 'scope',
          message: '输入作用域 (可选):',
          optional: true
        },
        {
          name: 'description',
          message: '输入描述:'
        },
        {
          name: 'body',
          message: '输入详细描述 (可选):',
          optional: true
        }
      ];

      let currentQuestion = 0;
      const answers = {};

      const askQuestion = () => {
        if (currentQuestion >= questions.length) {
          rl.close();
          resolve(answers);
          return;
        }

        const question = questions[currentQuestion];

        if (question.choices) {
          console.log(`\n${question.message}`);
          question.choices.forEach((choice, index) => {
            console.log(`  ${index + 1}. ${choice}`);
          });

          rl.question('请选择 (输入数字): ', (input) => {
            const index = parseInt(input) - 1;
            if (index >= 0 && index < question.choices.length) {
              answers[question.name] = question.choices[index];
              currentQuestion++;
              askQuestion();
            } else {
              console.log('无效选择，请重新输入');
              askQuestion();
            }
          });
        } else {
          rl.question(`${question.message} `, (input) => {
            if (input.trim() || question.optional) {
              answers[question.name] = input.trim();
              currentQuestion++;
              askQuestion();
            } else {
              console.log('此项为必填，请输入内容');
              askQuestion();
            }
          });
        }
      };

      askQuestion();
    });
  }

  formatCommitMessage(answers) {
    let commitMessage = '';

    // 构建标题
    commitMessage += `${answers.type}`;
    if (answers.scope) {
      commitMessage += `(${answers.scope})`;
    }
    commitMessage += `: ${answers.description}`;

    // 添加正文
    if (answers.body) {
      commitMessage += `\n\n${answers.body}`;
    }

    return commitMessage;
  }
}

// CLI接口
function main() {
  const args = process.argv.slice(2);
  const validator = new GitCommitValidator();

  if (args.includes('--help') || args.includes('-h')) {
    console.log(`
Git提交信息验证工具

用法:
  git-commit-validator <提交信息>              验证单个提交信息
  git-commit-validator --file <文件路径>      验证文件中的提交信息
  git-commit-validator --interactive          交互式生成提交信息
  git-commit-validator --template <类型>      生成指定类型的模板
  git-commit-validator --config <配置文件>    指定配置文件

选项:
  --help, -h              显示帮助信息
  --version               显示版本信息
  --interactive           交互式生成提交信息
  --template <类型>       生成指定类型的模板
  --file <文件路径>       从文件读取提交信息
  --config <配置文件>     指定配置文件路径
  --strict                严格模式（警告也视为错误）
`);
    process.exit(0);
  }

  if (args.includes('--version')) {
    console.log('Git Commit Validator v1.0.0');
    process.exit(0);
  }

  const isStrict = args.includes('--strict');
  const isInteractive = args.includes('--interactive');
  const fileIndex = args.indexOf('--file');
  const configIndex = args.indexOf('--config');
  const templateIndex = args.indexOf('--template');

  // 加载配置
  if (configIndex !== -1 && args[configIndex + 1]) {
    validator.config = validator.loadConfig(args[configIndex + 1]);
  }

  // 生成模板
  if (templateIndex !== -1 && args[templateIndex + 1]) {
    try {
      const template = validator.generateTemplate(args[templateIndex + 1]);
      console.log(template);
      process.exit(0);
    } catch (error) {
      console.error(`错误: ${error.message}`);
      process.exit(1);
    }
  }

  // 交互式生成
  if (isInteractive) {
    validator.interactivePrompt().then(answers => {
      const commitMessage = validator.formatCommitMessage(answers);
      console.log('\n生成的提交信息:');
      console.log('-------------------');
      console.log(commitMessage);
      console.log('-------------------');

      const result = validator.validate(commitMessage);
      if (result.valid) {
        console.log('\n✅ 提交信息格式正确');
      } else {
        console.log('\n❌ 提交信息格式有误:');
        result.errors.forEach(error => console.log(`  错误: ${error}`));
        result.warnings.forEach(warning => console.log(`  警告: ${warning}`));
      }
    });
    return;
  }

  // 从文件读取
  let commitMessage;
  if (fileIndex !== -1 && args[fileIndex + 1]) {
    try {
      commitMessage = fs.readFileSync(args[fileIndex + 1], 'utf8').trim();
    } catch (error) {
      console.error(`错误: 无法读取文件 ${args[fileIndex + 1]}: ${error.message}`);
      process.exit(1);
    }
  } else {
    // 从命令行参数读取
    commitMessage = args.join(' ');
  }

  // 验证提交信息
  const result = validator.validate(commitMessage);

  if (result.valid && (result.warnings.length === 0 || !isStrict)) {
    console.log('✅ 提交信息格式正确');
    if (result.warnings.length > 0) {
      console.log('\n⚠️  警告:');
      result.warnings.forEach(warning => console.log(`  ${warning}`));
    }
    process.exit(0);
  } else {
    console.log('❌ 提交信息格式有误:');
    result.errors.forEach(error => console.log(`  错误: ${error}`));
    result.warnings.forEach(warning => console.log(`  警告: ${warning}`));
    console.log('\n建议格式: <type>[optional scope]: <description>');
    console.log(`允许的类型: ${validator.config.types.join(', ')}`);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = GitCommitValidator;