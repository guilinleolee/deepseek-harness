import { describe, expect, it, vi } from 'vitest'
import { JobId } from '@deepseek-ai/dsh-jobs'
import type { JobHooks, JobSpec } from '@deepseek-ai/dsh-jobs'
import { resolveConfig } from '../src/config.ts'
import { DataSourceBreaker } from '../src/pdat/datasource.ts'
import { DEFAULT_GRID_SPEC } from '../src/compliance.ts'
import { inspectTrainRatioCap } from '../src/compliance.ts'
import {
  ANCHOR_LIMITS, ROLLING_WINDOWS_LIMITS, formatRollingWalkForwardSummary, formatWalkForwardSummary,
  runRollingWalkForward, runWalkForward, splitAnchoredWindows, splitBars, splitRollingWindows,
  validateAnchoredParams, validateRollingParams,
  validateWalkForwardParams,
} from '../src/pcpt/walk-forward.ts'
import type { RollingWindow, WalkForwardSplit } from '../src/pcpt/walk-forward.ts'
import { inspectAnchorCap, inspectRollingWindowsCap } from '../src/compliance.ts'
import type { BacktestReport, BacktestMetrics } from '../src/pcpt/backtest.ts'
import type { GridComboResult, GridSpec } from '../src/pcpt/optimize.ts'
import { walkForwardTool } from '../src/tools.ts'
import type { QuantToolDeps } from '../src/tools.ts'
import type { ToolDefinition } from '@deepseek-ai/dsh-tools'
import type { QuantKernelClient } from '../src/kernel-client/client.ts'

const ENV = { platform: 'linux' as const, dshHome: '/home/tester/.dsh' }
const CONFIG = resolveConfig(undefined, ENV)

const BARS = Array.from({ length: 250 }, (_, index) => ({
  date: `2024-${String(Math.floor(index / 28) + 1).padStart(2, '0')}-${String((index % 28) + 1).padStart(2, '0')}`,
  open: 10 + index,
  high: 11 + index,
  low: 9 + index,
  close: 10.5 + index,
  volume: 1000 + index,
}))

const combo = (fast: number, slow: number, totalReturn: number, sharpe: number, drawdown: number): GridComboResult => ({
  fast,
  slow,
  final_equity: 1_000_000 * (1 + totalReturn),
  metrics: {
    total_return: totalReturn,
    annual_return: totalReturn,
    max_drawdown: drawdown,
    sharpe,
    win_rate: 0.5,
    trade_count: 2,
  } as BacktestMetrics,
})

const metrics = (totalReturn: number, sharpe: number, drawdown: number): BacktestMetrics => ({
  total_return: totalReturn,
  annual_return: totalReturn,
  max_drawdown: drawdown,
  sharpe,
  win_rate: 0.5,
  trade_count: 2,
})

const report = (fast: number, slow: number, totalReturn: number, sharpe: number, drawdown: number): BacktestReport => ({
  symbol: '000001',
  fast,
  slow,
  initial_cash: 1_000_000,
  final_equity: 1_000_000 * (1 + totalReturn),
  equity: [{ date: '2024-03-01', value: 1_000_000 }, { date: '2024-03-31', value: 1_000_000 * (1 + totalReturn) }],
  trades: [],
  metrics: metrics(totalReturn, sharpe, drawdown),
})

const SPEC: GridSpec = { fast: { min: 5, max: 20, step: 5 }, slow: { min: 30, max: 60, step: 10 } }

describe('splitBars', () => {
  it('splits at an integer cut, both legs non-empty', () => {
    const split = splitBars(BARS, 0.7)
    expect(split.train.length).toBe(175) // ceil(250 * 0.7)
    expect(split.test.length).toBe(75)
    expect(split.train[0]?.date).toBe(BARS[0]?.date)
    expect(split.test[0]?.date).toBe(BARS[175]?.date)
    expect(split.test[split.test.length - 1]?.date).toBe(BARS[249]?.date)
  })

  it('respects the ratio bounds and keeps at least one bar per leg', () => {
    const half = splitBars(BARS.slice(0, 3), 0.5)
    expect(half.train.length).toBe(2)
    expect(half.test.length).toBe(1)
    const high = splitBars(BARS.slice(0, 10), 0.9)
    expect(high.train.length).toBe(9)
    expect(high.test.length).toBe(1)
  })
})

