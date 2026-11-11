/**
 * The sentiment alert push: message formatting (severity first, cap with an
 * overflow line), the channel gate (switch off / no alerts / unconfigured
 * channels fire nothing), and per-channel failure stringification through
 * an injected fetch.
 */
import { describe, expect, it } from 'vitest'
import type { SentimentAlert, SentimentAlertId, SentimentMention, SentimentSettings, SentimentTask } from '../src/sentiment/types.ts'
import {
  SENTIMENT_PUSH_ALERT_CAP, SENTIMENT_PUSH_MAX_ATTEMPTS, SENTIMENT_PUSH_RETRY_COOLDOWN_MS,
  advanceAlertDelivery, advanceChannelDelivery, formatAlertMessage, freshChannelDelivery, isAlertRetryDue,
  isChannelRetryDue, pushAlertRound, pushDingtalk, pushEmail, pushTestRound, pushWecom,
} from '../src/sentiment/push.ts'

const NOW = '2026-10-11T08:30:00.000Z'

function alert(overrides: Partial<SentimentAlert> = {}): SentimentAlert {
  return {
    id: 'sa-1' as SentimentAlertId, taskId: 'st-1' as SentimentTask['id'],
    eventKey: 'st-1:2026-10-11', level: 2, summary: '负面提及聚集', reason: '负面提及 3 条；热度 300',
    mentionIds: ['m-1' as SentimentMention['id']], handled: false, createdAt: NOW, handledAt: null,
    ...overrides,
  }
}

function task(overrides: Partial<SentimentTask> = {}): SentimentTask {
  return {
    id: 'st-1' as SentimentTask['id'], name: '品牌口碑', group: 'brand', enabled: true,
    subjects: ['卡巴格'], keywordGroups: [{ polarity: 'neg', terms: ['投诉'] }],
    sources: ['rss'], feedUrls: ['https://news.example/rss'], intervalMinutes: 60,
    createdAt: NOW, updatedAt: NOW, ...overrides,
  }
}

function settings(overrides: Partial<SentimentSettings> = {}): SentimentSettings {
  return {
    negativeHeatThreshold: 300, negativeSurgePercent: 50, domainBlacklist: [], accountBlacklist: [],
    retentionDays: 90, notifyEnabled: true,
    dingtalkWebhook: 'https://oapi.dingtalk.com/robot/send?access_token=a',
    wecomWebhook: 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=b',
    email: null,
    smtpHost: null, smtpPort: 465, smtpUser: null, smtpPassword: null, smtpFrom: null,
    ...overrides,
  }
}

declare module '../src/sentiment/types.ts' {
  interface SentimentMentionIdBrand { readonly brand: unique symbol }
}

describe('formatAlertMessage', () => {
  it('sorts by severity and names the task', () => {
    const message = formatAlertMessage(
      [alert({ level: 3, summary: '低级告警' }), alert({ level: 1, summary: '最严重' })],
      [task()], NOW,
    )
    const lines = message.split('\n')
    expect(lines[0]).toContain('新增 2 条')
    expect(lines[1]).toContain('L1')
    expect(lines[1]).toContain('最严重')
    expect(lines[2]).toContain('L3')
    expect(lines[2]).toContain('低级告警')
    expect(lines[2]).toContain('品牌口碑')
  })

  it('caps the lines and names the overflow', () => {
    const many = Array.from({ length: SENTIMENT_PUSH_ALERT_CAP + 3 }, (_, i) => alert({ id: `sa-${String(i)}` as SentimentAlertId, summary: `告警${String(i)}`, level: 4 }))
    const message = formatAlertMessage(many, [task()], NOW)
    expect(message).toContain(`告警${String(SENTIMENT_PUSH_ALERT_CAP - 1)}`)
    expect(message).toContain('其余 3 条见工作台告警中心')
  })
})

