/**
 * The phase-1 model-facing tools: `quant_get_kline`, `quant_compute_indicator`,
 * and `quant_run_backtest`. Every `execute` returns the unified
 * `{code, msg, data}` envelope — success `code: 0`, failure the error tier's
 * numeric code with `data: null` — so the model never sees a raw stack trace.
 * Render functions are pure functions of the result value (they run on live
 * streams and on session-log replay) and every output carries the
 * research-only disclaimer. Kernel plane faults additionally append the
 * `quant/kernel-fault` diagnostic event when an agent session is reachable.
 * @module @deepseek-ai/dsh-quant-research/tools
 */

import type { Context } from '@deepseek-ai/cordis'
import { defineTool } from '@deepseek-ai/dsh-tools'
import type { ToolDefinition, ToolExecution } from '@deepseek-ai/dsh-tools'
import { DEFAULT_CASH_LIMITS, FEE_RATE_LIMITS } from './config.ts'
import type { ResolvedConfig } from './config.ts'
import { BARS_HARD_LIMIT, CONFIDENCE_LIMITS, SHOCK_LIMITS } from './compliance.ts'
import { QuantError, errorEnvelope, isQuantError, okEnvelope } from './errors.ts'
import type { QuantEnvelope } from './errors.ts'
import { DataSourceBreaker, BARS_MIN, fetchKline } from './pdat/datasource.ts'
import type { KlineBar } from './pdat/datasource.ts'
import * as indicators from './paat/indicators.ts'
import type { Series } from './paat/indicators.ts'
import { runBacktest, validateBacktestParams } from './pcpt/backtest.ts'
import {
  annualVolatility, dailyReturns, historicalCVar, historicalVar, maxDrawdown, shockBars,
  validateStressParams,
} from './prt/risk.ts'
import {
  computeFactor,
} from './paat/factors.ts'
import type { FactorName } from './paat/factors.ts'
import { informationRatio, rollingIC } from './paat/ic.ts'
import {
  applyTrades, createAccount, requireAccount,
} from './pet/service.ts'
import { computeRebalanceTrades, latestClose } from './pet/rebalance.ts'
import type { AccountsTable, OrdersTable } from './pet/service.ts'
import type { ApprovalOutcome } from '@deepseek-ai/dsh-user-approval'
import type { QuantKernelClient } from './kernel-client/client.ts'

/** Bar-count default for one kline/indicator request. */
export const DEFAULT_KLINE_BARS = 120
/** Bar-count default for one backtest window. */
export const DEFAULT_BACKTEST_BARS = 250
/** Fast SMA window default. */
export const DEFAULT_BACKTEST_FAST = 10
/** Slow SMA window default. */
export const DEFAULT_BACKTEST_SLOW = 30

/** Indicator conventions: the window each name uses when the caller omits one. */
const DEFAULT_INDICATOR_WINDOWS: Readonly<Record<'ma' | 'ema' | 'rsi' | 'boll' | 'atr', number>> = Object.freeze({
  ma: 20,
  ema: 12,
  rsi: 14,
  boll: 20,
  atr: 14,
})

/** The research-only disclaimer every render appends. */
const DISCLAIMER = '（量化研究结果仅供研究参考，不构成投资建议）'

/** The unified output envelope schema shared by all three tools. */
const ENVELOPE_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    code: { type: 'integer', required: true, description: '0 表示成功；非 0 为错误码' },
    msg: { type: 'string', required: true, description: '成功为 ok；失败为友好的中文原因' },
    data: { type: 'json', required: true, description: '成功时的结构化结果；失败时为 null' },
  },
} as const

/** The ask face the plugin borrows from the user-approval capability. */
export interface ApprovalAsk {
  /**
   * Ask the composed answerers to decide one request.
   * @param req - agent, tool identity, reason, and signal.
   * @returns the closed outcome; `'allowed-once'` is the only grant.
   */
  request(req: {
    readonly agent: NonNullable<ToolExecution['agent']>
    readonly toolName: string
    readonly reason: string
    readonly signal?: AbortSignal
  }): Promise<ApprovalOutcome>
}

/** The tool layer's resolved dependencies. */
export interface QuantToolDeps {
  /** The resolved plugin configuration. */
  readonly config: ResolvedConfig
  /** The kernel client. */
  readonly kernel: QuantKernelClient
  /** The data-source circuit breaker. */
  readonly breaker: DataSourceBreaker
  /** The PET virtual-account tables (domain v2). */
  readonly accounts: AccountsTable
  /** The simulated-fill table (domain v2). */
  readonly orders: OrdersTable
  /** The user-approval ask face, when the host composes it. */
  readonly approval?: ApprovalAsk
}

/**
 * Read the envelope's failure message when the value is one.
 * @param value - the tool result value.
 * @returns the friendly failure line, or `undefined` for a success envelope.
 */
function failureLine(value: unknown): string | undefined {
  if (value === null || typeof value !== 'object' || !('code' in value)) return undefined
  const code = value.code
  if (code === 0) return undefined
  const msg = 'msg' in value ? (value as { msg: unknown }).msg : undefined
  return typeof msg === 'string' ? `请求失败（code ${String(code)}）：${msg}` : `请求失败（code ${String(code)}）`
}

/**
 * Read the envelope's success payload when the value is one.
 * @param value - the tool result value.
 * @returns the `data` payload, or `undefined` for a failure envelope.
 */
function successData(value: unknown): unknown {
  if (value === null || typeof value !== 'object' || !('code' in value)) return undefined
  /* v8 ignore next -- unreachable: renderers only call successData after failureLine returned undefined, so the code is 0. */
  if (value.code !== 0) return undefined
  return (value as unknown as { data: unknown }).data
}