describe('validateWalkForwardParams', () => {
  it('accepts a valid spec and ratio with enough bars on both legs', () => {
    expect(() => validateWalkForwardParams(250, SPEC, 0.7)).not.toThrow()
    expect(() => validateWalkForwardParams(250, DEFAULT_GRID_SPEC as unknown as GridSpec, 0.5)).not.toThrow()
  })

  it('rejects ratios outside the hard bounds', () => {
    expect(() => validateWalkForwardParams(120, SPEC, 0.4)).toThrow('train_ratio')
    expect(() => validateWalkForwardParams(120, SPEC, 0.95)).toThrow('train_ratio')
    expect(() => validateWalkForwardParams(120, SPEC, Number.NaN)).toThrow('train_ratio')
  })

  it('rejects when the test leg cannot cover the widest slow window', () => {
    // train 0.9 of 80 = 72, test = 8, but slow.max = 60 → need ≥ 61.
    expect(() => validateWalkForwardParams(80, SPEC, 0.9)).toThrow('测试段长度')
  })

  it('rejects grid-spec invariants through the delegate', () => {
    expect(() => validateWalkForwardParams(250, { ...SPEC, fast: { min: 1, max: 20, step: 5 } }, 0.7)).toThrow('2-120')
  })
})

describe('inspectTrainRatioCap', () => {
  it('allows absent fields and the defaults', () => {
    expect(inspectTrainRatioCap({})).toEqual({ kind: 'allow' })
    expect(inspectTrainRatioCap({ train_ratio: 0.7 })).toEqual({ kind: 'allow' })
    expect(inspectTrainRatioCap({ train_ratio: 0.5 })).toEqual({ kind: 'allow' })
    expect(inspectTrainRatioCap({ train_ratio: 0.9 })).toEqual({ kind: 'allow' })
  })

  it('denies ratios outside the hard bounds and non-numbers', () => {
    expect(inspectTrainRatioCap({ train_ratio: 0.4 })).toMatchObject({ kind: 'deny' })
    expect(inspectTrainRatioCap({ train_ratio: 0.95 })).toMatchObject({ kind: 'deny' })
    expect(inspectTrainRatioCap({ train_ratio: 'high' })).toMatchObject({ kind: 'deny' })
  })

})

function kernelByOp(handler: (op: string, params: Record<string, unknown>) => unknown): QuantKernelClient {
  return {
    request: vi.fn(async (op: string, params: Record<string, unknown>) => handler(op, params)),
  } as unknown as QuantKernelClient
}

/** Walk-forward kernel: get_kline → BARS; first backtest_grid → train results; backtest → test report. */
function walkForwardKernel(trainResults: GridComboResult[], testReport: BacktestReport): QuantKernelClient {
  let gridCalled = false
  return kernelByOp((op) => {
    if (op === 'get_kline') return BARS
    if (op === 'backtest_grid') {
      gridCalled = true
      return { symbol: '000001', count: trainResults.length, results: trainResults }
    }
    if (op === 'backtest') {
      if (!gridCalled) throw new Error('test leg ran before train leg')
      return testReport
    }
    return {}
  })
}

describe('runWalkForward', () => {
  it('runs the train grid, picks the best, and runs the test leg on the best params', async () => {
    const trainResults = [combo(5, 30, 0.1, 1.2, 0.05), combo(10, 30, 0.2, 0.8, 0.1)]
    const testReport = report(10, 30, 0.05, 0.6, 0.08)
    const kernel = walkForwardKernel(trainResults, testReport)
    const split: WalkForwardSplit = { train: BARS.slice(0, 175), test: BARS.slice(175) }
    const result = await runWalkForward(
      kernel, '000001', split, SPEC, 1_000_000, 0.0003, 'sharpe', 2,
    )
    expect(result.trainResults).toHaveLength(2)
    expect(result.ranked[0]?.fast).toBe(5) // sharpe 1.2 > 0.8
    expect(result.testReport).toEqual(testReport)
    const ops = (kernel.request as ReturnType<typeof vi.fn>).mock.calls.map(call => call[0])
    expect(ops).toEqual(['backtest_grid', 'backtest'])
    const testParams = (kernel.request as ReturnType<typeof vi.fn>).mock.calls[1]?.[1] as Record<string, unknown>
    expect(testParams).toMatchObject({ fast: 5, slow: 30, initial_cash: 1_000_000, fee_rate: 0.0003 })
  })

  it('rejects a malformed grid response with a friendly wire-shape error', async () => {
    const kernel = walkForwardKernel([], report(5, 30, 0, 0, 0))
    const split: WalkForwardSplit = { train: BARS.slice(0, 175), test: BARS.slice(175) }
    await expect(runWalkForward(kernel, '000001', split, SPEC, 1_000_000, 0.0003, 'sharpe', 2))
      .rejects.toThrow('不符合规格')
  })
})

