/**
 * The AI lead-scoring service (module 3): ICP profile and scoring-template
 * CRUD behind `can_manage_global_templates`, the score flows (one lead and
 * serial batches) with weight snapshots and intent write-back, the fully
 * retained scoring history, and the preset industry seed. Scoring is one
 * model call per lead (data contract §3.4): the service renders the
 * template prompt, runs it through the `PromptCompletion` port, validates
 * the JSON answer, and persists the run — the audit trail records every
 * scoring action (data contract §2.5).
 * @module @deepseek-ai/dsh-customer-acquisition/scoring/service
 */

import type { Context } from '@deepseek-ai/cordis'
import type { Domain, KvTable } from '@deepseek-ai/dsh-storage-domain'
import { appendAuditRecord, type AuditTable } from '../audit.ts'
import { IcpProfileId, ScoreRunId, ScoreRunItemId, ScoreTemplateId, newId } from '../domain/ids.ts'
import {
  customerAcquisitionDomainSpec,
  icpProfileSchema,
  scoreRunItemSchema,
  scoreRunSchema,
  scoreTemplateSchema,
  type IcpProfile,
  type Lead,
  type ScoreRun,
  type ScoreRunItem,
  type ScoreTemplate,
} from '../domain/spec.ts'
import { llmPromptCompletion, type PromptCompletion, type ResolvedAiPolicy } from '../llm/oneshot.ts'
import type { LeadLedgerService } from '../leads/service.ts'
import type { OperatorChannel, ResolvedOperator } from '../permission/types.ts'
import { INTENT_LABELS, intentTagFor, parseScoreOutput, SCORE_SYSTEM_PROMPT } from './evaluate.ts'
import type { ParsedScoreOutput } from './evaluate.ts'
import { aggregateKnowledge, renderScorePrompt } from './prompt.ts'
import { seedIndustryTemplates } from './seed.ts'
import type {
  IcpCreateInput, IcpDimensionInput, IcpProfileRefValue, IcpProfileValue, IcpUpdateInput,
  ScoreBatchInput, ScoreBatchValue, ScoreHistoryRequest, ScoreHistoryValue, ScoreOneInput,
  ScoreOneValue, ScoreTemplateCreateInput, ScoreTemplateRefValue, ScoreTemplateUpdateInput,
  ScoreTemplateValue,
} from './types.ts'

export { SEED_IDS, seedIndustryTemplates } from './seed.ts'

/** The upper bound of one scoring batch (enforced here and by the compliance gate). */
export const SCORE_BATCH_LIMIT = 50

/** Clamped paging bounds (offset floors at 0, limit ranges 1-100). */
function pagingOf(request: { limit?: number; offset?: number }): { offset: number; limit: number } {
  return {
    offset: Math.max(request.offset ?? 0, 0),
    limit: Math.min(Math.max(request.limit ?? 20, 1), 100),
  }
}

/** Validate one ICP dimension input: non-empty texts, finite weight in range. */
function validateDimension(dimension: IcpDimensionInput, index: number): void {
  const label = `维度 ${index + 1}`
  if (typeof dimension.id !== 'string' || dimension.id.trim().length === 0) throw new Error(`${label}的 id 不能为空`)
  if (typeof dimension.name !== 'string' || dimension.name.trim().length === 0) throw new Error(`${label}的名称不能为空`)
  if (typeof dimension.description !== 'string' || dimension.description.trim().length === 0) {
    throw new Error(`${label}的说明不能为空`)
  }
  if (typeof dimension.weight !== 'number' || !Number.isFinite(dimension.weight) || dimension.weight < 0 || dimension.weight > 100) {
    throw new Error(`${label}（${dimension.name}）的权重必须是 0-100 的数字`)
  }
}