describe('pushAlertRound', () => {
  it('is a no-op when disabled, or when no alerts fired', async () => {
    const posts: string[] = []
    const fetchImpl: typeof fetch = async (input) => {
      posts.push(typeof input === 'string' ? input : input instanceof URL ? input.href : input.url)
      return new Response('{}', { status: 200 })
    }
    const off = await pushAlertRound(settings({ notifyEnabled: false }), [alert()], [task()], NOW, { fetchImpl })
    const none = await pushAlertRound(settings(), [], [task()], NOW, { fetchImpl })
    expect(off.dingtalk).toEqual({ attempted: false, error: null })
    expect(none.wecom).toEqual({ attempted: false, error: null })
    expect(posts).toHaveLength(0)
  })

  it('posts one digest per configured channel', async () => {
    const bodies: unknown[] = []
    const fetchImpl: typeof fetch = async (_input, init) => {
      const raw: BodyInit | null | undefined = init?.body
      bodies.push(JSON.parse(typeof raw === 'string' ? raw : ''))
      return new Response('{}', { status: 200 })
    }
    const result = await pushAlertRound(settings(), [alert()], [task()], NOW, { fetchImpl })
    expect(result.dingtalk).toEqual({ attempted: true, error: null })
    expect(result.wecom).toEqual({ attempted: true, error: null })
    expect(bodies).toHaveLength(2)
    for (const body of bodies) {
      const text = (body as { text: { content: string } }).text.content
      expect(text).toContain('L2 品牌口碑：负面提及聚集')
    }
  })

  it('skips unconfigured channels and stringifies failures', async () => {
    const posts: string[] = []
    const fetchImpl: typeof fetch = async (input) => {
      posts.push(typeof input === 'string' ? input : input instanceof URL ? input.href : input.url)
      if (posts.at(-1)?.includes('dingtalk')) return new Response('err', { status: 500 })
      throw new Error('network down')
    }
    const result = await pushAlertRound(
      settings({ wecomWebhook: null }), [alert()], [task()], NOW, { fetchImpl },
    )
    expect(posts).toHaveLength(1)
    expect(result.dingtalk).toEqual({ attempted: true, error: 'HTTP 500' })
    expect(result.wecom).toEqual({ attempted: false, error: null })
  })
})

describe('alert delivery states', () => {
  it('advances pending → delivered on success and counts failures to a terminal failed', () => {
    const fresh = freshChannelDelivery()
    const ok = advanceChannelDelivery(fresh, { attempted: true, error: null }, NOW)
    expect(ok).toEqual({ status: 'delivered', attempts: 1, lastAt: NOW, lastError: null })
    let current = fresh
    for (let attempt = 1; attempt < SENTIMENT_PUSH_MAX_ATTEMPTS; attempt += 1) {
      current = advanceChannelDelivery(current, { attempted: true, error: 'HTTP 500' }, NOW)
      expect(current.status).toBe('pending')
    }
    const terminal = advanceChannelDelivery(current, { attempted: true, error: 'HTTP 500' }, NOW)
    expect(terminal.status).toBe('failed')
    expect(terminal.attempts).toBe(SENTIMENT_PUSH_MAX_ATTEMPTS)
    expect(advanceChannelDelivery(terminal, { attempted: true, error: null }, NOW)).toBe(terminal)
  })

  it('gates retries by cooldown, cap, and status', () => {
    const fresh = freshChannelDelivery()
    expect(isChannelRetryDue(fresh, new Date(Date.parse(NOW) + 1))).toBe(true)
    const tried = { status: 'pending' as const, attempts: 1, lastAt: NOW, lastError: 'HTTP 500' }
    expect(isChannelRetryDue(tried, new Date(Date.parse(NOW) + SENTIMENT_PUSH_RETRY_COOLDOWN_MS - 1))).toBe(false)
    expect(isChannelRetryDue(tried, new Date(Date.parse(NOW) + SENTIMENT_PUSH_RETRY_COOLDOWN_MS))).toBe(true)
    const capped = { ...tried, attempts: SENTIMENT_PUSH_MAX_ATTEMPTS }
    expect(isChannelRetryDue(capped, new Date())).toBe(false)
    const delivered = { ...tried, status: 'delivered' as const }
    expect(isChannelRetryDue(delivered, new Date())).toBe(false)
  })

  it('skips handled, untracked, and all-cooling-down alerts in retry selection', () => {
    const now = new Date()
    const delivery = advanceAlertDelivery(alert(), {
      dingtalk: { attempted: true, error: 'HTTP 500' }, wecom: { attempted: false, error: null }, email: { attempted: false, error: null },
    }, NOW)
    const pending = alert({ delivery })
    expect(isAlertRetryDue(pending, new Date(Date.parse(NOW) + SENTIMENT_PUSH_RETRY_COOLDOWN_MS))).toBe(true)
    expect(isAlertRetryDue(alert({ delivery, handled: true, handledAt: NOW }), now)).toBe(false)
    expect(isAlertRetryDue(alert(), now)).toBe(false)
  })

  it('sends the test message to configured channels only, ignoring the notify switch', async () => {
    const posts: string[] = []
    const fetchImpl: typeof fetch = async (input) => {
      posts.push(typeof input === 'string' ? input : input instanceof URL ? input.href : input.url)
      return new Response('{}', { status: 200 })
    }
    const result = await pushTestRound(settings({ notifyEnabled: false }), { fetchImpl })
    expect(posts).toHaveLength(2)
    expect(result.dingtalk).toEqual({ attempted: true, error: null })
    expect(result.email).toEqual({ attempted: false, error: null })
  })
})

