import { describe, expect, it, vi } from 'vitest'
import type { GatherMaterial } from '@deepseek-ai/dsh-content-outputs/types'
import { createGatherController } from '../src/client/gather/gather-store.ts'
import type { GatherGateway } from '../src/client/gather/types.ts'

/** In-memory storage backend so tests never touch real localStorage. */
function memoryBackend(): {
  getItem(key: string): string | null
  setItem(key: string, value: string): void
  removeItem(key: string): void
  map: Map<string, string>
} {
  const map = new Map<string, string>()
  return {
    map,
    getItem: key => map.get(key) ?? null,
    setItem: (key, value) => { map.set(key, value) },
    removeItem: (key) => { map.delete(key) },
  }
}

/** There is no storage-module injection point, so tests stub localStorage. */
function stubLocalStorage(): { map: Map<string, string> } {
  const backend = memoryBackend()
  ;(globalThis as { window?: unknown }).window = { localStorage: backend }
  return { map: backend.map }
}

function draft(id: string, overrides: Record<string, unknown> = {}) {
  return {
    id,
    rawGuid: null,
    url: `https://example.com/${id}`,
    title: `标题 ${id}`,
    publishedAt: '2026-09-20T10:00:00.000Z',
    summary: `摘要 ${id}`,
    content: null,
    ...overrides,
  }
}

interface Harness {
  gateway: GatherGateway
  fetchFeed: ReturnType<typeof vi.fn>
  writeAsset: ReturnType<typeof vi.fn>
  readAsset: ReturnType<typeof vi.fn>
  readManifest: ReturnType<typeof vi.fn>
  writeManifest: ReturnType<typeof vi.fn>
  /** Live manifest of the default theme, kept as an assignable array. */
  storedMaterials: GatherMaterial[]
  /** Per-theme manifest store backing the fake gateway. */
  manifests: Map<string, GatherMaterial[]>
  /** Per-theme body-snapshot store, keyed `<theme>/<file>`. */
  bodies: Map<string, string>
  themes: readonly string[]
  map: Map<string, string>
}

function harness(initialMaterials: GatherMaterial[] = [], themes: readonly string[] = ['AI 工具']): Harness {
  const { map } = stubLocalStorage()
  const manifests = new Map<string, GatherMaterial[]>([[themes[0]!, [...initialMaterials]]])
  const bodies = new Map<string, string>()
  const fetchFeed = vi.fn()
  const readManifest = vi.fn(async (theme: string) => ({
    manifest: { formatVersion: 0 as const, materials: manifests.get(theme) ?? [] },
    problems: [] as const,
  }))
  const writeManifest = vi.fn(async (theme: string, manifest: { formatVersion: 0; materials: readonly GatherMaterial[] }) => {
    manifests.set(theme, [...manifest.materials])
    return { formatVersion: 0 as const, materials: manifest.materials }
  })
  const writeAsset = vi.fn(async (write: { theme: string; file: string; content: string }) => {
    bodies.set(`${write.theme}/${write.file}`, write.content)
    return { truncated: false }
  })
  const readAsset = vi.fn(async (theme: string, file: string) => {
    const content = bodies.get(`${theme}/${file}`)
    return content === undefined ? {} : { content }
  })
  const deleteAsset = vi.fn(async (theme: string, file: string) => {
    bodies.delete(`${theme}/${file}`)
  })
  const gateway: GatherGateway = {
    fetchFeed: fetchFeed,
    writeAsset: writeAsset,
    readAsset: readAsset,
    readManifest: readManifest,
    writeManifest: writeManifest,
    moveAsset: async () => undefined,
    deleteAsset: deleteAsset,
    processMaterial: async () => ({ summary: 's', points: [], score: 50, tags: [] }),
  }
  return {
    gateway, fetchFeed, writeAsset, readAsset, readManifest, writeManifest,
    get storedMaterials() { return manifests.get(themes[0]!) ?? [] },
    manifests, bodies, themes, map,
  }
}

function makeController(h: Harness) {
  return createGatherController({
    gateway: h.gateway,
    listOutputs: async () => ({ projects: h.themes.map(topic => ({ topic: topic as never })) }),
    schedulePut: async () => ({}),
  })
}

function setup(h: Harness) {
  const gather = makeController(h)
  gather.addSource({ name: '源一', url: 'https://example.com/feed', intervalMinutes: 60, tags: [], excludeKeywords: [] })
  gather.addTask({
    name: '任务一',
    sourceIds: [gather.getState().sources[0]!.id],
    themeName: 'AI 工具',
    maxItemsPerRun: 20,
    since: null,
    includeKeywords: [],
    excludeKeywords: [],
    aiEnabled: true,
    intervalMinutes: null,
  })
  return { gather, source: gather.getState().sources[0]!, task: gather.getState().tasks[0]! }
}

