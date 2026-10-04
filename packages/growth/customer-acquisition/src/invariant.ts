/**
 * Package-owned invariant companion for `@deepseek-ai/dsh-customer-acquisition`.
 * @module @deepseek-ai/dsh-customer-acquisition/invariant
 */

/* jscpd:ignore-start */
import type { Context } from '@deepseek-ai/cordis'
import type { InvariantInstaller } from '@deepseek-ai/dsh-invariants'

const PACKAGE_NAME = '@deepseek-ai/dsh-customer-acquisition'

/** Cordis companion plugin name. */
export const name = 'customer-acquisition-invariant'
/** Service required before the companion can reserve package ownership. */
export const inject = ['invariants']

/**
 * The owned relationship under watch: this package provides both the
 * `permissionContext` seam (its local provider is the only in-tree
 * implementation) and the `customerAcquisition` service whose every mutation
 * appends to the audit log. No separate authority writes either key.
 */
const install: InvariantInstaller = Object.assign(() => {}, { inject: ['permissionContext', 'customerAcquisition'] })

/**
 * Register this package's invariant companion.
 * @param ctx - Cordis context carrying the invariant service.
 * @returns the installed registration's disposer after setup succeeds.
 */
export const apply = (ctx: Context): Promise<() => void> =>
  Promise.resolve(ctx.invariants.register(PACKAGE_NAME, install))
/* jscpd:ignore-end */
