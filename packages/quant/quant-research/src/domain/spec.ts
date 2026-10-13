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
/** One virtual research account (PET). */
export type AccountId = Branded<'AccountId'>
/** One simulated fill inside a virtual account. */
export type OrderId = Branded<'OrderId'>
export type ResearchNoteId = Branded<'ResearchNoteId'>

/** Brand a plain string as an account id. */
export const AccountId = (value: string): AccountId => value as AccountId

/** Brand a plain string as an order id. */
export const OrderId = (value: string): OrderId => value as OrderId

/** Brand a plain string as a research note id. */
export const ResearchNoteId = (value: string): ResearchNoteId => value as ResearchNoteId

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

/** One virtual account: cash plus long-only positions. */
export const accountSchema = z.object({
  id: z.string().min(1).transform(AccountId),
  name: z.string().min(1),
  initial_cash: z.number().positive(),
  cash: z.number(),
  positions: z.array(z.object({
    symbol: z.string().min(1),
    shares: z.number(),
    avg_cost: z.number(),
  })).refine(
    positions => new Set(positions.map(p => p.symbol)).size === positions.length,
    { message: 'duplicate position symbol' },
  ),
  created_at: epochMs,
  updated_at: epochMs,
})

/** One virtual account. */
export type Account = z.infer<typeof accountSchema>

/** One simulated fill. */
export const orderSchema = z.object({
  id: z.string().min(1).transform(OrderId),
  account_id: z.string().min(1).transform(AccountId),
  symbol: z.string().min(1),
  side: z.enum(['buy', 'sell']),
  shares: z.number(),
  price: z.number(),
  fee: z.number(),
  executed_at: epochMs,
})

/** One simulated fill record. */
export type Order = z.infer<typeof orderSchema>

export const researchNoteSchema = z.object({
  id: z.string().min(1).transform(ResearchNoteId),
  title: z.string().min(1),
  body: z.string().min(1),
  symbol: z.string().min(1).optional(),
  tags: z.array(z.string().min(1)).refine(
    tags => new Set(tags).size === tags.length,
    { message: 'duplicate tag' },
  ),
  created_at: epochMs,
})
export type ResearchNote = z.infer<typeof researchNoteSchema>

/** One red-line denial record. */
export type ComplianceDenial = z.infer<typeof complianceDenialSchema>

/**
 * The quant-research domain v2: the denial audit trail plus the PET virtual
 * accounts and their simulated fills. v2 adds the two PET tables; there is
 * no migration (pre-release stance), so a v1 medium rejects at open.
 */
export const quantResearchDomainSpec = defineDomain({
  name: 'quant_research',
  version: 2,
  tables: {
    compliance_denials: domainTable<ComplianceDenialId, ComplianceDenial>(complianceDenialSchema),
    accounts: domainTable<AccountId, Account>(accountSchema),
    orders: domainTable<OrderId, Order>(orderSchema),
    research_notes: domainTable<ResearchNoteId, ResearchNote>(researchNoteSchema),
  },
})
