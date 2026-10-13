// @vitest-environment jsdom
import { describe, expect, it } from 'vitest'
// Gateway-side tables are value imports here: the client tests run in Node,
// where they pin the bundle's mirrored copies (the purity gate only binds
// the shipped bundle, not the tests).
import {
  INTERACTION_MESSAGE_TYPES, INTERACTION_PLATFORMS, INTERACTION_STYLES,
  type InteractionConversation,
} from '@deepseek-ai/dsh-content-outputs/types'
import {
  INTERACTION_PLATFORM_IDS,
  INTERACTION_STYLE_IDS, INTERACTION_TYPE_IDS, batchIds, defaultInteractionFilters,
  filterConversations, insightToTopicInput, loadInteractionFilters, mergeInsightBatch,
  mergeInsightList, saveInteractionFilters, threadLines,
} from '../src/client/interaction/interaction-model.ts'

function conversation(overrides: Partial<InteractionConversation> = {}): InteractionConversation {
  return {
    id: 'conv-1',
    platform: 'xhs',
    participant: { externalUserId: 'u1', nickname: '阿芳' },
    topicRef: null,
    outputRef: null,
    personaId: null,
    status: 'unread',
    tags: [],
    note: '',
    starred: false,
    createdAt: '2026-09-28T00:00:00.000Z',
    updatedAt: '2026-09-28T00:00:00.000Z',
    messages: [{
      id: 'm1',
      externalMessageId: 'e1',
      direction: 'in',
      type: 'comment',
      content: '多少钱',
      inReplyTo: null,
      sentAt: '2026-09-28T01:00:00.000Z',
      sentiment: { value: 'unknown', source: 'user', aiMeta: null },
      intent: { value: 'unknown', source: 'user', aiMeta: null },
      replyDrafts: [],
    }],
    ...overrides,
  }
}

describe('enum table parity with the gateway', () => {
  it('mirrors the gateway tables exactly', () => {
    expect(INTERACTION_PLATFORM_IDS).toEqual(INTERACTION_PLATFORMS)
    expect(INTERACTION_TYPE_IDS).toEqual(INTERACTION_MESSAGE_TYPES)
    expect(INTERACTION_STYLE_IDS).toEqual(INTERACTION_STYLES)
  })
})

describe('filter persistence', () => {
  it('defaults whole on a version mismatch', () => {
    localStorage.setItem('dsh-content-studio.interaction.filters', JSON.stringify({ version: 99, platforms: ['xhs'] }))
    expect(loadInteractionFilters()).toEqual(defaultInteractionFilters())
  })

  it('round-trips a saved set and drops unknown enum values', () => {
    saveInteractionFilters({ ...defaultInteractionFilters(), platforms: ['xhs', 'tiktok' as never], status: 'replied', search: '包邮' })
    const loaded = loadInteractionFilters()
    expect(loaded.platforms).toEqual(['xhs'])
    expect(loaded.status).toBe('replied')
    expect(loaded.search).toBe('包邮')
  })
})

describe('filterConversations', () => {
  const list = [
    conversation(),
    conversation({ id: 'c2', platform: 'douyin', status: 'archived', participant: { externalUserId: 'u2', nickname: '' } }),
    conversation({
      id: 'c3', status: 'replied', tags: ['产品咨询'],
      participant: { externalUserId: 'u3', nickname: '小明' },
      messages: [{
        id: 'm9', externalMessageId: 'e9', direction: 'in', type: 'dm', content: '专属优惠有吗',
        inReplyTo: null, sentAt: '2026-09-28T02:00:00.000Z',
        sentiment: { value: 'question', source: 'ai', aiMeta: { promptVersion: 'interaction-sentiment@1', at: '2026-09-28T03:00:00.000Z' } },
        intent: { value: 'consult', source: 'ai', aiMeta: { promptVersion: 'interaction-sentiment@1', at: '2026-09-28T03:00:00.000Z' } },
        replyDrafts: [],
      }],
    }),
  ]

  it('filters by platform, status, tags-carrying messages, and search', () => {
    expect(filterConversations(list, { ...defaultInteractionFilters() })).toHaveLength(3)
    expect(filterConversations(list, { ...defaultInteractionFilters(), platforms: ['xhs'] }).map(entry => entry.id)).toEqual(['conv-1', 'c3'])
    expect(filterConversations(list, { ...defaultInteractionFilters(), status: 'archived' }).map(entry => entry.id)).toEqual(['c2'])
    expect(filterConversations(list, { ...defaultInteractionFilters(), type: 'dm' }).map(entry => entry.id)).toEqual(['c3'])
    expect(filterConversations(list, { ...defaultInteractionFilters(), sentiment: 'question' }).map(entry => entry.id)).toEqual(['c3'])
    expect(filterConversations(list, { ...defaultInteractionFilters(), search: '阿芳' }).map(entry => entry.id)).toEqual(['conv-1'])
    expect(filterConversations(list, { ...defaultInteractionFilters(), search: '专属' }).map(entry => entry.id)).toEqual(['c3'])
  })
})

