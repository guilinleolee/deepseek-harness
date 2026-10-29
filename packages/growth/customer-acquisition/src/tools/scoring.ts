/**
 * Module-3 model-facing tools (tools manifest §6): the AI scoring flows and
 * the ICP profile / scoring template CRUD. Every execute resolves the
 * operator per call; template writes gate on `can_manage_global_templates`,
 * scoring scopes through the ledger, and the JSON model answer never reaches
 * the model unvalidated.
 * @module @deepseek-ai/dsh-customer-acquisition/tools/scoring
 */

import { defineTool } from '@deepseek-ai/dsh-tools'
import type { ToolDefinition } from '@deepseek-ai/dsh-tools'
import type { LeadScoringService } from '../scoring/service.ts'
import { toIcpProfileRef, toScoreTemplateRef } from '../scoring/service.ts'
import { INTENT_LABELS } from '../scoring/evaluate.ts'
import type { ScoreBatchValue, ScoreHistoryValue, ScoreOneValue } from '../scoring/types.ts'
import { operatorRequest } from '../permission/types.ts'
import type { PermissionContextService } from '../permission/types.ts'

/** Dependencies every scoring tool shares. */
export interface ScoringToolDeps {
  readonly scoring: LeadScoringService
  readonly permission: PermissionContextService
}

/** The ICP dimension item schema shared by icp_create/icp_update parameters and the manage face. */
export const ICP_DIMENSION_PARAMETER_ITEM = {
  type: 'object',
  additionalProperties: false,
  properties: {
    id: { type: 'string', required: true, description: '维度标识，画像内唯一，如 budget_scale' },
    name: { type: 'string', required: true, description: '维度名称' },
    description: { type: 'string', required: true, description: '维度评分说明（模型打分依据）' },
    weight: { type: 'number', required: true, description: '权重 0-100，全部维度合计必须为 100' },
  },
} as const

/** Render one score_one value: headline, overall reason, and per-dimension lines. */
function renderScoreOne(value: ScoreOneValue): string {
  const lines = [
    `打分完成：总分 ${value.run.total}（${INTENT_LABELS[value.run.intent_tag]}），run id ${value.run.id}`,
    `整体理由：${value.run.reason}`,
    '分项得分：',
    ...value.items.map(item =>
      `- ${item.name}（权重 ${item.weight}%）：${item.score} 分 — ${item.reason}`),
  ]
  return lines.join('\n')
}

/**
 * Build `customer_acquisition_score_one`.
 * @param deps - scoring service and permission seam.
 * @returns the tool definition.
 */
export function scoreOneTool(deps: ScoringToolDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_score_one',
    description: '按选定的 ICP 画像与打分模板对一条线索做 AI 打分：输出总分（0-100）、逐维度得分与理由，并自动回填意向标签（high/mid/low/invalid）。画像与模板省略时依次取：全局默认 → 按线索行业匹配 → 启用中的任一套。线索挂接的资料会按上限注入上下文。',
    parameters: {
      lead_id: { type: 'string', required: true, description: '线索 id' },
      icp_profile_id: { type: 'string', description: 'ICP 画像 id；省略走默认/行业匹配' },
      score_template_id: { type: 'string', description: '打分模板 id；省略走默认/行业匹配' },
    },
    timeoutMs: 120_000,
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: {
          run: {
            type: 'object',
            required: true,
            additionalProperties: false,
            properties: {
              id: { type: 'string', required: true },
              total: { type: 'number', required: true },
              intent_tag: { type: 'string', required: true },
              reason: { type: 'string', required: true },
            },
          },
          items: {
            type: 'array',
            required: true,
            items: {
              type: 'object',
              additionalProperties: false,
              properties: {
                dimension_id: { type: 'string', required: true },
                name: { type: 'string', required: true },
                score: { type: 'number', required: true },
                weight: { type: 'number', required: true },
                reason: { type: 'string', required: true },
              },
            },
          },
        },
      },
      render: (_args, value) => [{ type: 'text', text: renderScoreOne(value as ScoreOneValue) }],
    },
    presentCall: args => ({
      card: 'generic',
      title: 'AI 打分',
      rawInput: args.lead_id,
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      const { lead_id: leadId, icp_profile_id: icpProfileId, score_template_id: scoreTemplateId } = args
      return deps.scoring.scoreOne(
        {
          lead_id: leadId,
          ...(icpProfileId === undefined ? {} : { icp_profile_id: icpProfileId }),
          ...(scoreTemplateId === undefined ? {} : { score_template_id: scoreTemplateId }),
        },
        operator,
        'agent',
        exec.signal,
      )
    },
  })
}

