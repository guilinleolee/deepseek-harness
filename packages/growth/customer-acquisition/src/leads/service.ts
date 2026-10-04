/**
 * The lead-ledger service (module 2): every lead, follow-up, and attached
 * document read and write behind the PermissionContext seam. One authority
 * for the model-facing tools and the future panel Remote face — ownership
 * filtering is enforced here on every call, never left to the UI. Every
 * mutating action appends one audit record; reads never audit (data
 * contract §2.5). The domain handle is owned by the P0
 * `CustomerAcquisitionService` (a domain opens once); this service borrows
 * it and the audit table, so it owns no lifecycle of its own.
 * @module @deepseek-ai/dsh-customer-acquisition/leads/service
 */

import type { Domain, KvTable } from '@deepseek-ai/dsh-storage-domain'
import { appendAuditRecord, type AuditTable } from '../audit.ts'
import {
  DocumentId, FollowupId, LeadId, ScoreRunId, UserId, newId,
} from '../domain/ids.ts'
import {
  customerAcquisitionDomainSpec,
  leadDocumentSchema,
  leadFollowupSchema,
  leadSchema,
  type Lead,
  type LeadDocument,
  type LeadFollowup,
} from '../domain/spec.ts'
import type { PromptCompletion } from '../llm/oneshot.ts'
import type { OperatorChannel, ResolvedOperator } from '../permission/types.ts'
import { frameExtractPrompt, parseExtractOutput, EXTRACT_MAX_CHARS, type ExtractOutput } from './extract.ts'
import { toLeadDetail, toDocumentValue, toFollowupValue } from './project.ts'
import type {
  DocumentValue, FollowupValue, IntentLevel, LeadCreateInput,
  LeadDetailValue, LeadListRequest, LeadUpdateInput,
} from './types.ts'

/** Storage cap on one attached document body (frozen schema `max(20_000)`). */
export const DOCUMENT_MAX_CHARS = 20_000

/** Clamp helper: offset floors at 0, limit ranges 1-100 (tools manifest §2). */
function pagingOf(request: { limit?: number | undefined; offset?: number | undefined }): { offset: number; limit: number } {
  return {
    offset: Math.max(request.offset ?? 0, 0),
    limit: Math.min(Math.max(request.limit ?? 20, 1), 100),
  }
}

/** Reject empty/whitespace-only strings for a required or explicitly passed field. */
function requireNonEmpty(value: string | undefined, label: string): string | undefined {
  if (value === undefined) return undefined
  if (value.trim().length === 0) throw new Error(`${label}不能为空`)
  return value
}

/** Validate one caller-supplied epoch-millisecond field. */
function requireEpochMs(value: number | undefined, label: string): number | undefined {
  if (value === undefined) return undefined
  if (!Number.isInteger(value) || value < 0) throw new Error(`${label}必须是合法的 epoch 毫秒整数`)
  return value
}

/** Validate one tags array: entries non-empty, no duplicates (frozen schema refine). */
function requireTags(tags: string[] | undefined): string[] | undefined {
  if (tags === undefined) return undefined
  if (tags.some(tag => tag.trim().length === 0)) throw new Error('标签不能为空字符串')
  if (new Set(tags).size !== tags.length) throw new Error(`标签存在重复：${tags.join('、')}`)
  return tags
}

/** Copy only the defined fields of a patch so omitted fields never clobber stored values. */
function definedFields<T extends object>(patch: T): Partial<T> {
  return Object.fromEntries(Object.entries(patch).filter(([, value]) => value !== undefined)) as Partial<T>
}

/**
 * Storage-backed lead ledger. All reads are synchronous from memory; every
 * write is durable-first and audited with the caller's already-resolved
 * operator.
 */
export class LeadLedgerService {
  private readonly domain: Domain<typeof customerAcquisitionDomainSpec>
  private readonly leads: KvTable<LeadId, Lead>
  private readonly followups: KvTable<FollowupId, LeadFollowup>
  private readonly documents: KvTable<DocumentId, LeadDocument>

