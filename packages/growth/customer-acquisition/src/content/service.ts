/**
 * The nurture-copy service (module 4): generates channel copy for one lead
 * over the PromptCompletion port, persists every artifact bound to the lead
 * (contract §3.8), and manages the content templates. Red line 3: output is
 * text only — the service has no send channel.
 * @module @deepseek-ai/dsh-customer-acquisition/content/service
 */

import type { Context } from '@deepseek-ai/cordis'
import type { Domain, KvTable } from '@deepseek-ai/dsh-storage-domain'
import { appendAuditRecord, type AuditTable } from '../audit.ts'
import { ContentTemplateId, GeneratedContentId, newId } from '../domain/ids.ts'
import {
  contentTemplateSchema,
  customerAcquisitionDomainSpec,
  generatedContentSchema,
  type ContentTemplate,
  type GeneratedContent,
  type Lead,
} from '../domain/spec.ts'
import { llmPromptCompletion, type PromptCompletion, type ResolvedAiPolicy } from '../llm/oneshot.ts'
import type { LeadLedgerService } from '../leads/service.ts'
import type { OperatorChannel, ResolvedOperator } from '../permission/types.ts'
import { aggregateKnowledge } from '../scoring/prompt.ts'
import { renderVariables } from '../templates/render.ts'

/** Copywriting system prompt shared by every generate call. */
export const CONTENT_SYSTEM_PROMPT = [
  '你是获客培育文案写手。按给定的渠道类型、模板与线索资料写一段可直接使用的中文文案：',
  '口吻自然、有具体行动点、不编造线索资料里没有的事实；模板里的 {{变量}} 全部落位（确实没有值的按落位说明略过）；',
  '发送人身份以线索资料中的 sender_name 为准，不要把收件人当成自己，也不要混用署名；',
  '只输出文案正文，不要解释（渠道要求的标题除外）。',
].join('')

/** Channel semantics fed to the model per type (open vocabulary, known values described). */
const TYPE_GUIDES: Readonly<Record<string, string>> = Object.freeze({
  wecom_first_touch: '企微初次触达话术：两三句话，先给价值再轻量提问，不硬销。',
  sms_followup: '跟进回访短信：70 字以内，一条要点一个行动点。',
  email_drip: '多阶段邮件培育序列：一次生成完整多轮，正文用「## 第 N 轮」分节，每轮一个主题句加正文。',
  short_video_script: '短视频口播脚本：开头 3 秒钩子、正文分镜要点、结尾行动点。',
  xiaohongshu_post: '小红书图文：标题 20 字内带钩子，正文分段口语化，结尾加话题标签。',
  website_product_intro: '官网产品介绍：结构化段落，能力清单加客户收益。',
  customer_case: '客户案例：背景、挑战、方案、结果四段式，数字具体。',
})

/** The channel-guide fallback for unknown open-vocabulary types. */
const DEFAULT_TYPE_GUIDE = '按类型语义写可直接使用的文案。'

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

/**
 * Resolve every variable a copy template may name.
 *
 * Precedence: a real lead field wins; a value the template itself declares
 * (its `variables[].example`) fills the gap; anything still empty stays open
 * and is reported to the model instead of being silently dropped.
 * @param lead - the lead the copy is for.
 * @param senderName - the configured sender identity (global setting).
 * @param template - the resolved template, whose declared examples backstop
 *   variables the lead cannot supply (notably `sender_name`).
 * @returns the variable map handed to the renderer.
 */
function copyVariables(
  lead: Lead,
  senderName: string | undefined,
  template: ContentTemplate | undefined,
): Record<string, string> {
  const fromLead: Record<string, string> = {
    contact_name: lead.contact_name ?? '',
    company_name: lead.company_name,
    industry: lead.industry ?? '',
    company_size: lead.company_size ?? '',
    demand_desc: lead.demand_desc ?? '',
    budget_range: lead.budget_range ?? '',
    sender_name: senderName ?? '',
  }
  const declared: Record<string, string> = {}
  if (template !== undefined) {
    for (const variable of template.variables) {
      if (variable.example !== undefined && variable.example.length > 0) {
        declared[variable.name] = variable.example
      }
    }
  }
  const merged: Record<string, string> = { ...declared }
  for (const [name, value] of Object.entries(fromLead)) {
    if (value.length > 0) merged[name] = value
  }
  return merged
}