/**
 * Build `customer_acquisition_score_batch`.
 * @param deps - scoring service and permission seam.
 * @returns the tool definition.
 */
export function scoreBatchTool(deps: ScoringToolDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_score_batch',
    description: '对最多 50 条线索逐条串行执行与 score_one 相同的 AI 打分并批量回填意向标签。单条失败不中断批次，失败清单随结果返回。',
    parameters: {
      lead_ids: { type: 'array', required: true, items: { type: 'string' }, description: '线索 id 列表，1-50 条，不可重复' },
      icp_profile_id: { type: 'string', description: 'ICP 画像 id；省略走默认/行业匹配' },
      score_template_id: { type: 'string', description: '打分模板 id；省略走默认/行业匹配' },
    },
    timeoutMs: 600_000,
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: {
          runs: {
            type: 'array',
            required: true,
            items: {
              type: 'object',
              additionalProperties: false,
              properties: {
                lead_id: { type: 'string', required: true },
                run_id: { type: 'string', required: true },
                total: { type: 'number', required: true },
                intent_tag: { type: 'string', required: true },
              },
            },
          },
          failed: {
            type: 'array',
            required: true,
            items: {
              type: 'object',
              additionalProperties: false,
              properties: {
                lead_id: { type: 'string', required: true },
                error: { type: 'string', required: true },
              },
            },
          },
        },
      },
      render: (_args, value) => {
        const batch = value as ScoreBatchValue
        const lines = [
          `批量打分完成：成功 ${batch.runs.length} 条，失败 ${batch.failed.length} 条。`,
          ...batch.runs.map(run => `- ${run.lead_id}：${run.total} 分（${INTENT_LABELS[run.intent_tag]}），run id ${run.run_id}`),
          ...batch.failed.map(entry => `- ${entry.lead_id}：失败 — ${entry.error}`),
        ]
        return [{ type: 'text', text: lines.join('\n') }]
      },
    },
    presentCall: args => ({
      card: 'generic',
      title: '批量 AI 打分',
      rawInput: `${args.lead_ids.length} 条线索`,
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      const { lead_ids: leadIds, icp_profile_id: icpProfileId, score_template_id: scoreTemplateId } = args
      return deps.scoring.scoreBatch(
        {
          lead_ids: leadIds,
          ...(icpProfileId === undefined ? {} : { icp_profile_id: icpProfileId }),
          ...(scoreTemplateId === undefined ? {} : { score_template_id: scoreTemplateId }),
        },
        operator,
        'agent',
        exec.signal,
      )
    },
  })
}

/**
 * Build `customer_acquisition_score_history`.
 * @param deps - scoring service and permission seam.
 * @returns the tool definition.
 */