  /**
   * @param domain - the opened customer-acquisition domain (borrowed).
   * @param audit - the audit-log table handle.
   */
  constructor(
    domain: Domain<typeof customerAcquisitionDomainSpec>,
    private readonly audit: AuditTable,
  ) {
    this.domain = domain
    this.leads = domain.table('leads')
    this.followups = domain.table('lead_followups')
    this.documents = domain.table('lead_documents')
  }

  /** One lead by id, readable by the operator; a miss or an out-of-scope read fails friendly. */
  getLead(leadId: string, operator: ResolvedOperator): Lead {
    return this.requireReadable(this.leads.get(LeadId(leadId)), leadId, operator)
  }

  /**
   * Whether one lead may appear in the operator's views — existence plus the
   * read-scope rule. Used by cross-cutting reads (scoring history) that
   * filter without surfacing per-lead errors.
   * @param leadId - the lead to test.
   * @param operator - the caller's resolved operator.
   * @returns whether the lead exists and is readable by the operator.
   */
  isLeadVisible(leadId: string, operator: ResolvedOperator): boolean {
    const lead = this.leads.get(LeadId(leadId))
    if (lead === undefined) return false
    return operator.capabilities.lead_scope === 'all'
      || lead.owner_id === undefined
      || lead.owner_id === operator.userId
  }

  /**
   * Create a lead. The owner defaults to the operator; `lead_scope=own`
   * operators may not name another owner. Durably stored, then audited.
   * @param input - the create fields (`company_name` required).
   * @param operator - the caller's resolved operator.
   * @param channel - which surface performed the write.
   * @returns the stored lead.
   */
  async createLead(input: LeadCreateInput, operator: ResolvedOperator, channel: OperatorChannel): Promise<Lead> {
    const companyName = input.company_name
    if (companyName === undefined || companyName.trim().length === 0) throw new Error('公司名称不能为空')
    const source = requireNonEmpty(input.source, '线索来源') ?? 'manual'
    const tags = requireTags(input.tags) ?? []
    const nextFollowupAt = requireEpochMs(input.next_followup_at, '下次跟进时间')
    let ownerId = operator.userId
    if (input.owner_id !== undefined) {
      if (input.owner_id.trim().length === 0) throw new Error('归属人 id 不能为空；省略该参数即归属当前操作者')
      ownerId = UserId(input.owner_id)
      if (operator.capabilities.lead_scope !== 'all' && ownerId !== operator.userId) {
        throw new Error('当前操作者只能把新线索归属设置为自己（lead_scope=own）')
      }
    }
    const now = Date.now()
    const lead = leadSchema.parse({
      id: newId<LeadId>(),
      owner_id: ownerId,
      source,
      company_name: companyName,
      contact_name: input.contact_name,
      phone: input.phone,
      email: input.email,
      industry: input.industry,
      company_size: input.company_size,
      demand_desc: input.demand_desc,
      budget_range: input.budget_range,
      decision_role: input.decision_role,
      tags,
      ...(input.opportunity_stage === undefined ? {} : { opportunity_stage: input.opportunity_stage }),
      ...(nextFollowupAt === undefined ? {} : { next_followup_at: nextFollowupAt }),
      created_at: now,
      updated_at: now,
    })
    await this.leads.put(lead.id, lead)
    await appendAuditRecord(this.audit, {
      action: 'lead.create',
      object_type: 'lead',
      object_id: lead.id,
      summary: `创建线索：${lead.company_name}（来源 ${lead.source}）`,
    }, operator, channel)
    return lead
  }

