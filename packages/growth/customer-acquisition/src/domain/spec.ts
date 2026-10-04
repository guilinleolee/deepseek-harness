/**
 * Durable storage-domain declaration for the customer-acquisition domain
 * (data contract v1, §3). One spec object is the single source of the
 * domain's identity and record schemas; the frozen contract may only change
 * through a domain version bump confirmed by the owner.
 * @module @deepseek-ai/dsh-customer-acquisition/domain/spec
 */

import { z } from 'zod'
import { defineDomain, domainTable } from '@deepseek-ai/dsh-storage-domain'
import {
  AuditLogId, ContentTemplateId, DocumentId, FollowupId, GeneratedContentId,
  GeoReportId, GeoScanId, IcpProfileId, LeadId, ScoreRunId, ScoreRunItemId,
  ScoreTemplateId, SopTaskId, SopTemplateId, UserId,
} from './ids.ts'

/** Epoch-millisecond timestamp bounded to the safe-integer range. */
const epochMs = z.number().int().nonnegative().max(Number.MAX_SAFE_INTEGER)

/** Validate one non-empty string and brand it via the id's constructor. */
function brandedId<B>(brand: (value: string) => B) {
  return z.string().min(1).transform(brand)
}

/** Lead qualification tag written back by the scoring flow. */
export const intentLevelSchema = z.enum(['high', 'mid', 'low', 'invalid'])
/** Lead lifecycle status; `recycled` is the recycle bin. */
export const leadStatusSchema = z.enum(['active', 'archived', 'recycled'])
/** Opportunity progress; `won`/`lost` feed the dashboard conversion rates. */
export const opportunityStageSchema = z.enum(['new', 'contacted', 'nurturing', 'qualified', 'won', 'lost'])
/** Contact's decision role in the buying process. */
export const decisionRoleSchema = z.enum(['decision_maker', 'influencer', 'end_user', 'gatekeeper', 'unknown'])
/** A/B variant marker on generated copy. */
export const contentVariantSchema = z.enum(['A', 'B'])
/** GEO scan lifecycle. */
export const geoScanStatusSchema = z.enum(['running', 'done', 'failed'])
/** Finding severity. */
export const geoSeveritySchema = z.enum(['high', 'mid', 'low'])
/** Operator channel of one audited action. */
export const auditSourceSchema = z.enum(['web', 'agent', 'acp'])
/** The audit source union, reused by the wire projections. */
export type AuditSource = z.infer<typeof auditSourceSchema>
/** Follow-up task state machine. */
export const sopTaskStatusSchema = z.enum(['pending', 'done', 'deferred', 'dropped'])

const auditTrail = { created_at: epochMs, updated_at: epochMs } as const

/** Refine helper: `updated_at` must not precede `created_at`. */
function updatedAtNotBeforeCreated<S extends z.ZodType<{ created_at: number; updated_at: number }>>(schema: S) {
  return schema.refine(
    record => record.updated_at >= record.created_at,
    { path: ['updated_at'], message: 'updated_at must not precede created_at' },
  )
}

// ---------------------------------------------------------------- leads ----

export const leadSchema = updatedAtNotBeforeCreated(z.object({
  id: brandedId(LeadId),
  owner_id: brandedId(UserId).optional(),
  source: z.string().min(1),
  company_name: z.string().min(1),
  contact_name: z.string().optional(),
  phone: z.string().optional(),
  email: z.string().optional(),
  industry: z.string().optional(),
  company_size: z.string().optional(),
  demand_desc: z.string().optional(),
  budget_range: z.string().optional(),
  decision_role: decisionRoleSchema.optional(),
  intent_level: intentLevelSchema.optional(),
  tags: z.array(z.string().min(1)).refine(
    tags => new Set(tags).size === tags.length,
    { message: 'duplicate lead tag' },
  ),
  opportunity_stage: opportunityStageSchema.default('new'),
  next_followup_at: epochMs.optional(),
  status: leadStatusSchema.default('active'),
  ...auditTrail,
}))

export type Lead = z.infer<typeof leadSchema>

export const leadFollowupSchema = z.object({
  id: brandedId(FollowupId),
  lead_id: brandedId(LeadId),
  content: z.string().min(1),
  created_at: epochMs,
})

export type LeadFollowup = z.infer<typeof leadFollowupSchema>

export const leadDocumentSchema = updatedAtNotBeforeCreated(z.object({
  id: brandedId(DocumentId),
  lead_id: brandedId(LeadId),
  title: z.string().min(1),
  content: z.string().min(1).max(20_000),
  ...auditTrail,
}))

export type LeadDocument = z.infer<typeof leadDocumentSchema>

// ------------------------------------------------------------ scoring ----

