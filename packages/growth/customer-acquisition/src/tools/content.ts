/**
 * Module-4 model-facing tools (tools manifest §7): nurture-copy generation
 * with A/B variants, per-lead artifact listing, and the content-template
 * CRUD. Red line 3: everything is text output — no send channel exists.
 * @module @deepseek-ai/dsh-customer-acquisition/tools/content
 */

import { defineTool } from '@deepseek-ai/dsh-tools'
import type { ToolDefinition } from '@deepseek-ai/dsh-tools'
import type { NurtureContentService } from '../content/service.ts'
import { CONTENT_SYSTEM_PROMPT } from '../content/service.ts'
import { llmPromptCompletion } from '../llm/oneshot.ts'
import type { ResolvedAiPolicy } from '../llm/oneshot.ts'
import { operatorRequest } from '../permission/types.ts'
import type { PermissionContextService } from '../permission/types.ts'

/** Dependencies every content tool shares. */
export interface ContentToolDeps {
  readonly content: NurtureContentService
  readonly permission: PermissionContextService
  readonly policy: ResolvedAiPolicy
}

/** The content-template parameter block shared by create and update. */
const TEMPLATE_FIELD_PARAMETERS = {
  name: { type: 'string', description: '模板名称' },
  industry: { type: 'string', description: '适用行业；省略 = 通用' },
  type: { type: 'string', description: '渠道类型（open 词表，已知值见 generate 描述）' },
  body: { type: 'string', description: '模板正文，支持 {{变量}} 占位' },
  variables: {
    type: 'array',
    items: {
      type: 'object',
      additionalProperties: false,
      properties: {
        name: { type: 'string', required: true },
        description: { type: 'string', required: true },
        example: { type: 'string' },
      },
    },
    description: '变量说明列表；更新时整体替换',
  },
  enabled: { type: 'boolean', description: '默认 true' },
} as const

/**
 * Build `customer_acquisition_content_generate`.
 * @param deps - content service, permission seam, and the AI policy.
 * @returns the tool definition.
 */
export function contentGenerateTool(deps: ContentToolDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_content_generate',
    description: '为一条线索按模板个性化生成培育文案。type 已知值：wecom_first_touch（企微初次触达）/ sms_followup（跟进短信）/ email_drip（多阶段邮件培育序列，一次生成完整多轮，正文按「## 第 N 轮」分节）/ short_video_script（短视频脚本）/ xiaohongshu_post（小红书图文）/ website_product_intro（官网产品介绍）/ customer_case（客户案例）。variant 为 A/B 版本标记，一次调用生成一个版本；线索资料自动注入上下文。产物仅是文本，本插件不提供任何发送能力。',
    parameters: {
      lead_id: { type: 'string', required: true, description: '线索 id' },
      type: { type: 'string', required: true, description: '文案类型（见描述已知值，也可用自定义类型）' },
      variant: { type: 'string', required: true, enum: ['A', 'B'], description: 'A/B 版本标记' },
      template_id: { type: 'string', description: '文案模板 id；省略时按行业匹配启用的模板，无匹配则自由撰写' },
    },
    timeoutMs: 120_000,
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: {
          content: {
            type: 'object',
            required: true,
            additionalProperties: false,
            properties: {
              id: { type: 'string', required: true },
              type: { type: 'string', required: true },
              variant: { type: 'string', required: true },
              content: { type: 'string', required: true },
              template_id: { type: 'string' },
            },
          },
        },
      },
      render: (_args, value) => [{
        type: 'text',
        text: `已生成（${value.content.type}，版本 ${value.content.variant}）：\n\n${value.content.content}`,
      }],
    },
    presentCall: args => ({
      card: 'generic',
      title: '生成培育文案',
      rawInput: `${args.lead_id}（${args.type}，${args.variant}）`,
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      const { lead_id: leadId, type, variant, template_id: templateId } = args
      const outcome = await deps.content.generate({
        lead_id: leadId,
        type,
        variant,
        ...(templateId === undefined ? {} : { template_id: templateId }),
      }, operator, 'agent', exec.signal)
      return {
        content: {
          id: outcome.content.id,
          type: outcome.content.type,
          variant: outcome.content.variant,
          content: outcome.content.content,
          ...(outcome.content.template_id === undefined ? {} : { template_id: outcome.content.template_id }),
        },
      }
    },
  })
}

