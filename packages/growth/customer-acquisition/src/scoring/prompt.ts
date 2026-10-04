/**
 * Scoring prompt assembly (data contract §3.6, §6): renders the template's
 * `{{lead}}`/`{{icp_profile}}`/`{{dimensions}}`/`{{knowledge}}` placeholders
 * and aggregates the lead's attached documents into the knowledge block.
 * Unknown placeholders render as the empty string; every known one is always
 * provided, so a rendered prompt never leaks a raw `{{token}}`.
 * @module @deepseek-ai/dsh-customer-acquisition/scoring/prompt
 */

import type { IcpProfile, Lead, LeadDocument } from '../domain/spec.ts'

/** Character cap on the aggregated knowledge block (data contract §6). */
export const KNOWLEDGE_INJECT_MAX_CHARS = 4_000

/** Truncation marker appended when the knowledge block exceeds the cap. */
export const KNOWLEDGE_TRUNCATED_MARK = '[已截断]'

/**
 * Aggregate the lead's attached documents into one ordered text block,
 * capped at the injection limit with an explicit truncation mark.
 * @param documents - the lead's documents, any order (sorted oldest first).
 * @returns the `{{knowledge}}` block; empty when the lead has no documents.
 */
export function aggregateKnowledge(documents: readonly LeadDocument[]): string {
  const ordered = [...documents].sort((left, right) => left.created_at - right.created_at)
  const body = ordered
    .map(document => `## ${document.title}\n\n${document.content}`)
    .join('\n\n')
  if (body.length <= KNOWLEDGE_INJECT_MAX_CHARS) return body
  return `${body.slice(0, KNOWLEDGE_INJECT_MAX_CHARS)}\n\n${KNOWLEDGE_TRUNCATED_MARK}`
}

/** Render the profile line: name plus optional industry. */
function profileLine(profile: IcpProfile): string {
  return profile.industry === undefined ? profile.name : `${profile.name}（适用行业：${profile.industry}）`
}

/** Render the dimension list: one line per dimension with its weight. */
function dimensionLines(profile: IcpProfile): string {
  return profile.dimensions
    .map(dimension => `- ${dimension.id} ${dimension.name}（权重 ${dimension.weight}%）：${dimension.description}`)
    .join('\n')
}

/** Render the lead block: the facts a scorer needs, as compact JSON. */
function leadBlock(lead: Lead): string {
  return JSON.stringify({
    company_name: lead.company_name,
    contact_name: lead.contact_name,
    phone: lead.phone,
    email: lead.email,
    industry: lead.industry,
    company_size: lead.company_size,
    demand_desc: lead.demand_desc,
    budget_range: lead.budget_range,
    decision_role: lead.decision_role,
    source: lead.source,
    tags: lead.tags,
  })
}

/**
 * Render one scoring prompt from a template. Every known placeholder is
 * substituted; any other `{{token}}` renders as the empty string.
 * @param templateText - the template's `prompt_text`.
 * @param parts - the lead, its resolved ICP profile, and the knowledge block.
 * @returns the complete user-prompt text.
 */
export function renderScorePrompt(
  templateText: string,
  parts: { lead: Lead; profile: IcpProfile; knowledge: string },
): string {
  return templateText.replace(/\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}/gu, (_match, name: string) => {
    switch (name) {
      case 'lead': return leadBlock(parts.lead)
      case 'icp_profile': return profileLine(parts.profile)
      case 'dimensions': return dimensionLines(parts.profile)
      case 'knowledge': return parts.knowledge.length === 0 ? '（无线索挂接资料）' : parts.knowledge
      default: return ''
    }
  })
}