/** Validate a whole dimensions list: per-dimension shape, unique ids, weights summing to 100. */
function validateDimensions(dimensions: IcpDimensionInput[]): void {
  if (!Array.isArray(dimensions) || dimensions.length < 1) throw new Error('ICP 画像至少需要一个评分维度')
  dimensions.forEach((dimension, index) => {
    validateDimension(dimension, index)
  })
  const seen = new Set<string>()
  for (const dimension of dimensions) {
    if (seen.has(dimension.id)) throw new Error(`维度 id 重复：${dimension.id}`)
    seen.add(dimension.id)
  }
  const total = dimensions.reduce((sum, dimension) => sum + dimension.weight, 0)
  if (Math.abs(total - 100) > 0.01) throw new Error(`维度权重必须合计为 100，当前为 ${total}`)
}

/** Validate one prompt template body: non-empty name and text. */
function validateTemplateFields(name: string | undefined, promptText: string | undefined): void {
  if (name !== undefined && name.trim().length === 0) throw new Error('模板名称不能为空')
  if (promptText !== undefined && promptText.trim().length === 0) throw new Error('打分提示词不能为空')
}

/** Strip `undefined` fields so an omitted patch key never clobbers the stored value. */
function definedFields<T extends object>(patch: T): Partial<T> {
  return Object.fromEntries(Object.entries(patch).filter(([, value]) => value !== undefined)) as Partial<T>
}

/** Construction dependencies of the scoring service. */
export interface LeadScoringDeps {
  /** Host context carrying the `llm` service (used by the default completion). */
  readonly ctx: Context
  /** The opened customer-acquisition domain (borrowed from the P0 service). */
  readonly domain: Domain<typeof customerAcquisitionDomainSpec>
  /** The audit-log table handle. */
  readonly audit: AuditTable
  /** The lead ledger the scoring flows read leads and write intent through. */
  readonly ledger: LeadLedgerService
  /** The validated AI call policy. */
  readonly policy: ResolvedAiPolicy
  /** Completion factory override; tests inject a deterministic fake. */
  readonly completionFactory?: (system: string) => PromptCompletion
}

/** One persisted scoring outcome before wire projection. */
export interface ScoreOutcome {
  run: ScoreRun
  items: ScoreRunItem[]
  /** The validated model answer the items persist; carries dimension names for the wire. */
  parsed: ParsedScoreOutput
}

/**
 * Storage-backed AI lead-scoring service. The domain handle is borrowed from
 * the P0 service (a domain opens once); this service owns no lifecycle.
 */
export class LeadScoringService {
  private readonly icpProfiles: KvTable<IcpProfileId, IcpProfile>
  private readonly scoreTemplates: KvTable<ScoreTemplateId, ScoreTemplate>
  private readonly scoreRuns: KvTable<ScoreRunId, ScoreRun>
  private readonly scoreRunItems: KvTable<ScoreRunItemId, ScoreRunItem>
  private readonly completionFactory: (system: string, signal?: AbortSignal) => PromptCompletion

  /** @param deps - context, borrowed domain and audit handle, ledger, policy, and completion factory. */
  constructor(private readonly deps: LeadScoringDeps) {
    this.icpProfiles = deps.domain.table('icp_profiles')
    this.scoreTemplates = deps.domain.table('score_templates')
    this.scoreRuns = deps.domain.table('score_runs')
    this.scoreRunItems = deps.domain.table('score_run_items')
    this.completionFactory = deps.completionFactory
      ?? (system => llmPromptCompletion(deps.ctx, deps.policy, system))
  }

  /** Seed the preset industry templates once (idempotent, data contract §5). */
  async seedTemplates(): Promise<void> {
    await seedIndustryTemplates(this.deps.domain)
  }

  // ------------------------------------------------------- icp profiles ----