describe('formatWalkForwardSummary', () => {
  it('renders the split, train table, OOS metrics, and the overfitting gap', () => {
    const ranked = [combo(5, 30, 0.2, 1.4, 0.05)]
    const testReport = report(5, 30, 0.05, 0.6, 0.08)
    const markdown = formatWalkForwardSummary('000001', SPEC, ranked, testReport, 0.7, 16, 'sharpe')
    expect(markdown).toContain('# Walk-forward 验证报告：000001')
    expect(markdown).toContain('训练段比例：0.7')
    expect(markdown).toContain('## 训练段寻优')
    expect(markdown).toContain('## 样本外测试（用训练段最优参数）')
    expect(markdown).toContain('SMA(5/30)')
    expect(markdown).toContain('## 过拟合差距')
    expect(markdown).toContain('总收益差距')
    expect(markdown).toContain('过拟合')
    expect(markdown).toContain('仅供研究参考')
  })

  it('renders the empty-ranked fallback paths (best undefined, trainMetrics undefined, gap zero)', () => {
    const testReport = report(5, 30, 0.05, 0.6, 0.08)
    const markdown = formatWalkForwardSummary('000001', SPEC, [], testReport, 0.7, 0, 'sharpe')
    expect(markdown).toContain('SMA(?/?)')
    expect(markdown).toContain('总收益差距')
    expect(markdown).toContain('0.00%')
    expect(markdown).toContain('（无结果）')
  })
})

/** Capturing fake registry: records every start and hands back its hooks. */
function fakeJobs(): {
  face: { start(spec: JobSpec): ReturnType<typeof JobId> }
  specs: JobSpec[]
  hooksOf(spec: JobSpec): JobHooks
} {
  const specs: JobSpec[] = []
  const hooksByIndex = new Map<JobSpec, JobHooks>()
  let counter = 0
  return {
    face: {
      start(spec: JobSpec): ReturnType<typeof JobId> {
        specs.push(spec)
        counter += 1
        const hooks = spec.run()
        hooksByIndex.set(spec, hooks)
        return JobId(`quant-walk-forward-${String(counter)}`)
      },
    },
    specs,
    hooksOf: (spec: JobSpec): JobHooks => hooksByIndex.get(spec) as JobHooks,
  }
}

function depsWith(kernel: QuantKernelClient, jobs?: () => unknown): QuantToolDeps {
  const store = new Map<string, unknown>()
  const base: QuantToolDeps = {
    config: CONFIG,
    kernel,
    breaker: new DataSourceBreaker(3),
    accounts: new Map() as never,
    orders: new Map() as never,
    notes: new Map() as never,
    snapshots: {
      entries: () => store.entries(),
      get size() { return store.size },
      get: (key: string) => store.get(key),
      put: async (key: string, value: unknown) => { store.set(key, value) },
      delete: async (key: string) => { store.delete(key) },
    } as never,
  }
  return { ...(jobs === undefined ? base : { ...base, jobs: jobs as QuantToolDeps['jobs'] }), store } as ReturnType<typeof depsWith>
}

