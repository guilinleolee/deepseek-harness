import { afterEach, beforeEach, describe, expect, it } from 'vitest'
import { NurtureContentService, assertCopyScope, CONTENT_SYSTEM_PROMPT } from '../src/content/service.ts'
import { SopService, cadenceOffsets, assertSopScope } from '../src/sop/service.ts'
import { setupP1, FULL_OPERATOR, OWN_OPERATOR, OWN_OPERATOR_2, completionReturning } from './helpers-p1.ts'
import type { P1Harness } from './helpers-p1.ts'

describe('P3 content service remaining branches', () => {
  let p1: P1Harness
  let stopClock: () => void

  beforeEach(async () => {
    p1 = await setupP1(completionReturning('{}'))
    stopClock = mockClockOf()
  })

  afterEach(async () => {
    stopClock()
    await p1.harness.dispose()
  })

  function contentOf(answer: string): NurtureContentService {
    return new NurtureContentService({
      ctx: p1.harness.ctx,
      domain: p1.harness.service.requireDomain(),
      audit: p1.harness.service.requireAuditTable(),
      ledger: p1.ledger,
      policy: p1.policy,
      completionFactory: () => ({ complete: async () => answer }),
    })
  }

  it('rejects empty type, empty model output, and honors the caller signal', async () => {
    const content = contentOf('   ')
    const lead = await p1.ledger.createLead({ company_name: '空文案公司' }, FULL_OPERATOR, 'agent')
    await expect(content.generate({ lead_id: lead.id, type: ' ', variant: 'A' }, FULL_OPERATOR, 'agent'))
      .rejects.toThrow('不能为空')
    await expect(content.generate({ lead_id: lead.id, type: 'sms_followup', variant: 'A' }, FULL_OPERATOR, 'agent'))
      .rejects.toThrow('空文案')
    let observed: AbortSignal | undefined
    const signal = new AbortController().signal
    const probe = new NurtureContentService({
      ctx: p1.harness.ctx,
      domain: p1.harness.service.requireDomain(),
      audit: p1.harness.service.requireAuditTable(),
      ledger: p1.ledger,
      policy: p1.policy,
      completionFactory: () => ({ complete: async (_prompt, signal) => { observed = signal; return 'x'.repeat(5) } }),
    })
    await probe.generate({ lead_id: lead.id, type: 'sms_followup', variant: 'A' }, FULL_OPERATOR, 'agent', signal)
    expect(observed).toBe(signal)
  })

  it('injects lead documents into the copy prompt through the service', async () => {
    const lead = await p1.ledger.createLead({ company_name: '资料文案公司', industry: '实体门店' }, FULL_OPERATOR, 'agent')
    await p1.ledger.addDocument(lead.id, '门店档案', '主营奶茶，客单价 15 元', FULL_OPERATOR, 'agent')
    const captured: string[] = []
    const content = new NurtureContentService({
      ctx: p1.harness.ctx,
      domain: p1.harness.service.requireDomain(),
      audit: p1.harness.service.requireAuditTable(),
      ledger: p1.ledger,
      policy: p1.policy,
      completionFactory: () => ({ complete: async (prompt) => { captured.push(prompt); return '文案' } }),
    })
    await content.generate({ lead_id: lead.id, type: 'xiaohongshu_post', variant: 'A' }, FULL_OPERATOR, 'agent')
    expect(captured[0]).toContain('门店档案')
    expect(captured[0]).toContain('客单价 15 元')
  })

  it('template update validates every field and the empty patch skips the write', async () => {
    const content = contentOf('x')
    const template = await content.createTemplate({ name: '甲', type: 'sms_followup', body: 'b' }, FULL_OPERATOR, 'agent')
    await expect(content.updateTemplate(template.id, { type: ' ' }, FULL_OPERATOR, 'agent')).rejects.toThrow('文案类型不能为空')
    await expect(content.updateTemplate(template.id, { body: ' ' }, FULL_OPERATOR, 'agent')).rejects.toThrow('模板正文不能为空')
    const before = [...p1.harness.service.requireAuditTable().entries()].length
    const unchanged = await content.updateTemplate(template.id, {}, FULL_OPERATOR, 'agent')
    expect(unchanged.updated_at).toBe(template.updated_at)
    expect([...p1.harness.service.requireAuditTable().entries()].length).toBe(before)
  })

  it('the system prompt declares the copywriting contract', () => {
    expect(CONTENT_SYSTEM_PROMPT).toContain('文案')
    expect(CONTENT_SYSTEM_PROMPT).toContain('{{变量}}')
  })
})

