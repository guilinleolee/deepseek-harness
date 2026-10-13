/**
 * PCPT report generation: format backtest results as a structured markdown
 * research report, and compare two backtest runs side by side. Pure
 * functions — no I/O, no clock.
 * @module @deepseek-ai/dsh-quant-research/pcpt/report
 */

import type { BacktestReport, BacktestTrade } from './backtest.ts'

/**
 * Format one backtest report as a markdown research document.
 * @param report - the backtest report to format.
 * @param title - the report title.
 * @returns the markdown string.
 */
export function formatBacktestReport(report: BacktestReport, title: string): string {
  const m = report.metrics
  const pct = (v: number): string => `${(v * 100).toFixed(2)}%`
  const trades = report.trades.length > 0
    ? report.trades.map(t =>
        `| ${t.date} | ${t.side === 'buy' ? '买入' : '卖出'} | ${t.price.toFixed(2)} | ${t.shares.toFixed(2)} |`,
      ).join('\n')
    : '（无交易）'
  const tradeHeader = '| 日期 | 方向 | 价格 | 股数 |\n|---|---|---|---|'
  const equityStart = report.equity[0]?.value ?? 0
  const equityEnd = report.equity[report.equity.length - 1]?.value ?? 0
  return [
    `# ${title}`,
    '',
    `> 仅供研究参考，不构成投资建议。`,
    '',
    '## 参数',
    `- 标的：${report.symbol}`,
    `- 快线/慢线：SMA(${report.fast}/${report.slow})`,
    `- 初始资金：${report.initial_cash.toFixed(2)}`,
    '',
    '## 绩效指标',
    `- 总收益：${pct(m.total_return)}（年化 ${pct(m.annual_return)}）`,
    `- 最大回撤：${pct(m.max_drawdown)}`,
    `- 夏普比率：${m.sharpe.toFixed(4)}`,
    `- 交易笔数：${m.trade_count}`,
    `- 胜率：${pct(m.win_rate)}`,
    `- 期末净值：${report.final_equity.toFixed(2)}`,
    '',
    '## 净值曲线',
    `- 期初：${equityStart.toFixed(2)}`,
    `- 期末：${equityEnd.toFixed(2)}`,
    `- 数据点：${report.equity.length} 个`,
    '',
    '## 成交记录',
    tradeHeader,
    trades,
    '',
  ].join('\n')
}

/**
 * Compare two backtest reports and produce the delta metrics.
 * @param baseline - the baseline report.
 * @param challenger - the comparison report.
 * @returns the delta fields.
 */
export function compareBacktests(
  baseline: BacktestReport,
  challenger: BacktestReport,
): {
  readonly total_return_delta: number
  readonly max_drawdown_delta: number
  readonly sharpe_delta: number
  readonly winner: 'baseline' | 'challenger'
} {
  const returnDelta = challenger.metrics.total_return - baseline.metrics.total_return
  const drawdownDelta = challenger.metrics.max_drawdown - baseline.metrics.max_drawdown
  const sharpeDelta = challenger.metrics.sharpe - baseline.metrics.sharpe
  const winner = returnDelta > 0 ? 'challenger' as const : 'baseline' as const
  return {
    total_return_delta: returnDelta,
    max_drawdown_delta: drawdownDelta,
    sharpe_delta: sharpeDelta,
    winner,
  }
}

/**
 * Extract trade summary lines for the research report.
 * @param trades - the fills to summarize.
 * @returns formatted trade lines.
 */
export function formatTrades(trades: readonly BacktestTrade[]): string[] {
  return trades.map(t =>
    `${t.date} ${t.side === 'buy' ? '买入' : '卖出'} ${t.shares.toFixed(0)} 股 @ ${t.price.toFixed(2)}`,
  )
}
