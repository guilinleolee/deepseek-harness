import { describe, expect, it } from 'vitest'
import { GEO_RESPONSE_MAX_BYTES } from '../src/main-package.ts'
import { isDisallowed, parseRobots, GEO_USER_AGENT } from '../src/robots.ts'
import { crawlSite, extractSameOriginLinks } from '../src/fetcher.ts'
import type { FetchOne } from '../src/fetcher.ts'
import type { WebFetchResult } from '@deepseek-ai/dsh-web'

function htmlFetch(routes: Record<string, string | { status: number; body: string }>): FetchOne & { calls: string[] } {
  const calls: string[] = []
  const fetchOne: FetchOne = async (url) => {
    calls.push(url)
    const route = routes[url]
    if (route === undefined) {
      return { url, statusCode: 404, body: { kind: 'text', content: 'not found' }, truncated: false }
    }
    const resolved = typeof route === 'string' ? { status: 200, body: route } : route
    const result: WebFetchResult = { url, statusCode: resolved.status, body: { kind: 'html', content: resolved.body }, truncated: false }
    return result
  }
  return Object.assign(fetchOne, { calls })
}

describe('robots.txt interpretation', () => {
  it('applies the wildcard group when the GEO agent has none', () => {
    const rules = parseRobots('User-agent: *\nDisallow: /private\nDisallow: /tmp/')
    expect(isDisallowed('https://x.com/private/data', rules)).toBe(true)
    expect(isDisallowed('https://x.com/tmp/cache', rules)).toBe(true)
    expect(isDisallowed('https://x.com/public', rules)).toBe(false)
  })

  it('a group naming the GEO agent overrides the wildcard group', () => {
    const rules = parseRobots(`User-agent: *\nDisallow: /\n\nUser-agent: ${GEO_USER_AGENT}\nDisallow:`)
    expect(isDisallowed('https://x.com/anything', rules)).toBe(false)
  })

  it('supports $ anchoring and comments, and an absent file allows all', () => {
    const rules = parseRobots('# comment\nUser-agent: *\nDisallow: /exact.html$\nDisallow: /drafts')
    expect(isDisallowed('https://x.com/exact.html', rules)).toBe(true)
    expect(isDisallowed('https://x.com/exact.html?x=1', rules)).toBe(false)
    expect(isDisallowed('https://x.com/drafts/2024/a', rules)).toBe(true)
    expect(isDisallowed('https://x.com/', parseRobots(undefined))).toBe(false)
  })

  it('ignores a Disallow that appears before any User-agent group', () => {
    const rules = parseRobots('Disallow: /orphan\nUser-agent: *\nDisallow: /real')
    expect(isDisallowed('https://x.com/orphan', rules)).toBe(false)
    expect(isDisallowed('https://x.com/real', rules)).toBe(true)
  })
})

describe('link extraction stays same-origin', () => {
  it('keeps only same-origin http(s) hrefs, deduplicated, fragments stripped', () => {
    const links = extractSameOriginLinks(
      '<a href="/a">1</a><a href="/a">dup</a><a href="https://other.com/x">外链</a>' +
      '<a href="https://x.com/b#frag">2</a><a href="javascript:alert(1)">js</a><a href="mailto:a@b.c">mail</a>',
      'https://x.com',
    )
    expect(links).toEqual(['https://x.com/a', 'https://x.com/b'])
  })

  it('skips a malformed href attribute and an href that no URL parser accepts', () => {
    const links = extractSameOriginLinks(
      '<a href>无值</a><a href="http://[">坏地址</a><a href="/ok">好</a>',
      'https://x.com',
    )
    expect(links).toEqual(['https://x.com/ok'])
  })
})

