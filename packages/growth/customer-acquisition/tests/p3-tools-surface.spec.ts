import { describe, expect, it, vi } from 'vitest'
import type { NurtureContentService } from '../src/content/service.ts'
import type { SopService } from '../src/sop/service.ts'
import type { PermissionContextService, ResolvedOperator } from '../src/permission/types.ts'
import type { PromptCompletion } from '../src/llm/oneshot.ts'
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

const EXEC = { callId: 'c', rootCallId: 'c', name: 'probe', arguments: {}, signal: new AbortController().signal, agent: { id: 'a1' } } as unknown as ToolRunContext
const COMPLETION: PromptCompletion = { complete: async () => 'x' }

function permissionOf(operator: ResolvedOperator = FULL_OPERATOR): PermissionContextService {
  return { resolve: async () => operator } as never
}

function contentOf(overrides: Record<string, unknown> = {}): NurtureContentService {
  return {
    generate: async () => ({
      content: { id: 'g1', lead_id: 'l1', type: 'sms_followup', variant: 'A', content: '短信正文', template_id: 't1', created_at: 1 },
      leadName: '公司甲',
    }),
    listByLead: () => ({ items: [], total: 0 }),
    createTemplate: async () => ({
      id: 't1', name: '模板甲', industry: undefined, type: 'sms_followup', body: 'b', variables: [], enabled: true,
      created_at: 1, updated_at: 1,
    }),
    updateTemplate: async () => ({
      id: 't1', name: '模板甲', industry: undefined, type: 'sms_followup', body: 'b', variables: [], enabled: true,
      created_at: 1, updated_at: 1,
    }),
    listTemplates: () => [],
    deleteTemplate: async () => undefined,
    ...overrides,
  } as never
}

function sopOf(overrides: Record<string, unknown> = {}): SopService {
  return {
    generateTasks: async () => ({
      intentLevel: 'high' as const,
      templateId: 's1',
      tasks: [{ task: { id: 'k1', lead_id: 'l1', title: '问候', status: 'pending' as const, planned_at: 0, created_at: 1, updated_at: 1 }, todoWritten: false }],
      leadName: '公司甲',
      todoList: [{ content: '问候（公司甲）', status: 'pending' as const }],
      todoWriteEnabled: true,
    }),
    listTasks: () => ({ items: [], total: 0 }),
    updateTask: async () => ({ id: 'k1', lead_id: 'l1', title: '问候', status: 'done' as const, planned_at: 5, created_at: 1, updated_at: 2 }),
    createTemplate: async () => ({
      id: 's1', name: 'SOP 甲', industry: undefined, enabled: true,
      rules: [{ intent_level: 'high' as const, cadence: 'D+0', points: ['p'], questions: [], risks: [] }],
      created_at: 1, updated_at: 1,
    }),
    updateTemplate: async () => ({
      id: 's1', name: 'SOP 甲', industry: undefined, enabled: true,
      rules: [{ intent_level: 'high' as const, cadence: 'D+0', points: ['p'], questions: [], risks: [] }],
      created_at: 1, updated_at: 1,
    }),
    listTemplates: () => [],
    deleteTemplate: async () => undefined,
    ...overrides,
  } as never
}

function buildAll(): ToolDefinition[] {
  const contentDeps = { content: contentOf(), permission: permissionOf(), policy: { provider: 'p', model: 'm', timeoutMs: 1000, maxOutputTokens: 256 } }
  const sopDeps = { sop: sopOf(), permission: permissionOf() }
  return [
    contentGenerateTool(contentDeps),
    contentListByLeadTool(contentDeps),
    contentTemplateCreateTool(contentDeps),
    contentTemplateUpdateTool(contentDeps),
    contentTemplateListTool(contentDeps),
    contentTemplateDeleteTool(contentDeps),
    sopGenerateTasksTool(sopDeps),
    sopTaskListTool(sopDeps),
    sopTaskUpdateTool(sopDeps),
    sopTemplateCreateTool(sopDeps),
    sopTemplateUpdateTool(sopDeps),
    sopTemplateListTool(sopDeps),
    sopTemplateDeleteTool(sopDeps),
  ]
}

