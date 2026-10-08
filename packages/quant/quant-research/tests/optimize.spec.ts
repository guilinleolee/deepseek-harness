import { describe, expect, it, vi } from 'vitest'
import { JobId } from '@deepseek-ai/dsh-jobs'
import type { JobHooks, JobStart } from '@deepseek-ai/dsh-jobs'
import { resolveConfig } from '../src/config.ts'
import { DataSourceBreaker } from '../src/pdat/datasource.ts'
import {
  DEFAULT_GRID_SPEC, GRID_COMBO_HARD_LIMIT,
} from '../src/compliance.ts'
import { inspectGridCaps } from '../src/compliance.ts'
import {
  DEFAULT_RANK_METRIC, axisLength, enumerateGrid, formatOptimizationSummary, rankGridResults,
  runBacktestGrid, validateGridSpec,
} from '../src/pcpt/optimize.ts'
import type { GridComboResult, GridSpec } from '../src/pcpt/optimize.ts'
import { optimizeParamsTool } from '../src/tools.ts'
import type { QuantToolDeps } from '../src/tools.ts'
import type { ToolDefinition } from '@deepseek-ai/dsh-tools'
import type { QuantKernelClient } from '../src/kernel-client/client.ts'

const ENV = { platform: 'linux' as const, dshHome: '/home/tester/.dsh' }
const CONFIG = resolveConfig(undefined, ENV)

const BARS = Array.from({ length: 80 }, (_, index) => ({
  date: `2024-01-${String(index + 1).padStart(2, '0')}`,
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
  },
})

describe('grid pure functions', () => {
  it('counts axis steps without materializing them', () => {
    expect(axisLength({ min: 5, max: 20, step: 5 })).toBe(4)
    expect(axisLength({ min: 30, max: 60, step: 10 })).toBe(4)
    expect(axisLength({ min: 10, max: 10, step: 3 })).toBe(1)
    expect(axisLength({ min: 2, max: 9, step: 4 })).toBe(2)
  })

  it('enumerates combinations fast-major in deterministic order', () => {
    expect(enumerateGrid({ fast: { min: 2, max: 5, step: 3 }, slow: { min: 8, max: 12, step: 4 } }))
      .toEqual([{ fast: 2, slow: 8 }, { fast: 2, slow: 12 }, { fast: 5, slow: 8 }, { fast: 5, slow: 12 }])
  })

  it('ranks return and sharpe descending, drawdown ascending, ties keeping grid order', () => {
    const results = [
      combo(2, 10, 0.1, 1.0, 0.2),
      combo(3, 10, 0.3, 0.5, 0.1),
      combo(4, 10, 0.3, 0.9, 0.3),
    ]
    expect(rankGridResults(results, 'total_return', 3).map(r => r.fast)).toEqual([3, 4, 2])
    expect(rankGridResults(results, 'sharpe', 3).map(r => r.fast)).toEqual([2, 4, 3])
    expect(rankGridResults(results, 'max_drawdown', 3).map(r => r.fast)).toEqual([3, 2, 4])
    expect(rankGridResults(results, 'total_return', 2)).toHaveLength(2)
  })

  it('formats the summary with grid shape, ranking table, and the overfitting warning', () => {
    const spec: GridSpec = { fast: { min: 5, max: 20, step: 5 }, slow: { min: 30, max: 60, step: 10 } }
    const markdown = formatOptimizationSummary('000001', spec, [combo(5, 30, 0.12, 1.4, 0.05)], DEFAULT_RANK_METRIC, 16)
    expect(markdown).toContain('# 参数寻优报告：000001')
    expect(markdown).toContain('快线：5-20 步长 5（4 个）')
    expect(markdown).toContain('慢线：30-60 步长 10（4 个）')
    expect(markdown).toContain('组合数：16')
    expect(markdown).toContain('排名指标：sharpe')
    expect(markdown).toContain('| 1 | 5 | 30 |')
    expect(markdown).toContain('过拟合风险')
  })

  it('renders the empty-table placeholder when no ranked results survive', () => {
    const spec: GridSpec = { fast: { min: 5, max: 5, step: 1 }, slow: { min: 30, max: 30, step: 1 } }
    const markdown = formatOptimizationSummary('000001', spec, [], DEFAULT_RANK_METRIC, 1)
    expect(markdown).toContain('（无结果）')
  })
})

