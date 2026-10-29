import { describe, expect, it, vi } from 'vitest'
import type { LeadLedgerService } from '../src/leads/service.ts'
import type { LeadScoringService } from '../src/scoring/service.ts'
import type { NurtureContentService } from '../src/content/service.ts'
import type { SopService } from '../src/sop/service.ts'
import type { PermissionContextService, ResolvedOperator } from '../src/permission/types.ts'
import { FULL_OPERATOR } from './helpers-p1.ts'
import { contentTemplateManageTool, icpManageTool, leadManageTool, scoreTemplateManageTool, sopTaskManageTool, sopTemplateManageTool } from '../src/tools/manage.ts'
import type { ToolRunContext } from '@deepseek-ai/dsh-tools'
import type { ContentBlock } from '@deepseek-ai/dsh-llm'

const EXEC: ToolRunContext = {
  callId: 'call-1',
  rootCallId: 'call-1',
  name: 'probe',
  arguments: {},
  signal: new AbortController().signal,
  agent: { id: 'agent-9' },
} as never

function permissionStub(): PermissionContextService {
  return { resolve: async (): Promise<ResolvedOperator> => FULL_OPERATOR } as never
}

function textOf(blocks: readonly ContentBlock[]): string {
  return blocks.filter((block): block is Extract<ContentBlock, { type: 'text' }> => block.type === 'text').map(block => block.text).join('\n')
}

function ledgerStub(overrides: Record<string, unknown> = {}): LeadLedgerService {
  return {
    createLead: async () => ({
      id: 'l1', company_name: '公司甲', source: 'manual', opportunity_stage: 'new',
      status: 'active', owner_id: 'local-default', tags: [], created_at: 1, updated_at: 2,
    }),
    updateLead: async () => ({
      id: 'l1', company_name: '公司甲', source: 'manual', opportunity_stage: 'new',
      status: 'active', owner_id: 'local-default', tags: [], created_at: 1, updated_at: 3,
    }),
    getLeadDetail: () => ({
      lead: { id: 'l1', company_name: '公司甲', source: 'manual', opportunity_stage: 'new', status: 'active', tags: [], updated_at: 2 },
      demand_desc: '需求', followups: [], documents: [],
    }),
    listLeads: () => ({ items: [], total: 0 }),
    ...overrides,
  } as never
}

function scoringStub(overrides: Record<string, unknown> = {}): LeadScoringService {
  return {
    createIcpProfile: async () => ({ id: 'icp1', name: '画像', enabled: true }),
    updateIcpProfile: async () => ({ id: 'icp1', name: '画像', enabled: false }),
    listIcpProfiles: () => [{
      id: 'icp1', name: '画像', industry: undefined, enabled: true,
      dimensions: [{ id: 'a', name: 'A', description: 'x', weight: 100 }],
    }],
    deleteIcpProfile: async () => undefined,
    createScoreTemplate: async () => ({ id: 't1', name: '模板', enabled: true }),
    updateScoreTemplate: async () => ({ id: 't1', name: '模板', enabled: true }),
    listScoreTemplates: () => [],
    deleteScoreTemplate: async () => undefined,
    ...overrides,
  } as never as LeadScoringService
}

function contentStub(overrides: Record<string, unknown> = {}): NurtureContentService {
  return {
    createTemplate: async () => ({ id: 'ct1', name: '文案', type: 'sms_followup', enabled: true }),
    updateTemplate: async () => ({ id: 'ct1', name: '文案', type: 'sms_followup', enabled: false }),
    listTemplates: () => [{
      id: 'ct1', name: '文案', industry: '餐饮', type: 'sms_followup', body: '{{sender_name}}',
      variables: [{ name: 'sender_name', description: '署名', example: '李秉凌' }], enabled: true,
    }],
    deleteTemplate: async () => undefined,
    ...overrides,
  } as never as NurtureContentService
}

