import { describe, expect, it, vi } from 'vitest'
import { Context } from '@deepseek-ai/cordis'
import { SlotRegistry } from '@deepseek-ai/dsh-client-ui-renderer/client'
import { LocaleRuntime } from '@deepseek-ai/dsh-client-locale/client'
import { apply, inject } from '@deepseek-ai/dsh-client-ui-quant-research/client'
import { apply as nodeApply } from '../src/index.ts'
import { QuantEntry } from '../src/client/QuantEntry.tsx'
import { QuantPanel } from '../src/client/QuantPanel.tsx'
import type { PanelController } from '../src/client/panel-controller.ts'

/** Compose the bench: slots + locale + a fake Remote carrier with the namespace mounted. */
async function bench() {
  const ctx = new Context()
  await ctx.plugin(SlotRegistry).await()
  const locale = new LocaleRuntime(ctx)
  locale.setLocale('zh')
  ctx.provide('locale', locale)
  const mounted: Array<() => void> = []
  const $mount = vi.fn(async (contribution: { package: string }) => {
    if (contribution.package !== '@deepseek-ai/dsh-quant-research') {
      throw new Error(`unexpected contribution ${contribution.package}`)
    }
    const dispose = ctx.provide('remote.quantResearch', {
      listAccounts: vi.fn(async () => ({ ok: true as const, value: { accounts: [] } })),
      listNotes: vi.fn(async () => ({ ok: true as const, value: { notes: [] } })),
      getAccountState: vi.fn(async () => ({ ok: true as const, value: { account_id: 'a', name: 'n', cash: 0, initial_cash: 0, equity: 0, positions: [] } })),
    })
    mounted.push(dispose)
    return async () => { dispose() }
  })
  ctx.provide('remote', {
    $mount,
    get quantResearch() { return ctx.get('remote.quantResearch') },
  } as never)
  return { ctx, slots: ctx.get('slots') as SlotRegistry, locale, $mount, mounted }
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

describe('ui-quant-research apply', () => {
  it('declares the services it drives', () => {
    expect(inject).toEqual(['slots', 'locale', 'remote'])
  })

  it('mounts the Remote contribution before registering the two slots', async () => {
    const before = await bench()
    declare(before.slots)
    await before.ctx.plugin({ inject: [...inject], apply }).await()
    expect(before.$mount).toHaveBeenCalledTimes(1)
    expect(before.slots.entries('sidebar.footer.action')[0]!.component).toBe(QuantEntry)
    expect(before.slots.entries('sidebar.footer.action')[0]!.options.id).toBe('quant-research-entry')
    expect(before.slots.entries('shell.overlay')[0]!.component).toBe(QuantPanel)
    expect(before.slots.entries('shell.overlay')[0]!.options.id).toBe('quant-research')
    expect(before.locale.bind('quant-research')('entry.label')).toBe('量化研究')

    const after = await bench()
    await after.ctx.plugin({ inject: [...inject], apply }).await()
    declare(after.slots)
    await Promise.resolve()
    expect(after.slots.entries('sidebar.footer.action')[0]!.component).toBe(QuantEntry)
    expect(after.slots.entries('shell.overlay')[0]!.component).toBe(QuantPanel)
  })

  it('injects the shared controller and the unwrapped gateway reads', async () => {
    const { ctx, slots } = await bench()
    declare(slots)
    await ctx.plugin({ inject: [...inject], apply }).await()
    const surface = slots.entries('shell.overlay')[0]!
    const face = surface.inject?.() as {
      panel: PanelController
      listAccounts: () => Promise<{ accounts: unknown[] }>
      listNotes: () => Promise<{ notes: unknown[] }>
      getAccountState: (ref: { account_id?: string }) => Promise<{ account_id: string }>
    }
    expect(face.panel.isOpen()).toBe(false)
    face.panel.open()
    expect(face.panel.isOpen()).toBe(true)
    await expect(face.listAccounts()).resolves.toMatchObject({ accounts: [] })
    await expect(face.listNotes()).resolves.toMatchObject({ notes: [] })
    await expect(face.getAccountState({ account_id: 'a' })).resolves.toMatchObject({ account_id: 'a' })
    const entry = slots.entries('sidebar.footer.action')[0]!
    const entryFace = entry.inject?.() as { panel: PanelController }
    expect(entryFace.panel.isOpen()).toBe(true) // shared controller, opened above
  })

  it('unwraps remote failures with the method identity and unwinds on dispose', async () => {
    const ctx = new Context()
    await ctx.plugin(SlotRegistry).await()
    const locale = new LocaleRuntime(ctx)
    locale.setLocale('zh')
    ctx.provide('locale', locale)
    let unmounted = false
    const $mount = vi.fn(async () => async () => { unmounted = true })
    ctx.provide('remote', {
      $mount,
      get quantResearch() { return ctx.get('remote.quantResearch') },
    } as never)
    const disposeNamespace = ctx.provide('remote.quantResearch', {
      listAccounts: vi.fn(async () => ({ ok: false as const, error: { code: 'DATA', message: 'boom' } })),
      listNotes: vi.fn(async () => ({ ok: true as const, value: { notes: [] } })),
      getAccountState: vi.fn(async () => ({ ok: true as const, value: { account_id: 'a', name: 'n', cash: 0, initial_cash: 0, equity: 0, positions: [] } })),
    })
    declare(ctx.get('slots') as SlotRegistry)
    const fiber = await ctx.plugin({ inject: [...inject], apply }).await()
    const surface = (ctx.get('slots') as SlotRegistry).entries('shell.overlay')[0]!
    const face = surface.inject?.() as {
      panel: PanelController
      listAccounts: () => Promise<{ accounts: unknown[] }>
    }
    await expect(face.listAccounts()).rejects.toThrow('quantResearch.listAccounts failed: DATA: boom')
    await fiber.dispose()
    expect(unmounted).toBe(true)
    disposeNamespace()
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

describe('node half', () => {
  it('exposes no host-side behavior', () => {
    nodeApply() // reaching here without throwing is the no-op contract
  })
})