/** Construction dependencies of the nurture-copy service. */
export interface NurtureContentDeps {
  /** Host context carrying the `llm` service (used by the default completion). */
  readonly ctx: Context
  /** The opened customer-acquisition domain (borrowed from the P0 service). */
  readonly domain: Domain<typeof customerAcquisitionDomainSpec>
  /** The audit-log table handle. */
  readonly audit: AuditTable
  /** The lead ledger the copy flows read leads and documents through. */
  readonly ledger: LeadLedgerService
  /** The validated AI call policy. */
  readonly policy: ResolvedAiPolicy
  /** Completion factory override; tests inject a deterministic fake. */
  readonly completionFactory?: (system: string) => PromptCompletion
}

/** One persisted generate outcome before wire projection. */
export interface ContentOutcome {
  content: GeneratedContent
  leadName: string
}

/**
 * Storage-backed nurture-copy service. The domain handle is borrowed from the
 * P0 service (a domain opens once); this service owns no lifecycle.
 */
export class NurtureContentService {
  private readonly contentTemplates: KvTable<ContentTemplateId, ContentTemplate>
  private readonly generatedContents: KvTable<GeneratedContentId, GeneratedContent>
  private readonly completionFactory: (system: string) => PromptCompletion

  /** @param deps - host context, borrowed domain and audit handle, ledger, policy, completion factory. */
  constructor(private readonly deps: NurtureContentDeps) {
    this.contentTemplates = deps.domain.table('content_templates')
    this.generatedContents = deps.domain.table('generated_contents')
    this.completionFactory = deps.completionFactory
      ?? (system => llmPromptCompletion(deps.ctx, deps.policy, system))
  }

  /**
   * Generate one nurture copy for a lead: resolve the template (explicit id →
   * type+industry → type → freeform), render it with the lead's fields and
   * knowledge, run one model call, and persist the artifact under the lead.
   * @param input - lead, open-vocabulary type, A/B variant, optional template id.
   * @param operator - the caller's resolved operator.
   * @param channel - which surface performed the action.
   * @param signal - caller cancellation signal for the model call.
   * @returns the persisted artifact and the lead name for the audit trail.
   */
  async generate(
    input: { lead_id: string; type: string; variant: 'A' | 'B'; template_id?: string },
    operator: ResolvedOperator,
    channel: OperatorChannel,
    signal?: AbortSignal,
  ): Promise<ContentOutcome> {
    const lead = this.deps.ledger.getLead(input.lead_id, operator)
    assertCopyScope(lead, operator)
    const type = input.type.trim()
    if (type.length === 0) throw new Error('文案类型（type）不能为空')
    const template = this.resolveTemplate(input.template_id, type, lead)
    const knowledge = aggregateKnowledge(this.deps.ledger.getLeadDocuments(lead.id, operator))
    const variables = copyVariables(lead, this.deps.domain.global.get().sender_name, template)
    const rendered = template === undefined
      ? { text: `渠道类型：${type}。请基于线索资料直接撰写。`, unresolved: [] as string[] }
      : renderVariables(template.body, variables)
    const body = rendered.text
    const prompt = [
      body,
      `渠道类型：${type} — ${TYPE_GUIDES[type] ?? DEFAULT_TYPE_GUIDE}`,
      '线索资料（JSON）：',
      JSON.stringify({
        company_name: variables.company_name,
        contact_name: variables.contact_name,
        industry: variables.industry,
        company_size: variables.company_size,
        demand_desc: variables.demand_desc,
        budget_range: variables.budget_range,
        sender_name: variables.sender_name,
      }),
      '补充资料：',
      knowledge.length === 0 ? '（无）' : knowledge,
      rendered.unresolved.length === 0
        ? '落位说明：模板变量已全部按实际值填入，直接照此撰写；发送人身份以线索资料中的 sender_name 为准。'
        : `落位说明：以下变量没有值，请在文案中自然略过（不要输出占位符本身，也不要猜测其内容）：${rendered.unresolved.map(name => `{{${name}}}`).join('、')}。发送人身份以线索资料中的 sender_name 为准。`,
    ].join('\n')
    const text = (await this.completionFactory(CONTENT_SYSTEM_PROMPT).complete(prompt, signal)).trim()
    if (text.length === 0) throw new Error('模型返回了空文案，请重试')
    const artifact = generatedContentSchema.parse({
      id: newId<GeneratedContentId>(),
      lead_id: lead.id,
      type,
      variant: input.variant,
      content: text,
      ...(template === undefined ? {} : { template_id: template.id }),
      created_at: Date.now(),
    })
    await this.generatedContents.put(artifact.id, artifact)
    await appendAuditRecord(this.deps.audit, {
      action: 'content.generate',
      object_type: 'content',
      object_id: artifact.id,
      summary: `生成${type}文案（${input.variant}）：${lead.company_name}`,
    }, operator, channel)
    return { content: artifact, leadName: lead.company_name }
  }