function sopStub(overrides: Record<string, unknown> = {}): SopService {
  return {
    createTemplate: async () => ({ id: 'sop1', name: 'SOP', enabled: true }),
    updateTemplate: async () => ({ id: 'sop1', name: 'SOP', enabled: true }),
    listTemplates: () => [{
      id: 'sop1', name: 'SOP', industry: undefined, enabled: true,
      rules: [{ intent_level: 'high', cadence: 'D+0 问候', points: ['要点'], questions: [], risks: [] }],
    }],
    deleteTemplate: async () => undefined,
    listTasks: () => ({
      items: [{
        id: 'task1', lead_id: 'l1', title: '首访', status: 'pending',
        planned_at: 1, created_at: 0,
      }],
      total: 1,
    }),
    updateTask: async () => ({ id: 'task1', status: 'done', planned_at: 2 }),
    ...overrides,
  } as never as SopService
}

describe('lead_manage', () => {
  it('only action is schema-required and per-action fields stay optional', () => {
    const tool = leadManageTool({ ledger: ledgerStub(), permission: permissionStub() })
    for (const [key, def] of Object.entries(tool.parameters as Record<string, { required?: boolean }>)) {
      expect(def.required === true).toBe(key === 'action')
    }
  })

  it('create forwards fields with company_name pinned and the agent channel', async () => {
    const createLead = vi.fn(async () => ({
      id: 'l1', company_name: '公司甲', source: 'chat', opportunity_stage: 'new',
      status: 'active', owner_id: 'local-default', tags: ['A'], created_at: 1, updated_at: 2,
    }))
    const tool = leadManageTool({ ledger: ledgerStub({ createLead }), permission: permissionStub() })
    const value = await tool.execute({
      action: 'create', company_name: '公司甲', source: 'chat', tags: ['A'], contact_name: '张三',
    }, EXEC) as { action: string; lead: { company_name: string } }
    expect(value.action).toBe('create')
    expect(value.lead.company_name).toBe('公司甲')
    expect(createLead).toHaveBeenCalledWith(
      { contact_name: '张三', source: 'chat', tags: ['A'], company_name: '公司甲' },
      FULL_OPERATOR,
      'agent',
    )
    expect(textOf(tool.output.render({ action: 'create' }, value))).toContain('已创建')
  })

  it('rejects create without company_name and update/get without lead_id', async () => {
    const tool = leadManageTool({ ledger: ledgerStub(), permission: permissionStub() })
    await expect(tool.execute({ action: 'create' }, EXEC)).rejects.toThrow('company_name')
    await expect(tool.execute({ action: 'update', contact_name: '张三' }, EXEC)).rejects.toThrow('lead_id')
    await expect(tool.execute({ action: 'get' }, EXEC)).rejects.toThrow('lead_id')
  })

  it('update forwards only the editable patch fields', async () => {
    const updateLead = vi.fn(async () => ({
      id: 'l1', company_name: '公司甲', source: 'manual', opportunity_stage: 'contacted',
      status: 'active', owner_id: 'local-default', tags: [], created_at: 1, updated_at: 3,
    }))
    const tool = leadManageTool({ ledger: ledgerStub({ updateLead }), permission: permissionStub() })
    await tool.execute({ action: 'update', lead_id: 'l1', opportunity_stage: 'contacted', action_extra: 'x' } as never, EXEC)
    expect(updateLead).toHaveBeenCalledWith(
      'l1',
      { opportunity_stage: 'contacted' },
      FULL_OPERATOR,
      'agent',
    )
  })

  it('get spreads the detail envelope and renders followups and documents', async () => {
    const getLeadDetail = vi.fn(() => ({
      lead: { id: 'l1', company_name: '公司甲', source: 'manual', opportunity_stage: 'new', status: 'active', tags: [], updated_at: 2 },
      demand_desc: '需求',
      budget_range: '10-50万',
      followups: [{ id: 'f1', content: '首访', created_at: 1 }],
      documents: [{ id: 'd1', title: '行业资料' }],
    }))
    const tool = leadManageTool({ ledger: ledgerStub({ getLeadDetail }), permission: permissionStub() })
    const value = await tool.execute({ action: 'get', lead_id: 'l1' }, EXEC) as { action: string; demand_desc: string }
    expect(value.action).toBe('get')
    expect(value.demand_desc).toBe('需求')
    expect(getLeadDetail).toHaveBeenCalledWith('l1', FULL_OPERATOR)
    const text = textOf(tool.output.render({ action: 'get' }, value))
    expect(text).toContain('最近跟进 1 条')
    expect(text).toContain('挂接资料 1 份：行业资料')
  })

  it('list forwards only the declared filters and paging', async () => {
    const listLeads = vi.fn(() => ({ items: [], total: 4 }))
    const tool = leadManageTool({ ledger: ledgerStub({ listLeads }), permission: permissionStub() })
    const value = await tool.execute({ action: 'list', status: 'recycled', q: '甲', limit: 5, action_extra: 'y' } as never, EXEC) as { total: number }
    expect(value.total).toBe(4)
    expect(listLeads).toHaveBeenCalledWith(
      expect.objectContaining({ status: 'recycled', q: '甲', limit: 5 }),
      FULL_OPERATOR,
    )
    const listCalls = listLeads.mock.calls as unknown as Array<[{ args?: Record<string, unknown> }, unknown]>
    const firstListCall = listCalls.length > 0 ? listCalls[0] : undefined
    expect(firstListCall?.[0]).not.toHaveProperty('action_extra')
    expect(textOf(tool.output.render({ action: 'list' }, { action: 'list', items: [], total: 4 }))).toContain('共 4 条')
  })
})

