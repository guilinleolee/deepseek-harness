/**
 * The customer-acquisition service: owns the domain's lifetime, serves the
 * browser Remote face (settings + audit log), and exposes the same reads and
 * writes to the model-facing tools. One authority for both surfaces; the
 * PermissionContext seam resolves the operator per call.
 * @module @deepseek-ai/dsh-customer-acquisition/service
 */

import type { Context } from '@deepseek-ai/cordis'
import { Service } from '@deepseek-ai/cordis'
import type { Domain } from '@deepseek-ai/dsh-storage-domain'
import { TypertRemoteService, Remote } from '@deepseek-ai/dsh-typert-protocol'
import { appendAuditRecord, selectAuditRecords, type AuditTable } from './audit.ts'
import { NurtureContentService } from './content/service.ts'
import { IcpProfileId, ScoreTemplateId } from './domain/ids.ts'
import {
  customerAcquisitionDomainSpec,
  customerAcquisitionSettingsSchema,
  type AuditLog,
  type CustomerAcquisitionSettings,
  type GeneratedContent,
  type GeoReport,
  type ScoreRun,
  type SopTask,
} from './domain/spec.ts'
import { LeadLedgerService } from './leads/service.ts'
import { toLeadRef } from './leads/project.ts'
import { DEFAULT_USER_DISPLAY_NAME, DEFAULT_USER_ID } from './permission/local-provider.ts'
import { FULL_CAPABILITIES } from './permission/types.ts'
import type { OperatorChannel, OperatorRequest, ResolvedOperator } from './permission/types.ts'
import { resolveAiPolicy } from './llm/oneshot.ts'
import { ReportService } from './report/service.ts'
import { LeadScoringService } from './scoring/service.ts'
import { SopService } from './sop/service.ts'
import type {
  AuditListRequest, AuditListValue, AuditLogValue, ContentTemplate, GeoScanListValue,
  GeoScanRowValue, IcpProfileValue, LeadListRequest, LeadListValue, OverviewRequest,
  OverviewValue, ScoreTemplateValue, SettingsPatchInput, SettingsSnapshotValue,
  SettingsValue, SopTemplate,
} from './types.ts'

/**
 * Storage-backed customer-acquisition service. The domain opens once at
 * service init and closes with the owning fiber; every read is synchronous
 * from memory, every write durable-first.
 */
export class CustomerAcquisitionService extends TypertRemoteService {
  static inject = ['storageDomain', 'permissionContext'] as const

  private domain: Domain<typeof customerAcquisitionDomainSpec> | undefined
  private auditTable: AuditTable | undefined

  /**
   * @param ctx - Host context providing storage, permissions, and the Remote registry.
   */
  constructor(ctx: Context) {
    super(ctx, 'customerAcquisition')
  }

  /** Open the frozen v1 domain and bind its lifetime to this fiber. */
  protected async [Service.init](): Promise<void> {
    const domain = await this.ctx.storageDomain.open(customerAcquisitionDomainSpec)
    this.ctx.effect(() => async () => {
      this.domain = undefined
      this.auditTable = undefined
      await domain.close()
    }, 'customer-acquisition.domainClose')
    this.domain = domain
    this.auditTable = domain.table('audit_logs')
  }

  /**
   * Authoritative audit handle, valid after init; a miss is a broken lifecycle.
   * @returns the audit log table.
   */
  requireAuditTable(): AuditTable {
    if (this.auditTable === undefined) {
      throw new Error('customer-acquisition: durable domain is not initialized')
    }
    return this.auditTable
  }

  /**
   * Authoritative domain, valid after init; a miss is a broken lifecycle.
   * Open to the P1 module services (lead ledger, scoring), which borrow the
   * domain's tables — the P0 service stays its single owner and closer.
   * @returns the durable customer-acquisition domain.
   */
  requireDomain(): Domain<typeof customerAcquisitionDomainSpec> {
    if (this.domain === undefined) {
      throw new Error('customer-acquisition: durable domain is not initialized')
    }
    return this.domain
  }

  /**
   * Current settings, projected to the exact-optional wire shape.
   * @returns the stored settings as the wire value.
   */
  getSettings(): SettingsValue {
    return toSettingsValue(this.requireDomain().global.get())
  }

