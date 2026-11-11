/**
 * Eastmoney fallback provider. Used when the Tushare primary throws — the
 * fallback does not require a token. The implementation targets the public
 * `push2his.eastmoney.com` daily endpoint and parses its text-shaped CSV
 * without a heavy dependency.
 *
 * @module @deepseek-ai/dsh-a-share-screener/sources/eastmoney
 */

import type { OHLCV, StockBasicInfo } from '../types.ts'

const HISTORY_URL = 'https://push2his.eastmoney.com/api/qt/stock/kline/get'

export class EastmoneySource {
  /** Fetch daily bars for one symbol. `secid` is the Eastmoney `1.000001` style market.code id. */
  async fetchDaily(secid: string, startDate: Date, endDate: Date, signal: AbortSignal): Promise<OHLCV[]> {
    const params = new URLSearchParams({
      secid,
      klt: '101', // daily
      fqt: '1',  // forward-adjusted
      beg: iso(startDate),
      end: iso(endDate),
      lmt: '1000',
    })
    const response = await fetch(`${HISTORY_URL}?${params.toString()}`, { signal })
    if (!response.ok) {
      throw new Error(`eastmoney: HTTP ${String(response.status)} ${response.statusText}`)
    }
    const body = await response.json() as EastmoneyHistoryResponse
    if (body.data === null) return []
    return body.data.klines.map(mapKline)
  }

  /** A best-effort stock listing. Eastmoney does not expose a clean full-market listing without a session cookie, so this returns an empty array unless callers provide rows through other channels. */
  async fetchStockList(): Promise<StockBasicInfo[]> {
    return []
  }
}

interface EastmoneyHistoryResponse {
  data: null | {
    klines: string[]
  }
}

function iso(value: Date): string {
  return value.toISOString().slice(0, 10).replace(/-/g, '')
}

function mapKline(line: string): OHLCV {
  // Eastmoney kline CSV format: `日期,开盘,收盘,最高,最低,成交量,成交额,振幅,换手率`.
  const [date, open, close, high, low, volume, amount, amplitude, turnover] = line.split(',')
  return {
    date: new Date(`${date}T00:00:00Z`),
    open: Number(open),
    high: Number(high),
    low: Number(low),
    close: Number(close),
    volume: Number(volume),
    amount: Number(amount),
    turnover: turnover === undefined ? undefined : Number(turnover),
  }
}
