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
import { BARS_HARD_LIMIT } from './compliance.ts'
import { errorEnvelope, isQuantError, okEnvelope } from './errors.ts'
import type { QuantEnvelope } from './errors.ts'
import { DataSourceBreaker, BARS_MIN, fetchKline } from './pdat/datasource.ts'
import type { KlineBar } from './pdat/datasource.ts'
import * as indicators from './paat/indicators.ts'
import type { Series } from './paat/indicators.ts'
import { runBacktest, validateBacktestParams } from './pcpt/backtest.ts'
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

/** The tool layer's resolved dependencies. */
export interface QuantToolDeps {
  /** The resolved plugin configuration. */
  readonly config: ResolvedConfig
  /** The kernel client. */
  readonly kernel: QuantKernelClient
  /** The data-source circuit breaker. */
  readonly breaker: DataSourceBreaker
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
  const windowText = data.window === undefined ? '' : `（窗口 ${String(data.window)}）`
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
 * Register the three research tools on one context.
 * @param ctx - the runtime fiber's context carrying the tool registry.
 * @param deps - the tool layer dependencies.
 * @returns the registration's disposer.
 */
export function registerQuantTools(ctx: Context, deps: QuantToolDeps): () => void {
  const tools = [getKlineTool(deps), computeIndicatorTool(deps), runBacktestTool(deps)]
  const disposers = tools.map(tool => ctx.tools.register(tool))
  return () => {
    for (const dispose of disposers) dispose()
  }
}

/** Re-exported envelope type for consumers typing against the tools. */
export type { QuantEnvelope }
