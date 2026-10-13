import { describe, expect, it } from 'vitest'
import { htmlToText, sanitizeGatherHtml } from '../src/gather/sanitize.ts'
import {
  GATHER_AI_TIMEOUT_CODE, GatherAiProcessor, isRateLimitError, parseGatherAiOutput, retryAfterMs,
} from '../src/gather/ai.ts'

describe('sanitizeGatherHtml (allowlist)', () => {
  const MALICIOUS = [
    '<p>正文开头</p>',
    '<script>alert(1)</script>',
    '<iframe src="https://evil.example"></iframe>',
    '<a href="javascript:alert(2)">链接</a>',
    '<a href="data:text/html,<script>alert(3)</script>">data 链接</a>',
    '<img src="x" onerror="alert(4)">',
    '<svg><script>alert(5)</script></svg>',
    '<math><mtext><script>alert(6)</script></mtext></math>',
    '<style>body{background:url(javascript:alert(7))}</style>',
    '<form action="https://evil.example"><input></form>',
    '<object data="https://evil.example"></object>',
  ].join('')

  it('strips every scripted vector while keeping the prose and safe links', () => {
    const clean = sanitizeGatherHtml(MALICIOUS)
    expect(clean).toContain('正文开头')
    expect(clean.toLowerCase()).not.toContain('<script')
    expect(clean).not.toContain('iframe')
    expect(clean).not.toContain('javascript:')
    expect(clean).not.toContain('data:text/html')
    expect(clean).not.toContain('onerror')
    expect(clean).not.toContain('<svg')
    expect(clean).not.toContain('<math')
    expect(clean).not.toContain('<style')
    expect(clean).not.toContain('<form')
    expect(clean).not.toContain('<object')
  })

  it('keeps prose markup, adds safe link rel, and reduces text-only variants', () => {
    const clean = sanitizeGatherHtml('<h2 id="s">标题</h2><p>段落 <strong>强调</strong></p><a href="https://example.com">原文</a>')
    expect(clean).toContain('<h2 id="s">标题</h2>')
    expect(clean).toContain('<strong>强调</strong>')
    expect(clean).toContain('rel="noopener noreferrer"')
    expect(htmlToText('<p>只取文本</p><script>alert(1)</script>')).toBe('只取文本')
  })
})

describe('parseGatherAiOutput', () => {
  it('parses a plain and a fenced JSON answer', () => {
    const answer = JSON.stringify({ summary: '摘要', points: ['要点一'], score: 88, tags: ['AI'] })
    expect(parseGatherAiOutput(answer)).toEqual({ summary: '摘要', points: ['要点一'], score: 88, tags: ['AI'] })
    expect(parseGatherAiOutput('```json\n' + answer + '\n```')).toEqual({ summary: '摘要', points: ['要点一'], score: 88, tags: ['AI'] })
  })

  it('clamps oversized arrays and rounds the score', () => {
    const answer = JSON.stringify({
      summary: ' 摘要 ', points: ['一', '二', '三', '四', '五', '六', ''], score: 88.6, tags: Array.from({ length: 9 }, (_, i) => `t${i}`),
    })
    const parsed = parseGatherAiOutput(answer)
    expect(parsed.points).toEqual(['一', '二', '三', '四', '五', '六'])
    expect(parsed.score).toBe(89)
    expect(parsed.tags).toHaveLength(8)
  })

  it('rejects non-JSON, non-object, and invalid field answers', () => {
    expect(() => parseGatherAiOutput('抱歉，我无法处理')).toThrow('no JSON object')
    expect(() => parseGatherAiOutput('[1,2]')).toThrow()
    expect(() => parseGatherAiOutput(JSON.stringify({ points: [], score: 1, tags: [] }))).toThrow('no summary')
    expect(() => parseGatherAiOutput(JSON.stringify({ summary: 's', points: 'x', score: 1, tags: [] }))).toThrow('invalid points')
    expect(() => parseGatherAiOutput(JSON.stringify({ summary: 's', points: [], score: 101, tags: [] }))).toThrow('invalid score')
    expect(() => parseGatherAiOutput(JSON.stringify({ summary: 's', points: [], score: 1, tags: 3 }))).toThrow('invalid tags')
  })
})

describe('AI rate-limit helpers', () => {
  it('detects rate limits from LlmError names and plain codes', () => {
    const rateError = Object.assign(new Error('429'), { code: 'RATE_LIMIT' })
    expect(isRateLimitError(rateError)).toBe(true)
    expect(isRateLimitError(new Error('boom'))).toBe(false)
    expect(retryAfterMs(rateError)).toBeUndefined()
  })

  it('carries the timeout code and the AI policy validation', () => {
    expect(GATHER_AI_TIMEOUT_CODE).toBe('GATHER_AI_TIMEOUT')
    const ctx = {} as never
    expect(() => new GatherAiProcessor(ctx, { timeoutMs: 50 })).toThrow('aiTimeoutMs')
    expect(() => new GatherAiProcessor(ctx, { maxOutputTokens: 8 })).toThrow('aiMaxOutputTokens')
    expect(() => new GatherAiProcessor(ctx, { maxInputChars: 10 })).toThrow('aiMaxInputChars')
  })

  it('rejects unsupported operations before touching the queue', async () => {
    const processor = new GatherAiProcessor({} as never, {})
    await expect(processor.process({ operation: 'nope' } as never, async () => undefined))
      .rejects.toThrow('unsupported gather AI operation')
  })
})
