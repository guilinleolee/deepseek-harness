import { Context } from '@deepseek-ai/cordis'
import { describe, expect, it, vi } from 'vitest'
import { SlotRegistry } from '@deepseek-ai/dsh-client-runtime/client'
import { LocaleRuntime } from '@deepseek-ai/dsh-client-locale/client'
import { apply, inject } from '@deepseek-ai/dsh-client-ui-customer-acquisition/client'
import { AcquisitionEntry } from '../src/client/AcquisitionEntry.tsx'
import { AcquisitionPanel } from '../src/client/AcquisitionPanel.tsx'
import type { PanelController } from '../src/client/panel-controller.ts'

async function bench() {
  const ctx = new Context()
  await ctx.plugin(SlotRegistry).await()
  const locale = new LocaleRuntime(ctx)
  locale.setLocale('zh')
  ctx.provide('locale', locale)
  const mounted: Array<() => void> = []
  const $mount = vi.fn(async (contribution: { package: string }) => {
    if (contribution.package !== '@deepseek-ai/dsh-customer-acquisition') {
      throw new Error(`unexpected contribution ${contribution.package}`)
    }
    const dispose = ctx.provide('remote.customerAcquisition', {
      getSettings: vi.fn(async () => ({
        ok: true as const,
        value: { settings: { geo_max_pages: 10, geo_page_timeout_ms: 10_000, sop_todo_write_enabled: true } },
      })),
      listAuditLogs: vi.fn(async () => ({ ok: true as const, value: { items: [], total: 0 } })),
    })
    mounted.push(dispose)
    return async () => { dispose() }
  })
  ctx.provide('remote', {
    $mount,
    // oxlint-disable-next-line typescript/no-unsafe-return -- test double resolves the mounted namespace from the untyped context.
    get customerAcquisition() { return ctx.get('remote.customerAcquisition') },
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

describe('ui-customer-acquisition apply', () => {
  it('declares the services it drives', () => {
    expect(inject).toEqual(['slots', 'locale', 'remote'])
  })

  it('mounts the Remote contribution before registering the two slots', async () => {
    const before = await bench()
    declare(before.slots)
    await before.ctx.plugin({ inject: [...inject], apply }).await()
    expect(before.$mount).toHaveBeenCalledTimes(1)
    expect(before.slots.entries('sidebar.footer.action')[0]!.component).toBe(AcquisitionEntry)
    expect(before.slots.entries('sidebar.footer.action')[0]!.options.id).toBe('customer-acquisition-entry')
    expect(before.slots.entries('shell.overlay')[0]!.component).toBe(AcquisitionPanel)
    expect(before.slots.entries('shell.overlay')[0]!.options.id).toBe('customer-acquisition')
    expect(before.locale.bind('customer-acquisition')('entry.label')).toBe('获客运营')

    const after = await bench()
    await after.ctx.plugin({ inject: [...inject], apply }).await()
    declare(after.slots)
    await Promise.resolve()
    expect(after.slots.entries('sidebar.footer.action')[0]!.component).toBe(AcquisitionEntry)
    expect(after.slots.entries('shell.overlay')[0]!.component).toBe(AcquisitionPanel)
  })

  it('injects the shared controller and the two unwrapped gateway reads', async () => {
    const { ctx, slots } = await bench()
    declare(slots)
    await ctx.plugin({ inject: [...inject], apply }).await()
    const surface = slots.entries('shell.overlay')[0]!
    const face = surface.inject?.() as {
      panel: PanelController
      getSettings: () => Promise<{ settings: { geo_max_pages: number } }>
      listAuditLogs: () => Promise<{ total: number }>
    }
    expect(face.panel.isOpen()).toBe(false)
    face.panel.open()
    expect(face.panel.isOpen()).toBe(true)
    await expect(face.getSettings()).resolves.toMatchObject({ settings: { geo_max_pages: 10 } })
    await expect(face.listAuditLogs()).resolves.toMatchObject({ total: 0 })
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
