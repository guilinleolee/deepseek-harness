/**
 * Package-owned invariant companion for `@deepseek-ai/dsh-customer-acquisition-geo`.
 * @module @deepseek-ai/dsh-customer-acquisition-geo/invariant
 */

/* jscpd:ignore-start */
import type { Context } from '@deepseek-ai/cordis'
import type { InvariantInstaller } from '@deepseek-ai/dsh-invariants'

const PACKAGE_NAME = '@deepseek-ai/dsh-customer-acquisition-geo'

/** Cordis companion plugin name. */
export const name = 'customer-acquisition-geo-invariant'
/** Service required before the companion can reserve package ownership. */
export const inject = ['invariants']

/**
 * The owned relationship under watch: this package provides the
 * `geoDiagnosis` service, the only writer of `geo_reports` records, and its
 * every completed scan appends a `geo.scan.start` audit record through the
 * main plugin's audit table. No separate authority writes either surface.
 */
const install: InvariantInstaller = Object.assign(() => {}, { inject: ['geoDiagnosis'] })

/**
 * Register this package's invariant companion.
 * @param ctx - Cordis context carrying the invariant service.
 * @returns the installed registration's disposer after setup succeeds.
 */
export const apply = (ctx: Context): Promise<() => void> =>
  Promise.resolve(ctx.invariants.register(PACKAGE_NAME, install))
/* jscpd:ignore-end */
