/**
 * Customer-acquisition operations plugin (GEO + lead ledger + AI lead
 * scoring + nurture copy + follow-up SOP + data dashboard), P0 foundation
 * through the P4 dashboard: the frozen v1 storage domain, the
 * PermissionContext seam with its bundled local provider, the pre-execute
 * compliance gate enforcing the feed-in red lines, the audit trail, the
 * model-facing tools for every module, the preset industry seeds, and the
 * browser Remote gateway the panel mounts.
 * @module @deepseek-ai/dsh-customer-acquisition
 */

import type { Context } from '@deepseek-ai/cordis'
import { installComplianceGate } from './compliance.ts'
import { LeadLedgerService } from './leads/service.ts'
import { resolveAiPolicy, type AiPolicyConfig } from './llm/oneshot.ts'
import { operatorRequest } from './permission/types.ts'
import { LocalPermissionProvider } from './permission/local-provider.ts'
import { CustomerAcquisitionService } from './service.ts'
import { LeadScoringService } from './scoring/service.ts'
import { NurtureContentService } from './content/service.ts'
import { SopService } from './sop/service.ts'
import { registerAcquisitionTools } from './tools/register.ts'
import { registerP1Tools } from './tools/register-p1.ts'
import { registerP3Tools } from './tools/register-p3.ts'
import { registerP4Tools } from './tools/register-p4.ts'
import { ReportService } from './report/service.ts'
import { seedIndustryTemplates } from './scoring/seed.ts'