export function scoreHistoryTool(deps: ScoringToolDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_score_history',
    description: '回溯打分历史：按线索列出每次打分的总分、意向标签、整体理由与逐维度分项（含打分时的权重快照）。可按线索或单次 run 过滤，按时间倒序分页。',
    parameters: {
      lead_id: { type: 'string', description: '按线索过滤' },
      run_id: { type: 'string', description: '按单次打分记录过滤' },
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
                run: {
                  type: 'object',
                  required: true,
                  additionalProperties: false,
                  properties: {
                    id: { type: 'string', required: true },
                    lead_id: { type: 'string', required: true },
                    total: { type: 'number', required: true },
                    intent_tag: { type: 'string', required: true },
                    reason: { type: 'string', required: true },
                    created_at: { type: 'integer', required: true },
                  },
                },
                items: {
                  type: 'array',
                  required: true,
                  items: {
                    type: 'object',
                    additionalProperties: false,
                    properties: {
                      dimension_id: { type: 'string', required: true },
                      score: { type: 'number', required: true },
                      weight: { type: 'number', required: true },
                      reason: { type: 'string', required: true },
                    },
                  },
                },
              },
            },
          },
          total: { type: 'integer', required: true },
        },
      },
      render: (_args, value) => {
        const history = value as ScoreHistoryValue
        return [{
          type: 'text',
          text: history.items.length === 0
            ? `打分历史共 ${history.total} 条，当前页无记录。`
            : `打分历史共 ${history.total} 条，本页 ${history.items.length} 条：\n${history.items.map((entry) => {
              const itemLines = entry.items
                .map(item => `  · ${item.dimension_id}（权重 ${item.weight}%）：${item.score} 分 — ${item.reason}`)
                .join('\n')
              return [
                `- ${new Date(entry.run.created_at).toISOString()} 线索 ${entry.run.lead_id}：${entry.run.total} 分（${INTENT_LABELS[entry.run.intent_tag]}），run id ${entry.run.id}`,
                `  整体理由：${entry.run.reason}`,
                itemLines,
              ].filter(part => part.length > 0).join('\n')
            }).join('\n')}`,
        }]
      },
    },
    presentCall: args => ({
      card: 'generic',
      title: '打分历史',
      rawInput: args.lead_id ?? args.run_id ?? '',
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      const { lead_id: leadId, run_id: runId, limit, offset } = args
      return deps.scoring.history({
        ...(leadId === undefined ? {} : { lead_id: leadId }),
        ...(runId === undefined ? {} : { run_id: runId }),
        ...(limit === undefined ? {} : { limit }),
        ...(offset === undefined ? {} : { offset }),
      }, operator)
    },
  })
}

/**
 * Build `customer_acquisition_icp_create`.
 * @param deps - scoring service and permission seam.
 * @returns the tool definition.
 */
export function icpCreateTool(deps: ScoringToolDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_icp_create',
    description: '新建一套 ICP 客户画像：若干评分维度及权重。权重必须合计为 100（±0.01），否则拒绝保存；维度 id 在画像内唯一。',
    parameters: {
      name: { type: 'string', required: true, description: '画像名称' },
      industry: { type: 'string', description: '适用行业；省略 = 通用' },
      dimensions: { type: 'array', required: true, items: ICP_DIMENSION_PARAMETER_ITEM, description: '评分维度列表，1-N 个' },
      enabled: { type: 'boolean', description: '默认 true' },
    },
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: {
          profile: {
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
        text: `已新建 ICP 画像：${(value).profile.name}（id ${(value).profile.id}，${(value).profile.enabled ? '启用中' : '已停用'}）`,
      }],
    },
    presentCall: args => ({
      card: 'generic',
      title: '新建 ICP 画像',
      rawInput: args.name,
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      const { name, industry, dimensions, enabled } = args
      const profile = await deps.scoring.createIcpProfile({
        name,
        ...(industry === undefined ? {} : { industry }),
        dimensions,
        ...(enabled === undefined ? {} : { enabled }),
      }, operator, 'agent')
      return { profile: toIcpProfileRef(profile) }
    },
  })
}

/**
 * Build `customer_acquisition_icp_update`.
 * @param deps - scoring service and permission seam.
 * @returns the tool definition.
 */
