/**
 * PDAT data access, TS side: route one kline request through the kernel,
 * validate the wire shape at the process boundary, and guard the data source
 * with a consecutive-failure circuit breaker. The kernel owns sources
 * (`synthetic`, `akshare`) and its on-disk cache; this layer owns symbol and
 * bar-count validation plus the breaker state machine.
 * @module @deepseek-ai/dsh-quant-research/pdat/datasource
 */

import { z } from 'zod'
import { BARS_HARD_LIMIT } from '../compliance.ts'
import { QuantError, isQuantError } from '../errors.ts'
import type { QuantDataSource } from '../config.ts'
import type { QuantKernelClient } from '../kernel-client/client.ts'

/** One normalized daily bar. */
export interface KlineBar {
  /** Trading date, `YYYY-MM-DD`. */
  readonly date: string
  /** Open price. */
  readonly open: number
  /** High price. */
  readonly high: number
  /** Low price. */
  readonly low: number
  /** Close price. */
  readonly close: number
  /** Traded volume. */
  readonly volume: number
}

/** Wire schema for one bar (the kernel/process boundary is a validated edge). */
export const klineBarSchema = z.object({
  date: z.string().min(1),
  open: z.number(),
  high: z.number(),
  low: z.number(),
  close: z.number(),
  volume: z.number(),
})

/** Wire schema for one kline series. */
export const klineSeriesSchema = z.array(klineBarSchema).min(1)

/** Smallest bar count one request may ask for. */
export const BARS_MIN = 5

/** Symbol charset: alphanumeric, dot, slash, and dash (A-share, US, and CCXT-style pairs). */
const SYMBOL_PATTERN = /^[A-Za-z0-9./-]{1,24}$/

/**
 * Consecutive-failure circuit breaker for one data source. Tripping needs
 * `threshold` consecutive `NETWORK`/`DATA` failures; any success resets the
 * count. A reset is manual by design (reload the plugin) until the phase-4
 * reset UX lands.
 */
export class DataSourceBreaker {
  private consecutiveFailures = 0
  private tripped = false

  /**
   * @param threshold - consecutive failures that trip the breaker.
   */
  constructor(private readonly threshold: number) {}

  /**
   * Whether the breaker has tripped.
   * @returns true when further requests fail fast.
   */
  get isTripped(): boolean {
    return this.tripped
  }

  /**
   * Fail fast when the breaker is open.
   * @throws {@link QuantError} code `NETWORK` with the manual-reset guidance.
   */
  check(): void {
    if (this.tripped) {
      throw new QuantError(
        'NETWORK',
        `数据源已熔断：连续 ${String(this.threshold)} 次获取失败，已暂停调用；请检查数据源配置后重新加载插件重置`,
      )
    }
  }

  /** Record one successful fetch; the consecutive-failure count resets. */
  success(): void {
    this.consecutiveFailures = 0
  }

  /** Record one failed fetch; the breaker trips at the threshold. */
  failure(): void {
    this.consecutiveFailures += 1
    if (this.consecutiveFailures >= this.threshold) this.tripped = true
  }
}

/**
 * Validate one symbol argument.
 * @param symbol - the caller-provided symbol.
 * @returns the validated symbol.
 * @throws {@link QuantError} code `DATA` on an empty or malformed symbol.
 */
export function validateSymbol(symbol: string): string {
  if (!SYMBOL_PATTERN.test(symbol)) {
    throw new QuantError('DATA', `标的代码格式不正确：「${symbol}」仅允许字母、数字与 . / -，长度 1-24`)
  }
  return symbol
}

/**
 * Validate one bar-count argument.
 * @param bars - the caller-provided bar count.
 * @returns the validated bar count.
 * @throws {@link QuantError} code `DATA` outside the inclusive range.
 */
export function validateBars(bars: number): number {
  if (!Number.isSafeInteger(bars) || bars < BARS_MIN || bars > BARS_HARD_LIMIT) {
    throw new QuantError('DATA', `K线根数必须是 ${String(BARS_MIN)}-${String(BARS_HARD_LIMIT)} 的整数，收到 ${String(bars)}`)
  }
  return bars
}

/** Parameters for one kline fetch. */
export interface FetchKlineOptions {
  /** The configured data source. */
  readonly source: QuantDataSource
  /** The symbol to fetch. */
  readonly symbol: string
  /** Bar count. */
  readonly bars: number
  /** Kernel-side retries for flaky sources. */
  readonly retries: number
  /** The kernel's cache directory (used by the `akshare` source). */
  readonly cacheDir: string
  /** The caller's cancellation signal. */
  readonly signal?: AbortSignal
}

/**
 * Fetch one kline series through the kernel. `NETWORK` and `DATA` failures
 * count against the breaker; cancellation does not.
 * @param kernel - the kernel client.
 * @param breaker - the caller's breaker instance.
 * @param options - source, symbol, bars, retries, cache dir, and signal.
 * @returns the validated kline series, oldest first.
 * @throws {@link QuantError} on validation, breaker, kernel, or wire-shape failure.
 */
export async function fetchKline(
  kernel: QuantKernelClient,
  breaker: DataSourceBreaker,
  options: FetchKlineOptions,
): Promise<KlineBar[]> {
  validateSymbol(options.symbol)
  validateBars(options.bars)
  breaker.check()
  try {
    const result = await kernel.request('get_kline', {
      source: options.source,
      symbol: options.symbol,
      period: 'daily',
      bars: options.bars,
      max_retries: options.retries,
      cache_dir: options.cacheDir,
    }, options.signal)
    const parsed = klineSeriesSchema.safeParse(result)
    if (!parsed.success) {
      throw new QuantError('DATA', '数据源返回了不符合规格的K线数据', { cause: parsed.error })
    }
    breaker.success()
    return parsed.data
  } catch (error: unknown) {
    if (isQuantError(error) && (error.code === 'NETWORK' || error.code === 'DATA')) {
      breaker.failure()
    }
    throw error
  }
}
