import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import type { ToolDefinition } from '@deepseek-ai/dsh-tools'
import { completionReturning, mockClock, setupP1, FULL_OPERATOR, OWN_OPERATOR } from './helpers-p1.ts'
import type { P1Harness } from './helpers-p1.ts'
import { NurtureContentService } from '../src/content/service.ts'
import { SopService } from '../src/sop/service.ts'
import type { PermissionContextService } from '../src/permission/types.ts'
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
/** Execute one tool and project the result (the registry returns unknown). */
async function runTool<T>(tool: { execute(args: unknown, exec: never): Promise<unknown> }, args: unknown): Promise<T> {
  return await tool.execute(args, EXEC) as T
}

function permissionOf(): PermissionContextService {
  return { resolve: async () => FULL_OPERATOR } as never
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

function renderText(tool: ToolDefinition, value: unknown): string {
  const [block] = tool.output.render({}, value as never)
  return (block as { text: string }).text
}

describe('P3 content tools every-branch fill', () => {
  const policy = { provider: 'p', model: 'm', timeoutMs: 1000, maxOutputTokens: 256 }
  const contentDeps = { content: contentOf(), permission: permissionOf(), policy }

  it('generate forwards the optional template id and renders the answer', async () => {
    const tool = contentGenerateTool(contentDeps)
    const minimal = await runTool<{ content: { template_id?: string } }>(tool, { lead_id: 'l1', type: 'sms_followup', variant: 'A' })
    expect(renderText(tool, minimal)).toContain('短信正文')

    const generate = vi.fn(async () => ({
      content: { id: 'g2', lead_id: 'l1', type: 'sms_followup', variant: 'B', content: '带模板正文', template_id: 't9', created_at: 2 },
      leadName: '公司乙',
    }))
    const explicit = contentGenerateTool({ ...contentDeps, content: contentOf({ generate }) })
    const value = await runTool<{ content: { template_id?: string } }>(explicit, { lead_id: 'l1', type: 'sms_followup', variant: 'A', template_id: 't9' })
    expect(value.content.template_id).toBe('t9')
  })

  it('list-by-lead projects items with and without a template reference', async () => {
    const listed = contentOf({
      listByLead: () => ({
        items: [
          { id: 'g1', type: 'sms_followup', variant: 'A', content: '无模板', created_at: 1 },
          { id: 'g2', type: 'wecom_first_touch', variant: 'B', content: '有模板', template_id: 't1', created_at: 2 },
        ],
        total: 2,
      }),
    })
    const tool = contentListByLeadTool({ ...contentDeps, content: listed })
    const page = await runTool<{ items: Array<{ template_id?: string }> }>(tool, { lead_id: 'l1' })
    expect(page.items).toHaveLength(2)
    expect(page.items[0]).not.toHaveProperty('template_id')
    expect(page.items[1]!.template_id).toBe('t1')
    expect(renderText(tool, page)).toContain('有模板')
  })

  it('template create forwards optional fields on both minimal and rich calls', async () => {
    const create = vi.fn(async () => ({
      id: 't1', name: '模板甲', industry: '教育', type: 'sms_followup', body: 'b', variables: [{ name: 'v', description: 'd', example: 'e' }], enabled: false,
      created_at: 1, updated_at: 1,
    }))
    const tool = contentTemplateCreateTool({ ...contentDeps, content: contentOf({ createTemplate: create }) })
    await tool.execute({ name: '甲', type: 'sms_followup', body: 'b' }, EXEC)
    expect(create).toHaveBeenLastCalledWith({ name: '甲', type: 'sms_followup', body: 'b' }, FULL_OPERATOR, 'agent')
    await tool.execute({ name: '甲', type: 'sms_followup', industry: '教育', body: 'b', variables: [{ name: 'v', description: 'd', example: 'e' }], enabled: false }, EXEC)
    expect(create).toHaveBeenLastCalledWith(
      { name: '甲', type: 'sms_followup', industry: '教育', body: 'b', variables: [{ name: 'v', description: 'd', example: 'e' }], enabled: false },
      FULL_OPERATOR, 'agent',
    )
  })

  it('template update forwards only provided fields', async () => {
    const update = vi.fn(async () => ({
      id: 't1', name: '模板甲', industry: undefined, type: 'sms_followup', body: 'b', variables: [], enabled: true,
      created_at: 1, updated_at: 1,
    }))
    const tool = contentTemplateUpdateTool({ ...contentDeps, content: contentOf({ updateTemplate: update }) })
    await tool.execute({ content_template_id: 't1' }, EXEC)
    expect(update).toHaveBeenLastCalledWith('t1', {}, FULL_OPERATOR, 'agent')
    await tool.execute({ content_template_id: 't1', name: '乙', industry: '零售', type: 'sms', body: 'b2', variables: [{ name: 'v', description: 'd', example: 'e' }], enabled: false }, EXEC)
    expect(update).toHaveBeenLastCalledWith('t1', { name: '乙', industry: '零售', type: 'sms', body: 'b2', variables: [{ name: 'v', description: 'd', example: 'e' }], enabled: false }, FULL_OPERATOR, 'agent')
  })

  it('template list renders empty and populated pages and forwards filters', async () => {
    const list = vi.fn(() => [])
    const tool = contentTemplateListTool({ ...contentDeps, content: contentOf({ listTemplates: list }) })
    expect(renderText(tool, { items: [] })).toContain('尚无文案模板')
    const emptyPage = await runTool<{ items: unknown[]; total: number }>(tool, { type: 'sms_followup', enabled_only: true })
    expect(emptyPage.items).toEqual([])
    expect(list).toHaveBeenLastCalledWith({ type: 'sms_followup', enabledOnly: true })

    const populated = contentTemplateListTool({
      ...contentDeps,
      content: contentOf({
        listTemplates: () => [
          { id: 't1', name: '通用甲', industry: undefined, type: 'sms_followup', body: 'b', variables: [{ name: 'v', description: 'd' }], enabled: true, created_at: 1, updated_at: 1 },
          { id: 't2', name: '教育乙', industry: '教育', type: 'sms_followup', body: 'b', variables: [{ name: 'v', description: 'd', example: 'e' }], enabled: false, created_at: 2, updated_at: 2 },
        ],
      }),
    })
    const page = await runTool<{ items: Array<{ variables?: Array<{ example?: string }> }>; total: number }>(populated, {})
    expect(page.items).toHaveLength(2)
    expect(page.items[0]).not.toHaveProperty('industry')
    expect(page.items[0]!.variables?.[0]).not.toHaveProperty('example')
    expect(page.items[1]!.variables?.[0]?.example).toBe('e')
    const rendered = renderText(populated, {
      items: [
        { id: 't1', name: '通用甲', type: 'sms_followup', enabled: true },
        { id: 't2', name: '教育乙', industry: '教育', type: 'sms_followup', enabled: false },
      ],
    })
    expect(rendered).toContain('通用')
    expect(rendered).toContain('停用')
  })

  it('template delete resolves and renders through the stub', async () => {
    const tool = contentTemplateDeleteTool(contentDeps)
    await expect(tool.execute({ content_template_id: 't1' }, EXEC)).resolves.toBeDefined()
  })
})

describe('P3 sop tools every-branch fill', () => {
  const sopDeps = { sop: sopOf(), permission: permissionOf() }

  it('generate renders the todo block only when the todo list is present', async () => {
    const tool = sopGenerateTasksTool(sopDeps)
    const outcome = await tool.execute({ lead_id: 'l1' }, EXEC)
    const rendered = renderText(tool, outcome)
    expect(rendered).toContain('待办联动已开启')
    expect(rendered).toContain('[pending]')

    // todo_write_enabled with no list degrades to no todo block
    const listless = renderText(tool, {
      intent_level: 'high', created: [{ planned_at: 0, title: '问候', task_id: 'k1' }],
      todo_write_enabled: true, todo_list: undefined,
    })
    expect(listless).not.toContain('待办联动已开启')
    expect(listless).toContain('问候')
    expect(renderText(tool, {
      intent_level: 'high', created: [],
      todo_write_enabled: false,
    })).not.toContain('待办联动已开启')
  })

  it('task list forwards filters and projects noted and note-less tasks', async () => {
    const list = vi.fn(() => ({
      items: [
        { id: 'k1', lead_id: 'l1', title: '无备注', status: 'pending' as const, planned_at: 1, created_at: 1 },
        { id: 'k2', lead_id: 'l1', title: '有备注', status: 'done' as const, planned_at: 2, note: '已完成', created_at: 2 },
      ],
      total: 2,
    }))
    const tool = sopTaskListTool({ ...sopDeps, sop: sopOf({ listTasks: list }) })
    const empty = await tool.execute({}, EXEC) as { items: Array<Record<string, unknown>> }
    expect(list).toHaveBeenLastCalledWith({}, FULL_OPERATOR)
    expect(empty.items[0]).not.toHaveProperty('note')
    const full = await tool.execute({ lead_id: 'l1', status: 'done', limit: 5, offset: 1 }, EXEC) as { items: Array<Record<string, unknown>> }
    expect(list).toHaveBeenLastCalledWith({ lead_id: 'l1', status: 'done', limit: 5, offset: 1 }, FULL_OPERATOR)
    expect(full.items[1]!.note).toBe('已完成')
  })

  it('task update resolves through the stub and renders the transition', async () => {
    const tool = sopTaskUpdateTool(sopDeps)
    const value = await tool.execute({ task_id: 'k1', status: 'done', note: 'ok' }, EXEC) as { task: Record<string, unknown> }
    expect(value.task).toMatchObject({ id: 'k1', status: 'done' })
    expect(renderText(tool, value)).toContain('任务已流转')
  })

  it('template create forwards minimal and rich rules', async () => {
    const create = vi.fn(async () => ({
      id: 's1', name: 'SOP 甲', industry: undefined, enabled: true,
      rules: [{ intent_level: 'high' as const, cadence: 'D+0', points: ['p'], questions: [], risks: [] }],
      created_at: 1, updated_at: 1,
    }))
    const tool = sopTemplateCreateTool({ ...sopDeps, sop: sopOf({ createTemplate: create }) })
    await tool.execute({ name: '甲', rules: [{ intent_level: 'high', cadence: 'D+0', points: ['p'] }] }, EXEC)
    expect(create).toHaveBeenLastCalledWith(
      { name: '甲', rules: [{ intent_level: 'high', cadence: 'D+0', points: ['p'], questions: [], risks: [] }] },
      FULL_OPERATOR, 'agent',
    )
    await tool.execute({
      name: '甲', industry: '零售', enabled: false,
      rules: [
        { intent_level: 'high', cadence: 'D+0', points: ['p'], questions: ['q'], risks: ['r'] },
        { intent_level: 'low', cadence: 'D+3', points: [] },
      ],
    }, EXEC)
    expect(create).toHaveBeenLastCalledWith(
      {
        name: '甲', industry: '零售', enabled: false,
        rules: [
          { intent_level: 'high', cadence: 'D+0', points: ['p'], questions: ['q'], risks: ['r'] },
          { intent_level: 'low', cadence: 'D+3', points: [], questions: [], risks: [] },
        ],
      },
      FULL_OPERATOR, 'agent',
    )
  })

  it('template update forwards only provided fields and maps rich rules', async () => {
    const update = vi.fn(async () => ({
      id: 's1', name: 'SOP 甲', industry: undefined, enabled: true,
      rules: [{ intent_level: 'high' as const, cadence: 'D+0', points: ['p'], questions: [], risks: [] }],
      created_at: 1, updated_at: 1,
    }))
    const tool = sopTemplateUpdateTool({ ...sopDeps, sop: sopOf({ updateTemplate: update }) })
    await tool.execute({ sop_template_id: 's1' }, EXEC)
    expect(update).toHaveBeenLastCalledWith('s1', {}, FULL_OPERATOR, 'agent')
    await tool.execute({
      sop_template_id: 's1', name: '乙', industry: '零售', enabled: true,
      rules: [
        { intent_level: 'high', cadence: 'D+1', points: ['p1'], questions: ['q'], risks: ['r'] },
        { intent_level: 'mid', cadence: 'D+2', points: [] },
      ],
    }, EXEC)
    expect(update).toHaveBeenLastCalledWith('s1', {
      name: '乙', industry: '零售', enabled: true,
      rules: [
        { intent_level: 'high', cadence: 'D+1', points: ['p1'], questions: ['q'], risks: ['r'] },
        { intent_level: 'mid', cadence: 'D+2', points: [], questions: [], risks: [] },
      ],
    }, FULL_OPERATOR, 'agent')
  })

  it('template list renders empty and populated pages with and without industry', async () => {
    const tool = sopTemplateListTool(sopDeps)
    expect(renderText(tool, { items: [] })).toContain('尚无 SOP 模板')
    const rendered = renderText(tool, {
      items: [
        { id: 's1', name: '通用甲', enabled: true, rules: [{ intent_level: 'high' }, { intent_level: 'low' }] },
        { id: 's2', name: '零售乙', industry: '零售', enabled: false, rules: [{ intent_level: 'mid' }] },
      ],
    })
    expect(rendered).toContain('通用')
    expect(rendered).toContain('high/low')
    expect(rendered).toContain('停用')

    const list = vi.fn(() => [
      {
        id: 's1', name: '通用甲', industry: undefined, enabled: true,
        rules: [{ intent_level: 'high' as const, cadence: 'D+0', points: ['p'], questions: [], risks: [] }],
        created_at: 1, updated_at: 1,
      },
    ])
    const populated = sopTemplateListTool({ ...sopDeps, sop: sopOf({ listTemplates: list }) })
    const page = await populated.execute({ enabled_only: true }, EXEC) as { items: Array<Record<string, unknown>> }
    expect(list).toHaveBeenLastCalledWith(true)
    expect(page.items[0]).not.toHaveProperty('industry')
  })

  it('sop template delete resolves through the stub', async () => {
    const tool = sopTemplateDeleteTool(sopDeps)
    await expect(tool.execute({ sop_template_id: 's1' }, EXEC)).resolves.toEqual({ deleted: true })
  })
})

describe('P3 service edge fills over the composed stack', () => {
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

  function contentOf(answer: string): NurtureContentService {
    const { ctx } = p1.harness
    return new NurtureContentService({
      ctx,
      domain: p1.harness.service.requireDomain(),
      audit: p1.harness.service.requireAuditTable(),
      ledger: p1.ledger,
      policy: p1.policy,
      completionFactory: () => ({ complete: async () => answer }),
    })
  }

  function sopOf(): SopService {
    return new SopService({
      domain: p1.harness.service.requireDomain(),
      audit: p1.harness.service.requireAuditTable(),
      ledger: p1.ledger,
    })
  }

  it('template CRUD edges: industry field, empty-name patch, sorted lists, unreferenced delete, missing id', async () => {
    const content = contentOf('x')
    const withIndustry = await content.createTemplate(
      { name: '行业模板', type: 'sms_followup', industry: '教育', body: '正文' }, FULL_OPERATOR, 'agent')
    expect(withIndustry.industry).toBe('教育')

    await content.createTemplate({ name: '一', type: 'sms_followup', body: 'b' }, FULL_OPERATOR, 'agent')
    const second = await content.createTemplate({ name: '二', type: 'wecom_first_touch', body: 'b' }, FULL_OPERATOR, 'agent')
    expect(content.listTemplates().map(template => template.name)).toEqual(['行业模板', '一', '二'])

    await expect(content.updateTemplate(withIndustry.id, { name: ' ' }, FULL_OPERATOR, 'agent')).rejects.toThrow('模板名称不能为空')
    await expect(content.updateTemplate('ghost', { name: '甲' }, FULL_OPERATOR, 'agent')).rejects.toThrow('文案模板不存在')

    // a generated copy referencing ANOTHER template lets the unreferenced one go
    const referencer = await p1.ledger.createLead({ company_name: '引用公司' }, FULL_OPERATOR, 'agent')
    await p1.ledger.applyIntent(referencer.id, 'high')
    await content.generate(
      { lead_id: referencer.id, type: 'sms_followup', variant: 'A', template_id: withIndustry.id },
      FULL_OPERATOR, 'agent')
    await content.deleteTemplate(second.id, FULL_OPERATOR, 'agent')
    expect(content.listTemplates().map(template => template.id)).not.toContain(second.id)
    await expect(content.deleteTemplate(withIndustry.id, FULL_OPERATOR, 'agent')).rejects.toThrow('已被生成产物引用')
  })

  it('generate resolves the type chain for an industry-less lead through the industry-absent template', async () => {
    const lead = await p1.ledger.createLead({ company_name: '无行业公司' }, FULL_OPERATOR, 'agent')
    await p1.ledger.applyIntent(lead.id, 'high')
    const generic = await contentOf('无行业问候').createTemplate({ name: '通用首触', type: 'wecom_first_touch', body: '{{company_name}}您好' }, FULL_OPERATOR, 'agent')
    const outcome = await contentOf('无行业问候').generate({ lead_id: lead.id, type: 'wecom_first_touch', variant: 'A' }, FULL_OPERATOR, 'agent')
    expect(outcome.content.template_id).toBe(generic.id)
  })

  it('generate falls back to the first enabled template when industries all miss', async () => {
    const other = await p1.ledger.createLead({ company_name: '教育公司', industry: '教育' }, FULL_OPERATOR, 'agent')
    await p1.ledger.applyIntent(other.id, 'high')
    const finance = await contentOf('金融模板').createTemplate({ name: '金融专用', type: 'wecom_first_touch', industry: '金融', body: '金融正文' }, FULL_OPERATOR, 'agent')
    const crossed = await contentOf('金融模板').generate({ lead_id: other.id, type: 'wecom_first_touch', variant: 'A' }, FULL_OPERATOR, 'agent')
    expect(crossed.content.template_id).toBe(finance.id)
  })

  it('sop service edges: no-template generation, sorted templates, missing ids, and the manager gate', async () => {
    const sop = sopOf()
    const unscoredReady = await p1.ledger.createLead({ company_name: '无模板公司' }, FULL_OPERATOR, 'agent')
    await p1.ledger.applyIntent(unscoredReady.id, 'high')
    await expect(sop.generateTasks({ lead_id: unscoredReady.id }, FULL_OPERATOR, 'agent')).rejects.toThrow('没有启用中的 SOP 模板')

    await sop.createTemplate({ name: '甲', rules: [{ intent_level: 'high', cadence: 'D+0', points: ['p'], questions: [], risks: [] }] }, FULL_OPERATOR, 'agent')
    await sop.createTemplate({ name: '乙', rules: [{ intent_level: 'high', cadence: 'D+1', points: ['p'], questions: [], risks: [] }] }, FULL_OPERATOR, 'agent')
    expect(sop.listTemplates().map(template => template.name)).toEqual(['甲', '乙'])

    await expect(sop.updateTask('ghost', { status: 'done' }, FULL_OPERATOR, 'agent')).rejects.toThrow('SOP 任务不存在')
    await expect(sop.updateTemplate('ghost', {}, FULL_OPERATOR, 'agent')).rejects.toThrow('SOP 模板不存在')

    const managed = await sop.createTemplate({ name: '丙', rules: [{ intent_level: 'low', cadence: 'D+2', points: ['p'], questions: [], risks: [] }] }, FULL_OPERATOR, 'agent')
    await expect(sop.updateTemplate(managed.id, { name: '丁' }, OWN_OPERATOR, 'agent')).rejects.toThrow('can_manage_global_templates')
  })
})
