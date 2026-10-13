import { describe, expect, it } from 'vitest'
import { ComplianceDenialId, complianceDenialSchema, quantResearchDomainSpec } from '../src/domain/spec.ts'

describe('quantResearchDomainSpec', () => {
  it('freezes the v1 contract: one audit table', () => {
    expect(quantResearchDomainSpec.name).toBe('quant_research')
    expect(quantResearchDomainSpec.version).toBe(1)
    expect(Object.keys(quantResearchDomainSpec.tables)).toEqual(['compliance_denials'])
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
