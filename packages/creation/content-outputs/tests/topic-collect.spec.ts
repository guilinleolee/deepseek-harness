import { describe, expect, it, vi } from 'vitest'
import { collectTopicEntries, TOPIC_COLLECT_RESULT_CAP, type TopicCollectDeps } from '../src/topic-collect.ts'
import type { GatherFeedResult } from '../src/types.ts'

/** One RSS feed result with the given items. */
function feed(items: Array<{ title: string; url: string; summary?: string }>): GatherFeedResult {
  return {
    notModified: false,
    etag: null,
    lastModified: null,
    feedTitle: null,
    items: items.map(item => ({
      id: item.url as never,
      rawGuid: null,
      url: item.url,
      title: item.title,
      publishedAt: '2026-10-30T00:00:00.000Z',
      summary: item.summary ?? null,
      content: null,
    })),
  }
}

/** One weibo/bili source entry in the sentiment vocabulary. */
function socialEntry(overrides: Partial<{ title: string; summary: string; url: string; author: string }> = {}) {
  return {
    title: overrides.title ?? '默认标题',
    summary: overrides.summary ?? '默认摘要',
    url: overrides.url ?? 'https://weibo.example/1',
    publishedAt: null,
    heat: null,
    author: overrides.author ?? null,
    refId: null,
  }
}

/** Deps whose every source returns the given fixtures, with call spies. */
function makeDeps(fixtures: {
  feeds?: GatherFeedResult[]
  weibo?: ReturnType<typeof socialEntry>[]
  bili?: ReturnType<typeof socialEntry>[]
  fetchFeed?: TopicCollectDeps['fetchFeed']
}): TopicCollectDeps & { feedCalls: string[]; weiboCalls: string[]; biliCalls: string[] } {
  const feedCalls: string[] = []
  const weiboCalls: string[] = []
  const biliCalls: string[] = []
  return {
    fetchFeed: fixtures.fetchFeed ?? vi.fn(async (request: { url: string }) => {
      feedCalls.push(request.url)
      return fixtures.feeds?.[feedCalls.length - 1] ?? feed([])
    }),
    fetchWeibo: vi.fn(async (keyword: string) => {
      weiboCalls.push(keyword)
      return fixtures.weibo ?? []
    }),
    fetchBili: vi.fn(async (keyword: string) => {
      biliCalls.push(keyword)
      return fixtures.bili ?? []
    }),
    feedCalls,
    weiboCalls,
    biliCalls,
  }
}

describe('collectTopicEntries', () => {
  it('keeps only entries whose title or summary contains a keyword, across all three sources', async () => {
    const deps = makeDeps({
      feeds: [feed([{ title: 'AI 编程工具横评', url: 'https://blog.example/1' }, { title: '周末爬山记录', url: 'https://blog.example/2' }])],
      weibo: [socialEntry({ title: '无关微博', summary: '今天天气不错', url: 'https://weibo.example/x' }), socialEntry({ title: '日常', summary: '聊聊 Copilot 的使用体验', url: 'https://weibo.example/y' })],
      bili: [socialEntry({ title: '智能体开发入门', url: 'https://bili.example/1' })],
    })
    const { entries } = await collectTopicEntries({ keywords: ['AI 编程', 'Copilot', '智能体'], feedUrls: ['https://feed.example/rss'], existingUrls: [], existingTitles: [] }, deps)
    expect(deps.weiboCalls).toEqual(['AI 编程', 'Copilot', '智能体'])
    expect(deps.feedCalls).toEqual(['https://feed.example/rss'])
    expect(entries.map(entry => entry.title)).toEqual(['AI 编程工具横评', '日常', '智能体开发入门'])
    expect(entries.map(entry => entry.source)).toEqual(['rss', 'weibo', 'bili'])
  })

  it('deduplicates by URL and by normalized title, within the run and against the bank', async () => {
    const deps = makeDeps({
      feeds: [feed([{ title: 'AI 编程', url: 'https://blog.example/1' }, { title: 'AI 编程', url: 'https://blog.example/other-slug' }])],
      weibo: [socialEntry({ title: 'AI 编程', url: 'https://weibo.example/z' })],
    })
    const { entries } = await collectTopicEntries(
      { keywords: ['AI 编程'], feedUrls: ['https://feed.example/rss'], existingUrls: ['https://BLOG.example/1'], existingTitles: [] },
      deps,
    )
    expect(entries).toEqual([])
  })

  it('keeps a title-only duplicate out even when the URLs differ, and lets a second keyword hit survive', async () => {
    const deps = makeDeps({
      weibo: [socialEntry({ title: 'AI 编程工具', url: 'https://weibo.example/a' })],
      bili: [socialEntry({ title: '另一篇', summary: 'AI 编程实践', url: 'https://bili.example/b' })],
    })
    const { entries } = await collectTopicEntries(
      { keywords: ['AI 编程'], feedUrls: [], existingUrls: [], existingTitles: ['ai 编程工具'] },
      deps,
    )
    expect(entries.map(entry => entry.url)).toEqual(['https://bili.example/b'])
  })

  it('skips not-modified feeds and degrades a failed feed to no entries', async () => {
    const deps = makeDeps({
      feeds: [],
      weibo: [socialEntry({ title: 'AI 编程动态' })],
      fetchFeed: async (request: { url: string }) => {
        if (request.url.includes('broken')) throw new Error('offline')
        return { notModified: true, etag: null, lastModified: null, feedTitle: null, items: [] }
      },
    })
    const { entries } = await collectTopicEntries(
      { keywords: ['AI 编程'], feedUrls: ['https://broken.example/rss', 'https://stale.example/rss'], existingUrls: [], existingTitles: [] },
      deps,
    )
    expect(entries.map(entry => entry.title)).toEqual(['AI 编程动态'])
  })

  it('caps the result and the keyword and feed reads', async () => {
    const many = Array.from({ length: 30 }, (_, index) => socialEntry({ title: `AI 编程 ${String(index)}`, url: `https://weibo.example/${String(index)}` }))
    const deps = makeDeps({ weibo: many })
    const { entries } = await collectTopicEntries(
      { keywords: ['AI 编程', ...Array.from({ length: 11 }, (_, index) => `词${String(index)}`)], feedUrls: Array.from({ length: 8 }, (_, index) => `https://f${String(index)}.example/rss`), existingUrls: [], existingTitles: [] },
      deps,
    )
    expect(entries).toHaveLength(TOPIC_COLLECT_RESULT_CAP)
    expect(deps.weiboCalls).toHaveLength(10)
    expect(deps.feedCalls).toHaveLength(5)
  })
})
