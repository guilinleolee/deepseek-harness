import { describe, expect, it } from 'vitest'
import {
  PersonaSiteHttpError, PERSONA_SITE_MAX_BYTES, fetchSiteText, normalizeSiteUrl,
} from '../src/persona/site.ts'

describe('normalizeSiteUrl', () => {
  it('prefixes https on scheme-less input and keeps absolute http(s) URLs', () => {
    expect(normalizeSiteUrl(' example.com/blog ')).toBe('https://example.com/blog')
    expect(normalizeSiteUrl('http://example.com')).toBe('http://example.com/')
    expect(normalizeSiteUrl('https://example.com')).toBe('https://example.com/')
  })

  it('rejects every non-http(s) scheme before a request is built', () => {
    expect(() => normalizeSiteUrl('file:///etc/passwd')).toThrow('must be http(s)')
    expect(() => normalizeSiteUrl('javascript:alert(1)')).toThrow()
    expect(() => normalizeSiteUrl('data:text/html,hi')).toThrow()
    expect(() => normalizeSiteUrl('not a url ??')).toThrow()
  })
})

describe('fetchSiteText', () => {
  /** A minimal Response-like body since the injected fetch never hits the network. */
  const response = (body: string, status = 200): Response => new Response(body, { status })

  it('fetches the normalized url and reduces the page to visible text', async () => {
    let seenUrl: string | undefined
    let seenUserAgent: string | undefined
    const fetchImpl: typeof fetch = async (input, init) => {
      seenUrl = typeof input === 'string' ? input : input instanceof URL ? input.toString() : input.url
      seenUserAgent = new Headers(init?.headers).get('user-agent') ?? undefined
      return response('<html><head><script>evil()</script><title>t</title></head><body><p>你好</p><style>.x{}</style><p>世界</p></body></html>')
    }
    const text = await fetchSiteText('example.com', { fetchImpl })
    expect(seenUrl).toBe('https://example.com/')
    expect(seenUserAgent).toContain('dsh-content-persona')
    expect(text).toBe('你好世界')
  })

  it('carries the HTTP status on failures and rejects oversized pages', async () => {
    const failing: typeof fetch = async () => response('nope', 403)
    await expect(fetchSiteText('https://example.com', { fetchImpl: failing }))
      .rejects.toMatchObject({ name: 'PersonaSiteHttpError', status: 403 })
    expect(new PersonaSiteHttpError(500, 'https://x').status).toBe(500)

    const huge: typeof fetch = async () => response('x'.repeat(PERSONA_SITE_MAX_BYTES + 1))
    await expect(fetchSiteText('https://example.com', { fetchImpl: huge }))
      .rejects.toMatchObject({ status: 413 })
  })

  it('returns empty text for a page without visible content', async () => {
    const blank: typeof fetch = async () => response('<html><body><script>only()</script></body></html>')
    await expect(fetchSiteText('https://example.com', { fetchImpl: blank })).resolves.toBe('')
  })
})
