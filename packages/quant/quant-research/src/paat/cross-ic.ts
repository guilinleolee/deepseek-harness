/**
 * Cross-sectional factor IC over a multi-symbol panel: at each date, rank
 * the symbols' factor values against their forward returns and correlate the
 * two cross sections (Spearman). The IC series aggregates into mean IC,
 * ICIR, positive-share, and a t-statistic — the standard factor-evaluation
 * vocabulary that no single-symbol time-series IC provides.
 * @module @deepseek-ai/dsh-quant-research/paat/cross-ic
 */

import { QuantError } from '../errors.ts'
import type { KlineBar } from '../pdat/datasource.ts'
import { computeFactor } from './factors.ts'
import type { FactorName, FactorSeries } from './factors.ts'
import { spearman } from './ic.ts'

/** Hard bounds for the forward-return horizon in bars. */
export const HORIZON_LIMITS = { min: 1, max: 20, default: 5 } as const

/** Hard bounds for the panel size (cross-section width). */
export const PANEL_SIZE_LIMITS = { min: 2, max: 10 } as const

/** One cross-sectional IC reading: the date and the rank correlation across symbols. */
export interface CrossICPoint {
  /** The factor-observation date. */
  readonly date: string
  /** Cross-sectional Spearman between factor values and forward returns; null when degenerate. */
  readonly ic: number | null
}

/** The aggregate evaluation of one cross-sectional IC series. */
export interface CrossICSummary {
  /** Observations entering the aggregate (non-null IC readings). */
  readonly observations: number
  /** Mean IC over the valid readings. */
  readonly meanIC: number
  /** Standard deviation of the valid IC readings. */
  readonly stdIC: number
  /** ICIR: mean IC divided by its standard deviation (0 when the std is 0). */
  readonly icir: number
  /** Share of positive IC readings in `[0, 1]`. */
  readonly positiveShare: number
  /** t-statistic of the mean IC against 0. */
  readonly tStat: number
}

/** The aligned panel one cross-sectional evaluation runs on. */
export interface AlignedPanel {
  /** The dates every symbol shares, oldest first. */
  readonly dates: readonly string[]
  /** One close-price series per symbol, aligned to `dates`. */
  readonly closes: Readonly<Record<string, readonly number[]>>
}

/**
 * Align a per-symbol bar map onto the dates every symbol shares, oldest
 * first. Symbols missing from the map or carrying fewer than two shared
 * dates collapse the panel.
 * @param seriesBySymbol - each symbol's fetched bars, oldest first.
 * @returns the shared dates with per-symbol close series aligned to them.
 * @throws {@link QuantError} code `DATA` when fewer than two shared dates exist.
 */
export function alignPanel(
  seriesBySymbol: Readonly<Record<string, readonly KlineBar[]>>,
): AlignedPanel {
  const symbols = Object.keys(seriesBySymbol).sort()
  const shared = new Map<string, Record<string, number>>()
  for (const symbol of symbols) {
    for (const bar of seriesBySymbol[symbol] ?? []) {
      shared.set(bar.date, { ...shared.get(bar.date), [symbol]: bar.close })
    }
  }
  const dates = [...shared.keys()].filter(date => {
    const row = shared.get(date) ?? {}
    return symbols.every(symbol => row[symbol] !== undefined)
  }).sort()
  if (dates.length < 2) {
    throw new QuantError('DATA', '各标的共享交易日不足 2 天，无法构建横截面')
  }
  const closes: Record<string, number[]> = {}
  for (const symbol of symbols) {
    closes[symbol] = dates.map(date => (shared.get(date) ?? {})[symbol] as number)
  }
  return { dates, closes }
}

/**
 * Compute one symbol's factor series across the panel dates. The factor runs
 * on the symbol's own full history up to each date (no lookahead: the value
 * at index t only reads closes up to t).
 * @param name - the factor to compute.
 * @param bars - the symbol's full fetched series, oldest first.
 * @param dates - the panel dates (a subset of the bars' dates).
 * @param window - the factor look-back window (factor-specific default when omitted).
 * @returns the factor values aligned to `dates` (null where undefined).
 */
export function factorOnDates(
  name: FactorName,
  bars: readonly KlineBar[],
  dates: readonly string[],
  window?: number,
): FactorSeries {
  const factor = computeFactor(name, bars, window)
  const byDate = new Map<string, number | null>()
  bars.forEach((bar, index) => { byDate.set(bar.date, factor[index] ?? null) })
  return dates.map(date => byDate.get(date) ?? null)
}

/**
 * Compute the cross-sectional IC at each date where every symbol has both a
 * factor value and a horizon-day forward return.
 * @param panel - the aligned panel.
 * @param factorBySymbol - each symbol's factor values aligned to the panel dates.
 * @param horizon - the forward-return horizon in bars (`HORIZON_LIMITS`).
 * @returns the IC series, oldest first.
 * @throws {@link QuantError} code `DATA` on an out-of-bounds horizon.
 */
