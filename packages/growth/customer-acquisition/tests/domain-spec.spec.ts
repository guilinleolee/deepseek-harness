import { describe, expect, it } from 'vitest'
import {
  auditLogSchema, customerAcquisitionSettingsSchema, icpProfileSchema, leadSchema,
  sopTaskSchema, sopTemplateSchema,
} from '../src/domain/spec.ts'

const NOW = 1_700_000_000_000

function leadFixture(overrides: Record<string, unknown> = {}) {
  return {
    id: '0f4bd8ae-1cd2-4f4a-9e5a-5d3ec2ea1a01',
    source: 'manual',
    company_name: '杭州示例商贸有限公司',
    tags: ['官网'],
    created_at: NOW,
    updated_at: NOW,
    ...overrides,
  }
}

describe('customer-acquisition domain schemas (frozen contract §3)', () => {
  it('accepts a minimal lead and fills the defaults', () => {
    const parsed = leadSchema.parse(leadFixture())
    expect(parsed.opportunity_stage).toBe('new')
    expect(parsed.status).toBe('active')
    expect(parsed.owner_id).toBeUndefined()
  })

  it('rejects a lead whose updated_at precedes created_at', () => {
    expect(leadSchema.safeParse(leadFixture({ updated_at: NOW - 1 })).success).toBe(false)
  })

  it('rejects duplicate lead tags', () => {
    expect(leadSchema.safeParse(leadFixture({ tags: ['a', 'a'] })).success).toBe(false)
  })

  it('rejects an unknown closed enum value but stores unknown open values', () => {
    expect(leadSchema.safeParse(leadFixture({ status: 'deleted' })).success).toBe(false)
    expect(leadSchema.safeParse(leadFixture({ source: '未来新渠道' })).success).toBe(true)
  })

  it('enforces the icp weights-sum-to-100 invariant and unique dimension ids', () => {
    const base = {
      id: 'f1e2d3c4-0000-4000-8000-000000000001',
      name: 'B2B 工厂商贸画像',
      enabled: true,
      created_at: NOW,
      updated_at: NOW,
    }
    const dimensions = [
      { id: 'budget', name: '预算规模', description: '…', weight: 40 },
      { id: 'demand', name: '需求匹配', description: '…', weight: 60 },
    ]
    expect(icpProfileSchema.safeParse({ ...base, dimensions }).success).toBe(true)
    expect(icpProfileSchema.safeParse({
      ...base, dimensions: dimensions.map(d => ({ ...d, weight: 30 })),
    }).success).toBe(false)
    expect(icpProfileSchema.safeParse({
      ...base,
      dimensions: [...dimensions, { id: 'budget', name: '重复', description: '…', weight: 0 }],
    }).success).toBe(false)
  })

  it('rejects duplicate sop rules for one intent level', () => {
    const rule = {
      intent_level: 'high' as const,
      cadence: 'D+1 问候，D+3 案例',
      points: ['确认需求'],
      questions: ['预算范围？'],
      risks: ['竞品比价'],
    }
    expect(sopTemplateSchema.safeParse({
      id: 'f1e2d3c4-0000-4000-8000-000000000002',
      name: '门店 SOP',
      rules: [rule, { ...rule, points: ['再次触达'] }],
      enabled: true,
      created_at: NOW,
      updated_at: NOW,
    }).success).toBe(false)
  })

  it('defaults sop task status to pending and rejects unknown statuses', () => {
    const task = {
      id: 'f1e2d3c4-0000-4000-8000-000000000003',
      lead_id: 'f1e2d3c4-0000-4000-8000-000000000004',
      title: 'D+1 微信问候',
      planned_at: NOW,
      created_at: NOW,
      updated_at: NOW,
    }
    expect(sopTaskSchema.parse(task).status).toBe('pending')
    expect(sopTaskSchema.safeParse({ ...task, status: 'cancelled' }).success).toBe(false)
  })

  it('keeps the audit record schema strict about source and operator identity', () => {
    const record = {
      id: 'f1e2d3c4-0000-4000-8000-000000000005',
      source: 'web',
      operator_user_id: 'local-default',
      action: 'settings.update',
      object_type: 'settings',
      summary: '更新全局参数',
      created_at: NOW,
    }
    expect(auditLogSchema.parse(record).operator_user_id).toBe('local-default')
    expect(auditLogSchema.safeParse({ ...record, source: 'cron' }).success).toBe(false)
  })

  it('caps the settings compliance values at the red-line constants', () => {
    expect(customerAcquisitionSettingsSchema.safeParse({ geo_max_pages: 21 }).success).toBe(false)
    expect(customerAcquisitionSettingsSchema.safeParse({ geo_max_pages: 20 }).success).toBe(true)
    expect(customerAcquisitionSettingsSchema.safeParse({ geo_page_timeout_ms: 10_001 }).success).toBe(false)
    expect(customerAcquisitionSettingsSchema.safeParse({ geo_page_timeout_ms: 10_000 }).success).toBe(true)
    expect(customerAcquisitionSettingsSchema.parse({}).geo_max_pages).toBe(10)
  })
})
