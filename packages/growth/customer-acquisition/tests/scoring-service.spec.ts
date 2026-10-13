import { afterEach, beforeEach, describe, expect, it } from 'vitest'
import {
  completionReturning, mockClock, scoreJsonFor, setupP1, FULL_OPERATOR, OWN_OPERATOR, OWN_OPERATOR_2,
} from './helpers-p1.ts'
import type { P1Harness } from './helpers-p1.ts'
import { SEED_IDS } from '../src/scoring/seed.ts'
import { LeadScoringService } from '../src/scoring/service.ts'
import { intentTagFor, parseScoreOutput, SCORE_INTENT_HIGH_MIN, SCORE_INTENT_LOW_MIN, SCORE_INTENT_MID_MIN } from '../src/scoring/evaluate.ts'
import { aggregateKnowledge, renderScorePrompt, KNOWLEDGE_INJECT_MAX_CHARS } from '../src/scoring/prompt.ts'
import { resolveAiPolicy } from '../src/llm/oneshot.ts'
import type { IcpProfile, Lead, LeadDocument } from '../src/domain/spec.ts'
import type { IcpProfileValue } from '../src/scoring/types.ts'
import { DocumentId, IcpProfileId, LeadId, UserId } from '../src/domain/ids.ts'

async function seedFor(p1: P1Harness): Promise<void> {
  await p1.scoring.seedTemplates()
}

async function makeScoredLead(p1: P1Harness, company = '被评分公司'): Promise<{ lead: Lead; runId: string }> {
  await seedFor(p1)
  const retail = retailProfile(p1)
  p1.setCompletion(completionReturning(scoreJsonFor(retail, 70)))
  const lead = await p1.ledger.createLead({
    company_name: company,
    industry: '实体门店',
    owner_id: FULL_OPERATOR.userId,
  }, FULL_OPERATOR, 'agent')
  const outcome = await p1.scoring.scoreOne({ lead_id: lead.id }, FULL_OPERATOR, 'agent')
  return { lead, runId: outcome.run.id }
}

function retailProfile(p1: P1Harness): IcpProfileValue {
  const profile = p1.scoring.listIcpProfiles().find(candidate => candidate.industry === '实体门店')
  if (profile === undefined) throw new Error('seed missing retail profile')
  return profile
}

describe('P1 industry seeds', () => {
  let p1: P1Harness
  let stopClock: () => void

  beforeEach(async () => {
    p1 = await setupP1(completionReturning('{}'))
    stopClock = mockClock()
  })

  afterEach(async () => {
    stopClock()
    await p1.harness.dispose()
  })

  it('seeds three industries once and respects user edits on re-seed', async () => {
    await seedFor(p1)
    const profiles = p1.scoring.listIcpProfiles()
    expect(profiles.map(profile => profile.id).sort()).toEqual([
      SEED_IDS.b2bTradeIcp, SEED_IDS.retailIcp, SEED_IDS.softwareIcp,
    ].sort())
    for (const profile of profiles) {
      const total = profile.dimensions.reduce((sum, dimension) => sum + dimension.weight, 0)
      expect(total).toBe(100)
      expect(profile.enabled).toBe(true)
    }
    expect(p1.scoring.listScoreTemplates()).toHaveLength(3)
    expect(p1.scoring.listIcpProfiles(true)).toHaveLength(3)
    expect(p1.scoring.listScoreTemplates(true)).toHaveLength(3)

    await p1.scoring.updateIcpProfile(SEED_IDS.retailIcp, { name: '用户改过的画像' }, FULL_OPERATOR, 'agent')
    await seedFor(p1)
    expect(p1.scoring.listIcpProfiles().find(profile => profile.id === SEED_IDS.retailIcp)?.name).toBe('用户改过的画像')
    expect(p1.scoring.listIcpProfiles()).toHaveLength(3)
  })
})