  /**
   * Create one ICP profile. Weights must sum to 100 (±0.01) and dimension
   * ids must be unique — misconfiguration fails loud before anything stores.
   * @param input - the profile fields with at least one dimension.
   * @param operator - the caller's resolved operator.
   * @param channel - which surface performed the write.
   * @returns the stored profile.
   */
  async createIcpProfile(
    input: IcpCreateInput,
    operator: ResolvedOperator,
    channel: OperatorChannel,
  ): Promise<IcpProfile> {
    this.requireTemplateManager(operator, '创建 ICP 画像')
    if (typeof input.name !== 'string' || input.name.trim().length === 0) throw new Error('画像名称不能为空')
    validateDimensions(input.dimensions)
    const now = Date.now()
    const profile = icpProfileSchema.parse({
      id: newId<IcpProfileId>(),
      name: input.name,
      ...(input.industry === undefined ? {} : { industry: input.industry }),
      dimensions: input.dimensions,
      enabled: input.enabled ?? true,
      created_at: now,
      updated_at: now,
    })
    await this.icpProfiles.put(profile.id, profile)
    await appendAuditRecord(this.deps.audit, {
      action: 'icp.create',
      object_type: 'icp_profile',
      object_id: profile.id,
      summary: `新建 ICP 画像：${profile.name}（${profile.dimensions.length} 个维度，权重合计 100）`,
    }, operator, channel)
    return profile
  }

  /**
   * Update one ICP profile; `dimensions` is whole-list replacement and still
   * must sum to 100. Historical runs keep their weight snapshots, so edits
   * never distort past scores.
   * @param profileId - the profile to update.
   * @param patch - the fields to change.
   * @param operator - the caller's resolved operator.
   * @param channel - which surface performed the write.
   * @returns the stored profile after the write.
   */
  async updateIcpProfile(
    profileId: string,
    patch: IcpUpdateInput,
    operator: ResolvedOperator,
    channel: OperatorChannel,
  ): Promise<IcpProfile> {
    this.requireTemplateManager(operator, '修改 ICP 画像')
    const profile = this.requireProfile(profileId)
    const changes = definedFields(patch)
    if (changes.dimensions !== undefined) validateDimensions(changes.dimensions)
    if (changes.name !== undefined && changes.name.trim().length === 0) throw new Error('画像名称不能为空')
    const keys = Object.keys(changes)
    if (keys.length === 0) return profile
    const next = icpProfileSchema.parse({
      ...profile,
      ...changes,
      updated_at: Math.max(Date.now(), profile.created_at),
    })
    await this.icpProfiles.put(next.id, next)
    await appendAuditRecord(this.deps.audit, {
      action: 'icp.update',
      object_type: 'icp_profile',
      object_id: next.id,
      summary: `修改 ICP 画像：${next.name}（${keys.join('、')}）`,
    }, operator, channel)
    return next
  }

  /**
   * List ICP profiles, optionally enabled-only.
   * @param enabledOnly - when true, only enabled profiles return.
   * @returns the profiles, oldest first.
   */
  listIcpProfiles(enabledOnly?: boolean): IcpProfileValue[] {
    return [...this.icpProfiles.entries()]
      .map(([, profile]) => profile)
      .filter(profile => enabledOnly !== true || profile.enabled)
      .sort((left, right) => left.created_at - right.created_at)
      .map(toIcpProfileValue)
  }

  /**
   * Delete one ICP profile. A profile referenced by any scoring run is
   * rejected — disable it with `enabled=false` instead (fail loud, keep the
   * history chain resolvable).
   * @param profileId - the profile to delete.
   * @param operator - the caller's resolved operator.
   * @param channel - which surface performed the write.
   * @returns resolution after the record is removed.
   */
  async deleteIcpProfile(
    profileId: string,
    operator: ResolvedOperator,
    channel: OperatorChannel,
  ): Promise<void> {
    this.requireTemplateManager(operator, '删除 ICP 画像')
    const profile = this.requireProfile(profileId)
    for (const [, run] of this.scoreRuns.entries()) {
      if (run.icp_profile_id === profile.id) {
        throw new Error(`ICP 画像「${profile.name}」已被打分历史引用，不能删除；请改用 icp_manage 的 update 停用（enabled=false）`)
      }
    }
    await this.icpProfiles.delete(profile.id)
    await appendAuditRecord(this.deps.audit, {
      action: 'icp.delete',
      object_type: 'icp_profile',
      object_id: profile.id,
      summary: `删除 ICP 画像：${profile.name}`,
    }, operator, channel)
  }

  // ----------------------------------------------------- score templates ----