export function icpUpdateTool(deps: ScoringToolDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_icp_update',
    description: '修改 ICP 画像：名称、行业、启用状态，或整体替换维度列表（权重仍须合计 100）。历史打分不受影响（分项保存了当时的权重快照）。',
    parameters: {
      icp_profile_id: { type: 'string', required: true, description: '画像 id' },
      name: { type: 'string', description: '新名称' },
      industry: { type: 'string', description: '新行业' },
      enabled: { type: 'boolean', description: '启用状态' },
      dimensions: { type: 'array', items: ICP_DIMENSION_PARAMETER_ITEM, description: '整体替换维度列表' },
    },
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: {
          profile: {
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
        text: `已更新 ICP 画像：${(value).profile.name}（id ${(value).profile.id}，${(value).profile.enabled ? '启用中' : '已停用'}）`,
      }],
    },
    presentCall: args => ({
      card: 'generic',
      title: '修改 ICP 画像',
      rawInput: args.icp_profile_id,
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      const { icp_profile_id: profileId, name, industry, enabled, dimensions } = args
      const profile = await deps.scoring.updateIcpProfile(profileId, {
        ...(name === undefined ? {} : { name }),
        ...(industry === undefined ? {} : { industry }),
        ...(enabled === undefined ? {} : { enabled }),
        ...(dimensions === undefined ? {} : { dimensions }),
      }, operator, 'agent')
      return { profile: toIcpProfileRef(profile) }
    },
  })
}

/**
 * Build `customer_acquisition_icp_list`.
 * @param deps - scoring service and permission seam.
 * @returns the tool definition.
 */
export function icpListTool(deps: ScoringToolDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_icp_list',
    description: '列出全部 ICP 画像（含维度与权重、启用状态）。',
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
        },
      },
      render: (_args, value) => {
        const icps = value
        return [{
          type: 'text',
          text: icps.items.length === 0
            ? '尚无 ICP 画像。'
            : `ICP 画像 ${icps.items.length} 套：\n${icps.items.map((profile) => {
              const dims = profile.dimensions
                .map(dimension => `${dimension.id}（${dimension.weight}%）`)
                .join('、')
              return `- ${profile.name}（id ${profile.id}，${profile.industry ?? '通用'}，${profile.enabled ? '启用' : '停用'}）：${dims}`
            }).join('\n')}`,
        }]
      },
    },
    presentCall: () => ({
      card: 'generic',
      title: '查看 ICP 画像',
    }),
    async execute(args, exec) {
      await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      return { items: deps.scoring.listIcpProfiles(args.enabled_only === true) }
    },
  })
}

/**
 * Build `customer_acquisition_icp_delete`.
 * @param deps - scoring service and permission seam.
 * @returns the tool definition.
 */
export function icpDeleteTool(deps: ScoringToolDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_icp_delete',
    description: '删除一套 ICP 画像。已被打分历史引用时拒绝删除，提示改用 icp_update 停用（enabled=false）。',
    parameters: {
      icp_profile_id: { type: 'string', required: true, description: '画像 id' },
    },
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: { deleted: { type: 'boolean', required: true } },
      },
      render: (_args, value) => [{
        type: 'text',
        text: value.deleted ? 'ICP 画像已删除。' : '未删除。',
      }],
    },
    presentCall: args => ({
      card: 'generic',
      title: '删除 ICP 画像',
      rawInput: args.icp_profile_id,
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      await deps.scoring.deleteIcpProfile(args.icp_profile_id, operator, 'agent')
      return { deleted: true }
    },
  })
}

/**
 * Build `customer_acquisition_score_template_create`.
 * @param deps - scoring service and permission seam.
 * @returns the tool definition.
 */
export function scoreTemplateCreateTool(deps: ScoringToolDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_score_template_create',
    description: '新建打分提示词模板。prompt_text 支持 {{lead}}（线索 JSON）、{{icp_profile}}（画像）、{{dimensions}}（维度清单）、{{knowledge}}（线索资料注入）占位符。',
    parameters: {
      name: { type: 'string', required: true, description: '模板名称' },
      industry: { type: 'string', description: '适用行业；省略 = 通用' },
      prompt_text: { type: 'string', required: true, description: '提示词正文（支持四类占位符）' },
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
        text: `已新建打分模板：${(value).template.name}（id ${(value).template.id}，${(value).template.enabled ? '启用中' : '已停用'}）`,
      }],
    },
    presentCall: args => ({
      card: 'generic',
      title: '新建打分模板',
      rawInput: args.name,
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      const { name, industry, prompt_text: promptText, enabled } = args
      const template = await deps.scoring.createScoreTemplate({
        name,
        ...(industry === undefined ? {} : { industry }),
        prompt_text: promptText,
        ...(enabled === undefined ? {} : { enabled }),
      }, operator, 'agent')
      return { template: toScoreTemplateRef(template) }
    },
  })
}

