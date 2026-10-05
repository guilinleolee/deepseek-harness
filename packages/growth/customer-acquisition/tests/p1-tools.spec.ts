import { describe, expect, it, vi } from 'vitest'
import type { LeadLedgerService } from '../src/leads/service.ts'
import type { LeadScoringService } from '../src/scoring/service.ts'
import type { PermissionContextService, ResolvedOperator } from '../src/permission/types.ts'
import { FULL_OPERATOR, OWN_OPERATOR } from './helpers-p1.ts'
import { UserId } from '../src/domain/ids.ts'
import {
  leadCreateTool, leadExportTool, leadExtractTool, leadGetTool, leadListTool, leadPurgeTool,
} from '../src/tools/leads.ts'
import {
  icpCreateTool, scoreBatchTool, scoreHistoryTool, scoreOneTool,
} from '../src/tools/scoring.ts'
import { registerP1Tools, P1_TOOL_NAMES } from '../src/tools/register-p1.ts'
import type { PromptCompletion } from '../src/llm/oneshot.ts'
import type { ToolRunContext } from '@deepseek-ai/dsh-tools'

const EXEC: ToolRunContext = {
  callId: 'call-1',
  rootCallId: 'call-1',
  name: 'probe',
  arguments: {},
  signal: new AbortController().signal,
  agent: { id: 'agent-9' },
} as never

function permissionSpy(returning: ResolvedOperator | Error = FULL_OPERATOR): {
  permission: PermissionContextService
  resolve: ReturnType<typeof vi.fn>
} {
  const resolve = vi.fn(async () => {
    if (returning instanceof Error) throw returning
    return returning
  })
  return { permission: { resolve } as never, resolve }
}

const completion: PromptCompletion = { complete: async () => '{}' }

function ledgerStub(overrides: Record<string, unknown> = {}): LeadLedgerService {
  return {
    createLead: async () => ({
      id: 'l1', company_name: '公司甲', source: 'manual', opportunity_stage: 'new',
      status: 'active', owner_id: UserId('local-default'), tags: [], created_at: 1, updated_at: 2,
    }),
    getLeadDetail: () => ({
      lead: { id: 'l1', company_name: '公司甲', source: 'manual', opportunity_stage: 'new', status: 'active', tags: [], updated_at: 2 },
      demand_desc: '需求',
      followups: [],
      documents: [],
    }),
    listLeads: () => ({ items: [], total: 0 }),
    extractLeadFields: async () => ({ fields: { company_name: '抽取公司' }, notes: '预算未识别' }),
    exportLeads: async () => [],
    ...overrides,
  } as never
}

function scoringStub(overrides: Record<string, unknown> = {}): LeadScoringService {
  return {
    scoreOne: async () => ({
      run: { id: 'r1', total: 77.5, intent_tag: 'mid', reason: '整体匹配' },
      items: [{ dimension_id: 'a', name: '维度A', score: 77.5, weight: 100, reason: 'A 理由' }],
    }),
    scoreBatch: async () => ({ runs: [], failed: [] }),
    history: () => ({ items: [], total: 0 }),
    createIcpProfile: async () => ({
      id: 'icp1', name: '画像', industry: undefined, enabled: true,
      dimensions: [{ id: 'a', name: 'A', description: 'x', weight: 100 }],
      created_at: 1, updated_at: 1,
    }),
    listIcpProfiles: () => [],
    ...overrides,
  } as never as LeadScoringService
}

describe('P1 tool registration', () => {
  it('registers exactly the 27 P1 tools in order and disposes them together', () => {
    const registered: string[] = []
    const disposers: (() => void)[] = []
    const ctx = {
      tools: {
        register: (tool: { name: string }) => {
          registered.push(tool.name)
          disposers.push(() => {})
          return () => { disposers.pop() }
        },
      },
      llm: {} as never,
    } as never
    const disposer = registerP1Tools(ctx, {
      ledger: ledgerStub(),
      scoring: scoringStub(),
      permission: permissionSpy().permission,
      policy: { provider: 'deepseek', model: 'deepseek-chat', timeoutMs: 120_000, maxOutputTokens: 2000 },
    })
    expect(registered).toEqual([...P1_TOOL_NAMES])
    expect(new Set(registered).size).toBe(registered.length)
    expect(registered.every(name => name.startsWith('customer_acquisition_'))).toBe(true)
    expect(registered).toHaveLength(27)
    disposer()
  })
})

