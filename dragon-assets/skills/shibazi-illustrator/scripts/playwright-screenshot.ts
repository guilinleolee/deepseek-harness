#!/usr/bin/env npx -y bun

/**
 * Playwright截图 - 将HTML渲染为PNG
 *
 * 使用方式：
 *   npx -y bun playwright-screenshot.ts poster.html -o poster.png
 *   npx -y bun playwright-screenshot.ts poster.html -o poster.png -w 600 -h 900
 */

import { readFile } from 'node:fs/promises';
import { chromium, type Browser, type Page, type BrowserContext } from 'playwright';
import { dirname, join } from 'node:path';

interface ScreenshotOptions {
  width: number;
  height: number;
  deviceScaleFactor: number;
  fullPage?: boolean;
  timeout?: number;
}

/**
 * 使用Playwright截图HTML
 */
export async function screenshotHTML(
  htmlPath: string,
  outputPath: string,
  options: Partial<ScreenshotOptions> = {}
): Promise<void> {
  const {
    width = 600,
    height = 900,
    deviceScaleFactor = 2,  // 高清截图
    fullPage = true,
    timeout = 30000
  } = options;

  console.log(`📸 Loading HTML: ${htmlPath}`);

  let browser: Browser | null = null;
  let context: BrowserContext | null = null;
  let page: Page | null = null;

  try {
    // 读取HTML内容
    const html = await readFile(htmlPath, 'utf-8');

    // 启动浏览器
    console.log('🌐 Launching browser...');
    browser = await chromium.launch({
      headless: true,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu'
      ]
    });

    // 创建上下文（设置视口）
    context = await browser.newContext({
      viewport: { width, height },
      deviceScaleFactor,
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    });

    // 创建页面
    page = await context.newPage();

    // 设置超时
    page.setDefaultTimeout(timeout);

    // 加载HTML
    console.log('⏳ Loading HTML content...');
    await page.setContent(html, {
      waitUntil: 'networkidle',
      timeout
    });

    // 等待字体加载
    console.log('⏳ Waiting for fonts to load...');
    try {
      await page.evaluate(async () => {
        // 等待所有字体加载完成
        await document.fonts.ready;
      });
    } catch (error) {
      console.warn('⚠ Font loading timeout, proceeding anyway');
    }

    // 额外等待确保渲染完成
    await page.waitForTimeout(1000);

    // 截图
    console.log(`📸 Taking screenshot (${width}x${height} @${deviceScaleFactor}x)...`);
    await page.screenshot({
      path: outputPath,
      fullPage,
      type: 'png'
    });

    console.log(`✅ Screenshot saved: ${outputPath}`);

  } catch (error) {
    console.error('❌ Screenshot failed:', error instanceof Error ? error.message : error);
    throw error;
  } finally {
    // 清理资源
    if (page) await page.close().catch(() => {});
    if (context) await context.close().catch(() => {});
    if (browser) await browser.close().catch(() => {});
  }
}

/**
 * CLI入口
 */
async function main() {
  const args = process.argv.slice(2);

  let htmlPath: string | null = null;
  let outputPath = 'output.png';
  let width = 600;
  let height = 900;
  let deviceScaleFactor = 2;
  let fullPage = true;

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    switch (arg) {
      case '-h':
      case '--help':
        console.log(`
Playwright Screenshot - Render HTML to PNG

Usage:
  npx -y bun playwright-screenshot.ts <input.html> [options]

Options:
  -o, --output <path>       Output PNG path (default: output.png)
  -w, --width <px>          Viewport width (default: 600)
  -h, --height <px>         Viewport height (default: 900)
  -d, --dpi <scale>         Device scale factor (default: 2)
  --no-full-page            Disable full-page screenshot
  --help                    Show this help

Examples:
  # Basic usage
  npx -y bun playwright-screenshot.ts poster.html

  # Custom size
  npx -y bun playwright-screenshot.ts poster.html -w 800 -h 1200

  # High resolution
  npx -y bun playwright-screenshot.ts poster.html -d 3

Note: Requires Playwright to be installed:
  npx -y playwright install chromium
`);
        process.exit(0);
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
      case '-d':
      case '--dpi':
        deviceScaleFactor = parseInt(args[++i], 10);
        break;
      case '--no-full-page':
        fullPage = false;
        break;
      default:
        if (!htmlPath) {
          htmlPath = arg;
        }
        break;
    }
  }

  if (!htmlPath) {
    console.error('Error: HTML path is required');
    console.error('Usage: npx -y bun playwright-screenshot.ts <input.html> [options]');
    process.exit(1);
  }

  try {
    await screenshotHTML(htmlPath, outputPath, {
      width,
      height,
      deviceScaleFactor,
      fullPage
    });

    console.log('\n✅ Done!');
  } catch (error) {
    console.error('Error:', error instanceof Error ? error.message : error);
    process.exit(1);
  }
}

// 仅在直接运行时执行CLI
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}
