import { mkdtemp, readFile, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { afterEach, describe, expect, it } from 'vitest'
import {
  INTERACTIONS_FILENAME, assertInteractionsManifest, commitInteractionImportFile,
  parseInteractionsManifest, readInteractionsFile, summarizeInteractions, writeInteractionsFile,
} from '../src/interactions/store.ts'
import { stubInteractionChannel } from '../src/interactions/channel.ts'
import type { InteractionConversation, InteractionsManifest } from '../src/interactions/types.ts'
import { EMPTY_INTERACTION_INSIGHTS } from '../src/interactions/types.ts'

let dir: string | undefined

afterEach(async () => {
  if (dir !== undefined) await rm(dir, { recursive: true, force: true })
  dir = undefined
})

async function storeRoot(): Promise<string> {
  dir = await mkdtemp(join(tmpdir(), 'interaction-store-'))
  return dir
}

/** One valid conversation, overridden per test. */
function conversation(overrides: Partial<InteractionConversation> = {}): InteractionConversation {
  return {
    id: 'conv-1',
    platform: 'xhs',
    participant: { externalUserId: 'fan-1', nickname: '小粉丝' },
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
      id: 'msg-1',
      externalMessageId: 'ext-1',
      direction: 'in',
      type: 'comment',
      content: '多少钱？',
      inReplyTo: null,
      sentAt: '2026-09-28T00:00:00.000Z',
      sentiment: { value: 'unknown', source: 'user', aiMeta: null },
      intent: { value: 'unknown', source: 'user', aiMeta: null },
      replyDrafts: [],
    }],
    ...overrides,
  }
}

function manifest(conversations: readonly InteractionConversation[]): InteractionsManifest {
  return {
    formatVersion: 0,
    conversations,
    insights: { ...EMPTY_INTERACTION_INSIGHTS },
    summary: summarizeInteractions(conversations),
  }
}

describe('parseInteractionsManifest', () => {
  it('rejects an unknown formatVersion wholesale', () => {
    const parsed = parseInteractionsManifest(JSON.stringify({ formatVersion: 1, conversations: [] }))
    expect(parsed.manifest.conversations).toEqual([])
    expect(parsed.problems[0]).toContain('formatVersion')
  })

  it('names invalid JSON instead of throwing', () => {
    const parsed = parseInteractionsManifest('{broken')
    expect(parsed.manifest.conversations).toEqual([])
    expect(parsed.problems[0]).toContain('not valid JSON')
  })

  it('drops one malformed conversation and keeps the rest', () => {
    const good = conversation()
    const raw = JSON.stringify({ formatVersion: 0, conversations: [good, { id: 'broken' }], insights: null, summary: {} })
    const parsed = parseInteractionsManifest(raw)
    expect(parsed.manifest.conversations).toEqual([good])
    expect(parsed.problems[0]).toContain('invalid interaction conversation')
  })

  it('recomputes the summary cache and normalizes ordering on read', () => {
    const older = conversation({ id: 'old', updatedAt: '2026-09-27T00:00:00.000Z', status: 'replied' })
    const newer = conversation({ id: 'new', updatedAt: '2026-09-28T00:00:00.000Z' })
    const reversed = JSON.stringify({ formatVersion: 0, conversations: [older, newer], insights: null, summary: {} })
    const parsed = parseInteractionsManifest(reversed)
    expect(parsed.manifest.conversations.map(entry => entry.id)).toEqual(['new', 'old'])
    expect(parsed.manifest.summary).toEqual({ unread: 1, pendingReply: 0, replied: 1, archived: 0, spam: 0 })
  })
})

describe('writeInteractionsFile', () => {
  it('rejects wholesale on an unknown formatVersion', async () => {
    const root = await storeRoot()
    const bad = { ...manifest([]), formatVersion: 2 } as unknown as InteractionsManifest
    await expect(writeInteractionsFile(root, bad)).rejects.toThrow(/formatVersion/)
  })

  it('rejects wholesale on one invalid conversation without writing', async () => {
    const root = await storeRoot()
    const bad = { ...manifest([conversation()]), conversations: [{ id: 'x' } as unknown as InteractionConversation] }
    await expect(writeInteractionsFile(root, bad)).rejects.toThrow(/invalid interaction conversation/)
    expect(await readInteractionsFile(root)).toEqual({ manifest: null, problems: [] })
  })

  it('stores, recomputes the summary, and reads back', async () => {
    const root = await storeRoot()
    const stored = await writeInteractionsFile(root, manifest([conversation()]))
    expect(stored.summary.unread).toBe(1)
    const read = await readInteractionsFile(root)
    expect(read.manifest?.conversations).toHaveLength(1)
    expect(read.problems).toEqual([])
    const raw = JSON.parse(await readFile(join(root, INTERACTIONS_FILENAME), 'utf8')) as InteractionsManifest
    expect(raw.formatVersion).toBe(0)
  })
})

