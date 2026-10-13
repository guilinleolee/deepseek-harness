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
  sopTemplateCreateTool,
  sopTemplateDeleteTool,
  sopTemplateListTool,
  sopTemplateUpdateTool,
} from '../src/tools/sop.ts'

const POLICY = { provider: 'p', model: 'm', timeoutMs: 1000, maxOutputTokens: 256 }
const EXEC = { callId: 'c', rootCallId: 'c', name: 'probe', arguments: {}, signal: new AbortController().signal, agent: { id: 'a1' } } as never

function permissionOf(): PermissionContextService {
  return { resolve: async () => FULL_OPERATOR } as never
}

function contentOf(): NurtureContentService {
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
  } as never
}

function sopOf(): SopService {
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
  } as never
}

function renderText(tool: ToolDefinition, value: unknown): string {
  const [block] = tool.output.render({}, value as never)
  return (block as { text: string }).text
}

describe('final P3 render and forward fills', () => {
  it('content tools cover the remaining render and forward branches', async () => {
    const deps = { content: contentOf(), permission: permissionOf(), policy: { provider: 'p', model: 'm', timeoutMs: 1000, maxOutputTokens: 256 } }

    const generate = contentGenerateTool(deps)
    expect(renderText(generate, { content: { id: 'g1', type: 'sms_followup', variant: 'A', content: '正文', template_id: 't1' } })).toContain('正文')
    expect(renderText(generate, { content: { id: 'g1', type: 'sms_followup', variant: 'A', content: '正文' } })).toContain('正文')
    const value = await generate.execute({ lead_id: 'l1', type: 'sms_followup', variant: 'A' }, EXEC) as { content: { template_id?: string } }
    expect(value.content.template_id).toBe('t1')

    const list = contentListByLeadTool(deps)
    expect(renderText(list, { items: [{ id: 'g1', type: 'sms_followup', variant: 'A', content: '长'.repeat(90), created_at: 0 }], total: 1 })).toContain('…')
    const listed = await list.execute({ lead_id: 'l1', type: 'sms_followup', limit: 5, offset: 5 }, EXEC) as { items: unknown[] }
    expect(listed.items).toHaveLength(1)

    const create = contentTemplateCreateTool(deps)
    const [createdOn] = create.output.render({}, { template: { id: 't1', name: '甲', type: 'sms_followup', enabled: true } })
    expect((createdOn as { text: string }).text).toContain('启用中')
    const [createdOff] = create.output.render({}, { template: { id: 't1', name: '甲', type: 'sms_followup', enabled: false } })
    expect((createdOff as { text: string }).text).toContain('已停用')
    await create.execute({ name: '甲', type: 'sms_followup', body: 'b', industry: '餐饮', enabled: false, variables: [{ name: 'a', description: 'd', example: 'e' }] }, EXEC)

    const update = contentTemplateUpdateTool(deps)
    const [updatedOn] = update.output.render({ content_template_id: 't1' }, { template: { id: 't1', name: '乙', type: 'sms_followup', enabled: true } })
    expect((updatedOn as { text: string }).text).toContain('启用中')
    const [updatedOff] = update.output.render({ content_template_id: 't1' }, { template: { id: 't1', name: '乙', type: 'sms_followup', enabled: false } })
    expect((updatedOff as { text: string }).text).toContain('已停用')

    const listTemplates = vi.fn(() => [
      { id: 't1', name: '甲', industry: undefined, type: 'sms_followup', body: 'b', enabled: true, variables: [] },
    ])
    const tListAll = contentTemplateListTool({ content: contentStubWith(listTemplates), permission: permissionOf(), policy: POLICY })
    await tListAll.execute({ type: 'sms_followup', enabled_only: true }, EXEC)
    const [bare] = tListAll.output.render({}, {
      items: [{ id: 't1', name: '甲', type: 'sms_followup', body: 'b', enabled: true, variables: [] }],
    })
    expect((bare as { text: string }).text).toContain('sms_followup')

    const deleteTemplate = vi.fn(async () => undefined)
    const remove = contentTemplateDeleteTool({ content: contentStubWith(deleteTemplate), permission: permissionOf(), policy: POLICY })
    await expect(remove.execute({ content_template_id: 't1' }, EXEC)).resolves.toEqual({ deleted: true })
  })

  it('SOP tools cover the remaining render and forward branches', async () => {
    const deps = { sop: sopOf(), permission: permissionOf() }

    const generate = sopGenerateTasksTool(deps)
    expect(renderText(generate, {
      intent_level: 'high',
      created: [
        { task_id: 'k1', title: '问候', planned_at: 0, todo_written: false },
        { task_id: 'k2', title: '确认', planned_at: 86_400_000, todo_written: true },
      ],
      todo_list: [{ content: '问候', status: 'pending' }],
      todo_write_enabled: true,
    })).toContain('todo_write')
    const value = await generate.execute({ lead_id: 'l1', sop_template_id: 's1' }, EXEC) as { created: unknown[] }
    expect(value.created).toHaveLength(2)

    const sList = sopTaskListTool(deps)
    expect(renderText(sList, { items: [{ id: 'k1', lead_id: 'l1', title: '问候', status: 'pending', planned_at: 0, note: '备注', created_at: 0 }], total: 1 })).toContain('问候')
    const listed = await sList.execute({ lead_id: 'l1', status: 'pending', limit: 5, offset: 5 }, EXEC) as { items: unknown[] }
    expect(listed.items).toHaveLength(1)

    const sCreate = sopTemplateCreateTool(deps)
    const [createdOn] = sCreate.output.render({}, { template: { id: 's1', name: 'SOP 甲', enabled: true } })
    expect((createdOn as { text: string }).text).toContain('启用中')
    const [createdOff] = sCreate.output.render({}, { template: { id: 's1', name: 'SOP 甲', enabled: false } })
    expect((createdOff as { text: string }).text).toContain('已停用')
    await sCreate.execute({
      name: 'SOP 甲', industry: '餐饮', enabled: false,
      rules: [{ intent_level: 'high', cadence: 'D+0', points: ['p'], questions: ['q'], risks: ['r'] }],
    }, EXEC)

    const sUpdate = sopTemplateUpdateTool(deps)
    const [updatedOn] = sUpdate.output.render({ sop_template_id: 's1' }, { template: { id: 's1', name: 'SOP 甲', enabled: true } })
    expect((updatedOn as { text: string }).text).toContain('已更新')
    const [updatedOff] = sUpdate.output.render({ sop_template_id: 's1' }, { template: { id: 's1', name: 'SOP 甲', enabled: false } })
    expect((updatedOff as { text: string }).text).toContain('已停用')
    await sUpdate.execute({ sop_template_id: 's1', name: '乙', enabled: true }, EXEC)

    const listTemplates = vi.fn(() => [
      { id: 's1', name: 'SOP 甲', industry: '餐饮', enabled: true,
        rules: [{ intent_level: 'high', cadence: 'D+0', points: ['p'], questions: ['q'], risks: ['r'] }] },
    ])
    const sListAll = sopTemplateListTool({ sop: sopStubWith(listTemplates), permission: permissionOf() })
    await sListAll.execute({ enabled_only: true }, EXEC)
    const [sopBlock] = sListAll.output.render({}, {
      items: [{ id: 's1', name: 'SOP 甲', industry: '餐饮', rules: [{ intent_level: 'high', cadence: 'D+0', points: ['p'], questions: ['q'], risks: ['r'] }], enabled: true }],
    })
    expect((sopBlock as { text: string }).text).toContain('餐饮')

    const deleteTemplate = vi.fn(async () => undefined)
    const sRemove = sopTemplateDeleteTool({ sop: sopStubWith(deleteTemplate), permission: permissionOf() })
    await expect(sRemove.execute({ sop_template_id: 's1' }, EXEC)).resolves.toEqual({ deleted: true })
  })
})

function contentStubWith(listTemplates: () => unknown): NurtureContentService {
  const base = contentOf()
  const proto = Object.getPrototypeOf(base) as object | null
  const stub: NurtureContentService = Object.assign(Object.create(proto) as NurtureContentService, base, { listTemplates })
  return stub
}

function sopStubWith(listTemplates: () => unknown): SopService {
  const base = sopOf()
  const proto = Object.getPrototypeOf(base) as object | null
  const stub: SopService = Object.assign(Object.create(proto) as SopService, base, { listTemplates })
  return stub
}
