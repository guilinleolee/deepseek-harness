/**
 * The sentiment source adapters: weibo visitor-search parsing (cards,
 * card groups, long text, engagement, author, refId), the weibo hot-comment
 * read, bilibili wbi signing (the public mixin-key shuffle + MD5), the bili
 * video-search normalization with its bvid refId, and the
 * empty-page-on-failure contract — every adapter degrades to `[]`, never
 * throwing into the scan.
 */
import { describe, expect, it } from 'vitest'
import { fetchBiliComments, fetchBiliVideos, fetchWeiboComments, fetchWeiboSearch, wbiSign } from '../src/sentiment/sources.ts'

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
    expect(entries[0]?.refId).toBe('501')
    expect(entries[1]?.url).toBe('https://m.weibo.cn/detail/502')
  })

  it('returns an empty page on HTTP failure or network throws', async () => {
    expect(await fetchWeiboSearch('x', { fetchImpl: stubFetch([{ match: 'm.weibo.cn', body: {}, status: 500 }]) })).toEqual([])
    const throwing: typeof fetch = async () => { throw new Error('net') }
    expect(await fetchWeiboSearch('x', { fetchImpl: throwing })).toEqual([])
  })
})

describe('fetchWeiboComments', () => {
  it('normalizes the hotflow comment list with heat and author', async () => {
    const fetchImpl = stubFetch([{
      match: 'comments/hotflow',
      body: {
        ok: 1,
        data: {
          data: [
            { text: '<b>售后</b>太差了，推诿', created_at: 'Mon Oct 12 09:00:00 +0800 2026', user: { screen_name: '小张' }, like_count: 7, comment_count: 1 },
            { text: '挺好的呀', user: { screen_name: '阿丽' }, like_count: 2 },
            { text: '' },
          ],
        },
      },
    }])
    const entries = await fetchWeiboComments('501', { fetchImpl })
    expect(entries).toHaveLength(2)
    expect(entries[0]?.title).toContain('售后')
    expect(entries[0]?.title).not.toContain('<')
    expect(entries[0]?.heat).toEqual({ likes: 7, comments: 1, shares: 0 })
    expect(entries[0]?.author).toBe('小张')
    expect(entries[0]?.refId).toBeNull()
  })

  it('returns an empty page on HTTP failure or network throws', async () => {
    expect(await fetchWeiboComments('501', { fetchImpl: stubFetch([{ match: 'hotflow', body: {}, status: 500 }]) })).toEqual([])
    const throwing: typeof fetch = async () => { throw new Error('net') }
    expect(await fetchWeiboComments('501', { fetchImpl: throwing })).toEqual([])
  })
})

describe('fetchBiliComments', () => {
  it('resolves the aid from the bvid and normalizes the comment list', async () => {
    const fetchImpl = stubFetch([
      { match: '/view', body: { data: { aid: 946429884 } } },
      {
        match: '/x/v2/reply',
        body: {
          code: 0,
          data: {
            replies: [
              { content: { message: '好家伙 <b>京中有善口技者</b>' }, ctime: 1760000000, rpid: 1, member: { uname: '小李飞刀' }, like: 12, rcount: 2 },
              { content: { message: '' } },
            ],
          },
        },
      },
    ])
    const entries = await fetchBiliComments('BV1LW4y1T7Yi', { fetchImpl })
    expect(entries).toHaveLength(1)
    expect(entries[0]?.title).toContain('好家伙')
    expect(entries[0]?.title).not.toContain('<')
    expect(entries[0]?.url).toBe('https://www.bilibili.com/video/BV1LW4y1T7Yi')
    expect(entries[0]?.heat).toEqual({ likes: 12, comments: 2, shares: 0 })
    expect(entries[0]?.author).toBe('小李飞刀')
    expect(entries[0]?.publishedAt).not.toBeNull()
  })

  it('returns an empty page when the aid cannot be resolved or the read fails', async () => {
    expect(await fetchBiliComments('BV1', { fetchImpl: stubFetch([{ match: '/view', body: { data: {} } }]) })).toEqual([])
    expect(await fetchBiliComments('BV1', { fetchImpl: stubFetch([{ match: '/view', body: { data: { aid: 1 } } }, { match: '/x/v2/reply', body: {}, status: 500 }]) })).toEqual([])
    const throwing: typeof fetch = async () => { throw new Error('net') }
    expect(await fetchBiliComments('BV1', { fetchImpl: throwing })).toEqual([])
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

describe('fetchBiliVideos', () => {
  it('normalizes the video search through the nav+wbi handshake with the bvid refId', async () => {
    const fetchImpl = stubFetch([
      { match: '/nav', body: { data: { wbi_img: { img_url: 'https://i0.hdslb.com/bfs/wbi/img123.png', sub_url: 'https://i0.hdslb.com/bfs/wbi/sub456.png' } } } },
      {
        match: 'search/type',
        body: {
          data: {
            result: [
              { bvid: 'BV1xx411c7mD', title: '<em class="keyword">卡巴格</em>评测', description: '开箱第一周', author: 'UP主老陈', pubdate: 1760000000, play: 5000, review: 120, favorites: 30 },
              { title: 'no bvid' },
            ],
          },
        },
      },
    ])
    const entries = await fetchBiliVideos('卡巴格', { fetchImpl })
    expect(entries).toHaveLength(1)
    expect(entries[0]?.title).toBe('卡巴格 评测')
    expect(entries[0]?.title).not.toContain('<')
    expect(entries[0]?.url).toBe('https://www.bilibili.com/video/BV1xx411c7mD')
    expect(entries[0]?.refId).toBe('BV1xx411c7mD')
    expect(entries[0]?.heat).toEqual({ likes: 5000, comments: 120, shares: 30 })
    expect(entries[0]?.author).toBe('UP主老陈')
    expect(entries[0]?.publishedAt).not.toBeNull()
  })

  it('returns an empty page when the nav handshake fails', async () => {
    const fetchImpl = stubFetch([{ match: '/nav', body: { data: {} } }])
    expect(await fetchBiliVideos('x', { fetchImpl })).toEqual([])
  })
})
