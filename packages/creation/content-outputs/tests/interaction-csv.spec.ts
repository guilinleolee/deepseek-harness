import { describe, expect, it } from 'vitest'
import {
  buildInteractionExportCsv, escapeCsvField, parseInteractionImport,
} from '../src/interactions/csv.ts'
import type { InteractionConversation } from '../src/interactions/types.ts'

const HEADER = 'platform,external_message_id,external_user_id,nickname,type,content,in_reply_to,sent_at,topic_ref,output_ref,persona_id'

function csv(...rows: readonly string[]): string {
  return [HEADER, ...rows].join('\n')
}

describe('parseInteractionImport', () => {
  it('parses valid rows and normalizes to null optionals', () => {
    const preview = parseInteractionImport({
      fileName: 'export.csv',
      text: csv('xhs,e1,u1,阿芳,comment,多少钱,,2026-09-28T01:00:00.000Z,,,'),
    })
    expect(preview.messages).toHaveLength(1)
    const message = preview.messages[0]
    expect(message).toMatchObject({
      platform: 'xhs', externalMessageId: 'e1', externalUserId: 'u1', nickname: '阿芳',
      type: 'comment', content: '多少钱', inReplyToExternal: null, personaId: null,
    })
  })

  it('tolerates a UTF-8 BOM', () => {
    const preview = parseInteractionImport({ fileName: 'x.csv', text: `\uFEFF${csv('xhs,e1,u1,,comment,hi,,2026-09-28T01:00:00.000Z,,,')}` })
    expect(preview.messages).toHaveLength(1)
  })

  it('rejects GBK-mojibake text wholesale', () => {
    expect(() => parseInteractionImport({ fileName: 'x.csv', text: csv('xhs,e1,u1,,comment,����,,2026-09-28T01:00:00.000Z,,,') }))
      .toThrow(/UTF-8/)
  })

  it('rejects when a required column is missing from the header', () => {
    expect(() => parseInteractionImport({ fileName: 'x.csv', text: 'platform,external_message_id\nxhs,e1' }))
      .toThrow(/missing required columns/)
  })

  it('reports per-row rejections with 1-based physical row numbers', () => {
    const preview = parseInteractionImport({
      fileName: 'x.csv',
      text: csv(
        'xhs,e1,u1,,comment,ok,,2026-09-28T01:00:00.000Z,,,',
        'tiktok,e2,u1,,comment,bad platform,,2026-09-28T01:00:00.000Z,,,',
        'xhs,,u1,,comment,missing id,,2026-09-28T01:00:00.000Z,,,',
        'xhs,e3,u1,,comment,bad date,,not-a-date,,,',
      ),
    })
    expect(preview.messages).toHaveLength(1)
    expect(preview.rejected.map(rejection => rejection.row)).toEqual([3, 4, 5])
  })

  it('collapses a repeated external message id inside one file (last wins)', () => {
    const preview = parseInteractionImport({
      fileName: 'x.csv',
      text: csv(
        'xhs,e1,u1,,comment,first,,2026-09-28T01:00:00.000Z,,,',
        'xhs,e1,u1,,comment,second,,2026-09-28T02:00:00.000Z,,,',
      ),
    })
    expect(preview.messages).toHaveLength(1)
    expect(preview.messages[0]?.content).toBe('second')
  })

  it('rejects past the 5000-row cap', () => {
    const rows = Array.from({ length: 5001 }, (_, index) => `xhs,e${index},u1,,comment,c${index},,2026-09-28T01:00:00.000Z,,,`)
    const preview = parseInteractionImport({ fileName: 'x.csv', text: csv(...rows) })
    expect(preview.messages).toHaveLength(5000)
    expect(preview.rejected[0]?.reason).toContain('5000-row cap')
  })
})

describe('buildInteractionExportCsv', () => {
  const conversation: InteractionConversation = {
    id: 'conv-1',
    platform: 'xhs',
    participant: { externalUserId: 'u1', nickname: '阿芳' },
    topicRef: null,
    outputRef: null,
    personaId: null,
    status: 'replied',
    tags: ['产品咨询', '其他'],
    note: '',
    starred: false,
    createdAt: '2026-09-28T00:00:00.000Z',
    updatedAt: '2026-09-28T00:00:00.000Z',
    messages: [
      {
        id: 'm1', externalMessageId: 'e1', direction: 'in', type: 'comment', content: '问题, 带逗号',
        inReplyTo: null, sentAt: '2026-09-28T01:00:00.000Z',
        sentiment: { value: 'unknown', source: 'user', aiMeta: null },
        intent: { value: 'unknown', source: 'user', aiMeta: null }, replyDrafts: [],
      },
      {
        id: 'm2', externalMessageId: 'local-1', direction: 'out', type: 'comment', content: '答复',
        inReplyTo: 'm1', sentAt: '2026-09-28T02:00:00.000Z',
        sentiment: { value: 'unknown', source: 'user', aiMeta: null },
        intent: { value: 'unknown', source: 'user', aiMeta: null }, replyDrafts: [],
      },
    ],
  }

  it('exports BOM + CRLF with the frozen column order and quoted fields', () => {
    const text = buildInteractionExportCsv([conversation])
    expect(text.charCodeAt(0)).toBe(0xfeff)
    expect(text.includes('\r\n')).toBe(true)
    const lines = text.slice(1).split('\r\n').filter(line => line.length > 0)
    expect(lines[0]).toBe('platform,external_message_id,external_user_id,nickname,type,content,in_reply_to,sent_at,topic_ref,output_ref,persona_id,conversation_id,status,tags')
    expect(lines[1]).toContain('"问题, 带逗号"')
    expect(lines[1]).toContain('conv-1')
    expect(lines[1]).toContain('产品咨询|其他')
  })

  it('round-trips through the import face unchanged', () => {
    const text = buildInteractionExportCsv([conversation])
    const preview = parseInteractionImport({ fileName: 'round-trip.csv', text })
    expect(preview.rejected).toEqual([])
    expect(preview.messages).toHaveLength(2)
    const [inbound, outbound] = preview.messages
    expect(inbound?.externalMessageId).toBe('e1')
    expect(inbound?.content).toBe('问题, 带逗号')
    // The out message re-imports as an inbound row of the same conversation,
    // keyed by its external id — the round trip preserves identity, and the
    // threading column resolves the parent by external id.
    expect(outbound?.inReplyToExternal).toBe('e1')
  })
})

describe('escapeCsvField', () => {
  it('doubles quotes and forces quoting on delimiters', () => {
    expect(escapeCsvField('plain')).toBe('plain')
    expect(escapeCsvField('a,b')).toBe('"a,b"')
    expect(escapeCsvField('say "hi"')).toBe('"say ""hi"""')
    expect(escapeCsvField('line\nbreak')).toBe('"line\nbreak"')
  })
})