describe('validateGridSpec', () => {
  const valid: GridSpec = { fast: { min: 5, max: 20, step: 5 }, slow: { min: 30, max: 60, step: 10 } }

  it('accepts the default spec with enough bars', () => {
    expect(() => validateGridSpec(80, valid)).not.toThrow()
    expect(() => validateGridSpec(250, DEFAULT_GRID_SPEC as unknown as GridSpec)).not.toThrow()
  })

  it('rejects non-integer axes, bad steps, and inverted ranges', () => {
    expect(() => validateGridSpec(80, { ...valid, fast: { min: 5.5, max: 20, step: 5 } })).toThrow('整数')
    expect(() => validateGridSpec(80, { ...valid, fast: { min: 5, max: 20, step: 0 } })).toThrow('步长')
    expect(() => validateGridSpec(80, { ...valid, slow: { min: 60, max: 30, step: 10 } })).toThrow('不能大于')
  })

  it('rejects axes outside the window bounds', () => {
    expect(() => validateGridSpec(80, { ...valid, fast: { min: 1, max: 20, step: 5 } })).toThrow('2-120')
    expect(() => validateGridSpec(300, { ...valid, slow: { min: 30, max: 251, step: 10 } })).toThrow('3-250')
  })

  it('rejects a fast range that touches the slow range', () => {
    expect(() => validateGridSpec(80, { ...valid, slow: { min: 20, max: 60, step: 10 } })).toThrow('必须小于慢线整段范围')
  })

  it('rejects grids over the combination cap and bars that miss the widest slow window', () => {
    expect(() => validateGridSpec(1500, {
      fast: { min: 2, max: 60, step: 1 },
      slow: { min: 61, max: 250, step: 1 },
    })).toThrow(`超过上限 ${String(GRID_COMBO_HARD_LIMIT)}`)
    expect(() => validateGridSpec(50, valid)).toThrow('至少覆盖最宽慢线窗口')
  })
})

describe('inspectGridCaps', () => {
  it('allows absent fields and the defaults', () => {
    expect(inspectGridCaps({})).toEqual({ kind: 'allow' })
    expect(inspectGridCaps({ symbol: '000001', bars: 250 })).toEqual({ kind: 'allow' })
  })

  it('denies non-integer fields, bad steps, out-of-bounds windows, and inverted ranges', () => {
    expect(inspectGridCaps({ fast_min: 2.5 })).toMatchObject({ kind: 'deny' })
    expect(inspectGridCaps({ slow_step: 0 })).toMatchObject({ kind: 'deny' })
    expect(inspectGridCaps({ fast_min: 1 })).toMatchObject({ kind: 'deny' })
    expect(inspectGridCaps({ slow_max: 251 })).toMatchObject({ kind: 'deny' })
    expect(inspectGridCaps({ slow_min: 60, slow_max: 30 })).toMatchObject({ kind: 'deny' })
  })

  it('denies a fast range touching the slow range and combination counts over the cap', () => {
    expect(inspectGridCaps({ fast_max: 30 })).toMatchObject({ kind: 'deny' })
    expect(inspectGridCaps({ fast_min: 2, fast_max: 100, slow_min: 120, slow_max: 250, fast_step: 1, slow_step: 1 }))
      .toMatchObject({ kind: 'deny' })
  })

  it('resolves partial fields against the defaults, so a legal-looking field cannot explode the grid', () => {
    // slow_max 250 alone is in-bounds, but with the default fast axis and
    // slow step 1 the resolved grid explodes past the cap.
    expect(inspectGridCaps({ slow_max: 250, slow_step: 1 })).toMatchObject({ kind: 'deny' })
    expect(inspectGridCaps({ slow_max: 120 })).toEqual({ kind: 'allow' })
  })
})

