/**
 * Article-copy extraction for the create workbench's paste-a-link entry. One
 * URL is fetched per call, the document is reduced to its visible prose
 * through the gather sanitization allowlist, and nothing is persisted: the
 * caller writes the extracted text into the editor draft. The HTTP fetch
 * happens exclusively inside this gateway-side module — the browser never
 * reaches cross-origin article pages itself.
 */

import { htmlToText, sanitizeGatherHtml } from '../gather/sanitize.ts'

/** Single-extraction deadline; a slow page must not pin the gateway. */
export const CREATE_EXTRACT_TIMEOUT_MS = 30_000

/** Hard response-size cap; a runaway page is rejected instead of buffered. */
export const CREATE_MAX_EXTRACT_BYTES = 10 * 1024 * 1024

/** Stored-text cap; longer prose is truncated and flagged to the caller. */
export const CREATE_MAX_EXTRACT_CHARS = 100_000

/** Declared fetcher identity of the create extraction face. */
const CREATE_EXTRACT_USER_AGENT = 'dsh-content-create/0.1 (dsh content studio create view)'

/** Injection face for tests: the fetch implementation defaults to the global one. */
export interface CreateExtractDeps {
  readonly fetchImpl?: typeof fetch
}

/** The fetch failure carries the HTTP status for caller-facing messages. */
export class CreateExtractHttpError extends Error {
  /** HTTP status of the failed response. */
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'CreateExtractHttpError'
    this.status = status
  }
}

/**
 * Fetch one article page and reduce it to title plus prose text.
 * @param url - the pasted article link; http/https only.
 * @param deps - test injection; defaults to the global fetch.
 * @param signal - caller cancellation.
 * @returns the resolved URL, the page title (empty when absent), and the
 * extracted prose with the truncation flag.
 */
export async function extractArticleCopy(
  url: string,
  deps: CreateExtractDeps,
  signal?: AbortSignal,
): Promise<{ url: string; title: string; text: string; truncated: boolean }> {
  let parsed: URL
  try {
    parsed = new URL(url)
  } catch {
    throw new Error(`create-extract: not a valid URL: ${url}`)
  }
  if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
    throw new Error(`create-extract: only http/https URLs are supported: ${parsed.protocol}`)
  }
  const timeout = AbortSignal.any([AbortSignal.timeout(CREATE_EXTRACT_TIMEOUT_MS), ...(signal ? [signal] : [])])
  const response = await (deps.fetchImpl ?? fetch)(parsed.href, {
    redirect: 'follow',
    signal: timeout,
    headers: { 'user-agent': CREATE_EXTRACT_USER_AGENT, accept: 'text/html,application/xhtml+xml' },
  })
  if (!response.ok) throw new CreateExtractHttpError(response.status, `create-extract: HTTP ${response.status} for ${parsed.href}`)
  const declared = Number(response.headers.get('content-length') ?? '0')
  if (Number.isFinite(declared) && declared > CREATE_MAX_EXTRACT_BYTES) {
    throw new Error(`create-extract: page exceeds the ${CREATE_MAX_EXTRACT_BYTES}-byte cap`)
  }
  const raw = await response.text()
  if (raw.length > CREATE_MAX_EXTRACT_BYTES) throw new Error(`create-extract: page exceeds the ${CREATE_MAX_EXTRACT_BYTES}-byte cap`)
  const title = /<title[^>]*>([\s\S]*?)<\/title>/i.exec(raw)?.[1]?.trim() ?? ''
  const text = htmlToText(toProseBlocks(sanitizeGatherHtml(raw)))
    .replace(/[ \t]+/g, ' ')
    .replace(/ ?\n ?/g, '\n')
    .replace(/\n{3,}/g, '\n\n')
    .trim()
  const truncated = text.length > CREATE_MAX_EXTRACT_CHARS
  return {
    url: response.url || parsed.href,
    title: decodeEntities(title).slice(0, 500),
    text: truncated ? text.slice(0, CREATE_MAX_EXTRACT_CHARS) : text,
    truncated,
  }
}

/**
 * Keep line structure before tag stripping: block-level elements become
 * hard newlines so paragraphs survive `htmlToText` as separate lines
 * instead of one glued blob.
 */
function toProseBlocks(html: string): string {
  return html
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<\/(p|div|h[1-6]|li|tr|blockquote|pre|section|article|figcaption)>/gi, '\n\n')
}

/** Decode the five named entities HTML guarantees in text content. */
function decodeEntities(text: string): string {
  return text
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, '\'')
}
