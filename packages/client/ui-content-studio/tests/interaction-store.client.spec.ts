// @vitest-environment jsdom
import { beforeEach, describe, expect, it } from 'vitest'
import { createInteractionController, type InteractionGateway } from '../src/client/interaction/interaction-store.ts'
import {
  EMPTY_INTERACTION_INSIGHTS, EMPTY_INTERACTION_SUMMARY,
  type InteractionsManifest,
} from '@deepseek-ai/dsh-content-outputs/types'

/** One well-formed manifest with one unread xhs conversation. */
function manifest(): InteractionsManifest {
  return {
    formatVersion: 0,
    conversations: [{
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
    }],
    insights: { ...EMPTY_INTERACTION_INSIGHTS },
    summary: { ...EMPTY_INTERACTION_SUMMARY, unread: 1 },
  }
}

/** A gateway stub whose write face echoes the recompute the real store does. */
function fakeGateway(overrides: Partial<InteractionGateway> = {}): { gateway: InteractionGateway; writes: InteractionsManifest[] } {
  const writes: InteractionsManifest[] = []
  const gateway: InteractionGateway = {
    readInteractions: async () => ({ manifest: manifest(), problems: [] }),
    writeInteractions: async (next) => {
      writes.push(next)
      return next
    },
    parseInteractionImport: async request => ({
      fileName: request.fileName, messages: [], rejected: [], totalRows: 0,
    }),
    commitInteractionImport: async () => ({ added: 2, updated: 0, conversationsCreated: 1, threadWarnings: [] }),
    generateInteractionReply: async () => ({
      drafts: [
        { style: 'friendly', content: '草稿一' },
        { style: 'friendly', content: '草稿二' },
        { style: 'friendly', content: '草稿三' },
      ],
      model: 'test-model',
      promptVersion: 'interaction-reply@1',
    }),
    classifyInteractions: async request => ({
      entries: request.messages.map(message => ({
        messageId: message.messageId,
        sentiment: 'positive' as const,
        intent: 'praise' as const,
      })),
      promptVersion: 'interaction-sentiment@1',
    }),
    extractInteractionInsights: async () => ({
      batch: {
        questions: [{ label: '价格', count: 1, exampleMessageId: 'm1', topicHint: null }],
        painPoints: [],
        interests: [{ label: '测评', count: 1, exampleMessageId: null, topicHint: '开箱' }],
      },
      promptVersion: 'interaction-insight@1',
    }),
    exportInteractionCsv: async () => ({ text: 'csv' }),
    sendInteractionReply: async () => ({ ok: false, reason: 'MCP_NOT_CONFIGURED' as const }),
    ...overrides,
  }
  return { gateway, writes }
}

async function booted(overrides: Partial<InteractionGateway> = {}): Promise<{
  controller: ReturnType<typeof createInteractionController>
  writes: InteractionsManifest[]
  topics: { puts: unknown[] }
  exports: Array<{ theme: string; file: string; content: string }>
}> {
  const { gateway, writes } = fakeGateway(overrides)
  const topics = { puts: [] as unknown[] }
  const exports: Array<{ theme: string; file: string; content: string }> = []
  const controller = createInteractionController(
    gateway,
    { put: async (input) => { topics.puts.push(input) } },
    async (theme, file, content) => { exports.push({ theme, file, content }) },
  )
  await controller.load()
  return { controller, writes, topics, exports }
}

beforeEach(() => {
  localStorage.clear()
})

describe('load', () => {
  it('boots the manifest and the summary', async () => {
    const { controller } = await booted()
    expect(controller.getState().manifest?.summary.unread).toBe(1)
    expect(controller.getState().problems).toEqual([])
  })

  it('surfaces a read failure as a notice instead of a throw', async () => {
    const { controller } = await booted({ readInteractions: async () => { throw new Error('down') } })
    await controller.load()
    expect(controller.getState().notice).toBe('load-failed')
  })
})

describe('conversation patches', () => {
  it('persists status, tags, note, star, and persona binding', async () => {
    const { controller, writes } = await booted()
    await controller.patchConversation('conv-1', { status: 'replied', tags: ['产品咨询'], note: '已报价', starred: true, personaId: 'p1' })
    expect(writes).toHaveLength(1)
    const stored = controller.getState().manifest?.conversations[0]
    expect(stored).toMatchObject({ status: 'replied', tags: ['产品咨询'], note: '已报价', starred: true, personaId: 'p1' })
  })

  it('keeps the old manifest and notices on a write failure', async () => {
    const { gateway } = fakeGateway()
    const controller = createInteractionController(
      {
        ...gateway,
        writeInteractions: async () => { throw new Error('disk full') },
      },
      { put: async () => undefined },
      async () => undefined,
    )
    await controller.load()
    await controller.patchConversation('conv-1', { starred: true })
    expect(controller.getState().notice).toBe('save-failed')
    expect(controller.getState().manifest?.conversations[0]?.starred).toBe(false)
  })
})

