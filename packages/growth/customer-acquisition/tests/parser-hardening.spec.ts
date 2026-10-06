import { describe, expect, it } from 'vitest'
import {
  canonicalKeyOf,
  parseExtractOutput,
  repairJsonNewlines,
} from '../src/leads/extract.ts'
import { parseScoreOutput } from '../src/scoring/evaluate.ts'
import { assertSopScope } from '../src/sop/service.ts'

// The parser's repair and normalization helpers are the production hardening
// for flash-model output slips; these tests pin every branch.

describe('repairJsonNewlines', () => {
  it('escapes literal line breaks inside strings', () => {
    expect(repairJsonNewlines('{"a":"第一行\n第二行"}')).toBe('{"a":"第一行\\n第二行"}')
    expect(repairJsonNewlines('{"a":"x\r\ny"}')).toBe('{"a":"x\\r\\ny"}')
  })

  it('leaves structural newlines outside strings untouched', () => {
    expect(repairJsonNewlines('{\n  "a": 1\n}')).toBe('{\n  "a": 1\n}')
  })

  it('preserves escaped quotes and backslashes inside strings', () => {
    expect(repairJsonNewlines('{"a":"say \\"hi\\" \\\\ ok"}')).toBe('{"a":"say \\"hi\\" \\\\ ok"}')
  })

  it('repairs a parse-failing body with in-string line breaks', () => {
    const parsed = JSON.parse(repairJsonNewlines('{"a":"第一行\n第二行"}'))
    expect(parsed.a).toBe('第一行\n第二行')
  })
})

describe('canonicalKeyOf', () => {
  it('maps Chinese and English key variants to canonical keys', () => {
    expect(canonicalKeyOf('公司名称')).toBe('company_name')
    expect(canonicalKeyOf('公司')).toBe('company_name')
    expect(canonicalKeyOf('联系人')).toBe('contact_name')
    expect(canonicalKeyOf('联系电话')).toBe('phone')
    expect(canonicalKeyOf('电子邮箱')).toBe('email')
    expect(canonicalKeyOf('所属行业')).toBe('industry')
    expect(canonicalKeyOf('公司规模')).toBe('company_size')
    expect(canonicalKeyOf('需求描述')).toBe('demand_desc')
    expect(canonicalKeyOf('预算范围')).toBe('budget_range')
    expect(canonicalKeyOf('决策角色')).toBe('decision_role')
    expect(canonicalKeyOf('备注说明')).toBe('notes')
  })

  it('maps English variants case-insensitively', () => {
    expect(canonicalKeyOf('CompanyName')).toBe('company_name')
    expect(canonicalKeyOf('Budget')).toBe('budget_range')
    expect(canonicalKeyOf('EMAIL')).toBe('email')
  })

  it('passes unknown keys through untouched', () => {
    expect(canonicalKeyOf('extraction_result')).toBe('extraction_result')
    expect(canonicalKeyOf('')).toBe('')
  })
})

describe('parseExtractOutput repair and normalization integration', () => {
  it('recovers from in-string newlines via repairJsonBody', () => {
    const parsed = parseExtractOutput('{"company_name":"甲公司","demand_desc":"第一行\n第二行"}')
    expect(parsed.fields.company_name).toBe('甲公司')
    expect(parsed.fields.demand_desc).toBe('第一行\n第二行')
  })

  it('recovers from full-width separators at structural positions', () => {
    const parsed = parseExtractOutput('{"company_name":"甲公司"，"contact_name":"乙"}')
    expect(parsed.fields.company_name).toBe('甲公司')
    expect(parsed.fields.contact_name).toBe('乙')
  })

  it('leaves full-width punctuation inside string values untouched', () => {
    const parsed = parseExtractOutput('{"company_name":"预算50万，3天答复","demand_desc":"报价：面议"}')
    expect(parsed.fields.company_name).toBe('预算50万，3天答复')
    expect(parsed.fields.demand_desc).toBe('报价：面议')
  })

  it('unwraps single-key object wrappers and normalizes Chinese keys inside', () => {
    const wrapped = JSON.stringify({ 抽取结果: { 公司名称: '甲公司', 联系人: '王' } })
    const parsed = parseExtractOutput(wrapped)
    expect(parsed.fields.company_name).toBe('甲公司')
    expect(parsed.fields.contact_name).toBe('王')
  })

  it('emits unrecognized-key notes so operators can see the drift', () => {
    const parsed = parseExtractOutput('{"公司名称":"甲公司","未知键":"值"}')
    expect(parsed.fields.company_name).toBe('甲公司')
    expect(parsed.notes).toContain('未知键')
  })

  it('drops unknown decision roles and model notes into the note line', () => {
    const parsed = parseExtractOutput('{"company_name":"甲公司","decision_role":"看门人","notes":"预算未提及"}')
    expect(parsed.fields.decision_role).toBeUndefined()
    expect(parsed.notes).toContain('预算未提及')
    expect(parsed.notes).toContain('不在已知取值中')
  })

  it('reports the model keys when company_name is missing', () => {
    const empty = parseExtractOutput('{}')
    expect(empty.fields.company_name).toBeUndefined()
    expect(empty.notes).toContain('（无）')
    const drifted = parseExtractOutput('{"闲聊":"只有闲聊"}')
    expect(drifted.notes).toContain('闲聊')
    expect(drifted.notes).toContain('未识别 company_name')
  })

  it('stops descending when the sole wrapper value is not an object', () => {
    const scalar = parseExtractOutput('{"包装":"纯文本"}')
    expect(scalar.fields.company_name).toBeUndefined()
    expect(scalar.notes).toContain('包装')
    const listed = parseExtractOutput('{"包装":["甲公司"]}')
    expect(listed.fields.company_name).toBeUndefined()
  })
})

describe('parseScoreOutput repair integration', () => {
  const profile = {
    id: 'p', name: '画像', industry: '测试',
    dimensions: [{ id: 'a', name: '维度A', description: 'd', weight: 100 }],
    enabled: true, created_at: 1, updated_at: 1,
  } as never

  it('recovers from in-string newlines via repairJsonBody', () => {
    const raw = '{"items":[{"dimension_id":"a","score":85,\n"reason":"多行\n理由"}],"reason":"整体"}'
    const parsed = parseScoreOutput(raw, profile as never)
    expect(parsed.total).toBe(85)
    expect(parsed.reason).toBe('整体')
  })

  it('recovers from full-width structural separators', () => {
    const raw = '{"items"：[{"dimension_id"："a"，"score"：85，"reason"："r"}]，"reason"："整体"}'
    const parsed = parseScoreOutput(raw, profile as never)
    expect(parsed.total).toBe(85)
  })
})

describe('SOP scope guard mirror', () => {
  const lead = { owner_id: undefined, company_name: '公海' } as never
  const ownOperator = {
    userId: 'u', displayName: 'n',
    capabilities: { lead_scope: 'own', can_manage_global_templates: false, can_delete_any_lead: false, can_export: false, can_manage_settings: false },
  } as never
  it('blocks pool and other-owned leads for copy and SOP generation alike', () => {
    expect(() => assertSopScope(lead, ownOperator)).toThrow('先领取')
    expect(() => assertSopScope({ ...lead, owner_id: 'u2' } as never, ownOperator)).toThrow('无权为他人线索')
  })
})
