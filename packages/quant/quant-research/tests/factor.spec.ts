/**
 * PAAT factor and IC tests: deterministic factor computation, Spearman rank
 * correlation, rolling IC, and Information Ratio.
 */
import { describe, expect, it } from 'vitest'
import {
  DEFAULT_FACTOR_WINDOWS, FACTOR_NAMES, computeFactor, momentum, pricePosition, volumeRatio,
  volatility,
} from '../src/paat/factors.ts'
import { informationRatio, rollingIC, spearman } from '../src/paat/ic.ts'
import { QuantError } from '../src/errors.ts'
import type { KlineBar } from '../src/pdat/datasource.ts'

function makeBars(closes: number[], volumes?: number[]): KlineBar[] {
  return closes.map((close, index) => ({
    date: `2024-01-${String(index + 1).padStart(2, '0')}`,
    open: close * 0.99,
    high: close * 1.01,
    low: close * 0.98,
    close,
    volume: volumes?.[index] ?? 1000 + index * 10,
  }))
}

describe('factors', () => {
  const closes = [100, 102, 101, 103, 105, 104, 106, 108, 107, 110]
  const bars = makeBars(closes, closes.map((_, i) => 1000 + i * 100))

  it('momentum computes rate of change after the window', () => {
    const result = momentum(bars, 3)
    expect(result[0]).toBeNull()
    expect(result[2]).toBeNull()
    expect(result[3]).toBeCloseTo(103 / 100 - 1, 10)
    expect(result[9]).toBeCloseTo(110 / 106 - 1, 10)
  })

  it('volatility computes rolling sample std', () => {
    const result = volatility(bars, 3)
    expect(result[0]).toBeNull()
    expect(result[3]).not.toBeNull()
    expect(result[9]).not.toBeNull()
  })

  it('volumeRatio reads current/mean ratio', () => {
    const vols = [100, 100, 100, 300]
    const vBars = makeBars([10, 10, 10, 10], vols)
    const result = volumeRatio(vBars, 3)
    expect(result[0]).toBeNull()
    expect(result[3]).not.toBeNull()
    expect(result[3]).toBeCloseTo(300 / ((100 + 100 + 300) / 3), 6)
  })

  it('pricePosition reads [0,1] range position', () => {
    const result = pricePosition(bars, 5)
    expect(result[4]).not.toBeNull()
    const value = result[9] as number
    expect(value).toBeGreaterThanOrEqual(0)
    expect(value).toBeLessThanOrEqual(1)
  })

  it('rejects impossible windows', () => {
    expect(() => momentum(bars, 0)).toThrow(QuantError)
    expect(() => momentum(bars, 11)).toThrow(QuantError)
    expect(() => volatility(bars, 1)).toThrow(QuantError)
    expect(() => volumeRatio(bars, 0)).toThrow(QuantError)
    expect(() => pricePosition(bars, 0)).toThrow(QuantError)
  })

  it('exposes the factor set and default windows', () => {
    expect(FACTOR_NAMES).toEqual(['momentum', 'volatility', 'volume_ratio', 'price_position'])
    expect(DEFAULT_FACTOR_WINDOWS.momentum).toBe(20)
  })

  it('pricePosition reads 0.5 for zero range (flat bars)', () => {
    const flat = makeBars([100, 100, 100])
    const result = pricePosition(flat, 3)
    // high = close * 1.01, low = close * 0.98 → close sits at 2/3 of the range
    expect(result[2]).toBeCloseTo(2 / 3, 10)
  })

  it('computeFactor dispatches by name', () => {
    for (const name of FACTOR_NAMES) {
      const series = computeFactor(name, bars, 3)
      expect(series).toHaveLength(bars.length)
    }
  })
})

describe('spearman', () => {
  it('reads 1 for perfectly monotonic pairs', () => {
    expect(spearman([1, 2, 3], [10, 20, 30])).toBe(1)
  })

  it('reads -1 for inversely monotonic pairs', () => {
    expect(spearman([1, 2, 3], [30, 20, 10])).toBe(-1)
  })

  it('reads null for degenerate inputs', () => {
    expect(spearman([1], [1])).toBeNull()
    expect(spearman([], [])).toBeNull()
  })

  it('handles ties with average ranks', () => {
    const result = spearman([1, 1, 2], [1, 2, 3])
    expect(result).not.toBeNull()
    expect(result as number).toBeGreaterThan(0)
  })
})

describe('rollingIC', () => {
  it('produces IC periods for a trending series', () => {
    const bars = makeBars(Array.from({ length: 30 }, (_, i) => 100 + i))
    const mom = momentum(bars, 5)
    const periods = rollingIC(bars, mom, 3, 10)
    expect(periods.length).toBeGreaterThan(0)
    for (const period of periods) {
      expect(period.ic).toBeGreaterThanOrEqual(-1)
      expect(period.ic).toBeLessThanOrEqual(1)
    }
  })

  it('rejects short series', () => {
    const bars = makeBars([100, 101, 102])
    expect(() => rollingIC(bars, [null, 0.01, 0.02], 3, 10)).toThrow(QuantError)
  })
})

describe('informationRatio', () => {
  it('reads null for degenerate IC sets', () => {
    expect(informationRatio([])).toBeNull()
    expect(informationRatio([{ date: 'd', ic: 0.5 }])).toBeNull()
  })

  it('reads null when all ICs are identical (std = 0)', () => {
    const periods = [
      { date: 'a', ic: 0.5 }, { date: 'b', ic: 0.5 },
    ]
    expect(informationRatio(periods)).toBeNull()
  })

  it('computes IR from varying ICs', () => {
    const periods = [{ date: 'a', ic: 0.3 }, { date: 'b', ic: 0.7 }]
    const ir = informationRatio(periods)
    expect(ir).not.toBeNull()
  })
})
