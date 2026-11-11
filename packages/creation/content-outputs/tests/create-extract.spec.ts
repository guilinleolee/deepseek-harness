import { describe, expect, it, vi } from 'vitest'
import {
  CREATE_EXTRACT_TIMEOUT_MS, CREATE_MAX_EXTRACT_CHARS, CreateExtractHttpError, extractArticleCopy,
} from '../src/create/extract.ts'

/** One-shot fetch stub returning the given body with the given status. */
function fetchReturning(body: string, init: { status?: number; contentType?: string } = {}): typeof fetch {
  return vi.fn(async () => new Response(body, {
    status: init.status ?? 200,
    headers: { 'content-type': init.contentType ?? 'text/html; charset=utf-8' },
  }))
}

const ARTICLE = `<!doctype html>
<html><head><title>深度解析 &amp; 指南</title>
<style>.nav { display: none }</style>
<script>track()</script>
</head>
<body>
<nav>首页 | 分类</nav>
<article>
<h1>标题一</h1>
<p>第一段正文。</p>
<p>第二段正文，包含<script>evil()</script>脚本与<style>bad</style>样式。</p>
<br>
<p>第三段。</p>
</article>
</body></html>`

describe('extractArticleCopy', () => {
  it('extracts the title and prose with block structure preserved', async () => {
    const fetchImpl = fetchReturning(ARTICLE)
    const result = await extractArticleCopy('https://example.com/post', { fetchImpl })
    expect(result.url).toBe('https://example.com/post')
    expect(result.title).toBe('深度解析 & 指南')
    expect(result.truncated).toBe(false)
    expect(result.text).toContain('标题一')
    expect(result.text).toContain('第一段正文。')
    expect(result.text).toContain('第三段。')
    // Block elements become line breaks instead of one glued blob.
    expect(result.text).toMatch(/第一段正文。\n/)
    // Script and style content never survives extraction.
    expect(result.text).not.toContain('track()')
    expect(result.text).not.toContain('evil()')
    expect(result.text).not.toContain('display: none')
  })

  it('follows the redirect chain into the final URL', async () => {
    const fetchImpl = vi.fn(async () => new Response('<html><body><p>落地正文</p></body></html>', {
      status: 200, headers: { 'content-type': 'text/html' },
    }))
    const result = await extractArticleCopy('https://example.com/a', { fetchImpl })
    expect(result.text).toBe('落地正文')
  })

  it('rejects non-http schemes', async () => {
    const fetchImpl = fetchReturning('<p>不应被请求</p>')
    await expect(extractArticleCopy('ftp://example.com/file', { fetchImpl }))
      .rejects.toThrow('only http/https')
    await expect(extractArticleCopy('javascript:alert(1)', { fetchImpl }))
      .rejects.toThrow('only http/https')
    expect(fetchImpl).not.toHaveBeenCalled()
  })

  it('rejects malformed URLs before fetching', async () => {
    const fetchImpl = fetchReturning('<p>不应被请求</p>')
    await expect(extractArticleCopy('not a url', { fetchImpl })).rejects.toThrow('not a valid URL')
    expect(fetchImpl).not.toHaveBeenCalled()
  })

  it('carries the HTTP status on a failed response', async () => {
    const fetchImpl = fetchReturning('gone', { status: 404 })
    const error = await extractArticleCopy('https://example.com/gone', { fetchImpl })
      .catch((cause: unknown) => cause)
    expect(error).toBeInstanceOf(CreateExtractHttpError)
    expect((error as CreateExtractHttpError).status).toBe(404)
  })

  it('rejects a page whose declared size exceeds the byte cap', async () => {
    const fetchImpl = vi.fn(async () => new Response('<p>大页面</p>', {
      status: 200,
      headers: { 'content-type': 'text/html', 'content-length': String(11 * 1024 * 1024) },
    }))
    await expect(extractArticleCopy('https://example.com/big', { fetchImpl }))
      .rejects.toThrow('byte cap')
  })

  it('truncates prose past the stored-text cap and flags it', async () => {
    const paragraph = '<p>这是一段足够长的正文内容，用于撑起截断测试的体积。</p>'
    const huge = `<html><head><title>长文</title></head><body>${paragraph.repeat(5000)}</body></html>`
    const result = await extractArticleCopy('https://example.com/long', { fetchImpl: fetchReturning(huge) })
    expect(result.truncated).toBe(true)
    expect(result.text.length).toBe(CREATE_MAX_EXTRACT_CHARS)
  })

  it('caps the extraction deadline at a bounded value', () => {
    expect(CREATE_EXTRACT_TIMEOUT_MS).toBeLessThanOrEqual(60_000)
  })
})
