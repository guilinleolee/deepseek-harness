import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import type { Context } from '@deepseek-ai/cordis'
import { selectAuditRecords } from '../src/audit.ts'
import { inspectToolCall, installComplianceGate } from '../src/compliance.ts'
import { ContentTemplateId, GeneratedContentId, GeoReportId, GeoScanId } from '../src/domain/ids.ts'
import type { ScoreRun, ScoreRunItem } from '../src/domain/spec.ts'
import { CustomerAcquisitionService } from '../src/service.ts'
import { complianceDenyAuditor } from '../src/index.ts'
import { parseExtractOutput } from '../src/leads/extract.ts'
import { renderLeadExport } from '../src/leads/export.ts'
import { intentTagFor, parseScoreOutput } from '../src/scoring/evaluate.ts'
import { assertScoringScope, toScoreTemplateRef } from '../src/scoring/service.ts'
import { SEED_IDS } from '../src/scoring/seed.ts'
import { setupP1, FULL_OPERATOR, OWN_OPERATOR, OWN_OPERATOR_2, completionReturning, mockClock } from './helpers-p1.ts'
import { LeadScoringService } from '../src/scoring/service.ts'
import { resolveAiPolicy } from '../src/llm/oneshot.ts'
import type { P1Harness } from './helpers-p1.ts'
import type { IcpProfile } from '../src/domain/spec.ts'

describe('lead service branches behind the friendly errors', () => {
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

  function auditCount(): number {
    return [...p1.harness.service.requireAuditTable().entries()].length
  }

  it('rejects a whitespace source, an empty tag, an empty owner, and a cross-scope owner', async () => {
    await expect(p1.ledger.createLead({ company_name: 'X', source: '  ' }, FULL_OPERATOR, 'agent'))
      .rejects.toThrow('线索来源不能为空')
    await expect(p1.ledger.createLead({ company_name: 'X', tags: ['  '] }, FULL_OPERATOR, 'agent'))
      .rejects.toThrow('标签不能为空字符串')
    await expect(p1.ledger.createLead({ company_name: 'X', owner_id: ' ' }, FULL_OPERATOR, 'agent'))
      .rejects.toThrow('归属人 id 不能为空')
    await expect(p1.ledger.createLead({ company_name: 'X', owner_id: OWN_OPERATOR_2.userId }, OWN_OPERATOR, 'agent'))
      .rejects.toThrow('只能把新线索归属设置为自己')
  })

  it('persists optional fields when present and skips the write on an empty update', async () => {
    const lead = await p1.ledger.createLead({
      company_name: '全字段公司',
      opportunity_stage: 'nurturing',
      next_followup_at: 1_700_000_100_000,
      tags: ['a'],
    }, FULL_OPERATOR, 'agent')
    expect(lead.opportunity_stage).toBe('nurturing')
    expect(lead.next_followup_at).toBe(1_700_000_100_000)

    const before = auditCount()
    const unchanged = await p1.ledger.updateLead(lead.id, {}, FULL_OPERATOR, 'agent')
    expect(unchanged.updated_at).toBe(lead.updated_at)
    expect(auditCount()).toBe(before)

    await expect(p1.ledger.updateLead(lead.id, { company_name: ' ' }, FULL_OPERATOR, 'agent'))
      .rejects.toThrow('公司名称不能为空')
  })

  it('restores a recycled lead back to active and audits it', async () => {
    const lead = await p1.ledger.createLead({ company_name: '恢复公司' }, FULL_OPERATOR, 'agent')
    await p1.ledger.deleteLead(lead.id, FULL_OPERATOR, 'agent')
    const restored = await p1.ledger.restoreLead(lead.id, FULL_OPERATOR, 'agent')
    expect(restored.status).toBe('active')
    const actions = [...p1.harness.service.requireAuditTable().entries()].map(([, record]) => record.action)
    expect(actions).toContain('lead.restore')
  })

  it('purge requires the global delete capability even on own leads', async () => {
    const lead = await p1.ledger.createLead({ company_name: '自删公司' }, OWN_OPERATOR, 'agent')
    await p1.ledger.deleteLead(lead.id, OWN_OPERATOR, 'agent')
    await expect(p1.ledger.purgeLead(lead.id, OWN_OPERATOR, 'agent'))
      .rejects.toThrow('物理删除线索需要全局删除权限（can_delete_any_lead）')
  })

  it('purge cascades score runs, items, generated contents, and SOP tasks', async () => {
    const lead = await p1.ledger.createLead({ company_name: '级联公司' }, FULL_OPERATOR, 'agent')
    await p1.ledger.addFollowup(lead.id, '跟进', FULL_OPERATOR, 'agent')
    await p1.ledger.addDocument(lead.id, '资料', '正文', FULL_OPERATOR, 'agent')
    const domain = p1.harness.service.requireDomain()
    const run: ScoreRun = {
      id: 'run-1', lead_id: lead.id, icp_profile_id: 'icp-x', template_id: 'tpl-x',
      total: 50, reason: 'r', intent_tag: 'mid', created_at: 1,
    }
    const item: ScoreRunItem = {
      id: 'item-1', run_id: 'run-1', dimension_id: 'd', score: 50, weight: 100, reason: 'r', created_at: 1,
    }
    await domain.table('score_runs').put(run.id, run)
    await domain.table('score_run_items').put(item.id, item)
    await domain.table('generated_contents').put('gc-1', {
      id: 'gc-1', lead_id: lead.id, type: 'sms_followup', variant: 'A', content: '文案', created_at: 1,
    })
    await domain.table('sop_tasks').put('task-1', {
      id: 'task-1', lead_id: lead.id, title: '任务', status: 'pending', planned_at: 1,
      created_at: 1, updated_at: 1,
    })
    await p1.ledger.deleteLead(lead.id, FULL_OPERATOR, 'agent')

    const removed = await p1.ledger.purgeLead(lead.id, FULL_OPERATOR, 'agent')
    expect(removed).toBe(7)
    for (const table of ['score_runs', 'score_run_items', 'generated_contents', 'sop_tasks'] as const) {
      expect([...domain.table(table).entries()]).toHaveLength(0)
    }
  })
})

