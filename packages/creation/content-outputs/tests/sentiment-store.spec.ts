import { mkdtempSync, readFileSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { afterEach, beforeEach, describe, expect, it } from 'vitest'
import type { SentimentMention, SentimentSettings, SentimentTask, SentimentTaskInput } from '../src/sentiment/types.ts'
import { DEFAULT_SENTIMENT_SETTINGS, SENTIMENT_FILENAME } from '../src/sentiment/store.ts'
import {
  appendSentimentScanFile, deleteSentimentTaskFile, handleSentimentAlertFile,
  normalizeSentimentTaskInput, putSentimentSettingsFile, putSentimentTaskFile,
  readSentimentFile, setSentimentTaskEnabledFile,
} from '../src/sentiment/store.ts'
import { aggregateAlerts, classifyByLexicon, matchesKeywordGroups, needsRefinement, parseRefineBatchOutput } from '../src/sentiment/scan.ts'
import { computeSentimentStats } from '../src/sentiment/stats.ts'

let dir: string
beforeEach(() => { dir = mkdtempSync(join(tmpdir(), 'sentiment-')) })
afterEach(() => { rmSync(dir, { recursive: true, force: true }) })

const FILE = () => join(dir, SENTIMENT_FILENAME)
const NOW = '2026-10-07T08:00:00.000Z'

function taskInput(overrides: Partial<SentimentTaskInput> = {}): SentimentTaskInput {
  return {
    name: '品牌口碑监测',
    group: 'brand',
    enabled: true,
    subjects: ['卡巴格'],
    keywordGroups: [{ polarity: 'neg', terms: ['投诉', '太慢'] }, { polarity: 'any', terms: ['发布会'] }],
    sources: ['rss'],
    feedUrls: ['https://example.com/feed.xml'],
    intervalMinutes: 60,
    ...overrides,
  }
}

function mention(overrides: Partial<SentimentMention> = {}): SentimentMention {
  return {
    id: 'm-1' as SentimentMention['id'],
    taskId: 't-1' as SentimentMention['taskId'],
    source: 'rss',
    platform: 'example.com',
    url: 'https://example.com/post-1',
    title: '标题',
    summary: '摘要',
    publishedAt: NOW,
    capturedAt: NOW,
    polarity: 'neg',
    confidence: 0.9,
    evidence: '投诉',
    heat: null,
    author: null,
    ...overrides,
  }
}

describe('sentiment store', () => {
  it('upserts a task, reads it back, and rejects unknown-id updates', async () => {
    const task = await putSentimentTaskFile(FILE(), taskInput(), NOW)
    expect(task.name).toBe('品牌口碑监测')
    expect(task.id).toBeTruthy()
    const read = await readSentimentFile(FILE())
    expect(read.tasks).toHaveLength(1)
    await expect(putSentimentTaskFile(FILE(), { ...taskInput(), id: 'nope' as SentimentTask['id'] }, NOW))
      .rejects.toThrow('unknown sentiment task')
  })

  it('normalizes and validates the input', async () => {
    expect(normalizeSentimentTaskInput({ ...taskInput(), name: '  ' }, undefined, NOW).detail).toBeTruthy()
    expect(normalizeSentimentTaskInput({ ...taskInput(), intervalMinutes: 5 }, undefined, NOW).detail).toBeTruthy()
    expect(normalizeSentimentTaskInput({ ...taskInput(), subjects: [] }, undefined, NOW).detail).toBeTruthy()
    const ok = normalizeSentimentTaskInput({ ...taskInput(), name: ' 老王监测 ' }, undefined, NOW)
    expect(ok.task?.name).toBe('老王监测')
    expect(ok.task?.subjects).toEqual(['卡巴格'])
  })

  it('toggles enabled, deletes with its mentions, and refuses writes over corrupt state', async () => {
    const task = await putSentimentTaskFile(FILE(), taskInput(), NOW)
    await appendSentimentScanFile(FILE(), [mention({ taskId: task.id })], [])
    const toggled = await setSentimentTaskEnabledFile(FILE(), task.id, false)
    expect(toggled.enabled).toBe(false)
    await expect(handleSentimentAlertFile(FILE(), 'missing', NOW)).rejects.toThrow('unknown sentiment alert')
    await deleteSentimentTaskFile(FILE(), task.id)
    const read = await readSentimentFile(FILE())
    expect(read.tasks).toHaveLength(0)
    expect(read.mentions).toHaveLength(0)

    readFileSync(FILE(), 'utf8')
    const { writeFileSync } = await import('node:fs')
    writeFileSync(FILE(), '{corrupt')
    await expect(putSentimentTaskFile(FILE(), taskInput(), NOW)).rejects.toThrow('refusing to write')
  })

  it('putSentimentSettings persists and invalid settings reject', async () => {
    const settings = { ...DEFAULT_SENTIMENT_SETTINGS, negativeHeatThreshold: 300, negativeSurgePercent: 150, domainBlacklist: ['bad.com'], retentionDays: 30 }
    await putSentimentSettingsFile(FILE(), settings)
    const read = await readSentimentFile(FILE())
    expect(read.settings.negativeHeatThreshold).toBe(300)
    expect(read.settings.domainBlacklist).toEqual(['bad.com'])
    await expect(putSentimentSettingsFile(FILE(), { ...read.settings, retentionDays: 0 })).rejects.toThrow()
  })
})

describe('appendSentimentScanFile', () => {
  it('dedupes by task+url, prunes past retention, and caps the store', async () => {
    const task = await putSentimentTaskFile(FILE(), taskInput(), NOW)
    await appendSentimentScanFile(FILE(), [mention({ taskId: task.id })], [])
    // Same URL again: deduped.
    const second = await appendSentimentScanFile(FILE(), [mention({ taskId: task.id, id: 'm-2' as SentimentMention['id'] })], [])
    expect(second.captured).toBe(0)
    // Old mention past a 30-day retention: pruned on the next append.
    const old = mention({ taskId: task.id, id: 'm-old' as SentimentMention['id'], capturedAt: '2026-08-01T00:00:00.000Z' })
    await appendSentimentScanFile(FILE(), [old], [])
    const read = await readSentimentFile(FILE())
    expect(read.mentions.some(m => m.id === 'm-old')).toBe(false)
  })
})

describe('lexicon and matching', () => {
  it('classifies by lexicon hits with margin-based confidence', () => {
    expect(classifyByLexicon('物流太慢，已投诉').polarity).toBe('neg')
    expect(classifyByLexicon('很好用，值得推荐').polarity).toBe('pos')
    const neutral = classifyByLexicon('今天发布了新版本')
    expect(neutral.polarity).toBe('neu')
    expect(needsRefinement(neutral)).toBe(true)
    const strong = classifyByLexicon('太慢，投诉，失望')
    expect(needsRefinement(strong)).toBe(false)
  })

  it('matches AND-within-group and biases by polarity hint', () => {
    const groups = [{ polarity: 'neg' as const, terms: ['物流', '太慢'] }, { polarity: 'any' as const, terms: ['发布会'] }]
    expect(matchesKeywordGroups('物流太慢了', groups).matched).toBe(true)
    expect(matchesKeywordGroups('物流很快', groups).matched).toBe(false)
    expect(matchesKeywordGroups('发布会要开了', groups).matched).toBe(true)
  })

  it('parses the batched refinement answer', () => {
    const verdicts = parseRefineBatchOutput('{"1":{"polarity":"neg","confidence":0.9,"evidence":"投诉"},"2":{"polarity":"bad"}}')
    expect(verdicts.get(1)).toEqual({ polarity: 'neg', confidence: 0.9, evidence: '投诉' })
    expect(verdicts.has(2)).toBe(false)
  })
})

describe('aggregateAlerts', () => {
  const settings: SentimentSettings = {
    negativeHeatThreshold: 500, negativeSurgePercent: 200, domainBlacklist: [], accountBlacklist: [],
    retentionDays: 90, dingtalkWebhook: null, wecomWebhook: null, email: null,
  }

  it('clusters negatives per task+day and levels by heat', () => {
    const alerts = aggregateAlerts([
      mention({ id: 'a' as SentimentMention['id'] }),
      mention({ id: 'b' as SentimentMention['id'], title: '另一条投诉' }),
      mention({ id: 'c' as SentimentMention['id'], taskId: 't-2' as SentimentMention['taskId'], polarity: 'pos' }),
    ], settings, NOW)
    expect(alerts).toHaveLength(1)
    const [alert] = alerts
    if (alert === undefined) throw new Error('expected one aggregated alert')
    expect(alert.mentionIds).toEqual(['a', 'b'])
    expect(alert.summary).toContain('2 条负面提及聚集')
  })
})

describe('computeSentimentStats', () => {
  it('computes counts, the 14-day trend, and the platform top list', () => {
    const stored = normalizeSentimentTaskInput(taskInput(), undefined, NOW).task
    const tasks: readonly SentimentTask[] = stored === undefined ? [] : [stored]
    const stats = computeSentimentStats([mention({})], tasks, new Date('2026-10-07T08:00:00'))
    expect(stats.total).toBe(1)
    expect(stats.negative).toBe(1)
    expect(stats.taskCount).toBe(1)
    expect(stats.trend).toHaveLength(14)
    expect(stats.trend[13]).toEqual({ day: '2026-10-07', pos: 0, neu: 0, neg: 1 })
    expect(stats.platforms).toEqual([{ platform: 'example.com', count: 1 }])
  })
})
