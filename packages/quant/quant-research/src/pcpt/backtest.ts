/**
 * PCPT backtesting, TS side: parameter validation and the kernel round trip.
 * The kernel receives the already-fetched bars and runs the daily SMA-cross
 * simulation (signal on close, execution at next open, all-in/all-out), so
 * the engine stays a pure function of its inputs and the same trade model
 * serves unit tests, replays, and live research calls alike.
 * @module @deepseek-ai/dsh-quant-research/pcpt/backtest
 */

import { z } from 'zod'
import { BARS_HARD_LIMIT, FEE_RATE_HARD_LIMIT, INITIAL_CASH_HARD_LIMIT } from '../compliance.ts'
import { QuantError } from '../errors.ts'
import type { QuantKernelClient } from '../kernel-client/client.ts'
import type { KlineBar } from '../pdat/datasource.ts'

/** Bounds for the fast SMA window. */
export const FAST_WINDOW_LIMITS = { min: 2, max: 120 } as const
/** Bounds for the slow SMA window. */
export const SLOW_WINDOW_LIMITS = { min: 3, max: 250 } as const

/** Parameters of one backtest run; the caller's config supplies the cash and fee defaults. */
export interface BacktestParams {
  /** Fast SMA window (bars). */
  readonly fast: number
  /** Slow SMA window (bars); must exceed `fast`. */
  readonly slow: number
  /** Starting cash. */
  readonly initialCash: number
  /** Per-trade fee rate. */
  readonly feeRate: number
}

/** One equity-curve point. */
export type EquityPoint = {
  /** Trading date, `YYYY-MM-DD`. */
  readonly date: string
  /** Account equity at the close. */
  readonly value: number
}

/** One simulated fill. */
export type BacktestTrade = {
  /** Execution date (the bar after the signal). */
  readonly date: string
  /** Fill side. */
  readonly side: 'buy' | 'sell'
  /** Fill price (the bar's open). */
  readonly price: number
  /** Shares filled. */
  readonly shares: number
}

/** Headline performance metrics of one run. */
export type BacktestMetrics = {
  /** Total return over the window (ratio). */
  readonly total_return: number
  /** Annualized return (ratio). */
  readonly annual_return: number
  /** Maximum drawdown (positive ratio). */
  readonly max_drawdown: number
  /** Daily-return Sharpe ratio, annualized, risk-free rate 0. */
  readonly sharpe: number
  /** Winning-trade ratio (0-1); 0 with no trades. */
  readonly win_rate: number
  /** Round-trip trade count. */
  readonly trade_count: number
}

/** Full report of one backtest run. */
export type BacktestReport = {
  /** The analyzed symbol. */
  readonly symbol: string
  /** Fast SMA window. */
  readonly fast: number
  /** Slow SMA window. */
  readonly slow: number
  /** Starting cash. */
  readonly initial_cash: number
  /** Ending equity. */
  readonly final_equity: number
  /** The equity curve, one point per bar. */
  readonly equity: readonly EquityPoint[]
  /** The simulated fills, chronological. */
  readonly trades: readonly BacktestTrade[]
  /** The headline metrics. */
  readonly metrics: BacktestMetrics
}

const equityPointSchema = z.object({ date: z.string().min(1), value: z.number() })
const tradeSchema = z.object({
  date: z.string().min(1),
  side: z.enum(['buy', 'sell']),
  price: z.number(),
  shares: z.number(),
})
const metricsSchema = z.object({
  total_return: z.number(),
  annual_return: z.number(),
  max_drawdown: z.number(),
  sharpe: z.number(),
  win_rate: z.number(),
  trade_count: z.number().int(),
})

const backtestReportSchema = z.object({
  symbol: z.string().min(1),
  fast: z.number().int(),
  slow: z.number().int(),
  initial_cash: z.number(),
  final_equity: z.number(),
  equity: z.array(equityPointSchema).min(1),
  trades: z.array(tradeSchema),
  metrics: metricsSchema,
})

/**
 * Validate one backtest parameter set. Bounds here mirror the compliance
 * gate's hard caps — the gate denies smuggling past them; this check gives
 * the friendly reason for ordinary mistakes.
 * @param bars - the bar count that will back the run.
 * @param params - fast/slow windows, cash, and fee rate.
 * @throws {@link QuantError} code `DATA` on any invalid parameter.
 */
export function validateBacktestParams(bars: number, params: BacktestParams): void {
  if (!Number.isSafeInteger(params.fast) || params.fast < FAST_WINDOW_LIMITS.min || params.fast > FAST_WINDOW_LIMITS.max) {
    throw new QuantError(
      'DATA',
      `快线窗口必须是 ${String(FAST_WINDOW_LIMITS.min)}-${String(FAST_WINDOW_LIMITS.max)} 的整数，收到 ${String(params.fast)}`,
    )
  }
  if (!Number.isSafeInteger(params.slow)
    || params.slow < SLOW_WINDOW_LIMITS.min
    || params.slow > SLOW_WINDOW_LIMITS.max) {
    throw new QuantError(
      'DATA',
      `慢线窗口必须是 ${String(SLOW_WINDOW_LIMITS.min)}-${String(SLOW_WINDOW_LIMITS.max)} 的整数，收到 ${String(params.slow)}`,
    )
  }
  if (params.fast >= params.slow) {
    throw new QuantError('DATA', `快线窗口（${String(params.fast)}）必须小于慢线窗口（${String(params.slow)}）`)
  }
  if (!Number.isFinite(params.initialCash) || params.initialCash <= 0 || params.initialCash > INITIAL_CASH_HARD_LIMIT) {
    throw new QuantError('DATA', `初始资金必须是 0-${String(INITIAL_CASH_HARD_LIMIT)} 的数值`)
  }
  if (!Number.isFinite(params.feeRate) || params.feeRate < 0 || params.feeRate > FEE_RATE_HARD_LIMIT) {
    throw new QuantError('DATA', `手续费率必须是 0-${String(FEE_RATE_HARD_LIMIT)} 之间的数值`)
  }
  if (!Number.isSafeInteger(bars) || bars < params.slow + 1 || bars > BARS_HARD_LIMIT) {
    throw new QuantError(
      'DATA',
      `K线根数必须至少覆盖慢线窗口（≥ ${String(params.slow + 1)}）且不超过 ${String(BARS_HARD_LIMIT)}，收到 ${String(bars)}`,
    )
  }
}

/**
 * Run one SMA-cross backtest through the kernel. The bars travel with the
 * request; the kernel stays a pure simulator.
 * @param kernel - the kernel client.
 * @param symbol - the analyzed symbol (echoed into the report).
 * @param bars - the validated daily bars, oldest first.
 * @param params - fast/slow windows, cash, and fee rate (pre-validated).
 * @param signal - the caller's cancellation signal.
 * @returns the validated backtest report.
 * @throws {@link QuantError} on kernel or wire-shape failure.
 */
export async function runBacktest(
  kernel: QuantKernelClient,
  symbol: string,
  bars: readonly KlineBar[],
  params: BacktestParams,
  signal?: AbortSignal,
): Promise<BacktestReport> {
  const result = await kernel.request('backtest', {
    symbol,
    bars: [...bars],
    fast: params.fast,
    slow: params.slow,
    initial_cash: params.initialCash,
    fee_rate: params.feeRate,
  }, signal)
  const parsed = backtestReportSchema.safeParse(result)
  if (!parsed.success) {
    throw new QuantError('DATA', '回测内核返回了不符合规格的报告', { cause: parsed.error })
  }
  return parsed.data
}
