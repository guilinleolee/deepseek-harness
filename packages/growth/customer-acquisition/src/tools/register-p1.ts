/**
 * Registration of the P1 model-facing tools (modules 2 and 3) on the runtime
 * fiber. Kept as a pure function of its dependencies so tests can drive the
 * tools without the plugin composition; the P0 tools register separately in
 * `tools/register.ts`.
 * @module @deepseek-ai/dsh-customer-acquisition/tools/register-p1
 */

import type { Context } from '@deepseek-ai/cordis'
import { EXTRACT_SYSTEM_PROMPT } from '../leads/extract.ts'
import type { LeadLedgerService } from '../leads/service.ts'
import { llmPromptCompletion } from '../llm/oneshot.ts'
import type { ResolvedAiPolicy } from '../llm/oneshot.ts'
import type { LeadScoringService } from '../scoring/service.ts'
import type { PermissionContextService } from '../permission/types.ts'
import {
  leadAssignTool,
  leadCreateTool,
  leadDeleteTool,
  leadDocumentAddTool,
  leadDocumentListTool,
  leadDocumentRemoveTool,
  leadExportTool,
  leadExtractTool,
  leadFollowupAddTool,
  leadFollowupListTool,
  leadGetTool,
  leadListTool,
  leadPurgeTool,
  leadRestoreTool,
  leadTransferTool,
  leadUpdateTool,
} from './leads.ts'
import {
  icpCreateTool,
  icpDeleteTool,
  icpListTool,
  icpUpdateTool,
  scoreBatchTool,
  scoreHistoryTool,
  scoreOneTool,
  scoreTemplateCreateTool,
  scoreTemplateDeleteTool,
  scoreTemplateListTool,
  scoreTemplateUpdateTool,
} from './scoring.ts'

/** Tool dependencies: the two module services plus the permission seam and AI policy. */
export interface P1ToolDeps {
  readonly ledger: LeadLedgerService
  readonly scoring: LeadScoringService
  readonly permission: PermissionContextService
  readonly policy: ResolvedAiPolicy
}

/** Every P1 tool name, in registration order. */
export const P1_TOOL_NAMES = [
  'customer_acquisition_lead_create',
  'customer_acquisition_lead_update',
  'customer_acquisition_lead_get',
  'customer_acquisition_lead_list',
  'customer_acquisition_lead_delete',
  'customer_acquisition_lead_restore',
  'customer_acquisition_lead_purge',
  'customer_acquisition_lead_assign',
  'customer_acquisition_lead_transfer',
  'customer_acquisition_lead_extract',
  'customer_acquisition_lead_export',
  'customer_acquisition_lead_document_add',
  'customer_acquisition_lead_document_list',
  'customer_acquisition_lead_document_remove',
  'customer_acquisition_lead_followup_add',
  'customer_acquisition_lead_followup_list',
  'customer_acquisition_score_one',
  'customer_acquisition_score_batch',
  'customer_acquisition_score_history',
  'customer_acquisition_icp_create',
  'customer_acquisition_icp_update',
  'customer_acquisition_icp_list',
  'customer_acquisition_icp_delete',
  'customer_acquisition_score_template_create',
  'customer_acquisition_score_template_update',
  'customer_acquisition_score_template_list',
  'customer_acquisition_score_template_delete',
] as const

/**
 * Register the P1 tools (16 lead-ledger + 11 scoring).
 * @param ctx - the runtime fiber's context carrying `ctx.tools` and `ctx.llm`.
 * @param deps - ledger, scoring, permission, and the AI policy.
 * @returns the combined disposer of every registration.
 */
export function registerP1Tools(ctx: Context, deps: P1ToolDeps): () => void {
  const leadDeps = {
    ledger: deps.ledger,
    permission: deps.permission,
    completion: llmPromptCompletion(ctx, deps.policy, EXTRACT_SYSTEM_PROMPT),
  }
  const scoringDeps = { scoring: deps.scoring, permission: deps.permission }
  const disposers = [
    ctx.tools.register(leadCreateTool(leadDeps)),
    ctx.tools.register(leadUpdateTool(leadDeps)),
    ctx.tools.register(leadGetTool(leadDeps)),
    ctx.tools.register(leadListTool(leadDeps)),
    ctx.tools.register(leadDeleteTool(leadDeps)),
    ctx.tools.register(leadRestoreTool(leadDeps)),
    ctx.tools.register(leadPurgeTool(leadDeps)),
    ctx.tools.register(leadAssignTool(leadDeps)),
    ctx.tools.register(leadTransferTool(leadDeps)),
    ctx.tools.register(leadExtractTool(leadDeps)),
    ctx.tools.register(leadExportTool(leadDeps)),
    ctx.tools.register(leadDocumentAddTool(leadDeps)),
    ctx.tools.register(leadDocumentListTool(leadDeps)),
    ctx.tools.register(leadDocumentRemoveTool(leadDeps)),
    ctx.tools.register(leadFollowupAddTool(leadDeps)),
    ctx.tools.register(leadFollowupListTool(leadDeps)),
    ctx.tools.register(scoreOneTool(scoringDeps)),
    ctx.tools.register(scoreBatchTool(scoringDeps)),
    ctx.tools.register(scoreHistoryTool(scoringDeps)),
    ctx.tools.register(icpCreateTool(scoringDeps)),
    ctx.tools.register(icpUpdateTool(scoringDeps)),
    ctx.tools.register(icpListTool(scoringDeps)),
    ctx.tools.register(icpDeleteTool(scoringDeps)),
    ctx.tools.register(scoreTemplateCreateTool(scoringDeps)),
    ctx.tools.register(scoreTemplateUpdateTool(scoringDeps)),
    ctx.tools.register(scoreTemplateListTool(scoringDeps)),
    ctx.tools.register(scoreTemplateDeleteTool(scoringDeps)),
  ]
  return () => { for (const dispose of disposers) dispose() }
}