export function crossSectionIC(
  panel: AlignedPanel,
  factorBySymbol: Readonly<Record<string, FactorSeries>>,
  horizon: number,
): CrossICPoint[] {
  if (!Number.isSafeInteger(horizon) || horizon < HORIZON_LIMITS.min || horizon > HORIZON_LIMITS.max) {
    throw new QuantError('DATA', `horizon 必须是 ${String(HORIZON_LIMITS.min)}-${String(HORIZON_LIMITS.max)} 的整数`)
  }
  const symbols = Object.keys(factorBySymbol).sort()
  const points: CrossICPoint[] = []
  for (let index = 0; index + horizon < panel.dates.length; index += 1) {
    const factorValues: number[] = []
    const forwardReturns: number[] = []
    for (const symbol of symbols) {
      const factorValue = factorBySymbol[symbol]?.[index]
      const closeToday = panel.closes[symbol]?.[index]
      const closeFuture = panel.closes[symbol]?.[index + horizon]
      if (factorValue === undefined || factorValue === null
        || closeToday === undefined || closeFuture === undefined) continue
      factorValues.push(factorValue)
      forwardReturns.push(closeFuture / closeToday - 1)
    }
    const ic = spearman(factorValues, forwardReturns)
    points.push({ date: panel.dates[index] ?? '', ic })
  }
  return points
}

/**
 * Aggregate one IC series into the factor-evaluation summary.
 * @param points - the IC series, oldest first.
 * @returns the aggregate, or null when fewer than two valid readings exist.
 */
export function summarizeIC(points: readonly CrossICPoint[]): CrossICSummary | null {
  const valid = points.map(point => point.ic).filter((ic): ic is number => ic !== null)
  if (valid.length < 2) return null
  const mean = valid.reduce((sum, ic) => sum + ic, 0) / valid.length
  const variance = valid.reduce((sum, ic) => sum + (ic - mean) ** 2, 0) / (valid.length - 1)
  const std = Math.sqrt(variance)
  const positive = valid.filter(ic => ic > 0).length
  return {
    observations: valid.length,
    meanIC: mean,
    stdIC: std,
    icir: std === 0 ? 0 : mean / std,
    positiveShare: positive / valid.length,
    tStat: std === 0 ? 0 : (mean / std) * Math.sqrt(valid.length),
  }
}

/**
 * Format the cross-sectional IC evaluation as a markdown research document.
 * The disclaimer states the reading discipline: a factor earns attention
 * only when |ICIR| clears 0.5 with a positive share clearly off 50%.
 * @param symbols - the panel symbols (sorted, as evaluated).
 * @param factor - the evaluated factor.
 * @param window - the factor look-back window in effect.
 * @param horizon - the forward-return horizon in bars.
 * @param bars - the per-symbol bar count requested.
 * @param points - the IC series.
 * @param summary - the aggregate (null when too few valid readings).
 * @returns the markdown string.
 */
export function formatCrossICSummary(
  symbols: readonly string[],
  factor: FactorName,
  window: number,
  horizon: number,
  bars: number,
  points: readonly CrossICPoint[],
  summary: CrossICSummary | null,
): string {
  const pct = (v: number): string => `${(v * 100).toFixed(1)}%`
  const tail = points.slice(-6)
  const tailLines = tail.map(point => `- ${point.date}: ${point.ic === null ? '（截面退化，无有效秩相关）' : point.ic.toFixed(4)}`)
  const verdict = summary === null
    ? '有效截面不足 2 个，无法评估该因子'
    : Math.abs(summary.icir) >= 0.5
      ? `ICIR ${summary.icir.toFixed(3)} 越过 ±0.5——在该面板与窗口上具备横截面区分力${summary.meanIC < 0 ? '（注意方向为负，因子值越高收益越低）' : ''}`
      : `ICIR ${summary.icir.toFixed(3)} 未越过 ±0.5——横截面区分力不足，不建议据此选股`
  const lines = [
    `# 横截面 IC 评估：${factor}（窗口 ${String(window)}，前视 ${String(horizon)} 日）`,
    '',
    '> 仅供研究参考，不构成投资建议。横截面 IC 衡量的是"同一时刻横跨标的"的排序预测力，与单标的时间序列 IC 含义不同；经验门槛 |ICIR| ≥ 0.5。',
    '',
    '## 面板',
    `- 标的（${String(symbols.length)} 只）：${symbols.join('、')}`,
    `- 每标的K线数：${String(bars)}；共享交易日：${String(points.length + horizon)}（截断说明：尾部 ${String(horizon)} 天无法构成前视收益）`,
    '',
    '## 聚合',
    ...(summary === null ? [] : [
      `- 有效截面：${String(summary.observations)} 个`,
      `- 平均 IC：${summary.meanIC.toFixed(4)}（IC 波动 ${summary.stdIC.toFixed(4)}）`,
      `- ICIR：${summary.icir.toFixed(4)}`,
      `- IC 为正的截面占比：${pct(summary.positiveShare)}`,
      `- t 统计：${summary.tStat.toFixed(3)}`,
    ]),
    '',
    '## 结论',
    `- ${verdict}`,
    '',
    '## 最近截面 IC',
    ...tailLines,
    '',
  ]
  return lines.join('\n')
}
