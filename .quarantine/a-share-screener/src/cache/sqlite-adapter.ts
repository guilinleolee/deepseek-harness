/**
 * Adapter that exposes a `better-sqlite3` `Database` as the `StockStore`
 * seam. Kept separate from `./cache.ts` so the cache module does not import
 * `better-sqlite3` at the top level — the plugin only loads the binding
 * when it actually opens a real database.
 *
 * @module @deepseek-ai/dsh-a-share-screener/cache/sqlite-adapter
 */

import type { OHLCV, StockBasicInfo } from '../types.ts'
import type { StockStore } from './cache.ts'

type SqliteDatabase = import('better-sqlite3').Database
type SqliteStatement<P extends unknown[] = unknown[], R = unknown> = import('better-sqlite3').Statement<P, R>

interface RawBarRow {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
  amount: number
  turnover: number | null
}

interface RawStockRow {
  symbol: string
  name: string
  market: 'SH' | 'SZ' | 'BJ'
  industry: string
  list_date: string
  is_st: number
  is_suspended: number
}

function toIsoDate(value: Date): string {
  return value.toISOString().slice(0, 10)
}

export class SqliteStoreAdapter implements StockStore {
  readonly #db: SqliteDatabase
  #getLastDate: SqliteStatement<[string], { last_date: string | null }>
  #upsertBar: SqliteStatement
  #upsertStock: SqliteStatement
  #loadStocks: SqliteStatement<[], RawStockRow[]>
  #loadBars: SqliteStatement<[string, string], RawBarRow[]>

  constructor(db: SqliteDatabase) {
    this.#db = db
    this.#getLastDate = db.prepare('SELECT MAX(date) AS last_date FROM daily_data WHERE symbol = ?')
    this.#upsertBar = db.prepare(
      `INSERT INTO daily_data (symbol, date, open, high, low, close, volume, amount, turnover)
       VALUES (@symbol, @date, @open, @high, @low, @close, @volume, @amount, @turnover)
       ON CONFLICT (symbol, date) DO UPDATE SET
         open = excluded.open, high = excluded.high, low = excluded.low, close = excluded.close,
         volume = excluded.volume, amount = excluded.amount, turnover = excluded.turnover`,
    )
    this.#upsertStock = db.prepare(
      `INSERT INTO stock_list (symbol, name, market, industry, list_date, is_st, is_suspended)
       VALUES (@symbol, @name, @market, @industry, @list_date, @is_st, @is_suspended)
       ON CONFLICT (symbol) DO UPDATE SET
         name = excluded.name, market = excluded.market, industry = excluded.industry,
         list_date = excluded.list_date, is_st = excluded.is_st, is_suspended = excluded.is_suspended`,
    )
    this.#loadStocks = db.prepare('SELECT * FROM stock_list')
    this.#loadBars = db.prepare(
      'SELECT * FROM daily_data WHERE symbol = ? AND date >= ? ORDER BY date ASC',
    )
  }

  bootstrap(): void {
    this.#db.exec(`
      CREATE TABLE IF NOT EXISTS stock_list (
        symbol TEXT PRIMARY KEY, name TEXT NOT NULL, market TEXT NOT NULL, industry TEXT,
        list_date DATE, is_st INTEGER NOT NULL DEFAULT 0, is_suspended INTEGER NOT NULL DEFAULT 0
      );
      CREATE TABLE IF NOT EXISTS daily_data (
        symbol TEXT NOT NULL, date DATE NOT NULL,
        open REAL NOT NULL, high REAL NOT NULL, low REAL NOT NULL, close REAL NOT NULL,
        volume INTEGER NOT NULL, amount REAL NOT NULL, turnover REAL,
        PRIMARY KEY (symbol, date)
      );
      CREATE INDEX IF NOT EXISTS idx_daily_date ON daily_data(date);
      CREATE INDEX IF NOT EXISTS idx_daily_symbol_date ON daily_data(symbol, date);
      CREATE TABLE IF NOT EXISTS cache_metadata (key TEXT PRIMARY KEY, value TEXT);
    `)
  }

  lastDate(symbol: string): string | undefined {
    return this.#getLastDate.get(symbol)?.last_date ?? undefined
  }

  putBar(symbol: string, bar: OHLCV): void {
    this.#upsertBar.run({
      symbol,
      date: toIsoDate(bar.date),
      open: bar.open,
      high: bar.high,
      low: bar.low,
      close: bar.close,
      volume: bar.volume,
      amount: bar.amount,
      turnover: bar.turnover ?? null,
    })
  }

  putStock(stock: StockBasicInfo): void {
    this.#upsertStock.run({
      symbol: stock.symbol,
      name: stock.name,
      market: stock.market,
      industry: stock.industry,
      list_date: toIsoDate(stock.listDate),
      is_st: stock.isST ? 1 : 0,
      is_suspended: stock.isSuspended ? 1 : 0,
    })
  }

  loadStocks(): StockBasicInfo[] {
    return this.#loadStocks.all().map((row) => ({
      symbol: row.symbol,
      name: row.name,
      market: row.market,
      industry: row.industry,
      listDate: new Date(row.list_date),
      isST: row.is_st === 1,
      isSuspended: row.is_suspended === 1,
    }))
  }

  loadBars(symbol: string, since: Date): OHLCV[] {
    return this.#loadBars.all(symbol, toIsoDate(since)).map((row) => ({
      date: new Date(row.date),
      open: row.open,
      high: row.high,
      low: row.low,
      close: row.close,
      volume: row.volume,
      amount: row.amount,
      turnover: row.turnover ?? undefined,
    }))
  }

  bulkPutBars(rows: ReadonlyArray<{ symbol: string; bar: OHLCV }>): void {
    const tx = this.#db.transaction((items: ReadonlyArray<{ symbol: string; bar: OHLCV }>) => {
      for (const { symbol, bar } of items) this.putBar(symbol, bar)
    })
    tx(rows)
  }

  close(): void {
    if (this.#db.open) this.#db.close()
  }
}
