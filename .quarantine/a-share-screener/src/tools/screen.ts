/**
 * The `a_share_screen` tool. Wraps a strategy registry evaluation in a
 * background job — full-market scans return a `{ kind: 'background', jobId }`
 * handle immediately, and the model polls the registry for the terminal
 * snapshot. The job producer lives in the same module so it can read the
 * closed-over service without exposing it on `ctx`.
 *
 * @module @deepseek-ai/dsh-a-share-screener/tools/screen
 */

import type { Context } from '@deepseek-ai/cordis'
import { defineTool } from '@deepseek-ai/dsh-tools'
import type { ScreenerService } from '../service.ts'
import { BUILTIN_STRATEGIES } from '../strategies/registry.ts'
import type { ScreenArgs, ScreenResult, StockBasicInfo, Universe } from '../types.ts'
import { SCREENER_JOB_KIND } from '../types.ts'

declare module '@deepseek-ai/dsh-jobs' {
  interface JobKindMap {
    [SCREENER_JOB_KIND]: typeof SCREENER_JOB_KIND
  }
}

export interface BackgroundOutput {
  kind: 'background'
  jobId: string
}

/**
 * Build the `a_share_screen` tool bound to a service instance. The factory
 * pattern keeps `tools/screen.ts` importable from tests that do not register
 * a real Cordis host.
 *
 * @param _ctx - the host context (currently unused; the tool pulls dependencies from `exec.context`).
 * @param service - the screener service this tool executes against.
 * @returns a registry-ready tool definition.
 */
export function defineScreenTool(_ctx: Context, service: ScreenerService) {
  for (const strategy of BUILTIN_STRATEGIES) {
    service.strategies.register(strategy)
  }

  return defineTool({
    name: 'a_share_screen',
    description:
      'Run an A-share screening strategy against a stock universe. Returns a background job handle; poll `ctx.jobs.read(jobId)` for the terminal result.',
    parameters: {
      strategy: {
        type: 'string',
        enum: BUILTIN_STRATEGIES.map((s) => s.id),
        description: 'Strategy id from the registry. Use `a_share_list_strategies` to enumerate.',
      },
      universe: {
        type: 'object',
        required: true,
        additionalProperties: false,
        properties: {
          kind: { type: 'string', required: true, enum: ['all', 'hot', 'symbols'] },
          size: { type: 'number' },
          symbols: { type: 'array', items: { type: 'string' } },
        },
        description: 'Stock universe selector.',
      },
      limit: {
        type: 'number',
        description: 'Maximum number of matches to return.',
      },
      sortByScore: {
        type: 'boolean',
        description: 'Sort matches by composite score (default true).',
      },
    },
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: {
          kind: { type: 'string', enum: ['background'] },
          jobId: { type: 'string' },
        },
      },
      render: (_args, value) => [
        { type: 'text', text: `started background job ${(value as BackgroundOutput).jobId}` },
      ],
    },
    async execute(args, exec): Promise<BackgroundOutput> {
      const jobs = exec.context.get('jobs')
      if (jobs === undefined) {
        throw new Error('background jobs unavailable: load @deepseek-ai/dsh-jobs-local + @deepseek-ai/dsh-tool-jobs')
      }
      const typed = args as ScreenArgs
      const universe = typed.universe ?? service.defaultUniverse
      const limit = typed.limit ?? service.defaultLimit

      const id = jobs.start({
        kind: SCREENER_JOB_KIND,
        label: `${typed.strategy} ${summarizeUniverse(universe)}`,
        ...(exec.agent ? { owner: exec.agent as never } : {}),
        ...(service.jobOutputLimitBytes > 0 ? { outputLimitBytes: service.jobOutputLimitBytes } : {}),
        run: () => runScreening(service, typed.strategy, universe, limit, exec.signal),
      })
      return { kind: 'background' as const, jobId: id }
    },
  })
}

export function summarizeUniverse(universe: Universe): string {
  switch (universe.kind) {
    case 'all':
      return 'universe=all'
    case 'hot':
      return `universe=hot:${String(universe.size)}`
    case 'symbols':
      return `universe=symbols:${universe.symbols.length}`
  }
}

/**
 * Run the screening synchronously inside the producer body. Exported so tests
 * can drive the same path without going through the tool executor.
 */
export function runScreening(
  service: ScreenerService,
  strategyId: string,
  universe: Universe,
  limit: number,
  signal: AbortSignal,
): { cancel(): void; done: Promise<{ status: 'completed'; output: string }>; readOutput(): string } {
  const stocks = selectUniverse(service, universe)
  const matched: ScreenResult['results'] = []
  let scanned = 0
  const startedAt = Date.now()

  for (const stock of stocks) {
    if (signal.aborted) break
    const bars = service.cache.loadBars(stock.symbol, new Date(Date.now() - 365 * 24 * 60 * 60 * 1000))
    console.error('[runScreening]', stock.symbol, 'bars:', bars.length)
    if (bars.length === 0) {
      scanned += 1
      continue
    }
    const quote: ScreenResult['results'][number]['currentQuote'] = {
      symbol: stock.symbol,
      price: bars[bars.length - 1]!.close,
      change: 0,
      changePercent: 0,
      volume: bars[bars.length - 1]!.volume,
      amount: bars[bars.length - 1]!.amount,
      timestamp: bars[bars.length - 1]!.date,
    }
    const evaluation = service.strategies.evaluate(strategyId, { stock, bars, quote })
    scanned += 1
    if (evaluation.passed) {
      matched.push(service.strategies.toMatch(evaluation, stock, quote))
    }
  }

  matched.sort((a, b) => (b.score ?? 0) - (a.score ?? 0))
  const final: ScreenResult = {
    totalScanned: scanned,
    matched: matched.length,
    results: matched.slice(0, limit),
    executionTimeMs: Date.now() - startedAt,
  }
  return {
    cancel: () => {},
    done: Promise.resolve({ status: 'completed' as const, output: JSON.stringify(final) }),
    readOutput: () => (final.results.length === 0 ? '<no matches>' : JSON.stringify(final.results)),
  }
}

export function selectUniverse(service: ScreenerService, universe: Universe): ScreenResult['results'][number]['stock'][] {
  const all = service.cache.loadStocks()
  if (all.length === 0) return []
  switch (universe.kind) {
    case 'all':
      return all
    case 'hot':
      return all.slice(0, universe.size)
    case 'symbols':
      return all.filter((stock) => universe.symbols.includes(stock.symbol))
  }
}