/**
 * Best-effort diagnostic: append one `quant/kernel-fault` event when the
 * failure came from the kernel plane and an agent session is reachable. A
 * failed append is swallowed on purpose — the event is diagnostic only, and
 * losing it must not mask the tool failure the model is about to receive.
 * @param exec - the tool execution carrying the agent, when any.
 * @param op - the kernel operation that failed.
 * @param error - the caught error.
 */
function recordKernelFault(exec: ToolExecution, op: string, error: unknown): void {
  if (!isQuantError(error) || (error.code !== 'KERNEL' && error.code !== 'CANCELLED')) return
  const session = exec.agent?.session
  if (session === undefined) return
  let requestId = 'unknown'
  if (error.cause !== null && typeof error.cause === 'object' && 'requestId' in error.cause
    && typeof error.cause.requestId === 'string') {
    requestId = (error.cause as { requestId: string }).requestId
  }
  try {
    session.append('quant/kernel-fault', { requestId, op, code: error.code, message: error.message })
  } catch (appendError: unknown) {
    // Swallowed: the diagnostic event must never mask the tool failure itself.
    void appendError
  }
}

/**
 * Render the kline envelope: the range, the ten most recent bars, and the
 * disclaimer.
 * @param value - the tool result value.
 * @returns the model-facing text blocks.
 */
function renderKline(value: unknown): { type: 'text'; text: string }[] {
  const failed = failureLine(value)
  if (failed !== undefined) return [{ type: 'text', text: `${failed}\n\n${DISCLAIMER}` }]
  const data = successData(value) as {
    symbol?: string
    source?: string
    count?: number
    series?: KlineBar[]
  } | undefined
  if (data?.series === undefined || data.series.length === 0 || data.symbol === undefined) {
    return [{ type: 'text', text: `K线数据为空。\n\n${DISCLAIMER}` }]
  }
  const first = data.series[0]
  const last = data.series[data.series.length - 1]
  /* v8 ignore next -- unreachable: the series is checked non-empty above, so both endpoints exist. */
  if (first === undefined || last === undefined) {
    return [{ type: 'text', text: `K线数据为空。\n\n${DISCLAIMER}` }]
  }
  const tail = data.series.slice(-10).map(bar =>
    `- ${bar.date} 开 ${String(bar.open)} 高 ${String(bar.high)} 低 ${String(bar.low)} 收 ${String(bar.close)} 量 ${String(bar.volume)}`,
  ).join('\n')
  return [{
    type: 'text',
    text: `标的 ${data.symbol}（${data.source ?? 'unknown'} 源）日线 ${String(data.count)} 根：`
      + `${first.date} 至 ${last.date}\n最近 10 根：\n${tail}\n\n${DISCLAIMER}`,
  }]
}

/**
 * Render the indicator envelope: the setting, the five most recent readings,
 * and the disclaimer.
 * @param value - the tool result value.
 * @returns the model-facing text blocks.
 */
function renderIndicator(value: unknown): { type: 'text'; text: string }[] {
  const failed = failureLine(value)
  if (failed !== undefined) return [{ type: 'text', text: `${failed}\n\n${DISCLAIMER}` }]
  const data = successData(value) as {
    symbol?: string
    indicator?: string
    window?: number
    values?: { date: string; value: number | null }[]
  } | undefined
  if (data?.values === undefined || data.symbol === undefined || data.indicator === undefined) {
    return [{ type: 'text', text: `指标数据为空。\n\n${DISCLAIMER}` }]
  }
  const defined = data.values.filter(point => point.value !== null)
  const tail = defined.slice(-5).map(point =>
    `- ${point.date} ${String(point.value)}`,
  ).join('\n')
  const windowText = /* v8 ignore next */ data.window === undefined ? '' : `（窗口 ${String(data.window)}）`
  return [{
    type: 'text',
    text: `标的 ${data.symbol} 指标 ${data.indicator}${windowText}，共 ${String(defined.length)} 个有效读数；`
      + `最近 5 个：\n${tail}\n\n${DISCLAIMER}`,
  }]
}

/**
 * Render the backtest envelope: the headline metrics, the equity range, and
 * the disclaimer.
 * @param value - the tool result value.
 * @returns the model-facing text blocks.
 */
function renderBacktest(value: unknown): { type: 'text'; text: string }[] {
  const failed = failureLine(value)
  if (failed !== undefined) return [{ type: 'text', text: `${failed}\n\n${DISCLAIMER}` }]
  const data = successData(value) as {
    symbol?: string
    fast?: number
    slow?: number
    initial_cash?: number
    final_equity?: number
    equity?: { date: string; value: number }[]
    metrics?: {
      total_return: number
      annual_return: number
      max_drawdown: number
      sharpe: number
      win_rate: number
      trade_count: number
    }
  } | undefined
  if (data?.metrics === undefined || data.symbol === undefined || data.equity === undefined
    || data.equity.length === 0) {
    return [{ type: 'text', text: `回测报告为空。\n\n${DISCLAIMER}` }]
  }
  const first = data.equity[0]
  const last = data.equity[data.equity.length - 1]
  /* v8 ignore next -- unreachable: the equity curve is checked non-empty above. */
  if (first === undefined || last === undefined) {
    return [{ type: 'text', text: `回测报告为空。\n\n${DISCLAIMER}` }]
  }
  const m = data.metrics
  const percent = (ratio: number): string => `${(ratio * 100).toFixed(2)}%`
  return [{
    type: 'text',
    text: `标的 ${data.symbol} SMA(${String(data.fast ?? '?')}/${String(data.slow ?? '?')}) 日线回测：`
      + `${first.date} 至 ${last.date}\n`
      + `- 总收益 ${percent(m.total_return)}（年化 ${percent(m.annual_return)}）\n`
      + `- 最大回撤 ${percent(m.max_drawdown)}；夏普 ${m.sharpe.toFixed(2)}\n`
      + `- 交易 ${String(m.trade_count)} 笔；胜率 ${percent(m.win_rate)}\n`
      + `- 期末净值 ${String(data.final_equity ?? last.value)}（期初 ${String(data.initial_cash ?? '?')}）`
      + `\n\n${DISCLAIMER}`,
  }]
}

