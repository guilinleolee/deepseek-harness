import { describe, expect, it } from 'vitest'
import {
  GatherFeedHttpError, dedupKey, fetchFeedDocument, normalizeDedupUrl, normalizeParsedFeed,
} from '../src/gather/feed.ts'
import type { GatherFeedRequest } from '../src/types.ts'

const RSS_DOCUMENT = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
  <title>示例订阅</title>
  <item>
    <title>第一篇</title>
    <link>https://example.com/post-1?utm_source=rss&amp;id=2&amp;a=1</link>
    <guid isPermaLink="false">guid-1</guid>
    <pubDate>Thu, 25 Sep 2026 08:00:00 GMT</pubDate>
    <description>摘要一</description>
    <content:encoded xmlns:content="http://purl.org/rss/1.0/modules/content/"><![CDATA[<p>正文一</p>]]></content:encoded>
  </item>
  <item>
    <title>第二篇</title>
    <link>https://example.com/post-2</link>
  </item>
</channel></rss>`

const ATOM_DOCUMENT = `<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Atom 订阅</title>
  <entry>
    <id>atom-1</id>
    <title>Atom 条目</title>
    <link rel="alternate" href="https://example.org/atom-1"/>
    <published>2026-09-24T10:00:00Z</published>
    <summary>Atom 摘要</summary>
    <content type="html">&lt;p&gt;Atom 正文&lt;/p&gt;</content>
  </entry>
</feed>`

describe('normalizeDedupUrl', () => {
  it('drops tracking parameters and sorts the query string', () => {
    expect(normalizeDedupUrl('https://example.com/post?a=1&utm_source=rss&id=2'))
      .toBe('https://example.com/post?a=1&id=2')
  })

  it('collapses ref-tagged reposts onto one normalized form', () => {
    expect(normalizeDedupUrl('https://example.com/post?utm_campaign=x'))
      .toBe(normalizeDedupUrl('HTTPS://example.com/post/'))
  })
})

describe('dedupKey', () => {
  it('prefers the feed guid and falls back to the link SHA-1', () => {
    expect(dedupKey('guid-1', 'https://example.com/post-1')).toBe('guid-1')
    const hashed = dedupKey(undefined, 'https://example.com/post-1')
    expect(hashed).toMatch(/^[0-9a-f]{40}$/)
    // Same normalized link → same key; a different link → a different key.
    expect(dedupKey(undefined, 'https://example.com/post-1?utm_source=rss')).toBe(hashed)
    expect(dedupKey(undefined, 'https://example.com/post-2')).not.toBe(hashed)
  })
})

describe('normalizeParsedFeed', () => {
  it('normalizes RSS items with guid, normalized link, and content', async () => {
    const { parseFeed } = await import('feedsmith')
    const { feedTitle, items } = normalizeParsedFeed(parseFeed(RSS_DOCUMENT))
    expect(feedTitle).toBe('示例订阅')
    expect(items).toHaveLength(2)
    expect(items[0]).toMatchObject({
      id: 'guid-1',
      rawGuid: 'guid-1',
      url: 'https://example.com/post-1?a=1&id=2',
      title: '第一篇',
      summary: '摘要一',
      content: '<p>正文一</p>',
    })
    expect(items[0]!.publishedAt).toBe('2026-09-25T08:00:00.000Z')
    // A guid-less item keys on the link hash and keeps the raw guid absent.
    expect(items[1]!.id).toMatch(/^[0-9a-f]{40}$/)
    expect(items[1]!.rawGuid).toBeNull()
  })

  it('normalizes Atom entries through the alternate link', async () => {
    const { parseFeed } = await import('feedsmith')
    const { feedTitle, items } = normalizeParsedFeed(parseFeed(ATOM_DOCUMENT))
    expect(feedTitle).toBe('Atom 订阅')
    expect(items[0]).toMatchObject({
      id: 'atom-1',
      rawGuid: 'atom-1',
      url: 'https://example.org/atom-1',
      title: 'Atom 条目',
      summary: 'Atom 摘要',
    })
  })
})

describe('fetchFeedDocument', () => {
  /** One-shot Response stub over a canned document. */
  function response(body: string | null, init: { status?: number; headers?: Record<string, string> } = {}): Response {
    return new Response(body, { status: init.status ?? 200, ...(init.headers !== undefined ? { headers: init.headers } : {}) })
  }

  it('sends conditional-request cursors and reports a 304 as notModified', async () => {
    const requests: Request[] = []
    const fetchImpl = (async (input: unknown, init?: RequestInit) => {
      requests.push(new Request(String(input), init))
      return response(null, { status: 304, headers: { etag: '"v2"' } })
    }) as typeof fetch
    const request: GatherFeedRequest = { url: 'https://example.com/feed', etag: '"v1"', lastModified: 'Wed, 24 Sep 2026 00:00:00 GMT' }
    const result = await fetchFeedDocument(request, { fetchImpl })
    expect(result.notModified).toBe(true)
    expect(result.items).toEqual([])
    expect(result.etag).toBe('"v2"')
    expect(requests[0]!.headers.get('if-none-match')).toBe('"v1"')
    expect(requests[0]!.headers.get('if-modified-since')).toBe('Wed, 24 Sep 2026 00:00:00 GMT')
  })

  it('returns drafts plus the next cursors from a full response', async () => {
    const fetchImpl = (async () => response(RSS_DOCUMENT, { headers: { etag: '"v2"', 'last-modified': 'Thu, 25 Sep 2026 00:00:00 GMT' } })) as typeof fetch
    const result = await fetchFeedDocument({ url: 'https://example.com/feed' }, { fetchImpl })
    expect(result.notModified).toBe(false)
    expect(result.etag).toBe('"v2"')
    expect(result.lastModified).toBe('Thu, 25 Sep 2026 00:00:00 GMT')
    expect(result.items).toHaveLength(2)
  })

  it('raises an HTTP error with the status for failed responses', async () => {
    const fetchImpl = (async () => response('nope', { status: 403 })) as typeof fetch
    await expect(fetchFeedDocument({ url: 'https://example.com/feed' }, { fetchImpl }))
      .rejects.toMatchObject({ name: 'GatherFeedHttpError', status: 403 })
    expect(new GatherFeedHttpError(500, 'https://x').status).toBe(500)
  })

  it('rejects an unparseable body and an oversized declared payload', async () => {
    const notFeed = (async () => response('<html><body>not a feed</body></html>')) as typeof fetch
    await expect(fetchFeedDocument({ url: 'https://example.com/feed' }, { fetchImpl: notFeed }))
      .rejects.toThrow('not a parseable')
    const huge = (async () => response('x', { headers: { 'content-length': String(10 * 1024 * 1024 + 1) } })) as typeof fetch
    await expect(fetchFeedDocument({ url: 'https://example.com/feed' }, { fetchImpl: huge }))
      .rejects.toMatchObject({ status: 413 })
  })
})
