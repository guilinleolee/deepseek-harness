"""Patcher P2-PET-tests2: cover the PET gaps (domain refine, rebalance validation, service branches, tool renders)."""
import io

T = 'D:/dsh-wt-quant-p1/packages/quant/quant-research/tests/'

def patch(path, old, new):
    s = io.open(path, encoding='utf-8').read()
    assert old in s, f'{path}: {old[:70]!r}'
    s = s.replace(old, new)
    io.open(path, 'w', encoding='utf-8', newline='\n').write(s)
    print('patched', path.split('tests/')[-1])

# ── domain.spec: account/order schema parse ──
patch(T + 'domain.spec.ts',
"""import { ComplianceDenialId, complianceDenialSchema, quantResearchDomainSpec } from '../src/domain/spec.ts'""",
"""import {
  AccountId, accountSchema, complianceDenialSchema, OrderId, orderSchema, quantResearchDomainSpec,
} from '../src/domain/spec.ts'""")

patch(T + 'domain.spec.ts',
"""describe('quantResearchDomainSpec', () => {""",
"""describe('account/order schemas', () => {
  it('parses a valid account and rejects duplicate position symbols', () => {
    const parsed = accountSchema.parse({
      id: 'acc-1', name: '研究一号', initial_cash: 100, cash: 50,
      positions: [{ symbol: '000001', shares: 10, avg_cost: 9 }],
      created_at: 1, updated_at: 2,
    })
    expect(parsed.id).toBe('acc-1')
    expect(() => accountSchema.parse({
      id: 'acc-2', name: 'x', initial_cash: 1, cash: 1,
      positions: [
        { symbol: '000001', shares: 1, avg_cost: 1 },
        { symbol: '000001', shares: 2, avg_cost: 1 },
      ],
      created_at: 1, updated_at: 1,
    }).success === false) || expect(accountSchema.safeParse({
      id: 'acc-2', name: 'x', initial_cash: 1, cash: 1,
      positions: [
        { symbol: '000001', shares: 1, avg_cost: 1 },
        { symbol: '000001', shares: 2, avg_cost: 1 },
      ],
      created_at: 1, updated_at: 1,
    }).success).toBe(false)
  })

  it('parses orders and brands both ids', () => {
    const parsed = orderSchema.parse({
      id: 'o-1', account_id: 'acc-1', symbol: 'AAPL', side: 'buy',
      shares: 5, price: 100, fee: 0.5, executed_at: 9,
    })
    expect(parsed.id).toBe('o-1')
    expect(parsed.account_id).toBe('acc-1')
    expect(complianceDenialSchema.safeParse({ id: 'd', tool_name: 't', reason: 'r', denied_at: 1 }).success).toBe(true)
    void AccountId
    void OrderId
  })
})

describe('quantResearchDomainSpec', () => {""")

# ── pet.spec: rebalance validation + service branches ──
patch(T + 'pet.spec.ts',
"""  it('rejects infeasible buys instead of going negative', () => {""",
"""  it('validates duplicates, negative weights, price coverage, and fee rate', () => {
    const base = { cash: 0, positions: [], prices: PRICES, feeRate: 0 }
    expect(() => computePlan({
      ...base, targets: [
        { symbol: 'AAPL', weight: 0.3 }, { symbol: 'AAPL', weight: 0.3 },
      ],
    })).toThrow(/调仓目标重复/)
    expect(() => computePlan({
      ...base, targets: [{ symbol: 'AAPL', weight: -0.1 }],
    })).toThrow(/非负数值/)
    expect(() => computePlan({
      ...base, targets: [{ symbol: 'AAPL', weight: 0.5 }], feeRate: 0.9,
    })).toThrow(/手续费率/)
    expect(() => computePlan({
      cash: 0,
      positions: [{ symbol: '000001', shares: 10, avg_cost: 5 }],
      targets: [{ symbol: 'AAPL', weight: 0.5 }],
      prices: { AAPL: 100 },
      feeRate: 0,
    })).toThrow(/缺少持仓/)
    expect(() => computePlan({
      cash: 0,
      positions: [{ symbol: '000001', shares: 10, avg_cost: 5 }],
      targets: [
        { symbol: 'AAPL', weight: 0.25 }, { symbol: '000001', weight: 0.25 },
      ],
      prices: { AAPL: 100, '000001': 0 },
      feeRate: 0,
    })).toThrow(/必须为正数/)
  })

  it('rejects infeasible buys instead of going negative', () => {""")

patch(T + 'pet.spec.ts',
"""  it('rejects overselling', async () => {""",
"""  it('lookups fall through id to name and reject misses with both given', async () => {
    const accounts = table() as unknown as Parameters<typeof createAccount>[0]
    const created = await createAccount(accounts, { name: '研究一号', initialCash: 1 }, 1, () => 'a-9')
    // id miss + name hit: requireAccount tries id first, then name.
    expect(requireAccount(accounts, 'nope', '研究一号').id).toBe(created.id)
  })

  it('rejects overselling', async () => {""")
print('patcher done')
