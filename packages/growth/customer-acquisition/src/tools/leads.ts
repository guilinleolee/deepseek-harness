/**
 * Module-2 model-facing tools (tools manifest §5): the lead ledger's CRUD,
 * pool semantics, extraction, export, documents, and follow-ups. Every
 * execute resolves the operator per call, delegates the whole capability and
 * scope enforcement to the ledger service, and returns the canonical value
 * the output schema declares. No send channel exists anywhere (red line 3).
 * @module @deepseek-ai/dsh-customer-acquisition/tools/leads
 */

import { defineTool } from '@deepseek-ai/dsh-tools'
import type { ToolDefinition } from '@deepseek-ai/dsh-tools'
import { COMPANY_SIZES_HINT, LEAD_SOURCES_HINT } from '../domain/vocab.ts'
import { renderLeadExport } from '../leads/export.ts'
import { EXTRACT_MAX_CHARS } from '../leads/extract.ts'
import { toLeadRef } from '../leads/project.ts'
import type { LeadLedgerService } from '../leads/service.ts'
import type { LeadRefValue, LeadListRequest } from '../leads/types.ts'
import type { PromptCompletion } from '../llm/oneshot.ts'
import { operatorRequest } from '../permission/types.ts'
import type { PermissionContextService } from '../permission/types.ts'

/** Lead summary projection schema shared by create/update/get/list outputs. */
const LEAD_REF_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    id: { type: 'string', required: true },
    company_name: { type: 'string', required: true },
    contact_name: { type: 'string' },
    source: { type: 'string', required: true },
    industry: { type: 'string' },
    intent_level: { type: 'string' },
    opportunity_stage: { type: 'string', required: true },
    owner_id: { type: 'string' },
    status: { type: 'string', required: true },
    tags: { type: 'array', items: { type: 'string' } },
    next_followup_at: { type: 'integer' },
    updated_at: { type: 'integer', required: true },
  },
} as const

/** The lead ref as a required envelope property (create/update/get outputs). */
const LEAD_REF_REQUIRED = { ...LEAD_REF_SCHEMA, required: true } as const

/** Editable lead fields shared by create and update (create adds id/name/source/owner). */
const LEAD_FIELD_PARAMETERS = {
  contact_name: { type: 'string', description: '联系人姓名' },
  phone: { type: 'string', description: '联系电话（宽松存储，格式提示在面板）' },
  email: { type: 'string', description: '邮箱' },
  industry: { type: 'string', description: '行业（自由文本，与模板的行业匹配用）' },
  company_size: { type: 'string', description: `规模档位，已知值：${COMPANY_SIZES_HINT}` },
  demand_desc: { type: 'string', description: '需求描述' },
  budget_range: { type: 'string', description: '预算档位（自由文本）' },
  decision_role: {
    type: 'string',
    enum: ['decision_maker', 'influencer', 'end_user', 'gatekeeper', 'unknown'],
    description: '决策角色',
  },
  tags: { type: 'array', items: { type: 'string' }, description: '标签；整体传入，不可重复（更新时整体替换）' },
  opportunity_stage: {
    type: 'string',
    enum: ['new', 'contacted', 'nurturing', 'qualified', 'won', 'lost'],
    description: '商机阶段，缺省 new',
  },
  next_followup_at: { type: 'integer', description: '下次跟进时间（epoch 毫秒）' },
} as const

/** Filters shared by lead list and export. */
const LEAD_FILTER_PARAMETERS = {
  status: { type: 'string', enum: ['active', 'archived', 'recycled'], description: '状态过滤；缺省只看 active，回收站传 recycled' },
  source: { type: 'string', description: '按来源精确过滤' },
  industry: { type: 'string', description: '按行业精确过滤' },
  intent_level: { type: 'string', enum: ['high', 'mid', 'low', 'invalid'], description: '按意向等级过滤' },
  tag: { type: 'string', description: '按标签过滤（任一匹配）' },
  owner: { type: 'string', enum: ['me', 'pool', 'all'], description: '归属过滤：me=我的；pool=公海（无归属人）；all=全部。缺省 all，own 能力自动收敛为自己+公海' },
  q: { type: 'string', description: '公司名/联系人模糊搜索' },
  created_from: { type: 'integer', description: '创建时间起（epoch 毫秒，含）' },
  created_to: { type: 'integer', description: '创建时间止（epoch 毫秒，含）' },
} as const

