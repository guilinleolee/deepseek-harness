/**
 * The follow-up SOP service (module 5): generates per-lead task lists from an
 * SOP template matched by the lead's intent level, tracks task state, and
 * manages the SOP templates. Todo linkage rides on the platform fact that DSH
 * todos are the agent's own `todo_write` checklist (no writable service):
 * generation returns a ready-to-forward todo list whenever the settings flag
 * is on, and `todo_written` stays false.
 * @module @deepseek-ai/dsh-customer-acquisition/sop/service
 */

import type { Domain, KvTable } from '@deepseek-ai/dsh-storage-domain'
import { appendAuditRecord, type AuditTable } from '../audit.ts'
import { SopTaskId, SopTemplateId, newId } from '../domain/ids.ts'
import {
  customerAcquisitionDomainSpec,
  sopTemplateSchema,
  sopTaskSchema,
  type Lead,
  type SopTemplate,
  type SopTask,
} from '../domain/spec.ts'
import type { LeadLedgerService } from '../leads/service.ts'
import type { OperatorChannel, ResolvedOperator } from '../permission/types.ts'

/** The day in milliseconds; cadence offsets (`D+N`) resolve against it. */
const DAY_MS = 86_400_000

/** Clamp helper: offset floors at 0, limit ranges 1-100. */
function pagingOf(request: { limit?: number | undefined; offset?: number | undefined }): { offset: number; limit: number } {
  return {
    offset: Math.max(request.offset ?? 0, 0),
    limit: Math.min(Math.max(request.limit ?? 20, 1), 100),
  }
}

/** Strip `undefined` fields so an omitted patch key never clobbers the stored value. */
function definedFields<T extends object>(patch: T): Partial<T> {
  return Object.fromEntries(Object.entries(patch).filter(([, value]) => value !== undefined)) as Partial<T>
}

/** Construction dependencies of the SOP service. */
export interface SopServiceDeps {
  /** The opened customer-acquisition domain (borrowed from the P0 service). */
  readonly domain: Domain<typeof customerAcquisitionDomainSpec>
  /** The audit-log table handle. */
  readonly audit: AuditTable
  /** The lead ledger the SOP flows read leads and write tasks against. */
  readonly ledger: LeadLedgerService
}

/** One generated follow-up task before wire projection. */
export interface SopTaskOutcome {
  task: SopTask
  todoWritten: boolean
}

/** One generate call's full outcome. */
export interface SopGenerateOutcome {
  intentLevel: NonNullable<Lead['intent_level']>
  templateId: SopTemplateId
  tasks: SopTaskOutcome[]
  leadName: string
  /** Ready to forward through `todo_write` when the settings flag is on. */
  todoList: { content: string; status: 'pending' }[]
  todoWriteEnabled: boolean
}

/**
 * Storage-backed SOP service. The domain handle is borrowed from the P0
 * service (a domain opens once); this service owns no lifecycle.
 */
export class SopService {
  private readonly sopTemplates: KvTable<SopTemplateId, SopTemplate>
  private readonly sopTasks: KvTable<SopTaskId, SopTask>

  /** @param deps - borrowed domain and audit handle, and the lead ledger. */
  constructor(private readonly deps: SopServiceDeps) {
    this.sopTemplates = deps.domain.table('sop_templates')
    this.sopTasks = deps.domain.table('sop_tasks')
  }

