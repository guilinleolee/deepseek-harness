import { describe, expect, it, vi } from 'vitest'
import { resolveConfig } from '../src/config.ts'
import { DataSourceBreaker } from '../src/pdat/datasource.ts'
import { QuantError } from '../src/errors.ts'
import type { ToolDefinition } from '@deepseek-ai/dsh-tools'
import type { Context } from '@deepseek-ai/cordis'
import type { QuantKernelClient } from '../src/kernel-client/client.ts'
import {
  computeIndicatorTool, getKlineTool, registerQuantTools, runBacktestTool,
} from '../src/tools.ts'
import type { QuantToolDeps } from '../src/tools.ts'

const ENV = { platform: 'linux' as const, dshHome: '/home/tester/.dsh' }
const CONFIG = resolveConfig(undefined, ENV)

const BARS = Array.from({ length: 30 }, (_, index) => ({
  date: `2024-01-${String(index + 1).padStart(2, '0')}`,
  open: 10 + index,
  high: 11 + index,
  low: 9 + index,
  close: 10.5 + index,
  volume: 1000 + index,
}))

const REPORT = {
  symbol: '000001',
  fast: 10,
  slow: 30,
  initial_cash: 1_000_000,
  final_equity: 1_100_000,
  equity: [{ date: '2024-01-01', value: 1_000_000 }, { date: '2024-01-30', value: 1_100_000 }],
  trades: [],
  metrics: {
    total_return: 0.1,
    annual_return: 2.1,
    max_drawdown: 0.02,
    sharpe: 1.4,
    win_rate: 0,
    trade_count: 0,
  },
}

function kernelByOp(handler: (op: string, params: Record<string, unknown>) => unknown): QuantKernelClient {
  return {
    request: vi.fn(async (op: string, params: Record<string, unknown>) => handler(op, params)),
  } as unknown as QuantKernelClient
}

function syntheticBarsKernel(): QuantKernelClient {
  return kernelByOp((op) => {
    if (op === 'get_kline') return BARS
    if (op === 'backtest') return REPORT
    return {}
  })
}

function execWith(sessionAppend?: (type: string, data: unknown) => void): never {
  const agent = sessionAppend === undefined
    ? undefined
    : { id: 'agent-1', session: { append: sessionAppend } }
  return { signal: new AbortController().signal, agent } as never
}

/** First text block of a render result, as a plain string. */
function textOf(blocks: unknown): string {
  return (blocks as { text?: string }[])[0]?.text ?? ''
}

function deps(kernel: QuantKernelClient): QuantToolDeps {
  return { config: CONFIG, kernel, breaker: new DataSourceBreaker(3) }
}

