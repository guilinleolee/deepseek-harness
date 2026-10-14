/**
 * Backtest result-snapshot tests: downsample geometry, save+prune, list
 * order, and the missing-id rejection.
 */
import { describe, expect, it } from 'vitest'
import type { KvTable } from '@deepseek-ai/dsh-storage-domain'
import { ResultSnapshotId } from '../src/domain/spec.ts'
import type { ResultSnapshot } from '../src/domain/spec.ts'
import type { BacktestReport } from '../src/pcpt/backtest.ts'
import {
  EQUITY_SNAPSHOT_MAX_POINTS, SNAPSHOT_KEEP_LIMIT, downsampleEquity, listSnapshots,
  requireSnapshot, saveSnapshot,
} from '../src/pcpt/snapshots.ts'
import type { ResultSnapshotsTable } from '../src/pcpt/snapshots.ts'

function table(): ResultSnapshotsTable {
  const store = new Map<ResultSnapshotId, ResultSnapshot>()
  return {
    entries: () => store.entries(),
    get size() { return store.size },
    get: (key: ResultSnapshotId) => store.get(key),
    put: async (key: ResultSnapshotId, value: ResultSnapshot) => { store.set(key, value) },
    delete: async (key: ResultSnapshotId) => { store.delete(key) },
  } as unknown as ResultSnapshotsTable
}

/** A synthetic equity curve with `count` evenly valued points. */
function equityCurve(count: number): { date: string; value: number }[] {
  return Array.from({ length: count }, (_, index) => ({
    date: `2024-01-${String(index + 1).padStart(2, '0')}`,
    value: 100 + index,
  }))
}

function report(overrides?: Partial<BacktestReport>): BacktestReport {
  return {
    symbol: '000001',
    fast: 3,
    slow: 10,
    initial_cash: 100000,
    final_equity: 105000,
    equity: equityCurve(5),
    trades: [],
    metrics: {
      total_return: 0.05,
      annual_return: 0.4,
      max_drawdown: 0.03,
      sharpe: 1.2,
      win_rate: 0.6,
      trade_count: 4,
    },
    ...overrides,
  }
}

describe('downsampleEquity', () => {
  it('keeps short curves untouched', () => {
    const curve = equityCurve(5)
    expect(downsampleEquity(curve)).toEqual(curve.map(p => ({ date: p.date, value: p.value })))
  })

  it('caps long curves at the hard limit and always keeps the last point', () => {
    const curve = equityCurve(EQUITY_SNAPSHOT_MAX_POINTS * 3)
    const down = downsampleEquity(curve)
    expect(down).toHaveLength(EQUITY_SNAPSHOT_MAX_POINTS)
    expect(down[0]).toEqual({ date: curve[0]!.date, value: curve[0]!.value })
    expect(down.at(-1)).toEqual({ date: curve.at(-1)!.date, value: curve.at(-1)!.value })
    // Deterministic stride: the same input maps to the same picks.
    expect(downsampleEquity(curve)).toEqual(down)
  })
})

describe('saveSnapshot / listSnapshots', () => {
  it('stores params, metrics, and the downsampled curve', async () => {
    const t = table()
    const snapshot = await saveSnapshot(
      t,
      { symbol: '000001', params: { fast: 3, slow: 10, bars: 60, initialCash: 100000, feeRate: 0.0005 }, report: report() },
      100,
      () => 'r-1',
    )
    expect(snapshot.kind).toBe('backtest')
    expect(snapshot.params).toEqual({ fast: 3, slow: 10, bars: 60, initial_cash: 100000, fee_rate: 0.0005 })
    expect(snapshot.metrics.trade_count).toBe(4)
    expect(snapshot.metrics.final_equity).toBe(105000)
    expect(snapshot.equity).toHaveLength(5)
    expect(requireSnapshot(t, 'r-1')).toEqual(snapshot)
  })

  it('lists newest first and prunes beyond the keep limit', async () => {
    const t = table()
    for (let index = 0; index < SNAPSHOT_KEEP_LIMIT + 3; index += 1) {
      await saveSnapshot(
        t,
        { symbol: '000001', params: { fast: 3, slow: 10, bars: 60, initialCash: 100000, feeRate: 0.0005 }, report: report() },
        index,
        () => `r-${String(index)}`,
      )
    }
    const all = listSnapshots(t)
    expect(all).toHaveLength(SNAPSHOT_KEEP_LIMIT)
    expect(all[0]?.id).toBe(`r-${String(SNAPSHOT_KEEP_LIMIT + 2)}`)
    expect(all.map(s => s.created_at)).toEqual([...all.map(s => s.created_at)].sort((a, b) => b - a))
  })

  it('requireSnapshot rejects a missing id', () => {
    const t = table()
    expect(() => requireSnapshot(t, 'missing')).toThrow(/未找到回测快照/)
  })
})