  /**
   * Create one scoring prompt template.
   * @param input - name, optional industry, `prompt_text` with the
   *   `{{lead}}`/`{{icp_profile}}`/`{{dimensions}}`/`{{knowledge}}` placeholders.
   * @param operator - the caller's resolved operator.
   * @param channel - which surface performed the write.
   * @returns the stored template.
   */
  async createScoreTemplate(
    input: ScoreTemplateCreateInput,
    operator: ResolvedOperator,
    channel: OperatorChannel,
  ): Promise<ScoreTemplate> {
    this.requireTemplateManager(operator, '创建打分模板')
    validateTemplateFields(input.name, input.prompt_text)
    const now = Date.now()
    const template = scoreTemplateSchema.parse({
      id: newId<ScoreTemplateId>(),
      name: input.name,
      ...(input.industry === undefined ? {} : { industry: input.industry }),
      prompt_text: input.prompt_text,
      enabled: input.enabled ?? true,
      created_at: now,
      updated_at: now,
    })
    await this.scoreTemplates.put(template.id, template)
    await appendAuditRecord(this.deps.audit, {
      action: 'score_template.create',
      object_type: 'score_template',
      object_id: template.id,
      summary: `新建打分模板：${template.name}`,
    }, operator, channel)
    return template
  }

  /**
   * Update one scoring prompt template.
   * @param templateId - the template to update.
   * @param patch - the fields to change.
   * @param operator - the caller's resolved operator.
   * @param channel - which surface performed the write.
   * @returns the stored template after the write.
   */
  async updateScoreTemplate(
    templateId: string,
    patch: ScoreTemplateUpdateInput,
    operator: ResolvedOperator,
    channel: OperatorChannel,
  ): Promise<ScoreTemplate> {
    this.requireTemplateManager(operator, '修改打分模板')
    const template = this.requireTemplate(templateId)
    validateTemplateFields(patch.name, patch.prompt_text)
    const changes = definedFields(patch)
    const keys = Object.keys(changes)
    if (keys.length === 0) return template
    const next = scoreTemplateSchema.parse({
      ...template,
      ...changes,
      updated_at: Math.max(Date.now(), template.created_at),
    })
    await this.scoreTemplates.put(next.id, next)
    await appendAuditRecord(this.deps.audit, {
      action: 'score_template.update',
      object_type: 'score_template',
      object_id: next.id,
      summary: `修改打分模板：${next.name}（${keys.join('、')}）`,
    }, operator, channel)
    return next
  }

  /**
   * List scoring prompt templates, optionally enabled-only.
   * @param enabledOnly - when true, only enabled templates return.
   * @returns the templates, oldest first.
   */
  listScoreTemplates(enabledOnly?: boolean): ScoreTemplateValue[] {
    return [...this.scoreTemplates.entries()]
      .map(([, template]) => template)
      .filter(template => enabledOnly !== true || template.enabled)
      .sort((left, right) => left.created_at - right.created_at)
      .map(toScoreTemplateValue)
  }

  /**
   * Delete one scoring prompt template. A template referenced by any scoring
   * run is rejected — disable it with `enabled=false` instead.
   * @param templateId - the template to delete.
   * @param operator - the caller's resolved operator.
   * @param channel - which surface performed the write.
   * @returns resolution after the record is removed.
   */
  async deleteScoreTemplate(
    templateId: string,
    operator: ResolvedOperator,
    channel: OperatorChannel,
  ): Promise<void> {
    this.requireTemplateManager(operator, '删除打分模板')
    const template = this.requireTemplate(templateId)
    for (const [, run] of this.scoreRuns.entries()) {
      if (run.template_id === template.id) {
        throw new Error(`打分模板「${template.name}」已被打分历史引用，不能删除；请改用 score_template_manage 的 update 停用（enabled=false）`)
      }
    }
    await this.scoreTemplates.delete(template.id)
    await appendAuditRecord(this.deps.audit, {
      action: 'score_template.delete',
      object_type: 'score_template',
      object_id: template.id,
      summary: `删除打分模板：${template.name}`,
    }, operator, channel)
  }

  // ------------------------------------------------------------ scoring ----

