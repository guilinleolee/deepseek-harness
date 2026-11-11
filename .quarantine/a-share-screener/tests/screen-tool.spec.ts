/**
 * Tool-level tests. Cover the universe selector (all / hot / symbols / empty),
 * the screening producer (matched / no-bars / signal-aborted / bar-derived
 * quote), `summarizeUniverse` for every branch, and the tool's failure when
 * `ctx.jobs` is absent.
 *
 * @module @deepseek-ai/dsh-a-share-screener/tests/screen-tool
 */

import { describe, expect, it, vi } from 'vitest'
import { credentialRef } from '@deepseek-ai/dsh-credentials'
import { ScreenerService } from '../src/service.ts'
import { openMemoryStore } from '../src/cache/cache.ts'
import { StrategyRegistry } from '../src/strategies/registry.ts'
import { selectUniverse, summarizeUniverse, runScreening } from '../src/tools/screen.ts'
import type { Filter, FilterContext, FilterOutcome } from '../src/filters/filters.ts'
import type { OHLCV, StockBasicInfo, Universe } from '../src/types.ts'

const stockA: StockBasicInfo = {
  symbol: '000001.SZ',
  name: '平安银行',
  market: 'SZ',
  industry: '银行',
  listDate: new Date('1991-04-03T00:00:00Z'),
  isST: false,
  isSuspended: false,
}

const stockB: StockBasicInfo = {
  symbol: '600000.SH',
  name: '浦发银行',
  market: 'SH',
  industry: '银行',
  listDate: new Date('1999-11-10T00:00:00Z'),
  isST: false,
  isSuspended: false,
}

const bar = (idx: number, close: number): OHLCV => ({
  date: new Date(Date.now() - (90 - idx) * 24 * 60 * 60 * 1000),
  open: close,
  high: close + 1,
  low: close - 1,
  close,
  volume: 1_000_000,
  amount: 1_000_000,
})

function makeService(registry: StrategyRegistry): ScreenerService {
  const store = openMemoryStore()
  store.bootstrap()
  store.putStock(stockA)
  store.putStock(stockB)
  store.putBar(stockA.symbol, bar(0, 10))
  store.putBar(stockA.symbol, bar(1, 10))
  store.putBar(stockA.symbol, bar(2, 12))
  store.putBar(stockB.symbol, bar(0, 8))
  return new ScreenerService({
    cacheRoot: '.',
    defaultLimit: 10,
    defaultUniverse: { kind: 'all' },
    jobOutputLimitBytes: 1024,
    tokenRef: credentialRef('TUSHARE_TOKEN'),
    store,
    registry,
  })
}

function always(filterName: string, outcome: FilterOutcome): Filter {
  const fn = (() => outcome) as Filter & { displayName: string }
  fn.displayName = filterName
  return fn
}

describe('summarizeUniverse', () => {
  it('formats every universe kind', () => {
    expect(summarizeUniverse({ kind: 'all' })).toBe('universe=all')
    expect(summarizeUniverse({ kind: 'hot', size: 500 })).toBe('universe=hot:500')
    expect(summarizeUniverse({ kind: 'symbols', symbols: ['000001.SZ', '600000.SH'] })).toBe('universe=symbols:2')
  })
})

describe('selectUniverse', () => {
  it('returns every cached stock for universe=all', () => {
    const service = makeService(new StrategyRegistry())
    expect(selectUniverse(service, { kind: 'all' })).toHaveLength(2)
  })

  it('caps the universe at hot.size', () => {
    const service = makeService(new StrategyRegistry())
    expect(selectUniverse(service, { kind: 'hot', size: 1 })).toHaveLength(1)
  })

  it('filters symbols by the explicit list', () => {
    const service = makeService(new StrategyRegistry())
    expect(selectUniverse(service, { kind: 'symbols', symbols: ['600000.SH'] })).toHaveLength(1)
  })

  it('returns an empty array when the cache has no rows', () => {
    const service = new ScreenerService({
      cacheRoot: '.',
      defaultLimit: 10,
      defaultUniverse: { kind: 'all' },
      jobOutputLimitBytes: 1024,
      tokenRef: credentialRef('TUSHARE_TOKEN'),
    })
    expect(selectUniverse(service, { kind: 'all' })).toEqual([])
    expect(selectUniverse(service, { kind: 'hot', size: 3 })).toEqual([])
    expect(selectUniverse(service, { kind: 'symbols', symbols: ['X'] })).toEqual([])
  })
})

