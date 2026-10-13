import { mkdtempSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { afterEach, beforeEach, describe, expect, it } from 'vitest'
import { renderSocialSection, SocialCaptureProcessor } from '../src/social/capture.ts'
import { consumeCapture, readCounters } from '../src/social/frequency.ts'
import { forgetSession, hasSession, readSession, saveSession } from '../src/social/sessions.ts'

let dir: string
beforeEach(() => { dir = mkdtempSync(join(tmpdir(), 'social-capture-')) })
afterEach(() => { rmSync(dir, { recursive: true, force: true }) })

const NOW = new Date('2026-10-05T08:00:00')
const STATE = JSON.stringify({ cookies: [{ name: 'web_session', value: 'v' }], origins: [] })

describe('sessions store', () => {
  it('round-trips a storage state and reports presence', async () => {
    expect(await hasSession(dir, 'xhs')).toBe(false)
    expect(await readSession(dir, 'xhs')).toBeNull()
    await saveSession(dir, 'xhs', STATE)
    expect(await hasSession(dir, 'xhs')).toBe(true)
    expect(await readSession(dir, 'xhs')).toBe(STATE)
    await forgetSession(dir, 'xhs')
    expect(await hasSession(dir, 'xhs')).toBe(false)
  })

  it('treats an unusable body as absent', async () => {
    await saveSession(dir, 'xhs', 'not json')
    expect(await hasSession(dir, 'xhs')).toBe(false)
  })
})

describe('frequency gate', () => {
  it('counts per platform and throws at the cap', async () => {
    await consumeCapture(dir, 'xhs', 2, NOW)
    await consumeCapture(dir, 'xhs', 2, NOW)
    await expect(consumeCapture(dir, 'xhs', 2, NOW)).rejects.toThrow('上限')
    // Other platforms keep their own counter.
    await expect(consumeCapture(dir, 'douyin', 2, NOW)).resolves.toBeUndefined()
    const counters = await readCounters(dir, NOW)
    expect(counters.counts).toEqual({ xhs: 2, douyin: 1 })
  })

  it('resets on the next local day', async () => {
    await consumeCapture(dir, 'xhs', 1, NOW)
    await expect(consumeCapture(dir, 'xhs', 1, NOW)).rejects.toThrow('上限')
    const nextDay = new Date('2026-10-06T08:00:00')
    await expect(consumeCapture(dir, 'xhs', 1, nextDay)).resolves.toBeUndefined()
  })
})

describe('renderSocialSection', () => {
  it('renders the labeled section deterministically', () => {
    const text = renderSocialSection('xhs', 'https://www.xiaohongshu.com/user/profile/1', {
      nickname: '老李',
      bio: '专注职场干货',
      verified: '职场博主',
      works: ['第一篇', '第二篇'],
    })
    expect(text).toBe('【小红书】https://www.xiaohongshu.com/user/profile/1\n昵称：老李\n简介：专注职场干货\n认证：职场博主\n作品标题：第一篇；第二篇')
    const bare = renderSocialSection('weibo', 'https://weibo.com/u/1', { nickname: null, bio: null, verified: null, works: [] })
    expect(bare).toContain('昵称：未获取')
    expect(bare).toContain('作品标题：未获取')
    expect(bare).not.toContain('认证')
  })
})

describe('SocialCaptureProcessor', () => {
  interface FakePage {
    url: string
    extraction: { nickname: string | null; bio: string | null; verified: string | null; works: string[] }
    loggedIn: boolean
  }

  /** A processor whose browser is a recording fake. */
  function processor(page: FakePage, now = NOW): SocialCaptureProcessor {
    return new SocialCaptureProcessor({ socialStatesDir: dir, maxDailyCaptures: 2 }, {
      openPage: async () => {
        let current = page.url
        return {
          // The fake lands every goto on the fixture's landing URL (simulating a site redirect).
          async goto(_url: string) { current = page.url },
          currentUrl: () => current,
          async hasCookie(): Promise<boolean> { return page.loggedIn },
          async storageState(): Promise<string> { return STATE },
          async extract() { return page.extraction },
          async close() { /* noop */ },
        }
      },
      now: () => now,
      sleep: async () => undefined,
    })
  }

  it('statuses report session presence and counters', async () => {
    const proc = processor({ url: 'https://www.xiaohongshu.com', extraction: { nickname: 'n', bio: null, verified: null, works: [] }, loggedIn: false })
    await saveSession(dir, 'xhs', STATE)
    await consumeCapture(dir, 'xhs', 3, NOW)
    const statuses = await proc.statuses()
    const xhs = statuses.rows.find(row => row.platform === 'xhs')
    expect(xhs).toEqual({ platform: 'xhs', hasSession: true, captureCountToday: 1 })
    expect(statuses.rows.find(row => row.platform === 'bili')?.hasSession).toBe(false)
  })

  it('rejects capture without a session, with a foreign URL, and past the cap', async () => {
    const proc = processor({ url: 'https://www.xiaohongshu.com', extraction: { nickname: 'n', bio: null, verified: null, works: [] }, loggedIn: true })
    // The no-session attempt consumes its slot first (compliance counts attempts).
    await expect(proc.capture('xhs', 'https://www.xiaohongshu.com/user/profile/1', NOW)).rejects.toThrow('还没有登录会话')
    await saveSession(dir, 'xhs', STATE)
    // A foreign URL rejects before any slot is consumed.
    await expect(proc.capture('xhs', 'https://weibo.com/u/123', NOW)).rejects.toThrow('不是小红书的主页地址')
    await consumeCapture(dir, 'xhs', 2, NOW)
    await expect(proc.capture('xhs', 'https://www.xiaohongshu.com/user/profile/1', NOW)).rejects.toThrow('上限')
  })

  it('captures the profile, consumes a slot, and renders the section', async () => {
    await saveSession(dir, 'xhs', STATE)
    const proc = processor({ url: 'https://www.xiaohongshu.com/user/profile/1', extraction: { nickname: '老李', bio: '职场干货', verified: null, works: ['第一篇'] }, loggedIn: true })
    const result = await proc.capture('xhs', ' https://www.xiaohongshu.com/user/profile/1 ', NOW)
    expect(result.text).toContain('【小红书】https://www.xiaohongshu.com/user/profile/1')
    expect(result.text).toContain('昵称：老李')
    const counters = await readCounters(dir, NOW)
    expect(counters.counts.xhs).toBe(1)
  })

  it('distinguishes an expired login from a structure change when the nickname is missing', async () => {
    await saveSession(dir, 'xhs', STATE)
    const expired = processor({ url: 'https://passport.xiaohongshu.com/login', extraction: { nickname: null, bio: null, verified: null, works: [] }, loggedIn: true })
    await expect(expired.capture('xhs', 'https://www.xiaohongshu.com/user/profile/1', NOW)).rejects.toThrow('登录已过期')
    const changed = processor({ url: 'https://www.xiaohongshu.com/user/profile/1', extraction: { nickname: null, bio: null, verified: null, works: [] }, loggedIn: true })
    await expect(changed.capture('xhs', 'https://www.xiaohongshu.com/user/profile/1', NOW)).rejects.toThrow('页面结构可能已改版')
  })

  it('startLogin persists the session once the cookie appears', async () => {
    const proc = processor({ url: 'https://www.xiaohongshu.com', extraction: { nickname: null, bio: null, verified: null, works: [] }, loggedIn: true })
    proc.startLogin('xhs')
    // startLogin returns before the flow finishes; the wait completes fast with the injected sleep.
    await new Promise(resolve => setTimeout(resolve, 50))
    expect(await hasSession(dir, 'xhs')).toBe(true)
  })
})