describe('scoring service and parser branches behind the friendly errors', () => {
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

  const profile: IcpProfile = {
    id: 'p', name: '画像', industry: '测试',
    dimensions: [{ id: 'a', name: '维度A', description: '说明', weight: 100 }],
    enabled: true, created_at: 1, updated_at: 1,
  }

  it('validates every dimension field, the list shape, and the template texts', async () => {
    await expect(p1.scoring.createIcpProfile({
      name: 'X', dimensions: [{ id: ' ', name: 'A', description: 'd', weight: 100 }],
    }, FULL_OPERATOR, 'agent')).rejects.toThrow('的 id 不能为空')
    await expect(p1.scoring.createIcpProfile({
      name: 'X', dimensions: [{ id: 'a', name: ' ', description: 'd', weight: 100 }],
    }, FULL_OPERATOR, 'agent')).rejects.toThrow('的名称不能为空')
    await expect(p1.scoring.createIcpProfile({
      name: 'X', dimensions: [{ id: 'a', name: 'A', description: ' ', weight: 100 }],
    }, FULL_OPERATOR, 'agent')).rejects.toThrow('的说明不能为空')
    await expect(p1.scoring.createIcpProfile({ name: 'X', dimensions: [] }, FULL_OPERATOR, 'agent'))
      .rejects.toThrow('至少需要一个评分维度')
    await expect(p1.scoring.createIcpProfile({ name: ' ', dimensions: [{ id: 'a', name: 'A', description: 'd', weight: 100 }] }, FULL_OPERATOR, 'agent'))
      .rejects.toThrow('画像名称不能为空')
    await expect(p1.scoring.createScoreTemplate({ name: 'X', prompt_text: ' ' }, FULL_OPERATOR, 'agent'))
      .rejects.toThrow('打分提示词不能为空')
    await expect(p1.scoring.createScoreTemplate({ name: ' ', prompt_text: 'p' }, FULL_OPERATOR, 'agent'))
      .rejects.toThrow('模板名称不能为空')
  })

  it('updates skip the write on empty patches and create carries the industry', async () => {
    const profile = await p1.scoring.createIcpProfile({
      name: '带行业', industry: '餐饮', dimensions: [{ id: 'a', name: 'A', description: 'd', weight: 100 }],
    }, FULL_OPERATOR, 'agent')
    expect(profile.industry).toBe('餐饮')
    const unchanged = await p1.scoring.updateIcpProfile(profile.id, {}, FULL_OPERATOR, 'agent')
    expect(unchanged.updated_at).toBe(profile.updated_at)
    await expect(p1.scoring.updateIcpProfile(profile.id, { name: ' ' }, FULL_OPERATOR, 'agent'))
      .rejects.toThrow('画像名称不能为空')

    const template = await p1.scoring.createScoreTemplate({ name: '带行业模板', industry: '餐饮', prompt_text: 'p' }, FULL_OPERATOR, 'agent')
    const unchangedTemplate = await p1.scoring.updateScoreTemplate(template.id, {}, FULL_OPERATOR, 'agent')
    expect(unchangedTemplate.prompt_text).toBe('p')
    await p1.scoring.updateScoreTemplate(template.id, { enabled: false }, FULL_OPERATOR, 'agent')
    expect(p1.scoring.listScoreTemplates(true)).toHaveLength(0)
    expect(toScoreTemplateRef(template)).toEqual({ id: template.id, name: '带行业模板', enabled: true })
  })

  it('delete refuses unknown template ids', async () => {
    await expect(p1.scoring.deleteScoreTemplate('missing', FULL_OPERATOR, 'agent')).rejects.toThrow('打分模板不存在')
  })

  it('resolves the default score template from settings before the industry chain', async () => {
    await p1.scoring.seedTemplates()
    const custom = await p1.scoring.createScoreTemplate({
      name: '默认模板', prompt_text: '默认模板标记 {{lead}}',
    }, FULL_OPERATOR, 'agent')
    await p1.harness.service.updateSettings({ default_score_template_id: custom.id }, FULL_OPERATOR, 'agent')

    const retail = p1.scoring.listIcpProfiles().find(candidate => candidate.industry === '实体门店')
    if (retail === undefined) throw new Error('seed missing retail profile')
    p1.setCompletion(completionReturning(JSON.stringify({
      items: retail.dimensions.map(dimension => ({ dimension_id: dimension.id, score: 70, reason: 'r' })),
      reason: '整体',
    })))
    const lead = await p1.ledger.createLead({ company_name: '奶茶店', industry: '实体门店' }, FULL_OPERATOR, 'agent')
    const captured: string[] = []
    p1.setCompletion({ complete: async (prompt) => { captured.push(prompt); return (await Promise.resolve(prompt), JSON.stringify({
      items: retail.dimensions.map(dimension => ({ dimension_id: dimension.id, score: 70, reason: 'r' })),
      reason: '整体',
    })) } })
    await p1.scoring.scoreOne({ lead_id: lead.id }, FULL_OPERATOR, 'agent')
    expect(captured[0]).toContain('默认模板标记')
  })

  it('refuses to score when no enabled profile exists at all', async () => {
    await p1.scoring.seedTemplates()
    for (const profile of p1.scoring.listIcpProfiles()) {
      await p1.scoring.updateIcpProfile(profile.id, { enabled: false }, FULL_OPERATOR, 'agent')
    }
    const lead = await p1.ledger.createLead({ company_name: '无画像公司' }, FULL_OPERATOR, 'agent')
    await expect(p1.scoring.scoreOne({ lead_id: lead.id }, FULL_OPERATOR, 'agent'))
      .rejects.toThrow('没有启用中的ICP 画像')
  })

  it('batch carries explicit ids into every lead attempt and stringifies non-Error failures', async () => {
    await p1.scoring.seedTemplates()
    const retail = p1.scoring.listIcpProfiles().find(candidate => candidate.industry === '实体门店')
    if (retail === undefined) throw new Error('seed missing retail profile')
    const software = p1.scoring.listIcpProfiles().find(candidate => candidate.id === SEED_IDS.softwareIcp)
    if (software === undefined) throw new Error('seed missing software profile')
    const lead = await p1.ledger.createLead({ company_name: '批量公司', industry: '实体门店' }, FULL_OPERATOR, 'agent')
    p1.setCompletion({ complete: async () => { throw '字符串错误' } })
    const batch = await p1.scoring.scoreBatch({
      lead_ids: [lead.id], icp_profile_id: software.id, score_template_id: SEED_IDS.softwareScore,
    }, FULL_OPERATOR, 'agent')
    expect(batch.failed).toEqual([{ lead_id: lead.id, error: '字符串错误' }])
  })

  it('history refuses unknown run ids and scope guards scoring directly', async () => {
    expect(() => p1.scoring.history({ run_id: 'missing' }, FULL_OPERATOR)).toThrow('打分记录不存在')

    const poolLead = {
      id: 'pl1', owner_id: undefined, source: 'manual', company_name: '公海评分', tags: [],
      opportunity_stage: 'new', status: 'active', created_at: 1, updated_at: 1,
    } as never
    expect(() =>{  assertScoringScope(poolLead, OWN_OPERATOR) }).toThrow('先领取')
    const otherLead = { ...poolLead, owner_id: OWN_OPERATOR_2.userId }
    expect(() =>{  assertScoringScope(otherLead, OWN_OPERATOR) }).toThrow('无权为他人线索打分')
    expect(() =>{  assertScoringScope({ ...poolLead, owner_id: OWN_OPERATOR.userId }, OWN_OPERATOR) }).not.toThrow()
  })

  it('parser carries dimension names and weights into the items', () => {
    const parsed = parseScoreOutput(JSON.stringify({
      items: [{ dimension_id: 'a', score: 80, reason: 'r' }],
      reason: '整体',
    }), profile)
    expect(parsed.items[0]).toEqual({ dimension_id: 'a', name: '维度A', score: 80, weight: 100, reason: 'r' })
  })

  it('parser rejects every malformed answer shape with its own reason', () => {
    const answer = (items: unknown, reason: unknown = 'r'): string => JSON.stringify({ items, reason })
    expect(() => parseScoreOutput('no braces at all', profile)).toThrow('不是有效的 JSON 对象')
    expect(() => parseScoreOutput('{ 坏 json }', profile)).toThrow('JSON 解析失败')

    expect(() => parseScoreOutput('{"items":{},"reason":"r"}', profile)).toThrow('缺少 items 数组')
    expect(() => parseScoreOutput(answer([1]), profile)).toThrow('非对象元素')
    expect(() => parseScoreOutput(answer([{ score: 1, reason: 'r' }]), profile)).toThrow('dimension_id')
    expect(() => parseScoreOutput(answer([
      { dimension_id: 'a', score: 1, reason: 'r' }, { dimension_id: 'a', score: 2, reason: 'r' },
    ]), profile)).toThrow('重复打分')
    expect(() => parseScoreOutput(answer([{ dimension_id: 'a', score: 'x', reason: 'r' }]), profile)).toThrow('0-100')
    expect(() => parseScoreOutput(answer([{ dimension_id: 'a', score: Number.NaN, reason: 'r' }]), profile)).toThrow('0-100')
    expect(() => parseScoreOutput(answer([{ dimension_id: 'a', score: 1 }]), profile)).toThrow('缺少打分理由')
    expect(() => parseScoreOutput(answer([{ dimension_id: 'a', score: 1, reason: 'r' }], '  '), profile)).toThrow('整体理由')
    expect(() => parseScoreOutput(answer([{ dimension_id: 'zz', score: 1, reason: 'r' }]), profile)).toThrow('未知维度')
  })

  it('maps threshold boundaries deterministically', () => {
    expect([0, 29.9, 30, 59.9, 60, 79.9, 80, 100].map(intentTagFor)).toEqual([
      'invalid', 'invalid', 'low', 'low', 'mid', 'mid', 'high', 'high',
    ])
  })
})

