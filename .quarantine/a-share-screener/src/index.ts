/**
 * A-share quant screener DSH plugin. The plugin registers one model-facing
 * tool (`a_share_screen`) on `ctx.tools` and one skill (`stock-screener`)
 * on `ctx.skills`. The tool runs as a background producer through
 * `ctx.jobs.start` so a 5,000-symbol scan never times out the model call.
 *
 * Wiring assumptions (validated by the example at
 * `examples/a-share-screener/cordis.yml`):
 * - `ctx.tools`, `ctx.skills`, `ctx.credentials`, `ctx.jobs` are present in
 *   the host composition.
 * - `TUSHARE_TOKEN` is configured through `ctx.credentials`.
 *
 * Function-plugin form: `name`/`inject`/`Config`/`apply`, no default export
 * (see `packages/AGENTS.md`).
 * @module @deepseek-ai/dsh-a-share-screener
 */

import type { Context } from '@deepseek-ai/cordis'
import { credentialRef } from '@deepseek-ai/dsh-credentials'
import { defineScreenTool } from './tools/screen.ts'
import { registerStockScreenerSkill } from './skill/stock-screener.ts'
import { ScreenerService, openDefaultStore } from './service.ts'
import type { Config } from './types.ts'
import { TUSHARE_TOKEN_REF } from './types.ts'

export const name = 'dsh-a-share-screener'

/** Required services; topological order is enforced by the Cordis injector. */
export const inject = ['tools', 'skills', 'credentials', 'jobs'] as const

export type { Config } from './types.ts'
export type {
  Market,
  OHLCV,
  Quote,
  ScreenArgs,
  ScreenResult,
  StockBasicInfo,
  StockMatch,
  Universe,
} from './types.ts'

/**
 * Apply the plugin to a host context. The Tushare token check, the cache
 * backend selection, and the tool + skill registrations all run synchronously
 * here; the heavy lifting (token lookup, native binding probe) lives in
 * `ctx.effect` so a slow token resolve never blocks other plugins' apply.
 *
 * @param ctx - the host context.
 * @param config - configuration block from the composition row.
 */
export function apply(ctx: Context, config: Config): void {
  // Default to the in-memory store; the SQLite path is opted into via the
  // `ctx.effect` callback below so a missing native binding never breaks
  // plugin loading.
  const service = new ScreenerService({
    cacheRoot: config.cacheRoot,
    defaultLimit: config.defaultLimit,
    defaultUniverse: config.defaultUniverse,
    jobOutputLimitBytes: config.jobOutputLimitBytes,
    tokenRef: TUSHARE_TOKEN_REF,
  })

  ctx.effect((signal) => {
    signal.throwIfAborted()
    void (async () => {
      const tokenConfigured = await ctx.credentials.describe(credentialRef('TUSHARE_TOKEN')).then(
        (info) => info.configured,
        () => false,
      )
      if (!tokenConfigured) {
        ctx.logger.warn('a-share-screener: TUSHARE_TOKEN is not configured; tool calls will fail until set')
      }
      const { store, kind } = await openDefaultStore(config.cacheRoot)
      if (kind === 'memory') {
        ctx.logger.warn('a-share-screener: better-sqlite3 unavailable; using in-memory store (data will not persist across restarts)')
      }
      // Swap the in-memory store the constructor installed with the SQLite
      // adapter when the binding is available. The previous store is closed
      // and its disposable handed to the effect so plugin disposal reclaims it.
      ;(service as { cache: typeof store }).cache = store
    })()
  })

  ctx.tools.register(defineScreenTool(ctx, service))
  registerStockScreenerSkill(ctx)
}
