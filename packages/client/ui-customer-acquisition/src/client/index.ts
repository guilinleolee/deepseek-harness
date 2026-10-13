/**
 * Customer-acquisition panel plugin, browser half. Self-contained Remote
 * assembly: this plugin mounts the host contribution (`customerAcquisition`)
 * through `ctx.remote.$mount()` — the pattern api-remotes and
 * ui-content-studio established — so the panel carries its server face with
 * it. Two registrations install atomically for their declarations'
 * lifetimes: the sidebar entry fills ui-sidebar's `sidebar.footer.action`
 * hole and the eight-page workbench fills ui-layout's additive
 * `shell.overlay` hole; both share one open/close controller created here.
 */
import type { Context } from '@deepseek-ai/cordis'
import customerAcquisitionRemote from '@deepseek-ai/dsh-customer-acquisition/remote'
// Type-only: pulls ui-renderer's SlotRegistry service merge (ctx.slots) in.
import type {} from '@deepseek-ai/dsh-client-ui-renderer/client'
// Type-only: pulls ui-layout's SlotMap merge ('shell.overlay') into this
// program so the surface registration below typechecks.
import type {} from '@deepseek-ai/dsh-client-ui-layout/client'
// Type-only: pulls ui-sidebar's SlotMap merge ('sidebar.footer.action').
import type {} from '@deepseek-ai/dsh-client-ui-sidebar/client'
// Type-only: pulls the locale plugin's Context merge (ctx.locale).
import type {} from '@deepseek-ai/dsh-client-locale/client'
import { AcquisitionEntry } from './AcquisitionEntry.tsx'
import { AcquisitionWorkbench } from './AcquisitionWorkbench.tsx'
import type { WorkbenchInjected } from './injected.ts'
import { createPanelController } from './panel-controller.ts'
import { en, zh, type AcquisitionKey } from './locales.ts'

export { createPanelController, type PanelController } from './panel-controller.ts'
export { AcquisitionWorkbench, type AcquisitionWorkbenchProps, type WorkbenchPage } from './AcquisitionWorkbench.tsx'
export type { WorkbenchInjected } from './injected.ts'
export type { AcquisitionEntryProps } from './AcquisitionEntry.tsx'
export type { AcquisitionKey } from './locales.ts'


declare module '@deepseek-ai/dsh-client-ui-slots' {
  interface LocaleNamespaceMap {
    /** Acquisition panel copy: entry, workbench pages. */
    'customer-acquisition': AcquisitionKey
  }
}

/** Dictionary namespace owned by this plugin. */
const NS = 'customer-acquisition'

/**
 * Services required by the panel plugin. The Remote namespace is mounted by
 * this plugin's own apply (not waited on as a service): the mount completes
 * before the slot registrations below run.
 */
export const inject = ['slots', 'locale', 'remote']

/**
 * Unwrap one Typert remote envelope, naming the failed call in the error.
 * @param label - the remote method identity for the error message.
 * @param call - the pending remote call.
 * @returns the unwrapped value.
 */
type RpcCall<T> = Promise<{ ok: true; value: T } | { ok: false; error: { code: string; message: string } }>

async function unwrap<T>(label: string, call: RpcCall<T>): Promise<T> {
  const result = await call
  if (!result.ok) throw new Error(`${label} failed: ${result.error.code}: ${result.error.message}`)
  return result.value
}

/**
 * Mount the plugin's own Remote contribution, then run the panel body on a
 * fiber that declares the namespace by its exact service name. Cordis
 * snapshots a namespace service only into fibers whose inject lists that
 * name (`remote.customerAcquisition`), so a consumer that merely injects
 * `remote` never resolves it. The mount runs first so the namespace service
 * exists before the panel fiber waits on it.
 * @param ctx - client root context.
 */
export async function apply(ctx: Context): Promise<() => Promise<void>> {
  ctx.effect(() => ctx.locale.register(NS, { zh, en }), 'ui-customer-acquisition: dictionaries')

  const mount = await ctx.remote.$mount(customerAcquisitionRemote)
  const surface = await ctx.plugin({
    name: 'ui-customer-acquisition:surface',
    inject: ['slots', 'locale', 'remote', 'remote.customerAcquisition'],
    apply: (surfaceCtx) => { mainApply(surfaceCtx) },
  })

  return async () => {
    await surface.dispose()
    await mount()
  }
}

/**
 * The panel body: the shared controller, the unwrapped Remote gateway
 * closures behind the workbench's pages, and the two slot registrations
 * (sidebar entry + frame-wide surface), on the fiber that declared the
 * Remote namespace. The `slots.inject` generator owns the registrations'
 * lifetime, so there is no separate disposer.
 * @param ctx - the panel fiber's context.
 */
function mainApply(ctx: Context): void {
  const panel = createPanelController()
  const face = ctx.remote.customerAcquisition
  const injected: Omit<WorkbenchInjected, 'panel'> = {
    getOverview: request => unwrap('customerAcquisition.getOverview', face.getOverview(request)),
    listLeads: request => unwrap('customerAcquisition.listLeads', face.listLeads(request)),
    listScoreRuns: request => unwrap('customerAcquisition.listScoreRuns', face.listScoreRuns(request)),
    listIcpProfiles: enabledOnly => unwrap('customerAcquisition.listIcpProfiles', face.listIcpProfiles(enabledOnly)),
    listScoreTemplates: enabledOnly => unwrap('customerAcquisition.listScoreTemplates', face.listScoreTemplates(enabledOnly)),
    listGeoScans: limit => unwrap('customerAcquisition.listGeoScans', face.listGeoScans(limit)),
    getGeoReport: reportId => unwrap('customerAcquisition.getGeoReport', face.getGeoReport(reportId)),
    listGeneratedContents: request => unwrap('customerAcquisition.listGeneratedContents', face.listGeneratedContents(request)),
    listContentTemplates: filters => unwrap('customerAcquisition.listContentTemplates', face.listContentTemplates(filters)),
    listSopTasks: request => unwrap('customerAcquisition.listSopTasks', face.listSopTasks(request)),
    listSopTemplates: enabledOnly => unwrap('customerAcquisition.listSopTemplates', face.listSopTemplates(enabledOnly)),
    getSettings: () => unwrap('customerAcquisition.getSettings', face.getSettings()),
    updateSettings: patch => unwrap('customerAcquisition.updateSettings', face.updateSettings(patch)),
    listAuditLogs: () => unwrap('customerAcquisition.listAuditLogs', face.listAuditLogs({ limit: 10 })),
  }

  ctx.slots.inject('sidebar.footer.action', function* () {
    yield ctx.slots.register({
      name: 'sidebar.footer.action',
      id: 'customer-acquisition-entry',
      locale: NS,
      inject: () => ({ panel }),
    }, AcquisitionEntry)
    yield ctx.slots.register({
      name: 'shell.overlay',
      id: 'customer-acquisition',
      order: 51,
      locale: NS,
      inject: () => ({ panel, ...injected }),
    }, AcquisitionWorkbench)
  })
}