describe('extract and export boundary branches', () => {
  it('extract rejects fenced-but-invalid and non-object answers', () => {
    expect(() => parseExtractOutput('没有大括号的文本')).toThrow('不是有效的 JSON 对象')
    expect(() => parseExtractOutput('{ 坏 }')).toThrow('JSON 解析失败')

  })

  it('export projects both present and absent optional columns', async () => {
    const p1 = await setupP1(completionReturning('{}'))
    try {
      const rich = await p1.ledger.createLead({
        company_name: '全列公司', contact_name: '张三', email: 'a@b.c', industry: '餐饮',
        decision_role: 'decision_maker', owner_id: OWN_OPERATOR.userId, next_followup_at: 42,
        demand_desc: '需求', budget_range: '5万', company_size: '1-10',
      }, FULL_OPERATOR, 'agent')
      await p1.ledger.applyIntent(rich.id, 'high')
      const bare = await p1.ledger.createLead({ company_name: '空列公司' }, FULL_OPERATOR, 'agent')
      const markdown = renderLeadExport('markdown', [
        await p1.ledger.getLead(rich.id, FULL_OPERATOR),
        await p1.ledger.getLead(bare.id, FULL_OPERATOR),
      ])
      expect(markdown).toContain('| a@b.c |')
      expect(markdown).toContain('decision_maker')
      expect(markdown).toContain('| 42 |')
      expect(markdown).toContain('high')
    } finally {
      await p1.harness.dispose()
    }
  })
})

