/** Locale dictionaries for the Trajectory Debug Workbench (zh/en). */

/** Dictionary namespace owned by this plugin (declared on the slot map). */
export const NS = 'trajectory-debug'

/** The trajectory-debug dictionary key set (source of truth for both locales). */
export type TrajectoryDebugKey =
  | 'view.tab'
  | 'waterfall.empty'
  | 'waterfall.steps'
  | 'waterfall.turn'
  | 'waterfall.step'
  | 'waterfall.tool'
  | 'waterfall.error'
  | 'waterfall.pending'
  | 'perf.title'
  | 'perf.steps'
  | 'perf.turns'
  | 'perf.tokens'
  | 'perf.llmMs'
  | 'perf.toolMs'
  | 'perf.toolCalls'
  | 'perf.failures'
  | 'perf.noData'
  | 'replay.title'
  | 'replay.pending'
  | 'session.unavailable'

declare module '@deepseek-ai/dsh-client-ui-slots' {
  interface LocaleNamespaceMap {
    /** The Debug view tab label and panel strings. */
    'trajectory-debug': TrajectoryDebugKey
  }
}

/** Simplified Chinese dictionary (the key-set source of truth). */
export const zh: Record<TrajectoryDebugKey, string> = {
  'view.tab': 'Debug',
  'waterfall.empty': '暂无轨迹数据',
  'waterfall.steps': '共 {{turns}} 轮 / {{steps}} 步',
  'waterfall.turn': '轮次',
  'waterfall.step': '步',
  'waterfall.tool': '工具',
  'waterfall.error': '错误',
  'waterfall.pending': '执行中',
  'perf.title': '性能分析',
  'perf.steps': '步数',
  'perf.turns': '轮次',
  'perf.tokens': 'Token',
  'perf.llmMs': '模型耗时',
  'perf.toolMs': '工具耗时',
  'perf.toolCalls': '工具调用',
  'perf.failures': '失败归类',
  'perf.noData': '暂无性能数据',
  'replay.title': '回放 / 对比 / 干预',
  'replay.pending': '此区域依赖 typert Remote 接线（M4）：确定性回放、断点、改参重跑、分叉对比将在此呈现。',
  'session.unavailable': '会话不可用',
}

/** English dictionary. */
export const en: Record<TrajectoryDebugKey, string> = {
  'view.tab': 'Debug',
  'waterfall.empty': 'No trajectory data yet',
  'waterfall.steps': '{{turns}} turns / {{steps}} steps',
  'waterfall.turn': 'turn',
  'waterfall.step': 'step',
  'waterfall.tool': 'tool',
  'waterfall.error': 'error',
  'waterfall.pending': 'running',
  'perf.title': 'Performance',
  'perf.steps': 'Steps',
  'perf.turns': 'Turns',
  'perf.tokens': 'Tokens',
  'perf.llmMs': 'LLM time',
  'perf.toolMs': 'Tool time',
  'perf.toolCalls': 'Tool calls',
  'perf.failures': 'Failures',
  'perf.noData': 'No performance data yet',
  'replay.title': 'Replay / Compare / Intervene',
  'replay.pending': 'This area depends on the typert Remote wiring (M4): deterministic replay, breakpoints, edit-and-rerun and fork compare will land here.',
  'session.unavailable': 'Session unavailable',
}
