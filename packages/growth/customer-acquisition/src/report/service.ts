/**
 * The P4 dashboard aggregation: one deterministic reduction of the domain
 * tables into the seven overview metrics. Pure read — no audit, no model —
 * served identically to the model tool and the browser Remote face.
 * @module @deepseek-ai/dsh-customer-acquisition/report/service
 */

import type { Domain } from '@deepseek-ai/dsh-storage-domain'
import { customerAcquisitionDomainSpec, type Lead, type ScoreRun } from '../domain/spec.ts'
import type { ResolvedOperator } from '../permission/types.ts'
import type {
  GeoStats, IntentDistribution, OverviewBreakdownGroup, OverviewGroupBy,
  OverviewRequest, OverviewTotals, OverviewValue, ScoreDistribution, TaskStats,
} from '../types.ts'

type AcquisitionDomain = Domain<typeof customerAcquisitionDomainSpec>

/** The latest-score buckets, ascending by lower bound. */
const SCORE_BUCKETS = [
  { key: '0-59', min: 0 },
  { key: '60-74', min: 60 },
  { key: '75-89', min: 75 },
  { key: '90-100', min: 90 },
] as const

/** The drill-down key standing in for a lead without the grouped field. */
const UNFILLED_KEY = '未填写'

/**
 * The dashboard aggregator over one open domain. Stateless — every call
 * re-reads the tables, so repeated panels never see stale aggregates.
 */
export class ReportService {
  private readonly domain: AcquisitionDomain

  /**
   * @param domain - the open customer-acquisition domain (borrowed, never closed here).
   */
  constructor(domain: AcquisitionDomain) {
    this.domain = domain
  }

  /**
   * Aggregate the seven metrics for one operator. `lead_scope=own` sees its
   * own leads plus the pool — the ledger's list scope, mirrored here so the
   * dashboard never exposes another operator's leads; GEO metrics are
   * site-level and shared. `period` bounds `new_in_period` only; the
   * distribution metrics always span all visible leads.
   * @param request - the window and drill-down selection.
   * @param operator - the caller's resolved operator.
   * @param now - the clock, injectable for deterministic tests.
   * @returns the totals plus the drill-down (absent breakdown when `group_by` is `none`/unset).
   */
  overview(request: OverviewRequest, operator: ResolvedOperator, now: number = Date.now()): OverviewValue {
    const window = resolveWindow(request, now)
    const leads = this.visibleLeads(operator)
    const leadIds = new Set(leads.map(lead => lead.id))
    const totals: OverviewTotals = {
      lead_count: leads.length,
      new_in_period: leads.filter(lead => lead.created_at >= window.from && lead.created_at <= window.to).length,
      intent_distribution: intentDistributionOf(leads),
      source_distribution: sourceDistributionOf(leads),
      score_distribution: this.scoreDistributionOf(leadIds),
      tasks: this.taskStatsOf(leadIds),
      geo: this.geoStats(),
    }
    const groupBy: OverviewGroupBy = request.group_by ?? 'none'
    return {
      totals,
      breakdown: groupBy === 'none' ? null : breakdownOf(leads, groupBy, window),
    }
  }

  /** Leads the operator may see: everything for `all`, own + pool for `own`. */
  private visibleLeads(operator: ResolvedOperator): Lead[] {
    return [...this.domain.table('leads').entries()]
      .map(([, lead]) => lead)
      .filter(lead => operator.capabilities.lead_scope === 'all'
        || lead.owner_id === undefined
        || lead.owner_id === operator.userId)
  }

  /** Latest-run-per-lead histogram over the four frozen score buckets. */
  private scoreDistributionOf(leadIds: Set<string>): ScoreDistribution {
    const latest = new Map<string, ScoreRun>()
    for (const [, run] of this.domain.table('score_runs').entries()) {
      if (!leadIds.has(run.lead_id)) continue
      const current = latest.get(run.lead_id)
      if (current === undefined || run.created_at > current.created_at) latest.set(run.lead_id, run)
    }
    const distribution: ScoreDistribution = { '0-59': 0, '60-74': 0, '75-89': 0, '90-100': 0 }
    for (const run of latest.values()) {
      // the highest lower bound the total satisfies = its bucket; the 0
      // bucket always satisfies, so `best` ends assigned
      let best: (typeof SCORE_BUCKETS)[number] = SCORE_BUCKETS[0]
      for (const candidate of SCORE_BUCKETS) {
        if (run.total >= candidate.min) best = candidate
      }
      distribution[best.key] += 1
    }
    return distribution
  }

