#!/usr/bin/env npx -y bun

/**
 * HTML渲染引擎 - 基于模板快速生成海报
 * 修复Windows路径兼容性
 */

import { readFile, writeFile } from 'node:fs/promises';
import { join, dirname, basename, extname, resolve } from 'node:path';
import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

// 获取脚本所在目录（兼容Windows）
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const TEMPLATES_DIR = resolve(__dirname, '../templates');

// 支持的模板类型
export type Template = 'kabager' | 'minimal' | 'dramatic';

// 输出格式
export type OutputFormat = 'html' | 'png' | 'both';

export interface HTMLExportOptions {
  template: Template;
  format: OutputFormat;
  outputPath: string;
  width?: number;
  height?: number;
}

/**
 * 文章内容结构
 */
export interface ArticleContent {
  brand: {
    name: string;
    version: string;
    tagline: string;
  };
  title: {
    main: string;
    highlight: string;
  };
  subtitle: string;
  sections: Array<{
    title: string;
    content: string;
  }>;
  footer: {
    summary: string;
    cta?: string;
  };
}

/**
 * 从文章提取结构化内容
 */
export async function extractArticleContent(
  articlePath: string
): Promise<ArticleContent> {
  const content = await readFile(articlePath, 'utf-8');
  const lines = content.split('\n');

  const result: ArticleContent = {
    brand: {
      name: "十八子写作",
      version: "v2.0",
      tagline: "智能写作助手 · 让写作更简单"
    },
    title: {
      main: "",
      highlight: ""
    },
    subtitle: "",
    sections: [],
    footer: {
      summary: ""
    }
  };

  let currentSection: { title: string; content: string } | null = null;
  let inCodeBlock = false;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();

    // 跳过代码块
    if (line.startsWith('```')) {
      inCodeBlock = !inCodeBlock;
      continue;
    }
    if (inCodeBlock) continue;

    // 一级标题 → 主标题
    if (line.startsWith('# ')) {
      const titleText = line.substring(2).trim();
      const parts = titleText.split(/[|｜]/);
      if (parts.length >= 2) {
        result.title.main = parts[0].trim();
        result.title.highlight = parts[1].trim();
      } else {
        result.title.main = titleText;
        result.title.highlight = titleText;
      }
      continue;
    }

    // 二级标题 → 章节标题
    if (line.startsWith('## ')) {
      if (currentSection && currentSection.content) {
        result.sections.push(currentSection);
      }
      currentSection = {
        title: line.substring(3).trim(),
        content: ""
      };
      continue;
    }

    // 引用块 → 副标题金句
    if (line.startsWith('> ')) {
      if (!result.subtitle) {
        result.subtitle = line.substring(2).trim();
      }
      continue;
    }

    // 水平线
    if (line === '---' || line === '***') {
      continue;
    }

    // 空行
    if (!line) {
      if (currentSection && currentSection.content) {
        result.sections.push(currentSection);
        currentSection = null;
      }
      continue;
    }

    // 普通段落
    if (currentSection) {
      if (currentSection.content) {
        currentSection.content += ' ';
      }
      currentSection.content += line;
    }
  }

  // 保存最后一个章节
  if (currentSection && currentSection.content) {
    result.sections.push(currentSection);
  }

  // 如果没有提取到页脚金句，使用最后一段
  if (!result.footer.summary && result.sections.length > 0) {
    const lastSection = result.sections[result.sections.length - 1];
    result.footer.summary = lastSection.content;
    result.sections.pop();
  }

  // 限制sections数量
  if (result.sections.length > 6) {
    result.sections = result.sections.slice(0, 6);
  }

  // 填充默认值
  if (!result.title.main) {
    result.title.main = "文章标题";
    result.title.highlight = "副标题";
  }
  if (!result.subtitle) {
    result.subtitle = "精选内容摘要";
  }
  if (!result.footer.summary) {
    result.footer.summary = "总结金句";
  }

  return result;
}

/**
 * 加载HTML模板
 */
async function loadTemplate(template: Template): Promise<string> {
  const templatePath = join(TEMPLATES_DIR, `${template}.html`);

  console.log(`Loading template: ${templatePath}`);

  if (!existsSync(templatePath)) {
    throw new Error(`Template not found: ${templatePath}`);
  }

  return await readFile(templatePath, 'utf-8');
}

/**
 * HTML转义
 */
