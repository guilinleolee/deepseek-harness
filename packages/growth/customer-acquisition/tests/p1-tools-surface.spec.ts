import { describe, expect, it, vi } from 'vitest'
import type { ToolDefinition } from '@deepseek-ai/dsh-tools'
import { auditListTool, auditExportTool } from '../src/tools/audit.ts'
import { settingsGetTool, settingsSetTool } from '../src/tools/settings.ts'
import {
  leadAssignTool, leadCreateTool, leadDeleteTool, leadDocumentAddTool, leadDocumentListTool,
  leadDocumentRemoveTool, leadExportTool, leadExtractTool, leadFollowupAddTool, leadFollowupListTool,
  leadGetTool, leadListTool, leadPurgeTool, leadRestoreTool, leadTransferTool, leadUpdateTool,
} from '../src/tools/leads.ts'
import {
  icpCreateTool, icpDeleteTool, icpListTool, icpUpdateTool, scoreBatchTool, scoreHistoryTool,
  scoreOneTool, scoreTemplateCreateTool, scoreTemplateDeleteTool, scoreTemplateListTool,
  scoreTemplateUpdateTool,
} from '../src/tools/scoring.ts'
import type { LeadLedgerService } from '../src/leads/service.ts'
import type { LeadScoringService } from '../src/scoring/service.ts'
import type { LeadRefValue } from '../src/leads/types.ts'
import type { PromptCompletion } from '../src/llm/oneshot.ts'
import { LeadId, UserId } from '../src/domain/ids.ts'
import type { Lead } from '../src/domain/spec.ts'
import type { PermissionContextService, ResolvedOperator } from '../src/permission/types.ts'
import { FULL_OPERATOR } from './helpers-p1.ts'

const EXEC = { callId: 'c', rootCallId: 'c', name: 'probe', arguments: {}, signal: new AbortController().signal, agent: { id: 'a1' } } as never

const COMPLETION: PromptCompletion = { complete: async () => '{}' }

function permissionOf(operator: ResolvedOperator = FULL_OPERATOR): PermissionContextService {
  return { resolve: async () => operator } as never
}

function ledgerOf(overrides: Record<string, unknown> = {}): LeadLedgerService {
  return {
    updateLead: async () => storedLead(),
    deleteLead: async () => ({ ...storedLead(), status: 'recycled' }),
    restoreLead: async () => ({ ...storedLead(), status: 'active' }),
    purgeLead: async () => 4,
    assignLead: async () => ({ ...storedLead(), owner_id: 'u9' }),
    transferLead: async () => storedLead(),
    exportLeads: async () => [storedLead()],
    addDocument: async () => ({ id: 'd1', lead_id: 'l1', title: '资料', content: '正文', created_at: 1, updated_at: 1 }),
    listDocuments: () => [{ id: 'd1', title: '资料', char_count: 2, content: '正文' }],
    removeDocument: async () => undefined,
    addFollowup: async () => ({ id: 'f1', lead_id: 'l1', content: '跟进', created_at: 3 }),
    listFollowups: () => ({ items: [{ id: 'f1', content: '跟进', created_at: 3 }], total: 1 }),
    ...overrides,
  } as never
}

function scoringOf(overrides: Record<string, unknown> = {}): LeadScoringService {
  return {
    updateIcpProfile: async () => storedProfile(),
    listIcpProfiles: vi.fn(() => [storedProfile()]),
    deleteIcpProfile: async () => undefined,
    createScoreTemplate: async () => storedTemplate(),
    updateScoreTemplate: async () => storedTemplate(),
    listScoreTemplates: vi.fn(() => [storedTemplate()]),
    deleteScoreTemplate: async () => undefined,
    ...overrides,
  } as never as LeadScoringService
}

function storedLead(): Lead {
  return {
    id: LeadId('l1'), owner_id: UserId('u1'), source: 'form', company_name: '公司甲', contact_name: '联系人',
    phone: '138', email: 'a@b.c', industry: '餐饮', company_size: '1-10', demand_desc: '要获客',
    budget_range: '5万', decision_role: 'decision_maker', intent_level: 'high', tags: ['重点'],
    opportunity_stage: 'qualified', next_followup_at: 9, status: 'active', created_at: 1, updated_at: 2,
  }
}