  /**
   * Score one lead: render the resolved template prompt (with the lead's
   * attached documents injected up to the knowledge cap), run one model call,
   * validate the answer, persist the run with a weight snapshot per item,
   * write the intent tag back, and audit `score.run`.
   * @param input - the lead plus optional explicit profile/template ids.
   * @param operator - the caller's resolved operator.
   * @param channel - which surface performed the action.
   * @param signal - caller cancellation signal for the model call.
   * @returns the persisted run and its items.
   */
  async scoreOne(
    input: ScoreOneInput,
    operator: ResolvedOperator,
    channel: OperatorChannel,
    signal?: AbortSignal,
  ): Promise<ScoreOneValue> {
    const outcome = await this.scoreLead(input, operator, signal)
    await appendAuditRecord(this.deps.audit, {
      action: 'score.run',
      object_type: 'score_run',
      object_id: outcome.run.id,
      summary: `AI 打分 ${outcome.run.total} 分（${INTENT_LABELS[outcome.run.intent_tag]}）：${outcome.leadName}`,
    }, operator, channel)
    return toScoreOneValue(outcome.run, outcome.parsed)
  }

  /**
   * Score up to {@link SCORE_BATCH_LIMIT} leads serially with the same
   * resolution rules as {@link scoreOne}. One failure never aborts the
   * batch — the failed lead and reason return in `failed`. Audited once as
   * `score.batch`.
   * @param input - the lead id list plus optional explicit profile/template ids.
   * @param operator - the caller's resolved operator.
   * @param channel - which surface performed the action.
   * @param signal - caller cancellation signal for the model calls.
   * @returns the per-lead successes and failures.
   */
  async scoreBatch(
    input: ScoreBatchInput,
    operator: ResolvedOperator,
    channel: OperatorChannel,
    signal?: AbortSignal,
  ): Promise<ScoreBatchValue> {
    if (!Array.isArray(input.lead_ids) || input.lead_ids.length < 1 || input.lead_ids.length > SCORE_BATCH_LIMIT) {
      throw new Error(`lead_ids 必须是 1-${SCORE_BATCH_LIMIT} 条线索的列表`)
    }
    if (new Set(input.lead_ids).size !== input.lead_ids.length) throw new Error('lead_ids 存在重复线索')
    const runs: ScoreBatchValue['runs'] = []
    const failed: ScoreBatchValue['failed'] = []
    for (const leadId of input.lead_ids) {
      try {
        const outcome = await this.scoreLead({
          lead_id: leadId,
          ...(input.icp_profile_id === undefined ? {} : { icp_profile_id: input.icp_profile_id }),
          ...(input.score_template_id === undefined ? {} : { score_template_id: input.score_template_id }),
        }, operator, signal)
        runs.push({
          lead_id: outcome.run.lead_id,
          run_id: outcome.run.id,
          total: outcome.run.total,
          intent_tag: outcome.run.intent_tag,
        })
      } catch (error) {
        failed.push({ lead_id: leadId, error: error instanceof Error ? error.message : String(error) })
      }
    }
    await appendAuditRecord(this.deps.audit, {
      action: 'score.batch',
      object_type: 'score_run',
      summary: `批量打分：成功 ${runs.length}/共 ${input.lead_ids.length} 条`,
    }, operator, channel)
    return { runs, failed }
  }

