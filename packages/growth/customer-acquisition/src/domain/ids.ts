/**
 * Branded identifiers owned by the customer-acquisition domain. Every id
 * crosses the tool and Remote boundaries as an opaque string; the brands keep
 * them from being interchanged at compile time (see `@deepseek-ai/dsh-brand`).
 * Each id ships a same-named constructor so zod schemas and service code can
 * brand a plain string in one call.
 * @module @deepseek-ai/dsh-customer-acquisition/domain/ids
 */

import type { Branded } from '@deepseek-ai/dsh-brand'

/** Operator identity: the local default user, or a platform-injected account id. */
export type UserId = Branded<'UserId'>
/** One lead record. */
export type LeadId = Branded<'LeadId'>
/** One follow-up note on a lead. */
export type FollowupId = Branded<'FollowupId'>
/** One plain-text document attached to a lead. */
export type DocumentId = Branded<'DocumentId'>
/** One AI scoring run (total + reason). */
export type ScoreRunId = Branded<'ScoreRunId'>
/** One per-dimension item of a scoring run. */
export type ScoreRunItemId = Branded<'ScoreRunItemId'>
/** One ICP profile (scoring dimensions + weights). */
export type IcpProfileId = Branded<'IcpProfileId'>
/** One scoring prompt template. */
export type ScoreTemplateId = Branded<'ScoreTemplateId'>
/** One nurture-copy template. */
export type ContentTemplateId = Branded<'ContentTemplateId'>
/** One generated nurture-copy artifact bound to a lead. */
export type GeneratedContentId = Branded<'GeneratedContentId'>
/** One follow-up SOP template. */
export type SopTemplateId = Branded<'SopTemplateId'>
/** One generated follow-up task. */
export type SopTaskId = Branded<'SopTaskId'>
/** One GEO diagnosis scan. */
export type GeoScanId = Branded<'GeoScanId'>
/** One GEO diagnosis report. */
export type GeoReportId = Branded<'GeoReportId'>
/** One audit-log entry. */
export type AuditLogId = Branded<'AuditLogId'>

/** Construct a branded {@link UserId} from its plain string form. */
export function UserId(id: string): UserId { return id as UserId }
/** Construct a branded {@link LeadId} from its plain string form. */
export function LeadId(id: string): LeadId { return id as LeadId }
/** Construct a branded {@link FollowupId} from its plain string form. */
export function FollowupId(id: string): FollowupId { return id as FollowupId }
/** Construct a branded {@link DocumentId} from its plain string form. */
export function DocumentId(id: string): DocumentId { return id as DocumentId }
/** Construct a branded {@link ScoreRunId} from its plain string form. */
export function ScoreRunId(id: string): ScoreRunId { return id as ScoreRunId }
/** Construct a branded {@link ScoreRunItemId} from its plain string form. */
export function ScoreRunItemId(id: string): ScoreRunItemId { return id as ScoreRunItemId }
/** Construct a branded {@link IcpProfileId} from its plain string form. */
export function IcpProfileId(id: string): IcpProfileId { return id as IcpProfileId }
/** Construct a branded {@link ScoreTemplateId} from its plain string form. */
export function ScoreTemplateId(id: string): ScoreTemplateId { return id as ScoreTemplateId }
/** Construct a branded {@link ContentTemplateId} from its plain string form. */
export function ContentTemplateId(id: string): ContentTemplateId { return id as ContentTemplateId }
/** Construct a branded {@link GeneratedContentId} from its plain string form. */
export function GeneratedContentId(id: string): GeneratedContentId { return id as GeneratedContentId }
/** Construct a branded {@link SopTemplateId} from its plain string form. */
export function SopTemplateId(id: string): SopTemplateId { return id as SopTemplateId }
/** Construct a branded {@link SopTaskId} from its plain string form. */
export function SopTaskId(id: string): SopTaskId { return id as SopTaskId }
/** Construct a branded {@link GeoScanId} from its plain string form. */
export function GeoScanId(id: string): GeoScanId { return id as GeoScanId }
/** Construct a branded {@link GeoReportId} from its plain string form. */
export function GeoReportId(id: string): GeoReportId { return id as GeoReportId }
/** Construct a branded {@link AuditLogId} from its plain string form. */
export function AuditLogId(id: string): AuditLogId { return id as AuditLogId }

/**
 * Generate one opaque id of the given brand. Seed records use fixed
 * string ids (see the data contract §5), so the schema validates `min(1)`
 * rather than UUID shape.
 * @returns a fresh random UUID carrying the brand.
 */
export function newId<B extends string>(): Branded<B> {
  return crypto.randomUUID() as Branded<B>
}