function storedProfile() {
  return {
    id: 'icp1', name: '画像甲', industry: '餐饮', enabled: true,
    dimensions: [{ id: 'budget', name: '预算', description: '预算说明', weight: 100 }],
    created_at: 1, updated_at: 1,
  } as never
}

function storedTemplate() {
  return { id: 't1', name: '模板甲', industry: '餐饮', prompt_text: '评估 {{lead}}', enabled: true, created_at: 1, updated_at: 1 } as never
}

const FULL_REF: LeadRefValue = {
  id: 'l1', company_name: '全字段公司', contact_name: '联系人', source: 'form', industry: '餐饮',
  intent_level: 'high', opportunity_stage: 'qualified', owner_id: 'u9', status: 'active',
  tags: ['重点', '华东'], next_followup_at: 5, updated_at: 6,
}

const BARE_REF = {
  id: 'l2', company_name: '裸公司', source: 'manual', opportunity_stage: 'new', status: 'recycled', updated_at: 1,
} as LeadRefValue

function renderText(tool: ToolDefinition, args: object, value: unknown): string {
  const [block] = tool.output.render(args, value as never)
  return (block as { text: string }).text
}

/** Lead-tool dependencies with the given ledger overrides. */
function leadDeps(overrides: Record<string, unknown> = {}): {
  ledger: LeadLedgerService
  permission: PermissionContextService
  completion: PromptCompletion
} {
  return { ledger: ledgerOf(overrides), permission: permissionOf(), completion: COMPLETION }
}

function scoringDeps(overrides: Record<string, unknown> = {}): { scoring: LeadScoringService; permission: PermissionContextService } {
  return { scoring: scoringOf(overrides), permission: permissionOf() }
}

describe('lead tool renders across sparse and rich values', () => {
  const create = leadCreateTool(leadDeps())
  const update = leadUpdateTool(leadDeps())
  const get = leadGetTool(leadDeps())
  const list = leadListTool(leadDeps())

  it('create and update render the full and the bare ref', () => {
    expect(renderText(create, { company_name: 'X' }, { lead: FULL_REF })).toContain('全字段公司')
    expect(renderText(create, { company_name: 'X' }, { lead: BARE_REF })).toContain('公海')
    expect(renderText(update, { lead_id: 'l1' }, { lead: FULL_REF })).toContain('已更新线索')
    expect(renderText(update, { lead_id: 'l1' }, { lead: BARE_REF })).toContain('裸公司')
  })

  it('lead_get renders demand, budget, follow-ups, and documents, or their absence', () => {
    const rich = renderText(get, { lead_id: 'l1' }, {
      lead: FULL_REF,
      demand_desc: '要获客',
      budget_range: '5万',
      followups: [{ id: 'f1', content: '聊过', created_at: 3 }],
      documents: [{ id: 'd1', title: '资料' }],
    })
    expect(rich).toContain('需求：要获客')
    expect(rich).toContain('预算：5万')
    expect(rich).toContain('最近跟进 1 条')
    expect(rich).toContain('挂接资料 1 份：资料')

    const bare = renderText(get, { lead_id: 'l1' }, { lead: BARE_REF, followups: [], documents: [] })
    expect(bare).not.toContain('需求：')
    expect(bare).not.toContain('最近跟进')
    expect(bare).not.toContain('挂接资料')
  })

  it('lead_list renders the empty page and the populated page', () => {
    expect(renderText(list, {}, { items: [], total: 0 })).toContain('当前页无记录')
    const populated = renderText(list, {}, { items: [FULL_REF, BARE_REF], total: 2 })
    expect(populated).toContain('本页 2 条')
    expect(populated).toContain('意向 high')
    expect(populated).toContain('标签 重点、华东')
  })
})

