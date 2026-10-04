/**
 * Wire and tool value types for AI lead scoring (tools manifest §6). Plain
 * projections of the stored records — no branded ids — kept exact-optional:
 * absent means unset, and no explicit `undefined` crosses the boundary.
 * @module @deepseek-ai/dsh-customer-acquisition/scoring/types
 */

import type { IntentLevel } from '../leads/types.ts'

/** One per-dimension score as the tool sees it. */
export interface ScoreItemValue {
  dimension_id: string
  name: string
  score: number
  weight: number
  reason: string
}

/** One scoring run's headline as the tool sees it. */
export interface ScoreRunValue {
  id: string
  total: number
  intent_tag: IntentLevel
  reason: string
}

/** `score_one` envelope: the run headline plus its per-dimension items. */
export interface ScoreOneValue {
  run: ScoreRunValue
  items: ScoreItemValue[]
}

/** One successful batch entry. */
export interface ScoreBatchEntryValue {
  lead_id: string
  run_id: string
  total: number
  intent_tag: IntentLevel
}

/** One failed batch entry; the batch never aborts on a single failure. */
export interface ScoreBatchFailedValue {
  lead_id: string
  error: string
}

/** `score_batch` envelope. */
export interface ScoreBatchValue {
  runs: ScoreBatchEntryValue[]
  failed: ScoreBatchFailedValue[]
}

/** One history row's run headline. */
export interface ScoreHistoryRunValue {
  id: string
  lead_id: string
  total: number
  intent_tag: IntentLevel
  reason: string
  created_at: number
}

/** One history row's per-dimension item (weight is the snapshot at scoring time). */
export interface ScoreHistoryItemValue {
  dimension_id: string
  score: number
  weight: number
  reason: string
}

/** One history row: run plus items. */
export interface ScoreHistoryEntryValue {
  run: ScoreHistoryRunValue
  items: ScoreHistoryItemValue[]
}

/** History filters; at most one of `lead_id`/`run_id` is meaningful. */
export interface ScoreHistoryRequest {
  lead_id?: string
  run_id?: string
  limit?: number
  offset?: number
}

/** Paged history envelope, newest first. */
export interface ScoreHistoryValue {
  items: ScoreHistoryEntryValue[]
  total: number
}

/** One ICP dimension as the tool sees it. */
export interface IcpDimensionValue {
  id: string
  name: string
  description: string
  weight: number
}

/** One full ICP profile as the list tool sees it. */
export interface IcpProfileValue {
  id: string
  name: string
  industry?: string
  enabled: boolean
  dimensions: IcpDimensionValue[]
}

/** The narrow profile projection of create/update outputs. */
export interface IcpProfileRefValue {
  id: string
  name: string
  enabled: boolean
}

/** ICP list envelope. */
export interface IcpListValue {
  items: IcpProfileValue[]
}

/** One scoring prompt template as the list tool sees it. */
export interface ScoreTemplateValue {
  id: string
  name: string
  industry?: string
  prompt_text: string
  enabled: boolean
}

/** The narrow template projection of create/update outputs. */
export interface ScoreTemplateRefValue {
  id: string
  name: string
  enabled: boolean
}

/** Template list envelope. */
export interface ScoreTemplateListValue {
  items: ScoreTemplateValue[]
}

/** One dimension accepted by icp create/update. */
export interface IcpDimensionInput {
  id: string
  name: string
  description: string
  weight: number
}

/** Fields accepted by icp create. */
export interface IcpCreateInput {
  name: string
  industry?: string
  dimensions: IcpDimensionInput[]
  enabled?: boolean
}

/** Fields accepted by icp update; `dimensions` is whole-list replacement. */
export interface IcpUpdateInput {
  name?: string
  industry?: string
  enabled?: boolean
  dimensions?: IcpDimensionInput[]
}

/** Fields accepted by score-template create. */
export interface ScoreTemplateCreateInput {
  name: string
  industry?: string
  prompt_text: string
  enabled?: boolean
}

/** Fields accepted by score-template update. */
export interface ScoreTemplateUpdateInput {
  name?: string
  industry?: string
  prompt_text?: string
  enabled?: boolean
}

/** `score_one` input. */
export interface ScoreOneInput {
  lead_id: string
  icp_profile_id?: string
  score_template_id?: string
}

/** `score_batch` input. */
export interface ScoreBatchInput {
  lead_ids: string[]
  icp_profile_id?: string
  score_template_id?: string
}