describe('quant_walk_forward rolling', () => {
  const exec = { signal: new AbortController().signal, agent: undefined } as never

  it('starts a rolling job on windows >= 2 and settles with the rolling markdown', async () => {
    const jobs = fakeJobs()
    const trainResults = [combo(5, 30, 0.2, 1.0, 0.05), combo(10, 30, 0.1, 0.5, 0.1)]
    const kernel = walkForwardKernel(trainResults, report(5, 30, 0.12, 0.6, 0.08))
    const deps = depsWith(kernel, () => jobs.face)
    const tool: ToolDefinition = walkForwardTool(deps)
    const value = await tool.execute?.({ symbol: '000001', bars: 400, windows: 2, top_n: 5 }, exec)
    const data = (value as { code: number; data: { job_id: string; windows?: number; combos: number } }).data
    expect(data.job_id).toBe('quant-walk-forward-1')
    expect(data.windows).toBe(2)
    expect(data.combos).toBe(16)
    expect(jobs.specs[0]?.label).toContain('滚动 walk-forward 2 窗')
    const outcome = await jobs.hooksOf(jobs.specs[0] as JobSpec).done
    expect(outcome.status).toBe('completed')
    expect(outcome.result).toContain('# 滚动 Walk-forward 验证报告：000001')
    expect(outcome.detail).toContain('2 窗聚合')
    // One kline fetch, then one grid + one backtest per window.
    const ops = (kernel.request as ReturnType<typeof vi.fn>).mock.calls.map(call => call[0])
    expect(ops).toEqual(['get_kline', 'backtest_grid', 'backtest', 'backtest_grid', 'backtest'])
    // Each window's out-of-sample report is persisted as one snapshot.
    expect(deps.store.size).toBe(2)
    const stored = [...deps.store.values()] as { symbol: string; kind: string }[]
    expect(stored.every(entry => entry.symbol === '000001' && entry.kind === 'backtest')).toBe(true)
  })

  it('runs an anchored rolling job and labels the mode', async () => {
    const jobs = fakeJobs()
    const kernel = walkForwardKernel([combo(5, 30, 0.2, 1.0, 0.05), combo(10, 30, 0.1, 0.5, 0.1)], report(5, 30, 0.12, 0.6, 0.08))
    const deps = depsWith(kernel, () => jobs.face)
    const tool: ToolDefinition = walkForwardTool(deps)
    const value = await tool.execute?.({ symbol: '000001', bars: 400, windows: 2, anchor: 100, top_n: 5 }, exec)
    const data = (value as { data: { windows?: number; anchor?: number } }).data
    expect(data.windows).toBe(2)
    expect(data.anchor).toBe(100)
    expect(jobs.specs[0]?.label).toContain('（锚定）')
    const outcome = await jobs.hooksOf(jobs.specs[0] as JobSpec).done
    expect(outcome.status).toBe('completed')
    expect(outcome.result).toContain('滚动切分（锚定窗）')
    expect(outcome.result).toContain('锚定训练窗 100 根')
  })

  it('denies windows outside the compliance bounds before any job starts', async () => {
    const jobs = fakeJobs()
    const tool: ToolDefinition = walkForwardTool(depsWith(walkForwardKernel([], report(5, 30, 0, 0, 0)), () => jobs.face))
    const value = await tool.execute?.({ symbol: '000001', windows: 11 }, exec)
    expect((value as { code: number }).code).not.toBe(0)
    expect((value as { msg: string }).msg).toContain('windows')
    expect(jobs.specs).toHaveLength(0)
  })
})

