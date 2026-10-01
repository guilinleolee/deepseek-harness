import { describe, expect, it } from 'vitest'
import type { MetricSnapshot, ReviewBaselines } from '@deepseek-ai/dsh-content-outputs/types'
import {
  aggregateSummary, collectRateOf, dataOnlyReport, DEFAULT_BASELINES as DEFAULT_BASELINES_CLIENT,
  engagementRateOf, isLongtail, poolSnapshots, rankWorks, REVIEW_PLATFORMS,
  REVIEW_REPORT_SECTIONS, REVIEW_WORK_FILTERS, selectDigests, verdictOf,
} from '../src/client/review/model.ts'
import {
  DEFAULT_BASELINES as GATEWAY_BASELINES, REVIEW_PLATFORMS as GATEWAY_PLATFORMS,
  REVIEW_WORK_FILTERS as GATEWAY_WORK_FILTERS,
} from '@deepseek-ai/dsh-content-outputs/types'

const BASELINES: ReviewBaselines = {
  engagementRate: 0.05, collectRate: 0.02, source: 'user', updatedAt: '2026-09-20T00:00:00.000Z',
}

describe('client/gateway enum parity', () => {
  it('carries the client constants byte-identical to the gateway lists', () => {
    expect([...REVIEW_PLATFORMS]).toEqual([...GATEWAY_PLATFORMS])
    expect([...REVIEW_WORK_FILTERS]).toEqual([...GATEWAY_WORK_FILTERS])
    expect(DEFAULT_BASELINES_CLIENT).toEqual(GATEWAY_BASELINES)
  })
})

/** One valid metrics record; the defaults sit in the neutral band (0.07 vs a 0.05 baseline). */
function metrics(overrides: Partial<MetricSnapshot['metrics']> = {}): MetricSnapshot['metrics'] {
  return {
    impressions: 1000, reads: 500, likes: 20, collects: 5,
    comments: 5, shares: 5, followersGained: null, coverCtr: null,
    ...overrides,
  }
}

/** One valid snapshot, overridden per test. */
function snapshot(overrides: Partial<MetricSnapshot> = {}): MetricSnapshot {
  return {
    snapshotId: crypto.randomUUID(),
    platformId: 'xhs',
    platformWorkId: 'work-1',
    title: '第一篇',
    publishedAt: '2026-08-01T00:00:00.000Z',
    capturedAt: '2026-09-20T00:00:00.000Z',
    contentId: 'content-1',
    matchMethod: 'title',
    contentType: 'image-text',
    metrics: metrics(),
    ...overrides,
  }
}

describe('engagementRateOf / collectRateOf', () => {
  it('divide by reads and read null when reads are missing or zero', () => {
    expect(engagementRateOf(metrics())).toBe(0.07)
    expect(collectRateOf(metrics())).toBe(0.01)
    expect(engagementRateOf(metrics({ reads: null }))).toBeNull()
    expect(engagementRateOf(metrics({ reads: 0 }))).toBeNull()
    expect(collectRateOf(metrics({ reads: 0 }))).toBeNull()
  })
})

describe('verdictOf', () => {
  it('judges viral at twice and weak below half of the baseline', () => {
    expect(verdictOf(metrics({ likes: 200 }), BASELINES)).toBe('viral')
    expect(verdictOf(metrics({ likes: 1, collects: 1, comments: 0, shares: 0 }), BASELINES)).toBe('weak')
    expect(verdictOf(metrics(), BASELINES)).toBe('neutral')
    expect(verdictOf(metrics({ reads: null }), BASELINES)).toBe('neutral')
  })
})

describe('isLongtail', () => {
  const now = new Date('2026-09-27T00:00:00.000Z')

  it('rejects works with fewer than two snapshots or a young publish age', () => {
    expect(isLongtail([snapshot()], now)).toBe(false)
    expect(isLongtail([
      snapshot({ publishedAt: '2026-09-20T00:00:00.000Z' }),
      snapshot({ snapshotId: crypto.randomUUID(), capturedAt: '2026-09-26T00:00:00.000Z' }),
    ], now)).toBe(false)
  })

  it('accepts a still-growing old work whose recent pace holds a fifth of lifetime', () => {
    const longtail = isLongtail([
      snapshot({ capturedAt: '2026-09-01T00:00:00.000Z', metrics: metrics({ likes: 100, collects: 0, comments: 0, shares: 0 }) }),
      snapshot({ snapshotId: crypto.randomUUID(), capturedAt: '2026-09-27T00:00:00.000Z', metrics: metrics({ likes: 260, collects: 0, comments: 0, shares: 0 }) }),
    ], now)
    // Lifetime pace: 160 interactions / 26 days ≈ 6.15/day; last 7 days:
    // 160 / 7 ≈ 22.9/day — far above a fifth of the pace.
    expect(longtail).toBe(true)
  })

  it('rejects works whose growth has stopped', () => {
    expect(isLongtail([
      snapshot({ capturedAt: '2026-09-01T00:00:00.000Z', metrics: metrics({ likes: 100 }) }),
      snapshot({ snapshotId: crypto.randomUUID(), capturedAt: '2026-09-27T00:00:00.000Z', metrics: metrics({ likes: 100 }) }),
    ], now)).toBe(false)
  })
})

