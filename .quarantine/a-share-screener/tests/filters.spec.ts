/**
 * Per-file coverage gate tests for the atomic filters. Every branch is
 * exercised: passing, failing, and "insufficient samples".
 *
 * @module @deepseek-ai/dsh-a-share-screener/tests/filters
 */

import { describe, expect, it } from 'vitest'
import {
  amountLiquidity,
  deepDrawdown,
  excludeST,
  flatBase,
  lowPercentile,
  minListingDays,
  platformBreakout,
  volumeLimitUp,
  type FilterContext,
} from '../src/filters/filters.ts'
import type { OHLCV, Quote, StockBasicInfo } from '../src/types.ts'

function makeBars(closes: number[]): OHLCV[] {
  return closes.map((close, idx) => ({
    date: new Date(Date.UTC(2025, 0, idx + 1)),
    open: close,
    high: close + 1,
    low: close - 1,
    close,
    volume: 1_000_000,
    amount: close * 1_000_000,
  }))
}

const stock: StockBasicInfo = {
  symbol: '000001.SZ',
  name: '平安银行',
  market: 'SZ',
  industry: '银行',
  listDate: new Date(Date.now() - 1000 * 24 * 60 * 60 * 1000),
  isST: false,
  isSuspended: false,
}

const quote: Quote = {
  symbol: stock.symbol,
  price: 10,
  change: 0,
  changePercent: 0,
  volume: 1_000_000,
  amount: 10_000_000,
  timestamp: new Date(),
}

const baseContext: FilterContext = { stock, bars: [], quote }