  /**
   * Trace the scoring history: runs newest first with their per-dimension
   * items (weights as snapshotted at scoring time), scoped to the leads the
   * operator may read.
   * @param request - optional lead/run filter plus paging bounds.
   * @param operator - the caller's resolved operator.
   * @returns the matching history page with the unfiltered total.
   */
  history(request: ScoreHistoryRequest, operator: ResolvedOperator): ScoreHistoryValue {
    let selected: ScoreRun[]
    if (request.run_id !== undefined) {
      const run = this.scoreRuns.get(ScoreRunId(request.run_id))
      if (run === undefined) throw new Error(`打分记录不存在：${request.run_id}`)
      this.deps.ledger.getLead(run.lead_id, operator)
      selected = [run]
    } else if (request.lead_id !== undefined) {
      const lead = this.deps.ledger.getLead(request.lead_id, operator)
      selected = [...this.scoreRuns.entries()]
        .map(([, run]) => run)
        .filter(run => run.lead_id === lead.id)
    } else {
      selected = [...this.scoreRuns.entries()]
        .map(([, run]) => run)
        .filter(run => this.deps.ledger.isLeadVisible(run.lead_id, operator))
    }
    selected = selected.sort((left, right) => right.created_at - left.created_at)
    const page = pagingOf(request)
    return {
      items: selected
        .slice(page.offset, page.offset + page.limit)
        .map(run => ({
          run: {
            id: run.id,
            lead_id: run.lead_id,
            total: run.total,
            intent_tag: run.intent_tag,
            reason: run.reason,
            created_at: run.created_at,
          },
          items: [...this.scoreRunItems.entries()]
            .map(([, item]) => item)
            .filter(item => item.run_id === run.id)
            .map(item => ({ dimension_id: item.dimension_id, score: item.score, weight: item.weight, reason: item.reason })),
        })),
      total: selected.length,
    }
  }

  // ----------------------------------------------------------- internals ----

  /** One lead's full scoring flow, without the audit write (shared by one and batch). */
  private async scoreLead(
    input: ScoreOneInput,
    operator: ResolvedOperator,
    signal?: AbortSignal,
  ): Promise<ScoreOutcome & { leadName: string }> {
    const lead = this.deps.ledger.getLead(input.lead_id, operator)
    assertScoringScope(lead, operator)
    const profile = this.resolveProfile(input.icp_profile_id, lead)
    const template = this.resolveTemplate(input.score_template_id, lead)
    const knowledge = aggregateKnowledge(this.deps.ledger.getLeadDocuments(lead.id, operator))
    const prompt = renderScorePrompt(template.prompt_text, { lead, profile, knowledge })
    const parsed = parseScoreOutput(
      await this.completionFactory(SCORE_SYSTEM_PROMPT).complete(prompt, signal),
      profile,
    )
    const intentTag = intentTagFor(parsed.total)
    const now = Date.now()
    const run = scoreRunSchema.parse({
      id: newId<ScoreRunId>(),
      lead_id: lead.id,
      icp_profile_id: profile.id,
      template_id: template.id,
      total: parsed.total,
      reason: parsed.reason,
      intent_tag: intentTag,
      created_at: now,
    })
    const items = parsed.items.map(item => scoreRunItemSchema.parse({
      id: newId<ScoreRunItemId>(),
      run_id: run.id,
      dimension_id: item.dimension_id,
      score: item.score,
      weight: item.weight,
      reason: item.reason,
      created_at: now,
    }))
    await this.scoreRuns.put(run.id, run)
    for (const item of items) await this.scoreRunItems.put(item.id, item)
    await this.deps.ledger.applyIntent(lead.id, intentTag)
    return { run, items, parsed, leadName: lead.company_name }
  }

  /** Resolve the ICP profile: explicit id, else global default, else industry match, else any enabled. */
  private resolveProfile(explicitId: string | undefined, lead: Lead): IcpProfile {
    return this.resolveFallbackChain<IcpProfile>(
      explicitId,
      this.deps.domain.global.get().default_icp_profile_id,
      id => this.icpProfiles.get(IcpProfileId(id)),
      () => [...this.icpProfiles.entries()].map(([, record]) => record),
      lead,
      'ICP 画像',
    )
  }

  /** Resolve the scoring template: explicit id, else global default, else industry match, else any enabled. */
  private resolveTemplate(explicitId: string | undefined, lead: Lead): ScoreTemplate {
    return this.resolveFallbackChain<ScoreTemplate>(
      explicitId,
      this.deps.domain.global.get().default_score_template_id,
      id => this.scoreTemplates.get(ScoreTemplateId(id)),
      () => [...this.scoreTemplates.entries()].map(([, record]) => record),
      lead,
      '打分模板',
    )
  }

