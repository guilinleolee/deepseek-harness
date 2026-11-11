"""Patcher P2-PET: domain v2 + PET module + tools wiring (worktree)."""
import io

WT = 'D:/dsh-wt-quant-p1/packages/quant/quant-research/src/'

def patch(path, old, new):
    s = io.open(WT + path, encoding='utf-8').read()
    assert old in s, f'{path}: missing {old[:70]!r}'
    s = s.replace(old, new)
    io.open(WT + path, 'w', encoding='utf-8', newline='\n').write(s)
    print('patched', path)

# ── domain/spec.ts → v2: accounts + orders ──
patch('domain/spec.ts',
"""/** One audited red-line denial. */
export type ComplianceDenialId = Branded<'ComplianceDenialId'>""",
"""/** One audited red-line denial. */
export type ComplianceDenialId = Branded<'ComplianceDenialId'>
/** One virtual research account (PET). */
export type AccountId = Branded<'AccountId'>
/** One simulated fill inside a virtual account. */
export type OrderId = Branded<'OrderId'>""")

patch('domain/spec.ts',
"""/** Brand a plain string as a denial id. */""",
"""/** One virtual account: cash plus long-only positions. */
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

/** Brand a plain string as a denial id. */""")

patch('domain/spec.ts',
"""/**
 * The quant-research domain: the denial audit table only; research ledgers arrive with later phases.
 */
export const quantResearchDomainSpec = defineDomain({
  name: 'quant_research',
  version: 1,
  tables: {
    compliance_denials: domainTable<ComplianceDenialId, ComplianceDenial>(complianceDenialSchema),
  },
})""",
"""/**
 * The quant-research domain v2: the denial audit trail plus the PET virtual
 * accounts and their simulated fills. v2 adds the two PET tables; no
 * migration exists (pre-release, see the repository's pre-release stance).
 */
export const quantResearchDomainSpec = defineDomain({
  name: 'quant_research',
  version: 2,
  tables: {
    compliance_denials: domainTable<ComplianceDenialId, ComplianceDenial>(complianceDenialSchema),
    accounts: domainTable<AccountId, Account>(accountSchema),
    orders: domainTable<OrderId, Order>(orderSchema),
  },
})""")
print('domain v2 done')