describe('gather controller collection runs', () => {
  it('merges new drafts into the manifest, snapshots bodies, and stores cursors', async () => {
    const h = harness()
    h.fetchFeed.mockResolvedValue({
      notModified: false,
      etag: 'W/"abc"',
      lastModified: null,
      feedTitle: '源一',
      items: [draft('a'), draft('b', { content: '<p>正文</p>' })],
    })
    const { gather, task } = setup(h)
    await gather.triggerTask(task.id)

    expect(h.writeAsset).toHaveBeenCalledWith({ theme: 'AI 工具', file: 'body-b.html', content: '<p>正文</p>' })
    expect(h.writeManifest).toHaveBeenCalledTimes(1)
    expect(h.storedMaterials.map(material => material.id)).toEqual(['a', 'b'])
    expect(h.storedMaterials[1]!.bodyFile).toBe('body-b.html')
    expect(h.storedMaterials[0]!.status).toBe('unread')

    expect(gather.getState().sources[0]!.etag).toBe('W/"abc"')
    expect(gather.getState().sources[0]!.lastStatus).toBe('ok')
    expect(gather.getState().tasks[0]!.status).toBe('done')
    expect(gather.getState().tasks[0]!.log).toHaveLength(1)
    expect(gather.getState().tasks[0]!.log[0]!.added).toBe(2)
  })

  it('treats a 304 as success: cursors refresh, the manifest is untouched', async () => {
    const h = harness()
    h.fetchFeed.mockResolvedValue({ notModified: true, etag: 'W/"same"', lastModified: null, feedTitle: null, items: [] })
    const { gather, task } = setup(h)
    await gather.triggerTask(task.id)
    expect(h.writeManifest).not.toHaveBeenCalled()
    expect(h.writeAsset).not.toHaveBeenCalled()
    // 素材零变化 is stronger than "no write": a 304 run never even reads the
    // manifest, so no merge can be computed against it.
    expect(h.readManifest).not.toHaveBeenCalled()
    expect(gather.getState().tasks[0]!.status).toBe('done')
    expect(gather.getState().tasks[0]!.log[0]!.outcome).toBe('notModified')
    // The run still counts as a successful fetch: lastFetchedAt and the
    // conditional-request cursor move, the failure counter stays at zero.
    expect(gather.getState().sources[0]!.etag).toBe('W/"same"')
    expect(gather.getState().sources[0]!.lastFetchedAt).not.toBeNull()
    expect(gather.getState().sources[0]!.lastStatus).toBe('ok')
    expect(gather.getState().sources[0]!.consecutiveFailures).toBe(0)
  })

  it('keeps every stored material and the user state on failure, and starts the backoff', async () => {
    const favorite = {
      id: 'keep', sourceId: 'x', sourceName: '旧', title: '旧素材', url: 'https://example.com/keep',
      gatheredAt: '2026-09-01T00:00:00.000Z', status: 'favorite' as const,
    } as unknown as GatherMaterial
    const h = harness([favorite])
    h.fetchFeed.mockRejectedValue(new Error('HTTP 503'))
    const { gather, task } = setup(h)
    await gather.triggerTask(task.id)

    expect(h.writeManifest).not.toHaveBeenCalled()
    expect(h.writeAsset).not.toHaveBeenCalled()
    expect(h.storedMaterials).toEqual([favorite])
    expect(gather.getState().tasks[0]!.status).toBe('failed')
    expect(gather.getState().tasks[0]!.log[0]!.outcome).toBe('failed')
    expect(gather.getState().tasks[0]!.log[0]!.detail).toContain('503')
    expect(gather.getState().sources[0]!.lastStatus).toBe('failed')
    expect(gather.getState().sources[0]!.consecutiveFailures).toBe(1)
  })

  it('never overwrites existing entries on refresh: user state survives', async () => {
    const h = harness()
    const { gather, source, task } = setup(h)
    // The entry the previous run stored, carrying user state, keyed by the
    // same (sourceId, id) composite the refresh will see.
    const existing = {
      id: 'a', sourceId: source.id, sourceName: source.name, title: '用户看到过的', url: 'https://example.com/a',
      gatheredAt: '2026-09-01T00:00:00.000Z', status: 'read' as const, tags: ['人工标签'],
    } as unknown as GatherMaterial
    h.storedMaterials.splice(0, h.storedMaterials.length, existing)
    h.fetchFeed.mockResolvedValue({ notModified: false, etag: null, lastModified: null, feedTitle: null, items: [draft('a'), draft('new')] })
    await gather.triggerTask(task.id)

    expect(h.storedMaterials).toHaveLength(2)
    const kept = h.storedMaterials.find(material => material.id === 'a')!
    expect(kept.status).toBe('read')
    expect(kept.tags).toEqual(['人工标签'])
    expect(kept.title).toBe('用户看到过的')
    void gather
  })

  it('applies task keyword filters and the per-run cap', async () => {
    const h = harness()
    h.fetchFeed.mockResolvedValue({
      notModified: false, etag: null, lastModified: null, feedTitle: null,
      items: [
        draft('n1', { publishedAt: '2026-09-23T00:00:00.000Z', title: 'AI 大事件' }),
        draft('n2', { publishedAt: '2026-09-22T00:00:00.000Z', title: 'AI 小更新' }),
        draft('n3', { publishedAt: '2026-09-21T00:00:00.000Z', title: '无关体育' }),
        draft('n4', { publishedAt: '2026-09-20T00:00:00.000Z', title: '很老的 AI' }),
      ],
    })
    const { gather, source } = setup(h)
    gather.addTask({
      name: '过滤任务',
      sourceIds: [source.id],
      themeName: 'AI 工具',
      maxItemsPerRun: 1,
      since: '2026-09-21T12:00:00.000Z',
      includeKeywords: ['AI'],
      excludeKeywords: [],
      aiEnabled: false,
      intervalMinutes: null,
    })
    await gather.triggerTask(gather.getState().tasks[1]!.id)
    // n3 misses the include keyword, n4 predates the since cursor, the cap keeps only the newest.
    expect(h.storedMaterials.map(material => material.id)).toEqual(['n1'])
  })
})

