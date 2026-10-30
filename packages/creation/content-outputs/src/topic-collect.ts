/**
 * The keyword topic-collection engine: one run fetches the category's RSS
 * feeds through the shared gather fetcher plus one page of weibo visitor
 * search and bilibili public video search per keyword, keeps entries whose
 * title or summary contains any of the category's keywords (case-folded),
 * and drops entries the topic bank already holds — by URL or normalized
 * title, so a repost under a changed slug still dedupes. No LLM, no scraper:
 * the same low-frequency public sources as the sentiment scan, degrading to
 * an empty page per source on any failure so one blocked endpoint never
 * kills the run.
 */

import { fetchFeedDocument } from './gather/feed.ts'
import { htmlToText } from './gather/sanitize.ts'
import { fetchBiliVideos, fetchWeiboSearch, type SourceEntry } from './sentiment/sources.ts'

/** Keywords read per collection run. */
export const TOPIC_COLLECT_KEYWORDS_CAP = 10

/** Feeds read per collection run. */
export const TOPIC_COLLECT_FEEDS_CAP = 5

/** Entries returned per collection run. */
export const TOPIC_COLLECT_RESULT_CAP = 20

/** The wire face of one collection request: the category's watch list plus the dedupe keys. */
export interface TopicCollectRequest {
  /** Keyword terms, OR-matched against each entry's title and summary. */
  readonly keywords: readonly string[]
  /** RSS feed URLs to read once per run (not per keyword). */
  readonly feedUrls: readonly string[]
  /** Topic URLs the bank already holds; matches are dropped. */
  readonly existingUrls: readonly string[]
  /** Topic titles the bank already holds; matches are dropped. */
  readonly existingTitles: readonly string[]
}

/** One collected candidate, normalized across the three sources. */
export interface TopicCollectEntry {
  readonly title: string
  readonly summary: string | null
  /** Original link; null for social entries whose card carries none. */
  readonly url: string | null
  readonly publishedAt: string | null
  /** Which source produced the entry. */
  readonly source: 'rss' | 'weibo' | 'bili'
  readonly author: string | null
}

/** The wire face of one collection result. */
export interface TopicCollectResult {
  /** Matched, deduplicated entries capped at `TOPIC_COLLECT_RESULT_CAP`. */
  readonly entries: readonly TopicCollectEntry[]
}

/** Injection face for tests: every network read is replaceable. */
export interface TopicCollectDeps {
  readonly fetchImpl?: typeof fetch
  readonly fetchFeed?: typeof fetchFeedDocument
  readonly fetchWeibo?: typeof fetchWeiboSearch
  readonly fetchBili?: typeof fetchBiliVideos
}

/** Case-folded dedupe and match key of one text. */
function textKey(value: string): string {
  return value.trim().toLowerCase()
}

/** Strip markup and collapse whitespace so weibo HTML summaries match like plain text. */
function plainText(value: string): string {
  return htmlToText(value).replace(/\s+/gu, ' ').trim()
}

/** True when any keyword appears in the entry's title or summary. */
function matchesKeywords(keywords: readonly string[], title: string, summary: string | null): boolean {
  const haystack = textKey(`${title} ${summary ?? ''}`)
  return keywords.some(keyword => haystack.includes(textKey(keyword)))
}

/** Map one social-source entry to the wire shape, marking up its summary. */
function entryOfSource(entry: SourceEntry, source: 'weibo' | 'bili'): TopicCollectEntry {
  const summary = plainText(entry.summary)
  return {
    title: entry.title,
    summary: summary.length === 0 ? null : summary,
    url: entry.url.length === 0 ? null : entry.url,
    publishedAt: entry.publishedAt,
    source,
    author: entry.author,
  }
}

/**
 * Run one collection pass for one category.
 * @param request - the category's keywords, feeds, and the bank's dedupe keys.
 * @param deps - injected network reads for tests.
 * @returns the matched, deduplicated entries, newest evidence kept per key.
 */
export async function collectTopicEntries(request: TopicCollectRequest, deps: TopicCollectDeps = {}): Promise<TopicCollectResult> {
  const keywords = request.keywords.slice(0, TOPIC_COLLECT_KEYWORDS_CAP)
  const feedUrls = request.feedUrls.slice(0, TOPIC_COLLECT_FEEDS_CAP)
  // `exactOptionalPropertyTypes` forbids an explicit `fetchImpl: undefined`;
  // build the shared injection object conditionally for all three readers.
  const fetchDeps: { fetchImpl?: typeof fetch } = deps.fetchImpl === undefined ? {} : { fetchImpl: deps.fetchImpl }
  const seenUrls = new Set(request.existingUrls.map(textKey))
  const seenTitles = new Set(request.existingTitles.map(textKey))
  const entries: TopicCollectEntry[] = []

  const accept = (entry: TopicCollectEntry): void => {
    if (!matchesKeywords(keywords, entry.title, entry.summary)) return
    const urlKey = entry.url === null ? null : textKey(entry.url)
    const titleKey = textKey(entry.title)
    if (urlKey !== null && seenUrls.has(urlKey)) {
      // The bank already holds this URL; its title under a new link is a
      // repost, so the title counts as seen too.
      seenTitles.add(titleKey)
      return
    }
    if (seenTitles.has(titleKey)) return
    if (urlKey !== null) seenUrls.add(urlKey)
    seenTitles.add(titleKey)
    if (entries.length < TOPIC_COLLECT_RESULT_CAP) entries.push(entry)
  }

  const feedReads = feedUrls.map(async (url) => {
    const feed = await (deps.fetchFeed ?? fetchFeedDocument)({ url }, fetchDeps).catch(() => null)
    if (feed === null || feed.notModified) return
    for (const item of feed.items) {
      if (item.title === null) continue
      accept({
        title: item.title,
        summary: item.summary === null ? null : plainText(item.summary),
        url: item.url,
        publishedAt: item.publishedAt,
        source: 'rss',
        author: null,
      })
    }
  })
  const socialReads = keywords.map(async (keyword) => {
    const [weibo, bili] = await Promise.all([
      (deps.fetchWeibo ?? fetchWeiboSearch)(keyword, fetchDeps).catch(() => []),
      (deps.fetchBili ?? fetchBiliVideos)(keyword, fetchDeps).catch(() => []),
    ])
    for (const entry of weibo) accept(entryOfSource(entry, 'weibo'))
    for (const entry of bili) accept(entryOfSource(entry, 'bili'))
  })
  await Promise.all([...feedReads, ...socialReads])
  // The reads resolve concurrently; the source rank then the title give the
  // wire face a stable order.
  const sourceRank = { rss: 0, weibo: 1, bili: 2 } as const
  entries.sort((a, b) => sourceRank[a.source] - sourceRank[b.source] || (a.title < b.title ? -1 : 1))
  return { entries }
}
