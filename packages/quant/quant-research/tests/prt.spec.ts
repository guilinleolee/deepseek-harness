/**
 * PRT risk metrics, TypeScript side: unit tests for the historical-simulation
 * tail metrics, volatility, drawdown, concentration checks, and the two
 * stress transforms.
 */
import { describe, expect, it } from 'vitest'
import {
  annualVolatility, concentrationBreaches, dailyReturns, empiricalQuantile, historicalCVar,
  historicalVar, maxDrawdown, shockBars, validateStressParams,
} from '../src/prt/risk.ts'
import { CONFIDENCE_LIMITS, SHOCK_LIMITS } from '../src/compliance.ts'
import { QuantError } from '../src/errors.ts'
import type { KlineBar } from '../src/pdat/datasource.ts'

const CLOSES = [100, 102, 101, 103, 99, 98, 102, 104, 103, 105]

describe('dailyReturns', () => {
  it('computes simple returns', () => {
    const returns = dailyReturns([100, 110, 99])
    expect(returns[0]).toBeCloseTo(0.1, 12)
    expect(returns[1]).toBeCloseTo(-0.1, 12)
  })

  it('rejects short series and non-positive prices', () => {
    expect(() => dailyReturns([100])).toThrow(QuantError)
    expect(() => dailyReturns([0, 1])).toThrow(/必须为正数/)
  })
})

describe('empiricalQuantile', () => {
  it('returns exact ranks and interpolates between them', () => {
    const sample = [3, 1, 2]
    expect(empiricalQuantile(sample, 0)).toBe(1)
    expect(empiricalQuantile(sample, 1)).toBe(3)
    expect(empiricalQuantile(sample, 0.5)).toBe(2)
    expect(empiricalQuantile([0, 1, 2, 3], 0.25)).toBe(0.75)
  })
})

describe('historicalVar / historicalCVar', () => {
  const returns = [0.02, -0.01, 0.03, -0.05, 0.01, -0.02, 0.04, -0.03, 0.015, -0.005]

  it('reads the empirical tail at the confidence level', () => {
    // q = 0.2 over the sorted sample interpolates to -0.022 → VaR 0.022.
    expect(historicalVar(returns, 0.8)).toBeCloseTo(0.022, 12)
    // The tail beyond −0.022 holds −0.05 and −0.03 → mean loss 0.04.
    expect(historicalCVar(returns, 0.8)).toBeCloseTo(0.04, 12)
  })

  it('reads zero when the empirical tail holds no loss', () => {
    expect(historicalVar([0.01, 0.02, 0.03], 0.8)).toBe(0)
    expect(historicalCVar([0.01, 0.02, 0.03], 0.8)).toBe(0)
  })

  it('rejects out-of-range confidence and short samples', () => {
    expect(() => historicalVar(returns, 0.5)).toThrow(QuantError)
    expect(() => historicalVar(returns, 1)).toThrow(/置信度/)
    expect(() => historicalCVar([0.01], 0.95)).toThrow(/收益率样本/)
  })

  it('exposes the hard bounds from the compliance gate', () => {
    expect(CONFIDENCE_LIMITS).toEqual({ min: 0.8, max: 0.99, default: 0.95 })
    expect(SHOCK_LIMITS).toEqual({ min: 0.01, max: 0.5, default: 0.1 })
  })
})

describe('annualVolatility', () => {
  it('reads zero on constant returns and annualizes the sample deviation', () => {
    expect(annualVolatility([0.01, 0.01, 0.01])).toBe(0)
    const vol = annualVolatility([0.1, -0.1])
    // Sample std = 0.2/√2 ≈ 0.141421; annualized by √252.
    expect(vol).toBeCloseTo((0.2 / Math.sqrt(2)) * Math.sqrt(252), 10)
  })

  it('rejects short samples', () => {
    expect(() => annualVolatility([0.01])).toThrow(QuantError)
  })
})

