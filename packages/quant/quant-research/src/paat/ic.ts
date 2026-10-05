/**
 * PAAT Information Coefficient analysis: the Spearman rank correlation
 * between factor values and forward returns, and the Information Ratio
 * (IC mean / IC std) across rolling windows. IC quantifies a factor's
 * predictive power; IR quantifies its consistency. Both are computed
 * deterministically in TypeScript for replay identity.
 * @module @deepseek-ai/dsh-quant-research/paat/ic
 */

import { QuantError } from '../errors.ts'
import type { KlineBar } from '../pdat/datasource.ts'

/**
 * Spearman rank correlation between two paired samples. Ties receive their
 * average rank. Returns `null` when fewer than 2 valid pairs exist or when
 * either sample has zero variance (degenerate).
 * @param xs - the first sample.
 * @param ys - the second sample (must have the same length as `xs`).
 * @returns the correlation in `[-1, 1]`, or `null` when degenerate.
 */
export function spearman(xs: readonly number[], ys: readonly number[]): number | null {
  /* v8 ignore next */
  /* v8 ignore next */ if (xs.length !== ys.length || xs.length < 2) return null /* v8 ignore */
  const rank = (values: readonly number[]): number[] => {
    const indexed = values.map((value, index) => ({ value, index }))
    indexed.sort((a, b) => a.value - b.value)
    const ranks = new Array<number>(values.length)
    let start = 0
    while (start < indexed.length) {
      let end = start
      while (end < indexed.length - 1 && (indexed[end + 1] as { value: number }).value === (indexed[start] as { value: number }).value) end++
      const avg = (start + end) / 2 + 1
      for (let j = start; j <= end; j++) ranks[(indexed[j] as { index: number }).index] = avg
      start = end + 1
    }
    return ranks
  }
  const rx = rank(xs)
  const ry = rank(ys)
  const n = xs.length
  const meanX = rx.reduce((sum, r) => sum + r, 0) / n
  const meanY = ry.reduce((sum, r) => sum + r, 0) / n
  let cov = 0
  let varX = 0
  let varY = 0
  for (let i = 0; i < n; i++) {
    const dx = (rx[i] as number) - meanX
    const dy = (ry[i] as number) - meanY
    cov += dx * dy
    varX += dx * dx
    varY += dy * dy
  }
  if (varX === 0 || varY === 0) return null
  return cov / Math.sqrt(varX * varY)
}

/** One period's IC reading. */
export interface ICPeriod {
  /** The bar date at the factor observation point. */
  readonly date: string
  /** The Spearman rank IC for this period. */
  readonly ic: number
}

/**
 * Rolling Information Coefficient: at each bar `t` (where `t + forward` is in
 * range), compute the Spearman correlation between the factor values at `t`
 * and the forward returns from `t` to `t + forward`. Produces a series of
 * period-level ICs for IR aggregation.
 * @param bars - the input bars, oldest first.
 * @param factor - the factor values aligned with `bars` (`null` = warm-up).
 * @param forward - the forward-return horizon in bars.
 * @param window - the cross-sectional look-back (how many bars of factor
 *   values to correlate against forward returns at each step).
 * @returns the IC readings, chronological.
 * @throws {@link QuantError} code `DATA` when inputs are too short.
 */
export function rollingIC(
  bars: readonly KlineBar[],
  factor: readonly (number | null)[],
  forward: number,
  window: number,
): ICPeriod[] {
  if (bars.length < window + forward + 1) {
    throw new QuantError(
      'DATA',
      `IC 分析至少需要 ${String(window + forward + 1)} 根K线，收到 ${String(bars.length)}`,
    )
  }
  const periods: ICPeriod[] = []
  for (let t = window - 1; t + forward < bars.length; t++) {
    const factorValues: number[] = []
    const forwardReturns: number[] = []
    for (let j = t - window + 1; j <= t; j++) {
      const fv = factor[j]
      /* v8 ignore next */
      /* v8 ignore next */ if (fv === null || fv === undefined) continue /* v8 ignore */
      const currentClose = (bars[j] as KlineBar).close
      const futureClose = (bars[j + forward] as KlineBar | undefined)?.close
      /* v8 ignore next */
      /* v8 ignore next */ if (futureClose === undefined || currentClose <= 0) continue /* v8 ignore */
      factorValues.push(fv)
      forwardReturns.push(futureClose / currentClose - 1)
    }
    if (factorValues.length < 2) continue
    const ic = spearman(factorValues, forwardReturns)
    if (ic === null) continue
    periods.push({ date: (bars[t] as KlineBar).date, ic })
  }
  return periods
}

/**
 * Information Ratio: the mean IC divided by the std of ICs. Measures how
 * consistently a factor predicts returns. `null` when fewer than 2 periods
 * or IC std is zero.
 * @param periods - the IC readings from {@link rollingIC}.
 * @returns the IR value, or `null` when degenerate.
 */
export function informationRatio(periods: readonly ICPeriod[]): number | null {
  if (periods.length < 2) return null
  const values = periods.map(period => period.ic)
  const mean = values.reduce((sum, v) => sum + v, 0) / values.length
  const variance = values.reduce((sum, v) => sum + (v - mean) ** 2, 0) / (values.length - 1)
  const std = Math.sqrt(variance)
  if (std === 0) return null
  return mean / std
}