  /**
   * Generate one lead's follow-up task list: resolve the SOP template
   * (explicit id → industry → industry-absent → any enabled), take the rule
   * for the lead's intent level (unscored leads are refused — score first),
   * and persist one task per follow-up point with `D+N` cadence scheduling.
   * @param input - the lead plus an optional explicit SOP template id.
   * @param operator - the caller's resolved operator.
   * @param channel - which surface performed the action.
   * @returns the persisted tasks, the intent level, and the todo-forwarding list.
   */
  async generateTasks(
    input: { lead_id: string; sop_template_id?: string },
    operator: ResolvedOperator,
    channel: OperatorChannel,
  ): Promise<SopGenerateOutcome> {
    const lead = this.deps.ledger.getLead(input.lead_id, operator)
    assertSopScope(lead, operator)
    if (lead.intent_level === undefined) {
      throw new Error(`线索尚未打分（无意向等级），请先用 score_one 打分：${lead.company_name}`)
    }
    const template = this.resolveTemplate(input.sop_template_id, lead)
    const rule = template.rules.find(candidate => candidate.intent_level === lead.intent_level)
    if (rule === undefined) {
      throw new Error(`SOP 模板「${template.name}」缺少 ${lead.intent_level} 等级的规则，请先补充该等级的跟进规则`)
    }
    const offsets = cadenceOffsets(rule.cadence)
    const now = Date.now()
    const tasks: SopTaskOutcome[] = []
    for (const [index, point] of rule.points.entries()) {
      const offset = offsets[Math.min(index, offsets.length - 1)] ?? 0
      const task = sopTaskSchema.parse({
        id: newId<SopTaskId>(),
        lead_id: lead.id,
        title: point,
        status: 'pending',
        planned_at: now + offset * DAY_MS,
        note: [
          rule.questions.length === 0 ? undefined : `提问清单：${rule.questions.join('；')}`,
          rule.risks.length === 0 ? undefined : `风险提示：${rule.risks.join('；')}`,
        ].filter(part => part !== undefined).join('\n') || undefined,
        created_at: now,
        updated_at: now,
      })
      await this.sopTasks.put(task.id, task)
      tasks.push({ task, todoWritten: false })
    }
    const todoWriteEnabled = this.deps.domain.global.get().sop_todo_write_enabled
    await appendAuditRecord(this.deps.audit, {
      action: 'sop.tasks.generate',
      object_type: 'sop_task',
      summary: `生成跟进任务 ${tasks.length} 条（${lead.intent_level}）：${lead.company_name}`,
    }, operator, channel)
    return {
      intentLevel: lead.intent_level,
      templateId: template.id,
      tasks,
      leadName: lead.company_name,
      todoList: tasks.map(({ task }) => ({ content: `${task.title}（${lead.company_name}）`, status: 'pending' as const })),
      todoWriteEnabled,
    }
  }

  /**
   * List SOP tasks: filter by lead and status, order by planned time ascending.
   * @param request - optional lead/status filters plus paging bounds.
   * @param operator - the caller's resolved operator.
   * @returns the matching page with the unfiltered total.
   */
  listTasks(
    request: { lead_id?: string; status?: 'pending' | 'done' | 'deferred' | 'dropped'; limit?: number; offset?: number },
    operator: ResolvedOperator,
  ): { items: SopTask[]; total: number } {
    const all = [...this.sopTasks.entries()]
      .map(([, task]) => task)
      .filter(task => this.deps.ledger.isLeadVisible(task.lead_id, operator)
        && (request.lead_id === undefined || task.lead_id === request.lead_id)
        && (request.status === undefined || task.status === request.status))
      .sort((left, right) => left.planned_at - right.planned_at)
    const page = pagingOf(request)
    return { items: all.slice(page.offset, page.offset + page.limit), total: all.length }
  }

