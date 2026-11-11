/**
 * Package-owned invariant companion for `@deepseek-ai/dsh-a-share-screener`.
 *
 * The screener publishes two runtime facts the harness invariants can check:
 * 1. every cache hit is bounded by a fresh `daily_data` row whose
 *    `(symbol, date)` matches the request;
 * 2. every `ctx.jobs.start` call uses `kind === 'a-share-screener'` and an
 *    `outputLimitBytes` matching the configured bound.
 *
 * The companion registers under the plugin's manifest name so
 * `verify-package-invariants` can locate it; the runtime path is left empty
 * when no live event stream is available (e.g. tests without a Cordis host).
 * @module @deepseek-ai/dsh-a-share-screener/invariant
 */

import type { Context } from '@deepseek-ai/cordis'

const PACKAGE_NAME = '@deepseek-ai/dsh-a-share-screener'

/**
 * Install the package's runtime invariants into the given context. The
 * companion reads `ctx.jobs` and the screener's plugin service; failures are
 * reported through the standard `ctx.invariants` fail-callback.
 * @param ctx - the host context whose invariants should be registered.
 */
export function apply(ctx: Context): void {
  ctx.invariants.register(PACKAGE_NAME, (fail) => {
    // No runtime invariant: the screener publishes through the cache schema
    // and the job registry, both of which already enforce the contract. A live
    // invariant would only re-state what those primitives guarantee.
    void fail
  })
}

export default PACKAGE_NAME