function toolOf(name: string): ToolDefinition {
  const tool = buildAll().find(candidate => candidate.name === name)
  if (tool === undefined) throw new Error(`tool not found: ${name}`)
  return tool
}

function renderText(tool: ToolDefinition, value: unknown): string {
  const [block] = tool.output.render({}, value as never)
  return (block as { text: string }).text
}

describe('P3 tool registry', () => {
  it('registers 13 tools and every call card is generic with a Chinese title', () => {
    const tools = buildAll()
    expect(tools).toHaveLength(13)
    for (const tool of tools) {
      const view = tool.presentCall?.(sampleArgs(tool.name))
      expect(view?.card, tool.name).toBe('generic')
      expect((view as { title?: string }).title, tool.name).toBeTruthy()
    }
  })

  it('the lead-list call card falls back through keyword, status, and empty raw input', () => {
    const sopList = toolOf('customer_acquisition_sop_task_list')
    expect(sopList.presentCall?.({ lead_id: 'l1' })).toMatchObject({ rawInput: 'l1' })
    expect(sopList.presentCall?.({ status: 'pending' })).toMatchObject({ rawInput: 'status=pending' })
    expect(sopList.presentCall?.({})).toMatchObject({ rawInput: '' })
  })
})

describe('P3 content tool renders and executes', () => {
  it('renders the generate envelope with and without a template id', () => {
    const tool = toolOf('customer_acquisition_content_generate')
    expect(renderText(tool, { content: { id: 'g1', type: 'sms_followup', variant: 'A', content: '短信正文', template_id: 't1' } })).toContain('短信正文')
    expect(renderText(tool, { content: { id: 'g2', type: 'email_drip', variant: 'B', content: '自由文案' } })).toContain('自由文案')
  })

  it('renders the history empty page and the populated page', () => {
    const list = toolOf('customer_acquisition_content_list_by_lead')
    expect(renderText(list, { items: [], total: 0 })).toContain('当前页无记录')
    expect(renderText(list, { items: [{ id: 'g1', type: 'sms_followup', variant: 'A', content: '正文', template_id: 't1', created_at: 0 }], total: 1 })).toContain('sms_followup')
  })

  it('executes generate and forwards the lead/type/variant', async () => {
    const generate = vi.fn(async () => ({
      content: { id: 'g1', lead_id: 'l1', type: 'sms_followup', variant: 'A' as const, content: '正文', created_at: 1 },
      leadName: '公司甲',
    }))
    const tool = contentGenerateTool({ content: contentOf({ generate }), permission: permissionOf(), policy: { provider: 'p', model: 'm', timeoutMs: 1000, maxOutputTokens: 256 } })
    const value = await tool.execute({ lead_id: 'l1', type: 'sms_followup', variant: 'A' }, EXEC) as { content: { id: string } }
    expect(value.content.id).toBe('g1')
    expect(generate).toHaveBeenCalledWith({ lead_id: 'l1', type: 'sms_followup', variant: 'A' }, FULL_OPERATOR, 'agent', EXEC.signal)
    expect(tool.timeoutMs).toBe(120_000)
  })
})