describe('crawlSite enforces every runtime red-line edge', () => {
  it('never fetches robots.txt Disallow paths and records them', async () => {
    const fetchOne = htmlFetch({
      'https://x.com/robots.txt': 'User-agent: *\nDisallow: /private\n',
      'https://x.com/': '<html><body><a href="/private/x">私密</a><a href="/ok">ok</a></body></html>',
      'https://x.com/ok': '<html><body>ok</body></html>',
    })
    const result = await crawlSite(fetchOne, 'https://x.com/', { maxPages: 5, timeoutMs: 1000, maxBytes: GEO_RESPONSE_MAX_BYTES })
    expect(result.robotsFetched).toBe(true)
    expect(result.robotsSkippedPaths).toEqual(['/private/x'])
    expect(fetchOne.calls).not.toContain('https://x.com/private/x')
    expect(result.pages.map(page => page.url)).toEqual(['https://x.com/', 'https://x.com/ok'])
  })

  it('never follows cross-origin links (no automatic domain discovery)', async () => {
    const fetchOne = htmlFetch({
      'https://x.com/robots.txt': '',
      'https://x.com/': '<a href="https://evil.com/steal">x</a><a href="https://x.com/next">y</a>',
      'https://x.com/next': '<html></html>',
    })
    const result = await crawlSite(fetchOne, 'https://x.com/', { maxPages: 5, timeoutMs: 1000, maxBytes: GEO_RESPONSE_MAX_BYTES })
    expect(fetchOne.calls).not.toContain('https://evil.com/steal')
    expect(result.pages).toHaveLength(2)
  })

  it('spends at most maxPages fetches including robots.txt', async () => {
    const routes: Record<string, string> = {
      'https://x.com/robots.txt': '',
      'https://x.com/': '<a href="/p1">1</a><a href="/p2">2</a><a href="/p3">3</a>',
      'https://x.com/p1': '<html></html>',
      'https://x.com/p2': '<html></html>',
      'https://x.com/p3': '<html></html>',
    }
    const fetchOne = htmlFetch(routes)
    const result = await crawlSite(fetchOne, 'https://x.com/', { maxPages: 3, timeoutMs: 1000, maxBytes: GEO_RESPONSE_MAX_BYTES })
    // robots.txt (1) + seed (2) + one more (3) — the budget stops the crawl.
    expect(fetchOne.calls).toHaveLength(3)
    expect(result.pages.length).toBeLessThanOrEqual(2)
  })

  it('drops pages whose body exceeds the byte cap', async () => {
    const huge = 'x'.repeat(64)
    const fetchOne = htmlFetch({
      'https://x.com/robots.txt': '',
      'https://x.com/': `<html><body>${huge}</body></html>`,
    })
    const result = await crawlSite(fetchOne, 'https://x.com/', { maxPages: 5, timeoutMs: 1000, maxBytes: 16 })
    expect(result.pages).toHaveLength(0)
    expect(result.oversizedUrls).toEqual(['https://x.com/'])
  })

  it('aborts a page that exceeds the per-page timeout and continues', async () => {
    const slow: FetchOne = async (url, signal) => {
      if (url.endsWith('robots.txt')) {
        return { url, statusCode: 200, body: { kind: 'text', content: '' }, truncated: false }
      }
      if (url === 'https://x.com/slow') {
        return new Promise<WebFetchResult>((resolve, reject) => {
          const timer = setTimeout(() => {
            resolve({ url, statusCode: 200, body: { kind: 'html', content: '<html></html>' }, truncated: false })
          }, 500)
          signal?.addEventListener('abort', () => {
            clearTimeout(timer)
            reject(new Error('aborted'))
          }, { once: true })
        })
      }
      return { url, statusCode: 200, body: { kind: 'html', content: '<html><body>fast</body></html>' }, truncated: false }
    }
    const result = await crawlSite(slow, 'https://x.com/slow', { maxPages: 5, timeoutMs: 30, maxBytes: GEO_RESPONSE_MAX_BYTES })
    expect(result.pages).toHaveLength(0)
    expect(result.failures).toHaveLength(1)
    expect(result.failures[0]!.reason).toContain('抓取失败')
  })

  it('fetches strictly serially (concurrency 1)', async () => {
    let inFlight = 0
    let peak = 0
    const serial: FetchOne = async (url) => {
      inFlight += 1
      peak = Math.max(peak, inFlight)
      await new Promise(resolve => setTimeout(resolve, 10))
      inFlight -= 1
      return { url, statusCode: 200, body: { kind: 'text', content: 'x' }, truncated: false }
    }
    await crawlSite(serial, 'https://x.com/', { maxPages: 4, timeoutMs: 1000, maxBytes: GEO_RESPONSE_MAX_BYTES })
    expect(peak).toBe(1)
  })

  it('a zero page budget fetches nothing at all', async () => {
    const fetchOne = htmlFetch({ 'https://x.com/robots.txt': '', 'https://x.com/': '<html></html>' })
    const result = await crawlSite(fetchOne, 'https://x.com/', { maxPages: 0, timeoutMs: 1000, maxBytes: GEO_RESPONSE_MAX_BYTES })
    expect(fetchOne.calls).toEqual([])
    expect(result).toMatchObject({ pages: [], robotsFetched: false })
  })

  it('a missing or failing robots.txt means allow-all, and a hard failure is recorded', async () => {
    const missing = htmlFetch({ 'https://x.com/': '<html><body><a href="/x">x</a></body></html>', 'https://x.com/x': '<html></html>' })
    const missingResult = await crawlSite(missing, 'https://x.com/', { maxPages: 3, timeoutMs: 1000, maxBytes: GEO_RESPONSE_MAX_BYTES })
    expect(missingResult.robotsFetched).toBe(false)
    expect(missingResult.pages).toHaveLength(2) // robots.txt 404s, then seed + /x fit the budget

    const failing: FetchOne = async (url) => {
      if (url.endsWith('robots.txt')) throw new Error('network down')
      return { url, statusCode: 200, body: { kind: 'html', content: '<html></html>' }, truncated: false }
    }
    const failed = await crawlSite(failing, 'https://x.com/', { maxPages: 3, timeoutMs: 1000, maxBytes: GEO_RESPONSE_MAX_BYTES })
    expect(failed.robotsFetched).toBe(false)
    expect(failed.failures[0]).toMatchObject({ url: 'https://x.com/robots.txt' })
    expect(failed.failures[0]!.reason).toContain('robots.txt 获取失败')
  })

  it('does not refetch a doubly queued candidate nor requeue a visited one', async () => {
    // seed queues /b and /c; /b also links /c while /c is still unvisited, so
    // /c enters the queue twice and the second pop must skip it; /c links back
    // to the already-visited /b, which must not requeue
    const fetchOne = htmlFetch({
      'https://x.com/robots.txt': '',
      'https://x.com/': '<html><body><a href="/b">b</a><a href="/c">c</a></body></html>',
      'https://x.com/b': '<html><body><a href="/c">c 再次</a></body></html>',
      'https://x.com/c': '<html><body><a href="/b">b 已访问</a></body></html>',
    })
    const result = await crawlSite(fetchOne, 'https://x.com/', { maxPages: 6, timeoutMs: 1000, maxBytes: GEO_RESPONSE_MAX_BYTES })
    expect(fetchOne.calls.filter(url => url === 'https://x.com/c')).toHaveLength(1)
    expect(result.pages).toHaveLength(3) // seed, /b, /c
  })

  it('records a non-2xx page as a failure instead of a page', async () => {
    const routes: Record<string, string | { status: number; body: string }> = {
      'https://x.com/robots.txt': '',
      'https://x.com/': '<html><body><a href="/gone">已删除</a></body></html>',
      'https://x.com/gone': { status: 404, body: 'deleted' },
    }
    const fetchOne = htmlFetch(routes)
    const result = await crawlSite(fetchOne, 'https://x.com/', { maxPages: 4, timeoutMs: 1000, maxBytes: GEO_RESPONSE_MAX_BYTES })
    expect(result.pages).toHaveLength(1)
    expect(result.failures).toEqual([{ url: 'https://x.com/gone', reason: 'HTTP 404' }])
  })
})
