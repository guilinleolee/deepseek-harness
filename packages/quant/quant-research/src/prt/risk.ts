/**
 * PRT risk metrics, TypeScript side: historical-simulation VaR/CVaR, annual
 * volatility, drawdown from a price path, and position-concentration checks.
 * Like the indicators, the risk math is deterministic TypeScript so replays
 * see identical numbers; the stress scenarios are pure price-path transforms
 * over the caller's bars, which lets the phase-1 kernel simulator serve as
 * the stressed engine without any kernel change.
 * @module @deepseek-ai/dsh-quant-research/prt/risk
 */

import { CONFIDENCE_LIMITS, SHOCK_LIMITS } from '../compliance.ts'
import { QuantError } from '../errors.ts'
import type { KlineBar } from '../pdat/datasource.ts'

export { CONFIDENCE_LIMITS, SHOCK_LIMITS }

/** Trading days per year, the annualization constant for volatilities. */
export const TRADING_DAYS_PER_YEAR = 252

/**
 * Daily simple returns of one close series; one fewer return than prices.
 * @param closes - the close prices, oldest first.
 * @returns the daily returns.
 * @throws {@link QuantError} code `DATA` when fewer than two prices are given.
 */
export function dailyReturns(closes: readonly number[]): number[] {
  if (closes.length < 2) {
    throw new QuantError('DATA', '风险指标至少需要 2 个收盘价')
  }
  const out: number[] = []
  for (let index = 1; index < closes.length; index++) {
    const previous = closes[index - 1] as number
    if (!(previous > 0)) {
      throw new QuantError('DATA', `第 ${String(index - 1)} 个收盘价必须为正数，收到 ${String(previous)}`)
    }
    out.push((closes[index] as number) / previous - 1)
  }
  return out
}

/**
 * The linearly interpolated empirical quantile of one sample.
 * @param sample - the values (not mutated).
 * @param q - the quantile in `[0, 1]`.
 * @returns the interpolated quantile value.
 */
export function empiricalQuantile(sample: readonly number[], q: number): number {
  const sorted = [...sample].sort((left, right) => left - right)
  const position = q * (sorted.length - 1)
  const lower = Math.floor(position)
  const upper = Math.ceil(position)
  if (lower === upper) return sorted[lower] as number
  const weight = position - lower
  return (sorted[lower] as number) * (1 - weight) + (sorted[upper] as number) * weight
}

/**
 * Historical-simulation VaR at one confidence level: the loss fraction the
 * portfolio would exceed with probability `1 - confidence`. Reported as a
 * positive loss ratio; `0` when the empirical tail holds no loss.
 * @param returns - the daily returns.
 * @param confidence - the confidence level in `[0.8, 0.99]`.
 * @returns the VaR as a positive loss fraction.
 */
export function historicalVar(returns: readonly number[], confidence: number): number {
  if (!Number.isFinite(confidence) || confidence < CONFIDENCE_LIMITS.min || confidence > CONFIDENCE_LIMITS.max) {
    throw new QuantError(
      'DATA',
      `置信度必须是 ${String(CONFIDENCE_LIMITS.min)}-${String(CONFIDENCE_LIMITS.max)} 之间的数值，收到 ${String(confidence)}`,
    )
  }
  if (returns.length < 2) {
    throw new QuantError('DATA', 'VaR 至少需要 2 个收益率样本')
  }
  const tailQuantile = empiricalQuantile(returns, 1 - confidence)
  return Math.max(0, -tailQuantile)
}

/**
 * Historical-simulation CVaR (expected shortfall): the mean loss beyond the
 * VaR threshold, reported with the same positive-loss convention.
 * @param returns - the daily returns.
 * @param confidence - the confidence level in `[0.8, 0.99]`.
 * @returns the CVaR as a positive loss fraction.
 */
export function historicalCVar(returns: readonly number[], confidence: number): number {
  const var_ = historicalVar(returns, confidence)
  const tail = returns.filter(value => -value >= var_)
  if (tail.length === 0) return 0
  return tail.reduce((sum, value) => sum + -value, 0) / tail.length
}

/**
 * Annualized volatility: the sample standard deviation of daily returns
 * scaled by the square root of the trading year.
 * @param returns - the daily returns.
 * @returns the annualized volatility as a fraction.
 */
export function annualVolatility(returns: readonly number[]): number {
  if (returns.length < 2) {
    throw new QuantError('DATA', '波动率至少需要 2 个收益率样本')
  }
  const mean = returns.reduce((sum, value) => sum + value, 0) / returns.length
  const variance = returns.reduce((sum, value) => sum + (value - mean) ** 2, 0) / (returns.length - 1)
  return Math.sqrt(variance) * Math.sqrt(TRADING_DAYS_PER_YEAR)
}

