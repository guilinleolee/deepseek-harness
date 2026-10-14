/**
 * Snapshot tool tests: list rendering, delete through approval (granted,
 * denied, missing runtime), and the missing-id rejection.
 */
import { describe, expect, it, vi } from 'vitest'
import { resolveConfig } from '../src/config.ts'
import { DataSourceBreaker } from '../src/pdat/datasource.ts'
import { saveSnapshot } from '../src/pcpt/snapshots.ts'
import type { ResultSnapshotsTable } from '../src/pcpt/snapshots.ts'
import type { BacktestReport } from '../src/pcpt/backtest.ts'
import { snapshotDeleteTool, snapshotListTool } from '../src/tools.ts'
import type { QuantToolDeps } from '../src/tools.ts'
import type { ToolDefinition } from '@deepseek-ai/dsh-tools'
import type { QuantKernelClient } from '../src/kernel-client/client.ts'

const ENV = { platform: 'linux' as const, dshHome: '/home/tester/.dsh' }
const CONFIG = resolveConfig(undefined, ENV)

/** A put-able in-memory snapshot table. */
function snapshotTable(): ResultSnapshotsTable & { store: Map<string, unknown> } {
  const store = new Map<string, unknown>()
  return {
    store,
    entries: () => store.entries(),
    get size() { return store.size },
    get: (key: string) => store.get(key),
    put: async (key: string, value: unknown) => { store.set(key, value) },
    delete: async (key: string) => { store.delete(key) },
  } as never
}

const REPORT: BacktestReport = {
  symbol: '000001',
  fast: 3,
  slow: 10,
  initial_cash: 100_000,
  final_equity: 105_000,
  equity: [{ date: '2024-01-01', value: 100_000 }, { date: '2024-01-02', value: 105_000 }],
  trades: [],
  metrics: { total_return: 0.05, annual_return: 0.4, max_drawdown: 0.03, sharpe: 1.2, win_rate: 0.6, trade_count: 4 },
}

function deps(snapshots: ResultSnapshotsTable, approval?: unknown): QuantToolDeps {
  return {
    config: CONFIG,
    kernel: {} as QuantKernelClient,
    breaker: new DataSourceBreaker(3),
    accounts: new Map() as never,
    orders: new Map() as never,
    notes: new Map() as never,
    snapshots,
    ...(approval === undefined ? {} : { approval: approval as QuantToolDeps['approval'] }),
  }
}

/** An exec carrying an agent session (approval charges per turn). */
const execWithAgent = { signal: new AbortController().signal, agent: { id: 'session-1' } } as never
const execNoAgent = { signal: new AbortController().signal, agent: undefined } as never

/** First text block of a render result. */
function textOf(blocks: unknown): string {
  return (blocks as { text?: string }[])[0]?.text ?? ''
}

async function seed(table: ResultSnapshotsTable, count: number): Promise<void> {
  for (let index = 0; index < count; index += 1) {
    await saveSnapshot(
      table,
      { symbol: index % 2 === 0 ? '000001' : '600519', params: { fast: 3, slow: 10, bars: 60, initialCash: 100_000, feeRate: 0.0005 }, report: REPORT },
      1_000 + index,
      () => `r-${String(index)}`,
    )
  }
}

describe('quant_list_snapshots', () => {
  it('renders the newest-first list with headline metrics', async () => {
    const table = snapshotTable()
    await seed(table, 3)
    const tool: ToolDefinition = snapshotListTool(deps(table))
    const value = await tool.execute?.({}, execNoAgent)
    expect(value).toMatchObject({ code: 0 })
    const data = (value as { data: { snapshots: { result_id: string }[] } }).data
    expect(data.snapshots.map(s => s.result_id)).toEqual(['r-2', 'r-1', 'r-0'])
    const rendered = textOf(tool.output?.render({}, value as never))
    expect(rendered).toContain('共 3 条快照')
    expect(rendered).toContain('000001')
    expect(rendered).toContain('SMA(3/10)')
    expect(rendered).toContain('5.00%')
    expect(rendered).toContain('仅供研究参考')
  })

  it('renders the empty list', async () => {
    const tool: ToolDefinition = snapshotListTool(deps(snapshotTable()))
    const value = await tool.execute?.({}, execNoAgent)
    expect(textOf(tool.output?.render({}, value as never))).toContain('快照列表为空')
  })
})

describe('quant_delete_snapshot', () => {
  it('deletes after an allowed-once approval and reports the symbol', async () => {
    const table = snapshotTable()
    await seed(table, 2)
    const request = vi.fn(async () => 'allowed-once' as const)
    const tool: ToolDefinition = snapshotDeleteTool(deps(table, { request }))
    const value = await tool.execute?.({ result_id: 'r-1', reason: '清理过期运行' }, execWithAgent)
    expect(value).toMatchObject({ code: 0, data: { result_id: 'r-1', symbol: '600519', deleted: true } })
    expect(table.size).toBe(1)
    expect(request).toHaveBeenCalledWith(expect.objectContaining({ toolName: 'quant_delete_snapshot' }))
    const ask = (request.mock.calls[0] as unknown[])[0] as { reason: string }
    const reason = ask.reason
    expect(reason).toContain('600519')
    expect(reason).toContain('清理过期运行')
    const rendered = textOf(tool.output?.render({}, value as never))
    expect(rendered).toContain('已删除回测快照')
  })

  it('keeps the record when the approval denies', async () => {
    const table = snapshotTable()
    await seed(table, 1)
    const tool: ToolDefinition = snapshotDeleteTool(deps(table, { request: vi.fn(async () => 'rejected' as const) }))
    const value = await tool.execute?.({ result_id: 'r-0', reason: 'x' }, execWithAgent)
    expect(value).toMatchObject({ code: 1004 })
    expect((value as { msg: string }).msg).toContain('未获批准')
    expect(table.size).toBe(1)
  })

  it('fails loud without an approval runtime or an agent session', async () => {
    const table = snapshotTable()
    await seed(table, 1)
    const noRuntime = await snapshotDeleteTool(deps(table)).execute?.({ result_id: 'r-0', reason: 'x' }, execWithAgent)
    expect((noRuntime as { msg: string }).msg).toContain('人工审核')
    const noAgent = await snapshotDeleteTool(deps(table, { request: vi.fn() })).execute?.({ result_id: 'r-0', reason: 'x' }, execNoAgent)
    expect((noAgent as { msg: string }).msg).toContain('agent 会话')
  })

  it('rejects a missing snapshot before any approval is asked', async () => {
    const table = snapshotTable()
    const request = vi.fn(async () => 'allowed-once' as const)
    const value = await snapshotDeleteTool(deps(table, { request })).execute?.({ result_id: 'missing', reason: 'x' }, execWithAgent)
    expect((value as { code: number }).code).not.toBe(0)
    expect((value as { msg: string }).msg).toContain('未找到回测快照')
    expect(request).not.toHaveBeenCalled()
  })
})
