/**
 * Package-owned invariant companion for `@deepseek-ai/dsh-experimental-skill-index`.
 *
 * No runtime invariant: this package reads jsonl files off the filesystem and
 * keeps one in-memory snapshot that consumers query synchronously. There is no
 * authoritative event stream or mutable data stream to cross-check.
 *
 * @module @deepseek-ai/dsh-experimental-skill-index/invariant
 */

import type { Context } from '@deepseek-ai/cordis'
import type { InvariantInstaller } from '@deepseek-ai/dsh-invariants'

const PACKAGE_NAME = '@deepseek-ai/dsh-experimental-skill-index'

/** Cordis companion plugin name. */
export const name = 'skill-index-invariant'
/** Service required before the companion can reserve package ownership. */
export const inject = ['invariants']

/**
 * No runtime invariant: the snapshot is rebuilt only by callers invoking
 * `loadAll()`, which does not touch an event stream the harness could observe.
 * Consumers that need change notifications should listen on their own bus.
 */
const install: InvariantInstaller = () => {}

/**
 * Register this package's invariant companion.
 * @param ctx - Cordis context carrying the invariant service.
 * @returns the installed registration's disposer after setup succeeds.
 */
export const apply = (ctx: Context): Promise<() => void> =>
  Promise.resolve(ctx.invariants.register(PACKAGE_NAME, install))
