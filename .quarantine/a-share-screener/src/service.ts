/**
 * Internal service that owns the screener's stateful collaborators: the stock
 * store, the active data-source provider, and the strategy registry.
 *
 * The tool executor reads from this object. The service is created by the
 * plugin's `apply` and torn down with the host fiber. Construction is
 * overridable through the static factory so unit tests can inject a
 * `StockStore` without touching the filesystem.
 *
 * @module @deepseek-ai/dsh-a-share-screener/service
 */

import type { CredentialRef } from '@deepseek-ai/dsh-credentials'
import { openMemoryStore, type StockStore } from './cache/cache.ts'
import { SqliteStoreAdapter } from './cache/sqlite-adapter.ts'
import { TushareSource } from './sources/tushare.ts'
import { EastmoneySource } from './sources/eastmoney.ts'
import { StrategyRegistry } from './strategies/registry.ts'
import type { Universe } from './types.ts'

export interface ScreenerServiceOptions {
  cacheRoot: string
  defaultLimit: number
  defaultUniverse: Universe
  jobOutputLimitBytes: number
  tokenRef: CredentialRef
  /** Override the cache (used by tests to inject a fresh `StockStore`). */
  store?: StockStore
  /** Override the strategy registry (used by tests to seed builtins). */
  registry?: StrategyRegistry
  /** Override the primary data source (used by tests with a stub resolver). */
  primarySource?: TushareSource
  /** Override the fallback data source (used by tests with a stub). */
  fallbackSource?: EastmoneySource
}

/**
 * Construct the service with an injected store. When `store` is omitted the
 * service builds an in-memory store; SQLite-backed storage is opened by the
 * plugin's `apply` through {@link openDefaultStore}, so unit tests do not
 * need the native binding.
 */
export class ScreenerService {
  readonly cache: StockStore
  readonly sources: { primary: TushareSource; fallback: EastmoneySource }
  readonly strategies: StrategyRegistry
  readonly jobOutputLimitBytes: number
  readonly defaultLimit: number
  readonly defaultUniverse: Universe
  readonly tokenRef: CredentialRef

  constructor(options: ScreenerServiceOptions) {
    this.cache = options.store ?? openMemoryStore()
    this.cache.bootstrap()
    this.sources = {
      primary: options.primarySource ?? new TushareSource(options.tokenRef),
      fallback: options.fallbackSource ?? new EastmoneySource(),
    }
    this.strategies = options.registry ?? new StrategyRegistry()
    this.jobOutputLimitBytes = options.jobOutputLimitBytes
    this.defaultLimit = options.defaultLimit
    this.defaultUniverse = options.defaultUniverse
    this.tokenRef = options.tokenRef
  }

  /** Close the underlying store. Idempotent. */
  close(): void {
    this.cache.close()
  }
}

/**
 * Try to open the SQLite store for the host environment. Returns the in-memory
 * store when the native binding cannot be loaded so the plugin still boots.
 *
 * @param cacheRoot - directory the SQLite file lives in.
 * @returns the constructed store and a `kind` discriminator.
 */
export async function openDefaultStore(cacheRoot: string): Promise<{ store: StockStore; kind: 'sqlite' | 'memory' }> {
  try {
    const imported = (await import('better-sqlite3')) as { default?: typeof import('better-sqlite3').Database }
    const Database = imported.default ?? imported
    const { mkdirSync } = await import('node:fs')
    const { join } = await import('node:path')
    mkdirSync(cacheRoot, { recursive: true })
    const db = Database.open(join(cacheRoot, 'a-share.sqlite'))
    db.pragma('journal_mode = WAL')
    return { store: new SqliteStoreAdapter(db), kind: 'sqlite' }
  } catch {
    return { store: openMemoryStore(), kind: 'memory' }
  }
}
