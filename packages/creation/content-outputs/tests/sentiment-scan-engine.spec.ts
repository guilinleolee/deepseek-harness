/**
 * The scan engine's platform-search integration: the expanded search terms
 * drive the weibo/bili fetches, matched entries capture their refIds for the
 * comment drill-down (hottest first, capped), comment entries ride the same
 * keyword filter and URL dedupe, and a failed expansion degrades to the raw
 * subjects without failing the scan.
 */
import { describe, expect, it } from 'vitest'
import type { Context } from '@deepseek-ai/cordis'
import type { SentimentSettings, SentimentTask, SentimentTaskInput } from '../src/sentiment/types.ts'
import type { ScanDeps } from '../src/sentiment/scan.ts'
import { runSentimentScan } from '../src/sentiment/scan.ts'
import { DEFAULT_SENTIMENT_SETTINGS } from '../src/sentiment/store.ts'
import type { SourceEntry } from '../src/sentiment/sources.ts'

const CTX = {} as Context
const AI = { provider: 'test', model: 'test', timeoutMs: 1_000, maxOutputTokens: 100 }
const NOW = () => new Date('2026-10-22T08:00:00.000Z')

function task(overrides: Partial<SentimentTaskInput> = {}): SentimentTask {
  return {
    id: 't-1' as SentimentTask['id'],
    name: '品牌口碑监测',
    group: 'brand',
    enabled: true,
    subjects: ['卡巴格'],
    keywordGroups: [{ polarity: 'neg', terms: ['投诉'] }],
    sources: ['rss', 'weibo', 'bili'],
    feedUrls: [],
    intervalMinutes: 60,
    createdAt: '2026-10-22T00:00:00.000Z',
    updatedAt: '2026-10-22T00:00:00.000Z',
    ...overrides,
  } as SentimentTask
}

const SETTINGS: SentimentSettings = DEFAULT_SENTIMENT_SETTINGS

function entry(url: string, text: string, refId: string | null = null, comments = 0): SourceEntry {
  return { title: text, summary: text, url, publishedAt: null, heat: { likes: 0, comments, shares: 0 }, author: null, refId }
}

describe('runSentimentScan platform search', () => {
  it('searches the expanded terms and drills comments behind the hottest matches', async () => {
    const searchedWeibo: string[] = []
    const searchedBili: string[] = []
    const drilledWeibo: string[] = []
    const drilledBili: string[] = []
    const deps: ScanDeps = {
      now: NOW,
      expandTerms: async (_ctx, _policy, subject) => {
        expect(subject.subjects).toEqual(['卡巴格'])
        return ['卡巴格', '扫地机克星', 'kabage']
      },
      fetchWeibo: async (term) => {
        searchedWeibo.push(term)
        if (term === '卡巴格') {
          return [
            entry('https://m.weibo.cn/detail/1', '卡巴格被投诉了', '1', 10),
            entry('https://m.weibo.cn/detail/2', '卡巴格被投诉了', '2', 90),
            entry('https://m.weibo.cn/detail/3', '无关内容'),
          ]
        }
        return []
      },
      fetchWeiboComments: async (id) => {
        drilledWeibo.push(id)
        return id === '2' ? [entry(`https://m.weibo.cn/detail/2#c1`, '这投诉太真实了', null)] : []
      },
      fetchBiliVideos: async (term) => {
        searchedBili.push(term)
        return term === '卡巴格' ? [entry('https://www.bilibili.com/video/BV1', '卡巴格投诉合集', 'BV1', 50)] : []
      },
      fetchBiliComments: async (bvid) => {
        drilledBili.push(bvid)
        return [entry('https://www.bilibili.com/video/BV1#c1', '我也投诉过', null)]
      },
    }
    const batch = await runSentimentScan(CTX, [task()], SETTINGS, AI, deps)
    expect(searchedWeibo).toEqual(['卡巴格', '扫地机克星', 'kabage'])
    expect(searchedBili).toEqual(['卡巴格', '扫地机克星', 'kabage'])
    // The two hottest matched weibo entries are drilled (cap 2).
    expect(drilledWeibo).toEqual(['2', '1'])
    expect(drilledBili).toEqual(['BV1'])
    const texts = batch.mentions.map(mention => mention.summary)
    expect(texts).toContain('卡巴格被投诉了')
    expect(texts).toContain('这投诉太真实了')
    expect(texts).toContain('我也投诉过')
    // Comment rows keep their drill-down platform label.
    expect(batch.mentions.filter(mention => mention.platform === '微博评论')).toHaveLength(1)
    expect(batch.mentions.filter(mention => mention.platform === 'B站评论')).toHaveLength(1)
    expect(batch.mentions.every(mention => mention.summary !== '无关内容')).toBe(true)
  })

  it('deduplicates entries re-found across expanded terms', async () => {
    const deps: ScanDeps = {
      now: NOW,
      expandTerms: async () => ['卡巴格', '扫地机克星', 'kabage'],
      fetchWeibo: async () => [entry('https://m.weibo.cn/detail/1', '卡巴格被投诉了', '1', 1)],
      fetchWeiboComments: async () => [],
      fetchBiliVideos: async () => [],
      fetchBiliComments: async () => [],
    }
    const batch = await runSentimentScan(CTX, [task()], SETTINGS, AI, deps)
    expect(batch.mentions).toHaveLength(1)
  })

  it('degrades to the raw subjects when the expansion fails, and still drills comments', async () => {
    const searched: string[] = []
    const deps: ScanDeps = {
      now: NOW,
      expandTerms: async () => { throw new Error('llm down') },
      fetchWeibo: async (term) => {
        searched.push(term)
        return term === '卡巴格' ? [entry('https://m.weibo.cn/detail/9', '卡巴格遭投诉', '9', 5)] : []
      },
      fetchWeiboComments: async (id) => [entry(`https://m.weibo.cn/detail/9#c${id}`, '投诉+1', null)],
      fetchBiliVideos: async () => [],
      fetchBiliComments: async () => [],
    }
    const batch = await runSentimentScan(CTX, [task()], SETTINGS, AI, deps)
    expect(searched).toEqual(['卡巴格'])
    expect(batch.mentions.map(mention => mention.summary)).toContain('投诉+1')
    expect(batch.result.captured).toBe(2)
  })
})

