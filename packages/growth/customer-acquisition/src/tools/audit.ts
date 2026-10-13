/**
 * P0 model-facing tools: `customer_acquisition_audit_list` and
 * `customer_acquisition_audit_export` (red line 6: the audit log is
 * queryable and exportable from the agent surface too). Export is text-only;
 * the plugin has no send channel (red line 3).
 * @module @deepseek-ai/dsh-customer-acquisition/tools/audit
 */

import { defineTool } from '@deepseek-ai/dsh-tools'
import type { ToolDefinition } from '@deepseek-ai/dsh-tools'
import { operatorRequest } from '../permission/types.ts'
import type { PermissionContextService } from '../permission/types.ts'
import type { CustomerAcquisitionService } from '../service.ts'
import type { AuditListRequest, AuditListValue, AuditLogValue } from '../types.ts'

/** Per-row projection schema shared by list and export. */
const AUDIT_ROW_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    id: { type: 'string', required: true },
    source: { type: 'string', required: true },
    operator_user_id: { type: 'string', required: true },
    action: { type: 'string', required: true },
    object_type: { type: 'string', required: true },
    object_id: { type: 'string' },
    summary: { type: 'string', required: true },
    created_at: { type: 'integer', required: true },
  },
} as const

/** Filter parameters shared by list and export. */
const FILTER_PARAMETERS = {
  source: { type: 'string', enum: ['web', 'agent', 'acp'], description: '操作来源过滤' },
  operator_user_id: { type: 'string', description: '按操作者过滤' },
  action_prefix: { type: 'string', description: '按动作前缀过滤，如 lead. / geo. / settings.' },
  object_type: { type: 'string', description: '按对象类型过滤，如 lead / score_run / settings' },
  from: { type: 'integer', description: '起始时间（epoch 毫秒，含）' },
  to: { type: 'integer', description: '结束时间（epoch 毫秒，含）' },
  limit: { type: 'integer', description: '每页条数，默认 20，最大 100；越界值自动收敛到该范围' },
  offset: { type: 'integer', description: '偏移量，默认 0；负值按 0 处理' },
} as const

/** Normalize and clamp the paging bounds. */
function pagingOf(request: AuditListRequest): { offset: number; limit: number } {
  return {
    offset: Math.max(request.offset ?? 0, 0),
    limit: Math.min(Math.max(request.limit ?? 20, 1), 100),
  }
}

/** Render one audit row as a human-readable line. */
function renderRow(record: AuditLogValue): string {
  const time = new Date(record.created_at).toISOString()
  const object = record.object_id === undefined
    ? record.object_type
    : `${record.object_type}:${record.object_id}`
  return `- [${time}] ${record.source}/${record.operator_user_id} ${record.action} ${object} — ${record.summary}`
}

/**
 * Build the audit list tool.
 * @param service - the customer-acquisition service.
 * @returns the tool definition.
 */
export function auditListTool(service: CustomerAcquisitionService): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_audit_list',
    description: '查询获客运营插件的操作审计日志。可按来源（web/agent/acp）、操作者、动作前缀、对象类型与时间范围过滤，按时间倒序分页返回。',
    parameters: FILTER_PARAMETERS,
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: {
          items: { type: 'array', required: true, items: AUDIT_ROW_SCHEMA },
          total: { type: 'integer', required: true },
        },
      },
      render: (_args, value: AuditListValue) => [{
        type: 'text',
        text: value.items.length === 0
          ? `审计日志共 ${value.total} 条，当前页无记录。`
          : `审计日志共 ${value.total} 条，本页 ${value.items.length} 条：\n${value.items.map(renderRow).join('\n')}`,
      }],
    },
    execute(args) {
      const request: AuditListRequest = { ...args }
      const { offset, limit } = pagingOf(request)
      const result = service.listAudit({ ...request, offset, limit })
      return Promise.resolve({ items: result.items, total: result.total })
    },
  })
}

/**
 * Escape one CSV cell against formula injection (red line: export safety).
 * @param cell - raw cell text.
 * @returns the safe quoted cell.
 */
function csvCell(cell: string): string {
  const guarded = /^[=+\-@\t]/.test(cell) ? `'${cell}` : cell
  return `"${guarded.replaceAll('"', '""')}"`
}

const AUDIT_CSV_COLUMNS = ['id', 'source', 'operator_user_id', 'action', 'object_type', 'object_id', 'summary', 'created_at'] as const

/**
 * Render audit rows as a Markdown table or a formula-guarded CSV document.
 * @param format - the requested format.
 * @param records - the rows in presentation order.
 * @returns the full export document text.
 */
export function renderAuditExport(format: 'markdown' | 'csv', records: readonly AuditLogValue[]): string {
  if (format === 'csv') {
    const rows = records.map(record => AUDIT_CSV_COLUMNS
      .map(column => csvCell(String(record[column] ?? '')))
      .join(','))
    return [AUDIT_CSV_COLUMNS.join(','), ...rows].join('\n')
  }
  const header = `| ${AUDIT_CSV_COLUMNS.join(' | ')} |`
  const rule = `| ${AUDIT_CSV_COLUMNS.map(() => '---').join(' | ')} |`
  const rows = records.map(record => `| ${AUDIT_CSV_COLUMNS.map(column => String(record[column] ?? '')).join(' | ')} |`)
  return [header, rule, ...rows].join('\n')
}

/**
 * Build the audit export tool.
 * @param service - the customer-acquisition service.
 * @param permission - the permission seam; export requires `can_export`.
 * @returns the tool definition.
 */
export function auditExportTool(
  service: CustomerAcquisitionService,
  permission: PermissionContextService,
): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_audit_export',
    description: '按 customer_acquisition_audit_list 相同的过滤条件导出审计日志全文，支持 Markdown 表格与 CSV 两种格式；CSV 已做公式注入防护。仅导出文本，不发送。',
    parameters: {
      ...FILTER_PARAMETERS,
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
        text: `已导出 ${value.count} 条审计记录（${value.format}）：\n\n${value.content}`,
      }],
    },
    async execute(args, exec) {
      const operator = await permission.resolve(operatorRequest('agent', exec.agent?.id))
      if (!operator.capabilities.can_export) {
        throw new Error('当前操作者没有导出权限（can_export）')
      }
      const { format, ...filter } = args
      const records = service.exportAudit(filter)
      return { format, count: records.length, content: renderAuditExport(format, records) }
    },
  })
}
