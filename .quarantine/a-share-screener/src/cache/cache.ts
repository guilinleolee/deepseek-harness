/**
 * Storage seam for the screener's daily bars and stock listings.
 *
 * The default plugin wiring opens a `better-sqlite3` handle through
 * `./sqlite-adapter.ts`; the in-memory store ships as a fallback for hosts
 * where the native binding cannot load. Tests inject a `StockStore`
 * directly so they do not need the binding.
 *
 * @module @deepseek-ai/dsh-a-share-screener/cache
 */

import type { OHLCV, StockBasicInfo } from '../types.ts'

/** Storage seam shared by both backends. Pure interface; no native references. */
export interface StockStore {
  bootstrap(): void
  lastDate(symbol: string): string | undefined
  putBar(symbol: string, bar: OHLCV): void
  putStock(stock: StockBasicInfo): void
  loadStocks(): StockBasicInfo[]
  loadBars(symbol: string, since: Date): OHLCV[]
  bulkPutBars(rows: ReadonlyArray<{ symbol: string; bar: OHLCV }>): void
  close(): void
}

/** Construct an in-memory store. The seam implementation has no native deps and is always available. */
export function openMemoryStore(): StockStore {
  return new MemoryStore()
}

function toIsoDate(value: Date): string {
  return value.toISOString().slice(0, 10)
}

class MemoryStore implements StockStore {
  readonly #stocks = new Map<string, StockBasicInfo>()
  readonly #bars = new Map<string, OHLCV>()

  bootstrap(): void {
    // The in-memory store has no schema; the method exists to satisfy the seam.
  }

  lastDate(symbol: string): string | undefined {
    let best: string | undefined
    for (const [key, bar] of this.#bars) {
      if (!key.startsWith(`${symbol}|`)) continue
      const candidate = key.slice(symbol.length + 1)
      if (best === undefined || new Date(candidate) > new Date(best)) {
        best = candidate
      }
    }
    return best
  }

  putBar(symbol: string, bar: OHLCV): void {
    const dateKey = toIsoDate(bar.date)
    this.#bars.set(`${symbol}|${dateKey}`, { ...bar, date: new Date(dateKey) })
  }

  putStock(stock: StockBasicInfo): void {
    this.#stocks.set(stock.symbol, { ...stock, listDate: new Date(stock.listDate) })
  }

  loadStocks(): StockBasicInfo[] {
    return Array.from(this.#stocks.values()).map((s) => ({ ...s, listDate: new Date(s.listDate) }))
  }

  loadBars(symbol: string, since: Date): OHLCV[] {
    const sinceKey = toIsoDate(since)
    const out: OHLCV[] = []
    for (const [key, bar] of this.#bars) {
      console.error('[MemoryStore.loadBars]', { key, sinceKey })
      if (!key.startsWith(`${symbol}|`)) continue
      const dateKey = key.slice(symbol.length + 1)
      if (dateKey < sinceKey) continue
      out.push(bar)
    }
    out.sort((a, b) => a.date.getTime() - b.date.getTime())
    return out
  }

  bulkPutBars(rows: ReadonlyArray<{ symbol: string; bar: OHLCV }>): void {
    for (const { symbol, bar } of rows) this.putBar(symbol, bar)
  }

  close(): void {
    this.#stocks.clear()
    this.#bars.clear()
  }
}
