/**
 * Design Token同步引擎
 *
 * 负责Figma Design Token到代码的自动化同步
 */

import { promises as fs } from 'fs';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

/**
 * Design Token同步引擎
 */
export class DesignTokenSyncEngine {
  constructor(config) {
    this.config = config;
    this.changes = [];
  }

  /**
   * 执行完整同步流程
   */
  async sync() {
    console.log('🎨 Starting Design Token sync...');

    try {
      // 1. 检测变更
      const changes = await this.detectChanges();
      if (changes.length === 0) {
        console.log('✅ No changes detected');
        return;
      }

      // 2. 提取Design Token
      const tokens = await this.extractTokens();

      // 3. 生成代码文件
      await this.generateCode(tokens);

      // 4. 运行测试
      await this.runTests();

      // 5. Git提交
      await this.commitChanges();

      // 6. 创建PR
      const prUrl = await this.createPullRequest();

      console.log('✅ Design Token sync completed!');
      console.log('📝 PR created:', prUrl);
    } catch (error) {
      console.error('❌ Sync failed:', error);
      throw error;
    }
  }

  /**
   * 检测Figma设计变更
   */
  async detectChanges() {
    console.log('🔍 Detecting changes...');

    // 获取当前Design Token版本
    const currentVersion = await this.getCurrentVersion();

    // 获取Figma最新版本
    const figmaVersion = await this.getFigmaVersion();

    if (currentVersion === figmaVersion) {
      return [];
    }

    // 比较差异
    const changes = await this.compareVersions(currentVersion, figmaVersion);
    this.changes = changes;

    console.log(`📊 Found ${changes.length} changes`);
    return changes;
  }

  /**
   * 提取Design Token
   */
  async extractTokens() {
    console.log('📦 Extracting tokens...');

    // 通过Vibma MCP获取设计变量
    const collection = await vibma_variables_get_collection();

    // 分类变量
    const tokens = {
      colors: this.extractColorTokens(collection),
      spacing: this.extractSpacingTokens(collection),
      typography: this.extractTypographyTokens(collection),
      effects: this.extractEffectTokens(collection)
    };

    console.log(`✅ Extracted ${Object.values(tokens).flat().length} tokens`);
    return tokens;
  }

  /**
   * 生成代码文件
   */
  async generateCode(tokens) {
    console.log('⚙️ Generating code files...');

    const generators = [
      this.generateCSS,
      this.generateTailwind,
      this.generateSCSS,
      this.generateTypeScript
    ];

    for (const generator of generators) {
      await generator.call(this, tokens);
    }

    console.log('✅ Code files generated');
  }

  /**
   * 生成CSS变量
   */
  async generateCSS(tokens) {
    const css = this.formatCSSVariables(tokens);
    await fs.writeFile(this.config.output.css, css, 'utf-8');
  }

  /**
   * 生成Tailwind配置
   */
  async generateTailwind(tokens) {
    const config = this.formatTailwindConfig(tokens);
    const js = `module.exports = ${JSON.stringify(config, null, 2)}`;
    await fs.writeFile(this.config.output.tailwind, js, 'utf-8');
  }

  /**
   * 生成SCSS变量
   */
  async generateSCSS(tokens) {
    const scss = this.formatSCSSVariables(tokens);
    await fs.writeFile(this.config.output.scss, scss, 'utf-8');
  }

  /**
   * 生成TypeScript类型定义
   */
  async generateTypeScript(tokens) {
    const types = this.formatTypeScriptTypes(tokens);
    await fs.writeFile(this.config.output.typescript, types, 'utf-8');
  }

  /**
   * 运行测试
   */
  async runTests() {
    console.log('🧪 Running tests...');

    if (this.config.tests.coverage) {
      await execAsync('npm run test:coverage');
    }

    if (this.config.tests.lint) {
      await execAsync('npm run lint');
    }

    if (this.config.tests.typeCheck) {
      await execAsync('npm run type-check');
    }

    console.log('✅ All tests passed');
  }

  /**
   * Git提交
   */
  async commitChanges() {
    console.log('📝 Committing changes...');

    const { branch, commitMessage } = this.config.git;

    // 创建分支
    await execAsync(`git checkout -b design-tokens-update-${Date.now()}`);

    // 添加文件
    await execAsync('git add .');

    // 提交
    await execAsync(`git commit -m "${commitMessage}"`);

    console.log('✅ Changes committed');
  }

