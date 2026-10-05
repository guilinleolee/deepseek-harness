/**
 * Module-5 model-facing tools (tools manifest §8): SOP task generation with
 * todo-forwarding guidance, task listing and state flow, and the SOP template
 * CRUD. The DSH todo list is the agent's own `todo_write` checklist — when
 * the settings flag is on, the generate output carries a ready-to-forward
 * list and the render says so.
 * @module @deepseek-ai/dsh-customer-acquisition/tools/sop
 */

import { defineTool } from '@deepseek-ai/dsh-tools'
import type { ToolDefinition } from '@deepseek-ai/dsh-tools'
import type { SopService } from '../sop/service.ts'
import { operatorRequest } from '../permission/types.ts'
import type { PermissionContextService } from '../permission/types.ts'

/** Dependencies every SOP tool shares. */
export interface SopToolDeps {
  readonly sop: SopService
  readonly permission: PermissionContextService
}

/** The SOP rule parameter block shared by template create and update. */
const SOP_RULE_PARAMETER_ITEM = {
  type: 'object',
  additionalProperties: false,
  properties: {
    intent_level: { type: 'string', required: true, enum: ['high', 'mid', 'low', 'invalid'], description: '该规则适用的意向等级；模板内不可重复' },
    cadence: { type: 'string', required: true, description: '跟进节奏，如「D+0 微信问候，D+3 到店」；D+N 会被解析为任务排期' },
    points: { type: 'array', required: true, items: { type: 'string' }, description: '跟进要点；每个要点生成一条任务' },
    questions: { type: 'array', items: { type: 'string' }, description: '沟通提问清单' },
    risks: { type: 'array', items: { type: 'string' }, description: '风险提示' },
  },
} as const

/**
 * Build `customer_acquisition_sop_generate_tasks`.
 * @param deps - SOP service and permission seam.
 * @returns the tool definition.
 */
export function sopGenerateTasksTool(deps: SopToolDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_sop_generate_tasks',
    description: '按线索的意向等级与 SOP 模板生成跟进任务清单：每条任务含标题（跟进要点）、计划时间（按模板节奏 D+N 排期）与备注（提问清单、风险提示）。线索未打分（无意向等级）时拒绝并提示先打分。全局设置开启待办联动时，输出附带可直接经 todo_write 写入的待办清单。',
    parameters: {
      lead_id: { type: 'string', required: true, description: '线索 id' },
      sop_template_id: { type: 'string', description: 'SOP 模板 id；省略时按行业匹配启用的模板' },
    },
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: {
          intent_level: { type: 'string', required: true },
          created: {
            type: 'array',
            required: true,
            items: {
              type: 'object',
              additionalProperties: false,
              properties: {
                task_id: { type: 'string', required: true },
                title: { type: 'string', required: true },
                planned_at: { type: 'integer', required: true },
                todo_written: { type: 'boolean', required: true },
              },
            },
          },
          todo_list: {
            type: 'array',
            items: {
              type: 'object',
              additionalProperties: false,
              properties: {
                content: { type: 'string', required: true },
                status: { type: 'string', required: true },
              },
            },
          },
          todo_write_enabled: { type: 'boolean', required: true },
        },
      },
      render: (_args, value) => {
        const lines = [
          `已按「${value.intent_level}」意向生成 ${value.created.length} 条跟进任务：`,
          ...value.created.map(task => `- ${new Date(task.planned_at).toISOString().slice(0, 10)} ${task.title}（id ${task.task_id}）`),
        ]
        const todoLines = value.todo_write_enabled
          ? (value.todo_list ?? []).map(entry => `  · [${entry.status}] ${entry.content}`)
          : []
        if (todoLines.length > 0) {
          lines.push(
            '待办联动已开启——DSH 待办清单由 agent 经 todo_write 维护，可将以下清单直接写入：',
            ...todoLines,
          )
        }
        return [{ type: 'text', text: lines.join('\n') }]
      },
    },
    presentCall: args => ({
      card: 'generic',
      title: '生成跟进任务',
      rawInput: args.lead_id,
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      const outcome = await deps.sop.generateTasks(
        { lead_id: args.lead_id, ...(args.sop_template_id === undefined ? {} : { sop_template_id: args.sop_template_id }) },
        operator,
        'agent',
      )
      return {
        intent_level: outcome.intentLevel,
        created: outcome.tasks.map(({ task, todoWritten }) => ({
          task_id: task.id,
          title: task.title,
          planned_at: task.planned_at,
          todo_written: todoWritten,
        })),
        todo_list: outcome.todoList,
        todo_write_enabled: outcome.todoWriteEnabled,
      }
    },
  })
}