  /** The shared fallback chain: explicit id → enabled default → exact industry → industry-absent → any enabled. */
  private resolveFallbackChain<T extends { enabled: boolean; industry?: string | undefined; created_at: number }>(
    explicitId: string | undefined,
    defaultId: string | undefined,
    get: (id: string) => T | undefined,
    all: () => T[],
    lead: Lead,
    label: string,
  ): T {
    if (explicitId !== undefined) {
      const explicit = get(explicitId)
      if (explicit === undefined) throw new Error(`${label}不存在：${explicitId}`)
      return explicit
    }
    if (defaultId !== undefined) {
      const fallback = get(defaultId)
      if (fallback !== undefined && fallback.enabled) return fallback
    }
    const enabled = all()
      .filter(record => record.enabled)
      .sort((left, right) => left.created_at - right.created_at)
    const first = enabled[0]
    if (first === undefined) {
      throw new Error(`没有启用中的${label}，请先创建或启用一套（icp_manage / score_template_manage 的 create）`)
    }
    const industryMatch = lead.industry === undefined
      ? undefined
      : enabled.find(record => record.industry === lead.industry)
    return industryMatch ?? enabled.find(record => record.industry === undefined) ?? first
  }

  /** Resolve one profile by id or fail friendly. */
  private requireProfile(profileId: string): IcpProfile {
    const profile = this.icpProfiles.get(IcpProfileId(profileId))
    if (profile === undefined) throw new Error(`ICP 画像不存在：${profileId}`)
    return profile
  }

  /** Resolve one template by id or fail friendly. */
  private requireTemplate(templateId: string): ScoreTemplate {
    const template = this.scoreTemplates.get(ScoreTemplateId(templateId))
    if (template === undefined) throw new Error(`打分模板不存在：${templateId}`)
    return template
  }

  /** Global-template management gate for every profile/template write. */
  private requireTemplateManager(operator: ResolvedOperator, action: string): void {
    if (!operator.capabilities.can_manage_global_templates) {
      throw new Error(`当前操作者没有${action}的权限（can_manage_global_templates）`)
    }
  }
}

/**
 * Scoring writes the lead's intent tag, so it is a lead write: `lead_scope=own`
 * operators may only score leads they own — a pool lead must be claimed first.
 * @param lead - the lead about to be scored.
 * @param operator - the caller's resolved operator.
 */
export function assertScoringScope(lead: Lead, operator: ResolvedOperator): void {
  if (operator.capabilities.lead_scope !== 'all' && lead.owner_id !== operator.userId) {
    throw new Error(lead.owner_id === undefined
      ? `公海线索需先领取（assign 给自己）再打分：${lead.company_name}`
      : `当前操作者无权为他人线索打分：${lead.company_name}`)
  }
}

/** Project a stored profile to its wire value. */
function toIcpProfileValue(profile: IcpProfile): IcpProfileValue {
  return {
    id: profile.id,
    name: profile.name,
    ...(profile.industry === undefined ? {} : { industry: profile.industry }),
    enabled: profile.enabled,
    dimensions: profile.dimensions.map(dimension => ({ ...dimension })),
  }
}

/** Project a stored template to its wire value. */
function toScoreTemplateValue(template: ScoreTemplate): ScoreTemplateValue {
  return {
    id: template.id,
    name: template.name,
    ...(template.industry === undefined ? {} : { industry: template.industry }),
    prompt_text: template.prompt_text,
    enabled: template.enabled,
  }
}

/** Narrow profile projection for create/update outputs. */
export function toIcpProfileRef(profile: IcpProfile): IcpProfileRefValue {
  return { id: profile.id, name: profile.name, enabled: profile.enabled }
}

/** Narrow template projection for create/update outputs. */
export function toScoreTemplateRef(template: ScoreTemplate): ScoreTemplateRefValue {
  return { id: template.id, name: template.name, enabled: template.enabled }
}

/** Project one scoring outcome to the `score_one` envelope; names ride the parsed answer. */
function toScoreOneValue(run: ScoreRun, parsed: ParsedScoreOutput): ScoreOneValue {
  return {
    run: { id: run.id, total: run.total, intent_tag: run.intent_tag, reason: run.reason },
    items: parsed.items.map(item => ({
      dimension_id: item.dimension_id,
      name: item.name,
      score: item.score,
      weight: item.weight,
      reason: item.reason,
    })),
  }
}