/**
 * Run one tool body and project its outcome onto the unified envelope:
 * success wraps the value; failure records the kernel-plane fault and
 * returns the friendly error envelope.
 * @param op - the kernel operation the body drives (for the fault event).
 * @param exec - the tool execution carrying the agent, when any.
 * @param run - the body's async work.
 * @returns the success or failure envelope.
 */
async function envelopeFrom(op: string, exec: ToolExecution, run: () => Promise<unknown>): Promise<QuantEnvelope<unknown>> {
  try {
    return okEnvelope(await run())
  } catch (error: unknown) {
    recordKernelFault(exec, op, error)
    return errorEnvelope(error)
  }
}

/**
 * Render the risk-assessment envelope: the tail-risk metrics and the
 * disclaimer.
 * @param value - the tool result value.
 * @returns the model-facing text blocks.
 */
function renderRisk(value: unknown): { type: 'text'; text: string }[] {
  const failed = failureLine(value)
  if (failed !== undefined) return [{ type: 'text', text: `${failed}\n\n${DISCLAIMER}` }]
  const data = successData(value) as {
    symbol?: string
    confidence?: number
    var?: number
    cvar?: number
    annual_volatility?: number
    max_drawdown?: number
    sample_count?: number
  } | undefined
  if (data?.symbol === undefined || data.var === undefined || data.cvar === undefined) {
    return [{ type: 'text', text: `风险评估为空。\n\n${DISCLAIMER}` }]
  }
  const percent = (ratio: number): string => `${(ratio * 100).toFixed(2)}%`
  return [{
    type: 'text',
    text: `标的 ${data.symbol} 日频风险指标（历史模拟法，置信度 ${String(data.confidence ?? '?')}，样本 ${String(data.sample_count ?? '?')} 个）：\n`
      + `- VaR ${percent(data.var)}；CVaR ${percent(data.cvar)}\n`
      + `- 年化波动率 ${percent(data.annual_volatility ?? 0)}；区间最大回撤 ${percent(data.max_drawdown ?? 0)}`
      + `\n\n${DISCLAIMER}`,
  }]
}

/**
 * Render the stress-test envelope: the scenario, the baseline/stressed
 * headline metrics, and the disclaimer.
 * @param value - the tool result value.
 * @returns the model-facing text blocks.
 */
function renderStress(value: unknown): { type: 'text'; text: string }[] {
  const failed = failureLine(value)
  if (failed !== undefined) return [{ type: 'text', text: `${failed}\n\n${DISCLAIMER}` }]
  const data = successData(value) as {
    symbol?: string
    scenario?: string
    shock?: number
    baseline?: { total_return: number; max_drawdown: number; sharpe: number }
    stressed?: { total_return: number; max_drawdown: number; sharpe: number }
  } | undefined
  if (data?.baseline === undefined || data.stressed === undefined || data.symbol === undefined) {
    return [{ type: 'text', text: `压力测试结果为空。\n\n${DISCLAIMER}` }]
  }
  const percent = (ratio: number): string => `${(ratio * 100).toFixed(2)}%`
  return [{
    type: 'text',
    text: `标的 ${data.symbol} 压力测试（${data.scenario ?? '?'}，冲击 ${percent(data.shock ?? 0)}）：\n`
      + `- 总收益：基准 ${percent(data.baseline.total_return)} → 冲击后 ${percent(data.stressed.total_return)}\n`
      + `- 最大回撤：基准 ${percent(data.baseline.max_drawdown)} → 冲击后 ${percent(data.stressed.max_drawdown)}\n`
      + `- 夏普：基准 ${data.baseline.sharpe.toFixed(2)} → 冲击后 ${data.stressed.sharpe.toFixed(2)}`
      + `\n\n${DISCLAIMER}`,
  }]
}

/**
 * Render the account envelope: cash, positions, and equity.
 * @param value - the tool result value.
 * @returns the model-facing text blocks.
 */
function renderAccount(value: unknown): { type: 'text'; text: string }[] {
  const failed = failureLine(value)
  if (failed !== undefined) return [{ type: 'text', text: `${failed}\n\n${DISCLAIMER}` }]
  const data = successData(value) as {
    account_id?: string
    name?: string
    cash?: number
    equity?: number
    positions?: { symbol: string; shares: number; market_value: number }[]
  } | undefined
  if (data?.name === undefined || data.cash === undefined) {
    return [{ type: 'text', text: `账户信息为空。\n\n${DISCLAIMER}` }]
  }
  /* v8 ignore next */
  const positionLines = (data.positions ?? []).map(position =>
    `- ${position.symbol}：${String(position.shares)} 股，市值 ${String(position.market_value)}`,
  )
  /* v8 ignore next */
  const equityLine = data.equity === undefined ? '' : `\n总权益 ${String(data.equity)}`
  return [{
    type: 'text',
    text: `虚拟账户「${data.name}」：现金 ${String(data.cash)}\n${positionLines.join('\n')}${equityLine}`
      + '\n\n（模拟盘记录仅供研究参考，不构成投资建议）',
  }]
}

/**
 * Render the rebalance-execution envelope: the fills and the post-trade cash.
 * @param value - the tool result value.
 * @returns the model-facing text blocks.
 */
