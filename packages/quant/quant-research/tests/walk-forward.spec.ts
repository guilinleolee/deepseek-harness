import { describe, expect, it, vi } from 'vitest'
import { JobId } from '@deepseek-ai/dsh-jobs'
import type { JobHooks, JobStart } from '@deepseek-ai/dsh-jobs'
import { resolveConfig } from '../src/config.ts'
import { DataSourceBreaker } from '../src/pdat/datasource.ts'
import { DEFAULT_GRID_SPEC } from '../src/compliance.ts'
import { inspectTrainRatioCap } from '../src/compliance.ts'
import {
  formatWalkForwardSummary, runWalkForward, splitBars,
  validateWalkForwardParams,
} from '../src/pcpt/walk-forward.ts'
import type { WalkForwardSplit } from '../src/pcpt/walk-forward.ts'
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
  face: { start(spec: JobStart): ReturnType<typeof JobId> }
  specs: JobStart[]
  hooksOf(spec: JobStart): JobHooks
} {
  const specs: JobStart[] = []
  const hooksByIndex = new Map<JobStart, JobHooks>()
  let counter = 0
  return {
    face: {
      start(spec: JobStart): ReturnType<typeof JobId> {
        specs.push(spec)
        counter += 1
        const hooks = spec.run()
        hooksByIndex.set(spec, hooks)
        return JobId(`quant-walk-forward-${String(counter)}`)
      },
    },
    specs,
    hooksOf: (spec: JobStart): JobHooks => hooksByIndex.get(spec) as JobHooks,
  }
}

function depsWith(kernel: QuantKernelClient, jobs?: () => unknown): QuantToolDeps {
  const base: QuantToolDeps = {
    config: CONFIG,
    kernel,
    breaker: new DataSourceBreaker(3),
    accounts: new Map() as never,
    orders: new Map() as never,
    notes: new Map() as never,
  }
  return jobs === undefined ? base : { ...base, jobs: jobs as QuantToolDeps['jobs'] }
}

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
    const outcome = await jobs.hooksOf(jobs.specs[0] as JobStart).done
    expect(outcome.status).toBe('completed')
    expect(outcome.output).toContain('# Walk-forward 验证报告：000001')
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
    const outcome = await jobs.hooksOf(jobs.specs[0] as JobStart).done
    expect(outcome.output).toContain('训练段比例：0.6')
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
    const hooks = jobs.hooksOf(jobs.specs[0] as JobStart)
    const settled = hooks.done
    hooks.cancel('no longer needed')
    await expect(settled).resolves.toMatchObject({ status: 'killed' })
  })

  it('settles as failed when the kernel plane breaks, keeping the friendly detail', async () => {
    const jobs = fakeJobs()
    const kernel = kernelByOp(() => { throw new Error('wire broke') })
    const tool: ToolDefinition = walkForwardTool(depsWith(kernel, () => jobs.face))
    await tool.execute?.({ symbol: '000001', bars: 250 }, exec)
    const outcome = await jobs.hooksOf(jobs.specs[0] as JobStart).done
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
