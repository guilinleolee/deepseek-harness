import { describe, expect, it } from 'vitest'
import { analyzePerf } from '../src/perf-analyzer.ts'
import { ev, sampleSession } from './helpers.ts'

describe('analyzePerf', () => {
  it('aggregates tool stats, durations and failure categories', () => {
    const perf = analyzePerf(sampleSession())
    expect(perf.tools['read']).toMatchObject({ calls: 1, ok: 1, failed: 0 })
    const bash = perf.tools['bash']!
    expect(bash).toMatchObject({ calls: 1, ok: 0, failed: 1 })
    expect(perf.timing.toolMs).toBeGreaterThan(0)
    expect(perf.failures).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ category: { kind: 'tool', code: 'EXIT_1' }, count: 1 }),
      ]),
    )
  })

  it('accounts tokens from usage chunks and per-step distribution', () => {
    const perf = analyzePerf(sampleSession())
    expect(perf.tokens.totalInput).toBe(280)
    expect(perf.tokens.totalOutput).toBe(70)
    // byStep is indexed by DSH step number (1-based); step 0 is unused.
    expect(perf.tokens.byStep[1]).toBe(150)
    expect(perf.tokens.byStep[2]).toBe(200)
  })

  it('computes model timing and ttft', () => {
    const events = [
      ev({ type: 'turn/start', turn: 1 }),
      ev({ type: 'step/start', turn: 1, step: 1, time: 0 }),
      ev({ type: 'assistant/chunk', step: 1, kind: 'text', text: 'hi', time: 500 }),
      ev({ type: 'assistant/message', turn: 1, step: 1, time: 1500 }),
      ev({ type: 'step/end', turn: 1, step: 1, time: 1500 }),
      ev({ type: 'turn/end', turn: 1, reason: 'completed', time: 1500 }),
    ]
    const perf = analyzePerf(events)
    expect(perf.timing.llmMs).toBe(1500)
    expect(perf.timing.ttftMs).toBe(500)
    expect(perf.timing.ttftSteps).toBe(1)
    expect(perf.timing.decodeMs).toBe(1000)
    expect(perf.turns).toMatchObject({ count: 1, steps: 1 })
  })

  it('counts retries and max-token ends', () => {
    const events = [
      ev({ type: 'turn/start', turn: 1 }),
      ev({ type: 'step/start', turn: 1, step: 1 }),
      ev({ type: 'llm/retry', turn: 1, step: 1 }),
      ev({ type: 'assistant/message', turn: 1, step: 1 }),
      ev({ type: 'step/end', turn: 1, step: 1 }),
      ev({ type: 'turn/end', turn: 1, reason: 'max-tokens' }),
    ]
    const perf = analyzePerf(events)
    expect(perf.turns.retries).toBe(1)
    expect(perf.turns.maxTokensEnds).toBe(1)
  })

  it('drops unresolved tool calls at turn end', () => {
    const events = [
      ev({ type: 'turn/start', turn: 1 }),
      ev({ type: 'tool/call', step: 1, callId: 'c1', name: 'bash', args: {} }),
      ev({ type: 'turn/end', turn: 1, reason: 'aborted' }),
    ]
    const perf = analyzePerf(events)
    expect(perf.tools['bash']).toBeUndefined()
  })

  it('estimates cost when a price table is configured', () => {
    const perf = analyzePerf(sampleSession(), undefined, undefined, {
      inputPerMillion: 1,
      outputPerMillion: 2,
      currency: 'USD',
    })
    // sampleSession tokens: 280 in / 70 out → $0.00028 + $0.00014
    expect(perf.cost).toBeDefined()
    expect(perf.cost!.input).toBeCloseTo(0.00028, 6)
    expect(perf.cost!.output).toBeCloseTo(0.00014, 6)
    expect(perf.cost!.total).toBeCloseTo(0.00042, 6)
    expect(perf.cost!.currency).toBe('USD')
  })

  it('omits cost when no price table is configured', () => {
    const perf = analyzePerf(sampleSession())
    expect(perf.cost).toBeUndefined()
  })

  it('computes percentiles', () => {
    const events = [
      ev({ type: 'turn/start', turn: 1 }),
      ev({ type: 'step/start', turn: 1, step: 1 }),
      ev({ type: 'tool/call', step: 1, callId: 'c1', name: 'x', args: {}, time: 0 }),
      ev({ type: 'tool/result', step: 1, callId: 'c1', isError: false, time: 100 }),
      ev({ type: 'step/end', turn: 1, step: 1 }),
      ev({ type: 'step/start', turn: 1, step: 2 }),
      ev({ type: 'tool/call', step: 2, callId: 'c2', name: 'x', args: {}, time: 200 }),
      ev({ type: 'tool/result', step: 2, callId: 'c2', isError: false, time: 600 }),
      ev({ type: 'step/end', turn: 1, step: 2 }),
      ev({ type: 'turn/end', turn: 1, reason: 'completed' }),
    ]
    const perf = analyzePerf(events)
    const x = perf.tools['x']!
    // durations [100, 400]; nearest-rank: p50 → 100, p90/p95 → 400
    expect(x.ms.p50).toBe(100)
    expect(x.ms.p90).toBe(400)
    expect(x.ms.p95).toBe(400)
    expect(x.ms.avg).toBe(250)
  })
})