describe('icp_manage', () => {
  it('create forwards the dimension list and update/delete/list dispatch to the service', async () => {
    const createIcpProfile = vi.fn(async () => ({ id: 'icp1', name: '画像', enabled: true }))
    const updateIcpProfile = vi.fn(async () => ({ id: 'icp1', name: '画像', enabled: false }))
    const deleteIcpProfile = vi.fn(async () => undefined)
    const listIcpProfiles = vi.fn(() => [])
    const tool = icpManageTool({
      scoring: scoringStub({ createIcpProfile, updateIcpProfile, deleteIcpProfile, listIcpProfiles }),
      permission: permissionStub(),
    })

    const dims = [{ id: 'a', name: 'A', description: 'x', weight: 100 }]
    await tool.execute({ action: 'create', name: '画像', industry: '餐饮', dimensions: dims, enabled: true }, EXEC)
    expect(createIcpProfile).toHaveBeenCalledWith(
      { name: '画像', industry: '餐饮', dimensions: dims, enabled: true },
      FULL_OPERATOR,
      'agent',
    )
    await expect(tool.execute({ action: 'create', name: '画像' }, EXEC)).rejects.toThrow('dimensions')

    await tool.execute({ action: 'update', icp_profile_id: 'icp1', enabled: false }, EXEC)
    expect(updateIcpProfile).toHaveBeenCalledWith('icp1', { enabled: false }, FULL_OPERATOR, 'agent')

    await tool.execute({ action: 'delete', icp_profile_id: 'icp1' }, EXEC)
    expect(deleteIcpProfile).toHaveBeenCalledWith('icp1', FULL_OPERATOR, 'agent')

    await tool.execute({ action: 'list', enabled_only: true }, EXEC)
    expect(listIcpProfiles).toHaveBeenCalledWith(true)
  })

  it('list render lists profiles with weight percentages', () => {
    const tool = icpManageTool({ scoring: scoringStub(), permission: permissionStub() })
    const text = textOf(tool.output.render({}, {
      action: 'list',
      items: [{
        id: 'icp1', name: '画像', industry: undefined, enabled: true,
        dimensions: [{ id: 'budget_scale', weight: 60 }, { id: 'fit', weight: 40 }],
      }],
    } as never))
    expect(text).toContain('budget_scale（60%）')
    expect(text).toContain('通用')
  })
})

