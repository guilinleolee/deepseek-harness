/**
 * The sentiment source adapters: weibo visitor-search parsing (cards,
 * card groups, long text, engagement, author), bilibili wbi signing (the
 * public mixin-key shuffle + MD5), the bili hot-search normalization, and
 * the empty-page-on-failure contract — every adapter degrades to `[]`,
 * never throwing into the scan.
 */
import { describe, expect, it } from 'vitest'
import { fetchBiliHot, fetchWeiboSearch, wbiSign } from '../src/sentiment/sources.ts'

/** A stub fetch that answers one canned body per URL fragment. */
function stubFetch(routes: ReadonlyArray<{ match: string; body: unknown; status?: number }>): typeof fetch {
  return async (input: RequestInfo | URL) => {
    const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url
    for (const route of routes) {
      if (url.includes(route.match)) {
        return new Response(JSON.stringify(route.body), { status: route.status ?? 200 })
      }
    }
    return new Response('{}', { status: 404 })
  }
}

describe('fetchWeiboSearch', () => {
  it('normalizes cards and card groups into entries with heat and author', async () => {
    const fetchImpl = stubFetch([{
      match: 'm.weibo.cn',
      body: {
        data: {
          cards: [
            {
              mblog: {
                id: '501',
                text: '<span class="surl-text">卡巴格</span> 物流太慢，已<b>投诉</b>',
                created_at: 'Mon Oct 12 08:00:00 +0800 2026',
                user: { screen_name: '老王' },
                attitudes_count: 12, comments_count: 3, reposts_count: 1,
              },
            },
            {
              card_group: [{ mblog: { id: 502, text: '卡巴格好评', user: { screen_name: '小李' }, attitudes_count: 5 } }],
            },
            { mblog: { text: '' } },
          ],
        },
      },
    }])
    const entries = await fetchWeiboSearch('卡巴格', { fetchImpl })
    expect(entries).toHaveLength(2)
    expect(entries[0]?.title).toContain('卡巴格')
    expect(entries[0]?.title).toContain('投诉')
    expect(entries[0]?.title).not.toContain('<')
    expect(entries[0]?.url).toBe('https://m.weibo.cn/detail/501')
    expect(entries[0]?.heat).toEqual({ likes: 12, comments: 3, shares: 1 })
    expect(entries[0]?.author).toBe('老王')
    expect(entries[1]?.url).toBe('https://m.weibo.cn/detail/502')
  })

  it('returns an empty page on HTTP failure or network throws', async () => {
    expect(await fetchWeiboSearch('x', { fetchImpl: stubFetch([{ match: 'm.weibo.cn', body: {}, status: 500 }]) })).toEqual([])
    const throwing: typeof fetch = async () => { throw new Error('net') }
    expect(await fetchWeiboSearch('x', { fetchImpl: throwing })).toEqual([])
  })
})

describe('wbiSign', () => {
  it('signs sorted params with the shuffled mixin key and is stable', () => {
    const rid = wbiSign({ keyword: 'wbi', page_size: '20' }, '7cd0849413384841', '4e4b2a8b2d2b4d7f')
    expect(rid).toMatch(/^[0-9a-f]{32}$/u)
    expect(wbiSign({ page_size: '20', keyword: 'wbi' }, '7cd0849413384841', '4e4b2a8b2d2b4d7f')).toBe(rid)
    expect(wbiSign({ keyword: 'wbi', page_size: '20' }, '0000000000000000', '4e4b2a8b2d2b4d7f')).not.toBe(rid)
  })
})

describe('fetchBiliHot', () => {
  it('normalizes the hot list through the nav+wbi handshake', async () => {
    const fetchImpl = stubFetch([
      { match: '/nav', body: { data: { wbi_img: { img_url: 'https://i0.hdslb.com/bfs/wbi/img123.png', sub_url: 'https://i0.hdslb.com/bfs/wbi/sub456.png' } } } },
      { match: 'search/square', body: { data: { list: [{ keyword: '卡巴格', show_name: '卡巴格上新' }] } } },
    ])
    const entries = await fetchBiliHot('卡巴格', { fetchImpl })
    expect(entries).toHaveLength(1)
    expect(entries[0]?.title).toBe('卡巴格上新')
    expect(entries[0]?.url).toContain('search.bilibili.com/all?keyword=')
  })

  it('returns an empty page when the nav handshake fails', async () => {
    const fetchImpl = stubFetch([{ match: '/nav', body: { data: {} } }])
    expect(await fetchBiliHot('x', { fetchImpl })).toEqual([])
  })
})
