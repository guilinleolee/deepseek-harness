/**
 * Wire and tool value types shared by the service, the tools, and the
 * browser Remote client. Storage record types live in `domain/spec.ts`;
 * everything here is a plain projection the model or the panel sees — no
 * branded ids, no readonly aliases — so the tool output schemas and the
 * generated Remote client stay in one type family.
 * @module @deepseek-ai/dsh-customer-acquisition/types
 */

import type { AuditSource } from './domain/spec.ts'

/** Partial settings update; omitted fields keep their current value. */
export interface SettingsPatchInput {
  default_icp_profile_id?: string
  default_score_template_id?: string
  geo_max_pages?: number
  geo_page_timeout_ms?: number
  sop_todo_write_enabled?: boolean
}

/**
 * The panel/tool-facing settings snapshot: exact-optional, wire-aligned
 * (absent means unset; no explicit `undefined` values cross the boundary).
 */
export interface SettingsValue {
  default_icp_profile_id?: string
  default_score_template_id?: string
  geo_max_pages: number
  geo_page_timeout_ms: number
  sop_todo_write_enabled: boolean
}

/** The settings projection both the tool and the panel return. */
export interface SettingsSnapshotValue {
  settings: SettingsValue
}

/** Audit list/export filter; every field is optional. */
export interface AuditListRequest {
  source?: AuditSource
  operator_user_id?: string
  action_prefix?: string
  object_type?: string
  from?: number
  to?: number
  limit?: number
  offset?: number
}

/** One audit row as the tool and panel see it. */
export interface AuditLogValue {
  id: string
  source: AuditSource
  operator_user_id: string
  action: string
  object_type: string
  object_id?: string
  summary: string
  created_at: number
}

/** Paged audit projection, newest first. */
export interface AuditListValue {
  items: AuditLogValue[]
  total: number
}

/** Export envelope produced by the audit export tool. */
export interface AuditExportValue {
  format: 'markdown' | 'csv'
  count: number
  content: string
}

/** One GEO scan-history row as the panel sees it: the scan joined with its report's score. */
export interface GeoScanRowValue {
  scan_id: string
  url: string
  status: 'running' | 'done' | 'failed'
  started_at: number
  finished_at?: number
  report_id?: string
  score?: number
}

/** Paged GEO scan history, newest first. */
export interface GeoScanListValue {
  items: GeoScanRowValue[]
  total: number
}

// ------------------------------------------------------- P4 dashboard ----

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

/** Panel-face re-exports: every Remote boundary type lives on a public type subpath. */
export type { LeadListRequest, LeadListValue } from './leads/types.ts'
export type { ContentTemplate } from './domain/spec.ts'
export type { GeneratedContent, GeoReport, ScoreRun, SopTask, SopTemplate } from './domain/spec.ts'
export type { IcpProfileValue, ScoreTemplateValue } from './scoring/types.ts'
