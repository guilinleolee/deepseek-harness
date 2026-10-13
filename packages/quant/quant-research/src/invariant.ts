/**
 * Package-owned invariant companion for `@deepseek-ai/dsh-quant-research`.
 * @module @deepseek-ai/dsh-quant-research/invariant
 */

/* jscpd:ignore-start */
import type { Context } from '@deepseek-ai/cordis'
import type { InvariantInstaller } from '@deepseek-ai/dsh-invariants'

const PACKAGE_NAME = '@deepseek-ai/dsh-quant-research'

/** Cordis companion plugin name. */
export const name = 'quant-research-invariant'
/** Service required before the companion can reserve package ownership. */
export const inject = ['invariants']

/**
 * No runtime invariant: the package's owned relationships — sole authority
 * over the `quant_` tool namespace, its `tools/pre-execute` research-only
 * gate, and the `quant_research` domain — are enforced where they run (the
 * gate denies, the domain single-opens), and the companion only reserves
 * package ownership; there is no cross-plugin relationship to re-assert here.
 */
const install: InvariantInstaller = Object.assign(() => {}, { inject: ['tools'] })

/**
 * Register this package's invariant companion.
 * @param ctx - Cordis context carrying the invariant service.
 * @returns the installed registration's disposer after setup succeeds.
 */
export const apply = (ctx: Context): Promise<() => void> =>
  Promise.resolve(ctx.invariants.register(PACKAGE_NAME, install))
/* jscpd:ignore-end */
