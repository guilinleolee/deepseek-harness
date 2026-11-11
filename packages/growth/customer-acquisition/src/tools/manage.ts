/**
 * Consolidated management tools (2026-10 tool-surface reduction): one
 * `*_manage` tool per entity replaces the per-action CRUD tools —
 * `lead_{create,update,get,list}` → `lead_manage`, `icp_*` → `icp_manage`,
 * `score_template_*` → `score_template_manage`, `content_template_*` →
 * `content_template_manage`, `sop_template_*` → `sop_template_manage`, and
 * `sop_task_{list,update}` → `sop_task_manage`. A merged parameter block
 * cannot express per-action `required` fields (the DSL hard-validates the
 * whole schema once before execute), so every execute re-checks the action's
 * required fields at runtime and then dispatches to exactly the service calls
 * the single-action tools used. The operator still resolves per call, and
 * capability/scope enforcement stays inside the services.
 * @module @deepseek-ai/dsh-customer-acquisition/tools/manage
 */

import { defineTool } from '@deepseek-ai/dsh-tools'
import type { ToolDefinition } from '@deepseek-ai/dsh-tools'
import type { NurtureContentService } from '../content/service.ts'
import { toLeadRef } from '../leads/project.ts'
import type { LeadLedgerService } from '../leads/service.ts'
import type { LeadCreateInput, LeadListRequest, LeadRefValue, LeadUpdateInput } from '../leads/types.ts'
import { operatorRequest } from '../permission/types.ts'
import type { PermissionContextService } from '../permission/types.ts'
import { toIcpProfileRef, toScoreTemplateRef } from '../scoring/service.ts'
import type { LeadScoringService } from '../scoring/service.ts'
import type { IcpDimensionInput } from '../scoring/types.ts'
import type { SopService } from '../sop/service.ts'
import { ICP_DIMENSION_PARAMETER_ITEM } from './scoring.ts'
import {
  LEAD_FIELD_PARAMETERS,
  LEAD_FILTER_PARAMETERS,
  LEAD_REF_SCHEMA,
  PAGING_PARAMETERS,
  renderLeadRef,
} from './leads.ts'
import { SOP_RULE_PARAMETER_ITEM } from './sop.ts'
import { TEMPLATE_FIELD_PARAMETERS } from './content.ts'

/** Dependencies the lead manage tool shares with the other lead tools. */
export interface LeadManageDeps {
  readonly ledger: LeadLedgerService
  readonly permission: PermissionContextService
}

/** Dependencies the two scoring manage tools share with the other scoring tools. */
export interface ScoringManageDeps {
  readonly scoring: LeadScoringService
  readonly permission: PermissionContextService
}

/** Dependencies the content-template manage tool shares with the other content tools. */
export interface ContentManageDeps {
  readonly content: NurtureContentService
  readonly permission: PermissionContextService
}

/** Dependencies the two SOP manage tools share with the other SOP tools. */
export interface SopManageDeps {
  readonly sop: SopService
  readonly permission: PermissionContextService
}

/**
 * Copy the defined entries of `args` for `keys` into a fresh object. Merged
 * args carry foreign keys (action, other actions' fields), so `pickDefined`
 * cannot be reused.
 */
function pickKeys(args: Record<string, unknown>, keys: readonly string[]): Record<string, unknown> {
  const picked: Record<string, unknown> = {}
  for (const key of keys) {
    const value = args[key]
    if (value !== undefined) picked[key] = value
  }
  return picked
}

/** Require a string field the schema could not mark required, or fail with the action and field name. */
function requireString(value: string | undefined, field: string, action: string): string {
  if (value === undefined || value.trim().length === 0) {
    throw new Error(`action=${action} 缺少必填字段 ${field}（string，不可为空）`)
  }
  return value
}

/** Require an array field the schema could not mark required, or fail with the action and field name. */
function requireArray<T>(value: T[] | undefined, field: string, action: string): T[] {
  if (value === undefined) {
    throw new Error(`action=${action} 缺少必填字段 ${field}（array，不可缺省）`)
  }
  return value
}

/**
 * Build `customer_acquisition_lead_manage` (replaces lead_create/update/get/list).
 * @param deps - ledger and permission seam.
 * @returns the tool definition.
 */
