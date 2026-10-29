/**
 * Source adapters beyond RSS: one shared entry-draft vocabulary and the
 * implementations. The weibo adapter reads the PUBLIC mobile-container
 * search API and the public hotflow comment endpoint (m.weibo.cn, no login,
 * visitor cookies only — the 2026-10-07 research's compliant visitor-page
 * path); the bili adapter reads bilibili's public wbi-signed video-search
 * and video-comment endpoints. All are low-frequency, keyword-scoped reads
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

/**
 * One normalized candidate row before keyword filtering; the scan owns
 * classification. `refId` carries the platform-native id a comment
 * drill-down needs (weibo mblog id, bilibili bvid); null for sources
 * without a comment layer.
 */
export interface SourceEntry {
  readonly title: string
  readonly summary: string
  readonly url: string
  readonly publishedAt: string | null
  /** Engagement counts when the endpoint exposes them; feeds the alert heat. */
  readonly heat: { likes: number; comments: number; shares: number } | null
  readonly author: string | null
  /** The platform-native id behind this entry, when a comment layer exists. */
  readonly refId?: string | null
}

/** Injection face for tests: the fetch implementation defaults to the global one. */
export interface SourceDeps {
  readonly fetchImpl?: typeof fetch
}

/** The m.weibo.cn container API: one page of keyword search results. */
const WEIBO_SEARCH_URL = 'https://m.weibo.cn/api/container/getIndex'
/** The m.weibo.cn hot-comment API: one page of top comments of one mblog. */
const WEIBO_COMMENT_URL = 'https://m.weibo.cn/comments/hotflow'

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
        refId: idText.length > 0 ? idText : null,
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

/**
 * Fetch one page of top comments of one weibo mblog (public hotflow
 * endpoint, visitor cookies only — the same access tier as the search
 * container API above).
 * @param id - the mblog's platform-native id (`SourceEntry.refId`).
 * @param deps - injected fetch for tests.
 * @returns normalized comment entries; empty on any failure (the scan continues).
 */
export async function fetchWeiboComments(id: string, deps: SourceDeps = {}): Promise<readonly SourceEntry[]> {
  try {
    const response = await (deps.fetchImpl ?? fetch)(`${WEIBO_COMMENT_URL}?id=${encodeURIComponent(id)}&mid=${encodeURIComponent(id)}&max_id_type=0`, {
      headers: {
        'user-agent': MOBILE_UA,
        'accept': 'application/json',
        'referer': `https://m.weibo.cn/detail/${encodeURIComponent(id)}`,
      },
      signal: AbortSignal.timeout(SENTIMENT_SOURCE_TIMEOUT_MS),
    })
    if (!response.ok) return []
    const body = await response.json() as {
      ok?: number
      data?: {
        data?: ReadonlyArray<{
          text?: string
          created_at?: string
          user?: { screen_name?: string }
          like_count?: number
          comment_count?: number
        }>
      }
    }
    const comments = body.data?.data ?? []
    return comments
      .filter((comment): comment is { text: string; created_at?: string; user?: { screen_name?: string }; like_count?: number; comment_count?: number } => typeof comment.text === 'string' && comment.text.length > 0)
      .slice(0, SENTIMENT_SOURCE_PAGE_CAP)
      .map(comment => {
        const text = plainText(comment.text)
        return {
          title: text.slice(0, 200),
          summary: text.slice(0, 500),
          url: `${WEIBO_COMMENT_URL}?id=${encodeURIComponent(id)}`,
          publishedAt: typeof comment.created_at === 'string' ? comment.created_at : null,
          heat: {
            likes: typeof comment.like_count === 'number' ? comment.like_count : 0,
            comments: typeof comment.comment_count === 'number' ? comment.comment_count : 0,
            shares: 0,
          },
          author: typeof comment.user?.screen_name === 'string' && comment.user.screen_name.length > 0 ? comment.user.screen_name : null,
          refId: null,
        }
      })
  } catch {
    // A failed comment read is an empty page, not a failed scan.
    return []
  }
}

/** The bilibili wbi video-search endpoint (public, signed like the web client). */
const BILI_VIDEO_SEARCH_URL = 'https://api.bilibili.com/x/web-interface/wbi/search/type'
/** The bilibili comment endpoint (public, no login; the wbi variant now demands a session). */
const BILI_COMMENT_URL = 'https://api.bilibili.com/x/v2/reply'

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
 * Fetch one page of bilibili videos matching the keyword (wbi video search;
 * no login, no SESSDATA). The entries carry the bvid in `refId` so the scan
 * can drill into each video's comment layer.
 * @param keyword - the search term.
 * @param deps - injected fetch for tests.
 * @returns normalized entries; empty on any failure.
 */