describe('gather controller configuration', () => {
  it('persists sources and tasks so a cleared store loses only them', () => {
    const h = harness()
    const { gather } = setup(h)
    expect(gather.getState().sources).toHaveLength(1)
    expect(gather.getState().tasks).toHaveLength(1)
    expect([...h.map.keys()].filter(key => key.startsWith('content-studio.gather.')).length).toBeGreaterThanOrEqual(2)
    // 素材 live on disk (the manifest), so only the browser keys vanish:
    // a fresh controller rebuilds empty, the live one keeps its runtime state.
    h.map.clear()
    expect(makeController(h).getState().sources).toHaveLength(0)
    expect(gather.getState().sources).toHaveLength(1)
  })

  it('enforces the source limit', () => {
    const h = harness()
    const gather = makeController(h)
    for (let index = 0; index < 100; index += 1) {
      gather.addSource({ name: `源${index}`, url: `https://example.com/${index}`, intervalMinutes: 60, tags: [], excludeKeywords: [] })
    }
    expect(gather.getState().sources).toHaveLength(100)
    gather.addSource({ name: '超出', url: 'https://example.com/over', intervalMinutes: 60, tags: [], excludeKeywords: [] })
    expect(gather.getState().sources).toHaveLength(100)
    expect(gather.getState().notice).toBe('source-limit')
  })
})

describe('gather controller theme rebind', () => {
  it('migrates the snapshot and both manifests, keeping user state', async () => {
    const h = harness([], ['AI 工具', '新主题'])
    h.fetchFeed.mockResolvedValue({
      notModified: false, etag: null, lastModified: null, feedTitle: null,
      items: [draft('a', { content: '<p>正文</p>' })],
    })
    const { gather, task } = setup(h)
    await gather.triggerTask(task.id)
    await gather.refreshThemes()
    await gather.selectTheme('AI 工具')
    // User state earned before the move must ride along.
    await gather.toggleFavorite('a')

    await gather.bindTheme('a', '新主题')

    // The old manifest drops the entry; the new one carries it with the
    // favorite marker and the snapshot reference intact.
    expect(h.manifests.get('AI 工具')).toEqual([])
    const moved = h.manifests.get('新主题')![0]!
    expect(moved.id).toBe('a')
    expect(moved.status).toBe('favorite')
    expect(moved.bodyFile).toBe('body-a.html')
    // The snapshot was carried over: present under the new theme, gone from
    // the old one, byte-identical.
    expect(h.bodies.get('新主题/body-a.html')).toBe('<p>正文</p>')
    expect(h.bodies.has('AI 工具/body-a.html')).toBe(false)
    // The selected theme's visible materials no longer contain it.
    expect(gather.getState().materials).toEqual([])
  })

  it('aborts the rebind with both manifests untouched when the snapshot read fails', async () => {
    const h = harness([], ['AI 工具', '新主题'])
    h.fetchFeed.mockResolvedValue({
      notModified: false, etag: null, lastModified: null, feedTitle: null,
      items: [draft('a', { content: '<p>正文</p>' })],
    })
    const { gather, task } = setup(h)
    await gather.triggerTask(task.id)
    await gather.refreshThemes()
    await gather.selectTheme('AI 工具')
    h.readAsset.mockRejectedValueOnce(new Error('read EPERM'))

    await gather.bindTheme('a', '新主题')

    expect(h.manifests.get('AI 工具')).toHaveLength(1)
    // The abort means the new theme's manifest was never written at all.
    expect(h.manifests.has('新主题')).toBe(false)
    expect(h.bodies.has('AI 工具/body-a.html')).toBe(true)
    expect(gather.getState().notice).toContain('EPERM')
  })
})