describe('quant_get_kline', () => {
  const tool = (): ToolDefinition => getKlineTool(deps(syntheticBarsKernel()))

  it('returns the success envelope and renders the tail with the disclaimer', async () => {
    const definition = tool()
    const value = await definition.execute?.({ symbol: '000001', bars: 30 }, execWith())
    expect(value).toMatchObject({ code: 0, msg: 'ok' })
    expect((value as { data: { series: unknown[] } }).data.series).toHaveLength(30)
    const rendered = textOf(definition.output.render({}, value as never))
    expect(rendered).toContain('000001')
    expect(rendered).toContain('最近 10 根')
    expect(rendered).toContain('仅供研究参考，不构成投资建议')
  })

  it('defaults the bar count when omitted', async () => {
    const kernel = syntheticBarsKernel()
    await getKlineTool(deps(kernel)).execute?.({ symbol: '000001' }, execWith())
    expect((kernel.request as ReturnType<typeof vi.fn>).mock.calls[0]?.[1]).toMatchObject({ bars: 120 })
  })

  it('renders the failure envelope without leaking internals', async () => {
    const kernel = kernelByOp(() => {
      throw new QuantError('DATA', '标的代码格式不正确')
    })
    const definition = getKlineTool(deps(kernel))
    const value = await definition.execute?.({ symbol: '!!' }, execWith())
    expect(value).toMatchObject({ code: 1002, data: null })
    expect(textOf(definition.output.render({}, value as never))).toContain('请求失败')
  })

  it('appends the kernel-fault event for kernel-plane failures when a session exists', async () => {
    const appended: Array<[string, unknown]> = []
    const kernel = kernelByOp(() => {
      throw new QuantError('KERNEL', '内核异常退出', { cause: { requestId: 'r-9' } })
    })
    const definition = getKlineTool(deps(kernel))
    const value = await definition.execute?.({ symbol: '000001' }, execWith((type, data) => {
      appended.push([type, data])
    }))
    expect(value).toMatchObject({ code: 1003 })
    expect(appended).toEqual([[
      'quant/kernel-fault',
      { requestId: 'r-9', op: 'get_kline', code: 'KERNEL', message: '内核异常退出' },
    ]])
  })

  it('does not append a fault event for data-tier failures or missing sessions', async () => {
    const appended: Array<[string, unknown]> = []
    const kernel = kernelByOp(() => {
      throw new QuantError('DATA', '格式错误')
    })
    const definition = getKlineTool(deps(kernel))
    await definition.execute?.({ symbol: '!!' }, execWith((type) => { appended.push([type, null]) }))
    expect(appended).toEqual([])
    await definition.execute?.({ symbol: '000001' }, execWith())
    const kernel2 = kernelByOp(() => {
      throw new QuantError('KERNEL', '内核超时')
    })
    await getKlineTool(deps(kernel2)).execute?.({ symbol: '000001' }, execWith())
    expect(appended).toEqual([])
  })

  it('renders the empty-series fallback', () => {
    const definition = tool()
    const rendered = textOf(definition.output.render({}, { code: 0, msg: 'ok', data: { symbol: 'x', series: [] } }))
    expect(rendered).toContain('K线数据为空')
    const rendered2 = textOf(definition.output.render({}, { code: 0, msg: 'ok', data: {} }))
    expect(rendered2).toContain('K线数据为空')
  })

  it('presents the call card from args alone', () => {
    const card = tool().presentCall?.({ symbol: 'AAPL', bars: 5 })
    expect(card).toEqual({ card: 'generic', title: '获取K线：AAPL' })
  })
})

describe('quant_compute_indicator', () => {
  it('computes ma with the default window and aligns dates', async () => {
    const definition = computeIndicatorTool(deps(syntheticBarsKernel()))
    const value = await definition.execute?.({ symbol: '000001', indicator: 'ma' }, execWith())
    expect(value).toMatchObject({ code: 0, msg: 'ok' })
    const data = (value as { data: { window: number; values: { date: string; value: number | null }[] } }).data
    expect(data.window).toBe(20)
    expect(data.values).toHaveLength(30)
    expect(data.values[18]?.value).toBeNull()
    expect(data.values[19]?.value).not.toBeNull()
    const rendered = textOf(definition.output.render({}, value as never))
    expect(rendered).toContain('指标 ma')
    expect(rendered).toContain('仅供研究参考')
  })

  it('computes each indicator family', async () => {
    for (const indicator of ['ema', 'rsi', 'atr', 'boll'] as const) {
      const definition = computeIndicatorTool(deps(syntheticBarsKernel()))
      const value = await definition.execute?.({ symbol: '000001', indicator, window: 10 }, execWith())
      expect(value).toMatchObject({ code: 0 })
    }
    const macdDefinition = computeIndicatorTool(deps(syntheticBarsKernel()))
    const macdValue = await macdDefinition.execute?.({ symbol: '000001', indicator: 'macd' }, execWith())
    expect((macdValue as { data: { window: number | undefined } }).data.window).toBeUndefined()
  })

  it('computes every indicator with its conventional default window', async () => {
    for (const indicator of ['ma', 'ema', 'rsi', 'atr', 'boll'] as const) {
      const definition = computeIndicatorTool(deps(syntheticBarsKernel()))
      const value = await definition.execute?.({ symbol: '000001', indicator }, execWith())
      expect(value).toMatchObject({ code: 0 })
    }
  })

  it('reports the friendly validation failure and no fault event', async () => {
    const appended: Array<[string, unknown]> = []
    const definition = computeIndicatorTool(deps(syntheticBarsKernel()))
    const value = await definition.execute?.(
      { symbol: '000001', indicator: 'ma', window: 999 },
      execWith((type, data) => { appended.push([type, data]) }),
    )
    expect(value).toMatchObject({ code: 1002 })
    expect((value as { msg: string }).msg).toContain('ma 窗口')
    expect(appended).toEqual([])
  })

  it('renders the empty fallback and the call card', () => {
    const definition = computeIndicatorTool(deps(syntheticBarsKernel()))
    expect(textOf(definition.output.render({}, { code: 0, msg: 'ok', data: {} }))).toContain('指标数据为空')
    expect(definition.presentCall?.({ symbol: '000001', indicator: 'rsi' }))
      .toEqual({ card: 'generic', title: '计算指标：000001 rsi' })
  })
})

