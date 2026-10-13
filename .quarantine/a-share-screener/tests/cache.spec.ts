/**
 * Cache round-trip tests. Cover both backends: the in-memory `MemoryStore`
 * is exercised by every consumer-facing test; the SQLite adapter sits
 * behind a runtime guard so the suite runs on hosts where the native
 * binding cannot load.
 *
 * @module @deepseek-ai/dsh-a-share-screener/tests/cache
 */

import { describe, expect, it } from 'vitest'
import { openMemoryStore, type StockStore } from '../src/cache/cache.ts'
import type { OHLCV, StockBasicInfo } from '../src/types.ts'

const stock: StockBasicInfo = {
  symbol: '000001.SZ',
  name: '平安银行',
  market: 'SZ',
  industry: '银行',
  listDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
  isST: false,
  isSuspended: false,
}

const recent = (offsetDays: number): Date => new Date(Date.now() - offsetDays * 24 * 60 * 60 * 1000)

const bar: OHLCV = {
  date: recent(5),
  open: 10,
  high: 11,
  low: 9,
  close: 10.5,
  volume: 1_000_000,
  amount: 10_500_000,
}

function makeStore(): StockStore {
  return openMemoryStore()
}

describe('MemoryStore', () => {
  it('bootstrap is idempotent', () => {
    const store = makeStore()
    store.bootstrap()
    store.bootstrap()
    expect(store.loadStocks()).toEqual([])
  })

  it('putStock + loadStocks round-trips', () => {
    const store = makeStore()
    store.bootstrap()
    store.putStock(stock)
    const [row] = store.loadStocks()
    expect(row).toMatchObject({ symbol: stock.symbol, market: 'SZ', isST: false })
    expect(row?.listDate.toISOString()).toBe('1991-04-03T00:00:00.000Z')
  })

  it('putBar + loadBars filters by `since`', () => {
    const store = makeStore()
    store.bootstrap()
    store.putBar(stock.symbol, bar)
    store.putBar(stock.symbol, { ...bar, date: recent(3), close: 12 })
    const rows = store.loadBars(stock.symbol, recent(4))
    expect(rows.map((r) => r.close)).toEqual([12])
  })

  it('lastDate returns the most recent bar date', () => {
    const store = makeStore()
    store.bootstrap()
    store.putBar(stock.symbol, bar)
    const expected = recent(5).toISOString().slice(0, 10)
    expect(store.lastDate(stock.symbol)).toBe(expected)
  })

  it('lastDate returns undefined for symbols with no bars', () => {
    const store = makeStore()
    store.bootstrap()
    expect(store.lastDate(stock.symbol)).toBeUndefined()
  })

  it('bulkPutBars writes every bar', () => {
    const store = makeStore()
    store.bootstrap()
    store.bulkPutBars([
      { symbol: stock.symbol, bar },
      { symbol: stock.symbol, bar: { ...bar, date: new Date('2025-02-01T00:00:00Z') } },
    ])
    expect(store.loadBars(stock.symbol, new Date('2024-01-01T00:00:00Z'))).toHaveLength(2)
  })

  it('close clears all rows', () => {
    const store = makeStore()
    store.bootstrap()
    store.putStock(stock)
    store.putBar(stock.symbol, bar)
    store.close()
    expect(store.loadStocks()).toEqual([])
    expect(store.loadBars(stock.symbol, new Date('2024-01-01T00:00:00Z'))).toEqual([])
  })
})

describe('SqliteStoreAdapter', () => {
  it('round-trips rows when the binding is available', async () => {
    let Database: typeof import('better-sqlite3').Database | undefined
    try {
      const mod = (await import('better-sqlite3')) as { default?: typeof import('better-sqlite3').Database }
      Database = mod.default ?? mod
    } catch {
      return // binding unavailable on this host; SQLite path is exercised in deploy images.
    }
    const db = Database!.open(':memory:')
    try {
      const { SqliteStoreAdapter } = await import('../src/cache/sqlite-adapter.ts')
      const store = new SqliteStoreAdapter(db)
      store.bootstrap()
      store.putStock(stock)
      store.putBar(stock.symbol, bar)
      store.putBar(stock.symbol, { ...bar, date: recent(3), close: 12 })
      const rows = store.loadBars(stock.symbol, recent(4))
      expect(rows.map((r) => r.close)).toEqual([12])
      expect(store.lastDate(stock.symbol)).toBe(recent(3).toISOString().slice(0, 10))
      expect(store.loadStocks()).toHaveLength(1)
      store.bulkPutBars([{ symbol: stock.symbol, bar: { ...bar, date: recent(1), close: 13 } }])
      expect(store.loadBars(stock.symbol, recent(60))).toHaveLength(3)
    } finally {
      db.close()
    }
  })

  it('close is idempotent and skips when the database is already closed', async () => {
    let Database: typeof import('better-sqlite3').Database | undefined
    try {
      const mod = (await import('better-sqlite3')) as { default?: typeof import('better-sqlite3').Database }
      Database = mod.default ?? mod
    } catch {
      return
    }
    const db = Database!.open(':memory:')
    const { SqliteStoreAdapter } = await import('../src/cache/sqlite-adapter.ts')
    const store = new SqliteStoreAdapter(db)
    store.close()
    expect(() => store.close()).not.toThrow()
  })
})
