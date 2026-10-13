/**
 * The `stock-screener` skill. The skill is prompt-only — natural-language
 * routing is the model's job, not the plugin's. The skill body teaches the
 * model how to translate Chinese-language screening descriptions into the
 * structured parameters `a_share_screen` expects.
 *
 * @module @deepseek-ai/dsh-a-share-screener/skill
 */

import type { Context } from '@deepseek-ai/cordis'

export function registerStockScreenerSkill(ctx: Context): void {
  ctx.skills.register({
    name: 'stock-screener',
    description:
      'Translate Chinese-language A-share screening requests into structured arguments for the `a_share_screen` tool. Use when the user asks for stocks filtered by technical or fundamental criteria without naming a strategy id.',
    source: 'runtime',
    modelInvocable: true,
    userInvocable: false,
    content: [
      '你是 A 股量化筛选助手。优先调用 `a_share_list_strategies` 列出可用策略；',
      '若用户的描述能映射到某个策略 id（low-flat-limit-up / oversold-rebound / momentum-breakout / value-play），',
      '用该策略 id 作为 `strategy`，并把用户的限定条件以 `universe` 与 `overrides` 形式传入。',
      '',
      '通用字段映射：',
      '- `universe.kind = "hot"` + `size = N` —— "成交额前 N 名"',
      '- `universe.kind = "symbols"` + `symbols = [...]` —— 用户点名的股票池',
      '- `limit` —— 用户期望的返回数量，默认 30，上限 200',
      '',
      '务必在调用前用一句话复述你的翻译结论；调用后用 `ctx.jobs.read` 轮询作业，',
      '作业完成后用 evidence 字段给用户解释为何命中。',
    ].join('\n'),
  })
}
