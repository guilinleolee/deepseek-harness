/**
 * Website fetching for the persona `site` AI operation. One page is fetched
 * per call with a declared fetcher identity, converted to visible text
 * through the shared gather sanitizer, and handed to the caller as the
 * extraction input. Network reading only: nothing here touches the
 * filesystem, and the HTTP fetch happens exclusively inside this
 * gateway-side module — the browser never reaches cross-origin sites itself.
 */

import { htmlToText } from '../gather/sanitize.ts'

/** Single-page fetch deadline; a slow site must not pin the AI queue. */
export const PERSONA_SITE_FETCH_TIMEOUT_MS = 30_000

/** Hard response-size cap; a runaway page is rejected instead of buffered. */
export const PERSONA_SITE_MAX_BYTES = 2 * 1024 * 1024

/** Declared fetcher identity of the persona site face. */
const PERSONA_SITE_USER_AGENT = 'dsh-content-persona/0.1 (dsh content studio persona view)'

/** Injection face for tests: the fetch implementation defaults to the global one. */
export interface PersonaSiteFetchDeps {
  readonly fetchImpl?: typeof fetch
}

/** The fetch failure carries the HTTP status for caller-facing messages. */
export class PersonaSiteHttpError extends Error {
  /** HTTP status of the failed response. */
  readonly status: number

  constructor(status: number, url: string) {
    super(`site request to ${url} failed with HTTP ${status}`)
    this.name = 'PersonaSiteHttpError'
    this.status = status
  }
}

/**
 * Validate and normalize one user-typed site address: a scheme-less input
 * gets `https://`, and only http(s) survives — every other scheme
 * (`file:`, `data:`, `javascript:`) rejects before any request is built.
 * @param raw - the address as the wizard's URL field carries it.
 * @returns the absolute http(s) URL to fetch.
 */
export function normalizeSiteUrl(raw: string): string {
  const trimmed = raw.trim()
  const candidate = /^[a-zA-Z][a-zA-Z\d+\-.]*:\/\//u.test(trimmed) ? trimmed : `https://${trimmed}`
  const parsed = new URL(candidate)
  if (parsed.protocol !== 'https:' && parsed.protocol !== 'http:') {
    throw new Error(`persona site url must be http(s), got: ${trimmed.slice(0, 200)}`)
  }
  return parsed.toString()
}

/**
 * Fetch one blog or company website and reduce it to its visible text.
 * @param url - the user-typed site address.
 * @param deps - injected fetch implementation for tests.
 * @param signal - caller cancellation; combined with the per-request deadline.
 * @returns the page's visible text, whitespace-squeezed; empty for a page without text.
 */
export async function fetchSiteText(
  url: string, deps: PersonaSiteFetchDeps = {}, signal?: AbortSignal,
): Promise<string> {
  const target = normalizeSiteUrl(url)
  const deadline = AbortSignal.timeout(PERSONA_SITE_FETCH_TIMEOUT_MS)
  const response = await (deps.fetchImpl ?? fetch)(target, {
    headers: {
      'user-agent': PERSONA_SITE_USER_AGENT,
      'accept': 'text/html,application/xhtml+xml;q=0.9,text/plain;q=0.8,*/*;q=0.1',
    },
    redirect: 'follow',
    signal: signal === undefined ? deadline : AbortSignal.any([deadline, signal]),
  })
  if (!response.ok) throw new PersonaSiteHttpError(response.status, target)

  const declared = Number(response.headers.get('content-length') ?? '0')
  if (declared > PERSONA_SITE_MAX_BYTES) throw new PersonaSiteHttpError(413, target)
  const body = await response.text()
  if (body.length > PERSONA_SITE_MAX_BYTES) throw new PersonaSiteHttpError(413, target)

  // The head's title and meta text would survive the tag strip as leading
  // noise; dropping the whole head keeps the visible body text only.
  const text = htmlToText(body.replace(/<head[\s>][\s\S]*?<\/head>/iu, ''))
  return text.replace(/\n{3,}/gu, '\n\n').trim()
}
