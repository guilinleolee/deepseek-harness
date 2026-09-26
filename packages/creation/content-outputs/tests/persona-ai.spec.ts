import { describe, expect, it, vi } from 'vitest'
import { streamLlmText } from '../src/gather/ai.ts'
import {
  PERSONA_AI_TIMEOUT_CODE, PERSONA_FILL_PROMPT_VERSION, PERSONA_REPORT_PROMPT_VERSION,
  PERSONA_RESUME_PROMPT_VERSION, PersonaAiProcessor, buildFactsText, parsePersonaFieldsOutput,
  parsePersonaReportOutput,
} from '../src/persona/ai.ts'
import type { PersonaEntry, PersonaFieldKey } from '../src/types.ts'
import { PERSONA_FIELD_KEYS } from '../src/persona/types.ts'

// The one-shot helper is the only external edge: mocked so every queued
// processor path runs without a model.
vi.mock('../src/gather/ai.ts', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../src/gather/ai.ts')>()
  return { ...actual, streamLlmText: vi.fn(async () => '') }
})

const streamMock = vi.mocked(streamLlmText)

const FILL_ANSWER = JSON.stringify({ audience: '25-40 岁职场人群', whoAmI: '不应出现', niche: '', extra: '丢弃' })

describe('parsePersonaFieldsOutput', () => {
  it('keeps only allowed keys, trims, and drops empty values', () => {
    const fields = parsePersonaFieldsOutput(FILL_ANSWER, ['audience', 'niche'])
    expect(fields).toEqual({ audience: '25-40 岁职场人群' })
  })

  it('caps one value at 2000 characters and rejects non-JSON output', () => {
    const long = parsePersonaFieldsOutput(JSON.stringify({ goal: '长'.repeat(3000) }), ['goal'])
    expect(long.goal).toHaveLength(2000)
    expect(() => parsePersonaFieldsOutput('抱歉', ['goal'])).toThrow('no JSON object')
    expect(() => parsePersonaFieldsOutput('[1]', ['goal'])).toThrow('not a JSON object')
    expect(() => parsePersonaFieldsOutput('[]', ['goal'])).toThrow('not a JSON object')
  })
})

describe('parsePersonaReportOutput', () => {
  it('strips fences and returns the markdown body', () => {
    expect(parsePersonaReportOutput('```markdown\n# 报告\n正文\n```')).toBe('# 报告\n正文')
    expect(() => parsePersonaReportOutput('   ')).toThrow('empty')
  })
})

describe('buildFactsText', () => {
  const entry: PersonaEntry = {
    id: 'p-1' as PersonaEntry['id'],
    name: '老李',
    platforms: ['xhs', 'douyin'],
    accountStage: 'fresh',
    revision: 4,
    digest: '老李（v4）',
    fields: {
      whoAmI: { value: '前大厂工程师', source: 'user', aiMeta: null },
      audience: { value: '25-40 岁职场人群', source: 'ai', aiMeta: { promptVersion: PERSONA_FILL_PROMPT_VERSION, at: '2026-09-25T00:00:00.000Z' } },
      oneLiner: { value: null, source: 'user', aiMeta: null },
      niche: { value: null, source: 'user', aiMeta: null },
      goal: { value: null, source: 'user', aiMeta: null },
      monetize: { value: null, source: 'user', aiMeta: null },
      contentValue: { value: null, source: 'user', aiMeta: null },
      cadence: { value: null, source: 'user', aiMeta: null },
      phrases: { value: null, source: 'user', aiMeta: null },
    },
    links: [{ platform: 'xhs', url: 'https://xhs.example/laoli', bio: '简介', sampleText: null }],
    site: { url: null, pastedText: '官网内容' },
    style: { preset: 'humor', customText: null, strength: 'strict', bannedWords: ['最好'], redLines: [] },
    assets: { resumeText: '简历文本', resumeName: null },
    report: null,
    clonedFrom: null,
    createdAt: '2026-09-25T00:00:00.000Z',
    updatedAt: '2026-09-25T00:00:00.000Z',
  }

  it('renders facts with platform labels and the AI provenance mark', () => {
    const facts = buildFactsText(entry)
    expect(facts).toContain('画像名：老李')
    expect(facts).toContain('小红书、抖音')
    expect(facts).toContain('全新起号')
    expect(facts).toContain('前大厂工程师')
    expect(facts).toContain('25-40 岁职场人群（AI 推断，供参考）')
    expect(facts).toContain('幽默网感（遵循强度：严格遵循）')
    expect(facts).toContain('禁用词：最好')
    expect(facts).toContain('内容红线：无')
    expect(facts).toContain('企业官网信息：官网内容')
    expect(facts).toContain('社媒链接（小红书）：https://xhs.example/laoli；简介')
    expect(facts).toContain('简历/背景文本：简历文本')
  })

  it('renders the empty-style fallback', () => {
    const facts = buildFactsText({ ...entry, style: { preset: null, customText: null, strength: 'light', bannedWords: [], redLines: ['不聊竞品'] }, links: [] })
    expect(facts).toContain('写作风格：未填写（遵循强度：轻度遵循）')
    expect(facts).toContain('内容红线：不聊竞品')
    expect(facts).not.toContain('社媒链接')
  })
})

