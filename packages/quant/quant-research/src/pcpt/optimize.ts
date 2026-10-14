/**
 * PCPT parameter optimization, TS side: grid enumeration, validation, the
 * kernel round trip, ranking, and the markdown summary. The whole grid runs
 * as one `backtest_grid` kernel request, so one short-lived Python process
 * simulates every combination through the SAME audited `run_backtest`
 * engine; the TypeScript side stays deterministic and replayable.
 * @module @deepseek-ai/dsh-quant-research/pcpt/optimize
 */

import { z } from 'zod'
import {
  BARS_HARD_LIMIT, DEFAULT_GRID_SPEC, FAST_WINDOW_LIMITS, GRID_COMBO_HARD_LIMIT, SLOW_WINDOW_LIMITS,
} from '../compliance.ts'
import type { GridAxisSpec } from '../compliance.ts'
import { QuantError } from '../errors.ts'
import type { QuantKernelClient } from '../kernel-client/client.ts'
import type { KlineBar } from '../pdat/datasource.ts'
import { metricsSchema } from './backtest.ts'
import type { BacktestMetrics } from './backtest.ts'

export { DEFAULT_GRID_SPEC }

/** The (fast, slow) search grid. */
export interface GridSpec {
  /** The fast-window axis. */
  readonly fast: GridAxisSpec
  /** The slow-window axis; its whole range must sit above the fast range. */
  readonly slow: GridAxisSpec
}

/** Metrics a ranking can order by. */
export type RankMetric = 'total_return' | 'sharpe' | 'max_drawdown'

/** The closed ranking-metric set. */
export const RANK_METRICS: readonly RankMetric[] = ['total_return', 'sharpe', 'max_drawdown']

/** Default ranking metric: risk-adjusted return. */
export const DEFAULT_RANK_METRIC: RankMetric = 'sharpe'

/** Bounds plus the default for the report's top-N cut. */
export const TOP_N_LIMITS = { min: 1, max: 50, default: 10 } as const

/** One combination's result from the kernel: metrics only, no curves. */
export interface GridComboResult {
  /** Fast SMA window. */
  readonly fast: number
  /** Slow SMA window. */
  readonly slow: number
  /** Ending equity of the run. */
  readonly final_equity: number
  /** The headline metrics. */
  readonly metrics: BacktestMetrics
}

const gridResponseSchema = z.object({
  symbol: z.string().min(1),
  count: z.number().int(),
  results: z.array(z.object({
    fast: z.number().int(),
    slow: z.number().int(),
    final_equity: z.number(),
    metrics: metricsSchema,
  })).min(1),
})

/**
 * Count one axis's steps without materializing them.
 * @param axis - the axis to count.
 * @returns how many windows the axis visits.
 */
export function axisLength(axis: GridAxisSpec): number {
  return Math.floor((axis.max - axis.min) / axis.step) + 1
}

/**
 * Enumerate every (fast, slow) combination of the grid, fast-major.
 * @param spec - the search grid.
 * @returns the combinations in deterministic order.
 */
export function enumerateGrid(spec: GridSpec): { fast: number; slow: number }[] {
  const combos: { fast: number; slow: number }[] = []
  for (let fast = spec.fast.min; fast <= spec.fast.max; fast += spec.fast.step) {
    for (let slow = spec.slow.min; slow <= spec.slow.max; slow += spec.slow.step) {
      combos.push({ fast, slow })
    }
  }
  return combos
}

/**
 * Validate a grid spec against the same hard bounds the single-run backtest
 * enforces, plus the grid's own invariants: integer axes, `min ≤ max`, the
 * whole fast range strictly below the whole slow range, the bar count
 * covering the widest slow window, and the combination cap.
 * @param bars - the bar count that will back every run.
 * @param spec - the search grid.
 * @throws {@link QuantError} code `DATA` on any invalid axis or combination.
 */
export function validateGridSpec(bars: number, spec: GridSpec): void {
  for (const [name, axis] of [['快线', spec.fast], ['慢线', spec.slow]] as const) {
    const bounds = name === '快线' ? FAST_WINDOW_LIMITS : SLOW_WINDOW_LIMITS
    for (const [field, value] of [['min', axis.min], ['max', axis.max], ['step', axis.step]] as const) {
      if (!Number.isSafeInteger(value)) {
        throw new QuantError('DATA', `${name}窗口的 ${field} 必须是整数，收到 ${String(value)}`)
      }
    }
    if (axis.step < 1) {
      throw new QuantError('DATA', `${name}窗口的步长必须至少为 1，收到 ${String(axis.step)}`)
    }
    if (axis.min < bounds.min || axis.max > bounds.max) {
      throw new QuantError(
        'DATA',
        `${name}窗口范围必须落在 ${String(bounds.min)}-${String(bounds.max)}，收到 ${String(axis.min)}-${String(axis.max)}`,
      )
    }
    if (axis.min > axis.max) {
      throw new QuantError('DATA', `${name}窗口的 min（${String(axis.min)}）不能大于 max（${String(axis.max)}）`)
    }
  }
  if (spec.fast.max >= spec.slow.min) {
    throw new QuantError(
      'DATA',
      `快线整段范围（≤ ${String(spec.fast.max)}）必须小于慢线整段范围（≥ ${String(spec.slow.min)}）`,
    )
  }
  const combos = axisLength(spec.fast) * axisLength(spec.slow)
  if (combos > GRID_COMBO_HARD_LIMIT) {
    throw new QuantError(
      'DATA',
      `参数组合数 ${String(combos)} 超过上限 ${String(GRID_COMBO_HARD_LIMIT)}，请加大步长或收窄范围`,
    )
  }
  if (!Number.isSafeInteger(bars) || bars < spec.slow.max + 1 || bars > BARS_HARD_LIMIT) {
    throw new QuantError(
      'DATA',
      `K线根数必须至少覆盖最宽慢线窗口（≥ ${String(spec.slow.max + 1)}）且不超过 ${String(BARS_HARD_LIMIT)}，收到 ${String(bars)}`,
    )
  }
}