  /**
   * Update the editable fields of one lead; omitted fields keep their value,
   * `tags` is whole-value replacement. `source` and `intent_level` are not
   * editable here (录入事实 / 打分回填). Recycled leads must be restored first.
   * @param leadId - the lead to update.
   * @param patch - the fields to change.
   * @param operator - the caller's resolved operator.
   * @param channel - which surface performed the write.
   * @returns the stored lead after the write.
   */
  async updateLead(
    leadId: string,
    patch: LeadUpdateInput,
    operator: ResolvedOperator,
    channel: OperatorChannel,
  ): Promise<Lead> {
    const lead = this.requireWritableLead(leadId, operator)
    if (lead.status === 'recycled') throw new Error('回收站中的线索不可编辑，请先恢复（restore）')
    const changes = definedFields(patch)
    if (changes.company_name !== undefined && changes.company_name.trim().length === 0) {
      throw new Error('公司名称不能为空')
    }
    requireTags(changes.tags)
    requireEpochMs(changes.next_followup_at, '下次跟进时间')
    const keys = Object.keys(changes)
    if (keys.length === 0) return lead
    const next = leadSchema.parse({
      ...lead,
      ...changes,
      updated_at: Math.max(Date.now(), lead.created_at),
    })
    await this.leads.put(next.id, next)
    await appendAuditRecord(this.audit, {
      action: 'lead.update',
      object_type: 'lead',
      object_id: next.id,
      summary: `更新线索：${next.company_name}（${keys.join('、')}）`,
    }, operator, channel)
    return next
  }

  /**
   * Lead detail: the ref plus long text, the most recent follow-ups, and
   * attached document references (projection in `project.ts`).
   * @param leadId - the lead to read.
   * @param operator - the caller's resolved operator.
   * @returns the detail envelope.
   */
  getLeadDetail(leadId: string, operator: ResolvedOperator): LeadDetailValue {
    const lead = this.getLead(leadId, operator)
    return toLeadDetail(
      lead,
      this.followupsByLead(lead.id).map(([, followup]) => followup),
      this.documentsByLead(lead.id).map(([, document]) => document),
    )
  }

  /**
   * Filter, sort, and page leads. `lead_scope=own` always clamps the result
   * to the operator's own leads plus the pool, whatever `owner` asked for.
   * @param request - filters plus paging bounds.
   * @param operator - the caller's resolved operator.
   * @returns the matching page, newest first, with the unfiltered total.
   */
  listLeads(request: LeadListRequest, operator: ResolvedOperator): { items: Lead[]; total: number } {
    const filtered = this.filterLeads(request, operator)
    const { offset, limit } = pagingOf(request)
    return { items: filtered.slice(offset, offset + limit), total: filtered.length }
  }

  /**
   * All leads matching the filter, unpaged — the export face. Scope rules
   * apply exactly as in {@link listLeads}; the export itself is a
   * first-class audited action (manifest `lead.export`).
   * @param request - filters without paging bounds.
   * @param operator - the caller's resolved operator.
   * @param channel - which surface performed the export.
   * @returns every matching lead, newest first.
   */
  async exportLeads(
    request: Omit<LeadListRequest, 'limit' | 'offset'>,
    operator: ResolvedOperator,
    channel: OperatorChannel,
  ): Promise<Lead[]> {
    const leads = this.filterLeads(request, operator)
    await appendAuditRecord(this.audit, {
      action: 'lead.export',
      object_type: 'lead',
      summary: `导出线索 ${leads.length} 条`,
    }, operator, channel)
    return leads
  }

  /**
   * Soft-delete: move the lead into the recycle bin (`status='recycled'`).
   * @param leadId - the lead to delete.
   * @param operator - the caller's resolved operator.
   * @param channel - which surface performed the write.
   * @returns the stored lead after the write.
   */
  async deleteLead(leadId: string, operator: ResolvedOperator, channel: OperatorChannel): Promise<Lead> {
    const lead = this.getLead(leadId, operator)
    this.requireDeletable(lead, operator)
    if (lead.status === 'recycled') throw new Error(`线索已在回收站中：${lead.company_name}`)
    const next = leadSchema.parse({
      ...lead,
      status: 'recycled',
      updated_at: Math.max(Date.now(), lead.created_at),
    })
    await this.leads.put(next.id, next)
    await appendAuditRecord(this.audit, {
      action: 'lead.delete',
      object_type: 'lead',
      object_id: next.id,
      summary: `线索移入回收站：${next.company_name}`,
    }, operator, channel)
    return next
  }