  /**
   * Merge a partial settings update, validate referenced templates exist,
   * persist, and audit. Referencing an unknown profile or template fails
   * loud with a friendly error instead of storing a dangling id.
   * @param patch - fields to change; omitted fields keep their value.
   * @param operator - the caller's resolved operator.
   * @param channel - which surface performed the write.
   * @returns the settings after the write.
   */
  async updateSettings(
    patch: SettingsPatchInput,
    operator: ResolvedOperator,
    channel: OperatorChannel,
  ): Promise<SettingsValue> {
    const domain = this.requireDomain()
    const changes = definedFields(patch)
    if (changes.default_icp_profile_id !== undefined
      && domain.table('icp_profiles').get(IcpProfileId(changes.default_icp_profile_id)) === undefined) {
      throw new Error(`默认 ICP 画像不存在：${changes.default_icp_profile_id}`)
    }
    if (changes.default_score_template_id !== undefined
      && domain.table('score_templates').get(ScoreTemplateId(changes.default_score_template_id)) === undefined) {
      throw new Error(`默认打分模板不存在：${changes.default_score_template_id}`)
    }
    const next = customerAcquisitionSettingsSchema.parse({ ...domain.global.get(), ...changes })
    await domain.global.set(next)
    await appendAuditRecord(this.requireAuditTable(), {
      action: 'settings.update',
      object_type: 'settings',
      summary: `更新全局参数：${Object.keys(changes).join('、') || '无变更'}`,
    }, operator, channel)
    return toSettingsValue(next)
  }

  /**
   * Filter the audit log for list and export faces.
   * @param request - filters plus paging bounds.
   * @returns the matching page, newest first, with the unfiltered total.
   */
  listAudit(request: AuditListRequest): AuditListValue {
    const records = selectAuditRecords([...this.requireAuditTable().entries()].map(([, record]) => record), request)
    const offset = request.offset ?? 0
    const limit = request.limit ?? 20
    return { items: records.map(toAuditValue).slice(offset, offset + limit), total: records.length }
  }

  /**
   * All audit records matching the filter, unpaged — the export face.
   * @param filter - filters without paging bounds.
   * @returns every matching record, newest first.
   */
  exportAudit(filter: Omit<AuditListRequest, 'limit' | 'offset'>): AuditListValue['items'] {
    return selectAuditRecords([...this.requireAuditTable().entries()].map(([, record]) => record), filter)
      .map(toAuditValue)
  }

  /**
   * Read face for the browser panel.
   * @returns the settings snapshot wire value.
   */
  @Remote('getSettings')
  getSettingsRemote(): Promise<SettingsSnapshotValue> {
    return Promise.resolve({ settings: this.getSettings() })
  }

  /**
   * Write face for the browser panel; resolves the web operator per call.
   * @param patch - partial settings update.
   * @returns the settings snapshot after the write.
   */
  @Remote('updateSettings')
  async updateSettingsRemote(patch: SettingsPatchInput): Promise<SettingsSnapshotValue> {
    const operator = await this.ctx.permissionContext.resolve({ via: 'web' })
    const settings = await this.updateSettings(patch, operator, 'web')
    return { settings }
  }

  /**
   * Audit read face for the browser panel.
   * @param request - list window and filters.
   * @returns the audit log page.
   */
  @Remote('listAuditLogs')
  async listAuditLogs(request: AuditListRequest): Promise<AuditListValue> {
    await this.ctx.permissionContext.resolve({ via: 'web' })
    return this.listAudit(request)
  }

  /**
   * Dashboard read face: the seven overview metrics through the same
   * aggregation the model tool serves. Resolves the web operator per call so
   * `lead_scope=own` panels never see another operator's leads.
   * @param request - the metric window and grouping.
   * @returns the seven overview metrics.
   */
  @Remote('getOverview')
  async getOverviewRemote(request: OverviewRequest): Promise<OverviewValue> {
    const operator = await this.ctx.permissionContext.resolve({ via: 'web' })
    return new ReportService(this.requireDomain()).overview(request, operator)
  }

  /**
   * Lead list read face; the ledger's list scope applies unchanged.
   * @param request - optional lead-id filter and paging.
   * @returns the visible lead reference page.
   */
  @Remote('listLeads')
  async listLeadsRemote(request?: LeadListRequest): Promise<LeadListValue> {
    const operator = await this.ctx.permissionContext.resolve({ via: 'web' })
    const { items, total } = this.panelStack().ledger.listLeads(request ?? {}, operator)
    return { items: items.map(toLeadRef), total }
  }

