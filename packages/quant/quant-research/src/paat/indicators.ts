/**
 * PAAT technical indicators, TS side: deterministic re-implementations of
 * the phase-1 indicator set (SMA, EMA, MACD, RSI, BOLL, ATR). Indicators run
 * in TypeScript rather than the kernel so replayed sessions see bit-identical
 * numbers regardless of the host's Python environment; every function is
 * pure and total over its validated inputs. Warm-up positions are `null`.
 * @module @deepseek-ai/dsh-quant-research/paat/indicators
 */

import { QuantError } from '../errors.ts'
import type { KlineBar } from '../pdat/datasource.ts'

/** One indicator output series aligned with the input; `null` during warm-up. */
export type Series = (number | null)[]

/**
 * Validate one indicator window.
 * @param name - the indicator name, for the error message.
 * @param length - the input length.
 * @param window - the requested window.
 * @throws {@link QuantError} code `DATA` when the window cannot fit the input.
 */
function validateWindow(name: string, length: number, window: number): void {
  if (!Number.isSafeInteger(window) || window < 1 || window > length) {
    throw new QuantError('DATA', `${name} 窗口必须是 1-${String(length)} 的整数，收到 ${String(window)}`)
  }
}

/**
 * Simple moving average.
 * @param values - the input series.
 * @param window - the averaging window.
 * @returns the SMA series; the first `window - 1` positions are `null`.
 */
export function sma(values: readonly number[], window: number): Series {
  validateWindow('sma', values.length, window)
  const out: Series = new Array(values.length).fill(null)
  let sum = 0
  for (const [index, value] of values.entries()) {
    sum += value
    if (index >= window) sum -= values[index - window] as number
    if (index >= window - 1) out[index] = sum / window
  }
  return out
}

/**
 * Exponential moving average, seeded with the SMA of the first window.
 * @param values - the input series.
 * @param window - the EMA window.
 * @returns the EMA series; the first `window - 1` positions are `null`.
 */
export function ema(values: readonly number[], window: number): Series {
  validateWindow('ema', values.length, window)
  const out: Series = new Array(values.length).fill(null)
  const weight = 2 / (window + 1)
  let seed = 0
  for (const [index, value] of values.entries()) {
    if (index < window) {
      seed += value
      if (index === window - 1) out[index] = seed / window
      continue
    }
    out[index] = (value - (out[index - 1] as number)) * weight + (out[index - 1] as number)
  }
  return out
}

/**
 * Moving average convergence/divergence.
 * @param values - the input series.
 * @param fast - the fast EMA window (default 12).
 * @param slow - the slow EMA window (default 26).
 * @param signalPeriod - the signal EMA window over the MACD line (default 9).
 * @returns the MACD line, signal line, and histogram, each aligned with the input.
 */
export function macd(
  values: readonly number[],
  fast: number = 12,
  slow: number = 26,
  signalPeriod: number = 9,
): { macdLine: Series; signalLine: Series; histogram: Series } {
  validateWindow('macd fast', values.length, fast)
  validateWindow('macd slow', values.length, slow)
  if (fast >= slow) {
    throw new QuantError('DATA', `macd 快线窗口（${String(fast)}）必须小于慢线窗口（${String(slow)}）`)
  }
  const fastLine = ema(values, fast)
  const slowLine = ema(values, slow)
  const macdLine: Series = values.map((_, index) => {
    const a = fastLine[index]
    const b = slowLine[index]
    return a === undefined || a === null || b === undefined || b === null ? null : a - b
  })
  // The signal EMA runs over the MACD line's defined tail only; a tail too
  // short for the signal window degrades to nulls rather than failing — the
  // MACD line itself is still valid research output.
  const defined = macdLine.filter((value): value is number => value !== null)
  const signalLine: Series = new Array(values.length).fill(null)
  if (defined.length >= signalPeriod) {
    const signalValues = ema(defined, signalPeriod)
    for (const [position, value] of signalValues.entries()) {
      if (value === null) continue
      const targetIndex = values.length - defined.length + position
      signalLine[targetIndex] = value
    }
  }
  const histogram: Series = values.map((_, index) => {
    const a = macdLine[index]
    const b = signalLine[index]
    return a === undefined || a === null || b === undefined || b === null ? null : a - b
  })
  return { macdLine, signalLine, histogram }
}