export function leadManageTool(deps: LeadManageDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_lead_manage',
    description: [
      '线索管理合并工具（原 lead_create/lead_update/lead_get/lead_list）。',
      'action=create：company_name 必填；source 记录线索来源（缺省 manual）；tags 整体传入（数组去重）；归属人缺省为当前操作者。',
      'action=update：lead_id 必填；只覆盖传入的字段，tags 为整体替换语义（传空数组即清空）；source 与 id 不可修改；intent_level 由打分流程回填，此处不接受；回收站中的线索需先恢复。',
      'action=get：lead_id 必填；返回完整字段，附带最近 5 条跟进记录与全部挂接文档的标题列表（文档正文与全部跟进用 list 类工具分页查看）。',
      'action=list：按状态、来源、行业、意向等级、标签、归属与时间范围筛选，支持公司名/联系人关键词模糊搜索，按创建时间倒序分页；status 缺省只看 active，回收站传 status=recycled。',
    ].join(''),
    parameters: {
      action: {
        type: 'string',
        required: true,
        enum: ['create', 'update', 'get', 'list'],
        description: '动作：create=创建 / update=更新 / get=查看 / list=筛选',
      },
      lead_id: { type: 'string', description: '线索 id（update/get 必填）' },
      company_name: { type: 'string', description: '公司名称（create 必填）' },
      owner_id: { type: 'string', description: '归属人 id；缺省为当前操作者（create）' },
      ...LEAD_FIELD_PARAMETERS,
      ...LEAD_FILTER_PARAMETERS,
      ...PAGING_PARAMETERS,
      industry: {
        type: 'string',
        description: '行业：create/update 为可编辑字段（与模板的行业匹配用）；list 为按行业精确过滤',
      },
    },
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: {
          action: { type: 'string', required: true },
          lead: LEAD_REF_SCHEMA,
          demand_desc: { type: 'string' },
          budget_range: { type: 'string' },
          followups: {
            type: 'array',
            items: {
              type: 'object',
              additionalProperties: false,
              properties: {
                id: { type: 'string', required: true },
                content: { type: 'string', required: true },
                created_at: { type: 'integer', required: true },
              },
            },
          },
          documents: {
            type: 'array',
            items: {
              type: 'object',
              additionalProperties: false,
              properties: {
                id: { type: 'string', required: true },
                title: { type: 'string', required: true },
              },
            },
          },
          items: { type: 'array', items: LEAD_REF_SCHEMA },
          total: { type: 'integer' },
        },
      },
      render: (_args, value) => {
        const action = (value as { action: string }).action
        if (action === 'list') {
          const page = value as { items: LeadRefValue[]; total: number }
          return [{
            type: 'text',
            text: page.items.length === 0
              ? `线索共 ${page.total} 条，当前页无记录。`
              : `线索共 ${page.total} 条，本页 ${page.items.length} 条：\n${page.items.map(renderLeadRef).join('\n')}`,
          }]
        }
        if (action === 'get') {
          const detail = value as {
            lead: LeadRefValue
            demand_desc?: string
            budget_range?: string
            followups: { id: string; content: string; created_at: number }[]
            documents: { id: string; title: string }[]
          }
          const lines = [
            renderLeadRef(detail.lead),
            detail.demand_desc === undefined ? '' : `需求：${detail.demand_desc}`,
            detail.budget_range === undefined ? '' : `预算：${detail.budget_range}`,
            detail.followups.length === 0 ? '' : `最近跟进 ${detail.followups.length} 条：`,
            ...detail.followups.map(followup => `  · ${new Date(followup.created_at).toISOString()} ${followup.content}`),
            detail.documents.length === 0 ? '' : `挂接资料 ${detail.documents.length} 份：${detail.documents.map(document => document.title).join('、')}`,
          ].filter(line => line.length > 0)
          return [{ type: 'text', text: lines.join('\n') }]
        }
        const ref = value as { action: 'create' | 'update'; lead: LeadRefValue }
        return [{
          type: 'text',
          text: `${ref.action === 'create' ? '已创建' : '已更新'}线索：\n${renderLeadRef(ref.lead)}`,
        }]
      },
    },
    presentCall: args => ({
      card: 'generic',
      title: args.action === 'create'
        ? '新建线索'
        : args.action === 'update'
          ? '更新线索'
          : args.action === 'get'
            ? '查看线索'
            : '筛选线索',
      rawInput: args.action === 'list'
        ? (args.q ?? (args.status === undefined ? '' : `status=${args.status}`))
        : (args.action === 'create' ? args.company_name : args.lead_id),
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      if (args.action === 'create') {
        const company = requireString(args.company_name, 'company_name', 'create')
        const input = {
          ...pickKeys(args, [...Object.keys(LEAD_FIELD_PARAMETERS), 'source', 'owner_id']),
          company_name: company,
        } as LeadCreateInput
        const lead = await deps.ledger.createLead(input, operator, 'agent')
        return { action: 'create', lead: toLeadRef(lead) }
      }
      if (args.action === 'update') {
        const leadId = requireString(args.lead_id, 'lead_id', 'update')
        const patch = pickKeys(args, Object.keys(LEAD_FIELD_PARAMETERS)) as LeadUpdateInput
        const lead = await deps.ledger.updateLead(leadId, patch, operator, 'agent')
        return { action: 'update', lead: toLeadRef(lead) }
      }
      if (args.action === 'get') {
        const leadId = requireString(args.lead_id, 'lead_id', 'get')
        const detail = await deps.ledger.getLeadDetail(leadId, operator)
        return { action: 'get', ...detail }
      }
      const request = pickKeys(args, [...Object.keys(LEAD_FILTER_PARAMETERS), ...Object.keys(PAGING_PARAMETERS)]) as LeadListRequest
      const { items, total } = deps.ledger.listLeads(request, operator)
      return { action: 'list', items: items.map(toLeadRef), total }
    },
  })
}

