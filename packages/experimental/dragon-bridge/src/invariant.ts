/**
 * Package-owned invariant companion for `@deepseek-ai/dsh-experimental-dragon-bridge`.
 *
 * No runtime invariant: the bridge joins three pure services (skill-index,
 * agent-roster, license-policy) into a single facade. The cache is rebuilt
 * only by `loadAll()`; no event stream observes its mutations.
 *
 * @module @deepseek-ai/dsh-experimental-dragon-bridge/invariant
 */

import type { Context } from '@deepseek-ai/cordis'
import type { InvariantInstaller } from '@deepseek-ai/dsh-invariants'

const PACKAGE_NAME = '@deepseek-ai/dsh-experimental-dragon-bridge'

/** Cordis companion plugin name. */
export const name = 'dragon-bridge-invariant'
/** Service required before the companion can reserve package ownership. */
export const inject = ['invariants']

/** No runtime invariant: cross-service facade with no observed mutations. */
const install: InvariantInstaller = () => {}

/**
 * Register this package's invariant companion.
 * @param ctx - Cordis context carrying the invariant service.
 * @returns the installed registration's disposer after setup succeeds.
 */
export const apply = (ctx: Context): Promise<() => void> =>
  Promise.resolve(ctx.invariants.register(PACKAGE_NAME, install))
