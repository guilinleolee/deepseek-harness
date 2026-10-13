/**
 * Dictionary for the customer-acquisition panel (entry + placeholder
 * workbench). The zh object is the source of the key union; en must carry
 * every key.
 * @module @deepseek-ai/dsh-client-ui-customer-acquisition/client/locales
 */

/** Chinese copy; keys are the panel's locale key union. */
export const zh = {
  'entry.label': '获客运营',
  'entry.aria': '打开获客运营工作台',
  'panel.title': '获客运营',
  'panel.phase': 'P0 占位面板',
  'panel.intro': '数据契约与工具清单已冻结。本面板打通 dsh.client 声明、ui-slots 注册与 Remote 挂载全链路；八页完整面板随 P4 交付。',
  'panel.settings.title': '全局参数',
  'panel.settings.geoMaxPages': 'GEO 单次诊断页数上限',
  'panel.settings.geoTimeout': 'GEO 单页超时（毫秒）',
  'panel.settings.todo': 'SOP 待办联动',
  'panel.settings.defaultIcp': '默认 ICP 画像',
  'panel.settings.defaultScore': '默认打分模板',
  'panel.audit.title': '最近操作审计',
  'panel.audit.empty': '暂无审计记录。',
  'panel.load.failed': 'Remote 读取失败',
  'panel.close': '返回对话',
} as const

/** The panel's locale key union. */
export type AcquisitionKey = keyof typeof zh

/** English copy, key-complete against {@link zh}. */
export const en: Record<AcquisitionKey, string> = {
  'entry.label': 'Acquisition',
  'entry.aria': 'Open the customer-acquisition workbench',
  'panel.title': 'Customer Acquisition',
  'panel.phase': 'P0 placeholder panel',
  'panel.intro': 'The data contract and tool manifest are frozen. This panel wires the full chain — dsh.client declaration, ui-slots registration, and Remote mounting; the eight-page panel ships with P4.',
  'panel.settings.title': 'Global settings',
  'panel.settings.geoMaxPages': 'GEO max pages per scan',
  'panel.settings.geoTimeout': 'GEO per-page timeout (ms)',
  'panel.settings.todo': 'SOP todo integration',
  'panel.settings.defaultIcp': 'Default ICP profile',
  'panel.settings.defaultScore': 'Default scoring template',
  'panel.audit.title': 'Recent audit trail',
  'panel.audit.empty': 'No audit records yet.',
  'panel.load.failed': 'Remote read failed',
  'panel.close': 'Back to chat',
}
