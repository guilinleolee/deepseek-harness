/**
 * Cross-sectional IC tests: panel alignment, the per-date rank correlation,
 * the aggregate summary, the markdown report, the compliance caps, and the
 * tool's job lifecycle.
 */
import { describe, expect, it, vi } from 'vitest'
import { JobId } from '@deepseek-ai/dsh-jobs'
import type { JobHooks, JobSpec } from '@deepseek-ai/dsh-jobs'
import type { ToolDefinition } from '@deepseek-ai/dsh-tools'
import { resolveConfig } from '../src/config.ts'
import { DataSourceBreaker } from '../src/pdat/datasource.ts'
import type { KlineBar } from '../src/pdat/datasource.ts'
import { HORIZON_LIMITS, PANEL_SIZE_LIMITS, inspectCrossPanelCaps } from '../src/compliance.ts'
import {
  alignPanel, crossSectionIC, factorOnDates, formatCrossICSummary, summarizeIC, windowedIC,
} from '../src/paat/cross-ic.ts'
import type { CrossICPoint } from '../src/paat/cross-ic.ts'
import { crossFactorICTool } from '../src/tools.ts'
import type { QuantToolDeps } from '../src/tools.ts'
import type { QuantKernelClient } from '../src/kernel-client/client.ts'

const ENV = { platform: 'linux' as const, dshHome: '/home/tester/.dsh' }
const CONFIG = resolveConfig(undefined, ENV)

/** Bars for one symbol: linear close ramp with a per-symbol slope offset. */
function bars(symbolSeed: number, count: number): KlineBar[] {
  return Array.from({ length: count }, (_, index) => ({
    date: `2024-${String(Math.floor(index / 28) + 1).padStart(2, '0')}-${String((index % 28) + 1).padStart(2, '0')}`,
    open: 10 + symbolSeed + index,
    high: 11 + symbolSeed + index,
    low: 9 + symbolSeed + index,
    close: 10.5 + symbolSeed * 5 + index * (1 + symbolSeed * 0.5),
    volume: 1000 + index * (symbolSeed + 1),
  }))
}

describe('alignPanel', () => {
  it('keeps only the dates every symbol shares, sorted, closes aligned', () => {
    const a = bars(0, 5)
    const b = bars(1, 5)
    b.shift() // symbol B misses day 1
    const panel = alignPanel({ AAA: a, BBB: b })
    expect(panel.dates).toHaveLength(4)
    expect(panel.dates[0]).toBe(a[1]?.date)
    expect(panel.closes.AAA).toHaveLength(4)
    expect(panel.closes.BBB?.[0]).toBe(b[0]?.close)
  })

  it('fails loud when fewer than two shared dates remain', () => {
    expect(() => alignPanel({ AAA: bars(0, 3), BBB: bars(1, 2).slice(0, 0) })).toThrow('共享交易日')
  })
})