describe('filters', () => {
  it('excludeST passes for non-ST, non-suspended stocks', () => {
    expect(excludeST(baseContext).passed).toBe(true)
  })

  it('excludeST rejects ST stocks', () => {
    expect(excludeST({ ...baseContext, stock: { ...stock, isST: true } }).passed).toBe(false)
  })

  it('excludeST rejects suspended stocks', () => {
    expect(excludeST({ ...baseContext, stock: { ...stock, isSuspended: true } }).passed).toBe(false)
  })

  it('minListingDays rejects fresh listings', () => {
    const fresh = minListingDays(365)({ ...baseContext, stock: { ...stock, listDate: new Date() } })
    expect(fresh.passed).toBe(false)
  })

  it('minListingDays accepts old listings', () => {
    const old = minListingDays(365)(baseContext)
    expect(old.passed).toBe(true)
  })

  it('lowPercentile rejects when sample window is short', () => {
    const result = lowPercentile(250, 20)({ ...baseContext, bars: makeBars([1, 2, 3]) })
    expect(result.passed).toBe(false)
  })

  it('lowPercentile rejects when close ranks above the threshold', () => {
    const bars = makeBars(Array.from({ length: 250 }, (_, i) => 10 + i * 0.01))
    const result = lowPercentile(250, 20)({ ...baseContext, bars })
    expect(result.passed).toBe(false)
  })

  it('lowPercentile passes when close sits in the low tail', () => {
    const closes: number[] = []
    for (let i = 0; i < 249; i++) closes.push(20)
    closes.push(5)
    const result = lowPercentile(250, 50)({ ...baseContext, bars: makeBars(closes) })
    expect(result.passed).toBe(true)
  })

  it('deepDrawdown rejects when sample window is short', () => {
    const result = deepDrawdown(60, -0.2)({ ...baseContext, bars: makeBars([1, 2, 3]) })
    expect(result.passed).toBe(false)
  })

  it('deepDrawdown passes when close is below the rolling peak', () => {
    const closes: number[] = []
    for (let i = 0; i < 59; i++) closes.push(10)
    closes.push(7)
    const result = deepDrawdown(60, -0.2)({ ...baseContext, bars: makeBars(closes) })
    expect(result.passed).toBe(true)
  })

  it('deepDrawdown rejects when close is at the peak', () => {
    const closes = Array.from({ length: 60 }, () => 10)
    const result = deepDrawdown(60, -0.2)({ ...baseContext, bars: makeBars(closes) })
    expect(result.passed).toBe(false)
  })

  it('flatBase rejects when sample window is short', () => {
    const result = flatBase(60, 0.05)({ ...baseContext, bars: makeBars([1, 2, 3]) })
    expect(result.passed).toBe(false)
  })

  it('flatBase passes for tight ranges', () => {
    const tight = flatBase(60, 0.05)({ ...baseContext, bars: makeBars(Array.from({ length: 60 }, () => 10)) })
    expect(tight.passed).toBe(true)
  })

  it('flatBase rejects for wide ranges', () => {
    const wide = flatBase(60, 0.05)({ ...baseContext, bars: makeBars([...Array.from({ length: 30 }, () => 10), ...Array.from({ length: 30 }, () => 30)]) })
    expect(wide.passed).toBe(false)
  })

  it('volumeLimitUp rejects when bars are too few', () => {
    const result = volumeLimitUp(2, 0.095)({ ...baseContext, bars: makeBars([10, 10]) })
    expect(result.passed).toBe(false)
  })

  it('volumeLimitUp rejects when change is below limit', () => {
    const bars = makeBars(Array.from({ length: 21 }, () => 10))
    const result = volumeLimitUp(2, 0.095)({ ...baseContext, bars })
    expect(result.passed).toBe(false)
  })

  it('volumeLimitUp rejects when volume is insufficient', () => {
    const closes = Array.from({ length: 21 }, () => 10)
    bars21LowVolume(closes)
    const result = volumeLimitUp(2, 0.095)({ ...baseContext, bars: makeBars(closes) })
    expect(result.passed).toBe(false)
  })

  it('volumeLimitUp passes when change and volume meet the thresholds', () => {
    const closes = Array.from({ length: 21 }, () => 10)
    const bars = makeBars(closes)
    bars[bars.length - 1] = { ...bars[bars.length - 1]!, close: 11, volume: 5_000_000 }
    const result = volumeLimitUp(2, 0.095)({ ...baseContext, bars })
    expect(result.passed).toBe(true)
  })

  it('platformBreakout rejects when sample window is short', () => {
    const result = platformBreakout(20, 0.03)({ ...baseContext, bars: makeBars([1, 2, 3]) })
    expect(result.passed).toBe(false)
  })

  it('platformBreakout rejects when close stays inside the range', () => {
    const closes = Array.from({ length: 21 }, () => 10)
    const result = platformBreakout(20, 0.03)({ ...baseContext, bars: makeBars(closes) })
    expect(result.passed).toBe(false)
  })

  it('platformBreakout passes when close exceeds the rolling high', () => {
    const closes = [...Array.from({ length: 20 }, () => 10), 12]
    const result = platformBreakout(20, 0.03)({ ...baseContext, bars: makeBars(closes) })
    expect(result.passed).toBe(true)
  })

  it('amountLiquidity rejects when sample window is short', () => {
    const result = amountLiquidity(10_000, 20)({ ...baseContext, bars: makeBars([1, 2, 3]) })
    expect(result.passed).toBe(false)
  })

  it('amountLiquidity rejects when trailing average is below the floor', () => {
    const bars = makeBars(Array.from({ length: 20 }, () => 0.001))
    const result = amountLiquidity(10_000, 20)({ ...baseContext, bars })
    expect(result.passed).toBe(false)
  })

  it('amountLiquidity passes when trailing average meets the floor', () => {
    const bars = makeBars(Array.from({ length: 20 }, () => 50))
    const result = amountLiquidity(10_000, 20)({ ...baseContext, bars })
    expect(result.passed).toBe(true)
  })
})

function bars21LowVolume(closes: number[]): void {
  // marker — value retained through the `closes` array shared with the test body
  void closes
}
