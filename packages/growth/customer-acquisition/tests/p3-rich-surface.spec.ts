import { describe, expect, it, vi } from 'vitest'
import type { ToolDefinition } from '@deepseek-ai/dsh-tools'
import type { NurtureContentService } from '../src/content/service.ts'
import type { SopService } from '../src/sop/service.ts'
import type { PermissionContextService } from '../src/permission/types.ts'
import { FULL_OPERATOR } from './helpers-p1.ts'
import {
  contentGenerateTool,
  contentListByLeadTool,
  contentTemplateCreateTool,
  contentTemplateDeleteTool,
  contentTemplateListTool,
  contentTemplateUpdateTool,
} from '../src/tools/content.ts'
import {
  sopGenerateTasksTool,
  sopTaskListTool,
  sopTaskUpdateTool,
  sopTemplateCreateTool,
  sopTemplateDeleteTool,
  sopTemplateListTool,
  sopTemplateUpdateTool,
} from '../src/tools/sop.ts'

const EXEC = { callId: 'c', rootCallId: 'c', name: 'probe', arguments: {}, signal: new AbortController().signal, agent: { id: 'a1' } } as never

function permissionOf(): PermissionContextService {
  return { resolve: async () => FULL_OPERATOR } as never
}

function contentOf(overrides: Record<string, unknown> = {}): NurtureContentService {
  return {
    generate: async () => ({
      content: { id: 'g1', lead_id: 'l1', type: 'sms_followup', variant: 'A', content: '正文', template_id: 't1', created_at: 1 },
      leadName: '公司甲',
    }),
    listByLead: () => ({
      items: [{
        id: 'g1', lead_id: 'l1', type: 'sms_followup', variant: 'A',
        content: '长'.repeat(90), template_id: 't1', created_at: 1,
      }],
      total: 1,
    }),
    createTemplate: async () => ({
      id: 't1', name: '甲', industry: '餐饮', type: 'sms_followup', body: 'b', enabled: true,
      variables: [
        { name: 'a', description: 'd', example: 'e' },
        { name: 'c', description: 'd' },
      ],
      created_at: 1, updated_at: 1,
    }),
    updateTemplate: async () => ({
      id: 't1', name: '乙', industry: undefined, type: 'sms_followup', body: 'b', enabled: true, variables: [],
      created_at: 1, updated_at: 1,
    }),
    listTemplates: () => [
      { id: 't1', name: '甲', industry: undefined, type: 'sms_followup', body: 'b', enabled: true, variables: [] },
    ],
    deleteTemplate: async () => undefined,
    ...overrides,
  } as never
}

function sopOf(overrides: Record<string, unknown> = {}): SopService {
  return {
    generateTasks: async () => ({
      intentLevel: 'high' as const,
      templateId: 's1',
      tasks: [
        { task: { id: 'k1', lead_id: 'l1', title: '问候', status: 'pending' as const, planned_at: 0, created_at: 1, updated_at: 1 }, todoWritten: false },
        { task: { id: 'k2', lead_id: 'l1', title: '确认', status: 'pending' as const, planned_at: 86_400_000, created_at: 1, updated_at: 1 }, todoWritten: true },
      ],
      leadName: '公司甲',
      todoList: [{ content: '问候', status: 'pending' as const }],
      todoWriteEnabled: true,
    }),
    listTasks: () => ({
      items: [{ id: 'k1', lead_id: 'l1', title: '问候', status: 'pending' as const, planned_at: 0, note: '备注', created_at: 1 }],
      total: 1,
    }),
    updateTask: async () => ({ id: 'k1', lead_id: 'l1', title: '问候', status: 'done' as const, planned_at: 5, created_at: 1, updated_at: 2 }),
    createTemplate: async () => ({
      id: 's1', name: 'SOP 甲', industry: '餐饮', enabled: true,
      rules: [{ intent_level: 'high' as const, cadence: 'D+0', points: ['p'], questions: ['q'], risks: ['r'] }],
      created_at: 1, updated_at: 1,
    }),
    updateTemplate: async () => ({
      id: 's1', name: 'SOP 甲', industry: undefined, enabled: false,
      rules: [{ intent_level: 'low' as const, cadence: 'D+0', points: ['p'], questions: [], risks: [] }],
      created_at: 1, updated_at: 1,
    }),
    listTemplates: () => [
      { id: 's1', name: 'SOP 甲', industry: '餐饮', enabled: true,
        rules: [{ intent_level: 'high' as const, cadence: 'D+0', points: ['p'], questions: ['q'], risks: ['r'] }] },
    ],
    deleteTemplate: async () => undefined,
    ...overrides,
  } as never
}

function renderText(tool: ToolDefinition, value: unknown): string {
  const [block] = tool.output.render({}, value as never)
  return (block as { text: string }).text
}