/**
 * Build `customer_acquisition_sop_task_list`.
 * @param deps - SOP service and permission seam.
 * @returns the tool definition.
 */
export function sopTaskListTool(deps: SopToolDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_sop_task_list',
    description: '查看 SOP 跟进任务：按线索、状态过滤，按计划时间升序分页返回。',
    parameters: {
      lead_id: { type: 'string', description: '按线索过滤' },
      status: { type: 'string', enum: ['pending', 'done', 'deferred', 'dropped'], description: '按状态过滤' },
      limit: { type: 'integer', description: '每页条数，默认 20，最大 100；越界值自动收敛' },
      offset: { type: 'integer', description: '偏移量，默认 0；负值按 0 处理' },
    },
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: {
          items: {
            type: 'array',
            required: true,
            items: {
              type: 'object',
              additionalProperties: false,
              properties: {
                id: { type: 'string', required: true },
                lead_id: { type: 'string', required: true },
                title: { type: 'string', required: true },
                status: { type: 'string', required: true },
                planned_at: { type: 'integer', required: true },
                note: { type: 'string' },
                created_at: { type: 'integer', required: true },
              },
            },
          },
          total: { type: 'integer', required: true },
        },
      },
      render: (_args, value) => [{
        type: 'text',
        text: value.items.length === 0
          ? `SOP 任务共 ${value.total} 条，当前页无记录。`
          : `SOP 任务共 ${value.total} 条，本页 ${value.items.length} 条：\n${value.items
            .map(task => `- ${new Date(task.planned_at).toISOString().slice(0, 10)} [${task.status}] ${task.title}（线索 ${task.lead_id}，id ${task.id}）`)
            .join('\n')}`,
      }],
    },
    presentCall: args => ({
      card: 'generic',
      title: '查看 SOP 任务',
      rawInput: args.lead_id ?? (args.status === undefined ? '' : `status=${args.status}`),
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      const { lead_id: leadId, status, limit, offset } = args
      const { items, total } = deps.sop.listTasks({
        ...(leadId === undefined ? {} : { lead_id: leadId }),
        ...(status === undefined ? {} : { status }),
        ...(limit === undefined ? {} : { limit }),
        ...(offset === undefined ? {} : { offset }),
      }, operator)
      return {
        items: items.map(task => ({
          id: task.id,
          lead_id: task.lead_id,
          title: task.title,
          status: task.status,
          planned_at: task.planned_at,
          ...(task.note === undefined ? {} : { note: task.note }),
          created_at: task.created_at,
        })),
        total,
      }
    },
  })
}

/**
 * Build `customer_acquisition_sop_task_update`.
 * @param deps - SOP service and permission seam.
 * @returns the tool definition.
 */