export const scoreRunSchema = z.object({
  id: brandedId(ScoreRunId),
  lead_id: brandedId(LeadId),
  icp_profile_id: brandedId(IcpProfileId),
  template_id: brandedId(ScoreTemplateId),
  total: z.number().min(0).max(100),
  reason: z.string().min(1),
  intent_tag: intentLevelSchema,
  created_at: epochMs,
})

export type ScoreRun = z.infer<typeof scoreRunSchema>

export const scoreRunItemSchema = z.object({
  id: brandedId(ScoreRunItemId),
  run_id: brandedId(ScoreRunId),
  dimension_id: z.string().min(1),
  score: z.number().min(0).max(100),
  weight: z.number().min(0).max(100),
  reason: z.string().min(1),
  created_at: epochMs,
})

export type ScoreRunItem = z.infer<typeof scoreRunItemSchema>

export const icpDimensionSchema = z.object({
  id: z.string().min(1),
  name: z.string().min(1),
  description: z.string().min(1),
  weight: z.number().min(0).max(100),
})

export type IcpDimension = z.infer<typeof icpDimensionSchema>

/** Floating-point tolerance for the weights-sum-to-100 invariant. */
export const ICP_WEIGHT_TOLERANCE = 0.01

export const icpProfileSchema = updatedAtNotBeforeCreated(z.object({
  id: brandedId(IcpProfileId),
  name: z.string().min(1),
  industry: z.string().optional(),
  dimensions: z.array(icpDimensionSchema).min(1),
  enabled: z.boolean(),
  ...auditTrail,
})).superRefine((profile, ctx) => {
  const seen = new Set<string>()
  profile.dimensions.forEach((dimension, index) => {
    if (seen.has(dimension.id)) {
      ctx.addIssue({
        code: 'custom',
        path: ['dimensions', index, 'id'],
        message: `duplicate icp dimension id '${dimension.id}'`,
      })
    }
    seen.add(dimension.id)
  })
  const total = profile.dimensions.reduce((sum, dimension) => sum + dimension.weight, 0)
  if (Math.abs(total - 100) > ICP_WEIGHT_TOLERANCE) {
    ctx.addIssue({
      code: 'custom',
      path: ['dimensions'],
      message: `icp dimension weights must sum to 100, got ${total}`,
    })
  }
})

export type IcpProfile = z.infer<typeof icpProfileSchema>

export const scoreTemplateSchema = updatedAtNotBeforeCreated(z.object({
  id: brandedId(ScoreTemplateId),
  name: z.string().min(1),
  industry: z.string().optional(),
  prompt_text: z.string().min(1),
  enabled: z.boolean(),
  ...auditTrail,
}))

export type ScoreTemplate = z.infer<typeof scoreTemplateSchema>

// ------------------------------------------------------------- copy ----

export const contentTemplateVariableSchema = z.object({
  name: z.string().min(1),
  description: z.string().min(1),
  example: z.string().optional(),
})

export type ContentTemplateVariable = z.infer<typeof contentTemplateVariableSchema>

export const contentTemplateSchema = updatedAtNotBeforeCreated(z.object({
  id: brandedId(ContentTemplateId),
  name: z.string().min(1),
  industry: z.string().optional(),
  type: z.string().min(1),
  body: z.string().min(1),
  variables: z.array(contentTemplateVariableSchema),
  enabled: z.boolean(),
  ...auditTrail,
}))

export type ContentTemplate = z.infer<typeof contentTemplateSchema>

export const generatedContentSchema = z.object({
  id: brandedId(GeneratedContentId),
  lead_id: brandedId(LeadId),
  type: z.string().min(1),
  variant: contentVariantSchema,
  content: z.string().min(1),
  template_id: brandedId(ContentTemplateId).optional(),
  created_at: epochMs,
})

export type GeneratedContent = z.infer<typeof generatedContentSchema>

// --------------------------------------------------------------- sop ----

export const sopRuleSchema = z.object({
  intent_level: intentLevelSchema,
  cadence: z.string().min(1),
  points: z.array(z.string().min(1)).min(1),
  questions: z.array(z.string().min(1)),
  risks: z.array(z.string().min(1)),
})

export type SopRule = z.infer<typeof sopRuleSchema>

export const sopTemplateSchema = updatedAtNotBeforeCreated(z.object({
  id: brandedId(SopTemplateId),
  name: z.string().min(1),
  industry: z.string().optional(),
  rules: z.array(sopRuleSchema).min(1),
  enabled: z.boolean(),
  ...auditTrail,
})).superRefine((template, ctx) => {
  const seen = new Set<string>()
  template.rules.forEach((rule, index) => {
    if (seen.has(rule.intent_level)) {
      ctx.addIssue({
        code: 'custom',
        path: ['rules', index, 'intent_level'],
        message: `duplicate sop rule for intent level '${rule.intent_level}'`,
      })
    }
    seen.add(rule.intent_level)
  })
})

export type SopTemplate = z.infer<typeof sopTemplateSchema>