/**
 * Run the whole grid through one kernel request. The kernel simulates every
 * combination with the audited single-run engine and returns metrics only.
 * @param kernel - the kernel client.
 * @param symbol - the analyzed symbol (echoed into the response).
 * @param bars - the fetched daily bars, oldest first.
 * @param spec - the pre-validated search grid.
 * @param initialCash - starting cash shared by every run.
 * @param feeRate - per-trade fee rate shared by every run.
 * @param signal - the caller's cancellation signal.
 * @returns the per-combination results, in grid order.
 * @throws {@link QuantError} on kernel or wire-shape failure.
 */
export async function runBacktestGrid(
  kernel: QuantKernelClient,
  symbol: string,
  bars: readonly KlineBar[],
  spec: GridSpec,
  initialCash: number,
  feeRate: number,
  signal?: AbortSignal,
): Promise<GridComboResult[]> {
  const result = await kernel.request('backtest_grid', {
    symbol,
    bars: [...bars],
    combos: enumerateGrid(spec),
    initial_cash: initialCash,
    fee_rate: feeRate,
  }, signal)
  const parsed = gridResponseSchema.safeParse(result)
  if (!parsed.success) {
    throw new QuantError('DATA', '寻优内核返回了不符合规格的结果', { cause: parsed.error })
  }
  return parsed.data.results
}

/**
 * Order the grid results by one metric and keep the top N. `total_return`
 * and `sharpe` rank descending; `max_drawdown` ranks ascending (smaller
 * drawdown is better). Ties keep grid order, so the ranking is deterministic.
 * @param results - the per-combination results.
 * @param metric - the ranking metric.
 * @param topN - how many leaders to keep.
 * @returns the ranked leaders, best first.
 */
export function rankGridResults(
  results: readonly GridComboResult[],
  metric: RankMetric,
  topN: number,
): GridComboResult[] {
  const factor = metric === 'max_drawdown' ? 1 : -1
  return [...results]
    .sort((a, b) => factor * (a.metrics[metric] - b.metrics[metric]))
    .slice(0, topN)
}

/**
 * Format the optimization summary as a markdown research document, including
 * the overfitting warning a grid search owes its reader.
 * @param symbol - the analyzed symbol.
 * @param spec - the search grid that ran.
 * @param ranked - the ranked leaders (best first).
 * @param metric - the ranking metric.
 * @param comboCount - the total number of combinations that ran.
 * @returns the markdown string.
 */
export function formatOptimizationSummary(
  symbol: string,
  spec: GridSpec,
  ranked: readonly GridComboResult[],
  metric: RankMetric,
  comboCount: number,
): string {
  const pct = (v: number): string => `${(v * 100).toFixed(2)}%`
  const metricName: Record<RankMetric, string> = {
    total_return: '总收益',
    sharpe: '夏普比率',
    max_drawdown: '最大回撤（升序）',
  }
  const rows = ranked.map((entry, index) =>
    `| ${String(index + 1)} | ${String(entry.fast)} | ${String(entry.slow)} | ${pct(entry.metrics.total_return)}`
    + ` | ${pct(entry.metrics.annual_return)} | ${pct(entry.metrics.max_drawdown)} | ${entry.metrics.sharpe.toFixed(4)}`
    + ` | ${pct(entry.metrics.win_rate)} | ${String(entry.metrics.trade_count)} |`,
  ).join('\n')
  return [
    `# 参数寻优报告：${symbol}`,
    '',
    '> 仅供研究参考，不构成投资建议。网格最优参数来自同一段历史样本，存在过拟合风险，样本外未必有效。',
    '',
    '## 搜索网格',
    `- 快线：${String(spec.fast.min)}-${String(spec.fast.max)} 步长 ${String(spec.fast.step)}（${String(axisLength(spec.fast))} 个）`,
    `- 慢线：${String(spec.slow.min)}-${String(spec.slow.max)} 步长 ${String(spec.slow.step)}（${String(axisLength(spec.slow))} 个）`,
    `- 组合数：${String(comboCount)}`,
    `- 排名指标：${metric}（${metricName[metric]}）`,
    '',
    '## 最优参数',
    '| 排名 | 快线 | 慢线 | 总收益 | 年化 | 最大回撤 | 夏普 | 胜率 | 交易笔数 |',
    '|---|---|---|---|---|---|---|---|---|',
    rows.length > 0 ? rows : '（无结果）',
    '',
  ].join('\n')
}
