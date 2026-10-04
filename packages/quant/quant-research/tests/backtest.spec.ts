import { describe, expect, it, vi } from 'vitest'
import { runBacktest, validateBacktestParams } from '../src/pcpt/backtest.ts'
import { QuantError } from '../src/errors.ts'
import type { QuantKernelClient } from '../src/kernel-client/client.ts'
import type { KlineBar } from '../src/pdat/datasource.ts'

const BARS: KlineBar[] = [
  { date: '2024-01-02', open: 1, high: 2, low: 0.5, close: 1.5, volume: 10 },
  { date: '2024-01-03', open: 1.5, high: 2.5, low: 1, close: 2, volume: 20 },
]

const REPORT = {
  symbol: '000001',
  fast: 2,
  slow: 3,
  initial_cash: 1_000_000,
  final_equity: 1_050_000,
  equity: [{ date: '2024-01-02', value: 1_000_000 }, { date: '2024-01-03', value: 1_050_000 }],
  trades: [{ date: '2024-01-03', side: 'buy', price: 1.5, shares: 600_000 }],
  metrics: {
    total_return: 0.05,
    annual_return: 12.5,
    max_drawdown: 0,
    sharpe: 1.8,
    win_rate: 1,
    trade_count: 1,
  },
}

function kernelReturning(result: unknown): QuantKernelClient {
  return { request: vi.fn(async () => result) } as unknown as QuantKernelClient
}

const PARAMS = { fast: 2, slow: 3, initialCash: 1_000_000, feeRate: 0.0003 }

describe('validateBacktestParams', () => {
  it('accepts a valid set', () => {
    expect(() => { validateBacktestParams(250, PARAMS) }).not.toThrow()
  })

  it('rejects window-bound violations', () => {
    expect(() => { validateBacktestParams(250, { ...PARAMS, fast: 1 }) }).toThrow(/快线窗口/)
    expect(() => { validateBacktestParams(250, { ...PARAMS, fast: 121 }) }).toThrow(/快线窗口/)
    expect(() => { validateBacktestParams(250, { ...PARAMS, slow: 2 }) }).toThrow(/慢线窗口/)
    expect(() => { validateBacktestParams(250, { ...PARAMS, slow: 251 }) }).toThrow(/慢线窗口/)
    expect(() => { validateBacktestParams(250, { ...PARAMS, fast: 1.5 }) }).toThrow(/快线窗口/)
  })

  it('requires fast < slow', () => {
    expect(() => { validateBacktestParams(250, { ...PARAMS, fast: 3, slow: 3 }) }).toThrow(/必须小于/)
  })

  it('rejects cash and fee-rate violations', () => {
    expect(() => { validateBacktestParams(250, { ...PARAMS, initialCash: 0 }) }).toThrow(/初始资金/)
    expect(() => { validateBacktestParams(250, { ...PARAMS, initialCash: Number.POSITIVE_INFINITY }) }).toThrow(/初始资金/)
    expect(() => { validateBacktestParams(250, { ...PARAMS, feeRate: -0.1 }) }).toThrow(/手续费率/)
    expect(() => { validateBacktestParams(250, { ...PARAMS, feeRate: 0.5 }) }).toThrow(/手续费率/)
  })

  it('requires the bars to cover the slow window and respect the cap', () => {
    expect(() => { validateBacktestParams(3, PARAMS) }).toThrow(/至少覆盖慢线窗口/)
    expect(() => { validateBacktestParams(1501, PARAMS) }).toThrow(/1500/)
    expect(() => { validateBacktestParams(2.5, PARAMS) }).toThrow(/K线根数/)
  })
})

describe('runBacktest', () => {
  it('sends the bars and parameters to the kernel and returns the validated report', async () => {
    const kernel = kernelReturning(REPORT)
    const report = await runBacktest(kernel, '000001', BARS, PARAMS)
    expect(report.metrics.total_return).toBe(0.05)
    const request = (kernel.request as ReturnType<typeof vi.fn>).mock.calls[0] as unknown as [string, Record<string, unknown>]
    expect(request[0]).toBe('backtest')
    expect(request[1]['fast']).toBe(2)
    expect(request[1]['slow']).toBe(3)
    expect(request[1]['initial_cash']).toBe(1_000_000)
    expect(request[1]['fee_rate']).toBe(0.0003)
    expect(request[1]['bars']).toEqual(BARS)
  })

  it('rejects wire-shape violations as DATA', async () => {
    await expect(runBacktest(kernelReturning({ symbol: '' }), '000001', BARS, PARAMS))
      .rejects.toThrow(/不符合规格的报告/)
    await expect(runBacktest(kernelReturning(null), '000001', BARS, PARAMS))
      .rejects.toThrow(QuantError)
  })
})