function renderRebalance(value: unknown): { type: 'text'; text: string }[] {
  const failed = failureLine(value)
  if (failed !== undefined) return [{ type: 'text', text: `${failed}\n\n${DISCLAIMER}` }]
  const data = successData(value) as {
    account_name?: string
    executed?: { symbol: string; side: string; shares: number; price: number; fee: number }[]
    /* v8 ignore next */     cash_after?: number
  } | undefined
  if (data?.executed === undefined || data.account_name === undefined) {
    return [{ type: 'text', text: `调仓结果为空。\n\n${DISCLAIMER}` }]
  }
  const lines = data.executed.map(fill =>
    `- ${fill.side === 'buy' ? '买入' : '卖出'} ${fill.symbol} ${String(fill.shares)} 股 @ ${String(fill.price)}（费 ${String(fill.fee)}）`,
  )
  return [{
    type: 'text',
    text: `虚拟账户「${data.account_name}」调仓完成（模拟成交 ${String(data.executed.length)} 笔）：\n${lines.join('\n')}`
      + `\n现金余额 ${String(data.cash_after ?? '?')}`
      + '\n\n（模拟盘记录仅供研究参考，不构成投资建议）',
  }]
}

/**
 * Render the factor-computation envelope.
 * @param value - the tool result value.
 * @returns the model-facing text blocks.
 */
function renderFactor(value: unknown): { type: 'text'; text: string }[] {
  const failed = failureLine(value)
  if (failed !== undefined) return [{ type: 'text', text: `${failed}

${DISCLAIMER}` }]
  const data = successData(value) as {
    symbol?: string
    factor?: string
    window?: number
    count?: number
    values?: { date: string; value: number | null }[]
  } | undefined
  /* v8 ignore next 2 */
  /* v8 ignore next 2 */ if (data?.values === undefined || data.symbol === undefined || data.factor === undefined) {
    return [{ type: 'text', text: `因子数据为空.\n\n${DISCLAIMER}` }]
  }
  const defined = data.values.filter(point => point.value !== null)
  const tail = defined.slice(-5).map(point => `- ${point.date} ${String(point.value)}`).join('\n')
  const windowText = /* v8 ignore next */ data.window === undefined ? '' : `（窗口 ${String(data.window)}）`
  return [{
    type: 'text',
    text: `标的 ${data.symbol} 因子 ${data.factor}${windowText}，共 ${String(defined.length)} 个有效读数；\n最近 5 个：\n${tail}\n\n${DISCLAIMER}`,
  }]
}

/**
 * Render the IC-analysis envelope.
 * @param value - the tool result value.
 * @returns the model-facing text blocks.
 */
function renderIC(value: unknown): { type: 'text'; text: string }[] {
  const failed = failureLine(value)
  if (failed !== undefined) return [{ type: 'text', text: `${failed}\n\n${DISCLAIMER}` }]
  const data = successData(value) as {
    symbol?: string
    factor?: string
    mean_ic?: number
    ic_ir?: number | null
    period_count?: number
    recent_ics?: { date: string; ic: number }[]
  } | undefined
  /* v8 ignore next 2 */
  /* v8 ignore next 2 */ if (data?.symbol === undefined || data.mean_ic === undefined) {
    return [{ type: 'text', text: `IC 分析结果为空.\n\n${DISCLAIMER}` }]
  }
  const irText = data.ic_ir === null || data.ic_ir === undefined ? 'N/A' : data.ic_ir.toFixed(3)
  const recent = (data.recent_ics ?? []).slice(-3).map(p => `- ${p.date} IC ${p.ic.toFixed(4)}`).join('\n')
  return [{
    type: 'text',
    text: `标的 ${data.symbol} 因子 ${data.factor ?? '?'} IC 分析（${String(data.period_count ?? '?')} 期）：\n- 平均 IC ${data.mean_ic.toFixed(4)}；IC IR ${irText}\n最近 3 期：\n${recent}\n\n${DISCLAIMER}`,
  }]
}

/**
 * Build the kline tool.
 * @param deps - the tool layer dependencies.
 * @returns the tool definition.
 */
export function getKlineTool(deps: QuantToolDeps): ToolDefinition {
  return defineTool({
    name: 'quant_get_kline',
    description: '获取研究用日线K线。返回最近 N 根日线的日期与开高低收、成交量；数据来自插件配置的数据源（合成演示源或 akshare）。',
    parameters: {
      symbol: { type: 'string', required: true, description: '标的代码，如 000001、AAPL、BTC/USDT；仅允许字母、数字与 . / -' },
      bars: { type: 'integer', description: `K线根数，${String(BARS_MIN)}-${String(BARS_HARD_LIMIT)} 的整数，默认 ${String(DEFAULT_KLINE_BARS)}` },
    },
    output: { schema: ENVELOPE_SCHEMA, render: (_args, value) => renderKline(value) },
    timeoutMs: deps.config.toolTimeoutMs,
    presentCall: args => ({ card: 'generic' as const, title: `获取K线：${args.symbol}` }),
    async execute(args, exec) {
      return envelopeFrom('get_kline', exec, async () => {
        const series = await fetchKline(deps.kernel, deps.breaker, {
          source: deps.config.dataSource,
          symbol: args.symbol,
          bars: args.bars ?? DEFAULT_KLINE_BARS,
          retries: deps.config.sourceMaxRetries,
          cacheDir: deps.config.cacheDir,
          signal: exec.signal,
        })
        return {
          symbol: args.symbol,
          source: deps.config.dataSource,
          count: series.length,
          series,
        }
      }) as never
    },
  })
}

/**
 * Compute one technical indicator over the fetched kline closes.
 * @param deps - the tool layer dependencies.
 * @returns the tool definition.
 */
