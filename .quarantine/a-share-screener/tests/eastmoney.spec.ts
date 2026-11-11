/**
 * Eastmoney fallback tests. Cover every branch:
 * - `data === null` → empty array;
 * - non-2xx response → thrown error;
 * - happy path maps `klines` rows into OHLCV;
 * - `fetchStockList` returns `[]` per the deferred-design choice.
 *
 * @module @deepseek-ai/dsh-a-share-screener/tests/eastmoney
 */

import { afterEach, describe, expect, it, vi } from 'vitest'
import { EastmoneySource } from '../src/sources/eastmoney.ts'

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('EastmoneySource', () => {
  it('returns an empty array when the upstream payload is null', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ data: null }),
    }))
    const source = new EastmoneySource()
    expect(await source.fetchDaily('1.000001', new Date('2025-01-01T00:00:00Z'), new Date('2025-01-31T00:00:00Z'), new AbortController().signal)).toEqual([])
  })

  it('throws on non-2xx responses', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 503, statusText: 'Service Unavailable' }))
    const source = new EastmoneySource()
    await expect(
      source.fetchDaily('1.000001', new Date('2025-01-01T00:00:00Z'), new Date('2025-01-31T00:00:00Z'), new AbortController().signal),
    ).rejects.toThrow(/HTTP 503/)
  })

  it('maps kline rows into OHLCV including turnover when present', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        // Eastmoney kline CSV order: 日期,开盘,收盘,最高,最低,成交量,成交额,振幅,换手率
        data: { klines: ['2025-01-02,10,10.5,11,9,1000,10500000,1.5,2.5'] },
      }),
    }))
    const source = new EastmoneySource()
    const bars = await source.fetchDaily('1.000001', new Date('2025-01-01T00:00:00Z'), new Date('2025-01-31T00:00:00Z'), new AbortController().signal)
    expect(bars).toHaveLength(1)
    expect(bars[0]).toMatchObject({
      open: 10,
      close: 10.5,
      high: 11,
      low: 9,
      volume: 1000,
      amount: 10500000,
      turnover: 2.5,
    })
    expect(bars[0]!.date.toISOString()).toBe('2025-01-02T00:00:00.000Z')
  })

  it('maps kline rows without turnover (legacy 7-field shape)', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ data: { klines: ['2025-01-02,10,10.5,11,9,1000,10500000'] } }),
    }))
    const source = new EastmoneySource()
    const [bar] = await source.fetchDaily('1.000001', new Date('2025-01-01T00:00:00Z'), new Date('2025-01-31T00:00:00Z'), new AbortController().signal)
    expect(bar?.turnover).toBeUndefined()
  })

  it('fetchStockList returns an empty array (deferred design)', async () => {
    const source = new EastmoneySource()
    expect(await source.fetchStockList()).toEqual([])
  })
})