describe('quant_walk_forward', () => {
  const exec = { signal: new AbortController().signal, agent: undefined } as never

  it('fails with a friendly CONFIG envelope when no jobs runtime is composed', async () => {
    const tool: ToolDefinition = walkForwardTool(depsWith(walkForwardKernel([], report(5, 30, 0, 0, 0))))
    const value = await tool.execute?.({ symbol: '000001' }, exec)
    expect((value as { code: number }).code).not.toBe(0)
    expect((value as { data: unknown }).data).toBeNull()
    expect((value as { msg: string }).msg).toContain('后台任务运行时')
  })

  it('starts one job, renders the split, and settles with the walk-forward markdown', async () => {
    const jobs = fakeJobs()
    const trainResults = [combo(5, 30, 0.1, 1.2, 0.05), combo(10, 30, 0.2, 0.8, 0.1)]
    const testReport = report(5, 30, 0.05, 0.6, 0.08)
    const kernel = walkForwardKernel(trainResults, testReport)
    const tool: ToolDefinition = walkForwardTool(depsWith(kernel, () => jobs.face))
    const value = await tool.execute?.({ symbol: '000001', bars: 250, top_n: 5 }, exec)
    const data = (value as { code: number; data: { job_id: string; combos: number; train_ratio: number; hint: string } }).data
    expect(data.job_id).toBe('quant-walk-forward-1')
    expect(data.combos).toBe(16)
    expect(data.train_ratio).toBe(0.7)
    expect(data.hint).toContain('job_output')
    const rendered = (tool.output?.render({}, value as never) as { text?: string }[])[0]?.text ?? ''
    expect(rendered).toContain('quant-walk-forward-1')
    expect(rendered).toContain('训练 70% / 测试 30%')
    expect(rendered).toContain('共 16 组合')
    expect(rendered).toContain('仅供研究参考')

    expect(jobs.specs).toHaveLength(1)
    expect(jobs.specs[0]?.kind).toBe('quant-walk-forward')
    expect(jobs.specs[0]?.label).toContain('16 组合')
    const outcome = await jobs.hooksOf(jobs.specs[0] as JobSpec).done
    expect(outcome.status).toBe('completed')
    expect(outcome.result).toContain('# Walk-forward 验证报告：000001')
    expect(outcome.detail).toContain('SMA(')
    const ops = (kernel.request as ReturnType<typeof vi.fn>).mock.calls.map(call => call[0])
    expect(ops).toEqual(['get_kline', 'backtest_grid', 'backtest'])
  })

  it('resolves caller axes, ratio, and ranking metric', async () => {
    const jobs = fakeJobs()
    const trainResults = [combo(2, 8, 0.3, 0.9, 0.02)]
    const testReport = report(2, 8, 0.1, 0.5, 0.05)
    const kernel = walkForwardKernel(trainResults, testReport)
    const tool: ToolDefinition = walkForwardTool(depsWith(kernel, () => jobs.face))
    const value = await tool.execute?.({
      symbol: '000001', bars: 40,
      fast_min: 2, fast_max: 2, slow_min: 8, slow_max: 8, rank_by: 'max_drawdown', top_n: 3, train_ratio: 0.6,
    }, exec)
    expect((value as { data: { combos: number; rank_by: string; train_ratio: number } }).data).toMatchObject({
      combos: 1, rank_by: 'max_drawdown', train_ratio: 0.6,
    })
    const outcome = await jobs.hooksOf(jobs.specs[0] as JobSpec).done
    expect(outcome.result).toContain('训练段比例：0.6')
  })

  it('settles as killed after cancel aborts the in-flight work', async () => {
    const jobs = fakeJobs()
    const kernel = kernelByOp(() => new Promise(() => {})) as unknown as QuantKernelClient
    kernel.request = vi.fn(async (_op: string, _params: Record<string, unknown>, signal?: AbortSignal) => {
      return await new Promise((_, reject) => {
        signal?.addEventListener('abort', () => reject(new Error('aborted')))
      })
    }) as never
    const tool: ToolDefinition = walkForwardTool(depsWith(kernel as QuantKernelClient, () => jobs.face))
    const value = await tool.execute?.({ symbol: '000001', bars: 250 }, exec)
    expect((value as { data: { job_id: string } }).data.job_id).toBe('quant-walk-forward-1')
    const hooks = jobs.hooksOf(jobs.specs[0] as JobSpec)
    const settled = hooks.done
    hooks.cancel('no longer needed')
    await expect(settled).resolves.toMatchObject({ status: 'killed' })
  })

  it('settles as failed when the kernel plane breaks, keeping the friendly detail', async () => {
    const jobs = fakeJobs()
    const kernel = kernelByOp(() => { throw new Error('wire broke') })
    const tool: ToolDefinition = walkForwardTool(depsWith(kernel, () => jobs.face))
    await tool.execute?.({ symbol: '000001', bars: 250 }, exec)
    const outcome = await jobs.hooksOf(jobs.specs[0] as JobSpec).done
    expect(outcome.status).toBe('failed')
    expect(outcome.detail).toBe('walk-forward 验证任务失败')
  })

  it('validates arguments before any job starts', async () => {
    const jobs = fakeJobs()
    const tool: ToolDefinition = walkForwardTool(depsWith(walkForwardKernel([], report(5, 30, 0, 0, 0)), () => jobs.face))
    const ratioBad = await tool.execute?.({ symbol: '000001', train_ratio: 0.3 }, exec)
    expect((ratioBad as { msg: string }).msg).toContain('train_ratio')
    const topBad = await tool.execute?.({ symbol: '000001', top_n: 99 }, exec)
    expect((topBad as { msg: string }).msg).toContain('top_n')
    const barsBad = await tool.execute?.({ symbol: '000001', bars: 50, train_ratio: 0.9, slow_max: 60 }, exec)
    expect((barsBad as { msg: string }).msg).toContain('测试段长度')
    expect(jobs.specs).toHaveLength(0)
  })
})

