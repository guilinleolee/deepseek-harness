/**
 * PCPT walk-forward / out-of-sample validation, TS side: bar splitting,
 * parameter validation on both legs, and the markdown summary. The whole
 * pipeline reuses the audited `backtest_grid` op on the train leg and the
 * audited `backtest` op on the test leg — no new kernel op — so the
 * engine that searches for the best parameters is the engine that gets
 * tested out-of-sample.
 * @module @deepseek-ai/dsh-quant-research/pcpt/walk-forward
 */

import { QuantError } from '../errors.ts'
import type { KlineBar } from '../pdat/datasource.ts'
import { runBacktest, validateBacktestParams } from './backtest.ts'
import type { BacktestReport } from './backtest.ts'
import {
  runBacktestGrid, validateGridSpec, rankGridResults, formatOptimizationSummary,
} from './optimize.ts'
import type { GridComboResult, GridSpec, RankMetric } from './optimize.ts'
import type { QuantKernelClient } from '../kernel-client/client.ts'

/** Bounds plus the default for the train/test split ratio. */
export const TRAIN_RATIO_LIMITS = { min: 0.5, max: 0.9, default: 0.7 } as const

/** The two legs of a walk-forward split. */
export interface WalkForwardSplit {
  /** The training leg, oldest first. */
  readonly train: KlineBar[]
  /** The testing leg, oldest first, immediately after the train leg. */
  readonly test: KlineBar[]
}

/**
 * Split one bar series into train and test legs at a ratio. The split is an
 * integer cut: `train` gets the first `ceil(n * ratio)` bars, `test` gets
 * the rest; both legs are non-empty for any ratio in `[0.5, 0.9]` and any
 * bar count above 2.
 * @param bars - the full fetched series, oldest first.
 * @param trainRatio - the fraction of bars assigned to train, `[0.5, 0.9]`.
 * @returns the two legs.
 */
export function splitBars(bars: readonly KlineBar[], trainRatio: number): WalkForwardSplit {
  const total = bars.length
  const trainLength = Math.max(1, Math.ceil(total * trainRatio))
  return {
    train: [...bars.slice(0, trainLength)],
    test: [...bars.slice(trainLength)],
  }
}

/**
 * Validate a walk-forward split: both legs must cover the widest slow window,
 * the ratio stays inside the hard bounds, and the grid passes its own check
 * against the train leg.
 * @param bars - the full fetched bar count.
 * @param spec - the search grid.
 * @param trainRatio - the train fraction.
 * @throws {@link QuantError} code `DATA` on any invalid parameter.
 */
export function validateWalkForwardParams(bars: number, spec: GridSpec, trainRatio: number): void {
  if (typeof trainRatio !== 'number' || !Number.isFinite(trainRatio)
    || trainRatio < TRAIN_RATIO_LIMITS.min || trainRatio > TRAIN_RATIO_LIMITS.max) {
    throw new QuantError(
      'DATA',
      `train_ratio 必须是 ${String(TRAIN_RATIO_LIMITS.min)}-${String(TRAIN_RATIO_LIMITS.max)} 之间的数值，收到 ${String(trainRatio)}`,
    )
  }
  const trainLength = Math.max(1, Math.ceil(bars * trainRatio))
  const testLength = bars - trainLength
  if (testLength < spec.slow.max + 1) {
    throw new QuantError(
      'DATA',
      `测试段长度 ${String(testLength)} 不足以覆盖最宽慢线窗口（≥ ${String(spec.slow.max + 1)}），请加大 bars 或降低 train_ratio`,
    )
  }
  // The train leg is what the grid validates against.
  validateGridSpec(trainLength, spec)
}

/**
 * Run the walk-forward pipeline through two kernel requests. The train leg
 * runs the grid (metrics only); the test leg runs one single backtest on
 * the best (fast, slow) from the train ranking, returning the full report.
 * @param kernel - the kernel client.
 * @param symbol - the analyzed symbol.
 * @param split - the pre-split train/test legs.
 * @param spec - the pre-validated search grid.
 * @param initialCash - starting cash shared by both legs.
 * @param feeRate - per-trade fee rate shared by both legs.
 * @param rankBy - the ranking metric for the train leg.
 * @param topN - how many train leaders to keep (for the summary table).
 * @param signal - the caller's cancellation signal.
 * @returns the train grid results, the ranked leaders, and the test report.
 * @throws {@link QuantError} on kernel or wire-shape failure.
 */
