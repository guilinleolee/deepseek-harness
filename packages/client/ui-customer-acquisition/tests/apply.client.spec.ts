import { Context } from '@deepseek-ai/cordis'
import { describe, expect, it, vi } from 'vitest'
import { SlotRegistry } from '@deepseek-ai/dsh-client-runtime/client'
import { LocaleRuntime } from '@deepseek-ai/dsh-client-locale/client'
import { apply, inject } from '@deepseek-ai/dsh-client-ui-customer-acquisition/client'
import { AcquisitionEntry } from '../src/client/AcquisitionEntry.tsx'
import { AcquisitionWorkbench } from '../src/client/AcquisitionWorkbench.tsx'
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
    const ok = <T,>(value: T) => ({ ok: true as const, value })
    const dispose = ctx.provide('remote.customerAcquisition', {
      getOverview: vi.fn(async () => ok({ totals: null, breakdown: null })),
      listLeads: vi.fn(async () => ok({ items: [], total: 0 })),
      listScoreRuns: vi.fn(async () => ok({ items: [], total: 0 })),
      listIcpProfiles: vi.fn(async () => ok([])),
      listScoreTemplates: vi.fn(async () => ok([])),
      listGeoScans: vi.fn(async () => ok({ items: [], total: 0 })),
      getGeoReport: vi.fn(async () => ok({ report_md: '', score: 0 })),
      listGeneratedContents: vi.fn(async () => ok({ items: [], total: 0 })),
      listContentTemplates: vi.fn(async () => ok([])),
      listSopTasks: vi.fn(async () => ok({ items: [], total: 0 })),
      listSopTemplates: vi.fn(async () => ok([])),
      getSettings: vi.fn(async () => ok({
        settings: { geo_max_pages: 10, geo_page_timeout_ms: 10_000, sop_todo_write_enabled: true },
      })),
      updateSettings: vi.fn(async () => ok({
        settings: { geo_max_pages: 12, geo_page_timeout_ms: 10_000, sop_todo_write_enabled: true },
      })),
      listAuditLogs: vi.fn(async () => ok({ items: [], total: 0 })),
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
    expect(before.slots.entries('shell.overlay')[0]!.component).toBe(AcquisitionWorkbench)
    expect(before.slots.entries('shell.overlay')[0]!.options.id).toBe('customer-acquisition')
    expect(before.locale.bind('customer-acquisition')('entry.label')).toBe('获客运营')

    const after = await bench()
    await after.ctx.plugin({ inject: [...inject], apply }).await()
    declare(after.slots)
    await Promise.resolve()
    expect(after.slots.entries('sidebar.footer.action')[0]!.component).toBe(AcquisitionEntry)
    expect(after.slots.entries('shell.overlay')[0]!.component).toBe(AcquisitionWorkbench)
  })

  it('injects the shared controller and every unwrapped gateway read', async () => {
    const { ctx, slots } = await bench()
    declare(slots)
    await ctx.plugin({ inject: [...inject], apply }).await()
    const surface = slots.entries('shell.overlay')[0]!
    const face = surface.inject?.() as {
      panel: PanelController
      getSettings: () => Promise<{ settings: { geo_max_pages: number } }>
      updateSettings: (patch: { geo_max_pages: number }) => Promise<{ settings: { geo_max_pages: number } }>
      listAuditLogs: () => Promise<{ total: number }>
      getOverview: (request: { period: string }) => Promise<{ breakdown: null }>
      listLeads: () => Promise<{ total: number }>
      listScoreRuns: () => Promise<{ total: number }>
      listIcpProfiles: () => Promise<unknown[]>
      listScoreTemplates: () => Promise<unknown[]>
      listGeoScans: () => Promise<{ total: number }>
      getGeoReport: (reportId: string) => Promise<{ report_md: string }>
      listGeneratedContents: () => Promise<{ total: number }>
      listContentTemplates: () => Promise<unknown[]>
      listSopTasks: () => Promise<{ total: number }>
      listSopTemplates: () => Promise<unknown[]>
    }
    expect(face.panel.isOpen()).toBe(false)
    face.panel.open()
    expect(face.panel.isOpen()).toBe(true)
    await expect(face.getSettings()).resolves.toMatchObject({ settings: { geo_max_pages: 10 } })
    await expect(face.updateSettings({ geo_max_pages: 12 })).resolves.toMatchObject({ settings: { geo_max_pages: 12 } })
    await expect(face.listAuditLogs()).resolves.toMatchObject({ total: 0 })
    await expect(face.getOverview({ period: 'week' })).resolves.toMatchObject({ breakdown: null })
    await expect(face.listLeads()).resolves.toMatchObject({ total: 0 })
    await expect(face.listScoreRuns()).resolves.toMatchObject({ total: 0 })
    await expect(face.listIcpProfiles()).resolves.toEqual([])
    await expect(face.listScoreTemplates()).resolves.toEqual([])
    await expect(face.listGeoScans()).resolves.toMatchObject({ total: 0 })
    await expect(face.getGeoReport('r1')).resolves.toMatchObject({ report_md: '' })
    await expect(face.listGeneratedContents()).resolves.toMatchObject({ total: 0 })
    await expect(face.listContentTemplates()).resolves.toEqual([])
    await expect(face.listSopTasks()).resolves.toMatchObject({ total: 0 })
    await expect(face.listSopTemplates()).resolves.toEqual([])
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