describe('P1 ICP profile and template CRUD', () => {
  let p1: P1Harness
  let stopClock: () => void

  beforeEach(async () => {
    p1 = await setupP1(completionReturning('{}'))
    stopClock = mockClock()
  })

  afterEach(async () => {
    stopClock()
    await p1.harness.dispose()
  })

  it('creates profiles with defaults and rejects bad weights and duplicate ids', async () => {
    const profile = await p1.scoring.createIcpProfile({
      name: '测试画像',
      dimensions: [
        { id: 'a', name: '维度 A', description: '说明', weight: 60 },
        { id: 'b', name: '维度 B', description: '说明', weight: 40 },
      ],
    }, FULL_OPERATOR, 'agent')
    expect(profile.enabled).toBe(true)

    await expect(p1.scoring.createIcpProfile({
      name: '坏权重',
      dimensions: [{ id: 'a', name: 'A', description: 'x', weight: 90 }],
    }, FULL_OPERATOR, 'agent')).rejects.toThrow('合计为 100')

    await expect(p1.scoring.createIcpProfile({
      name: '重复 id',
      dimensions: [
        { id: 'a', name: 'A', description: 'x', weight: 50 },
        { id: 'a', name: 'B', description: 'y', weight: 50 },
      ],
    }, FULL_OPERATOR, 'agent')).rejects.toThrow('维度 id 重复')

    await expect(p1.scoring.createIcpProfile({
      name: '超界',
      dimensions: [{ id: 'a', name: 'A', description: 'x', weight: 120 }],
    }, FULL_OPERATOR, 'agent')).rejects.toThrow('0-100')
  })

  it('updates profiles and lists enabled-only', async () => {
    const profile = await p1.scoring.createIcpProfile({
      name: '旧名',
      industry: '餐饮',
      dimensions: [{ id: 'a', name: 'A', description: 'x', weight: 100 }],
      enabled: true,
    }, FULL_OPERATOR, 'agent')
    const renamed = await p1.scoring.updateIcpProfile(profile.id, { name: '新名' }, FULL_OPERATOR, 'agent')
    expect(renamed.name).toBe('新名')

    const replaced = await p1.scoring.updateIcpProfile(profile.id, {
      dimensions: [
        { id: 'x', name: 'X', description: 'y', weight: 50 },
        { id: 'z', name: 'Z', description: 'w', weight: 50 },
      ],
    }, FULL_OPERATOR, 'agent')
    expect(replaced.dimensions.map(dimension => dimension.id).sort()).toEqual(['x', 'z'])

    await expect(p1.scoring.updateIcpProfile(profile.id, {
      dimensions: [{ id: 'x', name: 'X', description: 'y', weight: 30 }],
    }, FULL_OPERATOR, 'agent')).rejects.toThrow('合计为 100')
    await expect(p1.scoring.updateIcpProfile('missing', { name: 'N' }, FULL_OPERATOR, 'agent')).rejects.toThrow('不存在')

    await p1.scoring.updateIcpProfile(profile.id, { enabled: false }, FULL_OPERATOR, 'agent')
    expect(p1.scoring.listIcpProfiles(true)).toHaveLength(0)
    expect(p1.scoring.listIcpProfiles()).toHaveLength(1)
  })

  it('gates template writes behind can_manage_global_templates and audits', async () => {
    await expect(p1.scoring.createIcpProfile({
      name: '无权',
      dimensions: [{ id: 'a', name: 'A', description: 'x', weight: 100 }],
    }, OWN_OPERATOR, 'agent')).rejects.toThrow('can_manage_global_templates')

    const template = await p1.scoring.createScoreTemplate({
      name: '模板一',
      prompt_text: '评估 {{lead}}',
    }, FULL_OPERATOR, 'agent')
    expect(template.prompt_text).toBe('评估 {{lead}}')
    const updated = await p1.scoring.updateScoreTemplate(template.id, { prompt_text: '评估 {{lead}} {{knowledge}}' }, FULL_OPERATOR, 'agent')
    expect(updated.prompt_text).toContain('{{knowledge}}')
    await p1.scoring.updateScoreTemplate(template.id, { enabled: false }, FULL_OPERATOR, 'agent')
    expect(p1.scoring.listScoreTemplates(true)).toHaveLength(0)
    expect(p1.scoring.listScoreTemplates()).toHaveLength(1)
    // A scored run referencing another template makes the deletion guard scan
    // a non-empty run table; the unreferenced template still deletes cleanly.
    await makeScoredLead(p1, '扫描用线索')
    await p1.scoring.deleteScoreTemplate(template.id, FULL_OPERATOR, 'agent')
    expect(p1.scoring.listScoreTemplates().find(candidate => candidate.id === template.id)).toBeUndefined()
    const actions = [...p1.harness.service.requireAuditTable().entries()].map(([, record]) => record.action)
    expect(actions).toEqual(expect.arrayContaining(['score_template.create', 'score_template.update', 'score_template.delete']))
  })

  it('delete protection: referenced profiles and templates are rejected', async () => {
    const { runId } = await makeScoredLead(p1)
    expect(runId).toBeTruthy()
    const run = [...p1.harness.service.requireDomain().table('score_runs').entries()].map(([, value]) => value)[0]
    if (run === undefined) throw new Error('score run row missing')
    await expect(p1.scoring.deleteIcpProfile(run.icp_profile_id, FULL_OPERATOR, 'agent')).rejects.toThrow('已被打分历史引用')
    await expect(p1.scoring.deleteScoreTemplate(run.template_id, FULL_OPERATOR, 'agent')).rejects.toThrow('已被打分历史引用')

    const unreferenced = await p1.scoring.createIcpProfile({
      name: '无引用',
      dimensions: [{ id: 'a', name: 'A', description: 'x', weight: 100 }],
    }, FULL_OPERATOR, 'agent')
    await p1.scoring.deleteIcpProfile(unreferenced.id, FULL_OPERATOR, 'agent')
    expect(p1.scoring.listIcpProfiles().find(profile => profile.id === unreferenced.id)).toBeUndefined()
  })
})

