/**
 * Atomic filter primitives. Each filter receives the data it needs and returns
 * a `FilterOutcome` carrying the verdict, an optional score contribution, and
 * evidence lines the strategy engine surfaces in the result.
 *
 * @module @deepseek-ai/dsh-a-share-screener/filters
 */

import type { OHLCV, StockBasicInfo, Quote } from '../types.ts'

export interface FilterContext {
  stock: StockBasicInfo
  bars: OHLCV[]
  quote: Quote
}

export interface FilterOutcome {
  passed: boolean
  score: number
  evidence: string[]
}

export type Filter = (ctx: FilterContext) => FilterOutcome

const PASS: FilterOutcome = { passed: true, score: 0, evidence: [] }
const FAIL = (evidence: string): FilterOutcome => ({ passed: false, score: 0, evidence: [evidence] })

/** Excludes ST, *ST, suspended, and halted listings. */
export function excludeST(ctx: FilterContext): FilterOutcome {
  if (ctx.stock.isST) return FAIL('ST/退市风险股')
  if (ctx.stock.isSuspended) return FAIL('停牌')
  return PASS
}

/** Listing-age floor; defaults to one calendar year (≈ 252 trading days). */
export function minListingDays(days: number): Filter {
  const cutoff = new Date(Date.now() - days * 24 * 60 * 60 * 1000)
  return ({ stock }) => {
    if (stock.listDate.getTime() > cutoff.getTime()) return FAIL(`上市不足 ${String(days)} 天`)
    return PASS
  }
}

/** `lowPercentile(window, percentile)` — close at or below the `percentile`-th rank over the lookback. */
export function lowPercentile(window: number, percentile: number): Filter {
  return ({ bars }) => {
    if (bars.length < window) return FAIL(`样本不足 ${String(window)}`)
    const windowBars = bars.slice(-window)
    const last = windowBars[windowBars.length - 1]!.close
    const sorted = windowBars.map((b) => b.close).sort((a, b) => a - b)
    const rank = (sorted.findIndex((value) => value >= last) / sorted.length) * 100
    if (rank <= percentile) {
      return { passed: true, score: percentile - rank, evidence: [`低分位 ${rank.toFixed(1)}% ≤ ${String(percentile)}%`] }
    }
    return FAIL(`价格分位 ${rank.toFixed(1)}% 高于 ${String(percentile)}%`)
  }
}

/** `deepDrawdown(threshold)` — close at least `threshold` below the rolling peak. */
export function deepDrawdown(lookbackDays: number, threshold: number): Filter {
  return ({ bars }) => {
    if (bars.length < lookbackDays) return FAIL(`样本不足 ${String(lookbackDays)}`)
    const window = bars.slice(-lookbackDays)
    const peak = window.reduce((max, bar) => (bar.close > max ? bar.close : max), window[0]!.close)
    const last = window[window.length - 1]!.close
    const drawdown = (last - peak) / peak
    if (drawdown <= threshold) {
      return { passed: true, score: Math.abs(drawdown) * 100, evidence: [`回撤 ${(drawdown * 100).toFixed(1)}% ≤ ${String(threshold * 100)}%`] }
    }
    return FAIL(`回撤 ${(drawdown * 100).toFixed(1)}% 未达 ${String(threshold * 100)}%`)
  }
}

/** `flatBase(window, range)` — max-min range of closes bounded by `range`. */
export function flatBase(window: number, range: number): Filter {
  return ({ bars }) => {
    if (bars.length < window) return FAIL(`样本不足 ${String(window)}`)
    const windowBars = bars.slice(-window)
    const max = windowBars.reduce((m, b) => (b.close > m ? b.close : m), windowBars[0]!.close)
    const min = windowBars.reduce((m, b) => (b.close < m ? b.close : m), windowBars[0]!.close)
    const spread = (max - min) / max
    if (spread <= range) {
      return { passed: true, score: (range - spread) * 100, evidence: [`区间 ${(spread * 100).toFixed(1)}% ≤ ${String(range * 100)}%`] }
    }
    return FAIL(`区间 ${(spread * 100).toFixed(1)}% 超过 ${String(range * 100)}%`)
  }
}

/** `volumeLimitUp(multiplier, limitUpPct)` — close at or above `(1 + limitUpPct) * prior`, volume at least `multiplier * 20-day average`. */
export function volumeLimitUp(multiplier: number, limitUpPct: number): Filter {
  return ({ bars }) => {
    if (bars.length < 21) return FAIL('样本不足 21')
    const last = bars[bars.length - 1]!
    const prior = bars[bars.length - 2]!.close
    const change = (last.close - prior) / prior
    if (change < limitUpPct) return FAIL(`涨幅 ${(change * 100).toFixed(1)}% 未达 ${String(limitUpPct * 100)}%`)
    const avg = averageVolume(bars.slice(-21, -1))
    if (last.volume < avg * multiplier) return FAIL(`量能不足 ${String(multiplier)} 倍均量`)
    return { passed: true, score: last.volume / avg, evidence: [`量能 ${(last.volume / avg).toFixed(2)}× 均量`] }
  }
}

/** `platformBreakout(window, breakoutPct)` — close exceeds rolling high by `breakoutPct`. */
export function platformBreakout(window: number, breakoutPct: number): Filter {
  return ({ bars }) => {
    if (bars.length < window + 1) return FAIL(`样本不足 ${String(window + 1)}`)
    const prior = bars.slice(-(window + 1), -1)
    const high = prior.reduce((m, b) => (b.close > m ? b.close : m), prior[0]!.close)
    const last = bars[bars.length - 1]!.close
    const ratio = (last - high) / high
    if (ratio >= breakoutPct) {
      return { passed: true, score: ratio * 100, evidence: [`突破 ${(ratio * 100).toFixed(1)}% ≥ ${String(breakoutPct * 100)}%`] }
    }
    return FAIL(`未突破平台 (${(ratio * 100).toFixed(1)}%)`)
  }
}

/** `amountLiquidity(minAvgAmountWan, days)` — average daily `amount` over the trailing window, in 万元. */
export function amountLiquidity(minAvgAmountWan: number, days: number): Filter {
  return ({ bars }) => {
    if (bars.length < days) return FAIL(`样本不足 ${String(days)}`)
    const avg = averageAmount(bars.slice(-days))
    if (avg >= minAvgAmountWan) {
      return { passed: true, score: avg / minAvgAmountWan, evidence: [`均额 ${avg.toFixed(0)} 万元`] }
    }
    return FAIL(`均额 ${avg.toFixed(0)} 万元 低于 ${String(minAvgAmountWan)}`)
  }
}

function averageVolume(bars: OHLCV[]): number {
  return bars.reduce((sum, bar) => sum + bar.volume, 0) / bars.length
}

function averageAmount(bars: OHLCV[]): number {
  return bars.reduce((sum, bar) => sum + bar.amount, 0) / bars.length
}