  /**
   * Score-run history read face across the operator's visible leads, newest first.
   * @param request - optional lead-id filter and row cap (default 20).
   * @returns the score-run page.
   */
  @Remote('listScoreRuns')
  async listScoreRunsRemote(request?: { lead_id?: string; limit?: number }): Promise<{ items: ScoreRun[]; total: number }> {
    const operator = await this.ctx.permissionContext.resolve({ via: 'web' })
    const { ledger } = this.panelStack()
    const filter = request ?? {}
    const runs = [...this.requireDomain().table('score_runs').entries()]
      .map(([, run]) => run)
      .filter(run => ledger.isLeadVisible(run.lead_id, operator)
        && (filter.lead_id === undefined || run.lead_id === filter.lead_id))
      .sort((left, right) => right.created_at - left.created_at)
    const limit = filter.limit ?? 20
    return { items: runs.slice(0, limit), total: runs.length }
  }

  /**
   * ICP profile read face for the scoring page.
   * @param enabled_only - drop disabled profiles when true.
   * @returns the visible ICP profiles.
   */
  @Remote('listIcpProfiles')
  async listIcpProfilesRemote(enabled_only?: boolean): Promise<IcpProfileValue[]> {
    await this.ctx.permissionContext.resolve({ via: 'web' })
    return this.panelStack().scoring.listIcpProfiles(enabled_only)
  }

  /**
   * Score-template read face for the scoring page.
   * @param enabled_only - drop disabled templates when true.
   * @returns the visible score templates.
   */
  @Remote('listScoreTemplates')
  async listScoreTemplatesRemote(enabled_only?: boolean): Promise<ScoreTemplateValue[]> {
    await this.ctx.permissionContext.resolve({ via: 'web' })
    return this.panelStack().scoring.listScoreTemplates(enabled_only)
  }

  /**
   * GEO scan-history read face: every scan joined with its report's score.
   * @param limit - optional row cap on the returned items.
   * @returns the scan history page.
   */
  @Remote('listGeoScans')
  async listGeoScansRemote(limit?: number): Promise<GeoScanListValue> {
    await this.ctx.permissionContext.resolve({ via: 'web' })
    const domain = this.requireDomain()
    const reportsByScan = new Map<string, GeoReport>()
    for (const [, report] of domain.table('geo_reports').entries()) {
      const current = reportsByScan.get(report.scan_id)
      if (current === undefined || report.created_at > current.created_at) reportsByScan.set(report.scan_id, report)
    }
    const rows: GeoScanRowValue[] = [...domain.table('geo_scans').entries()]
      .map(([, scan]) => {
        const report = reportsByScan.get(scan.id)
        return {
          scan_id: scan.id,
          url: scan.url,
          status: scan.status,
          started_at: scan.started_at,
          ...(scan.finished_at === undefined ? {} : { finished_at: scan.finished_at }),
          ...(report === undefined ? {} : { report_id: report.id, score: report.score }),
        }
      })
      .sort((left, right) => right.started_at - left.started_at)
    const bounded = limit === undefined ? rows : rows.slice(0, limit)
    return { items: bounded, total: rows.length }
  }

  /**
   * One full GEO report for the diagnosis page.
   * @param reportId - the report to load.
   * @returns the stored GEO report.
   */
  @Remote('getGeoReport')
  getGeoReportRemote(reportId: string): Promise<GeoReport> {
    const report = this.requireDomain().table('geo_reports').get(reportId as never)
    if (report === undefined) return Promise.reject(new Error(`GEO 报告不存在：${reportId}`))
    return Promise.resolve(report)
  }

  /**
   * Generated-copy read face across the operator's visible leads, newest first.
   * @param request - optional lead-id filter and row cap (default 20).
   * @returns the generated-content page.
   */
  @Remote('listGeneratedContents')
  async listGeneratedContentsRemote(
    request?: { lead_id?: string; limit?: number },
  ): Promise<{ items: GeneratedContent[]; total: number }> {
    const operator = await this.ctx.permissionContext.resolve({ via: 'web' })
    const { ledger } = this.panelStack()
    const filter = request ?? {}
    const contents = [...this.requireDomain().table('generated_contents').entries()]
      .map(([, content]) => content)
      .filter(content => ledger.isLeadVisible(content.lead_id, operator)
        && (filter.lead_id === undefined || content.lead_id === filter.lead_id))
      .sort((left, right) => right.created_at - left.created_at)
    const limit = filter.limit ?? 20
    return { items: contents.slice(0, limit), total: contents.length }
  }

  /**
   * Copy-template read face for the templates page.
   * @param filters - optional type and enabled-only filters.
   * @returns the matching copy templates.
   */
  @Remote('listContentTemplates')
  async listContentTemplatesRemote(filters?: { type?: string; enabled_only?: boolean }): Promise<ContentTemplate[]> {
    await this.ctx.permissionContext.resolve({ via: 'web' })
    return this.panelStack().content.listTemplates(filters ?? {})
  }