  /**
   * One lead's generated copies, newest first, optionally filtered by type.
   * @param leadId - the lead to read.
   * @param operator - the caller's resolved operator.
   * @param type - optional type filter (open vocabulary).
   * @param limit - page size (1-100, default 20).
   * @param offset - page offset (default 0).
   * @returns the matching page with the unfiltered total.
   */
  listByLead(
    leadId: string,
    operator: ResolvedOperator,
    type: string | undefined,
    limit?: number,
    offset?: number,
  ): { items: GeneratedContent[]; total: number } {
    const lead = this.deps.ledger.getLead(leadId, operator)
    const all = [...this.generatedContents.entries()]
      .map(([, content]) => content)
      .filter(content => content.lead_id === lead.id && (type === undefined || content.type === type))
      .sort((left, right) => right.created_at - left.created_at)
    const page = pagingOf({ limit, offset })
    return { items: all.slice(page.offset, page.offset + page.limit), total: all.length }
  }

  /**
   * Create one content template.
   * @param input - name, type, optional industry, body with {{variables}}, variable docs.
   * @param operator - the caller's resolved operator.
   * @param channel - which surface performed the write.
   * @returns the stored template.
   */
  async createTemplate(
    input: { name: string; type: string; industry?: string; body: string; variables?: ContentTemplate['variables']; enabled?: boolean },
    operator: ResolvedOperator,
    channel: OperatorChannel,
  ): Promise<ContentTemplate> {
    this.requireTemplateManager(operator, '创建文案模板')
    if (input.name.trim().length === 0) throw new Error('模板名称不能为空')
    if (input.type.trim().length === 0) throw new Error('文案类型不能为空')
    if (input.body.trim().length === 0) throw new Error('模板正文不能为空')
    const now = Date.now()
    const template = contentTemplateSchema.parse({
      id: newId<ContentTemplateId>(),
      name: input.name,
      ...(input.industry === undefined ? {} : { industry: input.industry }),
      type: input.type,
      body: input.body,
      variables: input.variables ?? [],
      enabled: input.enabled ?? true,
      created_at: now,
      updated_at: now,
    })
    await this.contentTemplates.put(template.id, template)
    await appendAuditRecord(this.deps.audit, {
      action: 'content_template.create',
      object_type: 'content_template',
      object_id: template.id,
      summary: `新建文案模板：${template.name}（类型 ${template.type}）`,
    }, operator, channel)
    return template
  }

  /**
   * Update one content template; `body`/`variables` are whole-value replacement.
   * @param templateId - the template to update.
   * @param patch - the fields to change.
   * @param operator - the caller's resolved operator.
   * @param channel - which surface performed the write.
   * @returns the stored template after the write.
   */
  async updateTemplate(
    templateId: string,
    patch: { name?: string; industry?: string; type?: string; body?: string; variables?: ContentTemplate['variables']; enabled?: boolean },
    operator: ResolvedOperator,
    channel: OperatorChannel,
  ): Promise<ContentTemplate> {
    this.requireTemplateManager(operator, '修改文案模板')
    const template = this.requireTemplate(templateId)
    const changes = definedFields(patch)
    if (changes.name !== undefined && changes.name.trim().length === 0) throw new Error('模板名称不能为空')
    if (changes.type !== undefined && changes.type.trim().length === 0) throw new Error('文案类型不能为空')
    if (changes.body !== undefined && changes.body.trim().length === 0) throw new Error('模板正文不能为空')
    const keys = Object.keys(changes)
    if (keys.length === 0) return template
    const next = contentTemplateSchema.parse({
      ...template,
      ...changes,
      updated_at: Math.max(Date.now(), template.created_at),
    })
    await this.contentTemplates.put(next.id, next)
    await appendAuditRecord(this.deps.audit, {
      action: 'content_template.update',
      object_type: 'content_template',
      object_id: next.id,
      summary: `修改文案模板：${next.name}（${keys.join('、')}）`,
    }, operator, channel)
    return next
  }