function kernelByOp(handler: (op: string, params: Record<string, unknown>) => unknown): QuantKernelClient {
  return {
    request: vi.fn(async (op: string, params: Record<string, unknown>) => handler(op, params)),
  } as unknown as QuantKernelClient
}

describe('runBacktestGrid', () => {
  it('sends the enumerated combos in one request and returns the validated results', async () => {
    const kernel = kernelByOp(() => ({
      symbol: '000001',
      count: 2,
      results: [combo(5, 30, 0.1, 1.2, 0.05), combo(10, 30, 0.2, 0.8, 0.1)],
    }))
    const spec: GridSpec = { fast: { min: 5, max: 10, step: 5 }, slow: { min: 30, max: 30, step: 1 } }
    const results = await runBacktestGrid(kernel, '000001', BARS, spec, 1_000_000, 0.0003)
    expect(results).toHaveLength(2)
    expect((kernel.request as ReturnType<typeof vi.fn>).mock.calls[0]?.[0]).toBe('backtest_grid')
    expect((kernel.request as ReturnType<typeof vi.fn>).mock.calls[0]?.[1]).toMatchObject({
      combos: [{ fast: 5, slow: 30 }, { fast: 10, slow: 30 }],
      initial_cash: 1_000_000,
      fee_rate: 0.0003,
    })
  })

  it('rejects a response that misses the wire shape', async () => {
    const kernel = kernelByOp(() => ({ symbol: '000001', results: [{ fast: 5 }] }))
    await expect(runBacktestGrid(
      kernel, '000001', BARS,
      { fast: { min: 5, max: 5, step: 1 }, slow: { min: 30, max: 30, step: 1 } },
      1_000_000, 0.0003,
    )).rejects.toThrow('不符合规格')
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
        return JobId(`quant-optimize-${String(counter)}`)
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

function gridKernel(results: GridComboResult[]): QuantKernelClient {
  return kernelByOp((op) => {
    if (op === 'get_kline') return BARS
    if (op === 'backtest_grid') return { symbol: '000001', count: results.length, results }
    return {}
  })
}

describe('quant_optimize_params', () => {
  const exec = { signal: new AbortController().signal, agent: undefined } as never

  it('fails with a friendly CONFIG envelope when no jobs runtime is composed', async () => {
    const tool: ToolDefinition = optimizeParamsTool(depsWith(gridKernel([])))
    const value = await tool.execute?.({ symbol: '000001' }, exec)
    expect((value as { code: number }).code).not.toBe(0)
    expect((value as { data: unknown }).data).toBeNull()
    expect((value as { msg: string }).msg).toContain('后台任务运行时')
  })

  it('starts one background job, renders the job id, and settles with the ranked markdown', async () => {
    const jobs = fakeJobs()
    const kernel = gridKernel([combo(5, 30, 0.1, 1.2, 0.05), combo(10, 30, 0.2, 0.8, 0.1)])
    const tool: ToolDefinition = optimizeParamsTool(depsWith(kernel, () => jobs.face))
    const value = await tool.execute?.({ symbol: '000001', bars: 80 }, exec)
    const data = (value as { code: number; data: { job_id: string; combos: number; hint: string } }).data
    expect(data.job_id).toBe('quant-optimize-1')
    expect(data.combos).toBe(16)
    expect(data.hint).toContain('job_output')
    const rendered = (tool.output?.render({}, value as never) as { text?: string }[])[0]?.text ?? ''
    expect(rendered).toContain('quant-optimize-1')
    expect(rendered).toContain('共 16 组合')
    expect(rendered).toContain('仅供研究参考')

    expect(jobs.specs).toHaveLength(1)
    expect(jobs.specs[0]?.kind).toBe('quant-optimize')
    expect(jobs.specs[0]?.label).toContain('16 组合')
    const outcome = await jobs.hooksOf(jobs.specs[0] as JobStart).done
    expect(outcome.status).toBe('completed')
    expect(outcome.output).toContain('# 参数寻优报告：000001')
    expect(outcome.detail).toContain('SMA(')
    // One kernel fetch and exactly one grid request — the grid is one process.
    const ops = (kernel.request as ReturnType<typeof vi.fn>).mock.calls.map(call => call[0])
    expect(ops).toEqual(['get_kline', 'backtest_grid'])
    expect((kernel.request as ReturnType<typeof vi.fn>).mock.calls[1]?.[1]).toMatchObject({
      combos: expect.arrayContaining([{ fast: 5, slow: 30 }, { fast: 20, slow: 60 }]),
    })
  })

  it('resolves caller axes, ranking metric, and top N', async () => {
    const jobs = fakeJobs()
    const kernel = gridKernel([combo(2, 8, 0.3, 0.9, 0.02)])
    const tool: ToolDefinition = optimizeParamsTool(depsWith(kernel, () => jobs.face))
    const value = await tool.execute?.({
      symbol: '000001', bars: 40,
      fast_min: 2, fast_max: 2, slow_min: 8, slow_max: 8, rank_by: 'max_drawdown', top_n: 3,
    }, exec)
    expect((value as { data: { combos: number; rank_by: string } }).data).toMatchObject({
      combos: 1, rank_by: 'max_drawdown',
    })
    const outcome = await jobs.hooksOf(jobs.specs[0] as JobStart).done
    expect(outcome.output).toContain('排名指标：max_drawdown')
  })

  it('settles as killed after cancel aborts the in-flight work', async () => {
    const jobs = fakeJobs()
    const kernel = kernelByOp(() => new Promise(() => {})) as unknown as QuantKernelClient
    kernel.request = vi.fn(async (_op: string, _params: Record<string, unknown>, signal?: AbortSignal) => {
      return await new Promise((_, reject) => {
        signal?.addEventListener('abort', () => reject(new Error('aborted')))
      })
    }) as never
    const tool: ToolDefinition = optimizeParamsTool(depsWith(kernel as QuantKernelClient, () => jobs.face))
    const value = await tool.execute?.({ symbol: '000001', bars: 80 }, exec)
    expect((value as { data: { job_id: string } }).data.job_id).toBe('quant-optimize-1')
    const hooks = jobs.hooksOf(jobs.specs[0] as JobStart)
    const settled = hooks.done
    hooks.cancel('no longer needed')
    await expect(settled).resolves.toMatchObject({ status: 'killed' })
  })

  it('settles as failed when the kernel plane breaks, keeping the friendly detail', async () => {
    const jobs = fakeJobs()
    const kernel = kernelByOp(() => {
      throw new Error('wire broke')
    })
    const tool: ToolDefinition = optimizeParamsTool(depsWith(kernel, () => jobs.face))
    await tool.execute?.({ symbol: '000001', bars: 80 }, exec)
    const outcome = await jobs.hooksOf(jobs.specs[0] as JobStart).done
    expect(outcome.status).toBe('failed')
    expect(outcome.detail).toBe('参数寻优任务失败')
  })

  it('validates arguments before any job starts', async () => {
    const jobs = fakeJobs()
    const tool: ToolDefinition = optimizeParamsTool(depsWith(gridKernel([]), () => jobs.face))
    const topBad = await tool.execute?.({ symbol: '000001', top_n: 99 }, exec)
    expect((topBad as { msg: string }).msg).toContain('top_n')
    const gridBad = await tool.execute?.({ symbol: '000001', fast_max: 40 }, exec)
    expect((gridBad as { msg: string }).msg).toContain('慢线整段范围')
    const barsBad = await tool.execute?.({ symbol: '000001', bars: 10 }, exec)
    expect((barsBad as { msg: string }).msg).toContain('最宽慢线窗口')
    expect(jobs.specs).toHaveLength(0)
  })
})