  /**
   * SOP task read face; the service's lead-visibility scope applies unchanged.
   * @param request - optional lead-id, status, and paging filters.
   * @returns the SOP task page.
   */
  @Remote('listSopTasks')
  async listSopTasksRemote(
    request?: { lead_id?: string; status?: 'pending' | 'done' | 'deferred' | 'dropped'; limit?: number; offset?: number },
  ): Promise<{ items: SopTask[]; total: number }> {
    const operator = await this.ctx.permissionContext.resolve({ via: 'web' })
    return this.panelStack().sop.listTasks(request ?? {}, operator)
  }

  /**
   * SOP-template read face for the templates page.
   * @param enabled_only - drop disabled templates when true.
   * @returns the visible SOP templates.
   */
  @Remote('listSopTemplates')
  async listSopTemplatesRemote(enabled_only?: boolean): Promise<SopTemplate[]> {
    await this.ctx.permissionContext.resolve({ via: 'web' })
    return this.panelStack().sop.listTemplates(enabled_only)
  }

  /**
   * Module-service stack behind the panel's read faces. Construction is
   * cheap (plain classes over borrowed tables); every face resolves its
   * operator per call, so nothing user-visible is cached here.
   */
  private panelStack(): {
    ledger: LeadLedgerService
    scoring: LeadScoringService
    content: NurtureContentService
    sop: SopService
  } {
    const domain = this.requireDomain()
    const audit = this.requireAuditTable()
    const ledger = new LeadLedgerService(domain, audit)
    // the panel read faces never call the model; the defaults only satisfy the deps
    const policy = resolveAiPolicy(undefined)
    return {
      ledger,
      scoring: new LeadScoringService({ ctx: this.ctx, domain, audit, ledger, policy }),
      content: new NurtureContentService({ ctx: this.ctx, domain, audit, ledger, policy }),
      sop: new SopService({ domain, audit, ledger }),
    }
  }

  /**
   * Record one compliance denial (red lines 1-3 enforcement, red line 6
   * coverage). The operator resolves best-effort: a denial must be recorded
   * even when the caller carried no agent identity.
   * @param toolName - the denied tool.
   * @param reason - the friendly denial reason.
   * @param request - the operator reference when known.
   * @returns resolution after the audit record is durable.
   */
  async recordComplianceDeny(
    toolName: string,
    reason: string,
    request: OperatorRequest,
  ): Promise<void> {
    const fallback: ResolvedOperator = {
      userId: DEFAULT_USER_ID,
      displayName: DEFAULT_USER_DISPLAY_NAME,
      capabilities: FULL_CAPABILITIES,
    }
    const operator = await this.ctx.permissionContext.resolve(request).catch(() => fallback)
    await appendAuditRecord(this.requireAuditTable(), {
      action: 'compliance.deny',
      object_type: 'tool_call',
      object_id: toolName,
      summary: `合规校验拒绝 ${toolName}：${reason}`,
    }, operator, request.via)
  }
}

/** Copy only the defined fields of the patch so defaults never clobber stored values. */
function definedFields(patch: SettingsPatchInput): SettingsPatchInput {
  return Object.fromEntries(Object.entries(patch).filter(([, value]) => value !== undefined))
}

/** Project one stored record to the plain wire value (brands stay compile-time). */
function toAuditValue(record: AuditLog): AuditLogValue {
  return {
    id: record.id,
    source: record.source,
    operator_user_id: record.operator_user_id,
    action: record.action,
    object_type: record.object_type,
    ...(record.object_id === undefined ? {} : { object_id: record.object_id }),
    summary: record.summary,
    created_at: record.created_at,
  }
}

/** Project the stored settings to the exact-optional wire shape (no explicit undefined). */
function toSettingsValue(settings: CustomerAcquisitionSettings): SettingsValue {
  return {
    geo_max_pages: settings.geo_max_pages,
    geo_page_timeout_ms: settings.geo_page_timeout_ms,
    sop_todo_write_enabled: settings.sop_todo_write_enabled,
    ...(settings.default_icp_profile_id === undefined ? {} : { default_icp_profile_id: settings.default_icp_profile_id }),
    ...(settings.default_score_template_id === undefined ? {} : { default_score_template_id: settings.default_score_template_id }),
    ...(settings.sender_name === undefined ? {} : { sender_name: settings.sender_name }),
  }
}

export default CustomerAcquisitionService
