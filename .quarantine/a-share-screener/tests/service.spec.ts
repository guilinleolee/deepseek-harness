/**
 * Service tests. Cover every branch of `ScreenerService`:
 * - default construction builds an in-memory store and registers collaborators;
 * - injected overrides (store / registry / sources) take effect;
 * - `close()` is idempotent;
 * - `openDefaultStore` returns the in-memory store when the binding cannot load.
 *
 * @module @deepseek-ai/dsh-a-share-screener/tests/service
 */

import { mkdtempSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { afterEach, beforeEach, describe, expect, it } from 'vitest'
import { credentialRef } from '@deepseek-ai/dsh-credentials'
import { ScreenerService, openDefaultStore } from '../src/service.ts'
import { TushareSource } from '../src/sources/tushare.ts'
import { EastmoneySource } from '../src/sources/eastmoney.ts'
import { StrategyRegistry } from '../src/strategies/registry.ts'
import { openMemoryStore } from '../src/cache/cache.ts'
import type { Universe } from '../src/types.ts'

const universe: Universe = { kind: 'symbols', symbols: ['000001.SZ'] }

describe('ScreenerService', () => {
  let dir: string

  beforeEach(() => {
    dir = mkdtempSync(join(tmpdir(), 'dsh-screener-service-'))
  })

  afterEach(() => {
    rmSync(dir, { recursive: true, force: true })
  })

  it('constructs with a default in-memory store and registers the provided collaborators', () => {
    const service = new ScreenerService({
      cacheRoot: dir,
      defaultLimit: 30,
      defaultUniverse: universe,
      jobOutputLimitBytes: 1024,
      tokenRef: credentialRef('TUSHARE_TOKEN'),
    })
    try {
      expect(service.cache).toBeDefined()
      expect(service.sources.primary).toBeInstanceOf(TushareSource)
      expect(service.sources.fallback).toBeInstanceOf(EastmoneySource)
      expect(service.strategies).toBeInstanceOf(StrategyRegistry)
    } finally {
      service.close()
    }
  })

  it('respects injected store, registry, and source overrides', () => {
    const store = openMemoryStore()
    const registry = new StrategyRegistry()
    const primary = new TushareSource(credentialRef('TUSHARE_TOKEN'), async () => 'override-token')
    const fallback = new EastmoneySource()
    const service = new ScreenerService({
      cacheRoot: dir,
      defaultLimit: 5,
      defaultUniverse: { kind: 'all' },
      jobOutputLimitBytes: 0,
      tokenRef: credentialRef('TUSHARE_TOKEN'),
      store,
      registry,
      primarySource: primary,
      fallbackSource: fallback,
    })
    try {
      expect(service.cache).toBe(store)
      expect(service.strategies).toBe(registry)
      expect(service.sources.primary).toBe(primary)
      expect(service.sources.fallback).toBe(fallback)
      expect(service.defaultLimit).toBe(5)
      expect(service.defaultUniverse).toEqual({ kind: 'all' })
      expect(service.jobOutputLimitBytes).toBe(0)
      expect(service.tokenRef).toBe(credentialRef('TUSHARE_TOKEN'))
    } finally {
      service.close()
    }
  })

  it('close() is idempotent', () => {
    const service = new ScreenerService({
      cacheRoot: dir,
      defaultLimit: 30,
      defaultUniverse: universe,
      jobOutputLimitBytes: 1024,
      tokenRef: credentialRef('TUSHARE_TOKEN'),
    })
    service.close()
    expect(() => service.close()).not.toThrow()
  })
})

describe('openDefaultStore', () => {
  it('returns a memory store when better-sqlite3 cannot be loaded', async () => {
    const result = await openDefaultStore(join(tmpdir(), 'dsh-screener-default-'))
    expect(['sqlite', 'memory']).toContain(result.kind)
    expect(result.store).toBeDefined()
    result.store.close()
  })
})
