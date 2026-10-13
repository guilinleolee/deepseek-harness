/**
 * Dictionary for the quant-research panel (entry + real surface). The zh
 * object is the source of the key union; en must carry every key.
 * @module @deepseek-ai/dsh-client-ui-quant-research/client/locales
 */

/** Chinese copy; keys are the panel's locale key union. */
export const zh = {
  'entry.label': '量化研究',
  'entry.aria': '打开量化研究面板',
  'panel.title': '量化研究',
  'panel.phase': '研究面板',
  'panel.intro': '虚拟账户与研究笔记的只读视图。所有调仓与研究动作经模型工具的人工审核流执行；本面板不构成投资建议，插件没有任何实盘通道。',
  'panel.accounts.title': '虚拟账户',
  'panel.accounts.empty': '暂无虚拟账户。用 quant_account_create 工具创建。',
  'panel.accounts.positions': '持仓',
  'panel.accounts.noPositions': '空仓',
  'panel.accounts.cash': '现金',
  'panel.accounts.equity': '总权益',
  'panel.accounts.weight': '占比',
  'panel.notes.title': '研究笔记',
  'panel.notes.empty': '暂无研究笔记。用 quant_save_note 工具保存。',
  'panel.load.failed': 'Remote 读取失败',
  'panel.retry': '重试',
  'panel.close': '返回对话',
} as const

/** The panel's locale key union. */
export type QuantKey = keyof typeof zh

/** English copy, key-complete against {@link zh}. */
export const en: Record<QuantKey, string> = {
  'entry.label': 'Quant Research',
  'entry.aria': 'Open the quant-research panel',
  'panel.title': 'Quant Research',
  'panel.phase': 'Research panel',
  'panel.intro': 'Read-only views of the virtual accounts and research notes. Every rebalance and research action runs through the model tools\' human-review flows; nothing here is investment advice, and the plugin has no live-trading channel.',
  'panel.accounts.title': 'Virtual accounts',
  'panel.accounts.empty': 'No virtual accounts yet. Create one with the quant_account_create tool.',
  'panel.accounts.positions': 'Positions',
  'panel.accounts.noPositions': 'No open positions',
  'panel.accounts.cash': 'Cash',
  'panel.accounts.equity': 'Equity',
  'panel.accounts.weight': 'Weight',
  'panel.notes.title': 'Research notes',
  'panel.notes.empty': 'No research notes yet. Save one with the quant_save_note tool.',
  'panel.load.failed': 'Remote read failed',
  'panel.retry': 'Retry',
  'panel.close': 'Back to chat',
}
