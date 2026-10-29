import { afterEach, beforeEach, describe, expect, it } from 'vitest'
import { NurtureContentService } from '../src/content/service.ts'
import { SopService, cadenceOffsets, unreadableDayMentions } from '../src/sop/service.ts'
import { renderVariables } from '../src/templates/render.ts'
import { setupP1, FULL_OPERATOR, completionReturning } from './helpers-p1.ts'
import type { P1Harness } from './helpers-p1.ts'

/** One SOP service over the harness's domain, audit table, and ledger. */
function sopOf(p1: P1Harness): SopService {
  return new SopService({
    domain: p1.harness.service.requireDomain(),
    audit: p1.harness.service.requireAuditTable(),
    ledger: p1.ledger,
  })
}

/** One copy service that records every prompt the "model" was asked to write from. */
function contentOf(p1: P1Harness, captured: string[]): NurtureContentService {
  return new NurtureContentService({
    ctx: p1.harness.ctx,
    domain: p1.harness.service.requireDomain(),
    audit: p1.harness.service.requireAuditTable(),
    ledger: p1.ledger,
    policy: p1.policy,
    completionFactory: () => ({ complete: async (prompt) => { captured.push(prompt); return '文案' } }),
  })
}

describe('P0-1 template variables render, they are never silently blanked', () => {
  it('substitutes known variables and keeps unresolved ones visible', () => {
    const result = renderVariables('{{contact_name}}您好，我是{{sender_name}}，{{公司名称}}同行', {
      contact_name: '小美美妆',
      sender_name: '李秉凌',
    })
    expect(result.text).toContain('小美美妆您好，我是李秉凌')
    expect(result.text).toContain('{{公司名称}}')
    expect(result.unresolved).toEqual(['公司名称'])
  })

  it('keeps a placeholder whose value is empty instead of deleting it', () => {
    const result = renderVariables('{{contact_name}}您好', { contact_name: '' })
    expect(result.text).toBe('{{contact_name}}您好')
    expect(result.unresolved).toEqual(['contact_name'])
  })

  it('never turns an unknown placeholder into an empty string', () => {
    const result = renderVariables('{{unknown}}正文', {})
    expect(result.text).toBe('{{unknown}}正文')
  })
})

describe('P0-1 the copy prompt carries the real lead and the sender identity', () => {
  let p1: P1Harness

  beforeEach(async () => {
    p1 = await setupP1(completionReturning('文案'))
  })

  afterEach(async () => {
    await p1.harness.dispose()
  })

  it('fills the template body and never ships a blanked slot', async () => {
    const captured: string[] = []
    const content = contentOf(p1, captured)
    const template = await content.createTemplate({
      name: '初触达模板',
      type: 'wecom_first_touch',
      body: '{{contact_name}}您好，我是{{sender_name}}，{{industry}}同行都在用。',
      variables: [{ name: 'sender_name', description: '我方发送人署名', example: '李明' }],
    }, FULL_OPERATOR, 'agent')
    const lead = await p1.ledger.createLead(
      { company_name: '小美美妆', contact_name: '王姐', industry: '实体门店' },
      FULL_OPERATOR,
      'agent',
    )
    await content.generate(
      { lead_id: lead.id, type: 'wecom_first_touch', variant: 'A', template_id: template.id },
      FULL_OPERATOR,
      'agent',
    )
    const prompt = captured[0] ?? ''
    expect(prompt).toContain('王姐您好，我是李明，实体门店同行都在用。')
    expect(prompt).not.toContain('{{contact_name}}')
    expect(prompt).not.toContain('{{sender_name}}')
  })

  it('prefers the configured sender over the template example', async () => {
    await p1.harness.service.updateSettings({ sender_name: '李秉凌' }, FULL_OPERATOR, 'agent')
    const captured: string[] = []
    const content = contentOf(p1, captured)
    const template = await content.createTemplate({
      name: '署名模板',
      type: 'wecom_first_touch',
      body: '您好，我是{{sender_name}}。',
      variables: [{ name: 'sender_name', description: '我方发送人署名', example: '李明' }],
    }, FULL_OPERATOR, 'agent')
    const lead = await p1.ledger.createLead({ company_name: '署名公司' }, FULL_OPERATOR, 'agent')
    await content.generate(
      { lead_id: lead.id, type: 'wecom_first_touch', variant: 'A', template_id: template.id },
      FULL_OPERATOR,
      'agent',
    )
    const prompt = captured[0] ?? ''
    expect(prompt).toContain('您好，我是李秉凌。')
    expect(prompt).toContain('"sender_name":"李秉凌"')
  })

  it('reports the slots that have no value instead of pretending they were filled', async () => {
    const captured: string[] = []
    const content = contentOf(p1, captured)
    const template = await content.createTemplate({
      name: '缺联系人模板',
      type: 'sms_followup',
      body: '{{contact_name}}您好，{{company_name}}的方案给您看看。',
    }, FULL_OPERATOR, 'agent')
    const lead = await p1.ledger.createLead({ company_name: '无名公司' }, FULL_OPERATOR, 'agent')
    await content.generate(
      { lead_id: lead.id, type: 'sms_followup', variant: 'A', template_id: template.id },
      FULL_OPERATOR,
      'agent',
    )
    const prompt = captured[0] ?? ''
    expect(prompt).toContain('{{contact_name}}')
    expect(prompt).toContain('请在文案中自然略过')
    expect(prompt).toContain('无名公司的方案给您看看。')
  })
})