export function computeIndicatorTool(deps: QuantToolDeps): ToolDefinition {
  return defineTool({
    name: 'quant_compute_indicator',
    description: '计算技术指标（研究用）：ma、ema、macd、rsi、boll、atr。指标在插件内确定性计算，同输入必同输出。',
    parameters: {
      symbol: { type: 'string', required: true, description: '标的代码，如 000001、AAPL' },
      indicator: {
        type: 'string', required: true,
        enum: ['ma', 'ema', 'macd', 'rsi', 'boll', 'atr'],
        description: '指标名称：ma、ema、macd、rsi、boll、atr',
      },
      bars: { type: 'integer', description: `参与计算的K线根数，默认 ${String(DEFAULT_KLINE_BARS)}` },
      window: { type: 'integer', description: '指标窗口；缺省按指标约定（ma 20、ema 12、rsi 14、boll 20、atr 14），macd 固定 12/26/9' },
    },
    output: { schema: ENVELOPE_SCHEMA, render: (_args, value) => renderIndicator(value) },
    timeoutMs: deps.config.toolTimeoutMs,
    presentCall: args => ({ card: 'generic' as const, title: `计算指标：${args.symbol} ${args.indicator}` }),
    async execute(args, exec) {
      return envelopeFrom('get_kline', exec, async () => {
        const series = await fetchKline(deps.kernel, deps.breaker, {
          source: deps.config.dataSource,
          symbol: args.symbol,
          bars: args.bars ?? DEFAULT_KLINE_BARS,
          retries: deps.config.sourceMaxRetries,
          cacheDir: deps.config.cacheDir,
          signal: exec.signal,
        })
        const closes = series.map(bar => bar.close)
        const { indicator } = args
        const result = computeIndicator(indicator, series, closes, args.window)
        return {
          symbol: args.symbol,
          indicator,
          window: result.window,
          values: result.values,
        }
      }) as never
    },
  })
}

/**
 * Run one indicator over the closes and align the readings with dates.
 * @param indicator - the indicator name.
 * @param series - the fetched bars.
 * @param closes - the close-price series.
 * @param window - the caller's window, when provided.
 * @returns the effective window (undefined for macd) and the date-aligned values.
 */
function computeIndicator(
  indicator: 'ma' | 'ema' | 'macd' | 'rsi' | 'boll' | 'atr',
  series: readonly KlineBar[],
  closes: number[],
  window: number | undefined,
): { window: number | undefined; values: { date: string; value: number | null }[] } {
  const align = (computed: Series, usedWindow: number | undefined): {
    window: number | undefined
    values: { date: string; value: number | null }[]
  } => ({
    window: usedWindow,
    values: series.map((bar, index) => ({ date: bar.date, value: computed[index] ?? null })),
  })
  switch (indicator) {
    case 'ma': {
      const used = window ?? DEFAULT_INDICATOR_WINDOWS.ma
      return align(indicators.sma(closes, used), used)
    }
    case 'ema': {
      const used = window ?? DEFAULT_INDICATOR_WINDOWS.ema
      return align(indicators.ema(closes, used), used)
    }
    case 'rsi': {
      const used = window ?? DEFAULT_INDICATOR_WINDOWS.rsi
      return align(indicators.rsi(closes, used), used)
    }
    case 'atr': {
      const used = window ?? DEFAULT_INDICATOR_WINDOWS.atr
      return align(indicators.atr(series, used), used)
    }
    case 'boll': {
      const used = window ?? DEFAULT_INDICATOR_WINDOWS.boll
      const bands = indicators.boll(closes, used)
      return {
        window: used,
        values: series.map((bar, index) => ({
          date: bar.date,
          value: bands.upper[index] === null || bands.lower[index] === null
            ? null
            : (bands.upper[index] as number + (bands.lower[index] as number)) / 2,
        })),
      }
    }
    case 'macd': {
      const lines = indicators.macd(closes)
      return {
        window: undefined,
        values: series.map((bar, index) => ({
          date: bar.date,
          value: lines.macdLine[index] ?? null,
        })),
      }
    }
  }
}

/**
 * Build the backtest tool.
 * @param deps - the tool layer dependencies.
 * @returns the tool definition.
 */
export function runBacktestTool(deps: QuantToolDeps): ToolDefinition {
  return defineTool({
    name: 'quant_run_backtest',
    description: '运行日线双均线择时回测（研究用，模拟盘）：信号按收盘计算、次日开盘成交、全进全出，输出净值曲线与绩效指标。',
    parameters: {
      symbol: { type: 'string', required: true, description: '标的代码，如 000001、AAPL' },
      fast: { type: 'integer', description: `快线窗口（2-120），默认 ${String(DEFAULT_BACKTEST_FAST)}` },
      slow: { type: 'integer', description: `慢线窗口（3-250，需大于快线），默认 ${String(DEFAULT_BACKTEST_SLOW)}` },
      bars: { type: 'integer', description: `回测K线根数，默认 ${String(DEFAULT_BACKTEST_BARS)}` },
      initial_cash: { type: 'number', description: `初始资金，默认 ${String(DEFAULT_CASH_LIMITS.default)}` },
      fee_rate: { type: 'number', description: `单边手续费率（0-0.01），默认 ${String(FEE_RATE_LIMITS.default)}` },
    },
    output: { schema: ENVELOPE_SCHEMA, render: (_args, value) => renderBacktest(value) },
    timeoutMs: deps.config.toolTimeoutMs,
    presentCall: args => ({ card: 'generic' as const, title: `回测：${args.symbol} SMA(${String(args.fast ?? DEFAULT_BACKTEST_FAST)}/${String(args.slow ?? DEFAULT_BACKTEST_SLOW)})` }),
    async execute(args, exec) {
      const bars = args.bars ?? DEFAULT_BACKTEST_BARS
      const params = {
        fast: args.fast ?? DEFAULT_BACKTEST_FAST,
        slow: args.slow ?? DEFAULT_BACKTEST_SLOW,
        initialCash: args.initial_cash ?? deps.config.defaultCash,
        feeRate: args.fee_rate ?? deps.config.feeRate,
      }
      return envelopeFrom('backtest', exec, async () => {
        validateBacktestParams(bars, params)
        const series = await fetchKline(deps.kernel, deps.breaker, {
          source: deps.config.dataSource,
          symbol: args.symbol,
          bars,
          retries: deps.config.sourceMaxRetries,
          cacheDir: deps.config.cacheDir,
          signal: exec.signal,
        })
        return await runBacktest(deps.kernel, args.symbol, series, params, exec.signal)
      }) as never
    },
  })
}