describe('runSentimentScan depth round', () => {
  it('searches the next term tier and drills deeper comments when the task aggregates a high-level alert', async () => {
    const searched: string[] = []
    const drilled: string[] = []
    // Six negative mentions at 100 heat each cross the level-2 threshold (500).
    const subjects = Array.from({ length: 6 }, (_, i) => `https://m.weibo.cn/detail/${String(i + 1)}`)
    let weiboPage = 0
    const deps: ScanDeps = {
      now: NOW,
      expandTerms: async () => ['卡巴格', '词2', '词3', '词4', '词5', '词6'],
      fetchWeibo: async (term) => {
        searched.push(term)
        weiboPage += 1
        // Each breadth term yields two matched entries (refIds r1..r6); the
        // depth terms hit the same URLs (deduped) but the comment round still
        // drills the next un-drilled refs.
        return subjects.slice((weiboPage - 1) * 2, weiboPage * 2).map((url, i) =>
          entry(url, `卡巴格被投诉 ${url}`, `r${String((weiboPage - 1) * 2 + i + 1)}`, 100))
      },
      fetchWeiboComments: async (id) => {
        drilled.push(id)
        return []
      },
      fetchBiliVideos: async () => [],
      fetchBiliComments: async () => [],
    }
    const batch = await runSentimentScan(CTX, [task()], SETTINGS, AI, deps)
    // Breadth searched terms 1-3; the depth round added terms 4-6.
    expect(searched).toEqual(['卡巴格', '词2', '词3', '词4', '词5', '词6'])
    // Breadth drilled the two hottest; the depth round drilled two more.
    expect(drilled).toHaveLength(4)
    expect(batch.mentions.length).toBeGreaterThanOrEqual(6)
  })

  it('skips the LLM refinement stage under the rules analyzer', async () => {
    let refineCalls = 0
    const deps: ScanDeps = {
      now: NOW,
      expandTerms: async () => ['卡巴格'],
      refineBatch: async () => {
        refineCalls += 1
        return new Map()
      },
      fetchWeibo: async () => [entry('https://m.weibo.cn/detail/9', '卡巴格新品上市', '9')],
    }
    const batch = await runSentimentScan(
      CTX, [task({ keywordGroups: [{ polarity: 'any', terms: ['新品'] }], sources: ['weibo'] })], SETTINGS,
      { ...AI, analyzer: 'rules' }, deps,
    )
    expect(refineCalls).toBe(0)
    expect(batch.result.refinement).toBe('skipped')
    expect(batch.mentions[0]?.polarity).toBe('neu')
  })

  it('degrades to the lexicon verdicts when the LLM refinement fails', async () => {
    const deps: ScanDeps = {
      now: NOW,
      expandTerms: async () => ['卡巴格'],
      refineBatch: async () => { throw new Error('llm down') },
      fetchWeibo: async () => [entry('https://m.weibo.cn/detail/9', '卡巴格新品上市', '9')],
    }
    const batch = await runSentimentScan(
      CTX, [task({ keywordGroups: [{ polarity: 'any', terms: ['新品'] }], sources: ['weibo'] })], SETTINGS, AI, deps,
    )
    expect(batch.result.refinement).toBe('degraded')
    expect(batch.mentions[0]?.polarity).toBe('neu')
  })

  it('skips the depth round when the negative heat stays low', async () => {
    const searched: string[] = []
    const deps: ScanDeps = {
      now: NOW,
      expandTerms: async () => ['卡巴格', '词2', '词3', '词4', '词5', '词6'],
      fetchWeibo: async (term) => {
        searched.push(term)
        return term === '卡巴格' ? [entry('https://m.weibo.cn/detail/1', '卡巴格被投诉', '1', 1)] : []
      },
      fetchWeiboComments: async () => [],
      fetchBiliVideos: async () => [],
      fetchBiliComments: async () => [],
    }
    await runSentimentScan(CTX, [task()], SETTINGS, AI, deps)
    expect(searched).toEqual(['卡巴格', '词2', '词3'])
  })
})
