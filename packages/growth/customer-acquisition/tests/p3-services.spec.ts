import { afterEach, beforeEach, describe, expect, it } from 'vitest'
import { completionReturning, mockClock, setupP1, FULL_OPERATOR, OWN_OPERATOR, OWN_OPERATOR_2 } from './helpers-p1.ts'
import type { P1Harness } from './helpers-p1.ts'
import { NurtureContentService, assertCopyScope } from '../src/content/service.ts'
import { SopService, assertSopScope, cadenceOffsets } from '../src/sop/service.ts'
import { SEED_IDS } from '../src/scoring/seed.ts'

/** A lead owned by FULL with a scored intent level, over seeded retail templates. */
async function scoredRetailLead(p1: P1Harness, company = '评分线索公司'): Promise<string> {
  await p1.scoring.seedTemplates()
  const retail = p1.scoring.listIcpProfiles().find(candidate => candidate.industry === '实体门店')
  if (retail === undefined) throw new Error('seed missing retail profile')
  p1.setCompletion(completionReturning(JSON.stringify({
    items: retail.dimensions.map(dimension => ({ dimension_id: dimension.id, score: 70, reason: 'r' })),
    reason: '整体',
  })))
  const lead = await p1.ledger.createLead({ company_name: company, industry: '实体门店' }, FULL_OPERATOR, 'agent')
  await p1.scoring.scoreOne({ lead_id: lead.id }, FULL_OPERATOR, 'agent')
  return lead.id
}

describe('P3 nurture-copy service', () => {
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

  function contentOf(answer: string): NurtureContentService {
    const { ctx } = p1.harness
    return new NurtureContentService({
      ctx,
      domain: p1.harness.service.requireDomain(),
      audit: p1.harness.service.requireAuditTable(),
      ledger: p1.ledger,
      policy: p1.policy,
      completionFactory: () => ({ complete: async () => answer }),
    })
  }

  it('generates through the seeded template chain and persists the artifact', async () => {
    await p1.scoring.seedTemplates()
    const leadId = await scoredRetailLead(p1)
    const content = contentOf('王老板您好，这是为幸福奶茶店定制的企微开场白。')
    const outcome = await content.generate({
      lead_id: leadId, type: 'wecom_first_touch', variant: 'A',
    }, FULL_OPERATOR, 'agent')
    expect(outcome.content.content).toContain('幸福奶茶店')
    expect(outcome.content.template_id).toBe(SEED_IDS.retailContentWecom)
    const listed = content.listByLead(leadId, FULL_OPERATOR, undefined)
    expect(listed.total).toBe(1)
    const byType = content.listByLead(leadId, FULL_OPERATOR, 'sms_followup')
    expect(byType.total).toBe(0)

    // Unknown channel type falls to the default guide; a second artifact
    // exercises the list sort comparator.
    const custom = await content.generate({
      lead_id: leadId, type: 'custom_channel', variant: 'B',
    }, FULL_OPERATOR, 'agent')
    expect(custom.content.type).toBe('custom_channel')
    const second = await content.generate({
      lead_id: leadId, type: 'wecom_first_touch', variant: 'B',
    }, FULL_OPERATOR, 'agent')
    const ordered = content.listByLead(leadId, FULL_OPERATOR, undefined)
    expect(ordered.items[0]?.id).toBe(second.content.id)
    const audit = [...p1.harness.service.requireAuditTable().entries()].map(([, record]) => record)
    expect(audit.find(record => record.action === 'content.generate')?.summary).toContain('wecom_first_touch')
  })

  it('generates freeform when no template of the type exists, and honors explicit ids', async () => {
    const leadId = await scoredRetailLead(p1)
    const freeform = contentOf('自由生成的短视频脚本。')
    const outcome = await freeform.generate({
      lead_id: leadId, type: 'short_video_script', variant: 'B',
    }, FULL_OPERATOR, 'agent')
    expect(outcome.content.template_id).toBeUndefined()

    const created = await contentOf('x').createTemplate({
      name: '专用模板', type: 'sms_followup', body: '{{contact_name}}您好',
    }, FULL_OPERATOR, 'agent')
    const viaExplicit = contentOf('短信正文。')
    const explicit = await viaExplicit.generate({
      lead_id: leadId, type: 'sms_followup', variant: 'A', template_id: created.id,
    }, FULL_OPERATOR, 'agent')
    expect(explicit.content.template_id).toBe(created.id)
    await expect(viaExplicit.generate({
      lead_id: leadId, type: 'sms_followup', variant: 'A', template_id: 'missing',
    }, FULL_OPERATOR, 'agent')).rejects.toThrow('文案模板不存在')
  })

  it('scope-blocks pool and other-owned leads for copy generation', async () => {
    const leadId = await scoredRetailLead(p1, '他人文案公司')
    const pooled = { ...p1.ledger.getLead(leadId, FULL_OPERATOR), owner_id: undefined }
    expect(() =>{  assertCopyScope(pooled, OWN_OPERATOR) }).toThrow('先领取')
    expect(() =>{  assertCopyScope(
      { ...pooled, owner_id: OWN_OPERATOR_2.userId },
      OWN_OPERATOR,
    ) }).toThrow('无权为他人线索生成文案')
  })

  it('manages templates with the reference-protection and audit trail', async () => {
    const content = contentOf('x')
    const template = await content.createTemplate({ name: '模板甲', type: 'sms_followup', body: '{{contact_name}}您好' }, FULL_OPERATOR, 'agent')
    await expect(content.createTemplate({ name: ' ', type: 'sms', body: 'x' }, FULL_OPERATOR, 'agent')).rejects.toThrow('模板名称不能为空')
    await expect(content.createTemplate({ name: '甲', type: ' ', body: 'x' }, FULL_OPERATOR, 'agent')).rejects.toThrow('文案类型不能为空')
    await expect(content.createTemplate({ name: '甲', type: 'sms', body: ' ' }, FULL_OPERATOR, 'agent')).rejects.toThrow('模板正文不能为空')

    const generated = await content.generate({
      lead_id: (await p1.ledger.createLead({ company_name: '引用公司' }, FULL_OPERATOR, 'agent')).id,
      type: 'sms_followup', variant: 'A', template_id: template.id,
    }, FULL_OPERATOR, 'agent')
    expect(generated.content.template_id).toBe(template.id)

    await expect(content.deleteTemplate(template.id, FULL_OPERATOR, 'agent')).rejects.toThrow('已被生成产物引用')
    const updated = await content.updateTemplate(template.id, { name: '模板乙', body: '新正文 {{company_name}}' }, FULL_OPERATOR, 'agent')
    expect(updated.body).toContain('新正文')
    expect(content.listTemplates({ enabledOnly: true })).toHaveLength(1)
    expect(content.listTemplates({ type: 'wecom_first_touch' })).toHaveLength(0)
    await content.updateTemplate(template.id, { enabled: false }, FULL_OPERATOR, 'agent')
    expect(content.listTemplates({ enabledOnly: true })).toHaveLength(0)
    await expect(content.updateTemplate(template.id, {}, OWN_OPERATOR, 'agent')).rejects.toThrow('can_manage_global_templates')
  })
})

