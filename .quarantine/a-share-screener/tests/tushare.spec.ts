/**
 * Tushare source tests. Cover every branch of both `fetchDaily` and
 * `fetchStockList`:
 * - missing token throws a typed error;
 * - HTTP non-2xx throws;
 * - `code !== 0` throws with the upstream message;
 * - empty data returns an empty array;
 * - happy path maps fields and rows.
 *
 * @module @deepseek-ai/dsh-a-share-screener/tests/tushare
 */

import { afterEach, describe, expect, it, vi } from 'vitest'
import { credentialRef } from '@deepseek-ai/dsh-credentials'
import { TushareSource } from '../src/sources/tushare.ts'

const tokenRef = credentialRef('TUSHARE_TOKEN')

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('TushareSource', () => {
  it('throws a typed error when the token is not configured', async () => {
    const source = new TushareSource(tokenRef)
    await expect(
      source.fetchDaily('000001.SZ', new Date('2025-01-01T00:00:00Z'), new Date('2025-01-31T00:00:00Z'), new AbortController().signal),
    ).rejects.toThrow(/token TUSHARE_TOKEN is not configured/)
  })

  it('throws on non-2xx responses', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 502, statusText: 'Bad Gateway' }))
    const source = new TushareSource(tokenRef, async () => 'token')
    await expect(
      source.fetchDaily('000001.SZ', new Date('2025-01-01T00:00:00Z'), new Date('2025-01-31T00:00:00Z'), new AbortController().signal),
    ).rejects.toThrow(/HTTP 502/)
  })

  it('throws when Tushare returns a non-zero code', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ code: -1, msg: 'rate-limited' }),
    }))
    const source = new TushareSource(tokenRef, async () => 'token')
    await expect(
      source.fetchDaily('000001.SZ', new Date('2025-01-01T00:00:00Z'), new Date('2025-01-31T00:00:00Z'), new AbortController().signal),
    ).rejects.toThrow(/rate-limited/)
  })

  it('returns an empty array when the upstream payload has no fields', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ code: 0 }),
    }))
    const source = new TushareSource(tokenRef, async () => 'token')
    const bars = await source.fetchDaily('000001.SZ', new Date('2025-01-01T00:00:00Z'), new Date('2025-01-31T00:00:00Z'), new AbortController().signal)
    expect(bars).toEqual([])
  })

  it('maps rows into OHLCV when the upstream payload has fields', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        code: 0,
        data: { fields: [['20250102', '10', '11', '9', '10.5', '1000', '10500000']] },
      }),
    }))
    const source = new TushareSource(tokenRef, async () => 'token')
    const bars = await source.fetchDaily('000001.SZ', new Date('2025-01-01T00:00:00Z'), new Date('2025-01-31T00:00:00Z'), new AbortController().signal)
    expect(bars).toHaveLength(1)
    expect(bars[0]).toMatchObject({
      close: 10.5,
      volume: 1000,
      amount: 10500000,
    })
    expect(bars[0]!.date.toISOString()).toBe('2025-01-02T00:00:00.000Z')
  })

  it('throws on non-2xx responses from fetchStockList', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 500, statusText: 'Internal' }))
    const source = new TushareSource(tokenRef, async () => 'token')
    await expect(source.fetchStockList(new AbortController().signal)).rejects.toThrow(/HTTP 500/)
  })

  it('throws when stock_basic returns a non-zero code', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ code: 40001, msg: 'token expired' }),
    }))
    const source = new TushareSource(tokenRef, async () => 'token')
    await expect(source.fetchStockList(new AbortController().signal)).rejects.toThrow(/token expired/)
  })

  it('returns an empty array when stock_basic has no items', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ code: 0, data: { fields: [], items: [] } }),
    }))
    const source = new TushareSource(tokenRef, async () => 'token')
    expect(await source.fetchStockList(new AbortController().signal)).toEqual([])
  })

  it('maps stock_basic items into StockBasicInfo, including ST detection', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        code: 0,
        data: {
          fields: ['ts_code', 'name', 'industry', 'list_date', 'market'],
          items: [
            ['000001.SZ', '平安银行', '银行', '19910403', 'SZSE'],
            ['600000.SH', '浦发银行', '银行', '19991110', 'SSE'],
            ['000666.SZ', 'ST 测试', '化工', '20010101', 'SZSE'],
          ],
        },
      }),
    }))
    const source = new TushareSource(tokenRef, async () => 'token')
    const stocks = await source.fetchStockList(new AbortController().signal)
    expect(stocks).toHaveLength(3)
    expect(stocks[0]).toMatchObject({ symbol: '000001.SZ', market: 'SZ', isST: false })
    expect(stocks[1]).toMatchObject({ symbol: '600000.SH', market: 'SH', isST: false })
    expect(stocks[2]).toMatchObject({ symbol: '000666.SZ', isST: true })
  })

  it('exposes the credential ref it was constructed with', () => {
    const source = new TushareSource(tokenRef)
    expect(source.tokenRef).toBe(tokenRef)
  })
})
