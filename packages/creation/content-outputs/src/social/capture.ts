/**
 * The social-capture service: browser-session login, logged-in profile
 * reads, and the daily frequency gate. Architecture follows the 2026-10-05
 * scraping research: the user logs into THEIR OWN account in a headed
 * browser on THEIR machine (the session never leaves it), the capture reads
 * a handful of pages at capped frequency, and no signature reversal exists
 * anywhere in this file. Platform DOM extraction is best-effort and marked
 * for field iteration — every failure degrades to the manual-paste path.
 */

import { join } from 'node:path'
import { resolveDshHome } from '@deepseek-ai/dsh-home-paths'
import type { SocialCaptureResult, SocialPlatform, SocialStatuses } from '../persona/types.ts'
import { SOCIAL_PLATFORMS, SOCIAL_PLATFORM_LABELS } from '../persona/types.ts'
import { SOCIAL_PLATFORM_META } from './platforms.ts'
import { forgetSession, hasSession, saveSession, sessionPath } from './sessions.ts'
import { consumeCapture, readCounters } from './frequency.ts'

/** The structured facts one capture reads off the logged-in profile page. */
export interface SocialProfileExtraction {
  readonly nickname: string | null
  readonly bio: string | null
  readonly verified: string | null
  /** Up to ten work/video titles, trimmed. */
  readonly works: readonly string[]
}

/**
 * One open browser page the service drives. The production implementation
 * wraps Playwright; tests inject a fake. `extract` runs the platform's
 * in-page snippet.
 */
export interface SocialCapturePage {
  goto(url: string): Promise<void>
  currentUrl(): string
  hasCookie(name: string, forUrl: string): Promise<boolean>
  storageState(): Promise<string>
  extract(platform: SocialPlatform): Promise<SocialProfileExtraction>
  close(): Promise<void>
}

/** Opens one browser page; `storageStatePath` is the stored session file or null for a fresh context. */
export type SocialPageFactory = (options: {
  headless: boolean
  storageStatePath: string | null
}) => Promise<SocialCapturePage>

/** Injectable edges of the service (tests replace the browser and the clock). */
export interface SocialCaptureDeps {
  readonly openPage?: SocialPageFactory
  readonly now?: () => Date
  readonly sleep?: (ms: number) => Promise<void>
}

export interface SocialCaptureConfig {
  /** Where browser sessions and counters persist. Defaults to `<dsh home>/social-states`. */
  readonly socialStatesDir?: string | undefined
  /** Daily per-platform capture cap (1–10). Defaults to 3. */
  readonly maxDailyCaptures?: number | undefined
}

const LOGIN_TIMEOUT_MS = 180_000
const LOGIN_POLL_MS = 2_000
const SPA_RENDER_WAIT_MS = 2_500
export const SOCIAL_CAPTURE_MAX_DAILY = 3

function defaultSleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms))
}

/** The production Playwright page wrapper. */
async function openPlaywrightPage(options: { headless: boolean; storageStatePath: string | null }): Promise<SocialCapturePage> {
  const { chromium } = await import('playwright')
  const browser = await chromium.launch({ headless: options.headless })
  const context = await browser.newContext({
    locale: 'zh-CN',
    ...(options.storageStatePath === null ? {} : { storageState: options.storageStatePath }),
  })
  const page = await context.newPage()
  return {
    async goto(url: string): Promise<void> {
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30_000 }).catch(() => undefined)
    },
    currentUrl(): string {
      return page.url()
    },
    async hasCookie(name: string, forUrl: string): Promise<boolean> {
      const cookies = await context.cookies(forUrl)
      return cookies.some(cookie => cookie.name === name && cookie.value.length > 0)
    },
    async storageState(): Promise<string> {
      return JSON.stringify(await context.storageState())
    },
    async extract(platform: SocialPlatform): Promise<SocialProfileExtraction> {
      // The snippet runs inside the page: it reads the live DOM through
      // globalThis (this Node package has no DOM lib by design).
      return page.evaluate(EXTRACT_SNIPPETS[platform])
    },
    async close(): Promise<void> {
      await browser.close().catch(() => undefined)
    },
  }
}

/**
 * In-page extraction snippets. Selectors are the community-documented
 * logged-in DOM shapes (as of the research date) with fallbacks; they are
 * the part that degrades when a platform redesigns — every failure path
 * throws a message that points at the manual-paste fallback.
 */