function escapeHTML(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

/**
 * 生成sections HTML
 */
function generateSectionsHTML(sections: ArticleContent['sections'], template: Template): string {
  if (template === 'kabager') {
    return sections.map(section => `
                <div class="space-y-1">
                    <h3 class="section-title">${escapeHTML(section.title)}</h3>
                    <p class="section-body">${escapeHTML(section.content)}</p>
                </div>`).join('\n');
  } else {
    return sections.map(section => `
                <div>
                    <h3 class="section-title">${escapeHTML(section.title)}</h3>
                    <p class="section-body">${escapeHTML(section.content)}</p>
                </div>`).join('\n');
  }
}

/**
 * 渲染HTML
 */
export function renderHTML(
  template: string,
  content: ArticleContent,
  templateType: Template
): string {
  const sectionsHTML = generateSectionsHTML(content.sections, templateType);

  return template
    .replace(/{{BRAND_NAME}}/g, content.brand.name)
    .replace(/{{BRAND_VERSION}}/g, content.brand.version)
    .replace(/{{BRAND_TAGLINE}}/g, content.brand.tagline)
    .replace(/{{TITLE_MAIN}}/g, escapeHTML(content.title.main))
    .replace(/{{TITLE_HIGHLIGHT}}/g, escapeHTML(content.title.highlight))
    .replace(/{{SUBTITLE}}/g, escapeHTML(content.subtitle))
    .replace(/{{SECTIONS}}/g, sectionsHTML)
    .replace(/{{FOOTER_SUMMARY}}/g, escapeHTML(content.footer.summary))
    .replace(/{{FOOTER_CTA}}/g, content.footer.cta ? escapeHTML(content.footer.cta) : '');
}

/**
 * 主导出函数
 */
export async function exportHTML(
  articlePath: string,
  options: HTMLExportOptions
): Promise<{ htmlPath?: string; pngPath?: string }> {
  const { template, format, outputPath } = options;

  console.log(`📄 Extracting content from: ${articlePath}`);

  // 1. 提取内容
  const content = await extractArticleContent(articlePath);

  console.log(`✓ Extracted ${content.sections.length} sections`);
  console.log(`  Title: ${content.title.main} | ${content.title.highlight}`);

  // 2. 加载模板
  console.log(`🎨 Loading template: ${template}`);
  const templateHTML = await loadTemplate(template);

  // 3. 渲染HTML
  const renderedHTML = renderHTML(templateHTML, content, template);
  console.log('✓ HTML rendered');

  // 4. 输出
  const baseName = basename(outputPath, extname(outputPath));
  const outputDir = dirname(outputPath);
  const result: { htmlPath?: string; pngPath?: string } = {};

  if (format === 'html' || format === 'both') {
    const htmlPath = resolve(outputDir, `${baseName}.html`);
    await writeFile(htmlPath, renderedHTML, 'utf-8');
    result.htmlPath = htmlPath;
    console.log(`✓ HTML saved: ${htmlPath}`);
  }

  if (format === 'png' || format === 'both') {
    const pngPath = resolve(outputDir, `${baseName}.png`);
    result.pngPath = pngPath;
    console.log(`📸 PNG ready for export: ${pngPath}`);
  }

  return result;
}

/**
 * CLI入口
 */
async function main() {
  const args = process.argv.slice(2);

  let articlePath: string | null = null;
  let template: Template = 'kabager';
  let format: OutputFormat = 'html';
  let outputPath = 'poster';
  let width = 600;
  let height = 900;

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    switch (arg) {
      case '-h':
      case '--help':
        console.log(`
HTML Export Engine - Fast Template-based Poster Generation

Usage:
  bun html-export-fixed.ts <article.md> [options]

Options:
  -t, --template <name>    Template: kabager (default), minimal, dramatic
  -f, --format <format>    Output format: html (default), png, both
  -o, --output <path>      Output base path (default: poster)
  -w, --width <px>         Width in pixels (default: 600)
  -h, --height <px>        Height in pixels (default: 900)
  --help                   Show this help

Examples:
  # Generate HTML only
  bun html-export-fixed.ts article.md

  # Generate with custom template
  bun html-export-fixed.ts article.md -t minimal

  # Generate both HTML and PNG
  bun html-export-fixed.ts article.md -f both -o my-poster
`);
        process.exit(0);
      case '-t':
      case '--template':
        template = args[++i] as Template;
        break;
      case '-f':
      case '--format':
        format = args[++i] as OutputFormat;
        break;
      case '-o':
      case '--output':
        outputPath = args[++i];
        break;
      case '-w':
      case '--width':
        width = parseInt(args[++i], 10);
        break;
      case '-h':
      case '--height':
        height = parseInt(args[++i], 10);
        break;
      default:
        if (!articlePath) {
          articlePath = arg;
        }
        break;
    }
  }

  if (!articlePath) {
    console.error('Error: Article path is required');
    console.error('Usage: bun html-export-fixed.ts <article.md> [options]');
    process.exit(1);
  }

  try {
    const result = await exportHTML(articlePath, {
      template,
      format,
      outputPath,
      width,
      height
    });

    console.log('\n✅ Export complete!');
    if (result.htmlPath) {
      console.log(`  HTML: ${result.htmlPath}`);
    }
    if (result.pngPath) {
      console.log(`  PNG: ${result.pngPath} (use playwright-screenshot.ts to render)`);
    }
  } catch (error) {
    console.error('Error:', error instanceof Error ? error.message : error);
    process.exit(1);
  }
}

// 仅在直接运行时执行CLI
if (import.meta.url === `file://${process.argv[1].replace(/\\/g, '/')}`) {
  main();
}
