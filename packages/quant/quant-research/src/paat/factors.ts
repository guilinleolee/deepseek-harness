/**
 * PAAT quant factors, TypeScript side: deterministic cross-sectional factor
 * computations over daily kline series. Like the indicators, factors run in
 * TypeScript so replays see bit-identical values regardless of the host's
 * Python environment. Each factor produces one aligned series with `null`
 * during warm-up.
 *
 * Phase-2 factor set: momentum, volatility, volume_ratio, price_position.
 * The factor-library expansion (quality, valuation, alternative data) is a
 * later-phase item; the tool contract accepts a `factor` name so the wire
 * interface stays stable as the set grows.
 * @module @deepseek-ai/dsh-quant-research/paat/factors
 */

import { QuantError } from '../errors.ts'
import type { KlineBar } from '../pdat/datasource.ts'

/** One factor output series aligned with the input; `null` during warm-up. */
export type FactorSeries = (number | null)[]

/** The phase-2 factor names accepted by `quant_compute_factor`. */
export type FactorName = 'momentum' | 'volatility' | 'volume_ratio' | 'price_position'

/** The closed factor set. */
export const FACTOR_NAMES: readonly FactorName[] = ['momentum', 'volatility', 'volume_ratio', 'price_position']

/** Default look-back window per factor (bars). */
export const DEFAULT_FACTOR_WINDOWS: Readonly<Record<FactorName, number>> = Object.freeze({
  momentum: 20,
  volatility: 20,
  volume_ratio: 20,
  price_position: 20,
})

/**
 * Validate one factor window.
 * @param name - the factor name, for the error message.
 * @param length - the input series length.
 * @param window - the requested look-back window.
 * @throws {@link QuantError} code `DATA` when the window cannot fit.
 */
function validateWindow(name: string, length: number, window: number): void {
  if (!Number.isSafeInteger(window) || window < 2 || window > length) {
    throw new QuantError('DATA', `${name} 窗口必须是 2-${String(length)} 的整数，收到 ${String(window)}`)
  }
}

/**
 * Momentum: the N-bar rate of change `(close_t / close_{t-N} - 1)`.
 * @param bars - the input bars, oldest first.
 * @param window - the look-back period (default 20).
 * @returns the momentum series; the first `window` positions are `null`.
 */
export function momentum(bars: readonly KlineBar[], window: number = 20): FactorSeries {
  validateWindow('momentum', bars.length, window)
  const out: FactorSeries = new Array(bars.length).fill(null)
  for (let index = window; index < bars.length; index++) {
    const past = (bars[index - window] as KlineBar).close
    /* v8 ignore next */
    if (past <= 0) { out[index] = null; continue } /* v8 ignore */
    out[index] = (bars[index] as KlineBar).close / past - 1
  }
  return out
}

/**
 * Rolling volatility: the sample standard deviation of daily returns over
 * each look-back window.
 * @param bars - the input bars, oldest first.
 * @param window - the look-back period (default 20).
 * @returns the volatility series; the first `window` positions are `null`.
 */
export function volatility(bars: readonly KlineBar[], window: number = 20): FactorSeries {
  validateWindow('volatility', bars.length, window)
  const out: FactorSeries = new Array(bars.length).fill(null)
  for (let index = window; index < bars.length; index++) {
    const returns: number[] = []
    for (let j = index - window + 1; j <= index; j++) {
      const prev = (bars[j - 1] as KlineBar).close
      /* v8 ignore next */
      if (prev <= 0) { returns.push(0); continue } /* v8 ignore */
      returns.push((bars[j] as KlineBar).close / prev - 1)
    }
    const mean = returns.reduce((sum, r) => sum + r, 0) / window
    const variance = returns.reduce((sum, r) => sum + (r - mean) ** 2, 0) / (window - 1)
    out[index] = Math.sqrt(variance)
  }
  return out
}

/**
 * Volume ratio: current volume divided by the rolling mean volume.
 * @param bars - the input bars, oldest first.
 * @param window - the look-back period (default 20).
 * @returns the volume-ratio series; the first `window` positions are `null`.
 */
export function volumeRatio(bars: readonly KlineBar[], window: number = 20): FactorSeries {
  validateWindow('volume_ratio', bars.length, window)
  const out: FactorSeries = new Array(bars.length).fill(null)
  for (let index = window; index < bars.length; index++) {
    let sum = 0
    for (let j = index - window + 1; j <= index; j++) {
      sum += (bars[j] as KlineBar).volume
    }
    const meanVolume = sum / window
    /* v8 ignore next */
    if (meanVolume <= 0) { out[index] = null; continue } /* v8 ignore */
    out[index] = (bars[index] as KlineBar).volume / meanVolume
  }
  return out
}

/**
 * Price position: where the current close sits in the N-bar high–low range,
 * normalised to `[0, 1]` (0 = at the low, 1 = at the high).
 * @param bars - the input bars, oldest first.
 * @param window - the look-back period (default 20).
 * @returns the price-position series; the first `window - 1` positions are `null`.
 */
export function pricePosition(bars: readonly KlineBar[], window: number = 20): FactorSeries {
  validateWindow('price_position', bars.length, window)
  const out: FactorSeries = new Array(bars.length).fill(null)
  for (let index = window - 1; index < bars.length; index++) {
    let high = -Infinity
    let low = Infinity
    for (let j = index - window + 1; j <= index; j++) {
      high = Math.max(high, (bars[j] as KlineBar).high)
      low = Math.min(low, (bars[j] as KlineBar).low)
    }
    const range = high - low
    out[index] = range > 0 ? ((bars[index] as KlineBar).close - low) / range : /* v8 ignore next */ 0.5
  }
  return out
}

/**
 * Compute one named factor over the bars.
 * @param name - the factor name.
 * @param bars - the input bars, oldest first.
 * @param window - the look-back window (factor-specific default when omitted).
 * @returns the date-aligned factor values.
 * @throws {@link QuantError} code `DATA` on an unknown factor or invalid window.
 */
export function computeFactor(
  name: FactorName,
  bars: readonly KlineBar[],
  window?: number,
): FactorSeries {
  const used = window ?? DEFAULT_FACTOR_WINDOWS[name]
  switch (name) {
    case 'momentum': return momentum(bars, used)
    case 'volatility': return volatility(bars, used)
    case 'volume_ratio': return volumeRatio(bars, used)
    case 'price_position': return pricePosition(bars, used)
  }
}