/**
 * Build `customer_acquisition_content_list_by_lead`.
 * @param deps - content service and permission seam.
 * @returns the tool definition.
 */
export function contentListByLeadTool(deps: ContentToolDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_content_list_by_lead',
    description: '查看一个线索名下的全部历史生成产物，可按类型过滤，按生成时间倒序分页。',
    parameters: {
      lead_id: { type: 'string', required: true, description: '线索 id' },
      type: { type: 'string', description: '按类型过滤（open 词表）' },
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
                type: { type: 'string', required: true },
                variant: { type: 'string', required: true },
                content: { type: 'string', required: true },
                template_id: { type: 'string' },
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
          ? `历史产物共 ${value.total} 条，当前页无记录。`
          : `历史产物共 ${value.total} 条，本页 ${value.items.length} 条：\n${value.items
            .map(item => `- [${new Date(item.created_at).toISOString()}] ${item.type}（${item.variant}）：${item.content.slice(0, 80)}${item.content.length > 80 ? '…' : ''}`)
            .join('\n')}`,
      }],
    },
    presentCall: args => ({
      card: 'generic',
      title: '查看历史文案',
      rawInput: args.lead_id,
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      const { lead_id: leadId, type, limit, offset } = args
      const { items, total } = deps.content.listByLead(leadId, operator, type, limit, offset)
      return {
        items: items.map(item => ({
          id: item.id,
          type: item.type,
          variant: item.variant,
          content: item.content,
          ...(item.template_id === undefined ? {} : { template_id: item.template_id }),
          created_at: item.created_at,
        })),
        total,
      }
    },
  })
}

/**
 * Build `customer_acquisition_content_template_create`.
 * @param deps - content service and permission seam.
 * @returns the tool definition.
 */
export function contentTemplateCreateTool(deps: ContentToolDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_content_template_create',
    description: '新建文案模板。body 支持 {{变量}} 占位；variables 声明每个占位变量的名称、说明与示例。type 已知值同 content_generate 描述。',
    parameters: {
      name: { type: 'string', required: true, description: '模板名称' },
      type: { type: 'string', required: true, description: '渠道类型' },
      industry: { type: 'string', description: '适用行业；省略 = 通用' },
      body: { type: 'string', required: true, description: '模板正文' },
      variables: {
        type: 'array',
        items: {
          type: 'object',
          additionalProperties: false,
          properties: {
            name: { type: 'string', required: true },
            description: { type: 'string', required: true },
            example: { type: 'string' },
          },
        },
        description: '变量说明列表',
      },
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
              type: { type: 'string', required: true },
              enabled: { type: 'boolean', required: true },
            },
          },
        },
      },
      render: (_args, value) => [{
        type: 'text',
        text: `已新建文案模板：${value.template.name}（id ${value.template.id}，类型 ${value.template.type}，${value.template.enabled ? '启用中' : '已停用'}）`,
      }],
    },
    presentCall: args => ({
      card: 'generic',
      title: '新建文案模板',
      rawInput: args.name,
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      const { name, type, industry, body, variables, enabled } = args
      const template = await deps.content.createTemplate({
        name,
        type,
        ...(industry === undefined ? {} : { industry }),
        body,
        ...(variables === undefined ? {} : { variables }),
        ...(enabled === undefined ? {} : { enabled }),
      }, operator, 'agent')
      return { template: { id: template.id, name: template.name, type: template.type, enabled: template.enabled } }
    },
  })
}

/**
 * Build `customer_acquisition_content_template_update`.
 * @param deps - content service and permission seam.
 * @returns the tool definition.
 */
