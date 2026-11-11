"""Patcher P2-PET-tests3: cover the remaining PET branches."""
import io

T = 'D:/dsh-wt-quant-p1/packages/quant/quant-research/tests/'

def patch(path, old, new):
    s = io.open(path, encoding='utf-8').read()
    assert old in s, f'{path}: {old[:70]!r}'
    s = s.replace(old, new)
    io.open(path, 'w', encoding='utf-8', newline='\n').write(s)
    print('patched', path.split('tests/')[-1])

# ── pet.spec: remaining branches ──
patch(T + 'pet.spec.ts',
"""  it('rejects infeasible buys instead of going negative', () => {""",
"""  it('rejects tiny-delta skips only via the epsilon, not via segment or price checks', () => {
    // segment 非法值与微小的 delta 都会被校验/eps 处理。
    expect(() => shockBars([
      { date: '2024-01-02', open: 1, high: 1, low: 1, close: 1, volume: 1 },
    ], { scenario: 'crash', shock: 0.1, segment: Number.NaN })).toThrow(QuantError)
    const plan = computePlan({
      cash: 0,
      positions: [{ symbol: '000001', shares: 1_000_000, avg_cost: 10 }],
      targets: [{ symbol: '000001', weight: 1 }],
      prices: { '000001': 10 },
      feeRate: 0,
    })
    expect(plan.trades).toEqual([])
    expect(plan.cashAfter).toBe(0)
  })

  it('requires held-symbol prices even when the held symbol is not a target', () => {
    expect(() => computePlan({
      cash: 0,
      positions: [{ symbol: '000001', shares: 10, avg_cost: 5 }],
      targets: [{ symbol: 'AAPL', weight: 0.5 }],
      prices: { AAPL: 100 },
      feeRate: 0,
    })).toThrow(/缺少持仓/)
    expect(() => computePlan({
      cash: 0,
      positions: [{ symbol: '000001', shares: 10, avg_cost: 5 }],
      targets: [
        { symbol: 'AAPL', weight: 0.25 }, { symbol: '000001', weight: 0.25 },
      ],
      prices: { AAPL: 100, '000001': 0 },
      feeRate: 0,
    })).toThrow(/必须为正数/)
    expect(() => shockBars([
      { date: '2024-01-02', open: 1, high: 1, low: 1, close: 1, volume: 1 },
    ], { scenario: 'crash', shock: 0.1, segment: 1.5 })).toThrow(QuantError)
  })

  it('rejects infeasible buys instead of going negative', () => {""")

# ── pet.spec: service branches ──
patch(T + 'pet.spec.ts',
"""  it('rejects overselling', async () => {""",
"""  it('rejects empty names, sells past a nonzero position, and computes cash deltas', async () => {
    const accounts = table() as unknown as Parameters<typeof createAccount>[0]
    await expect(createAccount(accounts, { name: '  ', initialCash: 1 }, 1)).rejects.toThrow(/账户名/)
    const orders = table() as unknown as KvTable<string, Order>
    const account = await createAccount(accounts, { name: 'x', initialCash: 1_000 }, 1, () => 'a-1')
    const afterBuy = await applyTrades(
      accounts, orders, account,
      [{ symbol: 'AAPL', side: 'buy', shares: 5, price: 100, fee: 1 }],
      1_000 - 500 - 1, 2, () => 'o-1',
    )
    // 顶仓：avg_cost 按加权更新
    const topped = await applyTrades(
      accounts, orders, afterBuy,
      [{ symbol: 'AAPL', side: 'buy', shares: 5, price: 120, fee: 1 }],
      1_000 - 500 - 1 - 600 - 1, 3, () => 'o-2',
    )
    expect(topped.positions[0]).toEqual({ symbol: 'AAPL', shares: 10, avg_cost: 110 })
    // 持仓存在但数量不足：sell 分支的 held-defined 路径
    await expect(applyTrades(
      accounts, orders, topped,
      [{ symbol: 'AAPL', side: 'sell', shares: 99, price: 120, fee: 1 }],
      0, 4, () => 'o-3',
    )).rejects.toThrow(/持仓不足/)
    expect(cashDelta([
      { symbol: 'AAPL', side: 'sell', shares: 10, price: 100, fee: 1 },
      { symbol: '000001', side: 'buy', shares: 5, price: 10, fee: 2 },
    ])).toBe(1000 - 1 - 50 - 2)
  })

  it('rejects overselling', async () => {""")