export async function runWalkForward(
  kernel: QuantKernelClient,
  symbol: string,
  split: WalkForwardSplit,
  spec: GridSpec,
  initialCash: number,
  feeRate: number,
  rankBy: RankMetric,
  topN: number,
  signal?: AbortSignal,
): Promise<{
  readonly trainResults: GridComboResult[]
  readonly ranked: GridComboResult[]
  readonly testReport: BacktestReport
}> {
  const trainResults = await runBacktestGrid(kernel, symbol, split.train, spec, initialCash, feeRate, signal)
  const ranked = rankGridResults(trainResults, rankBy, topN)
  const best = ranked[0]
  /* v8 ignore next 2 -- unreachable: the grid schema requires min(1) results, so ranked is never empty. */
  if (best === undefined) {
    throw new QuantError('DATA', '寻优网格返回空结果，无法选出最优参数')
  }
  const params = { fast: best.fast, slow: best.slow, initialCash, feeRate }
  validateBacktestParams(split.test.length, params)
  const testReport = await runBacktest(kernel, symbol, split.test, params, signal)
  return { trainResults, ranked, testReport }
}

/**
 * Format the walk-forward summary as a markdown research document. The
 * overfitting warning is load-bearing: a walk-forward report owes its
 * reader a direct statement that the test leg is one sample path, not a
 * guarantee that the train-optimal parameters survive out-of-sample.
 * @param symbol - the analyzed symbol.
 * @param spec - the search grid that ran on the train leg.
 * @param ranked - the ranked train leaders (best first).
 * @param testReport - the single run on the test leg with the train-optimal parameters.
 * @param trainRatio - the train fraction that split the bars.
 * @param comboCount - the total number of combinations that ran on the train leg.
 * @param rankBy - the ranking metric for the train leg.
 * @returns the markdown string.
 */
export function formatWalkForwardSummary(
  symbol: string,
  spec: GridSpec,
  ranked: readonly GridComboResult[],
  testReport: BacktestReport,
  trainRatio: number,
  comboCount: number,
  rankBy: RankMetric,
): string {
  const pct = (v: number): string => `${(v * 100).toFixed(2)}%`
  const best = ranked[0]
  const trainMetrics = best?.metrics
  const testMetrics = testReport.metrics
  const returnGap = trainMetrics !== undefined ? testMetrics.total_return - trainMetrics.total_return : 0
  const sharpeGap = trainMetrics !== undefined ? testMetrics.sharpe - trainMetrics.sharpe : 0
  const trainTable = formatOptimizationSummary(symbol, spec, ranked, rankBy, comboCount)
  const lines = [
    `# Walk-forward 验证报告：${symbol}`,
    '',
    '> 仅供研究参考，不构成投资建议。测试段是样本外的一条路径，train 最优参数在 test 上的表现不保证稳定；过拟合差距越大，参数越不可信。',
    '',
    '## 切分',
    `- 总K线数：${String(testReport.equity.length + comboCount)}`,
    `- 训练段比例：${String(trainRatio)}（训练 ${String(Math.round(trainRatio * 100))}% / 测试 ${String(Math.round((1 - trainRatio) * 100))}%）`,
    '- 切分点：训练段末尾紧接测试段起点，无重叠、无前瞻',
    '',
    '## 训练段寻优',
    trainTable,
    '',
    '## 样本外测试（用训练段最优参数）',
    `- 最优参数：SMA(${String(best?.fast ?? '?')}/${String(best?.slow ?? '?')})`,
    `- 测试段总收益：${pct(testMetrics.total_return)}（年化 ${pct(testMetrics.annual_return)})`,
    `- 测试段最大回撤：${pct(testMetrics.max_drawdown)}`,
    `- 测试段夏普：${testMetrics.sharpe.toFixed(4)}`,
    `- 测试段交易笔数：${String(testMetrics.trade_count)}（胜率 ${pct(testMetrics.win_rate)})`,
    `- 测试段期末净值：${testReport.final_equity.toFixed(2)}`,
    '',
    '## 过拟合差距（训练 vs 测试）',
    `- 总收益差距：${pct(returnGap)}（负值表示样本外劣化）`,
    `- 夏普差距：${sharpeGap.toFixed(4)}`,
    '- 结论：差距越小，参数越可能样本外稳定；差距为负且较大时，train 最优参数大概率是过拟合产物',
    '',
  ]
  return lines.join('\n')
}
