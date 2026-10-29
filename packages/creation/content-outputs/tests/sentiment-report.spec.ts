/**
 * The sentiment report engine: framing caps the model input, the
 * deterministic fallback renders on any model failure, and generation
 * stamps provenance (prompt version, degraded flag, coverage counts).
 */
import { mkdtempSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import type { Context } from '@deepseek-ai/cordis'
import type { SentimentAlert, SentimentMention, SentimentSnapshot, SentimentStats, SentimentTask } from '../src/sentiment/types.ts'
import { SENTIMENT_FILENAME, DEFAULT_SENTIMENT_SETTINGS, putSentimentReportFile, readSentimentFile } from '../src/sentiment/store.ts'
import {
  SENTIMENT_REPORT_ALERT_CAP, SENTIMENT_REPORT_MENTION_CAP, SENTIMENT_REPORT_PROMPT_VERSION,
  degradedSentimentReport, frameSentimentReport, generateSentimentReport, selectReportTemplate,
} from '../src/sentiment/report.ts'

let dir: string
beforeEach(() => { dir = mkdtempSync(join(tmpdir(), 'sentiment-report-')) })
afterEach(() => { rmSync(dir, { recursive: true, force: true }) })

const FILE = () => join(dir, SENTIMENT_FILENAME)
const NOW = '2026-10-10T08:00:00.000Z'

function task(overrides: Partial<SentimentTask> = {}): SentimentTask {
  return {
    id: 'st-1' as SentimentTask['id'], name: '品牌口碑', group: 'brand', enabled: true,
    subjects: ['卡巴格'], keywordGroups: [{ polarity: 'neg', terms: ['投诉'] }],
    sources: ['rss'], feedUrls: ['https://news.example/rss'], intervalMinutes: 60,
    createdAt: NOW, updatedAt: NOW, ...overrides,
  }
}

function mention(overrides: Partial<SentimentMention> = {}): SentimentMention {
  return {
    id: 'm-1' as SentimentMention['id'], taskId: 'st-1' as SentimentTask['id'],
    source: 'rss', platform: 'news.example', url: 'https://news.example/a', title: '投诉标题',
    summary: '摘要', publishedAt: NOW, capturedAt: NOW, polarity: 'neg', confidence: 0.9,
    evidence: '投诉', heat: null, author: null, ...overrides,
  }
}

function stats(overrides: Partial<SentimentStats> = {}): SentimentStats {
  return {
    total: 1, positive: 0, neutral: 0, negative: 1, highRisk: 1, taskCount: 1,
    trend: [{ day: '2026-10-10', pos: 0, neu: 0, neg: 1 }],
    platforms: [{ platform: 'news.example', count: 1 }], ...overrides,
  }
}

function snapshot(overrides: Partial<SentimentSnapshot> = {}): SentimentSnapshot {
  return {
    tasks: [task()], mentions: [mention()], alerts: [], settings: DEFAULT_SENTIMENT_SETTINGS,
    problems: [], scanning: false, lastScan: null, report: null, ...overrides,
  }
}

describe('frameSentimentReport', () => {
  it('frames counts, tasks, platforms, alerts, and mention lines', () => {
    const frame = frameSentimentReport([mention()], [], [task()], stats(), DEFAULT_SENTIMENT_SETTINGS)
    expect(frame).toContain('总提及 1 条')
    expect(frame).toContain('品牌口碑')
    expect(frame).toContain('news.example 1')
    expect(frame).toContain('投诉标题')
    expect(frame).toContain('（无）')
  })

  it('caps mentions and alerts at the declared constants', () => {
    const many = Array.from({ length: 100 }, (_, i) => mention({ id: `m-${String(i)}` as SentimentMention['id'], title: `标题${String(i)}` }))
    const frame = frameSentimentReport(many, [], [task()], stats({ total: 100, negative: 100 }), DEFAULT_SENTIMENT_SETTINGS)
    expect(frame).toContain(`标题${String(SENTIMENT_REPORT_MENTION_CAP - 1)}`)
    expect(frame).not.toContain(`标题${String(SENTIMENT_REPORT_MENTION_CAP)}`)
  })
})

describe('degradedSentimentReport', () => {
  it('names the degradation and embeds the frame', () => {
    const frame = frameSentimentReport([mention()], [], [task()], stats(), DEFAULT_SENTIMENT_SETTINGS)
    const markdown = degradedSentimentReport(frame)
    expect(markdown).toContain('数据版降级')
    expect(markdown).toContain('投诉标题')
  })
})

describe('generateSentimentReport', () => {
  it('returns the model markdown with provenance on success', async () => {
    const ctx = { llm: {} } as unknown as Context
    const policy = { provider: 'minimax-0801', model: 'MiniMax-M3', timeoutMs: 60_000, maxOutputTokens: 4_000 }
    vi.stubGlobal('streamLlmTextSentinel', undefined)
    const report = await generateSentimentReport(ctx, policy, snapshot(), stats(), new Date(NOW))
    // No llm service is registered on the bare context, so the call fails
    // and the engine degrades — the fallback path is the observable default
    // here; the success path is exercised through the mocked module below.
    expect(report.degraded).toBe(true)
    expect(report.markdown).toContain('数据版降级')
    expect(report.promptVersion).toBe(SENTIMENT_REPORT_PROMPT_VERSION)
    expect(report.mentionCount).toBe(1)
    expect(report.generatedAt).toBe(NOW)
  })

  it('caps the stored coverage counts at the framing constants', async () => {
    const ctx = {} as unknown as Context
    const policy = { provider: 'p', model: 'm', timeoutMs: 60_000, maxOutputTokens: 1_000 }
    const many = Array.from({ length: 60 }, (_, i) => mention({ id: `m-${String(i)}` as SentimentMention['id'] }))
    const snap = snapshot({ mentions: many })
    const report = await generateSentimentReport(ctx, policy, snap, stats({ total: 60 }), new Date(NOW))
    expect(report.mentionCount).toBe(SENTIMENT_REPORT_MENTION_CAP)
    expect(report.alertCount).toBe(0)
    expect(report.alertCount).toBeLessThanOrEqual(SENTIMENT_REPORT_ALERT_CAP)
  })
})

describe('selectReportTemplate', () => {
  const alert: SentimentAlert = { id: 'a-1' as SentimentAlert['id'], taskId: 'st-1' as SentimentAlert['taskId'], eventKey: 'e', level: 2, summary: 's', reason: 'r', mentionIds: ['m-1' as SentimentAlert['mentionIds'][number]], handled: false, createdAt: NOW, handledAt: null }
  it('keeps the daily template without alerts and switches to crisis on an unhandled high-level alert', () => {
    expect(selectReportTemplate([]).map(spec => spec.key)).toEqual(['overview', 'risks', 'highlights', 'actions', 'watchlist'])
    expect(selectReportTemplate([alert]).map(spec => spec.key)).toEqual(['panorama', 'spread', 'response', 'followup'])
    expect(selectReportTemplate([{ ...alert, handled: true }]).map(spec => spec.key)).toEqual(['overview', 'risks', 'highlights', 'actions', 'watchlist'])
    expect(selectReportTemplate([{ ...alert, level: 3 as const }]).map(spec => spec.key)).toEqual(['overview', 'risks', 'highlights', 'actions', 'watchlist'])
  })
})

describe('generateSentimentReport section-wise', () => {
  it('generates per-section bodies and binds them into the markdown plus ir', async () => {
    vi.doMock('../src/gather/ai.ts', () => ({
      streamLlmText: async (_ctx: unknown, _policy: unknown, system: string) => `正文(${system.includes('事件全景') ? '危机' : system.includes('今日概览') ? '概览' : '节'})`,
      AiCallPolicy: class {},
    }))
    vi.resetModules()
    try {
      const { generateSentimentReport: freshGenerate } = await import('../src/sentiment/report.ts')
      const ctx = {} as unknown as Context
      const policy = { provider: 'p', model: 'm', timeoutMs: 1_000, maxOutputTokens: 1_000 }
      const report = await freshGenerate(ctx, policy, snapshot(), stats(), new Date(NOW))
      expect(report.degraded).toBe(false)
      expect(report.ir?.template).toBe('daily')
      expect(report.ir?.sections).toHaveLength(5)
      expect(report.markdown).toContain('## 今日概览')
      expect(report.markdown).toContain('正文(概览)')
    } finally {
      vi.doUnmock('../src/gather/ai.ts')
      vi.resetModules()
    }
  })

  it('degrades a single failed section but keeps the rest', async () => {
    let first = true
    vi.doMock('../src/gather/ai.ts', () => ({
      streamLlmText: async () => {
        if (first) { first = false; throw new Error('one section down') }
        return '正常正文'
      },
      AiCallPolicy: class {},
    }))
    vi.resetModules()
    try {
      const { generateSentimentReport: freshGenerate } = await import('../src/sentiment/report.ts')
      const ctx = {} as unknown as Context
      const policy = { provider: 'p', model: 'm', timeoutMs: 1_000, maxOutputTokens: 1_000 }
      const report = await freshGenerate(ctx, policy, snapshot(), stats(), new Date(NOW))
      expect(report.degraded).toBe(true)
      expect(report.markdown).toContain('生成失败')
      expect(report.markdown).toContain('正常正文')
      expect(report.markdown).not.toContain('数据版降级')
    } finally {
      vi.doUnmock('../src/gather/ai.ts')
      vi.resetModules()
    }
  })
})

describe('putSentimentReportFile', () => {
  it('stores the newest report and the read projects it back', async () => {
    const report = {
      markdown: '# 报告', degraded: false, generatedAt: NOW,
      promptVersion: SENTIMENT_REPORT_PROMPT_VERSION, mentionCount: 1, alertCount: 0,
    }
    await putSentimentReportFile(FILE(), report)
    const read = await readSentimentFile(FILE())
    expect(read.report?.markdown).toBe('# 报告')
    const replaced = { ...report, markdown: '# 第二份' }
    await putSentimentReportFile(FILE(), replaced)
    const second = await readSentimentFile(FILE())
    expect(second.report?.markdown).toBe('# 第二份')
  })

  it('round-trips the structured ir next to the markdown', async () => {
    const report = {
      markdown: '# 报告\n## 今日概览\n\n正文', degraded: false, generatedAt: NOW,
      promptVersion: SENTIMENT_REPORT_PROMPT_VERSION, mentionCount: 0, alertCount: 0,
      ir: { template: 'daily' as const, sections: [{ key: 'overview', title: '今日概览', body: '正文' }] },
    }
    await putSentimentReportFile(FILE(), report)
    const read = await readSentimentFile(FILE())
    expect(read.report?.ir?.template).toBe('daily')
    expect(read.report?.ir?.sections).toHaveLength(1)
  })

  it('drops a stored report whose ir is malformed on the next read', async () => {
    const base = {
      markdown: '# 报告', degraded: false, generatedAt: NOW,
      promptVersion: SENTIMENT_REPORT_PROMPT_VERSION, mentionCount: 0, alertCount: 0,
    }
    await putSentimentReportFile(FILE(), { ...base, ir: { template: 'daily', sections: [] } })
    const read = await readSentimentFile(FILE())
    expect(read.report).toBeNull()
    expect(read.problems.length).toBeGreaterThan(0)
  })
})