export async function fetchBiliVideos(keyword: string, deps: SourceDeps = {}): Promise<readonly SourceEntry[]> {
  const keys = await wbiKeys(deps)
  if (keys === null) return []
  try {
    const params: Record<string, string> = { keyword, search_type: 'video', page_size: String(SENTIMENT_SOURCE_PAGE_CAP) }
    const wRid = wbiSign(params, keys.imgKey, keys.subKey)
    const query = [...Object.entries(params)].map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`).join('&')
    const response = await (deps.fetchImpl ?? fetch)(`${BILI_VIDEO_SEARCH_URL}?${query}&w_rid=${wRid}`, {
      headers: { 'user-agent': DESKTOP_UA, 'accept': 'application/json', 'referer': 'https://search.bilibili.com/' },
      signal: AbortSignal.timeout(SENTIMENT_SOURCE_TIMEOUT_MS),
    })
    if (!response.ok) return []
    const body = await response.json() as {
      data?: { result?: ReadonlyArray<{
        bvid?: string
        title?: string
        description?: string
        author?: string
        pubdate?: number
        play?: number
        review?: number
        favorites?: number
      }> }
    }
    const results = body.data?.result ?? []
    return results
      .filter((item): item is { bvid: string; title?: string; description?: string; author?: string; pubdate?: number; play?: number; review?: number; favorites?: number } => typeof item.bvid === 'string' && item.bvid.length > 0)
      .slice(0, SENTIMENT_SOURCE_PAGE_CAP)
      .map(item => {
        const title = plainText(item.title ?? '').slice(0, 200)
        return {
          title,
          summary: (title.length > 0 ? `${title}\n` : '') + plainText(item.description ?? '').slice(0, 400),
          url: `https://www.bilibili.com/video/${item.bvid}`,
          publishedAt: typeof item.pubdate === 'number' ? new Date(item.pubdate * 1000).toISOString() : null,
          heat: { likes: item.play ?? 0, comments: item.review ?? 0, shares: item.favorites ?? 0 },
          author: typeof item.author === 'string' && item.author.length > 0 ? item.author : null,
          refId: item.bvid,
        }
      })
  } catch {
    return []
  }
}

/** The bilibili video-detail endpoint (public; resolves a BV id to its aid). */
const BILI_VIEW_URL = 'https://api.bilibili.com/x/web-interface/view'

/**
 * Resolve one video's numeric aid from its BV id through the public view
 * endpoint — the comment API keys on the aid, not the BV id.
 * @param bvid - the video's BV id.
 * @param deps - injected fetch for tests.
 * @returns the aid as a string, or null when the video or the read fails.
 */
export async function biliAidOf(bvid: string, deps: SourceDeps = {}): Promise<string | null> {
  try {
    const response = await (deps.fetchImpl ?? fetch)(`${BILI_VIEW_URL}?bvid=${encodeURIComponent(bvid)}`, {
      headers: { 'user-agent': DESKTOP_UA, 'accept': 'application/json' },
      signal: AbortSignal.timeout(SENTIMENT_SOURCE_TIMEOUT_MS),
    })
    if (!response.ok) return null
    const body = await response.json() as { data?: { aid?: number | string } }
    const aid = body.data?.aid
    if (typeof aid === 'number' && Number.isInteger(aid)) return String(aid)
    if (typeof aid === 'string' && aid.length > 0) return aid
    return null
  } catch {
    return null
  }
}

/**
 * Fetch one page of top comments of one bilibili video (BV id). The
 * comment API keys on the numeric aid, not the BV id, so the video is
 * resolved through the public view endpoint first.
 * @param bvid - the video's BV id.
 * @param deps - injected fetch for tests.
 * @returns normalized entries; empty on any failure.
 */
export async function fetchBiliComments(bvid: string, deps: SourceDeps = {}): Promise<readonly SourceEntry[]> {
  const aid = await biliAidOf(bvid, deps)
  if (aid === null) return []
  try {
    const params: Record<string, string> = { type: '1', oid: aid, sort: '2', pn: '1', ps: String(SENTIMENT_SOURCE_PAGE_CAP) }
    const query = [...Object.entries(params)].map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`).join('&')
    const response = await (deps.fetchImpl ?? fetch)(`${BILI_COMMENT_URL}?${query}`, {
      headers: { 'user-agent': DESKTOP_UA, 'accept': 'application/json', 'referer': 'https://www.bilibili.com/' },
      signal: AbortSignal.timeout(SENTIMENT_SOURCE_TIMEOUT_MS),
    })
    if (!response.ok) return []
    const body = await response.json() as {
      code?: number
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
    return replies
      .filter(reply => typeof reply.content?.message === 'string' && reply.content.message.length > 0)
      .slice(0, SENTIMENT_SOURCE_PAGE_CAP)
      .map(reply => ({
        title: plainText(reply.content?.message ?? '').slice(0, 200),
        summary: plainText(reply.content?.message ?? '').slice(0, 500),
        url: `https://www.bilibili.com/video/${bvid}`,
        publishedAt: typeof reply.ctime === 'number' ? new Date(reply.ctime * 1000).toISOString() : null,
        heat: { likes: reply.like ?? 0, comments: reply.rcount ?? 0, shares: 0 },
        author: reply.member?.uname ?? null,
        refId: null,
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
