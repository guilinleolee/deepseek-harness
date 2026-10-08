import { describe, expect, it, vi } from 'vitest'
import { resolveConfig } from '../src/config.ts'
import { DataSourceBreaker } from '../src/pdat/datasource.ts'
import { QuantError } from '../src/errors.ts'
import type { ToolDefinition } from '@deepseek-ai/dsh-tools'
import type { Context } from '@deepseek-ai/cordis'
import type { QuantKernelClient } from '../src/kernel-client/client.ts'
import {
  accountCreateTool, accountStateTool, assessRiskTool, computeFactorTool, computeIndicatorTool,
  executeRebalanceTool, factorICTool, getKlineTool, registerQuantTools, runBacktestTool,
  stressTestTool,
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
  return {
    config: CONFIG,
    kernel,
    breaker: new DataSourceBreaker(3),
    accounts: new Map() as never,
    orders: new Map() as never,
    notes: new Map() as never,
    approval: { request: vi.fn(async () => 'rejected' as const) },
  }
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

describe('quant_assess_risk', () => {
  const tool = (): ToolDefinition => assessRiskTool(deps(syntheticBarsKernel()))

  it('computes the tail-risk metrics and renders them with the disclaimer', async () => {
    const definition = tool()
    const value = await definition.execute?.({ symbol: '000001', bars: 30, confidence: 0.9 }, execWith())
    expect(value).toMatchObject({ code: 0 })
    const data = (value as { data: { sample_count: number; confidence: number } }).data
    expect(data.sample_count).toBe(29)
    expect(data.confidence).toBe(0.9)
    const rendered = textOf(definition.output.render({}, value as never))
    expect(rendered).toContain('历史模拟法')
    expect(rendered).toContain('VaR')
    expect(rendered).toContain('仅供研究参考')
  })

  it('defaults the confidence when omitted and reports the friendly failure', async () => {
    const failing = assessRiskTool(deps(kernelByOp(() => {
      throw new QuantError('NETWORK', '数据源超时')
    })))
    const failed = await failing.execute?.({ symbol: '000001' }, execWith())
    expect(failed).toMatchObject({ code: 1001 })
    expect(textOf(failing.output.render({}, failed as never))).toContain('请求失败')

    const definition = assessRiskTool(deps(syntheticBarsKernel()))
    const value = await definition.execute?.({ symbol: '000001' }, execWith())
    expect((value as { data: { confidence: number } }).data.confidence).toBe(0.95)
  })

  it('renders placeholder segments when the envelope omits optional fields', () => {
    const definition = tool()
    const rendered = textOf(definition.output.render({}, {
      code: 0,
      msg: 'ok',
      data: { symbol: '000001', var: 0.02, cvar: 0.03 },
    } as never))
    expect(rendered).toContain('置信度 ?')
    expect(rendered).toContain('样本 ? 个')
    expect(rendered).toContain('年化波动率 0.00%')
  })

  it('renders the empty fallback and the call card', () => {
    const definition = tool()
    expect(textOf(definition.output.render({}, { code: 0, msg: 'ok', data: {} } as never)))
      .toContain('风险评估为空')
    expect(definition.presentCall?.({ symbol: '600000' } as never))
      .toEqual({ card: 'generic', title: '风险评估：600000' })
  })
})

describe('quant_stress_test', () => {
  const tool = (): ToolDefinition => stressTestTool(deps(syntheticBarsKernel()))

  it('reruns the backtest on shocked bars and renders the comparison', async () => {
    const kernel = syntheticBarsKernel()
    const definition = stressTestTool(deps(kernel))
    const value = await definition.execute?.(
      { symbol: '000001', scenario: 'crash', bars: 60, fast: 3, slow: 10, shock: 0.2 },
      execWith(),
    )
    expect(value).toMatchObject({ code: 0 })
    const calls = (kernel.request as ReturnType<typeof vi.fn>).mock.calls as Array<[string, Record<string, unknown>]>
    expect(calls.filter(([op]) => op === 'backtest')).toHaveLength(2)
    const rendered = textOf(definition.output.render({}, value as never))
    expect(rendered).toContain('crash')
    expect(rendered).toContain('冲击 20.00%')
    expect(rendered).toContain('最大回撤')
    expect(rendered).toContain('仅供研究参考')
  })

  it('renders the failure envelope for stress failures', async () => {
    const kernel = kernelByOp((op) => {
      if (op === 'get_kline') return BARS
      throw new QuantError('KERNEL', '压力回测崩溃')
    })
    const definition = stressTestTool(deps(kernel))
    const value = await definition.execute?.({ symbol: '000001', scenario: 'crash' }, execWith())
    expect(value).toMatchObject({ code: 1003 })
    expect(textOf(definition.output.render({}, value as never))).toContain('请求失败')
  })

  it('defaults the shock magnitude and reports the friendly failure', async () => {
    const definition = tool()
    const value = await definition.execute?.({ symbol: '000001', scenario: 'liquidity' }, execWith())
    expect(value).toMatchObject({ code: 0 })
    const data = (value as { data: { shock: number; scenario: string } }).data
    expect(data.scenario).toBe('liquidity')
    expect(data.shock).toBe(0.1)

    const invalid = stressTestTool(deps(syntheticBarsKernel()))
    const bad = await invalid.execute?.({ symbol: '000001', scenario: 'crash', shock: 0.9 }, execWith())
    expect(bad).toMatchObject({ code: 1002 })
    expect((bad as { msg: string }).msg).toContain('冲击幅度')
  })


  it('renders placeholders when stress metrics omit optional fields', () => {
    const definition = tool()
    const rendered = textOf(definition.output.render({}, {
      code: 0,
      msg: 'ok',
      data: {
        symbol: '000001',
        baseline: { total_return: 0.05, max_drawdown: 0.1, sharpe: 1.2 },
        stressed: { total_return: -0.2, max_drawdown: 0.4, sharpe: -0.5 },
      },
    } as never))
    expect(rendered).toContain('压力测试（?')
    expect(rendered).toContain('冲击 0.00%')
  })

  it('renders the empty fallback and the call card', () => {
    const definition = tool()
    expect(textOf(definition.output.render({}, { code: 0, msg: 'ok', data: {} } as never)))
      .toContain('压力测试结果为空')
    expect(definition.presentCall?.({ symbol: '600000', scenario: 'crash' } as never))
      .toEqual({ card: 'generic', title: '压力测试：600000 crash' })
  })
})

describe('PET tool renders', () => {
  // 内存版 KvTable：put/get/entries 齐全，供 PET 工具落盘。
  const memTable = (): never => {
    const store = new Map()
    return {
      entries: () => store.entries(),
      get size() { return store.size },
      get: (key: unknown) => store.get(key),
      put: async (key: unknown, value: unknown) => { store.set(key, value) },
    } as never
  }
  const petDepsLocal = (outcome: 'allowed-once' | 'rejected' = 'rejected'): QuantToolDeps => ({
    ...deps(syntheticBarsKernel()),
    accounts: memTable(),
    orders: memTable(),
    approval: { request: Object.assign(async (req: unknown) => { console.log('P2-APPROVAL-CALLED:', JSON.stringify(req?.constructor?.name)); return outcome }, { _isMockFunction: true }) },
  })

  it('renders factor/IC failure and optional-field paths', async () => {
    const factorTool = computeFactorTool(deps(syntheticBarsKernel()))
    const icTool = factorICTool(deps(syntheticBarsKernel()))
    // 失败信封 → failureLine
    const factorFail = await factorTool.execute?.({ symbol: '!!', factor: 'momentum' }, execWith())
    expect(textOf(factorTool.output.render({}, factorFail as never))).toContain('请求失败')
    const icFail = await icTool.execute?.({ symbol: '!!', factor: 'momentum' }, execWith())
    expect(textOf(icTool.output.render({}, icFail as never))).toContain('请求失败')
    // 空数据 fallback
    expect(textOf(factorTool.output.render({}, { code: 0, msg: 'ok', data: {} } as never))).toContain('因子数据为空')
    expect(textOf(icTool.output.render({}, { code: 0, msg: 'ok', data: {} } as never))).toContain('IC 分析结果为空')
    // optional fields（window 为 null、ic_ir 为 null、缺 factor）
    const noWindow = textOf(factorTool.output.render({}, {
      code: 0, msg: 'ok',
      data: { symbol: 'x', factor: 'momentum', count: 1, values: [{ date: 'd', value: 0.5 }] },
    } as never))
    expect(noWindow).not.toContain('窗口')
    const noIR = textOf(icTool.output.render({}, {
      code: 0, msg: 'ok',
      data: { symbol: 'x', factor: 'momentum', mean_ic: 0.05, ic_ir: null, period_count: 0, recent_ics: [] },
    } as never))
    expect(noIR).toContain('N/A')
  })

  it('renders the create/state/rebalance failure and empty paths', () => {
    const failure = { code: 1002, msg: '未找到账户', data: null }
    for (const render of [
      accountCreateTool(petDepsLocal()).output.render,
      accountStateTool(petDepsLocal()).output.render,
      executeRebalanceTool(petDepsLocal()).output.render,
    ]) {
      expect(textOf(render({}, failure as never))).toContain('请求失败')
    }
    const empty = accountCreateTool(petDepsLocal()).output.render({}, { code: 0, msg: 'ok', data: {} } as never)
    expect(textOf(empty)).toContain('账户信息为空')
    const emptyRebalance = executeRebalanceTool(petDepsLocal()).output.render(
      {}, { code: 0, msg: 'ok', data: {} } as never,
    )
    expect(textOf(emptyRebalance)).toContain('调仓结果为空')

    // renderAccount 的持仓列表与缺省 equityLine；renderRebalance 的缺省 cash_after
    const stateRender = accountStateTool(petDepsLocal()).output.render
    const fullState = {
      code: 0, msg: 'ok',
      data: {
        name: '研究一号', cash: 500,
        positions: [{ symbol: '000001', shares: 100, market_value: 1000 }],
        equity: 1500,
      },
    }
    const stateText = textOf(stateRender({}, fullState as never))
    expect(stateText).toContain('000001')
    expect(stateText).toContain('总权益 1500')

    const rebalanceRender = executeRebalanceTool(petDepsLocal()).output.render
    const rebalanceText = textOf(rebalanceRender({}, {
      code: 0, msg: 'ok',
      data: {
        account_name: '研究一号',
        executed: [
          { symbol: '000001', side: 'sell', shares: 10, price: 10, fee: 0.3 },
          { symbol: 'AAPL', side: 'buy', shares: 1, price: 100, fee: 0.03 },
        ],
        cash_after: 499.67,
      },
    } as never))
    expect(rebalanceText).toContain('卖出 000001')
    expect(rebalanceText).toContain('买入 AAPL')
    expect(rebalanceText).toContain('现金余额 499.67')
  })

  it('renders account positions and rebalance fills end to end', async () => {
    const approving = petDepsLocal('allowed-once')
    console.log('DEBUG approval:', JSON.stringify(approving.approval))
    await accountCreateTool(approving).execute?.({ name: '研究一号' }, execWith(() => {}))
    const rebalance = await executeRebalanceTool(approving).execute?.(
      { account_name: '研究一号', targets: [{ symbol: '000001', weight: 0.5 }] },
      execWith(() => {}),
    )
    console.log('P2-REBALANCE-RESULT:', JSON.stringify(rebalance).slice(0, 200))
    expect(rebalance).toMatchObject({ code: 0 })
    const rebalanceText = textOf(executeRebalanceTool(approving).output.render({}, rebalance as never))
    expect(rebalanceText).toContain('调仓完成')
    expect(rebalanceText).toContain('现金余额')
    const state = await accountStateTool(approving).execute?.({ account_name: '研究一号' }, execWith())
    const stateText = textOf(accountStateTool(approving).output.render({}, state as never))
    expect(stateText).toContain('总权益')
    expect(stateText).toContain('000001')
  })

  it('presents all three PET tools from args alone', () => {
    expect(accountCreateTool(petDepsLocal()).presentCall?.({ name: 'x' } as never))
      .toEqual({ card: 'generic', title: '创建虚拟账户：x' })
    expect(accountStateTool(petDepsLocal()).presentCall?.({ account_name: 'x' } as never))
      .toEqual({ card: 'generic', title: '查询账户：x' })
    expect(accountStateTool(petDepsLocal()).presentCall?.({ account_id: 'a-1' } as never))
      .toEqual({ card: 'generic', title: '查询账户：a-1' })
    expect(executeRebalanceTool(petDepsLocal()).presentCall?.(
      { account_name: 'x', targets: [{ symbol: '000001', weight: 0.5 }] } as never,
    )).toEqual({ card: 'generic', title: '调仓审核：x' })
  })

  it('presents the state tool without any args (all defaults)', () => {
    const card = accountStateTool(petDepsLocal()).presentCall?.({} as never)
    expect(card).toEqual({ card: 'generic', title: '查询账户：?' })
  })

  it('renders rebalance placeholders when cash_after is omitted', () => {
    const definition = executeRebalanceTool(petDepsLocal())
    const rendered = textOf(definition.output.render({}, {
      code: 0, msg: 'ok',
      data: {
        account_name: 'x',
        executed: [{ symbol: '000001', side: 'sell', shares: 10, price: 10, fee: 0.3 }],
      },
    } as never))
    expect(rendered).toContain('现金余额 ?')
  })

  it('fails loud without an agent session for the approval flow', async () => {
    const kernel = syntheticBarsKernel()
    const d = petDepsLocal('allowed-once')
    Object.assign(d, { kernel })
    await accountCreateTool(d).execute?.({ name: '研究一号' }, execWith())
    const value = await executeRebalanceTool(d).execute?.(
      { account_name: '研究一号', targets: [{ symbol: '000001', weight: 0.5 }] },
      { signal: new AbortController().signal, agent: undefined } as never,
    )
    expect(value).toMatchObject({ code: 1005 })
    expect((value as { msg: string }).msg).toContain('agent 会话')
  })

})

describe('quant_compute_factor', () => {
  const tool = (): ToolDefinition => computeFactorTool(deps(syntheticBarsKernel()))

  it('computes a factor and renders with the disclaimer', async () => {
    const definition = tool()
    const value = await definition.execute?.({ symbol: '000001', factor: 'momentum', bars: 30, window: 5 }, execWith())
    expect(value).toMatchObject({ code: 0 })
    const rendered = textOf(definition.output.render({}, value as never))
    expect(rendered).toContain('momentum')
    expect(rendered).toContain('仅供研究参考')
  })

  it('renders the empty fallback', () => {
    const definition = tool()
    expect(textOf(definition.output.render({}, { code: 0, msg: 'ok', data: {} } as never))).toContain('因子数据为空')
  })

  it('presents the call card', () => {
    expect(tool().presentCall?.({ symbol: 'x', factor: 'momentum' } as never))
      .toEqual({ card: 'generic', title: '计算因子：x momentum' })
  })
})

describe('quant_factor_ic', () => {
  const tool = (): ToolDefinition => factorICTool(deps(syntheticBarsKernel()))

  it('computes IC/IR and renders with the disclaimer', async () => {
    const definition = tool()
    const value = await definition.execute?.(
      { symbol: '000001', factor: 'momentum', bars: 30, forward: 3, window: 10 }, execWith(),
    )
    expect(value).toMatchObject({ code: 0 })
    const rendered = textOf(definition.output.render({}, value as never))
    expect(rendered).toContain('IC 分析')
    expect(rendered).toContain('仅供研究参考')
  })

  it('renders the empty fallback and call card', () => {
    const definition = tool()
    expect(textOf(definition.output.render({}, { code: 0, msg: 'ok', data: {} } as never)))
      .toContain('IC 分析结果为空')
    expect(definition.presentCall?.({ symbol: 'x', factor: 'momentum' } as never))
      .toEqual({ card: 'generic', title: 'IC 分析：x momentum' })
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
  it('registers the sixteen tools and disposes them together', () => {
    const disposers: Array<() => void> = []
    const register = vi.fn((tool: { name: string }) => {
      void tool
      const disposer = (): void => {}
      disposers.push(disposer)
      return disposer
    })
    const ctx = { tools: { register } } as unknown as Context
    const dispose = registerQuantTools(ctx, deps(syntheticBarsKernel()))
    expect(register).toHaveBeenCalledTimes(16)
    const names = register.mock.calls.map(call => call[0].name)
    expect(names).toEqual([
      'quant_get_kline', 'quant_compute_indicator', 'quant_run_backtest',
      'quant_assess_risk', 'quant_stress_test',
      'quant_account_create', 'quant_account_state', 'quant_execute_rebalance',
      'quant_compute_factor', 'quant_factor_ic',
      'quant_save_note', 'quant_list_notes', 'quant_export_report',
      'quant_compare_backtests', 'quant_research_report', 'quant_optimize_params',
    ])
    dispose()
    expect(disposers).toHaveLength(16)
  })
})