export const sopTaskSchema = updatedAtNotBeforeCreated(z.object({
  id: brandedId(SopTaskId),
  lead_id: brandedId(LeadId),
  title: z.string().min(1),
  status: sopTaskStatusSchema.default('pending'),
  planned_at: epochMs,
  note: z.string().optional(),
  ...auditTrail,
}))

export type SopTask = z.infer<typeof sopTaskSchema>

// --------------------------------------------------------------- geo ----

export const geoScanSchema = z.object({
  id: brandedId(GeoScanId),
  url: z.string().min(1),
  status: geoScanStatusSchema,
  started_at: epochMs,
  finished_at: epochMs.optional(),
  error: z.string().optional(),
})

export type GeoScan = z.infer<typeof geoScanSchema>

export const geoFindingSchema = z.object({
  id: z.string().min(1),
  category: z.string().min(1),
  severity: geoSeveritySchema,
  title: z.string().min(1),
  detail: z.string().min(1),
  evidence_page: z.string().optional(),
})

export type GeoFinding = z.infer<typeof geoFindingSchema>

export const geoArtifactsSchema = z.object({
  faq_material: z.string().optional(),
  brand_kit: z.string().optional(),
  tasks: z.array(z.string().min(1)),
})

export type GeoArtifacts = z.infer<typeof geoArtifactsSchema>

export const geoReportSchema = z.object({
  id: brandedId(GeoReportId),
  scan_id: brandedId(GeoScanId),
  score: z.number().min(0).max(100),
  findings: z.array(geoFindingSchema),
  llms_txt: z.string().optional(),
  artifacts: geoArtifactsSchema,
  report_md: z.string().min(1),
  pages_fetched: z.number().int().nonnegative(),
  robots_skipped_paths: z.array(z.string()),
  created_at: epochMs,
})

export type GeoReport = z.infer<typeof geoReportSchema>

// ------------------------------------------------------------- audit ----

export const auditLogSchema = z.object({
  id: brandedId(AuditLogId),
  source: auditSourceSchema,
  operator_user_id: brandedId(UserId),
  action: z.string().min(1),
  object_type: z.string().min(1),
  object_id: z.string().optional(),
  summary: z.string().min(1),
  created_at: epochMs,
})

export type AuditLog = z.infer<typeof auditLogSchema>

// ----------------------------------------------------------- settings ----

export const customerAcquisitionSettingsSchema = z.object({
  default_icp_profile_id: z.string().min(1).optional(),
  default_score_template_id: z.string().min(1).optional(),
  geo_max_pages: z.number().int().min(1).max(20).default(10),
  geo_page_timeout_ms: z.number().int().min(1_000).max(10_000).default(10_000),
  sop_todo_write_enabled: z.boolean().default(true),
})

export type CustomerAcquisitionSettings = z.infer<typeof customerAcquisitionSettingsSchema>

/** Value served before the first settings write; the compliance caps are baked in. */
export const DEFAULT_SETTINGS: CustomerAcquisitionSettings = {
  geo_max_pages: 10,
  geo_page_timeout_ms: 10_000,
  sop_todo_write_enabled: true,
}

// -------------------------------------------------------------- domain ----

/** The frozen v1 domain declaration (data contract §1). */
export const customerAcquisitionDomainSpec = defineDomain({
  name: 'customer_acquisition',
  version: 1,
  global: {
    schema: customerAcquisitionSettingsSchema,
    initial: DEFAULT_SETTINGS,
  },
  tables: {
    leads: domainTable<LeadId, Lead>(leadSchema),
    lead_followups: domainTable<FollowupId, LeadFollowup>(leadFollowupSchema),
    lead_documents: domainTable<DocumentId, LeadDocument>(leadDocumentSchema),
    score_runs: domainTable<ScoreRunId, ScoreRun>(scoreRunSchema),
    score_run_items: domainTable<ScoreRunItemId, ScoreRunItem>(scoreRunItemSchema),
    icp_profiles: domainTable<IcpProfileId, IcpProfile>(icpProfileSchema),
    score_templates: domainTable<ScoreTemplateId, ScoreTemplate>(scoreTemplateSchema),
    content_templates: domainTable<ContentTemplateId, ContentTemplate>(contentTemplateSchema),
    generated_contents: domainTable<GeneratedContentId, GeneratedContent>(generatedContentSchema),
    sop_templates: domainTable<SopTemplateId, SopTemplate>(sopTemplateSchema),
    sop_tasks: domainTable<SopTaskId, SopTask>(sopTaskSchema),
    geo_scans: domainTable<GeoScanId, GeoScan>(geoScanSchema),
    geo_reports: domainTable<GeoReportId, GeoReport>(geoReportSchema),
    audit_logs: domainTable<AuditLogId, AuditLog>(auditLogSchema),
  },
})
