const { chromium } = require('playwright');
const path = require('path');

(async () => {
    console.log('🚀 Attempting Reset with Email Confirmation...');
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext();
    const page = await context.newPage();
    try {
        await page.goto('https://app.apollo.io/#/login');
        await page.click('text=Forgot password?');

        await page.waitForSelector('input[name="email"]');
        await page.fill('input[name="email"]', 'admin@acuity-ai.pro');

        // Wait for the confirmation field to appear/be interactable
        // In the screenshot it's the second input field
        await page.fill('input[placeholder="Re-type your email"]', 'admin@acuity-ai.pro');

        console.log('🖱️ Clicking Send Instructions...');
        await page.click('button:has-text("Send Instructions")');

        await page.waitForTimeout(5000);
        console.log('✅ Final Outcome: Check Zoho.');
        await page.screenshot({ path: path.join(__dirname, 'reset_sent_success.png') });
    } catch (e) {
        console.error('❌ Error:', e.message);
        await page.screenshot({ path: path.join(__dirname, 'reset_final_error.png') });
    } finally {
        await browser.close();
    }
})();