/** Paging bounds shared by the list faces. */
const PAGING_PARAMETERS = {
  limit: { type: 'integer', description: '每页条数，默认 20，最大 100；越界值自动收敛' },
  offset: { type: 'integer', description: '偏移量，默认 0；负值按 0 处理' },
} as const

/**
 * The structural slice of a lead ref the one-line render needs; looser than
 * `LeadRefValue` so the tool output schema's inferred types (open string
 * fields) feed it directly.
 */
interface LeadRefLike {
  readonly id: string
  readonly company_name: string
  readonly contact_name?: string
  readonly source: string
  readonly opportunity_stage: string
  readonly status: string
  readonly intent_level?: string
  readonly owner_id?: string
  readonly tags?: readonly string[]
}

/** One human-readable line for a lead ref. */
function renderLeadRef(lead: LeadRefLike): string {
  const parts = [
    lead.company_name,
    lead.contact_name === undefined ? '' : `联系人 ${lead.contact_name}`,
    `来源 ${lead.source}`,
    `阶段 ${lead.opportunity_stage}`,
    `状态 ${lead.status}`,
    lead.intent_level === undefined ? '' : `意向 ${lead.intent_level}`,
    lead.owner_id === undefined ? '公海' : `归属 ${lead.owner_id}`,
    lead.tags === undefined || lead.tags.length === 0 ? '' : `标签 ${lead.tags.join('、')}`,
  ].filter(part => part.length > 0)
  return `- ${lead.id}｜${parts.join('｜')}`
}

/** Copy only the defined entries of a raw args object into a typed request. */
function pickDefined<T extends object>(args: Record<string, unknown>): Partial<T> {
  return Object.fromEntries(Object.entries(args).filter(([, value]) => value !== undefined)) as Partial<T>
}

/** Dependencies every lead tool shares. */
export interface LeadToolDeps {
  readonly ledger: LeadLedgerService
  readonly permission: PermissionContextService
  /** The extraction face's prompt completion (fixed system prompt, production policy). */
  readonly completion: PromptCompletion
}

/**
 * Build `customer_acquisition_lead_create`.
 * @param deps - ledger and permission seam.
 * @returns the tool definition.
 */
export function leadCreateTool(deps: LeadToolDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_lead_create',
    description: `创建一条线索记录并返回完整字段。company_name 必填；source 记录线索来源，已知值：${LEAD_SOURCES_HINT}；tags 整体传入（数组去重）。归属人缺省为当前操作者。`,
    parameters: {
      company_name: { type: 'string', required: true, description: '公司名称（必填）' },
      source: { type: 'string', description: '线索来源；缺省 manual' },
      owner_id: { type: 'string', description: '归属人 id；缺省为当前操作者' },
      ...LEAD_FIELD_PARAMETERS,
    },
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: { lead: LEAD_REF_REQUIRED },
      },
      render: (_args, value) => [{
        type: 'text',
        text: `已创建线索：\n${renderLeadRef((value as { lead: LeadRefValue }).lead)}`,
      }],
    },
    presentCall: args => ({
      card: 'generic',
      title: '新建线索',
      rawInput: args.company_name,
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      const lead = await deps.ledger.createLead({
        ...pickDefined(args),
        company_name: args.company_name,
      }, operator, 'agent')
      return { lead: toLeadRef(lead) }
    },
  })
}

/**
 * Build `customer_acquisition_lead_update`.
 * @param deps - ledger and permission seam.
 * @returns the tool definition.
 */
export function leadUpdateTool(deps: LeadToolDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_lead_update',
    description: '更新线索的可编辑字段，只覆盖传入的字段。tags 为整体替换语义（传空数组即清空）。source 与 id 不可修改；intent_level 由打分流程回填，此处不接受。回收站中的线索需先恢复。',
    parameters: {
      lead_id: { type: 'string', required: true, description: '线索 id' },
      ...LEAD_FIELD_PARAMETERS,
    },
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: { lead: LEAD_REF_REQUIRED },
      },
      render: (_args, value) => [{
        type: 'text',
        text: `已更新线索：\n${renderLeadRef((value as { lead: LeadRefValue }).lead)}`,
      }],
    },
    presentCall: args => ({
      card: 'generic',
      title: '更新线索',
      rawInput: args.lead_id,
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      const { lead_id: leadId, ...patch } = args
      const lead = await deps.ledger.updateLead(leadId, pickDefined(patch), operator, 'agent')
      return { lead: toLeadRef(lead) }
    },
  })
}