describe('P1 scoring flows', () => {
  let p1: P1Harness
  let stopClock: () => void

  beforeEach(async () => {
    p1 = await setupP1(completionReturning('{}'))
    stopClock = mockClock()
  })

  afterEach(async () => {
    stopClock()
    await p1.harness.dispose()
  })

  it('score_one resolves industry-matched seeds, persists the run, and writes intent back', async () => {
    await seedFor(p1)
    const lead = await p1.ledger.createLead({ company_name: '幸福奶茶店', industry: '实体门店' }, FULL_OPERATOR, 'agent')
    p1.setCompletion({ complete: async (prompt) => {
      const profile = await Promise.resolve(prompt)
      expect(profile).toContain('幸福奶茶店')
      expect(profile).toContain('budget_scale')
      return JSON.stringify({
        items: [
          { dimension_id: 'budget_scale', score: 90, reason: '预算充足' },
          { dimension_id: 'demand_urgency', score: 80, reason: '急于引流' },
          { dimension_id: 'business_fit', score: 70, reason: '业态匹配' },
          { dimension_id: 'decision_role', score: 60, reason: '店长' },
          { dimension_id: 'reachability', score: 40, reason: '仅微信' },
        ],
        reason: '整体较匹配',
      })
    } })
    const outcome = await p1.scoring.scoreOne({ lead_id: lead.id }, FULL_OPERATOR, 'agent')
    expect(outcome.run.total).toBe(71.5)
    expect(outcome.run.intent_tag).toBe('mid')
    expect(outcome.items).toHaveLength(5)
    expect(outcome.items.find(item => item.dimension_id === 'budget_scale')?.name).toBe('预算规模')

    const scored = p1.ledger.getLead(lead.id, FULL_OPERATOR)
    expect(scored.intent_level).toBe('mid')

    const audit = [...p1.harness.service.requireAuditTable().entries()].map(([, record]) => record)
      .find(record => record.action === 'score.run')
    expect(audit?.object_type).toBe('score_run')
    expect(audit?.summary).toContain('71.5')
  })

  it('score_one validates the model answer strictly', async () => {
    await seedFor(p1)
    const lead = await p1.ledger.createLead({ company_name: '严格公司', industry: '实体门店' }, FULL_OPERATOR, 'agent')
    p1.setCompletion(completionReturning('这不是 JSON'))
    await expect(p1.scoring.scoreOne({ lead_id: lead.id }, FULL_OPERATOR, 'agent')).rejects.toThrow('JSON')

    p1.setCompletion(completionReturning(JSON.stringify({
      items: [{ dimension_id: 'budget_scale', score: 50, reason: 'r' }],
      reason: '缺维度',
    })))
    await expect(p1.scoring.scoreOne({ lead_id: lead.id }, FULL_OPERATOR, 'agent')).rejects.toThrow('缺少维度')

    p1.setCompletion(completionReturning(JSON.stringify({
      items: [{ dimension_id: 'budget_scale', score: 250, reason: 'r' }],
      reason: '超界',
    })))
    await expect(p1.scoring.scoreOne({ lead_id: lead.id }, FULL_OPERATOR, 'agent')).rejects.toThrow('0-100')
  })

  it('score_one scope: own operators cannot score others or pool leads', async () => {
    const { lead } = await makeScoredLead(p1, '别人的线索')
    await expect(p1.scoring.scoreOne({ lead_id: lead.id }, OWN_OPERATOR, 'agent')).rejects.toThrow('无权访问该线索')

    await p1.ledger.transferLead(lead.id, undefined, FULL_OPERATOR, 'agent')
    await expect(p1.scoring.scoreOne({ lead_id: lead.id }, OWN_OPERATOR, 'agent')).rejects.toThrow('先领取')
  })

  it('score_one falls back through default → industry → industry-absent → any', async () => {
    await seedFor(p1)
    const custom = await p1.scoring.createIcpProfile({
      name: '通用画像',
      dimensions: [{ id: 'fit', name: '匹配', description: '综合匹配', weight: 100 }],
      enabled: false,
    }, FULL_OPERATOR, 'agent')
    const software = p1.scoring.listIcpProfiles().find(candidate => candidate.id === SEED_IDS.softwareIcp)
    if (software === undefined) throw new Error('seed missing software profile')

    const noIndustryLead = await p1.ledger.createLead({ company_name: '无行业公司' }, FULL_OPERATOR, 'agent')
    // The wire run projection carries no profile id; the resolved profile is
    // identifiable through the dimensions rendered into the prompt instead.
    const prompts: string[] = []
    const capture = (answer: string): void => {
      p1.setCompletion({ complete: async (prompt) => { prompts.push(prompt); return answer } })
    }
    const lastPrompt = (): string => prompts.at(-1) ?? ''

    // All seeds carry an industry, so the un-industried lead falls through to
    // the oldest enabled profile (retail, seeded first).
    capture(scoreJsonFor(retailProfile(p1), 70))
    await p1.scoring.scoreOne({ lead_id: noIndustryLead.id }, FULL_OPERATOR, 'agent')
    expect(lastPrompt()).toContain('预算规模')

    await p1.harness.service.updateSettings({ default_icp_profile_id: custom.id }, FULL_OPERATOR, 'agent')
    capture(scoreJsonFor(retailProfile(p1), 70))
    await p1.scoring.scoreOne({ lead_id: noIndustryLead.id }, FULL_OPERATOR, 'agent')
    expect(lastPrompt()).toContain('预算规模')

    await p1.scoring.updateIcpProfile(custom.id, { enabled: true }, FULL_OPERATOR, 'agent')
    capture(scoreJsonFor(custom, 70))
    await p1.scoring.scoreOne({ lead_id: noIndustryLead.id }, FULL_OPERATOR, 'agent')
    expect(lastPrompt()).toContain('综合匹配')

    capture(scoreJsonFor(software, 70))
    await p1.scoring.scoreOne({ lead_id: noIndustryLead.id, icp_profile_id: SEED_IDS.softwareIcp }, FULL_OPERATOR, 'agent')
    expect(lastPrompt()).toContain('tech_fit')

    await expect(p1.scoring.scoreOne({ lead_id: noIndustryLead.id, icp_profile_id: 'missing' }, FULL_OPERATOR, 'agent'))
      .rejects.toThrow('ICP 画像不存在')
  })

  it('score_batch runs serially, isolates failures, and audits once', async () => {
    const { lead } = await makeScoredLead(p1, '批量一')
    const other = await p1.ledger.createLead({ company_name: '批量二', industry: '实体门店' }, FULL_OPERATOR, 'agent')

    const batch = await p1.scoring.scoreBatch({
      lead_ids: [lead.id, other.id, 'missing-lead'],
    }, FULL_OPERATOR, 'agent')
    expect(batch.runs).toHaveLength(2)
    expect(batch.failed).toEqual([expect.objectContaining({ lead_id: 'missing-lead' })])
    expect(p1.ledger.getLead(other.id, FULL_OPERATOR).intent_level).toBeDefined()

    const batchAudits = [...p1.harness.service.requireAuditTable().entries()]
      .map(([, record]) => record)
      .filter(record => record.action === 'score.batch')
    expect(batchAudits).toHaveLength(1)
    expect(batchAudits[0]?.summary).toContain('成功 2/共 3')

    await expect(p1.scoring.scoreBatch({ lead_ids: [lead.id, lead.id] }, FULL_OPERATOR, 'agent')).rejects.toThrow('重复')
    await expect(p1.scoring.scoreBatch({ lead_ids: Array.from({ length: 51 }, () => lead.id) }, FULL_OPERATOR, 'agent'))
      .rejects.toThrow('1-50')
  })

  it('history retains runs with weight snapshots and respects scope', async () => {
    const { lead, runId } = await makeScoredLead(p1, '历史线索')
    const before = p1.scoring.history({ lead_id: lead.id }, FULL_OPERATOR).items[0]
    expect(before?.run.id).toBe(runId)
    expect(before?.items).toHaveLength(5)

    await p1.scoring.updateIcpProfile(SEED_IDS.retailIcp, {
      dimensions: SEED_DIMENSIONS,
    }, FULL_OPERATOR, 'agent')
    p1.setCompletion(completionReturning(JSON.stringify({
      items: [{ dimension_id: 'budget_scale', score: 85, reason: '改权重后再评' }],
      reason: '第二次打分',
    })))
    await p1.scoring.scoreOne({ lead_id: lead.id }, FULL_OPERATOR, 'agent')

    const history = p1.scoring.history({ lead_id: lead.id }, FULL_OPERATOR)
    expect(history.total).toBe(2)
    expect(history.items[0]?.run.created_at).toBeGreaterThan(history.items[1]?.run.created_at ?? 0)

    const single = p1.scoring.history({ run_id: runId }, FULL_OPERATOR)
    expect(single.total).toBe(1)

    const ownLead = await p1.ledger.createLead({ company_name: '员工线索' }, OWN_OPERATOR, 'agent')
    await p1.scoring.scoreOne({ lead_id: ownLead.id }, OWN_OPERATOR, 'agent')
    const ownView = p1.scoring.history({}, OWN_OPERATOR)
    expect(ownView.items.map(entry => entry.run.lead_id)).toEqual([ownLead.id])

    const poolView = p1.scoring.history({}, OWN_OPERATOR_2)
    expect(poolView.total).toBe(0)
  })
})