/**
 * Relative strength index with Wilder's smoothing; the first value lands at
 * index `window`. A window of pure gains reads 100, pure losses reads 0.
 * @param values - the input series.
 * @param window - the RSI window (default 14).
 * @returns the RSI series; the first `window` positions are `null`.
 */
export function rsi(values: readonly number[], window: number = 14): Series {
  if (!Number.isSafeInteger(window) || window < 1 || window > values.length - 1) {
    throw new QuantError('DATA', `rsi 窗口必须是 1-${String(values.length - 1)} 的整数，收到 ${String(window)}`)
  }
  const out: Series = new Array(values.length).fill(null)
  let avgGain = 0
  let avgLoss = 0
  for (let index = 1; index < values.length; index++) {
    const change = (values[index] as number) - (values[index - 1] as number)
    const gain = Math.max(change, 0)
    const loss = Math.max(-change, 0)
    if (index <= window) {
      // The seed averages the first `window` diffs.
      avgGain += gain / window
      avgLoss += loss / window
      if (index < window) continue
    } else {
      // Wilder smoothing after the seed.
      avgGain = (avgGain * (window - 1) + gain) / window
      avgLoss = (avgLoss * (window - 1) + loss) / window
    }
    out[index] = relativeStrength(avgGain, avgLoss)
  }
  return out
}

/**
 * One RSI reading from Wilder's average gain and loss.
 * @param avgGain - the smoothed average gain.
 * @param avgLoss - the smoothed average loss.
 * @returns the RSI value (0-100); 100 when the average loss is zero.
 */
function relativeStrength(avgGain: number, avgLoss: number): number {
  if (avgLoss === 0) return 100
  const rs = avgGain / avgLoss
  return 100 - 100 / (1 + rs)
}

/**
 * Bollinger bands: the middle SMA plus/minus `mult` sample standard
 * deviations.
 * @param values - the input series.
 * @param window - the middle band window (default 20).
 * @param mult - the standard-deviation multiplier (default 2).
 * @returns the middle, upper, and lower bands, each aligned with the input.
 */
export function boll(
  values: readonly number[],
  window: number = 20,
  mult: number = 2,
): { middle: Series; upper: Series; lower: Series } {
  const middle = sma(values, window)
  const upper: Series = new Array(values.length).fill(null)
  const lower: Series = new Array(values.length).fill(null)
  for (let index = window - 1; index < values.length; index++) {
    const slice = values.slice(index - window + 1, index + 1)
    const mean = middle[index] as number
    const variance = slice.reduce((sum, value) => sum + (value - mean) ** 2, 0) / window
    const deviation = Math.sqrt(variance)
    upper[index] = mean + mult * deviation
    lower[index] = mean - mult * deviation
  }
  return { middle, upper, lower }
}

/**
 * Average true range with Wilder's smoothing over daily bars; the first
 * value lands at index `window - 1`.
 * @param bars - the input bars, oldest first.
 * @param window - the ATR window (default 14).
 * @returns the ATR series; positions before `window - 1` are `null`.
 */
export function atr(bars: readonly KlineBar[], window: number = 14): Series {
  validateWindow('atr', bars.length, window)
  const out: Series = new Array(bars.length).fill(null)
  let wilder = 0
  for (const [index, bar] of bars.entries()) {
    const trueRange = index === 0
      ? bar.high - bar.low
      : Math.max(
        bar.high - bar.low,
        Math.abs(bar.high - (bars[index - 1] as KlineBar).close),
        Math.abs(bar.low - (bars[index - 1] as KlineBar).close),
      )
    if (index < window) {
      wilder += trueRange
      if (index === window - 1) {
        wilder /= window
        out[index] = wilder
      }
      continue
    }
    wilder = (wilder * (window - 1) + trueRange) / window
    out[index] = wilder
  }
  return out
}