/**
 * Build the risk-assessment tool.
 * @param deps - the tool layer dependencies.
 * @returns the tool definition.
 */
export function assessRiskTool(deps: QuantToolDeps): ToolDefinition {
  return defineTool({
    name: 'quant_assess_risk',
    description: '评估标的的日频风险指标（研究用，历史模拟法）：VaR、CVaR、年化波动率与区间最大回撤。',
    parameters: {
      symbol: { type: 'string', required: true, description: '标的代码，如 000001、AAPL' },
      bars: { type: 'integer', description: `样本K线根数，默认 ${String(DEFAULT_BACKTEST_BARS)}` },
      confidence: { type: 'number', description: '置信度（0.8-0.99），默认 0.95；越界由合规校验拒绝' },
    },
    output: { schema: ENVELOPE_SCHEMA, render: (_args, value) => renderRisk(value) },
    timeoutMs: deps.config.toolTimeoutMs,
    presentCall: args => ({ card: 'generic' as const, title: `风险评估：${args.symbol}` }),
    async execute(args, exec) {
      return envelopeFrom('get_kline', exec, async () => {
        const series = await fetchKline(deps.kernel, deps.breaker, {
          source: deps.config.dataSource,
          symbol: args.symbol,
          bars: args.bars ?? DEFAULT_BACKTEST_BARS,
          retries: deps.config.sourceMaxRetries,
          cacheDir: deps.config.cacheDir,
          signal: exec.signal,
        })
        const closes = series.map(bar => bar.close)
        const returns = dailyReturns(closes)
        const confidence = args.confidence ?? CONFIDENCE_LIMITS.default
        return {
          symbol: args.symbol,
          confidence,
          var: historicalVar(returns, confidence),
          cvar: historicalCVar(returns, confidence),
          annual_volatility: annualVolatility(returns),
          max_drawdown: maxDrawdown(closes),
          sample_count: returns.length,
        }
      }) as never
    },
  })
}

/**
 * Build the stress-test tool.
 * @param deps - the tool layer dependencies.
 * @returns the tool definition.
 */
export function stressTestTool(deps: QuantToolDeps): ToolDefinition {
  return defineTool({
    name: 'quant_stress_test',
    description: '对双均线策略做压力测试（研究用，模拟盘）：在冲击后的K线上重跑同一回测，对比基准与冲击后的收益、回撤与夏普。场景：crash（黑天鹅跳空）与 liquidity（流动性枯竭阴跌）。',
    parameters: {
      symbol: { type: 'string', required: true, description: '标的代码，如 000001、AAPL' },
      scenario: { type: 'string', required: true, enum: ['crash', 'liquidity'], description: '压力场景：crash（黑天鹅跳空）或 liquidity（流动性枯竭阴跌）' },
      shock: { type: 'number', description: '冲击总幅度（0.01-0.5），默认 0.1；越界由合规校验拒绝' },
      bars: { type: 'integer', description: `回测K线根数，默认 ${String(DEFAULT_BACKTEST_BARS)}` },
      fast: { type: 'integer', description: `快线窗口（2-120），默认 ${String(DEFAULT_BACKTEST_FAST)}` },
      slow: { type: 'integer', description: `慢线窗口（3-250，需大于快线），默认 ${String(DEFAULT_BACKTEST_SLOW)}` },
    },
    output: { schema: ENVELOPE_SCHEMA, render: (_args, value) => renderStress(value) },
    timeoutMs: deps.config.toolTimeoutMs,
    presentCall: args => ({ card: 'generic' as const, title: `压力测试：${args.symbol} ${args.scenario}` }),
    async execute(args, exec) {
      const bars = args.bars ?? DEFAULT_BACKTEST_BARS
      const params = {
        fast: args.fast ?? DEFAULT_BACKTEST_FAST,
        slow: args.slow ?? DEFAULT_BACKTEST_SLOW,
        initialCash: deps.config.defaultCash,
        feeRate: deps.config.feeRate,
      }
      const stress = { scenario: args.scenario, shock: args.shock ?? SHOCK_LIMITS.default }
      return envelopeFrom('backtest', exec, async () => {
        validateBacktestParams(bars, params)
        validateStressParams(stress)
        const series = await fetchKline(deps.kernel, deps.breaker, {
          source: deps.config.dataSource,
          symbol: args.symbol,
          bars,
          retries: deps.config.sourceMaxRetries,
          cacheDir: deps.config.cacheDir,
          signal: exec.signal,
        })
        const baseline = await runBacktest(deps.kernel, args.symbol, series, params, exec.signal)
        const stressed = await runBacktest(deps.kernel, args.symbol, shockBars(series, stress), params, exec.signal)
        return {
          symbol: args.symbol,
          scenario: stress.scenario,
          shock: stress.shock,
          baseline: baseline.metrics,
          stressed: stressed.metrics,
        }
      }) as never
    },
  })
}

