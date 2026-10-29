/**
 * The keyword-expansion middleware: defensive parsing of the model's term
 * list (junk bodies, non-strings, caps, dedup), the raw-subject fallback on
 * any failure, and the per-task cache (hits within the TTL, retries after a
 * failed expansion instead of pinning the degraded terms).
 */
import { describe, expect, it } from 'vitest'
import type { Context } from '@deepseek-ai/cordis'
import type { SentimentTask } from '../src/sentiment/types.ts'
import { expandTaskTerms, parseExpandOutput } from '../src/sentiment/expand.ts'

const CTX = {} as Context
const POLICY = { provider: 'test', model: 'test', timeoutMs: 1_000, maxOutputTokens: 100 }
let taskSeq = 0

function task(overrides: Partial<SentimentTask> = {}): SentimentTask {
  return {
    id: `t-${String(++taskSeq)}` as SentimentTask['id'],
    name: '品牌口碑监测',
    group: 'brand',
    enabled: true,
    subjects: ['卡巴格'],
    keywordGroups: [],
    sources: ['weibo'],
    feedUrls: [],
    intervalMinutes: 60,
    createdAt: '2026-10-20T00:00:00.000Z',
    updatedAt: '2026-10-20T00:00:00.000Z',
    ...overrides,
  }
}

describe('parseExpandOutput', () => {
  it('parses the terms array with trimming, dedup, and the cap', () => {
    const terms = parseExpandOutput('```json\n{"terms":["卡巴格"," 卡巴格 ","扫地机Pro"]}\n```')
    expect(terms).toEqual(['卡巴格', '扫地机Pro'])
  })

  it('caps the term list at 8 entries', () => {
    const terms = parseExpandOutput(JSON.stringify({ terms: Array.from({ length: 12 }, (_, i) => `词${String(i)}`) }))
    expect(terms).toHaveLength(8)
  })

  it('drops overlong and non-string entries', () => {
    expect(parseExpandOutput(JSON.stringify({ terms: ['好', 42, null, 'x'.repeat(120)] }))).toEqual(['好'])
  })

  it('yields an empty list on junk bodies', () => {
    expect(parseExpandOutput('对不起我做不到')).toEqual([])
    expect(parseExpandOutput('{"terms":"不是数组"}')).toEqual([])
    expect(parseExpandOutput('{"terms":[]}')).toEqual([])
    expect(parseExpandOutput('{"items":[]}')).toEqual([])
  })
})

describe('expandTaskTerms', () => {
  it('returns the model terms and caches them per task', async () => {
    let calls = 0
    const deps = {
      now: () => 1_000,
      expand: async () => {
        calls += 1
        return ['卡巴格', '卡巴格扫地机']
      },
    }
    const subject = task()
    expect(await expandTaskTerms(CTX, POLICY, subject, deps)).toEqual(['卡巴格', '卡巴格扫地机'])
    expect(await expandTaskTerms(CTX, POLICY, subject, deps)).toEqual(['卡巴格', '卡巴格扫地机'])
    expect(calls).toBe(1)
  })

  it('re-expands after the TTL or a subject change', async () => {
    let clock = 1_000
    let calls = 0
    const deps = {
      now: () => clock,
      expand: async () => {
        calls += 1
        return ['变体']
      },
    }
    const subject = task()
    await expandTaskTerms(CTX, POLICY, subject, deps)
    clock += 25 * 60 * 60 * 1000
    await expandTaskTerms(CTX, POLICY, subject, deps)
    expect(calls).toBe(2)
  })

  it('falls back to the raw subjects on model failure without caching it', async () => {
    let calls = 0
    const deps = {
      now: () => 1_000,
      expand: async () => {
        calls += 1
        throw new Error('timeout')
      },
    }
    const subject = task({ subjects: ['卡巴格', '竞品A'] })
    expect(await expandTaskTerms(CTX, POLICY, subject, deps)).toEqual(['卡巴格', '竞品A'])
    expect(await expandTaskTerms(CTX, POLICY, subject, deps)).toEqual(['卡巴格', '竞品A'])
    expect(calls).toBe(2)
  })

  it('falls back to the raw subjects on an empty model answer', async () => {
    const deps = { now: () => 1_000, expand: async () => [] as const }
    const subject = task({ subjects: ['卡巴格'] })
    expect(await expandTaskTerms(CTX, POLICY, subject, deps)).toEqual(['卡巴格'])
  })
})
