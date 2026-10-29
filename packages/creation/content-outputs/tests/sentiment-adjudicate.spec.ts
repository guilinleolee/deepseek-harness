/**
 * The alert adjudication engine: opposed stances run in parallel and are
 * capped, the synthesis falls back to a deterministic join of the two
 * stances when it fails, and the verdict attaches to the stored alert and
 * survives a manifest round-trip.
 */
import { mkdtempSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import type { Context } from '@deepseek-ai/cordis'
import type { SentimentAlert, SentimentMention, SentimentTask } from '../src/sentiment/types.ts'
import { SENTIMENT_FILENAME, appendSentimentScanFile, putSentimentAlertAdjudicationFile, putSentimentTaskFile, readSentimentFile } from '../src/sentiment/store.ts'

const CTX = {} as Context
const POLICY = { provider: 'p', model: 'm', timeoutMs: 1_000, maxOutputTokens: 1_000 }
const NOW = new Date('2026-10-22T08:00:00.000Z')

function alert(): SentimentAlert {
  return {
    id: 'a-1' as SentimentAlert['id'], taskId: 't-1' as SentimentAlert['taskId'], eventKey: 't-1:2026-10-22',
    level: 2, summary: '投诉聚集', reason: '负面提及 3 条；热度 600', mentionIds: ['m-1' as SentimentMention['id']],
    handled: false, createdAt: '2026-10-22T08:00:00.000Z', handledAt: null,
  }
}

function task(): SentimentTask {
  return {
    id: 't-1' as SentimentTask['id'], name: '品牌口碑', group: 'brand', enabled: true,
    subjects: ['卡巴格'], keywordGroups: [], sources: ['weibo'], feedUrls: [], intervalMinutes: 60,
    createdAt: '2026-10-22T00:00:00.000Z', updatedAt: '2026-10-22T00:00:00.000Z',
  }
}

function mention(): SentimentMention {
  return {
    id: 'm-1' as SentimentMention['id'], taskId: 't-1' as SentimentMention['taskId'],
    source: 'weibo', platform: '微博', url: 'https://m.weibo.cn/detail/1', title: '投诉标题',
    summary: '摘要', publishedAt: null, capturedAt: '2026-10-22T08:00:00.000Z', polarity: 'neg',
    confidence: 0.9, evidence: '投诉', heat: null, author: null,
  }
}

function mockAi(handler: (system: string, framed: string) => Promise<string>): void {
  vi.doMock('../src/gather/ai.ts', () => ({
    streamLlmText: (_ctx: unknown, _policy: unknown, system: string, framed: string) => Promise.resolve().then(() => handler(system, framed)),
    AiCallPolicy: class {},
  }))
}

describe('adjudicateSentimentAlert', () => {
  beforeEach(() => { vi.resetModules() })
  afterEach(() => { vi.doUnmock('../src/gather/ai.ts'); vi.resetModules() })

  it('returns both stances and the synthesized verdict, framing the alert and mentions', async () => {
    const seenFrames: string[] = []
    mockAi(async (_system, framed) => {
      seenFrames.push(framed)
      if (_system.includes('乐观审读')) return '可能是一次性物流延误，已有客服跟进。'
      if (_system.includes('审慎审读')) return '投诉短语已被自媒体转载，存在扩散风险。'
      return '部分属实：建议 24 小时内发布跟进说明。'
    })
    const { adjudicateSentimentAlert } = await import('../src/sentiment/adjudicate.ts')
    const verdict = await adjudicateSentimentAlert(CTX, POLICY, alert(), task(), [mention()], NOW)
    expect(verdict.optimistic).toContain('物流延误')
    expect(verdict.cautious).toContain('扩散风险')
    expect(verdict.conclusion).toContain('部分属实')
    expect(verdict.at).toBe('2026-10-22T08:00:00.000Z')
    expect(seenFrames.some(frame => frame.includes('投诉聚集'))).toBe(true)
    expect(seenFrames.every(frame => frame.includes('投诉标题'))).toBe(true)
  })

  it('falls back to a deterministic join when the synthesis fails, and degrades stances individually', async () => {
    let calls = 0
    mockAi(async system => {
      calls += 1
      if (system.includes('综合')) throw new Error('synthesis down')
      if (system.includes('乐观审读')) throw new Error('optimist down')
      return '风险有限，但需盯转载。'
    })
    const { adjudicateSentimentAlert } = await import('../src/sentiment/adjudicate.ts')
    const verdict = await adjudicateSentimentAlert(CTX, POLICY, alert(), task(), [mention()], NOW)
    expect(verdict.optimistic).toBe('（本视角生成失败）')
    expect(verdict.cautious).toContain('风险有限')
    expect(verdict.conclusion).toContain('乐观视角')
    expect(verdict.conclusion).toContain('审慎视角')
    expect(calls).toBe(3)
  })
})

describe('putSentimentAlertAdjudicationFile', () => {
  let dir: string
  beforeEach(() => { dir = mkdtempSync(join(tmpdir(), 'sentiment-adjudicate-')) })
  afterEach(() => { rmSync(dir, { recursive: true, force: true }) })

  const FILE = (): string => join(dir, SENTIMENT_FILENAME)

  it('attaches the verdict to the stored alert and it survives a round-trip', async () => {
    await putSentimentTaskFile(FILE(), {
      name: '品牌口碑', group: 'brand', enabled: true, subjects: ['卡巴格'],
      keywordGroups: [{ polarity: 'neg', terms: ['投诉'] }], sources: ['weibo'], feedUrls: [], intervalMinutes: 60,
    })
    await appendSentimentScanFile(FILE(), [mention()], [alert()])
    const updated = await putSentimentAlertAdjudicationFile(FILE(), 'a-1', {
      optimistic: '可能误报', cautious: '存在扩散风险', conclusion: '部分属实', at: '2026-10-22T09:00:00.000Z',
    })
    expect(updated.adjudication?.conclusion).toBe('部分属实')
    const read = await readSentimentFile(FILE())
    const stored = read.alerts.find(candidate => candidate.id === 'a-1')
    expect(stored?.adjudication?.optimistic).toBe('可能误报')
    // A later run replaces the earlier verdict.
    await putSentimentAlertAdjudicationFile(FILE(), 'a-1', {
      optimistic: '二读', cautious: '二慎', conclusion: '二断', at: '2026-10-22T10:00:00.000Z',
    })
    const reread = await readSentimentFile(FILE())
    const replaced = reread.alerts.find(candidate => candidate.id === 'a-1')
    expect(replaced?.adjudication?.conclusion).toBe('二断')
  })

  it('rejects an unknown alert id and an invalid verdict', async () => {
    await expect(putSentimentAlertAdjudicationFile(FILE(), 'absent', {
      optimistic: 'o', cautious: 'c', conclusion: 'x', at: '2026-10-22T08:00:00.000Z',
    })).rejects.toThrow(/unknown sentiment alert/iu)
    await putSentimentTaskFile(FILE(), {
      name: '品牌口碑', group: 'brand', enabled: true, subjects: ['卡巴格'],
      keywordGroups: [{ polarity: 'neg', terms: ['投诉'] }], sources: ['weibo'], feedUrls: [], intervalMinutes: 60,
    })
    await appendSentimentScanFile(FILE(), [mention()], [alert()])
    await expect(putSentimentAlertAdjudicationFile(FILE(), 'a-1', {
      optimistic: '', cautious: 'c', conclusion: 'x', at: '2026-10-22T08:00:00.000Z',
    })).rejects.toThrow(/invalid sentiment alert adjudication/iu)
  })
})