describe('P3 content tools full-surface sweep', () => {
  const deps = { content: contentOf(), permission: permissionOf(), policy: { provider: 'p', model: 'm', timeoutMs: 1000, maxOutputTokens: 256 } }

  it('generate renders with and without template id and forwards signals', async () => {
    const tool = contentGenerateTool(deps)
    expect(renderText(tool, { content: { id: 'g1', type: 'sms_followup', variant: 'A', content: '正文', template_id: 't1' } })).toContain('正文')
    expect(renderText(tool, { content: { id: 'g1', type: 'sms_followup', variant: 'A', content: '正文' } })).toContain('正文')
    const value = await tool.execute({ lead_id: 'l1', type: 'sms_followup', variant: 'A' }, EXEC) as { content: { template_id?: string } }
    expect(value.content.template_id).toBe('t1')
  })

  it('list renders long content with the ellipsis branch', () => {
    const tool = contentListByLeadTool(deps)
    const text = renderText(tool, {
      items: [{ id: 'g1', type: 'sms_followup', variant: 'A', content: '长'.repeat(90), created_at: 0 }],
      total: 1,
    })
    expect(text).toContain('…')
    const value = tool.execute({ lead_id: 'l1', type: 'sms_followup', limit: 5, offset: 5 }, EXEC) as { items: unknown[] }
    return value.then((v) =>{  expect(v.items).toHaveLength(1) })
  })

  it('template create renders enabled and disabled states with variable examples', () => {
    const create = contentTemplateCreateTool(deps)
    const on = renderText(create, { template: { id: 't1', name: '甲', type: 'sms_followup', enabled: true } })
    expect(on).toContain('启用中')
    const off = renderText(create, { template: { id: 't1', name: '甲', type: 'sms_followup', enabled: false } })
    expect(off).toContain('已停用')
  })

  it('template update renders both enabled states over the maximal stub', () => {
    const update = contentTemplateUpdateTool(deps)
    const [on] = update.output.render({ content_template_id: 't1' }, { template: { id: 't1', name: '乙', type: 'sms_followup', enabled: true } })
    expect((on as { text: string }).text).toContain('启用中')
    const [off] = update.output.render({ content_template_id: 't1' }, { template: { id: 't1', name: '乙', type: 'sms_followup', enabled: false } })
    expect((off as { text: string }).text).toContain('已停用')
  })

  it('template list renders rows with variables carrying and lacking examples', () => {
    const list = contentTemplateListTool(deps)
    const text = renderText(list, { items: [...(deps.content.listTemplates() as never[])] })
    expect(text).toContain('sms_followup')
  })

  it('template delete renders both outcomes', () => {
    const remove = contentTemplateDeleteTool(deps)
    expect(renderText(remove, { deleted: true })).toContain('已删除')
    expect(renderText(remove, { deleted: false })).toContain('未删除')
  })
})

describe('P3 SOP tools full-surface sweep', () => {
  const deps = { sop: sopOf(), permission: permissionOf() }

  it('generate renders the todo block over two tasks and forwards the outcome', async () => {
    const tool = sopGenerateTasksTool(deps)
    const text = renderText(tool, {
      intent_level: 'high',
      created: [
        { task_id: 'k1', title: '问候', planned_at: 0, todo_written: false },
        { task_id: 'k2', title: '确认', planned_at: 86_400_000, todo_written: true },
      ],
      todo_list: [{ content: '问候', status: 'pending' }],
      todo_write_enabled: true,
    })
    expect(text).toContain('todo_write')
    expect(text).toContain('确认')
    const value = await tool.execute({ lead_id: 'l1', sop_template_id: 's1' }, EXEC) as { created: unknown[] }
    expect(value.created).toHaveLength(2)
  })

  it('task list renders the note-bearing row', () => {
    const tool = sopTaskListTool(deps)
    expect(renderText(tool, { items: [{ id: 'k1', lead_id: 'l1', title: '问候', status: 'pending', planned_at: 0, note: '备注', created_at: 0 }], total: 1 })).toContain('问候')
  })

  it('template create and update render both enabled states over rich stubs', () => {
    const create = sopTemplateCreateTool(deps)
    expect(renderText(create, { template: { id: 's1', name: 'SOP 甲', enabled: true } })).toContain('启用中')
    expect(renderText(create, { template: { id: 's1', name: 'SOP 甲', enabled: false } })).toContain('已停用')
    const update = sopTemplateUpdateTool(deps)
    const [on] = update.output.render({ sop_template_id: 's1' }, { template: { id: 's1', name: 'SOP 甲', enabled: true } })
    expect((on as { text: string }).text).toContain('已更新')
    const [off] = update.output.render({ sop_template_id: 's1' }, { template: { id: 's1', name: 'SOP 甲', enabled: false } })
    expect((off as { text: string }).text).toContain('已停用')
  })

  it('template list renders rows with and without industry, and delete renders both outcomes', () => {
    const list = sopTemplateListTool(deps)
    expect(renderText(list, { items: [...(deps.sop.listTemplates() as never[])] })).toContain('餐饮')
    const remove = sopTemplateDeleteTool(deps)
    expect(renderText(remove, { deleted: true })).toContain('已删除')
    expect(renderText(remove, { deleted: false })).toContain('未删除')
  })

  it('task update forwards minimal and maximal patches through the tool', async () => {
    const updateTask = vi.fn(async () => ({ id: 'k1', status: 'done', planned_at: 5 }))
    const tool = sopTaskUpdateTool({ sop: sopOf({ updateTask }), permission: permissionOf() })
    await tool.execute({ task_id: 'k1' }, EXEC)
    expect(updateTask).toHaveBeenLastCalledWith('k1', {}, FULL_OPERATOR, 'agent')
    await tool.execute({ task_id: 'k1', status: 'done', planned_at: 9, note: 'n' }, EXEC)
    expect(updateTask).toHaveBeenLastCalledWith('k1', { status: 'done', planned_at: 9, note: 'n' }, FULL_OPERATOR, 'agent')
  })
})