describe('lead tool execution paths', () => {
  it('lead_update forwards the patch and returns the ref', async () => {
    const updateLead = vi.fn(async () => storedLead())
    const tool = leadUpdateTool(leadDeps({ updateLead }))
    const value = await tool.execute({ lead_id: 'l1', contact_name: '王五', tags: ['新'] }, EXEC) as { lead: { company_name: string } }
    expect(value.lead.company_name).toBe('公司甲')
    expect(updateLead).toHaveBeenCalledWith('l1', { contact_name: '王五', tags: ['新'] }, FULL_OPERATOR, 'agent')
  })

  it('lead_delete, lead_restore, and lead_purge return their canonical envelopes', async () => {
    const deleted = await leadDeleteTool(leadDeps()).execute({ lead_id: 'l1' }, EXEC) as { status: string }
    expect(deleted.status).toBe('recycled')
    const restored = await leadRestoreTool(leadDeps()).execute({ lead_id: 'l1' }, EXEC) as { status: string }
    expect(restored.status).toBe('active')
    const purged = await leadPurgeTool(leadDeps()).execute({ lead_id: 'l1' }, EXEC) as { purged: boolean }
    expect(purged.purged).toBe(true)
  })

  it('lead_assign and lead_transfer map the owner envelope, empty string meaning the pool', async () => {
    const assign = leadAssignTool(leadDeps())
    await expect(assign.execute({ lead_id: 'l1', owner_id: 'u9' }, EXEC)).resolves.toEqual({ lead_id: 'l1', owner_id: 'u9' })
    expect(renderText(assign, { lead_id: 'l1', owner_id: 'u9' }, { lead_id: 'l1', owner_id: 'u9' })).toContain('已分配给 u9')

    const transfer = leadTransferTool(leadDeps({ transferLead: async () => ({ ...storedLead(), owner_id: undefined }) }))
    const moved = await transfer.execute({ lead_id: 'l1', owner_id: 'u9' }, EXEC) as { owner_id: string }
    expect(moved.owner_id).toBe('u9')
    const released = await transfer.execute({ lead_id: 'l1' }, EXEC) as { owner_id: string }
    expect(released.owner_id).toBe('')
    expect(renderText(transfer, { lead_id: 'l1' }, { lead_id: 'l1', owner_id: '' })).toContain('公海')
    expect(renderText(transfer, { lead_id: 'l1' }, { lead_id: 'l1', owner_id: 'u9' })).toContain('u9')
  })

  it('lifecycle and extract tools render their envelopes across both states', () => {
    const delete_ = leadDeleteTool(leadDeps())
    expect(renderText(delete_, { lead_id: 'l1' }, { lead_id: 'l1', status: 'recycled' })).toContain('已移入回收站')
    const restore = leadRestoreTool(leadDeps())
    expect(renderText(restore, { lead_id: 'l1' }, { lead_id: 'l1', status: 'active' })).toContain('已恢复')
    const purge = leadPurgeTool(leadDeps())
    expect(renderText(purge, { lead_id: 'l1' }, { purged: true })).toContain('已物理删除')
    expect(renderText(purge, { lead_id: 'l1' }, { purged: false })).toContain('未删除')

    const extract = leadExtractTool(leadDeps())
    const rich = renderText(extract, {}, {
      fields: { company_name: '甲公司', contact_name: '王经理', phone: '138', email: 'a@b.c', industry: '餐饮', company_size: '1-10', demand_desc: '要获客', budget_range: '5万', decision_role: 'decision_maker' },
      notes: '预算未提及',
    })
    expect(rich).toContain('甲公司')
    expect(rich).toContain('预算未提及')
    const bare = renderText(extract, {}, { fields: {} })
    expect(bare).toContain('未写库')
  })

  it('lead_export renders both formats over the filtered rows', async () => {
    const tool = leadExportTool(leadDeps())
    const markdown = await tool.execute({ format: 'markdown' }, EXEC) as { count: number; content: string }
    expect(markdown.count).toBe(1)
    expect(markdown.content).toContain('| id | company_name |')
    const csv = await tool.execute({ format: 'csv' }, EXEC) as { content: string }
    expect(csv.content).toContain('id,company_name')
    expect(renderText(tool, { format: 'csv' }, { format: 'csv', count: 1, content: 'id,company_name' })).toContain('已导出 1 条线索')
  })

  it('lead_document tools add, list (with and without bodies), and remove', async () => {
    const add = leadDocumentAddTool(leadDeps())
    const added = await add.execute({ lead_id: 'l1', title: '资料', content: '正文' }, EXEC) as { document: { id: string } }
    expect(added.document.id).toBe('d1')
    expect(renderText(add, {}, { document: { id: 'd1', lead_id: 'l1', title: '资料' } })).toContain('已挂接资料')

    const list = leadDocumentListTool(leadDeps())
    const withBody = await list.execute({ lead_id: 'l1', include_content: true }, EXEC) as { items: { content?: string }[] }
    expect(withBody.items[0]?.content).toBe('正文')
    expect(renderText(list, {}, { items: [{ id: 'd1', title: '资料', char_count: 2 }] })).toContain('挂接资料 1 份')
    const bareList = leadDocumentListTool(leadDeps({ listDocuments: () => [{ id: 'd1', title: '资料', char_count: 2 }] }))
    const withoutBody = await bareList.execute({ lead_id: 'l1' }, EXEC) as { items: { content?: string }[] }
    expect(withoutBody.items[0]?.content).toBeUndefined()
    expect(renderText(list, {}, { items: [] })).toContain('暂无挂接资料')

    const remove = leadDocumentRemoveTool(leadDeps())
    await expect(remove.execute({ document_id: 'd1' }, EXEC)).resolves.toEqual({ removed: true })
    expect(renderText(remove, { document_id: 'd1' }, { removed: true })).toContain('已移除')
    expect(renderText(remove, { document_id: 'd1' }, { removed: false })).toContain('未移除')
  })

  it('lead_followup tools append and page', async () => {
    const add = leadFollowupAddTool(leadDeps())
    const added = await add.execute({ lead_id: 'l1', content: '聊过' }, EXEC) as { followup: { id: string } }
    expect(added.followup.id).toBe('f1')
    expect(renderText(add, { lead_id: 'l1', content: '聊过' }, { followup: { id: 'f1', lead_id: 'l1', created_at: 3 } })).toContain('已新增跟进记录')

    const list = leadFollowupListTool(leadDeps())
    const page = await list.execute({ lead_id: 'l1', limit: 10, offset: 0 }, EXEC) as { total: number }
    expect(page.total).toBe(1)
    expect(renderText(list, {}, { items: [], total: 0 })).toContain('当前页无记录')
    expect(renderText(list, {}, { items: [{ id: 'f1', content: '聊过', created_at: 3 }], total: 1 })).toContain('聊过')
  })
})