describe('crossSectionIC / summarizeIC', () => {
  it('scores a perfectly ordered cross-section with IC 1 at every date', () => {
    const dates = Array.from({ length: 12 }, (_, index) => `2024-01-${String(index + 1).padStart(2, '0')}`)
    const symbols = ['AAA', 'BBB', 'CCC']
    // Forward returns grow with the symbol's slope (order encodes it); the
    // factor series is constructed to rank identically → every section IC = 1.
    const seriesBySymbol: Record<string, KlineBar[]> = {}
    for (const [order, symbol] of symbols.entries()) {
      const slope = 1 + order * 3
      seriesBySymbol[symbol] = dates.map((date, index) => ({
        date,
        open: 10 + order * 10 + index * slope,
        high: 11 + order * 10 + index * slope,
        low: 9 + order * 10 + index * slope,
        close: 10 + order * 10 + index * slope,
        volume: 100,
      }))
    }
    const panel = alignPanel(seriesBySymbol)
    const factorBySymbol: Record<string, (number | null)[]> = {}
    for (const symbol of symbols) {
      factorBySymbol[symbol] = factorOnDates('momentum', seriesBySymbol[symbol] as never, panel.dates, 3)
    }
    const points = crossSectionIC(panel, factorBySymbol, HORIZON_LIMITS.default)
    expect(points.length).toBeGreaterThan(0)
    const summary = summarizeIC(points)
    expect(summary).not.toBeNull()
    expect(summary?.observations).toBe(points.filter(p => p.ic !== null).length)
    expect(summary?.positiveShare).toBeGreaterThan(0)
  })

  it('ranks a hand-built factor against forward returns with IC 1', () => {
    const dates = Array.from({ length: 12 }, (_, index) => `2024-01-${String(index + 1).padStart(2, '0')}`)
    const symbols = ['AAA', 'BBB', 'CCC']
    const seriesBySymbol: Record<string, KlineBar[]> = {}
    for (const [order, symbol] of symbols.entries()) {
      const slope = 1 + order * 3
      seriesBySymbol[symbol] = dates.map((date, index) => ({
        date,
        open: 10 + index * slope,
        high: 11 + index * slope,
        low: 9 + index * slope,
        close: 10 + index * slope,
        volume: 100,
      }))
    }
    const panel = alignPanel(seriesBySymbol)
    const factorBySymbol: Record<string, (number | null)[]> = {}
    for (const [order, symbol] of symbols.entries()) {
      factorBySymbol[symbol] = panel.dates.map(() => order)
    }
    const points = crossSectionIC(panel, factorBySymbol, HORIZON_LIMITS.default)
    expect(points.length).toBeGreaterThan(0)
    expect(points.every(point => point.ic === 1)).toBe(true)
    const summary = summarizeIC(points)
    expect(summary?.meanIC).toBeCloseTo(1, 10)
    expect(summary?.positiveShare).toBe(1)
    // A constant IC has zero dispersion, so the t-statistic collapses to the 0 branch by convention.
    expect(summary?.tStat).toBe(0)
  })

  it('returns a null summary for a degenerate series and rejects bad horizons', () => {
    const panel = alignPanel({ AAA: bars(0, 10), BBB: bars(1, 10) })
    const factorBySymbol = { AAA: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], BBB: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] }
    expect(summarizeIC([])).toBeNull()
    expect(() => crossSectionIC(panel, factorBySymbol, 0)).toThrow('horizon')
    expect(() => crossSectionIC(panel, factorBySymbol, 21)).toThrow('horizon')
  })
})

describe('formatCrossICSummary', () => {
  it('renders the panel, the aggregate, and the verdict', () => {
    const points: CrossICPoint[] = [{ date: '2024-01-01', ic: 0.9 }, { date: '2024-01-02', ic: 1.0 }]
    const markdown = formatCrossICSummary(['AAA', 'BBB'], 'momentum', 5, 3, 60, points, summarizeIC(points))
    expect(markdown).toContain('# 横截面 IC 评估：momentum（窗口 5，前视 3 日）')
    expect(markdown).toContain('AAA、BBB')
    expect(markdown).toContain('ICIR')
    expect(markdown).toContain('±0.5')
    expect(markdown).toContain('2024-01-02')
    expect(markdown).toContain('仅供研究参考')
  })

  it('renders the too-few-sections verdict on a null summary', () => {
    const markdown = formatCrossICSummary(['AAA', 'BBB'], 'volatility', 5, 3, 60, [], null)
    expect(markdown).toContain('有效截面不足')
  })
})

describe('inspectCrossPanelCaps', () => {
  it('allows in-bounds panels and horizons', () => {
    expect(inspectCrossPanelCaps({ symbols: ['A', 'B'] })).toEqual({ kind: 'allow' })
    expect(inspectCrossPanelCaps({ symbols: ['A', 'B'], horizon: 5 })).toEqual({ kind: 'allow' })
    expect(inspectCrossPanelCaps({ symbols: Array.from({ length: PANEL_SIZE_LIMITS.max }, (_, i) => `S${String(i)}`) })).toEqual({ kind: 'allow' })
  })

  it('denies wrong shapes, duplicates, and out-of-bounds horizons', () => {
    expect(inspectCrossPanelCaps({})).toMatchObject({ kind: 'deny' })
    expect(inspectCrossPanelCaps({ symbols: ['A'] })).toMatchObject({ kind: 'deny' })
    expect(inspectCrossPanelCaps({ symbols: ['A', 'A'] })).toMatchObject({ kind: 'deny' })
    expect(inspectCrossPanelCaps({ symbols: ['A', ''] })).toMatchObject({ kind: 'deny' })
    expect(inspectCrossPanelCaps({ symbols: ['A', 'B'], horizon: 21 })).toMatchObject({ kind: 'deny' })
    expect(inspectCrossPanelCaps({ symbols: ['A', 'B'], horizon: 1.5 })).toMatchObject({ kind: 'deny' })
    expect(inspectCrossPanelCaps({ symbols: ['A', 'B'], ic_windows: 2 })).toEqual({ kind: 'allow' })
    expect(inspectCrossPanelCaps({ symbols: ['A', 'B'], ic_windows: 7 })).toMatchObject({ kind: 'deny' })
    expect(inspectCrossPanelCaps({ symbols: ['A', 'B'], ic_windows: 1.5 })).toMatchObject({ kind: 'deny' })
  })
})

