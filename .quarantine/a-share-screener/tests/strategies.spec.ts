/**
 * Strategy registry tests: short-circuit AND semantics, score accumulation,
 * and unknown-id failure mode. These tests lock the behavior the tool
 * executor relies on.
 *
 * @module @deepseek-ai/dsh-a-share-screener/tests/strategies
 */

import { describe, expect, it } from 'vitest'
import { BUILTIN_STRATEGIES, StrategyRegistry } from '../src/strategies/registry.ts'
import type { Filter, FilterContext } from '../src/filters/filters.ts'

const ctx: FilterContext = {
  stock: {
    symbol: '000001.SZ',
    name: '平安银行',
    market: 'SZ',
    industry: '银行',
    listDate: new Date('1991-04-03T00:00:00Z'),
    isST: false,
    isSuspended: false,
  },
  bars: [],
  quote: {
    symbol: '000001.SZ',
    price: 10,
    change: 0,
    changePercent: 0,
    volume: 0,
    amount: 0,
    timestamp: new Date(),
  },
}

function named(name: string, outcome: { passed: boolean; score: number; evidence: string[] }): Filter {
  const fn = (() => outcome) as Filter & { displayName: string }
  fn.displayName = name
  return fn
}

describe('StrategyRegistry', () => {
  it('passes when every filter passes and accumulates score + evidence', () => {
    const registry = new StrategyRegistry()
    registry.register({
      id: 'demo',
      label: 'demo',
      filters: [
        named('a', { passed: true, score: 1, evidence: ['a-ok'] }),
        named('b', { passed: true, score: 2, evidence: ['b-ok'] }),
      ],
    })
    const evaluation = registry.evaluate('demo', ctx)
    expect(evaluation).toEqual({
      passed: true,
      matchedFilters: ['a', 'b'],
      score: 3,
      evidence: ['a-ok', 'b-ok'],
    })
  })

  it('short-circuits on the first failing filter', () => {
    const registry = new StrategyRegistry()
    registry.register({
      id: 'demo',
      label: 'demo',
      filters: [
        named('a', { passed: true, score: 1, evidence: ['a-ok'] }),
        named('b', { passed: false, score: 0, evidence: ['b-fail'] }),
        named('c', { passed: true, score: 5, evidence: ['c-ok'] }),
      ],
    })
    const evaluation = registry.evaluate('demo', ctx)
    expect(evaluation.passed).toBe(false)
    expect(evaluation.matchedFilters).toEqual(['a'])
    expect(evaluation.score).toBe(1)
    expect(evaluation.evidence).toEqual(['a-ok', 'b-fail'])
  })

  it('throws on unknown strategy id', () => {
    const registry = new StrategyRegistry()
    expect(() => registry.evaluate('missing', ctx)).toThrow(/strategy "missing" is not registered/)
  })

  it('ships the built-in strategies enumerated in the README', () => {
    const ids = BUILTIN_STRATEGIES.map((strategy) => strategy.id)
    expect(ids).toEqual(['low-flat-limit-up', 'oversold-rebound', 'momentum-breakout'])
  })
})