describe('PersonaAiProcessor', () => {
  it('carries the timeout code and validates the AI policy at construction', () => {
    expect(PERSONA_AI_TIMEOUT_CODE).toBe('PERSONA_AI_TIMEOUT')
    expect(() => new PersonaAiProcessor({} as never, { timeoutMs: 50 })).toThrow('aiTimeoutMs')
    expect(() => new PersonaAiProcessor({} as never, { maxOutputTokens: 8 })).toThrow('aiMaxOutputTokens')
  })

  it('rejects unsupported operations before touching the queue', async () => {
    const processor = new PersonaAiProcessor({} as never, {})
    await expect(processor.process({ operation: 'nope' } as never)).rejects.toThrow('unsupported persona AI operation')
  })

  it('fills only the requested blank fields and stamps the fill prompt version', async () => {
    streamMock.mockResolvedValue(FILL_ANSWER)
    const processor = new PersonaAiProcessor({} as never, {})
    const result = await processor.process({
      operation: 'fill',
      known: { whoAmI: '前大厂工程师' },
      blanks: ['audience', 'whoAmI'],
    })
    expect(result.operation).toBe('fill')
    if (result.operation !== 'fill') return
    expect(result.promptVersion).toBe(PERSONA_FILL_PROMPT_VERSION)
    expect(Object.keys(result.fields)).toEqual(['audience'])
    expect(streamMock).toHaveBeenCalledWith(
      expect.anything(), expect.objectContaining({ provider: 'deepseek' }), expect.stringContaining('画像助手'),
      expect.stringContaining('前大厂工程师'), PERSONA_AI_TIMEOUT_CODE,
    )
  })

  it('refuses a fill with no fillable blanks and an empty résumé', async () => {
    const processor = new PersonaAiProcessor({} as never, {})
    await expect(processor.process({ operation: 'fill', known: {}, blanks: ['whoAmI'] })).rejects.toThrow('no fillable blank fields')
    await expect(processor.process({ operation: 'resume', resumeText: '   ' })).rejects.toThrow('no text to extract')
  })

  it('extracts résumé fields with the résumé prompt version', async () => {
    streamMock.mockResolvedValue(JSON.stringify({ whoAmI: '十年后端工程师', niche: 'AI 工具' }))
    const processor = new PersonaAiProcessor({} as never, {})
    const result = await processor.process({ operation: 'resume', resumeText: '简历正文' })
    expect(result.operation).toBe('resume')
    if (result.operation !== 'resume') return
    expect(result.promptVersion).toBe(PERSONA_RESUME_PROMPT_VERSION)
    expect(result.fields.whoAmI).toBe('十年后端工程师')
    expect(result.fields.niche).toBe('AI 工具')
  })

  it('generates the report markdown with the report prompt version', async () => {
    streamMock.mockResolvedValue('```markdown\n# 账号画像报告\n正文\n```')
    const processor = new PersonaAiProcessor({} as never, {})
    const result = await processor.process({ operation: 'report', facts: reportFacts() })
    expect(result.operation).toBe('report')
    if (result.operation !== 'report') return
    expect(result.promptVersion).toBe(PERSONA_REPORT_PROMPT_VERSION)
    expect(result.markdown).toContain('# 账号画像报告')
  })

  it('retries a rate-limited call and then succeeds', async () => {
    let calls = 0
    streamMock.mockImplementation(async () => {
      calls += 1
      if (calls === 1) throw Object.assign(new Error('429'), { code: 'RATE_LIMIT' })
      return '# 报告'
    })
    const processor = new PersonaAiProcessor({} as never, {})
    const result = await processor.process({ operation: 'report', facts: reportFacts() })
    expect(result.operation).toBe('report')
    expect(calls).toBe(2)
  })
})

/** A minimal saved entry for the report face. */
function reportFacts(): PersonaEntry {
  const fields = {} as Record<PersonaFieldKey, PersonaEntry['fields'][PersonaFieldKey]>
  for (const key of PERSONA_FIELD_KEYS) fields[key] = { value: null, source: 'user', aiMeta: null }
  return {
    id: 'p-1' as PersonaEntry['id'], name: '老李', platforms: [], accountStage: 'fresh', revision: 2, digest: '老李（v2）',
    fields, links: [], site: { url: null, pastedText: null },
    style: { preset: null, customText: null, strength: 'light', bannedWords: [], redLines: [] },
    assets: { resumeText: null, resumeName: null }, report: null, clonedFrom: null,
    createdAt: '2026-09-25T00:00:00.000Z', updatedAt: '2026-09-25T00:00:00.000Z',
  }
}