describe('splitRollingWindows', () => {
  it('cuts equal segments with expanding trains and no lookahead', () => {
    const windows: RollingWindow[] = splitRollingWindows(BARS, 4)
    // 250 bars → segment = floor(250 / 5) = 50, trimmed to 250 exactly.
    expect(windows).toHaveLength(4)
    expect(windows[0]?.train).toHaveLength(50)
    expect(windows[0]?.test).toHaveLength(50)
    expect(windows[3]?.train).toHaveLength(200)
    expect(windows[3]?.test).toHaveLength(50)
    // Expanding: window i's train is window (i+1)'s train prefix.
    expect(windows[1]?.train.slice(0, 50)).toEqual(windows[0]?.train)
    // No lookahead: each test segment starts exactly at its train end.
    expect(windows[2]?.test[0]?.date).toBe(BARS[150]?.date)
    // Remainder bars are dropped when the count does not divide evenly.
    const ragged = splitRollingWindows(BARS.slice(0, 243), 4)
    expect(ragged[0]?.train).toHaveLength(48) // floor(243 / 5) = 48
    expect(ragged[3]?.test).toHaveLength(48)
  })
})

describe('validateRollingParams', () => {
  it('enforces the window bounds', () => {
    expect(() => validateRollingParams(1500, SPEC, 1)).toThrow('windows')
    expect(() => validateRollingParams(1500, SPEC, 11)).toThrow('windows')
    expect(() => validateRollingParams(1500, SPEC, Number.NaN)).toThrow('windows')
    expect(() => validateRollingParams(1500, SPEC, 2)).not.toThrow()
  })

  it('rejects segments too short for the widest slow window', () => {
    // 300 bars / (4+1) = 60 segments, slow.max = 60 → need ≥ 61.
    expect(() => validateRollingParams(300, SPEC, 4)).toThrow('每段长度')
    expect(() => validateRollingParams(305, SPEC, 4)).not.toThrow()
  })
})

describe('inspectRollingWindowsCap', () => {
  it('allows absent windows and the in-bounds integers', () => {
    expect(inspectRollingWindowsCap({})).toEqual({ kind: 'allow' })
    expect(inspectRollingWindowsCap({ windows: 2 })).toEqual({ kind: 'allow' })
    expect(inspectRollingWindowsCap({ windows: 10 })).toEqual({ kind: 'allow' })
  })

  it('denies out-of-bounds and non-integer windows', () => {
    expect(inspectRollingWindowsCap({ windows: 1 })).toMatchObject({ kind: 'deny' })
    expect(inspectRollingWindowsCap({ windows: 11 })).toMatchObject({ kind: 'deny' })
    expect(inspectRollingWindowsCap({ windows: 2.5 })).toMatchObject({ kind: 'deny' })
    expect(inspectRollingWindowsCap({ windows: 'many' })).toMatchObject({ kind: 'deny' })
  })
})

describe('runRollingWalkForward', () => {
  it('re-optimizes per window and reports chronological gaps', async () => {
    // Every window: train grid returns two combos, best is fast 5; test runs on (5, 30).
    const kernel = walkForwardKernel([combo(5, 30, 0.2, 1.0, 0.05), combo(10, 30, 0.1, 0.5, 0.1)], report(5, 30, 0.1, 0.6, 0.08))
    const windows: RollingWindow[] = splitRollingWindows(BARS, ROLLING_WINDOWS_LIMITS.min)
    const results = await runRollingWalkForward(kernel, '000001', windows, SPEC, 1_000_000, 0.0005, 'total_return', 5)
    expect(results).toHaveLength(2)
    expect(results.map(r => r.index)).toEqual([0, 1])
    expect(results.every(r => r.best.fast === 5)).toBe(true)
    expect(results[0]?.returnGap).toBeCloseTo(0.1 - 0.2, 10)
    expect(results[1]?.sharpeGap).toBeCloseTo(0.6 - 1.0, 10)
    const ops = (kernel.request as ReturnType<typeof vi.fn>).mock.calls.map(call => call[0])
    // One grid + one backtest per window; the caller supplies bars directly, so no kline fetch.
    expect(ops).toEqual(['backtest_grid', 'backtest', 'backtest_grid', 'backtest'])
  })
})

