/**
 * Package-owned invariant companion for `@deepseek-ai/dsh-experimental-license-policy`.
 *
 * No runtime invariant: this package is a pure decision table with no event
 * stream, mutable data, or filesystem access. Consumers feed it license
 * strings; the policy returns a typed decision. The package participates in
 * the HMR-safety test through its Service registration.
 *
 * @module @deepseek-ai/dsh-experimental-license-policy/invariant
 */

import type { Context } from '@deepseek-ai/cordis'
import type { InvariantInstaller } from '@deepseek-ai/dsh-invariants'

const PACKAGE_NAME = '@deepseek-ai/dsh-experimental-license-policy'

/** Cordis companion plugin name. */
export const name = 'license-policy-invariant'
/** Service required before the companion can reserve package ownership. */
export const inject = ['invariants']

/** No runtime invariant: tier-to-decision is a closed pure function. */
const install: InvariantInstaller = () => {}

/**
 * Register this package's invariant companion.
 * @param ctx - Cordis context carrying the invariant service.
 * @returns the installed registration's disposer after setup succeeds.
 */
export const apply = (ctx: Context): Promise<() => void> =>
  Promise.resolve(ctx.invariants.register(PACKAGE_NAME, install))