  /**
   * Restore one recycled lead to `active`.
   * @param leadId - the lead to restore.
   * @param operator - the caller's resolved operator.
   * @param channel - which surface performed the write.
   * @returns the stored lead after the write.
   */
  async restoreLead(leadId: string, operator: ResolvedOperator, channel: OperatorChannel): Promise<Lead> {
    const lead = this.getLead(leadId, operator)
    this.requireDeletable(lead, operator)
    if (lead.status !== 'recycled') throw new Error(`线索不在回收站中：${lead.company_name}`)
    const next = leadSchema.parse({
      ...lead,
      status: 'active',
      updated_at: Math.max(Date.now(), lead.created_at),
    })
    await this.leads.put(next.id, next)
    await appendAuditRecord(this.audit, {
      action: 'lead.restore',
      object_type: 'lead',
      object_id: next.id,
      summary: `线索从回收站恢复：${next.company_name}`,
    }, operator, channel)
    return next
  }

  /**
   * Physically delete one recycled lead and every associated record:
   * follow-ups, documents, score runs and items, generated contents, and SOP
   * tasks. Irreversible; recycled status is required first.
   * @param leadId - the lead to purge.
   * @param operator - the caller's resolved operator.
   * @param channel - which surface performed the write.
   * @returns the number of records removed including the lead itself.
   */
  async purgeLead(leadId: string, operator: ResolvedOperator, channel: OperatorChannel): Promise<number> {
    const lead = this.getLead(leadId, operator)
    if (!operator.capabilities.can_delete_any_lead) {
      throw new Error('物理删除线索需要全局删除权限（can_delete_any_lead）')
    }
    if (lead.status !== 'recycled') {
      throw new Error(`仅回收站中的线索可物理删除，请先移入回收站：${lead.company_name}`)
    }
    let removed = 1
    for (const [id] of this.followupsByLead(lead.id)) {
      await this.followups.delete(id)
      removed += 1
    }
    for (const [id] of this.documentsByLead(lead.id)) {
      await this.documents.delete(id)
      removed += 1
    }
    const runIds: ScoreRunId[] = []
    for (const [id, run] of this.domain.table('score_runs').entries()) {
      if (run.lead_id === lead.id) runIds.push(id)
    }
    for (const [id, item] of this.domain.table('score_run_items').entries()) {
      if (runIds.includes(item.run_id)) {
        await this.domain.table('score_run_items').delete(id)
        removed += 1
      }
    }
    for (const runId of runIds) {
      await this.domain.table('score_runs').delete(runId)
      removed += 1
    }
    for (const [id, content] of this.domain.table('generated_contents').entries()) {
      if (content.lead_id === lead.id) {
        await this.domain.table('generated_contents').delete(id)
        removed += 1
      }
    }
    for (const [id, task] of this.domain.table('sop_tasks').entries()) {
      if (task.lead_id === lead.id) {
        await this.domain.table('sop_tasks').delete(id)
        removed += 1
      }
    }
    await this.leads.delete(lead.id)
    await appendAuditRecord(this.audit, {
      action: 'lead.purge',
      object_type: 'lead',
      object_id: lead.id,
      summary: `物理删除线索：${lead.company_name}（含 ${removed - 1} 条关联记录）`,
    }, operator, channel)
    return removed
  }

  /**
   * Assign one pool lead (no owner) to an operator. A lead that already has
   * an owner is rejected — use transfer. `lead_scope=own` operators may only
   * claim for themselves.
   * @param leadId - the pool lead.
   * @param ownerId - the target owner id.
   * @param operator - the caller's resolved operator.
   * @param channel - which surface performed the write.
   * @returns the stored lead after the write.
   */
  async assignLead(
    leadId: string,
    ownerId: string,
    operator: ResolvedOperator,
    channel: OperatorChannel,
  ): Promise<Lead> {
    const lead = this.getLead(leadId, operator)
    if (ownerId.trim().length === 0) throw new Error('目标归属人 id 不能为空')
    if (lead.owner_id !== undefined) {
      throw new Error(`线索已有归属人，不能重复分配，请改用 transfer：${lead.company_name}`)
    }
    const target = UserId(ownerId)
    if (operator.capabilities.lead_scope !== 'all' && target !== operator.userId) {
      throw new Error('当前操作者只能把公海线索分配给自己（lead_scope=own）')
    }
    const next = leadSchema.parse({
      ...lead,
      owner_id: target,
      updated_at: Math.max(Date.now(), lead.created_at),
    })
    await this.leads.put(next.id, next)
    await appendAuditRecord(this.audit, {
      action: 'lead.assign',
      object_type: 'lead',
      object_id: next.id,
      summary: `公海线索分配给 ${ownerId}：${next.company_name}`,
    }, operator, channel)
    return next
  }