describe('P0 surfaces the gate had not seen', () => {
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

  it('uninitialized service handles fail loud', () => {
    const fresh = Object.create(CustomerAcquisitionService.prototype) as CustomerAcquisitionService
    expect(() => fresh.requireAuditTable()).toThrow('durable domain is not initialized')
    expect(() => fresh.getSettings()).toThrow('durable domain is not initialized')
  })

  it('the Remote face serves settings and audit with the web operator', async () => {
    const settings = await p1.harness.service.getSettingsRemote()
    expect(settings.settings.geo_max_pages).toBe(10)
    const updated = await p1.harness.service.updateSettingsRemote({ geo_max_pages: 12 })
    expect(updated.settings.geo_max_pages).toBe(12)
    const audit = await p1.harness.service.listAuditLogs({})
    expect(audit.total).toBe(1)
    expect(audit.items[0]?.source).toBe('web')
  })

  it('updateSettings with an empty patch audits 无变更', async () => {
    await p1.harness.service.updateSettings({}, FULL_OPERATOR, 'agent')
    const records = [...p1.harness.service.requireAuditTable().entries()].map(([, record]) => record)
    expect(records[0]?.summary).toContain('无变更')
  })

  it('compliance denial audits fall back to the default operator when resolution fails', async () => {
    vi.spyOn(p1.harness.ctx.permissionContext, 'resolve').mockRejectedValue(new Error('身份失效'))
    await p1.harness.service.recordComplianceDeny('customer_acquisition_geo_scan', 'url 为空', { via: 'agent' })
    const records = [...p1.harness.service.requireAuditTable().entries()].map(([, record]) => record)
    expect(records[0]?.action).toBe('compliance.deny')
    expect(records[0]?.operator_user_id).toBe('local-default')
  })

  it('the denial auditor warns and continues when the audit write fails', async () => {
    const warn = vi.fn()
    const service = { recordComplianceDeny: () => Promise.reject(new Error('介质只读')) } as never
    const runtimeCtx = { logger: { warn } } as never as Context
    const onDeny = complianceDenyAuditor(service, runtimeCtx)
    onDeny('customer_acquisition_geo_scan', 'url 为空', 'agent-1')
    await await_vi_flush()
    expect(warn).toHaveBeenCalledWith(expect.stringContaining('介质只读'))
  })

  it('selectAuditRecords bounds the time window on both ends', () => {
    const record = (created_at: number) => ({
      id: `a${created_at}`, source: 'agent' as const, operator_user_id: 'u', action: 'a',
      object_type: 't', summary: 's', created_at,
    })
    const windowed = selectAuditRecords([record(1), record(2), record(3)], { from: 2, to: 2 })
    expect(windowed.map(entry => entry.created_at)).toEqual([2])
  })

  it('compliance gate rules allow unlisted plugin tools and deny malformed geo urls and settings', () => {
    expect(inspectToolCall('customer_acquisition_lead_create', {}).kind).toBe('allow')
    expect(inspectToolCall('customer_acquisition_geo_scan', { url: ':::bad:::' }).kind).toBe('deny')
    expect(inspectToolCall('customer_acquisition_settings_set', { geo_page_timeout_ms: 500 }).kind).toBe('deny')
  })

  it('brand constructors stay callable for every id family', () => {
    expect(ContentTemplateId('ct')).toBe('ct')
    expect(GeneratedContentId('gc')).toBe('gc')
    expect(GeoScanId('gs')).toBe('gs')
    expect(GeoReportId('gr')).toBe('gr')
  })
})

