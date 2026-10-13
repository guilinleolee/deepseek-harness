/**
 * Performance analyzer: a pure single-pass fold over the plugin's event log.
 *
 * Fold semantics deliberately mirror `@deepseek-ai/dsh-session-stats`:
 * - `llmMs`  = `step/start` → `assistant/message` per step that assembled one
 *              (retry waits inside the step count as model time);
 * - `ttftMs` = `step/start` → first non-empty delta chunk;
 * - `decodeMs` = first chunk → assembled message;
 * - `toolMs` = `tool/call` → `tool/result` pairs matched by callId; unresolved
 *              calls are dropped at turn/end;
 * - tokens from `assistant/chunk {kind:'usage'}` records, with
 *   `assistant/message.usage` as the committed-step fallback.
 *
 * The same fold backs the `trajectoryDebug/perf` projection unit, so the
 * registry drive and the on-demand panel can never disagree.
 *
 * @module dsh-trajectory-debug-host/perf-analyzer
 */

import type {
  CallId,
  DebugEvent,
  DebugToolResult,
  EventSeq,
  FailureAgg,
  FailureCategory,
  PerfSnapshot,
  ToolPerf,
  TurnEndReason,
} from 'dsh-trajectory-debug'

export interface PerfFoldState {
  tools: Record<string, { calls: number; ok: number; failed: number; durations: number[] }>
  failures: Record<string, { category: FailureCategory; count: number; samples: number[] }>
  totalInput: number
  totalOutput: number
  byStep: number[]
  byToolType: Record<string, number>
  llmMs: number
  ttftMs: number
  ttftSteps: number
  decodeMs: number
  decodeTokens: number
  toolMs: number
  turns: number
  steps: number
  maxTokensEnds: number
  retries: number
  /** open step accumulators keyed by step number. */
  openSteps: Record<number, { startTime: number; firstChunkTime?: number }>
  /** open tool calls (callId → call facts). */
  openCalls: Record<string, { time: number; name: string }>
  /** turns that have at least one closed step. */
  turnsWithSteps: Record<number, true>
  /** last seen turn end reasons. */
  turnEndReasons: Record<number, TurnEndReason>
}

export function createPerfState(): PerfFoldState {
  return {
    tools: {},
    failures: {},
    totalInput: 0,
    totalOutput: 0,
    byStep: [],
    byToolType: {},
    llmMs: 0,
    ttftMs: 0,
    ttftSteps: 0,
    decodeMs: 0,
    decodeTokens: 0,
    toolMs: 0,
    turns: 0,
    steps: 0,
    maxTokensEnds: 0,
    retries: 0,
    openSteps: {},
    openCalls: {},
    turnsWithSteps: {},
    turnEndReasons: {},
  }
}

/** Fold ONE event. Unrelated events return the same state. */
export function applyPerf(state: PerfFoldState, event: DebugEvent | null): PerfFoldState {
  if (event === null) return state
  switch (event.type) {
    case 'step/start': {
      state.steps += 1
      state.openSteps[event.step] = { startTime: event.time }
      if (state.byStep.length <= event.step) state.byStep.length = event.step + 1
      return state
    }
    case 'assistant/chunk': {
      const open = state.openSteps[event.step]
      if (open && open.firstChunkTime === undefined && event.kind !== 'usage') {
        open.firstChunkTime = event.time
      }
      if (event.kind === 'usage' && event.usage) {
        state.totalInput += event.usage.input
        state.totalOutput += event.usage.output
        state.byStep[event.step] = (state.byStep[event.step] ?? 0) + event.usage.input + event.usage.output
      }
      return state
    }
    case 'assistant/message': {
      const open = state.openSteps[event.step]
      if (open) {
        state.llmMs += Math.max(0, event.time - open.startTime)
        if (open.firstChunkTime !== undefined) {
          state.ttftMs += Math.max(0, open.firstChunkTime - open.startTime)
          state.ttftSteps += 1
          state.decodeMs += Math.max(0, event.time - open.firstChunkTime)
        }
      }
      if (event.usage) {
        state.totalInput += event.usage.input
        state.totalOutput += event.usage.output
        state.byStep[event.step] = (state.byStep[event.step] ?? 0) + event.usage.input + event.usage.output
      }
      return state
    }
    case 'llm/retry': {
      state.retries += 1
      return state
    }
    case 'tool/call': {
      state.openCalls[event.callId] = { time: event.time, name: event.name }
      state.byToolType[event.name] = (state.byToolType[event.name] ?? 0) + 1
      return state
    }
    case 'tool/result': {
      const entry = state.openCalls[event.callId]
      delete state.openCalls[event.callId]
      if (entry) {
        const tool = state.tools[entry.name] ?? { calls: 0, ok: 0, failed: 0, durations: [] }
        tool.calls += 1
        if (event.isError) tool.failed += 1
        else tool.ok += 1
        tool.durations.push(Math.max(0, event.time - entry.time))
        state.tools[entry.name] = tool
        state.toolMs += Math.max(0, event.time - entry.time)
      }
      if (event.isError) {
        const category = classifyFailure(event)
        const key = JSON.stringify(category)
        const agg = state.failures[key] ?? { category, count: 0, samples: [] }
        agg.count += 1
        agg.samples.push(event.seq)
        state.failures[key] = agg
      }
      return state
    }
    case 'step/end': {
      state.turnsWithSteps[event.turn] = true
      return state
    }
    case 'turn/end': {
      state.turnEndReasons[event.turn] = event.reason
      // drop unresolved calls (results land within their turn)
      state.openCalls = {}
      if (event.reason === 'max-tokens') state.maxTokensEnds += 1
      if (event.reason !== 'completed') {
        const category: FailureCategory = { kind: 'turn', reason: event.reason }
        const key = JSON.stringify(category)
        const agg = state.failures[key] ?? { category, count: 0, samples: [] }
        agg.count += 1
        agg.samples.push(event.seq)
        state.failures[key] = agg
      }
      return state
    }
    default:
      return state
  }
}

