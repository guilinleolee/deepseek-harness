/**
 * Quant-research panel plugin, browser half. Self-contained Remote
 * assembly: this plugin mounts the host contribution (`quantResearch`)
 * through `ctx.remote.$mount()` — the pattern api-remotes and
 * ui-customer-acquisition established — so the panel carries its server
 * face with it. Two registrations install atomically for their
 * declarations' lifetimes: the sidebar entry fills ui-sidebar's
 * `sidebar.footer.action` hole and the surface fills ui-layout's additive
 * `shell.overlay` hole; both share one open/close controller created here.
 * @module @deepseek-ai/dsh-client-ui-quant-research/client
 */
import type { Context } from '@deepseek-ai/cordis'
import type { TypertClientRemote } from '@deepseek-ai/dsh-typert-protocol'
import type { AccountListValue, NoteListValue } from '@deepseek-ai/dsh-quant-research/types'
import quantResearchRemote from '@deepseek-ai/dsh-quant-research/remote'
// Type-only: pulls ui-layout's SlotMap merge ('shell.overlay') into this
// program so the surface registration below typechecks.
import type {} from '@deepseek-ai/dsh-client-ui-layout/client'
// Type-only: pulls ui-sidebar's SlotMap merge ('sidebar.footer.action').
import type {} from '@deepseek-ai/dsh-client-ui-sidebar/client'
// Type-only: pulls the locale plugin's Context merge (ctx.locale).
import type {} from '@deepseek-ai/dsh-client-locale/client'
import { QuantEntry } from './QuantEntry.tsx'
import { QuantPanel, type QuantPanelInjected } from './QuantPanel.tsx'
import { createPanelController } from './panel-controller.ts'
import { en, zh, type QuantKey } from './locales.ts'

export { createPanelController, type PanelController } from './panel-controller.ts'
export type { QuantEntryProps } from './QuantEntry.tsx'
export type { QuantPanelInjected, QuantPanelProps } from './QuantPanel.tsx'
export type { QuantKey } from './locales.ts'

declare module '@deepseek-ai/cordis' {
  interface Context {
    /** Same carrier face api-remotes declares; identical merge is additive. */
    remote: TypertClientRemote
  }
}

declare module '@deepseek-ai/dsh-client-ui-slots' {
  interface LocaleNamespaceMap {
    /** Quant-research panel copy: entry, surface. */
    'quant-research': QuantKey
  }
}

/** Dictionary namespace owned by this plugin. */
const NS = 'quant-research'

/**
 * Services required by the panel plugin. The Remote namespace is mounted by
 * this plugin's own apply (not waited on as a service): the mount completes
 * before the slot registrations below run.
 */
export const inject = ['slots', 'locale', 'remote'] as const

/** Unwrapped Remote envelope shape (structural with the wire protocol). */
type RpcCall<T> = Promise<{ ok: true; value: T } | { ok: false; error: { code: string; message: string } }>

/**
 * Unwrap one Typert remote envelope, naming the failed call in the error.
 * @param label - the remote method identity for the error message.
 * @param call - the pending remote call.
 * @returns the unwrapped value.
 */
async function unwrap<T>(label: string, call: RpcCall<T>): Promise<T> {
  const result = await call
  if (!result.ok) throw new Error(`${label} failed: ${result.error.code}: ${result.error.message}`)
  return result.value
}

/**
 * Mount the plugin's own Remote contribution, then run the panel body on a
 * fiber that declares the namespace by its exact service name. Cordis
 * snapshots a namespace service only into fibers whose inject lists that
 * name (`remote.quantResearch`), so a consumer that merely injects `remote`
 * never resolves it. The mount runs first so the namespace service exists
 * before the panel fiber waits on it.
 * @param ctx - client root context.
 * @returns the plugin disposer unwinding the surface and the mount.
 */
export async function apply(ctx: Context): Promise<() => Promise<void>> {
  ctx.effect(() => ctx.locale.register(NS, { zh, en }), 'ui-quant-research: dictionaries')

  const mount = await ctx.remote.$mount(quantResearchRemote)
  const surface = await ctx.plugin({
    name: 'ui-quant-research:surface',
    inject: ['slots', 'locale', 'remote', 'remote.quantResearch'],
    apply: (surfaceCtx) => { mainApply(surfaceCtx) },
  })

  return async () => {
    await surface.dispose()
    await mount()
  }
}

/**
 * The panel body: the shared controller, the gateway closures, and the two
 * slot registrations (sidebar entry + frame-wide surface), on the fiber
 * that declared the Remote namespace. The `slots.inject` generator owns the
 * registrations' lifetime, so there is no separate disposer.
 * @param ctx - the panel fiber's context.
 */
function mainApply(ctx: Context): void {
  const panel = createPanelController()
  const listAccounts: QuantPanelInjected['listAccounts'] = () =>
    unwrap('quantResearch.listAccounts', ctx.remote.quantResearch.listAccounts())
  const listNotes: QuantPanelInjected['listNotes'] = (): Promise<NoteListValue> =>
    unwrap('quantResearch.listNotes', ctx.remote.quantResearch.listNotes())
  const getAccountState: QuantPanelInjected['getAccountState'] = (ref: { name?: string; account_id?: string }) =>
    unwrap('quantResearch.getAccountState', ctx.remote.quantResearch.getAccountState(ref))

  ctx.slots.inject('sidebar.footer.action', function* () {
    yield ctx.slots.register({
      name: 'sidebar.footer.action',
      id: 'quant-research-entry',
      locale: NS,
      inject: () => ({ panel }),
    }, QuantEntry)
    yield ctx.slots.register({
      name: 'shell.overlay',
      id: 'quant-research',
      order: 52,
      locale: NS,
      inject: () => ({ panel, listAccounts, listNotes, getAccountState }),
    }, QuantPanel)
  })
}

/** Re-exported for consumers typing against the wire shapes. */
export type { AccountListValue, NoteListValue }