/**
 * Build `customer_acquisition_lead_get`.
 * @param deps - ledger and permission seam.
 * @returns the tool definition.
 */
export function leadGetTool(deps: LeadToolDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_lead_get',
    description: '读取一条线索的完整字段，附带最近 5 条跟进记录与全部挂接文档的标题列表；文档正文与全部跟进用 list 类工具分页查看。',
    parameters: {
      lead_id: { type: 'string', required: true, description: '线索 id' },
    },
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: {
          lead: LEAD_REF_REQUIRED,
          demand_desc: { type: 'string' },
          budget_range: { type: 'string' },
          followups: {
            type: 'array',
            required: true,
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
            required: true,
            items: {
              type: 'object',
              additionalProperties: false,
              properties: {
                id: { type: 'string', required: true },
                title: { type: 'string', required: true },
              },
            },
          },
        },
      },
      render: (_args, value) => {
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
      },
    },
    presentCall: args => ({
      card: 'generic',
      title: '查看线索',
      rawInput: args.lead_id,
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      return deps.ledger.getLeadDetail(args.lead_id, operator)
    },
  })
}

/**
 * Build `customer_acquisition_lead_list`.
 * @param deps - ledger and permission seam.
 * @returns the tool definition.
 */
export function leadListTool(deps: LeadToolDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_lead_list',
    description: '按多维度筛选线索列表：状态、来源、行业、意向等级、标签、归属与时间范围，支持公司名/联系人关键词模糊搜索，按创建时间倒序分页。status 缺省只看 active；回收站传 status=recycled。',
    parameters: { ...LEAD_FILTER_PARAMETERS, ...PAGING_PARAMETERS },
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: {
          items: { type: 'array', required: true, items: LEAD_REF_SCHEMA },
          total: { type: 'integer', required: true },
        },
      },
      render: (_args, value) => [{
        type: 'text',
        text: value.items.length === 0
          ? `线索共 ${value.total} 条，当前页无记录。`
          : `线索共 ${value.total} 条，本页 ${value.items.length} 条：\n${value.items.map(renderLeadRef).join('\n')}`,
      }],
    },
    presentCall: args => ({
      card: 'generic',
      title: '筛选线索',
      rawInput: args.q ?? (args.status === undefined ? '' : `status=${args.status}`),
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      const { items, total } = deps.ledger.listLeads(pickDefined(args) as LeadListRequest, operator)
      return { items: items.map(toLeadRef), total }
    },
  })
}

/**
 * Build `customer_acquisition_lead_delete` (soft delete into the recycle bin).
 * @param deps - ledger and permission seam.
 * @returns the tool definition.
 */
export function leadDeleteTool(deps: LeadToolDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_lead_delete',
    description: '将线索移入回收站（软删除，status 置 recycled），不物理清除；可随时用 restore 恢复。',
    parameters: {
      lead_id: { type: 'string', required: true, description: '线索 id' },
    },
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: {
          lead_id: { type: 'string', required: true },
          status: { type: 'string', required: true },
        },
      },
      render: (_args, value) => [{
        type: 'text',
        text: `线索已移入回收站：${value.lead_id}（status=${value.status}）`,
      }],
    },
    presentCall: args => ({
      card: 'generic',
      title: '删除线索',
      rawInput: args.lead_id,
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      const lead = await deps.ledger.deleteLead(args.lead_id, operator, 'agent')
      return { lead_id: lead.id, status: lead.status }
    },
  })
}

/**
 * Build `customer_acquisition_lead_restore`.
 * @param deps - ledger and permission seam.
 * @returns the tool definition.
 */
export function leadRestoreTool(deps: LeadToolDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_lead_restore',
    description: '将回收站中的线索恢复为 active。',
    parameters: {
      lead_id: { type: 'string', required: true, description: '线索 id' },
    },
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: {
          lead_id: { type: 'string', required: true },
          status: { type: 'string', required: true },
        },
      },
      render: (_args, value) => [{
        type: 'text',
        text: `线索已恢复：${value.lead_id}（status=${value.status}）`,
      }],
    },
    presentCall: args => ({
      card: 'generic',
      title: '恢复线索',
      rawInput: args.lead_id,
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      const lead = await deps.ledger.restoreLead(args.lead_id, operator, 'agent')
      return { lead_id: lead.id, status: lead.status }
    },
  })
}