describe('scoring tool renders across sparse and rich values', () => {
  it('score_batch renders successes, failures, and the empty batch', () => {
    const tool = scoreBatchTool(scoringDeps())
    const populated = renderText(tool, {}, {
      runs: [{ lead_id: 'l1', run_id: 'r1', total: 88.5, intent_tag: 'high' }],
      failed: [{ lead_id: 'l2', error: '线索不存在' }],
    })
    expect(populated).toContain('成功 1 条，失败 1 条')
    expect(populated).toContain('高意向')
    expect(populated).toContain('线索不存在')
    expect(renderText(tool, {}, { runs: [], failed: [] })).toContain('成功 0 条')
  })

  it('score_history renders entries with items and the empty page', () => {
    const tool = scoreHistoryTool(scoringDeps())
    const populated = renderText(tool, {}, {
      items: [{
        run: { id: 'r1', lead_id: 'l1', total: 40, intent_tag: 'low', reason: '整体偏弱', created_at: 0 },
        items: [{ dimension_id: 'a', score: 40, weight: 100, reason: '偏弱' }],
      }],
      total: 1,
    })
    expect(populated).toContain('低意向')
    expect(populated).toContain('整体偏弱')
    expect(populated).toContain('偏弱')
    expect(renderText(tool, {}, { items: [], total: 0 })).toContain('当前页无记录')
    expect(tool.presentCall?.({ lead_id: 'l1' })).toMatchObject({ rawInput: 'l1' })
    expect(tool.presentCall?.({ run_id: 'r1' })).toMatchObject({ rawInput: 'r1' })
    expect(tool.presentCall?.({})).toMatchObject({ rawInput: '' })
  })

  it('icp renders cover create, update, delete, and the list with and without industry', () => {
    const create = icpCreateTool(scoringDeps())
    expect(renderText(create, {}, { profile: { id: 'icp1', name: '画像甲', enabled: true } })).toContain('启用中')
    expect(renderText(create, {}, { profile: { id: 'icp1', name: '画像甲', enabled: false } })).toContain('已停用')

    const list = icpListTool(scoringDeps())
    const withIndustry = renderText(list, {}, { items: [storedProfile()] })
    expect(withIndustry).toContain('餐饮')
    expect(withIndustry).toContain('budget（100%）')
    const bareProfile = { id: 'icp2', name: '通用画像', enabled: false, dimensions: [] }
    const withoutIndustry = renderText(list, {}, { items: [bareProfile] })
    expect(withoutIndustry).toContain('通用')
    expect(renderText(list, {}, { items: [] })).toContain('尚无 ICP 画像')

    const remove = icpDeleteTool(scoringDeps())
    expect(renderText(remove, {}, { deleted: true })).toContain('已删除')
    expect(renderText(remove, {}, { deleted: false })).toContain('未删除')
  })

  it('score template renders cover create, update, delete, and the list with and without industry', () => {
    const create = scoreTemplateCreateTool(scoringDeps())
    expect(renderText(create, {}, { template: { id: 't1', name: '模板甲', enabled: true } })).toContain('启用中')
    expect(renderText(create, {}, { template: { id: 't1', name: '模板甲', enabled: false } })).toContain('已停用')

    const list = scoreTemplateListTool(scoringDeps())
    expect(renderText(list, {}, { items: [storedTemplate()] })).toContain('餐饮')
    expect(renderText(list, {}, { items: [{ id: 't2', name: '通用模板', industry: undefined, prompt_text: 'p', enabled: true }] })).toContain('通用模板')
    expect(renderText(list, {}, { items: [] })).toContain('尚无打分模板')

    const remove = scoreTemplateDeleteTool(scoringDeps())
    expect(renderText(remove, {}, { deleted: true })).toContain('已删除')
    expect(renderText(remove, {}, { deleted: false })).toContain('未删除')

    const icpUpdateForRender = icpUpdateTool(scoringDeps())
    expect(renderText(icpUpdateForRender, { icp_profile_id: 'icp1' }, { profile: { id: 'icp1', name: '画像甲', enabled: true } })).toContain('启用中')
    expect(renderText(icpUpdateForRender, { icp_profile_id: 'icp1' }, { profile: { id: 'icp1', name: '画像甲', enabled: false } })).toContain('已停用')

    const templateUpdateForRender = scoreTemplateUpdateTool(scoringDeps())
    expect(renderText(templateUpdateForRender, { score_template_id: 't1' }, { template: { id: 't1', name: '模板甲', enabled: true } })).toContain('启用中')
    expect(renderText(templateUpdateForRender, { score_template_id: 't1' }, { template: { id: 't1', name: '模板甲', enabled: false } })).toContain('已停用')
  })
})