describe('P1 lead tools wiring', () => {
  it('lead_create resolves the operator with the calling agent id and projects the ref', async () => {
    const { permission, resolve } = permissionSpy()
    const tool = leadCreateTool({ ledger: ledgerStub(), permission, completion })
    const value = await tool.execute({ company_name: '公司甲' }, EXEC) as { lead: { company_name: string } }
    expect(value.lead.company_name).toBe('公司甲')
    expect(resolve).toHaveBeenCalledWith({ via: 'agent', agentId: 'agent-9' })

    const [block] = tool.output.render({}, value)
    expect((block as { text: string }).text).toContain('公司甲')
    const call = tool.presentCall?.({ company_name: '公司甲' })
    expect(call).toEqual({ card: 'generic', title: '新建线索', rawInput: '公司甲' })
  })

  it('lead_get returns the service detail envelope verbatim', async () => {
    const tool = leadGetTool({ ledger: ledgerStub(), permission: permissionSpy().permission, completion })
    const value = await tool.execute({ lead_id: 'l1' }, EXEC) as { demand_desc?: string }
    expect(value.demand_desc).toBe('需求')
  })

  it('lead_list forwards the filters to the ledger', async () => {
    const listLeads = vi.fn(() => ({ items: [], total: 4 }))
    const tool = leadListTool({ ledger: ledgerStub({ listLeads }), permission: permissionSpy().permission, completion })
    const value = await tool.execute({ status: 'recycled', q: '甲', limit: 5 }, EXEC) as { total: number }
    expect(value.total).toBe(4)
    expect(listLeads).toHaveBeenCalledWith(expect.objectContaining({ status: 'recycled', q: '甲', limit: 5 }), FULL_OPERATOR)
  })

  it('lead_export enforces can_export before touching the ledger', async () => {
    const exportLeads = vi.fn(async () => [])
    const restricted = leadExportTool({
      ledger: ledgerStub({ exportLeads }),
      permission: permissionSpy(OWN_OPERATOR).permission,
      completion,
    })
    await expect(restricted.execute({ format: 'csv' }, EXEC)).rejects.toThrow('can_export')
    expect(exportLeads).not.toHaveBeenCalled()

    const allowed = leadExportTool({ ledger: ledgerStub({ exportLeads }), permission: permissionSpy().permission, completion })
    const value = await allowed.execute({ format: 'csv' }, EXEC) as { count: number; format: string; content: string }
    expect(value.format).toBe('csv')
    expect(value.count).toBe(0)
    expect(value.content).toContain('id,company_name')
  })

  it('lead_purge surfaces the global-delete capability error', async () => {
    const purgeLead = vi.fn(async () => { throw new Error('物理删除线索需要全局删除权限（can_delete_any_lead）') })
    const tool = leadPurgeTool({ ledger: ledgerStub({ purgeLead }), permission: permissionSpy().permission, completion })
    await expect(tool.execute({ lead_id: 'l1' }, EXEC)).rejects.toThrow('can_delete_any_lead')
  })

  it('lead_extract rides the injected completion and returns the fields', async () => {
    const extractLeadFields = vi.fn(async () => ({ fields: { company_name: '抽取公司' } }))
    const ledger = ledgerStub({ extractLeadFields })
    const tool = leadExtractTool({ ledger, permission: permissionSpy().permission, completion })
    const value = await tool.execute({ text: '一段文本', source_hint: 'form' }, EXEC) as { fields: { company_name?: string } }
    expect(value.fields.company_name).toBe('抽取公司')
    expect(extractLeadFields).toHaveBeenCalledWith(
      { text: '一段文本', sourceHint: 'form' },
      completion,
      FULL_OPERATOR,
      'agent',
    )

    const noHint = await tool.execute({ text: '另一段' }, EXEC) as { fields: { company_name?: string } }
    expect(noHint.fields.company_name).toBe('抽取公司')
    expect(extractLeadFields).toHaveBeenLastCalledWith(
      { text: '另一段' },
      completion,
      FULL_OPERATOR,
      'agent',
    )
    const long = '字'.repeat(61)
    expect(tool.presentCall?.({ text: long })).toMatchObject({ rawInput: `${long.slice(0, 60)}…` })
    expect(tool.presentCall?.({ text: '短文本' })).toMatchObject({ rawInput: '短文本' })
  })
})

