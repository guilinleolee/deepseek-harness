---
license: UNKNOWN
name: e2e-testing
description: Playwright E2E testing patterns, Page Object Model, configuration, CI/CD integration, artifact management, and flaky test strategies.
github_repo: affaan-m/everything-claude-code
github_hash: 4e66b2882da9afb9747468b08a253ca2f09c85f3
last_updated: 2026-04-25
source_type: derived
origin: ECC (everything-claude-code)
triggers: ["e2e testing", "E2E Testing Patterns — 端到端测试模式"]
---

# E2E Testing Patterns — 端到端测试模式

> 来源: [affaan-m/everything-claude-code/skills/e2e-testing](https://github.com/affaan-m/everything-claude-code)

## 功能概述

基于Playwright的端到端测试模式，覆盖Page Object Model、多浏览器配置、CI/CD集成、制品管理及不稳定测试处理策略。

## 何时使用

- 编写新的E2E测试
- 配置Playwright测试套件
- 处理不稳定测试
- 集成CI/CD流水线
- 管理测试制品（截图/视频/追踪）

## 测试文件组织

```
tests/
├── e2e/
│   ├── auth/
│   │   ├── login.spec.ts
│   │   ├── logout.spec.ts
│   │   └── register.spec.ts
│   ├── features/
│   │   ├── browse.spec.ts
│   │   └── search.spec.ts
│   └── api/
│       └── endpoints.spec.ts
├── fixtures/
│   └── auth.ts
└── playwright.config.ts
```

## Page Object Model (POM)

```typescript
import { Page, Locator } from '@playwright/test'

export class ItemsPage {
  readonly page: Page
  readonly searchInput: Locator
  readonly itemCards: Locator
  readonly createButton: Locator

  constructor(page: Page) {
    this.page = page
    this.searchInput = page.locator('[data-testid="search-input"]')
    this.itemCards = page.locator('[data-testid="item-card"]')
    this.createButton = page.locator('[data-testid="create-btn"]')
  }

  async goto() {
    await this.page.goto('/items')
    await this.page.waitForLoadState('networkidle')
  }

  async search(query: string) {
    await this.searchInput.fill(query)
    await this.page.waitForResponse(resp => resp.url().includes('/api/search'))
    await this.page.waitForLoadState('networkidle')
  }

  async getItemCount() {
    return await this.itemCards.count()
  }
}
```

## Playwright配置

```typescript
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['junit', { outputFile: 'playwright-results.xml' }],
    ['json', { outputFile: 'playwright-results.json' }]
  ],
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 10000,
    navigationTimeout: 30000,
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
    { name: 'mobile-chrome', use: { ...devices['Pixel 5'] } },
  ],
})
```

## 不稳定测试处理

### 隔离与跳过

```typescript
test('flaky: complex search', async ({ page }) => {
  test.fixme(true, 'Flaky - Issue #123')
  // test code...
})

test('conditional skip', async ({ page }) => {
  test.skip(process.env.CI, 'Flaky in CI - Issue #123')
})
```

### 识别不稳定性

```bash
npx playwright test tests/search.spec.ts --repeat-each=10
npx playwright test tests/search.spec.ts --retries=3
```

### 常见原因与修复

| 问题类型 | ❌ Bad | ✅ Good |
|----------|--------|--------|
| 竞态条件 | `await page.click('[data-testid="btn"]')` | `await page.locator('[data-testid="btn"]').click()` |
| 网络时序 | `await page.waitForTimeout(5000)` | `await page.waitForResponse(resp => resp.url().includes('/api/data'))` |
| 动画时序 | 点击动画中元素 | `await page.locator('[data-testid="item"]').waitFor({ state: 'visible' })` |

## 制品管理

### 截图

```typescript
await page.screenshot({ path: 'artifacts/after-login.png' })
await page.screenshot({ path: 'artifacts/full-page.png', fullPage: true })
```

### 追踪

```typescript
await browser.startTracing(page, {
  path: 'artifacts/trace.json',
  screenshots: true,
  snapshots: true,
})
// ... 测试操作 ...
await browser.stopTracing()
```

## CI/CD集成

```yaml
# .github/workflows/e2e.yml
name: E2E Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npx playwright test
        env:
          BASE_URL: ${{ vars.STAGING_URL }}
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 30
```

## 关键场景测试

### Web3/钱包测试

```typescript
test('wallet connection', async ({ page, context }) => {
  await context.addInitScript(() => {
    window.ethereum = {
      isMetaMask: true,
      request: async ({ method }) => {
        if (method === 'eth_requestAccounts')
          return ['0x1234567890123456789012345678901234567890']
        if (method === 'eth_chainId') return '0x1'
      }
    }
  })

  await page.goto('/')
  await page.locator('[data-testid="connect-wallet"]').click()
})
```

### 关键流程测试（金融/交易）

```typescript
test('trade execution', async ({ page }) => {
  test.skip(process.env.NODE_ENV === 'production', 'Skip on production')

  await page.goto('/markets/test-market')
  await page.locator('[data-testid="position-yes"]').click()
  await page.locator('[data-testid="trade-amount"]').fill('1.0')

  // 验证预览
  const preview = page.locator('[data-testid="trade-preview"]')
  await expect(preview).toContainText('1.0')

  // 确认并等待区块链
  await page.locator('[data-testid="confirm-trade"]').click()
  await page.waitForResponse(
    resp => resp.url().includes('/api/trade') && resp.status() === 200,
    { timeout: 30000 }
  )
})
```

## 天龙引擎集成

### 适用岗位

| 岗位 | 集成方式 | 增强能力 |
|------|---------|---------|
| **04验证师** | Playwright测试 | POM模式 + 不稳定测试处理 |
| **03构建师** | 页面对象开发 | data-testid最佳实践 |
| **16-01 DevOps** | CI/CD集成 | GitHub Actions流水线 |

### 天龙引擎增强

```
┌─────────────────────────────────────────────────────────────┐
│ 天龙引擎 E2E测试体系                                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   测试流程:                                                  │
│   ├── 04验证师 → 测试编写 + POM + CI/CD                   │
│   ├── 03构建师 → data-testid实现 + 页面对象               │
│   └── 16-01 DevOps → GitHub Actions流水线                │
│                                                             │
│   协同技能:                                                 │
│   ├── /playwright-skill → Playwright CLI                  │
│   ├── /e2e-testing    → POM模式 + 不稳定测试            │
│   └── /webapp-testing  → 应用层测试                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 核心命令

```bash
# Playwright测试
[@验证师] 使用POM编写这个功能的E2E测试
[@验证师] 隔离这个不稳定的测试

# CI/CD集成
[@DevOps] 配置GitHub Actions E2E测试流水线
[@DevOps] 添加制品上传（报告/截图/视频）

# 调试
[@验证师] 生成测试追踪文件分析失败原因
[@验证师] 使用--repeat-each识别不稳定测试
```

---

**版本**: V1.0 | **兼容性**: 天龙引擎 V8.68+ | **来源**: ECC