export function contentTemplateUpdateTool(deps: ContentToolDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_content_template_update',
    description: '修改文案模板：名称、行业、类型、启用状态，或整体替换正文与变量说明。被生成产物引用的模板也可修改（产物保存了当时的正文快照不影响历史）。',
    parameters: {
      content_template_id: { type: 'string', required: true, description: '模板 id' },
      ...TEMPLATE_FIELD_PARAMETERS,
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
              type: { type: 'string', required: true },
              enabled: { type: 'boolean', required: true },
            },
          },
        },
      },
      render: (_args, value) => [{
        type: 'text',
        text: `已更新文案模板：${value.template.name}（id ${value.template.id}，${value.template.enabled ? '启用中' : '已停用'}）`,
      }],
    },
    presentCall: args => ({
      card: 'generic',
      title: '修改文案模板',
      rawInput: args.content_template_id,
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      const { content_template_id: templateId, name, industry, type, body, variables, enabled } = args
      const template = await deps.content.updateTemplate(templateId, {
        ...(name === undefined ? {} : { name }),
        ...(industry === undefined ? {} : { industry }),
        ...(type === undefined ? {} : { type }),
        ...(body === undefined ? {} : { body }),
        ...(variables === undefined ? {} : { variables }),
        ...(enabled === undefined ? {} : { enabled }),
      }, operator, 'agent')
      return { template: { id: template.id, name: template.name, type: template.type, enabled: template.enabled } }
    },
  })
}

/**
 * Build `customer_acquisition_content_template_list`.
 * @param deps - content service and permission seam.
 * @returns the tool definition.
 */
export function contentTemplateListTool(deps: ContentToolDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_content_template_list',
    description: '列出文案模板（含正文、变量说明与启用状态），可按类型过滤、仅看启用。',
    parameters: {
      type: { type: 'string', description: '按渠道类型过滤' },
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
                type: { type: 'string', required: true },
                body: { type: 'string', required: true },
                variables: {
                  type: 'array',
                  items: {
                    type: 'object',
                    additionalProperties: false,
                    properties: {
                      name: { type: 'string', required: true },
                      description: { type: 'string', required: true },
                      example: { type: 'string' },
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
          ? '尚无文案模板。'
          : `文案模板 ${value.items.length} 套：\n${value.items
            .map(template => `- ${template.name}（id ${template.id}，类型 ${template.type}，${template.industry ?? '通用'}，${template.enabled ? '启用' : '停用'}）`)
            .join('\n')}`,
      }],
    },
    presentCall: () => ({
      card: 'generic',
      title: '查看文案模板',
    }),
    async execute(args, exec) {
      await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      const filters = { ...(args.type === undefined ? {} : { type: args.type }), enabledOnly: args.enabled_only === true }
      const templates = deps.content.listTemplates(filters)
      return {
        items: templates.map(template => ({
          id: template.id,
          name: template.name,
          ...(template.industry === undefined ? {} : { industry: template.industry }),
          type: template.type,
          body: template.body,
          variables: template.variables.map(variable => ({
            name: variable.name,
            description: variable.description,
            ...(variable.example === undefined ? {} : { example: variable.example }),
          })),
          enabled: template.enabled,
        })),
      }
    },
  })
}

/**
 * Build `customer_acquisition_content_template_delete`.
 * @param deps - content service and permission seam.
 * @returns the tool definition.
 */
export function contentTemplateDeleteTool(deps: ContentToolDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_content_template_delete',
    description: '删除一套文案模板。已被生成产物引用时拒绝删除，提示改用 content_template_update 停用（enabled=false）。',
    parameters: {
      content_template_id: { type: 'string', required: true, description: '模板 id' },
    },
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: { deleted: { type: 'boolean', required: true } },
      },
      render: (_args, value) => [{
        type: 'text',
        text: value.deleted ? '文案模板已删除。' : '未删除。',
      }],
    },
    presentCall: args => ({
      card: 'generic',
      title: '删除文案模板',
      rawInput: args.content_template_id,
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      await deps.content.deleteTemplate(args.content_template_id, operator, 'agent')
      return { deleted: true }
    },
  })
}

/** Re-exported for the tool layer's generate-time system prompt wiring. */
export { CONTENT_SYSTEM_PROMPT, llmPromptCompletion }
