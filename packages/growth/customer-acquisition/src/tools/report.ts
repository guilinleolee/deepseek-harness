/**
 * Module-6 model-facing tool (tools manifest §9): the data-dashboard
 * overview. One aggregation service feeds both this tool and the browser
 * panel's Remote face; the render is the metric table the agent can quote.
 * @module @deepseek-ai/dsh-customer-acquisition/tools/report
 */

import { defineTool } from '@deepseek-ai/dsh-tools'
import type { ToolDefinition } from '@deepseek-ai/dsh-tools'
import { operatorRequest } from '../permission/types.ts'
import type { PermissionContextService } from '../permission/types.ts'
import type { ReportService } from '../report/service.ts'
import type { OverviewValue } from '../types.ts'

/** Dependencies the overview tool shares. */
export interface ReportToolDeps {
  readonly report: ReportService
  readonly permission: PermissionContextService
}

/**
 * Build `customer_acquisition_report_overview`.
 * @param deps - report aggregation service and permission seam.
 * @returns the tool definition.
 */
export function reportOverviewTool(deps: ReportToolDeps): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_report_overview',
    description: '汇总获客数据看板七项指标：线索总量、区间新增趋势、意向分布、来源分布、打分分数分布、SOP 任务完成率、GEO 诊断统计（诊断轮次与平均分）。支持日/周/月/自定义区间与按行业、来源下钻。',
    parameters: {
      period: { type: 'string', required: true, enum: ['today', 'week', 'month', 'custom'], description: '统计区间；today=今天零点起，week=近 7 天，month=近 30 天，custom=用 from/to' },
      from: { type: 'integer', description: '自定义区间起（epoch 毫秒）；period=custom 时必填' },
      to: { type: 'integer', description: '自定义区间止（epoch 毫秒）；period=custom 时必填' },
      group_by: { type: 'string', enum: ['none', 'industry', 'source'], description: '下钻维度，默认 none' },
    },
    presentCall: args => ({
      card: 'generic',
      title: '获客数据看板',
      rawInput: `${args.period}${args.group_by === undefined ? '' : ` / ${args.group_by}`}`,
    }),
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: {
          totals: {
            type: 'object',
            required: true,
            additionalProperties: false,
            properties: {
              lead_count: { type: 'integer', required: true },
              new_in_period: { type: 'integer', required: true },
              intent_distribution: {
                type: 'object',
                required: true,
                additionalProperties: false,
                properties: {
                  high: { type: 'integer', required: true },
                  mid: { type: 'integer', required: true },
                  low: { type: 'integer', required: true },
                  invalid: { type: 'integer', required: true },
                },
              },
              source_distribution: { type: 'object', required: true, additionalProperties: true, description: '{ <来源>: 线索数 }' },
              score_distribution: {
                type: 'object',
                required: true,
                additionalProperties: false,
                properties: {
                  '0-59': { type: 'integer', required: true },
                  '60-74': { type: 'integer', required: true },
                  '75-89': { type: 'integer', required: true },
                  '90-100': { type: 'integer', required: true },
                },
              },
              tasks: {
                type: 'object',
                required: true,
                additionalProperties: false,
                properties: {
                  total: { type: 'integer', required: true },
                  done: { type: 'integer', required: true },
                  deferred: { type: 'integer', required: true },
                  dropped: { type: 'integer', required: true },
                  completion_rate: { type: 'number', required: true },
                },
              },
              geo: {
                type: 'object',
                required: true,
                additionalProperties: false,
                properties: {
                  scan_count: { type: 'integer', required: true },
                  avg_score: { type: 'integer', required: true },
                  last_score: { type: 'integer' },
                },
              },
            },
          },
          breakdown: { type: 'json', description: 'group_by 时的分组明细；group_by=none 时为 null' },
        },
      },
      render: (_args, value) => [{ type: 'text', text: renderOverviewMd(value as OverviewValue) }],
    },
    async execute(args, exec) {
      const operator = await deps.permission.resolve(operatorRequest('agent', exec.agent?.id))
      return deps.report.overview({
        period: args.period,
        ...(args.from === undefined ? {} : { from: args.from }),
        ...(args.to === undefined ? {} : { to: args.to }),
        ...(args.group_by === undefined ? {} : { group_by: args.group_by }),
      }, operator)
    },
  })
}

/**
 * Render the overview as the metric table the agent can quote directly.
 * @param value - the aggregation output.
 * @returns the Markdown report.
 */
export function renderOverviewMd(value: OverviewValue): string {
  const t = value.totals
  const lines = [
    '# 获客数据看板',
    '',
    `- 线索总量：${t.lead_count}（区间新增 ${t.new_in_period}）`,
    `- 意向分布：高 ${t.intent_distribution.high} / 中 ${t.intent_distribution.mid} / 低 ${t.intent_distribution.low} / 无效 ${t.intent_distribution.invalid}`,
    `- 来源分布：${Object.entries(t.source_distribution).map(([source, count]) => `${source} ${count}`).join('、') || '（无）'}`,
    `- 打分分布：${SCORE_BUCKET_ORDER.map(bucket => `${bucket} ${t.score_distribution[bucket]}`).join('，')}`,
    `- SOP 任务：共 ${t.tasks.total}，完成 ${t.tasks.done}，延后 ${t.tasks.deferred}，放弃 ${t.tasks.dropped}（完成率 ${Math.round(t.tasks.completion_rate * 100)}%）`,
    `- GEO 诊断：${t.geo.scan_count} 轮，平均 ${t.geo.avg_score} 分${t.geo.last_score === undefined ? '' : `，最近 ${t.geo.last_score} 分`}`,
  ]
  if (value.breakdown !== null) {
    lines.push('', '| 分组 | 线索数 | 区间新增 | 高/中/低/无效 |', '|---|---|---|---|')
    for (const group of value.breakdown) {
      lines.push(`| ${group.key} | ${group.lead_count} | ${group.new_in_period} | ${group.intent_distribution.high}/${group.intent_distribution.mid}/${group.intent_distribution.low}/${group.intent_distribution.invalid} |`)
    }
  }
  return lines.join('\n')
}

/** Bucket key order for the render line. */
const SCORE_BUCKET_ORDER = ['0-59', '60-74', '75-89', '90-100'] as const
