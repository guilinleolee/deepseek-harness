/**
 * Tushare Pro provider. The token is resolved through `ctx.credentials` on
 * every request, matching the per-operation contract documented in
 * `@deepseek-ai/dsh-credentials`. The provider fetches with the global
 * `fetch`; aborting the caller's `signal` cancels the request.
 *
 * The class lives outside `index.ts` so unit tests can construct it without a
 * Cordis host: the credentials capability is replaced by a `tokenRef` lookup.
 * @module @deepseek-ai/dsh-a-share-screener/sources/tushare
 */

import type { CredentialRef } from '@deepseek-ai/dsh-credentials'
import type { OHLCV, StockBasicInfo } from '../types.ts'

const BASE_URL = 'https://api.tushare.pro'

export interface TushareSourceOptions {
  /** Resolver returning the token value; wired from `ctx.credentials` at construction. */
  resolveToken: () => Promise<string | undefined>
}

export class TushareSource {
  readonly #tokenRef: CredentialRef
  readonly #resolveToken: () => Promise<string | undefined>

  constructor(tokenRef: CredentialRef, resolveToken: TushareSourceOptions['resolveToken'] = defaultResolver) {
    this.#tokenRef = tokenRef
    this.#resolveToken = resolveToken
  }

  get tokenRef(): CredentialRef {
    return this.#tokenRef
  }

  /** Fetch one symbol's daily bars. Resolves with an empty array when the token is missing. */
  async fetchDaily(symbol: string, startDate: Date, endDate: Date, signal: AbortSignal): Promise<OHLCV[]> {
    const token = await this.#resolveToken()
    if (token === undefined) {
      throw new Error(`tushare: token ${this.#tokenRef} is not configured`)
    }
    const response = await fetch(`${BASE_URL}/api`, {
      method: 'POST',
      signal,
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({
        api_name: 'daily',
        token,
        params: {
          ts_code: symbol,
          start_date: iso(startDate),
          end_date: iso(endDate),
        },
        fields: 'trade_date,open,high,low,close,vol,amount',
      }),
    })
    if (!response.ok) {
      throw new Error(`tushare: HTTP ${String(response.status)} ${response.statusText}`)
    }
    const body = await response.json() as TushareDailyResponse
    if (body.code !== 0) {
      throw new Error(`tushare: ${body.msg ?? 'unknown error'}`)
    }
    return (body.data?.fields ?? []).length === 0
      ? []
      : body.data!.fields.map((row) => mapRow(row))
  }

  /** Fetch the full market's stock listing for the latest trading day. */
  async fetchStockList(signal: AbortSignal): Promise<StockBasicInfo[]> {
    const token = await this.#resolveToken()
    if (token === undefined) {
      throw new Error(`tushare: token ${this.#tokenRef} is not configured`)
    }
    const response = await fetch(`${BASE_URL}/api`, {
      method: 'POST',
      signal,
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({
        api_name: 'stock_basic',
        token,
        params: { list_status: 'L' },
        fields: 'ts_code,name,industry,list_date,market',
      }),
    })
    if (!response.ok) {
      throw new Error(`tushare: HTTP ${String(response.status)} ${response.statusText}`)
    }
    const body = await response.json() as TushareStockBasicResponse
    if (body.code !== 0) {
      throw new Error(`tushare: ${body.msg ?? 'unknown error'}`)
    }
    const items = body.data?.items ?? []
    if (items.length === 0) return []
    return items.map((row) => mapStock(row))
  }
}

const defaultResolver: TushareSourceOptions['resolveToken'] = async () => undefined

interface TushareDailyResponse {
  code: number
  msg?: string
  data?: {
    fields: string[][]
  }
}

interface TushareStockBasicResponse {
  code: number
  msg?: string
  data?: {
    fields: string[]
    items: string[][]
  }
}

function iso(value: Date): string {
  return value.toISOString().slice(0, 10).replace(/-/g, '')
}

function mapRow(row: string[]): OHLCV {
  const [tradeDate, open, high, low, close, vol, amount] = row
  return {
    date: new Date(`${tradeDate.slice(0, 4)}-${tradeDate.slice(4, 6)}-${tradeDate.slice(6, 8)}T00:00:00Z`),
    open: Number(open),
    high: Number(high),
    low: Number(low),
    close: Number(close),
    volume: Number(vol),
    amount: Number(amount),
  }
}

function mapStock(row: string[]): StockBasicInfo {
  const [tsCode, name, industry, listDate, market] = row
  const lastDot = tsCode.lastIndexOf('.')
  return {
    symbol: tsCode,
    name,
    market: tsCode.endsWith('.SH') ? 'SH' : tsCode.endsWith('.SZ') ? 'SZ' : 'BJ',
    industry: industry ?? '',
    listDate: listDate ? new Date(listDate) : new Date(),
    isST: name.startsWith('ST') || name.startsWith('*ST'),
    isSuspended: false,
  }
}