describe('commitInteractionImportFile', () => {
  it('groups messages into conversations and reports the accounting', async () => {
    const root = await storeRoot()
    const result = await commitInteractionImportFile(root, {
      messages: [
        {
          platform: 'xhs', externalMessageId: 'e1', externalUserId: 'u1', nickname: '阿芳', type: 'comment',
          content: '能包邮吗', inReplyToExternal: null, sentAt: '2026-09-28T01:00:00.000Z',
          topicRef: null, outputRef: null, personaId: null,
        },
        {
          platform: 'xhs', externalMessageId: 'e2', externalUserId: 'u2', nickname: null, type: 'dm',
          content: 'updated', inReplyToExternal: null, sentAt: '2026-09-28T02:00:00.000Z',
          topicRef: null, outputRef: null, personaId: 'p1',
        },
      ],
    })
    expect(result).toMatchObject({ added: 2, updated: 0, conversationsCreated: 2 })
    const read = await readInteractionsFile(root)
    expect(read.manifest?.summary.unread).toBe(2)
    const withPersona = read.manifest?.conversations.find(entry => entry.personaId === 'p1')
    expect(withPersona?.messages[0]?.content).toBe('updated')
  })

  it('threads against the batch and the library, warning on unresolved parents', async () => {
    const root = await storeRoot()
    await commitInteractionImportFile(root, {
      messages: [{
        platform: 'xhs', externalMessageId: 'parent', externalUserId: 'u1', nickname: null, type: 'comment',
        content: 'parent', inReplyToExternal: null, sentAt: '2026-09-28T01:00:00.000Z',
        topicRef: null, outputRef: null, personaId: null,
      }],
    })
    const result = await commitInteractionImportFile(root, {
      messages: [
        {
          platform: 'xhs', externalMessageId: 'child', externalUserId: 'u1', nickname: null, type: 'comment',
          content: 'child', inReplyToExternal: 'parent', sentAt: '2026-09-28T02:00:00.000Z',
          topicRef: null, outputRef: null, personaId: null,
        },
        {
          platform: 'xhs', externalMessageId: 'orphan', externalUserId: 'u1', nickname: null, type: 'comment',
          content: 'orphan', inReplyToExternal: 'missing', sentAt: '2026-09-28T03:00:00.000Z',
          topicRef: null, outputRef: null, personaId: null,
        },
      ],
    })
    expect(result.added).toBe(2)
    expect(result.threadWarnings).toHaveLength(1)
    expect(result.threadWarnings[0]).toContain('missing')
    const read = await readInteractionsFile(root)
    const conversation = read.manifest?.conversations[0]
    expect(conversation?.messages.map(message => message.externalMessageId)).toEqual(['parent', 'child', 'orphan'])
    const child = conversation?.messages.find(message => message.externalMessageId === 'child')
    const parent = conversation?.messages.find(message => message.externalMessageId === 'parent')
    expect(child?.inReplyTo).toBe(parent?.id)
    expect(conversation?.messages.find(message => message.externalMessageId === 'orphan')?.inReplyTo).toBeNull()
  })

  it('updates an existing external message id in place (idempotent re-import)', async () => {
    const root = await storeRoot()
    const row = {
      platform: 'xhs' as const, externalMessageId: 'e1', externalUserId: 'u1', nickname: null, type: 'comment' as const,
      content: '第一版', inReplyToExternal: null, sentAt: '2026-09-28T01:00:00.000Z',
      topicRef: null, outputRef: null, personaId: null,
    }
    await commitInteractionImportFile(root, { messages: [row] })
    const second = await commitInteractionImportFile(root, {
      messages: [{ ...row, content: '第二版' }],
    })
    expect(second).toMatchObject({ added: 0, updated: 1, conversationsCreated: 0 })
    const read = await readInteractionsFile(root)
    expect(read.manifest?.conversations[0]?.messages[0]?.content).toBe('第二版')
  })

  it('refuses to commit onto an unreadable manifest', async () => {
    const root = await storeRoot()
    const { writeFile, mkdir } = await import('node:fs/promises')
    await mkdir(root, { recursive: true })
    await writeFile(join(root, INTERACTIONS_FILENAME), '{broken', 'utf8')
    await expect(commitInteractionImportFile(root, { messages: [] })).rejects.toThrow(/unreadable/)
  })
})

describe('assertInteractionsManifest', () => {
  it('rejects a message past the per-conversation cap', () => {
    const flooded = conversation({
      messages: Array.from({ length: 5001 }, (_, index) => ({
        id: `m${index}`, externalMessageId: `e${index}`, direction: 'in' as const, type: 'comment' as const,
        content: 'x', inReplyTo: null, sentAt: '2026-09-28T00:00:00.000Z',
        sentiment: { value: 'unknown' as const, source: 'user' as const, aiMeta: null },
        intent: { value: 'unknown' as const, source: 'user' as const, aiMeta: null },
        replyDrafts: [],
      })),
    })
    expect(() =>{  assertInteractionsManifest(manifest([flooded])) }).toThrow(/message cap/)
  })
})

describe('stubInteractionChannel', () => {
  it('refuses both calls with MCP_NOT_CONFIGURED', async () => {
    expect(await stubInteractionChannel.fetchMessages()).toEqual({ ok: false, reason: 'MCP_NOT_CONFIGURED' })
    expect(await stubInteractionChannel.sendReply({ conversationId: 'c', inReplyTo: null, content: 'x', personaId: null }))
      .toEqual({ ok: false, reason: 'MCP_NOT_CONFIGURED' })
  })
})