  /** SOP task outcomes over the visible leads' tasks. */
  private taskStatsOf(leadIds: Set<string>): TaskStats {
    const stats: TaskStats = { total: 0, done: 0, deferred: 0, dropped: 0, completion_rate: 0 }
    for (const [, task] of this.domain.table('sop_tasks').entries()) {
      if (!leadIds.has(task.lead_id)) continue
      stats.total += 1
      if (task.status === 'done') stats.done += 1
      if (task.status === 'deferred') stats.deferred += 1
      if (task.status === 'dropped') stats.dropped += 1
    }
    stats.completion_rate = stats.total === 0 ? 0 : Math.round((stats.done / stats.total) * 100) / 100
    return stats
  }

  /** GEO roll-up over every scan and report (site-level, no operator scope). */
  private geoStats(): GeoStats {
    let last: { at: number; score: number } | undefined
    let scoreSum = 0
    let reportCount = 0
    for (const [, report] of this.domain.table('geo_reports').entries()) {
      scoreSum += report.score
      reportCount += 1
      if (last === undefined || report.created_at >= last.at) last = { at: report.created_at, score: report.score }
    }
    return {
      scan_count: [...this.domain.table('geo_scans').keys()].length,
      avg_score: reportCount === 0 ? 0 : Math.round(scoreSum / reportCount),
      ...(last === undefined ? {} : { last_score: last.score }),
    }
  }
}

/**
 * Resolve the aggregation window from the preset period or the explicit
 * custom range; a custom request without a valid range fails loud.
 * @param request - the period selection.
 * @param now - the clock.
 * @returns the inclusive `[from, to]` epoch-ms window.
 */
function resolveWindow(request: OverviewRequest, now: number): { from: number; to: number } {
  if (request.period === 'custom') {
    if (request.from === undefined || request.to === undefined) {
      throw new Error('period=custom 需要提供 from 与 to（epoch 毫秒）')
    }
    if (request.from > request.to) throw new Error('自定义区间起止颠倒：from 不能晚于 to')
    return { from: request.from, to: request.to }
  }
  if (request.period === 'today') {
    const midnight = new Date(now)
    midnight.setHours(0, 0, 0, 0)
    return { from: midnight.getTime(), to: now }
  }
  const days = request.period === 'week' ? 7 : 30
  return { from: now - days * 24 * 60 * 60 * 1000, to: now }
}

/** Zero-filled intent counts over the frozen value set; unset intents pass. */
function intentDistributionOf(leads: Lead[]): IntentDistribution {
  const distribution: IntentDistribution = { high: 0, mid: 0, low: 0, invalid: 0 }
  for (const lead of leads) {
    if (lead.intent_level === undefined) continue
    distribution[lead.intent_level] += 1
  }
  return distribution
}

/** Source counts, keys ascending so the wire value is deterministic. */
function sourceDistributionOf(leads: Lead[]): Record<string, number> {
  const counts: Record<string, number> = {}
  for (const lead of leads) counts[lead.source] = (counts[lead.source] ?? 0) + 1
  return Object.fromEntries(Object.entries(counts).sort(([left], [right]) => left.localeCompare(right)))
}

/** Group leads by the drill-down field, heaviest group first. */
function breakdownOf(
  leads: Lead[],
  groupBy: Exclude<OverviewGroupBy, 'none'>,
  window: { from: number; to: number },
): OverviewBreakdownGroup[] {
  const groups = new Map<string, Lead[]>()
  for (const lead of leads) {
    const key = groupBy === 'industry' ? lead.industry ?? UNFILLED_KEY : lead.source
    const bucket = groups.get(key)
    if (bucket === undefined) groups.set(key, [lead])
    else bucket.push(lead)
  }
  return [...groups.entries()]
    .map(([key, group]) => ({
      key,
      lead_count: group.length,
      new_in_period: group.filter(lead => lead.created_at >= window.from && lead.created_at <= window.to).length,
      intent_distribution: intentDistributionOf(group),
    }))
    .sort((left, right) => right.lead_count - left.lead_count || left.key.localeCompare(right.key))
}