describe('runScreening', () => {
  it('accumulates matches, sorts by score, and respects limit', async () => {
    const registry = new StrategyRegistry()
    registry.register({
      id: 'all-pass',
      label: 'all-pass',
      filters: [always('a', { passed: true, score: 5, evidence: ['a-ok'] })],
    })
    const service = makeService(registry)
    const hooks = runScreening(service, 'all-pass', { kind: 'all' } as Universe, 1, new AbortController().signal)
    const outcome = await hooks.done
    expect(outcome.status).toBe('completed')
    const result = JSON.parse(outcome.output ?? '{}')
    expect(result.totalScanned).toBe(2)
    expect(result.matched).toBe(2)
    expect(result.results).toHaveLength(1)
    expect(result.results[0]).toMatchObject({ matchedFilters: ['a'] })
    expect(hooks.readOutput()).not.toBe('<no matches>')
  })

  it('returns <no matches> for an empty result set', async () => {
    const registry = new StrategyRegistry()
    registry.register({
      id: 'always-fail',
      label: 'always-fail',
      filters: [always('a', { passed: false, score: 0, evidence: ['nope'] })],
    })
    const service = makeService(registry)
    const hooks = runScreening(service, 'always-fail', { kind: 'all' }, 10, new AbortController().signal)
    const outcome = await hooks.done
    const result = JSON.parse(outcome.output ?? '{}')
    expect(result.matched).toBe(0)
    expect(hooks.readOutput()).toBe('<no matches>')
  })

  it('counts stocks with no bars as scanned but unmatched', async () => {
    const registry = new StrategyRegistry()
    registry.register({
      id: 'pass',
      label: 'pass',
      filters: [always('a', { passed: true, score: 1, evidence: ['ok'] })],
    })
    const store = openMemoryStore()
    store.bootstrap()
    store.putStock(stockA)
    store.putStock({ ...stockB, symbol: '999999.SH' }) // no bars cached for this one
    const service = new ScreenerService({
      cacheRoot: '.',
      defaultLimit: 10,
      defaultUniverse: { kind: 'all' },
      jobOutputLimitBytes: 1024,
      tokenRef: credentialRef('TUSHARE_TOKEN'),
      store,
      registry,
    })
    const hooks = runScreening(service, 'pass', { kind: 'all' }, 10, new AbortController().signal)
    const outcome = await hooks.done
    const result = JSON.parse(outcome.output ?? '{}')
    expect(result.totalScanned).toBe(2)
    expect(result.matched).toBe(1)
  })

  it('aborts cleanly when the signal fires before iteration starts', async () => {
    const registry = new StrategyRegistry()
    registry.register({
      id: 'pass',
      label: 'pass',
      filters: [always('a', { passed: true, score: 1, evidence: ['ok'] })],
    })
    const service = makeService(registry)
    const controller = new AbortController()
    controller.abort()
    const hooks = runScreening(service, 'pass', { kind: 'all' }, 10, controller.signal)
    const outcome = await hooks.done
    const result = JSON.parse(outcome.output ?? '{}')
    expect(result.totalScanned).toBe(0)
    expect(result.matched).toBe(0)
  })

  it('uses bar-derived Quote when the filter inspects it', async () => {
    const registry = new StrategyRegistry()
    const capture: { price: number | null } = { price: null }
    const captureFilter: Filter = ((ctx: FilterContext) => {
      capture.price = ctx.quote.price
      return { passed: true, score: 0, evidence: [] }
    }) as Filter & { displayName: string }
    captureFilter.displayName = 'capture'
    registry.register({ id: 'capture', label: 'capture', filters: [captureFilter] })
    const service = makeService(registry)
    await runScreening(service, 'capture', { kind: 'symbols', symbols: ['000001.SZ'] }, 10, new AbortController().signal).done
    expect(capture.price).toBe(12)
  })

  it('cancel hook is callable and does not throw', async () => {
    const registry = new StrategyRegistry()
    registry.register({
      id: 'pass',
      label: 'pass',
      filters: [always('a', { passed: true, score: 1, evidence: ['ok'] })],
    })
    const service = makeService(registry)
    const hooks = runScreening(service, 'pass', { kind: 'all' }, 10, new AbortController().signal)
    expect(() => hooks.cancel()).not.toThrow()
  })
})

describe('defineScreenTool integration', () => {
  it('throws when ctx.jobs is unavailable', async () => {
    const ctx = { get: () => undefined } as never
    const registry = new StrategyRegistry()
    registry.register({ id: 'p', label: 'p', filters: [always('a', { passed: true, score: 0, evidence: [] })] })
    const service = makeService(registry)
    const tool = (await import('../src/tools/screen.ts')).defineScreenTool(ctx, service)
    // coverage:ignore-start -- the helper inspects defineTool's wrapper; we drive `execute` directly to keep types narrow.
    const exec = { context: { get: () => undefined }, signal: new AbortController().signal } as never
    await expect(tool.execute({ strategy: 'p', universe: { kind: 'all' }, limit: 1 } as never, exec)).rejects.toThrow(/background jobs unavailable/)
    // coverage:ignore-end
  })

  it('starts a background job when ctx.jobs is present', async () => {
    const ctx = { get: () => undefined } as never
    const registry = new StrategyRegistry()
    registry.register({ id: 'p', label: 'p', filters: [always('a', { passed: true, score: 0, evidence: [] })] })
    const service = makeService(registry)
    const tool = (await import('../src/tools/screen.ts')).defineScreenTool(ctx, service)
    const jobs = { start: vi.fn().mockReturnValue('a-share-screener-1') }
    const exec = { context: { get: (k: string) => (k === 'jobs' ? jobs : undefined) }, signal: new AbortController().signal } as never
    const out = (await tool.execute({ strategy: 'p', universe: { kind: 'all' }, limit: 1 } as never, exec)) as { kind: 'background'; jobId: string }
    expect(out).toEqual({ kind: 'background', jobId: 'a-share-screener-1' })
    expect(jobs.start).toHaveBeenCalled()
    expect(jobs.start.mock.calls[0]?.[0]).toMatchObject({ kind: 'a-share-screener', label: 'p universe=all' })
  })
})