/** Finalize: percentiles, turn counts, sorted failure list. */
export function finalizePerf(state: PerfFoldState, sessionId: string = 'session', asOfSeq: number = -1): PerfSnapshot {
  const tools: Record<string, ToolPerf> = {}
  for (const [name, t] of Object.entries(state.tools)) {
    const sorted = [...t.durations].sort((a, b) => a - b)
    tools[name] = {
      calls: t.calls,
      ok: t.ok,
      failed: t.failed,
      ms: {
        avg: t.durations.length === 0 ? 0 : t.durations.reduce((a, b) => a + b, 0) / t.durations.length,
        p50: percentile(sorted, 0.5),
        p90: percentile(sorted, 0.9),
        p95: percentile(sorted, 0.95),
      },
    }
  }
  const failures: FailureAgg[] = Object.values(state.failures)
    .sort((a, b) => b.count - a.count)
    .map((f) => ({ category: f.category, count: f.count, sampleSeqs: f.samples as EventSeq[] }))
  return {
    sessionId: sessionId as never,
    asOfSeq: asOfSeq as never,
    tools,
    failures,
    tokens: {
      totalInput: state.totalInput,
      totalOutput: state.totalOutput,
      byStep: state.byStep,
      byToolType: state.byToolType,
    },
    timing: {
      llmMs: state.llmMs,
      ttftMs: state.ttftMs,
      ttftSteps: state.ttftSteps,
      decodeMs: state.decodeMs,
      decodeTokens: state.decodeTokens,
      toolMs: state.toolMs,
    },
    turns: {
      count: Object.keys(state.turnsWithSteps).length,
      steps: state.steps,
      maxTokensEnds: state.maxTokensEnds,
      retries: state.retries,
    },
  }
}

/** Whole-log convenience: create → fold all → finalize. */
export function analyzePerf(
  events: readonly DebugEvent[],
  sessionId?: string,
  asOfSeq?: number,
  price?: TokenPriceTable,
): PerfSnapshot {
  const state = createPerfState()
  for (const event of events) applyPerf(state, event)
  const snapshot = finalizePerf(state, sessionId, asOfSeq)
  if (price !== undefined) {
    const input = (snapshot.tokens.totalInput / 1_000_000) * (price.inputPerMillion ?? 0)
    const output = (snapshot.tokens.totalOutput / 1_000_000) * (price.outputPerMillion ?? 0)
    return {
      ...snapshot,
      cost: {
        input: roundCost(input),
        output: roundCost(output),
        total: roundCost(input + output),
        currency: price.currency ?? 'USD',
      },
    }
  }
  return snapshot
}

/** Optional token price table (per 1M tokens), e.g. DeepSeek official rates. */
export interface TokenPriceTable {
  readonly inputPerMillion?: number
  readonly outputPerMillion?: number
  readonly currency?: string
}

function roundCost(value: number): number {
  return Math.round(value * 100_000) / 100_000
}

function classifyFailure(result: DebugToolResult): FailureCategory {
  const code = result.code ?? ''
  if (code.startsWith('SANDBOX_') || code.startsWith('FS_SANDBOX') || code === 'SANDBOX_UNAVAILABLE') {
    return { kind: 'sandbox', code }
  }
  if (code === 'TIMEOUT' || code === 'TOOL_TIMEOUT') return { kind: 'timeout' }
  return { kind: 'tool', code: code || 'UNKNOWN' }
}

/** Nearest-rank percentile over sorted durations (p in [0,1]). */
function percentile(sorted: readonly number[], p: number): number {
  if (sorted.length === 0) return 0
  const index = Math.min(sorted.length - 1, Math.max(0, Math.ceil(sorted.length * p) - 1))
  return sorted[index] ?? 0
}
