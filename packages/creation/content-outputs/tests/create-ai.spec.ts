import { describe, expect, it } from 'vitest'
import {
  CREATE_PROMPT_VERSION, CreateAiProcessor, evaluateSystemPrompt, fillCustomTemplate,
  frameGenerateRequest, generateFramedPrompt, generateSystemPrompt, parseCreateEvaluation,
  parseCreateVariants, rewriteSystemPrompt, validateEvaluateRequest, validateRewriteRequest,
} from '../src/create/ai.ts'
import type { CreateEvaluateRequest, CreateGenerateRequest } from '../src/types.ts'

const POLICY = { provider: 'p', model: 'm', timeoutMs: 1000, maxOutputTokens: 256, maxInputChars: 1000 }

function generateRequest(overrides: Partial<CreateGenerateRequest> = {}): CreateGenerateRequest {
  return {
    contentType: 'gzh-article', title: '标题', audience: '职场人群', points: '要点', references: '素材', profileDigest: '专业但亲切',
    ...overrides,
  }
}

describe('create generation prompts', () => {
  it('frames identity facts, audience, points, references, and the style digest', () => {
    expect(generateFramedPrompt(generateRequest())).toContain('主题：标题')
    expect(generateFramedPrompt(generateRequest())).toContain('目标人群：职场人群')
    expect(generateFramedPrompt(generateRequest({ audience: null, points: null, references: null }))).toBe('主题：标题')
    const system = generateSystemPrompt(generateRequest())
    expect(system).toContain('公众号文章')
    expect(system).toContain('专业但亲切')
    expect(generateSystemPrompt(generateRequest({ profileDigest: null }))).not.toContain('写作风格要求')
  })

  it('switches the brief per content type', () => {
    expect(generateSystemPrompt(generateRequest({ contentType: 'voiceover' }))).toContain('口播稿')
    expect(generateSystemPrompt(generateRequest({ contentType: 'xhs-note' }))).toContain('小红书')
    expect(generateSystemPrompt(generateRequest({ contentType: 'video-script' }))).toContain('短视频脚本')
    expect(generateSystemPrompt(generateRequest({ contentType: 'product-page' }))).toContain('商品详情')
    expect(generateSystemPrompt(generateRequest({ contentType: 'rewrite' }))).toContain('二创')
  })

  it('validates the request before framing', () => {
    expect(() => frameGenerateRequest(generateRequest({ contentType: 'poem' as never }), 1000)).toThrow('contentType')
    expect(() => frameGenerateRequest(generateRequest({ title: '  ' }), 1000)).toThrow('non-empty title')
    expect(() => frameGenerateRequest(generateRequest({ title: 'x'.repeat(201) }), 1000)).toThrow('200 characters')
    expect(frameGenerateRequest(generateRequest(), 20).length).toBeLessThanOrEqual(20)
  })
})

describe('create rewrite prompts', () => {
  it('maps each operation to its brief and the style label', () => {
    expect(rewriteSystemPrompt({ operation: 'condense', style: null, text: 'x' })).toContain('压缩')
    expect(rewriteSystemPrompt({ operation: 'expand', style: null, text: 'x' })).toContain('扩写')
    expect(rewriteSystemPrompt({ operation: 'style', style: 'story', text: 'x' })).toContain('故事化')
    expect(rewriteSystemPrompt({ operation: 'perspective', style: null, text: 'x' })).toContain('视角')
    expect(rewriteSystemPrompt({ operation: 'extract', style: null, text: 'x' })).toContain('金句')
  })

  it('validates the operation, the style requirement, and the selection text', () => {
    expect(() => validateRewriteRequest({ operation: 'vibes' as never, style: null, text: 'x' }, 1000)).toThrow('operation')
    expect(() => validateRewriteRequest({ operation: 'style', style: null, text: 'x' }, 1000)).toThrow('style key')
    expect(() => validateRewriteRequest({ operation: 'style', style: 'nope' as never, text: 'x' }, 1000)).toThrow('style key')
    expect(() => validateRewriteRequest({ operation: 'condense', style: null, text: '  \n' }, 1000)).toThrow('empty')
    expect(() => validateRewriteRequest({ operation: 'condense', style: null, text: 'x'.repeat(1001) }, 1000)).toThrow('cap')
    expect(validateRewriteRequest({ operation: 'condense', style: null, text: ' 正文 ' }, 1000)).toBe(' 正文 ')
  })

  it('briefs the humanize tiers and the title batch', () => {
    expect(rewriteSystemPrompt({ operation: 'humanize-light', style: null, text: 'x' })).toContain('轻度去 AI 味')
    expect(rewriteSystemPrompt({ operation: 'humanize-light', style: null, text: 'x' })).toContain('±10%')
    expect(rewriteSystemPrompt({ operation: 'humanize-deep', style: null, text: 'x' })).toContain('深度去 AI 味')
    expect(rewriteSystemPrompt({ operation: 'titles', style: null, text: 'x' })).toContain('5 个备选标题')
  })
})