/**
 * Build `customer_acquisition_lead_purge` (physical delete; requires the global delete capability).
 * @param deps - ledger and permission seam.
 * @returns the tool definition.
 */
export function leadPurgeTool(deps: LeadToolDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_lead_purge',
    description: '物理删除一条回收站（recycled）状态的线索及其跟进、文档、打分、内容、SOP 任务等全部关联记录，不可恢复。需要全局删除权限（can_delete_any_lead）。',
    parameters: {
      lead_id: { type: 'string', required: true, description: '线索 id' },
    },
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: { purged: { type: 'boolean', required: true } },
      },
      render: (_args, value) => [{
        type: 'text',
        text: value.purged ? '线索及关联记录已物理删除。' : '未删除。',
      }],
    },
    presentCall: args => ({
      card: 'generic',
      title: '物理删除线索',
      rawInput: args.lead_id,
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      await deps.ledger.purgeLead(args.lead_id, operator, 'agent')
      return { purged: true }
    },
  })
}

/**
 * Build `customer_acquisition_lead_assign` (claim a pool lead).
 * @param deps - ledger and permission seam.
 * @returns the tool definition.
 */
export function leadAssignTool(deps: LeadToolDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_lead_assign',
    description: '把一条公海线索（无归属人）分配给指定操作者。线索已有归属人时拒绝，应改用 transfer。',
    parameters: {
      lead_id: { type: 'string', required: true, description: '公海线索 id' },
      owner_id: { type: 'string', required: true, description: '目标归属人 id' },
    },
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: {
          lead_id: { type: 'string', required: true },
          owner_id: { type: 'string', required: true },
        },
      },
      render: (_args, value) => [{
        type: 'text',
        text: `线索 ${value.lead_id} 已分配给 ${value.owner_id}。`,
      }],
    },
    presentCall: args => ({
      card: 'generic',
      title: '分配线索',
      rawInput: `${args.lead_id} → ${args.owner_id}`,
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      await deps.ledger.assignLead(args.lead_id, args.owner_id, operator, 'agent')
      return { lead_id: args.lead_id, owner_id: args.owner_id }
    },
  })
}

/**
 * Build `customer_acquisition_lead_transfer`.
 * @param deps - ledger and permission seam.
 * @returns the tool definition.
 */
export function leadTransferTool(deps: LeadToolDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_lead_transfer',
    description: '转移线索归属人。owner_id 省略表示释放到公海。',
    parameters: {
      lead_id: { type: 'string', required: true, description: '线索 id' },
      owner_id: { type: 'string', description: '目标归属人 id；省略 = 释放到公海' },
    },
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: {
          lead_id: { type: 'string', required: true },
          owner_id: { type: 'string', required: true, description: '空串表示公海' },
        },
      },
      render: (_args, value) => [{
        type: 'text',
        text: `线索 ${value.lead_id} 归属已变更为 ${value.owner_id === '' ? '公海' : value.owner_id}。`,
      }],
    },
    presentCall: args => ({
      card: 'generic',
      title: '转移线索',
      rawInput: `${args.lead_id} → ${args.owner_id ?? '公海'}`,
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      await deps.ledger.transferLead(args.lead_id, args.owner_id, operator, 'agent')
      return { lead_id: args.lead_id, owner_id: args.owner_id ?? '' }
    },
  })
}

/**
 * Build `customer_acquisition_lead_extract`.
 * @param deps - ledger and permission seam.
 * @returns the tool definition.
 */
