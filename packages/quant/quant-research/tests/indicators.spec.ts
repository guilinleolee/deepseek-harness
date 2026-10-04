import { describe, expect, it } from 'vitest'
import { atr, boll, ema, macd, rsi, sma } from '../src/paat/indicators.ts'
import type { KlineBar } from '../src/pdat/datasource.ts'

describe('sma', () => {
  it('computes exact values after the warm-up', () => {
    expect(sma([1, 2, 3, 4], 2)).toEqual([null, 1.5, 2.5, 3.5])
  })

  it('accepts a full-length window', () => {
    expect(sma([2, 4, 6], 3)).toEqual([null, null, 4])
  })

  it('rejects impossible windows', () => {
    expect(() => sma([1, 2], 0)).toThrow(/sma 窗口/)
    expect(() => sma([1, 2], 3)).toThrow(/sma 窗口/)
    expect(() => sma([1, 2], 1.5)).toThrow(/sma 窗口/)
  })
})

describe('ema', () => {
  it('seeds with the SMA and smooths at 2/(n+1)', () => {
    expect(ema([1, 2, 3, 4, 5], 3)).toEqual([null, null, 2, 3, 4])
  })

  it('rejects impossible windows', () => {
    expect(() => ema([1], 2)).toThrow(/ema 窗口/)
  })
})

describe('macd', () => {
  it('rejects fast >= slow', () => {
    expect(() => macd([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5, 5)).toThrow(/快线窗口/)
    expect(() => macd([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 6, 5)).toThrow(/快线窗口/)
  })

  it('degrades the signal line to nulls when the defined tail is too short', () => {
    const values = Array.from({ length: 10 }, (_, index) => 10 + index)
    const { macdLine, signalLine, histogram } = macd(values, 3, 6, 9)
    expect(macdLine[5]).not.toBeNull()
    expect(signalLine.every(value => value === null)).toBe(true)
    expect(histogram.every(value => value === null)).toBe(true)
  })

  it('aligns all three lines with the input and keeps histogram = macd - signal', () => {
    const values = Array.from({ length: 40 }, (_, index) => 10 + index * 0.5)
    const { macdLine, signalLine, histogram } = macd(values, 3, 6, 3)
    expect(macdLine).toHaveLength(40)
    expect(signalLine).toHaveLength(40)
    // MACD line warm-up: the slow EMA (6) defines from index 5.
    expect(macdLine.slice(0, 5)).toEqual(Array.from({ length: 5 }, () => null))
    expect(macdLine[5]).not.toBeNull()
    // Signal EMA (3) runs over the 35 defined MACD values: first reading at index 7.
    expect(signalLine[6]).toBeNull()
    expect(signalLine[7]).not.toBeNull()
    for (const [index, value] of macdLine.entries()) {
      if (value === null || signalLine[index] === null) continue
      expect(histogram[index]).toBeCloseTo(value - (signalLine[index] as number), 10)
    }
  })
})

describe('rsi', () => {
  it('reads 100 on pure gains and 0 on pure losses', () => {
    const rising = Array.from({ length: 20 }, (_, index) => index + 1)
    expect(rsi(rising, 14)?.[19]).toBe(100)
    const falling = Array.from({ length: 20 }, (_, index) => 20 - index)
    expect(rsi(falling, 14)?.[19]).toBe(0)
  })

  it('warm-up positions stay null and window 1 flips signs', () => {
    const series = rsi([1, 2, 1], 1)
    expect(series[0]).toBeNull()
    expect(series[1]).toBe(100)
    expect(series[2]).toBe(0)
  })

  it('rejects windows that cannot see one diff', () => {
    expect(() => rsi([1], 1)).toThrow(/rsi 窗口/)
    expect(() => rsi([1, 2], 2)).toThrow(/rsi 窗口/)
    expect(() => rsi([1, 2, 3], 1.5)).toThrow(/rsi 窗口/)
    expect(() => rsi([1, 2, 3], 0)).toThrow(/rsi 窗口/)
  })
})

describe('boll', () => {
  it('collapses onto the middle band for a constant series', () => {
    const constant = [5, 5, 5, 5, 5]
    const { middle, upper, lower } = boll(constant, 3, 2)
    expect(middle[2]).toBe(5)
    expect(upper[2]).toBe(5)
    expect(lower[2]).toBe(5)
    expect(middle[0]).toBeNull()
  })

  it('spreads the bands by the deviation multiple', () => {
    const { upper, lower } = boll([1, 2, 3, 4, 5, 6], 3, 1)
    expect(upper[3]as number).toBeCloseTo(3 + Math.sqrt(2 / 3), 10)
    expect(lower[3] as number).toBeCloseTo(3 - Math.sqrt(2 / 3), 10)
  })

  it('rejects impossible windows', () => {
    expect(() => boll([1, 2], 5)).toThrow(/sma 窗口/)
  })
})

function bar(close: number, high?: number, low?: number): KlineBar {
  return {
    date: '2024-01-02',
    open: close,
    high: high ?? close,
    low: low ?? close,
    close,
    volume: 1,
  }
}

describe('atr', () => {
  it('keeps the wilder average over constant ranges', () => {
    const bars = Array.from({ length: 20 }, (_, index) => bar(100 + index, 101 + index, 99 + index))
    const series = atr(bars, 14)
    expect(series[12]).toBeNull()
    expect(series[13]).toBe(2)
    expect(series[19]).toBe(2)
  })

  it('uses the previous close in the true range', () => {
    const bars = [
      bar(100, 110, 95),
      bar(102, 120, 100),
    ]
    const series = atr(bars, 1)
    expect(series[0]).toBe(15)
    expect(series[1]).toBe(20)
  })

  it('rejects impossible windows', () => {
    expect(() => atr([bar(1)], 2)).toThrow(/atr 窗口/)
  })
})