/** Flush the void-promised auditor rejection into the logged warning. */
function await_vi_flush(): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, 0))
}


describe('second-round branch fills', () => {
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

  it('rejects empty owners, empty document fields, and unknown documents with their own reasons', async () => {
    const lead = await p1.ledger.createLead({ company_name: '边界公司' }, FULL_OPERATOR, 'agent')
    await expect(p1.ledger.assignLead(lead.id, ' ', FULL_OPERATOR, 'agent')).rejects.toThrow('目标归属人 id 不能为空')
    await expect(p1.ledger.transferLead(lead.id, ' ', FULL_OPERATOR, 'agent')).rejects.toThrow('目标归属人 id 不能为空')
    await expect(p1.ledger.addDocument(lead.id, ' ', 'c', FULL_OPERATOR, 'agent')).rejects.toThrow('资料标题不能为空')
    await expect(p1.ledger.addDocument(lead.id, 't', ' ', FULL_OPERATOR, 'agent')).rejects.toThrow('资料内容不能为空')
    await expect(p1.ledger.removeDocument('ghost', FULL_OPERATOR, 'agent')).rejects.toThrow('挂接资料不存在')
  })

  it('removeDocument fails loud when the owning lead row is gone', async () => {
    const lead = await p1.ledger.createLead({ company_name: '孤儿资料公司' }, FULL_OPERATOR, 'agent')
    const document = await p1.ledger.addDocument(lead.id, '资料', '正文', FULL_OPERATOR, 'agent')
    await p1.harness.service.requireDomain().table('leads').delete(lead.id)
    await expect(p1.ledger.removeDocument(document.id, FULL_OPERATOR, 'agent')).rejects.toThrow('所属线索不存在')
  })

  it('writeBackIntent refuses missing leads and pool writes ask the operator to claim first', async () => {
    await expect(p1.ledger.applyIntent('ghost', 'high')).rejects.toThrow('线索不存在')
    const lead = await p1.ledger.createLead({ company_name: '待领取公司' }, FULL_OPERATOR, 'agent')
    await p1.ledger.transferLead(lead.id, undefined, FULL_OPERATOR, 'agent')
    await expect(p1.ledger.updateLead(lead.id, { contact_name: 'X' }, OWN_OPERATOR, 'agent'))
      .rejects.toThrow('请先领取（assign 给自己）')
  })

  it('purge refuses non-recycled leads and spares rows of other leads', async () => {
    const active = await p1.ledger.createLead({ company_name: '活着公司' }, FULL_OPERATOR, 'agent')
    await expect(p1.ledger.purgeLead(active.id, FULL_OPERATOR, 'agent')).rejects.toThrow('仅回收站中的线索可物理删除')

    const doomed = await p1.ledger.createLead({ company_name: '将删公司' }, FULL_OPERATOR, 'agent')
    const survivor = await p1.ledger.createLead({ company_name: '幸存公司' }, FULL_OPERATOR, 'agent')
    const domain = p1.harness.service.requireDomain()
    await domain.table('score_runs').put('run-s', {
      id: 'run-s', lead_id: survivor.id, icp_profile_id: 'i', template_id: 't',
      total: 1, reason: 'r', intent_tag: 'low', created_at: 1,
    })
    await domain.table('score_run_items').put('item-s', {
      id: 'item-s', run_id: 'run-s', dimension_id: 'd', score: 1, weight: 100, reason: 'r', created_at: 1,
    })
    await p1.ledger.deleteLead(doomed.id, FULL_OPERATOR, 'agent')
    await p1.ledger.purgeLead(doomed.id, FULL_OPERATOR, 'agent')
    expect([...domain.table('score_runs').entries()]).toHaveLength(1)
    expect([...domain.table('score_run_items').entries()]).toHaveLength(1)
    expect(p1.ledger.getLead(survivor.id, FULL_OPERATOR).company_name).toBe('幸存公司')
  })

  it('detail projection carries the full optional surface', async () => {
    const rich = await p1.ledger.createLead({
      company_name: '全字段公司', contact_name: '张三', industry: '餐饮', next_followup_at: 7,
      demand_desc: '需求', budget_range: '5万',
    }, FULL_OPERATOR, 'agent')
    const detail = p1.ledger.getLeadDetail(rich.id, FULL_OPERATOR)
    expect(detail.lead.contact_name).toBe('张三')
    expect(detail.lead.industry).toBe('餐饮')
    expect(detail.lead.next_followup_at).toBe(7)
    expect(detail.demand_desc).toBe('需求')
    expect(detail.budget_range).toBe('5万')
  })

  it('export renders the empty owner cell of a pool lead', async () => {
    const lead = await p1.ledger.createLead({ company_name: '公海导出公司' }, FULL_OPERATOR, 'agent')
    await p1.ledger.transferLead(lead.id, undefined, FULL_OPERATOR, 'agent')
    const markdown = renderLeadExport('markdown', [await p1.ledger.getLead(lead.id, FULL_OPERATOR)])
    const ownerRow = markdown.split('\n').find(line => line.includes('公海导出公司'))
    expect(ownerRow).toBeDefined()
  })

  it('extract reports unrecognized companies and unknown decision roles directly', async () => {
    const unrecognized = parseExtractOutput(JSON.stringify({ notes: '全都缺' }))
    expect(unrecognized.fields.company_name).toBeUndefined()
    const dropped = parseExtractOutput(JSON.stringify({ company_name: '甲', decision_role: 'boss' }))
    expect(dropped.notes).toContain('decision_role')
  })

  it('the compliance listener delegates owned-but-legal calls and audits denials', async () => {
    let captured: ((exec: { name: string; arguments: object }, next: () => string) => unknown) | undefined
    const onDeny = vi.fn()
    const fakeCtx = {
      on: (_event: string, listener: never) => {
        captured = listener
        return () => {}
      },
    } as never
    installComplianceGate(fakeCtx, onDeny)
    const next = vi.fn(() => 'next-result')
    const legal = { name: 'customer_acquisition_lead_create', arguments: {} }
    await expect(captured?.(legal, next)).resolves.toBe('next-result')
    expect(next).toHaveBeenCalledTimes(1)
    expect(onDeny).not.toHaveBeenCalled()

    const denied = { name: 'customer_acquisition_geo_scan', arguments: { url: 'http://' }, agent: { id: 'a9' } }
    const verdict = await captured?.(denied, next)
    expect(verdict).toMatchObject({ kind: 'deny' })
    expect(next).toHaveBeenCalledTimes(1)
    expect(onDeny).toHaveBeenCalledWith('customer_acquisition_geo_scan', expect.stringContaining('不是合法网址'), 'a9')
  })

  it('gate-level rules deny the oversize batch and non-prefixed tools pass through', () => {
    expect(inspectToolCall('customer_acquisition_score_batch', { lead_ids: Array.from({ length: 51 }) }).kind).toBe('deny')
    expect(inspectToolCall('customer_acquisition_score_batch', { lead_ids: ['l1'] }).kind).toBe('allow')
    expect(inspectToolCall('unrelated_tool', {}).kind).toBe('allow')
  })

  it('applyIntent exposes the scoring write-back on the ledger', async () => {
    const lead = await p1.ledger.createLead({ company_name: '意向回填公司' }, FULL_OPERATOR, 'agent')
    const updated = await p1.ledger.applyIntent(lead.id, 'invalid')
    expect(updated.intent_level).toBe('invalid')
  })
})
describe('third-round branch fills', () => {
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

  it('accepts a known decision role into the fields', () => {
    const accepted = parseExtractOutput(JSON.stringify({ company_name: '甲', decision_role: 'decision_maker' }))
    expect(accepted.fields.decision_role).toBe('decision_maker')
  })

  it('detail projection leaves pool-lead owner and long text absent', async () => {
    const pooled = await p1.ledger.createLead({ company_name: '公海详情公司' }, FULL_OPERATOR, 'agent')
    await p1.ledger.transferLead(pooled.id, undefined, FULL_OPERATOR, 'agent')
    const detail = p1.ledger.getLeadDetail(pooled.id, FULL_OPERATOR)
    expect(detail.lead.owner_id).toBeUndefined()
    expect(detail.demand_desc).toBeUndefined()
    expect(detail.budget_range).toBeUndefined()
  })

  it('purge spares survivor rows in the content and SOP tables too', async () => {
    const doomed = await p1.ledger.createLead({ company_name: '内容级联公司' }, FULL_OPERATOR, 'agent')
    const survivor = await p1.ledger.createLead({ company_name: '内容幸存公司' }, FULL_OPERATOR, 'agent')
    const domain = p1.harness.service.requireDomain()
    await domain.table('generated_contents').put('gc-d', {
      id: 'gc-d', lead_id: doomed.id, type: 'sms_followup', variant: 'A', content: 'x', created_at: 1,
    })
    await domain.table('generated_contents').put('gc-s', {
      id: 'gc-s', lead_id: survivor.id, type: 'sms_followup', variant: 'B', content: 'y', created_at: 1,
    })
    await domain.table('sop_tasks').put('task-d', {
      id: 'task-d', lead_id: doomed.id, title: '删', status: 'pending', planned_at: 1, created_at: 1, updated_at: 1,
    })
    await domain.table('sop_tasks').put('task-s', {
      id: 'task-s', lead_id: survivor.id, title: '留', status: 'pending', planned_at: 1, created_at: 1, updated_at: 1,
    })
    await p1.ledger.deleteLead(doomed.id, FULL_OPERATOR, 'agent')
    await p1.ledger.purgeLead(doomed.id, FULL_OPERATOR, 'agent')
    expect([...domain.table('generated_contents').entries()].map(([, row]) => row.lead_id)).toEqual([survivor.id])
    expect([...domain.table('sop_tasks').entries()].map(([, row]) => row.lead_id)).toEqual([survivor.id])
  })

  it('extraction audits the unrecognized-company summary and write-protects the leads of others', async () => {
    const summary = await p1.ledger.extractLeadFields(
      { text: '没有任何字段的文本' },
      completionReturning(JSON.stringify({ notes: '无可识别字段' })),
      FULL_OPERATOR,
      'agent',
    )
    expect(summary.fields.company_name).toBeUndefined()
    const records = [...p1.harness.service.requireAuditTable().entries()].map(([, record]) => record)
    expect(records[0]?.summary).toContain('未识别公司')

    const owned = await p1.ledger.createLead({ company_name: '他人线索公司' }, OWN_OPERATOR, 'agent')
    await expect(p1.ledger.updateLead(owned.id, { contact_name: 'X' }, OWN_OPERATOR_2, 'agent'))
      .rejects.toThrow('无权访问该线索')
  })

  it('full-capability operators delete leads owned by others, and filters exclude by intent and window end', async () => {
    const owned = await p1.ledger.createLead({ company_name: '跨删公司' }, OWN_OPERATOR, 'agent')
    const deleted = await p1.ledger.deleteLead(owned.id, FULL_OPERATOR, 'agent')
    expect(deleted.status).toBe('recycled')

    const lead = await p1.ledger.createLead({ company_name: '过滤公司' }, FULL_OPERATOR, 'agent')
    await p1.ledger.applyIntent(lead.id, 'high')
    expect(p1.ledger.listLeads({ intent_level: 'high' }, FULL_OPERATOR).items.map(entry => entry.id)).toContain(lead.id)
    expect(p1.ledger.listLeads({ intent_level: 'low' }, FULL_OPERATOR).total).toBe(0)
    expect(p1.ledger.listLeads({ created_to: 1 }, FULL_OPERATOR).total).toBe(0)
  })

  it('gate-level batch cap rejects non-array lead id lists and passes absent ones', () => {
    expect(inspectToolCall('customer_acquisition_score_batch', { lead_ids: 'l1' }).kind).toBe('deny')
    expect(inspectToolCall('customer_acquisition_score_batch', {}).kind).toBe('allow')
  })

  it('pool leads need the global delete capability to enter the recycle bin', async () => {
    const lead = await p1.ledger.createLead({ company_name: '公海删除公司' }, FULL_OPERATOR, 'agent')
    await p1.ledger.transferLead(lead.id, undefined, FULL_OPERATOR, 'agent')
    await expect(p1.ledger.deleteLead(lead.id, OWN_OPERATOR, 'agent'))
      .rejects.toThrow('删除他人或公海线索需要全局删除权限（can_delete_any_lead）')
  })

  it('the scoring service builds its default completion when no factory is injected', async () => {
    const scoring = new LeadScoringService({
      ctx: p1.harness.ctx,
      domain: p1.harness.service.requireDomain(),
      audit: p1.harness.service.requireAuditTable(),
      ledger: p1.ledger,
      policy: resolveAiPolicy(undefined),
    })
    expect(scoring.listIcpProfiles()).toHaveLength(0)
  })
})
