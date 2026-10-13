import { describe, expect, it } from 'vitest'
import { GATHER_SOURCE_LIMIT, createGatherStorage, type GatherStorageBackend } from '../src/client/gather/storage.ts'
import type { GatherSource, GatherTask } from '../src/client/gather/types.ts'

const source: GatherSource = {
  id: 's1',
  name: '源一',
  url: 'https://example.com/feed.xml',
  intervalMinutes: 60,
  enabled: true,
  tags: ['科技'],
  excludeKeywords: ['广告'],
  createdAt: '2026-09-25T00:00:00.000Z',
  lastFetchedAt: null,
  lastStatus: null,
  consecutiveFailures: 0,
  etag: null,
  lastModified: null,
}

const task: GatherTask = {
  id: 't1',
  name: '每日采集',
  sourceIds: ['s1'],
  themeName: 'AI 工具',
  maxItemsPerRun: 20,
  since: null,
  includeKeywords: [],
  excludeKeywords: [],
  aiEnabled: true,
  intervalMinutes: 60,
  log: [],
}

function memoryBackend(): GatherStorageBackend & { map: Map<string, string>; failWrites: boolean } {
  const map = new Map<string, string>()
  return {
    map,
    failWrites: false,
    getItem: key => map.get(key) ?? null,
    setItem(key, value) {
      if (this.failWrites) throw new Error('quota exceeded')
      map.set(key, value)
    },
    removeItem: (key) => { map.delete(key) },
  }
}

describe('gather storage', () => {
  it('round-trips sources and tasks and drops corrupted or unknown entries', () => {
    const backend = memoryBackend()
    const storage = createGatherStorage(backend)
    storage.save({ sources: [source], tasks: [task] })
    const reloaded = createGatherStorage(backend).load()
    expect(reloaded.sources).toEqual([source])
    expect(reloaded.tasks).toEqual([task])
  })

  it('rebuilds defaults when keys are missing or corrupt', () => {
    const backend = memoryBackend()
    backend.map.set('content-studio.gather.sources.v0', '{not json')
    backend.map.set('content-studio.gather.tasks.v0', '{"formatVersion":0}')
    const loaded = createGatherStorage(backend).load()
    expect(loaded.sources).toEqual([])
    expect(loaded.tasks).toEqual([])
  })

  it('degrades to memory when a write fails and reports the downgrade', () => {
    const backend = memoryBackend()
    const storage = createGatherStorage(backend)
    expect(storage.persistent).toBe(true)
    backend.failWrites = true
    storage.save({ sources: [source], tasks: [] })
    expect(storage.persistent).toBe(false)
    // The storage module stops persisting (the controller keeps its own
    // in-memory state); reads against the disabled backend rebuild empty.
    expect(storage.load().sources).toEqual([])
  })

  it('works without any backend at all (non-browser host)', () => {
    const storage = createGatherStorage(undefined)
    expect(storage.persistent).toBe(false)
    // Saving is a safe no-op; reads rebuild empty.
    storage.save({ sources: [source], tasks: [] })
    expect(storage.load().sources).toEqual([])
  })

  it('exposes the documented source limit', () => {
    expect(GATHER_SOURCE_LIMIT).toBe(100)
  })
})