/**
 * Build `customer_acquisition_score_template_update`.
 * @param deps - scoring service and permission seam.
 * @returns the tool definition.
 */
export function scoreTemplateUpdateTool(deps: ScoringToolDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_score_template_update',
    description: '修改打分模板：名称、行业、启用状态或提示词正文。被历史引用也可修改（历史分项保存了当时的权重快照，提示词变更只影响后续打分）。',
    parameters: {
      score_template_id: { type: 'string', required: true, description: '模板 id' },
      name: { type: 'string', description: '新名称' },
      industry: { type: 'string', description: '新行业' },
      prompt_text: { type: 'string', description: '新提示词正文' },
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
        text: `已更新打分模板：${(value).template.name}（id ${(value).template.id}，${(value).template.enabled ? '启用中' : '已停用'}）`,
      }],
    },
    presentCall: args => ({
      card: 'generic',
      title: '修改打分模板',
      rawInput: args.score_template_id,
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      const { score_template_id: templateId, name, industry, prompt_text: promptText, enabled } = args
      const template = await deps.scoring.updateScoreTemplate(templateId, {
        ...(name === undefined ? {} : { name }),
        ...(industry === undefined ? {} : { industry }),
        ...(promptText === undefined ? {} : { prompt_text: promptText }),
        ...(enabled === undefined ? {} : { enabled }),
      }, operator, 'agent')
      return { template: toScoreTemplateRef(template) }
    },
  })
}

/**
 * Build `customer_acquisition_score_template_list`.
 * @param deps - scoring service and permission seam.
 * @returns the tool definition.
 */
export function scoreTemplateListTool(deps: ScoringToolDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_score_template_list',
    description: '列出全部打分提示词模板（含提示词全文与启用状态）。',
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
                prompt_text: { type: 'string', required: true },
                enabled: { type: 'boolean', required: true },
              },
            },
          },
        },
      },
      render: (_args, value) => {
        const templates = value
        return [{
          type: 'text',
          text: templates.items.length === 0
            ? '尚无打分模板。'
            : `打分模板 ${templates.items.length} 套：\n${templates.items
              .map(template => `- ${template.name}（id ${template.id}，${template.industry ?? '通用'}，${template.enabled ? '启用' : '停用'}）`)
              .join('\n')}`,
        }]
      },
    },
    presentCall: () => ({
      card: 'generic',
      title: '查看打分模板',
    }),
    async execute(args, exec) {
      await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      return { items: deps.scoring.listScoreTemplates(args.enabled_only === true) }
    },
  })
}

/**
 * Build `customer_acquisition_score_template_delete`.
 * @param deps - scoring service and permission seam.
 * @returns the tool definition.
 */
export function scoreTemplateDeleteTool(deps: ScoringToolDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_score_template_delete',
    description: '删除一套打分模板。已被打分历史引用时拒绝删除，提示改用 score_template_update 停用（enabled=false）。',
    parameters: {
      score_template_id: { type: 'string', required: true, description: '模板 id' },
    },
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: { deleted: { type: 'boolean', required: true } },
      },
      render: (_args, value) => [{
        type: 'text',
        text: value.deleted ? '打分模板已删除。' : '未删除。',
      }],
    },
    presentCall: args => ({
      card: 'generic',
      title: '删除打分模板',
      rawInput: args.score_template_id,
    }),
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      await deps.scoring.deleteScoreTemplate(args.score_template_id, operator, 'agent')
      return { deleted: true }
    },
  })
}