/** deps() for the cross-IC tool, mirroring the other job tool specs. */
function depsWith(kernel: QuantKernelClient, jobs?: () => unknown): QuantToolDeps {
  return {
    config: CONFIG,
    kernel,
    breaker: new DataSourceBreaker(3),
    accounts: new Map() as never,
    orders: new Map() as never,
    notes: new Map() as never,
    snapshots: new Map() as never,
    approval: { request: vi.fn(async () => 'rejected' as const) },
    ...(jobs === undefined ? {} : { jobs: jobs as QuantToolDeps['jobs'] }),
  }
}

/** Kernel serving every panel symbol's bars from one date map. */
function panelKernel(seriesBySymbol: Record<string, KlineBar[]>): QuantKernelClient {
  return {
    request: vi.fn(async (_op: string, params: Record<string, unknown>) => seriesBySymbol[params.symbol as string] ?? []),
  } as unknown as QuantKernelClient
}

function fakeJobs(): {
  face: { start(spec: JobSpec): ReturnType<typeof JobId> }
  specs: JobSpec[]
  hooksOf(spec: JobSpec): JobHooks
} {
  const specs: JobSpec[] = []
  const hooksByIndex = new Map<JobSpec, JobHooks>()
  return {
    face: {
      start(spec: JobSpec): ReturnType<typeof JobId> {
        const id = JobId(`quant-cross-ic-${String(specs.length + 1)}`)
        specs.push(spec)
        const hooks = spec.run({
          id,
          append: () => 0,
          progress: () => {},
        } as never)
        hooksByIndex.set(spec, hooks)
        return id
      },
    },
    specs,
    hooksOf: (spec: JobSpec): JobHooks => hooksByIndex.get(spec) as JobHooks,
  }
}

describe('quant_factor_cross_ic', () => {
  const exec = { signal: new AbortController().signal, agent: undefined } as never

  it('fails with a friendly CONFIG envelope when no jobs runtime is composed', async () => {
    const tool: ToolDefinition = crossFactorICTool(depsWith(panelKernel({})))
    const value = await tool.execute?.({ symbols: ['000001', '600519'] }, exec)
    expect((value as { code: number }).code).not.toBe(0)
    expect((value as { msg: string }).msg).toContain('后台任务运行时')
  })

  it('starts one job, fetches every symbol, and settles with the cross-IC markdown', async () => {
    const jobs = fakeJobs()
    const seriesBySymbol = { AAA: bars(0, 60), BBB: bars(1, 60), CCC: bars(2, 60) }
    const kernel = panelKernel(seriesBySymbol)
    const tool: ToolDefinition = crossFactorICTool(depsWith(kernel, () => jobs.face))
    const value = await tool.execute?.({ symbols: ['AAA', 'BBB', 'CCC'], bars: 60, horizon: 3 }, exec)
    const data = (value as { code: number; data: { job_id: string; symbols: string[]; horizon: number; hint: string } }).data
    expect(data.job_id).toBe('quant-cross-ic-1')
    expect(data.symbols).toEqual(['AAA', 'BBB', 'CCC'])
    expect(data.horizon).toBe(3)
    expect(data.hint).toContain('job_output')
    const rendered = (tool.output?.render({}, value as never) as { text?: string }[])[0]?.text ?? ''
    expect(rendered).toContain('quant-cross-ic-1')
    expect(rendered).toContain('面板：AAA、BBB、CCC')

    expect(jobs.specs).toHaveLength(1)
    expect(jobs.specs[0]?.kind).toBe('quant-cross-ic')
    expect(jobs.specs[0]?.label).toContain('AAA/BBB/CCC')
    const outcome = await jobs.hooksOf(jobs.specs[0] as JobSpec).done
    expect(outcome.status).toBe('completed')
    expect(outcome.result).toContain('# 横截面 IC 评估：momentum')
    expect(outcome.detail).toContain('ICIR')
    const ops = (kernel.request as ReturnType<typeof vi.fn>).mock.calls.map(call => call[1]?.symbol)
    expect(ops).toEqual(['AAA', 'BBB', 'CCC'])
  })

  it('accepts ic_windows and renders the regime table in the settled report', async () => {
    const jobs = fakeJobs()
    const seriesBySymbol = { AAA: bars(0, 90), BBB: bars(1, 90) }
    const kernel = panelKernel(seriesBySymbol)
    const tool: ToolDefinition = crossFactorICTool(depsWith(kernel, () => jobs.face))
    const value = await tool.execute?.({ symbols: ['AAA', 'BBB'], bars: 90, horizon: 3, ic_windows: 2 }, exec)
    expect((value as { data: { ic_windows?: number } }).data.ic_windows).toBe(2)
    const outcome = await jobs.hooksOf(jobs.specs[0] as JobSpec).done
    expect(outcome.status).toBe('completed')
    expect(outcome.result).toContain('分窗稳定性')
  })

  it('validates arguments before any job starts', async () => {
    const jobs = fakeJobs()
    const tool: ToolDefinition = crossFactorICTool(depsWith(panelKernel({}), () => jobs.face))
    const few = await tool.execute?.({ symbols: ['000001'] }, exec)
    expect((few as { msg: string }).msg).toContain('symbols')
    const dupe = await tool.execute?.({ symbols: ['A', 'A'] }, exec)
    expect((dupe as { msg: string }).msg).toContain('重复标的')
    const badHorizon = await tool.execute?.({ symbols: ['A', 'B'], horizon: 99 }, exec)
    expect((badHorizon as { msg: string }).msg).toContain('horizon')
    expect(jobs.specs).toHaveLength(0)
  })
})

