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

/** Bounds plus the default for the rolling-window count (`windows >= 2` enables rolling). */
export const ROLLING_WINDOWS_LIMITS = { min: 2, max: 10, default: 4 } as const

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

/** One rolling window: the expanding train prefix plus its out-of-sample segment. */
export interface RollingWindow {
  /** Zero-based window order, chronological. */
  readonly index: number
  /** Every bar before this window's test segment (expanding; includes earlier test segments). */
  readonly train: KlineBar[]
  /** This window's out-of-sample segment, oldest first. */
  readonly test: KlineBar[]
}

/**
 * Cut a series into `windows` rolling walk-forward windows with an expanding
 * train leg: the bars trim to `segmentLength * (windows + 1)`, where
 * `segmentLength = floor(total / (windows + 1))`; segment 0 is the initial
 * train prefix and each following segment is one window's out-of-sample test.
 * Every train leg therefore contains earlier test segments — the producer
 * never sees the future, and later windows re-optimize on more history.
 * @param bars - the full fetched series, oldest first.
 * @param windows - the window count, in `ROLLING_WINDOWS_LIMITS`.
 * @returns one window per test segment, chronological.
 */
export function splitRollingWindows(bars: readonly KlineBar[], windows: number): RollingWindow[] {
  const segmentLength = Math.floor(bars.length / (windows + 1))
  const usable = segmentLength * (windows + 1)
  const trimmed = bars.slice(0, usable)
  const windowsOut: RollingWindow[] = []
  for (let index = 0; index < windows; index += 1) {
    const trainEnd = segmentLength * (index + 1)
    windowsOut.push({
      index,
      train: [...trimmed.slice(0, trainEnd)],
      test: [...trimmed.slice(trainEnd, trainEnd + segmentLength)],
    })
  }
  return windowsOut
}

/**
 * Validate a rolling walk-forward plan: the window count stays inside the
 * hard bounds, and one segment length covers the widest slow window on both
 * the initial train leg (grid warmup) and every test leg.
 * @param bars - the full fetched bar count.
 * @param spec - the search grid.
 * @param windows - the window count.
 * @throws {@link QuantError} code `DATA` on any invalid parameter.
 */
