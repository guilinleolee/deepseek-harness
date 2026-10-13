import { describe, expect, it } from 'vitest'
import {
  INTERACTION_REPLY_CANDIDATES, classifySystemPrompt, frameClassifyRequest, frameInsightRequest,
  frameReplyRequest, insightSystemPrompt, parseClassifyOutput, parseInsightOutput, parseReplyOutput,
  replySystemPrompt,
} from '../src/interactions/ai.ts'
import type { InteractionReplyRequest } from '../src/interactions/types.ts'

const replyRequest: InteractionReplyRequest = {
  style: 'friendly',
  personaDigest: '亲切的本店主，语气轻快',
  personaPhrases: ['宝子', '亲'],
  personaSamples: ['这条笔记超实用！'],
  template: '你好 {{nickname}}，感谢关注！',
  thread: [
    { direction: 'in', content: '笔记写得好棒' },
    { direction: 'out', content: '谢谢支持！' },
    { direction: 'in', content: '多少钱能买？' },
  ],
}

describe('reply framing and parsing', () => {
  it('embeds the persona block, the template skeleton, and the style', () => {
    const system = replySystemPrompt(replyRequest)
    expect(system).toContain('亲切的本店主')
    expect(system).toContain('宝子')
    expect(system).toContain('<模板>')
    expect(system).toContain('friendly')
    expect(system).toContain(`恰好 ${INTERACTION_REPLY_CANDIDATES} 条`)
  })

  it('omits the persona and template blocks when none are bound', () => {
    const system = replySystemPrompt({ ...replyRequest, personaDigest: null, personaPhrases: [], personaSamples: [], template: null })
    expect(system).not.toContain('绑定画像')
    expect(system).not.toContain('<模板>')
  })

  it('frames the thread with role labels and trims to the latest window', () => {
    const framed = frameReplyRequest({
      ...replyRequest,
      thread: Array.from({ length: 30 }, (_, index) => ({ direction: 'in' as const, content: `line ${index}` })),
    }, 100_000)
    expect(framed).not.toContain('line 5\n')
    expect(framed).toContain('line 29')
    expect(framed.endsWith('请为最后一条「粉丝」消息生成回复草稿。')).toBe(true)
  })

  it('rejects an empty thread', () => {
    expect(() => frameReplyRequest({ ...replyRequest, thread: [] }, 100_000)).toThrow(/non-empty thread/)
  })

  it('parses exactly three candidates and coerces unknown styles', () => {
    const output = JSON.stringify({
      drafts: [
        { style: 'friendly', content: 'a' },
        { style: 'poetic', content: 'b' },
        { style: 'brief', content: ' c ' },
      ],
    })
    const drafts = parseReplyOutput(output, 'friendly')
    expect(drafts).toHaveLength(INTERACTION_REPLY_CANDIDATES)
    expect(drafts[1]?.style).toBe('friendly')
    expect(drafts[2]?.content).toBe('c')
  })

  it('throws on a short or unparseable candidate set', () => {
    expect(() => parseReplyOutput(JSON.stringify({ drafts: [{ style: 'friendly', content: 'a' }] }), 'friendly'))
      .toThrow(/exactly 3/)
    expect(() => parseReplyOutput('no json here', 'friendly')).toThrow(/JSON/)
    expect(() => parseReplyOutput(JSON.stringify({ drafts: [{ style: 'friendly', content: ' ' }, { style: 'friendly', content: 'b' }, { style: 'friendly', content: 'c' }] }), 'friendly'))
      .toThrow(/empty content/)
  })
})

describe('classification framing and parsing', () => {
  it('frames the numbered batch', () => {
    const framed = frameClassifyRequest({ messages: [{ messageId: 'm1', content: '你好' }] }, 100_000)
    expect(framed).toContain('- m1：你好')
    expect(classifySystemPrompt()).toContain('sentiment')
  })

  it('keeps only known ids and coerces unknown values to unknown', () => {
    const output = JSON.stringify({
      entries: [
        { messageId: 'm1', sentiment: 'positive', intent: 'praise' },
        { messageId: 'ghost', sentiment: 'negative', intent: 'spam' },
        { messageId: 'm2', sentiment: 'terrible', intent: 'whatever' },
      ],
    })
    const entries = parseClassifyOutput(output, new Set(['m1', 'm2']))
    expect(entries).toEqual([
      { messageId: 'm1', sentiment: 'positive', intent: 'praise' },
      { messageId: 'm2', sentiment: 'unknown', intent: 'unknown' },
    ])
  })

  it('degrades a garbled batch to no entries', () => {
    expect(parseClassifyOutput('garbage', new Set(['m1']))).toEqual([])
  })
})

describe('insight framing and parsing', () => {
  it('frames the numbered batch and pins the three lists', () => {
    const framed = frameInsightRequest({ messages: [{ messageId: 'm1', content: '什么时候发货' }] }, 100_000)
    expect(framed).toContain('- m1：什么时候发货')
    const system = insightSystemPrompt()
    expect(system).toContain('questions')
    expect(system).toContain('painPoints')
    expect(system).toContain('interests')
  })

  it('sanitizes counts, labels, and drops unusable lines', () => {
    const output = JSON.stringify({
      questions: [
        { label: '发货时间', count: 7, exampleMessageId: 'm1', topicHint: null },
        { label: '', count: 3, exampleMessageId: null, topicHint: null },
        { label: '只剩这点', count: 0.5, exampleMessageId: null, topicHint: null },
      ],
      painPoints: 'not-an-array',
      interests: [{ label: '测评', count: 2, exampleMessageId: null, topicHint: '做一期开箱测评' }],
    })
    const batch = parseInsightOutput(output)
    expect(batch.questions).toEqual([{ label: '发货时间', count: 7, exampleMessageId: 'm1', topicHint: null }])
    expect(batch.painPoints).toEqual([])
    expect(batch.interests).toEqual([{ label: '测评', count: 2, exampleMessageId: null, topicHint: '做一期开箱测评' }])
  })

  it('degrades garbage to an empty batch', () => {
    expect(parseInsightOutput('nothing')).toEqual({ questions: [], painPoints: [], interests: [] })
  })
})
