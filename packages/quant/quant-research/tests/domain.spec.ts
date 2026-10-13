import { describe, expect, it } from 'vitest'
import {
  AccountId, accountSchema, ComplianceDenialId, complianceDenialSchema, OrderId, orderSchema,
  quantResearchDomainSpec,
} from '../src/domain/spec.ts'

describe('account/order schemas', () => {
  it('parses a valid account and rejects duplicate position symbols', () => {
    const parsed = accountSchema.parse({
      id: 'acc-1', name: '研究一号', initial_cash: 100, cash: 50,
      positions: [{ symbol: '000001', shares: 10, avg_cost: 9 }],
      created_at: 1, updated_at: 2,
    })
    expect(parsed.id).toBe('acc-1')
    const duplicate = accountSchema.safeParse({
      id: 'acc-2', name: 'x', initial_cash: 1, cash: 1,
      positions: [
        { symbol: '000001', shares: 1, avg_cost: 1 },
        { symbol: '000001', shares: 2, avg_cost: 1 },
      ],
      created_at: 1, updated_at: 1,
    })
    expect(duplicate.success).toBe(false)
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

describe('quantResearchDomainSpec', () => {
  it('freezes the v2 contract: audit trail plus PET accounts and orders', () => {
    expect(quantResearchDomainSpec.name).toBe('quant_research')
    expect(quantResearchDomainSpec.version).toBe(2)
    expect(Object.keys(quantResearchDomainSpec.tables)).toEqual([
      'compliance_denials', 'accounts', 'orders', 'research_notes',
    ])
  })
})

describe('complianceDenialSchema', () => {
  it('brands the id and keeps the full record', () => {
    const parsed = complianceDenialSchema.parse({
      id: 'denial-1',
      tool_name: 'quant_run_backtest',
      reason: '禁止实盘指令',
      agent_id: 'agent-1',
      denied_at: 1_700_000_000_000,
    })
    expect(parsed.id).toBe('denial-1')
    expect(parsed).toMatchObject({
      tool_name: 'quant_run_backtest',
      reason: '禁止实盘指令',
      agent_id: 'agent-1',
      denied_at: 1_700_000_000_000,
    })
  })

  it('omits agent_id when absent', () => {
    const parsed = complianceDenialSchema.parse({
      id: 'denial-2',
      tool_name: 'quant_get_kline',
      reason: 'bars 超上限',
      denied_at: 1,
    })
    expect('agent_id' in parsed).toBe(false)
  })

  it('rejects empty tool names, reasons, and out-of-range timestamps', () => {
    expect(complianceDenialSchema.safeParse({
      id: 'd', tool_name: '', reason: 'x', denied_at: 1,
    }).success).toBe(false)
    expect(complianceDenialSchema.safeParse({
      id: 'd', tool_name: 't', reason: '', denied_at: 1,
    }).success).toBe(false)
    expect(complianceDenialSchema.safeParse({
      id: 'd', tool_name: 't', reason: 'x', denied_at: -1,
    }).success).toBe(false)
    expect(complianceDenialSchema.safeParse({
      id: '', tool_name: 't', reason: 'x', denied_at: 1,
    }).success).toBe(false)
  })

  it('brands through the constructor', () => {
    const branded = ComplianceDenialId('denial-9')
    expect(branded).toBe('denial-9')
  })
})