export function validateRollingParams(bars: number, spec: GridSpec, windows: number): void {
  if (!Number.isSafeInteger(windows) || windows < ROLLING_WINDOWS_LIMITS.min || windows > ROLLING_WINDOWS_LIMITS.max) {
    throw new QuantError(
      'DATA',
      `windows 必须是 ${String(ROLLING_WINDOWS_LIMITS.min)}-${String(ROLLING_WINDOWS_LIMITS.max)} 的整数，收到 ${String(windows)}`,
    )
  }
  const segmentLength = Math.floor(bars / (windows + 1))
  if (segmentLength < spec.slow.max + 1) {
    throw new QuantError(
      'DATA',
      `每段长度 ${String(segmentLength)} 不足以覆盖最宽慢线窗口（≥ ${String(spec.slow.max + 1)}），请加大 bars 或减少 windows`,
    )
  }
  // The initial train leg (one segment) is what the grid validates against.
  validateGridSpec(segmentLength, spec)
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

/** The out-of-sample outcome of one rolling window. */
export interface RollingWindowResult {
  /** Zero-based window order, chronological. */
  readonly index: number
  /** Bars in this window's train leg. */
  readonly trainBars: number
  /** Bars in this window's test leg. */
  readonly testBars: number
  /** The train-optimal parameters this window re-selected. */
  readonly best: GridComboResult
  /** The out-of-sample report on the test segment. */
  readonly testReport: BacktestReport
  /** Test minus train total return (negative means out-of-sample decay). */
  readonly returnGap: number
  /** Test minus train Sharpe. */
  readonly sharpeGap: number
}

/**
 * Run the rolling walk-forward pipeline: one grid re-optimization plus one
 * out-of-sample backtest per window, sequential and cancellable. Windows run
 * oldest first; each window re-runs the full grid on its expanding train leg.
 * @param kernel - the kernel client.
 * @param symbol - the analyzed symbol.
 * @param windows - the pre-split rolling windows.
 * @param spec - the pre-validated search grid.
 * @param initialCash - starting cash shared by every leg.
 * @param feeRate - per-trade fee rate shared by every leg.
 * @param rankBy - the ranking metric for each train leg.
 * @param topN - how many train leaders to keep per window.
 * @param signal - the caller's cancellation signal.
 * @returns one result per window, chronological.
 */
export async function runRollingWalkForward(
  kernel: QuantKernelClient,
  symbol: string,
  windows: readonly RollingWindow[],
  spec: GridSpec,
  initialCash: number,
  feeRate: number,
  rankBy: RankMetric,
  topN: number,
  signal?: AbortSignal,
): Promise<RollingWindowResult[]> {
  const results: RollingWindowResult[] = []
  for (const window of windows) {
    const { ranked, testReport } = await runWalkForward(
      kernel, symbol, { train: window.train, test: window.test }, spec,
      initialCash, feeRate, rankBy, topN, signal,
    )
    const best = ranked[0]
    /* v8 ignore next 2 -- unreachable: the grid schema requires min(1) results, so ranked is never empty. */
    if (best === undefined) {
      throw new QuantError('DATA', '寻优网格返回空结果，无法选出最优参数')
    }
    results.push({
      index: window.index,
      trainBars: window.train.length,
      testBars: window.test.length,
      best,
      testReport,
      returnGap: testReport.metrics.total_return - best.metrics.total_return,
      sharpeGap: testReport.metrics.sharpe - best.metrics.sharpe,
    })
  }
  return results
}

/**
 * Format the rolling walk-forward summary: a per-window table of the
 * re-optimized parameters against their out-of-sample outcomes, plus the
 * aggregate stability read (mean/median out-of-sample return, mean gap,
 * share of positive windows).
 * @param symbol - the analyzed symbol.
 * @param spec - the search grid re-run on every train leg (rendered into the split section).
 * @param results - the per-window outcomes, chronological.
 * @param windows - the requested window count.
 * @param rankBy - the ranking metric used on every train leg.
 * @param comboCount - combinations re-run per window.
 * @returns the markdown string.
 */
export function formatRollingWalkForwardSummary(
  symbol: string,
  spec: GridSpec,
  results: readonly RollingWindowResult[],
  windows: number,
  rankBy: RankMetric,
  comboCount: number,
): string {
  const pct = (v: number): string => `${(v * 100).toFixed(2)}%`
  const oosReturns = results.map(r => r.testReport.metrics.total_return)
  const meanOos = oosReturns.reduce((sum, v) => sum + v, 0) / results.length
  const sortedReturns = [...oosReturns].sort((a, b) => a - b)
  const mid = Math.floor(sortedReturns.length / 2)
  const medianOos = sortedReturns.length % 2 === 1
    ? sortedReturns[mid]!
    : (sortedReturns[mid - 1]! + sortedReturns[mid]!) / 2
  const meanGap = results.reduce((sum, r) => sum + r.returnGap, 0) / results.length
  const positiveShare = oosReturns.filter(v => v > 0).length / results.length
  const stable = meanGap >= 0 && positiveShare >= 0.5
  const rows = results.map(r => [
    `W${String(r.index + 1)}`,
    `SMA(${String(r.best.fast)}/${String(r.best.slow)})`,
    pct(r.best.metrics.total_return),
    pct(r.testReport.metrics.total_return),
    pct(r.returnGap),
    r.testReport.metrics.sharpe.toFixed(3),
    pct(r.testReport.metrics.max_drawdown),
  ].join(' | '))
  const lines = [
    `# 滚动 Walk-forward 验证报告：${symbol}`,
    '',
    '> 仅供研究参考，不构成投资建议。每个窗口都在各自时点重新寻优，样本外表现衡量的正是"每期重选参数"这一真实策略；聚合差距为负说明逐期重寻优整体在样本外劣化。',
    '',
    '## 滚动切分（扩展窗）',
    `- 窗口数：${String(windows)}（每窗重新寻优 ${String(comboCount)} 个组合）`,
    `- 切分：K线均分为 ${String(windows + 1)} 段，第 1 段为初始训练段（网格 ${String(spec.fast.min)}-${String(spec.fast.max)}/${String(spec.slow.min)}-${String(spec.slow.max)}），其后每段依次作样本外测试`,
    '- 训练窗扩展：第 i 个窗口用其之前全部历史（含更早的测试段）重新寻优，无前瞻',
    '',
    '## 逐窗样本外表现',
    '',
    '窗口 | 最优参数 | 训练收益 | 样本外收益 | 收益差距 | 样本外夏普 | 样本外回撤',
    '--- | --- | --- | --- | --- | --- | ---',
    ...rows,
    '',
    '## 聚合稳定性',
    `- 样本外收益均值：${pct(meanOos)}（中位数 ${pct(medianOos)}）`,
    `- 平均收益差距（样本外 − 训练）：${pct(meanGap)}（负值表示整体样本外劣化）`,
    `- 样本外为正的窗口占比：${pct(positiveShare)}`,
    `- 排名指标：${rankBy}`,
    `- 结论：${stable
      ? '平均差距非负且多数窗口样本外为正——逐期重寻优在该历史上表现出样本外稳定性'
      : '平均差距为负或多数窗口样本外亏损——逐期重寻优大概率是过拟合，参数不具备样本外可信度'}`,
    '',
  ]
  return lines.join('\n')
}