export function leadExtractTool(deps: LeadToolDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_lead_extract',
    description: `从用户粘贴的一段文本（表单内容/聊天记录/邮件正文）中抽取线索字段：公司名、联系人、电话、邮箱、行业、规模、需求描述、预算、决策角色。仅解析用户本次提供的文本，不做任何网络采集或批量提取；只返回识别结果，不写库——确认后用 lead_create 落库。文本上限 ${EXTRACT_MAX_CHARS} 字符。`,
    parameters: {
      text: { type: 'string', required: true, description: `用户提供的原始文本，≤${EXTRACT_MAX_CHARS} 字符` },
      source_hint: { type: 'string', description: '来源提示（form/chat/email），辅助歧义消解' },
    },
    timeoutMs: 120_000,
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: {
          fields: {
            type: 'object',
            required: true,
            additionalProperties: false,
            properties: {
              company_name: { type: 'string' },
              contact_name: { type: 'string' },
              phone: { type: 'string' },
              email: { type: 'string' },
              industry: { type: 'string' },
              company_size: { type: 'string' },
              demand_desc: { type: 'string' },
              budget_range: { type: 'string' },
              decision_role: { type: 'string' },
            },
          },
          notes: { type: 'string', description: '抽取歧义与未识别字段的说明' },
        },
      },
      render: (_args, value) => {
        const lines = Object.entries(value.fields)
          .filter(([, fieldValue]) => fieldValue !== undefined)
          .map(([key, fieldValue]) => `- ${key}：${String(fieldValue)}`)
        const notes = value.notes === undefined ? [] : [`识别说明：${value.notes}`]
        return [{
          type: 'text',
          text: `抽取结果（未写库，确认后用 lead_create 落库）：\n${[...lines, ...notes].join('\n')}`,
        }]
      },
    },
    presentCall: args => ({
      card: 'generic',
      title: '抽取线索字段',
      rawInput: args.text.length > 60 ? `${args.text.slice(0, 60)}…` : args.text,
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      return deps.ledger.extractLeadFields(
        { text: args.text, ...(args.source_hint === undefined ? {} : { sourceHint: args.source_hint }) },
        deps.completion,
        operator,
        'agent',
      )
    },
  })
}

/**
 * Build `customer_acquisition_lead_export`.
 * @param deps - ledger and permission seam.
 * @returns the tool definition.
 */
export function leadExportTool(deps: LeadToolDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_lead_export',
    description: '按 lead_list 相同的筛选条件导出线索为 Markdown 表格或 CSV（含表头，电话/邮箱防公式注入）。仅导出文本，不发送。需要导出权限（can_export）。',
    parameters: {
      ...LEAD_FILTER_PARAMETERS,
      format: { type: 'string', required: true, enum: ['markdown', 'csv'], description: '导出格式' },
    },
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: {
          format: { type: 'string', required: true },
          count: { type: 'integer', required: true },
          content: { type: 'string', required: true },
        },
      },
      render: (_args, value) => [{
        type: 'text',
        text: `已导出 ${value.count} 条线索（${value.format}）：\n\n${value.content}`,
      }],
    },
    presentCall: args => ({
      card: 'generic',
      title: '导出线索',
      rawInput: args.format,
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      if (!operator.capabilities.can_export) {
        throw new Error('当前操作者没有导出权限（can_export）')
      }
      const { format, ...filter } = args
      const leads = await deps.ledger.exportLeads(pickDefined(filter) as LeadListRequest, operator, 'agent')
      return { format, count: leads.length, content: renderLeadExport(format, leads) }
    },
  })
}

/**
 * Build `customer_acquisition_lead_document_add`.
 * @param deps - ledger and permission seam.
 * @returns the tool definition.
 */
export function leadDocumentAddTool(deps: LeadToolDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_lead_document_add',
    description: '给线索挂接一份纯文本资料（客户资料、行业文档、往来摘要等），供打分与文案生成时注入上下文；单份上限 20000 字符。',
    parameters: {
      lead_id: { type: 'string', required: true, description: '线索 id' },
      title: { type: 'string', required: true, description: '资料标题' },
      content: { type: 'string', required: true, description: '资料正文（≤20000 字符）' },
    },
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: {
          document: {
            type: 'object',
            required: true,
            additionalProperties: false,
            properties: {
              id: { type: 'string', required: true },
              lead_id: { type: 'string', required: true },
              title: { type: 'string', required: true },
            },
          },
        },
      },
      render: (_args, value) => [{
        type: 'text',
        text: `已挂接资料「${value.document.title}」到线索 ${value.document.lead_id}（id ${value.document.id}）。`,
      }],
    },
    presentCall: args => ({
      card: 'generic',
      title: '挂接资料',
      rawInput: args.title,
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      const document = await deps.ledger.addDocument(args.lead_id, args.title, args.content, operator, 'agent')
      return { document: { id: document.id, lead_id: document.lead_id, title: document.title } }
    },
  })
}