describe('thread projection and batch slicing', () => {
  it('projects role lines trimmed to the trailing window', () => {
    const many = conversation({
      messages: Array.from({ length: 25 }, (_, index) => ({
        id: `m${index}`, externalMessageId: `e${index}`, direction: index % 2 === 0 ? 'in' as const : 'out' as const,
        type: 'comment' as const, content: `line ${index}`, inReplyTo: null,
        sentAt: `2026-09-28T00:${String(index).padStart(2, '0')}:00.000Z`,
        sentiment: { value: 'unknown' as const, source: 'user' as const, aiMeta: null },
        intent: { value: 'unknown' as const, source: 'user' as const, aiMeta: null },
        replyDrafts: [],
      })),
    })
    const lines = threadLines(many, 20)
    expect(lines).toHaveLength(20)
    expect(lines[0]?.content).toBe('line 5')
    // Index 24 is even, so the trailing line is a fan message.
    expect(lines[19]?.direction).toBe('in')
    expect(lines[18]?.direction).toBe('out')
  })

  it('slices ids into batches with a short tail', () => {
    expect(batchIds(['a', 'b', 'c'], 2)).toEqual([['a', 'b'], ['c']])
    expect(batchIds([], 50)).toEqual([])
  })
})

describe('insight merging', () => {
  it('sums same-label counts across batches and caps at five lines', () => {
    const first = mergeInsightList([], [
      { label: '发货', count: 3, exampleMessageId: 'm1', topicHint: null },
      { label: '价格', count: 1, exampleMessageId: 'm2', topicHint: null },
    ])
    const second = mergeInsightList(first, [
      { label: '发货', count: 2, exampleMessageId: 'm9', topicHint: null },
    ])
    expect(second).toEqual([
      { label: '发货', count: 5, exampleMessageId: 'm1', topicHint: null },
      { label: '价格', count: 1, exampleMessageId: 'm2', topicHint: null },
    ])
    const flooded = mergeInsightList(
      Array.from({ length: 6 }, (_, index) => ({ label: `l${index}`, count: 1, exampleMessageId: null, topicHint: null })),
      [],
    )
    expect(flooded).toHaveLength(5)
  })

  it('merges one batch into the whole record without touching generatedAt', () => {
    const merged = mergeInsightBatch(
      { generatedAt: '2026-09-27T00:00:00.000Z', topQuestions: [], painPoints: [], interests: [] },
      { questions: [{ label: 'q', count: 1, exampleMessageId: null, topicHint: null }], painPoints: [], interests: [] },
    )
    expect(merged.generatedAt).toBe('2026-09-27T00:00:00.000Z')
    expect(merged.topQuestions).toHaveLength(1)
  })
})

describe('insightToTopicInput', () => {
  it('builds an interaction-sourced idea anchored to the conversation', () => {
    const input = insightToTopicInput('开箱测评', '做一期开箱测评', 'conv-9', '做一期开箱测评', '2026-09-28T00:00:00.000Z')
    expect(input.status).toBe('idea')
    expect(input.source).toEqual({
      type: 'interaction', refId: 'conv-9', url: null,
      snapshot: { title: '开箱测评', summary: '做一期开箱测评', capturedAt: '2026-09-28T00:00:00.000Z' },
    })
    expect(input.tags).toEqual(['互动'])
  })
})