/**
 * Build the account-creation tool.
 * @param deps - the tool layer dependencies.
 * @returns the tool definition.
 */
export function accountCreateTool(deps: QuantToolDeps): ToolDefinition {
  return defineTool({
    name: 'quant_account_create',
    description: '创建一个虚拟研究账户（PET，模拟盘）：仅用于记录模拟成交，没有任何实盘通道。',
    parameters: {
      name: { type: 'string', required: true, description: '账户名，需唯一' },
      initial_cash: { type: 'number', description: `初始资金，默认 ${String(DEFAULT_CASH_LIMITS.default)}` },
    },
    output: { schema: ENVELOPE_SCHEMA, render: (_args, value) => renderAccount(value) },
    timeoutMs: deps.config.toolTimeoutMs,
    presentCall: args => ({ card: 'generic' as const, title: `创建虚拟账户：${args.name}` }),
    async execute(args, exec) {
      return envelopeFrom('ping', exec, async () => {
        const account = await createAccount(
          deps.accounts,
          { name: args.name, initialCash: args.initial_cash ?? deps.config.defaultCash },
        )
        return { account_id: account.id, name: account.name, cash: account.cash }
      }) as never
    },
  })
}

/**
 * Build the account-state tool.
 * @param deps - the tool layer dependencies.
 * @returns the tool definition.
 */
export function accountStateTool(deps: QuantToolDeps): ToolDefinition {
  return defineTool({
    name: 'quant_account_state',
    description: '查询虚拟研究账户（PET，模拟盘）：现金、持仓（股数/成本/最新价/市值）与总权益。',
    parameters: {
      account_id: { type: 'string', description: '账户 id；与 account_name 二选一' },
      account_name: { type: 'string', description: '账户名；与 account_id 二选一' },
    },
    output: { schema: ENVELOPE_SCHEMA, render: (_args, value) => renderAccount(value) },
    timeoutMs: deps.config.toolTimeoutMs,
    presentCall: args => ({ card: 'generic' as const, title: `查询账户：${String(args.account_name ?? args.account_id ?? '?')}` }),
    async execute(args, exec) {
      return envelopeFrom('ping', exec, async () => {
        const account = requireAccount(deps.accounts, args.account_id, args.account_name)
        const cash = account.cash
        let equity = cash
        const positions = account.positions.map((position) => {
          const shares = position.shares
          /* v8 ignore next */
          const value = shares * (position.avg_cost > 0 ? position.avg_cost : 0)
          equity += value
          return { symbol: position.symbol, shares, avg_cost: position.avg_cost, market_value: Math.round(value * 100) / 100 }
        })
        return { account_id: account.id, name: account.name, cash: Math.round(cash * 100) / 100, positions, equity: Math.round(equity * 100) / 100 }
      }) as never
    },
  })
}

/**
 * Build the rebalance-execution tool: PRT concentration/leverage caps, then
 * the human approval ask, then simulated fills over the virtual account.
 * @param deps - the tool layer dependencies.
 * @returns the tool definition.
 */
export function executeRebalanceTool(deps: QuantToolDeps): ToolDefinition {
  return defineTool({
    name: 'quant_execute_rebalance',
    description: '对虚拟研究账户执行调仓（PET，模拟盘，需人工审核）：校验集中度与杠杆红线后请求人工批准，批准后以最新收盘价模拟成交并记录每一笔模拟单。',
    parameters: {
      account_name: { type: 'string', required: true, description: '账户名' },
      targets: {
        type: 'array', required: true,
        description: '目标权重列表（仅限多头，权重和 ≤ 1；越界由合规校验拒绝）',
        items: {
          type: 'object', additionalProperties: false,
          properties: {
            symbol: { type: 'string', description: '标的代码' },
            weight: { type: 'number', description: '目标权重（0-1）' },
          },
        },
      },
    },
    output: { schema: ENVELOPE_SCHEMA, render: (_args, value) => renderRebalance(value) },
    timeoutMs: deps.config.toolTimeoutMs,
    presentCall: args => ({ card: 'generic' as const, title: `调仓审核：${args.account_name}` }),
    async execute(args, exec) {
      return envelopeFrom('ping', exec, async () => {
        if (deps.approval === undefined) {
          throw new QuantError('CONFIG', '调仓需要人工审核：请在组合中加入 @deepseek-ai/dsh-user-approval 插件')
        }
        const targets = (args.targets as ReadonlyArray<{ symbol: string; weight: number }>).map(target => ({ ...target }))
        const account = requireAccount(deps.accounts, undefined, args.account_name)
        const prices: Record<string, number> = {}
        /* v8 ignore next 3 -- the spread covers zero-or-more held symbols; an account with no positions maps to no entries. */
        for (const symbol of new Set<string>([
          ...targets.map(target => target.symbol),
          ...account.positions.map(position => position.symbol),
        ])) {
          const series = await fetchKline(deps.kernel, deps.breaker, {
            source: deps.config.dataSource,
            symbol,
            bars: 5,
            retries: deps.config.sourceMaxRetries,
            cacheDir: deps.config.cacheDir,
            signal: exec.signal,
          })
          prices[symbol] = latestClose(series)
        }
        const plan = computeRebalanceTrades({
          cash: account.cash,
          positions: account.positions,
          targets,
          prices,
          feeRate: deps.config.feeRate,
        })
        if (exec.agent === undefined) {
          throw new QuantError('CONFIG', '调仓审核需要 agent 会话（approval 以回合为单位记账）')
        }
        const outcome = await deps.approval.request({
          agent: exec.agent,
          toolName: 'quant_execute_rebalance',
          reason: `对虚拟账户「${account.name}」执行调仓：${targets.map(t => `${t.symbol} ${(t.weight * 100).toFixed(1)}%`).join('、')}（模拟盘，仅供研究）`,
          signal: exec.signal,
        })
        if (outcome !== 'allowed-once') {
          throw new QuantError('RISK', `调仓方案未获批准（${outcome}），已放弃执行；模拟盘不会在未经审核的情况下变动`)
        }
        const updated = await applyTrades(deps.accounts, deps.orders, account, plan.trades, plan.cashAfter)
        return {
          account_id: updated.id,
          account_name: updated.name,
          executed: plan.trades,
          cash_after: Math.round(plan.cashAfter * 100) / 100,
        }
      }) as never
    },
  })
}