  /**
   * Transfer one lead's ownership; omitting the target owner releases the
   * lead back to the pool. `lead_scope=own` operators may only transfer
   * leads they own.
   * @param leadId - the lead to transfer.
   * @param ownerId - the target owner id; absent = release to the pool.
   * @param operator - the caller's resolved operator.
   * @param channel - which surface performed the write.
   * @returns the stored lead after the write.
   */
  async transferLead(
    leadId: string,
    ownerId: string | undefined,
    operator: ResolvedOperator,
    channel: OperatorChannel,
  ): Promise<Lead> {
    const lead = this.getLead(leadId, operator)
    if (operator.capabilities.lead_scope !== 'all' && lead.owner_id !== operator.userId) {
      throw new Error('当前操作者只能转移自己名下的线索（lead_scope=own）')
    }
    let target: UserId | undefined
    if (ownerId !== undefined) {
      if (ownerId.trim().length === 0) throw new Error('目标归属人 id 不能为空；省略该参数即释放到公海')
      target = UserId(ownerId)
    }
    const next = leadSchema.parse({
      ...lead,
      owner_id: target,
      updated_at: Math.max(Date.now(), lead.created_at),
    })
    await this.leads.put(next.id, next)
    await appendAuditRecord(this.audit, {
      action: 'lead.transfer',
      object_type: 'lead',
      object_id: next.id,
      summary: `线索转移：${next.company_name} → ${ownerId ?? '公海'}`,
    }, operator, channel)
    return next
  }

  /**
   * Attach one plain-text document to a lead for scoring and copy-generation
   * context injection. The body is capped at the frozen 20 000-char bound.
   * @param leadId - the lead to attach to.
   * @param title - the document title.
   * @param content - the document body.
   * @param operator - the caller's resolved operator.
   * @param channel - which surface performed the write.
   * @returns the stored document.
   */
  async addDocument(
    leadId: string,
    title: string,
    content: string,
    operator: ResolvedOperator,
    channel: OperatorChannel,
  ): Promise<LeadDocument> {
    const lead = this.requireWritableLead(leadId, operator)
    if (title.trim().length === 0) throw new Error('资料标题不能为空')
    if (content.trim().length === 0) throw new Error('资料内容不能为空')
    if (content.length > DOCUMENT_MAX_CHARS) {
      throw new Error(`挂接资料超出上限：${content.length}/${DOCUMENT_MAX_CHARS} 字符`)
    }
    const now = Date.now()
    const document = leadDocumentSchema.parse({
      id: newId<DocumentId>(),
      lead_id: lead.id,
      title,
      content,
      created_at: now,
      updated_at: now,
    })
    await this.documents.put(document.id, document)
    await appendAuditRecord(this.audit, {
      action: 'lead.document.add',
      object_type: 'document',
      object_id: document.id,
      summary: `挂接资料「${title}」（${content.length} 字符）：${lead.company_name}`,
    }, operator, channel)
    return document
  }

  /**
   * Remove one attached document (physical delete of the document record).
   * @param documentId - the document to remove.
   * @param operator - the caller's resolved operator.
   * @param channel - which surface performed the write.
   * @returns resolution after the record is removed.
   */
  async removeDocument(
    documentId: string,
    operator: ResolvedOperator,
    channel: OperatorChannel,
  ): Promise<void> {
    const document = this.documents.get(DocumentId(documentId))
    if (document === undefined) throw new Error(`挂接资料不存在：${documentId}`)
    const lead = this.leads.get(document.lead_id)
    if (lead === undefined) throw new Error(`挂接资料所属线索不存在：${document.lead_id}`)
    this.requireWritableLead(lead.id, operator)
    await this.documents.delete(document.id)
    await appendAuditRecord(this.audit, {
      action: 'lead.document.remove',
      object_type: 'document',
      object_id: document.id,
      summary: `移除资料「${document.title}」：${lead.company_name}`,
    }, operator, channel)
  }