describe('P3 SOP service', () => {
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

  function sopOf(): SopService {
    return new SopService({
      domain: p1.harness.service.requireDomain(),
      audit: p1.harness.service.requireAuditTable(),
      ledger: p1.ledger,
    })
  }

  it('generates tasks from cadence offsets and refuses unscored leads', async () => {
    await p1.scoring.seedTemplates()
    const lead = await p1.ledger.createLead({ company_name: '未打分公司', industry: '实体门店' }, FULL_OPERATOR, 'agent')
    await expect(sopOf().generateTasks({ lead_id: lead.id }, FULL_OPERATOR, 'agent')).rejects.toThrow('尚未打分')

    const scored = await p1.ledger.createLead({ company_name: '已打分公司', industry: '实体门店' }, FULL_OPERATOR, 'agent')
    await p1.ledger.applyIntent(scored.id, 'high')
    const outcome = await sopOf().generateTasks({ lead_id: scored.id }, FULL_OPERATOR, 'agent')
    expect(outcome.intentLevel).toBe('high')
    expect(outcome.tasks.length).toBeGreaterThanOrEqual(3)
    expect(outcome.tasks[0]?.todoWritten).toBe(false)
    expect(outcome.todoWriteEnabled).toBe(true)
    expect(outcome.todoList[0]?.content).toContain('已打分公司')

    const planned = outcome.tasks.map(({ task }) => task.planned_at)
    expect(planned[0]).toBeLessThan(planned[1] ?? planned[0] + 1)
    const audit = [...p1.harness.service.requireAuditTable().entries()].map(([, record]) => record)
    expect(audit.find(record => record.action === 'sop.tasks.generate')?.summary).toContain('high')
  })

  it('lists and flows tasks with scope checks', async () => {
    await p1.scoring.seedTemplates()
    const lead = await p1.ledger.createLead({ company_name: '流转公司', industry: '实体门店' }, FULL_OPERATOR, 'agent')
    await p1.ledger.applyIntent(lead.id, 'high')
    const outcome = await sopOf().generateTasks({ lead_id: lead.id }, FULL_OPERATOR, 'agent')

    const listed = sopOf().listTasks({ lead_id: lead.id, status: 'pending' }, FULL_OPERATOR)
    expect(listed.total).toBe(outcome.tasks.length)
    expect(sopOf().listTasks({ status: 'done' }, FULL_OPERATOR).total).toBe(0)

    const taskId = outcome.tasks[0]?.task.id ?? 'missing'
    const done = await sopOf().updateTask(taskId, { status: 'done', note: '已完成' }, FULL_OPERATOR, 'agent')
    expect(done.status).toBe('done')
    expect(sopOf().listTasks({ status: 'done' }, FULL_OPERATOR).total).toBe(1)

    const ownLead = await p1.ledger.createLead({ company_name: '员工任务线索' }, OWN_OPERATOR, 'agent')
    await p1.ledger.applyIntent(ownLead.id, 'high')
    const ownOutcome = await sopOf().generateTasks({ lead_id: ownLead.id }, OWN_OPERATOR, 'agent')
    const ownTaskId = ownOutcome.tasks[0]?.task.id ?? 'x'
    const otherLead = await p1.ledger.createLead({ company_name: '他人任务线索' }, FULL_OPERATOR, 'agent')
    await p1.ledger.applyIntent(otherLead.id, 'high')
    const otherOutcome = await sopOf().generateTasks({ lead_id: otherLead.id }, FULL_OPERATOR, 'agent')
    const otherTaskId = otherOutcome.tasks[0]?.task.id ?? 'x'
    await expect(sopOf().updateTask(otherTaskId, { status: 'done' }, OWN_OPERATOR, 'agent'))
      .rejects.toThrow('无权访问该线索')
    expect(taskId).toBeTruthy()
    expect(ownTaskId).toBeTruthy()
  })

  it('manages SOP templates with the cadence parser', () => {
    expect(cadenceOffsets('D+0 微信问候，D+3 到店，D+10 复盘')).toEqual([0, 3, 10])
    expect(cadenceOffsets('没有偏移的节奏')).toEqual([])
  })

  it('manages SOP template CRUD end to end', async () => {
    const sop = sopOf()
    const template = await sop.createTemplate({
      name: '模板甲', industry: '餐饮',
      rules: [{ intent_level: 'high', cadence: 'D+0 电话', points: ['要点一'], questions: ['问一'], risks: ['险一'] }],
    }, FULL_OPERATOR, 'agent')
    expect(template.enabled).toBe(true)
    await expect(sop.updateTemplate(template.id, { name: ' ' }, FULL_OPERATOR, 'agent')).rejects.toThrow('模板名称不能为空')
    const unchanged = await sop.updateTemplate(template.id, {}, FULL_OPERATOR, 'agent')
    expect(unchanged.name).toBe('模板甲')
    const updated = await sop.updateTemplate(template.id, { name: '模板乙' }, FULL_OPERATOR, 'agent')
    expect(updated.name).toBe('模板乙')
    expect(sop.listTemplates(true)).toHaveLength(1)
    await sop.updateTemplate(template.id, { enabled: false }, FULL_OPERATOR, 'agent')
    expect(sop.listTemplates(true)).toHaveLength(0)
    await sop.deleteTemplate(template.id, FULL_OPERATOR, 'agent')
    expect(sop.listTemplates()).toHaveLength(0)
    await expect(sop.createTemplate({ name: ' ', rules: template.rules }, FULL_OPERATOR, 'agent')).rejects.toThrow('模板名称不能为空')
    const audit = [...p1.harness.service.requireAuditTable().entries()].map(([, record]) => record)
    expect(audit.map(record => record.action)).toEqual(expect.arrayContaining([
      'sop_template.create', 'sop_template.update', 'sop_template.delete',
    ]))
  })

  it('scope-blocks pool and other-owned leads for task generation', () => {
    const pooled = { id: 'l1', owner_id: undefined, company_name: '公海公司' } as never
    expect(() =>{  assertSopScope(pooled, OWN_OPERATOR) }).toThrow('先领取')
    expect(() =>{  assertSopScope({ ...pooled, owner_id: OWN_OPERATOR_2.userId } as never, OWN_OPERATOR) }).toThrow('无权为他人线索生成跟进任务')
  })
})

describe('P3 seeds carry SOP and copy templates', () => {
  it('seeds three SOP packs and six copy packs idempotently', async () => {
    const p1 = await setupP1(completionReturning('{}'))
    try {
      await p1.scoring.seedTemplates()
      const domain = p1.harness.service.requireDomain()
      expect([...domain.table('sop_templates').entries()]).toHaveLength(3)
      expect([...domain.table('content_templates').entries()]).toHaveLength(6)
      await p1.scoring.seedTemplates()
      expect([...domain.table('sop_templates').entries()]).toHaveLength(3)
      expect([...domain.table('content_templates').entries()]).toHaveLength(6)
      const sop = [...domain.table('sop_templates').entries()].map(([, template]) => template)
      expect(sop.every(template => template.rules.some(rule => rule.intent_level === 'high'))).toBe(true)
    } finally {
      await p1.harness.dispose()
    }
  })
})
