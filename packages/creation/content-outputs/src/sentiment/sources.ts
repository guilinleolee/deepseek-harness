/**
 * Source adapters beyond RSS: one shared entry-draft vocabulary and three
 * implementations. The weibo adapter reads the PUBLIC mobile-container
 * search API (m.weibo.cn, no login, visitor cookies only — the 2026-10-07
 * research's compliant visitor-page path); the bili adapter reads bilibili's
 * public web-hot-search and video-comment endpoints with the wbi signature
 * every web client carries. Both are low-frequency, keyword-scoped reads
 * that degrade to an empty page on any failure — never a scraper shell,
 * never signature reversal of protected endpoints.
 */

import { createHash, createHmac } from 'node:crypto'

/** Deadline of one source request; a slow endpoint must not pin the scan. */
export const SENTIMENT_SOURCE_TIMEOUT_MS = 15_000

/** Entries kept per source request. */
export const SENTIMENT_SOURCE_PAGE_CAP = 20

/** The user agent a plain mobile/web visitor carries. */
const MOBILE_UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
const DESKTOP_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'

/** One normalized candidate row before keyword filtering; the scan owns classification. */
export interface SourceEntry {
  readonly title: string
  readonly summary: string
  readonly url: string
  readonly publishedAt: string | null
  /** Engagement counts when the endpoint exposes them; feeds the alert heat. */
  readonly heat: { likes: number; comments: number; shares: number } | null
  readonly author: string | null
}

/** Injection face for tests: the fetch implementation defaults to the global one. */
export interface SourceDeps {
  readonly fetchImpl?: typeof fetch
}

/** The m.weibo.cn container API: one page of keyword search results. */
const WEIBO_SEARCH_URL = 'https://m.weibo.cn/api/container/getIndex'

/**
 * Fetch one page of public weibo search results for the keyword.
 * @param keyword - the search term (one task subject or keyword-group term).
 * @param deps - injected fetch for tests.
 * @returns normalized entries; empty on any failure (the scan continues).
 */
export async function fetchWeiboSearch(keyword: string, deps: SourceDeps = {}): Promise<readonly SourceEntry[]> {
  try {
    const response = await (deps.fetchImpl ?? fetch)(`${WEIBO_SEARCH_URL}?containerid=100103type%3D1%26q%3D${encodeURIComponent(keyword)}&page_type=searchall`, {
      headers: { 'user-agent': MOBILE_UA, 'accept': 'application/json' },
      signal: AbortSignal.timeout(SENTIMENT_SOURCE_TIMEOUT_MS),
    })
    if (!response.ok) return []
    const body = await response.json() as {
      data?: {
        cards?: ReadonlyArray<{
          mblog?: {
            text?: string
            created_at?: string
            id?: string | number
            user?: { screen_name?: string }
            attitudes_count?: number
            comments_count?: number
            reposts_count?: number
            page_info?: { page_url?: string }
          }
          card_group?: ReadonlyArray<{ mblog?: Record<string, unknown> }>
        }>
      }
    }
    const cards = body.data?.cards ?? []
    const entries: SourceEntry[] = []
    const push = (mblog: Record<string, unknown>): void => {
      const text = typeof mblog.text === 'string' ? mblog.text : ''
      if (text.length === 0) return
      const longText = mblog.longText as { longTextContent?: unknown } | undefined
      const long = typeof longText?.longTextContent === 'string'
        ? `${text}\n${longText.longTextContent}`
        : text
      const id = mblog.id
      const idText = typeof id === 'string' || typeof id === 'number' ? String(id) : ''
      const user = mblog.user as { screen_name?: unknown } | undefined
      const screenName = typeof user?.screen_name === 'string' ? user.screen_name : ''
      entries.push({
        title: plainText(long).slice(0, 200),
        summary: plainText(long).slice(0, 500),
        url: idText.length === 0 ? WEIBO_SEARCH_URL : `https://m.weibo.cn/detail/${idText}`,
        publishedAt: typeof mblog.created_at === 'string' ? mblog.created_at : null,
        heat: {
          likes: typeof mblog.attitudes_count === 'number' ? mblog.attitudes_count : 0,
          comments: typeof mblog.comments_count === 'number' ? mblog.comments_count : 0,
          shares: typeof mblog.reposts_count === 'number' ? mblog.reposts_count : 0,
        },
        author: screenName.length > 0 ? screenName : null,
      })
      if (entries.length >= SENTIMENT_SOURCE_PAGE_CAP) return
    }
    for (const card of cards) {
      if (card.mblog !== undefined) push(card.mblog)
      for (const grouped of card.card_group ?? []) {
        if (grouped.mblog !== undefined) push(grouped.mblog)
      }
      if (entries.length >= SENTIMENT_SOURCE_PAGE_CAP) break
    }
    return entries
  } catch {
    // A failed source read is an empty page, not a failed scan.
    return []
  }
}

