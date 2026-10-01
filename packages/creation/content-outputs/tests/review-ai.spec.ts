import { describe, expect, it } from 'vitest'
import type { ReviewAnalyzeWorkRequest, ReviewGenerateReportRequest } from '../src/review/types.ts'
import {
  REVIEW_REPORT_SECTIONS, analyzeSystemPrompt, digestBlock, frameAnalyzeRequest,
  frameReportRequest, metricsLine, reportSystemPrompt,
} from '../src/review/ai.ts'

/** One valid metrics record. */
function metrics(overrides: Partial<ReviewAnalyzeWorkRequest['metrics']> = {}): ReviewAnalyzeWorkRequest['metrics'] {
  return {
    impressions: 10_000, reads: 2000, likes: 100, collects: 50,
    comments: 20, shares: 10, followersGained: null, coverCtr: 0.055,
    ...overrides,
  }
}

/** One valid diagnosis request, overridden per test. */
function analyze(overrides: Partial<ReviewAnalyzeWorkRequest> = {}): ReviewAnalyzeWorkRequest {
  return {
    title: '杭州咖啡地图',
    platformId: 'xhs',
    contentType: 'image-text',
    publishedAt: '2026-09-01T00:00:00.000Z',
    period: { from: '2026-09-01', to: '2026-09-15' },
    metrics: metrics(),
    verdict: 'viral',
    draftText: '正文……',
    tags: ['咖啡'],
    personaDigest: null,
    ...overrides,
  }
}

/** One valid report request, overridden per test. */
function report(overrides: Partial<ReviewGenerateReportRequest> = {}): ReviewGenerateReportRequest {
  return {
    name: '九月上旬复盘',
    period: { from: '2026-09-01', to: '2026-09-15' },
    platforms: ['xhs', 'douyin'],
    baselines: { engagementRate: 0.05, collectRate: 0.02, source: 'user', updatedAt: '2026-09-20T00:00:00.000Z' },
    summary: {
      totalWorks: 10, viralCount: 2, weakCount: 3, longtailCount: 1,
      perPlatform: {
        xhs: { works: 6, impressions: 50_000, engagement: 300 },
        douyin: { works: 4, impressions: 80_000, engagement: 500 },
        gzh: { works: 0, impressions: null, engagement: null },
        bilibili: { works: 0, impressions: null, engagement: null },
      },
      totalEngagement: 800,
      avgEngagementRate: 0.08,
      totalFollowersGained: 120,
    },
    topWorks: [{
      title: '爆款一', platformId: 'xhs', contentType: 'image-text', publishedAt: null,
      engagementRate: 0.15, collectRate: 0.08, reads: 12_000, excerpt: '开头摘录',
    }],
    bottomWorks: [{
      title: '垫底一', platformId: 'douyin', contentType: 'video', publishedAt: null,
      engagementRate: 0.01, collectRate: null, reads: 300, excerpt: '',
    }],
    ...overrides,
  }
}

describe('metricsLine', () => {
  it('joins present metrics and skips nulls entirely', () => {
    expect(metricsLine(metrics())).toBe('曝光 10000，阅读/播放 2000，点赞 100，收藏 50，评论 20，转发/分享 10，封面点击率 5.5%')
  })

  it('names the missing-data case instead of faking zeros', () => {
    const empty = {
      ...metrics(), impressions: null, reads: null, likes: null,
      collects: null, comments: null, shares: null, coverCtr: null,
    }
    expect(metricsLine(empty))
      .toBe('（该平台未提供指标数据）')
  })
})

describe('frameAnalyzeRequest', () => {
  it('frames facts, verdict, tags, and the draft', () => {
    const framed = frameAnalyzeRequest(analyze(), 10_000)
    expect(framed).toContain('作品：《杭州咖啡地图》')
    expect(framed).toContain('平台：小红书')
    expect(framed).toContain('初判类别：爆款')
    expect(framed).toContain('标签：咖啡')
    expect(framed).toContain('正文（可能截断）：')
  })

  it('rejects an unknown platform and an empty title', () => {
    expect(() => frameAnalyzeRequest(analyze({ platformId: 'twitter' as never }), 10_000)).toThrow(/platformId/)
    expect(() => frameAnalyzeRequest(analyze({ title: '  ' }), 10_000)).toThrow(/non-empty title/)
  })

  it('truncates to the input cap', () => {
    expect(frameAnalyzeRequest(analyze({ draftText: 'x'.repeat(5000) }), 100).length).toBeLessThanOrEqual(100)
  })
})

describe('analyzeSystemPrompt', () => {
  it('argues reuse for viral and fixes for weak', () => {
    expect(analyzeSystemPrompt(analyze({ verdict: 'viral' }))).toContain('可复用元素')
    expect(analyzeSystemPrompt(analyze({ verdict: 'weak' }))).toContain('改进方向')
  })
})

describe('frameReportRequest', () => {
  it('frames summary, per-platform rows for active platforms only, and digests', () => {
    const framed = frameReportRequest(report(), 10_000)
    expect(framed).toContain('复盘名称：九月上旬复盘')
    expect(framed).toContain('小红书：6 件，曝光 50000，互动 300')
    expect(framed).toContain('抖音：4 件，曝光 80000，互动 500')
    expect(framed).not.toContain('公众号：')
    expect(framed).toContain('1. 《爆款一》')
    expect(framed).toContain('1. 《垫底一》')
    expect(framed).toContain('（用户设置）')
  })

  it('rejects an empty name and an invalid platform', () => {
    expect(() => frameReportRequest(report({ name: '' }), 10_000)).toThrow(/non-empty name/)
    expect(() => frameReportRequest(report({ platforms: ['xhs', 'weibo' as never] }), 10_000)).toThrow(/invalid platform/)
  })
})

describe('reportSystemPrompt', () => {
  it('pins the frozen six sections and the audience placeholder rule', () => {
    const prompt = reportSystemPrompt()
    REVIEW_REPORT_SECTIONS.forEach((section) => {
      expect(prompt).toContain(`## ${section}`)
    })
    expect(prompt).toContain('暂缺')
  })
})

describe('digestBlock', () => {
  it('renders rates, reads, and the empty-excerpt placeholder', () => {
    const block = digestBlock({
      title: '爆款一', platformId: 'xhs', contentType: null, publishedAt: null,
      engagementRate: 0.15, collectRate: null, reads: 12_000, excerpt: '',
    }, 2)
    expect(block).toContain('2. 《爆款一》（小红书，形式未知')
    expect(block).toContain('互动率 15.0%，收藏率 —，阅读/播放 12000')
    expect(block).toContain('正文摘录：（无）')
  })
})