export { customerAcquisitionDomainSpec } from './domain/spec.ts'
export {
  auditLogSchema, auditSourceSchema, contentTemplateSchema, contentVariantSchema,
  customerAcquisitionSettingsSchema, decisionRoleSchema, geoArtifactsSchema,
  geoFindingSchema, geoReportSchema, geoScanSchema, geoScanStatusSchema,
  geoSeveritySchema, icpDimensionSchema, icpProfileSchema, intentLevelSchema,
  leadDocumentSchema, leadFollowupSchema, leadSchema, leadStatusSchema,
  opportunityStageSchema, scoreRunItemSchema, scoreRunSchema, scoreTemplateSchema,
  sopRuleSchema, sopTaskSchema, sopTaskStatusSchema, sopTemplateSchema,
} from './domain/spec.ts'
export type {
  AuditLog, ContentTemplate, ContentTemplateVariable, CustomerAcquisitionSettings,
  GeoArtifacts, GeoFinding, GeoReport, GeoScan, IcpDimension, IcpProfile, Lead,
  LeadDocument, LeadFollowup, ScoreRun, ScoreRunItem, ScoreTemplate, SopRule,
  SopTask, SopTemplate,
} from './domain/spec.ts'
export { newId } from './domain/ids.ts'
export type {
  AuditLogId, ContentTemplateId, DocumentId, FollowupId, GeneratedContentId,
  GeoReportId, GeoScanId, IcpProfileId, LeadId, ScoreRunId, ScoreRunItemId,
  ScoreTemplateId, SopTaskId, SopTemplateId, UserId,
} from './domain/ids.ts'
export { KNOWN_COMPANY_SIZES, KNOWN_CONTENT_TYPES, KNOWN_LEAD_SOURCES } from './domain/vocab.ts'
export {
  FULL_CAPABILITIES, PermissionContextService, operatorRequest,
} from './permission/types.ts'
export type {
  OperatorCapabilities, OperatorChannel, OperatorRequest, ResolvedOperator,
} from './permission/types.ts'
export { DEFAULT_USER_DISPLAY_NAME, DEFAULT_USER_ID, LocalPermissionProvider } from './permission/local-provider.ts'
export {
  GEO_FETCH_CONCURRENCY, GEO_MAX_PAGES_HARD_LIMIT, GEO_PAGE_TIMEOUT_MS_HARD_LIMIT,
  GEO_RESPONSE_MAX_BYTES, SCORE_BATCH_HARD_LIMIT, inspectToolCall, installComplianceGate,
} from './compliance.ts'
export type { ComplianceVerdict } from './compliance.ts'
export { appendAuditRecord, selectAuditRecords } from './audit.ts'
export type { AuditEntryInput, AuditTable } from './audit.ts'
export { CustomerAcquisitionService } from './service.ts'
export { registerAcquisitionTools } from './tools/register.ts'
export { auditExportTool, auditListTool, renderAuditExport } from './tools/audit.ts'
export { settingsGetTool, settingsSetTool } from './tools/settings.ts'
export type {
  AuditExportValue, AuditListRequest, AuditListValue, AuditLogValue, GeoScanListValue,
  GeoScanRowValue, SettingsPatchInput, SettingsSnapshotValue,
} from './types.ts'
export { LeadLedgerService, DOCUMENT_MAX_CHARS } from './leads/service.ts'
export { registerP1Tools, P1_TOOL_NAMES } from './tools/register-p1.ts'
export { registerP3Tools, P3_TOOL_NAMES } from './tools/register-p3.ts'
export { registerP4Tools, P4_TOOL_NAMES } from './tools/register-p4.ts'
export { ReportService } from './report/service.ts'
export { reportOverviewTool, renderOverviewMd } from './tools/report.ts'
export type { ReportToolDeps } from './tools/report.ts'
export type {
  GeoStats, IntentDistribution, OverviewBreakdownGroup, OverviewGroupBy,
  OverviewPeriod, OverviewRequest, OverviewTotals, OverviewValue,
  ScoreDistribution, TaskStats,
} from './report/types.ts'
export type { LeadToolDeps } from './tools/leads.ts'
export type { ScoringToolDeps } from './tools/scoring.ts'
export type {
  DecisionRole, DocumentListValue, DocumentRefValue, DocumentValue, ExtractedLeadFields,
  FollowupValue, IntentLevel, LeadCreateInput, LeadDetailValue, LeadExportValue, LeadListRequest,
  LeadListValue, LeadMutationValue, LeadOwnerValue, LeadPurgeValue, LeadRefValue, LeadStatusValue,
  LeadStatus, LeadUpdateInput, OpportunityStage,
} from './leads/types.ts'
export { EXTRACT_MAX_CHARS, EXTRACT_SYSTEM_PROMPT, frameExtractPrompt, parseExtractOutput } from './leads/extract.ts'
export type { ExtractOutput } from './leads/extract.ts'
export { LEAD_EXPORT_COLUMNS, renderLeadExport } from './leads/export.ts'
export { toDocumentRef, toDocumentValue, toFollowupValue, toLeadDetail, toLeadRef } from './leads/project.ts'
export { LeadScoringService, SCORE_BATCH_LIMIT, toIcpProfileRef, toScoreTemplateRef } from './scoring/service.ts'
export { NurtureContentService, CONTENT_SYSTEM_PROMPT, assertCopyScope } from './content/service.ts'
export { SopService, assertSopScope, cadenceOffsets } from './sop/service.ts'
export type { LeadScoringDeps, ScoreOutcome } from './scoring/service.ts'
export type {
  IcpCreateInput, IcpDimensionInput, IcpDimensionValue, IcpListValue, IcpProfileRefValue,
  IcpProfileValue, IcpUpdateInput, ScoreBatchEntryValue, ScoreBatchFailedValue, ScoreBatchInput,
  ScoreBatchValue, ScoreHistoryEntryValue, ScoreHistoryItemValue, ScoreHistoryRequest,
  ScoreHistoryRunValue, ScoreHistoryValue, ScoreItemValue, ScoreOneInput, ScoreOneValue,
  ScoreRunValue, ScoreTemplateCreateInput, ScoreTemplateListValue, ScoreTemplateRefValue,
  ScoreTemplateUpdateInput, ScoreTemplateValue,
} from './scoring/types.ts'
export {
  INTENT_LABELS, SCORE_INTENT_HIGH_MIN, SCORE_INTENT_LOW_MIN, SCORE_INTENT_MID_MIN,
  SCORE_SYSTEM_PROMPT, intentTagFor, parseScoreOutput,
} from './scoring/evaluate.ts'
export { aggregateKnowledge, KNOWLEDGE_INJECT_MAX_CHARS, KNOWLEDGE_TRUNCATED_MARK, renderScorePrompt } from './scoring/prompt.ts'
export { SEED_IDS, seedIndustryTemplates } from './scoring/seed.ts'
export {
  AI_TIMEOUT_CODE, llmPromptCompletion, resolveAiPolicy,
} from './llm/oneshot.ts'
export type { AiPolicyConfig, PromptCompletion, ResolvedAiPolicy } from './llm/oneshot.ts'