describe('channel helpers', () => {
  it('stringify non-Error throws and report null on ok', async () => {
    const okFetch: typeof fetch = async () => new Response('{}', { status: 200 })
    expect(await pushDingtalk('https://x', 'm', { fetchImpl: okFetch })).toBeNull()
    const throwFetch = (async () => { throw 'boom' }) as unknown as typeof fetch
    expect(await pushWecom('https://x', 'm', { fetchImpl: throwFetch })).toBe('boom')
  })
})

describe('pushEmail', () => {
  const smtp = (overrides: Partial<SentimentSettings> = {}): SentimentSettings => settings({
    email: 'ops@example.com',
    smtpHost: 'smtp.example.com',
    smtpUser: 'ops@example.com',
    smtpPassword: 'auth-code',
    smtpFrom: 'alerts@example.com',
    ...overrides,
  })

  it('sends one digest through the injected transport with TLS on 465', async () => {
    const mails: unknown[] = []
    const createTransport = (options: unknown): { sendMail: (mail: unknown) => Promise<unknown> } => {
      const typed = options as { host: string; port: number; secure: boolean; auth?: { user: string } }
      expect(typed.host).toBe('smtp.example.com')
      expect(typed.port).toBe(465)
      expect(typed.secure).toBe(true)
      expect(typed.auth?.user).toBe('ops@example.com')
      return { sendMail: async (mail: unknown) => { mails.push(mail) } }
    }
    expect(await pushEmail(smtp(), 'digest', { createTransport })).toBeNull()
    expect(mails).toHaveLength(1)
    expect((mails[0] as { subject: string }).subject).toBe('企业舆情告警')
    expect((mails[0] as { text: string }).text).toBe('digest')
  })

  it('sends nothing when the transport is not configured', async () => {
    const createTransport = (): { sendMail: (mail: unknown) => Promise<unknown> } => {
      throw new Error('must not be called')
    }
    expect(await pushEmail(settings(), 'digest', { createTransport })).toBeNull()
    expect(await pushEmail(smtp({ smtpHost: null }), 'digest', { createTransport })).toBeNull()
    expect(await pushEmail(smtp({ smtpPassword: null }), 'digest', { createTransport })).toBeNull()
  })

  it('stringifies transport failures', async () => {
    const createTransport = (): { sendMail: (mail: unknown) => Promise<unknown> } => ({
      sendMail: async () => { throw new Error('smtp refused') },
    })
    expect(await pushEmail(smtp(), 'digest', { createTransport })).toBe('smtp refused')
  })
})