describe('P1 scoring prompt and evaluation pure functions', () => {
  const profile: IcpProfile = {
    id: IcpProfileId('p1'),
    name: '画像',
    industry: '测试',
    dimensions: [
      { id: 'a', name: '维度A', description: '说明A', weight: 60 },
      { id: 'b', name: '维度B', description: '说明B', weight: 40 },
    ],
    enabled: true,
    created_at: 1,
    updated_at: 1,
  }
  const lead: Lead = {
    id: LeadId('l1'),
    owner_id: UserId('u1'),
    source: 'manual',
    company_name: '测试公司',
    tags: [],
    opportunity_stage: 'new',
    status: 'active',
    created_at: 1,
    updated_at: 1,
  }

  it('renders all placeholders and drops unknown ones', () => {
    const rendered = renderScorePrompt('画像：{{icp_profile}} 维度：{{dimensions}} 线索：{{lead}} 资料：{{knowledge}} 未知：{{nope}}', {
      lead,
      profile,
      knowledge: '补充资料',
    })
    expect(rendered).toContain('画像')
    expect(rendered).toContain('维度A（权重 60%）')
    expect(rendered).toContain('测试公司')
    expect(rendered).toContain('补充资料')
    expect(rendered).not.toContain('{{nope}}')
    expect(rendered).not.toContain('{{')
  })

  it('aggregates knowledge with the truncation mark', () => {
    const documents: LeadDocument[] = [
      { id: DocumentId('d1'), lead_id: LeadId('l1'), title: '资料一', content: '内容一', created_at: 2, updated_at: 2 },
      { id: DocumentId('d2'), lead_id: LeadId('l1'), title: '资料二', content: '内容二', created_at: 1, updated_at: 1 },
    ]
    const block = aggregateKnowledge(documents)
    expect(block.indexOf('资料二')).toBeLessThan(block.indexOf('资料一'))
    expect(block).toContain('内容一')

    const big: LeadDocument[] = [{
      id: DocumentId('d3'), lead_id: LeadId('l1'), title: '大部头', content: 'x'.repeat(KNOWLEDGE_INJECT_MAX_CHARS + 500),
      created_at: 1, updated_at: 1,
    }]
    const truncated = aggregateKnowledge(big)
    expect(truncated.length).toBeLessThanOrEqual(KNOWLEDGE_INJECT_MAX_CHARS + 20)
    expect(truncated).toContain('[已截断]')
  })

  it('parses scores, computes the weighted total, and maps intent thresholds', () => {
    const parsed = parseScoreOutput(JSON.stringify({
      items: [
        { dimension_id: 'a', score: 80, reason: 'A 理由' },
        { dimension_id: 'b', score: 90.4, reason: 'B 理由' },
      ],
      reason: '整体良好',
    }), profile)
    expect(parsed.total).toBe(84.16)
    expect(intentTagFor(parsed.total)).toBe('high')

    expect(SCORE_INTENT_HIGH_MIN).toBe(80)
    expect(SCORE_INTENT_MID_MIN).toBe(60)
    expect(SCORE_INTENT_LOW_MIN).toBe(30)
    expect(intentTagFor(80)).toBe('high')
    expect(intentTagFor(79.99)).toBe('mid')
    expect(intentTagFor(60)).toBe('mid')
    expect(intentTagFor(30)).toBe('low')
    expect(intentTagFor(29.99)).toBe('invalid')
    expect(intentTagFor(0)).toBe('invalid')

    expect(() => parseScoreOutput('{"items":[],"reason":"空"}', profile)).toThrow('缺少维度 a')
    expect(() => parseScoreOutput('{"items":[{"dimension_id":"a","score":50}],"reason":"r"}', profile)).toThrow('理由')
    expect(() => parseScoreOutput('{"items":[{"dimension_id":"zzz","score":50,"reason":"r"}],"reason":"r"}', profile)).toThrow('未知维度')
    expect(parseScoreOutput('{"items":[{"dimension_id":"a","score":50,"reason":"r"},{"dimension_id":"b","score":50,"reason":"r"}],"reason":"r"}', profile).total).toBe(50)
  })

  it('resolves the declared AI policy with bounds', () => {
    expect(resolveAiPolicy(undefined)).toEqual({ provider: 'deepseek', model: 'deepseek-chat', timeoutMs: 120_000, maxOutputTokens: 2000 })
    expect(() => resolveAiPolicy({ timeoutMs: 100 })).toThrow('timeoutMs')
    expect(() => resolveAiPolicy({ maxOutputTokens: 1 })).toThrow('maxOutputTokens')
    expect(resolveAiPolicy({ provider: 'zhipu', model: 'glm-4.6' }).provider).toBe('zhipu')
  })
})


