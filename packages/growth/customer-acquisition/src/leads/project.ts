/**
 * Pure projections from stored lead-ledger records to the wire values of
 * tools manifest §5. Exact-optional discipline: an unset optional field is
 * absent from the projection, never an explicit `undefined`.
 * @module @deepseek-ai/dsh-customer-acquisition/leads/project
 */

import type { Lead, LeadDocument, LeadFollowup } from '../domain/spec.ts'
import type {
  DocumentRefValue, DocumentValue, FollowupValue, LeadDetailValue, LeadRefValue,
} from './types.ts'

/** How many recent follow-ups the lead detail envelope carries. */
export const LEAD_DETAIL_FOLLOWUPS = 5

/**
 * Project a stored lead to the summary ref shared by list and mutation outputs.
 * @param lead - the stored record.
 * @returns the wire ref.
 */
export function toLeadRef(lead: Lead): LeadRefValue {
  return {
    id: lead.id,
    company_name: lead.company_name,
    ...(lead.contact_name === undefined ? {} : { contact_name: lead.contact_name }),
    source: lead.source,
    ...(lead.industry === undefined ? {} : { industry: lead.industry }),
    ...(lead.intent_level === undefined ? {} : { intent_level: lead.intent_level }),
    opportunity_stage: lead.opportunity_stage,
    ...(lead.owner_id === undefined ? {} : { owner_id: lead.owner_id }),
    status: lead.status,
    tags: [...lead.tags],
    ...(lead.next_followup_at === undefined ? {} : { next_followup_at: lead.next_followup_at }),
    updated_at: lead.updated_at,
  }
}

/**
 * Project one follow-up row to its wire value.
 * @param followup - the stored record.
 * @returns the wire value.
 */
export function toFollowupValue(followup: LeadFollowup): FollowupValue {
  return { id: followup.id, content: followup.content, created_at: followup.created_at }
}

/**
 * Project one document row to its title-only reference.
 * @param document - the stored record.
 * @returns the wire reference.
 */
export function toDocumentRef(document: LeadDocument): DocumentRefValue {
  return { id: document.id, title: document.title }
}

/**
 * Project one document row to a list row, body included on request.
 * @param document - the stored record.
 * @param includeContent - whether the body rides along.
 * @returns the wire value.
 */
export function toDocumentValue(document: LeadDocument, includeContent: boolean): DocumentValue {
  return {
    id: document.id,
    title: document.title,
    char_count: document.content.length,
    ...(includeContent ? { content: document.content } : {}),
  }
}

/**
 * Build the lead detail envelope: ref plus demand/budget long text, the most
 * recent follow-ups (newest first), and the attached document references.
 * @param lead - the stored lead.
 * @param followups - the lead's follow-ups, newest first.
 * @param documents - the lead's documents, any order.
 * @returns the detail envelope.
 */
export function toLeadDetail(lead: Lead, followups: LeadFollowup[], documents: LeadDocument[]): LeadDetailValue {
  return {
    lead: toLeadRef(lead),
    ...(lead.demand_desc === undefined ? {} : { demand_desc: lead.demand_desc }),
    ...(lead.budget_range === undefined ? {} : { budget_range: lead.budget_range }),
    followups: followups
      .sort((left, right) => right.created_at - left.created_at)
      .slice(0, LEAD_DETAIL_FOLLOWUPS)
      .map(toFollowupValue),
    documents: documents.map(toDocumentRef),
  }
}