/** Bundle-row config of the plugin (`config:` on the `customer-acquisition` row). */
export interface CustomerAcquisitionPluginConfig {
  /** Policy for the plugin's internal model calls (lead extraction, AI scoring). */
  readonly ai?: AiPolicyConfig
}

/**
 * The compliance gate's denial auditor: best-effort audit with
 * warn-and-continue — a failed denial audit never un-denies the call, the
 * medium rejected the write, so containment only warns.
 * @param service - the customer-acquisition service owning the audit table.
 * @param runtimeCtx - the fiber context whose logger carries the warning.
 * @returns the `onDeny` callback for {@link installComplianceGate}.
 */
export function complianceDenyAuditor(
  service: CustomerAcquisitionService,
  runtimeCtx: Context,
): (name: string, reason: string, agentId?: string) => void {
  return (name, reason, agentId) => {
    void service.recordComplianceDeny(name, reason, operatorRequest('agent', agentId))
      .catch((error: unknown) => { runtimeCtx.logger.warn(`customer-acquisition: denial audit failed: ${String(error)}`) })
  }
}

declare module '@deepseek-ai/cordis' {
  interface Context {
    customerAcquisition: CustomerAcquisitionService
  }
}

/** Services required before the plugin body runs. */
export const inject = ['storageDomain', 'tools']

/**
 * Compose the plugin: the local permission provider and the domain service
 * install as services, then a runtime fiber declares both plus `tools` and
 * `llm`, seeds the preset industry templates, and registers the P0 tools,
 * the P1 lead/scoring tools, and the compliance gate. Every registration is
 * an effect; the returned disposer unwinds runtime, service, and provider.
 * @param ctx - host context providing storage, tools, and the loader.
 * @param config - bundle-row config; `ai` tunes the internal model calls.
 * @returns resolution to the disposer releasing every registration, after
 * the runtime fiber finished its registrations.
 */
export async function apply(
  ctx: Context,
  config?: CustomerAcquisitionPluginConfig,
): Promise<() => Promise<void>> {
  const policy = resolveAiPolicy(config?.ai)
  const permissionFiber = await ctx.plugin(LocalPermissionProvider).await()
  const serviceFiber = await ctx.plugin(CustomerAcquisitionService).await()
  const runtimeFiber = await ctx.plugin({
    name: 'customer-acquisition:runtime',
    inject: ['tools', 'permissionContext', 'customerAcquisition', 'llm'],
    // Seeding runs inside the fiber so the injected service (never the outer
    // context) provides the domain; the tools register only after the preset
    // industries exist.
    apply: async (runtimeCtx: Context) => {
      const service = runtimeCtx.customerAcquisition
      await seedIndustryTemplates(service.requireDomain())
      const ledger = new LeadLedgerService(service.requireDomain(), service.requireAuditTable())
      const scoring = new LeadScoringService({
        ctx: runtimeCtx,
        domain: service.requireDomain(),
        audit: service.requireAuditTable(),
        ledger,
        policy,
      })
      const content = new NurtureContentService({
        ctx: runtimeCtx,
        domain: service.requireDomain(),
        audit: service.requireAuditTable(),
        ledger,
        policy,
      })
      const sop = new SopService({
        domain: service.requireDomain(),
        audit: service.requireAuditTable(),
        ledger,
      })
      const report = new ReportService(service.requireDomain())
      const unregisterTools = registerAcquisitionTools(runtimeCtx, service, runtimeCtx.permissionContext)
      const unregisterP1Tools = registerP1Tools(runtimeCtx, {
        ledger,
        scoring,
        permission: runtimeCtx.permissionContext,
        policy,
      })
      const unregisterP3Tools = registerP3Tools(runtimeCtx, {
        content,
        sop,
        permission: runtimeCtx.permissionContext,
        policy,
      })
      const unregisterP4Tools = registerP4Tools(runtimeCtx, {
        report,
        permission: runtimeCtx.permissionContext,
      })
      const uninstallGate = installComplianceGate(runtimeCtx, complianceDenyAuditor(service, runtimeCtx))
      return () => {
        uninstallGate()
        unregisterTools()
        unregisterP1Tools()
        unregisterP3Tools()
        unregisterP4Tools()
      }
    },
  }).await()
  return async () => {
    await runtimeFiber.dispose()
    await serviceFiber.dispose()
    await permissionFiber.dispose()
  }
}

export default apply
