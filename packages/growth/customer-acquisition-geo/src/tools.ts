/**
 * The four P2 GEO tools (tools manifest §4): `customer_acquisition_geo_scan`,
 * `_history`, `_report_get`, and `_compare`. Parameters use the harness
 * `ParameterSchemaSpec` DSL; the fetch boundary is enforced upstream by the
 * geo pre-execute gate and in the crawler — the tool bodies only project
 * friendly errors.
 * @module @deepseek-ai/dsh-customer-acquisition-geo/tools
 */

import { defineTool } from '@deepseek-ai/dsh-tools'
import type { ToolDefinition } from '@deepseek-ai/dsh-tools'
import type { Context } from '@deepseek-ai/cordis'
import { operatorRequest } from './main-package.ts'
import type { PermissionContextService, ResolvedOperator } from './main-package.ts'
import type { GeoDiagnosisService } from './service.ts'

/** Resolve the calling agent's operator once per call (data contract §7). */
async function resolveOperator(permission: PermissionContextService, exec: { agent?: { id?: string } }): Promise<ResolvedOperator> {
  return permission.resolve(operatorRequest('agent', exec.agent?.id))
}

/** Generic call card, one per tool (manifest §1 convention). */
function card(title: string, detail: string) {
  return { card: 'generic' as const, title, detail }
}

/**
 * Build the scan tool.
 * @param service - the GEO diagnosis service.
 * @param permission - the permission seam backing per-call operator resolution.
 * @returns the tool definition.
 */
export function geoScanTool(service: GeoDiagnosisService, permission: PermissionContextService): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_geo_scan',
    description: '对用户显式提供的网站执行 GEO（生成式引擎优化）诊断并产出报告。合规边界：仅处理本次调用中用户显式给出的 URL；串行抓取（并发 1）、单页超时 10 秒、响应体上限 2MB、单次最多 20 页；抓取前检查 robots.txt，Disallow 路径跳过并记录；不自动发现新域名，不批量采集手机号/邮箱。输出：GEO 综合分（0-100）、短板发现清单、可部署的 llms.txt、FAQ/品牌知识素材、优化任务清单。',
    parameters: {
      url: { type: 'string', required: true, description: '用户显式提供的站点 URL（http/https）' },
      max_pages: { type: 'integer', description: '最多抓取页数，默认 10，上限 20 的整数；超出范围由合规校验拒绝' },
    },
    timeoutMs: 300_000,
    presentCall: args => card('GEO 诊断', `站点：${args.url}，页数上限：${args.max_pages ?? 10}`),
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: {
          scan_id: { type: 'string', required: true },
          score: { type: 'integer', required: true },
          findings_count: { type: 'integer', required: true },
          pages_fetched: { type: 'integer', required: true },
          robots_skipped_paths: { type: 'array', items: { type: 'string' } },
          llms_txt: { type: 'string', description: '可直接部署的 llms.txt；无可生成时为空串' },
          report_md: { type: 'string', required: true, description: '完整 Markdown 诊断报告' },
        },
      },
      render: (_args, value) => [{ type: 'text', text: value.report_md }],
    },
    async execute(args, exec) {
      const operator = await resolveOperator(permission, exec)
      return service.runScan({ url: args.url, ...(args.max_pages === undefined ? {} : { maxPages: args.max_pages }) }, operator)
    },
  })
}

/**
 * Build the history tool.
 * @param service - the GEO diagnosis service.
 * @returns the tool definition.
 */
export function geoHistoryTool(service: GeoDiagnosisService): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_geo_history',
    description: '查询历史 GEO 诊断记录（含每轮得分与状态），按开始时间倒序分页返回。',
    parameters: {
      url_filter: { type: 'string', description: '按 URL 前缀过滤' },
      from: { type: 'integer', description: '起始时间（epoch 毫秒，含）' },
      to: { type: 'integer', description: '结束时间（epoch 毫秒，含）' },
      limit: { type: 'integer', description: '每页条数，默认 20，最大 100' },
      offset: { type: 'integer', description: '偏移量，默认 0' },
    },
    presentCall: args => card('GEO 历史查询', args.url_filter === undefined ? '全部站点' : `前缀：${args.url_filter}`),
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
                scan_id: { type: 'string', required: true },
                report_id: { type: 'string', required: true },
                url: { type: 'string', required: true },
                status: { type: 'string', required: true },
                score: { type: 'integer', required: true },
                pages_fetched: { type: 'integer', required: true },
                started_at: { type: 'integer', required: true },
              },
            },
          },
          total: { type: 'integer', required: true, description: '过滤后的记录总数（不含分页截断）' },
        },
      },
      render: (_args, value) => [{
        type: 'text',
        text: value.items.length === 0
          ? '暂无 GEO 诊断记录。'
          : `共 ${value.total} 条 GEO 诊断记录：\n${value.items.map(item => `- ${item.url}：${item.score} 分（${item.status}，${new Date(item.started_at).toISOString()}）`).join('\n')}`,
      }],
    },
    execute(args) {
      return Promise.resolve(service.listHistory(args))
    },
  })
}

