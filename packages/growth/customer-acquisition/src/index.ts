/**
 * Customer-acquisition operations plugin (GEO + lead ledger + AI lead
 * scoring), P0 foundation: the frozen v1 storage domain, the
 * PermissionContext seam with its bundled local provider, the pre-execute
 * compliance gate enforcing the feed-in red lines, the audit trail, the four
 * P0 model-facing tools, and the browser Remote gateway the panel mounts.
 * @module @deepseek-ai/dsh-customer-acquisition
 */

import type { Context } from '@deepseek-ai/cordis'
import { installComplianceGate } from './compliance.ts'
import { operatorRequest } from './permission/types.ts'
import { LocalPermissionProvider } from './permission/local-provider.ts'
import { CustomerAcquisitionService } from './service.ts'
import { registerAcquisitionTools } from './tools/register.ts'

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
  AuditExportValue, AuditListRequest, AuditListValue, AuditLogValue,
  SettingsPatchInput, SettingsSnapshotValue,
} from './types.ts'

declare module '@deepseek-ai/cordis' {
  interface Context {
    customerAcquisition: CustomerAcquisitionService
  }
}

/** Services required before the plugin body runs. */
export const inject = ['storageDomain', 'tools'] as const

/**
 * Compose the plugin: the local permission provider and the domain service
 * install as services, then a runtime fiber declares both plus `tools` and
 * registers the P0 tools and the compliance gate. Every registration is an
 * effect; the returned disposer unwinds runtime, service, and provider.
 * @param ctx - host context providing storage, tools, and the loader.
 * @returns resolution to the disposer releasing every registration, after
 * the runtime fiber finished its registrations.
 */
export async function apply(ctx: Context): Promise<() => Promise<void>> {
  const permissionFiber = await ctx.plugin(LocalPermissionProvider).await()
  const serviceFiber = await ctx.plugin(CustomerAcquisitionService).await()
  const runtimeFiber = await ctx.plugin({
    name: 'customer-acquisition:runtime',
    inject: ['tools', 'permissionContext', 'customerAcquisition'],
    apply: (runtimeCtx: Context) => {
      const service = runtimeCtx.customerAcquisition
      const permission = runtimeCtx.permissionContext
      const unregisterTools = registerAcquisitionTools(runtimeCtx, service, permission)
      const uninstallGate = installComplianceGate(runtimeCtx, (name, reason, agentId) => {
        // A failed denial audit never un-denies the call; the medium rejected
        // the write, so containment is warn-and-continue.
        void service.recordComplianceDeny(name, reason, operatorRequest('agent', agentId))
          .catch((error: unknown) => { runtimeCtx.logger.warn(`customer-acquisition: denial audit failed: ${String(error)}`) })
      })
      return () => {
        uninstallGate()
        unregisterTools()
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