const EXTRACT_SNIPPETS: Readonly<Record<SocialPlatform, () => SocialProfileExtraction | Promise<SocialProfileExtraction>>> = {
  xhs: () => {
    const g = globalThis as unknown as DocumentApi
    const nickname = g.querySelector('.user-name')?.textContent?.trim() ?? g.querySelector('.nickName')?.textContent?.trim() ?? null
    const bio = g.querySelector('.user-desc')?.textContent?.trim() ?? g.querySelector('.desc')?.textContent?.trim() ?? null
    const verifiedBadge = g.querySelector('.user-verified-icon')
    const verified = verifiedBadge === null ? null : verifiedBadge.getAttribute?.('aria-label') ?? '认证用户'
    const works = Array.from(g.querySelectorAll('.note-item a.title, section a.title'))
      .map(el => el.textContent?.trim() ?? '').filter(title => title.length > 0).slice(0, 10)
    return { nickname, bio, verified, works }
  },
  douyin: () => {
    const g = globalThis as unknown as DocumentApi
    const nickname = g.querySelector('[data-e2e="user-info-nickname"]')?.textContent?.trim() ?? g.querySelector('h1')?.textContent?.trim() ?? null
    const bio = g.querySelector('[data-e2e="user-info-bio"]')?.textContent?.trim() ?? null
    const verified = g.querySelector('[data-e2e="user-info-verified"]')?.textContent?.trim() ?? null
    const works = Array.from(g.querySelectorAll('[data-e2e="user-post-item"] .title, [data-e2e="user-post-item-video"] p'))
      .map(el => el.textContent?.trim() ?? '').filter(title => title.length > 0).slice(0, 10)
    return { nickname, bio, verified, works }
  },
  weibo: () => {
    const g = globalThis as unknown as DocumentApi
    const nickname = g.querySelector('.ProfileHeader_name')?.textContent?.trim() ?? g.querySelector('.username')?.textContent?.trim() ?? null
    const bio = g.querySelector('.ProfileHeader_bio')?.textContent?.trim() ?? g.querySelector('.bio')?.textContent?.trim() ?? null
    const verified = g.querySelector('.ProfileHeader_ico .icon-verify')?.getAttribute?.('title') ?? null
    const works = Array.from(g.querySelectorAll('.wb-item .wb-text, [node-type="feed_list_item"] .wb-text'))
      .map(el => el.textContent?.trim() ?? '').filter(title => title.length > 0).slice(0, 10)
    return { nickname, bio, verified, works }
  },
  bili: () => {
    const g = globalThis as unknown as DocumentApi
    const nickname = g.querySelector('.h-name')?.textContent?.trim() ?? null
    const bio = g.querySelector('.h-desc')?.textContent?.trim() ?? null
    const verified = g.querySelector('.h-basic-badge')?.getAttribute?.('title') ?? null
    const works = Array.from(g.querySelectorAll('.video-card .title, .small-item .title'))
      .map(el => el.textContent?.trim() ?? '').filter(title => title.length > 0).slice(0, 10)
    return { nickname, bio, verified, works }
  },
}

/** Minimal DOM surface the in-page snippets rely on (browser-side only). */
interface DocumentApi {
  querySelector(selector: string): { textContent?: string | null; getAttribute?(name: string): string | null } | null
  querySelectorAll(selector: string): ArrayLike<{ textContent?: string | null }>
}

/** Render one extraction into the labeled AI section text. Same input, same bytes. */
export function renderSocialSection(platform: SocialPlatform, url: string, extraction: SocialProfileExtraction): string {
  const lines = [
    `【${SOCIAL_PLATFORM_LABELS[platform]}】${url}`,
    `昵称：${extraction.nickname ?? '未获取'}`,
    `简介：${extraction.bio ?? '未获取'}`,
  ]
  if (extraction.verified !== null) lines.push(`认证：${extraction.verified}`)
  lines.push(extraction.works.length > 0 ? `作品标题：${extraction.works.join('；')}` : '作品标题：未获取')
  return lines.join('\n')
}

/**
 * The queued capture processor behind the contentOutputs social faces.
 * State lives on disk (sessions + counters), never in memory; logins are
 * deduplicated per platform; every capture consumes one daily slot before
 * the browser opens.
 */
export class SocialCaptureProcessor {
  private readonly statesDir: string
  private readonly maxDailyCaptures: number
  private readonly logins = new Map<SocialPlatform, Promise<void>>()

  constructor(
    config: SocialCaptureConfig,
    private readonly deps: SocialCaptureDeps = {},
  ) {
    const max = config.maxDailyCaptures ?? SOCIAL_CAPTURE_MAX_DAILY
    if (!Number.isInteger(max) || max < 1 || max > 10) throw new Error('contentOutputs maxDailyCaptures must be an integer from 1 through 10')
    this.statesDir = config.socialStatesDir ?? join(resolveDshHome(), 'social-states')
    this.maxDailyCaptures = max
  }

  /** Per-platform availability: stored session presence plus today's capture count. */
  async statuses(): Promise<SocialStatuses> {
    const counters = await readCounters(this.statesDir, this.deps.now?.() ?? new Date())
    const rows = await Promise.all(SOCIAL_PLATFORMS.map(async platform => ({
      platform,
      hasSession: await hasSession(this.statesDir, platform),
      captureCountToday: counters.counts[platform] ?? 0,
    })))
    return { rows, dailyCap: this.maxDailyCaptures }
  }