  /**
   * List one lead's attached documents.
   * @param leadId - the lead to read.
   * @param operator - the caller's resolved operator.
   * @param includeContent - whether bodies ride along.
   * @returns the document rows, oldest first.
   */
  listDocuments(leadId: string, operator: ResolvedOperator, includeContent: boolean): DocumentValue[] {
    const lead = this.getLead(leadId, operator)
    return [...this.documentsByLead(lead.id)].map(([, document]) => toDocumentValue(document, includeContent))
  }

  /**
   * One lead's attached documents as stored records — the scoring flow's
   * knowledge-injection source.
   * @param leadId - the lead to read.
   * @param operator - the caller's resolved operator.
   * @returns the stored documents, oldest first.
   */
  getLeadDocuments(leadId: string, operator: ResolvedOperator): LeadDocument[] {
    const lead = this.getLead(leadId, operator)
    return [...this.documentsByLead(lead.id)].map(([, document]) => document)
  }

  /**
   * Append one follow-up note to a lead.
   * @param leadId - the lead to append to.
   * @param content - the note body.
   * @param operator - the caller's resolved operator.
   * @param channel - which surface performed the write.
   * @returns the stored follow-up.
   */
  async addFollowup(
    leadId: string,
    content: string,
    operator: ResolvedOperator,
    channel: OperatorChannel,
  ): Promise<LeadFollowup> {
    const lead = this.requireWritableLead(leadId, operator)
    if (content.trim().length === 0) throw new Error('跟进记录内容不能为空')
    const followup = leadFollowupSchema.parse({
      id: newId<FollowupId>(),
      lead_id: lead.id,
      content,
      created_at: Date.now(),
    })
    await this.followups.put(followup.id, followup)
    await appendAuditRecord(this.audit, {
      action: 'lead.followup.add',
      object_type: 'followup',
      object_id: followup.id,
      summary: `新增跟进记录：${lead.company_name}`,
    }, operator, channel)
    return followup
  }

  /**
   * Page one lead's follow-up notes, newest first.
   * @param leadId - the lead to read.
   * @param operator - the caller's resolved operator.
   * @param limit - page size (1-100, default 20).
   * @param offset - page offset (default 0).
   * @returns the matching page with the unfiltered total.
   */
  listFollowups(
    leadId: string,
    operator: ResolvedOperator,
    limit?: number,
    offset?: number,
  ): { items: FollowupValue[]; total: number } {
    const lead = this.getLead(leadId, operator)
    const all = this.followupsByLead(lead.id)
      .map(([, followup]) => followup)
      .sort((left, right) => right.created_at - left.created_at)
    const page = pagingOf({ limit, offset })
    return {
      items: all.slice(page.offset, page.offset + page.limit).map(followup => toFollowupValue(followup)),
      total: all.length,
    }
  }

  /**
   * Extract lead fields from user-provided text (form snippet, chat log,
   * email body). Only this call's text is parsed — no network access, no
   * batch collection (red lines 1-2). The result is returned, never stored;
   * the caller confirms with `lead.create`.
   * @param input - the user-provided text and optional source hint.
   * @param completion - the prompt-completion port backing the extraction.
   * @param operator - the caller's resolved operator.
   * @param channel - which surface performed the action.
   * @returns the recognized fields and notes.
   */
  async extractLeadFields(
    input: { text: string; sourceHint?: string },
    completion: PromptCompletion,
    operator: ResolvedOperator,
    channel: OperatorChannel,
  ): Promise<ExtractOutput> {
    const text = input.text
    if (text.trim().length === 0) throw new Error('请提供要抽取的原始文本')
    if (text.length > EXTRACT_MAX_CHARS) {
      throw new Error(`文本超出上限：${text.length}/${EXTRACT_MAX_CHARS} 字符`)
    }
    const output = parseExtractOutput(await completion.complete(frameExtractPrompt(text, input.sourceHint)))
    const recognized = Object.values(output.fields).filter(value => value !== undefined).length
    await appendAuditRecord(this.audit, {
      action: 'lead.extract',
      object_type: 'lead',
      summary: `抽取线索字段：${output.fields.company_name ?? '未识别公司'}（识别 ${recognized}/9 个字段）`,
    }, operator, channel)
    return output
  }