describe('fillCustomTemplate', () => {
  const request: CreateGenerateRequest = {
    contentType: 'gzh-article', title: '标题', audience: '职场', points: '要点', references: '素材', profileDigest: '亲切',
  }

  it('fills the whitelisted placeholders from the request', () => {
    const filled = fillCustomTemplate('写{{title}}，给{{audience}}，讲{{points}}，参考{{references}}，风格{{profile}}。', request)
    expect(filled).toBe('写标题，给职场，讲要点，参考素材，风格亲切。')
  })

  it('rejects the run when an unknown placeholder survives the fill', () => {
    expect(() => fillCustomTemplate('写{{title}}和{{mystery}}。', request)).toThrow('unknown placeholder {{mystery}}')
  })

  it('fills missing context facts with empty strings', () => {
    expect(fillCustomTemplate('A{{audience}}B', { ...request, audience: null })).toBe('AB')
  })
})

describe('create variant batches', () => {
  it('parses the fenced JSON answer into exactly the requested variants', () => {
    const answer = JSON.stringify({ variants: ['方案一', '方案二', '方案三'] })
    expect(parseCreateVariants(answer, 3)).toEqual(['方案一', '方案二', '方案三'])
    expect(parseCreateVariants('```json\n' + answer + '\n```', 3)).toHaveLength(3)
  })

  it('rejects non-JSON, wrong counts, and empty variants', () => {
    expect(() => parseCreateVariants('抱歉', 3)).toThrow('no JSON object')
    expect(() => parseCreateVariants(JSON.stringify({ variants: ['只有一套'] }), 3)).toThrow('exactly 3')
    expect(() => parseCreateVariants(JSON.stringify({ variants: ['一', '', '三'] }), 3)).toThrow('exactly 3')
    expect(() => parseCreateVariants(JSON.stringify({ nope: [] }), 3)).toThrow('exactly 3')
  })
})

describe('create evaluation', () => {
  const request: CreateEvaluateRequest = { contentType: 'gzh-article', title: '标题', text: '正文' }

  it('frames the rubric and the JSON contract', () => {
    const system = evaluateSystemPrompt(request)
    expect(system).toContain('吸引力')
    expect(system).toContain('人群匹配')
    expect(system).toContain('{"attraction"')
  })

  it('validates the request bounds', () => {
    expect(() => validateEvaluateRequest({ ...request, contentType: 'poem' as never }, 1000)).toThrow('contentType')
    expect(() => validateEvaluateRequest({ ...request, title: ' ' }, 1000)).toThrow('non-empty title')
    expect(() => validateEvaluateRequest({ ...request, text: ' ' }, 1000)).toThrow('empty')
    expect(() => validateEvaluateRequest({ ...request, text: 'x'.repeat(1001) }, 1000)).toThrow('cap')
  })

  it('parses a full four-dimension answer with provenance', () => {
    const dim = { grade: '良', reason: '依据' }
    const answer = JSON.stringify({ attraction: dim, readability: dim, differentiation: dim, audienceFit: dim, grade: '良' })
    const evaluation = parseCreateEvaluation(answer, 'deepseek-chat')
    expect(evaluation.grade).toBe('良')
    expect(evaluation.model).toBe('deepseek-chat')
    expect(evaluation.promptVersion).toBe(CREATE_PROMPT_VERSION)
    expect(evaluation.attraction).toEqual({ grade: '良', reason: '依据' })
    expect(evaluation.evaluatedAt.length).toBeGreaterThan(0)
  })

  it('rejects broken JSON, unknown grades, and empty reasons', () => {
    expect(() => parseCreateEvaluation('不行', 'm')).toThrow('no JSON object')
    const dim = { grade: '神', reason: '依据' }
    expect(() => parseCreateEvaluation(JSON.stringify({ attraction: dim, readability: dim, differentiation: dim, audienceFit: dim, grade: '良' }), 'm'))
      .toThrow('invalid attraction')
    const emptyReason = { grade: '良', reason: ' ' }
    expect(() => parseCreateEvaluation(JSON.stringify({ attraction: emptyReason, readability: dim, differentiation: dim, audienceFit: dim, grade: '良' }), 'm'))
      .toThrow('invalid attraction')
    const good = { grade: '优', reason: '依据' }
    expect(() => parseCreateEvaluation(JSON.stringify({ attraction: good, readability: good, differentiation: good, audienceFit: good, grade: '神' }), 'm'))
      .toThrow('invalid overall grade')
  })
})

describe('CreateAiProcessor', () => {
  it('pins the prompt version and the shared timeout code', () => {
    expect(CREATE_PROMPT_VERSION).toBe(1)
  })

  it('rejects invalid requests before touching the queue', async () => {
    const processor = new CreateAiProcessor({} as never, POLICY)
    await expect(processor.generate(generateRequest({ title: '' }))).rejects.toThrow('non-empty title')
    await expect(processor.rewrite({ operation: 'nope' as never, style: null, text: 'x' })).rejects.toThrow('operation')
  })
})