describe('scoring tool execution paths', () => {
  it('icp_update forwards the patch fields', async () => {
    const updateIcpProfile = vi.fn(async () => storedProfile())
    const tool = icpUpdateTool(scoringDeps({ updateIcpProfile }))
    const value = await tool.execute({ icp_profile_id: 'icp1', name: '新名', enabled: false }, EXEC) as { profile: { id: string } }
    expect(value.profile.id).toBe('icp1')
    expect(updateIcpProfile).toHaveBeenCalledWith('icp1', { name: '新名', enabled: false }, FULL_OPERATOR, 'agent')
  })

  it('icp_list forwards the enabled-only flag', async () => {
    const listIcpProfiles = vi.fn(() => [storedProfile()])
    const tool = icpListTool(scoringDeps({ listIcpProfiles }))
    await tool.execute({ enabled_only: true }, EXEC)
    expect(listIcpProfiles).toHaveBeenCalledWith(true)
  })

  it('every scoring create/update/list tool accepts both the minimal and the maximal form', async () => {
    const storedProfile = {
      id: 'icp1', name: '画像甲', industry: undefined, enabled: true,
      dimensions: [{ id: 'budget', name: '预算', description: '说明', weight: 100 }],
      created_at: 1, updated_at: 1,
    }
    const storedTemplate = { id: 't1', name: '模板甲', industry: undefined, prompt_text: 'p', enabled: false, created_at: 1, updated_at: 1 }

    const createIcpProfile = vi.fn(async () => storedProfile)
    const icpCreate = icpCreateTool(scoringDeps({ createIcpProfile }))
    await icpCreate.execute({
      name: '画像', industry: '餐饮', dimensions: [{ id: 'a', name: 'A', description: 'd', weight: 100 }], enabled: false,
    }, EXEC)
    expect(createIcpProfile).toHaveBeenLastCalledWith({
      name: '画像', industry: '餐饮', dimensions: [{ id: 'a', name: 'A', description: 'd', weight: 100 }], enabled: false,
    }, FULL_OPERATOR, 'agent')
    await icpCreate.execute({ name: '画像', dimensions: [{ id: 'a', name: 'A', description: 'd', weight: 100 }] }, EXEC)
    expect(createIcpProfile).toHaveBeenLastCalledWith({
      name: '画像', dimensions: [{ id: 'a', name: 'A', description: 'd', weight: 100 }],
    }, FULL_OPERATOR, 'agent')

    const updateIcpProfile = vi.fn(async () => storedProfile)
    const icpUpdate = icpUpdateTool(scoringDeps({ updateIcpProfile }))
    await icpUpdate.execute({
      icp_profile_id: 'icp1', name: '新名', industry: '零售', enabled: true,
      dimensions: [{ id: 'b', name: 'B', description: 'd', weight: 100 }],
    }, EXEC)
    expect(updateIcpProfile).toHaveBeenLastCalledWith('icp1', {
      name: '新名', industry: '零售', enabled: true,
      dimensions: [{ id: 'b', name: 'B', description: 'd', weight: 100 }],
    }, FULL_OPERATOR, 'agent')
    await icpUpdate.execute({ icp_profile_id: 'icp1' }, EXEC)
    expect(updateIcpProfile).toHaveBeenLastCalledWith('icp1', {}, FULL_OPERATOR, 'agent')

    const createScoreTemplate = vi.fn(async () => storedTemplate)
    const templateCreate = scoreTemplateCreateTool(scoringDeps({ createScoreTemplate }))
    await templateCreate.execute({ name: '模板', industry: '餐饮', prompt_text: 'p', enabled: true }, EXEC)
    expect(createScoreTemplate).toHaveBeenLastCalledWith(
      { name: '模板', industry: '餐饮', prompt_text: 'p', enabled: true },
      FULL_OPERATOR, 'agent',
    )
    await templateCreate.execute({ name: '模板', prompt_text: 'p' }, EXEC)
    expect(createScoreTemplate).toHaveBeenLastCalledWith(
      { name: '模板', prompt_text: 'p' },
      FULL_OPERATOR, 'agent',
    )

    const updateScoreTemplate = vi.fn(async () => storedTemplate)
    const templateUpdate = scoreTemplateUpdateTool(scoringDeps({ updateScoreTemplate }))
    await templateUpdate.execute({
      score_template_id: 't1', name: '新模板', industry: '零售', prompt_text: 'q', enabled: false,
    }, EXEC)
    expect(updateScoreTemplate).toHaveBeenLastCalledWith('t1', {
      name: '新模板', industry: '零售', prompt_text: 'q', enabled: false,
    }, FULL_OPERATOR, 'agent')
    await templateUpdate.execute({ score_template_id: 't1' }, EXEC)
    expect(updateScoreTemplate).toHaveBeenLastCalledWith('t1', {}, FULL_OPERATOR, 'agent')

    const listScoreTemplates = vi.fn(() => [storedTemplate])
    const templateList = scoreTemplateListTool(scoringDeps({ listScoreTemplates }))
    await templateList.execute({ enabled_only: true }, EXEC)
    await templateList.execute({}, EXEC)
    expect(renderText(templateList, {}, { items: [storedTemplate] })).toContain('通用')
    const industryTemplate = { ...storedTemplate, industry: '餐饮' }
    expect(renderText(templateList, {}, { items: [industryTemplate] })).toContain('餐饮')

    const listIcpProfiles = vi.fn(() => [storedProfile])
    const icpList = icpListTool(scoringDeps({ listIcpProfiles }))
    await icpList.execute({ enabled_only: true }, EXEC)
    await icpList.execute({}, EXEC)
    expect(renderText(icpList, {}, { items: [storedProfile] })).toContain('通用')
    const industryProfile = { ...storedProfile, industry: '餐饮' }
    expect(renderText(icpList, {}, { items: [industryProfile] })).toContain('餐饮')
  })

  it('icp_delete and the score-template CRUD envelope their results', async () => {
    const deleteIcpProfile = vi.fn(async () => undefined)
    await expect(icpDeleteTool(scoringDeps({ deleteIcpProfile })).execute({ icp_profile_id: 'icp1' }, EXEC))
      .resolves.toEqual({ deleted: true })
    expect(deleteIcpProfile).toHaveBeenCalledWith('icp1', FULL_OPERATOR, 'agent')

    const createScoreTemplate = vi.fn(async () => storedTemplate())
    const created = await scoreTemplateCreateTool(scoringDeps({ createScoreTemplate })).execute({
      name: '模板甲', prompt_text: 'p',
    }, EXEC) as { template: { id: string } }
    expect(created.template.id).toBe('t1')

    const updateScoreTemplate = vi.fn(async () => storedTemplate())
    const updated = await scoreTemplateUpdateTool(scoringDeps({ updateScoreTemplate })).execute({
      score_template_id: 't1', prompt_text: '新正文',
    }, EXEC) as { template: { id: string } }
    expect(updated.template.id).toBe('t1')
    expect(updateScoreTemplate).toHaveBeenCalledWith('t1', { prompt_text: '新正文' }, FULL_OPERATOR, 'agent')

    const listScoreTemplates = vi.fn(() => [storedTemplate()])
    const listed = await scoreTemplateListTool(scoringDeps({ listScoreTemplates })).execute({}, EXEC) as { items: unknown[] }
    expect(listed.items).toHaveLength(1)
    expect(listScoreTemplates).toHaveBeenCalledWith(false)

    const deleteScoreTemplate = vi.fn(async () => undefined)
    await expect(scoreTemplateDeleteTool(scoringDeps({ deleteScoreTemplate })).execute({ score_template_id: 't1' }, EXEC))
      .resolves.toEqual({ deleted: true })
  })
})

