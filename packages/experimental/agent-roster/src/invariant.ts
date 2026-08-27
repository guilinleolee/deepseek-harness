/**
 * Package-owned invariant companion for `@deepseek-ai/dsh-experimental-agent-roster`.
 *
 * No runtime invariant: this package reads markdown files off the filesystem
 * and keeps one in-memory roster that consumers query synchronously. There is
 * no authoritative event stream or mutable data stream to cross-check.
 *
 * @module @deepseek-ai/dsh-experimental-agent-roster/invariant
 */

import type { Context } from '@deepseek-ai/cordis'
import type { InvariantInstaller } from '@deepseek-ai/dsh-invariants'

const PACKAGE_NAME = '@deepseek-ai/dsh-experimental-agent-roster'

/** Cordis companion plugin name. */
export const name = 'agent-roster-invariant'
/** Service required before the companion can reserve package ownership. */
export const inject = ['invariants']

/** No runtime invariant: roster entries are derived from disk-only state. */
const install: InvariantInstaller = () => {}

/**
 * Register this package's invariant companion.
 * @param ctx - Cordis context carrying the invariant service.
 * @returns the installed registration's disposer after setup succeeds.
 */
export const apply = (ctx: Context): Promise<() => void> =>
  Promise.resolve(ctx.invariants.register(PACKAGE_NAME, install))