describe('P3 SOP tool renders and executes', () => {
  it('renders the generate output including the todo-forwarding block', () => {
    const generate = toolOf('customer_acquisition_sop_generate_tasks')
    const withTodo = renderText(generate, {
      intent_level: 'high',
      created: [
        { task_id: 'k1', title: '微信问候', planned_at: 0, todo_written: false },
        { task_id: 'k2', title: '电话确认', planned_at: 86_400_000, todo_written: true },
      ],
      todo_list: [{ content: '问候（幸福奶茶店）', status: 'pending' }],
      todo_write_enabled: true,
    })
    expect(withTodo).toContain('high')
    expect(withTodo).toContain('todo_write')
    expect(withTodo).toContain('问候（幸福奶茶店）')
    const disabled = renderText(generate, { intent_level: 'low', created: [], todo_list: [], todo_write_enabled: false })
    expect(disabled).toContain('0 条跟进任务')
    expect(disabled).not.toContain('todo_write')
  })

  it('renders the SOP task list, flow, and the template CRUD envelopes', () => {
    const list = toolOf('customer_acquisition_sop_task_list')
    expect(renderText(list, { items: [], total: 0 })).toContain('当前页无记录')
    expect(renderText(list, { items: [{ id: 'k1', lead_id: 'l1', title: '问候', status: 'pending', planned_at: 0, created_at: 0 }], total: 1 })).toContain('pending')

    const taskUpdate = toolOf('customer_acquisition_sop_task_update')
    expect(renderText(taskUpdate, { task: { id: 'k1', status: 'done', planned_at: 0 } })).toContain('done')

    const create = toolOf('customer_acquisition_sop_template_create')
    expect(renderText(create, { template: { id: 's1', name: 'SOP 甲', enabled: true } })).toContain('启用中')
    expect(renderText(create, { template: { id: 's1', name: 'SOP 甲', enabled: false } })).toContain('已停用')
    const templateUpdate = toolOf('customer_acquisition_sop_template_update')
    expect(renderText(templateUpdate, { template: { id: 's1', name: 'SOP 甲', enabled: true } })).toContain('已更新')
    const listT = toolOf('customer_acquisition_sop_template_list')
    expect(renderText(listT, { items: [] })).toContain('尚无 SOP 模板')
    expect(renderText(listT, { items: [{ id: 's1', name: 'SOP 甲', industry: undefined, rules: [{ intent_level: 'high', cadence: 'D+0', points: ['p'], questions: [], risks: [] }], enabled: true }] })).toContain('high')
    const remove = toolOf('customer_acquisition_sop_template_delete')
    expect(renderText(remove, { deleted: true })).toContain('已删除')
    expect(renderText(remove, { deleted: false })).toContain('未删除')
  })

  it('executes the SOP task flow and forwards status and note', async () => {
    const updateTask = vi.fn(async () => ({
      id: 'k1', lead_id: 'l1', title: '问候', status: 'done' as const, planned_at: 5, created_at: 1, updated_at: 2,
    }))
    const tool = sopTaskUpdateTool({ sop: sopOf({ updateTask }), permission: permissionOf() })
    const value = await tool.execute({ task_id: 'k1', status: 'done', note: '完成' }, EXEC) as { task: { status: string } }
    expect(value.task.status).toBe('done')
    expect(updateTask).toHaveBeenCalledWith('k1', { status: 'done', note: '完成' }, FULL_OPERATOR, 'agent')
  })
})

export { COMPLETION, permissionOf, contentOf, sopOf, vi }
import type { ToolDefinition as ToolDefinitionType, ToolRunContext } from '@deepseek-ai/dsh-tools'
type ToolDefinition = ToolDefinitionType
/** Minimal args each presentCall accepts; absent optionals stay undefined. */
function sampleArgs(name: string): Record<string, unknown> {
  if (name.endsWith('content_generate')) return { lead_id: 'l1', type: 'sms_followup', variant: 'A' }
  if (name.endsWith('content_list_by_lead')) return { lead_id: 'l1' }
  if (name.endsWith('content_template_create')) return { name: 't', type: 'sms_followup', body: 'b' }
  if (name.endsWith('content_template_update')) return { content_template_id: 't1' }
  if (name.endsWith('content_template_delete')) return { content_template_id: 't1' }
  if (name.endsWith('sop_generate_tasks')) return { lead_id: 'l1' }
  if (name.endsWith('sop_task_list')) return { lead_id: 'l1' }
  if (name.endsWith('sop_task_update')) return { task_id: 'k1' }
  if (name.endsWith('sop_template_create')) return { name: 'sop', rules: [] }
  if (name.endsWith('sop_template_update')) return { sop_template_id: 's1' }
  if (name.endsWith('sop_template_delete')) return { sop_template_id: 's1' }
  return {}
}