/** Minimal document stand-in so the controller binds its visibility listener. */
function installFakeDocument(): { setVisibility(state: 'visible' | 'hidden'): void; uninstall(): void } {
  const listeners = new Map<string, Set<() => void>>()
  const doc = {
    visibilityState: 'visible',
    addEventListener(type: string, fn: () => void) {
      const set = listeners.get(type) ?? new Set()
      set.add(fn)
      listeners.set(type, set)
    },
    removeEventListener(type: string, fn: () => void) {
      listeners.get(type)?.delete(fn)
    },
  }
  ;(globalThis as { document?: unknown }).document = doc
  return {
    setVisibility(state: 'visible' | 'hidden') {
      doc.visibilityState = state
      for (const fn of listeners.get('visibilitychange') ?? []) fn()
    },
    uninstall() {
      delete (globalThis as { document?: unknown }).document
    },
  }
}

describe('gather controller scheduler lifecycle', () => {
  it('catches up an overdue interval task on open, carrying the stored cursor', async () => {
    vi.useFakeTimers()
    try {
      const h = harness()
      h.fetchFeed.mockResolvedValue({ notModified: false, etag: 'W/"v1"', lastModified: null, feedTitle: null, items: [draft('a')] })
      const { gather } = setup(h)
      gather.updateTask(gather.getState().tasks[0]!.id, { intervalMinutes: 60 })
      const doc = installFakeDocument()

      // First open: the task has never run, so the catch-up runs it once.
      gather.start()
      await vi.advanceTimersByTimeAsync(50)
      expect(h.fetchFeed).toHaveBeenCalledTimes(1)
      gather.dispose()

      // Reopening 61 minutes later: the task is overdue and runs again, this
      // time sending the ETag the previous run stored.
      vi.setSystemTime(Date.now() + 61 * 60_000)
      gather.start()
      await vi.advanceTimersByTimeAsync(50)
      expect(h.fetchFeed).toHaveBeenCalledTimes(2)
      expect(h.fetchFeed.mock.calls[1]?.[0]).toMatchObject({ etag: 'W/"v1"' })
      gather.dispose()

      // Reopening 10 minutes after that: nothing is due, no extra fetch.
      vi.setSystemTime(Date.now() + 10 * 60_000)
      gather.start()
      await vi.advanceTimersByTimeAsync(50)
      expect(h.fetchFeed).toHaveBeenCalledTimes(2)
      gather.dispose()
      doc.uninstall()
    } finally {
      vi.useRealTimers()
    }
  })

  it('pauses while the tab is hidden and runs the catch-up when visible again', async () => {
    vi.useFakeTimers()
    try {
      const h = harness()
      h.fetchFeed.mockResolvedValue({ notModified: true, etag: null, lastModified: null, feedTitle: null, items: [] })
      const { gather } = setup(h)
      gather.updateTask(gather.getState().tasks[0]!.id, { intervalMinutes: 60 })
      const doc = installFakeDocument()

      gather.start()
      await vi.advanceTimersByTimeAsync(50)
      expect(h.fetchFeed).toHaveBeenCalledTimes(1)

      // Hidden while the workbench stays open; the interval elapses with the
      // tick paused. Becoming visible again runs the one overdue catch-up.
      doc.setVisibility('hidden')
      vi.setSystemTime(Date.now() + 61 * 60_000)
      doc.setVisibility('visible')
      await vi.advanceTimersByTimeAsync(50)
      expect(h.fetchFeed).toHaveBeenCalledTimes(2)

      // Still visible and nothing overdue: visibility flips do not re-run.
      doc.setVisibility('hidden')
      doc.setVisibility('visible')
      await vi.advanceTimersByTimeAsync(50)
      expect(h.fetchFeed).toHaveBeenCalledTimes(2)

      gather.dispose()
      doc.uninstall()
    } finally {
      vi.useRealTimers()
    }
  })
})
