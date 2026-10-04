/**
 * Lead export rendering (tools manifest §5 `lead_export`): one Markdown
 * table or one formula-injection-guarded CSV document per call. Text only —
 * the plugin has no send channel (red line 3). Timestamps render as epoch
 * milliseconds, matching the audit export convention.
 * @module @deepseek-ai/dsh-customer-acquisition/leads/export
 */

import type { Lead } from '../domain/spec.ts'

/** Export columns, in presentation order. */
export const LEAD_EXPORT_COLUMNS = [
  'id', 'company_name', 'contact_name', 'phone', 'email', 'source', 'industry',
  'company_size', 'demand_desc', 'budget_range', 'decision_role', 'intent_level',
  'opportunity_stage', 'status', 'owner_id', 'tags', 'next_followup_at',
  'created_at', 'updated_at',
] as const

/** One lead projected to the export row, cells in {@link LEAD_EXPORT_COLUMNS} order. */
function exportRow(lead: Lead): string[] {
  const cells: Record<(typeof LEAD_EXPORT_COLUMNS)[number], string> = {
    id: lead.id,
    company_name: lead.company_name,
    contact_name: lead.contact_name ?? '',
    phone: lead.phone ?? '',
    email: lead.email ?? '',
    source: lead.source,
    industry: lead.industry ?? '',
    company_size: lead.company_size ?? '',
    demand_desc: lead.demand_desc ?? '',
    budget_range: lead.budget_range ?? '',
    decision_role: lead.decision_role ?? '',
    intent_level: lead.intent_level ?? '',
    opportunity_stage: lead.opportunity_stage,
    status: lead.status,
    owner_id: lead.owner_id ?? '',
    tags: lead.tags.join(';'),
    next_followup_at: lead.next_followup_at === undefined ? '' : String(lead.next_followup_at),
    created_at: String(lead.created_at),
    updated_at: String(lead.updated_at),
  }
  return LEAD_EXPORT_COLUMNS.map(column => cells[column])
}

/**
 * Guard one CSV cell against formula injection: a leading formula trigger
 * character is neutralized with a single quote, then the cell is quoted and
 * inner quotes doubled.
 * @param cell - raw cell text.
 * @returns the safe quoted cell.
 */
function guardedCell(cell: string): string {
  const neutralized = /^[=+\-@\t]/.test(cell) ? `'${cell}` : cell
  return `"${neutralized.replaceAll('"', '""')}"`
}

/**
 * Render leads as a Markdown table or a guarded CSV document.
 * @param format - the requested format.
 * @param leads - the leads in presentation order.
 * @returns the full export document text.
 */
export function renderLeadExport(format: 'markdown' | 'csv', leads: readonly Lead[]): string {
  const rows = leads.map(exportRow)
  if (format === 'csv') {
    return [LEAD_EXPORT_COLUMNS.join(','), ...rows.map(row => row.map(guardedCell).join(','))].join('\n')
  }
  const line = (cells: readonly string[]): string => `| ${cells.join(' | ')} |`
  return [
    line([...LEAD_EXPORT_COLUMNS]),
    line(LEAD_EXPORT_COLUMNS.map(() => '---')),
    ...rows.map(row => line(row.map(value => value.replaceAll('|', '\\|')))),
  ].join('\n')
}