/**
 * Build the report-read tool.
 * @param service - the GEO diagnosis service.
 * @returns the tool definition.
 */
export function geoReportGetTool(service: GeoDiagnosisService): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_geo_report_get',
    description: '按报告 id 读取一轮 GEO 诊断的完整报告：综合分、全部发现项、llms.txt 产物、FAQ/品牌素材、优化任务清单与 Markdown 报告原文。',
    parameters: { report_id: { type: 'string', required: true, description: '报告 id' } },
    presentCall: args => card('GEO 报告详情', `报告：${args.report_id}`),
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: {
          report: {
            type: 'object',
            required: true,
            additionalProperties: false,
            properties: {
              id: { type: 'string', required: true },
              scan_id: { type: 'string', required: true },
              url: { type: 'string', required: true },
              score: { type: 'integer', required: true },
              findings: {
                type: 'array',
                required: true,
                items: {
                  type: 'object',
                  additionalProperties: false,
                  properties: {
                    id: { type: 'string', required: true },
                    category: { type: 'string', required: true },
                    severity: { type: 'string', required: true },
                    title: { type: 'string', required: true },
                    detail: { type: 'string', required: true },
                    evidence_page: { type: 'string' },
                  },
                },
              },
              llms_txt: { type: 'string' },
              report_md: { type: 'string', required: true },
              robots_skipped_paths: { type: 'array', required: true, items: { type: 'string' } },
              created_at: { type: 'integer', required: true },
            },
          },
        },
      },
      render: (_args, value) => [{ type: 'text', text: value.report.report_md }],
    },
    execute(args) {
      return Promise.resolve(service.getReport(args.report_id))
    },
  })
}

/**
 * Build the two-report comparison tool.
 * @param service - the GEO diagnosis service.
 * @returns the tool definition.
 */
export function geoCompareTool(service: GeoDiagnosisService): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_geo_compare',
    description: '对比两轮 GEO 诊断报告：总分变化、已解决与新增的短板、逐项差异摘要。两份报告须来自同一站点。',
    parameters: {
      report_a_id: { type: 'string', required: true, description: '基线报告 id' },
      report_b_id: { type: 'string', required: true, description: '对比报告 id' },
    },
    presentCall: args => card('GEO 报告对比', `${args.report_a_id} vs ${args.report_b_id}`),
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: {
          score_a: { type: 'integer', required: true },
          score_b: { type: 'integer', required: true },
          score_delta: { type: 'integer', required: true },
          resolved: { type: 'array', items: { type: 'string' } },
          introduced: { type: 'array', items: { type: 'string' } },
          summary_md: { type: 'string', required: true },
        },
      },
      render: (_args, value) => [{ type: 'text', text: value.summary_md }],
    },
    execute(args) {
      return Promise.resolve(service.compareReports(args.report_a_id, args.report_b_id))
    },
  })
}

/**
 * Register the four GEO tools.
 * @param ctx - the runtime fiber's context carrying `ctx.tools`.
 * @param service - the GEO diagnosis service.
 * @param permission - the permission seam backing per-call operator resolution.
 * @returns the combined disposer of every registration.
 */
export function registerGeoTools(
  ctx: Context,
  service: GeoDiagnosisService,
  permission: PermissionContextService,
): () => void {
  const disposers = [
    ctx.tools.register(geoScanTool(service, permission)),
    ctx.tools.register(geoHistoryTool(service)),
    ctx.tools.register(geoReportGetTool(service)),
    ctx.tools.register(geoCompareTool(service)),
  ]
  return () => { for (const dispose of disposers) dispose() }
}