export function sopTaskUpdateTool(deps: SopToolDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_sop_task_update',
    description: '流转 SOP 任务状态（pending/done/deferred/dropped），可调整计划时间与备注。',
    parameters: {
      task_id: { type: 'string', required: true, description: '任务 id' },
      status: { type: 'string', enum: ['pending', 'done', 'deferred', 'dropped'], description: '目标状态' },
      planned_at: { type: 'integer', description: '调整后的计划时间（epoch 毫秒）' },
      note: { type: 'string', description: '备注（整体替换）' },
    },
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: {
          task: {
            type: 'object',
            required: true,
            additionalProperties: false,
            properties: {
              id: { type: 'string', required: true },
              status: { type: 'string', required: true },
              planned_at: { type: 'integer', required: true },
            },
          },
        },
      },
      render: (_args, value) => [{
        type: 'text',
        text: `任务已流转：id ${value.task.id} → ${value.task.status}（计划 ${new Date(value.task.planned_at).toISOString().slice(0, 10)}）`,
      }],
    },
    presentCall: args => ({
      card: 'generic',
      title: '流转 SOP 任务',
      rawInput: `${args.task_id} → ${args.status ?? '（不变）'}`,
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      const { task_id: taskId, status, planned_at: plannedAt, note } = args
      const task = await deps.sop.updateTask(taskId, {
        ...(status === undefined ? {} : { status }),
        ...(plannedAt === undefined ? {} : { planned_at: plannedAt }),
        ...(note === undefined ? {} : { note }),
      }, operator, 'agent')
      return { task: { id: task.id, status: task.status, planned_at: task.planned_at } }
    },
  })
}

/**
 * Build `customer_acquisition_sop_template_create`.
 * @param deps - SOP service and permission seam.
 * @returns the tool definition.
 */
export function sopTemplateCreateTool(deps: SopToolDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_sop_template_create',
    description: '新建 SOP 跟进模板：按意向等级（high/mid/low/invalid）各给一条规则，含跟进节奏（D+N 会被解析为任务排期）、跟进要点、沟通提问清单与风险提示；等级在模板内不可重复。',
    parameters: {
      name: { type: 'string', required: true, description: '模板名称' },
      industry: { type: 'string', description: '适用行业；省略 = 通用' },
      rules: { type: 'array', required: true, items: SOP_RULE_PARAMETER_ITEM, description: '规则列表，1-N 条' },
      enabled: { type: 'boolean', description: '默认 true' },
    },
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: {
          template: {
            type: 'object',
            required: true,
            additionalProperties: false,
            properties: {
              id: { type: 'string', required: true },
              name: { type: 'string', required: true },
              enabled: { type: 'boolean', required: true },
            },
          },
        },
      },
      render: (_args, value) => [{
        type: 'text',
        text: `已新建 SOP 模板：${value.template.name}（id ${value.template.id}，${value.template.enabled ? '启用中' : '已停用'}）`,
      }],
    },
    presentCall: args => ({
      card: 'generic',
      title: '新建 SOP 模板',
      rawInput: args.name,
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      const { name, industry, rules, enabled } = args
      const template = await deps.sop.createTemplate({
        name,
        ...(industry === undefined ? {} : { industry }),
        rules: rules.map(rule => ({
          intent_level: rule.intent_level,
          cadence: rule.cadence,
          points: [...rule.points],
          questions: [...(rule.questions ?? [])],
          risks: [...(rule.risks ?? [])],
        })),
        ...(enabled === undefined ? {} : { enabled }),
      }, operator, 'agent')
      return { template: { id: template.id, name: template.name, enabled: template.enabled } }
    },
  })
}

/**
 * Build `customer_acquisition_sop_template_update`.
 * @param deps - SOP service and permission seam.
 * @returns the tool definition.
 */
