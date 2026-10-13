import { mkdtemp, writeFile, readFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { describe, expect, it } from 'vitest'
import { SCHEDULE_FILENAME, mutateSchedule, normalizeInput, readSchedule } from '../src/store.ts'
import type { ScheduleItem } from '../src/types.ts'

async function tempFile(): Promise<string> {
  const dir = await mkdtemp(join(tmpdir(), 'dsh-content-schedule-'))
  return join(dir, SCHEDULE_FILENAME)
}

const BASE: ScheduleItem = {
  id: 'a' as ScheduleItem['id'],
  title: '秋日图文',
  date: '2026-09-20',
  time: '10:00',
  platform: '小红书',
  status: 'scheduled',
  kind: 'content',
  topic: 'autumn-note',
  url: null,
}

/** Overrides accept plain string ids; the helper brands them at the boundary. */
function item(overrides: Partial<Omit<ScheduleItem, 'id'>> & { id?: string }): ScheduleItem {
  const { id, ...rest } = overrides
  return { ...BASE, ...rest, ...(id === undefined ? {} : { id: id as ScheduleItem['id'] }) }
}

describe('readSchedule', () => {
  it('reads an absent file as an empty calendar', async () => {
    const snapshot = await readSchedule(await tempFile())
    expect(snapshot.items).toEqual([])
    expect(snapshot.problems).toEqual([])
  })

  it('sorts items by date, then time, then id', async () => {
    const file = await tempFile()
    await writeFile(file, JSON.stringify({ formatVersion: 0, items: [
      item({ id: 'b', date: '2026-09-21', time: null }),
      item({ id: 'c', date: '2026-09-20', time: '09:00' }),
      item({ id: 'a', date: '2026-09-20', time: '10:00' }),
    ] }))
    const snapshot = await readSchedule(file)
    expect(snapshot.items.map(entry => entry.id)).toEqual(['c', 'a', 'b'])
  })

  it('names a malformed record in problems and keeps the valid rest', async () => {
    const file = await tempFile()
    await writeFile(file, JSON.stringify({ formatVersion: 0, items: [
      BASE,
      { id: 'x', title: '' },
      'not-an-object',
    ] }))
    const snapshot = await readSchedule(file)
    expect(snapshot.items.map(entry => entry.id)).toEqual(['a'])
    expect(snapshot.problems).toHaveLength(2)
  })

  it('loads an unsupported formatVersion as an empty calendar with a problem', async () => {
    const file = await tempFile()
    await writeFile(file, JSON.stringify({ formatVersion: 1, items: [BASE] }))
    const snapshot = await readSchedule(file)
    expect(snapshot.items).toEqual([])
    expect(snapshot.problems).toHaveLength(1)
  })

  it('reports a non-JSON file as a problem', async () => {
    const file = await tempFile()
    await writeFile(file, '{oops')
    const snapshot = await readSchedule(file)
    expect(snapshot.items).toEqual([])
    expect(snapshot.problems).toHaveLength(1)
  })
})

describe('normalizeInput', () => {
  it('generates an id when absent and normalizes a blank platform to null', () => {
    const { item: normalized } = normalizeInput({
      title: '  新选题  ', date: '2026-10-01', time: null, platform: '  ', status: 'idea', kind: 'content', topic: null, url: null,
    })
    expect(normalized).toBeDefined()
    expect(normalized!.id.length).toBeGreaterThan(0)
    expect(normalized!.title).toBe('新选题')
    expect(normalized!.platform).toBeNull()
  })

  it('rejects an empty title, a bad date, and a bad time', () => {
    const bad: never[] = []
    void bad
    expect(normalizeInput({ title: ' ', date: '2026-10-01', time: null, platform: null, status: 'idea', kind: 'content', topic: null, url: null }).detail).toBeDefined()
    expect(normalizeInput({ title: 't', date: '20261001', time: null, platform: null, status: 'idea', kind: 'content', topic: null, url: null }).detail).toBeDefined()
    expect(normalizeInput({ title: 't', date: '2026-10-01', time: '25:00', platform: null, status: 'idea', kind: 'content', topic: null, url: null }).detail).toBeDefined()
  })
})

describe('mutateSchedule', () => {
  it('persists an upsert and rounds the format through the file', async () => {
    const file = await tempFile()
    const { item: created } = normalizeInput({ title: '新选题', date: '2026-10-01', time: null, platform: null, status: 'idea', kind: 'content', topic: null, url: null })
    await mutateSchedule(file, items => [...items, created!])
    const snapshot = await readSchedule(file)
    expect(snapshot.items).toHaveLength(1)
    expect(snapshot.items[0]!.title).toBe('新选题')
    const raw: unknown = JSON.parse(await readFile(file, 'utf8'))
    expect((raw as { formatVersion: unknown }).formatVersion).toBe(0)
  })

  it('replaces in place on a known id and keeps order', async () => {
    const file = await tempFile()
    await mutateSchedule(file, () => [item({ id: 'a' }), item({ id: 'b', date: '2026-09-21' })])
    await mutateSchedule(file, items => items.map(entry => entry.id === 'a' ? item({ id: 'a', status: 'published', url: 'https://x' }) : entry))
    const snapshot = await readSchedule(file)
    expect(snapshot.items.map(entry => entry.status)).toEqual(['published', 'scheduled'])
    expect(snapshot.items[0]!.url).toBe('https://x')
  })

  it('removes by id and tolerates unknown ids', async () => {
    const file = await tempFile()
    await mutateSchedule(file, () => [item({ id: 'a' }), item({ id: 'b' })])
    await mutateSchedule(file, items => items.filter(entry => entry.id !== 'a'))
    await mutateSchedule(file, items => items.filter(entry => entry.id !== 'ghost'))
    const snapshot = await readSchedule(file)
    expect(snapshot.items.map(entry => entry.id)).toEqual(['b'])
  })
})