/** The bilibili web-hot-search endpoint (public, wbi-signed like the web client). */
const BILI_HOT_URL = 'https://api.bilibili.com/x/web-interface/wbi/search/square'
/** The bilibili comment endpoint (public, wbi-signed). */
const BILI_COMMENT_URL = 'https://api.bilibili.com/x/v2/reply/wbi/main'

/** The wbi signing key table, rotated by bilibili; the shuffle below encodes the 2023-10 order. */
const WBI_KEY_ORDER: readonly number[] = [
  46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49,
  33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13, 37, 48, 7, 16, 24, 55, 40, 61,
  26, 17, 0, 1, 60, 51, 30, 4, 22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11, 36, 20, 34, 44, 52,
]

/**
 * Compute one wbi signature (mixin key shuffle + MD5 of sorted params), the
 * public algorithm every bilibili web client runs. Reverse-engineering-free
 * by stance: the algorithm is publicly documented by the community and
 * carries no auth bypass.
 * @param params - the request's query params (values already encoded).
 * @param imgKey - the img_key from nav.
 * @param subKey - the sub_key from nav.
 * @returns the `w_rid` signature value.
 */
export function wbiSign(params: Readonly<Record<string, string>>, imgKey: string, subKey: string): string {
  const mixin = `${imgKey}${subKey}`.slice(0, 32)
  const mixed: string[] = []
  for (const position of WBI_KEY_ORDER) mixed.push(mixin[position] ?? '')
  const mixinKey = mixed.join('')
  const sorted = [...Object.entries(params)].sort(([left], [right]) => left < right ? -1 : 1)
  const query = sorted.map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`).join('&')
  return createHash('md5').update(`${query}${mixinKey}`).digest('hex')
}

/** Current wbi keys, fetched from the public nav endpoint. */
async function wbiKeys(deps: SourceDeps): Promise<{ imgKey: string; subKey: string } | null> {
  try {
    const response = await (deps.fetchImpl ?? fetch)('https://api.bilibili.com/x/web-interface/nav', {
      headers: { 'user-agent': DESKTOP_UA, 'accept': 'application/json' },
      signal: AbortSignal.timeout(SENTIMENT_SOURCE_TIMEOUT_MS),
    })
    if (!response.ok) return null
    const body = await response.json() as {
      data?: { wbi_img?: { img_url?: string; sub_url?: string } }
    }
    const img = body.data?.wbi_img?.img_url
    const sub = body.data?.wbi_img?.sub_url
    if (img === undefined || sub === undefined) return null
    const base = (url: string): string => url.slice(url.lastIndexOf('/') + 1, url.lastIndexOf('.'))
    return { imgKey: base(img), subKey: base(sub) }
  } catch {
    return null
  }
}

/**
 * Fetch one page of bilibili web-hot-search entries matching the keyword
 * (trending-list search by keyword; no login, no SESSDATA).
 * @param keyword - the search term.
 * @param deps - injected fetch for tests.
 * @returns normalized entries; empty on any failure.
 */
export async function fetchBiliHot(keyword: string, deps: SourceDeps = {}): Promise<readonly SourceEntry[]> {
  const keys = await wbiKeys(deps)
  if (keys === null) return []
  try {
    const params: Record<string, string> = { keyword, page_size: String(SENTIMENT_SOURCE_PAGE_CAP) }
    const wRid = wbiSign(params, keys.imgKey, keys.subKey)
    const query = [...Object.entries(params)].map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`).join('&')
    const response = await (deps.fetchImpl ?? fetch)(`${BILI_HOT_URL}?${query}&w_rid=${wRid}`, {
      headers: { 'user-agent': DESKTOP_UA, 'accept': 'application/json' },
      signal: AbortSignal.timeout(SENTIMENT_SOURCE_TIMEOUT_MS),
    })
    if (!response.ok) return []
    const body = await response.json() as {
      data?: { list?: ReadonlyArray<{ keyword?: string; show_name?: string; icon?: string }> }
    }
    const list = body.data?.list ?? []
    return list
      .filter((item): item is { keyword: string; show_name?: string; icon?: string } => typeof item.keyword === 'string')
      .map(item => ({
        title: item.show_name ?? item.keyword,
        summary: item.show_name ?? item.keyword,
        url: `https://search.bilibili.com/all?keyword=${encodeURIComponent(item.keyword)}`,
        publishedAt: null,
        heat: null,
        author: null,
      }))
  } catch {
    return []
  }
}