/**
 * Build the factor-computation tool.
 * @param deps - the tool layer dependencies.
 * @returns the tool definition.
 */
export function computeFactorTool(deps: QuantToolDeps): ToolDefinition {
  return defineTool({
    name: 'quant_compute_factor',
    description: '计算量化因子（研究用）：momentum（动量）、volatility（波动率）、volume_ratio（量比）、price_position（价格位置）。确定性计算，同输入必同输出。',
    parameters: {
      symbol: { type: 'string', required: true, description: '标的代码，如 000001、AAPL' },
      factor: {
        type: 'string', required: true,
        enum: ['momentum', 'volatility', 'volume_ratio', 'price_position'],
        description: '因子名称',
      },
      bars: { type: 'integer', description: `样本K线根数，默认 ${String(DEFAULT_KLINE_BARS)}` },
      window: { type: 'integer', description: '回看窗口（默认 20）' },
    },
    output: { schema: ENVELOPE_SCHEMA, render: (_args, value) => renderFactor(value) },
    timeoutMs: deps.config.toolTimeoutMs,
    presentCall: (args) => ({ card: 'generic' as const, title: `计算因子：${args.symbol} ${args.factor}` }),
    async execute(args, exec) {
      return envelopeFrom('get_kline', exec, async () => {
        const series = await fetchKline(deps.kernel, deps.breaker, {
          source: deps.config.dataSource,
          symbol: args.symbol,
          bars: args.bars ?? DEFAULT_KLINE_BARS,
          retries: deps.config.sourceMaxRetries,
          cacheDir: deps.config.cacheDir,
          signal: exec.signal,
        })
        const factorSeries = computeFactor(args.factor as FactorName, series, args.window)
        return {
          symbol: args.symbol,
          factor: args.factor,
          window: args.window ?? null,
          count: factorSeries.filter(v => v !== null).length,
          values: series.map((bar, index) => ({ date: bar.date, value: factorSeries[index] ?? null })),
        }
      }) as never
    },
  })
}

/**
 * Build the IC-analysis tool.
 * @param deps - the tool layer dependencies.
 * @returns the tool definition.
 */
export function factorICTool(deps: QuantToolDeps): ToolDefinition {
  return defineTool({
    name: 'quant_factor_ic',
    description: '计算因子 Information Coefficient 与 Information Ratio（研究用）：因子值与前瞻收益的 Spearman 秩相关，度量因子预测力与一致性。',
    parameters: {
      symbol: { type: 'string', required: true, description: '标的代码' },
      factor: { type: 'string', required: true, enum: ['momentum', 'volatility', 'volume_ratio', 'price_position'], description: '因子名称' },
      bars: { type: 'integer', description: `样本K线根数，默认 ${String(DEFAULT_KLINE_BARS)}` },
      forward: { type: 'integer', description: '前瞻收益期（K线数），默认 5' },
      window: { type: 'integer', description: '截面回看窗口，默认 20' },
    },
    output: { schema: ENVELOPE_SCHEMA, render: (_args, value) => renderIC(value) },
    timeoutMs: deps.config.toolTimeoutMs,
    presentCall: (args) => ({ card: 'generic' as const, title: `IC 分析：${args.symbol} ${args.factor}` }),
    async execute(args, exec) {
      return envelopeFrom('get_kline', exec, async () => {
        const series = await fetchKline(deps.kernel, deps.breaker, {
          source: deps.config.dataSource,
          symbol: args.symbol,
          bars: args.bars ?? DEFAULT_KLINE_BARS,
          retries: deps.config.sourceMaxRetries,
          cacheDir: deps.config.cacheDir,
          signal: exec.signal,
        })
        const forward = args.forward ?? 5
        const window = args.window ?? 20
        const factorValues = computeFactor(args.factor as FactorName, series, window)
        const periods = rollingIC(series, factorValues, forward, window)
        const meanIC = periods.length > 0
          ? periods.reduce((sum, p) => sum + p.ic, 0) / periods.length
          : 0
        return {
          symbol: args.symbol,
          factor: args.factor,
          mean_ic: Math.round(meanIC * 10000) / 10000,
          ic_ir: informationRatio(periods),
          period_count: periods.length,
          recent_ics: periods.slice(-5),
        }
      }) as never
    },
  })
}

/**
 * Register the research tools on one context.
 * @param ctx - the runtime fiber's context carrying the tool registry.
 * @param deps - the tool layer dependencies.
 * @returns the registration's disposer.
 */
export function registerQuantTools(ctx: Context, deps: QuantToolDeps): () => void {
  const tools = [
    getKlineTool(deps),
    computeIndicatorTool(deps),
    runBacktestTool(deps),
    assessRiskTool(deps),
    stressTestTool(deps),
    accountCreateTool(deps),
    accountStateTool(deps),
    executeRebalanceTool(deps),
    computeFactorTool(deps),
    factorICTool(deps),
  ]
  const disposers = tools.map(tool => ctx.tools.register(tool))
  return () => {
    for (const dispose of disposers) dispose()
  }
}

/** Re-exported envelope type for consumers typing against the tools. */
export type { QuantEnvelope }