describe('reply drafts and send', () => {
  it('generates the candidate set onto the target message', async () => {
    const { controller } = await booted()
    await controller.generateDrafts('conv-1', 'm1', 'friendly', null, null)
    const drafts = controller.getState().manifest?.conversations[0]?.messages[0]?.replyDrafts
    expect(drafts).toHaveLength(3)
    expect(drafts?.every(draft => draft.style === 'friendly')).toBe(true)
    expect(controller.getState().notice).toBe('drafts-ready')
  })

  it('archives the reply, flips the status to replied, and knocks the refused channel', async () => {
    let knocks = 0
    const { controller } = await booted({
      sendInteractionReply: async () => {
        knocks += 1
        return { ok: false, reason: 'MCP_NOT_CONFIGURED' as const }
      },
    })
    await controller.sendReply('conv-1', 'm1', '亲，48 元包邮', null)
    const stored = controller.getState().manifest?.conversations[0]
    expect(stored?.status).toBe('replied')
    const out = stored?.messages.find(message => message.direction === 'out')
    expect(out?.content).toBe('亲，48 元包邮')
    expect(out?.inReplyTo).toBe('m1')
    expect(out?.externalMessageId.startsWith('local-')).toBe(true)
    expect(knocks).toBe(1)
    expect(controller.getState().notice).toBe('sent-archived')
  })
})

describe('batch classification and insights', () => {
  it('writes AI taggings with provenance per batch', async () => {
    const { controller } = await booted()
    await controller.classifySelected(['conv-1'])
    const message = controller.getState().manifest?.conversations[0]?.messages[0]
    expect(message?.sentiment.value).toBe('positive')
    expect(message?.sentiment.source).toBe('ai')
    expect(message?.sentiment.aiMeta?.promptVersion).toBe('interaction-sentiment@1')
    expect(typeof message?.sentiment.aiMeta?.at).toBe('string')
    expect(message?.intent).toMatchObject({ value: 'praise', source: 'ai' })
    expect(controller.getState().notice).toBe('classify-done')
  })

  it('merges insight batches and stamps generatedAt once', async () => {
    const { controller } = await booted()
    await controller.extractInsights(['conv-1'])
    const insights = controller.getState().manifest?.insights
    expect(typeof insights?.generatedAt).toBe('string')
    expect(insights?.topQuestions).toEqual([{ label: '价格', count: 1, exampleMessageId: 'm1', topicHint: null }])
    expect(insights?.interests).toEqual([{ label: '测评', count: 1, exampleMessageId: null, topicHint: '开箱' }])
  })

  it('continues after a failed batch and reports partial failure', async () => {
    let calls = 0
    const { controller } = await booted({
      extractInteractionInsights: async () => {
        calls += 1
        if (calls > 1) throw new Error('upstream')
        return {
          batch: { questions: [], painPoints: [], interests: [{ label: '测评', count: 1, exampleMessageId: null, topicHint: null }] },
          promptVersion: 'interaction-insight@1',
        }
      },
    })
    // Two conversations → two batches (the batch size is 200, so force two
    // by classifying two calls' worth of conversations is not possible here;
    // instead run two extract rounds and fail the second call).
    await controller.extractInsights(['conv-1'])
    await controller.extractInsights(['conv-1'])
    expect(controller.getState().notice).toBe('insights-failed')
  })
})

describe('topic push and export', () => {
  it('pushes an interaction-sourced topic', async () => {
    const { controller, topics } = await booted()
    await controller.pushTopic('开箱测评', '做一期开箱测评', 'conv-1', 'summary')
    expect(topics.puts).toHaveLength(1)
    expect(topics.puts[0]).toMatchObject({ status: 'idea', source: { type: 'interaction', refId: 'conv-1' } })
  })

  it('exports the inbox CSV into the theme assets', async () => {
    const { controller, exports } = await booted()
    await controller.exportCsv('')
    expect(controller.getState().notice).toBe('need-theme')
    await controller.exportCsv('我的主题')
    expect(exports).toHaveLength(1)
    expect(exports[0]?.theme).toBe('我的主题')
    expect(exports[0]?.file).toMatch(/^interactions-\d{4}-\d{2}-\d{2}\.csv$/u)
    expect(exports[0]?.content).toBe('csv')
  })
})

describe('import staging', () => {
  it('stages the preview then commits and reports', async () => {
    const { controller } = await booted()
    await controller.stageImport('fans.csv', 'platform,external_message_id\nxhs,e1')
    expect(controller.getState().preview?.fileName).toBe('fans.csv')
    expect(controller.getState().notice).toBe('import-parsed')
    await controller.commitImport()
    expect(controller.getState().preview).toBeNull()
    expect(controller.getState().importReport).toMatchObject({ added: 2, conversationsCreated: 1 })
    expect(controller.getState().notice).toBe('import-committed')
  })
})