describe('P0 tool renders missed by the P0 suites', () => {
  it('audit_list renders the empty page, rows with and without object ids, and defaults its paging', async () => {
    const listAudit = vi.fn(() => ({ items: [], total: 0 }))
    const tool = auditListTool({ listAudit } as never)
    expect(renderText(tool, {}, { items: [], total: 0 })).toContain('当前页无记录')
    await tool.execute({}, EXEC)
    expect(listAudit).toHaveBeenCalledWith(expect.objectContaining({ limit: 20, offset: 0 }))
    const populated = renderText(tool, {}, {
      items: [
        { id: 'a1', source: 'web', operator_user_id: 'u1', action: 'lead.create', object_type: 'lead', object_id: 'l1', summary: '创建', created_at: 0 },
        { id: 'a2', source: 'agent', operator_user_id: 'u1', action: 'settings.update', object_type: 'settings', summary: '更新', created_at: 0 },
      ],
      total: 2,
    })
    expect(populated).toContain('lead:l1')
    expect(populated).toContain('settings — 更新')
  })

  it('audit_export renders its envelope', () => {
    const tool = auditExportTool(ledgerOf() as never, permissionOf())
    expect(renderText(tool, { format: 'markdown' }, { format: 'markdown', count: 0, content: '' })).toContain('已导出 0 条')
  })

  it('settings renders cover set and unset defaults', async () => {
    const get = settingsGetTool(ledgerOf() as never)
    const sparse = renderText(get, {}, {
      settings: { geo_max_pages: 10, geo_page_timeout_ms: 10_000, sop_todo_write_enabled: true },
    })
    expect(sparse).toContain('(未设置)')
    const rich = renderText(get, {}, {
      settings: { default_icp_profile_id: 'icp1', default_score_template_id: 't1', geo_max_pages: 12, geo_page_timeout_ms: 8_000, sop_todo_write_enabled: false },
    })
    expect(rich).toContain('icp1')
    expect(rich).toContain('t1')

    const updateSettings = vi.fn(async () => ({
      default_icp_profile_id: 'icp1', default_score_template_id: 't1', geo_max_pages: 18,
      geo_page_timeout_ms: 9_000, sop_todo_write_enabled: false,
    }))
    const set = settingsSetTool({ updateSettings } as never, permissionOf())
    expect(renderText(set, {}, { settings: { geo_max_pages: 15, geo_page_timeout_ms: 10_000, sop_todo_write_enabled: true } })).toContain('geo_max_pages: 15')
    await set.execute({
      default_icp_profile_id: 'icp1',
      default_score_template_id: 't1',
      geo_max_pages: 18,
      geo_page_timeout_ms: 9_000,
      sop_todo_write_enabled: false,
    }, EXEC)
    expect(updateSettings).toHaveBeenCalledWith({
      default_icp_profile_id: 'icp1',
      default_score_template_id: 't1',
      geo_max_pages: 18,
      geo_page_timeout_ms: 9_000,
      sop_todo_write_enabled: false,
    }, FULL_OPERATOR, 'agent')
    await set.execute({ sop_todo_write_enabled: true }, EXEC)
    expect(updateSettings).toHaveBeenLastCalledWith(
      { sop_todo_write_enabled: true },
      FULL_OPERATOR,
      'agent',
    )
  })
})