/**
 * Build `customer_acquisition_lead_document_list`.
 * @param deps - ledger and permission seam.
 * @returns the tool definition.
 */
export function leadDocumentListTool(deps: LeadToolDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_lead_document_list',
    description: '列出一个线索挂接的全部文档；默认只回标题与字数，传 include_content 时返回正文。',
    parameters: {
      lead_id: { type: 'string', required: true, description: '线索 id' },
      include_content: { type: 'boolean', description: '默认 false' },
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
                title: { type: 'string', required: true },
                char_count: { type: 'integer', required: true },
                content: { type: 'string' },
              },
            },
          },
        },
      },
      render: (_args, value) => [{
        type: 'text',
        text: value.items.length === 0
          ? '该线索暂无挂接资料。'
          : `挂接资料 ${value.items.length} 份：\n${value.items.map(document => `- ${document.title}（${document.char_count} 字符，id ${document.id}）`).join('\n')}`,
      }],
    },
    presentCall: args => ({
      card: 'generic',
      title: '查看挂接资料',
      rawInput: args.lead_id,
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      return { items: deps.ledger.listDocuments(args.lead_id, operator, args.include_content === true) }
    },
  })
}

/**
 * Build `customer_acquisition_lead_document_remove`.
 * @param deps - ledger and permission seam.
 * @returns the tool definition.
 */
export function leadDocumentRemoveTool(deps: LeadToolDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_lead_document_remove',
    description: '从线索上移除一份挂接文档（物理删除该文档记录）。',
    parameters: {
      document_id: { type: 'string', required: true, description: '文档 id' },
    },
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: { removed: { type: 'boolean', required: true } },
      },
      render: (_args, value) => [{
        type: 'text',
        text: value.removed ? '挂接资料已移除。' : '未移除。',
      }],
    },
    presentCall: args => ({
      card: 'generic',
      title: '移除挂接资料',
      rawInput: args.document_id,
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      await deps.ledger.removeDocument(args.document_id, operator, 'agent')
      return { removed: true }
    },
  })
}

/**
 * Build `customer_acquisition_lead_followup_add`.
 * @param deps - ledger and permission seam.
 * @returns the tool definition.
 */
export function leadFollowupAddTool(deps: LeadToolDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_lead_followup_add',
    description: '为线索追加一条跟进记录（内容为本次沟通摘要/结论）。',
    parameters: {
      lead_id: { type: 'string', required: true, description: '线索 id' },
      content: { type: 'string', required: true, description: '跟进内容' },
    },
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: {
          followup: {
            type: 'object',
            required: true,
            additionalProperties: false,
            properties: {
              id: { type: 'string', required: true },
              lead_id: { type: 'string', required: true },
              created_at: { type: 'integer', required: true },
            },
          },
        },
      },
      render: (args, value) => [{
        type: 'text',
        text: `已新增跟进记录（id ${value.followup.id}）：${args.content}`,
      }],
    },
    presentCall: args => ({
      card: 'generic',
      title: '新增跟进记录',
      rawInput: args.lead_id,
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      const followup = await deps.ledger.addFollowup(args.lead_id, args.content, operator, 'agent')
      return { followup: { id: followup.id, lead_id: followup.lead_id, created_at: followup.created_at } }
    },
  })
}

/**
 * Build `customer_acquisition_lead_followup_list`.
 * @param deps - ledger and permission seam.
 * @returns the tool definition.
 */
export function leadFollowupListTool(deps: LeadToolDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_lead_followup_list',
    description: '分页查看一个线索的全部跟进记录，按时间倒序。',
    parameters: {
      lead_id: { type: 'string', required: true, description: '线索 id' },
      ...PAGING_PARAMETERS,
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
                content: { type: 'string', required: true },
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
          ? `跟进记录共 ${value.total} 条，当前页无记录。`
          : `跟进记录共 ${value.total} 条，本页 ${value.items.length} 条：\n${value.items
            .map(followup => `- ${new Date(followup.created_at).toISOString()} ${followup.content}`)
            .join('\n')}`,
      }],
    },
    presentCall: args => ({
      card: 'generic',
      title: '查看跟进记录',
      rawInput: args.lead_id,
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      const { lead_id: leadId, limit, offset } = args
      return deps.ledger.listFollowups(leadId, operator, limit, offset)
    },
  })
}
