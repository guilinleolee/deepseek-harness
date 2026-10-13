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
import { IcpProfileId, ScoreTemplateId } from './domain/ids.ts'
import {
  customerAcquisitionDomainSpec,
  customerAcquisitionSettingsSchema,
  type AuditLog,
  type CustomerAcquisitionSettings,
} from './domain/spec.ts'
import { DEFAULT_USER_DISPLAY_NAME, DEFAULT_USER_ID } from './permission/local-provider.ts'
import { FULL_CAPABILITIES } from './permission/types.ts'
import type { OperatorChannel, OperatorRequest, ResolvedOperator } from './permission/types.ts'
import type {
  AuditListRequest, AuditListValue, AuditLogValue, SettingsPatchInput,
  SettingsSnapshotValue, SettingsValue,
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

  /** Authoritative audit handle, valid after init; a miss is a broken lifecycle. */
  requireAuditTable(): AuditTable {
    if (this.auditTable === undefined) {
      throw new Error('customer-acquisition: durable domain is not initialized')
    }
    return this.auditTable
  }

  /** Authoritative domain, valid after init; a miss is a broken lifecycle. */
  private requireDomain(): Domain<typeof customerAcquisitionDomainSpec> {
    if (this.domain === undefined) {
      throw new Error('customer-acquisition: durable domain is not initialized')
    }
    return this.domain
  }

  /** Current settings, projected to the exact-optional wire shape. */
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

  /** Read face for the browser panel. */
  @Remote('getSettings')
  getSettingsRemote(): Promise<SettingsSnapshotValue> {
    return Promise.resolve({ settings: this.getSettings() })
  }

  /** Write face for the browser panel; resolves the web operator per call. */
  @Remote('updateSettings')
  async updateSettingsRemote(patch: SettingsPatchInput): Promise<SettingsSnapshotValue> {
    const operator = await this.ctx.permissionContext.resolve({ via: 'web' })
    const settings = await this.updateSettings(patch, operator, 'web')
    return { settings }
  }

  /** Audit read face for the browser panel. */
  @Remote('listAuditLogs')
  async listAuditLogs(request: AuditListRequest): Promise<AuditListValue> {
    await this.ctx.permissionContext.resolve({ via: 'web' })
    return this.listAudit(request)
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
  }
}

export default CustomerAcquisitionService
