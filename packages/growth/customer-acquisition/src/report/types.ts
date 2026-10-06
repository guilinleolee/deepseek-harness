/**
 * Wire and tool value types for the P4 data dashboard (tools manifest §9).
 * Everything here is the plain projection both the model tool and the
 * browser Remote face serve; exact-optional like every other surface.
 * @module @deepseek-ai/dsh-customer-acquisition/report/types
 */

/** Preset aggregation windows; `custom` reads `from`/`to` off the request. */
export type OverviewPeriod = 'today' | 'week' | 'month' | 'custom'

/** Drill-down dimension; `none` serves no breakdown. */
export type OverviewGroupBy = 'none' | 'industry' | 'source'

/** Overview request as both faces see it. */
export type OverviewRequest = {
  period: OverviewPeriod
  /** Custom-window start (epoch ms); required when `period=custom`. */
  from?: number
  /** Custom-window end (epoch ms); required when `period=custom`. */
  to?: number
  group_by?: OverviewGroupBy
}

/** Lead intent-level counts, zero-filled over the frozen value set. */
export type IntentDistribution = {
  high: number
  mid: number
  low: number
  invalid: number
}

/** Latest-score-per-lead histogram over the four frozen buckets. */
export type ScoreDistribution = {
  '0-59': number
  '60-74': number
  '75-89': number
  '90-100': number
}

/** SOP task outcomes; `completion_rate` is `done/total` in 0-1 (2 decimals). */
export type TaskStats = {
  total: number
  done: number
  deferred: number
  dropped: number
  completion_rate: number
}

/** GEO diagnosis roll-up; `last_score` is absent before the first report. */
export type GeoStats = {
  scan_count: number
  avg_score: number
  last_score?: number
}

/** The seven dashboard metrics. */
export type OverviewTotals = {
  lead_count: number
  new_in_period: number
  intent_distribution: IntentDistribution
  source_distribution: Record<string, number>
  score_distribution: ScoreDistribution
  tasks: TaskStats
  geo: GeoStats
}

/** One drill-down group; `key` is the industry/source value or `未填写`. */
export type OverviewBreakdownGroup = {
  key: string
  lead_count: number
  new_in_period: number
  intent_distribution: IntentDistribution
}

/** The dashboard value: totals plus the drill-down (`null` when `group_by=none`). */
export type OverviewValue = {
  totals: OverviewTotals
  breakdown: OverviewBreakdownGroup[] | null
}
