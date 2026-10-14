/**
 * Strategy registry: each strategy is a named list of filters evaluated with
 * short-circuiting AND semantics. The first failing filter populates the
 * `failedAt` evidence; a passing run accumulates the per-filter scores.
 *
 * @module @deepseek-ai/dsh-a-share-screener/strategies
 */

import {
  amountLiquidity,
  deepDrawdown,
  excludeST,
  flatBase,
  lowPercentile,
  minListingDays,
  platformBreakout,
  volumeLimitUp,
  type Filter,
} from '../filters/filters.ts'
import type { StockMatch } from '../types.ts'

export interface StrategyDefinition {
  readonly id: string
  readonly label: string
  readonly filters: readonly Filter[]
}

export interface StrategyEvaluation {
  readonly passed: boolean
  readonly matchedFilters: readonly string[]
  readonly score: number
  readonly evidence: readonly string[]
}

export class StrategyRegistry {
  readonly #strategies = new Map<string, StrategyDefinition>()

  register(definition: StrategyDefinition): void {
    this.#strategies.set(definition.id, definition)
  }

  get(id: string): StrategyDefinition | undefined {
    return this.#strategies.get(id)
  }

  list(): readonly StrategyDefinition[] {
    return Array.from(this.#strategies.values())
  }

  evaluate(id: string, args: Parameters<Filter>[0]): StrategyEvaluation {
    const strategy = this.#strategies.get(id)
    if (strategy === undefined) {
      throw new Error(`strategy "${id}" is not registered`)
    }
    const matched: string[] = []
    let score = 0
    const evidence: string[] = []
    for (const filter of strategy.filters) {
      const outcome = filter(args)
      console.error('[evaluate]', strategyId, 'filter outcome:', JSON.stringify(outcome))
      if (!outcome.passed) {
        return { passed: false, matchedFilters: matched, score, evidence: [...evidence, ...outcome.evidence] }
      }
      matched.push((filter as Filter & { displayName?: string }).displayName ?? filter.name ?? '<anonymous>')
      score += outcome.score
      evidence.push(...outcome.evidence)
    }
    return { passed: true, matchedFilters: matched, score, evidence }
  }

  toMatch(evaluation: StrategyEvaluation, stock: StockMatch['stock'], quote: StockMatch['currentQuote']): StockMatch {
    return {
      stock,
      currentQuote: quote,
      score: evaluation.score,
      matchedFilters: evaluation.matchedFilters,
      evidence: evaluation.evidence,
    }
  }
}

export const BUILTIN_STRATEGIES: readonly StrategyDefinition[] = [
  {
    id: 'low-flat-limit-up',
    label: '低位平台放量突破',
    filters: [
      instrument('excludeST', excludeST),
      instrument('minListingDays:365', minListingDays(365)),
      instrument('lowPercentile:250:30', lowPercentile(250, 30)),
      instrument('flatBase:60:0.15', flatBase(60, 0.15)),
      instrument('volumeLimitUp:2:0.095', volumeLimitUp(2, 0.095)),
    ],
  },
  {
    id: 'oversold-rebound',
    label: '超跌反弹',
    filters: [
      instrument('excludeST', excludeST),
      instrument('deepDrawdown:60:-0.2', deepDrawdown(60, -0.2)),
    ],
  },
  {
    id: 'momentum-breakout',
    label: '动量突破',
    filters: [
      instrument('excludeST', excludeST),
      instrument('platformBreakout:20:0.03', platformBreakout(20, 0.03)),
      instrument('amountLiquidity:10000:20', amountLiquidity(10_000, 20)),
    ],
  },
]

function instrument(name: string, filter: Filter): Filter {
  // ESM function `name` is read-only; expose the identifier on a holder the
  // registry reads without breaking language semantics.
  const holder: { displayName: string } = { displayName: name }
  const named = ((...args: Parameters<Filter>) => filter(...args)) as Filter & { displayName: string }
  named.displayName = name
  void holder
  return named
}