describe('scoring prompt knowledge injection through the service', () => {
  let p1: P1Harness
  let stopClock: () => void

  beforeEach(async () => {
    p1 = await setupP1(completionReturning('{}'))
    stopClock = mockClock()
  })

  afterEach(async () => {
    stopClock()
    await p1.harness.dispose()
  })

  it('builds the default completion over the llm service when no factory is injected', async () => {
    await seedFor(p1)
    const retail = retailProfile(p1)
    const answer = JSON.stringify({
      items: retail.dimensions.map(dimension => ({ dimension_id: dimension.id, score: 70, reason: 'r' })),
      reason: '整体',
    })
    const ctx = {
      llm: {
        stream: () => (async function* replay() {
          yield { type: 'text-delta', index: 0, text: answer }
          yield { type: 'block-end', index: 0, block: { type: 'text', text: answer } }
          yield { type: 'finish', reason: { kind: 'stop' } }
        })(),
      },
    } as never
    const scoring = new LeadScoringService({
      ctx,
      domain: p1.harness.service.requireDomain(),
      audit: p1.harness.service.requireAuditTable(),
      ledger: p1.ledger,
      policy: resolveAiPolicy({ timeoutMs: 5_000, maxOutputTokens: 4_096 }),
    })
    const lead = await p1.ledger.createLead({ company_name: '默认工厂公司', industry: '实体门店' }, FULL_OPERATOR, 'agent')
    const outcome = await scoring.scoreOne({ lead_id: lead.id }, FULL_OPERATOR, 'agent')
    expect(outcome.run.total).toBe(70)
    expect(outcome.items[0]?.weight).toBeGreaterThan(0)
  })

  it('injects the lead documents into the scoring prompt through the service', async () => {
    await seedFor(p1)
    const retail = retailProfile(p1)
    const lead = await p1.ledger.createLead({ company_name: '资料公司', industry: '实体门店' }, FULL_OPERATOR, 'agent')
    await p1.ledger.addDocument(lead.id, '门店档案', '主营奶茶，日流水两万', FULL_OPERATOR, 'agent')
    const captured: string[] = []
    p1.setCompletion({ complete: async (prompt) => {
      captured.push(prompt)
      return JSON.stringify({
        items: retail.dimensions.map(dimension => ({ dimension_id: dimension.id, score: 70, reason: 'r' })),
        reason: '整体',
      })
    } })
    await p1.scoring.scoreOne({ lead_id: lead.id }, FULL_OPERATOR, 'agent')
    expect(captured[0]).toContain('门店档案')
    expect(captured[0]).toContain('主营奶茶')
  })

})


const SEED_DIMENSIONS = [
  { id: 'budget_scale', name: '预算规模', description: '改过的说明', weight: 100 },
]