describe('score_template_manage', () => {
  it('create requires prompt_text and delete/update/list dispatch correctly', async () => {
    const createScoreTemplate = vi.fn(async () => ({ id: 't1', name: '模板', enabled: true }))
    const updateScoreTemplate = vi.fn(async () => ({ id: 't1', name: '模板', enabled: false }))
    const deleteScoreTemplate = vi.fn(async () => undefined)
    const listScoreTemplates = vi.fn(() => [])
    const tool = scoreTemplateManageTool({
      scoring: scoringStub({ createScoreTemplate, updateScoreTemplate, deleteScoreTemplate, listScoreTemplates }),
      permission: permissionStub(),
    })

    await expect(tool.execute({ action: 'create', name: '模板' }, EXEC)).rejects.toThrow('prompt_text')
    await tool.execute({ action: 'create', name: '模板', prompt_text: 'P {{lead}}' }, EXEC)
    expect(createScoreTemplate).toHaveBeenCalledWith({ name: '模板', prompt_text: 'P {{lead}}' }, FULL_OPERATOR, 'agent')

    await tool.execute({ action: 'update', score_template_id: 't1', enabled: false }, EXEC)
    expect(updateScoreTemplate).toHaveBeenCalledWith('t1', { enabled: false }, FULL_OPERATOR, 'agent')

    await tool.execute({ action: 'delete', score_template_id: 't1' }, EXEC)
    expect(deleteScoreTemplate).toHaveBeenCalledWith('t1', FULL_OPERATOR, 'agent')

    await tool.execute({ action: 'list' }, EXEC)
    expect(listScoreTemplates).toHaveBeenCalledWith(false)
  })
})

describe('content_template_manage', () => {
  it('create requires body, list maps variables, delete dispatches', async () => {
    const createTemplate = vi.fn(async () => ({ id: 'ct1', name: '文案', type: 'sms_followup', enabled: true }))
    const updateTemplate = vi.fn(async () => ({ id: 'ct1', name: '文案', type: 'sms_followup', enabled: false }))
    const deleteTemplate = vi.fn(async () => undefined)
    const listTemplates = vi.fn(() => [{
      id: 'ct1', name: '文案', industry: '餐饮', type: 'sms_followup', body: '{{sender_name}}',
      variables: [{ name: 'sender_name', description: '署名', example: '李秉凌' }], enabled: true,
    }])
    const tool = contentTemplateManageTool({
      content: contentStub({ createTemplate, updateTemplate, deleteTemplate, listTemplates }),
      permission: permissionStub(),
    })

    await expect(tool.execute({ action: 'create', name: '文案', type: 'sms_followup' }, EXEC)).rejects.toThrow('body')
    await tool.execute({ action: 'create', name: '文案', type: 'sms_followup', body: 'B' }, EXEC)
    expect(createTemplate).toHaveBeenCalledWith({ name: '文案', type: 'sms_followup', body: 'B' }, FULL_OPERATOR, 'agent')

    await tool.execute({ action: 'update', content_template_id: 'ct1', enabled: false }, EXEC)
    expect(updateTemplate).toHaveBeenCalledWith('ct1', { enabled: false }, FULL_OPERATOR, 'agent')

    const listed = await tool.execute({ action: 'list', enabled_only: true }, EXEC) as { items: { variables: { example?: string }[] }[] }
    expect(listTemplates).toHaveBeenCalledWith({ enabledOnly: true })
    const [firstItem] = listed.items
    expect(firstItem?.variables[0]?.example).toBe('李秉凌')

    await tool.execute({ action: 'delete', content_template_id: 'ct1' }, EXEC)
    expect(deleteTemplate).toHaveBeenCalledWith('ct1', FULL_OPERATOR, 'agent')
  })
})