  /**
   * Flow one task's state (pending/done/deferred/dropped), optionally
   * rescheduling it or appending a note.
   * @param taskId - the task to update.
   * @param patch - status, planned_at, and/or note.
   * @param operator - the caller's resolved operator.
   * @param channel - which surface performed the write.
   * @returns the stored task after the write.
   */
  async updateTask(
    taskId: string,
    patch: { status?: 'pending' | 'done' | 'deferred' | 'dropped'; planned_at?: number; note?: string },
    operator: ResolvedOperator,
    channel: OperatorChannel,
  ): Promise<SopTask> {
    const task = this.requireTask(taskId)
    const lead = this.deps.ledger.getLead(task.lead_id, operator)
    if (operator.capabilities.lead_scope !== 'all' && lead.owner_id !== operator.userId) {
      throw new Error('当前操作者无权流转他人线索的 SOP 任务')
    }
    const changes = definedFields(patch)
    if (changes.planned_at !== undefined && (!Number.isInteger(changes.planned_at) || changes.planned_at < 0)) {
      throw new Error('计划时间必须是合法的 epoch 毫秒整数')
    }
    const keys = Object.keys(changes)
    if (keys.length === 0) return task
    const next = sopTaskSchema.parse({
      ...task,
      ...changes,
      updated_at: Math.max(Date.now(), task.created_at),
    })
    await this.sopTasks.put(next.id, next)
    await appendAuditRecord(this.deps.audit, {
      action: 'sop.task.update',
      object_type: 'sop_task',
      object_id: next.id,
      summary: `SOP 任务流转：${next.title} → ${next.status}（${lead.company_name}）`,
    }, operator, channel)
    return next
  }

  /**
   * Create one SOP template: one rule per intent level (contract §3.9).
   * @param input - name, optional industry, rules, enabled flag.
   * @param operator - the caller's resolved operator.
   * @param channel - which surface performed the write.
   * @returns the stored template.
   */
  async createTemplate(
    input: {
      name: string
      industry?: string
      rules: SopTemplate['rules']
      enabled?: boolean
    },
    operator: ResolvedOperator,
    channel: OperatorChannel,
  ): Promise<SopTemplate> {
    this.requireTemplateManager(operator, '创建 SOP 模板')
    if (input.name.trim().length === 0) throw new Error('模板名称不能为空')
    const now = Date.now()
    const template = sopTemplateSchema.parse({
      id: newId<SopTemplateId>(),
      name: input.name,
      ...(input.industry === undefined ? {} : { industry: input.industry }),
      rules: input.rules,
      enabled: input.enabled ?? true,
      created_at: now,
      updated_at: now,
    })
    await this.sopTemplates.put(template.id, template)
    await appendAuditRecord(this.deps.audit, {
      action: 'sop_template.create',
      object_type: 'sop_template',
      object_id: template.id,
      summary: `新建 SOP 模板：${template.name}（${template.rules.length} 条规则）`,
    }, operator, channel)
    return template
  }

  /**
   * Update one SOP template; `rules` is whole-list replacement.
   * @param templateId - the template to update.
   * @param patch - the fields to change.
   * @param operator - the caller's resolved operator.
   * @param channel - which surface performed the write.
   * @returns the stored template after the write.
   */
  async updateTemplate(
    templateId: string,
    patch: { name?: string; industry?: string; rules?: SopTemplate['rules']; enabled?: boolean },
    operator: ResolvedOperator,
    channel: OperatorChannel,
  ): Promise<SopTemplate> {
    this.requireTemplateManager(operator, '修改 SOP 模板')
    const template = this.requireTemplate(templateId)
    if (patch.name !== undefined && patch.name.trim().length === 0) throw new Error('模板名称不能为空')
    const changes = definedFields(patch)
    const keys = Object.keys(changes)
    if (keys.length === 0) return template
    const next = sopTemplateSchema.parse({
      ...template,
      ...changes,
      updated_at: Math.max(Date.now(), template.created_at),
    })
    await this.sopTemplates.put(next.id, next)
    await appendAuditRecord(this.deps.audit, {
      action: 'sop_template.update',
      object_type: 'sop_template',
      object_id: next.id,
      summary: `修改 SOP 模板：${next.name}（${keys.join('、')}）`,
    }, operator, channel)
    return next
  }

  /**
   * List SOP templates, optionally enabled-only.
   * @param enabledOnly - when true, only enabled templates return.
   * @returns the templates, oldest first.
   */
  listTemplates(enabledOnly?: boolean): SopTemplate[] {
    return [...this.sopTemplates.entries()]
      .map(([, template]) => template)
      .filter(template => enabledOnly !== true || template.enabled)
      .sort((left, right) => left.created_at - right.created_at)
  }