/**
 * Build `customer_acquisition_icp_manage` (replaces icp_create/update/list/delete).
 * @param deps - scoring service and permission seam.
 * @returns the tool definition.
 */
export function icpManageTool(deps: ScoringManageDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_icp_manage',
    description: [
      'ICP 画像管理合并工具（原 icp_create/icp_update/icp_list/icp_delete）。',
      'action=create：name 与 dimensions 必填；权重必须合计为 100（±0.01），否则拒绝保存；维度 id 在画像内唯一。',
      'action=update：icp_profile_id 必填；可改名称、行业、启用状态，或整体替换维度列表（权重仍须合计 100）；历史打分不受影响（分项保存了当时的权重快照）。',
      'action=list：列出全部画像（含维度与权重、启用状态），可仅看启用。',
      'action=delete：icp_profile_id 必填；已被打分历史引用时拒绝删除，请改用 update 停用（enabled=false）。',
    ].join(''),
    parameters: {
      action: {
        type: 'string',
        required: true,
        enum: ['create', 'update', 'list', 'delete'],
        description: '动作：create / update / list / delete',
      },
      icp_profile_id: { type: 'string', description: '画像 id（update/delete 必填）' },
      name: { type: 'string', description: '画像名称（create 必填）；update 为新名称' },
      industry: { type: 'string', description: '适用行业；省略 = 通用（update 为新行业）' },
      dimensions: {
        type: 'array',
        items: ICP_DIMENSION_PARAMETER_ITEM,
        description: '评分维度列表，1-N 个（create 必填；update 为整体替换）',
      },
      enabled: { type: 'boolean', description: 'create：默认 true；update：启用状态' },
      enabled_only: { type: 'boolean', description: 'list：仅看启用，默认 false' },
    },
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: {
          action: { type: 'string', required: true },
          profile: {
            type: 'object',
            additionalProperties: false,
            properties: {
              id: { type: 'string', required: true },
              name: { type: 'string', required: true },
              enabled: { type: 'boolean', required: true },
            },
          },
          items: {
            type: 'array',
            items: {
              type: 'object',
              additionalProperties: false,
              properties: {
                id: { type: 'string', required: true },
                name: { type: 'string', required: true },
                industry: { type: 'string' },
                enabled: { type: 'boolean', required: true },
                dimensions: {
                  type: 'array',
                  required: true,
                  items: {
                    type: 'object',
                    additionalProperties: false,
                    properties: {
                      id: { type: 'string', required: true },
                      name: { type: 'string', required: true },
                      description: { type: 'string', required: true },
                      weight: { type: 'number', required: true },
                    },
                  },
                },
              },
            },
          },
          deleted: { type: 'boolean' },
        },
      },
      render: (_args, value) => {
        const action = (value as { action: string }).action
        if (action === 'list') {
          const list = value as {
            items: {
              id: string
              name: string
              industry?: string
              enabled: boolean
              dimensions: { id: string; weight: number }[]
            }[]
          }
          return [{
            type: 'text',
            text: list.items.length === 0
              ? '尚无 ICP 画像。'
              : `ICP 画像 ${list.items.length} 套：\n${list.items.map((profile) => {
                const dims = profile.dimensions
                  .map(dimension => `${dimension.id}（${dimension.weight}%）`)
                  .join('、')
                return `- ${profile.name}（id ${profile.id}，${profile.industry ?? '通用'}，${profile.enabled ? '启用' : '停用'}）：${dims}`
              }).join('\n')}`,
          }]
        }
        if (action === 'delete') {
          const removed = value as { deleted: boolean }
          return [{ type: 'text', text: removed.deleted ? 'ICP 画像已删除。' : '未删除。' }]
        }
        const ref = value as { action: 'create' | 'update'; profile: { id: string; name: string; enabled: boolean } }
        return [{
          type: 'text',
          text: `${ref.action === 'create' ? '已新建' : '已更新'} ICP 画像：${ref.profile.name}（id ${ref.profile.id}，${ref.profile.enabled ? '启用中' : '已停用'}）`,
        }]
      },
    },
    presentCall: args => ({
      card: 'generic',
      title: args.action === 'create'
        ? '新建 ICP 画像'
        : args.action === 'update'
          ? '修改 ICP 画像'
          : args.action === 'delete'
            ? '删除 ICP 画像'
            : '查看 ICP 画像',
      rawInput: args.action === 'create' ? args.name : args.icp_profile_id,
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      if (args.action === 'create') {
        const name = requireString(args.name, 'name', 'create')
        const dimensions = requireArray(args.dimensions, 'dimensions', 'create')
        const profile = await deps.scoring.createIcpProfile({
          name,
          ...(args.industry === undefined ? {} : { industry: args.industry }),
          dimensions,
          ...(args.enabled === undefined ? {} : { enabled: args.enabled }),
        }, operator, 'agent')
        return { action: 'create', profile: toIcpProfileRef(profile) }
      }
      if (args.action === 'update') {
        const profileId = requireString(args.icp_profile_id, 'icp_profile_id', 'update')
        const profile = await deps.scoring.updateIcpProfile(profileId, {
          ...(args.name === undefined ? {} : { name: args.name }),
          ...(args.industry === undefined ? {} : { industry: args.industry }),
          ...(args.enabled === undefined ? {} : { enabled: args.enabled }),
          ...(args.dimensions === undefined ? {} : { dimensions: args.dimensions as IcpDimensionInput[] }),
        }, operator, 'agent')
        return { action: 'update', profile: toIcpProfileRef(profile) }
      }
      if (args.action === 'delete') {
        const profileId = requireString(args.icp_profile_id, 'icp_profile_id', 'delete')
        await deps.scoring.deleteIcpProfile(profileId, operator, 'agent')
        return { action: 'delete', deleted: true }
      }
      return { action: 'list', items: deps.scoring.listIcpProfiles(args.enabled_only === true) }
    },
  })
}