# ── tools.spec: PET presentCall + render fallback paths ──
patch(T + 'tools.spec.ts',
"""describe('render fallbacks', () => {""",
"""describe('PET tool renders', () => {
  const petDepsLocal = (): QuantToolDeps => ({
    ...deps(syntheticBarsKernel()),
    accounts: new Map() as never,
    orders: new Map() as never,
    approval: { request: vi.fn(async () => 'rejected' as const) },
  })

  it('renders the create/state/rebalance failure and empty paths', async () => {
    const failingKernel = kernelByOp(() => {
      throw new QuantError('KERNEL', '内核崩溃')
    })
    const failing = petDepsLocal()
    failing.kernel = failingKernel
    const createFailed = await accountCreateTool(failing).execute?.({ name: 'x' }, execLike())
    expect(textOf(accountCreateTool(deps(syntheticBarsKernel())).output.render({}, createFailed as never)))
      .toContain('请求失败')
    const stateFailed = await accountStateTool(failing).execute?.({ account_name: 'x' }, execLike())
    expect(textOf(accountStateTool(deps(syntheticBarsKernel())).output.render({}, stateFailed as never)))
      .toContain('请求失败')
    const rebalanceFailed = await executeRebalanceTool(failing).execute?.(
      { account_name: 'x', targets: [{ symbol: '000001', weight: 0.5 }] }, execLike(),
    )
    expect(textOf(executeRebalanceTool(deps(syntheticBarsKernel())).output.render({}, rebalanceFailed as never)))
      .toContain('请求失败')

    const empty = accountCreateTool(deps(syntheticBarsKernel())).output.render({}, { code: 0, msg: 'ok', data: {} } as never)
    expect(textOf(empty)).toContain('账户信息为空')
    const emptyRebalance = executeRebalanceTool(deps(syntheticBarsKernel())).output.render(
      {}, { code: 0, msg: 'ok', data: {} } as never,
    )
    expect(textOf(emptyRebalance)).toContain('调仓结果为空')
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

  it('renders account positions and rebalance fills end to end', async () => {
    const kernel = syntheticBarsKernel()
    const d = petDepsLocal()
    d.kernel = kernel
    await accountCreateTool(d).execute?.({ name: '研究一号' }, execLike())
    const rebalance = await executeRebalanceTool(d).execute?.(
      { account_name: '研究一号', targets: [{ symbol: '000001', weight: 0.5 }] },
      execLike(),
    )
    const rebalanceText = textOf(executeRebalanceTool(d).output.render({}, rebalance as never))
    expect(rebalanceText).toContain('调仓完成')
    expect(rebalanceText).toContain('现金余额')
    const state = await accountStateTool(d).execute?.({ account_name: '研究一号' }, execLike())
    const stateText = textOf(accountStateTool(d).output.render({}, state as never))
    expect(stateText).toContain('总权益')
    expect(stateText).toContain('000001')
  })
})

describe('render fallbacks', () => {""")

# tools.spec imports: QuantError + new builders + textOf already present
patch(T + 'tools.spec.ts',
"""import {
  accountCreateTool, accountStateTool, assessRiskTool, computeIndicatorTool, executeRebalanceTool,
  getKlineTool, registerQuantTools, runBacktestTool, stressTestTool,
} from '../src/tools.ts'""",
"""import {
  accountCreateTool, accountStateTool, assessRiskTool, computeIndicatorTool, executeRebalanceTool,
  getKlineTool, registerQuantTools, runBacktestTool, stressTestTool,
} from '../src/tools.ts'
import { QuantError } from '../src/errors.ts'""")
print('patcher done')
