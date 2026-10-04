/**
 * Quant-research panel plugin, browser half. Phase 1 is a self-contained
 * placeholder: two registrations install atomically for their declarations'
 * lifetimes — the sidebar entry fills ui-sidebar's `sidebar.footer.action`
 * hole and the placeholder surface fills ui-layout's additive
 * `shell.overlay` hole; both share one open/close controller created here.
 * The Remote face arrives with the phase-2 panel (the core package exposes
 * no Remote contribution yet).
 * @module @deepseek-ai/dsh-client-ui-quant-research/client
 */
import type { Context } from '@deepseek-ai/cordis'
// Type-only: pulls ui-layout's SlotMap merge ('shell.overlay') into this
// program so the surface registration below typechecks.
import type {} from '@deepseek-ai/dsh-client-ui-layout/client'
// Type-only: pulls ui-sidebar's SlotMap merge ('sidebar.footer.action').
import type {} from '@deepseek-ai/dsh-client-ui-sidebar/client'
import { QuantEntry } from './QuantEntry.tsx'
import { QuantPanel } from './QuantPanel.tsx'
import { createPanelController } from './panel-controller.ts'

export { createPanelController, type PanelController } from './panel-controller.ts'
export type { QuantEntryProps } from './QuantEntry.tsx'
export type { QuantPanelProps } from './QuantPanel.tsx'

/**
 * Services required by the panel plugin. No Remote namespace yet — the
 * placeholder reads nothing from the server.
 */
export const inject = ['slots'] as const

/**
 * Register the two slot registrations on the plugin's own fiber; the
 * `slots.inject` generator owns their lifetime, so the disposer is a no-op.
 * @param ctx - client root context.
 * @returns the plugin disposer.
 */
export function apply(ctx: Context): Promise<() => Promise<void>> {
  const panel = createPanelController()
  // The `slots.inject` generator owns the registrations' lifetime, so the
  // disposer is a no-op; the promise shape stays for the plugin contract.
  ctx.slots.inject('sidebar.footer.action', function* () {
    yield ctx.slots.register({
      name: 'sidebar.footer.action',
      id: 'quant-research-entry',
      inject: () => ({ panel }),
    }, QuantEntry)
    yield ctx.slots.register({
      name: 'shell.overlay',
      id: 'quant-research',
      order: 52,
      inject: () => ({ panel }),
    }, QuantPanel)
  })
  return Promise.resolve(() => Promise.resolve())
}
