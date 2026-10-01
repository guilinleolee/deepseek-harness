import { Context } from '@deepseek-ai/cordis'
import { describe, expect, it, vi } from 'vitest'
import { SlotRegistry } from '@deepseek-ai/dsh-client-runtime/client'
import { LocaleRuntime } from '@deepseek-ai/dsh-client-locale/client'
import { apply, inject } from '@deepseek-ai/dsh-client-ui-content-studio/client'
import { ContentStudio } from '../src/client/ContentStudio.tsx'
import { StudioEntry } from '../src/client/StudioEntry.tsx'

async function bench() {
  const ctx = new Context()
  await ctx.plugin(SlotRegistry).await()
  const locale = new LocaleRuntime(ctx)
  // These specs assert the shipped Chinese copy. There is no jsdom `window`
  // in this lane, so browser-language detection never runs and the locale
  // comes from FALLBACK_LOCALE (en): state the asserted locale explicitly.
  locale.setLocale('zh')
  ctx.provide('locale', locale)
  const list = vi.fn(async () => ({
    ok: true as const,
    value: { root: '/outputs', projects: [], problems: [] },
  }))
  const scheduleList = vi.fn(async () => ({
    ok: true as const,
    value: { file: '/outputs/_schedule.json', items: [], problems: [] },
  }))
  const schedule = { list: scheduleList, put: vi.fn(), remove: vi.fn() }
  const topicsList = vi.fn(async () => ({
    ok: true as const,
    value: { file: '/outputs/_topics.json', items: [], problems: [] },
  }))
  const topics = { list: topicsList, put: vi.fn(), delete: vi.fn() }
  // The real mount provides each namespace as its own Cordis service
  // (`remote.<namespace>`); the workbench fiber declares those names in its
  // inject and only starts once every one of them is available.
  const NAMESPACE_SERVICES: Record<string, Record<string, unknown>> = {
    '@deepseek-ai/dsh-content-outputs': { list },
    '@deepseek-ai/dsh-content-schedule': schedule,
    '@deepseek-ai/dsh-content-topics': topics,
  }
  const NAMESPACE_NAMES: Record<string, string> = {
    '@deepseek-ai/dsh-content-outputs': 'remote.contentOutputs',
    '@deepseek-ai/dsh-content-schedule': 'remote.contentSchedule',
    '@deepseek-ai/dsh-content-topics': 'remote.contentTopics',
  }
  const mounted: Array<() => void> = []
  const $mount = vi.fn(async (contribution: { package: string }) => {
    const name = NAMESPACE_NAMES[contribution.package]
    if (name === undefined) throw new Error(`unexpected contribution ${contribution.package}`)
    const dispose = ctx.provide(name, NAMESPACE_SERVICES[contribution.package])
    mounted.push(dispose)
    return async () => { dispose() }
  })
  // The real gateway service resolves `remote.<namespace>` reads through the
  // calling context; the getters stand in for that traced indirection.
  ctx.provide('remote', {
    $mount,
    // The test context has no typert type merge, so these traced reads are
    // untyped by construction. oxlint-disable typescript/no-unsafe-return
    get contentOutputs() { return ctx.get('remote.contentOutputs') },
    // oxlint-disable-next-line typescript/no-unsafe-return
    get contentSchedule() { return ctx.get('remote.contentSchedule') },
    // oxlint-disable-next-line typescript/no-unsafe-return
    get contentTopics() { return ctx.get('remote.contentTopics') },
  })
  return { ctx, slots: ctx.get('slots') as SlotRegistry, locale, list, $mount, topicsList, mounted }
}

/** Declare both target holes with a single root registration ('root' is a single slot). */
function declare(slots: SlotRegistry): () => void {
  return slots.register({
    name: 'root',
    children: {
      'sidebar.footer.action': { kind: 'list', scope: 'root' },
      'shell.overlay': { kind: 'list', scope: 'root' },
    },
  } as never, () => null)
}

describe('ui-content-studio apply', () => {
  it('declares the services it drives', () => {
    expect(inject).toEqual(['slots', 'locale', 'remote'])
  })

  it('mounts its own Remote contributions before registering the slots', async () => {
    const before = await bench()
    declare(before.slots)
    await before.ctx.plugin({ inject: [...inject], apply }).await()
    // contentOutputs + contentSchedule + contentTopics (the topics face added
    // alongside the topic bank).
    expect(before.$mount).toHaveBeenCalledTimes(3)
    expect(before.slots.entries('sidebar.footer.action')[0]!.component).toBe(StudioEntry)
    expect(before.slots.entries('sidebar.footer.action')[0]!.options.id).toBe('content-studio-entry')
    expect(before.slots.entries('shell.overlay')[0]!.component).toBe(ContentStudio)
    expect(before.slots.entries('shell.overlay')[0]!.options.id).toBe('content-studio')
    // Copy rides the standard locale seat: the entries declare the namespace
    // and apply registered both dictionaries.
    expect(before.locale.bind('content-studio')('entry.label')).toBe('内容创作')

    const after = await bench()
    await after.ctx.plugin({ inject: [...inject], apply }).await()
    declare(after.slots)
    await Promise.resolve()
    expect(after.slots.entries('sidebar.footer.action')[0]!.component).toBe(StudioEntry)
    expect(after.slots.entries('shell.overlay')[0]!.component).toBe(ContentStudio)
  })

  it('injects one shared controller plus the library read into the registrations', async () => {
    const { ctx, slots, list, topicsList } = await bench()
    declare(slots)
    await ctx.plugin({ inject: [...inject], apply }).await()
    const entry = slots.entries('sidebar.footer.action')[0]!
    const surface = slots.entries('shell.overlay')[0]!
    const entryFace = entry.inject?.() as { studio: { open(): void; isOpen(): boolean } }
    const surfaceFace = surface.inject?.() as {
      studio: { isOpen(): boolean }
      listOutputs: () => Promise<{ root: string }>
      topics: { list: () => Promise<{ file: string }> }
      gather: {
        getState(): { sources: unknown[] }
        start(): void
        dispose(): void
      }
    }
    expect(surfaceFace.studio.isOpen()).toBe(false)
    entryFace.studio.open()
    expect(surfaceFace.studio.isOpen()).toBe(true)
    // The gather controller rides the same inject: one scheduler per surface,
    // sources empty on first launch, and the lifecycle verbs present.
    expect(typeof surfaceFace.gather.start).toBe('function')
    expect(typeof surfaceFace.gather.dispose).toBe('function')
    expect(surfaceFace.gather.getState().sources).toEqual([])
    // The library read wraps the contentOutputs Remote and unwraps the
    // envelope: the snapshot passes through, failures throw.
    await expect(surfaceFace.listOutputs()).resolves.toEqual({
      root: '/outputs', projects: [], problems: [],
    })
    expect(list).toHaveBeenCalledTimes(1)
    // The topic bank rides the same unwrapping pattern over contentTopics.
    await expect(surfaceFace.topics.list()).resolves.toEqual({ file: '/outputs/_topics.json', items: [], problems: [] })
    expect(topicsList).toHaveBeenCalledTimes(1)
  })

  it('drops both registrations when the declaration collapses', async () => {
    const { ctx, slots } = await bench()
    const dispose = declare(slots)
    await ctx.plugin({ inject: [...inject], apply }).await()
    dispose()
    await Promise.resolve()
    expect(slots.entries('sidebar.footer.action')).toEqual([])
    expect(slots.entries('shell.overlay')).toEqual([])
  })
})