  /**
   * 创建Pull Request
   */
  async createPullRequest() {
    console.log('🔀 Creating pull request...');

    const { prTitle, prBody } = this.config.git;

    // 使用gh CLI创建PR
    const { stdout } = await execAsync(
      `gh pr create --title "${prTitle}" --body "${prBody}"`
    );

    // 提取PR URL
    const prUrl = stdout.match(/https:\/\/github\.com\/[^ ]+/)[0];

    return prUrl;
  }

  /**
   * 获取当前版本
   */
  async getCurrentVersion() {
    try {
      const data = await fs.readFile('.design-token-version', 'utf-8');
      return data.trim();
    } catch {
      return null;
    }
  }

  /**
   * 获取Figma版本
   */
  async getFigmaVersion() {
    const doc = await vibma_document_get();
    return doc.version;
  }

  /**
   * 比较版本差异
   */
  async compareVersions(current, latest) {
    // 实现版本比较逻辑
    // 返回变更列表
    return [];
  }

  /**
   * 格式化CSS变量
   */
  formatCSSVariables(tokens) {
    const sections = [];

    for (const [category, items] of Object.entries(tokens)) {
      const vars = items.map(token => {
        return `  --${token.name}: ${token.value};`;
      }).join('\n');

      sections.push(`/* ${category} */\n${vars}`);
    }

    return `:root {\n${sections.join('\n\n')}\n}`;
  }

  /**
   * 格式化Tailwind配置
   */
  formatTailwindConfig(tokens) {
    const config = {
      theme: {
        extend: {}
      }
    };

    for (const [category, items] of Object.entries(tokens)) {
      config.theme.extend[category] = Object.fromEntries(
        items.map(token => [token.kebabCase, token.value])
      );
    }

    return config;
  }

  /**
   * 格式化SCSS变量
   */
  formatSCSSVariables(tokens) {
    const sections = [];

    for (const [category, items] of Object.entries(tokens)) {
      const vars = items.map(token => {
        return `$${token.name}: ${token.value};`;
      }).join('\n');

      sections.append(`// ${category}\n${vars}`);
    }

    return sections.join('\n\n');
  }

  /**
   * 格式化TypeScript类型
   */
  formatTypeScriptTypes(tokens) {
    const types = [];

    for (const [category, items] of Object.entries(tokens)) {
      const typeItems = items.map(token => {
        return `  ${token.pascalCase}: '${token.value}';`;
      }).join('\n');

      types.push(
        `export type ${category} = {\n${typeItems}\n};`
      );
    }

    return types.join('\n\n');
  }

  /**
   * 提取颜色Token
   */
  extractColorTokens(collection) {
    return collection.variables
      .filter(v => v.resolvedType === 'COLOR')
      .map(v => ({
        name: v.name,
        kebabCase: toKebabCase(v.name),
        pascalCase: toPascalCase(v.name),
        value: this.formatColor(v.value)
      }));
  }

  /**
   * 提取间距Token
   */
  extractSpacingTokens(collection) {
    return collection.variables
      .filter(v => v.name.includes('spacing'))
      .map(v => ({
        name: v.name,
        kebabCase: toKebabCase(v.name),
        pascalCase: toPascalCase(v.name),
        value: `${v.value}px`
      }));
  }

  /**
   * 提取字体Token
   */
  extractTypographyTokens(collection) {
    return collection.variables
      .filter(v => v.name.includes('font'))
      .map(v => ({
        name: v.name,
        kebabCase: toKebabCase(v.name),
        pascalCase: toPascalCase(v.name),
        value: `${v.value}px`
      }));
  }

  /**
   * 提取效果Token
   */
  extractEffectTokens(collection) {
    return collection.variables
      .filter(v => v.name.includes('shadow') || v.name.includes('blur'))
      .map(v => ({
        name: v.name,
        kebabCase: toKebabCase(v.name),
        pascalCase: toPascalCase(v.name),
        value: this.formatEffect(v.value)
      }));
  }

  /**
   * 格式化颜色值
   */
  formatColor(color) {
    if (color.r !== undefined) {
      return `rgba(${color.r}, ${color.g}, ${color.b}, ${color.a || 1})`;
    }
    return color;
  }

  /**
   * 格式化效果值
   */
  formatEffect(effect) {
    // 实现效果格式化逻辑
    return effect;
  }
}

/**
 * 工具函数
 */
function toKebabCase(str) {
  return str.replace(/([A-Z])/g, '-$1').toLowerCase();
}

function toPascalCase(str) {
  return str.replace(/(^|-)(\w)/g, (_, __, char) => char.toUpperCase());
}

/**
 * 创建同步引擎实例
 */
export function createDesignTokenSyncEngine(config) {
  return new DesignTokenSyncEngine(config);
}