  /**
   * List content templates, optionally filtered by type or enabled state.
   * @param filters - optional type filter and enabled-only switch.
   * @returns the templates, oldest first.
   */
  listTemplates(filters: { type?: string; enabledOnly?: boolean } = {}): ContentTemplate[] {
    return [...this.contentTemplates.entries()]
      .map(([, template]) => template)
      .filter(template => (filters.enabledOnly !== true || template.enabled)
        && (filters.type === undefined || template.type === filters.type))
      .sort((left, right) => left.created_at - right.created_at)
  }

  /**
   * Delete one content template. A template referenced by any generated copy
   * is rejected — disable it instead (fail loud, keep the artifact chain).
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
    this.requireTemplateManager(operator, '删除文案模板')
    const template = this.requireTemplate(templateId)
    for (const [, content] of this.generatedContents.entries()) {
      if (content.template_id === template.id) {
        throw new Error(`文案模板「${template.name}」已被生成产物引用，不能删除；请改用 content_template_update 停用（enabled=false）`)
      }
    }
    await this.contentTemplates.delete(template.id)
    await appendAuditRecord(this.deps.audit, {
      action: 'content_template.delete',
      object_type: 'content_template',
      object_id: template.id,
      summary: `删除文案模板：${template.name}`,
    }, operator, channel)
  }

  /** Resolve one template by id or fail friendly. */
  private requireTemplate(templateId: string): ContentTemplate {
    const template = this.contentTemplates.get(ContentTemplateId(templateId))
    if (template === undefined) throw new Error(`文案模板不存在：${templateId}`)
    return template
  }

  /**
   * The generate-time template chain: explicit id → type+industry → type →
   * industry-absent → any of the type; an explicit id is honored even when
   * disabled (the operator named it).
   */
  private resolveTemplate(explicitId: string | undefined, type: string, lead: Lead): ContentTemplate | undefined {
    if (explicitId !== undefined) {
      const explicit = this.contentTemplates.get(ContentTemplateId(explicitId))
      if (explicit === undefined) throw new Error(`文案模板不存在：${explicitId}`)
      return explicit
    }
    const enabled = [...this.contentTemplates.entries()]
      .map(([, template]) => template)
      .filter(template => template.enabled && template.type === type)
      .sort((left, right) => left.created_at - right.created_at)
    if (enabled.length === 0) return undefined
    const industryMatch = lead.industry === undefined
      ? undefined
      : enabled.find(template => template.industry === lead.industry)
    return industryMatch ?? enabled.find(template => template.industry === undefined) ?? enabled[0]
  }

  /** Global-template management gate for every template write. */
  private requireTemplateManager(operator: ResolvedOperator, action: string): void {
    if (!operator.capabilities.can_manage_global_templates) {
      throw new Error(`当前操作者没有${action}的权限（can_manage_global_templates）`)
    }
  }
}

/**
 * Copy generation writes the lead's artifact list, so it is a lead write:
 * `lead_scope=own` operators may only generate for leads they own — a pool
 * lead must be claimed first.
 * @param lead - the lead about to receive generated copy.
 * @param operator - the caller's resolved operator.
 */
export function assertCopyScope(lead: Lead, operator: ResolvedOperator): void {
  if (operator.capabilities.lead_scope !== 'all' && lead.owner_id !== operator.userId) {
    throw new Error(lead.owner_id === undefined
      ? `公海线索需先领取（assign 给自己）再生成文案：${lead.company_name}`
      : `当前操作者无权为他人线索生成文案：${lead.company_name}`)
  }
}