describe('every P1 tool presents a generic call card', () => {
  it('declares card=generic with a Chinese title across the registry', () => {
    const lead = leadDeps()
    const scoring = scoringDeps()
    const tools: ToolDefinition[] = [
      leadCreateTool(lead), leadUpdateTool(lead), leadGetTool(lead), leadListTool(lead),
      leadDeleteTool(lead), leadRestoreTool(lead), leadPurgeTool(lead), leadAssignTool(lead),
      leadTransferTool(lead), leadExtractTool(lead), leadExportTool(lead), leadDocumentAddTool(lead),
      leadDocumentListTool(lead), leadDocumentRemoveTool(lead), leadFollowupAddTool(lead), leadFollowupListTool(lead),
      scoreOneTool(scoring), scoreBatchTool(scoring), scoreHistoryTool(scoring),
      icpCreateTool(scoring), icpUpdateTool(scoring), icpListTool(scoring), icpDeleteTool(scoring),
      scoreTemplateCreateTool(scoring), scoreTemplateUpdateTool(scoring), scoreTemplateListTool(scoring),
      scoreTemplateDeleteTool(scoring),
    ]
    expect(tools).toHaveLength(27)
    for (const tool of tools) {
      const view = tool.presentCall?.(sampleArgs(tool.name))
      expect(view?.card, tool.name).toBe('generic')
      expect((view as { title?: string }).title, tool.name).toBeTruthy()
    }
  })

  it('the lead list call card falls back through keyword, status, and empty raw input', () => {
    const list = leadListTool(leadDeps())
    expect(list.presentCall?.({ q: '甲' })).toMatchObject({ card: 'generic', rawInput: '甲' })
    expect(list.presentCall?.({ status: 'recycled' })).toMatchObject({ rawInput: 'status=recycled' })
    expect(list.presentCall?.({})).toMatchObject({ rawInput: '' })
  })
})