describe('quant_run_backtest', () => {
  const tool = (): ToolDefinition => runBacktestTool(deps(syntheticBarsKernel()))

  it('fetches the bars, runs the kernel, and renders the metrics', async () => {
    const definition = tool()
    const value = await definition.execute?.({ symbol: '000001' }, execWith())
    expect(value).toMatchObject({ code: 0 })
    const rendered = textOf(definition.output.render({}, value as never))
    expect(rendered).toContain('SMA(10/30)')
    expect(rendered).toContain('总收益')
    expect(rendered).toContain('仅供研究参考')
  })

  it('passes caller cash and fee overrides to the kernel', async () => {
    const kernel = syntheticBarsKernel()
    await runBacktestTool(deps(kernel)).execute?.(
      { symbol: '000001', initial_cash: 500_000, fee_rate: 0.001, fast: 5, slow: 20, bars: 60 },
      execWith(),
    )
    const calls = (kernel.request as ReturnType<typeof vi.fn>).mock.calls as Array<[string, Record<string, unknown>]>
    expect(calls[1]?.[1]).toMatchObject({ fast: 5, slow: 20, initial_cash: 500_000, fee_rate: 0.001 })
  })

  it('returns the friendly envelope for impossible parameters', async () => {
    const definition = tool()
    const value = await definition.execute?.({ symbol: '000001', fast: 30, slow: 10 }, execWith())
    expect(value).toMatchObject({ code: 1002 })
    expect((value as { msg: string }).msg).toContain('必须小于')
  })

  it('appends the backtest kernel fault', async () => {
    const appended: Array<[string, unknown]> = []
    const kernel = kernelByOp((op) => {
      if (op === 'get_kline') return BARS
      throw new QuantError('KERNEL', '回测进程崩溃')
    })
    const definition = runBacktestTool(deps(kernel))
    const value = await definition.execute?.({ symbol: '000001' }, execWith((type, data) => {
      appended.push([type, data])
    }))
    expect(value).toMatchObject({ code: 1003 })
    expect(appended).toEqual([[
      'quant/kernel-fault',
      { requestId: 'unknown', op: 'backtest', code: 'KERNEL', message: '回测进程崩溃' },
    ]])
  })

  it('renders the empty fallback and the call card', () => {
    const definition = tool()
    expect(textOf(definition.output.render({}, { code: 0, msg: 'ok', data: {} }))).toContain('回测报告为空')
    expect(definition.presentCall?.({ symbol: '600000' }))
      .toEqual({ card: 'generic', title: '回测：600000 SMA(10/30)' })
  })
})