describe('formatRollingWalkForwardSummary', () => {
  it('renders the per-window table and the aggregate stability read', async () => {
    const kernel = walkForwardKernel([combo(5, 30, 0.2, 1.0, 0.05), combo(10, 30, 0.15, 0.8, 0.1)], report(5, 30, 0.12, 0.6, 0.08))
    const windows: RollingWindow[] = splitRollingWindows(BARS, ROLLING_WINDOWS_LIMITS.min)
    const results = await runRollingWalkForward(kernel, '600519', windows, SPEC, 1_000_000, 0.0005, 'total_return', 5)
    const markdown = formatRollingWalkForwardSummary('600519', SPEC, results, 2, 'total_return', 16)
    expect(markdown).toContain('# 滚动 Walk-forward 验证报告：600519')
    expect(markdown).toContain('窗口数：2')
    expect(markdown).toContain('W1 | SMA(5/30)')
    expect(markdown).toContain('W2 | SMA(5/30)')
    expect(markdown).toContain('样本外收益均值')
    expect(markdown).toContain('平均收益差距')
    expect(markdown).toContain('样本外为正的窗口占比')
    expect(markdown).toContain('结论：')
    expect(markdown).toContain('仅供研究参考')
  })
})

describe('splitAnchoredWindows', () => {
  it('walks a fixed-length train with non-overlapping test segments', () => {
    // 400 bars, anchor 100, 3 windows → segment = floor(300 / 3) = 100.
    const bars400 = BARS.concat(Array.from({ length: 150 }, (_, index) => ({
      date: `2025-${String(index + 1).padStart(2, '0')}-01`,
      open: 10 + index, high: 11 + index, low: 9 + index, close: 10.5 + index, volume: 1000 + index,
    })))
    const windows = splitAnchoredWindows(bars400, 3, 100)
    expect(windows).toHaveLength(3)
    for (const window of windows) {
      expect(window.train).toHaveLength(100)
      expect(window.test).toHaveLength(100)
    }
    // Window 0 trains on [0,100), tests [100,200); window 1 [100,200) → [200,300).
    expect(windows[0]?.train[0]?.date).toBe(bars400[0]?.date)
    expect(windows[0]?.test[0]?.date).toBe(bars400[100]?.date)
    expect(windows[1]?.train[0]?.date).toBe(bars400[100]?.date)
    expect(windows[1]?.test[0]?.date).toBe(bars400[200]?.date)
    // No lookahead: each train ends exactly where its test begins.
    expect(windows[2]?.train.at(-1)?.date).toBe(bars400[299]?.date)
    expect(windows[2]?.test[0]?.date).toBe(bars400[300]?.date)
  })
})

describe('validateAnchoredParams', () => {
  it('enforces the anchor bounds and the slow-window coverage', () => {
    expect(() => validateAnchoredParams(1500, SPEC, 2, 29)).toThrow('anchor')
    expect(() => validateAnchoredParams(1500, SPEC, 2, 1001)).toThrow('anchor')
    expect(() => validateAnchoredParams(1500, SPEC, 11, 100)).toThrow('windows')
    // slow.max = 60 → anchor must be ≥ 61.
    expect(() => validateAnchoredParams(1500, SPEC, 2, 60)).toThrow('锚定训练窗')
    // (500 - 100) / 2 = 200 segments — fine.
    expect(() => validateAnchoredParams(500, SPEC, 2, 100)).not.toThrow()
    // (150 - 100) / 2 = 25 segments < 61 — too short.
    expect(() => validateAnchoredParams(150, SPEC, 2, 100)).toThrow('每段长度')
  })
})

describe('inspectAnchorCap', () => {
  it('allows absent anchors and in-bounds integers, denies the rest', () => {
    expect(inspectAnchorCap({})).toEqual({ kind: 'allow' })
    expect(inspectAnchorCap({ anchor: 30 })).toEqual({ kind: 'allow' })
    expect(inspectAnchorCap({ anchor: 1000 })).toEqual({ kind: 'allow' })
    expect(inspectAnchorCap({ anchor: 29 })).toMatchObject({ kind: 'deny' })
    expect(inspectAnchorCap({ anchor: 1001 })).toMatchObject({ kind: 'deny' })
    expect(inspectAnchorCap({ anchor: 2.5 })).toMatchObject({ kind: 'deny' })
    expect(inspectAnchorCap({ anchor: 'long' })).toMatchObject({ kind: 'deny' })
  })
})
