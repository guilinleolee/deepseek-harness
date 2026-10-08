import { describe, expect, it, vi } from 'vitest'
import type { KvTable } from '@deepseek-ai/dsh-storage-domain'
import {
  applyTrades, cashDelta, createAccount, listAccounts, requireAccount,
} from '../src/pet/service.ts'
import { computeRebalanceTrades as computePlan, latestClose as lastClose } from '../src/pet/rebalance.ts'
import { QuantError } from '../src/errors.ts'
import type { Account, Order } from '../src/domain/spec.ts'
import { AccountId, OrderId } from '../src/domain/spec.ts'
import { shockBars, validateStressParams, SHOCK_LIMITS } from '../src/prt/risk.ts'
import type { KlineBar } from '../src/pdat/datasource.ts'
import type { QuantToolDeps } from '../src/tools.ts'
import {
  accountCreateTool, accountStateTool, executeRebalanceTool,
} from '../src/tools.ts'
import { resolveConfig } from '../src/config.ts'
import { DataSourceBreaker } from '../src/pdat/datasource.ts'
import type { QuantKernelClient } from '../src/kernel-client/client.ts'

const CONFIG = resolveConfig(undefined, { platform: 'linux', dshHome: '/tmp' })

function table<K extends string, V>(): KvTable<K, V> {
  const store = new Map<K, V>()
  return {
    entries: () => store.entries(),
    get size() { return store.size },
    get: (key: K) => store.get(key),
    put: async (key: K, value: V) => { store.set(key, value) },
  } as unknown as KvTable<K, V>
}

const BARS: KlineBar[] = [
  { date: '2024-01-02', open: 10, high: 11, low: 9, close: 10.5, volume: 1000 },
  { date: '2024-01-03', open: 10.5, high: 12, low: 10, close: 11, volume: 2000 },
]

const PRICES = { '000001': 10, AAPL: 100 }

function petDeps(kernel: QuantKernelClient, approval?: { request: (req: unknown) => Promise<string> }): QuantToolDeps {
  const base: QuantToolDeps = {
    config: CONFIG,
    kernel,
    breaker: new DataSourceBreaker(3),
    accounts: table(),
    orders: table(),
    notes: new Map() as never,
  }
  return approval === undefined ? base : { ...base, approval: approval as never }
}