/**
 * Build `customer_acquisition_score_template_manage` (replaces score_template_create/update/list/delete).
 * @param deps - scoring service and permission seam.
 * @returns the tool definition.
 */
export function scoreTemplateManageTool(deps: ScoringManageDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_score_template_manage',
    description: [
      '打分提示词模板管理合并工具（原 score_template_create/update/list/delete）。',
      'action=create：name 与 prompt_text 必填；prompt_text 支持 {{lead}}（线索 JSON）、{{icp_profile}}（画像）、{{dimensions}}（维度清单）、{{knowledge}}（线索资料注入）占位符。',
      'action=update：score_template_id 必填；可改名称、行业、启用状态或提示词正文；被历史引用也可修改（历史分项保存了当时的权重快照，提示词变更只影响后续打分）。',
      'action=list：列出全部模板（含提示词全文与启用状态），可仅看启用。',
      'action=delete：score_template_id 必填；已被打分历史引用时拒绝删除，请改用 update 停用（enabled=false）。',
    ].join(''),
    parameters: {
      action: {
        type: 'string',
        required: true,
        enum: ['create', 'update', 'list', 'delete'],
        description: '动作：create / update / list / delete',
      },
      score_template_id: { type: 'string', description: '模板 id（update/delete 必填）' },
      name: { type: 'string', description: '模板名称（create 必填）；update 为新名称' },
      industry: { type: 'string', description: '适用行业；省略 = 通用（update 为新行业）' },
      prompt_text: { type: 'string', description: '提示词正文，支持四类占位符（create 必填）；update 为新提示词正文' },
      enabled: { type: 'boolean', description: 'create：默认 true；update：启用状态' },
      enabled_only: { type: 'boolean', description: 'list：仅看启用，默认 false' },
    },
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: {
          action: { type: 'string', required: true },
          template: {
            type: 'object',
            additionalProperties: false,
            properties: {
              id: { type: 'string', required: true },
              name: { type: 'string', required: true },
              enabled: { type: 'boolean', required: true },
            },
          },
          items: {
            type: 'array',
            items: {
              type: 'object',
              additionalProperties: false,
              properties: {
                id: { type: 'string', required: true },
                name: { type: 'string', required: true },
                industry: { type: 'string' },
                prompt_text: { type: 'string', required: true },
                enabled: { type: 'boolean', required: true },
              },
            },
          },
          deleted: { type: 'boolean' },
        },
      },
      render: (_args, value) => {
        const action = (value as { action: string }).action
        if (action === 'list') {
          const list = value as {
            items: { id: string; name: string; industry?: string; enabled: boolean }[]
          }
          return [{
            type: 'text',
            text: list.items.length === 0
              ? '尚无打分模板。'
              : `打分模板 ${list.items.length} 套：\n${list.items
                .map(template => `- ${template.name}（id ${template.id}，${template.industry ?? '通用'}，${template.enabled ? '启用' : '停用'}）`)
                .join('\n')}`,
          }]
        }
        if (action === 'delete') {
          const removed = value as { deleted: boolean }
          return [{ type: 'text', text: removed.deleted ? '打分模板已删除。' : '未删除。' }]
        }
        const ref = value as { action: 'create' | 'update'; template: { id: string; name: string; enabled: boolean } }
        return [{
          type: 'text',
          text: `${ref.action === 'create' ? '已新建' : '已更新'}打分模板：${ref.template.name}（id ${ref.template.id}，${ref.template.enabled ? '启用中' : '已停用'}）`,
        }]
      },
    },
    presentCall: args => ({
      card: 'generic',
      title: args.action === 'create'
        ? '新建打分模板'
        : args.action === 'update'
          ? '修改打分模板'
          : args.action === 'delete'
            ? '删除打分模板'
            : '查看打分模板',
      rawInput: args.action === 'create' ? args.name : args.score_template_id,
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      if (args.action === 'create') {
        const name = requireString(args.name, 'name', 'create')
        const promptText = requireString(args.prompt_text, 'prompt_text', 'create')
        const template = await deps.scoring.createScoreTemplate({
          name,
          ...(args.industry === undefined ? {} : { industry: args.industry }),
          prompt_text: promptText,
          ...(args.enabled === undefined ? {} : { enabled: args.enabled }),
        }, operator, 'agent')
        return { action: 'create', template: toScoreTemplateRef(template) }
      }
      if (args.action === 'update') {
        const templateId = requireString(args.score_template_id, 'score_template_id', 'update')
        const template = await deps.scoring.updateScoreTemplate(templateId, {
          ...(args.name === undefined ? {} : { name: args.name }),
          ...(args.industry === undefined ? {} : { industry: args.industry }),
          ...(args.prompt_text === undefined ? {} : { prompt_text: args.prompt_text }),
          ...(args.enabled === undefined ? {} : { enabled: args.enabled }),
        }, operator, 'agent')
        return { action: 'update', template: toScoreTemplateRef(template) }
      }
      if (args.action === 'delete') {
        const templateId = requireString(args.score_template_id, 'score_template_id', 'delete')
        await deps.scoring.deleteScoreTemplate(templateId, operator, 'agent')
        return { action: 'delete', deleted: true }
      }
      return { action: 'list', items: deps.scoring.listScoreTemplates(args.enabled_only === true) }
    },
  })
}

