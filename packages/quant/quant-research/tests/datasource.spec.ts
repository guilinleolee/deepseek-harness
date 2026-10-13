import { describe, expect, it, vi } from 'vitest'
import { DataSourceBreaker, fetchKline, validateBars, validateSymbol } from '../src/pdat/datasource.ts'
import { QuantError } from '../src/errors.ts'
import type { QuantKernelClient } from '../src/kernel-client/client.ts'

const BARS = [
  { date: '2024-01-02', open: 1, high: 2, low: 0.5, close: 1.5, volume: 10 },
  { date: '2024-01-03', open: 1.5, high: 2.5, low: 1, close: 2, volume: 20 },
]

function kernelReturning(result: unknown): QuantKernelClient {
  return {
    request: vi.fn(async () => (typeof result === 'function' ? (result as () => unknown)() : result)),
  } as unknown as QuantKernelClient
}

const OPTIONS = {
  source: 'synthetic' as const,
  symbol: '000001',
  bars: 30,
  retries: 0,
  cacheDir: '/tmp/cache',
}

describe('validateSymbol', () => {
  it('accepts alphanumeric, dot, slash, and dash', () => {
    expect(validateSymbol('000001')).toBe('000001')
    expect(validateSymbol('BTC/USDT')).toBe('BTC/USDT')
    expect(validateSymbol('BRK.B')).toBe('BRK.B')
    expect(validateSymbol('sh-600000')).toBe('sh-600000')
  })

  it('rejects empty, oversized, and foreign-character symbols', () => {
    expect(() => validateSymbol('')).toThrow(/标的代码/)
    expect(() => validateSymbol('x'.repeat(25))).toThrow(/标的代码/)
    expect(() => validateSymbol('贵州茅台')).toThrow(/标的代码/)
    expect(() => validateSymbol('000 001')).toThrow(/标的代码/)
  })
})

describe('validateBars', () => {
  it('accepts in-range integers', () => {
    expect(validateBars(5)).toBe(5)
    expect(validateBars(1500)).toBe(1500)
  })

  it('rejects out-of-range and non-integer counts', () => {
    expect(() => validateBars(4)).toThrow(/K线根数/)
    expect(() => validateBars(1501)).toThrow(/K线根数/)
    expect(() => validateBars(1.5)).toThrow(/K线根数/)
  })
})

describe('DataSourceBreaker', () => {
  it('trips after the consecutive-failure threshold and fails fast', () => {
    const breaker = new DataSourceBreaker(2)
    expect(breaker.isTripped).toBe(false)
    breaker.failure()
    expect(breaker.isTripped).toBe(false)
    expect(() => { breaker.check() }).not.toThrow()
    breaker.failure()
    expect(breaker.isTripped).toBe(true)
    expect(() => { breaker.check() }).toThrow(QuantError)
    expect(() => { breaker.check() }).toThrow(/已熔断/)
  })

  it('resets the count on success', () => {
    const breaker = new DataSourceBreaker(2)
    breaker.failure()
    breaker.success()
    breaker.failure()
    expect(breaker.isTripped).toBe(false)
  })
})

describe('fetchKline', () => {
  it('returns the validated series and records success', async () => {
    const breaker = new DataSourceBreaker(2)
    const series = await fetchKline(kernelReturning(BARS), breaker, OPTIONS)
    expect(series).toEqual(BARS)
    expect(breaker.isTripped).toBe(false)
  })

  it('sends the source, symbol, period, bars, retries, and cache dir in the request', async () => {
    const kernel = kernelReturning(BARS)
    await fetchKline(kernel, new DataSourceBreaker(2), OPTIONS)
    expect((kernel.request as ReturnType<typeof vi.fn>).mock.calls[0]?.[0]).toBe('get_kline')
    expect((kernel.request as ReturnType<typeof vi.fn>).mock.calls[0]?.[1]).toEqual({
      source: 'synthetic',
      symbol: '000001',
      period: 'daily',
      bars: 30,
      max_retries: 0,
      cache_dir: '/tmp/cache',
    })
  })

  it('rejects wire-shape violations as DATA', async () => {
    const breaker = new DataSourceBreaker(5)
    await expect(fetchKline(kernelReturning([{ date: 'x' }]), breaker, OPTIONS)).rejects.toThrow(/不符合规格的K线/)
    await expect(fetchKline(kernelReturning([]), breaker, OPTIONS)).rejects.toThrow(QuantError)
  })

  it('counts NETWORK and DATA failures toward the breaker', async () => {
    const breaker = new DataSourceBreaker(2)
    const kernel = kernelReturning(() => {
      throw new QuantError('NETWORK', '超时')
    })
    await expect(fetchKline(kernel, breaker, OPTIONS)).rejects.toThrow(/超时/)
    await expect(fetchKline(kernel, breaker, OPTIONS)).rejects.toThrow(/超时/)
    expect(breaker.isTripped).toBe(true)
    await expect(fetchKline(kernelReturning(BARS), breaker, OPTIONS)).rejects.toThrow(/已熔断/)
  })

  it('does not count cancellation toward the breaker', async () => {
    const breaker = new DataSourceBreaker(1)
    const kernel = kernelReturning(() => {
      throw new QuantError('CANCELLED', '调用已取消')
    })
    await expect(fetchKline(kernel, breaker, OPTIONS)).rejects.toThrow(/已取消/)
    expect(breaker.isTripped).toBe(false)
  })

  it('validates the symbol and bars before touching the breaker', async () => {
    const breaker = new DataSourceBreaker(1)
    const kernel = kernelReturning(BARS)
    await expect(fetchKline(kernel, breaker, { ...OPTIONS, symbol: '!!' })).rejects.toThrow(/标的代码/)
    await expect(fetchKline(kernel, breaker, { ...OPTIONS, bars: 0 })).rejects.toThrow(/K线根数/)
    expect((kernel.request as ReturnType<typeof vi.fn>).mock.calls).toHaveLength(0)
  })
})