  /**
   * Start the headed login flow for one platform and return immediately;
   * the browser stays open until the session cookie appears or the
   * 3-minute deadline passes. Concurrent logins per platform collapse onto
   * the running promise. Failures surface through `statuses()` staying
   * session-less and a console error here.
   */
  startLogin(platform: SocialPlatform): void {
    const existing = this.logins.get(platform)
    if (existing !== undefined) return
    const run = this.runLogin(platform).finally(() => { this.logins.delete(platform) })
    this.logins.set(platform, run)
  }

  private async runLogin(platform: SocialPlatform): Promise<void> {
    const meta = SOCIAL_PLATFORM_META[platform]
    const openPage = this.deps.openPage ?? openPlaywrightPage
    const sleep = this.deps.sleep ?? defaultSleep
    const page = await openPage({ headless: false, storageStatePath: null })
    try {
      await page.goto(meta.loginUrl)
      const deadline = Date.now() + LOGIN_TIMEOUT_MS
      let loggedIn = false
      while (Date.now() < deadline) {
        await sleep(LOGIN_POLL_MS)
        if (await page.hasCookie(meta.sessionCookie, meta.loginSuccessUrl)) {
          loggedIn = true
          break
        }
      }
      if (!loggedIn) throw new Error(`登录超时（${String(LOGIN_TIMEOUT_MS / 1000)} 秒）`)
      await saveSession(this.statesDir, platform, await page.storageState())
    } catch (error) {
      console.error(`[social-capture] ${platform} login failed:`, error)
      throw error
    } finally {
      await page.close()
    }
  }

  /** Whether a login flow is currently running for the platform. */
  loginPending(platform: SocialPlatform): boolean {
    return this.logins.has(platform)
  }

  /**
   * Capture one profile: consumes a daily slot, opens a headless logged-in
   * page on the user-provided URL, extracts the profile facts, and returns
   * the rendered labeled section for the social AI face.
   */
  async capture(platform: SocialPlatform, url: string, now: Date = this.deps.now?.() ?? new Date()): Promise<SocialCaptureResult> {
    const meta = SOCIAL_PLATFORM_META[platform]
    const trimmed = url.trim()
    if (!meta.profileUrlPattern.test(trimmed)) {
      throw new Error(`链接不是${meta.label}的主页地址（应为 ${meta.profileUrlPattern.source} 开头），请检查第 2 步该平台的链接`)
    }
    await consumeCapture(this.statesDir, platform, this.maxDailyCaptures, now)
    if (!(await hasSession(this.statesDir, platform))) throw new Error(`${meta.label}还没有登录会话，请先点击「登录」`)
    const openPage = this.deps.openPage ?? openPlaywrightPage
    const page = await openPage({ headless: true, storageStatePath: sessionPath(this.statesDir, platform) })
    try {
      await page.goto(trimmed)
      await (this.deps.sleep ?? defaultSleep)(SPA_RENDER_WAIT_MS)
      const extraction = await page.extract(platform)
      if (extraction.nickname === null) {
        const current = page.currentUrl()
        if (/passport|login|verify/u.test(current)) throw new Error(`${meta.label}登录已过期，请重新点击「登录」`)
        throw new Error(`${meta.label}页面结构可能已改版，未能读取主页信息；请手动粘贴主页内容`)
      }
      return { platform, url: trimmed, text: renderSocialSection(platform, trimmed, extraction), capturedAt: now.toISOString() }
    } finally {
      await page.close()
    }
  }

  /**
   * Verify one stored session against its platform: a headless read of the
   * platform home checking the live session cookie (and that the page did
   * not bounce to a login domain). Not a profile read — no frequency slot.
   */
  async verify(platform: SocialPlatform): Promise<{ platform: SocialPlatform; valid: boolean; nickname: string | null }> {
    const meta = SOCIAL_PLATFORM_META[platform]
    if (!(await hasSession(this.statesDir, platform))) return { platform, valid: false, nickname: null }
    const openPage = this.deps.openPage ?? openPlaywrightPage
    const page = await openPage({ headless: true, storageStatePath: sessionPath(this.statesDir, platform) })
    try {
      await page.goto(meta.loginSuccessUrl)
      await (this.deps.sleep ?? defaultSleep)(SPA_RENDER_WAIT_MS)
      const valid = (await page.hasCookie(meta.sessionCookie, meta.loginSuccessUrl))
        && !/passport|login|verify/u.test(page.currentUrl())
      return { platform, valid, nickname: null }
    } finally {
      await page.close()
    }
  }

  /** Drop the stored session for one platform. */
  async forget(platform: SocialPlatform): Promise<void> {
    await forgetSession(this.statesDir, platform)
  }
}