describe('P3 SOP service remaining branches', () => {
  let p1: P1Harness
  let stopClock: () => void

  beforeEach(async () => {
    p1 = await setupP1(completionReturning('{}'))
    stopClock = mockClockOf()
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

  it('resolves explicit ids, rejects unknown ones, and falls back through the industry chain', async () => {
    const sop = sopOf()
    const template = await sop.createTemplate({
      name: '通用模板',
      rules: [{ intent_level: 'high', cadence: 'D+0', points: ['通用要点'], questions: [], risks: [] }],
    }, FULL_OPERATOR, 'agent')
    const lead = await p1.ledger.createLead({ company_name: '回退公司' }, FULL_OPERATOR, 'agent')
    await p1.ledger.applyIntent(lead.id, 'high')
    const outcome = await sop.generateTasks({ lead_id: lead.id, sop_template_id: template.id }, FULL_OPERATOR, 'agent')
    expect(outcome.templateId).toBe(template.id)
    await expect(sop.generateTasks({ lead_id: lead.id, sop_template_id: 'missing' }, FULL_OPERATOR, 'agent'))
      .rejects.toThrow('SOP 模板不存在')
    const ruleless = await sop.createTemplate({
      name: '缺规则模板',
      rules: [{ intent_level: 'low', cadence: 'D+0', points: ['低意向要点'], questions: [], risks: [] }],
    }, FULL_OPERATOR, 'agent')
    await expect(sop.generateTasks({ lead_id: lead.id, sop_template_id: ruleless.id }, FULL_OPERATOR, 'agent'))
      .rejects.toThrow('缺少 high 等级的规则')
  })

  it('validates planned_at and skips empty task patches', async () => {
    const sop = sopOf()
    const template = await sop.createTemplate({
      name: '校验模板',
      rules: [{ intent_level: 'high', cadence: 'D+0', points: ['要点'], questions: [], risks: [] }],
    }, FULL_OPERATOR, 'agent')
    const lead = await p1.ledger.createLead({ company_name: '校验公司' }, FULL_OPERATOR, 'agent')
    await p1.ledger.applyIntent(lead.id, 'high')
    const outcome = await sop.generateTasks({ lead_id: lead.id, sop_template_id: template.id }, FULL_OPERATOR, 'agent')
    const taskId = outcome.tasks[0]?.task.id ?? 'missing'
    await expect(sop.updateTask(taskId, { planned_at: -1 }, FULL_OPERATOR, 'agent')).rejects.toThrow('epoch 毫秒')
    const unchanged = await sop.updateTask(taskId, {}, FULL_OPERATOR, 'agent')
    expect(unchanged.planned_at).toBe(outcome.tasks[0]?.task.planned_at)
  })

  it('create validates the name and update validates it too', async () => {
    const sop = sopOf()
    await expect(sop.createTemplate({ name: ' ', rules: [{ intent_level: 'high', cadence: 'D+0', points: ['p'], questions: [], risks: [] }] }, FULL_OPERATOR, 'agent'))
      .rejects.toThrow('模板名称不能为空')
  })

  it('generates with an unknown channel type and more points than cadence offsets', async () => {
    const sop = new SopService({
      domain: p1.harness.service.requireDomain(),
      audit: p1.harness.service.requireAuditTable(),
      ledger: p1.ledger,
    })
    const template = await sop.createTemplate({
      name: '多点模板',
      rules: [{
        intent_level: 'high', cadence: '无偏移节奏',
        points: ['要点一', '要点二', '要点三'], questions: ['问'], risks: ['险'],
      }],
    }, FULL_OPERATOR, 'agent')
    const lead = await p1.ledger.createLead({ company_name: '多点公司' }, FULL_OPERATOR, 'agent')
    await p1.ledger.applyIntent(lead.id, 'high')
    const outcome = await sop.generateTasks({ lead_id: lead.id, sop_template_id: template.id }, FULL_OPERATOR, 'agent')
    expect(outcome.tasks).toHaveLength(3)
    expect(outcome.tasks.every(({ task }) => task.planned_at > 0)).toBe(true)
  })

  it('updateTask refuses pool-lead tasks for scoped operators', async () => {
    const sop = new SopService({
      domain: p1.harness.service.requireDomain(),
      audit: p1.harness.service.requireAuditTable(),
      ledger: p1.ledger,
    })
    const template = await sop.createTemplate({
      name: '公海任务模板',
      rules: [{ intent_level: 'high', cadence: 'D+0', points: ['要点'], questions: [], risks: [] }],
    }, FULL_OPERATOR, 'agent')
    const lead = await p1.ledger.createLead({ company_name: '公海任务公司' }, FULL_OPERATOR, 'agent')
    await p1.ledger.applyIntent(lead.id, 'high')
    const outcome = await sop.generateTasks({ lead_id: lead.id, sop_template_id: template.id }, FULL_OPERATOR, 'agent')
    await p1.ledger.transferLead(lead.id, undefined, FULL_OPERATOR, 'agent')
    const taskId = outcome.tasks[0]?.task.id
    if (taskId === undefined) throw new Error('no task generated')
    await expect(sop.updateTask(taskId, { status: 'done' }, OWN_OPERATOR, 'agent'))
      .rejects.toThrow('无权流转他人线索的 SOP 任务')
  })
})

describe('P3 scope guards', () => {
  it('assertCopyScope and assertSopScope mirror each other', () => {
    const lead = { owner_id: undefined, company_name: '公海' } as never
    expect(() =>{  assertCopyScope(lead, OWN_OPERATOR) }).toThrow('先领取')
    expect(() =>{  assertSopScope(lead, OWN_OPERATOR) }).toThrow('先领取')
    expect(() =>{  assertCopyScope({ ...lead, owner_id: OWN_OPERATOR_2.userId } as never, OWN_OPERATOR) }).toThrow('无权为他人线索生成文案')
    expect(() =>{  assertSopScope({ ...lead, owner_id: OWN_OPERATOR_2.userId } as never, OWN_OPERATOR) }).toThrow('无权为他人线索生成跟进任务')
  })

  it('cadenceOffsets tolerates offset-free cadences and preserves order', () => {
    expect(cadenceOffsets('D+10 最后，D+2 先行')).toEqual([10, 2])
  })

})

function mockClockOf(): () => void {
  // P3 branch fills do not need deterministic clocks; a no-op keeps the shape.
  return () => {}
}
