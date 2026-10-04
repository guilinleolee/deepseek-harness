/**
 * Durable storage-domain declaration for the quant-research domain (v1):
 * the compliance-denial audit trail. One spec object is the single source of
 * the domain's identity and record schemas; the frozen contract may only
 * change through a domain version bump confirmed by the owner.
 * @module @deepseek-ai/dsh-quant-research/domain/spec
 */

import { z } from 'zod'
import type { Branded } from '@deepseek-ai/dsh-brand'
import { defineDomain, domainTable } from '@deepseek-ai/dsh-storage-domain'

/** One audited red-line denial. */
export type ComplianceDenialId = Branded<'ComplianceDenialId'>

/**
 * Brand a plain string as a denial id.
 * @param value - the plain string to brand.
 * @returns the branded denial id.
 */
export const ComplianceDenialId = (value: string): ComplianceDenialId => value as ComplianceDenialId

/** Epoch-millisecond timestamp bounded to the safe-integer range. */
const epochMs = z.number().int().nonnegative().max(Number.MAX_SAFE_INTEGER)

/** One red-line denial: what the model tried, why the gate refused, and when. */
export const complianceDenialSchema = z.object({
  id: z.string().min(1).transform(ComplianceDenialId),
  /** The denied tool name. */
  tool_name: z.string().min(1),
  /** The friendly Chinese reason the gate returned to the model. */
  reason: z.string().min(1),
  /** Calling agent id, when the execution carried one. */
  agent_id: z.string().min(1).optional(),
  /** Denial timestamp in epoch milliseconds. */
  denied_at: epochMs,
})

/** One red-line denial record. */
export type ComplianceDenial = z.infer<typeof complianceDenialSchema>

/** The quant-research domain: the denial audit table only; research ledgers arrive with later phases. */
export const quantResearchDomainSpec = defineDomain({
  name: 'quant_research',
  version: 1,
  tables: {
    compliance_denials: domainTable<ComplianceDenialId, ComplianceDenial>(complianceDenialSchema),
  },
})
