import { mkdtemp, writeFile, readFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { describe, expect, it } from 'vitest'
import { TOPICS_FILENAME, mutateTopics, normalizeInput, readTopics } from '../src/store.ts'
import type { TopicItem, TopicItemInput, TopicScore, TopicScoreFactor } from '../src/types.ts'

async function tempFile(): Promise<string> {
  const dir = await mkdtemp(join(tmpdir(), 'dsh-content-topics-'))
  return join(dir, TOPICS_FILENAME)
}

const BASE: TopicItem = {
  id: 'a' as TopicItem['id'],
  title: '秋日图文选题',
  oneLiner: '一次城市秋日的图文记录',
  status: 'todo',
  source: { type: 'manual', refId: null, url: null, snapshot: null },
  tags: ['图文'],
  description: null,
  score: null,
  planDate: '2026-10-01',
  scheduleItemId: null,
  topicDir: null,
  createdAt: '2026-09-20T08:00:00.000Z',
  updatedAt: '2026-09-20T08:00:00.000Z',
}

/** A record carrying every optional payload: provenance snapshot and AI score. */
const SOURCED: TopicItem = {
  ...BASE,
  id: 'g' as TopicItem['id'],
  title: '对标拆解改编',
  source: {
    type: 'gather',
    refId: '6f0a9b2e-1c3d-4e5f-8a7b-9c0d1e2f3a4b',
    url: 'https://example.com/post',
    snapshot: { title: '原文标题', summary: '原文摘要', capturedAt: '2026-09-21T09:30:00.000Z' },
  },
  score: {
    total: 7.5,
    source: 'ai',
    factors: [{ name: '受众匹配', score: 8, reason: '与既有读者画像重合', confidence: 0.8, estimated: true }],
    evaluatedAt: '2026-09-22T10:00:00.000Z',
  },
}

/** Overrides accept plain string ids; the helper brands them at the boundary. */
function item(overrides: Partial<Omit<TopicItem, 'id'>> & { id?: string }): TopicItem {
  const { id, ...rest } = overrides
  return { ...BASE, ...rest, ...(id === undefined ? {} : { id: id as TopicItem['id'] }) }
}

/** Builds a deliberately malformed stored record; the looseness is the point. */
function badRecord(overrides: Record<string, unknown>): unknown {
  return { ...BASE, ...overrides }
}

describe('readTopics', () => {
  it('reads an absent file as an empty bank', async () => {
    const snapshot = await readTopics(await tempFile())
    expect(snapshot.items).toEqual([])
    expect(snapshot.problems).toEqual([])
  })

  it('sorts items by updatedAt descending, then id for ties', async () => {
    const file = await tempFile()
    await writeFile(file, JSON.stringify({ formatVersion: 0, items: [
      item({ id: 'a' }),
      item({ id: 'b', updatedAt: '2026-09-25T10:00:00.000Z' }),
      item({ id: 'e', updatedAt: '2026-09-23T00:00:00.000Z' }),
      item({ id: 'd', updatedAt: '2026-09-23T00:00:00.000Z' }),
      item({ id: 'c', updatedAt: '2026-09-22T09:00:00.000Z' }),
    ] }))
    const snapshot = await readTopics(file)
    expect(snapshot.items.map(entry => entry.id)).toEqual(['b', 'd', 'e', 'c', 'a'])
  })

  it('keeps a record with populated source snapshot and score intact', async () => {
    const file = await tempFile()
    await writeFile(file, JSON.stringify({ formatVersion: 0, items: [SOURCED] }))
    const snapshot = await readTopics(file)
    expect(snapshot.items).toEqual([SOURCED])
    expect(snapshot.problems).toEqual([])
  })

  it('names a malformed record in problems and keeps the valid rest', async () => {
    const file = await tempFile()
    await writeFile(file, JSON.stringify({ formatVersion: 0, items: [
      BASE,
      { id: 'x', title: '' },
      { ...BASE, id: 's', status: 'archived' },
      'not-an-object',
    ] }))
    const snapshot = await readTopics(file)
    expect(snapshot.items.map(entry => entry.id)).toEqual(['a'])
    expect(snapshot.problems).toHaveLength(3)
  })

  it('rejects stored records failing any field gate', async () => {
    const file = await tempFile()
    await writeFile(file, JSON.stringify({ formatVersion: 0, items: [
      BASE,
      badRecord({ id: '' }),
      badRecord({ oneLiner: 42 }),
      badRecord({ source: null }),
      badRecord({ source: { type: 'rss', refId: null, url: null, snapshot: null } }),
      badRecord({ source: { type: 'manual', refId: null, url: null, snapshot: { title: 't', summary: null, capturedAt: 'nope' } } }),
      badRecord({ source: { type: 'manual', refId: null, url: null, snapshot: {} } }),
      badRecord({ tags: 'x' }),
      badRecord({ tags: ['ok', ''] }),
      badRecord({ description: 42 }),
      badRecord({ score: 42 }),
      badRecord({ score: { total: 99, source: 'manual', factors: null, evaluatedAt: '2026-09-25T00:00:00.000Z' } }),
      badRecord({ score: { total: 'high', source: 'manual', factors: null, evaluatedAt: '2026-09-25T00:00:00.000Z' } }),
      badRecord({ score: { total: 5, source: 'gpt', factors: null, evaluatedAt: '2026-09-25T00:00:00.000Z' } }),
      badRecord({ score: { total: 5, source: 'ai', factors: ['x'], evaluatedAt: '2026-09-25T00:00:00.000Z' } }),
      badRecord({ score: { total: 5, source: 'ai', factors: [{ name: '', score: 5, reason: null, confidence: 1, estimated: true }], evaluatedAt: '2026-09-25T00:00:00.000Z' } }),
      badRecord({ score: { total: 5, source: 'ai', factors: [{ name: 'n', score: 'high', reason: null, confidence: 1, estimated: true }], evaluatedAt: '2026-09-25T00:00:00.000Z' } }),
      badRecord({ score: { total: 5, source: 'ai', factors: [{ name: 'n', score: 5, reason: 42, confidence: 1, estimated: true }], evaluatedAt: '2026-09-25T00:00:00.000Z' } }),
      badRecord({ score: { total: 5, source: 'ai', factors: [{ name: 'n', score: 5, reason: null, confidence: 1.5, estimated: true }], evaluatedAt: '2026-09-25T00:00:00.000Z' } }),
      badRecord({ score: { total: 5, source: 'ai', factors: [{ name: 'n', score: 5, reason: null, confidence: 1, estimated: 'yes' }], evaluatedAt: '2026-09-25T00:00:00.000Z' } }),
      badRecord({ score: { total: 5, source: 'ai', factors: null, evaluatedAt: 'nope' } }),
      badRecord({ planDate: 'nope' }),
      badRecord({ scheduleItemId: 42 }),
      badRecord({ topicDir: 42 }),
      badRecord({ createdAt: 'nope' }),
      badRecord({ updatedAt: '2026-13-99T00:00:00.000Z' }),
    ] }))
    const snapshot = await readTopics(file)
    expect(snapshot.items.map(entry => entry.id)).toEqual(['a'])
    expect(snapshot.problems).toHaveLength(25)
  })

  it('loads an unsupported formatVersion as an empty bank with a problem', async () => {
    const file = await tempFile()
    await writeFile(file, JSON.stringify({ formatVersion: 1, items: [BASE] }))
    const snapshot = await readTopics(file)
    expect(snapshot.items).toEqual([])
    expect(snapshot.problems).toHaveLength(1)
  })

  it('reports a non-JSON file as a problem', async () => {
    const file = await tempFile()
    await writeFile(file, '{oops')
    const snapshot = await readTopics(file)
    expect(snapshot.items).toEqual([])
    expect(snapshot.problems).toHaveLength(1)
  })

  it('reports a missing items array as a problem', async () => {
    const file = await tempFile()
    await writeFile(file, JSON.stringify({ formatVersion: 0 }))
    const snapshot = await readTopics(file)
    expect(snapshot.items).toEqual([])
    expect(snapshot.problems).toHaveLength(1)
  })
})

describe('normalizeInput', () => {
  it('generates an id, stamps both timestamps, and normalizes blanks', () => {
    const { item: normalized } = normalizeInput({
      title: '  新选题  ',
      oneLiner: '  一句话  ',
      status: 'idea',
      source: { type: 'gather', refId: '  mat-1  ', url: '  ', snapshot: null },
      tags: [' 图文 ', '', '备选'],
      description: '  ',
      score: null,
      planDate: '2026-10-01',
      scheduleItemId: null,
      topicDir: null,
    })
    expect(normalized).toBeDefined()
    expect(normalized!.id.length).toBeGreaterThan(0)
    expect(normalized!.title).toBe('新选题')
    expect(normalized!.oneLiner).toBe('一句话')
    expect(normalized!.source.refId).toBe('mat-1')
    expect(normalized!.source.url).toBeNull()
    expect(normalized!.tags).toEqual(['图文', '备选'])
    expect(normalized!.description).toBeNull()
    expect(normalized!.createdAt).toBe(normalized!.updatedAt)
  })

  it('rejects an empty title, an unknown status, and a bad planDate', () => {
    const base = {
      title: 't', oneLiner: null, status: 'idea', source: { type: 'manual', refId: null, url: null, snapshot: null },
      tags: [], description: null, score: null, planDate: null, scheduleItemId: null, topicDir: null,
    } as const
    expect(normalizeInput({ ...base, title: ' ' }).detail).toBeDefined()
    expect(normalizeInput({ ...base, status: 'archived' as TopicItem['status'] }).detail).toBeDefined()
    expect(normalizeInput({ ...base, planDate: '20261001' }).detail).toBeDefined()
  })

  it('rejects an out-of-range score total and a non-ISO evaluatedAt', () => {
    const base = {
      title: 't', oneLiner: null, status: 'idea', source: { type: 'manual', refId: null, url: null, snapshot: null },
      tags: [], description: null, planDate: null, scheduleItemId: null, topicDir: null,
    } as const
    expect(normalizeInput({
      ...base,
      score: { total: 10.5, source: 'manual', factors: null, evaluatedAt: '2026-09-25T00:00:00.000Z' },
    }).detail).toBeDefined()
    expect(normalizeInput({
      ...base,
      score: { total: 5, source: 'manual', factors: null, evaluatedAt: 'yesterday' },
    }).detail).toBeDefined()
  })

  it('rejects an unknown source type and a non-string tag entry', () => {
    const base: TopicItemInput = {
      title: 't', oneLiner: null, status: 'idea', source: { type: 'manual', refId: null, url: null, snapshot: null },
      tags: [], description: null, score: null, planDate: null, scheduleItemId: null, topicDir: null,
    }
    expect(normalizeInput({ ...base, source: { ...base.source, type: 'rss' as unknown as TopicItem['source']['type'] } }).detail).toBeDefined()
    expect(normalizeInput({ ...base, tags: [42] as unknown as readonly string[] }).detail).toBeDefined()
  })

  it('rejects non-string scalars in every nullable string field', () => {
    const base = {
      title: 't', oneLiner: null, status: 'idea', source: { type: 'manual', refId: null, url: null, snapshot: null },
      tags: [], description: null, score: null, planDate: null, scheduleItemId: null, topicDir: null,
    } as const
    const bad = 42 as unknown as string
    expect(normalizeInput({ ...base, oneLiner: bad }).detail).toBeDefined()
    expect(normalizeInput({ ...base, description: bad }).detail).toBeDefined()
    expect(normalizeInput({ ...base, planDate: bad }).detail).toBeDefined()
    expect(normalizeInput({ ...base, scheduleItemId: bad }).detail).toBeDefined()
    expect(normalizeInput({ ...base, topicDir: bad }).detail).toBeDefined()
    expect(normalizeInput({ ...base, source: { ...base.source, refId: bad } }).detail).toBeDefined()
    expect(normalizeInput({ ...base, source: { ...base.source, url: bad } }).detail).toBeDefined()
    expect(normalizeInput({ ...base, source: { ...base.source, snapshot: 42 as unknown as TopicItem['source']['snapshot'] } }).detail).toBeDefined()
    expect(normalizeInput({ ...base, score: 42 as unknown as TopicScore }).detail).toBeDefined()
  })

  it('rejects a score outside its numeric and enum ranges', () => {
    const base = {
      title: 't', oneLiner: null, status: 'idea', source: { type: 'manual', refId: null, url: null, snapshot: null },
      tags: [], description: null, planDate: null, scheduleItemId: null, topicDir: null,
    } as const
    expect(normalizeInput({
      ...base,
      score: { total: -1, source: 'manual', factors: null, evaluatedAt: '2026-09-25T00:00:00.000Z' },
    }).detail).toBeDefined()
    expect(normalizeInput({
      ...base,
      score: { total: Number.POSITIVE_INFINITY, source: 'manual', factors: null, evaluatedAt: '2026-09-25T00:00:00.000Z' },
    }).detail).toBeDefined()
    expect(normalizeInput({
      ...base,
      score: { total: 5, source: 'gpt' as TopicScore['source'], factors: null, evaluatedAt: '2026-09-25T00:00:00.000Z' },
    }).detail).toBeDefined()
    expect(normalizeInput({
      ...base,
      score: { total: 5, source: 'ai', factors: [{} as unknown as TopicScoreFactor], evaluatedAt: '2026-09-25T00:00:00.000Z' },
    }).detail).toBeDefined()
  })

  it('honors an explicit id and keeps null optionals intact', () => {
    const { item: normalized } = normalizeInput({
      id: 'fixed' as TopicItem['id'],
      title: 't', oneLiner: '  ', status: 'idea', source: { type: 'benchmark', refId: '  ', url: ' https://x ', snapshot: null },
      tags: [], description: null, score: null, planDate: null, scheduleItemId: null, topicDir: null,
    })
    expect(normalized).toBeDefined()
    expect(normalized!.id).toBe('fixed')
    expect(normalized!.oneLiner).toBeNull()
    expect(normalized!.source.refId).toBeNull()
    expect(normalized!.source.url).toBe('https://x')
    expect(normalized!.description).toBeNull()
  })

  it('keeps a fully populated score with factors intact', () => {
    const score: TopicScore = {
      total: 7.5,
      source: 'ai',
      factors: [{ name: '受众匹配', score: 8, reason: '重合', confidence: 0.8, estimated: true }],
      evaluatedAt: '2026-09-25T00:00:00.000Z',
    }
    const { item: normalized } = normalizeInput({
      title: 't', oneLiner: null, status: 'idea', source: { type: 'manual', refId: null, url: null, snapshot: null },
      tags: [], description: null, score, planDate: null, scheduleItemId: null, topicDir: null,
    })
    expect(normalized).toBeDefined()
    expect(normalized!.score).toEqual(score)
  })
})

describe('mutateTopics', () => {
  it('persists an upsert and rounds the format through the file', async () => {
    const file = await tempFile()
    const { item: created } = normalizeInput({
      title: '新选题', oneLiner: null, status: 'idea', source: { type: 'manual', refId: null, url: null, snapshot: null },
      tags: [], description: null, score: null, planDate: '2026-10-01', scheduleItemId: null, topicDir: null,
    })
    await mutateTopics(file, items => [...items, created!])
    const snapshot = await readTopics(file)
    expect(snapshot.items).toHaveLength(1)
    expect(snapshot.items[0]!.title).toBe('新选题')
    const raw: unknown = JSON.parse(await readFile(file, 'utf8'))
    expect((raw as { formatVersion: unknown }).formatVersion).toBe(0)
  })

  it('replaces in place on a known id and keeps the other items', async () => {
    const file = await tempFile()
    await mutateTopics(file, () => [item({ id: 'a' }), item({ id: 'b', updatedAt: '2026-09-21T08:00:00.000Z' })])
    await mutateTopics(file, items => items.map(
      entry => entry.id === 'a' ? item({ id: 'a', status: 'creating', updatedAt: '2026-09-22T08:00:00.000Z' }) : entry,
    ))
    const snapshot = await readTopics(file)
    expect(snapshot.items.map(entry => entry.id)).toEqual(['a', 'b'])
    expect(snapshot.items[0]!.status).toBe('creating')
    expect(snapshot.items[1]!.title).toBe(BASE.title)
  })

  it('removes by id and tolerates unknown ids', async () => {
    const file = await tempFile()
    await mutateTopics(file, () => [item({ id: 'a' }), item({ id: 'b' })])
    await mutateTopics(file, items => items.filter(entry => entry.id !== 'a'))
    await mutateTopics(file, items => items.filter(entry => entry.id !== 'ghost'))
    const snapshot = await readTopics(file)
    expect(snapshot.items.map(entry => entry.id)).toEqual(['b'])
  })

  it('keeps the previous file intact when a mutation fails', async () => {
    const file = await tempFile()
    await mutateTopics(file, () => [item({ id: 'a' })])
    const before = await readFile(file, 'utf8')
    await expect(mutateTopics(file, () => {
      throw new Error('boom')
    })).rejects.toThrow('boom')
    expect(await readFile(file, 'utf8')).toBe(before)
  })
})