describe('P1 scoring tools wiring', () => {
  it('score_one forwards the signal and renders the headline', async () => {
    const scoreOne = vi.fn(async () => ({
      run: { id: 'r1', total: 77.5, intent_tag: 'mid' as const, reason: '整体匹配' },
      items: [{ dimension_id: 'a', name: '维度A', score: 77.5, weight: 100, reason: 'A 理由' }],
    }))
    const tool = scoreOneTool({ scoring: scoringStub({ scoreOne }), permission: permissionSpy().permission })
    const value = await tool.execute({ lead_id: 'l1' }, EXEC) as { run: { total: number } }
    expect(value.run.total).toBe(77.5)
    expect(scoreOne).toHaveBeenCalledWith(
      { lead_id: 'l1' },
      FULL_OPERATOR,
      'agent',
      EXEC.signal,
    )
    const [block] = tool.output.render({}, value)
    expect((block as { text: string }).text).toContain('77.5')
    expect(tool.timeoutMs).toBe(120_000)

    await tool.execute({ lead_id: 'l1', icp_profile_id: 'p1', score_template_id: 't1' }, EXEC)
    expect(scoreOne).toHaveBeenLastCalledWith(
      { lead_id: 'l1', icp_profile_id: 'p1', score_template_id: 't1' },
      FULL_OPERATOR,
      'agent',
      EXEC.signal,
    )
  })

  it('score_batch and score_history forward their parameters', async () => {
    const scoreBatch = vi.fn(async () => ({ runs: [], failed: [] }))
    const batchTool = scoreBatchTool({ scoring: scoringStub({ scoreBatch }), permission: permissionSpy().permission })
    await batchTool.execute({ lead_ids: ['a', 'b'], icp_profile_id: 'p1', score_template_id: 't1' }, EXEC)
    expect(scoreBatch).toHaveBeenCalledWith(
      { lead_ids: ['a', 'b'], icp_profile_id: 'p1', score_template_id: 't1' },
      FULL_OPERATOR,
      'agent',
      EXEC.signal,
    )
    expect(batchTool.timeoutMs).toBe(600_000)

    await batchTool.execute({ lead_ids: ['l1'] }, EXEC)
    expect(scoreBatch).toHaveBeenLastCalledWith(
      { lead_ids: ['l1'] },
      FULL_OPERATOR,
      'agent',
      EXEC.signal,
    )

    const history = vi.fn(() => ({ items: [], total: 0 }))
    const historyTool = scoreHistoryTool({ scoring: scoringStub({ history }), permission: permissionSpy().permission })
    await historyTool.execute({ lead_id: 'l1', limit: 5, offset: 5 }, EXEC)
    expect(history).toHaveBeenCalledWith({ lead_id: 'l1', limit: 5, offset: 5 }, FULL_OPERATOR)
    await historyTool.execute({ run_id: 'r1' }, EXEC)
    expect(history).toHaveBeenLastCalledWith({ run_id: 'r1' }, FULL_OPERATOR)
  })

  it('icp_create passes explicit fields and the agent channel', async () => {
    const createIcpProfile = vi.fn(async () => ({
      id: 'icp1', name: '画像', industry: undefined, enabled: true,
      dimensions: [{ id: 'a', name: 'A', description: 'x', weight: 100 }],
      created_at: 1, updated_at: 1,
    }))
    const tool = icpCreateTool({ scoring: scoringStub({ createIcpProfile }), permission: permissionSpy().permission })
    const value = await tool.execute({
      name: '画像',
      industry: '餐饮',
      dimensions: [{ id: 'a', name: 'A', description: 'x', weight: 100 }],
      enabled: false,
    }, EXEC) as { profile: { id: string } }
    expect(value.profile.id).toBe('icp1')
    expect(createIcpProfile).toHaveBeenCalledWith(
      {
        name: '画像',
        industry: '餐饮',
        dimensions: [{ id: 'a', name: 'A', description: 'x', weight: 100 }],
        enabled: false,
      },
      FULL_OPERATOR,
      'agent',
    )
  })
})
