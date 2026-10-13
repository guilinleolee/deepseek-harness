/**
 * Dual-face typert Remote bridge — CLIENT face (M1 skeleton).
 *
 * M2: import the generated `/remote` artifact and mount it so the browser can
 * call the Host endpoints:
 *
 * ```ts
 * import { trajectoryDebugRemote } from 'dsh-trajectory-debug-remotes/remote'
 * export function apply(ctx: Context) {
 *   ctx.effect(() => ctx.remote.$mount(trajectoryDebugRemote))
 * }
 * ```
 *
 * `ctx.remote.$mount` is effect-owned: unload withdraws the contribution.
 *
 * @module dsh-trajectory-debug-remotes/client
 */

import type { Context } from '@deepseek-ai/cordis'

export const name = 'trajectory-debug-remotes-client'

/** Client entry. M1 keeps the row loadable; mount wiring is M2. */
export function apply(ctx: Context): void {
  ctx.effect(() => {
    // M2: ctx.remote.$mount(trajectoryDebugRemote)
    return () => undefined
  })
}