  /**
   * Write one scoring outcome back to the lead's `intent_level`. Audited by
   * the caller's `score.run`/`score.batch` entry, not again here.
   * @param leadId - the scored lead.
   * @param intent - the new intent level.
   * @returns the stored lead after the write.
   */
  async applyIntent(leadId: string, intent: IntentLevel): Promise<Lead> {
    const lead = this.leads.get(LeadId(leadId))
    if (lead === undefined) throw new Error(`线索不存在：${leadId}`)
    const next = leadSchema.parse({
      ...lead,
      intent_level: intent,
      updated_at: Math.max(Date.now(), lead.created_at),
    })
    await this.leads.put(next.id, next)
    return next
  }

  /** Read one lead with the read-scope check; a miss fails with the id in the message. */
  private requireReadable(lead: Lead | undefined, leadId: string, operator: ResolvedOperator): Lead {
    if (lead === undefined) throw new Error(`线索不存在：${leadId}`)
    if (operator.capabilities.lead_scope !== 'all'
      && lead.owner_id !== undefined
      && lead.owner_id !== operator.userId) {
      throw new Error('当前操作者无权访问该线索（仅可访问自己名下与公海线索）')
    }
    return lead
  }

  /** Resolve one lead for a write, enforcing the write-scope rules on the way. */
  private requireWritableLead(leadId: string, operator: ResolvedOperator): Lead {
    const lead = this.getLead(leadId, operator)
    if (operator.capabilities.lead_scope === 'all' || lead.owner_id === operator.userId) return lead
    // The read gate above already rejects other operators' leads, so the only
    // reachable write failure here is a pool lead.
    throw new Error('当前操作者无权修改公海线索，请先领取（assign 给自己）')
  }

  /** Delete/restore permission: own leads freely; others and pool need the global cap. */
  private requireDeletable(lead: Lead, operator: ResolvedOperator): void {
    if (lead.owner_id === operator.userId) return
    if (operator.capabilities.can_delete_any_lead) return
    throw new Error('删除他人或公海线索需要全局删除权限（can_delete_any_lead）')
  }

  /** The full sorted filtered lead array behind both the list and the export face. */
  private filterLeads(request: LeadListRequest, operator: ResolvedOperator): Lead[] {
    const needle = request.q?.trim().toLowerCase()
    const ownerFilter = request.owner ?? 'all'
    const status = request.status ?? 'active'
    const matched = [...this.leads.entries()]
      .filter(([, lead]) => {
        if (operator.capabilities.lead_scope !== 'all'
          && lead.owner_id !== undefined
          && lead.owner_id !== operator.userId) return false
        if (ownerFilter === 'me' && lead.owner_id !== operator.userId) return false
        if (ownerFilter === 'pool' && lead.owner_id !== undefined) return false
        if (lead.status !== status) return false
        if (request.source !== undefined && lead.source !== request.source) return false
        if (request.industry !== undefined && lead.industry !== request.industry) return false
        if (request.intent_level !== undefined && lead.intent_level !== request.intent_level) return false
        if (request.tag !== undefined && !lead.tags.includes(request.tag)) return false
        if (needle !== undefined && needle.length > 0) {
          const contact = lead.contact_name ?? ''
          if (!lead.company_name.toLowerCase().includes(needle) && !contact.toLowerCase().includes(needle)) return false
        }
        if (request.created_from !== undefined && lead.created_at < request.created_from) return false
        if (request.created_to !== undefined && lead.created_at > request.created_to) return false
        return true
      })
      .map(([, lead]) => lead)
    return matched.sort((left, right) => right.created_at - left.created_at)
  }

  /** One lead's follow-ups in insertion order. */
  private followupsByLead(leadId: string): [FollowupId, LeadFollowup][] {
    return [...this.followups.entries()].filter(([, followup]) => followup.lead_id === leadId)
  }

  /** One lead's documents in insertion order. */
  private documentsByLead(leadId: string): [DocumentId, LeadDocument][] {
    return [...this.documents.entries()].filter(([, document]) => document.lead_id === leadId)
  }
}