describe('sop_template_manage', () => {
  it('create requires rules, maps rule copies, and list/delete dispatch', async () => {
    const createTemplate = vi.fn(async () => ({ id: 'sop1', name: 'SOP', enabled: true }))
    const updateTemplate = vi.fn(async () => ({ id: 'sop1', name: 'SOP', enabled: true }))
    const deleteTemplate = vi.fn(async () => undefined)
    const listTemplates = vi.fn(() => [{
      id: 'sop1', name: 'SOP', industry: undefined, enabled: true,
      rules: [{ intent_level: 'high', cadence: 'D+0 问候', points: ['要点'], questions: [], risks: [] }],
    }])
    const tool = sopTemplateManageTool({
      sop: sopStub({ createTemplate, updateTemplate, deleteTemplate, listTemplates }),
      permission: permissionStub(),
    })

    const rule = { intent_level: 'high', cadence: 'D+0 问候', points: ['要点'], questions: ['问'], risks: ['险'] }
    const rules = [rule]
    await expect(tool.execute({ action: 'create', name: 'SOP' }, EXEC)).rejects.toThrow('rules')
    await tool.execute({ action: 'create', name: 'SOP', rules }, EXEC)
    expect(createTemplate).toHaveBeenCalledWith({ name: 'SOP', rules: [rule] }, FULL_OPERATOR, 'agent')
    const calls = createTemplate.mock.calls as unknown as Array<[{ rules: Array<{ points: string[] }> }]>
    const forwarded = calls[0]?.[0]?.rules[0]
    expect(forwarded?.points).not.toBe(rule.points)
    expect(forwarded?.points).toEqual(['要点'])

    await tool.execute({ action: 'update', sop_template_id: 'sop1', enabled: true }, EXEC)
    expect(updateTemplate).toHaveBeenCalledWith('sop1', { enabled: true }, FULL_OPERATOR, 'agent')

    const listed = await tool.execute({ action: 'list' }, EXEC) as { items: unknown[] }
    expect(listTemplates).toHaveBeenCalledWith(false)
    expect(listed.items).toHaveLength(1)

    await tool.execute({ action: 'delete', sop_template_id: 'sop1' }, EXEC)
    expect(deleteTemplate).toHaveBeenCalledWith('sop1', FULL_OPERATOR, 'agent')
  })
})

describe('sop_task_manage', () => {
  it('update requires task_id and forwards status/note/planned_at; list forwards filters', async () => {
    const updateTask = vi.fn(async () => ({ id: 'task1', status: 'done', planned_at: 2 }))
    const listTasks = vi.fn(() => ({ items: [], total: 0 }))
    const tool = sopTaskManageTool({ sop: sopStub({ updateTask, listTasks }), permission: permissionStub() })

    await expect(tool.execute({ action: 'update', status: 'done' }, EXEC)).rejects.toThrow('task_id')
    await tool.execute({ action: 'update', task_id: 'task1', status: 'done', note: '已完成', planned_at: 99 }, EXEC)
    expect(updateTask).toHaveBeenCalledWith(
      'task1',
      { status: 'done', note: '已完成', planned_at: 99 },
      FULL_OPERATOR,
      'agent',
    )

    await tool.execute({ action: 'list', lead_id: 'l1', status: 'pending', limit: 3 }, EXEC)
    expect(listTasks).toHaveBeenCalledWith({ lead_id: 'l1', status: 'pending', limit: 3 }, FULL_OPERATOR)
  })

  it('renders the list page and the moved task', () => {
    const tool = sopTaskManageTool({ sop: sopStub(), permission: permissionStub() })
    const listText = textOf(tool.output.render({}, {
      action: 'list',
      items: [{ id: 'task1', lead_id: 'l1', title: '首访', status: 'pending', planned_at: Date.UTC(2026, 0, 5) }],
      total: 1,
    }))
    expect(listText).toContain('2026-01-05')
    expect(listText).toContain('首访')
    const movedText = textOf(tool.output.render({}, { action: 'update', task: { id: 'task1', status: 'done', planned_at: Date.UTC(2026, 0, 5) } }))
    expect(movedText).toContain('done')
  })
})
