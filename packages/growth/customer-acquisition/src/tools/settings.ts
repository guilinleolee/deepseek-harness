/**
 * P0 model-facing tools: `customer_acquisition_settings_get` (the smoke tool)
 * and `customer_acquisition_settings_set`. Parameters use the harness
 * `ParameterSchemaSpec` DSL; the compliance caps are also enforced upstream
 * by the pre-execute gate (defense in depth, not duplication of ownership —
 * the gate owns red-line enforcement).
 * @module @deepseek-ai/dsh-customer-acquisition/tools/settings
 */

import { defineTool } from '@deepseek-ai/dsh-tools'
import type { ToolDefinition } from '@deepseek-ai/dsh-tools'
import { operatorRequest } from '../permission/types.ts'
import type { PermissionContextService } from '../permission/types.ts'
import type { CustomerAcquisitionService } from '../service.ts'
import type { SettingsPatchInput, SettingsSnapshotValue } from '../types.ts'

/** Output schema shared by get and set: the full settings snapshot. */
const SETTINGS_VALUE_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    settings: {
      type: 'object',
      required: true,
      additionalProperties: false,
      properties: {
        default_icp_profile_id: { type: 'string' },
        default_score_template_id: { type: 'string' },
        geo_max_pages: { type: 'integer', required: true },
        geo_page_timeout_ms: { type: 'integer', required: true },
        sop_todo_write_enabled: { type: 'boolean', required: true },
      },
    },
  },
} as const

/** Render the settings snapshot as one line per field. */
function renderSettings(value: SettingsSnapshotValue): { type: 'text'; text: string }[] {
  const s = value.settings
  const lines = [
    `- geo_max_pages: ${s.geo_max_pages}`,
    `- geo_page_timeout_ms: ${s.geo_page_timeout_ms}`,
    `- sop_todo_write_enabled: ${String(s.sop_todo_write_enabled)}`,
    `- default_icp_profile_id: ${s.default_icp_profile_id ?? '(未设置)'}`,
    `- default_score_template_id: ${s.default_score_template_id ?? '(未设置)'}`,
  ]
  return [{ type: 'text', text: `获客运营全局参数：\n${lines.join('\n')}` }]
}

/**
 * Build the settings-read tool (the P0 smoke tool).
 * @param service - the customer-acquisition service.
 * @returns the tool definition.
 */
export function settingsGetTool(service: CustomerAcquisitionService): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_settings_get',
    description: '读取获客运营插件的全局参数：默认 ICP 画像、默认打分模板、GEO 诊断的页数与超时上限、SOP 待办联动开关。',
    parameters: {},
    output: {
      schema: SETTINGS_VALUE_SCHEMA,
      render: (_args, value) => renderSettings(value),
    },
    execute() {
      return Promise.resolve({ settings: service.getSettings() })
    },
  })
}

/**
 * Build the settings-write tool.
 * @param service - the customer-acquisition service.
 * @param permission - the permission seam; the write requires `can_manage_settings`.
 * @returns the tool definition.
 */
export function settingsSetTool(
  service: CustomerAcquisitionService,
  permission: PermissionContextService,
): ToolDefinition {
  return defineTool({
    name: 'customer_acquisition_settings_set',
    description: '修改获客运营插件的全局参数。只更新传入的字段，其余保持不变；页数上限不超过 20、单页超时不超过 10 秒（合规硬上限，配置只允许更保守）。引用的画像或模板 id 必须已存在。',
    parameters: {
      default_icp_profile_id: { type: 'string', description: '默认 ICP 画像 id；需为已存在的画像' },
      default_score_template_id: { type: 'string', description: '默认打分模板 id；需为已存在的模板' },
      geo_max_pages: { type: 'integer', description: 'GEO 单次诊断页数上限，1-20 的整数；超出范围的值由合规校验拒绝' },
      geo_page_timeout_ms: { type: 'integer', description: 'GEO 单页抓取超时毫秒数，1000-10000 的整数；超出范围的值由合规校验拒绝' },
      sop_todo_write_enabled: { type: 'boolean', description: 'SOP 生成任务时是否同步写入 DSH 待办' },
    },
    output: {
      schema: SETTINGS_VALUE_SCHEMA,
      render: (_args, value) => renderSettings(value),
    },
    async execute(args, exec) {
      const operator = await permission.resolve(operatorRequest('agent', exec.agent?.id))
      if (!operator.capabilities.can_manage_settings) {
        throw new Error('当前操作者没有修改全局参数的权限（can_manage_settings）')
      }
      const patch: SettingsPatchInput = {
        ...(args.default_icp_profile_id === undefined ? {} : { default_icp_profile_id: args.default_icp_profile_id }),
        ...(args.default_score_template_id === undefined ? {} : { default_score_template_id: args.default_score_template_id }),
        ...(args.geo_max_pages === undefined ? {} : { geo_max_pages: args.geo_max_pages }),
        ...(args.geo_page_timeout_ms === undefined ? {} : { geo_page_timeout_ms: args.geo_page_timeout_ms }),
        ...(args.sop_todo_write_enabled === undefined ? {} : { sop_todo_write_enabled: args.sop_todo_write_enabled }),
      }
      return { settings: await service.updateSettings(patch, operator, 'agent') }
    },
  })
}
