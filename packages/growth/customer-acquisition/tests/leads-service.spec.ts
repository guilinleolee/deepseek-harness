import { afterEach, beforeEach, describe, expect, it } from 'vitest'
import { setupP1, FULL_OPERATOR, OWN_OPERATOR, OWN_OPERATOR_2, completionReturning, mockClock } from './helpers-p1.ts'
import { parseExtractOutput, EXTRACT_SYSTEM_PROMPT, frameExtractPrompt, EXTRACT_MAX_CHARS } from '../src/leads/extract.ts'
import { renderLeadExport } from '../src/leads/export.ts'
import type { P1Harness } from './helpers-p1.ts'

describe('P1 lead ledger service', () => {
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

  async function auditActions(): Promise<string[]> {
    return [...p1.harness.service.requireAuditTable().entries()].map(([, record]) => record.action)
  }

  it('create applies defaults, persists, and audits', async () => {
    const lead = await p1.ledger.createLead({ company_name: '杭州示例贸易有限公司', tags: ['重点', '华东'] }, FULL_OPERATOR, 'agent')
    expect(lead.source).toBe('manual')
    expect(lead.opportunity_stage).toBe('new')
    expect(lead.status).toBe('active')
    expect(lead.owner_id).toBe(FULL_OPERATOR.userId)
    expect(lead.tags).toEqual(['重点', '华东'])
    expect(await auditActions()).toContain('lead.create')

    const audit = [...p1.harness.service.requireAuditTable().entries()].map(([, record]) => record)[0]
    expect(audit!.source).toBe('agent')
    expect(audit!.operator_user_id).toBe(FULL_OPERATOR.userId)
    expect(audit!.object_type).toBe('lead')
  })

  it('create rejects duplicate tags, empty company, and bad timestamps with friendly errors', async () => {
    await expect(p1.ledger.createLead({ company_name: 'X', tags: ['a', 'a'] }, FULL_OPERATOR, 'agent'))
      .rejects.toThrow('标签存在重复')
    await expect(p1.ledger.createLead({ company_name: '  ' }, FULL_OPERATOR, 'agent'))
      .rejects.toThrow('公司名称不能为空')
    await expect(p1.ledger.createLead({ company_name: 'X', next_followup_at: 1.5 }, FULL_OPERATOR, 'agent'))
      .rejects.toThrow('下次跟进时间')
  })

  it('get returns the detail envelope with recent followups and document titles', async () => {
    const lead = await p1.ledger.createLead({ company_name: '某公司', demand_desc: '要获客', budget_range: '5-10 万' }, FULL_OPERATOR, 'agent')
    for (let index = 0; index < 6; index += 1) {
      await p1.ledger.addFollowup(lead.id, `跟进 ${index}`, FULL_OPERATOR, 'agent')
    }
    await p1.ledger.addDocument(lead.id, '客户资料', '主营缝纫机', FULL_OPERATOR, 'agent')
    const detail = p1.ledger.getLeadDetail(lead.id, FULL_OPERATOR)
    expect(detail.demand_desc).toBe('要获客')
    expect(detail.budget_range).toBe('5-10 万')
    expect(detail.followups).toHaveLength(5)
    expect(detail.followups[0]?.content).toBe('跟进 5')
    expect(detail.documents).toEqual([expect.objectContaining({ title: '客户资料' })])
  })

  it('list filters by status, source, industry, intent, tag, owner, keyword, and time, with paging', async () => {
    const a = await p1.ledger.createLead({ company_name: 'Alpha 工厂', source: 'form', industry: '制造业', tags: ['hot'] }, FULL_OPERATOR, 'agent')
    const b = await p1.ledger.createLead({ company_name: 'beta 商行', source: 'chat', contact_name: '李四', owner_id: OWN_OPERATOR_2.userId }, FULL_OPERATOR, 'agent')
    const gamma = await p1.ledger.createLead({ company_name: 'Gamma 门店', source: 'referral' }, FULL_OPERATOR, 'agent')
    await p1.ledger.deleteLead(b.id, FULL_OPERATOR, 'agent')
    // Release one lead to the pool so the owner filters have all three shapes.
    await p1.ledger.transferLead(gamma.id, undefined, FULL_OPERATOR, 'agent')

    const active = p1.ledger.listLeads({}, FULL_OPERATOR)
    expect(active.total).toBe(2)
    expect(active.items.map(lead => lead.id).sort()).toEqual([a.id, gamma.id].sort())

    expect(p1.ledger.listLeads({ status: 'recycled' }, FULL_OPERATOR).total).toBe(1)
    expect(p1.ledger.listLeads({ source: 'form' }, FULL_OPERATOR).total).toBe(1)
    expect(p1.ledger.listLeads({ industry: '制造业' }, FULL_OPERATOR).total).toBe(1)
    expect(p1.ledger.listLeads({ tag: 'hot' }, FULL_OPERATOR).total).toBe(1)
    expect(p1.ledger.listLeads({ owner: 'pool' }, FULL_OPERATOR).total).toBe(1)
    expect(p1.ledger.listLeads({ owner: 'me' }, FULL_OPERATOR).total).toBe(1)
    // beta belongs to emp-2 but sits in the recycle bin; the active-only
    // default view counts neither.
    expect(p1.ledger.listLeads({ owner: 'me' }, OWN_OPERATOR_2).total).toBe(0)
    expect(p1.ledger.listLeads({ q: 'alpha' }, FULL_OPERATOR).total).toBe(1)
    // beta (the 李四 lead) sits in the recycle bin; the active view misses it.
    expect(p1.ledger.listLeads({ q: '李四' }, FULL_OPERATOR).total).toBe(0)
    expect(p1.ledger.listLeads({ q: '李四', status: 'recycled' }, FULL_OPERATOR).total).toBe(1)
    expect(p1.ledger.listLeads({ created_from: 9_999_999_999_999 }, FULL_OPERATOR).total).toBe(0)

    const page = p1.ledger.listLeads({ limit: 1, offset: 1 }, FULL_OPERATOR)
    expect(page.items).toHaveLength(1)
    expect(page.total).toBe(2)
  })

  it('own-scope list clamps to own leads plus the pool', async () => {
    await p1.ledger.createLead({ company_name: '我的线索' }, OWN_OPERATOR, 'agent')
    await p1.ledger.createLead({ company_name: '别人线索', owner_id: OWN_OPERATOR_2.userId }, FULL_OPERATOR, 'agent')
    const pooled = await p1.ledger.createLead({ company_name: '公海线索' }, FULL_OPERATOR, 'agent')
    await p1.ledger.transferLead(pooled.id, undefined, FULL_OPERATOR, 'agent')

    const visible = p1.ledger.listLeads({}, OWN_OPERATOR)
    expect(visible.total).toBe(2)
    expect(visible.items.map(lead => lead.company_name).sort()).toEqual(['公海线索', '我的线索'])
    expect(p1.ledger.listLeads({ owner: 'all' }, OWN_OPERATOR).total).toBe(2)
  })

  it('update merges defined fields, replaces tags, and rejects recycled leads', async () => {
    const lead = await p1.ledger.createLead({ company_name: '原公司', tags: ['旧'] }, FULL_OPERATOR, 'agent')
    const updated = await p1.ledger.updateLead(lead.id, { contact_name: '王五', tags: ['新'] }, FULL_OPERATOR, 'agent')
    expect(updated.company_name).toBe('原公司')
    expect(updated.contact_name).toBe('王五')
    expect(updated.tags).toEqual(['新'])

    await expect(p1.ledger.updateLead('missing', { contact_name: 'X' }, FULL_OPERATOR, 'agent')).rejects.toThrow('线索不存在')
    await p1.ledger.deleteLead(lead.id, FULL_OPERATOR, 'agent')
    await expect(p1.ledger.updateLead(lead.id, { contact_name: 'Y' }, FULL_OPERATOR, 'agent'))
      .rejects.toThrow('回收站中的线索不可编辑')
  })

  it('delete, restore, and purge follow the recycle-bin lifecycle', async () => {
    const lead = await p1.ledger.createLead({ company_name: '要删的公司' }, FULL_OPERATOR, 'agent')
    await p1.ledger.addFollowup(lead.id, '跟进', FULL_OPERATOR, 'agent')
    await p1.ledger.addDocument(lead.id, '资料', '正文', FULL_OPERATOR, 'agent')

    const deleted = await p1.ledger.deleteLead(lead.id, FULL_OPERATOR, 'agent')
    expect(deleted.status).toBe('recycled')
    await expect(p1.ledger.deleteLead(lead.id, FULL_OPERATOR, 'agent')).rejects.toThrow('已在回收站')
    await expect(p1.ledger.purgeLead(lead.id, OWN_OPERATOR, 'agent')).rejects.toThrow('无权访问')

    const removed = await p1.ledger.purgeLead(lead.id, FULL_OPERATOR, 'agent')
    expect(removed).toBe(3)
    expect(p1.ledger.listLeads({ status: 'recycled' }, FULL_OPERATOR).total).toBe(0)
    expect(await auditActions()).toEqual(expect.arrayContaining(['lead.delete', 'lead.purge']))
  })

  it('restore rejects leads that are not recycled', async () => {
    const lead = await p1.ledger.createLead({ company_name: '活着' }, FULL_OPERATOR, 'agent')
    await expect(p1.ledger.restoreLead(lead.id, FULL_OPERATOR, 'agent')).rejects.toThrow('不在回收站')
  })

  it('assign claims pool leads only; own-scope can only claim for itself', async () => {
    const lead = await p1.ledger.createLead({ company_name: '公海鱼' }, FULL_OPERATOR, 'agent')
    await p1.ledger.transferLead(lead.id, undefined, FULL_OPERATOR, 'agent')

    const claimed = await p1.ledger.assignLead(lead.id, OWN_OPERATOR.userId, OWN_OPERATOR, 'agent')
    expect(claimed.owner_id).toBe(OWN_OPERATOR.userId)

    const second = await p1.ledger.createLead({ company_name: '公海鱼二' }, FULL_OPERATOR, 'agent')
    await p1.ledger.transferLead(second.id, undefined, FULL_OPERATOR, 'agent')
    await expect(p1.ledger.assignLead(second.id, OWN_OPERATOR_2.userId, OWN_OPERATOR, 'agent'))
      .rejects.toThrow('只能把公海线索分配给自己')
    await expect(p1.ledger.assignLead(lead.id, OWN_OPERATOR.userId, OWN_OPERATOR, 'agent'))
      .rejects.toThrow('已有归属人')
  })

  it('transfer moves ownership and can release to the pool', async () => {
    const lead = await p1.ledger.createLead({ company_name: '转手' }, OWN_OPERATOR, 'agent')
    const moved = await p1.ledger.transferLead(lead.id, OWN_OPERATOR_2.userId, OWN_OPERATOR, 'agent')
    expect(moved.owner_id).toBe(OWN_OPERATOR_2.userId)

    await expect(p1.ledger.transferLead(lead.id, OWN_OPERATOR.userId, OWN_OPERATOR, 'agent'))
      .rejects.toThrow('无权访问该线索')
    const released = await p1.ledger.transferLead(lead.id, undefined, OWN_OPERATOR_2, 'agent')
    expect(released.owner_id).toBeUndefined()
    await expect(p1.ledger.transferLead(lead.id, OWN_OPERATOR.userId, OWN_OPERATOR, 'agent'))
      .rejects.toThrow('只能转移自己名下的线索')
  })

  it('documents enforce the 20k cap and scope; removal audits', async () => {
    const lead = await p1.ledger.createLead({ company_name: '资料公司' }, OWN_OPERATOR, 'agent')
    await expect(p1.ledger.addDocument(lead.id, '太大', 'x'.repeat(20_001), OWN_OPERATOR, 'agent'))
      .rejects.toThrow('超出上限')
    const document = await p1.ledger.addDocument(lead.id, '行业报告', '正文内容', OWN_OPERATOR, 'agent')

    expect(p1.ledger.listDocuments(lead.id, OWN_OPERATOR, false)[0]?.content).toBeUndefined()
    expect(p1.ledger.listDocuments(lead.id, OWN_OPERATOR, true)[0]?.content).toBe('正文内容')
    expect(() => p1.ledger.listDocuments(lead.id, OWN_OPERATOR_2, false)).toThrow('无权访问')

    await p1.ledger.removeDocument(document.id, OWN_OPERATOR, 'agent')
    expect(p1.ledger.listDocuments(lead.id, OWN_OPERATOR, false)).toHaveLength(0)
    expect(await auditActions()).toEqual(expect.arrayContaining(['lead.document.add', 'lead.document.remove']))
  })

  it('followups append and page newest first', async () => {
    const lead = await p1.ledger.createLead({ company_name: '跟进公司' }, FULL_OPERATOR, 'agent')
    for (const content of ['一', '二', '三']) {
      await p1.ledger.addFollowup(lead.id, content, FULL_OPERATOR, 'agent')
    }
    const page = p1.ledger.listFollowups(lead.id, FULL_OPERATOR, 2, 0)
    expect(page.total).toBe(3)
    expect(page.items.map(followup => followup.content)).toEqual(['三', '二'])
    await expect(p1.ledger.addFollowup(lead.id, ' ', FULL_OPERATOR, 'agent')).rejects.toThrow('不能为空')
  })

  it('extract parses model output, drops unknown roles into notes, and audits', async () => {
    const { ledger } = p1
    const completion = completionReturning(JSON.stringify({
      company_name: ' 杭州示例 ',
      contact_name: '王经理',
      phone: '13800000000',
      decision_role: 'boss',
      notes: '预算未提及',
    }))
    const output = await ledger.extractLeadFields({ text: '表单内容……', sourceHint: 'form' }, completion, FULL_OPERATOR, 'agent')
    expect(output.fields.company_name).toBe('杭州示例')
    expect(output.fields.decision_role).toBeUndefined()
    expect(output.notes).toContain('预算未提及')
    expect(output.notes).toContain('decision_role')
    expect(await auditActions()).toContain('lead.extract')

    await expect(ledger.extractLeadFields({ text: 'x'.repeat(EXTRACT_MAX_CHARS + 1) }, completion, FULL_OPERATOR, 'agent'))
      .rejects.toThrow('文本超出上限')
    await expect(ledger.extractLeadFields({ text: '   ' }, completion, FULL_OPERATOR, 'agent'))
      .rejects.toThrow('请提供要抽取的原始文本')
  })

  it('retries once with a stiffer prompt when the first answer is not JSON', async () => {
    const { ledger } = p1
    const prompts: string[] = []
    let turn = 0
    const completion = {
      complete: async (prompt: string) => {
        prompts.push(prompt)
        turn += 1
        return turn === 1 ? '抱歉，这段文字里没有找到公司信息。' : '{"company_name":"重试公司"}'
      },
    }
    const output = await ledger.extractLeadFields({ text: '表单内容' }, completion, FULL_OPERATOR, 'agent')
    expect(output.fields.company_name).toBe('重试公司')
    expect(prompts[1]).toContain('无法解析为 JSON')
    expect(await auditActions()).toContain('lead.extract')
  })

  it('export applies the same filters and audits the export', async () => {
    await p1.ledger.createLead({ company_name: '导出一', source: 'form' }, FULL_OPERATOR, 'agent')
    await p1.ledger.createLead({ company_name: '导出二', source: 'chat' }, FULL_OPERATOR, 'agent')
    const leads = await p1.ledger.exportLeads({ source: 'form' }, FULL_OPERATOR, 'agent')
    expect(leads).toHaveLength(1)
    expect(await auditActions()).toContain('lead.export')
  })

  it('writeBackIntent updates the lead intent level', async () => {
    const lead = await p1.ledger.createLead({ company_name: '意向公司' }, FULL_OPERATOR, 'agent')
    const updated = await p1.ledger.applyIntent(lead.id, 'high')
    expect(updated.intent_level).toBe('high')
  })

  it('isLeadVisible mirrors the read-scope rule', () => {
    expect(p1.ledger.isLeadVisible('missing', FULL_OPERATOR)).toBe(false)
  })
})