  /**
   * Delete one SOP template. The frozen sop_tasks schema carries no template
   * reference, so deletion has no referential guard; generated tasks stay.
   * @param templateId - the template to delete.
   * @param operator - the caller's resolved operator.
   * @param channel - which surface performed the write.
   * @returns resolution after the record is removed.
   */
  async deleteTemplate(
    templateId: string,
    operator: ResolvedOperator,
    channel: OperatorChannel,
  ): Promise<void> {
    this.requireTemplateManager(operator, '删除 SOP 模板')
    const template = this.requireTemplate(templateId)
    await this.sopTemplates.delete(template.id)
    await appendAuditRecord(this.deps.audit, {
      action: 'sop_template.delete',
      object_type: 'sop_template',
      object_id: template.id,
      summary: `删除 SOP 模板：${template.name}`,
    }, operator, channel)
  }

  /** Resolve one task by id or fail friendly. */
  private requireTask(taskId: string): SopTask {
    const task = this.sopTasks.get(SopTaskId(taskId))
    if (task === undefined) throw new Error(`SOP 任务不存在：${taskId}`)
    return task
  }

  /** Resolve one template by id or fail friendly. */
  private requireTemplate(templateId: string): SopTemplate {
    const template = this.sopTemplates.get(SopTemplateId(templateId))
    if (template === undefined) throw new Error(`SOP 模板不存在：${templateId}`)
    return template
  }

  /**
   * The generate-time template chain: explicit id → industry →
   * industry-absent → any enabled.
   */
  private resolveTemplate(explicitId: string | undefined, lead: Lead): SopTemplate {
    if (explicitId !== undefined) {
      const explicit = this.sopTemplates.get(SopTemplateId(explicitId))
      if (explicit === undefined) throw new Error(`SOP 模板不存在：${explicitId}`)
      return explicit
    }
    const enabled = [...this.sopTemplates.entries()]
      .map(([, template]) => template)
      .filter(template => template.enabled)
      .sort((left, right) => left.created_at - right.created_at)
    const industryMatch = lead.industry === undefined
      ? undefined
      : enabled.find(template => template.industry === lead.industry)
    const fallback = industryMatch ?? enabled.find(template => template.industry === undefined)
    if (fallback !== undefined) return fallback
    const first = enabled[0]
    if (first === undefined) throw new Error('没有启用中的 SOP 模板，请先创建或启用一套（sop_template_create）')
    return first
  }

  /** Global-template management gate for every template write. */
  private requireTemplateManager(operator: ResolvedOperator, action: string): void {
    if (!operator.capabilities.can_manage_global_templates) {
      throw new Error(`当前操作者没有${action}的权限（can_manage_global_templates）`)
    }
  }
}

/**
 * SOP generation writes the lead's task list, so it is a lead write:
 * `lead_scope=own` operators may only generate for leads they own — a pool
 * lead must be claimed first.
 * @param lead - the lead about to receive follow-up tasks.
 * @param operator - the caller's resolved operator.
 */
export function assertSopScope(lead: Lead, operator: ResolvedOperator): void {
  if (operator.capabilities.lead_scope !== 'all' && lead.owner_id !== operator.userId) {
    throw new Error(lead.owner_id === undefined
      ? `公海线索需先领取（assign 给自己）再生成跟进任务：${lead.company_name}`
      : `当前操作者无权为他人线索生成跟进任务：${lead.company_name}`)
  }
}

/**
 * Extract the `D+N` day offsets from a cadence string, ascending.
 * @param cadence - the rule's cadence text (e.g. `D+0 微信问候，D+3 到店`).
 * @returns the offsets in order of appearance.
 */
export function cadenceOffsets(cadence: string): number[] {
  return [...cadence.matchAll(/D\+(\d+)/g)].map(match => Number(match[1]))
}