/**
 * Fetch one page of top comments of one bilibili video (BV id).
 * @param bvid - the video's BV id.
 * @param deps - injected fetch for tests.
 * @returns normalized entries; empty on any failure.
 */
export async function fetchBiliComments(bvid: string, deps: SourceDeps = {}): Promise<readonly SourceEntry[]> {
  const keys = await wbiKeys(deps)
  if (keys === null) return []
  try {
    const params: Record<string, string> = { oid: bvid, type: '1', mode: '3', pagination_str: '{"offset":""}' }
    const wRid = wbiSign(params, keys.imgKey, keys.subKey)
    const query = [...Object.entries(params)].map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`).join('&')
    const response = await (deps.fetchImpl ?? fetch)(`${BILI_COMMENT_URL}?${query}&w_rid=${wRid}`, {
      headers: { 'user-agent': DESKTOP_UA, 'accept': 'application/json' },
      signal: AbortSignal.timeout(SENTIMENT_SOURCE_TIMEOUT_MS),
    })
    if (!response.ok) return []
    const body = await response.json() as {
      data?: { replies?: ReadonlyArray<{
        content?: { message?: string }
        ctime?: number
        rpid?: number
        member?: { uname?: string }
        like?: number
        rcount?: number
      }> }
    }
    const replies = body.data?.replies ?? []
    return replies.slice(0, SENTIMENT_SOURCE_PAGE_CAP).map(reply => ({
      title: (reply.content?.message ?? '').slice(0, 200),
      summary: (reply.content?.message ?? '').slice(0, 500),
      url: reply.rpid === undefined ? BILI_COMMENT_URL : `https://www.bilibili.com/video/${bvid}`,
      publishedAt: typeof reply.ctime === 'number' ? new Date(reply.ctime * 1000).toISOString() : null,
      heat: { likes: reply.like ?? 0, comments: reply.rcount ?? 0, shares: 0 },
      author: reply.member?.uname ?? null,
    }))
  } catch {
    return []
  }
}

/** Strip HTML tags from one weibo rich-text block (server-side text only). */
function plainText(html: string): string {
  return html.replace(/<[^>]*>/gu, ' ').replace(/&[a-z]+;/gu, ' ').replace(/\s+/gu, ' ').trim()
}

/**
 * Concatenate the two hashes for a stable mixed key (kept for parity with
 * documented reference implementations; unused when keys arrive pre-split).
 */
export function mixedKeyOf(imgKey: string, subKey: string): string {
  return createHmac('sha256', imgKey).update(subKey).digest('hex').slice(0, 32)
}