describe('poolSnapshots', () => {
  it('admits only bound snapshots inside the period', () => {
    const pooled = poolSnapshots({
      snapshots: [
        snapshot(),
        snapshot({ snapshotId: crypto.randomUUID(), contentId: null }),
        snapshot({ snapshotId: crypto.randomUUID(), capturedAt: '2026-08-01T00:00:00.000Z' }),
      ],
    }, { platforms: [], contentTypes: [], workFilter: 'all' }, { from: '2026-09-15', to: '2026-09-27' }, BASELINES)
    expect(pooled).toHaveLength(1)
  })

  it('filters by platform, form, and the verdict slice', () => {
    const snapshots = [
      snapshot({ metrics: metrics({ likes: 200 }) }),
      snapshot({ snapshotId: crypto.randomUUID(), platformId: 'douyin' as const }),
      snapshot({ snapshotId: crypto.randomUUID(), contentType: 'video' as const }),
    ]
    const byPlatform = poolSnapshots({ snapshots }, { platforms: ['douyin'], contentTypes: [], workFilter: 'all' }, { from: '2026-09-01', to: '2026-09-27' }, BASELINES)
    expect(byPlatform).toHaveLength(1)
    const viralOnly = poolSnapshots({ snapshots }, { platforms: [], contentTypes: [], workFilter: 'viral' }, { from: '2026-09-01', to: '2026-09-27' }, BASELINES)
    expect(viralOnly).toHaveLength(1)
  })
})

describe('aggregateSummary', () => {
  it('sums impressions per platform only and counts verdicts', () => {
    const now = new Date('2026-09-27T00:00:00.000Z')
    const summary = aggregateSummary([
      snapshot({ metrics: metrics({ impressions: 100, likes: 200 }) }),
      snapshot({ snapshotId: crypto.randomUUID(), platformWorkId: 'w2', platformId: 'douyin', metrics: metrics({ impressions: 900 }) }),
      snapshot({ snapshotId: crypto.randomUUID(), platformWorkId: 'w1' }),
    ], BASELINES, now)
    expect(summary.totalWorks).toBe(3)
    expect(summary.viralCount).toBe(1)
    expect(summary.perPlatform.xhs.impressions).toBe(1100)
    expect(summary.perPlatform.douyin.impressions).toBe(900)
    expect(summary.perPlatform.gzh.works).toBe(0)
  })
})

describe('rankWorks / selectDigests', () => {
  it('ranks by engagement rate and keeps the latest snapshot per work', () => {
    const ranked = rankWorks([
      snapshot({ metrics: metrics({ likes: 200 }) }),
      snapshot({ snapshotId: crypto.randomUUID(), platformWorkId: 'w2', metrics: metrics({ likes: 10, collects: 0, comments: 0, shares: 0 }) }),
      // Same work as the first: the newer snapshot replaces it in the rank.
      snapshot({ snapshotId: crypto.randomUUID(), platformWorkId: 'work-1', capturedAt: '2026-09-21T00:00:00.000Z', metrics: metrics({ likes: 999 }) }),
    ])
    expect(ranked[0]?.platformWorkId).toBe('work-1')
    expect(ranked).toHaveLength(2)
  })

  it('selects top/bottom digests with 500-char excerpts', () => {
    const ranked = rankWorks([
      snapshot({ metrics: metrics() }),
      snapshot({ snapshotId: crypto.randomUUID(), platformWorkId: 'w2', title: '第二篇', metrics: metrics({ likes: 1, collects: 0, comments: 0, shares: 0 }) }),
    ])
    const { top, bottom, sampled } = selectDigests(ranked, { 'xhs:work-1': 'x'.repeat(600) })
    expect(top).toHaveLength(2)
    expect(bottom).toHaveLength(2)
    expect(top[0]?.title).toBe('第一篇')
    expect(top[0]?.excerpt).toHaveLength(500)
    expect(bottom.map(digest => digest.title)).toContain('第二篇')
    expect(sampled).toBe(false)
  })
})

describe('dataOnlyReport', () => {
  it('carries the frozen six sections and the interaction placeholder', () => {
    const now = new Date('2026-09-27T00:00:00.000Z')
    const summary = aggregateSummary([snapshot()], BASELINES, now)
    const report = dataOnlyReport('九月复盘', { from: '2026-09-01', to: '2026-09-27' }, summary, rankWorks([snapshot()]), BASELINES)
    REVIEW_REPORT_SECTIONS.forEach((section) => {
      expect(report).toContain(`## ${section}`)
    })
    expect(report).toContain('AI 增强部分生成失败')
    expect(report).toContain('【互动】栏目未上线')
  })
})
