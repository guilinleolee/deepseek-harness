/**
 * Wire and tool value types for the lead ledger (tools manifest §5). Storage
 * record types live in `domain/spec.ts`; everything here is the plain
 * projection the model sees — no branded ids, no readonly aliases — kept
 * exact-optional: absent means unset, and no explicit `undefined` crosses
 * the boundary.
 * @module @deepseek-ai/dsh-customer-acquisition/leads/types
 */

import type { z } from 'zod'
import type {
  decisionRoleSchema, intentLevelSchema, leadStatusSchema, opportunityStageSchema,
} from '../domain/spec.ts'

/** Lead qualification tag written back by the scoring flow. */
export type IntentLevel = z.infer<typeof intentLevelSchema>
/** Contact's decision role in the buying process. */
export type DecisionRole = z.infer<typeof decisionRoleSchema>
/** Lead lifecycle status; `recycled` is the recycle bin. */
export type LeadStatus = z.infer<typeof leadStatusSchema>
/** Opportunity progress. */
export type OpportunityStage = z.infer<typeof opportunityStageSchema>

/**
 * Lead summary projection shared by list, batch surfaces, and the future
 * dashboard; long free-text fields (demand, budget) stay out on purpose.
 */
export interface LeadRefValue {
  id: string
  company_name: string
  contact_name?: string
  source: string
  industry?: string
  intent_level?: IntentLevel
  opportunity_stage: OpportunityStage
  owner_id?: string
  status: LeadStatus
  tags: string[]
  next_followup_at?: number
  updated_at: number
}

/** Filters for lead list and lead export; every field is optional. */
export interface LeadListRequest {
  status?: LeadStatus
  source?: string
  industry?: string
  intent_level?: IntentLevel
  tag?: string
  /** `me` = owned by the operator, `pool` = unowned, `all` = no owner filter. */
  owner?: 'me' | 'pool' | 'all'
  q?: string
  created_from?: number
  created_to?: number
  limit?: number
  offset?: number
}

/** Paged lead projection, newest first. */
export interface LeadListValue {
  items: LeadRefValue[]
  total: number
}

/** One follow-up note as the tool sees it. */
export interface FollowupValue {
  id: string
  content: string
  created_at: number
}

/** One attached document as the tool sees it. */
export interface DocumentRefValue {
  id: string
  title: string
}

/** Document list row; `content` appears only when explicitly requested. */
export interface DocumentValue {
  id: string
  title: string
  char_count: number
  content?: string
}

/** Document list envelope. */
export interface DocumentListValue {
  items: DocumentValue[]
}

/** Lead detail envelope: the ref plus the long free-text fields and recent activity. */
export interface LeadDetailValue {
  lead: LeadRefValue
  demand_desc?: string
  budget_range?: string
  followups: FollowupValue[]
  documents: DocumentRefValue[]
}

/** Lead create/update envelope. */
export interface LeadMutationValue {
  lead: LeadRefValue
}

/** Soft delete/restore envelope. */
export interface LeadStatusValue {
  lead_id: string
  status: LeadStatus
}

/** Physical delete envelope. */
export interface LeadPurgeValue {
  purged: boolean
}

/** Ownership change envelope; an empty `owner_id` string means the pool. */
export interface LeadOwnerValue {
  lead_id: string
  owner_id: string
}

/** Extracted lead fields; only recognized fields are present. */
export interface ExtractedLeadFields {
  company_name?: string
  contact_name?: string
  phone?: string
  email?: string
  industry?: string
  company_size?: string
  demand_desc?: string
  budget_range?: string
  decision_role?: string
}

/** Lead extract envelope. */
export interface LeadExtractValue {
  fields: ExtractedLeadFields
  notes?: string
}

/** Lead export envelope produced by the export tool. */
export interface LeadExportValue {
  format: 'markdown' | 'csv'
  count: number
  content: string
}

/** Fields accepted by lead create; all but `company_name` optional. */
export interface LeadCreateInput {
  company_name: string
  source?: string
  contact_name?: string
  phone?: string
  email?: string
  industry?: string
  company_size?: string
  demand_desc?: string
  budget_range?: string
  decision_role?: DecisionRole
  tags?: string[]
  opportunity_stage?: OpportunityStage
  next_followup_at?: number
  owner_id?: string
}

/** Fields accepted by lead update; `source` and `intent_level` are not editable. */
export interface LeadUpdateInput {
  company_name?: string
  contact_name?: string
  phone?: string
  email?: string
  industry?: string
  company_size?: string
  demand_desc?: string
  budget_range?: string
  decision_role?: DecisionRole
  tags?: string[]
  opportunity_stage?: OpportunityStage
  next_followup_at?: number
}