describe('P0-2 SOP task generation is idempotent', () => {
  let p1: P1Harness

  beforeEach(async () => {
    p1 = await setupP1(completionReturning('{}'))
  })

  afterEach(async () => {
    await p1.harness.dispose()
  })

  it('does not pile a second copy of the task set on a repeat call', async () => {
    const sop = sopOf(p1)
    const template = await sop.createTemplate({
      name: '高意向模板',
      rules: [{
        intent_level: 'high',
        cadence: 'D+0 问候，D+3 回访',
        points: ['首次问候', '三天后回访'],
        questions: [],
        risks: [],
      }],
    }, FULL_OPERATOR, 'agent')
    const lead = await p1.ledger.createLead({ company_name: '幂等公司' }, FULL_OPERATOR, 'agent')
    await p1.ledger.applyIntent(lead.id, 'high')

    const first = await sop.generateTasks({ lead_id: lead.id, sop_template_id: template.id }, FULL_OPERATOR, 'agent')
    expect(first.tasks).toHaveLength(2)
    expect(first.skipped).toEqual([])

    const second = await sop.generateTasks({ lead_id: lead.id, sop_template_id: template.id }, FULL_OPERATOR, 'agent')
    expect(second.tasks).toHaveLength(0)
    expect(second.skipped.map(entry => entry.title)).toEqual(['首次问候', '三天后回访'])
    expect(sop.listTasks({ lead_id: lead.id }, FULL_OPERATOR).total).toBe(2)
  })

  it('re-creates a point whose earlier task was already done', async () => {
    const sop = sopOf(p1)
    const template = await sop.createTemplate({
      name: '单点模板',
      rules: [{ intent_level: 'high', cadence: 'D+0', points: ['首次问候'], questions: [], risks: [] }],
    }, FULL_OPERATOR, 'agent')
    const lead = await p1.ledger.createLead({ company_name: '重做公司' }, FULL_OPERATOR, 'agent')
    await p1.ledger.applyIntent(lead.id, 'high')

    const first = await sop.generateTasks({ lead_id: lead.id, sop_template_id: template.id }, FULL_OPERATOR, 'agent')
    await sop.updateTask(first.tasks[0]?.task.id ?? '', { status: 'done' }, FULL_OPERATOR, 'agent')

    const second = await sop.generateTasks({ lead_id: lead.id, sop_template_id: template.id }, FULL_OPERATOR, 'agent')
    expect(second.tasks).toHaveLength(1)
    expect(second.skipped).toEqual([])
  })
})

describe('P0-3 the D+N cadence is read as written', () => {
  let p1: P1Harness

  beforeEach(async () => {
    p1 = await setupP1(completionReturning('{}'))
  })

  afterEach(async () => {
    await p1.harness.dispose()
  })

  it('parses the spellings an operator actually types', () => {
    expect(cadenceOffsets('D+0 问候，D+3 回访')).toEqual([0, 3])
    expect(cadenceOffsets('d+3 回访')).toEqual([3])
    expect(cadenceOffsets('D +3 回访')).toEqual([3])
    expect(cadenceOffsets('D＋3 回访')).toEqual([3])
    expect(cadenceOffsets('第3天回访')).toEqual([3])
    expect(cadenceOffsets('3天后回访')).toEqual([3])
    expect(cadenceOffsets('不跟进')).toEqual([])
  })

  it('counts the day mentions the parser could not read', () => {
    expect(unreadableDayMentions('D+0 问候，D+下次 回访')).toBe(1)
    expect(unreadableDayMentions('D+0 问候，D+3 回访')).toBe(0)
    expect(unreadableDayMentions('不主动跟进，仅朋友圈可见')).toBe(0)
  })

  it('refuses to schedule silently when a day token cannot be read', async () => {
    const sop = sopOf(p1)
    const template = await sop.createTemplate({
      name: '坏节奏模板',
      rules: [{
        intent_level: 'high',
        cadence: 'D+0 问候，D+下次 回访',
        points: ['首次问候', '二次回访'],
        questions: [],
        risks: [],
      }],
    }, FULL_OPERATOR, 'agent')
    const lead = await p1.ledger.createLead({ company_name: '坏节奏公司' }, FULL_OPERATOR, 'agent')
    await p1.ledger.applyIntent(lead.id, 'high')
    await expect(sop.generateTasks({ lead_id: lead.id, sop_template_id: template.id }, FULL_OPERATOR, 'agent'))
      .rejects.toThrow('无法解析的排期表达')
  })

  it('schedules a cadence without any day token on today', async () => {
    const sop = sopOf(p1)
    const template = await sop.createTemplate({
      name: '归档模板',
      rules: [{ intent_level: 'invalid', cadence: '不跟进', points: ['归档标注'], questions: [], risks: [] }],
    }, FULL_OPERATOR, 'agent')
    const lead = await p1.ledger.createLead({ company_name: '归档公司' }, FULL_OPERATOR, 'agent')
    await p1.ledger.applyIntent(lead.id, 'invalid')
    const outcome = await sop.generateTasks({ lead_id: lead.id, sop_template_id: template.id }, FULL_OPERATOR, 'agent')
    expect(outcome.tasks).toHaveLength(1)
    expect(outcome.tasks[0]?.task.planned_at).toBe(outcome.tasks[0]?.task.created_at)
  })
})