/**
 * Maximum drawdown of one price path: the largest peak-to-trough decline,
 * as a positive fraction.
 * @param prices - the price path, oldest first.
 * @returns the maximum drawdown in `[0, 1)`.
 */
export function maxDrawdown(prices: readonly number[]): number {
  let peak = prices[0] as number
  let drawdown = 0
  for (const price of prices) {
    peak = Math.max(peak, price)
    if (peak > 0) drawdown = Math.max(drawdown, (peak - price) / peak)
  }
  return drawdown
}

/**
 * One position weight against the portfolio caps.
 * @param weights - symbol → weight fraction; the weights should sum to ≤ 1.
 * @param maxPerPosition - the hard cap for any single position.
 * @param maxTotal - the hard cap for the invested total.
 * @returns the breaches: per-symbol overweights and the total overage.
 */
export function concentrationBreaches(
  weights: Readonly<Record<string, number>>,
  maxPerPosition: number,
  maxTotal: number,
): { readonly symbols: readonly string[]; readonly total: number | null } {
  const symbols = Object.entries(weights)
    .filter(([, weight]) => weight > maxPerPosition)
    .map(([symbol]) => symbol)
    .sort((left, right) => left.localeCompare(right))
  const total = Object.values(weights).reduce((sum, weight) => sum + weight, 0)
  return { symbols, total: total > maxTotal ? total : null }
}

/** The supported stress scenarios. */
export type StressScenario = 'crash' | 'liquidity'

/** Parameters of one stress transform. */
export interface StressParams {
  /** The scenario to apply. */
  readonly scenario: StressScenario
  /** Total shock magnitude as a fraction (crash gap / liquidity slide). */
  readonly shock: number
  /** Fraction of the window the stress occupies (default the final third). */
  readonly segment?: number
}

/** Default fraction of the window the stress occupies. */
export const DEFAULT_STRESS_SEGMENT = 1 / 3

/**
 * Validate one stress parameter set.
 * @param params - the scenario, shock, and optional segment.
 * @throws {@link QuantError} code `DATA` on any invalid value.
 */
export function validateStressParams(params: StressParams): void {
  if (params.scenario !== 'crash' && params.scenario !== 'liquidity') {
    throw new QuantError('DATA', `压力场景只支持 crash / liquidity，收到 ${String(params.scenario)}`)
  }
  if (!Number.isFinite(params.shock) || params.shock < SHOCK_LIMITS.min || params.shock > SHOCK_LIMITS.max) {
    throw new QuantError(
      'DATA',
      `冲击幅度必须是 ${String(SHOCK_LIMITS.min)}-${String(SHOCK_LIMITS.max)} 之间的数值，收到 ${String(params.shock)}`,
    )
  }
  if (params.segment !== undefined
    && (!Number.isFinite(params.segment) || params.segment <= 0 || params.segment > 1)) {
    throw new QuantError('DATA', `压力段占比必须是 0-1 之间的数值，收到 ${String(params.segment)}`)
  }
}

/**
 * Transform one kline series under a stress scenario. Pure: the input bars
 * are never mutated.
 *
 * - `crash` (black swan): an overnight gap — every bar from the segment
 *   start trades at `(1 - shock)` of its previous price.
 * - `liquidity` (drying liquidity): a cascading slide — the segment glides
 *   from the last pre-segment close down `shock` in equal daily steps, while
 *   volume dries up by the same fraction. The phase-1 simulator fills at
 *   next open and ignores depth, so the price path is the binding
 *   constraint; the volume hair-cut is reported in the data for later
 *   depth-sensitive fills.
 * @param bars - the validated bars, oldest first.
 * @param params - the scenario, shock, and optional segment.
 * @returns the stressed copy of the series.
 */
export function shockBars(bars: readonly KlineBar[], params: StressParams): KlineBar[] {
  validateStressParams(params)
  const segment = params.segment ?? DEFAULT_STRESS_SEGMENT
  const start = Math.floor(bars.length * (1 - segment))
  const segmentLength = Math.max(1, bars.length - start)
  // The liquidity slide references the last pre-segment close (or the first
  // bar when the segment covers the whole window).
  const reference = (bars[start - 1] ?? bars[0])?.close ?? 1
  return bars.map((bar, index) => {
    if (index < start) return bar
    if (params.scenario === 'crash') {
      const factor = 1 - params.shock
      return {
        ...bar,
        open: bar.open * factor,
        high: bar.high * factor,
        low: bar.low * factor,
        close: bar.close * factor,
      }
    }
    const step = index - start
    const factor = 1 - params.shock * ((step + 1) / segmentLength)
    return {
      ...bar,
      open: reference * factor,
      high: reference * factor,
      low: reference * factor,
      close: reference * factor,
      volume: bar.volume * (1 - Math.min(params.shock, 0.9)),
    }
  })
}