describe('render fallbacks', () => {
  it('treats non-envelope values as empty for every renderer', () => {
    const tools = [
      getKlineTool(deps(syntheticBarsKernel())),
      computeIndicatorTool(deps(syntheticBarsKernel())),
      runBacktestTool(deps(syntheticBarsKernel())),
    ]
    for (const tool of tools) {
      for (const value of [undefined, null, 'text', 42, {}]) {
        expect(textOf(tool.output.render({}, value as never))).toContain('仅供研究参考')
      }
    }
  })

  it('swallows a failing fault append and keeps the envelope', async () => {
    const kernel = kernelByOp(() => {
      throw new QuantError('KERNEL', '内核崩溃', { cause: { requestId: 'r-1' } })
    })
    const definition = getKlineTool(deps(kernel))
    const value = await definition.execute?.(
      { symbol: '000001' },
      execWith(() => {
        throw new Error('session closed')
      }),
    )
    expect(value).toMatchObject({ code: 1003 })
  })

  it('renders the source placeholder when the envelope omits the source', () => {
    const tool = getKlineTool(deps(syntheticBarsKernel()))
    const rendered = textOf(tool.output.render({}, {
      code: 0, msg: 'ok',
      data: { symbol: 'AAPL', count: 1, series: [{ date: '2024-01-02', open: 1, high: 2, low: 0.5, close: 1.5, volume: 9 }] },
    }))
    expect(rendered).toContain('unknown 源')
  })

  it('renders failure envelopes without a message field', () => {
    const tool = getKlineTool(deps(syntheticBarsKernel()))
    expect(textOf(tool.output.render({}, { code: 7 }))).toContain('请求失败（code 7）')
    expect(textOf(tool.output.render({}, { code: 8, msg: 42 }))).toContain('请求失败（code 8）')
    expect(textOf(tool.output.render({}, { code: 9, msg: '原因' }))).toContain('请求失败（code 9）：原因')
  })

  it('renders the indicator failure and a window-less (macd) reading', async () => {
    const failing = computeIndicatorTool(deps(kernelByOp(() => {
      throw new QuantError('DATA', '标的不存在')
    })))
    const failed = await failing.execute?.({ symbol: '000001', indicator: 'ma' }, execWith())
    expect(textOf(failing.output.render({}, failed as never))).toContain('请求失败')

    const kernel = syntheticBarsKernel()
    const definition = computeIndicatorTool(deps(kernel))
    const value = await definition.execute?.({ symbol: '000001', indicator: 'macd' }, execWith())
    const rendered = textOf(definition.output.render({}, value as never))
    expect(rendered).toContain('指标 macd，')
    expect(rendered).not.toContain('窗口')
    expect(rendered).toContain('最近 5 个')
  })

  it('renders the backtest failure and sparse reports with placeholders', async () => {
    const failing = runBacktestTool(deps(kernelByOp(() => {
      throw new QuantError('NETWORK', '数据源超时')
    })))
    const failed = await failing.execute?.({ symbol: '000001' }, execWith())
    expect(textOf(failing.output.render({}, failed as never))).toContain('请求失败')

    const definition = runBacktestTool(deps(syntheticBarsKernel()))
    const sparse = {
      code: 0,
      msg: 'ok',
      data: {
        symbol: '000001',
        equity: [{ date: '2024-01-01', value: 1_000_000 }],
        metrics: { total_return: 0, annual_return: 0, max_drawdown: 0, sharpe: 0, win_rate: 0, trade_count: 0 },
      },
    }
    const rendered = textOf(definition.output.render({}, sparse))
    expect(rendered).toContain('SMA(?/?)')
    expect(rendered).toContain('期末净值 1000000（期初 ?）')
  })
})

describe('registerQuantTools', () => {
  it('registers the three tools and disposes them together', () => {
    const disposers: Array<() => void> = []
    const register = vi.fn((tool: { name: string }) => {
      void tool
      const disposer = (): void => {}
      disposers.push(disposer)
      return disposer
    })
    const ctx = { tools: { register } } as unknown as Context
    const dispose = registerQuantTools(ctx, deps(syntheticBarsKernel()))
    expect(register).toHaveBeenCalledTimes(3)
    const names = register.mock.calls.map(call => call[0].name)
    expect(names).toEqual(['quant_get_kline', 'quant_compute_indicator', 'quant_run_backtest'])
    dispose()
    expect(disposers).toHaveLength(3)
  })
})