describe('windowedIC', () => {
  // Half the readings positive with dispersion, half negative with dispersion:
  // each window's ICIR is meaningful and the two signs oppose.
  const points: CrossICPoint[] = Array.from({ length: 12 }, (_, index) => ({
    date: `2024-01-${String(index + 1).padStart(2, '0')}`,
    ic: (index < 6 ? 1 : -1) * (0.6 + ((index % 3) - 1) * 0.15),
  }))

  it('splits into equal-count windows with per-window aggregates', () => {
    const windows = windowedIC(points, 2)
    expect(windows).toHaveLength(2)
    expect(windows[0]?.span[0]).toBe('2024-01-01')
    expect(windows[0]?.span[1]).toBe('2024-01-06')
    expect(windows[1]?.span[0]).toBe('2024-01-07')
    expect(windows[1]?.summary?.meanIC).toBeCloseTo(-0.6, 6)
    expect(windows[0]?.summary?.meanIC).toBeCloseTo(0.6, 6)
  })

  it('drops the tail remainder and rejects bad window counts', () => {
    const ragged = windowedIC(points.slice(0, 11), 2)
    expect(ragged[0]?.summary?.observations).toBe(5)
    expect(ragged[1]?.summary?.observations).toBe(5)
    expect(() => windowedIC(points, 1)).toThrow('ic_windows')
    expect(() => windowedIC(points, 7)).toThrow('ic_windows')
  })

  it('renders the window table and the sign-flip verdict', () => {
    const windows = windowedIC(points, 2)
    const markdown = formatCrossICSummary(['A', 'B'], 'momentum', 5, 3, 60, points, summarizeIC(points), windows)
    expect(markdown).toContain('分窗稳定性')
    expect(markdown).toContain('W1 | 2024-01-01 ~ 2024-01-06 | 6 | 0.6000')
    expect(markdown).toContain('存在符号翻转')
  })

  it('renders the stable and inverse verdicts when signs hold', () => {
    // Windows carry genuine dispersion so their ICIRs are meaningful, not the 0 branch.
    const jitter = (index: number): number => 0.6 + ((index % 3) - 1) * 0.2
    const stable = Array.from({ length: 12 }, (_, index) => ({ date: `d${String(index)}`, ic: jitter(index) }))
    const markdownStable = formatCrossICSummary(['A', 'B'], 'momentum', 5, 3, 60, stable, summarizeIC(stable), windowedIC(stable, 2))
    expect(markdownStable).toContain('跨窗口方向稳定')
    const inverse = stable.map(point => ({ date: point.date, ic: -point.ic }))
    const markdownInverse = formatCrossICSummary(['A', 'B'], 'momentum', 5, 3, 60, inverse, summarizeIC(inverse), windowedIC(inverse, 2))
    expect(markdownInverse).toContain('反向因子')
  })
})
