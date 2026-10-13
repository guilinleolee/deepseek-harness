const { chromium } = require('playwright');
const path = require('path');

(async () => {
  console.log('🚀 Starting the Lead Extraction (V7 - High Patience)...');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
  });
  const page = await context.newPage();

  try {
    console.log('📡 Logging in...');
    await page.goto('https://app.apollo.io/#/login', { timeout: 60000 });
    await page.fill('input[name="email"]', 'admin@acuity-ai.pro');
    await page.fill('input[name="password"]', 'AcuityAI2026!');
    await page.click('button[type="submit"]');

    console.log('⏳ Waiting for Post-Login redirect (60s timeout)...');
    await page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 60000 }).catch(() => console.log('Timeout waiting for navigation, continuing...'));

    console.log('🎯 Navigating to Prospecting...');
    await page.goto('https://app.apollo.io/#/people', { waitUntil: 'domcontentloaded', timeout: 60000 });
    console.log('📍 Current URL:', page.url());

    // Take a large screenshot to see the whole page
    await page.waitForTimeout(10000);
    await page.screenshot({ path: path.join(__dirname, 'apollo_v7_land.png'), fullPage: true });

    // Try a broad search in the main box if it exists
    const searchBox = page.locator('input[placeholder*="Search across Apollo"], input[placeholder*="Search people"]');
    if (await searchBox.isVisible()) {
      console.log('⌨️ Typing broad search...');
      await searchBox.fill('Partner California Personal Injury');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(10000);
      await page.screenshot({ path: path.join(__dirname, 'apollo_v7_results.png'), fullPage: true });
    }

  } catch (error) {
    console.error('❌ Hunter Error:', error.message);
  } finally {
    await browser.close();
    console.log('🏁 Mission complete.');
  }
})();