export function sopTemplateUpdateTool(deps: SopToolDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_sop_template_update',
    description: '修改 SOP 模板：名称、行业、启用状态，或整体替换规则列表（每等级一条，D+N 节奏重新生效于后续生成）。',
    parameters: {
      sop_template_id: { type: 'string', required: true, description: '模板 id' },
      name: { type: 'string', description: '新名称' },
      industry: { type: 'string', description: '新行业' },
      rules: { type: 'array', items: SOP_RULE_PARAMETER_ITEM, description: '整体替换规则列表' },
      enabled: { type: 'boolean', description: '启用状态' },
    },
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: {
          template: {
            type: 'object',
            required: true,
            additionalProperties: false,
            properties: {
              id: { type: 'string', required: true },
              name: { type: 'string', required: true },
              enabled: { type: 'boolean', required: true },
            },
          },
        },
      },
      render: (_args, value) => [{
        type: 'text',
        text: `已更新 SOP 模板：${value.template.name}（id ${value.template.id}，${value.template.enabled ? '启用中' : '已停用'}）`,
      }],
    },
    presentCall: args => ({
      card: 'generic',
      title: '修改 SOP 模板',
      rawInput: args.sop_template_id,
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      const { sop_template_id: templateId, name, industry, rules, enabled } = args
      const template = await deps.sop.updateTemplate(templateId, {
        ...(name === undefined ? {} : { name }),
        ...(industry === undefined ? {} : { industry }),
        ...(rules === undefined ? {} : { rules: rules.map(rule => ({
          intent_level: rule.intent_level,
          cadence: rule.cadence,
          points: [...rule.points],
          questions: [...(rule.questions ?? [])],
          risks: [...(rule.risks ?? [])],
        })) }),
        ...(enabled === undefined ? {} : { enabled }),
      }, operator, 'agent')
      return { template: { id: template.id, name: template.name, enabled: template.enabled } }
    },
  })
}

/**
 * Build `customer_acquisition_sop_template_list`.
 * @param deps - SOP service and permission seam.
 * @returns the tool definition.
 */
export function sopTemplateListTool(deps: SopToolDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_sop_template_list',
    description: '列出 SOP 跟进模板（含规则全文与启用状态）。',
    parameters: {
      enabled_only: { type: 'boolean', description: '默认 false' },
    },
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: {
          items: {
            type: 'array',
            required: true,
            items: {
              type: 'object',
              additionalProperties: false,
              properties: {
                id: { type: 'string', required: true },
                name: { type: 'string', required: true },
                industry: { type: 'string' },
                rules: {
                  type: 'array',
                  required: true,
                  items: {
                    type: 'object',
                    additionalProperties: false,
                    properties: {
                      intent_level: { type: 'string', required: true },
                      cadence: { type: 'string', required: true },
                      points: { type: 'array', required: true, items: { type: 'string' } },
                      questions: { type: 'array', items: { type: 'string' } },
                      risks: { type: 'array', items: { type: 'string' } },
                    },
                  },
                },
                enabled: { type: 'boolean', required: true },
              },
            },
          },
        },
      },
      render: (_args, value) => [{
        type: 'text',
        text: value.items.length === 0
          ? '尚无 SOP 模板。'
          : `SOP 模板 ${value.items.length} 套：\n${value.items
            .map((template) => {
              const levels = template.rules.map(rule => rule.intent_level).join('/')
              return `- ${template.name}（id ${template.id}，${template.industry ?? '通用'}，${template.enabled ? '启用' : '停用'}）：等级 ${levels}`
            })
            .join('\n')}`,
      }],
    },
    presentCall: () => ({
      card: 'generic',
      title: '查看 SOP 模板',
    }),
    async execute(args, exec) {
      await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      return {
        items: deps.sop.listTemplates(args.enabled_only === true).map(template => ({
          id: template.id,
          name: template.name,
          ...(template.industry === undefined ? {} : { industry: template.industry }),
          rules: template.rules.map(rule => ({ ...rule })),
          enabled: template.enabled,
        })),
      }
    },
  })
}

/**
 * Build `customer_acquisition_sop_template_delete`.
 * @param deps - SOP service and permission seam.
 * @returns the tool definition.
 */
export function sopTemplateDeleteTool(deps: SopToolDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_sop_template_delete',
    description: '删除一套 SOP 模板。已生成的跟进任务不受影响（任务独立存储）；删除后不可恢复。',
    parameters: {
      sop_template_id: { type: 'string', required: true, description: '模板 id' },
    },
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: { deleted: { type: 'boolean', required: true } },
      },
      render: (_args, value) => [{
        type: 'text',
        text: value.deleted ? 'SOP 模板已删除。' : '未删除。',
      }],
    },
    presentCall: args => ({
      card: 'generic',
      title: '删除 SOP 模板',
      rawInput: args.sop_template_id,
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      await deps.sop.deleteTemplate(args.sop_template_id, operator, 'agent')
      return { deleted: true }
    },
  })
}