describe('maxDrawdown', () => {
  it('reads the largest peak-to-trough decline', () => {
    expect(maxDrawdown([100, 110, 90, 95])).toBeCloseTo(20 / 110, 12)
    expect(maxDrawdown([100, 120, 130, 125])).toBeCloseTo(5 / 130, 12)
  })

  it('ignores the ratio guard on a non-positive path', () => {
    expect(maxDrawdown([0, 0])).toBe(0)
  })
})

describe('concentrationBreaches', () => {
  it('lists per-symbol overweights and the total overage', () => {
    const breaches = concentrationBreaches({ A: 0.5, B: 0.3, C: 0.2 }, 0.4, 1.0)
    expect(breaches.symbols).toEqual(['A'])
    expect(breaches.total).toBeNull()

    const over = concentrationBreaches({ A: 0.6, B: 0.45 }, 0.4, 0.9)
    expect(over.symbols).toEqual(['A', 'B'])
    expect(over.total).toBeCloseTo(1.05, 12)
  })
})

function bar(index: number, close: number): KlineBar {
  return { date: `2024-01-${String(index + 1).padStart(2, '0')}`, open: close, high: close, low: close, close, volume: 1000 }
}

describe('shockBars', () => {
  const bars = CLOSES.map((close, index) => bar(index, close))

  it('gaps the crash segment down and leaves the rest untouched', () => {
    const shocked = shockBars(bars, { scenario: 'crash', shock: 0.2 })
    expect(shocked[0]).toEqual(bars[0])
    const segmentStart = Math.floor(bars.length * (2 / 3))
    expect(shocked[segmentStart]?.close).toBeCloseTo((bars[segmentStart] as KlineBar).close * 0.8, 10)
    expect(shocked[bars.length - 1]?.close).toBeCloseTo((bars[bars.length - 1] as KlineBar).close * 0.8, 10)
    // The input is never mutated.
    expect(bars[segmentStart]?.close).toBe(CLOSES[segmentStart])
  })

  it('slides the liquidity segment down step by step and dries the volume', () => {
    const shocked = shockBars(bars, { scenario: 'liquidity', shock: 0.3 })
    const start = Math.floor(bars.length * (2 / 3))
    const length = bars.length - start
    const reference = (bars[start - 1] as KlineBar).close
    const first = shocked[start] as KlineBar
    const last = shocked[bars.length - 1] as KlineBar
    expect(first.close).toBeCloseTo(reference * (1 - 0.3 / length), 10)
    expect(last.close).toBeCloseTo(reference * 0.7, 10)
    expect(last.volume).toBeCloseTo(1000 * 0.7, 10)
  })

  it('tolerates an empty series via the reference fallback', () => {
    expect(shockBars([], { scenario: 'crash', shock: 0.1 })).toEqual([])
    expect(shockBars([], { scenario: 'liquidity', shock: 0.1 })).toEqual([])
  })

  it('references the first bar when the segment covers the whole window', () => {
    const shocked = shockBars(bars, { scenario: 'liquidity', shock: 0.5, segment: 1 })
    const first = shocked[0] as KlineBar
    expect(first.close).toBeCloseTo((bars[0] as KlineBar).close * (1 - 0.5 / bars.length), 10)
    expect(shocked[bars.length - 1]?.close).toBeCloseTo((bars[0] as KlineBar).close * 0.5, 10)
  })

  it('rejects impossible scenarios, shocks, and segments', () => {
    expect(() => shockBars(bars, { scenario: 'pandemic' as never, shock: 0.1 })).toThrow(QuantError)
    expect(() => shockBars(bars, { scenario: 'crash', shock: 0.9 })).toThrow(/冲击幅度/)
    expect(() => shockBars(bars, { scenario: 'crash', shock: 0.1, segment: 2 })).toThrow(/压力段占比/)
    expect(validateStressParams({ scenario: 'crash', shock: SHOCK_LIMITS.default })).toBeUndefined()
  })
})
