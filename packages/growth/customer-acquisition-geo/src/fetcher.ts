/**
 * The GEO serial crawler: turns one user-provided URL into a bounded,
 * same-origin page set, enforcing every runtime edge of red line 1 that
 * pre-execute cannot see — serial fetches (concurrency 1), per-page timeout,
 * response-body size cap, robots.txt `Disallow` skipping, and no cross-domain
 * discovery (only links on the seed URL's origin are followed, ever).
 * @module @deepseek-ai/dsh-customer-acquisition-geo/fetcher
 */

import type { WebFetchResult } from '@deepseek-ai/dsh-web'
import { isDisallowed, parseRobots, type RobotsRules } from './robots.ts'

/** One URL fetched through the web capability. */
export type FetchOne = (url: string, signal?: AbortSignal) => Promise<WebFetchResult>

/** One successfully retrieved page, already reduced to text. */
export interface FetchedPage {
  /** Final URL after redirects. */
  readonly url: string
  /** HTTP status code. */
  readonly statusCode: number
  /** Body text (HTML or plain text). */
  readonly body: string
}

/** Everything the crawler learned in one scan. */
export interface CrawlResult {
  /** Retrieved pages, in visit order. */
  readonly pages: readonly FetchedPage[]
  /** Paths skipped because robots.txt disallowed them. */
  readonly robotsSkippedPaths: readonly string[]
  /** Candidates dropped for exceeding the response-body cap. */
  readonly oversizedUrls: readonly string[]
  /** Fetch failures (timeout, network) with their reason; the scan continues. */
  readonly failures: readonly { url: string; reason: string }[]
  /** Whether a robots.txt file was retrieved and parsed. */
  readonly robotsFetched: boolean
}

/** Tunables for one crawl; every value is already capped by the caller. */
export interface CrawlOptions {
  /** Maximum pages to fetch, including robots.txt (the hard cap is 20). */
  readonly maxPages: number
  /** Per-request timeout in milliseconds (the hard cap is 10s). */
  readonly timeoutMs: number
  /** Response-body byte cap (the hard cap is 2 MiB). */
  readonly maxBytes: number
}

/**
 * Fetch one URL under the per-page timeout, or throw a {@link CrawlSkip}.
 * @param fetchOne - the web-capability fetch function.
 * @param url - the URL to fetch.
 * @param timeoutMs - per-request timeout.
 * @returns the fetch result.
 */
function timedFetch(fetchOne: FetchOne, url: string, timeoutMs: number): Promise<WebFetchResult> {
  return fetchOne(url, AbortSignal.timeout(timeoutMs))
}

/**
 * Extract same-origin links from an HTML page. Only `<a href>` with an
 * http(s) URL on the seed's origin survives; fragments are stripped.
 * @param html - the page body.
 * @param origin - the seed URL's origin; anything else is dropped.
 * @returns candidate URLs in document order, deduplicated.
 */
export function extractSameOriginLinks(html: string, origin: string): string[] {
  const links: string[] = []
  const seen = new Set<string>()
  for (const match of html.matchAll(/<a\b[^>]*\shref\s*=\s*["']([^"'\s]+)["']/gi)) {
    let candidate: URL
    const href = match[1]
    if (href === undefined) continue
    try {
      candidate = new URL(href, origin)
    } catch {
      continue
    }
    if (candidate.protocol !== 'http:' && candidate.protocol !== 'https:') continue
    if (candidate.origin !== origin) continue
    candidate.hash = ''
    const resolved = candidate.href
    if (!seen.has(resolved)) {
      seen.add(resolved)
      links.push(resolved)
    }
  }
  return links
}

/**
 * Crawl one site serially from the seed URL. The robots.txt at the seed's
 * origin is fetched first (it counts against the page budget); every
 * candidate — seed included — is checked against it, and `Disallow`ed paths
 * are recorded, never fetched. The crawl ends when the page budget is spent
 * or no same-origin candidate remains.
 * @param fetchOne - the web-capability fetch function.
 * @param seedUrl - the user-provided URL; only its origin is ever fetched.
 * @param options - capped crawl tunables.
 * @returns the pages, skips, and failures of the crawl.
 */
export async function crawlSite(
  fetchOne: FetchOne,
  seedUrl: string,
  options: CrawlOptions,
): Promise<CrawlResult> {
  const seed = new URL(seedUrl)
  const origin = seed.origin
  const pages: FetchedPage[] = []
  const robotsSkippedPaths: string[] = []
  const oversizedUrls: string[] = []
  const failures: { url: string; reason: string }[] = []
  let budget = options.maxPages

  // robots.txt first: a non-2xx or failed retrieval means allow-all, which
  // the robots standard prescribes for absent files.
  let robots: RobotsRules = { rules: [] }
  let robotsFetched = false
  if (budget > 0) {
    budget -= 1
    try {
      const result = await timedFetch(fetchOne, `${origin}/robots.txt`, options.timeoutMs)
      if (result.statusCode >= 200 && result.statusCode < 300) {
        robots = parseRobots(result.body.kind === 'html' ? stripTags(result.body.content) : result.body.content)
        robotsFetched = true
      }
    } catch (error) {
      failures.push({ url: `${origin}/robots.txt`, reason: `robots.txt 获取失败：${String(error)}` })
    }
  }

  const queue: string[] = [seed.href]
  const visited = new Set<string>()
  while (budget > 0) {
    const candidate = queue.shift()
    if (candidate === undefined) break
    if (visited.has(candidate)) continue
    visited.add(candidate)
    if (isDisallowed(candidate, robots)) {
      robotsSkippedPaths.push(new URL(candidate).pathname)
      continue
    }
    budget -= 1
    try {
      const result = await timedFetch(fetchOne, candidate, options.timeoutMs)
      const byteLength = byteLengthOf(result)
      if (byteLength > options.maxBytes) {
        oversizedUrls.push(candidate)
        continue
      }
      if (result.statusCode >= 200 && result.statusCode < 300) {
        pages.push({ url: result.url, statusCode: result.statusCode, body: result.body.content })
        if (result.body.kind === 'html') {
          for (const link of extractSameOriginLinks(result.body.content, origin)) {
            if (!visited.has(link)) queue.push(link)
          }
        }
      } else {
        failures.push({ url: candidate, reason: `HTTP ${result.statusCode}` })
      }
    } catch (error) {
      failures.push({ url: candidate, reason: `抓取失败：${String(error)}` })
    }
  }
  return { pages, robotsSkippedPaths, oversizedUrls, failures, robotsFetched }
}

/**
 * Byte length of one fetch result's decoded body.
 * @param result - the fetch result.
 * @returns the body's UTF-8 byte length.
 */
function byteLengthOf(result: WebFetchResult): number {
  return new TextEncoder().encode(result.body.content).byteLength
}

/**
 * Reduce an HTML robots.txt body (some servers mis-serve it as HTML) to text.
 * @param html - the raw body.
 * @returns tag-stripped text.
 */
function stripTags(html: string): string {
  return html.replace(/<[^>]*>/g, '')
}