/**
 * Build `customer_acquisition_content_template_manage` (replaces content_template_create/update/list/delete).
 * @param deps - content service and permission seam.
 * @returns the tool definition.
 */
export function contentTemplateManageTool(deps: ContentManageDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_content_template_manage',
    description: [
      '文案模板管理合并工具（原 content_template_create/update/list/delete）。',
      'action=create：name、type、body 必填；body 支持 {{变量}} 占位；variables 声明每个占位变量的名称、说明与示例；type 已知值同 content_generate 描述。',
      'action=update：content_template_id 必填；可改名称、行业、类型、启用状态，或整体替换正文与变量说明；被生成产物引用的模板也可修改（产物保存了当时的正文快照不影响历史）。',
      'action=list：列出全部模板（含正文、变量说明与启用状态），可按类型过滤、仅看启用。',
      'action=delete：content_template_id 必填；已被生成产物引用时拒绝删除，请改用 update 停用（enabled=false）。',
    ].join(''),
    parameters: {
      action: {
        type: 'string',
        required: true,
        enum: ['create', 'update', 'list', 'delete'],
        description: '动作：create / update / list / delete',
      },
      content_template_id: { type: 'string', description: '模板 id（update/delete 必填）' },
      ...TEMPLATE_FIELD_PARAMETERS,
      enabled_only: { type: 'boolean', description: 'list：仅看启用，默认 false' },
    },
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: {
          action: { type: 'string', required: true },
          template: {
            type: 'object',
            additionalProperties: false,
            properties: {
              id: { type: 'string', required: true },
              name: { type: 'string', required: true },
              type: { type: 'string', required: true },
              enabled: { type: 'boolean', required: true },
            },
          },
          items: {
            type: 'array',
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
          deleted: { type: 'boolean' },
        },
      },
      render: (_args, value) => {
        const action = (value as { action: string }).action
        if (action === 'list') {
          const list = value as {
            items: { id: string; name: string; industry?: string; type: string; enabled: boolean }[]
          }
          return [{
            type: 'text',
            text: list.items.length === 0
              ? '尚无文案模板。'
              : `文案模板 ${list.items.length} 套：\n${list.items
                .map(template => `- ${template.name}（id ${template.id}，类型 ${template.type}，${template.industry ?? '通用'}，${template.enabled ? '启用' : '停用'}）`)
                .join('\n')}`,
          }]
        }
        if (action === 'delete') {
          const removed = value as { deleted: boolean }
          return [{ type: 'text', text: removed.deleted ? '文案模板已删除。' : '未删除。' }]
        }
        const ref = value as { action: 'create' | 'update'; template: { id: string; name: string; type: string; enabled: boolean } }
        return [{
          type: 'text',
          text: `${ref.action === 'create' ? '已新建' : '已更新'}文案模板：${ref.template.name}（id ${ref.template.id}，${ref.action === 'create' ? `类型 ${ref.template.type}，` : ''}${ref.template.enabled ? '启用中' : '已停用'}）`,
        }]
      },
    },
    presentCall: args => ({
      card: 'generic',
      title: args.action === 'create'
        ? '新建文案模板'
        : args.action === 'update'
          ? '修改文案模板'
          : args.action === 'delete'
            ? '删除文案模板'
            : '查看文案模板',
      rawInput: args.action === 'create' ? args.name : args.content_template_id,
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      if (args.action === 'create') {
        const name = requireString(args.name, 'name', 'create')
        const type = requireString(args.type, 'type', 'create')
        const body = requireString(args.body, 'body', 'create')
        const template = await deps.content.createTemplate({
          name,
          type,
          ...(args.industry === undefined ? {} : { industry: args.industry }),
          body,
          ...(args.variables === undefined ? {} : { variables: args.variables }),
          ...(args.enabled === undefined ? {} : { enabled: args.enabled }),
        }, operator, 'agent')
        return { action: 'create', template: { id: template.id, name: template.name, type: template.type, enabled: template.enabled } }
      }
      if (args.action === 'update') {
        const templateId = requireString(args.content_template_id, 'content_template_id', 'update')
        const template = await deps.content.updateTemplate(templateId, {
          ...(args.name === undefined ? {} : { name: args.name }),
          ...(args.industry === undefined ? {} : { industry: args.industry }),
          ...(args.type === undefined ? {} : { type: args.type }),
          ...(args.body === undefined ? {} : { body: args.body }),
          ...(args.variables === undefined ? {} : { variables: args.variables }),
          ...(args.enabled === undefined ? {} : { enabled: args.enabled }),
        }, operator, 'agent')
        return { action: 'update', template: { id: template.id, name: template.name, type: template.type, enabled: template.enabled } }
      }
      if (args.action === 'delete') {
        const templateId = requireString(args.content_template_id, 'content_template_id', 'delete')
        await deps.content.deleteTemplate(templateId, operator, 'agent')
        return { action: 'delete', deleted: true }
      }
      const filters = { ...(args.type === undefined ? {} : { type: args.type }), enabledOnly: args.enabled_only === true }
      const templates = deps.content.listTemplates(filters)
      return {
        action: 'list',
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
 * Build `customer_acquisition_sop_template_manage` (replaces sop_template_create/update/list/delete).
 * @param deps - SOP service and permission seam.
 * @returns the tool definition.
 */
export function sopTemplateManageTool(deps: SopManageDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_sop_template_manage',
    description: [
      'SOP 跟进模板管理合并工具（原 sop_template_create/update/list/delete）。',
      'action=create：name 与 rules 必填；按意向等级（high/mid/low/invalid）各给一条规则，含跟进节奏（D+N 会被解析为任务排期）、跟进要点、沟通提问清单与风险提示；等级在模板内不可重复。',
      'action=update：sop_template_id 必填；可改名称、行业、启用状态，或整体替换规则列表（每等级一条，D+N 节奏重新生效于后续生成）。',
      'action=list：列出全部模板（含规则全文与启用状态），可仅看启用。',
      'action=delete：sop_template_id 必填；已生成的跟进任务不受影响（任务独立存储）；删除后不可恢复。',
    ].join(''),
    parameters: {
      action: {
        type: 'string',
        required: true,
        enum: ['create', 'update', 'list', 'delete'],
        description: '动作：create / update / list / delete',
      },
      sop_template_id: { type: 'string', description: '模板 id（update/delete 必填）' },
      name: { type: 'string', description: '模板名称（create 必填）；update 为新名称' },
      industry: { type: 'string', description: '适用行业；省略 = 通用（update 为新行业）' },
      rules: { type: 'array', items: SOP_RULE_PARAMETER_ITEM, description: '规则列表，1-N 条（create 必填；update 为整体替换）' },
      enabled: { type: 'boolean', description: 'create：默认 true；update：启用状态' },
      enabled_only: { type: 'boolean', description: 'list：仅看启用，默认 false' },
    },
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: {
          action: { type: 'string', required: true },
          template: {
            type: 'object',
            additionalProperties: false,
            properties: {
              id: { type: 'string', required: true },
              name: { type: 'string', required: true },
              enabled: { type: 'boolean', required: true },
            },
          },
          items: {
            type: 'array',
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
          deleted: { type: 'boolean' },
        },
      },
      render: (_args, value) => {
        const action = (value as { action: string }).action
        if (action === 'list') {
          const list = value as {
            items: {
              id: string
              name: string
              industry?: string
              enabled: boolean
              rules: { intent_level: string }[]
            }[]
          }
          return [{
            type: 'text',
            text: list.items.length === 0
              ? '尚无 SOP 模板。'
              : `SOP 模板 ${list.items.length} 套：\n${list.items
                .map((template) => {
                  const levels = template.rules.map(rule => rule.intent_level).join('/')
                  return `- ${template.name}（id ${template.id}，${template.industry ?? '通用'}，${template.enabled ? '启用' : '停用'}）：等级 ${levels}`
                })
                .join('\n')}`,
          }]
        }
        if (action === 'delete') {
          const removed = value as { deleted: boolean }
          return [{ type: 'text', text: removed.deleted ? 'SOP 模板已删除。' : '未删除。' }]
        }
        const ref = value as { action: 'create' | 'update'; template: { id: string; name: string; enabled: boolean } }
        return [{
          type: 'text',
          text: `${ref.action === 'create' ? '已新建' : '已更新'} SOP 模板：${ref.template.name}（id ${ref.template.id}，${ref.template.enabled ? '启用中' : '已停用'}）`,
        }]
      },
    },
    presentCall: args => ({
      card: 'generic',
      title: args.action === 'create'
        ? '新建 SOP 模板'
        : args.action === 'update'
          ? '修改 SOP 模板'
          : args.action === 'delete'
            ? '删除 SOP 模板'
            : '查看 SOP 模板',
      rawInput: args.action === 'create' ? args.name : args.sop_template_id,
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      if (args.action === 'create') {
        const name = requireString(args.name, 'name', 'create')
        const rules = requireArray(args.rules, 'rules', 'create')
        const template = await deps.sop.createTemplate({
          name,
          ...(args.industry === undefined ? {} : { industry: args.industry }),
          rules: rules.map(rule => ({
            intent_level: rule.intent_level,
            cadence: rule.cadence,
            points: [...rule.points],
            questions: [...(rule.questions ?? [])],
            risks: [...(rule.risks ?? [])],
          })),
          ...(args.enabled === undefined ? {} : { enabled: args.enabled }),
        }, operator, 'agent')
        return { action: 'create', template: { id: template.id, name: template.name, enabled: template.enabled } }
      }
      if (args.action === 'update') {
        const templateId = requireString(args.sop_template_id, 'sop_template_id', 'update')
        const template = await deps.sop.updateTemplate(templateId, {
          ...(args.name === undefined ? {} : { name: args.name }),
          ...(args.industry === undefined ? {} : { industry: args.industry }),
          ...(args.rules === undefined ? {} : { rules: args.rules.map(rule => ({
            intent_level: rule.intent_level,
            cadence: rule.cadence,
            points: [...rule.points],
            questions: [...(rule.questions ?? [])],
            risks: [...(rule.risks ?? [])],
          })) }),
          ...(args.enabled === undefined ? {} : { enabled: args.enabled }),
        }, operator, 'agent')
        return { action: 'update', template: { id: template.id, name: template.name, enabled: template.enabled } }
      }
      if (args.action === 'delete') {
        const templateId = requireString(args.sop_template_id, 'sop_template_id', 'delete')
        await deps.sop.deleteTemplate(templateId, operator, 'agent')
        return { action: 'delete', deleted: true }
      }
      return {
        action: 'list',
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
 * Build `customer_acquisition_sop_task_manage` (replaces sop_task_list/update).
 * @param deps - SOP service and permission seam.
 * @returns the tool definition.
 */
export function sopTaskManageTool(deps: SopManageDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_sop_task_manage',
    description: [
      'SOP 跟进任务管理合并工具（原 sop_task_list/sop_task_update）。',
      'action=list：按线索、状态过滤，按计划时间升序分页返回。',
      'action=update：task_id 必填；流转任务状态（pending/done/deferred/dropped），可调整计划时间与备注（整体替换）。',
    ].join(''),
    parameters: {
      action: {
        type: 'string',
        required: true,
        enum: ['list', 'update'],
        description: '动作：list / update',
      },
      task_id: { type: 'string', description: '任务 id（update 必填）' },
      lead_id: { type: 'string', description: '按线索过滤（list）' },
      status: { type: 'string', enum: ['pending', 'done', 'deferred', 'dropped'], description: 'list：按状态过滤；update：目标状态' },
      planned_at: { type: 'integer', description: '调整后的计划时间（epoch 毫秒，update）' },
      note: { type: 'string', description: '备注（整体替换，update）' },
      limit: { type: 'integer', description: '每页条数，默认 20，最大 100；越界值自动收敛（list）' },
      offset: { type: 'integer', description: '偏移量，默认 0；负值按 0 处理（list）' },
    },
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: {
          action: { type: 'string', required: true },
          items: {
            type: 'array',
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
          total: { type: 'integer' },
          task: {
            type: 'object',
            additionalProperties: false,
            properties: {
              id: { type: 'string', required: true },
              status: { type: 'string', required: true },
              planned_at: { type: 'integer', required: true },
            },
          },
        },
      },
      render: (_args, value) => {
        const action = (value as { action: string }).action
        if (action === 'list') {
          const page = value as {
            items: { id: string; lead_id: string; title: string; status: string; planned_at: number }[]
            total: number
          }
          return [{
            type: 'text',
            text: page.items.length === 0
              ? `SOP 任务共 ${page.total} 条，当前页无记录。`
              : `SOP 任务共 ${page.total} 条，本页 ${page.items.length} 条：\n${page.items
                .map(task => `- ${new Date(task.planned_at).toISOString().slice(0, 10)} [${task.status}] ${task.title}（线索 ${task.lead_id}，id ${task.id}）`)
                .join('\n')}`,
          }]
        }
        const moved = value as { task: { id: string; status: string; planned_at: number } }
        return [{
          type: 'text',
          text: `任务已流转：id ${moved.task.id} → ${moved.task.status}（计划 ${new Date(moved.task.planned_at).toISOString().slice(0, 10)}）`,
        }]
      },
    },
    presentCall: args => ({
      card: 'generic',
      title: args.action === 'list' ? '查看 SOP 任务' : '流转 SOP 任务',
      rawInput: args.action === 'list'
        ? (args.lead_id ?? (args.status === undefined ? '' : `status=${args.status}`))
        : `${args.task_id} → ${args.status ?? '（不变）'}`,
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      if (args.action === 'update') {
        const taskId = requireString(args.task_id, 'task_id', 'update')
        const task = await deps.sop.updateTask(taskId, {
          ...(args.status === undefined ? {} : { status: args.status }),
          ...(args.planned_at === undefined ? {} : { planned_at: args.planned_at }),
          ...(args.note === undefined ? {} : { note: args.note }),
        }, operator, 'agent')
        return { action: 'update', task: { id: task.id, status: task.status, planned_at: task.planned_at } }
      }
      const { lead_id: leadId, status, limit, offset } = args
      const { items, total } = deps.sop.listTasks({
        ...(leadId === undefined ? {} : { lead_id: leadId }),
        ...(status === undefined ? {} : { status }),
        ...(limit === undefined ? {} : { limit }),
        ...(offset === undefined ? {} : { offset }),
      }, operator)
      return {
        action: 'list',
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
