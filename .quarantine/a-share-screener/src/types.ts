/**
 * Type-only declarations for the A-share screener plugin. The runtime surface
 * lives in `./index.ts`; this file holds data shapes shared by the cache,
 * sources, filters, and strategies.
 * @module @deepseek-ai/dsh-a-share-screener/types
 */

import type { CredentialRef } from '@deepseek-ai/dsh-credentials'

/** Coarse market segmentation carried on the screener's stock-list rows. */
export type Market = 'SH' | 'SZ' | 'BJ'

/** One row in `stock_list` (the cached exchange listing). */
export interface StockBasicInfo {
  symbol: string
  name: string
  market: Market
  industry: string
  listDate: Date
  isST: boolean
  isSuspended: boolean
}

/** One daily bar as it lives in the cache and travels to filters. */
export interface OHLCV {
  date: Date
  open: number
  high: number
  low: number
  close: number
  volume: number
  amount: number
  turnover?: number
}

/** Quote at execution time. `amount` is in CNY; `changePercent` is the percent move since the prior close. */
export interface Quote {
  symbol: string
  price: number
  change: number
  changePercent: number
  volume: number
  amount: number
  timestamp: Date
}

/** Stock-pool selector handed to `a_share_screen`. */
export type Universe =
  | { kind: 'all' }
  | { kind: 'hot'; size: number }
  | { kind: 'symbols'; symbols: readonly string[] }

/** Composite shape the tool receives after JSON-Schema validation. */
export interface ScreenArgs {
  strategy: 'low-flat-limit-up' | 'oversold-rebound' | 'momentum-breakout' | 'value-play'
  universe: Universe
  limit: number
  sortByScore: boolean
  overrides?: Record<string, number>
}

/** One matched stock and the evidence the composite produced. */
export interface StockMatch {
  stock: StockBasicInfo
  score?: number
  matchedFilters: readonly string[]
  evidence: readonly string[]
  currentQuote: Quote
}

/** Canonical return of the foreground filter evaluator; the tool wraps this in a background handle. */
export interface ScreenResult {
  totalScanned: number
  matched: number
  results: StockMatch[]
  executionTimeMs: number
}

/** Configuration block sourced from `cordis.yml` (validated at load). */
export interface Config {
  cacheRoot: string
  defaultLimit: number
  defaultUniverse: Universe
  jobOutputLimitBytes: number
}

/** The credential the plugin needs. Exported so the README and tests agree on the name. */
export const TUSHARE_TOKEN_REF: CredentialRef = 'TUSHARE_TOKEN' as CredentialRef

/** Background-job kind for the screener. Augments `JobKindMap` in `./index.ts`. */
export const SCREENER_JOB_KIND = 'a-share-screener' as const