/** Minimal args each presentCall accepts; absent optionals keep their undefined. */
function sampleArgs(name: string): Record<string, unknown> {
  if (name.endsWith('lead_create')) return { company_name: '公司' }
  if (name.endsWith('lead_update')) return { lead_id: 'l1' }
  if (name.endsWith('lead_get')) return { lead_id: 'l1' }
  if (name.endsWith('lead_delete')) return { lead_id: 'l1' }
  if (name.endsWith('lead_restore')) return { lead_id: 'l1' }
  if (name.endsWith('lead_purge')) return { lead_id: 'l1' }
  if (name.endsWith('lead_assign')) return { lead_id: 'l1', owner_id: 'u1' }
  if (name.endsWith('lead_transfer')) return { lead_id: 'l1' }
  if (name.endsWith('lead_extract')) return { text: '文本' }
  if (name.endsWith('lead_export')) return { format: 'csv' }
  if (name.endsWith('lead_document_add')) return { lead_id: 'l1', title: 't', content: 'c' }
  if (name.endsWith('lead_document_list')) return { lead_id: 'l1' }
  if (name.endsWith('lead_document_remove')) return { document_id: 'd1' }
  if (name.endsWith('lead_followup_add')) return { lead_id: 'l1', content: 'c' }
  if (name.endsWith('lead_followup_list')) return { lead_id: 'l1' }
  if (name.endsWith('score_one')) return { lead_id: 'l1' }
  if (name.endsWith('score_batch')) return { lead_ids: ['l1'] }
  if (name.endsWith('score_history')) return { lead_id: 'l1' }
  if (name.endsWith('icp_create')) return { name: '画像', dimensions: [] }
  if (name.endsWith('icp_update')) return { icp_profile_id: 'icp1' }
  if (name.endsWith('icp_delete')) return { icp_profile_id: 'icp1' }
  if (name.endsWith('score_template_create')) return { name: '模板', prompt_text: 'p' }
  if (name.endsWith('score_template_update')) return { score_template_id: 't1' }
  if (name.endsWith('score_template_delete')) return { score_template_id: 't1' }
  return {}
}