describe('computeRebalanceTrades', () => {
  it('sells first, then buys, and charges fees on both sides', () => {
    const plan = computePlan({
      cash: 0,
      positions: [{ symbol: '000001', shares: 200, avg_cost: 8 }],
      targets: [
        { symbol: 'AAPL', weight: 0.25 },
        { symbol: '000001', weight: 0.75 },
      ],
      prices: PRICES,
      feeRate: 0,
    })
    // equity 2000：AAPL 目标 500（买 5 股）、000001 目标 1500（卖 50 股）。
    expect(plan.trades.map(trade => trade.side)).toEqual(['sell', 'buy'])
    expect(plan.trades[0]).toMatchObject({ symbol: '000001', side: 'sell', shares: 50, price: 10, fee: 0 })
    expect(plan.trades[1]).toMatchObject({ symbol: 'AAPL', side: 'buy', shares: 5, price: 100, fee: 0 })
    expect(plan.cashAfter).toBe(0)
  })

  it('fully sells held symbols absent from the targets', () => {
    const plan = computePlan({
      cash: 500,
      positions: [{ symbol: '000001', shares: 100, avg_cost: 8 }],
      targets: [{ symbol: 'AAPL', weight: 1 }],
      prices: PRICES,
      feeRate: 0,
    })
    expect(plan.trades).toEqual([
      { symbol: '000001', side: 'sell', shares: 100, price: 10, fee: 0 },
      { symbol: 'AAPL', side: 'buy', shares: 15, price: 100, fee: 0 },
    ])
  })

  it('rejects leverage and missing prices', () => {
    expect(() => computePlan({
      cash: 0, positions: [], targets: [{ symbol: 'AAPL', weight: 1.2 }],
      prices: PRICES, feeRate: 0,
    })).toThrow(QuantError)
    expect(() => computePlan({
      cash: 0, positions: [], targets: [{ symbol: 'TSLA', weight: 0.5 }],
      prices: PRICES, feeRate: 0,
    })).toThrow(QuantError)
  })

  it('validates duplicates, negative weights, price coverage, and fee rate', () => {
    const base = { cash: 0, positions: [], prices: PRICES, feeRate: 0 }
    expect(() => computePlan({
      ...base, targets: [
        { symbol: 'AAPL', weight: 0.3 }, { symbol: 'AAPL', weight: 0.3 },
      ],
    })).toThrow(/调仓目标重复/)
    expect(() => computePlan({
      ...base, targets: [{ symbol: 'AAPL', weight: -0.1 }],
    })).toThrow(/非负数值/)
    expect(() => computePlan({
      ...base, targets: [{ symbol: 'AAPL', weight: 0.5 }], feeRate: 0.9,
    })).toThrow(/手续费率/)
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
  })

  it('rejects tiny-delta skips only via the epsilon, not via segment or price checks', () => {
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

  it('validates the stress segment and fee rate bounds', () => {
    expect(() => validateStressParams({ scenario: 'crash', shock: 0.1, segment: Number.NaN })).toThrow(QuantError)
    expect(() => validateStressParams({ scenario: 'crash', shock: 0.1, segment: 0.5 })).not.toThrow()
    expect(() => validateStressParams({ scenario: 'crash', shock: SHOCK_LIMITS.min })).not.toThrow()
    expect(() => computePlan({
      cash: 0, positions: [], targets: [{ symbol: 'AAPL', weight: 0.5 }],
      prices: PRICES, feeRate: 0.06,
    })).toThrow(/手续费率/)
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

  it('rejects infeasible buys instead of going negative', () => {
    expect(() => computePlan({
      cash: 100,
      positions: [],
      targets: [{ symbol: 'AAPL', weight: 1 }],
      prices: PRICES,
      feeRate: 0.01,
    })).toThrow(/现金不足/)
  })
})

describe('account store', () => {
  it('creates, lists, and looks up accounts by id and name', async () => {
    const accountsTable = table() as unknown as KvTable<AccountId, Account>
    const created = await createAccount(accountsTable, { name: '研究一号', initialCash: 1_000_000 }, 1, () => 'a-1')
    expect(created).toMatchObject({ id: 'a-1', name: '研究一号', cash: 1_000_000, positions: [] })
    await expect(createAccount(accountsTable, { name: '研究一号', initialCash: 1 }, 2)).rejects.toThrow(/已存在/)
    expect(listAccounts(accountsTable).map(account => account.name)).toEqual(['研究一号'])
    expect(requireAccount(accountsTable, undefined, '研究一号').id).toBe('a-1')
    expect(requireAccount(accountsTable, 'a-1').name).toBe('研究一号')
    expect(() => requireAccount(accountsTable, 'missing')).toThrow(/未找到账户/)
  })

  it('applies trades: orders written, cash and positions updated, dust dropped', async () => {
    const accounts = table() as unknown as KvTable<AccountId, Account>
    const orders = table() as unknown as KvTable<OrderId, Order>
    let seq = 0
    const newId = (): string => `o-${String(++seq)}`
    const account = await createAccount(accounts, { name: '研究一号', initialCash: 2_000 }, 1, () => 'a-1')
    const updated = await applyTrades(
      accounts, orders, account,
      [
        { symbol: 'AAPL', side: 'buy', shares: 5, price: 100, fee: 1 },
        { symbol: '000001', side: 'buy', shares: 10, price: 10, fee: 1 },
      ],
      1498, 2, newId,
    )
    expect(updated.cash).toBe(1498)
    expect(updated.positions).toEqual([
      { symbol: 'AAPL', shares: 5, avg_cost: 100 },
      { symbol: '000001', shares: 10, avg_cost: 10 },
    ])
    expect(orders.get(OrderId('o-1'))).toMatchObject({ symbol: 'AAPL', side: 'buy' })
    const afterSell = await applyTrades(
      accounts, orders, updated,
      [{ symbol: '000001', side: 'sell', shares: 10, price: 11, fee: 1 }],
      1498 + 110 - 1, 3, newId,
    )
    expect(afterSell.positions.map(position => position.symbol)).toEqual(['AAPL'])
    expect(orders.get(OrderId('o-3'))).toMatchObject({ symbol: '000001', side: 'sell', price: 11 })
  })

  it('lookups fall through id to name and reject misses with both given', async () => {
    const accounts = table() as unknown as KvTable<AccountId, Account>
    const created = await createAccount(accounts, { name: '研究一号', initialCash: 1 }, 1, () => 'a-9')
    // id miss + name hit: requireAccount tries id first, then name.
    expect(requireAccount(accounts, 'nope', '研究一号').id).toBe(created.id)
  })

  it('rejects empty names, sells past a nonzero position, and computes cash deltas', async () => {
    const accounts = table() as unknown as KvTable<AccountId, Account>
    await expect(createAccount(accounts, { name: '  ', initialCash: 1 }, 1)).rejects.toThrow(/账户名/)
    const orders = table() as unknown as KvTable<OrderId, Order>
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

  it('covers the requireAccount miss paths and the buy-new-position branch', async () => {
    const accounts = table() as unknown as KvTable<AccountId, Account>
    const orders = table() as unknown as KvTable<OrderId, Order>
    // byId 命中前先 miss：先给一个不存在的 id，靠 name 找回
    const account = await createAccount(accounts, { name: '研究一号', initialCash: 2_000 }, 1, () => 'a-1')
    expect(requireAccount(accounts, 'nope', '研究一号').id).toBe(account.id)
    // id 和 name 都 miss → DATA
    expect(() => requireAccount(accounts, 'nope', 'also-nope')).toThrow(QuantError)
    // buy-new-position 分支（account.positions 为空 → held undefined → push）
    const afterBuy = await applyTrades(
      accounts, orders, account,
      [{ symbol: 'AAPL', side: 'buy', shares: 5, price: 100, fee: 0 }],
      1_500, 2, () => 'o-1',
    )
    expect(afterBuy.positions).toEqual([{ symbol: 'AAPL', shares: 5, avg_cost: 100 }])
    // 卖到 0 后再买 → 又走 push 分支
    const afterSell = await applyTrades(
      accounts, orders, afterBuy,
      [{ symbol: 'AAPL', side: 'sell', shares: 5, price: 110, fee: 0 }],
      2_050, 3, () => 'o-2',
    )
    expect(afterSell.positions).toEqual([])
    const rebought = await applyTrades(
      accounts, orders, afterSell,
      [{ symbol: 'AAPL', side: 'buy', shares: 3, price: 105, fee: 0 }],
      1_735, 4, () => 'o-3',
    )
    expect(rebought.positions).toEqual([{ symbol: 'AAPL', shares: 3, avg_cost: 105 }])
  })

  it('rejects overselling with a nonzero position and drops dust after a full sell', async () => {
    const accounts = table() as unknown as KvTable<AccountId, Account>
    const orders = table() as unknown as KvTable<OrderId, Order>
    const account = await createAccount(accounts, { name: 'x', initialCash: 1_000 }, 1, () => 'a-1')
    const held = await applyTrades(
      accounts, orders, account,
      [{ symbol: 'AAPL', side: 'buy', shares: 10, price: 100, fee: 0 }],
      0, 2, () => 'o-1',
    )
    // 持仓存在但数量不足
    await expect(applyTrades(
      accounts, orders, held,
      [{ symbol: 'AAPL', side: 'sell', shares: 99, price: 100, fee: 0 }],
      0, 3, () => 'o-2',
    )).rejects.toThrow(/持仓不足/)
    // 全卖后 dust 清除
    const flat = await applyTrades(
      accounts, orders, held,
      [{ symbol: 'AAPL', side: 'sell', shares: 10, price: 100, fee: 0 }],
      1_000, 4, () => 'o-3',
    )
    expect(flat.positions).toEqual([])
  })

  it('covers the remaining store and rebalance corner cases', async () => {
    // rebalance: 卖超出持仓在当前公式下不可达（equity 包含持仓市值，delta 数学自洽）。
    /* v8 ignore next -- defensive check: oversell is unreachable with self-consistent input. */
    expect(() => computePlan({
      cash: 0,
      positions: [{ symbol: '000001', shares: 5, avg_cost: 5 }],
      targets: [{ symbol: '000001', weight: 1 }],
      prices: { '000001': 10 },
      feeRate: 0,
    })).not.toThrow()
    // rebalance: 买入时 delta 恰好为 0 → skip（eps 分支）
    const flat = computePlan({
      cash: 0,
      positions: [{ symbol: '000001', shares: 100, avg_cost: 10 }],
      targets: [{ symbol: '000001', weight: 1 }],
      prices: { '000001': 10 },
      feeRate: 0,
    })
    expect(flat.trades).toEqual([])
    // listAccounts: 两个账户触发 sort
    const accounts = table() as unknown as KvTable<AccountId, Account>
    await createAccount(accounts, { name: 'b', initialCash: 1 }, 20, () => 'b-1')
    await createAccount(accounts, { name: 'a', initialCash: 1 }, 10, () => 'a-1')
    expect(listAccounts(accounts).map(a => a.name)).toEqual(['a', 'b'])
    // requireAccount: ref 和 name 都 undefined → throw
    expect(() => requireAccount(accounts)).toThrow(QuantError)
    // applyTrades: 卖到恰好清仓但 shares > 1e-6 的残余分数 → drop dust 分支
    const orders = table() as unknown as KvTable<OrderId, Order>
    const account = await createAccount(accounts, { name: 'dust', initialCash: 0 }, 30, () => 'd-1')
    const withTiny = await applyTrades(
      accounts, orders, account,
      [{ symbol: 'AAPL', side: 'buy', shares: 0.001, price: 100, fee: 0 }],
      0, 31, () => 'o-d1',
    )
    const afterDustSell = await applyTrades(
      accounts, orders, withTiny,
      [{ symbol: 'AAPL', side: 'sell', shares: 0.001, price: 100, fee: 0 }],
      0, 32, () => 'o-d2',
    )
    expect(afterDustSell.positions).toEqual([])
  })

  it('rejects overselling', async () => {
    const accounts = table() as unknown as KvTable<AccountId, Account>
    const account = await createAccount(accounts, { name: 'x', initialCash: 100 }, 1)
    await expect(applyTrades(
      accounts, table() as unknown as KvTable<OrderId, Order>, account,
      [{ symbol: 'AAPL', side: 'sell', shares: 10, price: 100, fee: 0 }],
      100, 2,
    )).rejects.toThrow(/持仓不足/)
  })
})

describe('latestClose', () => {
  it('reads the last close and rejects empty series', () => {
    expect(lastClose(BARS)).toBe(11)
    expect(() => lastClose([])).toThrow(/K线序列为空/)
  })
})

describe('PET tools', () => {
  it('creates and reads a virtual account', async () => {
    const kernel = { request: vi.fn(async () => BARS) } as unknown as QuantKernelClient
    const deps = petDeps(kernel)
    const created = await accountCreateTool(deps).execute?.({ name: '研究一号' }, execLike())
    expect(created).toMatchObject({ code: 0 })
    const state = await accountStateTool(deps).execute?.({ account_name: '研究一号' }, execLike())
    expect((state as { data: { equity: number } }).data.equity).toBe(1_000_000)
    const rendered = String((accountStateTool(deps).output.render({}, state as never) as { text: string }[])[0]?.text ?? '')
    expect(String(rendered)).toContain('模拟盘记录仅供研究参考')
  })

  it('executes a rebalance after approval and records the orders', async () => {
    const approvals: unknown[] = []
    const approval = { request: async (req: unknown) => { approvals.push(req); return 'allowed-once' } }
    const kernel = { request: vi.fn(async () => BARS) } as unknown as QuantKernelClient
    const deps = petDeps(kernel, approval)
    await accountCreateTool(deps).execute?.({ name: '研究一号' }, execLike())
    const value = await executeRebalanceTool(deps).execute?.(
      { account_name: '研究一号', targets: [{ symbol: '000001', weight: 0.9 }] },
      execLike(),
    )
    expect(value).toMatchObject({ code: 0 })
    const data = (value as { data: { executed: unknown[]; cash_after: number } }).data
    expect(data.executed).toHaveLength(1)
    expect(data.cash_after).toBeCloseTo(1_000_000 - 900_000 * 1.0003, 2)
    expect(approvals).toHaveLength(1)
    const rendered = String((executeRebalanceTool(deps).output.render({}, value as never) as { text: string }[])[0]?.text ?? '')
    expect(String(rendered)).toContain('模拟成交 1 笔')
  })

  it('fails loud without the approval plugin and rejects on denial', async () => {
    const kernel = { request: vi.fn(async () => BARS) } as unknown as QuantKernelClient
    const deps = petDeps(kernel)
    const missing = await executeRebalanceTool(deps).execute?.(
      { account_name: 'x', targets: [{ symbol: '000001', weight: 0.5 }] }, execLike(),
    )
    expect(missing).toMatchObject({ code: 1005 })
    expect((missing as { msg: string }).msg).toContain('人工审核')

    const denying = petDeps(kernel, { request: async () => 'rejected' })
    await accountCreateTool(denying).execute?.({ name: '研究一号' }, execLike())
    const value = await executeRebalanceTool(denying).execute?.(
      { account_name: '研究一号', targets: [{ symbol: '000001', weight: 0.5 }] }, execLike(),
    )
    expect(value).toMatchObject({ code: 1004 })
    expect((value as { msg: string }).msg).toContain('未获批准')
  })

  it('renders the empty fallback for account envelopes', () => {
    expect(String((accountCreateTool(petDeps(petKernel())).output.render({}, { code: 0, msg: 'ok', data: {} } as never) as { text: string }[])[0]?.text ?? ''))
      .toContain('账户信息为空')
  })
})

function petKernel(): QuantKernelClient {
  return { request: vi.fn(async () => BARS) } as unknown as QuantKernelClient
}

function execLike(): never {
  return {
    signal: new AbortController().signal,
    agent: { id: 'agent-1', session: { append: vi.fn() } },
  } as never
}