describe('P1 lead extract/parser pure functions', () => {
  it('frames the prompt with the source hint and full text', () => {
    const framed = frameExtractPrompt('正文', 'form')
    expect(framed).toContain('来源提示：form')
    expect(framed).toContain('正文')
    expect(frameExtractPrompt('正文')).not.toContain('来源提示')
  })

  it('parses fenced JSON, trims fields, and reports non-JSON output', () => {
    const parsed = parseExtractOutput('```json\n{"company_name":" 甲公司 ","demand_desc":"要获客"}\n```')
    expect(parsed.fields.company_name).toBe('甲公司')
    expect(parsed.fields.demand_desc).toBe('要获客')
    expect(() => parseExtractOutput('完全不是 JSON')).toThrow('JSON')
    expect(() => parseExtractOutput('{"company_name": 1}')).not.toThrow()
    expect(parseExtractOutput('{"company_name": 1}').fields.company_name).toBeUndefined()
  })

  it('declares the extraction output contract in the system prompt', () => {
    expect(EXTRACT_SYSTEM_PROMPT).toContain('decision_maker')
    expect(EXTRACT_SYSTEM_PROMPT).toContain('JSON')
  })
})

describe('P1 lead export renderer', () => {
  it('renders markdown tables and formula-guarded csv', async () => {
    const p1x = await setupP1(completionReturning('{}'))
    try {
      const lead = await p1x.ledger.createLead({
        company_name: '=危险()公司', contact_name: '张三', phone: '13800000000', tags: ['A', 'B'],
      }, FULL_OPERATOR, 'agent')

      const markdown = renderLeadExport('markdown', [lead])
      expect(markdown.split('\n')[0]).toContain('| id | company_name |')
      expect(markdown).toContain('=危险()公司')

      const csv = renderLeadExport('csv', [lead])
      const header = csv.split('\n')[0]
      expect(header?.startsWith('id,company_name,contact_name,phone')).toBe(true)
      expect(csv).toContain('"\'=危险()公司"')
    } finally {
      await p1x.harness.dispose()
    }
  })
})
